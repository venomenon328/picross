"""Independent interval-graph justification of proof v3; no solver imports."""
from __future__ import annotations

from itertools import combinations

from .contract import (Budget, Clue, EMPTY, INK, InvalidInput, InvalidProof,
                       PAIRED_IDS, PAIRED_PROOF_FORMAT, digest, domain_values,
                       exact_keys, integer, selected_profile, wire_grid)
from .verifier import justified_support, _matches_clues


def _interval_graph(clues, domains, budget):
    """Place whole blocks with required trailing separators, then label intervals.

    A boundary is (0, completed blocks); a private interval is (1, block, start).
    Layer position determines progress inside that fixed interval. This graph is
    built from independent interval compatibility, not the producer's automaton.
    """
    n = len(domains)
    blocks = [(c.length, c.color) if isinstance(c, Clue) else (c, INK) for c in clues]
    graph = [{} for _ in range(n)]
    if sum(length for length, _ in blocks) + sum(
            a[1] == b[1] for a, b in zip(blocks, blocks[1:])) > n:
        return graph, (0, len(blocks))

    def edge(p, source, value, target):
        budget.pair_tick()
        if source not in graph[p]:
            budget.hold()
            graph[p][source] = []
        budget.hold()
        graph[p][source].append((value, target))

    for k in range(len(blocks) + 1):
        for p in range(n):
            budget.pair_tick()
            if domains[p] & EMPTY:
                edge(p, (0, k), EMPTY, (0, k))
            if k == len(blocks):
                continue
            length, color = blocks[k]
            end = p + length
            separator = k + 1 < len(blocks) and color == blocks[k + 1][1]
            stop = end + int(separator)
            if stop > n:
                continue
            legal = True
            for q in range(p, stop):
                budget.pair_tick()
                if not domains[q] & (color if q < end else EMPTY):
                    legal = False
                    break
            if not legal:
                continue
            for q in range(p, stop):
                source = (0, k) if q == p else (1, k, p)
                target = (0, k + 1) if q + 1 == stop else (1, k, p)
                edge(q, source, color if q < end else EMPTY, target)
    return graph, (0, len(blocks))


def _accepts(graph, finish, first, second, a, b, budget):
    with budget.pair_scope():
        budget.hold()
        reached = {(0, 0)}
        for p, layer in enumerate(graph):
            following = set()
            for node in reached:
                for value, target in layer.get(node, ()):
                    budget.pair_tick()
                    if (p != first or value == a) and (p != second or value == b):
                        if target not in following:
                            budget.hold()
                            following.add(target)
            budget.release(len(reached))
            reached = following
        return finish in reached


def justified_relation(clues, domains, first, second, budget):
    with budget.pair_scope():
        graph, finish = _interval_graph(clues, domains, budget)
        relation = set()
        for i in range(domains[first].bit_length()):
            a = 1 << i
            if not domains[first] & a:
                continue
            for j in range(domains[second].bit_length()):
                budget.pair_tick()
                b = 1 << j
                if domains[second] & b and _accepts(graph, finish, first, second, a, b, budget):
                    budget.hold()
                    relation.add((a, b))
        return relation


def justified_pair(puzzle, grid, axis, first, second, budget):
    budget.tick()
    with budget.pair_scope():
        clues_a, domains_a = puzzle.line(grid, axis, first)
        clues_b, domains_b = puzzle.line(grid, axis, second)
        ga, end_a = _interval_graph(clues_a, domains_a, budget)
        gb, end_b = _interval_graph(clues_b, domains_b, budget)
        relations = []
        for p in range(len(domains_a)):
            clues, domains = puzzle.line(grid, "column" if axis == "row" else "row", p)
            relation = justified_relation(clues, domains, first, second, budget)
            budget.hold(len(relation) + 1)
            relations.append(relation)
        budget.hold()
        reachable = [{((0, 0), (0, 0))}]
        for p in range(len(ga)):
            layer = set()
            for u, v in reachable[-1]:
                for a, unext in ga[p].get(u, ()):
                    for b, vnext in gb[p].get(v, ()):
                        budget.pair_tick()
                        item = (unext, vnext)
                        if (a, b) in relations[p] and item not in layer:
                            budget.hold()
                            layer.add(item)
            reachable.append(layer)
        support = [[0] * len(ga), [0] * len(gb)]
        if (end_a, end_b) not in reachable[-1]:
            return support
        budget.hold()
        viable = {(end_a, end_b)}
        for p in reversed(range(len(ga))):
            previous = set()
            for u, v in reachable[p]:
                for a, unext in ga[p].get(u, ()):
                    for b, vnext in gb[p].get(v, ()):
                        budget.pair_tick()
                        if (a, b) in relations[p] and (unext, vnext) in viable:
                            if (u, v) not in previous:
                                budget.hold()
                                previous.add((u, v))
                            support[0][p] |= a
                            support[1][p] |= b
            budget.release(len(viable))
            viable = previous
        return support


