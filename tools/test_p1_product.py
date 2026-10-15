import tempfile
import os
import shutil
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

from p1_preflight import PreflightError
from p1_product import (EXPECTED_PROJECT_NAME, package, package_player, player_extras, player_guide,
                        project_name, require_clean_output, require_foreign_slot_failure)
from gp48_delivery import PLAYER_FILES, verify_player_package
from ci_scope import FLAGS, JOBS, classify, evaluate


class ProductHarnessTests(unittest.TestCase):
    def test_import_override_is_temporary_even_after_failed_process(self):
        from p1_product import run_phase
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project.godot"
            project.write_bytes(b"original project\n")
            program = ("import pathlib,sys; p=pathlib.Path(sys.argv[-1]); "
                       "assert (p/'override.cfg').read_text() == '[editor]\\nimport/use_multiple_threads=false\\n'; "
                       "sys.exit(3)")
            result = run_phase("import-probe", [sys.executable, "-c", program, "--import", "--path", str(root)],
                               os.environ.copy(), 10, root)
            self.assertEqual(result["exit_code"], 3)
            self.assertFalse((root / "override.cfg").exists())
            self.assertEqual(project.read_bytes(), b"original project\n")

    def test_import_override_never_replaces_existing_settings_or_affects_runtime(self):
        from p1_product import import_settings
        with tempfile.TemporaryDirectory() as temporary:
            override = Path(temporary) / "override.cfg"
            override.write_bytes(b"caller settings\n")
            with self.assertRaises(FileExistsError):
                with import_settings(["engine", "--path", temporary, "--import"]):
                    self.fail("must not run with overwritten settings")
            with import_settings(["engine", "--path", temporary, "--export-release", "Windows"]):
                self.assertEqual(override.read_bytes(), b"caller settings\n")
            self.assertEqual(override.read_bytes(), b"caller settings\n")

    def test_native_fixture_catalog_is_bounded_and_player_export_keeps_real_content(self):
        from product_fixtures import copy_regression_game, restore_player_catalog
        import json
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            source = temp / "source"
            (source / "game/data/content").mkdir(parents=True)
            (source / "game/art/content").mkdir(parents=True)
            (source / "game/model").mkdir()
            (source / "game/model/loader.gd").write_text("runtime code\n")
            shutil.copytree(root / "tests/puzzle_production/fixtures/catalog", source / "tests/puzzle_production/fixtures/catalog")
            (source / "game/data/registry.json").write_text('{"actual":"catalog"}\n')
            (source / "game/data/content/new.json").write_text("not a valid puzzle; must never be certified here")
            (source / "game/art/content/new.png").write_bytes(b"opaque bytes")
            project = temp / "regression"
            copy_regression_game(source, project)
            self.assertEqual(len(json.loads((project / "data/registry.json").read_text())["entries"]), 6)
            self.assertFalse((project / "data/content").exists())
            self.assertFalse((project / "art/content").exists())
            self.assertTrue((project / "model/loader.gd").exists())
            self.assertTrue(restore_player_catalog(source, project))
            self.assertEqual((project / "data/registry.json").read_bytes(), (source / "game/data/registry.json").read_bytes())
            self.assertEqual((project / "art/content/new.png").read_bytes(), b"opaque bytes")

    def test_regular_identity_and_study_exclusions_survive_project_move(self):
        root = Path(__file__).resolve().parents[1] / "game"
        project = (root / "project.godot").read_text(encoding="utf-8")
        self.assertIn('run/main_scene="res://main.tscn"', project)
        self.assertEqual(project_name(root / "project.godot"), EXPECTED_PROJECT_NAME)
        export = (root / "export_presets.cfg").read_text(encoding="utf-8")
        for prefix in ("tests/*", "study/*", "full_view_study/*", "perf_a/*"):
            self.assertIn(prefix, export)

    @staticmethod
    def placeholder_build(output):
        build = output / "build"
        build.mkdir()
        for name in ("picross-p1.exe", "picross-p1.console.exe", "picross-p1.pck"):
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
                    expected = player_guide(root, manifest["source_commit"]).encode("utf-8") if name == "SPIELANLEITUNG.md" else source.read_bytes()
                    self.assertEqual(bundle.read(name), expected)
                self.assertIn(player_guide(root, manifest["source_commit"]).encode("utf-8"), bundle.read("README.txt"))
                self.assertNotIn(b"](../", bundle.read("SPIELANLEITUNG.md"))

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
        valid = dict(exit_code=4, output="RP6_T01_SAVE status=loaded unknown=399\n"
                     "ERROR: RP3_FAIL: isolated T04 preserves T01 cells after restart\n"
                     "RP6_RESULT index=2 stage=read checks=41 failures=1\n")
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
            for name in ("picross-p1.exe", "picross-p1.console.exe", "picross-p1.pck"):
                (build / name).write_bytes(name.encode())
            extra = root / "extra.txt"
            extra.write_text("neutral", encoding="utf-8")
            extras = {name: extra for name in PLAYER_FILES - {"picross-p1.exe", "picross-p1.console.exe", "README.txt", "product-report.json"}}
            manifest = dict(source_commit="b" * 40, source_tree_dirty=False, render_metrics={2: (0.25, 0.78)})
            artifact = package(build, root, manifest, "neutral instructions", extras)
            self.assertEqual(set(verify_player_package(artifact, manifest)["files"]), PLAYER_FILES | {"picross-p1.pck"})
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
        project = Path(__file__).resolve().parents[1] / "game/project.godot"
        self.assertEqual(project_name(project), EXPECTED_PROJECT_NAME)
        self.assertNotIn("Â", project.read_text(encoding="utf-8"))

    def test_wrong_project_name_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project.godot"
            project.write_text('[application]\nconfig/name="picross Â· P1"\n', encoding="utf-8")
            with self.assertRaises(PreflightError):
                project_name(project)

    def test_native_pack_audit_targets_separate_pack_and_binds_its_bytes(self):
        from za1_product import audit_pack
        from unittest.mock import Mock
        import hashlib
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "picross-p1.exe"
            executable.write_bytes(b"MZengine")
            pack = executable.with_suffix(".pck")
            phase = Mock()
            for data in (None, b"", b"MZinvalid"):
                if data is not None: pack.write_bytes(data)
                with self.subTest(data=data), self.assertRaises(PreflightError):
                    audit_pack(root, "godot", executable, {}, phase, 10, "pack-audit")
                phase.assert_not_called()
            pack.write_bytes(b"GDPCactual-resources")
            result = audit_pack(root, "godot", executable, {}, phase, 10, "pack-audit")
            command = phase.call_args.args[1]
            self.assertEqual(command[command.index("--main-pack")+1], str(pack))
            self.assertEqual(result['pack_sha256'], hashlib.sha256(pack.read_bytes()).hexdigest())
            self.assertEqual(phase.call_args.kwargs['phase_env']['ZA1_PACK_COUNT'], '10')

    def test_artifact_requires_executables_and_pack_and_binds_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            build.mkdir()
            manifest = dict(source_commit="a" * 40, source_tree_dirty=False)
            (build / "picross-p1.exe").write_bytes(b"main")
            with self.assertRaises(PreflightError):
                package(build, root, manifest, "instructions")
            (build / "picross-p1.console.exe").write_bytes(b"console")
            with self.assertRaises(PreflightError):
                package(build, root, manifest, "instructions")
            (build / "picross-p1.pck").write_bytes(b"")
            with self.assertRaises(PreflightError):
                package(build, root, manifest, "instructions")
            (build / "picross-p1.pck").write_bytes(b"GDPCresources")
            artifact = package(build, root, manifest, "instructions")
            with zipfile.ZipFile(artifact) as archive:
                self.assertEqual(set(archive.namelist()), {"picross-p1.exe", "picross-p1.console.exe", "picross-p1.pck", "README.txt", "product-report.json"})
                self.assertIn(b"a" * 40, archive.read("README.txt"))
            (build / "unrelated.txt").write_text("unrelated")
            with self.assertRaises(PreflightError):
                package(build, root, manifest, "instructions")
