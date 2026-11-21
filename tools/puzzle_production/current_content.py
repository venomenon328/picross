"""Current catalog records. No production packages or historical receipts."""
from copy import deepcopy
from pathlib import Path
from . import catalog_profiles
from . import catalog_io as io, categories, catalog_rating as rating, catalog_added as added
from .authoring_package import ID, STEM, require, relative, sha
from .contract import canonical_bytes, digest, exact_keys, integer

FORMAT = "picross-content-registry-v5"
REVEAL = "picross-catalog-reveal-v6"
BACKGROUND = "picross-catalog-background-v7"
REGISTRY = "content/registry.json"
RUNTIME = "game/data/registry.json"
RUNTIME_FORMAT = "picross-runtime-registry-v9"
RUNTIME_LIMIT = 16*1024*1024
LIMIT = 64*1024*1024
ENTRY_FIELDS = {"id", "key", "save_slot", "definition", "reveal", "visible", "mode", "category_id"}


def encoded(value):
    return canonical_bytes(value) + b"\n"


def ref(name, raw):
    return {"file": name, "bytes": len(raw), "sha256": io.checksum(raw)}


def reference(value, *, name=None, limit=LIMIT):
    exact_keys(value, {"file", "bytes", "sha256"})
    relative(value["file"]); sha(value["sha256"])
    integer(value["bytes"], 1, limit, "file bytes")
    require(name is None or name == value["file"], "Unexpected current path")
    return value


def bound(root, value, *, limit=LIMIT):
    reference(value, limit=limit)
    raw = io.read(root, value["file"], limit)
    require(ref(value["file"], raw) == value, "Changed input: " + value["file"])
    return raw


def entries(values, catalog=None):
    require(isinstance(values, list) and len(values) <= 10000, "Invalid entries")
    seen = {k: set() for k in ("id", "key", "save_slot", "definition", "reveal")}
    for entry in values:
        exact_keys(entry, ENTRY_FIELDS)
        require(isinstance(entry["id"], str) and ID.fullmatch(entry["id"]) and
                entry["key"] == entry["id"], "Invalid current identity")
        require(isinstance(entry["save_slot"], str) and STEM.fullmatch(entry["save_slot"]), "Invalid save slot")
        relative(entry["save_slot"]+".json")
        require(entry["mode"] in ("mono", "color") and type(entry["visible"]) is bool, "Invalid mode/visibility")
        for key, prefix, suffix in (("definition", "data/content/", (".json",)),
                                    ("reveal", "art/content/", (".png", ".svg"))):
            relative(entry[key])
            require(entry[key].startswith(prefix) and entry[key].endswith(suffix) and
                    STEM.fullmatch(Path(entry[key]).stem) and Path(entry[key]).parent.as_posix()+"/" == prefix, "Invalid current resource")
        require(isinstance(entry["category_id"], str) and categories.ID.fullmatch(entry["category_id"]), "Invalid category")
        if catalog is not None: categories.lookup(catalog, entry["category_id"])
        for key in seen:
            folded = (str(Path(entry[key]).with_suffix("")) if key == "reveal" else entry[key]).casefold()
            require(folded not in seen[key], "Current collision: " + key)
            seen[key].add(folded)
    require(values == sorted(values, key=lambda e: e["id"]), "Unsorted entries")
    return values


