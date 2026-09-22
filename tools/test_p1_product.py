import tempfile
import unittest
import zipfile
from pathlib import Path

from p1_preflight import PreflightError
from p1_product import package, require_clean_output


class ProductHarnessTests(unittest.TestCase):
    def test_exit_zero_with_script_error_fails(self):
        with self.assertRaises(PreflightError):
            require_clean_output(dict(name="import", exit_code=0, output="SCRIPT ERROR: parse failure"))

    def test_missing_success_marker_fails(self):
        with self.assertRaises(PreflightError):
            require_clean_output(dict(name="tests", exit_code=0, output=""), "P1_TESTS_OK")

    def test_artifact_requires_executable_pair_and_binds_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            build.mkdir()
            manifest = dict(source_commit="a" * 40, source_tree_dirty=False)
            (build / "picross-p1.exe").write_bytes(b"main")
            with self.assertRaises(PreflightError):
                package(build, root, manifest, "instructions")
            (build / "picross-p1.console.exe").write_bytes(b"console")
            artifact = package(build, root, manifest, "instructions")
            with zipfile.ZipFile(artifact) as archive:
                self.assertEqual(set(archive.namelist()), {"picross-p1.exe", "picross-p1.console.exe", "README.txt", "product-report.json"})
                self.assertIn(b"a" * 40, archive.read("README.txt"))
            (build / "unrelated.txt").write_text("unrelated")
            with self.assertRaises(PreflightError):
                package(build, root, manifest, "instructions")
