import tempfile
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

from p1_preflight import PreflightError
from p1_product import EXPECTED_PROJECT_NAME, package, project_name, require_clean_output
from gp48_delivery import PLAYER_FILES, verify_player_package


class ProductHarnessTests(unittest.TestCase):
    def test_gp48_slim_upload_is_only_player_zip(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/p1-product.yml").read_text(encoding="utf-8")
        step = workflow.split("- name: Upload compact player package\n", 1)[1].split("- name:", 1)[0]
        self.assertIn("name: picross-p1-player-${{ github.event.pull_request.head.sha || github.sha }}", step)
        self.assertIn("path: ${{ runner.temp }}/p1-product-output/picross-p1-windows-x86_64.zip\n", step)
        self.assertIn("if-no-files-found: error", step)
        self.assertEqual(step.count("path:"), 1)

    def test_zv50_review_upload_is_separate(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/p1-product.yml").read_text(encoding="utf-8")
        step = workflow.split("- name: Upload ZV-50 native zoom comparisons\n", 1)[1].split("- name:", 1)[0]
        self.assertIn("name: zv50-review-${{ github.event.pull_request.head.sha || github.sha }}", step)
        self.assertIn("path: ${{ runner.temp }}/p1-product-output/picross-zv50-review.zip\n", step)
        self.assertEqual(step.count("path:"), 1)

    def test_player_contents_and_report_verifier_is_generic(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            build.mkdir()
            for name in ("picross-p1.exe", "picross-p1.console.exe"):
                (build / name).write_bytes(name.encode())
            extra = root / "extra.txt"
            extra.write_text("neutral", encoding="utf-8")
            extras = {name: extra for name in PLAYER_FILES - {"picross-p1.exe", "picross-p1.console.exe", "README.txt", "product-report.json"}}
            manifest = dict(source_commit="b" * 40, source_tree_dirty=False, render_metrics={2: (0.25, 0.78)})
            artifact = package(build, root, manifest, "neutral instructions", extras)
            self.assertEqual(set(verify_player_package(artifact, manifest)["files"]), PLAYER_FILES)
            with zipfile.ZipFile(artifact, "a") as bundle:
                bundle.writestr("renders/screenshot.png", b"technical")
            with self.assertRaisesRegex(PreflightError, "contents"):
                verify_player_package(artifact, manifest)

    def test_harness_import_needs_no_image_dependency(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-S", "-c",
                                 "import sys; sys.path.insert(0,'tools'); import p1_product"],
                                cwd=root, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_workflow_publishes_compact_player_artifact_separately(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/p1-product.yml").read_text(encoding="utf-8")
        marker = "      - name: Upload compact player package"
        self.assertIn(marker, workflow)
        block = workflow.split(marker, 1)[1].split("      - name:", 1)[0]
        self.assertIn(
            "name: picross-p1-player-${{ github.event.pull_request.head.sha || github.sha }}",
            block,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/p1-product-output/picross-p1-windows-x86_64.zip",
            block,
        )
        self.assertNotIn("renders", block)
        self.assertNotIn("path: ${{ runner.temp }}/p1-product-output/\n", block)
        self.assertIn(
            "name: picross-p1-technical-evidence-${{ github.event.pull_request.head.sha || github.sha }}",
            workflow,
        )

    def test_exit_zero_with_script_error_fails(self):
        with self.assertRaises(PreflightError):
            require_clean_output(dict(name="import", exit_code=0, output="SCRIPT ERROR: parse failure"))

    def test_missing_success_marker_fails(self):
        with self.assertRaises(PreflightError):
            require_clean_output(dict(name="tests", exit_code=0, output=""), "P1_TESTS_OK")

    def test_project_name_is_exact_utf8_without_mojibake(self):
        project = Path(__file__).resolve().parents[1] / "prototypes/p1/project.godot"
        self.assertEqual(project_name(project), EXPECTED_PROJECT_NAME)
        self.assertNotIn("Â", project.read_text(encoding="utf-8"))

    def test_wrong_project_name_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project.godot"
            project.write_text('[application]\nconfig/name="picross Â· P1"\n', encoding="utf-8")
            with self.assertRaises(PreflightError):
                project_name(project)

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