def validate(value, catalog):
    exact_keys(value, {"format", "entries", "metadata", "backgrounds"})
    require(value["format"] == FORMAT, "Current catalog format required")
    categories.validate(catalog)
    entries(value["entries"], catalog)
    require(isinstance(value["metadata"], list) and len(value["metadata"]) == len(value["entries"]), "Incomplete metadata")
    for entry, meta in zip(value["entries"], value["metadata"]):
        exact_keys(meta, {"id", "name", "category_id"})
        require(meta["id"] == entry["id"], "Metadata identity mismatch")
        require(isinstance(meta["name"], str) and 1 <= len(meta["name"]) <= 128 and meta["name"].strip(), "Invalid name")
        categories.lookup(catalog, meta["category_id"])
    require(isinstance(value["backgrounds"], list), "Invalid backgrounds")
    ids = []
    for row in value["backgrounds"]:
        exact_keys(row, {"id", "source"})
        require(row["id"] in {e["id"] for e in value["entries"]}, "Unknown background ID")
        reference(row["source"], name=source_path(row["id"], "background"), limit=1024*1024)
        ids.append(row["id"])
    require(ids == [e["id"] for e in value["entries"]], "Incomplete/unsorted backgrounds")
    require(len(encoded(value)) <= 8*1024*1024, "Oversized current index")
    return value


def source_path(identifier, kind):
    rating.identity(identifier)
    require(kind in ("reveal", "background"), "Invalid image kind")
    return "content/" + ("reveals" if kind == "reveal" else "backgrounds") + "/" + identifier + ".json"


def identity(entry, raw):
    definition = io.json_bytes(raw, 2*1024*1024)
    require(definition["id"] == entry["id"], "Definition ID differs")
    return {"key": entry["key"], "save_slot": entry["save_slot"],
            "definition": ref("game/"+entry["definition"], raw),
            "runtime_revision": definition["revision"]}


def source(entry, raw, current, kind, *, record_revision=1, catalog=None):
    value = {"format": REVEAL if kind == "reveal" else BACKGROUND, "id": entry["id"],
             "record_revision": record_revision, "binding": {"identity": identity(entry, raw)},
             "current": deepcopy(current)}
    if kind == "reveal":
        value["catalog"] = deepcopy(catalog)
    value["record_hash"] = digest(value)
    return validate_source(value, entry)


def validate_binding(binding, identifier, entry=None):
    exact_keys(binding, {"identity"})
    value = exact_keys(binding["identity"], {"key", "save_slot", "definition", "runtime_revision"})
    require(value["key"] == identifier and isinstance(value["save_slot"], str) and STEM.fullmatch(value["save_slot"]),
            "Invalid current binding")
    reference(value["definition"], limit=2*1024*1024)
    integer(value["runtime_revision"], 1, 1000000, "runtime revision")
    if entry is not None:
        require(value["save_slot"] == entry["save_slot"] and
                value["definition"]["file"] == "game/"+entry["definition"], "Foreign current binding")
    return binding


def validate_source(value, entry=None):
    fields = {"format", "id", "record_revision", "binding", "current", "record_hash"}
    exact_keys(value, fields | ({"catalog"} if isinstance(value, dict) and value.get("format") == REVEAL else set()))
    require(value["format"] in (REVEAL, BACKGROUND), "Current image source required")
    rating.identity(value["id"])
    require(entry is None or value["id"] == entry["id"], "Wrong source ID")
    validate_binding(value["binding"], value["id"], entry)
    integer(value["record_revision"], 1, 1000000, "source revision")
    current = value["current"]
    bg = value["format"] == BACKGROUND
    exact_keys(current, {"image_revision", "asset"} | ({"status"} if bg else set()))
    integer(current["image_revision"], 1, 1000000, "image revision")
    if bg:
        require(current["status"] in ("selected", "none", "standard"), "Invalid background preference")
        require((current["asset"] is not None) == (current["status"] == "selected"), "Background preference/asset mismatch")
        if current["asset"]:
            reference(current["asset"], name="game/art/backgrounds/"+value["id"]+".png", limit=32*1024*1024)
    else:
        reference(current["asset"], limit=32*1024*1024)
        require(current["asset"]["file"].startswith("game/art/content/") and
                current["asset"]["file"].endswith((".png", ".svg")), "Invalid reveal path")
        catalog_profiles.validate(value["catalog"], value["id"], current["asset"])
        if entry is not None:
            require(Path(current["asset"]["file"]).with_suffix("") == Path("game/"+entry["reveal"]).with_suffix(""),
                    "Foreign reveal resource")
    require(value["record_hash"] == digest({k: v for k, v in value.items() if k != "record_hash"}), "Changed current source")
    return value


