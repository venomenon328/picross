"""Current Windows verification stays independent of the historical R1 failure."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import rp4_windows_check as check


class WindowsCheckContractTests(unittest.TestCase):
    def run_check(self, phase='current', *, count=14, fail=False, runtime_changes=None,
                  wheel_host='files.pythonhosted.org', test_checkout=None):
        # Exercise the CLI's decision/report path without claiming a Windows run.
        with tempfile.TemporaryDirectory(prefix='rp4-check-contract-') as temporary:
            folder = Path(temporary)
            root, output, prefix = folder / 'repo', folder / 'output', folder / 'venv'
            root.mkdir()
            output.mkdir()
            prefix.mkdir()
            (prefix / 'pyvenv.cfg').write_text('include-system-site-packages = false\n')
            wheel = f'https://{wheel_host}/packages/pillow-12.3.0-cp312-cp312-win_amd64.whl'
            (output / 'pillow-install.json').write_text(json.dumps({'install': [
                {'download_info': {'url': wheel, 'archive_info': {'hashes': {'sha256': 'c' * 64}}}}
            ]}))
            data = {'python': '3.12.10', 'system': 'Windows', 'bits': 64, 'machine': 'AMD64',
                    'pillow': '12.3.0', 'pillow_zlib': 'different-current-codec',
                    'isolated': 1, 'user_site_enabled': False,
                    'pillow_file': str(prefix / 'Lib/site-packages/PIL/Image.py')}
            data.update(runtime_changes or {})
            head = 'a' * 40
            environment = {'RUNNER_TEMP': str(folder), 'RP4_SOURCE_HEAD': head,
                           'RP4_BASE_COMMIT': 'b' * 40, 'GITHUB_SHA': head,
                           'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_JOB': 'rp4-windows',
                           'GITHUB_SERVER_URL': 'https://github.com', 'GITHUB_REPOSITORY': 'example/picross'}

            def fake_git(path, *args):
                if args[0] == 'status':
                    return ''
                if Path(path) == root:
                    return test_checkout or (check.R1_HEAD if phase == 'baseline' else head)
                return head

            def sample_test():
                if fail:
                    raise AssertionError('Current RP-4 regression')

            loader = Mock(errors=[])
            loader.discover.return_value = unittest.TestSuite(
                unittest.FunctionTestCase(sample_test) for _ in range(count))
            arguments = ['rp4_windows_check.py', '--phase', phase, '--repo', str(root),
                         '--output-dir', str(output)]
            with patch.dict(os.environ, environment), patch.object(check.sys, 'argv', arguments), \
                    patch.object(check.sys, 'path', list(check.sys.path)), \
                    patch.object(check.sys, 'prefix', str(prefix)), \
                    patch.object(check.sys, 'base_prefix', str(folder / 'base-python')), \
                    patch.object(check, 'git', side_effect=fake_git), \
                    patch.object(check, 'runtime', return_value=data), \
                    patch.object(check.unittest, 'TestLoader', return_value=loader), \
                    redirect_stdout(io.StringIO()):
                status = check.main()
            if phase == 'current':
                self.assertFalse((output / 'baseline.json').exists())
            return status, json.loads((output / f'{phase}.json').read_text())

    def test_current_accepts_passing_suite_without_baseline_or_old_codec(self):
        status, report = self.run_check()
        self.assertEqual(status, 0)
        self.assertTrue(report['phase_passed'] and report['accepted'])
        self.assertEqual(report['format'], 'picross-rp4-windows-v2')
        self.assertEqual(report['verification'], 'current-regression')
        self.assertNotIn('r1_head', report)
        self.assertNotIn('baseline_reproduced', report)

    def test_failed_or_incomplete_current_suite_is_rejected(self):
        for options in ({'fail': True}, {'count': 13}):
            with self.subTest(options=options):
                status, report = self.run_check(**options)
                self.assertEqual(status, 1)
                self.assertFalse(report['accepted'] or report['phase_passed'])
                self.assertIn('Current RP-4 regressions failed or missing', report['error'])

    def test_current_keeps_wheel_runtime_and_commit_requirements(self):
        for options in ({'wheel_host': 'untrusted.example'},
                        {'runtime_changes': {'pillow': '12.2.0'}},
                        {'runtime_changes': {'system': 'Linux'}},
                        {'runtime_changes': {'isolated': 0}},
                        {'test_checkout': 'd' * 40}):
            with self.subTest(options=options):
                status, report = self.run_check(**options)
                self.assertEqual(status, 1)
                self.assertFalse(report['accepted'] or report['phase_passed'])

    def test_historical_diagnosis_still_requires_r1_codec(self):
        status, report = self.run_check('baseline')
        self.assertEqual(status, 1)
        self.assertEqual(report['verification'], 'historical-r1-reproduction')
        self.assertEqual(report['r1_head'], check.R1_HEAD)
        self.assertIn('Actual zlib differs from R1', report['error'])


if __name__ == '__main__':
    unittest.main()
