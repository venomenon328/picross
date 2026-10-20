"""Behavioral tests for the CI selection and the final required-result gate."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from ci_scope import FLAGS, JOBS, apply_event_policy, classify, content_path, evaluate, make_plan


class SelectionTests(unittest.TestCase):
    def test_added_data_path_and_both_tree_modes_are_exact(self):
        from unittest.mock import patch
        valid = "content/added/pz-synthetic.json"
        self.assertTrue(classify([valid])["content_only"])
        for path in ("content/added/PZ-synthetic.json", "content/added/pz-Synthetic.json",
                     "content/added/pz-synthetic.JSON", "content/added/pz-synthetic.json.py",
                     "content/added/pz-synthetic/rating.json", "content/added/../pz-synthetic.json",
                     "content/added/pz-synthetic.json/", "content/added/pz-.json", "content/added/other.json"):
            with self.subTest(path=path): self.assertFalse(content_path(path))
        modes = [("000000", "100644")]
        def fake_git(*args):
            if "--name-only" in args: return (valid + "\0").encode()
            if "--raw" in args:
                old, new = modes[0]
                return f":{old} {new} {'a'*40} {'b'*40} M\0{valid}\0".encode()
            if args[0] == "rev-parse": return b"c"*40
            raise AssertionError("Content shortcut must not read blobs: " + repr(args))
        with patch("ci_scope.git", side_effect=fake_git):
            for pair in (("000000", "100644"), ("100644", "000000"), ("100644", "100644")):
                modes[0] = pair
                self.assertTrue(make_plan("a"*40, "b"*40, "auto")["content_only"])
            for mode in ("100755", "120000", "160000"):
                for pair in ((mode, "000000"), ("000000", mode)):
                    modes[0] = pair
                    with self.subTest(pair=pair), self.assertRaises(ValueError):
                        make_plan("a"*40, "b"*40, "auto")
        self.assertTrue(all(classify([valid, "tools/ci_scope.py"])["selected"].values()))

    def test_at_reveal_paths_and_both_sides_of_git_modes(self):
        from unittest.mock import patch
        valid = 'content/reveals/pz-test.json'
        self.assertTrue(classify([valid])['content_only'])
        for path in ('content/reveals/PZ-test.json', 'content/reveals/pz-Test.json', 'content/reveals/pz-test.JSON',
                     'content/reveals/pz-test/record.json', 'content/reveals/pz-test.json.py', 'content/reveals/../pz-test.json',
                     'content/reveals/pz-test.json/', 'content/reveals/pz-.json', 'content/reveals/other.json'):
            with self.subTest(path=path): self.assertFalse(content_path(path))
        paths, modes = [valid], [('000000','100644')]
        def fake_git(*args):
            if '--name-only' in args: return ('\0'.join(paths)+'\0').encode()
            if '--raw' in args: return ''.join(f":{a} {b} {'a'*40} {'b'*40} M\0{p}\0" for p,(a,b) in zip(paths,modes)).encode()
            if args[0] == 'rev-parse': return b'c'*40
            if '--check' in args: return b''
            raise AssertionError(args)
        with patch('ci_scope.git', side_effect=fake_git):
            for pair in [('000000','100644'),('100644','000000'),('100644','100644')]:
                modes[0] = pair; self.assertTrue(make_plan('a'*40,'b'*40,'auto')['content_only'])
            for mode in ('100755','120000','160000'):
                for pair in ((mode,'000000'),('000000',mode)):
                    modes[0] = pair
                    with self.subTest(pair=pair), self.assertRaises(ValueError): make_plan('a'*40,'b'*40,'auto')
            paths[:] = [valid, 'tools/puzzle_production/catalog_reveal.py']; modes[:] = [('100644','000000'),('000000','100644')]
            selected = make_plan('a'*40,'b'*40,'auto')['selected']
            self.assertTrue(all(selected[k] for k in ('docs','production','product','web','delivery')))

    def test_difficulty_data_allowlist_is_exact_and_c1_keeps_full_ci(self):
        allowed = ["content/difficulty/pz-test/rating.json", "content/difficulty/reports/first-run/report.json",
                   "content/difficulty/reports/first-run/report.md"]
        self.assertTrue(classify(allowed)["content_only"])
        for path in ["content/difficulty/pz-test/rating.py", "content/difficulty/pz-test/report.json",
                     "content/difficulty/reports/first-run/trace.json", "content/difficulty/reports/Upper/report.md",
                     "content/difficulty/pz-Test/rating.json", "content/difficulty/pz-test/nested/rating.json",
                     "content/difficulty/reports/../report.md", "content/difficulty/reports/a/report.gd",
                     "content/difficulty/reports/con/report.md", "content/difficulty/reports/lpt9/report.json",
                     "content/difficulty/pz-test/rating.json/", "content/difficulty/pz-test/rating.json.py"]:
            with self.subTest(path=path):
                self.assertFalse(content_path(path))
                self.assertFalse(classify(allowed + [path])["content_only"])
        self.assertTrue(all(classify(allowed + ["tools/ci_scope.py"])["selected"].values()))

    def test_difficulty_modes_deletions_and_renames_use_both_tree_paths(self):
        from unittest.mock import patch
        paths = ["content/difficulty/pz-a/rating.json", "content/difficulty/reports/one/report.md"]
        modes = [("100644", "000000"), ("000000", "100644")]
        def fake_git(*args):
            if "--name-only" in args: return ("\0".join(paths) + "\0").encode()
            if "--raw" in args:
                return "".join(f":{old} {new} {'a'*40} {'b'*40} M\0{p}\0" for p,(old,new) in zip(paths,modes)).encode()
            if args[0] == "rev-parse": return b"c"*40
            if "--check" in args: return b""
            raise AssertionError(args)
        with patch("ci_scope.git", side_effect=fake_git):
            self.assertTrue(make_plan("a"*40, "b"*40, "auto")["content_only"])
            for mode in ("100755", "120000", "160000"):
                for pair in ((mode,"000000"),("000000",mode)):
                    modes[0] = pair
                    with self.subTest(pair=pair), self.assertRaises(ValueError): make_plan("a"*40,"b"*40,"auto")
            paths[0] = "tools/ci_scope.py"  # A rename cannot hide its executable/source side.
            self.assertTrue(all(make_plan("a"*40,"b"*40,"auto")["selected"].values()))

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
                     ".github/workflows/ci-chromium.yml", "unknown.json"]:
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
        for path in ("game/ui/catalog.gd", "game/tests/kat2_probe.gd", "tools/kat2_product.py"):
            plan = classify([path])
            self.assertTrue(plan["selected"]["product"])
            self.assertIn("catalog", plan["native_groups"])
            self.assertNotIn("history", plan["native_groups"])
            if path == "game/ui/catalog.gd":
                self.assertIn("adapters", plan["native_groups"])
                self.assertIn("graphics", plan["native_groups"])
            else:
                self.assertNotIn("adapters", plan["native_groups"])
        self.assertEqual(classify(["tools/kat2_product.py"])["native_groups"], ["catalog"])

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

    def test_unknown_cell_resource_is_conservative(self):
        self.assertTrue(classify(["game/art/cells/unknown.png"])["selected"]["integration"])

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
                     "tests/puzzle_production/test_p1_export.py"]:
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


class PartialCloneTests(unittest.TestCase):
    """Real filtered Git transport with independent synthetic text/binary data."""

    def setUp(self):
        from unittest.mock import patch
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source, self.clone = self.root / "source", self.root / "clone"
        self.source.mkdir()
        self.run_git(self.source, "init", "-q")
        for key, value in (("user.name", "CI fixture"), ("user.email", "ci@example.invalid"),
                           ("core.autocrlf", "false"), ("uploadpack.allowFilter", "true")):
            self.run_git(self.source, "config", key, value)
        self.cwd = Path.cwd()
        self.addCleanup(os.chdir, self.cwd)
        # Isolate the transport from machine-level conversion configuration.
        env = patch.dict(os.environ, {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.autocrlf",
                                      "GIT_CONFIG_VALUE_0": "false"})
        env.start()
        self.addCleanup(env.stop)

    def run_git(self, repo, *args, **kwargs):
        return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL,
                                       timeout=20, **kwargs).decode().strip()

    def write(self, name, data):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def commit(self):
        self.run_git(self.source, "add", "-A")
        self.run_git(self.source, "commit", "-qm", "synthetic fixture")
        return self.run_git(self.source, "rev-parse", "HEAD")

    def start_clone(self):
        self.run_git(self.root, "clone", "-q", "--filter=blob:none", "--no-checkout",
                     self.source.as_uri(), str(self.clone))
        self.assertEqual(self.run_git(self.clone, "config", "remote.origin.promisor"), "true")
        os.chdir(self.clone)

    def lookup(self, oid):
        return self.run_git(self.clone, "--no-lazy-fetch", "cat-file", "--batch-check",
                            input=(oid + "\n").encode())

    def test_batches_both_sides_deleted_renamed_binary_and_many_added_blobs(self):
        from unittest.mock import patch
        import ci_scope
        self.write("docs/change.md", b"before\n")
        self.write("docs/deleted.md", b"deleted text\n")
        self.write("docs/renamed old.md", b"renamed text\n")
        self.write("unchanged.bin", b"\0unrelated corpus\n")
        base = self.commit()
        old = [self.run_git(self.source, "rev-parse", base + ":" + path) for path in
               ("docs/change.md", "docs/deleted.md", "docs/renamed old.md")]
        untouched = self.run_git(self.source, "rev-parse", base + ":unchanged.bin")
        self.write("docs/change.md", b"after\n")
        (self.source / "docs/deleted.md").unlink()
        (self.source / "docs/renamed old.md").rename(self.source / "docs/renamed new.md")
        self.write("binary.png", b"\0synthetic binary\n")
        for i in range(64):
            self.write(f"docs/added {i}.md", f"synthetic line {i}\n".encode())
        head = self.commit()
        self.start_clone()
        self.assertTrue(all(self.lookup(oid).endswith(" missing") for oid in old))
        with patch("ci_scope.git", wraps=ci_scope.git) as calls:
            plan = make_plan(base, head, "auto", fetch=True)
        batches = [c for c in calls.call_args_list if "--stdin" in c.args]
        self.assertEqual(len(batches), 1)
        self.assertGreater(len(batches[0].kwargs["input"].splitlines()), 64)
        self.assertEqual(plan["diff_check"], "full-whitespace-check")
        self.assertTrue(all(" blob " in self.lookup(oid) for oid in old))
        self.assertTrue(self.lookup(untouched).endswith(" missing"))
        with patch("ci_scope.git", wraps=ci_scope.git) as calls:
            make_plan(base, head, "auto", fetch=True)
        self.assertFalse(any("--stdin" in c.args for c in calls.call_args_list))

    def test_whitespace_error_remains_fatal_and_no_base_checks_root(self):
        self.write("docs/bad.md", b"trailing whitespace \n")
        head = self.commit()
        self.start_clone()
        for base in ("", "0" * 40):
            with self.subTest(base=base):
                with self.assertRaises(subprocess.CalledProcessError) as failure:
                    make_plan(base, head, "auto", fetch=True)
                self.assertEqual(failure.exception.returncode, 2)
                self.assertIn(b"trailing whitespace", failure.exception.output)

    def test_content_only_never_fetches_blobs(self):
        self.write("README.md", b"base\n")
        base = self.commit()
        path = "content/authoring/pz-synthetic/r01/package.zip"
        self.write(path, b"\0synthetic content\n")
        head = self.commit()
        oid = self.run_git(self.source, "rev-parse", head + ":" + path)
        self.start_clone()
        plan = make_plan(base, head, "auto", fetch=True)
        self.assertTrue(plan["content_only"])
        self.assertTrue(self.lookup(oid).endswith(" missing"))

    def test_missing_blob_remote_failure_is_fatal(self):
        from ci_scope import fetch_diff_blobs
        self.write("docs/base.md", b"base\n")
        base = self.commit()
        self.write("docs/new.md", b"new\n")
        head = self.commit()
        self.start_clone()
        self.run_git(self.clone, "remote", "set-url", "origin", str(self.root / "absent"))
        with self.assertRaises(subprocess.CalledProcessError):
            fetch_diff_blobs(base, head)


class SchedulerTransportTests(unittest.TestCase):
    """Exercise the real GitHub output producer and fail-closed result evaluator."""

    def test_real_plan_output_and_finish_with_empty_native_selection(self):
        script = str(Path(__file__).with_name("ci_scope.py"))
        for filename, event in (
            ("docs/AT_NOTE.md", "pull_request"),
            ("content/authoring/pz-demo/r01/input.json", "pull_request"),
            ("tools/puzzle_production/analysis.py", "pull_request"),
            ("docs/AT_NOTE.md", "push"),
        ):
            with self.subTest(filename=filename, event=event), tempfile.TemporaryDirectory() as temporary:
                repo = Path(temporary)
                def git(*args):
                    return subprocess.check_output(["git", *args], cwd=repo,
                                                   stderr=subprocess.DEVNULL).decode().strip()
                git("init", "-q")
                git("config", "user.name", "CI fixture")
                git("config", "user.email", "ci@example.invalid")
                (repo / "README.md").write_text("before\n", encoding="utf-8")
                git("add", ".")
                git("commit", "-qm", "base")
                base = git("rev-parse", "HEAD")
                selected = repo / filename
                selected.parent.mkdir(parents=True, exist_ok=True)
                selected.write_text("fixture\n", encoding="utf-8")
                git("add", ".")
                git("commit", "-qm", "change")
                head = git("rev-parse", "HEAD")
                plan_path, outputs_path = repo / "plan.json", repo / "outputs"
                env = {**os.environ, "GITHUB_OUTPUT": str(outputs_path),
                       "GITHUB_RUN_ID": "456", "GITHUB_RUN_ATTEMPT": "1",
                       "GITHUB_EVENT_NAME": event, "GITHUB_STEP_SUMMARY": ""}
                plan_call = subprocess.run([os.sys.executable, script, "plan", "--base", base,
                                            "--head", head, "--scope", "auto", "--event", event,
                                            "--output", str(plan_path)], cwd=repo,
                                           env=env, capture_output=True, text=True, timeout=20)
                self.assertEqual(plan_call.returncode, 0, plan_call.stderr)
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                self.assertEqual(plan["native_groups"], [])
                # Simulate the real scheduler discarding empty values, not a hand-built full dictionary.
                emitted = dict(line.split("=", 1) for line in outputs_path.read_text().splitlines())
                scheduled = {key: value for key, value in emitted.items()
                             if key in (*FLAGS, "selection_attempt", "native_groups") and value != ""}
                self.assertEqual(scheduled["native_groups"], "[]")
                self.assertEqual(set(scheduled), set(FLAGS) | {"selection_attempt", "native_groups"})
                self.assertEqual(scheduled["product"], "false")
                binding = {key: plan[key] for key in ("source_head", "base_commit", "tested_checkout",
                                                     "run_id", "run_attempt", "event")}
                binding["gate_attempt"] = "1"
                results = {job: {"result": "success" if plan["selected"][job] else "skipped"}
                           for job in JOBS}
                result_file = repo / "gate.json"
                finish_env = {**env, "GITHUB_ACTIONS": "true",
                              "CI_BINDING": json.dumps(binding),
                              "CI_RESULTS": json.dumps(results)}
                def finish(gate_outputs):
                    return subprocess.run([os.sys.executable, script, "finish", "--plan-file",
                                           str(plan_path), "--output", str(result_file)],
                                          cwd=repo, env={**finish_env, "CI_OUTPUTS": json.dumps(gate_outputs)},
                                          capture_output=True, text=True, timeout=20)
                passed = finish(scheduled)
                self.assertEqual(passed.returncode, 0, passed.stderr)
                self.assertTrue(json.loads(result_file.read_text())["accepted"])
                for invalid in (
                    {key: val for key, val in scheduled.items() if key != "native_groups"},
                    {**scheduled, "native_groups": ""},
                    {**scheduled, "native_groups": " [] "},
                    {**scheduled, "native_groups": '["core"]'},
                    {**scheduled, "native_groups": None},
                    {**scheduled, "unexpected": "false"},
                ):
                    with self.subTest(invalid=invalid):
                        self.assertNotEqual(finish(invalid).returncode, 0)

    def test_nonempty_group_order_and_workflow_consumers(self):
        from ci_scope import native_groups_output, validate_binding
        from native_contract import GROUPS
        for paths, force in ( (["tools/kat2_product.py"], "auto"), ([], "all") ):
            plan = apply_event_policy(classify(paths, force), "pull_request")
            self.assertTrue(plan["native_groups"])
            binding = dict(source_head="a" * 40, base_commit="b" * 40,
                           tested_checkout="c" * 40, run_id="123", run_attempt="1",
                           event="pull_request", gate_attempt="1")
            plan.update({key: binding[key] for key in binding if key != "gate_attempt"},
                        comparison="exact-base-to-head-trees-no-renames",
                        diff_check="full-whitespace-check")
            outputs = {key: str(plan["selected"][key]).lower() for key in FLAGS}
            outputs.update(selection_attempt="1", native_groups=native_groups_output(plan["native_groups"]))
            self.assertEqual(json.loads(outputs["native_groups"]), plan["native_groups"])
            validate_binding(plan, binding, outputs)
            for malformed in (
                ",".join(plan["native_groups"]),
                json.dumps(plan["native_groups"]),
                json.dumps(list(reversed(plan["native_groups"])), separators=(",", ":")),
                "[]",
                '{"groups":[]}',
            ):
                if malformed == outputs["native_groups"]:
                    continue
                with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                    validate_binding(plan, binding, {**outputs, "native_groups": malformed})
            if force == "all":
                self.assertEqual(plan["native_groups"], list(GROUPS))
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/ci-chromium.yml").read_text()
        self.assertIn("join(fromJSON(needs.docs.outputs.native_groups), ',')", workflow)
        self.assertIn("contains(fromJSON(needs.docs.outputs.native_groups), 'export')", workflow)
        self.assertIn("needs.docs.outputs.product == 'true' && contains(", workflow)


class RequiredGateTests(unittest.TestCase):
    def test_large_selection_file_keeps_every_path_and_rejects_failed_jobs(self):
        plan = classify([f"content/authoring/pz-{i}/r01/production/area-128-proof.json" for i in range(5000)])
        results = {key: {"result": "success" if key == "docs" else "skipped"} for key in JOBS}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "selection.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            self.assertGreater(path.stat().st_size, 131072)
            for status, expected in [("success", 0), ("failure", 1)]:
                results["docs"]["result"] = status
                run = subprocess.run([os.sys.executable, str(Path(__file__).with_name("ci_scope.py")), "finish",
                                      "--plan-file", str(path), "--results", json.dumps(results)],
                                     capture_output=True, text=True, timeout=10, env={**os.environ, "GITHUB_ACTIONS": "false"})
                self.assertEqual(run.returncode, expected, run.stderr)
                self.assertEqual(json.loads(run.stdout)["accepted"], expected == 0)
            self.assertEqual(len(json.loads(path.read_text())["changed_paths"]), 5000)

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
                             capture_output=True, text=True, timeout=10, env={**os.environ, "GITHUB_ACTIONS": "false"})
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(run.stdout)["accepted"])


if __name__ == "__main__":
    unittest.main()
