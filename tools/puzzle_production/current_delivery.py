"""Selected committed delivery used for completion and main comparison."""
from . import puzzle_catalog
from .authoring_package import require
from .contract import digest


def from_source(source, commit, identifier):
    def read(name, limit, *, missing=False):
        return source.read(commit,name,limit,missing)
    catalog,runtime = puzzle_catalog.index(read,source.puzzle_ids(commit))
    row = next((r for r in runtime["entries"] if r["id"] == identifier),None)
    require(row is not None,"Selected delivery missing")
    checked = puzzle_catalog.delivery(read,identifier,catalog,row)
    entry = checked["entry"].copy()
    mode = entry.pop("mode")
    return {"entry":entry,"mode":mode,"metadata":checked["metadata"],"runtime":row,
            "difficulty_sha256":digest(checked["record"]["difficulty"]),"files":checked["files"]}


def same(left,right):
    return left == right
