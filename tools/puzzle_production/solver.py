"""Complete line support from forward/backward cell automaton reachability."""
from __future__ import annotations

from collections import deque

from .contract import (Aborted, Budget, EMPTY, INK, Puzzle, domain_values,
                       proof_header, wire_grid)


def line_support(clues: tuple[int, ...], domains: list[int]) -> list[int]:
    """Union of supported values at each position; zeros mean no legal line.

    A state records either a gap after k completed blocks, or progress within
    block k. Paths consume one cell per edge. No complete placements are listed.
    """
    n = len(domains)
    if sum(clues) + max(0, len(clues) - 1) > n:
        return [0] * n
    states = [("gap", k, 0) for k in range(len(clues) + 1)]
    states += [("run", k, r) for k, length in enumerate(clues)
               for r in range(1, length + 1)]
    ids = {state: i for i, state in enumerate(states)}
    edges = [[] for _ in states]
    for i, (kind, k, r) in enumerate(states):
        if kind == "gap":
            edges[i].append((EMPTY, i))
            if k < len(clues):
                edges[i].append((INK, ids[("run", k, 1)]))
        elif r < clues[k]:
            edges[i].append((INK, ids[("run", k, r + 1)]))
        else:
            edges[i].append((EMPTY, ids[("gap", k + 1, 0)]))
    accepting = {ids[("gap", len(clues), 0)]}
    if clues:
        accepting.add(ids[("run", len(clues) - 1, clues[-1])])
    forward = [{ids[("gap", 0, 0)]}]
    for mask in domains:
        forward.append({target for source in forward[-1]
                        for bit, target in edges[source] if mask & bit})
    if not forward[-1] & accepting:
        return [0] * n
    backward = [set() for _ in range(n + 1)]
    backward[n] = accepting
    support = [0] * n
    for p in range(n - 1, -1, -1):
        for source in forward[p]:
            for bit, target in edges[source]:
                if domains[p] & bit and target in backward[p + 1]:
                    backward[p].add(source)
                    support[p] |= bit
    return support


def solve(puzzle: Puzzle, budget: Budget | None = None,
          order: str = "rows-first") -> dict:
    """Generate an untrusted proof; callers must run the independent verifier."""
    if order not in {"rows-first", "columns-first", "reverse"}:
        raise ValueError("Unsupported line order")
    budget = budget if budget is not None else Budget()
    grid = puzzle.unknown_grid()
    rows = [("row", i) for i in range(puzzle.height)]
    columns = [("column", i) for i in range(puzzle.width)]
    lines = columns + rows if order == "columns-first" else rows + columns
    if order == "reverse":
        lines.reverse()
    queue = deque(lines)
    pending = set(lines)
    steps = []
    contradiction = None
    reason = None
    status = "stalled"
    try:
        while queue:
            budget.tick()
            axis, index = queue.popleft()
            pending.remove((axis, index))
            clues, domains = puzzle.line(grid, axis, index)
            supported = line_support(clues, domains)
            if not all(supported):
                contradiction = {"axis": axis, "index": index}
                status = "contradiction"
                break
            changes = []
            for offset, (before, after) in enumerate(zip(domains, supported)):
                if before == after:
                    continue
                changes.append({"offset": offset, "before": domain_values(before),
                                "after": domain_values(after)})
                y, x = (index, offset) if axis == "row" else (offset, index)
                grid[y][x] = after
                cross = ("column", x) if axis == "row" else ("row", y)
                if cross not in pending:
                    pending.add(cross)
                    queue.append(cross)
            if changes:
                steps.append({"axis": axis, "index": index, "changes": changes})
        else:
            # Queue exhaustion only; no unknown cells get assigned here.
            status = "solved" if all(mask in (EMPTY, INK) for row in grid
                                     for mask in row) else "stalled"
        budget.check()
    except Aborted as exc:
        status, contradiction, reason = "aborted", None, str(exc)
    return {**proof_header(puzzle), "steps": steps, "status": status,
            "final_domains": wire_grid(grid), "contradiction": contradiction,
            "reason": reason}
