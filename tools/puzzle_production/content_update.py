"""Explicit raster replacement: fixed identity/reveal, increasing runtime revision.

Ordinary registration still rejects occupied IDs. No package code is executed,
no old production package or user save is changed. A journal preserves exact
text bytes and binds the new package for rollback after an interrupted update.
"""
import hashlib
import json
from pathlib import Path
import shutil
import time

from .authoring_package import file_hash, file_table, relative, require, sha
from .contract import exact_keys, integer, load_json
from . import categories
from .content_registry import (REGISTRY, RUNTIME, atomic_bytes, check_checkout,
                               validate, recovery_projection, recovery_target)

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


def update(export_dir, checkout, expected_definition_sha256, *, apply=False, fail_step=None,
           difficulty=None, rebind_difficulty=False):
    from .catalog_integration import integrate
    return integrate(export_dir, checkout, expected_definition_sha256=expected_definition_sha256,
                     apply=apply, fail_step=fail_step, difficulty=difficulty, rebind_difficulty=rebind_difficulty)


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
    from .content_registry import reject_unbound_ratings
    reject_unbound_ratings(root, before, after)
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
    runtime = recovery_projection(j, before, after, catalog)
    integer(old_def["revision"],1,1000000,"old runtime revision")
    integer(new_def["revision"],1,1000000,"new runtime revision")
    require(old_def["id"] == new_def["id"] == old["id"] and new_def["revision"] > old_def["revision"],"Invalid update revision delta")
    for side,registry in (("old",before),("new",after)):
        entry = old if side == "old" else new
        require(hashlib.sha256(j[side][definition_name].encode("utf-8")).hexdigest() == entry["production"]["definition_sha256"],"Invalid update definition backup")
    expected_package = "content/packages/"+new["id"]+"/"+new["production"]["revision"]
    require(j["package"] == new["production"]["package"] == expected_package and
            j["package"] != old["production"]["package"],"Invalid update package target")
    package_path = path_in(root,j["package"])
    for name in names:
        path = path_in(root,name)
        allowed = [j[side][name].encode("utf-8") for side in ("old", "new")]
        if name == RUNTIME:
            allowed.append(runtime)
        require(path.is_file() and path.read_bytes() in allowed,
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
    retained = recovery_target(root, j, before, runtime)
    require(not any(n == j["package"] or n.startswith(j["package"]+"/") for n in retained),
            "Recovery package overlaps retained content")
    # Preflight completed before any rollback mutation. Only the new package is
    # removed; old packages, reveals and every user save remain untouched.
    for name in (definition_name,notice_name,REGISTRY,RUNTIME):
        atomic_bytes(root/name, runtime if name == RUNTIME else j["old"][name].encode("utf-8"))
    if package_path.exists():
        require(package_path.resolve().is_relative_to(root/"content/packages") and not package_path.is_symlink(),"Unsafe update cleanup")
        shutil.rmtree(package_path)
    lock.unlink()
    check_checkout(root)
    return {"status":"rolled-back","registered":False}
