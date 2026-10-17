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

from .authoring_package import require, file_hash, file_table, sha, relative
from .contract import canonical_bytes, exact_keys
from . import catalog_rating as rating, categories

LOCK = "content/.registration-pending.json"
REGISTRY = "content/registry.json"
RUNTIME = "game/data/registry.json"
LIMIT = 24 * 1024 * 1024
FORMATS = {"registration": "picross-registration-journal-v3", "update": "picross-content-update-journal-v2",
           "adoption": "picross-difficulty-adoption-journal-v1", "sync": "picross-difficulty-adoption-journal-v1"}


def safe(root, name):
    from .content_update import path_in
    return path_in(root, name)


def read(root, name):
    path = safe(root, name)
    require(not path.exists() or path.is_file(), "Transaction target must be a file: " + name)
    if not path.exists(): return None
    limit = (LIMIT if name == LOCK else 131072 if name == categories.PATH else
             rating.LIMIT if name.startswith("content/difficulty/pz-") else
             16 * 1024 * 1024 if name.startswith("content/difficulty/reports/") else
             8 * 1024 * 1024 if name in (REGISTRY,RUNTIME) else
             2 * 1024 * 1024 if name.startswith("game/data/content/") else 64 * 1024 * 1024)
    return rating.read_file(path, limit)


def text_names(registry):
    from .content_update import notice_path
    names = {REGISTRY, RUNTIME, categories.PATH}
    for e in registry["entries"]:
        names.update(("game/" + e["definition"], notice_path(e), rating.path(e["id"])))
    return names


def retained_names(root, registry):
    from .content_update import notice_path
    names = set()
    for e in registry["entries"]:
        manifest = e["production"]["package"] + "/manifest.json"
        names.update((manifest, "game/" + e["reveal"]))
        data = rating.bytes_json(read(root, manifest), 8 * 1024 * 1024)
        if data.get("format") != "picross-integrated-content-v1":
            names.add(e["production"]["package"] + "/runtime/" + notice_path(e).removeprefix("game/"))
    return names


def capture(root, *, allow_stale=False):
    from .content_registry import check_checkout
    root = root.resolve()
    require(read(root, LOCK) is None, "Interrupted registration: recovery required")
    # Snapshot first, then validate it against the same checkout. No later read
    # may silently replace this starting point during expensive export checks.
    registry = rating.bytes_json(read(root, REGISTRY), 8 * 1024 * 1024)
    names = text_names(registry)
    texts = {n: read(root, n) for n in names}
    retained = {n: file_hash(safe(root, n)) for n in retained_names(root, registry)}
    check_checkout(root, check_projection=not allow_stale)
    require(all(read(root, n) == b for n, b in texts.items()) and
            all(file_hash(safe(root, n)) == h for n, h in retained.items()), "Checkout changed during snapshot")
    return {"registry": registry, "texts": texts, "retained": retained}


def report_names(run):
    if run is None: return set()
    from .catalog_analysis import run_id
    run_id(run)
    return {"content/difficulty/reports/" + run + "/report." + ext for ext in ("json", "md")}


def projection(texts, registry):
    from .content_registry import projection as project, validate
    catalog = rating.bytes_json(texts[categories.PATH].encode(), 131072)
    validate(registry, catalog)
    records = {}
    for e in registry["entries"]:
        raw = texts["game/" + e["definition"]].encode()
        require(hashlib.sha256(raw).hexdigest() == e["production"]["definition_sha256"], "Wrong transaction definition binding")
        value = texts[rating.path(e["id"])]
        if value is not None:
            records[e["id"]] = rating.validate(rating.bytes_json(value.encode()), definition_bytes=raw)
    return canonical_bytes(project(registry, catalog, ratings=records)) + b"\n"


def _stage_check(root, texts, retained, additions=None):
    """Check a complete target view in isolation; no user saves or source replay."""
    from .content_registry import check_checkout, ROOT
    registry = rating.bytes_json(texts[REGISTRY].encode(), 8 * 1024 * 1024)
    require(root != ROOT.resolve() or all(not e["production"]["test_only"] for e in registry["entries"]),
            "Test-only content cannot enter the real catalog")
    with tempfile.TemporaryDirectory(prefix="sd-c-check-") as temp:
        stage = Path(temp)
        for name in sorted(set(retained) | set(texts) | set(additions or {})):
            if name in texts:
                data = texts[name].encode() if texts[name] is not None else None
            elif additions and name in additions:
                data = additions[name].read_bytes()
            else:
                data = read(root, name)
            if data is None: continue
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        check_checkout(stage)


