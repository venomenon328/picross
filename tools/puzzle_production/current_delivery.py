"""Selected committed delivery used for completion and main comparison."""
from . import catalog_io as io, categories, current_content as content, puzzle_catalog
from .authoring_package import require
from .contract import digest


def snapshot(read, identifier):
    runtime = io.json_bytes(read(content.RUNTIME,content.RUNTIME_LIMIT),content.RUNTIME_LIMIT)
    catalog = categories.validate(io.json_bytes(read(categories.PATH,categories.MAX_BYTES),categories.MAX_BYTES))
    puzzle_catalog.validate_runtime(runtime,catalog,[r["id"] for r in runtime["entries"]])
    row = next((r for r in runtime["entries"] if r["id"] == identifier),None)
    require(row is not None,"Selected delivery missing")
    checked = puzzle_catalog.delivery(read,identifier,catalog,row)
    entry = checked["entry"].copy()
    mode = entry.pop("mode")
    return {"entry":entry,"mode":mode,"metadata":checked["metadata"],"runtime":row,
            "difficulty_sha256":digest(checked["record"]["difficulty"]),"files":checked["files"]}


def same(left,right):
    return left == right
