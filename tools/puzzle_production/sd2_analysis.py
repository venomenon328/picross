"""Synchronous, weak-first SD analysis, with no target matrix or catalog access."""
from __future__ import annotations

from .sd2_contract import (AnalysisBudget, BYTE_LIMIT, apply_changes,
                                combined_changes, header, line_event, parameters)
from .sd2_rules import deductions
from .contract import Aborted, canonical_bytes, validate_logic


def next_wave(puzzle, grid, budget):
    for level in range(4):
        lines = []
        for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
            for index in range(count):
                budget.tick()
                clues, domains = puzzle.line(grid, axis, index)
                event = line_event(axis, index, domains, deductions(clues, domains, level, budget))
                if event["rules"]:
                    lines.append(event)
        budget.check()
        changes = combined_changes(grid, lines)
        if changes:
            return {"family": f"E{level}", "lines": lines, "changes": changes}
    return None


def analyze(puzzle, config=None, budget=None):
    """Return an untrusted trace; sd2_verifier must check it separately."""
    puzzle = validate_logic(puzzle.to_wire())
    config = parameters(config)
    budget = budget if budget is not None else AnalysisBudget()
    grid = puzzle.unknown_grid()
    waves = []
    trace = {**header(puzzle, config), "waves": waves, "status": "aborted",
             "reason": None, "terminal": None, "final_domains": grid}
    # Reserve room for header/end grid; per-wave byte charges precede mutation.
    byte_count = len(canonical_bytes(trace)) + 1024
    try:
        while True:
            wave = next_wave(puzzle, grid, budget)
            if wave is None:
                trace["status"] = "solved" if all(d.bit_count() == 1 for row in grid for d in row) else "stalled"
                break
            wave_bytes = len(canonical_bytes(wave)) + 1
            if byte_count + wave_bytes > BYTE_LIMIT:
                raise Aborted("trace_byte_limit")
            if any(c["after"] == 0 for c in wave["changes"]):
                trace.update(status="contradiction", terminal=wave)
                break
            if len(waves) >= budget.max_waves:
                raise Aborted("wave_limit")
            # Build first, then publish the entire new wave/grid together.
            updated = apply_changes(grid, wave["changes"])
            budget.check()
            waves.append(wave)
            grid = updated
            byte_count += wave_bytes
    except (Aborted, MemoryError, KeyboardInterrupt) as exc:
        reason = ("memory_limit" if isinstance(exc, MemoryError) else
                  "cancelled" if isinstance(exc, KeyboardInterrupt) else str(exc))
        trace.update(status="aborted", reason=reason, terminal=None)
    trace["final_domains"] = grid
    return trace
