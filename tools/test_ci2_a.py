"""CI2-A: original opt-in, exact scopes, scheduler boundaries and inert Git IO."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from ci_scope import (ANALYSIS_PATHS, FLAGS, JOBS, apply_event_policy, classify,
                      request_output)
from test_ci_a import run_blocks
from test_ci_b import fixture, plan_for, write
from web_tests.contract import GROUPS, browser_request

ROOT = Path(__file__).resolve().parents[1]


class ExplicitRequest(unittest.TestCase):
    def test_all_20_sd2_paths_and_integration_boundaries(self):
        pure = {p for p in ANALYSIS_PATHS if '/sd2_' in p or '/test_sd2_' in p}
        self.assertEqual(len(pure), 20)
        for path in pure:
            self.assertTrue((ROOT/path).is_file(), path)
            for event in ('pull_request', 'push'):
                plan = apply_event_policy(classify([path]), event)
                self.assertEqual({j for j in JOBS if plan['selected'][j]},
                                 {'docs', 'production'} if event == 'pull_request' else {'docs'})
        for name in ('sd2_catalog_rating.py', 'sd2_new.py', 'catalog_analysis.py',
                     'catalog_method.py', 'contract.py', 'content_registry.py', 'p1_export.py', 'za1_fixtures.py'):
            plan = classify([*pure, 'tools/puzzle_production/'+name])
            self.assertEqual({j for j in JOBS if plan['selected'][j]}, set(JOBS)-{'web', 'preflight'})
        plan = classify([*pure, 'tests/puzzle_production/test_sd2_catalog.py'])
        self.assertTrue(plan['selected']['product'])
        # Main is not a blanket restriction: conscious dispatch still runs it.
        self.assertTrue(apply_event_policy(classify([], 'production'), 'workflow_dispatch')['selected']['production'])

    def test_automatic_and_general_manual_scopes_never_install_or_expect_browser(self):
        for paths in ([], ['docs/note.md'], ['content/registry.json'],
                      ['tools/puzzle_production/sd2_rating.py'], ['game/ui/main.gd'],
                      ['tools/ci_scope.py'], ['unknown.py'], ['README.md', 'game/ui/board.gd']):
            for scope in ('auto', 'all', 'toolchain', 'runtime', 'visual', 'perf-b', 'production'):
                for event in ('pull_request', 'push', 'workflow_dispatch'):
                    plan = apply_event_policy(classify(paths, scope), event)
                    self.assertFalse(plan['selected']['web'])
                    self.assertIsNone(plan['browser_request'])
                    self.assertEqual(plan['browser_groups'], [])
                    self.assertEqual(plan['browser_expected'], {})

    def test_real_underworkflow_guards_refuse_missing_forged_and_automatic_requests(self):
        git = shutil.which('git')
        bash = str(Path(git).resolve().parents[1]/'bin/bash.exe') if os.name == 'nt' and git else shutil.which('bash')
        if not bash or not Path(bash).is_file():
            self.skipTest('No local Bash; Linux CI exercises the same literal guards')
        for filename in ('web-chromium.yml', 'browser-chromium.yml'):
            workflow = (ROOT/'.github/workflows'/filename).read_text()
            # All guards execute before checkout, cache restoration or installs.
            prefix = workflow.split('      - name: Bind')[0]
            guards = run_blocks(prefix)
            self.assertIn('ORIGINAL_SCOPE: ${{ github.event.inputs.browser_scope }}', prefix)
            for scope in (*GROUPS, 'all'):
                env = {**os.environ, 'BROWSER': 'chromium', 'EVENT':'workflow_dispatch',
                       'ORIGINAL_SCOPE':scope, 'BROWSER_SCOPE':scope,
                       'BROWSER_REQUEST':request_output(browser_request(scope))}
                mutations = ({}, {'EVENT':'pull_request'}, {'EVENT':'push'},
                             {'ORIGINAL_SCOPE':'none'}, {'BROWSER_SCOPE':'none'},
                             {'BROWSER_REQUEST':'null'}, {'BROWSER_REQUEST':''},
                             {'BROWSER_REQUEST':'{"browser":"chromium","scope":"bogus"}'})
                for changes in mutations:
                    result = subprocess.run([bash, '--noprofile', '--norc', '-eo', 'pipefail', '-c',
                                             '\n'.join(guards)+'\nprintf "SETUP_REACHED"'],
                                            env={**env, **changes}, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1 if changes else 0, result.stderr)
                    self.assertEqual('SETUP_REACHED' in result.stdout, not changes)

    def test_scheduler_propagates_request_and_separates_concurrency(self):
        source = (ROOT/'.github/workflows/ci-chromium.yml').read_text()
        self.assertNotIn('411', source)
        self.assertIn('default: auto', source)
        self.assertIn('default: none', source)
        self.assertIn('ci-${{ github.event_name }}-${{ github.ref }}-', source)
        self.assertIn('browser_request: ${{ needs.docs.outputs.browser_request }}', source)
        download = source.split('      - name: Download chromium evidence', 1)[1].split('        uses:', 1)[0]
        self.assertIn("github.event_name == 'workflow_dispatch' && inputs.browser_scope != 'none'", download)
        for filename in ('web-chromium.yml', 'browser-chromium.yml'):
            source = (ROOT/'.github/workflows'/filename).read_text()
            self.assertIn('run_groups.py check', source)
            self.assertLess(source.index('run_groups.py check'),
                            source.index('python3 -m venv'))

    def test_real_gate_minimal_evidence_and_original_event_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan = plan_for(['tools/web_tests/browser.py'], browser_scope='regular')
            fixture(plan, 'chromium', root/'evidence/chromium')
            write(root/'event.json', {'inputs': {'scope':'auto', 'browser_scope':'regular'}})
            def finish(candidate, results=None, outputs=None):
                write(root/'plan.json', candidate)
                scheduler = {**{k:str(candidate['selected'][k]).lower() for k in FLAGS},
                             'native_groups':'[]', 'selection_attempt':'1',
                             'production_groups':'[]',
                             'browser_request':request_output(candidate['browser_request'])}
                binding = {k:candidate[k] for k in ('source_head','base_commit','tested_checkout','event','run_id','run_attempt')}
                env = {**os.environ, 'GITHUB_ACTIONS':'true', 'GITHUB_EVENT_NAME':'workflow_dispatch',
                       'GITHUB_EVENT_PATH':str(root/'event.json'), 'GITHUB_RUN_ATTEMPT':'2', 'GITHUB_STEP_SUMMARY':'',
                       'CI_BINDING':json.dumps({**binding, 'gate_attempt':'2'}),
                       'CI_OUTPUTS':json.dumps(scheduler), 'CI_WEB_OUTPUTS':json.dumps(outputs or {'chromium_attempt':'1'}),
                       'CI_RESULTS':json.dumps(results or {j:{'result':'success' if candidate['selected'][j] else 'skipped'} for j in JOBS})}
                return subprocess.run([sys.executable, str(ROOT/'tools/ci_scope.py'), 'finish',
                                       '--plan-file', str(root/'plan.json'), '--web-evidence', str(root/'evidence'),
                                       '--output', str(root/'result.json')], env=env, capture_output=True, text=True)
            passed = finish(plan)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            for status in ('failure', 'cancelled', 'skipped', '', 'missing'):
                jobs = {j:{'result':'success' if plan['selected'][j] else 'skipped'} for j in JOBS}
                jobs['web']['result'] = status
                self.assertNotEqual(finish(plan, jobs).returncode, 0)
            self.assertNotEqual(finish(plan, outputs={'chromium_attempt':'2'}).returncode, 0)
            forged = plan_for(['tools/web_tests/browser.py'], browser_scope='input')
            self.assertNotEqual(finish(forged).returncode, 0)  # even with self-consistent scheduler
            self.assertNotEqual(finish(plan_for(['tools/web_tests/browser.py'], browser_scope='none')).returncode, 0)
            (root/'evidence/chromium/web-result.json').unlink()
            self.assertNotEqual(finish(plan).returncode, 0)
            write(root/'event.json', {})
            unrequested = plan_for(['docs/note.md'], browser_scope='none')
            self.assertEqual(finish(unrequested).returncode, 0)
            self.assertEqual(json.loads((root/'result.json').read_text())['browser_status'], 'not requested')
            jobs = {j:{'result':'success' if unrequested['selected'][j] else 'skipped'} for j in JOBS}
            jobs['web']['result'] = 'success'
            self.assertNotEqual(finish(unrequested, jobs).returncode, 0)


if __name__ == '__main__':
    unittest.main()
