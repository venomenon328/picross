"""Check solution witnesses by direct run extraction, without importing search."""
from __future__ import annotations

import math

from .contract import Budget, InvalidInput, Puzzle, exact_keys

WITNESS_FORMAT = "picross-solution-witness-v1"


class InvalidDiagnosis(ValueError):
    """Malformed, mismatched or invalid diagnosis evidence."""


def validate_measurements(obj: dict, puzzle: Puzzle) -> None:
    """Validate reported limits/counters, without treating them as a search proof."""
    from .contract import integer
    limits = exact_keys(obj["budgets"], {"seconds", "max_lines", "max_nodes"}, InvalidDiagnosis)
    stats = exact_keys(obj["statistics"], {"nodes", "line_evaluations",
                                       "witness_line_evaluations", "elapsed_seconds"},
                       InvalidDiagnosis)
    for value in (limits["seconds"], stats["elapsed_seconds"]):
        try:
            valid = type(value) in (int, float) and math.isfinite(value) and value >= 0
        except OverflowError:
            valid = False
        if not valid:
            raise InvalidDiagnosis("Time measurements must be finite and nonnegative")
    integer(limits["max_lines"], 0, 1_000_000, "max_lines", InvalidDiagnosis)
    integer(limits["max_nodes"], 0, 1_000_000, "max_nodes", InvalidDiagnosis)
    integer(stats["nodes"], 0, limits["max_nodes"], "nodes", InvalidDiagnosis)
    integer(stats["line_evaluations"], 0, limits["max_lines"], "lines", InvalidDiagnosis)
    integer(stats["witness_line_evaluations"], 0, stats["line_evaluations"],
            "witness lines", InvalidDiagnosis)
    if stats["witness_line_evaluations"] < len(obj["witnesses"]) * (puzzle.width + puzzle.height):
        raise InvalidDiagnosis("Missing reported witness verification work")


def verify_witness(puzzle: Puzzle, witness: object,
                   budget: Budget | None = None) -> list[list[str]]:
    """Independently establish existence, never uniqueness or deduction."""
    budget = budget if budget is not None else Budget()
    obj = exact_keys(witness, {"format", "logic_hash", "matrix"}, InvalidDiagnosis)
    if obj["format"] != WITNESS_FORMAT or obj["logic_hash"] != puzzle.logic_hash:
        raise InvalidDiagnosis("Wrong witness format or logic binding")
    matrix = obj["matrix"]
    values = {"empty", *puzzle.colors}
    if (not isinstance(matrix, list) or len(matrix) != puzzle.height or
            any(not isinstance(row, list) or len(row) != puzzle.width or
                any(not isinstance(value, str) or value not in values for value in row)
                for row in matrix)):
        raise InvalidDiagnosis("Witness must be a complete matrix of palette IDs")

    def runs(line):
        result = []
        previous = "empty"
        for value in line:
            if value != previous and value != "empty":
                result.append({"length": 1, "color": value})
            elif value != "empty":
                result[-1]["length"] += 1
            previous = value
        return result

    wire = puzzle.to_wire()
    for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
        for index in range(count):
            budget.tick()
            line = matrix[index] if axis == "row" else [row[index] for row in matrix]
            if runs(line) != wire[axis + "_clues"][index]:
                raise InvalidDiagnosis("Witness violates the ordered length/color clues")
    budget.check()
    return matrix


def load_evidence(path, byte_limit):
    # Keep malformed evidence distinct from malformed logic inputs.
    from .contract import load_json
    try:
        if path.is_symlink():
            raise InvalidDiagnosis("Evidence must be a regular local file")
        return load_json(path, byte_limit)
    except InvalidInput as exc:
        raise InvalidDiagnosis(str(exc)) from exc
