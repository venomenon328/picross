"""Shared SD-C publication/rollback, bounded journals and foreign-byte guards.

Recovery only restores the validated old view. It never replays a solver and
never removes a file whose bytes are not owned by this transaction.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import tempfile
import time

from . import catalog_io
from .authoring_package import require, file_hash, file_table, sha, relative
from .contract import canonical_bytes, exact_keys
from . import catalog_rating as rating, categories, catalog_added as added, catalog_io as io, reveal_source as reveal, catalog_method
from . import operation_diagnostics as diagnostic

LOCK = "content/.registration-pending.json"
REGISTRY = "content/registry.json"
RUNTIME = "game/data/registry.json"
LIMIT = 24 * 1024 * 1024
LEGACY_FORMATS = {"registration": "picross-registration-journal-v3", "update": "picross-content-update-journal-v2",
           "adoption": "picross-difficulty-adoption-journal-v1", "sync": "picross-difficulty-adoption-journal-v1"}

PREVIOUS_FORMATS = {"registration": "picross-registration-journal-v4", "update": "picross-content-update-journal-v3",
           "adoption": "picross-catalog-metadata-journal-v1", "sync": "picross-catalog-metadata-journal-v1",
           "added-adoption": "picross-catalog-metadata-journal-v1"}
AT_FORMATS = {"registration": "picross-registration-journal-v5", "update": "picross-content-update-journal-v4",
           "adoption": "picross-catalog-metadata-journal-v2", "sync": "picross-catalog-metadata-journal-v2",
           "added-adoption": "picross-catalog-metadata-journal-v2", "reveal-adoption": "picross-reveal-adoption-journal-v1"}
FORMATS = {"registration": "picross-registration-journal-v6", "update": "picross-content-update-journal-v5",
           "adoption": "picross-catalog-metadata-journal-v3", "sync": "picross-catalog-metadata-journal-v3",
           "added-adoption": "picross-catalog-metadata-journal-v3", "reveal-adoption": "picross-reveal-adoption-journal-v2",
           "method-activation": "picross-difficulty-activation-journal-v1"}
REVEAL_LIMIT = 128 * 1024 * 1024


def modern(j):
    return isinstance(j, dict) and j.get("format") in (*FORMATS.values(), *AT_FORMATS.values())


def sd2(j):
    return isinstance(j, dict) and j.get("format") in FORMATS.values()


def safe(root, name):
    from .content_update import path_in
    return path_in(root, name)


def read(root, name):
    if name == LOCK:
        from .catalog_publication import read_journal
        return read_journal(root)
    limit = (catalog_method.LIMIT if name == catalog_method.PATH else reveal.LIMIT if name.startswith(reveal.ROOT + "/") else 131072 if name == categories.PATH else
             added.REPORT_LIMIT if name.startswith(added.ROOT + "/reports/") else
             added.LIMIT if name.startswith(added.ROOT + "/") else
             rating.LIMIT if name.startswith("content/difficulty/pz-") else
             16 * 1024 * 1024 if name.startswith("content/difficulty/reports/") else
             8 * 1024 * 1024 if name in (REGISTRY,RUNTIME) else
             2 * 1024 * 1024 if name.startswith("game/data/content/") else 64 * 1024 * 1024)
    return io.read(root, name, limit, missing=True)


def text_names(registry, *, legacy=False, previous=False, sd2=True):
    from .content_update import notice_path
    names = {REGISTRY, RUNTIME, categories.PATH}
    if sd2: names.add(catalog_method.PATH)
    for e in registry["entries"]:
        names.update(("game/" + e["definition"], notice_path(e), rating.path(e["id"])))
    if not legacy: names.update(added.path(e["id"]) for e in registry["entries"])
    if not legacy and not previous: names.update(reveal.path(e["id"]) for e in registry["entries"])
    return names


def retained_names(root, registry, *, reports=None, previous=False, exclude=()):
    from .content_update import notice_path
    if reports is None: _, reports = added.source_paths(root, registry)
    names = set(reports)
    if not previous:
        # Namespace validation belongs to capture/guard, with both registries
        # during recovery: a newly registered rating is a valid own text target.
        directory = safe(root, "content/difficulty/reports")
        if directory.exists():
            names.update(p.relative_to(root).as_posix() for p in directory.rglob("*") if p.is_file())
        for entry in registry["entries"]:
            names.add("game/" + entry["reveal"])
            names.update(reveal.package(root, entry)[3])
        return names - set(exclude)
    for e in registry["entries"]:
        manifest = e["production"]["package"] + "/manifest.json"
        names.update((manifest, "game/" + e["reveal"]))
        data = rating.bytes_json(read(root, manifest), 8 * 1024 * 1024)
        if data.get("format") != "picross-integrated-content-v1":
            names.add(e["production"]["package"] + "/runtime/" + notice_path(e).removeprefix("game/"))
    return names


@diagnostic.measured("Snapshot", "snapshots")
def capture(root, *, allow_stale=False):
    from .content_registry import check_checkout, validate
    root = catalog_io.external(root)
    from .catalog_publication import staging
    require(read(root, LOCK) is None and not staging(root), "Interrupted registration: recovery required")
    # Snapshot first, then validate it against the same checkout. No later read
    # may silently replace this starting point during expensive export checks.
    registry = rating.bytes_json(read(root, REGISTRY), 8 * 1024 * 1024)
    validate(registry, io.json_bytes(read(root, categories.PATH), 131072))
    initial_namespaces = namespaces(root, registry)
    names = text_names(registry)
    texts = {n: read(root, n) for n in names}
    retained = {n: io.file_hash(root, n) for n in retained_names(root, registry)}
    check_checkout(root, check_projection=not allow_stale)
    require(all(read(root, n) == b for n, b in texts.items()) and
            all(io.file_hash(root, n) == h for n, h in retained.items()), "Checkout changed during snapshot")
    require(namespaces(root, registry) == initial_namespaces, 'Checkout namespace changed during snapshot')
    return {"registry": registry, "texts": texts, "retained": retained, "namespaces": initial_namespaces}


def namespaces(root, *registries, temporary=()):
    catalog_method.load(root)
    reveals = reveal.source_paths(root, *registries, temporary=temporary)
    difficulty = rating.source_paths(root, *registries)
    reports = safe(root, "content/difficulty/reports")
    if reports.exists(): difficulty |= {p.relative_to(root).as_posix() for p in reports.rglob("*") if p.is_file()}
    dates, evidence = added.source_paths(root, *registries)
    packages = set()
    for r in registries:
        for e in r["entries"]:
            base = safe(root, e["production"]["package"])
            if base.exists():
                for p in base.rglob("*"):
                    p = safe(root, p.relative_to(root).as_posix())
                    if p.is_file(): packages.add(p.relative_to(root).as_posix())
    return {"reveals": sorted(reveals), "difficulty": sorted(difficulty), "added": sorted(set(dates) | evidence), "packages": sorted(packages)}


def pre_sd2_snapshot(snapshot):
    """Old plans cannot silently bind new method/default/runtime authorities."""
    require(snapshot["texts"].get(catalog_method.PATH) is None, "Legacy plan cannot bind production default")
    runtime = io.json_bytes(snapshot["texts"][RUNTIME], 8 * 1024 * 1024)
    require(runtime["format"] != "picross-runtime-registry-v5", "Legacy plan cannot bind runtime v5")
    for name, raw in snapshot["texts"].items():
        if name.startswith("content/difficulty/pz-") and raw is not None:
            require(rating.method(rating.validate(rating.bytes_json(raw))) == catalog_method.OLD, "Legacy plan cannot bind SD2 rating")
    return {**snapshot, "texts": {n: b for n, b in snapshot["texts"].items() if n != catalog_method.PATH}}


def historical_snapshot(snapshot):
    """Exact pre-AT source scope for stored reports, never an AT fallback."""
    from .content_update import notice_path
    r = rating.bytes_json(snapshot["texts"][REGISTRY], 8 * 1024 * 1024)
    require(all(snapshot["texts"].get(reveal.path(e["id"])) is None for e in r["entries"]), "Legacy plan/report cannot bind active reveal sources")
    names = {n for n in snapshot["retained"] if n.startswith(added.ROOT + "/reports/")}
    for e in r["entries"]:
        names |= {"game/" + e["reveal"], e["production"]["package"] + "/manifest.json"}
        n = e["production"]["package"] + "/runtime/" + notice_path(e).removeprefix("game/")
        if n in snapshot["retained"]: names.add(n)
    return {"texts": {n: b for n, b in snapshot["texts"].items() if not n.startswith(reveal.ROOT + "/")},
            "retained": {n: snapshot["retained"][n] for n in names}}


def report_names(run, operation="adoption"):
    if operation == "added-adoption": return {added.report_path(run)}
    if run is None: return set()
    from .catalog_analysis import run_id
    run_id(run)
    return {"content/difficulty/reports/" + run + "/report." + ext for ext in ("json", "md")}


def projection(texts, registry, *, version=5):
    from .content_registry import projection as project, validate
    catalog = rating.bytes_json(texts[categories.PATH].encode(), 131072)
    validate(registry, catalog)
    default = texts.get(catalog_method.PATH)
    catalog_method.from_bytes(default.encode() if default is not None else None)
    records = {}
    for e in registry["entries"]:
        raw = texts["game/" + e["definition"]].encode()
        require(hashlib.sha256(raw).hexdigest() == e["production"]["definition_sha256"], "Wrong transaction definition binding")
        value = texts[rating.path(e["id"])]
        if value is not None:
            records[e["id"]] = rating.validate(rating.bytes_json(value.encode()), definition_bytes=raw,
                                              production_mode=e["production"]["mode"])
    dates = {}
    for e in registry["entries"]:
        value = texts.get(added.path(e["id"]))
        if value is not None: dates[e["id"]] = added.validate(rating.bytes_json(value.encode(), added.LIMIT), e["id"])
    result = project(registry, catalog, ratings=records, added=dates, version=3 if version == 2 else version)
    if version == 2:
        result["format"] = "picross-runtime-registry-v2"
        for e in result["entries"]: del e["difficulty"]
    return canonical_bytes(result) + b"\n"


@diagnostic.measured("Staging/Proof", "staged_checkout_checks")
def _stage_check(root, texts, retained, additions=None, replacements=None, legacy=False):
    """Check a complete target view in isolation; no user saves or source replay."""
    from .content_registry import check_checkout, ROOT
    registry = rating.bytes_json(texts[REGISTRY].encode(), 8 * 1024 * 1024)
    if legacy:
        # Historical journals bind the manifest, which in turn binds the full
        # inventory. Reconstruct that inventory without altering journal fields.
        retained = dict(retained)
        for e in registry['entries']:
            for n in reveal.package(root, e)[3]: retained[n] = io.file_hash(root, n)
    require(root != ROOT.resolve() or all(not e["production"]["test_only"] for e in registry["entries"]),
            "Test-only content cannot enter the real catalog")
    with tempfile.TemporaryDirectory(prefix="sd-c-check-") as temp:
        stage = Path(temp)
        for name in sorted(set(retained) | set(texts) | set(additions or {}) | set(replacements or {})):
            if name in texts:
                data = texts[name].encode() if texts[name] is not None else None
            elif additions and name in additions:
                data = io.read(additions[name].parent, additions[name].name, 64 * 1024 * 1024)
            elif replacements and name in replacements:
                from .catalog_publication import decode_binary
                data = decode_binary(replacements[name])
            else:
                data = read(root, name)
            if data is None: continue
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        check_checkout(stage)


def prepare(root, snapshot, changes, *, operation, additions=None, report_run=None, replacements=None, generation="sd2"):
    additions = additions or {}
    require(operation in FORMATS, "Unknown transaction operation")
    before = snapshot["registry"]
    require(generation in ("sd2", "at"), "Unknown journal generation")
    current = generation == "sd2"
    if not current: snapshot = pre_sd2_snapshot(snapshot)
    after_raw = changes.get(REGISTRY, snapshot["texts"][REGISTRY])
    after = rating.bytes_json(after_raw, 8 * 1024 * 1024)
    names = text_names(before, sd2=current) | text_names(after, sd2=current) | report_names(report_run, operation)
    require(set(changes) <= names and not (set(additions) & names), "Unexpected transaction write target")
    old = {n: snapshot["texts"].get(n) if n in snapshot["texts"] else read(root, n) for n in names}
    # New ID resources and sidecars must not pre-exist outside the source registry.
    for n in names - text_names(before, sd2=current) - report_names(report_run, operation):
        require(old[n] is None, "Target already exists/collides: " + n)
    new = {**old, **changes}
    require(all(b is None or isinstance(b, bytes) for b in new.values()), "Invalid transaction bytes")
    j = {"format": (FORMATS if current else AT_FORMATS)[operation], "operation": operation,
         "old": {n: b.decode("utf-8") if b is not None else None for n, b in old.items()},
         "new": {n: b.decode("utf-8") if b is not None else None for n, b in new.items()},
         "retained": {n: h for n, h in snapshot["retained"].items() if n not in (replacements or {})},
         "additions": {n: io.file_hash(p.parent, p.name) for n, p in additions.items()}, "report_run": report_run, "replacements": replacements or {}}
    if operation not in ("reveal-adoption", "method-activation"): j["new"][RUNTIME] = projection(j["new"], after, version=5 if current else 4).decode()
    validate_journal(root, j, before_write=True)
    _stage_check(root, j["new"], j["retained"], additions, {n: pair["new"] for n, pair in j["replacements"].items()})
    from .catalog_publication import journal_bytes
    journal_bytes(j)
    return j


def _delta(j, before, after, root=None):
    from .content_update import notice_path
    op = j["operation"]
    changed = {n for n in j["old"] if j["old"][n] != j["new"][n]}
    mutable = {RUNTIME}
    package = None
    reveal_target = None
    if op == "registration":
        new_entries = [e for e in after["entries"] if e not in before["entries"]]
        require(len(new_entries) == 1 and [e for e in after["entries"] if e not in new_entries] == before["entries"], "Invalid registration delta")
        e = new_entries[0]
        mutable |= {REGISTRY, "game/" + e["definition"], notice_path(e), rating.path(e["id"])}
        if j["format"] in (FORMATS["registration"], AT_FORMATS["registration"], PREVIOUS_FORMATS["registration"]):
            mutable.add(added.path(e["id"]))
            value = j["new"][added.path(e["id"])]
            require(value is not None and added.validate(rating.bytes_json(value.encode(), added.LIMIT), e["id"])["provenance"]["kind"] == "registration", "Registration needs its first added timestamp")
        require(all(j["old"][n] is None for n in mutable - {REGISTRY, RUNTIME}), "Occupied registration target")
        require(j["new"][rating.path(e["id"])] is not None, "New registration requires difficulty 0.3")
        package, reveal_target = e["production"]["package"], "game/" + e["reveal"]
    elif op == "update":
        pairs = [(a, b) for a, b in zip(before["entries"], after["entries"]) if a != b]
        require(len(before["entries"]) == len(after["entries"]) and len(pairs) == 1, "Invalid update delta")
        a, e = pairs[0]
        active = j["old"].get(reveal.path(a["id"]))
        active = io.json_bytes(active.encode(), reveal.LIMIT) if active is not None else None
        require(all(a[k] == e[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")) and
                (active["revisions"][-1]["reveal_sha256"] if active else a["production"]["reveal_sha256"]) == e["production"]["reveal_sha256"], "Update changes fixed identity/reveal")
        n = "game/" + e["definition"]
        old_def = rating.bytes_json(j["old"][n].encode(), 2 * 1024 * 1024)
        new_def = rating.bytes_json(j["new"][n].encode(), 2 * 1024 * 1024)
        require(old_def["id"] == new_def["id"] == e["id"] and new_def["revision"] > old_def["revision"], "Invalid update revision")
        mutable |= {REGISTRY, n, notice_path(e), rating.path(e["id"])}
        if active:
            mutable.add(reveal.path(e["id"]))
            fresh = io.json_bytes(j["new"][reveal.path(e["id"])].encode(), reveal.LIMIT)
            catalog = rating.bytes_json(j["old"][categories.PATH].encode(), 131072)
            expected = reveal.rebind(active, e, new_def["revision"], fresh["bindings"][-1]["notice"]["text"].encode(), catalog)
            require(fresh == expected and j["new"][notice_path(e)] == j["old"][notice_path(e)], "Invalid reveal rebind delta")
        if (rating.definition(j["old"][n].encode())[3] != rating.definition(j["new"][n].encode())[3] or
                a["production"]["mode"] != e["production"]["mode"]):
            require(j["new"][rating.path(e["id"])] is not None, "Changed logic requires difficulty 0.3")
        package = e["production"]["package"]
        require(package != a["production"]["package"], "Update reuses old package")
    else:
        require(before == after, "Difficulty operation changes production registry")
        if op == "method-activation":
            mutable = {catalog_method.PATH}
            require(j["report_run"] is None and sd2(j), "Invalid activation transaction")
            prior = catalog_method.from_bytes(j["old"][catalog_method.PATH].encode() if j["old"][catalog_method.PATH] is not None else None)
            current = catalog_method.from_bytes(j["new"][catalog_method.PATH].encode())
            sources = catalog_method.source_hashes({"retained": j["retained"], "texts": {n: b.encode() if b is not None else None for n, b in j["old"].items()}})
            plan = rating.hashed({"format": catalog_method.PLAN, "expected": catalog_method.current(prior),
                "target": {k: current[k] for k in ("method", "method_hash")}, "sources": sources}, "result_hash")
            catalog_method.validate_plan(plan)
            require(current == catalog_method.record_for(plan, prior), "Invalid activation delta")
        elif op == "reveal-adoption":
            require(j["report_run"] is None, "Reveal adoption cannot adopt reports")
            from .catalog_reveal import validate_delta
            mutable |= validate_delta(j, before, root)
        elif op == "adoption": mutable |= {rating.path(e["id"]) for e in before["entries"]} | report_names(j["report_run"], j["operation"])
        elif op == "added-adoption":
            mutable |= {added.path(e["id"]) for e in before["entries"]} | report_names(j["report_run"], op)
            from .catalog_added_history import validate_delta
            validate_delta(j, before)
        else: require(j["report_run"] is None, "Sync cannot adopt reports")
    require(changed <= mutable, "Unexpected transaction source mutation")
    if package:
        rating_name = rating.path(e["id"])
        prior = rating.bytes_json(j["old"][rating_name].encode()) if j["old"][rating_name] is not None else None
        current = rating.bytes_json(j["new"][rating_name].encode()) if j["new"][rating_name] is not None else None
        if sd2(j):
            new_logic = op == "registration" or rating.definition(j["old"][n].encode())[3] != rating.definition(j["new"][n].encode())[3] or a["production"]["mode"] != e["production"]["mode"]
            default = catalog_method.from_bytes(j["old"][catalog_method.PATH].encode() if j["old"][catalog_method.PATH] is not None else None)
            require(not new_logic or current is not None and rating.method(current) == catalog_method.current(default)["method"], "New logic requires active production method")
        require(prior is None or current is not None, "Update cannot remove active difficulty")
        if current is not None and prior != current:
            require(current["rating_revision"] == (prior["rating_revision"] + 1 if prior else 1) and
                    current["adoption"]["previous_record_hash"] == (prior["record_hash"] if prior else None) and
                    current["adoption"]["report"] is None, "Invalid integration rating revision/provenance")
        require(package == "content/packages/" + e["id"] + "/" + e["production"]["revision"], "Invalid package target")
        require(all(n.startswith(package + "/") or n == reveal_target for n in j["additions"]), "Invalid package addition target")
        require(j["additions"].get(package + "/manifest.json") == e["production"]["package_sha256"], "Wrong package manifest binding")
        exported_notice = (fresh["bindings"][-1]["notice"]["sha256"] if op == "update" and active else hashlib.sha256(j["new"][notice_path(e)].encode()).hexdigest())
        for n, h in (("runtime/" + e["definition"], e["production"]["definition_sha256"]),
                     ("runtime/" + e["reveal"], e["production"]["reveal_sha256"]),
                     ("runtime/" + notice_path(e).removeprefix("game/"), exported_notice)):
            require(j["additions"].get(package + "/" + n) == h, "Wrong package runtime binding")
        if reveal_target: require(j["additions"].get(reveal_target) == e["production"]["reveal_sha256"], "Wrong new reveal binding")
        require(not any(n == package or n.startswith(package + "/") for n in j["retained"]), "Addition overlaps retained package")
    else:
        require(not j["additions"], "Unexpected difficulty additions")
    return package


@diagnostic.measured("Journal validation", "journal_validations")
def validate_journal(root, j, *, before_write=False):
    require(isinstance(j, dict) and isinstance(j.get("format"), str), "Invalid catalog journal")
    current_generation = modern(j)
    new_generation = sd2(j)
    exact_keys(j, {"format", "operation", "old", "new", "retained", "additions", "report_run"} | ({"replacements"} if current_generation else set()))
    require(isinstance(j["format"], str) and isinstance(j["operation"], str) and j["operation"] in FORMATS and
            j["format"] in (FORMATS[j["operation"]], AT_FORMATS.get(j["operation"]), PREVIOUS_FORMATS.get(j["operation"]), LEGACY_FORMATS.get(j["operation"])), "Unsupported catalog journal")
    legacy = j["format"] in LEGACY_FORMATS.values()
    for k in ("old", "new", "retained", "additions"): require(isinstance(j[k], dict), "Invalid journal map")
    require(all(v is None or isinstance(v, str) for side in ("old", "new") for v in j[side].values()), "Invalid journal text")
    for side in ("old", "new"):
        for n in (REGISTRY, RUNTIME, categories.PATH): require(isinstance(j[side].get(n), str), "Missing journal source")
    before, after = (rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
    from .content_registry import validate
    for side, registry in (("old",before),("new",after)):
        validate(registry, io.json_bytes(j[side][categories.PATH].encode(), 131072))
    names = text_names(before, legacy=legacy, previous=not current_generation, sd2=new_generation) | text_names(after, legacy=legacy, previous=not current_generation, sd2=new_generation) | report_names(j["report_run"], j["operation"])
    if not new_generation:
        require(catalog_method.load(root) is None, "Legacy journal cannot bind production default")
        # Old sync permits opaque stale bytes, but must never downgrade the
        # recognized C authority under that exception.
        try: old_runtime = io.json_bytes(j["old"][RUNTIME].encode(), 8 * 1024 * 1024)
        except ValueError: old_runtime = None
        require(not isinstance(old_runtime, dict) or old_runtime.get("format") != "picross-runtime-registry-v5",
                "Legacy journal cannot bind runtime v5")
    if not current_generation:
        require(not reveal.source_paths(root, before, after), "Legacy journal cannot bind reveal sources")
    else:
        from .catalog_publication import validate_replacements
        validate_replacements(j, before)
    if legacy:
        present, reports = added.source_paths(root, before, after)
        require(not present and not reports, "Legacy journal cannot bind added sources")
    require(set(j["old"]) == set(j["new"]) == names, "Invalid journal target set")
    old_reports = set()
    for e in before["entries"]:
        raw = j["old"].get(added.path(e["id"]))
        if raw is not None:
            source = added.validate(rating.bytes_json(raw.encode(), added.LIMIT), e["id"])["provenance"]["evidence"]
            if source: old_reports.add(source["path"])
    retained = retained_names(root, before, reports=old_reports, previous=not current_generation,
                              exclude=set(j.get("replacements", {})) | report_names(j["report_run"], j["operation"]))
    require(set(j["retained"]) == retained, "Invalid retained source set")
    for side, registry in (("old", before), ("new", after)):
        from .content_registry import validate
        validate(registry, rating.bytes_json(j[side][categories.PATH].encode(), 131072))
        require(j[side][REGISTRY].encode() == canonical_bytes(registry) + b"\n", "Noncanonical journal registry")
        versions = [5] if new_generation else [3] if legacy else [4]
        if j["operation"] in ("reveal-adoption", "method-activation") or new_generation and side == "old": versions = [4, 5] if new_generation else [4]
        if not legacy and side == "old" and all(j[side].get(added.path(e["id"])) is None for e in registry["entries"]): versions += [2, 3]
        if j["operation"] in ("reveal-adoption", "method-activation") and all(j[side].get(added.path(e["id"])) is None for e in registry["entries"]): versions += [2, 3]
        if side == "new" or j["operation"] != "sync":
            raw = j[side][RUNTIME].encode()
            runtime = io.json_bytes(raw, 8 * 1024 * 1024)
            matching = [v for v in versions if runtime.get("format") == "picross-runtime-registry-v" + str(v)]
            require(matching and raw == projection(j[side], registry, version=matching[0]), "Invalid journal projection")
    package = _delta(j, before, after, root)
    for n, h in {**j["retained"], **j["additions"]}.items(): relative(n); sha(h); safe(root, n)
    if j["report_run"] is not None and j["operation"] != "added-adoption":
        from .catalog_analysis import validate_report, markdown
        prefix = "content/difficulty/reports/" + j["report_run"] + "/report."
        report = validate_report(rating.bytes_json(j["new"][prefix + "json"].encode(), 16 * 1024 * 1024))
        require(report["run_id"] == j["report_run"] and j["new"][prefix + "md"] == markdown(report), "Conflicting journal report")
        require(j["operation"] == "adoption" and report["operation"]["phase"] == "adopted" and
                all(j["old"][n] is None for n in report_names(j["report_run"], j["operation"])), "Report is not a new adoption")
        require(all(hashlib.sha256(j["old"][n].encode()).hexdigest() == h for n,h in report["result"]["snapshot"].items()),
                "Wrong report snapshot")
        from .catalog_analysis import SOURCE_FORMATS, source_hashes
        if report["format"] in SOURCE_FORMATS:
            captured = {"retained": j["retained"], "texts": {n: j["old"][n].encode() if j["old"][n] is not None else None
                        for n in text_names(before, legacy=legacy, previous=not current_generation, sd2=new_generation)}}
            require(report["result"]["sources"] == source_hashes(captured, report["format"]), "Wrong report source snapshot")
        entries = {e["id"]: e for e in before["entries"]}
        rows = {r["id"]: r for r in report["result"]["entries"]}
        require(set(rows) <= set(entries) and (report["result"]["selection"] != "all" or set(rows) == set(entries)), "Wrong report selection")
        from .catalog_difficulty import project as historical
        for identifier, entry in entries.items():
            name = rating.path(identifier)
            prior = rating.bytes_json(j["old"][name].encode()) if j["old"][name] is not None else None
            current = rating.bytes_json(j["new"][name].encode()) if j["new"][name] is not None else None
            row = rows.get(identifier)
            if row is None:
                require(prior == current, "Unselected rating changed")
                continue
            require(row["previous_record_hash"] == (prior["record_hash"] if prior else None) and
                    row["old"] == (rating.project(prior) if prior else historical(entry["production"]["difficulty"])), "Wrong report old rating")
            if report["format"] in SOURCE_FORMATS:
                require(row["previous_rating_revision"] == (prior["rating_revision"] if prior else None), "Wrong report old revision")
            if row["current_source"] is not None:
                _, _, source, logic = rating.definition(j["old"]["game/" + entry["definition"]].encode(), method=report["result"].get("method", catalog_method.OLD))
                require(row["current_source"] == source and row["logic_binding"] == logic, "Wrong report definition binding")
            if row["status"] != "rated":
                require(prior == current, "Incomplete attempt changed active rating")
            else:
                require(current is not None and rating.project(current) == row["proposed"] and
                        current["rating"]["rating_hash"] == row["rating_hash"], "Wrong adopted report rating")
                from .catalog_analysis import FORMAT as CURRENT_REPORT
                if report["format"] == CURRENT_REPORT:
                    require(row["assessment"] == current["rating"]["result"].get("assessment"), "Wrong adopted report assessment")
                if prior != current:
                    require(current["rating_revision"] == (prior["rating_revision"] + 1 if prior else 1) and
                            current["adoption"]["previous_record_hash"] == row["previous_record_hash"] and
                            current["adoption"]["report"] == {"run_id": report["run_id"], "result_hash": report["result_hash"]} and
                            rating.checked_from_active(current)["checked_hash"] == row["checked_hash"], "Wrong adopted report provenance")
    else:
        require(j["operation"] != "adoption", "Adoption requires a report")
    guard(root, j, old_only=before_write)
    # The rollback goal is checked in full before any real mutation. A sync may
    # have started with a stale projection; recovery directly restores current v4.
    old = deepcopy(j["old"])
    old[RUNTIME] = restore_runtime(j, before)
    _stage_check(root, old, j["retained"], replacements={n: pair["old"] for n, pair in j.get("replacements", {}).items()}, legacy=not current_generation)
    return package, old[RUNTIME]


def restore_runtime(j, registry):
    if j["operation"] in ("reveal-adoption", "method-activation") or sd2(j) and j["operation"] != "sync":
        return j["old"][RUNTIME]
    if sd2(j):
        raw = j["old"][RUNTIME].encode()
        try:
            runtime = io.json_bytes(raw, 8 * 1024 * 1024)
            version = next((v for v in (2, 3, 4, 5) if runtime.get("format") == "picross-runtime-registry-v" + str(v)), None)
            if version is not None and raw == projection(j["old"], registry, version=version): return j["old"][RUNTIME]
        except (ValueError, TypeError, KeyError):
            pass  # A sync may have begun with stale bytes; sources remain strict.
    return projection(j["old"], registry, version=5 if sd2(j) else 4).decode()


def guard(root, j, *, old_only=False, journal_bytes=None):
    if modern(j):
        from .catalog_publication import guard as current_guard
        return current_guard(root, j, old_only=old_only, raw=journal_bytes)
    from . import catalog_method
    require(catalog_method.load(root) is None, "Legacy journal cannot bind production default")
    registries = [rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new")]
    require(not reveal.source_paths(root, *registries), "Legacy journal cannot bind reveal sources")
    for e in registries[0]['entries']: reveal.package(root, e)
    rating.source_paths(root, *registries)
    extras = set(j["retained"]) & {n for n in j["retained"] if n.startswith(added.ROOT + "/reports/")}
    if j["operation"] == "added-adoption": extras |= report_names(j["report_run"], j["operation"])
    added.source_paths(root, *registries, extra_reports=extras)
    if journal_bytes is not None:
        require(read(root, LOCK) == journal_bytes, "Journal changed; preserve all transaction files")
    for n, old in j["old"].items():
        allowed = [old]
        if not old_only:
            allowed.append(j["new"][n])
            if n == RUNTIME:
                registry = rating.bytes_json(j["old"][REGISTRY].encode(), 8 * 1024 * 1024)
                allowed.append(restore_runtime(j, registry))
        current = read(root, n)
        require(current in [v.encode() if v is not None else None for v in allowed], "Transaction target changed; preserve journal: " + n)
    for n, h in j["retained"].items():
        p = safe(root, n)
        require(p.is_file() and file_hash(p) == h, "Retained source changed; preserve journal: " + n)
    for n, h in j["additions"].items():
        p = safe(root, n)
        require(not p.exists() if old_only else not p.exists() or p.is_file() and file_hash(p) == h,
                "Transaction package changed; preserve journal: " + n)
    # Unknown files in an added package belong to somebody else. Never rmtree.
    packages = set()  # roots derived below, not supplied by callers
    for n in j["additions"]:
        if n.startswith("content/packages/"):
            packages.add("/".join(n.split("/")[:4]))
    for name in packages:
        p = safe(root, name)
        if p.exists():
            present = file_table(p, time.monotonic() + 300)
            require(all(name + "/" + n in j["additions"] for n in present), "Transaction package changed; unexpected file")


def _write(root, name, text, *, create=False):
    from .content_registry import atomic_bytes
    target = safe(root, name)
    if text is None:
        target.unlink(missing_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        if create: _publish_new(target, text.encode())
        else: atomic_bytes(target, text.encode())


def _publish_new(target, data):
    """Publish complete new bytes without replacing a concurrently created file."""
    fd, temporary = tempfile.mkstemp(dir=target.parent, prefix=".sd-c-new-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.link(temporary, target)  # Atomic no-replace on the same filesystem.
    finally:
        Path(temporary).unlink(missing_ok=True)


def execute(root, j, additions=None, *, fail_step=None, publication_seconds=None, recovery_seconds=None):
    diagnostic.seconds(publication_seconds)
    diagnostic.seconds(recovery_seconds)
    require(isinstance(j, dict), "Invalid catalog journal")
    require(modern(j) and j.get("operation") == "registration" or publication_seconds is None and recovery_seconds is None,
            "RI-A overrides require a new registration")
    if modern(j):
        from .catalog_publication import execute as current_execute
        return current_execute(root, j, additions, fail_step=fail_step,
                               publication_seconds=publication_seconds, recovery_seconds=recovery_seconds)
    from .content_registry import check_checkout
    additions = additions or {}
    validate_journal(root, j, before_write=True)
    raw = canonical_bytes(j) + b"\n"
    require(len(raw) <= LIMIT, "Transaction journal exceeds 24 MiB")
    lock = safe(root, LOCK)
    with lock.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    try:
        guard(root, j, old_only=True, journal_bytes=raw)
        for index, (n, h) in enumerate(sorted(j["additions"].items())):
            guard(root, j, journal_bytes=raw)
            data = additions[n].read_bytes()
            require(hashlib.sha256(data).hexdigest() == h, "Staged package changed")
            target = safe(root, n)
            target.parent.mkdir(parents=True, exist_ok=True)
            require(not target.exists(), "Addition appeared during publication")
            _publish_new(target, data)
            if index == 0 and fail_step == "crash": raise InterruptedError("Injected registration interruption")
            if index == 0 and fail_step == "files": raise OSError("Injected registration interruption")
        if fail_step == "crash-package": raise InterruptedError("Injected update crash after package")
        if j["operation"] == "registration":
            from .target_adapter import verify_export
            before, after = (rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
            package = _delta(j, before, after)
            verify_export(safe(root, package))  # Retain mandatory ZA-1 written-package verification.
        names = sorted(n for n in j["new"] if n != RUNTIME and j["old"][n] != j["new"][n]) + [RUNTIME]
        for n in names:
            guard(root, j, journal_bytes=raw)
            require(read(root, n) == (j["old"][n].encode() if j["old"][n] is not None else None), "Transaction target changed during publication")
            _write(root, n, j["new"][n], create=j["old"][n] is None and j["new"][n] is not None)
            if fail_step == "crash-" + n or n == REGISTRY and fail_step == "crash-index" or n == RUNTIME and fail_step == "crash-runtime":
                raise InterruptedError("Injected transaction interruption: " + n)
            if fail_step == n or n == REGISTRY and fail_step == "index": raise OSError("Injected update failure: " + n)
        guard(root, j, journal_bytes=raw)
        check_checkout(root, replay=j["operation"] == "registration", pending_journal=raw)
        guard(root, j, journal_bytes=raw)
        require(all(read(root, n) == (v.encode() if v is not None else None) for n,v in j["new"].items()), "Publication changed before completion")
        require(lock.read_bytes() == raw, "Journal changed during publication")
        lock.unlink()
    except InterruptedError:
        raise
    except BaseException:
        # Recovery refuses foreign changes and keeps the lock if rollback is unsafe.
        require(read(root, LOCK) == raw, "Journal changed; preserve all transaction files")
        recover(root)
        raise


def recover(root):
    if diagnostic.frame.get() is None or diagnostic.frame.get().kind != "Recovery":
        from .content_registry import recover as classified_recover
        return classified_recover(root)
    return _recover(root)


def _recover(root):
    from .content_registry import check_checkout
    root = catalog_io.external(root)
    raw = read(root, LOCK)
    if raw is None or modern(io.json_bytes(raw, REVEAL_LIMIT)):
        from .catalog_publication import recover as current_recover
        return current_recover(root)
    j = rating.bytes_json(raw, LIMIT)
    _, runtime = validate_journal(root, j)
    # Delete only individually hash-checked additions. Empty directory cleanup is
    # cosmetic; retaining empty parents cannot conceal or destroy foreign work.
    for n in sorted(j["additions"], reverse=True):
        guard(root, j, journal_bytes=raw)
        safe(root, n).unlink(missing_ok=True)
    for n in sorted(j["old"]):
        if n == RUNTIME or j["old"][n] == j["new"][n]: continue
        guard(root, j, journal_bytes=raw)
        _write(root, n, j["old"][n])
    guard(root, j, journal_bytes=raw)
    _write(root, RUNTIME, runtime)
    check_checkout(root, pending_journal=raw)
    guard(root, j, journal_bytes=raw)
    goal = {**j["old"], RUNTIME: runtime}
    require(all(read(root, n) == (v.encode() if v is not None else None) for n,v in goal.items()) and
            all(read(root, n) is None for n in j["additions"]), "Recovery goal changed before completion")
    require(read(root, LOCK) == raw, "Journal changed during recovery")
    safe(root, LOCK).unlink()
    # Only remove verified empty directories under the new package/sidecar roots.
    for n in sorted(set(j["additions"]) | {n for n in j["old"] if j["old"][n] is None}, reverse=True):
        p = safe(root, n).parent
        while p != root and p.is_relative_to(root) and p not in (root/"content", root/"game"):
            try: p.rmdir()
            except OSError: break
            p = p.parent
    return {"status": "rolled-back", "registered": False}