def prepare(root, snapshot, changes, *, operation, additions=None, report_run=None):
    additions = additions or {}
    require(operation in FORMATS, "Unknown transaction operation")
    before = snapshot["registry"]
    after_raw = changes.get(REGISTRY, snapshot["texts"][REGISTRY])
    after = rating.bytes_json(after_raw, 8 * 1024 * 1024)
    names = text_names(before) | text_names(after) | report_names(report_run)
    require(set(changes) <= names and not (set(additions) & names), "Unexpected transaction write target")
    old = {n: snapshot["texts"].get(n) if n in snapshot["texts"] else read(root, n) for n in names}
    # New ID resources and sidecars must not pre-exist outside the source registry.
    for n in names - text_names(before) - report_names(report_run):
        require(old[n] is None, "Target already exists/collides: " + n)
    new = {**old, **changes}
    require(all(b is None or isinstance(b, bytes) for b in new.values()), "Invalid transaction bytes")
    j = {"format": FORMATS[operation], "operation": operation,
         "old": {n: b.decode("utf-8") if b is not None else None for n, b in old.items()},
         "new": {n: b.decode("utf-8") if b is not None else None for n, b in new.items()},
         "retained": snapshot["retained"], "additions": {n: file_hash(p) for n, p in additions.items()}, "report_run": report_run}
    j["new"][RUNTIME] = projection(j["new"], after).decode()
    validate_journal(root, j, before_write=True)
    _stage_check(root, j["new"], j["retained"], additions)
    require(len(canonical_bytes(j)) + 1 <= LIMIT, "Transaction journal exceeds 24 MiB")
    return j


