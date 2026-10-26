"""Bounded CI2-C profiles, actual workflow build selection and negative evidence."""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_ci_a import run_blocks
from test_ci_b import envelope, fixture, plan_for
from web_tests.contract import CORE_GROUPS, GROUPS, expected, required_builds
from web_tests.results import validate_builds, validate_browser

ROOT = Path(__file__).resolve().parents[1]


class ShortBrowser(unittest.TestCase):
    def test_short_is_nine_cases_and_export_is_never_implicit(self):
        for scope in ('short', 'all'):
            plan = plan_for(browser_scope=scope)
            self.assertEqual(plan['browser_groups'], list(CORE_GROUPS))
            self.assertEqual(len(expected('chromium', plan['browser_groups'])), 9)
            self.assertEqual(required_builds(plan['browser_groups']), ('web-player', 'web-test'))
        self.assertEqual(plan_for(browser_scope='export')['browser_groups'], ['regular', 'export'])
        self.assertEqual(required_builds(['regular']), ('web-player',))

    def test_build_gate_checks_exact_need_and_real_export_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            for scope in (*GROUPS, 'short'):
                plan = plan_for(browser_scope=scope)
                good = envelope(plan, Path(tmp))
                validate_builds(good, plan, '1')
                for name in list(good['builds']):
                    bad = deepcopy(good); del bad['builds'][name]
                    with self.assertRaises(ValueError): validate_builds(bad, plan, '1')
                bad = deepcopy(good); bad['builds']['unexpected'] = next(iter(bad['builds'].values()))
                with self.assertRaises(ValueError): validate_builds(bad, plan, '1')
                if scope == 'export':
                    for key in ('build_id', 'built_at'):
                        bad = deepcopy(good)
                        bad['builds']['web-test-update']['manifest'][key] = bad['builds']['web-test']['manifest'][key]
                        with self.assertRaises(ValueError): validate_builds(bad, plan, '1')

    def test_actual_case_log_cannot_be_empty_missing_duplicate_or_wrong(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); plan = plan_for(browser_scope='input')
            report = fixture(plan, 'chromium', root)
            log = root/'input/execution.log'; original = log.read_text()
            for text in ('', original.splitlines()[0]+'\n', original+original, original.replace('C02','C99')):
                log.write_text(text)
                # Even re-sealing the changed log must not bless omitted executions.
                from web_tests.results import file_record
                report['files']['input/execution.log'] = file_record(log)
                with self.assertRaises(ValueError):
                    validate_browser(report, plan, 'chromium', '1', '1', root)

    def test_actual_workflow_builds_only_requested_exports(self):
        git = shutil.which('git')
        bash = str(Path(git).resolve().parents[1]/'bin/bash.exe') if os.name == 'nt' and git else shutil.which('bash')
        self.assertTrue(bash and Path(bash).is_file(), 'Bash is required for the workflow counterprobe')
        source = (ROOT/'.github/workflows/web-chromium.yml').read_text()
        block = next(b for b in run_blocks(source) if 'tools/build_web_player.py' in b)
        # A shell function records real branch execution without running an engine.
        stub = 'python3() { printf "%s\\n" "$*"; return "${INJECT_EXIT:-0}"; }\n'
        for scope in (*GROUPS, 'short', 'all'):
            result = subprocess.run([bash, '--noprofile', '--norc', '-eo', 'pipefail', '-c',
                                     stub+block.replace('${{ runner.temp }}', '/tmp/ci2-c')],
                                    env={**os.environ, 'BROWSER_SCOPE':scope}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            names = required_builds(plan_for(browser_scope=scope)['browser_groups'])
            self.assertEqual(len(lines), len(names))
            for line, name in zip(lines, names, strict=True):
                self.assertIn('--output-dir artifacts/'+name, line)
            if scope == 'export': self.assertIn('--test-reveal-revision 2', lines[-1])
        result = subprocess.run([bash, '--noprofile', '--norc', '-eo', 'pipefail', '-c',
                                 stub+block.replace('${{ runner.temp }}', '/tmp/ci2-c')],
                                env={**os.environ, 'BROWSER_SCOPE':'short', 'INJECT_EXIT':'23'}, capture_output=True)
        self.assertEqual(result.returncode, 23)

    def test_real_storage_bridge_below_browser(self):
        # Node is supplied by the workstation/Ubuntu runner; no npm dependency.
        result = subprocess.run(['node', str(ROOT/'tools/web_tests/storage_contract.cjs'),
                                 str(ROOT/'game/web/storage.js')], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(len([line for line in result.stdout.splitlines() if line.startswith('PASS ')]), 5)


if __name__ == '__main__':
    unittest.main()
