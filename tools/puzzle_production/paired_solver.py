"""Exact paired-line projection using coupled cell automata; no grid probing."""
from __future__ import annotations

from itertools import combinations

from .contract import (Aborted, Budget, Clue, EMPTY, INK, PAIRED_PROOF_FORMAT,
                       digest, domain_values, selected_profile, wire_grid)
from .solver import line_support


def _automaton(clues, n, budget):
    lengths = [c.length if isinstance(c, Clue) else c for c in clues]
    colors = [c.color if isinstance(c, Clue) else INK for c in clues]
    if sum(lengths) + sum(a == b for a, b in zip(colors, colors[1:])) > n:
        return [[]], set()
    budget.hold(2 * (len(clues) + 1 + sum(lengths)))
    states = [(k, 0) for k in range(len(clues) + 1)]
    states += [(k, r) for k, length in enumerate(lengths) for r in range(1, length + 1)]
    ids = {s: i for i, s in enumerate(states)}
    edges = [[] for _ in states]
    for s, (k, r) in enumerate(states):
        budget.pair_tick()
        if not r:
            out = [(EMPTY, s)]
            if k < len(clues):
                out.append((colors[k], ids[k, 1]))
        elif r < lengths[k]:
            out = [(colors[k], ids[k, r + 1])]
        else:
            out = [(EMPTY, ids[k + 1, 0])]
            if k + 1 < len(clues) and colors[k] != colors[k + 1]:
                out.append((colors[k + 1], ids[k + 1, 1]))
        budget.hold(len(out))
        edges[s] = out
    accepting = {ids[len(clues), 0]}
    if clues:
        accepting.add(ids[len(clues) - 1, lengths[-1]])
    return edges, accepting


def crossing_relation(clues, domains, first, second, budget):
    """Track only the two observed labels through every legal automaton path."""
    with budget.pair_scope():
        edges, accepting = _automaton(clues, len(domains), budget)
        budget.hold()
        frontier = {(0, 0, 0)}
        for p, mask in enumerate(domains):
            following = set()
            for state, a, b in frontier:
                for value, target in edges[state]:
                    budget.pair_tick()
                    if mask & value:
                        item = (target, value if p == first else a,
                                value if p == second else b)
                        if item not in following:
                            budget.hold()
                            following.add(item)
            budget.release(len(frontier))
            frontier = following
        relation = set()
        for state, a, b in frontier:
            budget.pair_tick()
            if state in accepting and (a, b) not in relation:
                budget.hold()
                relation.add((a, b))
        return relation


def pair_support(puzzle, grid, axis, first, second, budget):
    budget.tick()
    with budget.pair_scope():
        ca, da = puzzle.line(grid, axis, first)
        cb, db = puzzle.line(grid, axis, second)
        relations = []
        cross = "column" if axis == "row" else "row"
        for x in range(len(da)):
            clues, domains = puzzle.line(grid, cross, x)
            relation = crossing_relation(clues, domains, first, second, budget)
            budget.hold(len(relation) + 1)
            relations.append(relation)
        ea, aa = _automaton(ca, len(da), budget)
        eb, ab = _automaton(cb, len(db), budget)
        budget.hold()
        forward = [{(0, 0)}]
        for x, relation in enumerate(relations):
            following = set()
            for a, b in forward[-1]:
                for va, ta in ea[a]:
                    for vb, tb in eb[b]:
                        budget.pair_tick()
                        if da[x] & va and db[x] & vb and (va, vb) in relation:
                            if (ta, tb) not in following:
                                budget.hold()
                                following.add((ta, tb))
            forward.append(following)
        backward = set()
        for a, b in forward[-1]:
            budget.pair_tick()
            if a in aa and b in ab:
                budget.hold()
                backward.add((a, b))
        supports = [[0] * len(da), [0] * len(db)]
        for x in range(len(da) - 1, -1, -1):
            previous = set()
            for a, b in forward[x]:
                for va, ta in ea[a]:
                    for vb, tb in eb[b]:
                        budget.pair_tick()
                        if (ta, tb) in backward and da[x] & va and db[x] & vb and (va, vb) in relations[x]:
                            if (a, b) not in previous:
                                budget.hold()
                                previous.add((a, b))
                            supports[0][x] |= va
                            supports[1][x] |= vb
            budget.release(len(backward))
            backward = previous
        return supports


def solve_paired(puzzle, budget: Budget, profile: str):
    chosen = selected_profile(puzzle, profile)
    grid, steps = puzzle.unknown_grid(), []
    reason = contradiction = None
    status = "stalled"

    def apply(axis, indices, supports):
        nonlocal contradiction, status
        ref = {"kind": "line" if len(indices) == 1 else "pair", "axis": axis, "indices": indices}
        if any(not all(s) for s in supports):
            status, contradiction = "contradiction", ref
            return False
        changes = []
        for index, support in zip(indices, supports):
            for p, after in enumerate(support):
                y, x = (index, p) if axis == "row" else (p, index)
                before = grid[y][x]
                if before != after:
                    changes.append({"row": y, "column": x,
                                    "before": domain_values(before, puzzle.colors),
                                    "after": domain_values(after, puzzle.colors)})
        # Only apply a fully evaluated projection, never a partial budget result.
        changes.sort(key=lambda c: (c["row"], c["column"]))
        for index, support in zip(indices, supports):
            for p, after in enumerate(support):
                y, x = (index, p) if axis == "row" else (p, index)
                grid[y][x] = after
        if changes:
            steps.append({**ref, "changes": changes})
        return bool(changes)

    try:
        while True:
            while True:
                changed = False
                for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
                    for i in range(count):
                        budget.tick()
                        clues, domains = puzzle.line(grid, axis, i)
                        changed |= apply(axis, [i], [line_support(clues, domains)])
                        if contradiction:
                            break
                    if contradiction:
                        break
                if contradiction or not changed:
                    break
            if contradiction:
                break
            if all(d & (d - 1) == 0 for row in grid for d in row):
                status = "solved"
                break
            changed = False
            for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
                for i, j in combinations(range(count), 2):
                    changed = apply(axis, [i, j], pair_support(puzzle, grid, axis, i, j, budget))
                    if contradiction or changed:
                        break
                if contradiction or changed:
                    break
            if contradiction or not changed:
                break
        budget.check()
    except Aborted as exc:
        status, contradiction, reason = "aborted", None, str(exc)
    return {"format": PAIRED_PROOF_FORMAT, "logic_hash": puzzle.logic_hash,
            "profile": chosen, "profile_hash": digest(chosen), "steps": steps,
            "status": status, "final_domains": wire_grid(grid, puzzle.colors),
            "contradiction": contradiction, "reason": reason}
