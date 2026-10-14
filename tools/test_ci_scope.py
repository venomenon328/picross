"""Behavioral tests for the CI selection and the final required-result gate."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from ci_scope import FLAGS, JOBS, apply_event_policy, classify, content_path, evaluate, make_plan


class SelectionTests(unittest.TestCase):
    def test_puzzle_deliveries_select_no_test_suites_at_any_catalog_size(self):
        paths = ["content/registry.json", "game/data/registry.json", "content/authoring/index.json"]
        for i in range(500):
            paths += [f"content/authoring/pz-{i}/r01/package.zip",
                      f"content/packages/pz-{i}/r01/input/import/area-proof.json",
                      f"game/data/content/puzzle_{i}.json", f"game/art/content/puzzle_{i}.png"]
        plan = classify(paths)
        self.assertTrue(plan["content_only"])
        self.assertFalse(any(plan["selected"][k] for k in FLAGS))
        self.assertTrue(apply_event_policy(plan, "push")["content_only"])

    def test_content_shortcut_cannot_hide_code_assets_or_explicit_widening(self):
        for path in ["game/data/content/loader.gd", "game/art/content/importer.py",
                     "content/authoring/pz-a/r01/run.py", "content/packages/pz-a/r01/plugin.gd",
                     "content/.registration-pending.json", "game/art/book/paper.png",
                     ".github/workflows/setup.yml", "unknown.json"]:
            with self.subTest(path=path):
                self.assertFalse(content_path(path))
                plan = classify(["game/data/content/a.json", path])
                self.assertFalse(plan["content_only"])
                self.assertTrue(any(plan["selected"][k] for k in FLAGS))
        self.assertFalse(classify(["content/registry.json", "docs/CI_POLICY.md"])["content_only"])
        self.assertFalse(classify(["content/registry.json"], "all")["content_only"])

    def test_content_diff_uses_no_blob_reads_and_rejects_executable_or_symlink(self):
        from unittest.mock import patch
        calls = []
        def fake_git(*args):
            calls.append(args)
            if "--name-only" in args: return b"content/authoring/pz-a/r01/package.zip\0"
            if "--raw" in args: return (f":000000 {mode} {'0'*40} {'a'*40} A\0content/authoring/pz-a/r01/package.zip\0").encode()
            if args[0] == "rev-parse": return b"c"*40
            raise AssertionError("Unexpected corpus/blob access: " + repr(args))
        mode = "100644"
        with patch("ci_scope.git", side_effect=fake_git):
            self.assertTrue(make_plan("a"*40, "b"*40, "auto")["content_only"])
            for mode in ["100755", "120000", "160000"]:
                with self.subTest(mode=mode), self.assertRaises(ValueError):
                    make_plan("a"*40, "b"*40, "auto")

    def test_catalog_native_route_and_harness_keep_required_checks(self):
        for path in ("game/ui/catalog.gd", "game/tests/kat2_probe.gd"):
            selected = classify([path])["selected"]
            self.assertTrue(selected["product"] and selected["integration"] and selected["visual"] and selected["perf_b"])
        self.assertTrue(all(classify(["tools/kat2_product.py"])["selected"].values()))

    def test_save_recovery_and_gameplay_keep_integration_without_manufacturer(self):
        for path in ("game/model/save_store.gd", "game/model/gesture.gd", "game/ui/main.gd"):
            value = classify([path])["selected"]
            self.assertTrue(value["product"] and value["integration"] and value["visual"] and value["perf_b"])
            self.assertFalse(value["production"] or value["preflight"])

    def test_runtime_resources_select_native_regression(self):
        for path in ("game/ui/cell_atlas.gd", "game/art/cells/x-small.png", "tools/perf_b_resources.py", "tools/cell_atlas_reference.json", "game/tests/perf_b_cases.gd"):
            value = classify([path])["selected"]
            self.assertTrue(value["visual"] and value["perf_b"] and value["product"])
            self.assertFalse(value["integration"] or value["preflight"])

    def test_removed_legacy_game_paths_preserve_required_coverage(self):
        plan = classify(["prototypes/p1/model/save_store.gd", "docs/archived.md"])
        self.assertTrue(plan["selected"]["integration"] and plan["selected"]["product"])

    def test_document_only_change_requires_only_docs(self):
        plan = classify(["docs/VS2_VERIFICATION.md", "game/README.md"])
        self.assertTrue(plan["selected"]["docs"])
        self.assertFalse(any(plan["selected"][key] for key in FLAGS))

    def test_renderer_selects_real_pixels_without_unrelated_pilot_replay(self):
        selection = classify(["game/ui/pencil_marks.gd"])["selected"]
        self.assertTrue(selection["product"] and selection["visual"])
        self.assertFalse(selection["pilots"] or selection["production"] or selection["integration"])

    def test_state_and_navigation_keep_500_action_route(self):
        for path in ["game/model/player.gd", "game/ui/board.gd"]:
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

    def test_hash_bound_markdown_and_technical_fixture_files_are_inputs(self):
        for path in ["examples/rp4/SELECTION.md", "game/data/technical.json",
                     "tests/puzzle_production/fixtures/catalog/runtime.json", "game/tests/rp6_probe.gd"]:
            with self.subTest(path=path):
                value = classify([path])["selected"]
                self.assertTrue(value["production"] and value["pilots"])

    def test_active_technical_vs_corpus_keeps_production_verification(self):
        for path in ["game/full_view_study/cases/vs01/definition.json",
                     "game/full_view_study/catalog.json"]:
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
                source = Path("game/ui/board.gd")
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
                self.assertIn("game/ui/board.gd", plan["changed_paths"])
                self.assertIn("docs/archived.md", plan["changed_paths"])
                self.assertTrue(plan["selected"]["integration"])
            finally:
                os.chdir(old_cwd)


class RequiredGateTests(unittest.TestCase):
    def test_content_result_still_requires_successful_scope_job(self):
        plan = classify(["content/registry.json"])
        results = {key: {"result": "success" if key == "docs" else "skipped"} for key in JOBS}
        self.assertTrue(all(row["accepted"] for row in evaluate(plan, results)))
        results["docs"]["result"] = "failure"
        self.assertFalse(all(row["accepted"] for row in evaluate(plan, results)))
        plan["selected"]["production"] = True
        with self.assertRaises(ValueError): evaluate(plan, results)

    def test_success_and_explicit_not_applicable_are_accepted(self):
        for paths in [["README.md"], ["game/ui/board.gd"], ["new_unknown.py"]]:
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

    def test_incomplete_subscope_or_scope_without_product_is_rejected(self):
        plan = classify([], force="all")
        del plan["selected"]["perf_b"]
        with self.assertRaises(ValueError):
            evaluate(plan, {})
        plan = classify([], force="all")
        plan["selected"]["product"] = False
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
