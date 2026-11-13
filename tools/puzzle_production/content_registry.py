"""Single authoring registry, deterministic runtime projection and atomic adoption."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile

from . import catalog_io
from . import operation_diagnostics as diagnostic
from .authoring_package import ID, STEM, REVISION, relative, require, sha, file_hash, file_table
from .contract import canonical_bytes, exact_keys, load_json, integer
from . import categories
from . import catalog_difficulty
from . import catalog_added
import time
import os

REGISTRY = "content/registry.json"
RUNTIME = "game/data/registry.json"
FORMAT = "picross-content-registry-v2"
BACKGROUND_FORMAT = "picross-content-registry-v3"
METADATA_FORMAT = "picross-content-registry-v4"
METADATA_RUNTIME_FORMAT = "picross-runtime-registry-v7"
IMAGE_RUNTIME_FORMAT = "picross-runtime-registry-v8"
JOURNAL = "picross-registration-journal-v2"
ROOT = Path(__file__).resolve().parents[2]


def atomic_bytes(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".za1-index-")
    temp = Path(name)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)


def projection(registry, catalog, root=None, *, ratings=None, added=None, backgrounds=None, reveals=None, version=None):
    from . import catalog_rating, catalog_background as background
    if ratings is None:
        ratings = catalog_rating.load_sources(root, registry) if root is not None else {}
    if added is None:
        added = catalog_added.load_sources(root, registry) if root is not None else {}
    if version is None:
        version = 7 if registry["format"] == METADATA_FORMAT else 6 if registry["format"] == BACKGROUND_FORMAT else 5
        if version == 7 and root is not None:
            raw = catalog_io.read(root, RUNTIME, 8 * 1024 * 1024, missing=True)
            from .catalog_transaction import image_generation
            if raw is not None and image_generation({"texts": {RUNTIME: raw}}):
                version = 8
    require(type(version) is int and version in (3, 4, 5, 6, 7, 8), "Unsupported projection version")
    require(registry["format"] != BACKGROUND_FORMAT or version == 6, "Background registry cannot be downgraded")
    require((registry["format"] == METADATA_FORMAT) == (version in (7, 8)), "Metadata registry requires runtime v7/v8")
    metadata = current_metadata(registry, catalog) if version >= 7 else {}
    if version >= 6 and backgrounds is None:
        require(root is not None, "Background projection requires its bound active sources")
        texts = {name: catalog_io.read(root, name, background.LIMIT, missing=True)
                 for name in background.text_names(registry)}
        backgrounds = background.projection(registry, texts)
        background.capability(root, required=version == 6 or any(row["status"] in ("selected", "none") for row in backgrounds.values()))
    if version == 8:
        if reveals is None:
            require(root is not None, "Image projection requires its bound active reveal sources")
            from . import reveal_source
            reveals = {entry["id"]: reveal_source.resolve(root, entry, catalog).get("effective_reveal", entry["reveal"])
                       for entry in registry["entries"]}
        require(set(reveals) == {entry["id"] for entry in registry["entries"]}, "Image projection must bind every reveal")
    result = {"format": "picross-runtime-registry-v" + str(version), "categories": categories.ordered(catalog), "entries": [
        {**{k: e[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")},
         "difficulty": catalog_rating.project(ratings[e["id"]]) if e["id"] in ratings else
                       catalog_difficulty.project(e["production"]["difficulty"]),
         **({"added_at": added[e["id"]]["added_at"] if e["id"] in added else None} if version >= 4 else {}),
         **({"background": backgrounds[e["id"]]} if version >= 6 else {}),
         **({"name": metadata[e["id"]]["name"], "category_id": metadata[e["id"]]["category_id"]} if version >= 7 else {}),
         **({"reveal": reveals[e["id"]]} if version == 8 else {})}
        for e in registry["entries"]]}
    for entry in result["entries"]: catalog_difficulty.validate_projection(entry["difficulty"], version=min(version, 5))
    require(len(canonical_bytes(result)) + 1 <= 8 * 1024 * 1024, "Runtime registry exceeds 8 MiB")
    return result


def validate(registry, catalog):
    categories.validate(catalog)
    metadata = isinstance(registry, dict) and registry.get("format") == METADATA_FORMAT
    modern = isinstance(registry, dict) and registry.get("format") in (BACKGROUND_FORMAT, METADATA_FORMAT)
    exact_keys(registry, {"format", "entries"} | ({"backgrounds"} if modern else set()) | ({"metadata"} if metadata else set()))
    require(registry["format"] in (FORMAT, BACKGROUND_FORMAT, METADATA_FORMAT) and isinstance(registry["entries"], list) and len(registry["entries"]) <= 10000 and
            len(canonical_bytes(registry)) + 1 <= 8 * 1024 * 1024,
            "Unsupported registry")
    validate_entries(registry["entries"], None if metadata else catalog)
    if metadata:
        rows = registry["metadata"]
        require(isinstance(rows, list) and len(rows) == len(registry["entries"]), "Metadata must cover every registered ID exactly once")
        for row in rows:
            exact_keys(row, {"id", "name", "category_id"})
            require(isinstance(row["id"], str) and ID.fullmatch(row["id"]), "Invalid metadata ID")
            validate_name(row["name"])
            categories.lookup(catalog, row["category_id"])
        require([row["id"] for row in rows] == [entry["id"] for entry in registry["entries"]],
                "Metadata IDs must match the sorted registry exactly once")
    if modern:
        from . import catalog_background
        catalog_background.index(registry)
    return registry


def validate_name(name):
    require(isinstance(name, str) and 1 <= len(name) <= 128 and bool(name.strip()),
            "Puzzle name must contain 1..128 characters and cannot be whitespace only")
    return name


def require_current(registry):
    require(isinstance(registry, dict) and registry.get("format") == METADATA_FORMAT,
            "Catalog migration required: run metadata_cli plan-migration before changing this v2/v3 checkout")


def current_metadata(registry, catalog, root=None, *, definitions=None):
    """Resolve current fields once; v4 never opens definitions or production files."""
    validate(registry, catalog)
    if registry["format"] == METADATA_FORMAT:
        return {row["id"]: deepcopy(row) for row in registry["metadata"]}
    result = {}
    for entry in registry["entries"]:
        if definitions is None:
            require(root is not None, "Legacy metadata requires bound definitions")
            raw = catalog_io.read(root, "game/" + entry["definition"], 2 * 1024 * 1024)
        else:
            require(entry["id"] in definitions, "Missing legacy metadata definition")
            raw = definitions[entry["id"]]
        if isinstance(raw, str): raw = raw.encode("utf-8")
        if isinstance(raw, bytes):
            require(catalog_io.checksum(raw) == entry["production"]["definition_sha256"], "Legacy metadata definition binding differs")
            definition = catalog_io.json_bytes(raw, 2 * 1024 * 1024)
        else:
            definition = raw
        require(isinstance(definition, dict) and definition.get("id") == entry["id"], "Legacy metadata identity differs")
        reveal = definition.get("reveal")
        require(isinstance(reveal, dict), "Legacy metadata lacks reveal name")
        result[entry["id"]] = {"id": entry["id"], "name": validate_name(reveal.get("name")), "category_id": entry["category_id"]}
    return result


def validate_entries(entries, catalog=None):
    """Validate immutable production entry structure separately from current FKs."""
    require(isinstance(entries, list) and len(entries) <= 10000, "Invalid production entries")
    seen = {k: set() for k in ("id", "key", "save_slot", "definition", "reveal")}
    for e in entries:
        exact_keys(e, {"id", "key", "save_slot", "definition", "reveal", "visible", "production", "category_id"})
        for field in seen:
            value = e[field]
            require(isinstance(value, str), "Invalid registry value")
            if field in ("definition", "reveal"):
                relative(value)
            folded = value.casefold()
            require(folded not in seen[field], "Registry collision: " + field)
            seen[field].add(folded)
        require(type(e["visible"]) is bool, "Invalid visibility")
        require(isinstance(e["category_id"], str) and categories.ID.fullmatch(e["category_id"]), "Invalid production category ID")
        if catalog is not None: categories.lookup(catalog, e["category_id"])
        require(ID.fullmatch(e["id"]) and e["key"] == e["id"] and STEM.fullmatch(e["save_slot"]), "Invalid new registry ID/slot")
        relative(e["save_slot"]+".json")
        require(e["definition"].startswith("data/content/") and e["definition"].endswith(".json") and
                e["reveal"].startswith("art/content/") and Path(e["reveal"]).suffix in (".png", ".svg"), "Invalid content resource path")
        p = exact_keys(e["production"], {"package", "package_sha256", "revision", "width", "height", "mode", "difficulty",
                                         "status", "blockers", "test_only", "definition_sha256", "reveal_sha256"})
        relative(p["package"])
        require(p["package"].startswith("content/packages/") and p["status"] == "registered" and p["blockers"] == [] and
                type(p["test_only"]) is bool, "Invalid production index")
        for field in ("package_sha256", "definition_sha256", "reveal_sha256"):
            sha(p[field])
        for field in ("width","height"):
            integer(p[field],1,50,"index "+field)
        require(isinstance(p["revision"],str) and REVISION.fullmatch(p["revision"]) and
                p["mode"] in ("mono","color") and isinstance(p["difficulty"],dict), "Invalid index metadata")
        catalog_difficulty.project(p["difficulty"])
    require(entries == sorted(entries, key=lambda e: e["id"]), "Registry entries must be sorted")
    return entries


def check_checkout(root, replay=False, *, check_projection=True, pending_journal=None, _verification=None):
    from . import catalog_io as io, reveal_source as reveal, catalog_background as background
    if _verification is not None:
        from .registration_verification import require_context
        require_context(_verification)
        require(replay and check_projection, "Verification requires a complete publishing checkout replay")
        _verification.checkout(root, pending_journal)
    lock = root / "content/.registration-pending.json"
    require(not lock.exists() or pending_journal is not None and lock.read_bytes() == pending_journal,
            "Interrupted registration: recovery required")
    catalog = categories.load(root / categories.PATH)
    r = validate(io.json_bytes(io.read(root, REGISTRY, 8 * 1024 * 1024), 8 * 1024 * 1024), catalog)
    from . import catalog_method
    catalog_method.load(root)
    reveal.source_paths(root, r)
    background.source_paths(root, r)
    background_index = background.index(r)
    expected = projection(r, catalog, root)
    image_runtime = expected["format"] == IMAGE_RUNTIME_FORMAT
    if image_runtime:
        from .catalog_transaction import reveal_assets
        live = {"game/" + row["reveal"] for row in expected["entries"]}
        live |= {reveal.identity(entry)["notice"] for entry in r["entries"]}
        require(reveal_assets(root, r) == live, "Reveal namespace has missing or inactive image resources")
    if check_projection:
        allowed = [canonical_bytes(expected)+b"\n"]
        has_sd2 = any(e["difficulty"] and e["difficulty"]["method"] == catalog_method.NEW for e in expected["entries"])
        if not has_sd2 and r["format"] == FORMAT:
            older = deepcopy(expected); older["format"] = "picross-runtime-registry-v4"
            allowed.append(canonical_bytes(older) + b"\n")
            if not catalog_added.load_sources(root, r):
                older["format"] = "picross-runtime-registry-v3"
                for e in older["entries"]: del e["added_at"]
                allowed.append(canonical_bytes(older) + b"\n")
                older["format"] = "picross-runtime-registry-v2"
                for e in older["entries"]: del e["difficulty"]
                allowed.append(canonical_bytes(older) + b"\n")
        require(io.read(root, RUNTIME, 8 * 1024 * 1024) in allowed, "Runtime registry is stale")
    for e in r["entries"]:
        p = e["production"]
        require(not p["test_only"] or root.resolve() != ROOT.resolve(), "Test-only content cannot enter the real catalog")
        package = root / p["package"]
        reveal.resolve(root, e, catalog)
        active_reveal = reveal.load(root, e, catalog)
        require(image_runtime or active_reveal is None or active_reveal.get("format") != "picross-catalog-reveal-v3",
                "Editor reveal requires explicit runtime v8 migration")
        # Also enforce the category binding without the expensive production replay.
        m = load_json(package / "manifest.json")
        from . import integrated_content
        source = background.load(root, r, e)
        require(image_runtime or source is None or source.get("format") != "picross-catalog-background-v5",
                "Editor background requires explicit runtime v8 migration")
        declared = m.get("format") in ("picross-target-export-v6", background.RECEIPT_FORMAT) or (
            m.get("format") == "picross-target-export-v5" and source is not None and source["format"] in background.REBIND_FORMATS)
        if source is not None and source.get("format") == "picross-catalog-background-v5":
            declared = True  # Manual authority is independently bound to the original production.
        require(declared == (e["id"] in background_index), "Background export v6/receipt requires its exact active index")
        if m.get("format") in integrated_content.FORMATS:
            integrated_content.check(root, e, m)
            continue  # Final integration is checked by runtime hashes, never by production replay.
        require(m.get("format") in ("picross-target-export-v1", "picross-target-export-v2", "picross-target-export-v3", "picross-target-export-v4", "picross-target-export-v5", "picross-target-export-v6"), "Unsupported registered export")
        if m["format"] != "picross-target-export-v1":
            require(m.get("category_id") == e["category_id"], "Registered category differs from export")
        if replay:
            from .target_adapter import verify_export
            if _verification is not None and p["package"] == _verification.package:
                m, report = _verification.written(root, p["package"], pending_journal)
            else:
                m, report = verify_export(package)
            require(m["definition_id"] == e["id"] and m["save_slot"] == e["save_slot"] and
                    m["definition"] == "runtime/"+e["definition"] and m["reveal"] == "runtime/"+e["reveal"] and
                    report["package_revision"] == p["revision"] and
                    all(report[k] == p[k] for k in ("width","height","mode","difficulty")), "Registered package identity differs")
    return r


def sync_runtime(root):
    """Explicit guarded projection; no difficulty analysis or trace replay."""
    from . import catalog_transaction as tx
    root = catalog_io.external(root)
    snapshot = tx.capture(root, allow_stale=True)
    check_checkout(root, replay=False, check_projection=False)
    catalog = catalog_io.json_bytes(snapshot["texts"][categories.PATH], categories.MAX_BYTES)
    expected = canonical_bytes(projection(snapshot["registry"], catalog, root)) + b"\n"
    if snapshot["texts"][RUNTIME] != expected:
        require_current(snapshot["registry"])
        journal = tx.prepare(root, snapshot, {}, operation="sync")
        tx.execute(root, journal)
    return {"status": "projected", "entries": len(snapshot["registry"]["entries"]),
            "categories": len(categories.load(root / categories.PATH)["categories"])}


def export_entry(export_dir, m, report, category, *, background=False):
    require(m.get("format") != "picross-target-export-v6" or background,
            "Background export v6 requires the full target-bound registration path")
    return {"id": m["definition_id"], "key": m["definition_id"], "save_slot": m["save_slot"],
         "definition": m["definition"].removeprefix("runtime/"), "reveal": m["reveal"].removeprefix("runtime/"), "visible": True,
         "category_id": category["id"],
         "production": {"package": "content/packages/" + m["definition_id"] + "/" + m["package_revision"],
             "package_sha256": file_hash(export_dir / "manifest.json"),
             "revision": m["package_revision"], "width": report["width"], "height": report["height"], "mode": report["mode"],
             "difficulty": report["difficulty"], "status": "registered", "blockers": [], "test_only": m["test_only"],
             "definition_sha256": m["files"][m["definition"]], "reveal_sha256": m["files"][m["reveal"]]}}


def registration(export_dir, root, *, apply=False, fail_step=None, difficulty=None, rebind_difficulty=False,
                 publication_seconds=None, recovery_seconds=None):
    diagnostic.seconds(publication_seconds)
    diagnostic.seconds(recovery_seconds)
    require(apply or publication_seconds is None and recovery_seconds is None, "Plan cannot accept RI-A budget overrides")
    from .catalog_integration import integrate
    return integrate(export_dir, root, apply=apply, fail_step=fail_step,
                     difficulty=difficulty, rebind_difficulty=rebind_difficulty,
                     publication_seconds=publication_seconds, recovery_seconds=recovery_seconds)


def recovery_projection(journal, before, after, catalog):
    """Accept exactly one canonical journal generation; return the current goal."""
    versions = []
    for side, registry in (("old", before), ("new", after)):
        require(journal[side][REGISTRY].encode() == canonical_bytes(registry)+b"\n",
                "Noncanonical journal registry")
        current = projection(registry, catalog, version=3)  # Exact legacy journal projection.
        legacy = deepcopy(current)
        legacy["format"] = "picross-runtime-registry-v2"
        for entry in legacy["entries"]:
            del entry["difficulty"]
        raw = journal[side][RUNTIME].encode()
        require(raw in (canonical_bytes(legacy)+b"\n", canonical_bytes(current)+b"\n"),
                "Invalid journal projections")
        versions.append(json.loads(raw)["format"])
    require(versions[0] == versions[1], "Mixed journal projection versions")
    return canonical_bytes(projection(before, catalog, version=4))+b"\n"


def recovery_target(root, journal, registry, runtime):
    """Validate the entire rollback view without writing into the checkout.

    Runtime bindings and complete retained exports are copied. No solver,
    export reconstruction, historical production replay or user data is involved.
    """
    from .content_update import path_in, notice_path
    overrides = {name: value.encode() for name, value in journal["old"].items()}
    overrides[RUNTIME] = runtime
    names = {REGISTRY, RUNTIME, categories.PATH}
    for entry in registry["entries"]:
        p = entry["production"]
        require(not p["test_only"] or root != ROOT.resolve(), "Test-only content cannot enter the real catalog")
        manifest = p["package"]+"/manifest.json"
        notice = notice_path(entry)
        names.update((manifest, "game/"+entry["definition"], "game/"+entry["reveal"], notice))
        if load_json(path_in(root, manifest)).get("format") != "picross-integrated-content-v1":
            from . import reveal_source
            # The frozen wire contract remains unchanged. Its retained package
            # is validated in full, then copied for the shared AT-aware checker.
            names.update(reveal_source.package(root, entry)[3])
    with tempfile.TemporaryDirectory(prefix="za1-recovery-check-") as directory:
        staged = Path(directory)
        for name in sorted(names):
            source = path_in(root, name)
            data = overrides[name] if name in overrides else source.read_bytes()
            destination = staged/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        check_checkout(staged)
    return names


def recover(root, *, recovery_seconds=None):
    """Explicit rollback after process death; preflight every byte before mutation."""
    started = time.monotonic()
    diagnostic.seconds(recovery_seconds, now=started)
    # Classification is read-only and bounded. All subsequent checks and writes
    # share the original call origin, including legacy recovery dispatch.
    with diagnostic.operation("Recovery", 300 if recovery_seconds is None else min(300, recovery_seconds),
                              "classification-pending", started=started) as active:
        root = catalog_io.external(root)
        def select_registration():
            active.classified_limit(1800 if recovery_seconds is None else recovery_seconds,
                                    "registration-default" if recovery_seconds is None else "override")
        operation, raw, staging_name = diagnostic.classify(root, on_registration=select_registration)
        require(operation == "registration" or recovery_seconds is None,
                "RI-A recovery override requires a registration journal")
        limit = (1800 if recovery_seconds is None else recovery_seconds) if operation == "registration" else 300
        active.classified_limit(limit, "override" if recovery_seconds is not None else operation + "-default")
        active.journal_raw = raw
        from . import catalog_publication as publication
        require(publication.read_journal(root, staging_name or "content/.registration-pending.json") == raw,
                "Journal changed during recovery classification")
        diagnostic.begin_segment("R0")
        result = _recover(root)
        if not active.complete:
            diagnostic.durable("rolled-back", lock_state="removed-legacy-contract")
        return result


def _recover(root):
    root = catalog_io.external(root)
    from .content_update import path_in
    lock = path_in(root, "content/.registration-pending.json")
    from . import catalog_transaction as tx
    from . import catalog_io as io
    raw = tx.read(root, tx.LOCK)
    if raw is None: return tx.recover(root)
    j = io.json_bytes(raw, tx.REVEAL_LIMIT)
    if isinstance(j, dict) and j.get("format") in set(tx.IMAGE_FORMATS.values()) | set(tx.PE_FORMATS.values()) | set(tx.REBIND_FORMATS.values()) | set(tx.BACKGROUND_FORMATS.values()) | set(tx.FORMATS.values()) | set(tx.AT_FORMATS.values()) | set(tx.PREVIOUS_FORMATS.values()) | set(tx.LEGACY_FORMATS.values()):
        return tx.recover(root)
    if isinstance(j, dict) and j.get("format") == "picross-content-update-journal-v1":
        from .content_update import recover_update
        return recover_update(root)
    require(isinstance(j, dict) and j.get("format") != "picross-registration-journal-v1",
            "Legacy registration journal: preserve all files and resolve with the pre-KAT-1 tool/registry contract before migration")
    exact_keys(j, {"format", "targets", "files", "old", "new", "categories"})
    require(j["format"] == JOURNAL and isinstance(j["files"], dict) and
            isinstance(j["targets"], list) and len(j["targets"]) == 4, "Invalid registration journal")
    require(isinstance(j["old"], dict) and isinstance(j["new"], dict) and
            set(j["old"]) == set(j["new"]) == {REGISTRY, RUNTIME} and
            all(isinstance(value, str) for side in ("old", "new") for value in j[side].values()), "Invalid journal indexes")
    require(isinstance(j["categories"], str) and categories.source_bytes(root / categories.PATH) == j["categories"].encode("utf-8"),
            "Categories changed since interrupted registration; preserve journal for manual review")
    catalog = categories.load(root / categories.PATH)
    old_registry = validate(json.loads(j["old"][REGISTRY]), catalog)
    new_registry = validate(json.loads(j["new"][REGISTRY]), catalog)
    tx.require_legacy_background(root, old_registry, new_registry, runtimes=(j["old"][RUNTIME], j["new"][RUNTIME]))
    reject_unbound_ratings(root, old_registry, new_registry)
    runtime = recovery_projection(j, old_registry, new_registry, catalog)
    added = [e for e in new_registry["entries"] if e not in old_registry["entries"]]
    require(len(added) == 1 and [e for e in new_registry["entries"] if e not in added] == old_registry["entries"], "Invalid journal change")
    e = added[0]
    notice = str(Path(e["reveal"]).with_suffix(".txt")).replace("\\", "/")
    require(j["targets"] == ["game/"+e["definition"], "game/"+e["reveal"], "game/"+notice, e["production"]["package"]], "Invalid journal targets")
    for name in (REGISTRY, RUNTIME):
        allowed = [j[side][name].encode() for side in ("old", "new")]
        if name == RUNTIME:
            allowed.append(runtime)  # Exact, derived recovery intermediate only.
        require(path_in(root,name).read_bytes() in allowed, "Index changed since interrupted registration")
    for name, value in j["files"].items():
        relative(name); sha(value)
        require(name in j["targets"][:3] or name.startswith(j["targets"][3]+"/"), "Invalid journal file target")
    for name, digest in ((j["targets"][0], e["production"]["definition_sha256"]),
                         (j["targets"][1], e["production"]["reveal_sha256"]),
                         (j["targets"][3]+"/manifest.json", e["production"]["package_sha256"])):
        require(j["files"].get(name) == digest, "Invalid journal file binding")
    for name in j["targets"][:3]:
        require(name in j["files"] and j["files"][name] == j["files"].get(j["targets"][3]+"/runtime/"+name.removeprefix("game/")),
                "Invalid journal runtime package binding")
    existing = []
    for name in j["targets"]:
        relative(name)
        path = path_in(root,name)
        if path.exists():
            present = file_table(path, time.monotonic()+300) if path.is_dir() else {"": path}
            for suffix, file in present.items():
                key = name+("/"+suffix if suffix else "")
                require(key in j["files"] and file_hash(file) == sha(j["files"][key]), "Recovery target changed; preserve files for manual review")
            existing.append(path)
    retained = recovery_target(root, j, old_registry, runtime)
    require(not any(n == target or n.startswith(target+"/") for n in retained for target in j["targets"]),
            "Recovery target overlaps retained content")
    # All checks passed; restore old indexes and the validated current projection.
    diagnostic.begin_segment("R1")
    for name, text in j["old"].items():
        atomic_bytes(root/name, runtime if name == RUNTIME else text.encode("utf-8"))
    for path in reversed(existing):
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    diagnostic.begin_segment("R2")
    lock.unlink()
    check_checkout(root)
    return {"status": "rolled-back", "registered": False}


def reject_unbound_ratings(root, *registries):
    from . import catalog_method
    require(catalog_method.load(root) is None, "Legacy journal cannot bind production default")
    from . import reveal_source
    require(not reveal_source.source_paths(root, *registries), "Legacy journal cannot bind reveal sources")
    from .catalog_rating import path, source_paths
    from .content_update import path_in
    source_paths(root, *registries)
    present, reports = catalog_added.source_paths(root, *registries)
    require(not present and not reports, "Legacy journal has unbound added data")
    for registry in registries:
        for entry in registry["entries"]:
            require(not path_in(root, path(entry["id"])).exists(),
                    "Legacy journal has unbound difficulty data; preserve all files and journal")
