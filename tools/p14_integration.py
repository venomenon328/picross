"""Deterministic P1.4 input plan and an independent, contract-level oracle.

The oracle deliberately does not import or translate the Godot Gesture/Player code.
It applies the documented start-cell modes to integer coordinates and compares a
trace emitted by the running scene after each completed UI action.
"""
from __future__ import annotations

import json
import hashlib
import os
import platform
import tempfile
from collections import Counter
from pathlib import Path

REGIONS = ((2, 2), (45, 2), (88, 2), (2, 45), (45, 45),
           (88, 45), (2, 88), (45, 88), (88, 88), (45, 65))
WIDTH = HEIGHT = 100


def build_plan() -> list[dict]:
    """Ten 50-action visits: 41 edits, 6 navigation actions, 3 history actions.

    The final visit replaces its last edit with Undo, preserving a real Redo
    branch for the independent process restart.
    """
    result: list[dict] = []
    for region, (bx, by) in enumerate(REGIONS):
        block: list[dict] = [{"kind": "mini", "point": [min(bx + 4, 96), min(by + 4, 96)]}]
        for j in range(33):
            block.append(_edit(bx, by, j))
        block += [
            {"kind": "pan", "delta": [-60 if bx < 45 else 60, -40 if by < 45 else 40]},
            {"kind": "zoom", "direction": 1},
            {"kind": "zoom", "direction": -1},
            {"kind": "hint", "axis": "row", "index": by + 3, "slots": 1.2},
            {"kind": "hint", "axis": "column", "index": bx + 3, "slots": 1.2},
            {"kind": "undo"}, {"kind": "redo"}, {"kind": "undo"},
            {"kind": "cell", "start": [bx, by + 6], "end": [bx, by + 6],
             "button": "right", "tool": "fill", "color": 1, "purpose": "redo branch"},
        ]
        for j in range(33, 40):
            block.append(_edit(bx, by, j))
        if region == len(REGIONS) - 1:
            block[-1] = {"kind": "undo", "purpose": "restart redo"}
        assert len(block) == 50
        for item in block:
            result.append({"number": len(result) + 1, "region": region + 1, **item})
    assert len(result) == 500
    return result


