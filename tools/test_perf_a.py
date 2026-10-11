"""PERF-A independent data and identity regression oracles."""
import copy
import json
import unittest
from pathlib import Path
import perf_a


class BaselineTests(unittest.TestCase):
    def test_fixed_plan(self):
        plan = json.loads(perf_a.PLAN.read_text(encoding="utf-8"))
        self.assertEqual(plan["repetitions"], 3)
        self.assertEqual(plan["scenarios"], ["hover", "fill", "x"])
        self.assertEqual({c[3] for c in plan["contexts"]}, {16, 18, 20, 72})
        self.assertEqual({c[1] for c in plan["contexts"]}, {1.0, 1.25})

    def test_quantiles_and_empty(self):
        self.assertEqual(perf_a.distribution(range(1, 101)), dict(n=100, p50=50, p95=95, p99=99, maximum=100))
        self.assertIsNone(perf_a.distribution([])["p95"])

    def test_synthetic_history_negative_controls(self):
        definition = dict(id="F-02", revision=2)
        save = dict(schema=1, definition_id="F-02", definition_revision=2, width=40, height=40, completed=False,
                    history=[[dict(index=0, before=-1, after=1)]], cursor=1, cells=[1]+[-1]*1599)
        self.assertEqual(perf_a.verify_save(save, definition), dict(fills=1, x=0, unknown=1599))
        for key, value in (("cells", [2]+[-1]*1599), ("definition_revision", 3), ("completed", True)):
            wrong = copy.deepcopy(save)
            wrong[key] = value
            with self.assertRaises(ValueError): perf_a.verify_save(wrong, definition)
        wrong = copy.deepcopy(save)
        wrong["history"][0] *= 2
        with self.assertRaises(ValueError): perf_a.verify_save(wrong, definition)


if __name__ == "__main__": unittest.main()
