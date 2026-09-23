"""Finite, colored line-intersection certificate for the single F-02 fixture."""
import json
from functools import lru_cache
from check_f01 import DATA


@lru_cache(maxsize=None)
def placements(blocks: tuple[tuple[int, int], ...], width: int) -> tuple:
    if not blocks:
        return ((0,) * width,)
    length, color = blocks[0]
    rest = blocks[1:]
    gap = int(bool(rest) and rest[0][1] == color)
    minimum = sum(n for n, _ in rest) + sum(a[1] == b[1] for a, b in zip(rest, rest[1:]))
    result = []
    for start in range(width - length - gap - minimum + 1):
        prefix = (0,) * start + (color,) * length + (0,) * gap
        for tail in placements(rest, width - len(prefix)):
            result.append(prefix + tail)
    return tuple(result)


def derive(data):
    if (data['id'], data['revision'], data['width'], data['height']) != ('F-02', 2, 40, 40):
        raise ValueError('Certificate scoped to F-02 revision 2')
    known = [[-1] * 40 for _ in range(40)]
    candidates = {}
    for axis, clues in [('row', data['rows']), ('column', data['columns'])]:
        for i, blocks in enumerate(clues):
            if any(b['color'] not in (1, 2, 3, 4) for b in blocks):
                raise ValueError('Invalid fixture color')
            candidates[axis, i] = placements(tuple((b['length'], b['color']) for b in blocks), 40)
    steps = []
    while True:
        changed = False
        for (axis, i), options in candidates.items():
            points = [(i, n) if axis == 'row' else (n, i) for n in range(40)]
            viable = [p for p in options if all(known[y][x] in (-1, p[n]) for n, (y, x) in enumerate(points))]
            if not viable:
                raise ValueError('Contradictory clues')
            candidates[axis, i] = viable
            forced = []
            for n, (y, x) in enumerate(points):
                values = {p[n] for p in viable}
                if known[y][x] == -1 and len(values) == 1:
                    known[y][x] = values.pop()
                    forced.append([n + 1, known[y][x]])
            if forced:
                steps.append(dict(axis=axis, line=i + 1, candidates=len(viable), forced=forced))
                changed = True
        if not changed:
            return steps, known


def verify(data, certificate):
    steps, known = derive(data)
    if certificate != dict(id='F-02', revision=2, rule='colored-line-intersection', steps=steps):
        raise ValueError('Certificate differs from deductions')
    if any(-1 in row for row in known) or known != data['solution']:
        raise ValueError('Deductions do not determine supplied solution')
    return len(steps)


if __name__ == '__main__':
    count = verify(json.loads((DATA / 'f02.json').read_text()), json.loads((DATA / 'f02-proof.json').read_text()))
    print(f'F-02 PROOF PASS: {count} steps, 1600 forced cells, no givens/guesses')
