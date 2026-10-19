"""No browser processes: reject unsupported CI inputs before any side effects."""
import ast
import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from test_ci_a import run_blocks
from web_tests.run_groups import run

ROOT = Path(__file__).resolve().parents[1]
REJECTED = ('firefox', 'webkit', 'both', '', 'Chromium', 'chromium firefox')


class ChromiumBoundary(unittest.TestCase):
    def test_all_cli_inputs_rejected_before_playwright_import_or_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # If a CLI imports Playwright before rejecting the input, the trap
            # fails the test. This cannot invoke a real browser or driver.
            trap = root/'playwright'
            trap.mkdir()
            (trap/'__init__.py').write_text("raise RuntimeError('PLAYWRIGHT_IMPORT_FORBIDDEN')\n")
            env = {**os.environ, 'PYTHONPATH': str(root)}
            common = ['--build', str(root/'absent'), '--output', str(root/'out')]
            commands = {
                'browser.py': [*common, '--update-build', str(root/'absent-update')],
                'smoke.py': common,
                'run_groups.py': ['run', '--plan', str(root/'absent-plan'),
                                  '--build-root', str(root/'absent'),
                                  '--output', str(root/'out'), '--build-attempt', '1'],
            }
            for script, arguments in commands.items():
                for browser in REJECTED:
                    with self.subTest(script=script, browser=browser):
                        result = subprocess.run([sys.executable, str(ROOT/'tools/web_tests'/script),
                                                 *arguments, '--browser', browser],
                                                env=env, capture_output=True, text=True)
                        self.assertEqual(result.returncode, 2, result.stderr)
                        self.assertIn('invalid choice', result.stderr)
                        self.assertNotIn('PLAYWRIGHT_IMPORT_FORBIDDEN', result.stderr)
                        self.assertFalse((root/'out').exists())

    def test_direct_runner_and_all_launches_reject_unsupported_values(self):
        with patch.object(sys, 'path', [str(ROOT/'tools/web_tests'), *sys.path]):
            runtime = importlib.import_module('browser_runtime')
            browser_module = importlib.import_module('browser')
        for browser in REJECTED:
            with self.subTest(browser=browser):
                with patch('web_tests.run_groups.subprocess.run') as process:
                    with self.assertRaisesRegex(ValueError, 'Unsupported CI browser'):
                        run(SimpleNamespace(browser=browser), {})
                    process.assert_not_called()
                pw = Mock()
                with self.assertRaises(ValueError):
                    runtime.options(browser)
                with self.assertRaises(ValueError):
                    runtime.launch(pw, browser, 'unused-profile')
                with self.assertRaises(ValueError):
                    browser_module.Session(pw, browser, 'unused-profile', {}).launch()
                self.assertEqual(pw.mock_calls, [])
        pw = Mock()
        runtime.launch(pw, 'chromium', 'synthetic-profile', device_scale_factor=1.25)
        pw.chromium.launch_persistent_context.assert_called_once_with(
            'synthetic-profile', headless=True, device_scale_factor=1.25)

    def test_workflows_have_no_firefox_and_validate_before_installation(self):
        for path in (ROOT/'.github/workflows').glob('*.yml'):
            self.assertNotIn('firefox', path.read_text().lower(), path)
        workflow = (ROOT/'.github/workflows/web-browser.yml').read_text()
        blocks = run_blocks(workflow)
        self.assertIn('if [ "$BROWSER" != chromium ]; then', blocks[0])
        self.assertIn('exit 1', blocks[0])
        self.assertIn('BROWSER: ${{ inputs.browser }}', workflow.split('      - name: Bind')[0])
        installs = [block for block in blocks if 'playwright" install' in block]
        self.assertEqual(len(installs), 1)
        self.assertIn('playwright" install --with-deps chromium', installs[0])
        self.assertNotIn('install --with-deps "$BROWSER"', workflow)
        web = (ROOT/'.github/workflows/web.yml').read_text()
        self.assertEqual(web.count('uses: ./.github/workflows/web-browser.yml'), 1)
        self.assertIn('browser: chromium', web)

    def test_actual_first_workflow_step_rejects_before_next_step(self):
        bash = shutil.which('bash')
        if os.name == 'nt':
            # Prefer Git's local Bash; Windows' bash.exe may only be a WSL stub.
            git = shutil.which('git')
            bash = str(Path(git).resolve().parents[1]/'bin/bash.exe') if git else None
        if not bash or not Path(bash).is_file():
            self.skipTest('No local Bash; full workflow shell probe runs on Linux')
        guard = run_blocks((ROOT/'.github/workflows/web-browser.yml').read_text())[0]
        for browser in ('chromium', *REJECTED):
            with self.subTest(browser=browser):
                result = subprocess.run([bash, '--noprofile', '--norc', '-eo', 'pipefail', '-c',
                                         guard + '\nprintf "INSTALLATION_REACHED\\n"'],
                                        env={**os.environ, 'BROWSER': browser},
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0 if browser == 'chromium' else 1, result.stderr)
                self.assertEqual('INSTALLATION_REACHED' in result.stdout, browser == 'chromium')

    def test_browser_launch_sites_use_only_guarded_chromium(self):
        launches = []
        for path in (ROOT/'tools/web_tests').glob('*.py'):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr in ('launch', 'launch_persistent_context')
                        and not (isinstance(node.func.value, ast.Name) and node.func.value.id == 'session')):
                    launches.append((path.name, ast.unparse(node.func)))
        self.assertEqual(launches, [('browser_runtime.py', 'pw.chromium.launch_persistent_context')])


if __name__ == '__main__':
    unittest.main()
