"""Fail before readiness when a portable program file is missing or changed."""
import sys
from pathlib import Path

from tools.puzzle_production import catalog_io as io
from tools.puzzle_production.authoring_package import require
from tools.puzzle_production.contract import exact_keys


def verify(root=None):
    root = io.external(root or Path(sys.executable).parent)
    value = io.json_bytes(io.read(root, "inventory.json", 2*1024*1024), 2*1024*1024)
    exact_keys(value, {"commit", "files"})
    seen = set()
    require(isinstance(value["files"], list) and value["files"], "Leeres Programminventar.")
    for row in value["files"]:
        exact_keys(row, {"file", "bytes", "sha256"})
        require(row["file"] not in seen and row["file"] != "inventory.json", "Doppeltes Programminventar.")
        raw = io.read(root, row["file"], 64*1024*1024)
        require(type(row["bytes"]) is int and len(raw) == row["bytes"] and io.checksum(raw) == row["sha256"],
                "Programmdatei fehlt oder ist verändert: "+row["file"])
        seen.add(row["file"])
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(actual == seen | {"inventory.json"}, "Programmpaket enthält fehlende oder zusätzliche Dateien.")
    return value["commit"]
