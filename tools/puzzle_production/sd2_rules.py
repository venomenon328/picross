"""Finite SD rule generator. Full line support is used exclusively at E3."""
from __future__ import annotations

from .contract import Clue


def deductions(clues, domains, level, budget):
    n = len(domains)
    blocks = [(c.length, c.color) if isinstance(c, Clue) else (c, 2) for c in clues]
    lengths = [b[0] for b in blocks]
    colors = [b[1] for b in blocks]
    gaps = [int(a == b) for a, b in zip(colors, colors[1:])]
    size = sum(lengths) + sum(gaps)
    result = {}

    def add(name, permitted):
        result[name] = [a & b for a, b in zip(domains, permitted)]

    if not blocks:
        add("E0-empty", [1] * n)
    if size >= n:
        packed = []
        for i, (length, color) in enumerate(blocks):
            packed.extend([color] * length)
            if i < len(gaps):
                packed.extend([1] * gaps[i])
        add("E0-packed", packed if size == n else [0] * n)
    anchors = []
    for p, mask in enumerate(domains):
        if mask > 1 and mask.bit_count() == 1:
            if anchors and anchors[-1][1] == p and anchors[-1][2] == mask:
                a, _, c = anchors[-1]
                anchors[-1] = (a, p + 1, c)
            else:
                anchors.append((p, p + 1, mask))
    if [(b-a, c) for a, b, c in anchors] == blocks:
        add("E0-cleanup", [d if d > 1 and d.bit_count() == 1 else 1 for d in domains])
    if level == 0 or size > n:
        return result

    starts = []
    left = 0
    for i, length in enumerate(lengths):
        right = n - sum(lengths[i:]) - sum(gaps[i:])
        starts.append(set(range(left, right + 1)))
        left += length + (gaps[i] if i < len(gaps) else 0)

    for i, (length, color) in enumerate(blocks):
        keep = set()
        for s in starts[i]:
            budget.work()
            end = s + length
            if any(not domains[p] & color for p in range(s, end)):
                continue
            if s and domains[s-1] == color or end < n and domains[end] == color:
                continue
            if i and gaps[i-1] and (s == 0 or not domains[s-1] & 1):
                continue
            if i < len(gaps) and gaps[i] and (end == n or not domains[end] & 1):
                continue
            keep.add(s)
        starts[i] = keep
    if any(not choices for choices in starts):
        add("E1-overlap", [0] * n)
        add("E1-exclusion", [0] * n)
    else:
        coverage = [1] * n
        for (length, color), choices in zip(blocks, starts):
            for start in choices:
                budget.work()
                for position in range(start, start + length):
                    coverage[position] |= color
        add("E1-exclusion", coverage)
    overlap = list(domains)
    for (length, color), choices in zip(blocks, starts):
        for p in range(max(choices), min(choices) + length) if choices else ():
            overlap[p] &= color
    if all(starts):
        add("E1-overlap", overlap)
    anchored = list(domains)
    for a, b, color in anchors:
        budget.work()
        owners = [(i, {s for s in choices if s <= a and b <= s + lengths[i]})
                  for i, choices in enumerate(starts) if colors[i] == color]
        owners = [(i, choices) for i, choices in owners if choices]
        if not owners:
            anchored = [0] * n
            break
        if len(owners) == 1:
            i, choices = owners[0]
            for p in range(max(choices), min(choices) + lengths[i]):
                anchored[p] &= color
            if len(choices) == 1:
                start = next(iter(choices))
                for p in (start - 1, start + lengths[i]):
                    if 0 <= p < n:
                        anchored[p] &= ~color
    add("E1-anchored", anchored)
    if level == 1:
        return result

    while True:
        before = [set(s) for s in starts]
        if any(not s for s in starts):
            add("E2-combination", [0] * n)
            break
        for i, choices in enumerate(starts):
            keep = set()
            for s in choices:
                budget.work()
                if i and not any(t + lengths[i-1] + gaps[i-1] <= s for t in starts[i-1]):
                    continue
                if i + 1 < len(starts) and not any(s + lengths[i] + gaps[i] <= t for t in starts[i+1]):
                    continue
                keep.add(s)
            starts[i] = keep
        impossible = False
        for p, mask in enumerate(domains):
            if mask & 1:
                continue
            owners = []
            for i, choices in enumerate(starts):
                budget.work()
                covering = {s for s in choices if s <= p < s + lengths[i]}
                if covering:
                    owners.append((i, covering))
            if not owners:
                impossible = True
                break
            if len(owners) == 1:
                i, covering = owners[0]
                starts[i] &= covering
        if impossible or any(not s for s in starts):
            add("E2-combination", [0] * n)
            break
        if starts == before:
            support = [1] * n
            for (length, color), choices in zip(blocks, starts):
                for s in choices:
                    budget.work()
                    for p in range(s, s + length):
                        support[p] |= color
                for p in range(max(choices), min(choices) + length) if choices else ():
                    support[p] &= ~1
            add("E2-combination", support)
            break
    if level == 3:
        from .solver import line_support
        add("E3-support", line_support(clues, domains))
    return result
