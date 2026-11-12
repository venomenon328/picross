"""P4-T01: inexpensive source/metadata guards, never build or install an MSI."""
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import os
import threading
import uuid
from unittest.mock import patch
import xml.etree.ElementTree as ET

from tools.production_workspace import build_installer as installer
from tools.production_workspace.release import release, version_tuple, check_history

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': installer.NS}


class InstallerContractTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'Actual Windows kernel mutex regression')
    def test_idle_versus_held_kernel_mutex_without_touching_real_msi(self):
        import ctypes
        from ctypes import wintypes as w
        from tools.production_workspace.install_interlock import _mutex_busy
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateMutexW.argtypes = [ctypes.c_void_p, w.BOOL, w.LPCWSTR]
        kernel.CreateMutexW.restype = w.HANDLE
        kernel.CloseHandle.argtypes = [w.HANDLE]
        kernel.ReleaseMutex.argtypes = [w.HANDLE]
        name = 'Local\\Picross.P4.Test.' + uuid.uuid4().hex
        self.assertFalse(_mutex_busy(name))
        idle = kernel.CreateMutexW(None, False, name)
        try:
            self.assertTrue(idle)
            self.assertFalse(_mutex_busy(name))
        finally:
            kernel.CloseHandle(idle)
        entered, release = threading.Event(), threading.Event()
        def owner():
            handle = kernel.CreateMutexW(None, True, name)
            try:
                entered.set(); release.wait(10)
            finally:
                kernel.ReleaseMutex(handle); kernel.CloseHandle(handle)
        thread = threading.Thread(target=owner); thread.start()
        try:
            self.assertTrue(entered.wait(5))
            self.assertTrue(_mutex_busy(name))
        finally:
            release.set(); thread.join(5)
        self.assertFalse(_mutex_busy(name))

    def test_source_history_refuses_decrease_or_upgrade_identity_change(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'release.json'
            product = release()
            source.write_text(json.dumps(product))
            for args in (('init', '-q'), ('add', '.'), ('-c', 'user.name=P4 test', '-c', 'user.email=p4@example.invalid', 'commit', '-qm', 'synthetic')):
                subprocess.run(['git', '-C', str(root), *args], check=True, stdout=subprocess.DEVNULL)
            with patch('tools.production_workspace.release.SOURCE', source):
                check_history(root, product)
                with self.assertRaisesRegex(ValueError, 'monoton'):
                    check_history(root, {**product, 'version': '0.0.1'})
                with self.assertRaisesRegex(ValueError, 'Upgradeidentität'):
                    check_history(root, {**product, 'upgrade_code': '11111111-1111-1111-1111-111111111111'})

    def test_strict_msi_versions_and_identity(self):
        for invalid in ('01.2.3', '1.0', '1.2.3.4', '1.2.3-rc1', '256.0.0', '1.256.0', '1.0.65536', '0.0.0', '1.2.3\n'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                version_tuple(invalid)
        product = release()
        self.assertIn(product['version'], product['filename'])
        self.assertEqual(product['product_code'], release()['product_code'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'release.json'
            other = {**product, 'version': '255.255.65535'}
            path.write_text(json.dumps(other))
            updated = release(path)
            self.assertEqual(updated['upgrade_code'], product['upgrade_code'])
            self.assertNotEqual(updated['product_code'], product['product_code'])
            self.assertGreater(version_tuple(updated['version']), version_tuple(product['version']))

    def test_generated_installer_is_per_user_preserves_state_and_refuses_running_or_same_version(self):
        with tempfile.TemporaryDirectory() as folder:
            app = Path(folder); (app / 'Picross-Start.exe').write_bytes(b'synthetic')
            (app / 'LICENSES').mkdir(); (app / 'LICENSES/Python.txt').write_text('synthetic')
            root = installer.wix_source(app, release(), app / 'guard.dll').getroot()
            package = root.find('.//w:Package', NS)
            self.assertEqual(package.get('InstallScope'), 'perUser')
            self.assertEqual(package.get('InstallPrivileges'), 'limited')
            self.assertEqual(root.find('.//w:MajorUpgrade', NS).get('Schedule'), 'afterInstallInitialize')
            self.assertIn('NOT SAMEVERSION', root.find('.//w:Product/w:Condition', NS).text)
            self.assertEqual(root.find('.//w:UpgradeVersion', NS).get('IncludeMaximum'), 'yes')
            check = root.find('.//w:InstallExecuteSequence/w:Custom', NS)
            self.assertEqual(check.get('Before'), 'InstallValidate')
            self.assertEqual(check.text, '1')  # Includes fresh install, upgrade AND uninstall.
            self.assertIsNone(root.find('.//w:RemoveFile', NS))
            self.assertEqual(len(root.findall('.//w:File', NS)), 2)
            self.assertTrue(all(e.get('Root') == 'HKCU' for e in root.findall('.//w:RegistryValue', NS)))
            text = ET.tostring(root).decode()
            self.assertNotIn('PicrossProductionWorkspace/.launcher', text)
            guard = (ROOT / 'tools/production_workspace/packaging/Guard.cs').read_text()
            self.assertIn('RmGetList', guard)
            self.assertIn('FileShare.None', guard)
            self.assertNotIn('RmShutdown(', guard)

    def test_dispatch_is_only_trigger_and_no_core_coupling(self):
        workflow = (ROOT / '.github/workflows/pw-installer.yml').read_text()
        triggers = workflow.split('\non:\n', 1)[1].split('\npermissions:', 1)[0]
        self.assertIn('workflow_dispatch:', triggers)
        self.assertNotIn('inputs:', triggers)
        self.assertIn('ref: main', workflow)
        self.assertIn('git checkout --detach $source', workflow)
        self.assertIn('steps.source.outputs.source_commit', workflow)
        for forbidden in ('pull_request:', 'push:', 'schedule:', 'workflow_run:', 'workflow_call:'):
            self.assertNotIn(forbidden, triggers)
        for path in (ROOT / '.github/workflows/ci-modular.yml', ROOT / 'tools/ci_modular.py'):
            self.assertNotIn('build_installer', path.read_text())
            self.assertNotIn('smoke_installer', path.read_text())


if __name__ == '__main__':
    unittest.main()
