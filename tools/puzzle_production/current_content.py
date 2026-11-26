"""Current catalog records. No production packages or historical receipts."""
from pathlib import Path
from . import catalog_profiles
from . import catalog_io as io, categories, catalog_rating as rating
from .authoring_package import ID, STEM, require, relative, sha
from .contract import canonical_bytes, digest, exact_keys, integer

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
    for entry in values:
        exact_keys(entry, ENTRY_FIELDS)
        require(entry["mode"] in ("mono", "color"), "Invalid puzzle mode")
    validate_identities([{k:v for k,v in entry.items() if k != "mode"} for entry in values], catalog)
    return values


def validate_identities(values, catalog=None):
    require(isinstance(values, list) and len(values) <= 10000, "Invalid entries")
    seen = {k: set() for k in ("id", "key", "save_slot", "definition", "reveal")}
    for entry in values:
        exact_keys(entry, ENTRY_FIELDS - {"mode"})
        require(isinstance(entry["id"], str) and ID.fullmatch(entry["id"]) and
                entry["key"] == entry["id"], "Invalid current identity")
        require(isinstance(entry["save_slot"], str) and STEM.fullmatch(entry["save_slot"]), "Invalid save slot")
        relative(entry["save_slot"]+".json")
        require(type(entry["visible"]) is bool, "Invalid mode/visibility")
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


def notice_path(entry):
    return "game/"+str(Path(entry["reveal"]).with_suffix(".txt")).replace("\\", "/")
