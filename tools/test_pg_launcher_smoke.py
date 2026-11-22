"""Small source regressions for the separate PG native release gate."""
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from tools.game_app import launcher_smoke as smoke


class LauncherSmokeTests(unittest.TestCase):
    version = '0.1.25'
    text = 'Picross Automatische Update-Suche Nicht verfügbar Version O. l.2S Suche aktivieren Spielen'

    def test_ocr_glyphs_match_only_the_expected_complete_version(self):
        for rendered in ('0.1.25', 'O. l.2S', 'O . I . ZS'):
            with self.subTest(rendered=rendered):
                self.assertTrue(smoke.launcher_controls(self.text.replace('O. l.2S', rendered), self.version))
        self.assertTrue(smoke.launcher_controls(self.text.replace('O. l.2S', 'O. l.2SB'), '0.1.258'))
        for rendered in ('0.1.24', '0.1.26', '0.1.250', '0.1.25.0', '0.1.25 . 0', '0.1.25x', '0.1.25-rc1'):
            with self.subTest(rendered=rendered):
                self.assertFalse(smoke.launcher_controls(self.text.replace('O. l.2S', rendered), self.version))
        for label in ('Automatische Update-Suche', 'Nicht verfügbar', 'Suche aktivieren', 'Spielen', 'Version'):
            with self.subTest(label=label):
                self.assertFalse(smoke.launcher_controls(self.text.replace(label, ''), self.version))
        self.assertFalse(smoke.launcher_controls(self.text.replace('Spielen', 'Spie1en'), self.version))

    def test_timeout_reports_when_no_window_was_seen(self):
        log = Mock()
        with (patch.object(smoke.time, 'monotonic', side_effect=[0, 0, 46]),
              patch.object(smoke.time, 'sleep'),
              patch.object(smoke, 'windows', return_value=[]) as windows,
              patch.object(smoke, 'read_window') as read,
              self.assertRaises(TimeoutError)):
            smoke.observe(123, lambda: None, lambda: 1, self.version, Path('unused.png'), log)
        windows.assert_called_once_with(123)
        read.assert_not_called()
        log.assert_called_once_with('No visible titled window observed for PID=123.')

    def test_only_the_responsive_tk_window_with_launcher_controls_is_accepted(self):
        with (patch.object(smoke, 'windows', return_value=[
                  (10, 'Picross', '#32770'), (20, 'Picross', 'TkTopLevel'),
                  (30, 'Picross', 'TkTopLevel'), (40, 'Picross', 'TkTopLevel')]),
              patch.object(smoke, 'responsive', side_effect=[False, True, True]) as responsive,
              patch.object(smoke, 'read_window', side_effect=['Picross Version 0.1.25', self.text]) as read):
            handle, _ = smoke.observe(123, lambda: None, lambda: 1, self.version, Path('unused.png'), Mock())
        self.assertEqual(handle, 40)
        self.assertEqual([call.args[0] for call in responsive.call_args_list], [20, 30, 40])
        self.assertEqual([call.args[0] for call in read.call_args_list], [30, 40])

    def test_early_process_exit_and_spawned_child_fail(self):
        for code in (0, 23):
            with self.subTest(code=code), self.assertRaisesRegex(smoke.EarlyExit, f'exit {code}'):
                smoke.observe(123, lambda: code, lambda: 1, self.version, Path('unused.png'), Mock())
        with self.assertRaisesRegex(RuntimeError, 'spawned'):
            smoke.observe(123, lambda: None, lambda: 2, self.version, Path('unused.png'), Mock())

    def test_result_must_bind_inspection_head_and_launcher_observation(self):
        commit = 'a' * 40
        common = {'commit': commit, 'version': self.version,
                  'msi_sha256': 'b' * 64, 'payload_fingerprint': 'c' * 64}
        delivery = {**common, 'exe_sha256': 'd' * 64}
        inspection = {**common, 'compared_to_build': True, 'inventory_files': 3}
        result = {**common, 'format': smoke.FORMAT, 'launcher_sha256': delivery['exe_sha256'],
                  'window_class': 'TkTopLevel', 'window_text': self.text, 'exit_code': 0, 'processes': 1,
                  'inventory_files': 4}
        smoke.verify_result(result, delivery, inspection, commit)
        for changes in ({'commit': 'e' * 40}, {'msi_sha256': 'e' * 64}, {'exit_code': 1},
                        {'window_text': 'Picross version 0.1.25'}, {'processes': 2}):
            with self.subTest(changes=changes), self.assertRaises(RuntimeError):
                smoke.verify_result({**result, **changes}, delivery, inspection, commit)

    def test_missing_result_fails_before_candidate_seal(self):
        with patch('sys.argv', ['launcher_smoke', '--build', '.', '--inspection', 'unused.json',
                               '--output', 'absent-pg-smoke', '--expected-commit', 'a' * 40, '--verify-result']):
            with self.assertRaises(FileNotFoundError):
                smoke.main()
