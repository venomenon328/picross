"""Small PG packaging regressions. Real MSI/process probes run separately on Windows."""
from pathlib import Path
from types import SimpleNamespace
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools.app_products import PE, PG, PW
from tools.game_app.gate import StartupGate
from tools.game_app.inputs import selected
from tools.game_app.inspect import verify_database
from tools.production_workspace import payload
from tools.production_workspace.app_updates import Updates
from tools.production_workspace.release import release
from tools.production_workspace.release_channel import next_version
from tools.production_workspace.update_storage import Preferences, atomic_json, recover


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
        product = release(version='0.1.1', app=PG)
        key = PG.registry + '\\Installer'
        tables = {'Shortcut': good, 'Registry': [
            ['1', key, 'EmptyFolders', '#1', 'EmptyFolders'],
            ['1', key, 'DesktopShortcut', '#1', 'DesktopShortcut'],
            ['1', key, 'MenuShortcut', '#1', 'MenuShortcut'],
            ['1', key, 'Version', product['version'], 'ProductRegistration'],
            ['1', key, 'ProductCode', '{' + product['product_code'] + '}', 'ProductRegistration'],
        ]}
        with patch('tools.game_app.inspect.msi_rows', side_effect=lambda _, name, columns: tables[name]):
            verify_database(Path('fake.msi'), product)
            good.append(['UpdateSettingsLink', 'AppMenu', '[INSTALLFOLDER]Picross-Game.exe', '--update-settings'])
            with self.assertRaisesRegex(RuntimeError, 'shortcut target'):
                verify_database(Path('fake.msi'), product)
            good.pop()
            good[1][2] = 'picross-p1.exe'
            with self.assertRaisesRegex(RuntimeError, 'shortcut target'):
                verify_database(Path('fake.msi'), product)
            good[1][2] = '[INSTALLFOLDER]Picross-Game.exe'
            tables['Registry'].pop()
            with self.assertRaisesRegex(RuntimeError, 'registration'):
                verify_database(Path('fake.msi'), product)


    def test_frozen_runtime_and_helper_inputs_are_bound(self):
        for relative in ('game_app/gate.py', 'game_app/restart.py', 'production_workspace/update_client.py',
                         'production_workspace/packaging/UpdateHelper.cs', 'production_workspace/requirements-windows.txt'):
            self.assertTrue(selected('tools/' + relative), relative)
        self.assertFalse(selected('tools/game_app/diagnose.py'))
        self.assertFalse(selected('tools/production_workspace/helper_diagnostic.py'))
        self.assertFalse(selected('tools/puzzle_editor/desktop.py'))

    def test_pending_is_unconfirmed_and_requires_end_before_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='pg-pending-') as folder:
            launcher = Path(folder)
            nonce = '0' * 48
            stage = launcher / 'update-staging' / nonce
            stage.mkdir(parents=True)
            msi = release(version='0.1.1', app=PG)['filename']
            pending = {'format': 'picross-update-pending-v1', 'nonce': nonce, 'stage': nonce,
                       'version': '0.1.1', 'files': [msi, msi + '.sha256', 'START.txt', 'delivery.json',
                            'inputs.json', 'manifest.json', 'manifest.sig.json', 'UpdateHelper.exe', 'active']}
            atomic_json(launcher / 'update-pending.json', pending)
            (stage / 'active').write_bytes(b'')
            foreign = stage / 'foreign'
            foreign.write_bytes(b'external')
            self.assertIn('unbestätigt', recover(launcher, app=PG))
            self.assertEqual(foreign.read_bytes(), b'external')
            atomic_json(launcher / 'update-result.json', {'format': 'picross-update-result-v1',
                        'nonce': nonce, 'status': 'cancelled', 'version': '0.1.1'})
            with self.assertRaisesRegex(ValueError, 'Foreign PG'):
                recover(launcher, app=PG)
            self.assertTrue((stage / 'active').exists())
            foreign.unlink()
            self.assertIn('abgebrochen', recover(launcher, app=PG))
            self.assertFalse(stage.exists())
            self.assertIsNone(recover(launcher, app=PG))

    def test_consent_changes_stay_local_until_one_play_request(self):
        with tempfile.TemporaryDirectory(prefix='pg-consent-') as folder:
            state = Path(folder) / 'state'
            owner = SimpleNamespace(lock=SimpleNamespace(state=state, directory=state / '.updates'),
                                    stop_requested=Mock())
            owner.stop_requested.is_set.return_value = False
            identity = SimpleNamespace(executable=Path(folder) / 'app/launcher.exe')
            with patch('tools.production_workspace.app_updates.windows.installation', return_value=identity), \
                    patch('tools.production_workspace.app_updates.production_trust', return_value={'accepted': True}), \
                    patch('tools.game_app.gate.StateLock'), patch('tools.game_app.gate.LauncherWindow'):
                updates = Updates(owner, app=PG)
                gate = StartupGate(state, owner, updates, PG.anchor)
                with patch.object(updates, '_run') as worker:
                    gate.toggle()
                    self.assertTrue(updates.preferences.read())
                    gate.toggle()
                    self.assertFalse(updates.preferences.read())
                    gate.toggle()
                    self.assertTrue(updates.preferences.read())
                    worker.assert_not_called()
                    gate.play()
                    gate.play()
                    updates.thread.join(2)
                    worker.assert_called_once()
                    gate.toggle()
                    self.assertFalse(updates.preferences.read())
                    self.assertTrue(updates.cancelled.is_set())
                    gate.stop('close')
                    self.assertEqual(gate.result, 'close')

    def test_first_play_is_offline_even_if_storing_decline_fails(self):
        for fail in (False, True):
            with self.subTest(fail=fail), tempfile.TemporaryDirectory(prefix='pg-first-play-') as folder:
                state = Path(folder) / 'state'
                preferences = Preferences(state / '.updates')
                updates = Mock(enabled=None, started=False, preferences=preferences)

                def save(value):
                    if fail:
                        return False
                    preferences.write(value)
                    updates.enabled = value
                    return True

                updates.save_preference.side_effect = save
                with patch('tools.game_app.gate.StateLock'), patch('tools.game_app.gate.LauncherWindow'):
                    gate = StartupGate(state, SimpleNamespace(stop_requested=Mock()), updates, PG.anchor)
                    gate.play()
                    gate.play()
                    updates.save_preference.assert_called_once_with(False)
                    updates.start.assert_not_called()
                    self.assertEqual(gate.result, 'play')
                    self.assertIs(preferences.read(), None if fail else False)
                    if fail:
                        self.assertIn('nicht gespeichert', gate.view.show.call_args.args[0])

    def test_start_gate_ignores_a_late_skip_after_ready_take(self):
        # Drive the GUI-owned transition with a READY worker, without requiring a Tk display.
        update = Mock()
        update.take.return_value.nonce = '0' * 48
        update.preferences.read.return_value = True
        with patch('tools.game_app.gate.StateLock') as lock, patch('tools.game_app.gate.LauncherWindow'), \
                patch('tools.game_app.gate.atomic_json') as save:
            lock.return_value.directory = Path('pg-install')
            gate = StartupGate(Path('pg-state'), SimpleNamespace(stop_requested=Mock()), update, PG.anchor)
            gate.requested = True
            self.assertTrue(gate.take())
            save.assert_called_once_with(Path('pg-install/update-accepted.json'), {'nonce': '0' * 48})
            gate.stop('play')
            update.cancel.assert_not_called()
            self.assertIsNone(gate.result)

    def test_disabled_preference_or_close_cannot_take_a_ready_worker(self):
        for action in ('preference', 'close'):
            update = Mock()
            update.preferences.read.return_value = False
            stop = Mock()
            with patch('tools.game_app.gate.StateLock'), patch('tools.game_app.gate.LauncherWindow'):
                gate = StartupGate(Path('pg-state'), SimpleNamespace(stop_requested=stop), update, PG.anchor)
                gate.requested = True
                if action == 'close':
                    gate.stop('close')
                    stop.set.assert_called_once()
                    self.assertEqual(gate.result, 'close')
                else:
                    self.assertFalse(gate.take())
                    self.assertEqual(gate.result, 'play')
                update.cancel.assert_called_once()
                update.take.assert_not_called()


if __name__ == '__main__':
    unittest.main()
