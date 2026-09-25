import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from p14_integration import Oracle, build_plan, validate_trace


class IntegrationContractTests(unittest.TestCase):
    def test_plan_has_500_effective_numbered_actions_and_restart_redo(self):
        plan = build_plan()
        self.assertEqual([action["number"] for action in plan], list(range(1, 501)))
        self.assertEqual(Counter(action["kind"] for action in plan),
                         Counter(cell=409, undo=21, redo=10, mini=10, pan=10, zoom=20, hint=20))
        self.assertEqual(plan[-1]["kind"], "undo")
        oracle = Oracle()
        for action in plan:
            oracle.step(action)
        self.assertEqual(oracle.cursor + 1, len(oracle.history))
        self.assertGreater(sum(value != -1 for value in oracle.cells), 500)

    def test_oracle_rejects_tampered_expectation_and_incomplete_trace(self):
        plan = build_plan()[:2]
        oracle = Oracle()
        records = []
        for action in plan:
            changes = oracle.step(action)
            records.append({"number": action["number"], "kind": action["kind"],
                            "changes": changes, "cursor": oracle.cursor,
                            "history_size": len(oracle.history), "undo_used": oracle.undo_used,
                            "history_tail": oracle.history[-1] if oracle.history else [],
                            "redo_next": []})
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "trace.jsonl"
            trace.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")
            self.assertEqual(validate_trace(plan, trace)["actions"], 2)
            with self.assertRaisesRegex(AssertionError, "action 2"):
                validate_trace(plan, trace, {2: []})
            trace.write_text(json.dumps(records[0]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "incomplete trace"):
                validate_trace(plan, trace)
