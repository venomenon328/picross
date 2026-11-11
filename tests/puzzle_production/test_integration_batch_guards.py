"""BA-B ownership/history boundaries, not substitutes for real native tests."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tests.puzzle_production.integration_batch_fixtures import IntegrationFixture, encoded, file_ref, stamps
from tools.puzzle_production import batch_io as bio, catalog_io
from tools.puzzle_production import content_registry, catalog_background_change, integration_batch_contract as contract
from tools.puzzle_production import integration_batch_cli
from tools.puzzle_production import integration_batch_runner as runner, integration_batch_operations as operations
from tools.puzzle_production import operation_diagnostics as diagnostics, target_adapter
from tools.puzzle_production.contract import Aborted, InvalidInput, load_json


class IntegrationBatchGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ba-b-guards-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.template = IntegrationFixture(cls.root / "template")
        cls.jobs = deepcopy(cls.template.plan["jobs"])
        cls.template.plan["jobs"] = [cls.template.plan["jobs"][0]]
        cls.template.save()

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory(prefix="case-", dir=self.root)
        self.addCleanup(self.temp_case.cleanup)
        self.fixture = self.template.clone(Path(self.temp_case.name) / "fixture")

    def test_transport_corruption_is_a_closed_error_including_unhashable_values(self):
        view = runner._view(self.fixture.plan["jobs"][0])
        for key in ("status", "operation"):
            value = deepcopy(view); value[key] = []
            with self.subTest(key=key), self.assertRaises(InvalidInput):
                contract.job_view(value)
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}',
                    b'{"a":1e999}', b'[' * 33 + b'0' + b']' * 33):
            with self.subTest(raw=raw[:30]), self.assertRaises((InvalidInput, ValueError)):
                bio.json_bytes(raw)
        plan = deepcopy(self.fixture.plan)
        for key in ("revision", "source_commit", "jobs"):
            changed = deepcopy(plan); changed[key] = True
            with self.subTest(key=key), self.assertRaises(InvalidInput):
                contract.validate_plan(changed)
        f = self.fixture
        package = f.source / "invalid-package.zip"
        before = stamps(f.target, control=False)
        for malformed_rulebook in (False, True):
            if malformed_rulebook:
                with zipfile.ZipFile(package, "w") as archive:
                    archive.writestr("handoff.json", encoded({
                        "puzzle_id": f.plan["jobs"][0]["puzzle_id"],
                        "revision": f.plan["jobs"][0]["revision"], "test_only": True, "rulebook": []}))
            else:
                package.write_bytes(b"TEST ONLY malformed original ZIP")
            f.plan["jobs"][0]["inputs"]["package"] = file_ref(f.source, package.name)
            f.save()
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = integration_batch_cli.main([
                    "validate", "--plan", str(f.path), "--source-root", str(f.source),
                    "--repo-root", str(f.repo), "--target-root", str(f.target)])
            self.assertEqual(code, 2, stdout.getvalue())
            self.assertEqual(json.loads(stdout.getvalue())["status"], "invalid_input")
            self.assertFalse(f.work.exists())
            self.assertEqual(stamps(f.target, control=False), before)

    def test_checkout_lock_excludes_different_workroots_and_unsafe_aliases(self):
        f = self.fixture
        f.plan["jobs"][0]["authorization"] = None
        f.save()
        other = f.root / "second-work"
        command = [sys.executable, "-m", "tools.puzzle_production.integration_batch_cli", "run",
                   "--plan", str(f.path), "--source-root", str(f.source), "--repo-root", str(f.repo),
                   "--target-root", str(f.target), "--work-root", str(other)]
        before = stamps(f.target, control=False)
        with runner._control(f.target):
            child = subprocess.run(command, cwd=f.repo, capture_output=True, text=True, timeout=45)
            self.assertEqual(child.returncode, 2, child.stderr + child.stdout[:1000])
            self.assertIn("lock", child.stdout)
            self.assertFalse(other.exists())
        alias = f.root / "target-alias"
        alias.symlink_to(f.target, target_is_directory=True)
        with self.assertRaises(InvalidInput):
            runner.validate(**{**f.arguments(), "target_root": alias})
        self.assertEqual(stamps(f.target, control=False), before)

    def test_safe_shared_tool_target_roots_and_unsafe_source_hardlinks(self):
        f = self.fixture
        # The roots guard must allow the executing checkout itself as target
        # and explicitly selected authoring sources within it. No writer runs.
        roots = runner._roots(f.repo / "content/authoring", f.repo, f.repo, f.work, None)
        self.assertEqual(roots[1], roots[2])
        original = f.source / f.plan["jobs"][0]["authorization"]["file"]
        linked = f.root / "foreign-hardlink"
        os.link(original, linked)
        with self.assertRaisesRegex(InvalidInput, "hardlink"):
            runner.validate(**f.arguments())
        self.assertFalse(f.work.exists())

    def test_unbooked_foreign_export_is_preserved_and_fresh_export_spends_own_allowance(self):
        f = self.fixture
        original_boundary = runner.checkpoint
        interrupted = []
        def boundary(name):
            original_boundary(name)
            if name == "before-result-publication" and not interrupted:
                interrupted.append(name)
                raise OSError("TEST ONLY checkpoint destination failed after actual export")
        with patch.object(runner, "checkpoint", side_effect=boundary), self.assertRaises(runner.BatchTechnicalError):
            runner.run(**f.arguments())
        checkpoint = load_json(f.work / "checkpoint.json")
        self.assertEqual(len(checkpoint["attempts"]), 1)
        self.assertIsNone(checkpoint["attempts"][0]["result"])
        original_source = stamps(f.source)
        unknown = f.work / "attempts/000001/output/export"
        shutil.rmtree(unknown)
        shutil.copytree(f.preparation / "none-export", unknown)
        foreign = stamps(unknown)
        with patch.object(target_adapter, "export", wraps=target_adapter.export) as exported:
            report = runner.resume(**f.arguments())
        self.assertEqual(report["status"], "completed", [(j["status"], j["reason"]) for j in report["jobs"]])
        self.assertEqual(exported.call_count, 1)
        self.assertEqual(stamps(unknown), foreign)
        entries = load_json(f.target / content_registry.REGISTRY)["entries"]
        self.assertEqual({e["id"] for e in entries}, {"pz-ba-b-existing", "pz-ba-b-selected"})
        self.assertIsNone(report["execution_seconds"])
        self.assertEqual(stamps(f.source), original_source)

        limited = self.template.clone(f.root / "limited")
        limited.plan["jobs"][0]["max_attempts"]["export"] = 1
        limited.save(); interrupted.clear()
        with patch.object(runner, "checkpoint", side_effect=boundary), self.assertRaises(runner.BatchTechnicalError):
            runner.run(**limited.arguments())
        before = stamps(limited.target, control=False)
        with patch.object(target_adapter, "export", side_effect=AssertionError("Refilled local export allowance")), \
                patch.object(content_registry, "registration", side_effect=AssertionError("Unbooked export reached registration")):
            refused = runner.resume(**limited.arguments())
        self.assertEqual(refused["jobs"][0]["status"], "blocked")
        self.assertIn("budget_exhausted", refused["jobs"][0]["reason"])
        self.assertEqual(stamps(limited.target, control=False), before)

    def test_unanchored_forged_adopt_result_never_certifies_the_old_target(self):
        f = self.fixture
        f.plan["jobs"] = [deepcopy(self.jobs[1])]; f.save()
        original = runner.checkpoint
        def interrupt(name):
            original(name)
            if name == "after-reservation":
                value = load_json(f.work / "checkpoint.json")
                if value["attempts"][-1]["reservation"]["phase"] == "adopt":
                    raise OSError("TEST ONLY before native adoption")
        with patch.object(runner, "checkpoint", side_effect=interrupt), self.assertRaises(runner.BatchTechnicalError):
            runner.run(**f.arguments())
        cp = load_json(f.work / "checkpoint.json")
        attempted = cp["attempts"][-1]
        self.assertIsNone(attempted["result"])
        forged = deepcopy(cp["attempts"][-2]["result"])
        forged.update(number=attempted["reservation"]["number"], output_files=[],
                      reached=operations.reached(f.target, f.plan["jobs"][0]["puzzle_id"]))
        forged["native"]["status"] = "adopted"
        contract.result(forged)
        result_path = f.work / "attempts" / f"{attempted['reservation']['number']:06d}" / "result.json"
        result_path.write_bytes(encoded(forged))
        old = deepcopy(forged["reached"])
        with patch.object(catalog_background_change, "adopt", wraps=catalog_background_change.adopt) as adopted:
            report = runner.resume(**f.arguments())
        self.assertEqual(report["status"], "completed", [(j["status"], j["reason"]) for j in report["jobs"]])
        self.assertEqual(adopted.call_count, 1, "A forged old target incorrectly bypassed real adoption")
        self.assertFalse(adopted.call_args.kwargs.get("no_op_only", False))
        self.assertNotEqual(report["jobs"][0]["reached"], old)
        self.assertIsNone(report["attempts"][attempted["reservation"]["number"]-1]["result"])
        self.assertEqual(result_path.read_bytes(), encoded(forged), "Untrusted original was overwritten")

    def test_result_anchor_crash_inside_a_prereserved_group_uses_fresh_readers(self):
        f = self.fixture
        f.plan["jobs"] = [deepcopy(self.jobs[0]), deepcopy(self.jobs[2])]; f.save()
        original = runner.checkpoint
        crashed = []
        def interrupt(name):
            original(name)
            if name != "before-anchor-publication" or crashed: return
            path = f.work / "checkpoint.json"
            if not path.exists(): return
            cp = load_json(path)
            group = [a for a in cp["attempts"] if a["reservation"]["phase"] == "reconcile"]
            if len(group) == 2 and group[0]["result"] is not None and group[1]["result"] is None:
                crashed.append(group[0]["reservation"]["number"])
                raise OSError("TEST ONLY result published before its group anchor")
        with patch.object(runner, "checkpoint", side_effect=interrupt), self.assertRaises(runner.BatchTechnicalError):
            runner.run(**f.arguments())
        self.assertEqual(len(crashed), 1)
        before = stamps(f.target, control=False)
        with patch.object(content_registry, "registration", side_effect=AssertionError("Group resume must use fresh reached readers")):
            report = runner.resume(**f.arguments())
        self.assertEqual(report["status"], "completed", [(j["status"], j["reason"]) for j in report["jobs"]])
        self.assertIsNone(report["attempts"][crashed[0]-1]["result"])
        self.assertEqual(stamps(f.target, control=False), before)

    def test_successor_checkpoint_crash_finishes_only_the_unexecuted_plan_transition(self):
        f = self.fixture
        f.plan["jobs"][0]["authorization"] = None
        f.save()
        first = runner.run(**f.arguments())
        self.assertEqual(first["jobs"][0]["status"], "waiting_human")
        f.plan["previous_plan_sha256"] = bio.sha(f.path.read_bytes())
        f.plan["revision"] = 2
        f.plan["jobs"][0]["job_id"] = "renamed-waiting-order"
        f.save()
        original = runner.checkpoint
        def interrupt(name):
            original(name)
            if name == "before-anchor-publication" and load_json(f.work / "checkpoint.json")["plan"]["revision"] == 2:
                raise OSError("TEST ONLY successor checkpoint published before its anchor")
        before = stamps(f.target, control=False)
        with patch.object(runner, "checkpoint", side_effect=interrupt), self.assertRaises(runner.BatchTechnicalError):
            runner.resume(**f.arguments())
        work_before = stamps(f.work)
        status = runner.status(f.work)
        self.assertFalse(status["fresh"])
        self.assertEqual(stamps(f.work), work_before)
        f.plan["previous_plan_sha256"] = bio.sha(f.path.read_bytes())
        f.plan["revision"] = 3
        f.plan["jobs"][0]["job_id"] = "third-waiting-order"
        f.save()
        # Even a second interruption while accepting Plan 3 must first leave
        # the proven Plan 2 transition recoverable, never CP3 with Anchor1.
        with patch.object(runner, "checkpoint", side_effect=interrupt), self.assertRaises(runner.BatchTechnicalError):
            runner.resume(**f.arguments())
        with patch.object(target_adapter, "export", side_effect=AssertionError("Plan transition is not an integration order")):
            report = runner.resume(**f.arguments())
        self.assertEqual(report["jobs"][0]["status"], "waiting_human")
        self.assertEqual(report["attempts"], [])
        cp = load_json(f.work / "checkpoint.json")
        self.assertEqual(cp["plan"]["revision"], 3)
        anchor = load_json(f.target / runner.CONTROL / "anchors" / (f.plan["batch_id"] + ".json"))
        self.assertEqual(anchor["plan_sha256"], cp["plan"]["sha256"])
        self.assertEqual(stamps(f.target, control=False), before)

    def test_external_anchor_rejects_byte_changed_and_truncated_result_history(self):
        f = self.fixture
        report = runner.run(**f.arguments())
        self.assertEqual(report["status"], "completed")
        target = stamps(f.target, control=False)
        first_result = f.work / "attempts/000001/result.json"
        original = first_result.read_bytes()
        first_result.write_bytes(original + b" ")  # Same JSON semantics, wrong immutable original bytes.
        with self.assertRaisesRegex(runner.BatchTechnicalError, "anchor|history"):
            runner.resume(**f.arguments())
        first_result.write_bytes(original)
        last = sorted((f.work / "attempts").iterdir())[-1]
        moved = f.root / "preserved-last-attempt"
        last.rename(moved)
        try:
            with self.assertRaisesRegex(runner.BatchTechnicalError, "Truncated|truncated|history"):
                runner.resume(**f.arguments())
        finally:
            moved.rename(last)
        self.assertEqual(stamps(f.target, control=False), target)

    def test_changed_reached_target_retains_historical_success_without_any_repair(self):
        f = self.fixture
        report = runner.run(**f.arguments())
        self.assertEqual(report["status"], "completed")
        entry = next(e for e in load_json(f.target / content_registry.REGISTRY)["entries"] if e["id"] == "pz-ba-b-selected")
        target = f.target / "game" / entry["reveal"]
        target.write_bytes(b"TEST ONLY foreign changed target, deliberately invalid\n")
        before = stamps(f.target, control=False)
        with patch.object(content_registry, "registration", side_effect=AssertionError("Read-only stale reconciliation reached writer")):
            resumed = runner.resume(**f.arguments())
        self.assertEqual(resumed["status"], "incomplete")
        self.assertEqual(resumed["jobs"][0]["status"], "stale")
        self.assertTrue(resumed["jobs"][0]["historical_completed"])
        self.assertFalse(resumed["jobs"][0]["current_verified"])
        self.assertEqual(stamps(f.target, control=False), before)

    def test_register_apply_preserves_separate_native_budget_frames(self):
        f = self.fixture
        job = f.plan["jobs"][0]
        output = f.root / "bounded-call"; output.mkdir()
        times = {"now": 100.0}
        observed = []
        def native(export, target, **kwargs):
            self.assertIsNone(catalog_io._deadline.get(), "Batch imposed an outer deadline on native recovery")
            self.assertTrue(kwargs["apply"])
            for phase, key in (("Publication", "publication_seconds"), ("Recovery", "recovery_seconds")):
                with diagnostics.operation(phase, kwargs[key], "controlled-native-boundary"):
                    times["now"] += kwargs[key] - 1
                    catalog_io.tick()
                    observed.append(phase)
            raise InvalidInput("TEST ONLY no mutation in the controlled-clock dispatch check")
        # This narrow controlled-clock check tests wrapper budgets only. Real
        # native success/rollback and all dispatch results run in the other cases.
        with patch.object(diagnostics.time, "monotonic", side_effect=lambda: times["now"]), \
                patch.object(content_registry, "registration", side_effect=native), redirect_stdout(io.StringIO()), \
                self.assertRaises(InvalidInput):
            operations.execute("apply", job, f.source, f.target, output, None,
                               export_dir=f.preparation / "selected-export")
        self.assertEqual(observed, ["Publication", "Recovery"])


if __name__ == "__main__":
    unittest.main()
