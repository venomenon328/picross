import tempfile
import shutil
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

from p1_preflight import PreflightError
from p1_product import (EXPECTED_PROJECT_NAME, package, package_player, player_extras,
                        project_name, require_clean_output, require_foreign_slot_failure)
from gp48_delivery import PLAYER_FILES, verify_player_package
from ci_scope import FLAGS, JOBS, classify, evaluate


class ProductHarnessTests(unittest.TestCase):

    @staticmethod
    def placeholder_build(output):
        build = output / "build"
        build.mkdir()
        for name in ("picross-p1.exe", "picross-p1.console.exe"):
            (build / name).write_bytes(b"packaging contract placeholder; not a Windows build")
        return build

    def test_current_player_inputs_really_package_in_fast_docs_path(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build = self.placeholder_build(output)
            manifest = dict(source_commit="a" * 40, source_tree_dirty=False)
            archive, audit = package_player(build, output, manifest, root)
            self.assertGreater(audit["bytes"], 0)
            with zipfile.ZipFile(archive) as bundle:
                for name, source in player_extras(root, output).items():
                    self.assertEqual(bundle.read(name), source.read_bytes())
                self.assertIn((root / "docs/ZS2_OWNER_TRIAL.md").read_bytes(), bundle.read("README.txt"))

    def test_deleted_or_moved_actual_markdown_inputs_fail_docs_and_required_gate(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            fixture = output / "source"
            # Derive delivery sources from the real extras, not another input list.
            extras = player_extras(root, output)
            for source in extras.values():
                if source.is_relative_to(root):
                    target = fixture / source.relative_to(root)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
            shutil.copytree(root / "tools", fixture / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            build = self.placeholder_build(output)
            markdown = [p.relative_to(root) for p in extras.values()
                        if p.is_relative_to(root) and p.suffix == ".md"]
            self.assertTrue(markdown)
            for relative in markdown:
                path = fixture / relative
                for operation in ("delete", "move"):
                    with self.subTest(path=relative.as_posix(), operation=operation):
                        content = path.read_bytes()
                        moved = path.with_suffix(".moved.md")
                        if operation == "delete":
                            path.unlink()
                        else:
                            path.rename(moved)
                        try:
                            paths = [relative.as_posix()]
                            if operation == "move":
                                paths.append(moved.relative_to(fixture).as_posix())
                            plan = classify(paths)
                            self.assertFalse(any(plan["selected"][key] for key in FLAGS))
                            with self.assertRaises(FileNotFoundError):
                                package_player(build, output, dict(source_commit="b" * 40,
                                               source_tree_dirty=False), fixture)
                            results = {job: {"result": "failure" if job == "docs" else "skipped"}
                                       for job in JOBS}
                            self.assertFalse(all(row["accepted"] for row in evaluate(plan, results)))
                        finally:
                            if moved.exists():
                                moved.rename(path)
                            else:
                                path.write_bytes(content)

    def test_foreign_slot_control_requires_valid_load_and_exact_semantic_failure(self):
        valid = dict(exit_code=4, output="RP6_F01_SAVE status=loaded unknown=399\n"
                     "ERROR: RP3_FAIL: isolated F04 preserves F01 cells after restart\n"
                     "RP6_RESULT index=3 stage=read checks=41 failures=1\n")
        require_foreign_slot_failure(valid)
        for result in [dict(valid, exit_code=0),
                       dict(valid, output=valid["output"].replace("loaded", "recovered")),
                       dict(valid, output=valid["output"].replace("399", "400")),
                       dict(valid, output=valid["output"].replace("failures=1", "failures=2")),
                       dict(valid, output=valid["output"] + "SCRIPT ERROR: parse failed\n"),
                       dict(valid, output=valid["output"] + "RP6_READ_OK\n")]:
            with self.subTest(result=result), self.assertRaises(PreflightError):
                require_foreign_slot_failure(result)


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