def _reference(ref, puzzle):
    exact_keys(ref, {"kind", "axis", "indices"}, InvalidProof)
    if ref["kind"] not in ("line", "pair") or ref["axis"] not in ("row", "column"):
        raise InvalidProof("Invalid typed deduction reference")
    indices = ref["indices"]
    size = puzzle.height if ref["axis"] == "row" else puzzle.width
    count = 1 if ref["kind"] == "line" else 2
    if not isinstance(indices, list) or len(indices) != count:
        raise InvalidProof("Wrong line/pair index count")
    for index in indices:
        integer(index, 0, size - 1, "deduction index", InvalidProof)
    if count == 2 and indices[0] >= indices[1]:
        raise InvalidProof("Pair indices must be distinct and ascending")
    return ref["axis"], indices


def _projection(puzzle, grid, ref, budget):
    axis, indices = _reference(ref, puzzle)
    if len(indices) == 2:
        return justified_pair(puzzle, grid, axis, *indices, budget)
    budget.tick()
    clues, domains = puzzle.line(grid, axis, indices[0])
    return [justified_support(clues, domains)]


def verify_paired(puzzle, proof, budget: Budget):
    start_lines, start_work = budget.lines, budget.pair_work
    obj = exact_keys(proof, {"format", "logic_hash", "profile", "profile_hash", "steps",
                            "status", "final_domains", "contradiction", "reason"}, InvalidProof)
    try:
        profile = selected_profile(puzzle, obj["profile"].get("id"))
    except (InvalidInput, AttributeError, TypeError) as exc:
        raise InvalidProof("Invalid paired profile") from exc
    if (profile["id"] not in PAIRED_IDS or obj["format"] != PAIRED_PROOF_FORMAT or
            obj["logic_hash"] != puzzle.logic_hash or digest(obj["profile"]) != digest(profile) or
            obj["profile_hash"] != digest(profile)):
        raise InvalidProof("Wrong logic, paired format or profile binding")
    steps = obj["steps"]
    if not isinstance(steps, list) or len(steps) > puzzle.max_proof_steps:
        raise InvalidProof("Invalid or excessive proof step count")
    grid = puzzle.unknown_grid()
    for step in steps:
        exact_keys(step, {"kind", "axis", "indices", "changes"}, InvalidProof)
        ref = {k: step[k] for k in ("kind", "axis", "indices")}
        axis, indices = _reference(ref, puzzle)
        supports = _projection(puzzle, grid, ref, budget)
        if any(not all(s) for s in supports):
            raise InvalidProof("Deduction on an impossible relation")
        expected = []
        for index, support in zip(indices, supports):
            for p, after in enumerate(support):
                y, x = (index, p) if axis == "row" else (p, index)
                before = grid[y][x]
                if before != after:
                    expected.append({"row": y, "column": x,
                                     "before": domain_values(before, puzzle.colors),
                                     "after": domain_values(after, puzzle.colors)})
        expected.sort(key=lambda c: (c["row"], c["column"]))
        if not expected or digest(step["changes"]) != digest(expected):
            raise InvalidProof("Changes differ from the complete independent projection")
        for index, support in zip(indices, supports):
            for p, value in enumerate(support):
                y, x = (index, p) if axis == "row" else (p, index)
                grid[y][x] = value
    if digest(obj["final_domains"]) != digest(wire_grid(grid, puzzle.colors)):
        raise InvalidProof("Final domains differ from unknown-start replay")
    status = obj["status"]
    if status not in ("solved", "stalled", "contradiction", "aborted"):
        raise InvalidProof("Invalid proof status")
    if status == "contradiction":
        supports = _projection(puzzle, grid, obj["contradiction"], budget)
        if any(any(s) for s in supports):
            raise InvalidProof("Claimed contradiction has a compatible relation")
    elif obj["contradiction"] is not None:
        raise InvalidProof("Unexpected contradiction reference")
    if status == "aborted":
        if obj["reason"] not in ("time_limit", "work_limit", "cancelled", "pair_work_limit", "pair_memory_limit"):
            raise InvalidProof("Unsupported abort reason")
    elif obj["reason"] is not None:
        raise InvalidProof("Completed proof carries abort reason")
    if status in ("solved", "stalled"):
        complete = all(d and d & (d - 1) == 0 for row in grid for d in row)
        if (status == "solved") != complete:
            raise InvalidProof("Status disagrees with completeness")
        for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
            for i in range(count):
                budget.tick()
                clues, domains = puzzle.line(grid, axis, i)
                if status == "solved":
                    if not _matches_clues(domains, clues):
                        raise InvalidProof("Complete matrix violates clues")
                elif justified_support(clues, domains) != domains:
                    raise InvalidProof("Not a single-line fixpoint")
            if status == "stalled":
                for i, j in combinations(range(count), 2):
                    expected = [puzzle.line(grid, axis, k)[1] for k in (i, j)]
                    if justified_pair(puzzle, grid, axis, i, j, budget) != expected:
                        raise InvalidProof("Not a paired-line fixpoint")
    budget.check()
    return {"status": status, "certified": status == "solved", "proof_verified": True,
            "logic_hash": puzzle.logic_hash, "profile": profile, "profile_hash": digest(profile),
            "steps": len(steps), "line_evaluations": budget.lines - start_lines,
            "pair_work": budget.pair_work - start_work, "pair_peak_records": budget.pair_peak_records}
