"""SD wire data, budgets and pure measurement reducers; no line deductions."""
from __future__ import annotations

from .contract import (Aborted, Budget, InvalidInput, canonical_bytes, digest,
                       exact_keys, integer)

ANALYZER = "picross-sd-analyzer-1"
RULES = "sd-rules-1"
TRACE = "picross-analysis-trace-v1"
REPORT = "picross-analysis-report-v1"
BYTE_LIMIT = 64 * 1024 * 1024
RULE_IDS = ("R0-empty", "R0-packed", "R0-cleanup", "R1-overlap",
            "R1-anchored", "R2-segments", "R3-support")
REASONS = ("time_limit", "work_limit", "rule_work_limit", "wave_limit",
           "trace_byte_limit", "cancelled", "memory_limit")


class AnalysisBudget(Budget):
    def __init__(self, seconds=120, max_lines=100_000, max_rule_work=20_000_000,
                 max_waves=80_000, cancelled=None, **kwargs):
        super().__init__(seconds, max_lines, cancelled, **kwargs)
        self.seconds = seconds
        self.max_rule_work = integer(max_rule_work, 0, 100_000_000, "max_rule_work")
        self.max_waves = integer(max_waves, 0, 80_000, "max_waves")
        self.rule_work = 0

    def work(self):
        self.check()
        if self.rule_work >= self.max_rule_work:
            raise Aborted("rule_work_limit")
        self.rule_work += 1

    def limits(self):
        return {"seconds": self.seconds, "max_lines": self.max_lines,
                "max_rule_work": self.max_rule_work, "max_waves": self.max_waves,
                "max_pair_work": self.max_pair_work, "max_pair_records": self.max_pair_records}

    def usage(self):
        return {"lines": self.lines, "rule_work": self.rule_work,
                "pair_work": self.pair_work, "pair_peak_records": self.pair_peak_records}


def parameters(value=None):
    if value is None:
        return {"aggregation": None}
    obj = exact_keys(value, {"aggregation"})
    agg = obj["aggregation"]
    if agg is not None:
        exact_keys(agg, {"format", "min_family", "max_productive_fraction", "cleanup_remaining_cells"})
        if agg["format"] != "sd-aggregation-1":
            raise InvalidInput("Unknown aggregation contract")
        integer(agg["min_family"], 0, 3, "min_family")
        integer(agg["cleanup_remaining_cells"], 0, 10000, "cleanup_remaining_cells")
        fraction = agg["max_productive_fraction"]
        if not isinstance(fraction, list) or len(fraction) != 2:
            raise InvalidInput("Expected [numerator, denominator]")
        integer(fraction[1], 1, 1_000_000, "denominator")
        integer(fraction[0], 0, fraction[1], "numerator")
    # Detach mutable caller configuration from the recorded result.
    import json
    return json.loads(canonical_bytes(obj))


def analysis_input(puzzle):
    return {"format": "picross-analysis-input-v1", "logic": puzzle.to_wire()}


def header(puzzle, config):
    return {"format": TRACE, "analysis_hash": digest(analysis_input(puzzle)),
            "analyzer": ANALYZER, "rules": RULES, "parameters": parameters(config)}


def line_event(axis, index, domains, deductions):
    rules = []
    for name in RULE_IDS:
        if name not in deductions:
            continue
        changes = [{"offset": p, "before": old, "after": new}
                   for p, (old, new) in enumerate(zip(domains, deductions[name])) if old != new]
        if changes:
            rules.append({"rule": name, "changes": changes})
    return {"axis": axis, "index": index, "rules": rules}


def combined_changes(grid, events):
    after = {}
    for event in events:
        for rule in event["rules"]:
            for change in rule["changes"]:
                p = change["offset"]
                y, x = (event["index"], p) if event["axis"] == "row" else (p, event["index"])
                after[y, x] = after.get((y, x), grid[y][x]) & change["after"]
    return [{"row": y, "column": x, "before": grid[y][x], "after": value}
            for (y, x), value in sorted(after.items()) if grid[y][x] != value]


def apply_changes(grid, changes):
    result = [list(row) for row in grid]
    for c in changes:
        result[c["row"]][c["column"]] = c["after"]
    return result


