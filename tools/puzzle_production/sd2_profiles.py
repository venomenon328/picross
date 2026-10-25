"""Reproducible raw profiles from checked SD2 waves, never a difficulty grade."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction

from .analysis_contract import apply_changes
from .contract import Clue
from .sd2_contract import AnalysisBudget, RULE_IDS


def ratio(numerator, denominator=1):
    if not denominator:
        return None
    value = Fraction(numerator, denominator)
    return [value.numerator, value.denominator]


def blocks_of(clues):
    return [(c.length, c.color) if isinstance(c, Clue) else (c, 2) for c in clues]


def histogram(values):
    return {str(k): v for k, v in sorted(Counter(values).items())}


def structure(puzzle):
    blocks = [blocks_of(line) for line in (*puzzle.rows, *puzzle.columns)]
    lengths = [length for line in blocks for length, _ in line]
    gaps = [sum(a[1] == b[1] for a, b in zip(line, line[1:])) for line in blocks]
    dimensions = [puzzle.width] * puzzle.height + [puzzle.height] * puzzle.width
    return {"width": puzzle.width, "height": puzzle.height,
            "cells": puzzle.width * puzzle.height, "colors": len(puzzle.colors),
            "total_clues": len(lengths), "total_clue_length": sum(lengths),
            "clue_length_histogram": histogram(lengths),
            "short_blocks": sum(n <= 2 for n in lengths),
            "adjacent_color_changes": sum(a[1] != b[1] for line in blocks for a, b in zip(line, line[1:])),
            "mandatory_gaps": sum(gaps),
            "geometric_slack": sum(max(0, n - sum(b[0] for b in line) - gap)
                                   for n, line, gap in zip(dimensions, blocks, gaps))}


def state_signals(puzzle, grid, budget):
    """Local placement census only; never returns deductions to the engine."""
    result = dict.fromkeys(("open_lines", "solved_lines", "open_cells", "local_candidates",
                           "geometric_candidates", "ambiguous_required_cells",
                           "unique_owner_required_cells", "restricted_cells", "open_blocks",
                           "open_short_blocks", "undetermined_blocks", "undetermined_short_blocks"), 0)
    free_local = free_geometry = 0
    hint_colors = set()
    for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
        for index in range(count):
            budget.check()
            clues, domains = puzzle.line(grid, axis, index)
            if all(d.bit_count() == 1 for d in domains):
                result["solved_lines"] += 1
                continue
            result["open_lines"] += 1
            result["restricted_cells"] += sum(d != puzzle.full_domain for d in domains)
            blocks = blocks_of(clues)
            result["open_blocks"] += len(blocks)
            result["open_short_blocks"] += sum(length <= 2 for length, _ in blocks)
            hint_colors.update(color for _, color in blocks)
            gaps = [int(a[1] == b[1]) for a, b in zip(blocks, blocks[1:])]
            owners = [set() for _ in domains]
            for i, (length, color) in enumerate(blocks):
                lower = sum(b[0] for b in blocks[:i]) + sum(gaps[:i])
                upper = len(domains) - sum(b[0] for b in blocks[i:]) - sum(gaps[i:])
                geometry = max(0, upper - lower + 1)
                local = 0
                for start in range(lower, upper + 1):
                    budget.work()
                    end = start + length
                    if any(not domains[p] & color for p in range(start, end)):
                        continue
                    if any(domains[p] == color for p in (start - 1, end) if 0 <= p < len(domains)):
                        continue
                    if i and gaps[i-1] and (start == 0 or not domains[start-1] & 1):
                        continue
                    if i < len(gaps) and gaps[i] and (end == len(domains) or not domains[end] & 1):
                        continue
                    local += 1
                    for p in range(start, end):
                        owners[p].add(i)
                result["geometric_candidates"] += geometry
                result["local_candidates"] += local
                result["undetermined_blocks"] += local > 1
                result["undetermined_short_blocks"] += local > 1 and length <= 2
                free_geometry += max(0, geometry - 1)
                free_local += max(0, local - 1)
            for domain, possible in zip(domains, owners):
                if not domain & 1:
                    result["ambiguous_required_cells"] += len(possible) > 1
                    result["unique_owner_required_cells"] += len(possible) == 1
    cells = [d for row in grid for d in row if d.bit_count() > 1]
    result["open_cells"] = len(cells)
    result["open_hint_colors"] = len(hint_colors)
    result["placement_freedom"] = ratio(free_local, free_geometry)
    result["color_options"] = ratio(sum((d & ~1).bit_count() for d in cells),
                                    len(cells) * len(puzzle.colors))
    return result


def span_signals(changes):
    filled = {(c["row"], c["column"]): c["after"] for c in changes
              if c["after"] > 1 and c["after"].bit_count() == 1}
    empty = {(c["row"], c["column"]): 1 for c in changes if c["after"] == 1}

    def lengths(cells, dy, dx):
        runs = []
        for (y, x), value in cells.items():
            if cells.get((y-dy, x-dx)) == value:
                continue
            length = 1
            while cells.get((y+length*dy, x+length*dx)) == value:
                length += 1
            runs.append(length)
        return runs

    horizontal, vertical = lengths(filled, 0, 1), lengths(filled, 1, 0)
    return {"filled_singletons": len(filled), "empty_singletons": len(empty),
            "fill_spans": min(len(horizontal), len(vertical)),
            "empty_spans": min(len(lengths(empty, 0, 1)), len(lengths(empty, 1, 0))),
            "isolated_fills": sum(all(filled.get((y+dy, x+dx)) != value
                                      for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                                  for (y, x), value in filled.items()),
            "fill_run_lengths": histogram(horizontal + vertical)}


def bottlenecks(series):
    phases = []
    for index, wave in enumerate(series):
        if not wave["bottleneck"]:
            continue
        if not phases or phases[-1]["end"] != index:
            phases.append({"start": index, "end": index, "duration": 0,
                           "stage": "early" if Fraction(*wave["progress_before"]) < Fraction(1, 2) else "late",
                           "peak_strain": [0, 1]})
        phase = phases[-1]
        phase["end"] = index + 1
        phase["duration"] += 1
        phase["peak_strain"] = ratio(max(Fraction(*phase["peak_strain"]), Fraction(*wave["strain"])))
    return phases


def profiles(puzzle, trace, budget=None):
    """Pure measurement semantics; callers must validate the trace separately."""
    budget = budget if budget is not None else AnalysisBudget()
    grid = puzzle.unknown_grid()
    area, colors = puzzle.width * puzzle.height, len(puzzle.colors)
    families = {f"E{i}": 0 for i in range(4)}
    demand = {"highest_family": None, "family_waves": dict(families),
              "family_line_applications": dict(families), "rule_applications": dict.fromkeys(RULE_IDS, 0),
              "information_by_family": {}, "strong_information_fraction": None, "trajectory": []}
    information = dict(families)
    search = {"trajectory": []}
    workload = {"structure": structure(puzzle), "trajectory": []}
    seen, partial_seen = set(), set()
    determined = 0
    for wave in trace["waves"]:
        budget.check()
        changes, family = wave["changes"], wave["family"]
        positions = {(c["row"], c["column"]) for c in changes}
        partial = {(c["row"], c["column"]) for c in changes if c["after"].bit_count() > 1}
        singletons = len(changes) - len(partial)
        removed = sum(c["before"].bit_count() - c["after"].bit_count() for c in changes)
        state = state_signals(puzzle, grid, budget)
        productive = 0
        restricted_context = interacting = 0
        for event in wave["lines"]:
            clues, domains = puzzle.line(grid, event["axis"], event["index"])
            productive += any(d.bit_count() > 1 for d in domains)
            restricted_context += sum(d != puzzle.full_domain for d in domains)
            interacting += len(clues)
            for rule in event["rules"]:
                demand["rule_applications"][rule["rule"]] += 1
        offer = Fraction(productive, state["open_lines"])
        gain = sum((Fraction(c["before"].bit_count() - c["after"].bit_count(),
                             c["before"].bit_count() - 1) for c in changes), Fraction()) / state["open_cells"]
        search["trajectory"].append({"offer": ratio(offer), "gain": ratio(gain),
            "changed_fraction": ratio(len(changes), state["open_cells"]),
            "singletons_per_productive_line": ratio(singletons, productive),
            "strain": ratio((1-offer)*(1-gain)), "progress_before": ratio(determined, area),
            "state": state, "bottleneck": offer <= Fraction(1, 4) and gain <= Fraction(1, 4)})
        demand["trajectory"].append({"family": family, "new_singletons": singletons,
            "partial_changes": len(partial), "restricted_context_cells": restricted_context,
            "interacting_blocks": interacting, "ambiguous_required_cells": state["ambiguous_required_cells"]})
        workload["trajectory"].append({"changed_cells": len(changes), "new_singletons": singletons,
            "partial_changes": len(partial), "removed_values": removed,
            "first_changed_cells": len(positions-seen), **span_signals(changes)})
        demand["family_waves"][family] += 1
        demand["family_line_applications"][family] += len(wave["lines"])
        information[family] += removed
        demand["highest_family"] = max(demand["highest_family"] or family, family)
        seen |= positions
        partial_seen |= partial
        determined += singletons
        grid = apply_changes(grid, changes)
    demand["information_by_family"] = {f: ratio(n, area*colors) for f, n in information.items()}
    demand["strong_information_fraction"] = ratio(information["E2"] + information["E3"], area*colors)
    phases = bottlenecks(search["trajectory"])
    search.update(bottleneck_phases=phases, bottleneck_waves=sum(p["duration"] for p in phases),
                  longest_bottleneck=max((p["duration"] for p in phases), default=0),
                  peak_strain=ratio(max((Fraction(*w["strain"]) for w in search["trajectory"]), default=Fraction())))
    workload.update(unique_changed_cells=len(seen), unique_partial_cells=len(partial_seen),
                    cell_change_events=sum(w["changed_cells"] for w in workload["trajectory"]),
                    partial_change_events=sum(w["partial_changes"] for w in workload["trajectory"]))
    for key in ("new_singletons", "removed_values", "fill_spans", "empty_spans", "isolated_fills"):
        workload[key] = sum(w[key] for w in workload["trajectory"])
    budget.check()
    return {"demand": demand, "search": search, "workload": workload}
