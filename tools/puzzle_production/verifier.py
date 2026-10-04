"""Independent block-interval DAG proof checker. Never imports the solver."""
from __future__ import annotations

from .contract import (Budget, Clue, EMPTY, INK, InvalidProof,
                       Puzzle, digest, domain_values, exact_keys, integer,
                       wire_grid)


def justified_support(clues: tuple[int | Clue, ...], domains: list[int]) -> list[int]:
    """Compute support through edges placing an entire block or one empty cell.

    Node (k, p): k complete blocks and p consumed cells. A block edge includes
    a trailing separator exactly when its next block has the same color.
    Forward reachability and reverse
    co-reachability identify legal edges; edge intervals supply cell support.
    This has no shared state machine, transitions or deduction cache with solver.
    """
    n, m = len(domains), len(clues)
    blocks = [(c.length, c.color) if isinstance(c, Clue) else (c, INK) for c in clues]
    if sum(length for length, _ in blocks) + sum(
            blocks[k][1] == blocks[k + 1][1] for k in range(m - 1)) > n:
        return [0] * n
    # O(1) interval compatibility, independently from the solver's cell edges.
    blocked = {}
    for _, color in blocks:
        if color not in blocked:
            prefix = [0]
            for mask in domains:
                prefix.append(prefix[-1] + (not mask & color))
            blocked[color] = prefix
    graph = {}
    reachable = {(0, 0)}
    for k in range(m + 1):
        for p in range(n + 1):
            node = (k, p)
            if node not in reachable:
                continue
            edges = []
            if p < n and domains[p] & EMPTY:
                edges.append(((k, p + 1), p, p + 1, EMPTY))
            if k < m:
                length, color = blocks[k]
                end = p + length
                separator = k + 1 < m and color == blocks[k + 1][1]
                if (end <= n and blocked[color][end] == blocked[color][p] and
                        (not separator or end < n and domains[end] & EMPTY)):
                    target = (k + 1, end + int(separator))
                    edges.append((target, p, end, color))
            graph[node] = edges
            reachable.update(edge[0] for edge in edges)
    finish = (m, n)
    if finish not in reachable:
        return [0] * n
    coreachable = {finish}
    support = [0] * n
    for k in range(m, -1, -1):
        for p in range(n, -1, -1):
            node = (k, p)
            for target, start, end, bit in graph.get(node, ()):
                if target not in coreachable:
                    continue
                coreachable.add(node)
                for offset in range(start, end):
                    support[offset] |= bit
                if bit != EMPTY and target[1] > end:
                    support[end] |= EMPTY
    return support


def _line_ref(obj: dict, puzzle: Puzzle):
    axis = obj["axis"]
    if axis not in ("row", "column"):
        raise InvalidProof("Invalid line axis")
    limit = puzzle.height if axis == "row" else puzzle.width
    return axis, integer(obj["index"], 0, limit - 1, "line index", InvalidProof)


def _matches_clues(values: list[int], clues: tuple[int | Clue, ...]) -> bool:
    # Direct run extraction, independent also from this checker's support routine.
    runs, length, color = [], 0, EMPTY
    for value in values + [EMPTY]:
        if value != color:
            if length:
                runs.append((length, color))
            length, color = 0, value
        if value != EMPTY:
            length += 1
    expected = tuple((c.length, c.color) if isinstance(c, Clue) else (c, INK) for c in clues)
    return tuple(runs) == expected


def verify(puzzle: Puzzle, proof: object, budget: Budget | None = None) -> dict:
    budget = budget if budget is not None else Budget()
    start_lines = budget.lines
    obj = exact_keys(proof, {
        "format", "logic_hash", "profile", "profile_hash", "steps", "status",
        "final_domains", "contradiction", "reason",
    }, InvalidProof)
    if (obj["format"] != puzzle.proof_format or obj["logic_hash"] != puzzle.logic_hash or
            digest(obj["profile"]) != digest(puzzle.profile) or
            obj["profile_hash"] != digest(puzzle.profile)):
        raise InvalidProof("Wrong logic, format or rule profile binding")
    steps = obj["steps"]
    if not isinstance(steps, list) or len(steps) > puzzle.max_proof_steps:
        raise InvalidProof("Invalid or excessive proof step count")
    grid = puzzle.unknown_grid()
    for step in steps:
        step = exact_keys(step, {"axis", "index", "changes"}, InvalidProof)
        axis, index = _line_ref(step, puzzle)
        clues, domains = puzzle.line(grid, axis, index)
        budget.tick()
        support = justified_support(clues, domains)
        if not all(support):
            raise InvalidProof("Deduction step on an impossible line")
        expected = [{"offset": p, "before": domain_values(before, puzzle.colors),
                     "after": domain_values(after, puzzle.colors)}
                    for p, (before, after) in enumerate(zip(domains, support))
                    if before != after]
        # Canonical JSON comparison also distinguishes bool/float from int offsets.
        if not expected or digest(step["changes"]) != digest(expected):
            raise InvalidProof("Changes do not equal the independently forced exclusions")
        for p, mask in enumerate(support):
            y, x = (index, p) if axis == "row" else (p, index)
            grid[y][x] = mask
    if digest(obj["final_domains"]) != digest(wire_grid(grid, puzzle.colors)):
        raise InvalidProof("End domains do not match replay from the unknown grid")
    status = obj["status"]
    if status not in ("solved", "stalled", "contradiction", "aborted"):
        raise InvalidProof("Invalid proof end status")
    if status == "contradiction":
        ref = exact_keys(obj["contradiction"], {"axis", "index"}, InvalidProof)
        axis, index = _line_ref(ref, puzzle)
        clues, domains = puzzle.line(grid, axis, index)
        budget.tick()
        if any(justified_support(clues, domains)):
            raise InvalidProof("Claimed contradiction has a legal line placement")
    elif obj["contradiction"] is not None:
        raise InvalidProof("Unexpected contradiction reference")
    if status == "aborted":
        if obj["reason"] not in ("time_limit", "work_limit", "cancelled"):
            raise InvalidProof("Aborted proof needs an explicit supported reason")
    elif obj["reason"] is not None:
        raise InvalidProof("Completed proof cannot carry an abort reason")
    if status in ("solved", "stalled"):
        complete = all(mask != 0 and mask & (mask - 1) == 0 for row in grid for mask in row)
        if (status == "solved") != complete:
            raise InvalidProof("Claimed end status disagrees with domain completeness")
        for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
            for index in range(count):
                clues, domains = puzzle.line(grid, axis, index)
                budget.tick()
                if status == "solved":
                    if not _matches_clues(domains, clues):
                        raise InvalidProof("Completed raster violates the clues")
                elif justified_support(clues, domains) != domains:
                    raise InvalidProof("Not a true fixpoint: line still forces exclusions")
    budget.check()
    return {"status": status, "proof_verified": True,
            "certified": status == "solved", "logic_hash": puzzle.logic_hash,
            "profile": puzzle.profile, "profile_hash": digest(puzzle.profile), "steps": len(steps),
            "line_evaluations": budget.lines - start_lines}
