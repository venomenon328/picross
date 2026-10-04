from itertools import product
import unittest

from oracle import placements, runs, support
from tools.puzzle_production.solver import line_support
from tools.puzzle_production.verifier import justified_support


class LineOracleTests(unittest.TestCase):
    def test_all_small_domains_and_clues(self):
        comparisons = 0
        for n in range(1, 7):
            hints = {runs(cells) for cells in product((0, 1), repeat=n)}
            hints.update({(n + 1,), (n, n), (1,) * (n + 1)})
            for clues in sorted(hints):
                candidates = placements(n, clues)
                for domains in product((1, 2, 3), repeat=n):
                    expected = support(candidates, domains)
                    actual = line_support(clues, list(domains))
                    checked = justified_support(clues, list(domains))
                    if actual != expected or checked != expected:
                        self.fail(f"n={n}, clues={clues}, domains={domains}: "
                                  f"oracle={expected}, solver={actual}, checker={checked}")
                    comparisons += 1
        self.assertGreater(comparisons, 20_000)
        print(f"RP1-A01: {comparisons} exhaustive supported-domain comparisons")

    def test_partial_information_and_impossible_domains(self):
        for clues, domains in [((), [3] * 5), ((5,), [3] * 5),
                               ((3,), [3] * 5), ((1, 1), [3, 1, 3, 1, 3]),
                               ((1,), [3, 0, 3]), ((1, 1), [2, 2, 1])]:
            with self.subTest(clues=clues, domains=domains):
                expected = support(placements(len(domains), clues), domains)
                self.assertEqual(line_support(clues, domains), expected)
                self.assertEqual(justified_support(clues, domains), expected)
        self.assertEqual(line_support((3,), [3] * 5), [3, 3, 2, 3, 3])

    def test_information_poor_long_line(self):
        clues, domains = (1,) * 20, [3] * 100
        self.assertEqual(line_support(clues, domains), domains)
        self.assertEqual(justified_support(clues, domains), domains)
