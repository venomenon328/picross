import copy
import tempfile
import unittest
from pathlib import Path

import p1_preflight as tc
from z1_design import compare_pairs, design_dependencies

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "prototypes/p1"


class Z1Contracts(unittest.TestCase):
    def test_original_fixtures_and_proofs_byte_identical(self):
        expected = {
            "f01-proof.json": "ae32854c8a74d5e576e3169d0e1da3c79d0d05c5dbf48e999adb6840ad0874c3",
            "f01.json": "4cb13e7d2de777e463b75b60f6e336d4fcf1ae4cab3fb6dd6de2b7218a43954a",
            "f02-proof.json": "c3426d5c8c643d1ac9634ea74e04a0a6204bde215a677c99dd4e8e9ff2d4121d",
            "f02.json": "0c9884102866c16d73e8a27ffd7bdcd186a30cdfa3596bfae42bc800fb5794f7",
            "f03.json": "68d1a0a137c4439f8067785a7f362f903a7350c0df501c092d002d2760a1bd73",
        }
        for name, digest in expected.items():
            self.assertEqual(tc.sha256_file(PROJECT / "data" / name), digest)

    def test_separate_dependency_closure_has_no_save_path(self):
        deps = design_dependencies(PROJECT)
        for required in ("ui/board.gd", "ui/miniature.gd", "model/session.gd", "model/gesture.gd"):
            self.assertIn(PROJECT / required, deps)
        # Dynamic resource construction must remain the fixed fixture loader only.
        for path in deps:
            if path.name != "definition.gd":
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"FileAccess|DirAccess|ResourceLoader|\bload\(")

    def test_dependency_audit_rejects_indirect_save_import(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "design").mkdir()
            (project / "design/design.gd").write_text('const A = preload("res://helper.gd")\n')
            (project / "helper.gd").write_text('const B = preload("res://model/save_store.gd")\n')
            with self.assertRaises(tc.PreflightError):
                design_dependencies(project)

    def test_normal_entry_and_styling_default_unchanged(self):
        self.assertIn('run/main_scene="res://main.tscn"', (PROJECT / "project.godot").read_text(encoding="utf-8"))
        board = (PROJECT / "ui/board.gd").read_text(encoding="utf-8")
        self.assertIn("var frame_style: StyleBox = null", board)
        self.assertIn('style.bg_color = Color("f4efdf")', board)
        self.assertNotIn("design/", (PROJECT / "ui/main.gd").read_text(encoding="utf-8"))

    def test_demo_does_not_consult_solution_reveal_or_proof(self):
        text = (PROJECT / "design/demo.gd").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\.solution|\.reveal|\.rows|\.columns|proof")

    def test_pair_verifier_rejects_zoom_or_state_difference(self):
        items = []
        keys = ("state_sha256", "history_sha256", "clues_sha256", "logical_size", "ui_scale", "cell_size", "view", "board_rect", "grid_viewport", "palette")
        for suffix in ("f02-1920x1080", "f02-2560x1440", "f01-1920x1080", "f03-1920x1080"):
            for variant in (1, 2):
                items.append(dict(file=f"v{variant}-{suffix}.png", miniature_matches_visible_cells=True, **{k: "same" for k in keys}))
        compare_pairs(dict(captures=items))
        for key in keys:
            bad = copy.deepcopy(items)
            bad[1][key] = "different"
            with self.assertRaises(tc.PreflightError):
                compare_pairs(dict(captures=bad))
