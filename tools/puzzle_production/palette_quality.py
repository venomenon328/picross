"""P-B1 read-only distance diagnosis; never a production certificate.

The scalar arithmetic follows PUZZLE_QUALITY.md §8.4 verbatim. The reader
reconstructs the report from the explicit current inputs, not recorded flags.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, DecimalException, ROUND_HALF_EVEN, localcontext
from itertools import combinations
import json
import os
from pathlib import Path
import re
import stat

from .contract import (Aborted, Budget, InvalidInput, canonical_bytes, digest,
                       exact_keys, integer, load_json)

FORMAT = "picross-palette-assessment-v1"
RULE = "picross-palette-separation-1"
NORM = {"file": "docs/PUZZLE_QUALITY.md", "contract": "1.0",
        "document_revision": 4, "commit": "45b8fe697364bf73f4277c8b76f92d5c00400919"}
ID = re.compile(r"[a-z][a-z0-9_-]{0,31}\Z")
RGB = re.compile(r"#[0-9a-fA-F]{6}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
M1 = (("0.4122214708", "0.5363325363", "0.0514459929"),
      ("0.2119034982", "0.6806995451", "0.1073969566"),
      ("0.0883024619", "0.2817188376", "0.6299787005"))
M2 = (("0.2104542553", "0.7936177850", "-0.0040720468"),
      ("1.9779984951", "-2.4285922050", "0.4505937099"),
      ("0.0259040371", "0.7827717662", "-0.8086757660"))


def _require(condition, message):
    if not condition:
        raise InvalidInput(message)


def quantized_oklab(rgb: str) -> list[int]:
    _require(isinstance(rgb, str) and RGB.fullmatch(rgb), "RGB must be #rrggbb")
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 80, ROUND_HALF_EVEN
        channels = [Decimal(int(rgb[i:i + 2], 16)) / Decimal(255) for i in (1, 3, 5)]
        linear = [c / Decimal("12.92") if c <= Decimal("0.04045") else
                  ((c + Decimal("0.055")) / Decimal("1.055")) ** Decimal("2.4")
                  for c in channels]
        lms = [sum((Decimal(k) * c for k, c in zip(row, linear)), Decimal(0)) for row in M1]
        roots = [c ** (Decimal(1) / Decimal(3)) if c else Decimal(0) for c in lms]
        lab = [sum((Decimal(k) * c for k, c in zip(row, roots)), Decimal(0)) for row in M2]
        return [int((c * Decimal(1000000)).to_integral_value(rounding=ROUND_HALF_EVEN)) for c in lab]


def pair_status(s: int) -> str:
    integer(s, 0, 10**16, "S")
    return "negative" if s < 10000000000 else "borderline" if s < 22500000000 else "positive"


def _distance(s):
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 80, ROUND_HALF_EVEN
        return format((Decimal(s).sqrt() / Decimal(10000)).quantize(Decimal("0.000001")), "f")


def _inputs(matrix, palette, identity, budget):
    budget.check()
    exact_keys(identity, {"id", "revision", "source_id", "normalized_sha256"})
    _require(isinstance(identity["id"], str) and 1 <= len(identity["id"]) <= 128 and
             identity["id"].isprintable(), "Invalid candidate ID")
    integer(identity["revision"], 1, 1000000, "candidate revision")
    _require(isinstance(identity["source_id"], str) and ID.fullmatch(identity["source_id"]), "Invalid source ID")
    _require(isinstance(identity["normalized_sha256"], str) and SHA.fullmatch(identity["normalized_sha256"]),
             "Invalid normalized source SHA-256")
    _require(isinstance(palette, list) and 1 <= len(palette) <= 8, "Expected 1..8 palette entries")
    colors = {}
    for entry in palette:
        exact_keys(entry, {"id", "rgb"})
        name, rgb = entry["id"], entry["rgb"]
        _require(isinstance(name, str) and ID.fullmatch(name) and name != "empty" and name not in colors,
                 "Invalid/duplicate foreground ID")
        _require(isinstance(rgb, str) and RGB.fullmatch(rgb), "RGB must be #rrggbb")
        colors[name] = rgb.lower()
    _require(isinstance(matrix, list) and 1 <= len(matrix) <= 100, "Invalid matrix height")
    _require(isinstance(matrix[0], list) and 1 <= len(matrix[0]) <= 100, "Invalid matrix width")
    width, height = len(matrix[0]), len(matrix)
    counts = Counter()
    for row in matrix:
        budget.check()
        _require(isinstance(row, list) and len(row) == width, "Ragged matrix")
        for cell in row:
            _require(isinstance(cell, str) and (cell == "empty" or cell in colors), "Undefined matrix cell")
            counts[cell] += 1
    _require(any(counts[name] for name in colors), "No used foreground colors")
    return dict(sorted(colors.items())), counts, width, height


def _binding(matrix, colors, identity, width, height):
    grid = {"width": width, "height": height, "order": "row-major"}
    binding = {"rule_id": RULE, "norm": dict(NORM), "candidate": dict(identity),
               "matrix": {**grid, "sha256": digest({**grid, "cells": matrix})},
               "palette_sha256": digest([{"id": k, "rgb": v} for k, v in colors.items()])}
    return {**binding, "source_fingerprint": digest(binding)}


def _pair(a, b):
    s = sum((x - y) ** 2 for x, y in zip(a["q"], b["q"]))
    return {"ids": [a["id"], b["id"]], "rgb": [a["rgb"], b["rgb"]],
            "q": [a["q"], b["q"]], "S": s, "D": _distance(s),
            "status": pair_status(s), "rule_id": RULE}


def assess(matrix, palette, identity, budget=None) -> dict:
    """Pure candidate diagnosis. Duplicate RGB are distance zero, not invalid."""
    budget = Budget() if budget is None else budget
    colors, counts, width, height = _inputs(matrix, palette, identity, budget)
    used = []
    for name, rgb in colors.items():
        if counts[name]:
            budget.check()
            used.append({"id": name, "rgb": rgb, "cells": counts[name], "q": quantized_oklab(rgb)})
    pairs = []
    for a, b in combinations(used, 2):
        budget.check()
        pairs.append(_pair(a, b))
    negative = [p for p in pairs if p["status"] == "negative"]
    result = {"format": FORMAT, **_binding(matrix, colors, identity, width, height),
              "used": used, "unused_ids": [k for k in colors if not counts[k]],
              "empty_cells": counts["empty"], "pair_count": len(pairs), "pairs": pairs,
              "worst_pair": min(pairs, key=lambda p: (p["S"], p["ids"])) if pairs else None,
              "negative_pairs": negative, "warning_pairs": [p for p in pairs if p["status"] == "borderline"],
              "status": "negative" if negative else "positive", "complete": True}
    budget.check()
    return result


def _equal(actual, expected):
    # Canonical bytes also distinguish bool/int and int/float (Python == does not).
    _require(canonical_bytes(actual) == canonical_bytes(expected), "Stale or altered palette assessment")


def verify_assessment(report, matrix, palette, identity, budget=None) -> None:
    """Fresh reader: enumerate/check every pair and derive status independently.

    Shares only input, scalar arithmetic and canonical binding primitives with
    the producer; never calls assess or trusts stored q/S/status/counts.
    """
    budget = Budget() if budget is None else budget
    colors, counts, width, height = _inputs(matrix, palette, identity, budget)
    binding = _binding(matrix, colors, identity, width, height)
    exact_keys(report, {"format", *binding, "used", "unused_ids", "empty_cells", "pair_count", "pairs",
                        "worst_pair", "negative_pairs", "warning_pairs", "status", "complete"})
    for key, value in binding.items():
        _equal(report[key], value)
    _equal(report["format"], FORMAT)
    names = [name for name in colors if counts[name]]
    used = []
    for name in names:
        budget.check()
        used.append({"id": name, "rgb": colors[name], "cells": counts[name], "q": quantized_oklab(colors[name])})
    _equal(report["used"], used)
    _equal(report["unused_ids"], [name for name in colors if not counts[name]])
    _equal(report["empty_cells"], counts["empty"])
    _equal(report["pair_count"], len(names) * (len(names) - 1) // 2)
    _require(isinstance(report["pairs"], list) and len(report["pairs"]) == report["pair_count"],
             "Incomplete pair evaluation")
    negatives, warnings, worst = [], [], None
    at = 0
    for i in range(len(used)):
        for j in range(i + 1, len(used)):
            budget.check()
            a, b = used[i], used[j]
            s = sum((a["q"][k] - b["q"][k]) ** 2 for k in range(3))
            status = "negative" if s < 10000000000 else "borderline" if s < 22500000000 else "positive"
            pair = {"ids": [a["id"], b["id"]], "rgb": [a["rgb"], b["rgb"]],
                    "q": [a["q"], b["q"]], "S": s, "D": _distance(s), "status": status, "rule_id": RULE}
            _equal(report["pairs"][at], pair)
            at += 1
            if worst is None or s < worst["S"]:
                worst = pair
            if status == "negative":
                negatives.append(pair)
            elif status == "borderline":
                warnings.append(pair)
    for key, expected in {"worst_pair": worst, "negative_pairs": negatives, "warning_pairs": warnings,
                          "status": "negative" if negatives else "positive", "complete": True}.items():
        _equal(report[key], expected)
    budget.check()


def _safe_path(path: Path) -> Path:
    _require(".." not in path.parts, "Parent traversal is not allowed")
    absolute = path.absolute()
    for part in (*reversed(absolute.parents), absolute):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        _require(not stat.S_ISLNK(info.st_mode) and
                 not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
                 "Links/reparse points are not allowed")
    return absolute.resolve()


def read_candidate(path: Path):
    """Reuse the RP-3 design, hint and identity readers; no solver or replay."""
    from .images import PILLOW_VERSION, VERSION, candidate, logic_from_matrix, validate_design
    value = load_json(_safe_path(path), 2 * 1024 * 1024)
    exact_keys(value, {"id", "format", "revision", "source_id", "normalized_sha256", "versions",
                       "design", "variant", "matrix", "logic_hash"})
    _require(value["format"] == "picross-image-candidate-v1" and type(value["revision"]) is int and
             value["revision"] == 1, "Unsupported candidate format/revision")
    design = validate_design(value["design"])
    identity = {k: value[k] for k in ("id", "revision", "source_id", "normalized_sha256")}
    _inputs(value["matrix"], design["palette"], identity, Budget())
    _require(len(value["matrix"]) == design["height"] and len(value["matrix"][0]) == design["width"],
             "Matrix/design dimensions differ")
    _require(value["source_id"] == design["source_id"] and value["variant"] in design["variants"],
             "Candidate source/variant differs from design")
    versions = exact_keys(value["versions"], {"tool", "pillow", "jpeg", "jpeg_turbo", "littlecms", "zlib"})
    _require(versions["tool"] == VERSION and versions["pillow"] == PILLOW_VERSION and
             all(v is None or isinstance(v, str) and 1 <= len(v) <= 128 for v in versions.values()),
             "Invalid candidate producer versions")
    _equal(value["logic_hash"], digest(logic_from_matrix(value["matrix"], design)))
    expected = candidate(value["normalized_sha256"], design, value["variant"], value["matrix"], versions)
    _equal(value, expected)
    return value["matrix"], design["palette"], identity


def _report_target(path, candidate_path):
    target = _safe_path(path)
    _require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.json", path.name) and
             target.parent.is_dir() and not target.exists(), "Report must be a new simple .json file")
    _require(not target.is_relative_to(_safe_path(candidate_path).parent), "Report must be outside candidate folder")
    for parent in target.parents:
        _require(not any((parent / marker).exists() for marker in
                         (".git", "handoff.json", "inventory.json", "manifest.json", "package.zip")),
                 "Report must be outside checkouts and sealed packages")
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only palette diagnosis; Authoring 0.6.0 final gates use ZA-1 v5 separately.")
    parser.add_argument("command", choices=("check-palette",))
    parser.add_argument("--candidate", type=Path, required=True)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--report", type=Path)
    output.add_argument("--verify", type=Path)
    parser.add_argument("--seconds", type=float, default=120)
    args = parser.parse_args(argv)
    try:
        budget = Budget(args.seconds)
        budget.check()
        target = _report_target(args.report, args.candidate) if args.report else None
        matrix, palette, identity = read_candidate(args.candidate)
        budget.check()
        report = (load_json(_safe_path(args.verify), 128 * 1024) if args.verify else
                  assess(matrix, palette, identity, budget))
        verify_assessment(report, matrix, palette, identity, budget)
        if target:
            # Recheck immediately before exclusive creation. No replace/overwrite.
            _report_target(args.report, args.candidate)
            created = None
            try:
                try:
                    stream = target.open("xb")
                except FileExistsError as exc:
                    raise InvalidInput("Report appeared during diagnosis; refusing to overwrite") from exc
                with stream:
                    created = os.fstat(stream.fileno())
                    stream.write(canonical_bytes(report) + b"\n")
                verify_assessment(load_json(target, 128 * 1024), matrix, palette, identity, budget)
            except BaseException:
                # Only remove our own failed write, never a replacement file.
                if created is not None and target.exists() and os.path.samestat(created, target.lstat()):
                    target.unlink()
                raise
        print(json.dumps(report, ensure_ascii=False, separators=(",", ":"), allow_nan=False))
        return 0
    except (InvalidInput, Aborted, KeyboardInterrupt, MemoryError, OSError, DecimalException,
            RuntimeError, ValueError, TypeError) as exc:
        status = ("invalid_input" if isinstance(exc, InvalidInput) else
                  "aborted" if isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError)) else "error")
        print(json.dumps({"format": "picross-palette-error-v1", "status": status,
                          "message": str(exc) or type(exc).__name__}, ensure_ascii=False, separators=(",", ":")))
        return {"invalid_input": 2, "aborted": 4, "error": 5}[status]
