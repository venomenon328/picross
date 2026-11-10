"""Actual Web loader mechanism in Node; no browser, image decoder or npm claim."""
from pathlib import Path
import shutil
import subprocess
import unittest


class BackgroundWebContractTests(unittest.TestCase):
    def test_background_worker_contract(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'tools module requires Node; never silently skip')
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [node, str(root / 'tools/web_tests/background_loader_contract.cjs'),
             str(root / 'game/web/background_loader.js')],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS background container, asynchronous ownership, cancellation and pixels', result.stdout)
