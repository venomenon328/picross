"""Cheap actual-JS bridge checks; no browser/IndexedDB or npm installation."""
from pathlib import Path
import shutil
import subprocess
import unittest


class StorageContractTests(unittest.TestCase):
    def test_actual_storage_bridge(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'tools module requires Node for storage_contract.cjs; never silently skip')
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([node, str(root/'tools/web_tests/storage_contract.cjs'),
                                 str(root/'game/web/storage.js')], capture_output=True,
                                text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS recent callback ownership, isolation and retry', result.stdout)
