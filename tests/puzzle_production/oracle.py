"""Small exhaustive test oracles; deliberately absent from production modules."""
from itertools import product


def runs(cells):
    result, length = [], 0
    for cell in tuple(cells) + (0,):
        if cell:
            length += 1
        elif length:
            result.append(length)
            length = 0
    return tuple(result)


def placements(length, clues):
    return [cells for cells in product((0, 1), repeat=length) if runs(cells) == clues]


def support(candidates, domains):
    result = [0] * len(domains)
    for cells in candidates:
        if all(mask & (1 << value) for mask, value in zip(domains, cells)):
            for p, value in enumerate(cells):
                result[p] |= 1 << value
    return result


def grid_solutions(puzzle):
    # Enumerate independent row placements; filter only by direct column runs.
    return [grid for grid in product(*(placements(puzzle.width, clues)
                                      for clues in puzzle.rows))
            if all(runs(row[x] for row in grid) == clue
                   for x, clue in enumerate(puzzle.columns))]