def measurements(puzzle, trace):
    """Reduce already checked trace data, retaining exact integer numerators."""
    grid = puzzle.unknown_grid()
    seen, partial_seen = set(), set()
    family_waves = {f"R{i}": 0 for i in range(4)}
    family_lines = dict(family_waves)
    rule_counts = dict.fromkeys(RULE_IDS, 0)
    series = []
    simple = direct = singletons = total_changes = total_removed = 0
    for wave in trace["waves"]:
        changes = wave["changes"]
        positions = {(c["row"], c["column"]) for c in changes}
        partial = {(c["row"], c["column"]) for c in changes if c["after"].bit_count() > 1}
        new_singletons = sum(c["after"].bit_count() == 1 for c in changes)
        open_by_axis = {
            "row": sum(any(d.bit_count() > 1 for d in row) for row in grid),
            "column": sum(any(d.bit_count() > 1 for d in col) for col in zip(*grid))}
        productive = {axis: sum(e["axis"] == axis for e in wave["lines"])
                      for axis in ("row", "column")}
        removed = sum(c["before"].bit_count() - c["after"].bit_count() for c in changes)
        series.append({"family": wave["family"], "open_lines": open_by_axis,
            "productive_lines": productive,
            "productive_fraction": [sum(productive.values()), sum(open_by_axis.values())],
            "open_cells_before": sum(d.bit_count() > 1 for row in grid for d in row),
            "changed_cells": len(changes), "first_changed_cells": len(positions - seen),
            "new_singletons": new_singletons, "partial_changes": len(partial),
            "removed_values": removed,
            "domain_cardinalities": sorted([[c["before"].bit_count(), c["after"].bit_count()]
                                             for c in changes])})
        seen |= positions
        partial_seen |= partial
        family_waves[wave["family"]] += 1
        family_lines[wave["family"]] += len(wave["lines"])
        for event in wave["lines"]:
            for rule in event["rules"]:
                rule_counts[rule["rule"]] += 1
        if wave["family"] <= "R1":
            simple += new_singletons
        if wave["family"] == "R0":
            direct += new_singletons
        singletons += new_singletons
        total_changes += len(changes)
        total_removed += removed
        grid = apply_changes(grid, changes)
    agg = trace["parameters"]["aggregation"]
    aggregation = None
    if agg is not None:
        durations = []
        duration = 0
        a, b = agg["max_productive_fraction"]
        for wave in series:
            p, q = wave["productive_fraction"]
            if int(wave["family"][1]) >= agg["min_family"] and p * b <= q * a:
                duration += 1
            elif duration:
                durations.append(duration)
                duration = 0
        if duration:
            durations.append(duration)
        cleanup = 0
        for wave in reversed(series) if trace["status"] == "solved" else ():
            if wave["family"] != "R0" or wave["open_cells_before"] > agg["cleanup_remaining_cells"]:
                break
            cleanup += 1
        aggregation = {"bottleneck_phases": len(durations), "durations": durations,
            "bottleneck_waves": sum(durations), "longest_bottleneck": max(durations, default=0),
            "cleanup_suffix_waves": cleanup}
    area = puzzle.width * puzzle.height
    clue_count = {axis: sum(len(line) for line in lines)
                  for axis, lines in (("row", puzzle.rows), ("column", puzzle.columns))}
    from .contract import Clue
    clue_load = {axis: sum(c.length if isinstance(c, Clue) else c for line in lines for c in line)
                for axis, lines in (("row", puzzle.rows), ("column", puzzle.columns))}
    return {"waves": series, "wave_count": len(series), "family_waves": family_waves,
        "family_line_applications": family_lines, "rule_applications": rule_counts,
        "highest_family_used": max((w["family"] for w in trace["waves"]), default=None),
        "unique_changed_cells": len(seen), "unique_partial_cells": len(partial_seen),
        "cell_change_events": total_changes, "new_singletons": singletons,
        "partial_change_events": total_changes - singletons, "removed_values": total_removed,
        "simple_fraction_all_cells": [simple, area], "simple_fraction_determined": [simple, singletons],
        "r0_fraction_all_cells": [direct, area], "aggregation": aggregation,
        "workload": {"width": puzzle.width, "height": puzzle.height, "cells": area,
                     "colors": len(puzzle.colors), "clue_count": clue_count,
                     "clue_length_sum": clue_load,
                     "total_clues": sum(clue_count.values()), "total_clue_length": sum(clue_load.values())}}


def result_data(puzzle, trace, r4=None):
    metrics = measurements(puzzle, trace)
    status = trace["status"]
    return {"analysis_hash": trace["analysis_hash"], "analyzer": ANALYZER, "rules": RULES,
        "parameters": trace["parameters"], "trace_hash": digest(trace), "status": status,
        "reason": trace["reason"], "line_analysis_complete": status == "solved",
        "line_fixpoint_confirmed": status in ("solved", "stalled"),
        "metrics": metrics, "r4": r4,
        "deduction_complete": status == "solved" or bool(r4 and r4["proof_status"] == "solved"),
        "method": None, "level": None, "confidence": None, "estimated_minutes": None,
        "explanation": (f"Linienanalyse {status}: {metrics['wave_count']} synchrone Wellen; "
                        f"{metrics['new_singletons']}/{puzzle.width * puzzle.height} Zellen bestimmt. "
                        f"Höchste eingesetzte Linienfamilie: {metrics['highest_family_used'] or 'keine'}; "
                        f"{metrics['partial_change_events']} partielle Domainänderungen. "
                        f"R4-Notwendigkeit: {r4['necessity'] if r4 else 'nicht untersucht'}. "
                        "Keine kalibrierte Schwierigkeitsstufe (SD-B ausstehend).")}
