"""BA-B uses the full native adoption replay without a mutating fallback."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.background_change_fixtures import create_work
from tools.puzzle_production import background_request as requests
from tools.puzzle_production import catalog_background_change as change, catalog_transaction as tx
from tools.puzzle_production.contract import InvalidInput, write_json


def files(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


class BackgroundAdoptionReadOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.base = prepare(owner, "selected", registered=True).checkout
        write_json(cls.base / requests.INDEX, {"format": "picross-authoring-index-v1", "entries": []})

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ba-b-adoption-readonly-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.checkout = self.work / "checkout"
        shutil.copytree(self.base, self.checkout)

    def planned(self, choice="selected"):
        working = create_work(self, self.checkout, self.work / "work", choice=choice)
        plan = self.work / "plan"
        self.assertEqual(change.plan(self.checkout, working.record_path, plan)["status"], "planned")
        return working, plan

    def assert_readonly_failure(self, plan, message=None):
        before, bundle = files(self.checkout), files(plan)
        with patch.object(tx, "execute", side_effect=AssertionError("Read-only replay reached the writer")) as execute:
            with self.assertRaisesRegex(InvalidInput, message or ".+"):
                change.adopt(self.checkout, plan, no_op_only=True)
            execute.assert_not_called()
        self.assertEqual(files(self.checkout), before)
        self.assertEqual(files(plan), bundle)

    def test_old_valid_state_rejects_without_writer_and_regular_adopt_remains_available(self):
        _, plan = self.planned()
        self.assert_readonly_failure(plan, "exact adopted target")
        self.assertEqual(change.adopt(self.checkout, plan)["status"], "adopted")

    def test_complete_selected_and_none_targets_have_exact_native_noop_without_writes(self):
        for choice in ("selected", "none"):
            with self.subTest(choice=choice):
                root = self.work / choice
                shutil.copytree(self.base, root)
                working = create_work(self, root, self.work / (choice + "-work"), choice=choice)
                plan = self.work / (choice + "-plan")
                change.plan(root, working.record_path, plan)
                self.assertEqual(change.adopt(root, plan)["status"], "adopted")
                before, bundle = files(root), files(plan)
                with patch.object(tx, "execute", side_effect=AssertionError("Read-only replay reached the writer")) as execute:
                    actual = change.adopt(root, plan, no_op_only=True)
                    execute.assert_not_called()
                self.assertEqual(actual, change.adopt(root, plan))
                self.assertEqual(actual["status"], "no-op")
                self.assertEqual(files(root), before)
                self.assertEqual(files(plan), bundle)

    def test_native_work_bundle_and_pending_transaction_guards_remain_mandatory(self):
        working, plan = self.planned()
        change.adopt(self.checkout, plan)
        evidence = self.checkout / requests.directory(working.request) / working.request["authorization"]["evidence"]["file"]
        raw = evidence.read_bytes()
        evidence.unlink()
        self.assert_readonly_failure(plan)
        evidence.write_bytes(raw)
        extra = plan / "foreign.txt"
        extra.write_bytes(b"TEST ONLY unknown plan member")
        self.assert_readonly_failure(plan, "inventory")
        extra.unlink()
        for name in (tx.LOCK, "content/.registration-journal-readonly-test.tmp"):
            pending = self.checkout / name
            pending.write_bytes(b"TEST ONLY preserved unfinished transaction")
            self.assert_readonly_failure(plan, "recovery required")
            pending.unlink()

    def test_target_changed_back_to_old_during_replay_cannot_start_an_adoption(self):
        _, plan = self.planned()
        old = files(self.checkout)
        change.adopt(self.checkout, plan)
        changed = []

        def race(phase):
            if phase != "work-checked":
                return
            for path in self.checkout.rglob("*"):
                if path.is_file() and path.relative_to(self.checkout).as_posix() not in old:
                    path.unlink()
            for name, (raw, _) in old.items():
                path = self.checkout / name
                if not path.exists() or path.read_bytes() != raw:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
            changed.append(files(self.checkout))

        bundle = files(plan)
        with patch.object(change, "checkpoint", side_effect=race), patch.object(
                tx, "execute", side_effect=AssertionError("Read-only race reached the writer")) as execute:
            with self.assertRaisesRegex(InvalidInput, "Checkout changed"):
                change.adopt(self.checkout, plan, no_op_only=True)
            execute.assert_not_called()
        self.assertEqual(len(changed), 1)
        self.assertEqual(files(self.checkout), changed[0])
        self.assertEqual(files(plan), bundle)

    def test_readonly_option_is_an_explicit_boolean(self):
        before = files(self.checkout)
        for value in (None, 0, 1, "true"):
            with self.subTest(value=value), self.assertRaisesRegex(InvalidInput, "boolean"):
                change.adopt(self.checkout, self.work / "absent-plan", no_op_only=value)
        self.assertEqual(files(self.checkout), before)


if __name__ == "__main__":
    unittest.main()
