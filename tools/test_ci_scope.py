"""Behavioral tests for the CI selection and the final required-result gate."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from ci_scope import FLAGS, JOBS, apply_event_policy, classify, evaluate, make_plan


class SelectionTests(unittest.TestCase):
    def test_document_only_change_requires_only_docs(self):
        plan = classify(["docs/VS2_VERIFICATION.md", "prototypes/p1/README.md"])
        self.assertTrue(plan["selected"]["docs"])
        self.assertFalse(any(plan["selected"][key] for key in FLAGS))

    def test_renderer_selects_real_pixels_without_unrelated_pilot_replay(self):
        selection = classify(["prototypes/p1/ui/pencil_marks.gd"])["selected"]
        self.assertTrue(selection["product"] and selection["visual"])
        self.assertFalse(selection["pilots"] or selection["production"] or selection["integration"])

    def test_state_and_navigation_keep_500_action_route(self):
        for path in ["prototypes/p1/model/player.gd", "prototypes/p1/ui/board.gd"]:
            with self.subTest(path=path):
                self.assertTrue(classify([path])["selected"]["integration"])

    def test_production_reconstructs_inputs_and_exercises_pilots(self):
        for path in ["tools/puzzle_production/export.py", "examples/rp6/plan.json",
                     "tests/puzzle_production/test_lines.py"]:
            with self.subTest(path=path):
                value = classify([path])["selected"]
                self.assertTrue(value["production"] and value["product"] and value["pilots"])

    def test_active_inputs_in_docs_do_not_use_document_shortcut(self):
        value = classify(["docs/design/book_inventory/composition/inputs/fonts.json"])["selected"]
        self.assertTrue(value["product"] and value["visual"])

    def test_hash_bound_markdown_and_actual_pilot_files_are_inputs(self):
        for path in ["examples/rp4/SELECTION.md", "prototypes/p1/data/f05.json",
                     "prototypes/p1/art/f05.png", "prototypes/p1/tests/rp6_probe.gd"]:
            with self.subTest(path=path):
                value = classify([path])["selected"]
                self.assertTrue(value["production"] and value["pilots"])

    def test_active_technical_vs_corpus_keeps_production_verification(self):
        for path in ["prototypes/p1/full_view_study/cases/vs01/definition.json",
                     "prototypes/p1/full_view_study/catalog.json"]:
            with self.subTest(path=path):
                self.assertTrue(classify([path])["selected"]["production"])

    def test_unknown_paths_and_ci_changes_fail_toward_full_coverage(self):
        for path in ["unknown/new_runtime.py", ".github/workflows/p1-product.yml"]:
            with self.subTest(path=path):
                self.assertTrue(all(classify([path])["selected"].values()))

    def test_manual_scope_only_widens_actual_changed_paths(self):
        plan = classify(["tools/puzzle_production/core.py"], force="visual")
        self.assertTrue(plan["selected"]["production"] and plan["selected"]["visual"])
        self.assertTrue(all(classify([], force="all")["selected"].values()))
        with self.assertRaises(ValueError):
            classify([], force="none")

    def test_main_push_preserves_integrity_checks_without_repeating_product(self):
        plan = apply_event_policy(classify(["tools/puzzle_production/core.py"]), "push")
        self.assertTrue(plan["selected"]["docs"] and plan["selected"]["production"])
        self.assertFalse(plan["selected"]["product"] or plan["selected"]["preflight"])
        pr = apply_event_policy(classify(["tools/puzzle_production/core.py"]), "pull_request")
        self.assertTrue(pr["selected"]["product"] and pr["selected"]["pilots"])

    def test_real_diff_includes_deleted_and_renamed_input_paths(self):
        old_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as temporary:
            os.chdir(temporary)
            try:
                def git(*args):
                    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL).decode().strip()
                git("init", "-q")
                git("config", "user.name", "CI test")
                git("config", "user.email", "ci-test@example.invalid")
                source = Path("prototypes/p1/ui/board.gd")
                source.parent.mkdir(parents=True)
                source.write_text("old current renderer\n")
                git("add", ".")
                git("commit", "-qm", "base")
                base = git("rev-parse", "HEAD")
                Path("docs").mkdir()
                source.rename("docs/archived.md")
                git("add", "-A")
                git("commit", "-qm", "move")
                plan = make_plan(base, git("rev-parse", "HEAD"), "auto")
                self.assertIn("prototypes/p1/ui/board.gd", plan["changed_paths"])
                self.assertIn("docs/archived.md", plan["changed_paths"])
                self.assertTrue(plan["selected"]["integration"])
            finally:
                os.chdir(old_cwd)


class RequiredGateTests(unittest.TestCase):
    def test_success_and_explicit_not_applicable_are_accepted(self):
        for paths in [["README.md"], ["prototypes/p1/ui/board.gd"], ["new_unknown.py"]]:
            plan = classify(paths)
            results = {key: {"result": "success" if plan["selected"][key] else "skipped"} for key in JOBS}
            self.assertTrue(all(row["accepted"] for row in evaluate(plan, results)))

    def test_failure_cancel_skipped_missing_required_job_never_turn_green(self):
        plan = classify([], force="all")
        for job in JOBS:
            for outcome in ["failure", "cancelled", "skipped", "missing"]:
                with self.subTest(job=job, outcome=outcome):
                    results = {key: {"result": "success"} for key in JOBS}
                    results[job]["result"] = outcome
                    self.assertFalse(all(row["accepted"] for row in evaluate(plan, results)))

    def test_missing_or_corrupted_selection_is_rejected(self):
        for plan in [{}, {"format": "picross-ci-selection-v1", "selected": {"docs": False}}]:
            with self.assertRaises(ValueError):
                evaluate(plan, {})

    def test_cli_returns_nonzero_for_failed_required_job(self):
        plan = classify([], force="all")
        results = {key: {"result": "success"} for key in JOBS}
        results["product"]["result"] = "failure"
        run = subprocess.run([os.sys.executable, str(Path(__file__).with_name("ci_scope.py")), "finish",
                              "--plan", json.dumps(plan), "--results", json.dumps(results)],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(run.stdout)["accepted"])


if __name__ == "__main__":
    unittest.main()
