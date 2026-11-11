"""Selected BA-B regressions with real small native exports and transactions.

Fixtures are synthetic and shared with the one-time actual SIGKILL CLI probe.
These cases test orchestration boundaries; existing native suites retain the
full proof, palette, publication, budget and no-op-only race contracts.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.integration_batch_fixtures import (
    IntegrationFixture, checksum, encoded, stamps,
)
from tools.puzzle_production import background_request, catalog_background_change as background_change
from tools.puzzle_production import catalog_publication, catalog_transaction
from tools.puzzle_production import content_registry, integration_batch_cli, integration_batch_runner
from tools.puzzle_production import target_adapter
from tools.puzzle_production.contract import InvalidInput, load_json


class IntegrationBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="ba-b-selected-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.home = Path(cls.temporary.name)
        cls.template = IntegrationFixture(cls.home / "template")

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="case-", dir=self.home)
        self.addCleanup(self.directory.cleanup)
        self.local = Path(self.directory.name)
        self.fixture = self.template.clone(self.local / "fixture")

    def choose(self, names):
        self.fixture.plan["jobs"] = [job for job in self.fixture.plan["jobs"] if job["job_id"] in names]
        self.fixture.save()

    def cli(self, command, *, fixture=None, work=None):
        fixture = fixture or self.fixture
        argv = [command, "--work-root", str(work or fixture.work)]
        if command != "status":
            argv += ["--plan", str(fixture.path), "--source-root", str(fixture.source),
                     "--repo-root", str(fixture.repo), "--target-root", str(fixture.target)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = integration_batch_cli.main(argv)
        self.assertTrue(stdout.getvalue(), stderr.getvalue())
        return code, json.loads(stdout.getvalue())

    def completed(self, report):
        detail = {"status": report["status"],
                  "jobs": [{key: value.get(key) for key in ("job_id", "status", "reason")}
                           for value in report["jobs"]]}
        self.assertEqual((report["status"], report["exit_code"]), ("completed", 0), detail)
        self.assertTrue(all(job["historical_completed"] and job["current_verified"]
                            for job in report["jobs"]))

    def test_two_real_registrations_plan_sequentially_and_final_resume_is_readonly(self):
        self.choose({"selected", "none"})
        f = self.fixture
        before = stamps(f.source)
        calls = []
        original = content_registry.registration

        def registration(export, target, **kwargs):
            result = original(export, target, **kwargs)
            calls.append((kwargs.get("apply", False), deepcopy(result), deepcopy(kwargs)))
            return result

        with patch.object(content_registry, "registration", side_effect=registration):
            report = integration_batch_runner.run(**f.arguments())
        self.completed(report)
        plans = [result for apply, result, _ in calls if not apply and result["status"] == "planned"]
        self.assertEqual([value["id"] for value in plans], ["pz-ba-b-selected", "pz-ba-b-none"])
        self.assertIn("pz-ba-b-selected", {entry["id"] for entry in plans[1]["before"]["entries"]})
        writes = [(result, kwargs) for apply, result, kwargs in calls if apply]
        self.assertEqual([result["status"] for result, _ in writes], ["registered", "registered"])
        for _, kwargs in writes:
            self.assertEqual((kwargs["publication_seconds"], kwargs["recovery_seconds"]), (1800, 1800))
        for apply, _, kwargs in calls:
            if not apply:
                self.assertNotIn("publication_seconds", kwargs)
                self.assertNotIn("recovery_seconds", kwargs)
        self.assertEqual(stamps(f.source), before)
        target_before = stamps(f.target, control=False)
        with patch.object(content_registry, "registration", side_effect=AssertionError("A booked result is checked through its reached binding")):
            self.completed(integration_batch_runner.resume(**f.arguments()))
        self.assertEqual(stamps(f.target, control=False), target_before)
        work_before = stamps(f.work)
        code, historical = self.cli("status")
        self.assertEqual(code, 3)
        self.assertIs(historical["fresh"], False)
        self.assertEqual(historical["report"]["status"], "incomplete")
        self.assertEqual(stamps(f.work), work_before)

    def test_booked_background_before_later_register_uses_one_current_snapshot(self):
        f = self.fixture
        originals = stamps(f.source)
        report = integration_batch_runner.run(**f.arguments())
        self.completed(report)
        registry = load_json(f.target / content_registry.REGISTRY)
        self.assertEqual({entry["id"] for entry in registry["entries"]},
                         {"pz-ba-b-existing", "pz-ba-b-selected", "pz-ba-b-none"})
        target_before = stamps(f.target, control=False)
        with patch.object(background_change, "adopt", side_effect=AssertionError("Old catalog-bound plan must not be adopted again")), \
                patch.object(catalog_transaction, "capture", wraps=catalog_transaction.capture) as capture:
            resumed = integration_batch_runner.resume(**f.arguments())
        self.completed(resumed)
        self.assertEqual(capture.call_count, 1)
        self.assertEqual(stamps(f.target, control=False), target_before)
        self.assertEqual(stamps(f.source), originals)
        self.assertTrue(any(a["result"] and a["result"]["native"].get("status") == "reconciled"
                            for a in resumed["attempts"] if a["reservation"]["phase"] == "reconcile"))

    def test_unbooked_native_registration_is_confirmed_without_a_second_apply(self):
        self.choose({"selected"})
        f = self.fixture
        original = content_registry.registration
        applied = []

        def interrupt_after_real_publish(export, target, **kwargs):
            result = original(export, target, **kwargs)
            if kwargs.get("apply"):
                applied.append(result)
                raise InterruptedError("TEST ONLY after actual native completion, before batch booking")
            return result

        with patch.object(content_registry, "registration", side_effect=interrupt_after_real_publish):
            interrupted = integration_batch_runner.run(**f.arguments())
        self.assertNotEqual(interrupted["status"], "completed")
        self.assertEqual([value["status"] for value in applied], ["registered"])
        self.assertFalse((f.target / catalog_transaction.LOCK).exists())
        native_before = stamps(f.target, control=False)
        calls = []

        def readonly(export, target, **kwargs):
            self.assertFalse(kwargs.get("apply", False), "Resume used a writer for diagnosis")
            result = original(export, target, **kwargs)
            calls.append(result)
            return result

        with patch.object(content_registry, "registration", side_effect=readonly):
            resumed = integration_batch_runner.resume(**f.arguments())
        self.completed(resumed)
        self.assertTrue(any(value["status"] == "no-op" and value["registered"] and value["changes"] == [] for value in calls))
        self.assertEqual(stamps(f.target, control=False), native_before)

    def test_missing_optional_inputs_and_decisions_remain_explicit_before_writers(self):
        for key, status in (("authorization", "waiting_human"), ("approval", "waiting_human"), ("package", "waiting_input")):
            with self.subTest(key=key):
                f = self.template.clone(self.local / ("missing-" + key))
                f.plan["jobs"] = [f.plan["jobs"][0]]
                job = f.plan["jobs"][0]
                if key == "authorization":
                    job[key] = None
                else:
                    job["inputs"][key] = None
                f.save()
                before = stamps(f.target, control=False)
                with patch.object(target_adapter, "export", side_effect=AssertionError("Missing gate reached export")), \
                        patch.object(content_registry, "registration", side_effect=AssertionError("Missing gate reached writer")):
                    report = integration_batch_runner.run(**f.arguments())
                self.assertEqual((report["status"], report["exit_code"]), ("incomplete", 3))
                self.assertEqual(report["jobs"][0]["status"], status)
                self.assertEqual(stamps(f.target, control=False), before)

    def test_all_declared_originals_are_checked_before_the_first_writer(self):
        f = self.fixture
        ref = f.plan["jobs"][-1]["inputs"]["difficulty"]
        path = f.source / ref["file"]
        path.write_bytes(path.read_bytes() + b" ")
        target_before = stamps(f.target, control=False)
        source_before = stamps(f.source)
        with patch.object(target_adapter, "export", side_effect=AssertionError("Late invalid bytes allowed an earlier writer")):
            code, response = self.cli("run")
        self.assertEqual(code, 2, response)
        self.assertEqual(stamps(f.target, control=False), target_before)
        self.assertEqual(stamps(f.source), source_before)

    def test_closed_forms_reject_invalid_json_identity_paths_and_budgets_without_writes(self):
        f = self.fixture
        original = deepcopy(f.plan)
        before = stamps(f.target, control=False)
        changes = (
            lambda plan: plan.update(unexpected=True),
            lambda plan: plan["jobs"].append(deepcopy(plan["jobs"][0])),
            lambda plan: plan["jobs"][0]["budgets"].update(publication_seconds=True),
            lambda plan: plan["jobs"][0]["max_attempts"].update(apply=0),
            lambda plan: plan["jobs"][0]["inputs"]["package"].update(file="../outside.zip"),
            lambda plan: plan["jobs"][0].update(operation="retire"),
        )
        for index, change in enumerate(changes):
            value = deepcopy(original)
            change(value)
            f.path.write_bytes(encoded(value))
            with self.subTest(case=index):
                code, response = self.cli("validate")
                self.assertEqual(code, 2, response)
                self.assertEqual(stamps(f.target, control=False), before)
                self.assertFalse(f.work.exists())
        raw = encoded(original)
        for malformed in (b'{"format":"duplicate",' + raw[1:], raw.replace(b'"export_seconds":300', b'"export_seconds":NaN', 1)):
            f.path.write_bytes(malformed)
            code, response = self.cli("validate")
            self.assertEqual(code, 2, response)
        self.assertEqual(stamps(f.target, control=False), before)

    def test_native_staging_and_pending_require_separate_recovery_before_resume(self):
        for phase in ("journal-complete", "P3"):
            with self.subTest(phase=phase):
                f = self.template.clone(self.local / ("stop-" + phase))
                f.plan["jobs"] = [f.plan["jobs"][0]]
                f.save()
                original = stamps(f.target, control=False)

                def stop(actual, name=None):
                    if actual == phase:
                        raise InterruptedError("TEST ONLY retained native " + phase)

                with patch.object(catalog_publication, "checkpoint", side_effect=stop), \
                        patch.object(content_registry, "recover", side_effect=AssertionError("Runner must not recover automatically")):
                    interrupted = integration_batch_runner.run(**f.arguments())
                self.assertEqual(interrupted["jobs"][0]["status"], "recovery_required",
                                 interrupted["jobs"][0]["reason"])
                pending = stamps(f.target, control=False)
                with patch.object(content_registry, "recover", side_effect=AssertionError("Resume must not recover automatically")):
                    refused = integration_batch_runner.resume(**f.arguments())
                self.assertEqual(refused["jobs"][0]["status"], "recovery_required")
                self.assertEqual(stamps(f.target, control=False), pending)
                self.assertEqual(content_registry.recover(f.target)["status"], "rolled-back")
                self.assertEqual(stamps(f.target, control=False), original)
                self.completed(integration_batch_runner.resume(**f.arguments()))

    def test_successful_prefix_survives_a_later_native_collision(self):
        self.choose({"selected", "none"})
        f = self.fixture
        f.plan["jobs"][1]["parameters"]["stem"] = f.plan["jobs"][0]["parameters"]["stem"]
        f.save()
        report = integration_batch_runner.run(**f.arguments())
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["jobs"][0]["status"], "completed")
        self.assertIn(report["jobs"][1]["status"], ("blocked", "failed"))
        entries = load_json(f.target / content_registry.REGISTRY)["entries"]
        self.assertEqual({entry["id"] for entry in entries}, {"pz-ba-b-existing", "pz-ba-b-selected"})
        before = stamps(f.target, control=False)
        resumed = integration_batch_runner.resume(**f.arguments())
        self.assertEqual(resumed["status"], "incomplete")
        self.assertEqual(stamps(f.target, control=False), before)

    def test_partial_native_store_preserves_foreign_bytes_and_stops_later_jobs(self):
        f = self.fixture
        f.plan["jobs"] = [f.plan["jobs"][1], f.plan["jobs"][2]]
        f.save()
        selected = f.plan["jobs"][0]
        partial = f.target / background_request.selection(selected["puzzle_id"], selected["revision"])
        partial.mkdir(parents=True)
        (partial / "foreign.txt").write_bytes(b"TEST ONLY foreign incomplete store bytes\n")
        before = stamps(f.target, control=False)
        with patch.object(content_registry, "registration", side_effect=AssertionError("A later writer followed an unsettled store")):
            report = integration_batch_runner.run(**f.arguments())
        self.assertEqual(report["status"], "incomplete")
        self.assertIn(report["jobs"][0]["status"], ("blocked", "failed"))
        self.assertFalse(report["jobs"][1]["historical_completed"])
        self.assertEqual(stamps(f.target, control=False), before)

    def test_successor_cannot_overtake_or_remove_unbooked_real_background_publication(self):
        f = self.fixture
        f.plan["jobs"] = [f.plan["jobs"][1], f.plan["jobs"][2]]
        f.save()
        initial = deepcopy(f.plan)
        previous = checksum(f.path.read_bytes())
        native = []
        original_book = integration_batch_runner._Ledger.book

        def stop_before_booking(ledger, attempt, result):
            if attempt["reservation"]["phase"] == "adopt":
                native.append(deepcopy(result["native"]))
                raise InterruptedError("TEST ONLY real background publication before its batch result")
            return original_book(ledger, attempt, result)

        with patch.object(integration_batch_runner._Ledger, "book", new=stop_before_booking), \
                self.assertRaisesRegex(integration_batch_runner.BatchTechnicalError, "before its batch result"):
            integration_batch_runner.run(**f.arguments())
        self.assertEqual([value["status"] for value in native], ["adopted"])
        checkpoint = load_json(f.work / "checkpoint.json")
        self.assertEqual(checkpoint["attempts"][-1]["reservation"]["phase"], "adopt")
        self.assertIsNone(checkpoint["attempts"][-1]["result"])
        target_before, work_before = stamps(f.target, control=False), stamps(f.work)
        for name, selected in (("overtake", list(reversed(initial["jobs"]))),
                               ("remove", [initial["jobs"][1]])):
            f.plan = {**deepcopy(initial), "revision": 2, "previous_plan_sha256": previous,
                      "jobs": deepcopy(selected)}
            f.save()
            with self.subTest(successor=name), \
                    patch.object(target_adapter, "export", side_effect=AssertionError("A new writer overtook unresolved adoption")), \
                    self.assertRaisesRegex(integration_batch_runner.BatchTechnicalError, "unresolved writer"):
                integration_batch_runner.resume(**f.arguments())
            self.assertEqual(stamps(f.target, control=False), target_before)
            self.assertEqual(stamps(f.work), work_before)

    def test_successor_cannot_remove_a_real_partial_store_with_remaining_paths(self):
        f = self.fixture
        f.plan["jobs"] = [f.plan["jobs"][1], f.plan["jobs"][2]]
        f.save()
        previous = checksum(f.path.read_bytes())

        def stop_after_work_before_index(name):
            if name == "before-index-publication":
                raise OSError("TEST ONLY real work directory published before its index")

        with patch.object(background_change, "checkpoint", side_effect=stop_after_work_before_index):
            report = integration_batch_runner.run(**f.arguments())
        self.assertNotEqual(report["status"], "completed")
        attempt = next(a for a in report["attempts"] if a["reservation"]["phase"] == "store")
        self.assertNotEqual(attempt["result"]["status"], "completed")
        selected = f.plan["jobs"][0]
        partial = f.target / background_request.selection(selected["puzzle_id"], selected["revision"])
        self.assertTrue((partial / "record.json").is_file())
        self.assertFalse((f.target / background_request.INDEX).exists())
        self.assertEqual(attempt["result"]["remaining"], [str(partial)])
        target_before, work_before = stamps(f.target, control=False), stamps(f.work)
        f.plan.update(revision=2, previous_plan_sha256=previous, jobs=[f.plan["jobs"][1]])
        f.save()
        with patch.object(target_adapter, "export", side_effect=AssertionError("A later writer followed a removed partial store")), \
                self.assertRaisesRegex(integration_batch_runner.BatchTechnicalError, "unresolved writer"):
            integration_batch_runner.resume(**f.arguments())
        self.assertEqual(stamps(f.target, control=False), target_before)
        self.assertEqual(stamps(f.work), work_before)

    def test_consumed_apply_cannot_be_refilled_by_rename_or_another_workroot(self):
        self.choose({"selected"})
        f = self.fixture
        f.plan["jobs"][0]["max_attempts"]["apply"] = 1
        f.save()
        original = content_registry.registration
        writes = []

        def blocked(export, target, **kwargs):
            if kwargs.get("apply"):
                writes.append(None)
                raise InvalidInput("TEST ONLY controlled rejection before native mutation")
            return original(export, target, **kwargs)

        with patch.object(content_registry, "registration", side_effect=blocked):
            first = integration_batch_runner.run(**f.arguments())
            self.assertEqual(first["status"], "incomplete")
            previous = checksum(f.path.read_bytes())
            f.plan["revision"] += 1
            f.plan["previous_plan_sha256"] = previous
            f.plan["jobs"][0]["job_id"] = "renamed"
            f.save()
            second = integration_batch_runner.resume(**f.arguments())
            self.assertEqual(second["status"], "incomplete")
        self.assertEqual(len(writes), 1)
        before = stamps(f.target, control=False)
        f.plan.update(batch_id="new-name-same-authorization", revision=1, previous_plan_sha256=None)
        f.save()
        code, response = self.cli("run", work=self.local / "another-work")
        self.assertIn(code, (2, 5), response)
        self.assertEqual(stamps(f.target, control=False), before)
        self.assertTrue(any(a["reservation"]["phase"] == "apply" and a["reservation"]["ordinal"] == 1
                            for a in second["attempts"]))


if __name__ == "__main__":
    unittest.main()
