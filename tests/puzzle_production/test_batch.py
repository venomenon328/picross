"""Small BA-A orchestration regressions; domain success always comes from files."""
from copy import deepcopy
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from tools.puzzle_production import batch_io, batch_runner as runner
from tools.puzzle_production.contract import InvalidInput, load_json
from tests.puzzle_production.batch_fixtures import (
    BatchFixture, ROOT, artifact_path, checksum, encoded, output_ref, put,
    source_ref, stage_result, stamps, walkthrough_fixture,
)


class BatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ba-a-runner-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.fixture = BatchFixture(self.root / "fixture")

    def one(self, *, attempts=4, revalidations=12):
        job = self.fixture.add_job("one")
        stage = self.fixture.solve_stage(job, produce_attempts=attempts, revalidate_attempts=revalidations)
        self.fixture.write_plan()
        return job, stage

    def call(self, name="run", fixture=None, **overrides):
        fixture = fixture or self.fixture
        args = {"plan_path": fixture.path, "source_root": fixture.source,
                "repo_root": ROOT, "work_root": fixture.work}
        args.update(overrides)
        return getattr(runner, name)(**args)

    def assert_completed(self, report):
        self.assertEqual(report["status"], "completed", self.brief(report))
        self.assertIsNone(report["human_seconds"])

    def brief(self, report):
        return {"status": report.get("status"), "jobs": report.get("jobs"),
                "attempts": [{"number": a["number"], "error": a.get("error"),
                              "domain": (a.get("result") or {}).get("domain"),
                              "reason": (a.get("result") or {}).get("details", {}).get("reason")}
                             for a in report.get("attempts", [])]}

    def rejected(self, name="run", fixture=None, **overrides):
        with self.assertRaises((InvalidInput, ValueError, OSError, runner.BatchTechnicalError)) as error:
            self.call(name, fixture, **overrides)
        return str(error.exception)

    def test_closed_plan_refs_and_strict_json_fail_before_mutation(self):
        _, stage = self.one()
        original = deepcopy(self.fixture.plan)
        invalid = []
        def case(change):
            value = deepcopy(original)
            change(value)
            invalid.append(encoded(value))
        case(lambda p: p.update(extra=True))
        case(lambda p: p.update(revision=True))
        case(lambda p: p.update(source_commit="0" * 40))
        case(lambda p: p["jobs"].append(deepcopy(p["jobs"][0])))
        case(lambda p: p["jobs"][0]["stages"].append(deepcopy(p["jobs"][0]["stages"][0])))
        case(lambda p: p["jobs"][0]["stages"][0].update(kind=[]))
        case(lambda p: p["jobs"][0]["stages"][0].update(operation={}))
        case(lambda p: p["jobs"][0]["stages"][0]["inputs"].update(logic=output_ref("future", "logic")))
        case(lambda p: p["jobs"][0]["stages"][0]["inputs"]["logic"].update(file="../outside.json"))
        case(lambda p: p["jobs"][0]["stages"][0]["inputs"]["logic"].update(sha256="0" * 64))
        case(lambda p: p["jobs"][0]["stages"][0]["tool_binding"].update(modules=[]))
        case(lambda p: p["jobs"][0]["stages"][0]["limits"]["produce"].update(max_lines=True))
        raw = encoded(original)
        invalid.extend((raw.replace(b'"revision":1', b'"revision":1,"revision":1', 1),
                        raw.replace(b'"max_lines":1000', b'"max_lines":NaN', 1),
                        b"\xef\xbb\xbf" + raw))
        before_source, before_work = stamps(self.fixture.source), stamps(self.fixture.work)
        for index, raw in enumerate(invalid):
            with self.subTest(case=index):
                self.fixture.path.write_bytes(raw)
                self.rejected("validate")
                self.assertEqual(stamps(self.fixture.source), before_source)
                self.assertEqual(stamps(self.fixture.work), before_work)
        self.fixture.path.write_bytes(invalid[0])
        self.rejected()
        self.assertEqual(stamps(self.fixture.work), before_work)

    def test_overlapping_roots_symlinks_and_hardlinks_are_rejected(self):
        self.one()
        before = stamps(self.fixture.source)
        self.rejected("validate", work_root=self.fixture.source / "overlap")
        self.assertEqual(stamps(self.fixture.source), before)
        data = self.fixture.data["one"]
        original = self.fixture.source / data["logic"]["file"]
        alias = original.with_name("alias.json")
        alias.write_bytes(original.read_bytes())
        raw = original.read_bytes()
        original.unlink()
        original.symlink_to(alias.name)
        self.rejected("validate")
        original.unlink()
        original.write_bytes(raw)
        alias.unlink()
        os.link(original, alias)
        self.rejected("validate")
        self.assertEqual(stamps(self.fixture.work), {})

    def test_missing_human_decision_blocks_only_its_branch_and_request_is_input_wait(self):
        job = self.fixture.add_job("human", background=True)
        self.fixture.solve_stage(job)
        self.fixture.background(job, offered=True)
        self.fixture.stage(job, "background", "background", "derive", {"request": None})
        self.fixture.stage(job, "build", "authoring_build", "build", {"request": None})
        independent = self.fixture.add_job("independent")
        self.fixture.solve_stage(independent)
        self.fixture.write_plan()
        result = self.call()
        self.assertEqual(result["status"], "incomplete", self.brief(result))
        for name in ("human", "independent"):
            state, attempt = stage_result(result, name, "solve")
            self.assertEqual(state["status"], "completed")
            self.assertTrue(attempt["result"]["certified"])
        self.assertEqual(stage_result(result, "human", "background")[0]["status"], "waiting_human")
        self.assertEqual(stage_result(result, "human", "build")[0]["status"], "waiting_input")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertIsNone(result["human_seconds"])
        for mismatch in ("parameters", "background-revision"):
            with self.subTest(identity=mismatch):
                fixture = BatchFixture(self.root / mismatch)
                job = fixture.add_job("identity", background=mismatch == "background-revision")
                if mismatch == "parameters":
                    fixture.solve_stage(job)
                    ref = job["decisions"]["parameters"]
                    handoff = load_json(fixture.source / ref["file"])
                    handoff["puzzle_id"] = "pz-another-synthetic-puzzle"
                    job["decisions"]["parameters"] = put(fixture.source, ref["file"], handoff)
                else:
                    request = fixture.background(job, none=True)
                    fixture.stage(job, "background", "background", "derive", {"request": request})
                    job["background_revision"] = "bg99"
                fixture.write_plan()
                rejected = self.call(fixture=fixture)
                self.assertEqual(rejected["status"], "incomplete", self.brief(rejected))
                self.assertEqual(rejected["attempts"], [], "wrong identity must fail before booking an operation")
                self.assertEqual(rejected["jobs"][0]["stages"][0]["status"], "failed")

    def test_resume_freshly_revalidates_and_status_is_read_only(self):
        self.one()
        first = self.call()
        self.assert_completed(first)
        _, first_attempt = stage_result(first, "one", "solve")
        proof = artifact_path(self.fixture, first_attempt["result"]["slots"]["proof"])
        original = stamps(proof.parent)
        second = self.call("resume")
        self.assert_completed(second)
        self.assertGreaterEqual(second["elapsed_seconds"], first["elapsed_seconds"])
        state, attempt = stage_result(second, "one", "solve")
        self.assertTrue(state["reused"])
        self.assertEqual(attempt["attempt_type"], "revalidate")
        self.assertEqual(stamps(proof.parent), original)
        self.assertEqual([a["attempt_type"] for a in second["attempts"]], ["produce", "revalidate"])
        before = stamps(self.fixture.work)
        status = runner.status(self.fixture.work)
        self.assertFalse(status["fresh"])
        self.assertEqual(status["report"]["status"], "completed")
        self.assertEqual(stamps(self.fixture.work), before)

    def test_a_real_second_process_cannot_enter_the_same_workspace(self):
        self.one()
        self.assert_completed(self.call())
        program = ("from pathlib import Path\nimport sys\n"
                   "from tools.puzzle_production.batch_io import writer\n"
                   "with writer(Path(sys.argv[1])):\n"
                   " print('locked',flush=True)\n sys.stdin.read()\n")
        process = subprocess.Popen([sys.executable, "-c", program, str(self.fixture.work)], cwd=ROOT,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = queue.Queue()
        reader = threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True)
        reader.start()
        try:
            self.assertEqual(lines.get(timeout=10).strip(), "locked")
            before = stamps(self.fixture.work)
            error = self.rejected("resume")
            self.assertIn("lock", error.lower())
            self.assertEqual(stamps(self.fixture.work), before)
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            process.stdout.close()
            process.stderr.close()

    def test_changed_missing_extra_artifacts_and_forged_checkpoint_are_not_success(self):
        for mutation in ("changed", "missing", "extra", "checkpoint"):
            with self.subTest(mutation=mutation):
                fixture = BatchFixture(self.root / mutation)
                job = fixture.add_job("one")
                fixture.solve_stage(job)
                fixture.write_plan()
                first = self.call(fixture=fixture)
                self.assert_completed(first)
                _, attempt = stage_result(first, "one", "solve")
                proof = artifact_path(fixture, attempt["result"]["slots"]["proof"])
                if mutation == "changed":
                    value = load_json(proof)
                    value["status"] = "stalled"
                    proof.write_bytes(encoded(value))
                elif mutation == "missing":
                    proof.unlink()
                elif mutation == "extra":
                    (proof.parent / "foreign.txt").write_bytes(b"foreign bytes must survive\n")
                else:
                    checkpoint = load_json(fixture.work / "checkpoint.json")
                    checkpoint["attempts"][0]["result"]["domain"] = "forged-success"
                    (fixture.work / "checkpoint.json").write_bytes(encoded(checkpoint))
                broken = stamps(proof.parent)
                if mutation == "checkpoint":
                    self.rejected("resume", fixture=fixture)
                    self.assertEqual(stamps(proof.parent), broken)
                    continue
                result = self.call("resume", fixture=fixture)
                self.assertNotEqual(result["status"], "completed", self.brief(result))
                self.assertEqual(stamps(proof.parent), broken)
                self.assertFalse(any(a.get("result", {}).get("domain") == "forged-success"
                                     for a in result.get("attempts", []) if a.get("result")))

    def test_original_output_inventory_is_checked_after_an_intermediate_revalidation(self):
        self.one()
        first = self.call()
        self.assert_completed(first)
        _, production = stage_result(first, "one", "solve")
        original = self.fixture.work / production["output_dir"]
        self.assert_completed(self.call("resume"))
        foreign = original / "extra-after-revalidation.txt"
        foreign.write_bytes(b"TEST ONLY unaccounted bytes in the original producer directory\n")
        broken = stamps(original)
        result = self.call("resume")
        self.assertNotEqual(result["status"], "completed", self.brief(result))
        self.assertEqual(stage_result(result, "one", "solve")[0]["status"], "failed")
        self.assertIn("inventory", json.dumps(self.brief(result)).lower())
        self.assertEqual(stamps(original), broken)

    def test_forged_overall_completion_cannot_hide_an_open_human_stage(self):
        job = self.fixture.add_job("open", background=True)
        self.fixture.background(job, offered=True)
        self.fixture.stage(job, "background", "background", "derive", {"request": None})
        self.fixture.write_plan()
        result = self.call()
        self.assertEqual(result["status"], "incomplete", self.brief(result))
        checkpoint = load_json(self.fixture.work / "checkpoint.json")
        self.assertEqual(checkpoint["stages"][0]["status"], "waiting_human")
        for status in ("completed", []):
            with self.subTest(status=status):
                checkpoint["status"] = status
                raw = encoded(checkpoint)
                (self.fixture.work / "checkpoint.json").write_bytes(raw)
                with self.assertRaises(runner.BatchTechnicalError):
                    runner.status(self.fixture.work)
                with self.assertRaises(runner.BatchTechnicalError):
                    self.call("resume")
                self.assertEqual((self.fixture.work / "checkpoint.json").read_bytes(), raw)

    def test_parent_only_kill_ends_worker_lifetime_and_worker_lock_prevents_overlap(self):
        self.one()
        self.assert_completed(self.call())
        ready = self.root / "worker-ready.txt"
        # A real process uses the product's lifetime guard and worker lock while
        # standing in for a slow bounded operation. Killing only its parent must
        # close its inherited pipes and lock, not leave an orphan free to write.
        worker = ("import os,sys,time\nfrom pathlib import Path\n"
                  "from tools.puzzle_production.batch_worker import lifetime\n"
                  "from tools.puzzle_production.batch_io import writer\n"
                  "with lifetime(os.getppid(),10),writer(Path(sys.argv[1]),name='.batch-worker.lock'):\n"
                  " Path(sys.argv[2]).write_text(str(os.getpid()))\n time.sleep(30)\n")
        parent = ("import subprocess,sys\n"
                  "child=subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]])\n"
                  "sys.stdin.read()\nchild.wait()\n")
        process = subprocess.Popen([sys.executable, "-c", parent, worker, str(self.fixture.work), str(ready)],
                                   cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 5
            while not ready.is_file() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.is_file(), "real worker never acquired its lifetime/lock")
            before = stamps(self.fixture.work)
            self.assertIn("lock", self.rejected("resume").lower())
            self.assertEqual(stamps(self.fixture.work), before)
            started = time.monotonic()
            process.kill()  # parent only; deliberately not killpg()
            process.communicate(timeout=3)  # inherited pipes remain open until the real worker exits
            self.assertLess(time.monotonic() - started, 3)
            with batch_io.writer(self.fixture.work, name=".batch-worker.lock"):
                pass
            self.assert_completed(self.call("resume"))
        finally:
            if process.poll() is None:
                process.kill()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                # This branch is a failed watchdog test, but its explicitly
                # owned worker still must not survive temporary-directory cleanup.
                if ready.is_file():
                    os.kill(int(ready.read_text()), getattr(signal, "SIGKILL", signal.SIGTERM))
                process.communicate(timeout=3)

    def test_produce_and_revalidate_allowances_are_separate_and_finite(self):
        self.one(attempts=1, revalidations=1)
        self.assert_completed(self.call())
        self.assert_completed(self.call("resume"))
        third = self.call("resume")
        self.assertNotEqual(third["status"], "completed")
        self.assertIn("budget_exhausted", json.dumps(third))
        self.assertEqual([a["attempt_type"] for a in third["attempts"]], ["produce", "revalidate"])

    def test_rename_remove_reinsert_and_revision_do_not_refill_a_production_line(self):
        job, stage = self.one(attempts=1)
        other = self.fixture.add_job("other")
        self.fixture.solve_stage(other)
        self.fixture.write_plan()
        original = self.call()
        self.assert_completed(original)
        _, original_attempt = stage_result(original, "one", "solve")
        proof = artifact_path(self.fixture, original_attempt["result"]["slots"]["proof"])
        saved = stamps(proof.parent)
        self.fixture.plan["jobs"] = [other]
        self.fixture.successor("plan-removed.json")
        self.assert_completed(self.call("resume"))
        # Same puzzle and operation: a new name/revision and changed logic are
        # not a new authorization to spend the already exhausted produce count.
        job["job_id"] = "renamed"
        job["revision"] = "r02"
        stage["stage_id"] = "renamed-solve"
        stage["parameters"]["order"] = "columns-first"
        self.fixture.plan["jobs"] = [job, other]
        self.fixture.successor()
        result = self.call("resume")
        self.assertNotEqual(result["status"], "completed")
        self.assertIn("budget_exhausted", json.dumps(result))
        produced = [a for a in result["attempts"] if a["puzzle_id"] == job["puzzle_id"] and a["attempt_type"] == "produce"]
        self.assertEqual(len(produced), 1)
        self.assertEqual(stamps(proof.parent), saved)
        self.assertEqual(stage_result(result, "other", "solve")[0]["status"], "completed")

    def test_successor_cannot_increase_a_spent_budget(self):
        _, stage = self.one(attempts=1)
        self.assert_completed(self.call())
        before = stamps(self.fixture.work)
        stage["max_attempts"]["produce"] = 2
        self.fixture.successor()
        error = self.rejected("resume")
        self.assertIn("budget", error.lower())
        self.assertEqual(stamps(self.fixture.work), before)

    def test_image_only_change_retains_logic_rating_and_other_job_originals(self):
        fixture = walkthrough_fixture(self.root / "walkthrough")
        initial = self.call(fixture=fixture)
        self.assertEqual(initial["status"], "incomplete", self.brief(initial))
        preserve = {}
        for job_id, stage_id in (("selected", "import"), ("selected", "solve"),
                                  ("selected", "difficulty"), ("waiting", "solve")):
            state, attempt = stage_result(initial, job_id, stage_id)
            self.assertEqual(state["status"], "completed", self.brief(initial))
            preserve[(job_id, stage_id)] = (attempt, stamps(fixture.work / attempt["output_dir"]))
        selected = fixture.plan["jobs"][0]
        request = fixture.background(selected, revision="bg02", color=(20, 90, 180, 128))
        selected["stages"][-1]["inputs"]["request"] = request
        fixture.successor()
        resumed = self.call("resume", fixture=fixture)
        self.assertEqual(resumed["status"], "incomplete", self.brief(resumed))
        for (job_id, stage_id), (old, saved) in preserve.items():
            state, _ = stage_result(resumed, job_id, stage_id)
            self.assertEqual(state["status"], "completed")
            self.assertTrue(state["reused"])
            self.assertEqual(stamps(fixture.work / old["output_dir"]), saved)
            self.assertEqual(len([a for a in resumed["attempts"] if a["job_id"] == job_id and
                                  a["stage_id"] == stage_id and a["attempt_type"] == "produce"]), 1)
        self.assertEqual(len([a for a in resumed["attempts"] if a["job_id"] == "selected" and
                              a["stage_id"] == "background" and a["attempt_type"] == "produce"]), 2)

    def test_local_builder_repeat_is_a_noop_and_changed_same_revision_conflicts(self):
        job = self.fixture.add_job("build")
        request_ref = self.fixture.builder_request(job)
        stage = self.fixture.stage(job, "build", "authoring_build", "build", {"request": request_ref})
        self.fixture.write_plan()
        first = self.call()
        self.assert_completed(first)
        _, attempt = stage_result(first, "build", "build")
        package = artifact_path(self.fixture, attempt["result"]["slots"]["package"])
        before = stamps(package.parent)
        self.assert_completed(self.call("resume"))
        self.assertEqual(stamps(package.parent), before)
        request = load_json(self.fixture.source / request_ref["file"])
        request["handoff"]["next_action"] = "TEST ONLY changed bytes, still the same immutable revision."
        stage["inputs"]["request"] = put(self.fixture.source, request_ref["file"], request)
        self.fixture.successor()
        result = self.call("resume")
        self.assertNotEqual(result["status"], "completed")
        self.assertIn("target_conflict", json.dumps(result))
        self.assertEqual(stamps(package.parent), before)

    def test_later_explicit_background_builder_request_keeps_original_plan_and_open_gates(self):
        job = self.fixture.add_job("none", background=True)
        request = self.fixture.background(job, none=True)
        self.fixture.stage(job, "background", "background", "derive", {"request": request})
        build = self.fixture.stage(job, "build", "authoring_build", "build", {"request": None})
        self.fixture.write_plan()
        original_plan = self.fixture.path.read_bytes()
        first = self.call()
        self.assertEqual(first["status"], "incomplete", self.brief(first))
        self.assertEqual(stage_result(first, "none", "build")[0]["status"], "waiting_input")
        _, bg_attempt = stage_result(first, "none", "background")
        finding = artifact_path(self.fixture, bg_attempt["result"]["slots"]["background_finding"])
        build["inputs"]["request"] = self.fixture.builder_request(job, finding=finding)
        self.fixture.successor()
        second = self.call("resume")
        self.assert_completed(second)
        self.assertEqual((self.fixture.root / "plan-initial.json").read_bytes(), original_plan)
        self.assertEqual(self.fixture.plan["previous_plan_sha256"], checksum(original_plan))
        _, built = stage_result(second, "none", "build")
        handoff = load_json(artifact_path(self.fixture, built["result"]["slots"]["handoff"]))
        self.assertEqual(handoff["format"], "picross-authoring-handoff-v3")
        self.assertEqual(handoff["gates"]["final_editorial"], "pending")
        self.assertEqual(handoff["gates"]["target_export"], "blocked")

    def test_checkpoint_replace_failure_retains_the_previous_complete_bytes(self):
        from unittest.mock import patch
        path = self.root / "checkpoint.json"
        raw = encoded({"before": True})
        path.write_bytes(raw)
        with patch.object(batch_io.os, "fsync", side_effect=OSError("TEST ONLY publish failure")):
            with self.assertRaises(OSError):
                batch_io.replace_json(path, {"after": True}, raw)
        self.assertEqual(path.read_bytes(), raw)

    def test_interruption_after_reservation_consumes_attempt_and_keeps_unknown_usage(self):
        from unittest.mock import patch
        class SimulatedProcessLoss(BaseException):
            pass
        self.one(attempts=1)
        other = self.fixture.add_job("independent")
        self.fixture.solve_stage(other)
        self.fixture.write_plan()
        def interrupted(*args):
            checkpoint = load_json(self.fixture.work / "checkpoint.json")
            self.assertEqual(checkpoint["attempts"][0]["status"], "running")
            reservation = load_json(self.fixture.work / "attempts/000001/reservation.json")
            self.assertEqual(reservation["attempt_type"], "produce")
            self.assertGreater(reservation["reserved_limits"]["seconds"], 0)
            raise SimulatedProcessLoss()
        with patch.object(runner, "_worker", side_effect=interrupted):
            with self.assertRaises(SimulatedProcessLoss):
                self.call()
        resumed = self.call("resume")
        self.assertEqual(resumed["status"], "incomplete", self.brief(resumed))
        interrupted_attempt = resumed["attempts"][0]
        self.assertEqual(interrupted_attempt["status"], "interrupted")
        self.assertIsNone(interrupted_attempt["seconds"])
        self.assertIsNone(interrupted_attempt["result"])
        self.assertIsNone(resumed["elapsed_seconds"])
        self.assertIn("budget_exhausted", stage_result(resumed, "one", "solve")[0]["reason"])
        self.assertEqual(stage_result(resumed, "independent", "solve")[0]["status"], "completed")

    def test_result_ledger_before_checkpoint_is_recovered_then_reverified(self):
        from unittest.mock import patch
        class SimulatedProcessLoss(BaseException):
            pass
        self.one(attempts=1)
        replace = batch_io.replace_json
        def interrupted(path, value, expected):
            if Path(path).name == "checkpoint.json" and value.get("attempts") and value["attempts"][-1]["status"] == "completed":
                self.assertTrue((self.fixture.work / "attempts/000001/result.json").is_file())
                raise SimulatedProcessLoss()
            return replace(path, value, expected)
        with patch.object(batch_io, "replace_json", side_effect=interrupted):
            with self.assertRaises(SimulatedProcessLoss):
                self.call()
        old = load_json(self.fixture.work / "attempts/000001/result.json")
        proof = artifact_path(self.fixture, old["result"]["slots"]["proof"])
        before = stamps(proof.parent)
        result = self.call("resume")
        self.assert_completed(result)
        self.assertEqual([a["attempt_type"] for a in result["attempts"]], ["produce", "revalidate"])
        self.assertTrue(stage_result(result, "one", "solve")[0]["reused"])
        self.assertEqual(stamps(proof.parent), before)


if __name__ == "__main__":
    unittest.main()
