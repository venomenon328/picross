from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.cli import main
from tools.puzzle_production.contract import Puzzle, load_json, write_json


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="picross-rp1-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "logic.json"
        write_json(self.input, Puzzle(3, 3, ((1,), (3,), (1,)),
                                     ((1,), (3,), (1,))).to_wire())

    def invoke(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.puzzle_production", *args],
                              capture_output=True, text=True, timeout=30)

    def test_solve_and_fresh_verification(self):
        out = self.root / "solved"
        proc = self.invoke("solve", "--input", str(self.input), "--output-dir", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        proc = self.invoke("verify", "--input", str(self.input), "--proof",
                           str(out / "proof.json"), "--report", str(self.input))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("row_clues", load_json(self.input))
        result = load_json(out / "result.json")
        self.assertTrue(result["certified"])
        proc = self.invoke("verify", "--input", str(self.input), "--proof", str(out / "proof.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        # Existing certificate output must be refused, not silently reused.
        proc = self.invoke("solve", "--input", str(self.input), "--output-dir", str(out))
        self.assertEqual(proc.returncode, 2)
        self.assertIn('"certified": false', proc.stdout)

    def test_statuses_and_exit_codes(self):
        for name, puzzle, expected in [
            ("stalled", Puzzle(2, 2, ((1,), (1,)), ((1,), (1,))), "stalled"),
            ("contradiction", Puzzle(1, 1, ((1,),), ((),)), "contradiction")]:
            write_json(self.input, puzzle.to_wire())
            out = self.root / name
            proc = self.invoke("solve", "--input", str(self.input), "--output-dir", str(out))
            self.assertEqual(proc.returncode, 0)
            result = load_json(out / "result.json")
            self.assertEqual(result["status"], expected)
            self.assertFalse(result["certified"])
        proc = self.invoke("solve", "--input", str(self.input), "--output-dir",
                           str(self.root / "abort"), "--max-lines", "0")
        self.assertEqual(proc.returncode, 4)
        result = load_json(self.root / "abort" / "result.json")
        self.assertEqual(result["status"], "aborted")
        self.assertFalse(result["certified"])
        self.assertFalse(result["proof_verified"])
        write_json(self.input, {"solution": []})
        proc = self.invoke("solve", "--input", str(self.input), "--output-dir", str(self.root / "invalid"))
        self.assertEqual(proc.returncode, 2)

    def test_invalid_proof_and_verifier_abort(self):
        out = self.root / "proof"
        self.assertEqual(self.invoke("solve", "--input", str(self.input),
                                     "--output-dir", str(out)).returncode, 0)
        proc = self.invoke("verify", "--input", str(self.input), "--proof",
                           str(out / "proof.json"), "--max-lines", "0")
        self.assertEqual(proc.returncode, 4)
        proof = load_json(out / "proof.json")
        proof["logic_hash"] = "bad"
        write_json(out / "proof.json", proof)
        proc = self.invoke("verify", "--input", str(self.input), "--proof", str(out / "proof.json"))
        self.assertEqual(proc.returncode, 3)
        (out / "proof.json").write_text("{", encoding="utf-8")
        self.assertEqual(self.invoke("verify", "--input", str(self.input), "--proof",
                                     str(out / "proof.json")).returncode, 3)

    def test_json_resource_and_duplicate_key_rejection(self):
        for data in ('{"width":2,"width":3}', '{"x":NaN}', '[1,]'):
            self.input.write_text(data, encoding="utf-8")
            self.assertEqual(self.invoke("solve", "--input", str(self.input), "--output-dir",
                                         str(self.root / "bad-json")).returncode, 2)
        self.input.write_bytes(b" " * (2 * 1024 * 1024 + 1))
        self.assertEqual(self.invoke("solve", "--input", str(self.input), "--output-dir",
                                     str(self.root / "big-json")).returncode, 2)

    def test_memory_and_technical_errors_cannot_certify(self):
        for exc, expected in ((MemoryError("test"), 4), (RuntimeError("test"), 5)):
            with patch("tools.puzzle_production.cli.solve", side_effect=exc):
                self.assertEqual(main(["solve", "--input", str(self.input),
                                       "--output-dir", str(self.root / str(expected))]), expected)
                result = load_json(self.root / str(expected) / "result.json")
                self.assertFalse(result["certified"])
