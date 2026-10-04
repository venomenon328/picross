from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.benchmark import reference, run
from tools.puzzle_production.contract import canonical_bytes, digest, load_json
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify


class BenchmarkTests(unittest.TestCase):
    def test_references_do_real_propagation(self):
        for n in (40, 100):
            puzzle = reference(n)
            proof = solve(puzzle)
            result = verify(puzzle, proof)
            self.assertTrue(result["certified"])
            self.assertGreater(result["steps"], n)
            self.assertEqual({value[0] for row in proof["final_domains"] for value in row},
                             {"empty", "ink"})
            expected = []
            for y in range(n):
                length = 2 * (min(y, n - y - 1) + 1)
                left = (n - length) // 2
                expected.append([["ink"] if left <= x < left + length else ["empty"]
                                 for x in range(n)])
            self.assertEqual(proof["final_domains"], expected)

    def test_timeout_and_dead_process_fail_acceptance(self):
        for outcome in (subprocess.TimeoutExpired("test", 120),
                        subprocess.CompletedProcess([], -9, "", "killed")):
            with tempfile.TemporaryDirectory() as temp:
                with patch("tools.puzzle_production.benchmark._run_worker") as spawn:
                    if isinstance(outcome, Exception):
                        spawn.side_effect = outcome
                    else:
                        spawn.return_value = outcome
                    report = run(Path(temp))
                self.assertFalse(report["accepted"])
                self.assertTrue(all(not case["accepted"] for case in report["cases"]))
                self.assertEqual(load_json(Path(temp) / "benchmark.json"), report)
                self.assertFalse(any((Path(temp) / case["name"] / "result.json").exists()
                                     for case in report["cases"]))

    def test_canonical_hash_golden(self):
        self.assertEqual(canonical_bytes({"b": 2, "a": ["ink", "empty"]}),
                         b'{"a":["ink","empty"],"b":2}')
        self.assertEqual(digest({"a": 1}),
                         "015abd7f5cc57a2dd94b7590f04ad8084273905ee33ec5cebeae62276a97f862")