def load_source(root, entry, kind, *, texts=None):
    name = source_path(entry["id"], kind)
    raw = texts[name] if texts is not None and name in texts else io.read(root, name, 1024*1024)
    if isinstance(raw, str): raw = raw.encode()
    value = validate_source(io.json_bytes(raw, 1024*1024), entry)
    require(value["format"] == (REVEAL if kind == "reveal" else BACKGROUND), "Wrong image source kind")
    return value


def notice_path(entry):
    return "game/"+str(Path(entry["reveal"]).with_suffix(".txt")).replace("\\", "/")


def selected(root, value, identifier, *, read=None):
    """Read exactly one current delivery, never a package tree."""
    read = read or (lambda n, limit=LIMIT, *, missing=False: io.read(root, n, limit, missing=missing))
    entry = next((e for e in value["entries"] if e["id"] == identifier), None)
    require(entry is not None, "Unknown current ID")
    raw = read("game/"+entry["definition"], 2*1024*1024)
    definition = rating.definition(raw)[0]
    require(definition["id"] == identifier, "Wrong current definition")
    result = {"entry": deepcopy(entry), "definition": raw,
              "metadata": deepcopy(next(m for m in value["metadata"] if m["id"] == identifier))}
    for kind in ("reveal", "background"):
        name = source_path(identifier, kind)
        source_raw = read(name, 1024*1024)
        image = validate_source(io.json_bytes(source_raw, 1024*1024), entry)
        require(image["binding"]["identity"] == identity(entry, raw), "Stale current image binding")
        if kind == "background":
            require(next((r["source"] for r in value["backgrounds"] if r["id"] == identifier), None) == ref(name, source_raw),
                    "Background index mismatch")
        require(image["format"] == (REVEAL if kind == "reveal" else BACKGROUND), "Wrong image source kind")
        asset = image["current"]["asset"]
        if asset is not None:
            asset_raw = read(asset["file"], 32*1024*1024)
            require(ref(asset["file"], asset_raw) == asset, "Changed active image")
            result[kind+"_bytes"] = asset_raw
        if kind == "reveal":
            require(image["catalog"]["source_width"] >= 2*definition["width"] and
                    image["catalog"]["source_height"] >= 2*definition["height"], "Reveal is too small for definition")
            for profile in image["catalog"]["profiles"]:
                asset = profile["asset"]
                payload = read(asset["file"], catalog_profiles.LIMIT)
                catalog_profiles.validate_png(profile, payload)
        result[kind] = image
    result["notice"] = read(notice_path(entry), 65536)
    if result["background"]["current"]["status"] == "selected":
        # PE-EDIT2 backgrounds may have no TXT; preserve actual presence/absence.
        result["background_notice"] = read("game/art/backgrounds/"+identifier+".txt", 65536, missing=True)
    result["rating"] = rating.validate(io.json_bytes(read(rating.path(identifier), rating.LIMIT), rating.LIMIT),
                                      definition_bytes=raw, production_mode=entry["mode"])
    result["added"] = added.validate(io.json_bytes(read(added.path(identifier), added.LIMIT), added.LIMIT), identifier)
    return result


def runtime_row(delivery):
    entry = delivery["entry"]
    background = deepcopy(delivery["background"]["current"])
    if background["asset"]:
        background["asset"]["file"] = background["asset"]["file"].removeprefix("game/")
    return {**{k: entry[k] for k in ("id", "key", "save_slot", "definition", "visible", "category_id")},
            "reveal": delivery["reveal"]["current"]["asset"]["file"].removeprefix("game/"),
            "catalog_reveal": catalog_profiles.project(delivery["reveal"]["catalog"]),
            "name": delivery["metadata"]["name"], "category_id": delivery["metadata"]["category_id"],
            "background": background, "difficulty": rating.project(delivery["rating"]), "added_at": delivery["added"]["added_at"]}
