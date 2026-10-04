from itertools import product
import unittest

from oracle import colored_runs, support
from tools.puzzle_production.contract import Clue
from tools.puzzle_production.solver import line_support
from tools.puzzle_production.verifier import justified_support


class ColorLineOracleTests(unittest.TestCase):
    def test_exhaustive_color_domain_matrix(self):
        total = 0
        # ALL value assignments, resulting hints, nonempty AND empty domains.
        # Keep four/eight-color matrices small rather than exploding long lines.
        for colors, max_length in ((2, 4), (4, 2), (8, 1)):
            comparisons = 0
            for n in range(1, max_length + 1):
                grouped = {}
                for cells in product(range(colors + 1), repeat=n):
                    grouped.setdefault(colored_runs(cells), []).append(cells)
                grouped.update({((n + 1, 1),): [], ((n, 1), (n, 1)): [],
                                ((n, 1), (n, 2)): []})
                for hints, candidates in grouped.items():
                    clues = tuple(Clue(length, 1 << color) for length, color in hints)
                    for domains in product(range(1 << (colors + 1)), repeat=n):
                        expected = support(candidates, domains)
                        actual = line_support(clues, list(domains))
                        checked = justified_support(clues, list(domains))
                        if actual != expected or checked != expected:
                            self.fail(f"colors={colors}, n={n}, hints={hints}, domains={domains}: "
                                      f"oracle={expected}, solver={actual}, checker={checked}")
                        comparisons += 1
            total += comparisons
            print(f"RP2-A01: colors={colors}, n=1..{max_length}, comparisons={comparisons}")
        self.assertGreater(total, 100_000)

    def test_long_color_lines_and_touching_rules(self):
        cases = [
            ((Clue(1, 2), Clue(1, 4)), [31, 31], [2, 4]),
            ((Clue(1, 2), Clue(1, 2)), [31, 31], [0, 0]),
            ((Clue(1, 2), Clue(1, 2)), [31] * 3, [2, 1, 2]),
            ((Clue(1, 2), Clue(1, 4)), [2, 1, 4], [2, 1, 4]),
            (tuple(Clue(1, 2 << (i % 4)) for i in range(100)),
             [31] * 100, [2 << (i % 4) for i in range(100)]),
            ((Clue(100, 256),), [511] * 100, [256] * 100),
        ]
        for clues, domains, expected in cases:
            self.assertEqual(line_support(clues, domains), expected)
            self.assertEqual(justified_support(clues, domains), expected)
