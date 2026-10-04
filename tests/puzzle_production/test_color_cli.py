import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.puzzle_production.contract import load_json, write_json

FIXTURES = Path(__file__).parent / "fixtures"


class ColorCliTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.puzzle_production", *map(str, args)],
                              capture_output=True, text=True, timeout=30)

    def test_saved_color_solve_fresh_verify_profile_and_attacks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("color-propagation", "color-four"):
                logic = FIXTURES / (name + ".json")
                out = root / name
                proc = self.invoke("solve", "--input", logic, "--output-dir", out)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                result = load_json(out / "result.json")
                self.assertTrue(result["certified"])
                self.assertEqual(result["profile"]["id"], "full-line-color")
                proc = self.invoke("verify", "--input", logic, "--proof", out / "proof.json")
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(json.loads(proc.stdout)["profile_hash"], result["profile_hash"])
                proof = load_json(out / "proof.json")
                proof["steps"][0]["changes"][0]["after"] = ["yellow"]
                write_json(out / "proof.json", proof)
                self.assertEqual(self.invoke("verify", "--input", logic, "--proof",
                                             out / "proof.json").returncode, 3)
                proc = self.invoke("solve", "--input", logic, "--output-dir", root / (name + "-abort"),
                                   "--max-lines", 1)
                self.assertEqual(proc.returncode, 4)
                self.assertFalse(json.loads(proc.stdout)["certified"])
                self.assertEqual(json.loads(proc.stdout)["profile"]["id"], "full-line-color")

    def test_color_proof_file_cap_exceeds_old_mono_cap(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            logic = FIXTURES / "color-four.json"
            out = root / "color"
            self.assertEqual(self.invoke("solve", "--input", logic, "--output-dir", out).returncode, 0)
            path = out / "proof.json"
            original = path.read_bytes()
            # JSON whitespace does not change the canonical proof, but the file
            # exceeds 8 MiB. Exercise the actual CLI loader, not just constants.
            path.write_bytes(original + b" " * (8 * 1024 * 1024))
            self.assertEqual(self.invoke("verify", "--input", logic, "--proof", path).returncode, 0)
            mono = FIXTURES / "deductive.json"
            self.assertEqual(self.invoke("verify", "--input", mono, "--proof", path).returncode, 3)
            path.write_bytes(original.replace(b'"version":1', b'"version":1e999999'))
            proc = self.invoke("verify", "--input", logic, "--proof", path)
            self.assertEqual(proc.returncode, 3)
            self.assertEqual(json.loads(proc.stdout)["status"], "invalid_proof")
