"""Canonical registered puzzle records and their runtime-v9 rows."""
from copy import deepcopy
from pathlib import PurePosixPath
import json
import stat

from . import catalog_added, catalog_io as io, catalog_profiles, categories
from . import current_content as content, current_rating
from .authoring_package import ID, require
from .contract import exact_keys, integer

FORMAT = "picross-puzzle-record-v1"
DIRECTORY = "content/puzzles"
LIMIT = 128 * 1024
FIELDS = {"format", "id", "save_slot", "visible", "mode", "name", "category_id",
          "definition", "added", "reveal", "background", "difficulty"}


def path(identifier):
    require(isinstance(identifier, str) and ID.fullmatch(identifier), "Invalid puzzle ID")
    return f"{DIRECTORY}/{identifier}.json"


def encode(record):
    raw = (json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()
    require(len(raw) <= LIMIT, "Puzzle record exceeds 128 KiB")
    return raw


def entry(record):
    return {key: record[key] for key in ("id", "save_slot", "visible", "mode", "category_id")} | {
        "key": record["id"], "definition": record["definition"]["file"].removeprefix("game/"),
        "reveal": record["reveal"]["asset"]["file"].removeprefix("game/")}


def catalog(record):
    reveal = record["reveal"]
    return {**reveal["catalog"], "source_sha256": reveal["asset"]["sha256"]}


def validate(record, identifier, definition_bytes, *, category_catalog=None):
    exact_keys(record, FIELDS)
    require(record["format"] == FORMAT and record["id"] == identifier, "Puzzle record identity differs")
    path(identifier)
    reveal = exact_keys(record["reveal"], {"image_revision", "asset", "catalog"})
    definition_ref = content.reference(record["definition"], limit=2*1024*1024)
    require(definition_ref["file"].startswith("game/data/content/") and
            len(definition_bytes) == definition_ref["bytes"], "Changed puzzle definition")
    asset = content.reference(reveal["asset"], limit=32*1024*1024)
    require(asset["file"].startswith("game/art/content/"), "Invalid reveal resource")
    content.entries([entry(record)], category_catalog)
    require(isinstance(record["name"], str) and record["name"].strip() and
            len(record["name"]) <= 128, "Invalid puzzle name")
    exact_keys(reveal["catalog"], {"generator", "profiles", "source_height", "source_width"})
    catalog_profiles.validate(catalog(record), identifier, asset)
    integer(reveal["image_revision"], 1, 1000000, "reveal revision")
    bg = exact_keys(record["background"], {"status", "image_revision", "asset"})
    integer(bg["image_revision"], 1, 1000000, "background revision")
    require(bg["status"] in ("selected", "none", "standard") and
            (bg["asset"] is not None) == (bg["status"] == "selected"), "Invalid background decision")
    if bg["asset"] is not None:
        content.reference(bg["asset"], name=f"game/art/backgrounds/{identifier}.png", limit=32*1024*1024)
    catalog_added.validate_fields(record["added"])
    data = io.json_bytes(definition_bytes, 2*1024*1024)
    require(data["id"] == identifier, "Foreign puzzle definition")
    require(reveal["catalog"]["source_width"] >= 2*data["width"] and
            reveal["catalog"]["source_height"] >= 2*data["height"], "Reveal is too small for puzzle")
    diff = exact_keys(record["difficulty"], {"rating_revision", "logic_binding", "rating", "compact_analysis"})
    integer(diff["rating_revision"], 1, 1000000, "rating revision")
    binding = diff["logic_binding"]
    if "analysis_hash" in diff["compact_analysis"]:
        exact_keys(binding, {"matrix_hash"})
        binding = {**binding, "analysis_hash": diff["compact_analysis"]["analysis_hash"]}
    else:
        exact_keys(binding, {"matrix_hash","analysis_hash"})
    current_rating.validate_fields(diff["rating"], diff["compact_analysis"], record["mode"],
        {"id": identifier, "runtime_revision": data["revision"], "definition_sha256": definition_ref["sha256"]},
        binding,
        definition_bytes=definition_bytes, active=True)
    return record


def decode(raw, identifier):
    value = io.json_bytes(raw, LIMIT)
    exact_keys(value, FIELDS)
    require(value["id"] == identifier and value["format"] == FORMAT and encode(value) == raw,
            "Noncanonical or foreign puzzle record: " + identifier)
    return value


def load(root, identifier, *, category_catalog, read=None):
    read = read or (lambda name, limit: io.read(root, name, limit))
    record = decode(read(path(identifier), LIMIT), identifier)
    ref = content.reference(record["definition"], limit=2*1024*1024)
    require(ref["file"].startswith("game/data/content/") and
            PurePosixPath(ref["file"]).parent.as_posix() == "game/data/content" and ref["file"].endswith(".json"),
            "Invalid puzzle definition path")
    return validate(record, identifier, read(ref["file"], 2*1024*1024), category_catalog=category_catalog)


def runtime_row(record):
    from . import catalog_rating
    diff = record["difficulty"]
    background = deepcopy(record["background"])
    if background["asset"] is not None:
        background["asset"]["file"] = background["asset"]["file"].removeprefix("game/")
    return {k: v for k, v in entry(record).items() if k != "mode"} | {
        "name": record["name"], "added_at": record["added"]["added_at"],
        "catalog_reveal": catalog_profiles.project(catalog(record)), "background": background,
        "difficulty": catalog_rating.project_rating(diff["rating"])}


def inventory(root, tracked=None):
    """Check the flat namespace; sparse-hidden names come from the bound Git tree."""
    directory = io.safe(root, DIRECTORY)
    identifiers = set()
    names = set()
    if directory.exists():
        require(directory.is_dir(), "Puzzle namespace must be a directory")
        for file in directory.iterdir():
            info = file.lstat()
            name = f"{DIRECTORY}/{file.name}"
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                    not getattr(info,"st_file_attributes",0) & 1024, "Invalid puzzle namespace member: " + name)
            require(len(names) < 10000, "Too many puzzle records")
            names.add(name)
    if tracked is not None and tracked.names is not None:
        for folded, entries in tracked.names.items():
            if folded.startswith(DIRECTORY + "/"):
                require(len(entries) == 1, "Puzzle namespace case collision")
                name, mode = next(iter(entries))
                require(mode == b"100644" and (name in names or name in tracked.hidden_records),
                        "Missing or invalid tracked puzzle record: "+name)
                names.add(name)
    for name in names:
        identifier = PurePosixPath(name).stem
        require(path(identifier) == name and identifier not in identifiers, "Unexpected puzzle record: " + name)
        identifiers.add(identifier)
    require(len(identifiers) <= 10000, "Too many puzzle records")
    return identifiers
