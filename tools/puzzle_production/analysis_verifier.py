"""Independent SD rule/fixpoint checker; never imports the analysis generator."""
from __future__ import annotations

from .analysis_contract import (AnalysisBudget, REASONS, apply_changes, combined_changes,
                                header, line_event, parameters, result_data)
from .contract import Clue, InvalidInput, InvalidProof, digest, exact_keys
from .verifier import justified_support


def justified_rules(clues, domains, level, budget):
    """Interval-set derivation and simultaneous constraint elimination.

    No generator helpers or complete line support are used for R0--R2.
    A candidate is (block index, tuple of covered positions).
    """
    count = len(domains)
    blocks = [(c.length, c.color) if isinstance(c, Clue) else (c, 2) for c in clues]
    m = len(blocks)
    separator = lambda i: int(blocks[i][1] == blocks[i+1][1])
    packed_length = sum(b[0] for b in blocks) + sum(separator(i) for i in range(m-1))
    rules = {}
    if not clues:
        rules["R0-empty"] = [d & 1 for d in domains]
    if packed_length >= count:
        packed = [1] * count
        cursor = 0
        if packed_length == count:
            for i, (size, color) in enumerate(blocks):
                packed[cursor:cursor+size] = [color] * size
                cursor += size + (separator(i) if i + 1 < m else 0)
            rules["R0-packed"] = [d & p for d, p in zip(domains, packed)]
        else:
            rules["R0-packed"] = [0] * count
    runs = []
    p = 0
    while p < count:
        mask = domains[p]
        if mask <= 1 or mask.bit_count() != 1:
            p += 1
            continue
        end = p + 1
        while end < count and domains[end] == mask:
            end += 1
        runs.append((set(range(p, end)), mask))
        p = end
    if [(len(r), c) for r, c in runs] == blocks:
        occupied = set().union(*(r for r, _ in runs))
        rules["R0-cleanup"] = [d if p in occupied else d & 1 for p, d in enumerate(domains)]
    if level == 0 or packed_length > count:
        return rules

    candidates = []
    for i, (size, _) in enumerate(blocks):
        prefix = sum(b[0] for b in blocks[:i]) + sum(separator(j) for j in range(i))
        suffix = sum(b[0] for b in blocks[i+1:]) + sum(separator(j) for j in range(i, m-1))
        candidates.append([frozenset(range(s, s+size)) for s in range(prefix, count-suffix-size+1)])
    overlap = list(domains)
    for i, options in enumerate(candidates):
        for p in set.intersection(*(set(o) for o in options)):
            overlap[p] &= blocks[i][1]
    rules["R1-overlap"] = overlap
    anchored = list(domains)
    for run, color in runs:
        budget.work()
        owners = {i: [o for o in options if run <= o]
                  for i, options in enumerate(candidates) if blocks[i][1] == color}
        owners = {i: options for i, options in owners.items() if options}
        if not owners:
            anchored = [0] * count
            break
        if len(owners) != 1:
            continue
        options = next(iter(owners.values()))
        for p in set.intersection(*(set(o) for o in options)):
            anchored[p] &= color
        if len(options) == 1:
            for p in (min(options[0])-1, max(options[0])+1):
                if p in range(count):
                    anchored[p] &= ~color
    rules["R1-anchored"] = anchored
    if level == 1:
        return rules

    live = set()
    for i, options in enumerate(candidates):
        color = blocks[i][1]
        for cells in options:
            budget.work()
            left, right = min(cells)-1, max(cells)+1
            if not all(domains[p] & color for p in cells):
                continue
            if any(domains[p] == color for p in (left, right) if p in range(count)):
                continue
            required = []
            if i and separator(i-1):
                required.append(left)
            if i + 1 < m and separator(i):
                required.append(right)
            if any(p not in range(count) or not domains[p] & 1 for p in required):
                continue
            live.add((i, cells))
    while True:
        dead = set()
        by_block = [[cells for j, cells in live if i == j] for i in range(m)]
        impossible = any(not options for options in by_block)
        for i, cells in live:
            budget.work()
            if i and not any(max(prev) + separator(i-1) < min(cells) for prev in by_block[i-1]):
                dead.add((i, cells))
            if i + 1 < m and not any(max(cells) + separator(i) < min(nxt) for nxt in by_block[i+1]):
                dead.add((i, cells))
        for p, domain in enumerate(domains):
            if domain & 1:
                continue
            owners = set()
            for i, cells in live:
                budget.work()
                if p in cells:
                    owners.add(i)
            if not owners:
                impossible = True
            if len(owners) == 1:
                owner = next(iter(owners))
                dead.update((i, cells) for i, cells in live if i == owner and p not in cells)
        if impossible:
            rules["R2-segments"] = [0] * count
            break
        if not dead:
            projected = []
            for p, domain in enumerate(domains):
                supported = 1
                for i, options in enumerate(by_block):
                    if any(p in cells for cells in options):
                        supported |= blocks[i][1]
                    if all(p in cells for cells in options):
                        supported &= ~1
                projected.append(domain & supported)
            rules["R2-segments"] = projected
            break
        live -= dead
    if level == 3:
        rules["R3-support"] = justified_support(clues, domains)
    return rules


