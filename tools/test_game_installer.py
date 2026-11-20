"""Small PG packaging regressions. Real MSI/process probes run separately on Windows."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.app_products import PE, PG, PW
from tools.game_app.inspect import verify_database
from tools.production_workspace import payload
from tools.production_workspace.release import release
from tools.production_workspace.release_channel import next_version


class GameInstallerTests(unittest.TestCase):
    def test_fixed_product_and_versions(self):
        pg = release(version='0.1.1', app=PG)
        self.assertEqual(pg['filename'], 'Picross-Spiel-0.1.1-windows-x64.msi')
        self.assertEqual(len({release(app=app)['upgrade_code'] for app in (PW, PE, PG)}), 3)
        second = release(version='0.1.2', app=PG)
        self.assertEqual(second['upgrade_code'], pg['upgrade_code'])
        self.assertNotEqual(second['product_code'], pg['product_code'])
        with self.assertRaises(ValueError):
            release(version='0.2.1', app=PG)

    def test_committed_packaging_and_runtime_changes_and_unshipped_noop(self):
        with tempfile.TemporaryDirectory(prefix='pg-inputs-') as folder:
            root = Path(folder)

            def git(*args):
                subprocess.run(['git', '-C', folder, *args], check=True, capture_output=True)

            def put(name, data):
                target = root / name
                target.parent.mkdir(exist_ok=True, parents=True)
                target.write_bytes(data)

            def commit():
                git('add', '--all')
                git('-c', 'user.email=test@example.invalid', '-c', 'user.name=Test', 'commit', '-m', 'fixture')
                return payload.fingerprint(root, app=PG)

            git('init')
            path = 'game/data/content/one.json'
            packaging = 'tools/production_workspace/build_windows.py'
            put(path, b'a')
            put(packaging, b'# original packaging')
            original = commit()
            previous = {'manifest': {'version': '0.1.1', 'payload_fingerprint': original['sha256']}}
            put('content/authoring/wip.jpg', b'work in progress')
            put('game/tests/fixture.png', b'synthetic')
            put('docs/operations/trial.md', b'unshipped')
            unchanged = commit()
            self.assertEqual(original, unchanged)
            self.assertIsNone(next_version(unchanged, previous, app=PG))
            put(packaging, b'# changed packaging')
            changed = commit()
            self.assertNotEqual(original['sha256'], changed['sha256'])
            self.assertEqual(next_version(changed, previous, app=PG), '0.1.2')
            put(path, b'b')
            put('game/art/content/one.png', b'image')
            second = commit()
            self.assertNotEqual(changed['sha256'], second['sha256'])
            self.assertEqual({row['file'] for row in second['files']},
                             {path, 'game/art/content/one.png', packaging})
            (root / path).rename(root / 'game/data/content/two.json')
            self.assertNotEqual(second['sha256'], commit()['sha256'])

    def test_inspector_refuses_wrong_shortcut_target_or_arguments(self):
        good = [
            ['DesktopShortcutLink', 'DesktopFolder', '[INSTALLFOLDER]Picross-Game.exe', ''],
            ['MenuShortcutLink', 'AppMenu', '[INSTALLFOLDER]Picross-Game.exe', ''],
        ]
        with patch('tools.game_app.inspect.msi_rows', return_value=good):
            verify_database(Path('fake.msi'))
            good[1][2] = 'picross-p1.exe'
            with self.assertRaisesRegex(RuntimeError, 'shortcut target'):
                verify_database(Path('fake.msi'))


if __name__ == '__main__':
    unittest.main()
