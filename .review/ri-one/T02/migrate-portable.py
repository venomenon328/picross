"""Temporary RI-ONE/T02 transition; never installed as a product importer."""
import copy, hashlib, json, pathlib, shutil, sys
ROOT = pathlib.Path(sys.argv[3]).resolve()
sys.path.insert(0, str(pathlib.Path(sys.argv[4]).resolve()))
from tools.puzzle_production import current_content as current
from tools.puzzle_production.contract import digest

def read(root, name):
    return (root/name).read_bytes()

def obj(root, name):
    return json.loads(read(root, name))

def inventory(root, registry):
    runtime_raw = read(root, current.RUNTIME)
    runtime = json.loads(runtime_raw)
    rows = {r["id"]: r for r in runtime["entries"]}
    names = {current.RUNTIME, "content/authoring/index.json", "content/categories.json", "content/difficulty-method.json", "game/data/background-capability.json"}
    values = []
    for entry in registry["entries"]:
        identifier = entry["id"]
        row = rows[identifier]
        names.update(("game/"+entry["definition"], "game/"+row["reveal"], current.notice_path(entry),
                      "content/difficulty/"+identifier+"/rating.json", "content/added/"+identifier+".json"))
        if row["background"]["asset"]:
            names.update(("game/"+row["background"]["asset"]["file"], "game/art/backgrounds/"+identifier+".txt"))
        values.append({"entry": {k:v for k,v in entry.items() if k != "production"},
                       "mode": entry.get("mode", entry.get("production", {}).get("mode"))})
    # Normalize the pre-transition entry representation for semantic comparison.
    for v in values: v["entry"]["mode"] = v["mode"]
    active={e.get("production",{}).get("package") for e in registry["entries"]}
    active_ids={e["id"] for e in registry["entries"]}
    for child in (root/"content/packages").glob("*/*"):
        if child.parent.name not in active_ids and child.is_dir():
            # Only nonintegrated work is retained here; no ZIP is unpacked.
            names.update(p.relative_to(root).as_posix() for p in child.rglob("*") if p.is_file())
    for tree in ("content/authoring",):
        names.update(p.relative_to(root).as_posix() for p in (root/tree).rglob("*") if p.is_file())
    files = {name: {"sha256": hashlib.sha256(read(root,name)).hexdigest(), "bytes": len(read(root,name))}
             for name in sorted(names) if (root/name).is_file()}
    return {"entries": values, "metadata": registry["metadata"], "runtime": runtime, "files": files}

def migrate(root):
    root = root.resolve()
    assert root.is_relative_to(ROOT) and root != ROOT
    registry = obj(root, current.REGISTRY)
    if registry["format"] == current.FORMAT:
        from tools.puzzle_production.content_registry import check_checkout
        check_checkout(root)
        return {"status": "no-op", "entries": len(registry["entries"])}
    assert registry["format"] == "picross-content-registry-v4"
    assert not (root/"content/.registration-pending.json").exists()
    before = inventory(root, registry)
    value = copy.deepcopy(registry)
    runtime = {r["id"]: r for r in before["runtime"]["entries"]}
    changes, remove = {}, []
    notices = []
    for entry in value["entries"]:
        production = entry.pop("production")
        entry["mode"] = production["mode"]
        raw = read(root, "game/"+entry["definition"])
        assert hashlib.sha256(raw).hexdigest() == production["definition_sha256"]
        row = runtime[entry["id"]]
        for kind in ("reveal", "background"):
            name = current.source_path(entry["id"], kind)
            old = obj(root,name) if (root/name).exists() else None
            if old and "current" in old:
                effective = old["current"]
                revision = old["record_revision"]
            elif kind == "background":
                assert old["format"] == "picross-catalog-background-v1"
                effective = {"status": row["background"]["status"], "image_revision": row["background"]["image_revision"],
                             "asset": old["asset"]}
                revision = 1
                if old["asset"]:
                    notice_name = "game/art/backgrounds/"+entry["id"]+".txt"
                    notice = read(root, notice_name).decode()
                    for field in ("author","source","usage_basis"):
                        assert old["provenance"][field] in notice, (entry["id"],field)
                    if old["provenance"].get("attribution"):
                        assert old["provenance"]["attribution"] in notice
                    notices.append({"id": entry["id"], "notice": notice_name, "rights": "current notice contains all required rights"})
            else:
                assert old is None
                asset_name = "game/"+row["reveal"]
                asset = read(root,asset_name)
                assert hashlib.sha256(asset).hexdigest() == production["reveal_sha256"]
                effective = {"image_revision": 1, "asset": current.ref(asset_name,asset)}
                revision = 1
            record = current.source(entry,raw,effective,kind,record_revision=revision)
            changes[name] = current.encoded(record)
            if kind == "background":
                source = next(r for r in value["backgrounds"] if r["id"] == entry["id"])
                source["source"] = current.ref(name,changes[name])
        package = (root/production["package"]).resolve()
        assert package.is_relative_to(root/"content/packages"/entry["id"])
        manifest = obj(root, production["package"]+"/manifest.json")
        assert manifest["format"] in ("picross-integrated-content-v1","picross-integrated-content-v2","picross-integrated-content-v4")
        files = [p for p in package.rglob("*") if p.is_file()]
        assert files == [package/"manifest.json"], (package,files)
        assert hashlib.sha256(read(root,production["package"]+"/manifest.json")).hexdigest() == production["package_sha256"]
        remove.extend(files)
    value["format"] = current.FORMAT
    current.validate(value,obj(root,"content/categories.json"))
    changes[current.REGISTRY] = current.encoded(value)
    for name, raw in changes.items():
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        (root/name).write_bytes(raw)
    after = inventory(root,value)
    assert after == before, "Current semantic data or live bytes changed"
    projected = {"format": current.RUNTIME_FORMAT, "categories": before["runtime"]["categories"],
                 "entries":[current.runtime_row(current.selected(root,value,e["id"])) for e in value["entries"]]}
    assert current.encoded(projected) == read(root,current.RUNTIME), "Runtime projection changed"
    for path in remove:
        assert path.resolve().is_relative_to(root/"content/packages")
        path.unlink()
    return {"status":"migrated", "entries":len(value["entries"]), "preserved":before,
            "changed": {n:hashlib.sha256(v).hexdigest() for n,v in changes.items()},
            "removed":[p.relative_to(root).as_posix() for p in remove], "rights":notices}

if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1])
    result = migrate(root)
    destination = pathlib.Path(sys.argv[2])
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"entries":result["entries"],"report":str(destination)}))
