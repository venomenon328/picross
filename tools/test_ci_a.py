"""CI-A dependency, execution and adversarial gate probes; no real puzzle inputs."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from ci_scope import (ANALYSIS_PATHS, FLAGS, JOBS, apply_event_policy, classify,
                      evaluate, unique_object, validate_binding, native_groups_output)

ROOT = Path(__file__).resolve().parents[1]
# The exact 17 changed paths of #241, not a copy of its puzzle/calibration data.
PR241 = ["AGENTS.md", *["docs/" + name + ".md" for name in (
    "PAIRED_LINES", "PRODUCT_DEFINITION", "PROJECT_PROFILE", "PUZZLE_DIFFICULTY",
    "PUZZLE_PRODUCTION", "SD_ANALYZER", "SD_CALIBRATION")],
    "tests/puzzle_production/test_difficulty_rating.py", "tools/puzzle_production/README.md",
    *["tools/puzzle_production/" + name for name in (
        "analysis_cli.py", "analysis_io.py", "difficulty_calibration_0_3.json",
        "difficulty_identity.py", "difficulty_method_0_3.json", "difficulty_rating.py",
        "difficulty_references_0_3.json")]]


def jobs(paths, force="auto", event="pull_request"):
    plan = apply_event_policy(classify(paths, force), event)
    return {key for key in JOBS if plan["selected"][key]}


class DependencyTests(unittest.TestCase):
    def test_exact_analysis_allowlist_and_reference_diff(self):
        self.assertEqual(len(PR241), 17)
        self.assertEqual(jobs(PR241), {"docs", "production"})
        for path in ANALYSIS_PATHS:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())
                self.assertEqual(jobs([path]), {"docs", "production"})
        for name in ("contract.py", "__init__.py", "p1_export.py", "content_registry.py",
                     "catalog_rating.py", "catalog_difficulty.py", "za1_fixtures.py",
                     "analysis_new.py", "difficulty_method_0_4.json"):
            self.assertTrue({"product", "web", "delivery", "production"} <=
                            jobs(["tools/puzzle_production/" + name]))

    def test_template_exception_is_exact_and_union_preserves_obligations(self):
        template = ".github/pull_request_template.md"
        self.assertEqual(jobs([template]), {"docs"})
        for path in (".github/other.md", ".github/workflows/web-chromium.yml", ".github/workflows/delivery.yml"):
            self.assertEqual(jobs([path]), set(JOBS))
        self.assertEqual(jobs([template, "tools/deploy_web.py"]), {"docs", "delivery"})
        self.assertEqual(jobs(PR241 + ["tools/deploy_web.py"]), {"docs", "production", "delivery"})
        self.assertEqual(jobs(PR241 + ["unknown.py"]), set(JOBS))

    def test_browser_delivery_native_and_shared_dependencies(self):
        for path in ("tools/deploy_web.py", "tools/web_tests/ssh_reference.py"):
            self.assertEqual(jobs([path]), {"docs", "delivery"})
        for path in ("tools/web_tests/browser.py", "tools/web_tests/smoke.py"):
            self.assertEqual(jobs([path]), {"docs", "web"})
        self.assertEqual(jobs(["tools/perf_b_resources.py"]), {"docs", "product"})
        for path in ("game/ui/main.gd", "game/model/save_store.gd"):
            self.assertEqual(jobs([path]), {"docs", "product", "web"})
        for path in ("tools/build_web_player.py", "tools/web_bundle.py", "tools/web_tests/serve.py"):
            self.assertEqual(jobs([path]), {"docs", "web", "delivery"})
        for path in ("game/export_presets.cfg", "game/project.godot", "game/web/shell.html"):
            self.assertTrue({"product", "web", "delivery"} <= jobs([path]))

    def test_manual_scopes_and_main_contract(self):
        expected = {
            "auto": {"docs"}, "all": set(JOBS), "toolchain": set(JOBS),
            "runtime": {"docs", "product", "web"}, "visual": {"docs", "product", "web"},
            "perf-b": {"docs", "product", "web"},
            "production": {"docs", "production", "product", "web", "delivery"},
        }
        for scope, selected in expected.items():
            self.assertEqual(jobs([], scope), selected)
            self.assertEqual(jobs(["tools/deploy_web.py"], scope), selected | {"delivery"})
        self.assertEqual(jobs(["tools/ci_scope.py"], event="push"), {"docs", "production"})
        self.assertEqual(jobs(["tools/deploy_web.py"], event="push"), {"docs"})

    def test_real_rename_delete_and_full_diff_not_last_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            def git(*args):
                return subprocess.check_output(["git", "-C", temporary, *args], stderr=subprocess.DEVNULL).decode().strip()
            git("init", "-q"); git("config", "user.name", "CI probe")
            git("config", "user.email", "ci@example.invalid")
            root = Path(temporary)
            p = root / "tools/deploy_web.py"; p.parent.mkdir(); p.write_text("base\n")
            git("add", "."); git("commit", "-qm", "base"); base = git("rev-parse", "HEAD")
            p.rename(root / "README.md")
            git("add", "-A"); git("commit", "-qm", "rename")
            (root / "README.md").write_text("later docs\n")
            git("add", "."); git("commit", "-qm", "docs")
            plan_file = root / "plan.json"
            subprocess.run([sys.executable, str(ROOT / "tools/ci_scope.py"), "plan", "--base", base,
                            "--head", git("rev-parse", "HEAD"), "--event", "pull_request",
                             "--output", str(plan_file)],
                           cwd=root, capture_output=True, check=True)
            plan = json.loads(plan_file.read_text())
            self.assertEqual(plan["changed_paths"], ["README.md", "tools/deploy_web.py"])
            self.assertTrue(plan["selected"]["delivery"])
            self.assertFalse(plan["selected"]["web"])


class AdversarialGateTests(unittest.TestCase):
    def test_independent_checks_cannot_impersonate_each_other(self):
        for paths in (["tools/deploy_web.py"], ["tools/web_tests/browser.py"],
                      ["tools/deploy_web.py", "tools/web_tests/browser.py"]):
            plan = classify(paths)
            results = {key: {"result": "success" if plan["selected"][key] else "skipped"} for key in JOBS}
            self.assertTrue(all(r["accepted"] for r in evaluate(plan, results)))
            for job in ("web", "delivery"):
                for status in ("failure", "cancelled", "skipped", "", None, "missing", "success"):
                    changed = deepcopy(results); changed[job]["result"] = status
                    self.assertEqual(all(r["accepted"] for r in evaluate(plan, changed)),
                                     status == results[job]["result"])
                changed = deepcopy(results); del changed[job]
                with self.assertRaises(ValueError): evaluate(plan, changed)

    def test_forged_selection_and_malformed_results_fail_closed(self):
        plan = classify(["tools/deploy_web.py"])
        results = {key: {"result": "success" if plan["selected"][key] else "skipped"} for key in JOBS}
        for key, value in (("selected", {**plan["selected"], "delivery": False}),
                           ("reasons", {}), ("changed_paths", []), ("requested_scope", "all")):
            changed = deepcopy(plan); changed[key] = value
            with self.assertRaises(ValueError): evaluate(changed, results)
        for value in (None, [], {**results, "surprise": {"result": "success"}},
                      {**results, "delivery": {}}, {**results, "delivery": "success"}):
            with self.assertRaises(ValueError): evaluate(plan, value)
        for raw in ('{"delivery":true,"delivery":false}', '{"docs":{"result":"success","result":"skipped"}}'):
            with self.assertRaises(ValueError): json.loads(raw, object_pairs_hook=unique_object)

    def test_source_run_and_scheduler_binding(self):
        plan = apply_event_policy(classify(["tools/deploy_web.py"]), "pull_request")
        binding = dict(source_head="a"*40, base_commit="b"*40, tested_checkout="c"*40,
                       run_id="123", run_attempt="2", event="pull_request")
        plan.update(binding, comparison="exact-base-to-head-trees-no-renames", diff_check="full-whitespace-check")
        outputs = {key: str(plan["selected"][key]).lower() for key in FLAGS}
        outputs["selection_attempt"] = "2"
        outputs["native_groups"] = native_groups_output(plan["native_groups"])
        binding["gate_attempt"] = "2"
        validate_binding(plan, binding, outputs)
        binding["gate_attempt"] = "3"
        validate_binding(plan, binding, outputs)  # same-run successful-job reuse
        for attempt in ("1", "", "0", "wrong"):
            with self.assertRaises(ValueError):
                validate_binding(plan, {**binding, "gate_attempt": attempt}, outputs)
        for key in set(binding) - {"gate_attempt"}:
            for value in (None, "wrong"):
                changed = deepcopy(plan); changed[key] = value
                with self.assertRaises(ValueError): validate_binding(changed, binding, outputs)
        for key in FLAGS:
            changed = dict(outputs); del changed[key]
            with self.assertRaises(ValueError): validate_binding(plan, binding, changed)
            changed[key] = "false" if outputs[key] == "true" else "true"
            with self.assertRaises(ValueError): validate_binding(plan, binding, changed)
        with self.assertRaises(ValueError):
            validate_binding(plan, binding, {**outputs, "selection_attempt": "1"})


def run_blocks(source):
    """Read only the literal run blocks used by these two pinned workflows.

    This is deliberately not a YAML parser. Fail on an unrecognized run shape.
    Actions metadata/conditions are checked separately below.
    """
    lines = source.splitlines()
    blocks = []
    for i, line in enumerate(lines):
        if line.startswith("        run: "):
            value = line.removeprefix("        run: ")
            if value == "|":
                body = []
                for following in lines[i+1:]:
                    if following and not following.startswith("          "): break
                    body.append(following)
                value = textwrap.dedent("\n".join(body))
            elif value.startswith((">", "|")):
                raise AssertionError("Unsupported run block")
            blocks.append(value)
    if not blocks: raise AssertionError("No executable workflow steps")
    return blocks


class WorkflowExecutionTests(unittest.TestCase):
    def test_scheduler_and_gate_have_both_independent_jobs(self):
        source = (ROOT / ".github/workflows/ci-chromium.yml").read_text()
        for job, workflow in (("web", "web-chromium"), ("delivery", "delivery")):
            condition = f"needs.docs.outputs.{job} == 'true'"
            if job == "web":
                condition += " && github.event.pull_request.number != 411"
            section = source.split(f"  {job}:\n", 1)[1].split("\n\n", 1)[0]
            self.assertIn("    needs: docs\n", section)
            self.assertIn(f"    if: {condition}\n    uses: ./.github/workflows/{workflow}.yml", section)
            self.assertIn(f'"{job}":{{"result":"${{{{ needs.{job}.result }}}}"}}', source)
        self.assertIn("needs: [docs, product, production, preflight, web, delivery]", source)
        self.assertIn("CI_OUTPUTS: ${{ toJSON(needs.docs.outputs) }}", source)
        self.assertIn("CI_BINDING:", source)

    def test_pr411_web_omission_keeps_required_gate_incomplete(self):
        plan = classify(["content/difficulty-method.json"])
        self.assertTrue(plan["selected"]["web"])
        results = {job: {"result": "success" if plan["selected"][job] else "skipped"}
                   for job in JOBS}
        self.assertTrue(all(row["accepted"] for row in evaluate(plan, results)))
        results["web"]["result"] = "skipped"
        rows = evaluate(plan, results)
        self.assertFalse(next(row["accepted"] for row in rows if row["job"] == "web"))
        self.assertFalse(all(row["accepted"] for row in rows))

    @unittest.skipUnless(sys.platform == "linux", "Executes the Linux workflow shell on its actual platform")
    def test_actual_workflow_commands_with_synthetic_tools_and_failure_propagation(self):
        # Execute the real shell blocks with journalled external tools. No engine,
        # browser, SSH server or network. The full CI separately runs real tools.
        for kind in ("delivery",):  # CI-B tests the new build/browser workflows separately.
            source = (ROOT / f".github/workflows/{kind}.yml").read_text()
            blocks = run_blocks(source)
            with tempfile.TemporaryDirectory() as temporary:
                work = Path(temporary); bin_dir = work / "bin"; bin_dir.mkdir()
                venv = work / "web-venv/bin"; venv.mkdir(parents=True)
                journal = work / "commands.jsonl"
                stub = '#!' + sys.executable + '\n' + textwrap.dedent('''\
                    import json, os, sys
                    from pathlib import Path
                    args = [Path(sys.argv[0]).name, *sys.argv[1:]]
                    with open(os.environ['JOURNAL'], 'a') as out: out.write(json.dumps(args)+'\\n')
                    if os.environ.get('FAIL_COMMAND') and os.environ['FAIL_COMMAND'] in ' '.join(args): sys.exit(23)
                    ''')
                for path in [bin_dir / n for n in ("python3", "sudo", "xvfb-run")] + [venv / n for n in ("pip", "python", "playwright")]:
                    path.write_text(stub); path.chmod(0o755)
                env = {**os.environ, "PATH": str(bin_dir)+os.pathsep+os.environ["PATH"], "JOURNAL": str(journal)}
                def execute(failure=""):
                    for block in blocks:
                        result = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c",
                            block.replace("${{ runner.temp }}", temporary)], cwd=work,
                            env={**env, "FAIL_COMMAND": failure}, capture_output=True)
                        if result.returncode: return result.returncode
                    return 0
                self.assertEqual(execute(), 0)
                calls = [json.loads(line) for line in journal.read_text().splitlines()]
                builds = [c for c in calls if "tools/build_web_player.py" in c]
                self.assertEqual(len(builds), 1)
                self.assertNotIn("--test", builds[0])
                self.assertFalse(any(any(word in ' '.join(c) for word in ("playwright", "xvfb", "web-test", "smoke.py", "browser.py")) for c in calls))
                required = "ssh_reference.py"
                print("CI_A_EXECUTION_PROBE " + json.dumps({"route": kind, "commands": calls,
                    "real_external_tools": False, "build_count": len(builds)}, sort_keys=True), flush=True)
                for failure in ("build_web_player.py", required):
                    self.assertEqual(execute(failure), 23)


if __name__ == "__main__":
    unittest.main()