def _edit(bx: int, by: int, j: int) -> dict:
    x, y = bx + j % 8, by + j // 8
    if j == 30:
        return {"kind": "cell", "start": [bx, by], "end": [bx, by],
                "button": "left", "tool": "erase", "color": 1, "purpose": "eraser"}
    if j == 31:
        x, y = bx + 1, by
    if j == 32:
        x, y = bx + 2, by
    pattern = j % 5
    button = "right" if pattern in (1, 3) or j == 32 else "left"
    dx, dy = (4, 0) if pattern in (0, 2, 3) else (0, 7 if pattern == 4 else 3)
    if j >= 30:
        dx, dy = 0, 0
    end = [x + dx, y + dy]
    action = {"kind": "cell", "start": [x, y], "end": end,
              "button": button, "tool": "fill", "color": 1 + (j // 10) % 4,
              "purpose": ("elastic" if pattern == 2 and j < 30 else "stroke")}
    if pattern == 2 and j < 30:
        action["via"] = [x + 4, y]
        action["end"] = [x + 2, y]
    return action


class Oracle:
    def __init__(self) -> None:
        self.cells = [-1] * (WIDTH * HEIGHT)
        self.history: list[list[dict]] = []
        self.cursor = 0
        self.undo_used = False

    def step(self, action: dict) -> list[dict]:
        kind = action["kind"]
        if kind == "undo":
            if not self.cursor:
                raise AssertionError(f"action {action['number']}: empty Undo")
            self.cursor -= 1
            changes = [{"index": c["index"], "before": c["after"], "after": c["before"]}
                       for c in self.history[self.cursor]]
            self.undo_used = True
        elif kind == "redo":
            if self.cursor == len(self.history):
                raise AssertionError(f"action {action['number']}: empty Redo")
            changes = self.history[self.cursor]
            self.cursor += 1
        elif kind == "cell":
            sx, sy = action["start"]
            ex, ey = action["end"]
            assert sx == ex or sy == ey
            start = self.cells[sy * WIDTH + sx]
            button = action["button"]
            erase = action["tool"] == "erase" and button == "left"
            target = -1 if erase else (0 if button == "right" else action["color"])
            remove_fill = target > 0 and start > 0
            remove_empty = target == 0 and start == 0
            if remove_fill or remove_empty:
                target = -1
            changes = []
            for y in range(min(sy, ey), max(sy, ey) + 1):
                for x in range(min(sx, ex), max(sx, ex) + 1):
                    index = y * WIDTH + x
                    before = self.cells[index]
                    eligible = (erase and before != -1 or remove_fill and before > 0
                                or remove_empty and before == 0 or not (erase or remove_fill or remove_empty)
                                and (before in (-1, 0) if target > 0 else before == -1 or before > 0))
                    if eligible and before != target:
                        changes.append({"index": index, "before": before, "after": target})
            if not changes:
                raise AssertionError(f"action {action['number']}: ineffective cell gesture: {action}")
            self.history = self.history[:self.cursor] + [changes]
            self.cursor += 1
        else:
            changes = []
        for change in changes:
            index = change["index"]
            if self.cells[index] != change["before"]:
                raise AssertionError(f"action {action['number']}: oracle precondition at {index}")
            self.cells[index] = change["after"]
        return changes


def validate_trace(plan: list[dict], trace_path: Path, expected_override: dict | None = None) -> dict:
    actual = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    if len(actual) != len(plan):
        raise AssertionError(f"incomplete trace: expected {len(plan)} actions, got {len(actual)}")
    oracle = Oracle()
    categories = Counter()
    for action, observed in zip(plan, actual, strict=True):
        n = action["number"]
        expected_changes = oracle.step(action)
        if expected_override and n in expected_override:
            expected_changes = expected_override[n]
        expected = {"number": n, "kind": action["kind"], "changes": expected_changes,
                    "cursor": oracle.cursor, "history_size": len(oracle.history),
                    "undo_used": oracle.undo_used,
                    "history_tail": oracle.history[-1] if oracle.history else [],
                    "redo_next": oracle.history[oracle.cursor] if oracle.cursor < len(oracle.history) else []}
        for key, value in expected.items():
            if observed.get(key) != value:
                raise AssertionError(f"action {n} {action}: {key} expected {value!r}, got {observed.get(key)!r}")
        categories[action["kind"]] += 1
    return {"actions": len(plan), "categories": dict(categories), "cells": oracle.cells,
            "history": oracle.history, "cursor": oracle.cursor, "undo_used": oracle.undo_used}


def write_plan(path: Path) -> list[dict]:
    plan = build_plan()
    path.write_text(json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return plan


def verify_navigation(plan: list[dict], trace_path: Path) -> None:
    """Check valid views, navigational isolation, and individual clue identities."""
    trace = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    assert len(trace) == 500
    previous = None
    visited_regions = set()
    for action, item in zip(plan, trace, strict=True):
        n = action["number"]
        view = item["view"]
        x, y = view["center"]
        zoom = view["cell_size"]
        left, top, width, height = view["viewport"]
        if not (0 <= x <= WIDTH and 0 <= y <= HEIGHT and 12 <= zoom <= 72 and
                0 <= left < left + width <= 1600 and 0 <= top < top + height <= 900):
            raise AssertionError(f"action {n}: invalid view {view}")
        if action["kind"] == "mini":
            visited_regions.add(action["region"])
            half_x, half_y = width / (2 * zoom), height / (2 * zoom)
            want_x = min(max(action["point"][0], half_x), WIDTH - half_x)
            want_y = min(max(action["point"][1], half_y), HEIGHT - half_y)
            if abs(x - want_x) > 0.02 or abs(y - want_y) > 0.02:
                raise AssertionError(f"action {n}: miniature target {action['point']} expected {(want_x,want_y)}, got {(x,y)}")
        if previous:
            if action["kind"] == "pan":
                px, py = previous["view"]["center"]
                dx, dy = action["delta"]
                half_x, half_y = width / (2 * zoom), height / (2 * zoom)
                want_x = min(max(px - dx / zoom, half_x), WIDTH - half_x)
                want_y = min(max(py - dy / zoom, half_y), HEIGHT - half_y)
                if abs(x - want_x) > 0.02 or abs(y - want_y) > 0.02 or (x, y) == (px, py):
                    raise AssertionError(f"action {n}: grid pan expected {(want_x,want_y)}, got {(x,y)}")
            if action["kind"] == "zoom":
                steps = (12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 44, 48, 54, 60, 66, 72)
                before = previous["view"]["cell_size"]
                choices = [v for v in steps if v > before] if action["direction"] > 0 else [v for v in steps if v < before]
                expected_zoom = min(choices) if action["direction"] > 0 else max(choices)
                if zoom != expected_zoom:
                    raise AssertionError(f"action {n}: zoom expected {expected_zoom}, got {zoom}")
            rows_before, cols_before = previous["row_reads"], previous["column_reads"]
            rows, cols = item["row_reads"], item["column_reads"]
            if action["kind"] == "hint":
                axis, index = action["axis"], action["index"]
                current, old = (rows, rows_before) if axis == "row" else (cols, cols_before)
                other, old_other = (cols, cols_before) if axis == "row" else (rows, rows_before)
                if other != old_other or any(current[i] != old[i] for i in range(100) if i != index):
                    raise AssertionError(f"action {n}: clue drag altered a neighbour or opposite axis")
                read = current[index]
                if read == old[index] or read.get("anchor") != "middle" or not (0 <= read["start"] < read["end"] <= 100):
                    raise AssertionError(f"action {n}: wrong semantic target read {old[index]} -> {read}")
            elif rows != rows_before or cols != cols_before:
                raise AssertionError(f"action {n}: non-clue action changed semantic clue reads")
        previous = item
    if len(visited_regions) != 10:
        raise AssertionError(f"only {len(visited_regions)} of 10 distant regions visited")


def verify_negative_controls(plan: list[dict], trace_path: Path) -> None:
    first_change = next(a["number"] for a in plan if a["kind"] == "cell")
    try:
        validate_trace(plan, trace_path, {first_change: []})
    except AssertionError as exc:
        if f"action {first_change}" not in str(exc):
            raise
    else:
        raise AssertionError("tampered expectation unexpectedly passed")
    with tempfile.TemporaryDirectory(prefix="p14-negative-") as directory:
        incomplete = Path(directory) / "incomplete.jsonl"
        lines = trace_path.read_text(encoding="utf-8").splitlines()
        incomplete.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        try:
            validate_trace(plan, incomplete)
        except AssertionError as exc:
            if "incomplete trace" not in str(exc):
                raise
        else:
            raise AssertionError("incomplete trace unexpectedly passed")


def _stats(values: list[int]) -> dict:
    ordered = sorted(values)
    return {"count": len(values), "median_us": ordered[len(ordered) // 2],
            "p95_us": ordered[min(len(ordered) - 1, int(len(ordered) * .95))],
            "max_us": ordered[-1]}


def summarize(plan: list[dict], trace_path: Path, final: dict, host: str) -> dict:
    trace = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    by_kind = {kind: _stats([r["dispatch_us"] for r in trace if r["kind"] == kind])
               for kind in sorted({r["kind"] for r in trace})}
    frame_by_kind = {kind: _stats([r["frame_wait_us"] for r in trace if r["kind"] == kind])
                     for kind in by_kind}
    oracle = Oracle()
    for action in plan:
        oracle.step(action)
    return {"schema": 1, "plan": "ten deterministic 50-action regions; no random seed",
            "actions": len(plan), "categories": dict(Counter(a["kind"] for a in plan)),
            "region_origins": REGIONS, "unique_changed_cells": len({c["index"] for r in trace for c in r["changes"]}),
            "final_non_unknown_cells": sum(v != -1 for v in oracle.cells),
            "final_cursor": oracle.cursor, "final_history_size": len(oracle.history),
            "final_cells_sha256": hashlib.sha256(json.dumps(oracle.cells, separators=(",", ":")).encode()).hexdigest(),
            "host": {"os": host, "platform": platform.platform(), "machine": platform.machine(),
                     "processor": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unavailable")},
            "engine": final["engine"], "renderer": final["renderer"],
            "logical_window": [1600, 900], "ui_scale": 1.0, "work_zoom_range": [24, 26],
            "save_profile": "P1_TEST_SAVE_ROOT isolated per product run; normal SaveStore writes enabled",
            "input_cadence": "synthetic viewport Down/Move/Up for Board, local Miniature._gui_input for miniature, button signals for Undo/Redo; one rendered process frame between completed actions",
            "warmup": "scene creation plus four frames before action 1, excluded from action timing",
            "measurement_boundary": "dispatch_us sums synchronous event/command calls including normal save I/O; frame_wait_us is separate scheduled frame time; trace/assertion writing excluded; neither is physical input latency",
            "dispatch_by_category_us": by_kind, "frame_wait_by_category_us": frame_by_kind,
            "dispatch_outliers": [{"number": r["number"], "kind": r["kind"], "dispatch_us": r["dispatch_us"]}
                                  for r in sorted(trace, key=lambda r: r["dispatch_us"], reverse=True)[:10]],
            "negative_controls": ["tampered expected change failed at its action number", "499-action trace rejected"],
            "restart": "real separate Godot process; full oracle cells/history/cursor/redo and recorded view/semantic reads checked"}
