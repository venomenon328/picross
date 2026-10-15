"""Explicit raster replacement: fixed identity/reveal, increasing runtime revision.

Ordinary registration still rejects occupied IDs. No package code is executed,
no old production package or user save is changed. A journal preserves exact
text bytes and binds the new package for rollback after an interrupted update.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time

from .authoring_package import file_hash, file_table, relative, require, sha
from .contract import canonical_bytes, exact_keys, integer, load_json
from . import categories
from .content_registry import (ROOT, REGISTRY, RUNTIME, atomic_bytes, check_checkout,
                               export_entry, projection, validate)

FORMAT = "picross-content-update-journal-v1"
JOURNAL_LIMIT = 24 * 1024 * 1024
LOCK = "content/.registration-pending.json"


def path_in(root, name):
    """Reject aliases, reparse points and nonregular parent components on Windows too."""
    current = root
    parts = relative(name).split("/")
    for i, part in enumerate(parts):
        if current.exists():
            matches = [p for p in current.iterdir() if p.name.casefold() == part.casefold()]
            require(not matches or len(matches) == 1 and matches[0].name == part,
                    "Update path case collision: " + name)
        current /= part
        require(not current.is_symlink(), "Unsafe update path: " + name)
        if current.exists():
            require(not (getattr(current.lstat(), "st_file_attributes", 0) & 1024), "Unsafe update path: " + name)
        require(not current.exists() or (current.is_dir() if i < len(parts)-1 else
                current.is_dir() or current.is_file()), "Unsafe update component: " + name)
    require(current.resolve().is_relative_to(root), "Update path escapes checkout")
    return current


def notice_path(entry):
    return "game/" + str(Path(entry["reveal"]).with_suffix(".txt")).replace("\\", "/")


def update(export_dir, checkout, expected_definition_sha256, *, apply=False, fail_step=None):
    from .target_adapter import verify_export, FORMAT as EXPORT_FORMAT, MANUAL_FORMAT, PAIRED_FORMAT
    root = checkout.resolve()
    sha(expected_definition_sha256)
    catalog_bytes = categories.source_bytes(root / categories.PATH)
    catalog = categories.load(root / categories.PATH)
    registry = check_checkout(root)
    m, report = verify_export(export_dir)
    require(m["format"] in (EXPORT_FORMAT, MANUAL_FORMAT, PAIRED_FORMAT), "Update needs categorized export")
    require(not m["test_only"] or root != ROOT.resolve(), "Test-only content cannot update the real catalog")
    e = export_entry(export_dir, m, report, categories.lookup(catalog, m["category_id"]))
    existing = next((v for v in registry["entries"] if v["id"] == e["id"]), None)
    require(existing is not None, "Update requires an existing production ID")
    definition_name = "game/" + existing["definition"]
    definition_path = path_in(root, definition_name)
    require(file_hash(definition_path) == expected_definition_sha256, "Stale expected definition hash")
    require(all(e[k] == existing[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")),
            "Raster update must retain identity, paths, visibility, category and save slot")
    require(e["production"]["reveal_sha256"] == existing["production"]["reveal_sha256"],
            "Raster update must retain the approved reveal bytes")
    if e == existing:
        require((root / e["production"]["package"] / "manifest.json").read_bytes() == (export_dir / "manifest.json").read_bytes(),
                "Different repeated update input")
        return {"status": "no-op", "registered": True, "id": e["id"], "changes": []}
    before_definition = load_json(definition_path)
    require(m["runtime_revision"] > before_definition["revision"], "Update requires a higher runtime revision")
    package_name = e["production"]["package"]
    package_path = path_in(root, package_name)
    require(package_name != existing["production"]["package"] and not package_path.exists(), "Update package revision already exists")
    notice_name = notice_path(e)
    path_in(root, notice_name)
    path_in(root, "game/" + existing["reveal"])
    for name in (REGISTRY, RUNTIME, LOCK): path_in(root, name)
    new = deepcopy(registry)
    new["entries"][new["entries"].index(existing)] = e
    validate(new, catalog)
    old_bytes = {name: (root / name).read_bytes() for name in (REGISTRY, RUNTIME, definition_name, notice_name)}
    new_bytes = {REGISTRY: canonical_bytes(new)+b"\n", RUNTIME: canonical_bytes(projection(new,catalog))+b"\n",
                 definition_name: (export_dir / m["definition"]).read_bytes(),
                 notice_name: (export_dir / ("runtime/"+notice_name.removeprefix("game/"))).read_bytes()}
    require(hashlib.sha256(new_bytes[definition_name]).hexdigest() == m["files"][m["definition"]],
            "Export definition changed during planning")
    plan = {"status": "planned-update", "registered": False, "id": e["id"],
            "expected_definition_sha256": expected_definition_sha256,
            "previous_runtime_revision": before_definition["revision"], "runtime_revision": m["runtime_revision"],
            "update_module_sha256": file_hash(Path(__file__)),
            "changes": [{"path": package_name, "operation": "add"}] +
                [{"path": name, "operation": "replace" if old_bytes[name] != data else "unchanged"}
                 for name,data in new_bytes.items()], "before": registry, "after": new,
            "old_package_retained": existing["production"]["package"], "user_saves_modified": False}
    require(categories.source_bytes(root / categories.PATH) == catalog_bytes, "Categories changed during update planning")
    if not apply: return plan
    with tempfile.TemporaryDirectory(prefix="za1-update-",dir=root/"content") as temp:
        stage = Path(temp)/"package"
        shutil.copytree(export_dir,stage)
        verify_export(stage)
        files = {n:file_hash(p) for n,p in file_table(stage,time.monotonic()+300).items()}
        require(files.get("manifest.json") == e["production"]["package_sha256"], "Export changed during update staging")
        require(all((root/name).read_bytes() == data for name,data in old_bytes.items()) and
                categories.source_bytes(root/categories.PATH) == catalog_bytes and not package_path.exists(),
                "Checkout changed during update staging; retry")
        journal = {"format":FORMAT,"package":package_name,"files":files,"categories":catalog_bytes.decode("utf-8"),
                   "old":{n:b.decode("utf-8") for n,b in old_bytes.items()},
                   "new":{n:b.decode("utf-8") for n,b in new_bytes.items()}}
        raw = canonical_bytes(journal)+b"\n"
        require(len(raw) <= JOURNAL_LIMIT,"Update journal exceeds resource limit")
        lock = root/LOCK
        with lock.open("xb") as stream:
            stream.write(raw);stream.flush()
            import os
            os.fsync(stream.fileno())
        try:
            require(all((root/name).read_bytes() == data for name,data in old_bytes.items()) and
                    categories.source_bytes(root/categories.PATH) == catalog_bytes,
                    "Checkout changed before update; preserve journal")
            package_path.mkdir(parents=True)
            shutil.copytree(stage,package_path,dirs_exist_ok=True)
            require({n:file_hash(p) for n,p in file_table(package_path,time.monotonic()+300).items()} == files,
                    "Written update package differs")
            if fail_step == "crash-package": raise InterruptedError("Injected update crash after package")
            for name in (definition_name,notice_name,REGISTRY,RUNTIME):
                require(categories.source_bytes(root/categories.PATH) == catalog_bytes,"Categories changed during update")
                require((root/name).read_bytes() == old_bytes[name],"Update target changed during publication")
                atomic_bytes(root/name,new_bytes[name])
                if fail_step == "crash-"+name: raise InterruptedError("Injected update crash: "+name)
                if fail_step == name: raise OSError("Injected update failure: "+name)
            # Internal final binding check; do not re-certify unrelated puzzles.
            lock.unlink()
            try:
                check_checkout(root)
            except BaseException:
                lock.write_bytes(raw)
                raise
        except InterruptedError:
            raise
        except BaseException:
            recover_update(root)
            raise
    return {**plan,"status":"updated","registered":True}


def recover_update(checkout):
    root = checkout.resolve()
    lock = path_in(root,LOCK)
    j = exact_keys(load_json(lock,JOURNAL_LIMIT),{"format","package","files","categories","old","new"})
    require(j["format"] == FORMAT and isinstance(j["files"],dict) and isinstance(j["categories"],str) and
            isinstance(j["old"],dict) and isinstance(j["new"],dict),"Invalid update journal")
    require(categories.source_bytes(root/categories.PATH) == j["categories"].encode("utf-8"),"Categories changed since interrupted update")
    catalog = categories.load(root/categories.PATH)
    before = validate(json.loads(j["old"][REGISTRY]),catalog)
    after = validate(json.loads(j["new"][REGISTRY]),catalog)
    changed = [(a,b) for a,b in zip(before["entries"],after["entries"]) if a != b]
    require(len(before["entries"]) == len(after["entries"]) and len(changed) == 1,"Invalid update registry delta")
    old,new = changed[0]
    require(all(old[k] == new[k] for k in ("id","key","save_slot","definition","reveal","visible","category_id")) and
            old["production"]["reveal_sha256"] == new["production"]["reveal_sha256"],"Update journal changes fixed identity/reveal")
    definition_name,notice_name = "game/"+old["definition"],notice_path(old)
    names = {REGISTRY,RUNTIME,definition_name,notice_name}
    require(set(j["old"]) == set(j["new"]) == names and
            all(isinstance(v,str) for side in ("old","new") for v in j[side].values()),"Invalid update journal text targets")
    old_def,new_def = (json.loads(j[side][definition_name]) for side in ("old","new"))
    integer(old_def["revision"],1,1000000,"old runtime revision")
    integer(new_def["revision"],1,1000000,"new runtime revision")
    require(old_def["id"] == new_def["id"] == old["id"] and new_def["revision"] > old_def["revision"],"Invalid update revision delta")
    for side,registry in (("old",before),("new",after)):
        require(j[side][RUNTIME].encode("utf-8") == canonical_bytes(projection(registry,catalog))+b"\n","Invalid update runtime projection")
        entry = old if side == "old" else new
        require(hashlib.sha256(j[side][definition_name].encode("utf-8")).hexdigest() == entry["production"]["definition_sha256"],"Invalid update definition backup")
    expected_package = "content/packages/"+new["id"]+"/"+new["production"]["revision"]
    require(j["package"] == new["production"]["package"] == expected_package and
            j["package"] != old["production"]["package"],"Invalid update package target")
    package_path = path_in(root,j["package"])
    for name in names:
        path = path_in(root,name)
        require(path.is_file() and path.read_bytes() in (j["old"][name].encode("utf-8"),j["new"][name].encode("utf-8")),
                "Update target changed; preserve journal for manual review")
    for name,value in j["files"].items(): relative(name);sha(value)
    require(j["files"].get("manifest.json") == new["production"]["package_sha256"],"Invalid update package binding")
    previous_manifest = path_in(root,old["production"]["package"]+"/manifest.json")
    require(file_hash(previous_manifest) == old["production"]["package_sha256"],"Previous package changed during update")
    previous = load_json(previous_manifest)
    notice_key = "runtime/"+notice_name.removeprefix("game/")
    previous_notice = (previous.get("notice_sha256") if previous.get("format") == "picross-integrated-content-v1"
                       else previous.get("files",{}).get(notice_key))
    require(hashlib.sha256(j["old"][notice_name].encode("utf-8")).hexdigest() == sha(previous_notice) and
            hashlib.sha256(j["new"][notice_name].encode("utf-8")).hexdigest() == j["files"].get(notice_key),
            "Invalid update notice backup")
    require(j["files"].get("runtime/"+new["definition"]) == new["production"]["definition_sha256"] and
            j["files"].get("runtime/"+new["reveal"]) == new["production"]["reveal_sha256"],
            "Invalid update runtime package bindings")
    if package_path.exists():
        present = file_table(package_path,time.monotonic()+300)
        require(all(name in j["files"] and file_hash(p) == j["files"][name] for name,p in present.items()),
                "Update package changed; preserve journal for manual review")
    # Preflight completed before any rollback mutation. Only the new package is
    # removed; old packages, reveals and every user save remain untouched.
    for name in (definition_name,notice_name,REGISTRY,RUNTIME): atomic_bytes(root/name,j["old"][name].encode("utf-8"))
    if package_path.exists():
        require(package_path.resolve().is_relative_to(root/"content/packages") and not package_path.is_symlink(),"Unsafe update cleanup")
        shutil.rmtree(package_path)
    lock.unlink()
    check_checkout(root)
    return {"status":"rolled-back","registered":False}
