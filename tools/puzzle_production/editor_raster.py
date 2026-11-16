"""Current raster parsing, clues and independent proof-end validation."""
from copy import deepcopy

from pathlib import Path

import re

from .authoring_package import require, relative, sha

from .contract import canonical_bytes, digest, exact_keys, integer, Budget, load_json

from . import catalog_io as io, catalog_rating as rating, catalog_background as bg

from . import editor_image_source as images, reveal_source as reveal

def encoded(value):
    return canonical_bytes(value) + b"\n"

def parse(text, palette):
    require(isinstance(text, str) and len(text.encode("utf-8")) <= 65536, "Rastertext exceeds 64 KiB")
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    if lines and lines[-1] == "": lines.pop()
    require(lines, "Zeile 1, Spalte 1: Raster fehlt")
    allowed = {0, *(row["id"] for row in palette)}
    matrix = []
    for y, line in enumerate(lines, 1):
        require(y <= 50, f"Zeile {y}, Spalte 1: höchstens 50 Rasterzeilen")
        tokens = line.split()
        require(tokens, f"Zeile {y}, Spalte 1: leere Rasterzeile")
        row = []
        for x, token in enumerate(tokens, 1):
            location = f"Zeile {y}, Spalte {x}: "
            require(x <= 50, location + "höchstens 50 Zellen je Zeile")
            require(re.fullmatch(r"[0-9]+", token), location + "nichtnegative Ganzzahl erwartet")
            normalized = token.lstrip("0") or "0"
            require(len(normalized) == 1, location + "unbekannte Palette-ID")
            value = int(normalized)
            require(value in allowed, location + "unbekannte Palette-ID")
            row.append(value)
        if matrix:
            require(len(row) == len(matrix[0]), f"Zeile {y}, Spalte {min(len(row),len(matrix[0]))+1}: abweichende Zeilenbreite")
        matrix.append(row)
    return matrix

def clues(line):
    result, previous = [], 0
    for color in line:
        if color:
            if color == previous: result[-1]["length"] += 1
            else: result.append({"length": 1, "color": color})
        previous = color
    return result

def definition(previous, matrix):
    value = deepcopy(previous)
    value.update(width=len(matrix[0]), height=len(matrix), solution=matrix,
                 rows=[clues(row) for row in matrix], columns=[clues(row) for row in zip(*matrix)])
    if (previous["width"], previous["height"], previous["solution"]) != (value["width"], value["height"], matrix):
        value["revision"] = integer(previous["revision"]+1, 1, 1000000, "new runtime revision")
    rating.definition(encoded(value))
    return value

def check_end(definition, proof):
    expected = [[["empty" if value == 0 else "c"+str(value)] for value in row] for row in definition["solution"]]
    require(proof.get("status") == "solved" and proof.get("final_domains") == expected,
            "Independently checked proof end differs from selected matrix")