"""Versioned wire contract and validation; no deduction routines live here."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
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
COLOR_LOGIC_FORMAT = "picross-logic-v2"
COLOR_PROOF_FORMAT = "picross-proof-v2"
MAX_COLORS = 8
COLOR_PROFILE = {**PROFILE, "id": "full-line-color"}
LOGIC_BYTE_LIMIT = 2 * 1024 * 1024
COLOR_PROOF_BYTE_LIMIT = 64 * 1024 * 1024


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


def domain_values(mask: int, colors: tuple[str, ...] = ("ink",)) -> list[str]:
    return [name for i, name in enumerate(("empty", *colors)) if mask & (1 << i)]


def wire_grid(grid: list[list[int]], colors: tuple[str, ...] = ("ink",)) -> list[list[list[str]]]:
    return [[domain_values(mask, colors) for mask in row] for row in grid]


@dataclass(frozen=True)
class Clue:
    length: int
    color: int  # Single domain bit, allocated from the normalized palette.


@dataclass(frozen=True)
class Puzzle:
    width: int
    height: int
    rows: tuple[tuple[int | Clue, ...], ...]
    columns: tuple[tuple[int | Clue, ...], ...]
    colors: tuple[str, ...] = ("ink",)
    format: str = LOGIC_FORMAT

    @property
    def full_domain(self) -> int:
        return (1 << (len(self.colors) + 1)) - 1

    @property
    def profile(self) -> dict:
        return dict(PROFILE if self.format == LOGIC_FORMAT else COLOR_PROFILE)

    @property
    def proof_format(self) -> str:
        return PROOF_FORMAT if self.format == LOGIC_FORMAT else COLOR_PROOF_FORMAT

    @property
    def max_proof_steps(self) -> int:
        # Every step removes at least one value, and every cell retains >=1.
        return self.width * self.height * len(self.colors)

    @property
    def proof_byte_limit(self) -> int:
        return 8 * 1024 * 1024 if self.format == LOGIC_FORMAT else COLOR_PROOF_BYTE_LIMIT

    def to_wire(self) -> dict:
        def clues(lines):
            return [[{"length": clue.length if isinstance(clue, Clue) else clue,
                      "color": self.colors[clue.color.bit_length() - 2]
                      if isinstance(clue, Clue) else "ink"} for clue in line]
                    for line in lines]
        return {
            "format": self.format, "width": self.width, "height": self.height,
            "colors": list(self.colors), "empty": "empty",
            "rules": ({"id": "mono-gap-v1", "same_color_gap": 1}
                      if self.format == LOGIC_FORMAT else
                      {"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0}),
            "initial_domain": ["empty", *self.colors],
            "row_clues": clues(self.rows), "column_clues": clues(self.columns),
        }

    @property
    def logic_hash(self) -> str:
        return digest(self.to_wire())

    def unknown_grid(self) -> list[list[int]]:
        return [[self.full_domain] * self.width for _ in range(self.height)]

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
    mono = obj["format"] == LOGIC_FORMAT
    if not mono and obj["format"] != COLOR_LOGIC_FORMAT:
        raise InvalidInput("Unsupported logic format")
    raw_colors = obj["colors"]
    if (not isinstance(raw_colors, list) or not 1 <= len(raw_colors) <= MAX_COLORS or
            any(not isinstance(c, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", c)
                or c == "empty" for c in raw_colors) or len(set(raw_colors)) != len(raw_colors)):
        raise InvalidInput("Expected 1..8 unique foreground IDs, 1..32 ASCII characters")
    if mono and raw_colors != ["ink"]:
        raise InvalidInput("picross-logic-v1 requires foreground ID ink")
    colors = tuple(sorted(raw_colors))
    rules = exact_keys(obj["rules"], {"id", "same_color_gap"} if mono else
                       {"id", "same_color_gap", "different_color_gap"})
    if (rules["id"] != ("mono-gap-v1" if mono else "color-gap-v1") or
            integer(rules["same_color_gap"], 1, 1, "same_color_gap") != 1):
        raise InvalidInput("Unsupported spacing rules")
    if not mono:
        integer(rules["different_color_gap"], 0, 0, "different_color_gap")
    if obj["empty"] != "empty" or obj["initial_domain"] != ["empty", *raw_colors]:
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
                if clue["color"] not in colors:
                    raise InvalidInput("Unsupported clue color")
                length = integer(clue["length"], 1, 100, "clue length")
                lengths.append(length if mono else Clue(length, 1 << (colors.index(clue["color"]) + 1)))
            result.append(tuple(lengths))
        return tuple(result)

    # Overfull lines and disagreeing totals are logical contradictions, not syntax.
    return Puzzle(width, height, lines(obj["row_clues"], height),
                  lines(obj["column_clues"], width), colors, obj["format"])


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
    return {"format": puzzle.proof_format, "logic_hash": puzzle.logic_hash,
            "profile": puzzle.profile, "profile_hash": digest(puzzle.profile)}
