"""Targeted catalog reads. The checked-in player projection indexes record names."""
from copy import deepcopy

from . import catalog_added, catalog_io as io, catalog_profiles, categories
from . import current_content as content, puzzle_record
from .authoring_package import require
from .contract import exact_keys, integer

ROW_FIELDS = {"id", "key", "save_slot", "definition", "reveal", "visible", "category_id",
              "name", "difficulty", "added_at", "background", "catalog_reveal"}


def validate_runtime(value, category_catalog, identifiers):
    exact_keys(value, {"format", "categories", "entries"})
    require(value["format"] == content.RUNTIME_FORMAT and value["categories"] == categories.ordered(category_catalog),
            "Invalid runtime format or categories")
    rows = value["entries"]
    require(isinstance(rows, list) and len(rows) <= 10000, "Invalid runtime row count")
    identities = []
    for row in rows:
        exact_keys(row, ROW_FIELDS)
        require(isinstance(row["name"], str) and row["name"].strip() and len(row["name"]) <= 128,
                "Invalid projected name")
        identities.append({k:row[k] for k in content.ENTRY_FIELDS if k != "mode"})
        catalog_profiles.validate_projection(row)
        catalog_added.timestamp(row["added_at"])
        bg = exact_keys(row["background"], {"status", "image_revision", "asset"})
        integer(bg["image_revision"], 1, 1000000, "background revision")
        require(bg["status"] in ("selected", "none", "standard") and
                (bg["asset"] is not None) == (bg["status"] == "selected"), "Invalid projected background")
        if bg["asset"] is not None:
            content.reference(bg["asset"], name="art/backgrounds/"+row["id"]+".png", limit=32*1024*1024)
        difficulty = exact_keys(row["difficulty"], {"method","level","assessment_type","confidence","plausible_range","r4_required"})
        from .catalog_method import METHODS
        require(difficulty["method"] in METHODS and difficulty["level"] in ("L1","L2","L3","L4","L5") and
                difficulty["assessment_type"] == "instrumented" and difficulty["confidence"] == "medium" and
                difficulty["plausible_range"] == [difficulty["level"]]*2 and type(difficulty["r4_required"]) is bool,
                "Invalid projected difficulty")
    content.validate_identities(identities, category_catalog)
    require([r["id"] for r in rows] == sorted(identifiers), "Puzzle record inventory differs from runtime")
    return value


def index(read, identifiers):
    cats = categories.validate(io.json_bytes(read(categories.PATH, categories.MAX_BYTES), categories.MAX_BYTES))
    runtime = io.json_bytes(read(content.RUNTIME, content.RUNTIME_LIMIT), content.RUNTIME_LIMIT)
    return cats, validate_runtime(runtime, cats, identifiers)


def inspect(root, *, tracked=None):
    return index(lambda name, limit: io.read(root,name,limit), puzzle_record.inventory(root,tracked))


def difficulty_fields(assessment):
    binding = deepcopy(assessment["logic_binding"])
    if "analysis_hash" in assessment["compact_analysis"]:
        require(binding.pop("analysis_hash") == assessment["compact_analysis"]["analysis_hash"], "Rating logic differs")
    return {key:deepcopy(assessment[key]) for key in ("rating_revision","rating","compact_analysis")} | {
        "logic_binding":binding}


def delivery(read, identifier, catalog, row, *, record=None):
    """Read the selected record and the assets that establish its current delivery."""
    if record is None:
        record = puzzle_record.load(None, identifier, category_catalog=catalog, read=read)
    require(puzzle_record.runtime_row(record) == row, "Selected puzzle projection differs: " + identifier)
    entry = puzzle_record.entry(record)
    files = {}
    def get(name, limit, optional=False):
        data = read(name, limit, missing=optional)
        files[name] = content.ref(name,data) if data is not None else None
        return data
    name = puzzle_record.path(identifier)
    files[name] = content.ref(name,puzzle_record.encode(record))
    definition = get(record["definition"]["file"],2*1024*1024)
    require(files[record["definition"]["file"]] == record["definition"],"Definition changed")
    reveal = record["reveal"]
    image = get(reveal["asset"]["file"],32*1024*1024)
    require(files[reveal["asset"]["file"]] == reveal["asset"],"Reveal changed")
    for profile in reveal["catalog"]["profiles"]:
        catalog_profiles.validate_png(profile,get(profile["asset"]["file"],catalog_profiles.LIMIT))
    notice = get(content.notice_path(entry),65536)
    result = {"entry":entry,"record":record,"metadata":{k:record[k] for k in ("id","name","category_id")},
              "definition":definition,"reveal_bytes":image,"notice":notice,"files":files}
    background = record["background"]["asset"]
    if background:
        result["background_bytes"] = get(background["file"],32*1024*1024)
        require(files[background["file"]] == background,"Background changed")
        result["background_notice"] = get("game/art/backgrounds/"+identifier+".txt",65536,True)
    return result
