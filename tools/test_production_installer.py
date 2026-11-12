"""P4-T01: inexpensive source/metadata guards, never build or install an MSI."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from tools.production_workspace import build_installer as installer
from tools.production_workspace.release import release, version_tuple

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': installer.NS}


class InstallerContractTests(unittest.TestCase):
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
            self.assertEqual(check.get('Before'), 'InstallInitialize')
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
        for forbidden in ('pull_request:', 'push:', 'schedule:', 'workflow_run:', 'workflow_call:'):
            self.assertNotIn(forbidden, triggers)
        for path in (ROOT / '.github/workflows/ci-modular.yml', ROOT / 'tools/ci_modular.py'):
            self.assertNotIn('build_installer', path.read_text())
            self.assertNotIn('smoke_installer', path.read_text())


if __name__ == '__main__':
    unittest.main()
