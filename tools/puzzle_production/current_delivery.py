"""Selected committed delivery views for completion and main comparison."""
from . import current_content as content, catalog_io as io, catalog_rating as rating, catalog_added as added
from .authoring_package import require


def snapshot(read, identifier):
    """read(name, limit, missing=False) supplies local or Git bytes; no archives."""
    value = io.json_bytes(read(content.REGISTRY,8*1024*1024),8*1024*1024)
    runtime = io.json_bytes(read(content.RUNTIME,content.RUNTIME_LIMIT),content.RUNTIME_LIMIT)
    require(runtime["format"] == content.RUNTIME_FORMAT,"Current runtime required")
    entries=[e for e in value["entries"] if e["id"]==identifier]
    rows=[e for e in runtime["entries"] if e["id"]==identifier]
    metadata=[e for e in value["metadata"] if e["id"]==identifier]
    require(len(entries)==len(rows)==len(metadata)==1,"Selected delivery missing or ambiguous")
    entry,row,meta=entries[0],rows[0],metadata[0]
    fixed={k:entry[k] for k in ("id","key","save_slot","definition","reveal","visible","category_id")}
    # A branch's extra, obsolete provenance fields are not authorities. Compare
    # the selected current paths/live bytes, including already closed v4 fruit.
    for key in ("id","key","save_slot","definition","visible"):
        require(entry[key]==row[key],"Current delivery identity differs")
    require(meta["name"]==row["name"] and meta["category_id"]==row["category_id"],"Current metadata differs")
    for path,prefix in ((entry["definition"],"data/content/"),(row["reveal"],"art/content/")):
        content.relative(path);require(path.startswith(prefix),"Foreign delivery resource")
    names={"game/"+entry["definition"],"game/"+row["reveal"],content.notice_path(entry),
           rating.path(identifier),added.path(identifier)}
    source_name = content.source_path(identifier, "reveal")
    source_raw = read(source_name, 1024*1024)
    source = content.validate_source(io.json_bytes(source_raw, 1024*1024), entry)
    require(source["current"]["asset"]["file"] == "game/"+row["reveal"] and
            content.catalog_profiles.project(source["catalog"]) == row["catalog_reveal"],
            "Current delivery catalog projection differs")
    expected = [source["binding"]["identity"]["definition"], source["current"]["asset"]]
    expected.extend(profile["asset"] for profile in source["catalog"]["profiles"])
    names.update(asset["file"] for asset in expected)
    optional=set()
    if row["background"]["asset"]:
        asset=row["background"]["asset"]
        require(asset["file"]=="art/backgrounds/"+identifier+".png","Foreign background asset")
        names.add("game/"+asset["file"])
        optional.add("game/art/backgrounds/"+identifier+".txt")
    files={}
    for name in sorted(names | optional):
        raw=read(name,content.LIMIT,missing=name in optional)
        # For optional older notices, absence is compared just as strictly as bytes.
        files[name]=content.ref(name,raw) if raw is not None else None
    files[source_name] = content.ref(source_name, source_raw)
    require(all(files[asset["file"]] == asset for asset in expected), "Current delivery asset binding differs")
    return {"entry":fixed,"mode":entry.get("mode"),"metadata":meta,"runtime":row,"files":files}


def same(left,right):
    return (all(left[k]==right[k] for k in ("entry","metadata","runtime","files")) and
            (left["mode"] is None or right["mode"] is None or left["mode"]==right["mode"]))