def expected_wave(puzzle, grid, budget):
    # Each tier is exhausted over both axes before accepting any progress.
    for strength in range(4):
        events = []
        for axis, lines in (("row", puzzle.rows), ("column", puzzle.columns)):
            for index, clues in enumerate(lines):
                domains = list(grid[index]) if axis == "row" else [row[index] for row in grid]
                budget.tick()
                allowed = justified_rules(clues, domains, strength, budget)
                event = line_event(axis, index, domains, allowed)
                if event["rules"]:
                    events.append(event)
        changes = combined_changes(grid, events)
        budget.check()
        if changes:
            return {"family": f"R{strength}", "lines": events, "changes": changes}
    return None


def verify_trace(puzzle, trace, budget=None):
    budget = budget if budget is not None else AnalysisBudget()
    obj = exact_keys(trace, {"format", "analysis_hash", "analyzer", "rules", "parameters",
                            "waves", "status", "reason", "terminal", "final_domains"}, InvalidProof)
    try:
        config = parameters(obj["parameters"])
    except InvalidInput as exc:
        raise InvalidProof(str(exc)) from exc
    for key, value in header(puzzle, config).items():
        if digest(obj[key]) != digest(value):
            raise InvalidProof(f"Wrong SD binding: {key}")
    if not isinstance(obj["waves"], list) or len(obj["waves"]) > puzzle.max_proof_steps:
        raise InvalidProof("Invalid SD wave count")
    grid = puzzle.unknown_grid()
    for index, wave in enumerate(obj["waves"]):
        if index >= budget.max_waves:
            from .contract import Aborted
            raise Aborted("wave_limit")
        expected = expected_wave(puzzle, grid, budget)
        if expected is None or any(c["after"] == 0 for c in expected["changes"]):
            raise InvalidProof("Progress claimed beyond a fixpoint or contradiction")
        if digest(wave) != digest(expected):
            raise InvalidProof("Wrong family, missing weaker progress or incomplete simultaneous deductions")
        grid = apply_changes(grid, expected["changes"])
    if digest(obj["final_domains"]) != digest(grid):
        raise InvalidProof("SD final domains differ from checked wave replay")
    status = obj["status"]
    if status == "aborted":
        if obj["reason"] not in REASONS or obj["terminal"] is not None:
            raise InvalidProof("Invalid SD abort record")
    else:
        if status not in ("solved", "stalled", "contradiction") or obj["reason"] is not None:
            raise InvalidProof("Invalid SD status/reason")
        expected = expected_wave(puzzle, grid, budget)
        if status == "contradiction":
            if expected is None or not any(c["after"] == 0 for c in expected["changes"]):
                raise InvalidProof("No independently confirmed contradiction")
            if digest(obj["terminal"]) != digest(expected):
                raise InvalidProof("Incomplete contradiction wave")
        else:
            if expected is not None or obj["terminal"] is not None:
                raise InvalidProof("Claimed fixpoint still permits progress")
            solved = all(d.bit_count() == 1 for row in grid for d in row)
            if solved != (status == "solved"):
                raise InvalidProof("Completeness and status disagree")
    budget.check()
    return {"trace_verified": True, "status": status, "line_analysis_complete": status == "solved"}


def verify_result(puzzle, trace, result, budget=None, r4=None):
    checked = verify_trace(puzzle, trace, budget)
    if digest(result) != digest(result_data(puzzle, trace, r4)):
        raise InvalidProof("Analysis report differs from reconstructed metrics/status/bindings")
    return checked