def _delta(j, before, after):
    from .content_update import notice_path
    op = j["operation"]
    changed = {n for n in j["old"] if j["old"][n] != j["new"][n]}
    mutable = {RUNTIME}
    package = None
    reveal = None
    if op == "registration":
        added = [e for e in after["entries"] if e not in before["entries"]]
        require(len(added) == 1 and [e for e in after["entries"] if e not in added] == before["entries"], "Invalid registration delta")
        e = added[0]
        mutable |= {REGISTRY, "game/" + e["definition"], notice_path(e), rating.path(e["id"])}
        require(all(j["old"][n] is None for n in mutable - {REGISTRY, RUNTIME}), "Occupied registration target")
        require(j["new"][rating.path(e["id"])] is not None, "New registration requires difficulty 0.3")
        package, reveal = e["production"]["package"], "game/" + e["reveal"]
    elif op == "update":
        pairs = [(a, b) for a, b in zip(before["entries"], after["entries"]) if a != b]
        require(len(before["entries"]) == len(after["entries"]) and len(pairs) == 1, "Invalid update delta")
        a, e = pairs[0]
        require(all(a[k] == e[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")) and
                a["production"]["reveal_sha256"] == e["production"]["reveal_sha256"], "Update changes fixed identity/reveal")
        n = "game/" + e["definition"]
        old_def = rating.bytes_json(j["old"][n].encode(), 2 * 1024 * 1024)
        new_def = rating.bytes_json(j["new"][n].encode(), 2 * 1024 * 1024)
        require(old_def["id"] == new_def["id"] == e["id"] and new_def["revision"] > old_def["revision"], "Invalid update revision")
        mutable |= {REGISTRY, n, notice_path(e), rating.path(e["id"])}
        if rating.definition(j["old"][n].encode())[3] != rating.definition(j["new"][n].encode())[3]:
            require(j["new"][rating.path(e["id"])] is not None, "Changed logic requires difficulty 0.3")
        package = e["production"]["package"]
        require(package != a["production"]["package"], "Update reuses old package")
    else:
        require(before == after, "Difficulty operation changes production registry")
        if op == "adoption": mutable |= {rating.path(e["id"]) for e in before["entries"]} | report_names(j["report_run"])
        else: require(j["report_run"] is None, "Sync cannot adopt reports")
    require(changed <= mutable, "Unexpected transaction source mutation")
    if package:
        rating_name = rating.path(e["id"])
        prior = rating.bytes_json(j["old"][rating_name].encode()) if j["old"][rating_name] is not None else None
        current = rating.bytes_json(j["new"][rating_name].encode()) if j["new"][rating_name] is not None else None
        require(prior is None or current is not None, "Update cannot remove active difficulty")
        if current is not None and prior != current:
            require(current["rating_revision"] == (prior["rating_revision"] + 1 if prior else 1) and
                    current["adoption"]["previous_record_hash"] == (prior["record_hash"] if prior else None) and
                    current["adoption"]["report"] is None, "Invalid integration rating revision/provenance")
        require(package == "content/packages/" + e["id"] + "/" + e["production"]["revision"], "Invalid package target")
        require(all(n.startswith(package + "/") or n == reveal for n in j["additions"]), "Invalid package addition target")
        require(j["additions"].get(package + "/manifest.json") == e["production"]["package_sha256"], "Wrong package manifest binding")
        for n, h in (("runtime/" + e["definition"], e["production"]["definition_sha256"]),
                     ("runtime/" + e["reveal"], e["production"]["reveal_sha256"]),
                     ("runtime/" + notice_path(e).removeprefix("game/"), hashlib.sha256(j["new"][notice_path(e)].encode()).hexdigest())):
            require(j["additions"].get(package + "/" + n) == h, "Wrong package runtime binding")
        if reveal: require(j["additions"].get(reveal) == e["production"]["reveal_sha256"], "Wrong new reveal binding")
        require(not any(n == package or n.startswith(package + "/") for n in j["retained"]), "Addition overlaps retained package")
    else:
        require(not j["additions"], "Unexpected difficulty additions")
    return package


def validate_journal(root, j, *, before_write=False):
    exact_keys(j, {"format", "operation", "old", "new", "retained", "additions", "report_run"})
    require(j["operation"] in FORMATS and j["format"] == FORMATS[j["operation"]], "Unsupported catalog journal")
    for k in ("old", "new", "retained", "additions"): require(isinstance(j[k], dict), "Invalid journal map")
    require(all(v is None or isinstance(v, str) for side in ("old", "new") for v in j[side].values()), "Invalid journal text")
    for side in ("old", "new"):
        for n in (REGISTRY, RUNTIME, categories.PATH): require(isinstance(j[side].get(n), str), "Missing journal source")
    before, after = (rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
    names = text_names(before) | text_names(after) | report_names(j["report_run"])
    require(set(j["old"]) == set(j["new"]) == names, "Invalid journal target set")
    require(set(j["retained"]) == retained_names(root, before), "Invalid retained source set")
    for side, registry in (("old", before), ("new", after)):
        from .content_registry import validate
        validate(registry, rating.bytes_json(j[side][categories.PATH].encode(), 131072))
        require(j[side][REGISTRY].encode() == canonical_bytes(registry) + b"\n", "Noncanonical journal registry")
        expected = projection(j[side], registry)
        if side == "new" or j["operation"] != "sync":
            require(j[side][RUNTIME].encode() == expected, "Invalid journal projection")
    package = _delta(j, before, after)
    for n, h in {**j["retained"], **j["additions"]}.items(): relative(n); sha(h); safe(root, n)
    if j["report_run"] is not None:
        from .catalog_analysis import validate_report, markdown
        prefix = "content/difficulty/reports/" + j["report_run"] + "/report."
        report = validate_report(rating.bytes_json(j["new"][prefix + "json"].encode(), 16 * 1024 * 1024))
        require(report["run_id"] == j["report_run"] and j["new"][prefix + "md"] == markdown(report), "Conflicting journal report")
        require(j["operation"] == "adoption" and report["operation"]["phase"] == "adopted" and
                all(j["old"][n] is None for n in report_names(j["report_run"])), "Report is not a new adoption")
        require(all(hashlib.sha256(j["old"][n].encode()).hexdigest() == h for n,h in report["result"]["snapshot"].items()),
                "Wrong report snapshot")
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
            if row["current_source"] is not None:
                _, _, source, logic = rating.definition(j["old"]["game/" + entry["definition"]].encode())
                require(row["current_source"] == source and row["logic_binding"] == logic, "Wrong report definition binding")
            if row["status"] != "rated":
                require(prior == current, "Incomplete attempt changed active rating")
            else:
                require(current is not None and rating.project(current) == row["proposed"] and
                        current["rating"]["rating_hash"] == row["rating_hash"], "Wrong adopted report rating")
                if prior != current:
                    require(current["rating_revision"] == (prior["rating_revision"] + 1 if prior else 1) and
                            current["adoption"]["previous_record_hash"] == row["previous_record_hash"] and
                            current["adoption"]["report"] == {"run_id": report["run_id"], "result_hash": report["result_hash"]} and
                            rating.checked_from_active(current)["checked_hash"] == row["checked_hash"], "Wrong adopted report provenance")
    else:
        require(j["operation"] != "adoption", "Adoption requires a report")
    guard(root, j, old_only=before_write)
    # The rollback goal is checked in full before any real mutation. A sync may
    # have started with a stale projection; recovery directly restores current v3.
    old = deepcopy(j["old"])
    old[RUNTIME] = projection(old, before).decode()
    _stage_check(root, old, j["retained"])
    return package, old[RUNTIME]


def guard(root, j, *, old_only=False, journal_bytes=None):
    if journal_bytes is not None:
        require(read(root, LOCK) == journal_bytes, "Journal changed; preserve all transaction files")
    for n, old in j["old"].items():
        allowed = [old]
        if not old_only:
            allowed.append(j["new"][n])
            if n == RUNTIME and j["operation"] == "sync":
                registry = rating.bytes_json(j["old"][REGISTRY].encode(), 8 * 1024 * 1024)
                allowed.append(projection(j["old"], registry).decode())
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


def execute(root, j, additions=None, *, fail_step=None):
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
    from .content_registry import check_checkout
    root = root.resolve()
    raw = read(root, LOCK)
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
