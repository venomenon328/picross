"""Single authoring registry, deterministic runtime projection and atomic adoption."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile

from .authoring_package import ID, STEM, REVISION, relative, require, sha, file_hash, file_table
from .contract import canonical_bytes, exact_keys, load_json, integer
from . import categories
from . import catalog_difficulty
import time
import os

REGISTRY = "content/registry.json"
RUNTIME = "game/data/registry.json"
FORMAT = "picross-content-registry-v2"
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


def projection(registry, catalog):
    return {"format": "picross-runtime-registry-v3", "categories": categories.ordered(catalog), "entries": [
        {**{k: e[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")},
         "difficulty": catalog_difficulty.project(e["production"]["difficulty"])}
        for e in registry["entries"]]}


def validate(registry, catalog):
    categories.validate(catalog)
    exact_keys(registry, {"format", "entries"})
    require(registry["format"] == FORMAT and isinstance(registry["entries"], list) and len(registry["entries"]) <= 10000,
            "Unsupported registry")
    seen = {k: set() for k in ("id", "key", "save_slot", "definition", "reveal")}
    for e in registry["entries"]:
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
        categories.lookup(catalog, e["category_id"])
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
    require(registry["entries"] == sorted(registry["entries"], key=lambda e: e["id"]), "Registry entries must be sorted")
    return registry


def check_checkout(root, replay=False, *, check_projection=True):
    require(not (root / "content/.registration-pending.json").exists(), "Interrupted registration: recovery required")
    catalog = categories.load(root / categories.PATH)
    r = validate(load_json(root / REGISTRY), catalog)
    if check_projection:
        require((root / RUNTIME).read_bytes() == canonical_bytes(projection(r, catalog))+b"\n", "Runtime registry is stale")
    for e in r["entries"]:
        p = e["production"]
        require(not p["test_only"] or root.resolve() != ROOT.resolve(), "Test-only content cannot enter the real catalog")
        package = root / p["package"]
        require(file_hash(package / "manifest.json") == p["package_sha256"] and
                file_hash(root / "game" / e["definition"]) == p["definition_sha256"] and
                file_hash(root / "game" / e["reveal"]) == p["reveal_sha256"], "Registered content binding changed")
        # Also enforce the category binding without the expensive production replay.
        m = load_json(package / "manifest.json")
        from . import integrated_content
        if m.get("format") == integrated_content.FORMAT:
            integrated_content.check(root, e, m)
            continue  # Final integration is checked by runtime hashes, never by production replay.
        require(m.get("format") in ("picross-target-export-v1", "picross-target-export-v2", "picross-target-export-v3", "picross-target-export-v4"), "Unsupported registered export")
        if m["format"] in ("picross-target-export-v2", "picross-target-export-v3", "picross-target-export-v4"):
            require(m.get("category_id") == e["category_id"], "Registered category differs from export")
        if replay:
            from .target_adapter import verify_export
            m, report = verify_export(package)
            require(m["definition_id"] == e["id"] and m["save_slot"] == e["save_slot"] and
                    m["definition"] == "runtime/"+e["definition"] and m["reveal"] == "runtime/"+e["reveal"] and
                    report["package_revision"] == p["revision"] and
                    all(report[k] == p[k] for k in ("width","height","mode","difficulty")), "Registered package identity differs")
        notice = str(Path(e["reveal"]).with_suffix(".txt")).replace("\\", "/")
        require(file_hash(root / "game" / notice) == file_hash(package / "runtime" / notice), "Player notice differs")
    return r


def sync_runtime(root):
    """Explicit metadata projection; never repairs or edits the authoritative data."""
    root = root.resolve()
    before = {REGISTRY: (root / REGISTRY).read_bytes(), categories.PATH: categories.source_bytes(root / categories.PATH)}
    registry = check_checkout(root, replay=True, check_projection=False)
    catalog = categories.load(root / categories.PATH)
    require(all((root / name).read_bytes() == data for name, data in before.items()),
            "Registry/categories changed during projection; retry")
    require(not (root / "content/.registration-pending.json").exists(), "Interrupted registration: recovery required")
    atomic_bytes(root / RUNTIME, canonical_bytes(projection(registry, catalog))+b"\n")
    check_checkout(root)
    return {"status": "projected", "entries": len(registry["entries"]), "categories": len(catalog["categories"])}


def export_entry(export_dir, m, report, category):
    return {"id": m["definition_id"], "key": m["definition_id"], "save_slot": m["save_slot"],
         "definition": m["definition"].removeprefix("runtime/"), "reveal": m["reveal"].removeprefix("runtime/"), "visible": True,
         "category_id": category["id"],
         "production": {"package": "content/packages/" + m["definition_id"] + "/" + m["package_revision"],
             "package_sha256": file_hash(export_dir / "manifest.json"),
             "revision": m["package_revision"], "width": report["width"], "height": report["height"], "mode": report["mode"],
             "difficulty": report["difficulty"], "status": "registered", "blockers": [], "test_only": m["test_only"],
             "definition_sha256": m["files"][m["definition"]], "reveal_sha256": m["files"][m["reveal"]]}}


def registration(export_dir, root, *, apply=False, fail_step=None):
    from .target_adapter import verify_export, FORMAT as EXPORT_FORMAT, MANUAL_FORMAT, PAIRED_FORMAT
    root = root.resolve()
    catalog_bytes = categories.source_bytes(root / categories.PATH)
    catalog = categories.load(root / categories.PATH)
    require(catalog_bytes == categories.source_bytes(root / categories.PATH), "Categories changed during planning; retry")
    registry = check_checkout(root)
    m, report = verify_export(export_dir)
    require(m["format"] in (EXPORT_FORMAT, MANUAL_FORMAT, PAIRED_FORMAT), "Category-less legacy export: create a new categorized export from the unchanged approved input")
    category = categories.lookup(catalog, m["category_id"])
    require(not m["test_only"] or root != ROOT.resolve(), "Test-only fixtures cannot be registered in the real repository")
    package_rel = "content/packages/" + m["definition_id"] + "/" + m["package_revision"]
    e = export_entry(export_dir, m, report, category)
    existing = next((item for item in registry["entries"] if item["id"].casefold() == e["id"].casefold()), None)
    if existing is not None:
        from . import integrated_content
        retained = load_json(root / existing["production"]["package"] / "manifest.json")
        if retained.get("format") == integrated_content.FORMAT:
            require(retained["entry"] == e, "Occupied production ID/revision: update is outside ZA-1")
            return {"status": "no-op", "registered": True, "id": e["id"], "category": category, "changes": []}
        require(existing == e, "Occupied production ID/revision: update is outside ZA-1")
        check_checkout(root, replay=True)
        require((root / package_rel / "manifest.json").read_bytes() == (export_dir / "manifest.json").read_bytes(), "Different repeated input")
        require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed during planning; retry")
        return {"status": "no-op", "registered": True, "id": e["id"], "category": category, "changes": []}
    new = deepcopy(registry)
    new["entries"].append(e)
    new["entries"].sort(key=lambda item: item["id"])
    validate(new, catalog)
    notice = str(Path(e["reveal"]).with_suffix(".txt")).replace("\\", "/")
    targets = ["game/" + e["definition"], "game/" + e["reveal"], "game/"+notice, package_rel]
    # Preflight ALL target components using Windows semantics on every host.
    for name in targets:
        current = root
        for part in relative(name).split("/"):
            if current.exists():
                matches = [p for p in current.iterdir() if p.name.casefold() == part.casefold()]
                require(not matches or len(matches) == 1 and matches[0].name == part and matches[0].is_dir() and not matches[0].is_symlink() and
                        not (getattr(matches[0].lstat(),"st_file_attributes",0) & 1024),
                        "Target path exists/collides: " + name)
            current /= part
        require(not current.exists(), "Target already exists: " + name)
    plan = {"status": "planned", "registered": False, "id": e["id"], "category": category, "changes": [
        {"path": n, "operation": "add"} for n in targets] + [{"path": REGISTRY, "operation": "replace"},
        {"path": RUNTIME, "operation": "replace"}], "before": registry, "after": new}
    if not apply:
        require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed during planning; retry")
        return plan
    lock = root / "content/.registration-pending.json"
    # Exclusive lock plus recoverable journal. Runtime projection is published LAST.
    old = {name: (root / name).read_bytes() for name in (REGISTRY, RUNTIME)}
    expected = {targets[0]: m["files"][m["definition"]], targets[1]: m["files"][m["reveal"]], targets[2]: m["files"]["runtime/"+notice],
                **{package_rel+"/"+n: file_hash(p) for n, p in file_table(export_dir, time.monotonic()+300).items()}}
    journal = {"format": JOURNAL, "targets": targets, "files": expected,
               "categories": catalog_bytes.decode("utf-8"),
               "old": {name: data.decode("utf-8") for name, data in old.items()},
               "new": {REGISTRY: (canonical_bytes(new)+b"\n").decode(), RUNTIME: (canonical_bytes(projection(new, catalog))+b"\n").decode()}}
    require(old[REGISTRY] == canonical_bytes(registry)+b"\n" and old[RUNTIME] == canonical_bytes(projection(registry, catalog))+b"\n" and
            categories.source_bytes(root / categories.PATH) == catalog_bytes, "Registry/categories changed during planning; retry")
    with lock.open("x", encoding="utf-8") as stream:
        json.dump(journal, stream)
        stream.flush()
        os.fsync(stream.fileno())
    created = []
    try:
        require(all((root / name).read_bytes() == data for name, data in old.items()) and
                categories.source_bytes(root / categories.PATH) == catalog_bytes,
                "Registry changed during planning; retry")
        require(all(not (root/n).exists() for n in targets), "Target appeared during planning; retry")
        with tempfile.TemporaryDirectory(prefix="za1-register-", dir=root / "content") as temp:
            stage = Path(temp)
            staged_package = stage / "package"
            shutil.copytree(export_dir, staged_package)
            verify_export(staged_package)
            require(file_hash(staged_package / "manifest.json") == e["production"]["package_sha256"], "Export changed during planning; retry")
            require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed during staging; retry")
            for target, source in ((targets[0], staged_package / m["definition"]), (targets[1], staged_package / m["reveal"]),
                                   (targets[2], staged_package / ("runtime/"+notice)),
                                   (package_rel, staged_package)):
                destination = root / target
                destination.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    destination.mkdir()
                    created.append(destination)
                    shutil.copytree(source, destination, dirs_exist_ok=True)
                else:
                    with destination.open("xb") as stream:
                        stream.write(source.read_bytes())
                    created.append(destination)
                if fail_step == "crash":
                    # Test-only injection models a killed process with journal intact.
                    raise InterruptedError("Injected hard interruption")
                if fail_step == "files":
                    raise OSError("Injected registration interruption")
            verify_export(root / package_rel)
            require(all(file_hash(root/n) == expected[n] for n in targets[:3]), "Written runtime files differ")
            require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed before publication; retry")
            atomic_bytes(root / REGISTRY, canonical_bytes(new)+b"\n")
            if fail_step == "crash-index":
                raise InterruptedError("Injected hard interruption after index")
            if fail_step == "index":
                raise OSError("Injected registration interruption")
            require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed during publication; retry")
            atomic_bytes(root / RUNTIME, canonical_bytes(projection(new, catalog))+b"\n")
            require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed during publication; retry")
            if fail_step == "crash-runtime":
                raise InterruptedError("Injected hard interruption after projection")
    except InterruptedError:
        raise
    except BaseException:
        for name, data in old.items():
            atomic_bytes(root / name,data)
        for path in reversed(created):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        lock.unlink()
        raise
    lock.unlink()
    check_checkout(root, replay=True)
    return {**plan, "status": "registered", "registered": True}


def recovery_projection(journal, before, after, catalog):
    """Accept exactly one canonical journal generation; return the current goal."""
    versions = []
    for side, registry in (("old", before), ("new", after)):
        require(journal[side][REGISTRY].encode() == canonical_bytes(registry)+b"\n",
                "Noncanonical journal registry")
        current = projection(registry, catalog)  # Also validates present difficulty.
        legacy = deepcopy(current)
        legacy["format"] = "picross-runtime-registry-v2"
        for entry in legacy["entries"]:
            del entry["difficulty"]
        raw = journal[side][RUNTIME].encode()
        require(raw in (canonical_bytes(legacy)+b"\n", canonical_bytes(current)+b"\n"),
                "Invalid journal projections")
        versions.append(json.loads(raw)["format"])
    require(versions[0] == versions[1], "Mixed journal projection versions")
    return canonical_bytes(projection(before, catalog))+b"\n"


def recovery_target(root, journal, registry, runtime):
    """Validate the entire rollback view without writing into the checkout.

    Only runtime bindings and retained manifests/notices are copied. No solver,
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
            names.add(p["package"]+"/runtime/"+notice.removeprefix("game/"))
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


def recover(root):
    """Explicit rollback after process death; preflight every byte before mutation."""
    root = root.resolve()
    from .content_update import path_in
    lock = path_in(root, "content/.registration-pending.json")
    j = load_json(lock, 24 * 1024 * 1024)
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
    for name, text in j["old"].items():
        atomic_bytes(root/name, runtime if name == RUNTIME else text.encode("utf-8"))
    for path in reversed(existing):
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    lock.unlink()
    check_checkout(root)
    return {"status": "rolled-back", "registered": False}
