"""Versioned wire contract and validation; no deduction routines live here."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time

EMPTY, INK, FULL = 1, 2, 3
VALUES = ((EMPTY, "empty"), (INK, "ink"))
PROFILE = {
    "id": "full-line-mono", "version": 1,
    "start": "unknown", "deduction": "all-line-supported-values",
    "search": False,
}
LOGIC_FORMAT = "picross-logic-v1"
PROOF_FORMAT = "picross-proof-v1"


class InvalidInput(ValueError):
    """Malformed or unsupported input, distinct from logical contradiction."""


class InvalidProof(ValueError):
    """Proof fails validation or independent justification."""


class Aborted(RuntimeError):
    """Controlled budget/cancellation termination, never a certificate."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def exact_keys(value: object, keys: set[str], error=InvalidInput) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise error(f"Expected exactly these keys: {sorted(keys)}")
    return value


def integer(value: object, low: int, high: int, label: str,
            error=InvalidInput) -> int:
    if type(value) is not int or not low <= value <= high:
        raise error(f"{label} must be an integer in {low}..{high}")
    return value


def domain_values(mask: int) -> list[str]:
    return [name for bit, name in VALUES if mask & bit]


def wire_grid(grid: list[list[int]]) -> list[list[list[str]]]:
    return [[domain_values(mask) for mask in row] for row in grid]


@dataclass(frozen=True)
class Puzzle:
    width: int
    height: int
    rows: tuple[tuple[int, ...], ...]
    columns: tuple[tuple[int, ...], ...]

    def to_wire(self) -> dict:
        def clues(lines):
            return [[{"length": length, "color": "ink"} for length in line]
                    for line in lines]
        return {
            "format": LOGIC_FORMAT, "width": self.width, "height": self.height,
            "colors": ["ink"], "empty": "empty",
            "rules": {"id": "mono-gap-v1", "same_color_gap": 1},
            "initial_domain": ["empty", "ink"],
            "row_clues": clues(self.rows), "column_clues": clues(self.columns),
        }

    @property
    def logic_hash(self) -> str:
        return digest(self.to_wire())

    def unknown_grid(self) -> list[list[int]]:
        return [[FULL] * self.width for _ in range(self.height)]

    def line(self, grid: list[list[int]], axis: str, index: int):
        if axis == "row":
            return self.rows[index], list(grid[index])
        return self.columns[index], [row[index] for row in grid]


def validate_logic(value: object) -> Puzzle:
    obj = exact_keys(value, {
        "format", "width", "height", "colors", "empty", "rules",
        "initial_domain", "row_clues", "column_clues",
    })
    width = integer(obj["width"], 1, 100, "width")
    height = integer(obj["height"], 1, 100, "height")
    if obj["format"] != LOGIC_FORMAT or obj["colors"] != ["ink"]:
        raise InvalidInput("Only picross-logic-v1 with foreground ID ink is supported")
    rules = exact_keys(obj["rules"], {"id", "same_color_gap"})
    if (rules["id"] != "mono-gap-v1" or
            integer(rules["same_color_gap"], 1, 1, "same_color_gap") != 1):
        raise InvalidInput("Unsupported spacing rules")
    if obj["empty"] != "empty" or obj["initial_domain"] != ["empty", "ink"]:
        raise InvalidInput("Every cell must start with the full ordered domain")

    def lines(raw, count):
        if not isinstance(raw, list) or len(raw) != count:
            raise InvalidInput("Clue line count must match dimensions")
        result = []
        for line in raw:
            if not isinstance(line, list) or len(line) > 100:
                raise InvalidInput("Each line needs a list of at most 100 clues")
            lengths = []
            for clue in line:
                clue = exact_keys(clue, {"length", "color"})
                if clue["color"] != "ink":
                    raise InvalidInput("Unsupported clue color")
                lengths.append(integer(clue["length"], 1, 100, "clue length"))
            result.append(tuple(lengths))
        return tuple(result)

    # Overfull lines and disagreeing totals are logical contradictions, not syntax.
    return Puzzle(width, height, lines(obj["row_clues"], height),
                  lines(obj["column_clues"], width))


def load_json(path: Path, max_bytes: int = 8 * 1024 * 1024) -> object:
    def unique_pairs(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise InvalidInput(f"Duplicate JSON key: {key}")
            obj[key] = value
        return obj

    def reject_constant(value):
        raise InvalidInput(f"Non-JSON constant: {value}")

    with path.open("rb") as stream:
        data = stream.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise InvalidInput(f"Input exceeds {max_bytes} byte limit")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs,
                           parse_constant=reject_constant)
        # Keep parser acceptance and our canonical wire contract aligned. This
        # rejects data such as exponent overflow to inf or lone surrogates before
        # they can surface later as generic technical errors.
        canonical_bytes(value)
        return value
    except InvalidInput:
        raise
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise InvalidInput(f"Invalid or unsupported UTF-8 JSON: {exc}") from exc


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement prevents truncated files from appearing as complete output.
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(canonical_bytes(value) + b"\n")
    temp.replace(path)


class Budget:
    """Cooperative line-evaluation budget, separate from measured RSS limits."""

    def __init__(self, seconds: float = 120, max_lines: int = 100_000,
                 cancelled=None):
        if not math.isfinite(seconds) or seconds < 0:
            raise InvalidInput("Time budget must be finite and nonnegative")
        integer(max_lines, 0, 1_000_000, "max_lines")
        self.deadline = time.monotonic() + seconds
        self.max_lines = max_lines
        self.lines = 0
        self.cancelled = cancelled

    def check(self) -> None:
        if self.cancelled is not None and self.cancelled():
            raise Aborted("cancelled")
        if time.monotonic() >= self.deadline:
            raise Aborted("time_limit")

    def tick(self) -> None:
        self.check()
        if self.lines >= self.max_lines:
            raise Aborted("work_limit")
        self.lines += 1


def proof_header(puzzle: Puzzle) -> dict:
    return {"format": PROOF_FORMAT, "logic_hash": puzzle.logic_hash,
            "profile": dict(PROFILE), "profile_hash": digest(PROFILE)}
