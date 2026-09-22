"""Verify F-01's finite line-intersection certificate (test tooling, no game solver)."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "prototypes/p1/data"


def placements(lengths: list[int], width: int = 20) -> list[list[int]]:
    """Enumerate this monochrome fixture's line placements, never grid guesses."""
    if not lengths:
        return [[0] * width]
    result = []
    first, *rest = lengths
    remaining = sum(rest) + len(rest)
    for start in range(width - first - remaining + 1):
        prefix = [0] * start + [1] * first
        if rest:
            for tail in placements(rest, width - len(prefix) - 1):
                result.append(prefix + [0] + tail)
        else:
            result.append(prefix + [0] * (width - len(prefix)))
    return result


def derive(data: dict) -> tuple[list[dict], list[list[int]]]:
    if (data["id"], data["revision"], data["width"], data["height"]) != ("F-01", 1, 20, 20):
        raise ValueError("Certificate is scoped to F-01 revision 1, 20x20")
    candidates = {}
    for axis, hints in (("row", data["rows"]), ("column", data["columns"])):
        for index, blocks in enumerate(hints):
            if any(block["color"] != 1 for block in blocks):
                raise ValueError("F-01 is monochrome")
            candidates[axis, index] = placements([block["length"] for block in blocks])
    known = [[-1] * 20 for _ in range(20)]
    steps = []
    # At least one previously unknown cell per step: bounded by 400 steps.
    while True:
        changed = False
        for (axis, index), options in candidates.items():
            points = [(index, n) if axis == "row" else (n, index) for n in range(20)]
            viable = [line for line in options if all(known[y][x] in (-1, line[n]) for n, (y, x) in enumerate(points))]
            if not viable:
                raise ValueError("Contradictory clues/certificate")
            forced = []
            for n, (y, x) in enumerate(points):
                values = {line[n] for line in viable}
                if known[y][x] == -1 and len(values) == 1:
                    value = values.pop()
                    known[y][x] = value
                    forced.append([n + 1, value])
            if forced:
                steps.append(dict(axis=axis, line=index + 1, candidates=len(viable), forced=forced))
                changed = True
        if not changed:
            break
    return steps, known


def verify(data: dict, certificate: dict) -> int:
    steps, known = derive(data)
    if certificate != {"id": "F-01", "revision": 1, "rule": "line-intersection", "steps": steps}:
        raise ValueError("Certificate differs from reproducible deductions")
    if any(-1 in row for row in known) or known != data["solution"]:
        raise ValueError("Deductions do not determine the entire supplied solution")
    return len(steps)


if __name__ == "__main__":
    count = verify(json.loads((DATA / "f01.json").read_text(encoding="utf-8")), json.loads((DATA / "f01-proof.json").read_text(encoding="utf-8")))
    print(f"F-01 PROOF PASS: {count} steps, 400 forced cells, no givens/guesses")
