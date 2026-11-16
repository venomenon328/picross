"""Small synthetic regressions for the new boundary, never catalog puzzles."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from tools.puzzle_production import images, palette_gate as gate, palette_quality as quality
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import Aborted, Budget, InvalidInput, load_json, write_json
from tools.puzzle_production.authoring_inspection import inspect

def hashes(root):
    return {p.relative_to(root).as_posix(): images.file_hash(p) for p in root.rglob("*") if p.is_file()}
from tools.puzzle_production.za1_fixtures import ROOT, approve, make, seal


class PaletteGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def inspect(self, package, approval=None, exception=None):
        with open_package(package) as p:
            return inspect(p, approval, palette_exception=exception)[0]

    def package(self, *, colors=None, repaired=False, mode="color", name="package"):
        package = self.root / name
        original = images.import_image
        def recolor(source, design_path, output, *args, **kwargs):
            design = load_json(design_path)
            if colors:
                mapping = {tuple(bytes.fromhex(e["rgb"][1:])): tuple(bytes.fromhex(rgb[1:]))
                           for e, rgb in zip(design["palette"], colors)}
                with Image.open(source) as picture:
                    picture.load()
                    changed = picture.copy()
                for y in range(changed.height):
                    for x in range(changed.width):
                        old = changed.getpixel((x, y))
                        changed.putpixel((x, y), mapping.get(old, old))
                changed.save(source)
                for entry, rgb in zip(design["palette"], colors):
                    entry["rgb"] = rgb
                write_json(design_path, design)
            return original(source, design_path, output, *args, **kwargs)
        with patch("tools.puzzle_production.za1_fixtures.import_image", side_effect=recolor):
            make(package, "pz-palette-synthetic", max(3, len(colors or [])), 3, mode,
                 repaired=repaired, colors=len(colors) if colors else 2)
        h = load_json(package / "handoff.json")
        h["state"] = "raster_review"
        (package / "rulebook.md").write_text(
            "**Version 0.6.0 · Dokumentrevision 1 · TEST ONLY**\nSynthetic unchanged legacy-contract fixture.\n",
            encoding="utf-8")
        h["rulebook"] = {"version": "0.6.0", "file": "rulebook.md", "sha256": images.file_hash(package / "rulebook.md")}
        seal(package, h)
        return package

    def review(self, package, result="erfüllt", accepted=False):
        report = self.inspect(package)
        a = report["palette_gate"]["assessment"]
        record = {"format": gate.VISUAL, "puzzle_id": report["puzzle_id"], "revision": report["package_revision"],
                  "matrix_hash": report["selection"]["matrix_hash"], "logic_hash": report["selection"]["logic_hash"],
                  "palette_sha256": a["palette_sha256"], "criteria": {}}
        for criterion in gate.CRITERIA:
            record["criteria"][criterion] = {"result": result, "accepted": accepted,
                "actor": "TEST ONLY", "timestamp_utc": "2026-11-08T00:00:00Z",
                "statement": "Synthetic record, no actual owner acceptance", "reason": "Boundary test only",
                "evidence": [{"file": "evidence.txt", "sha256": images.file_hash(package / "evidence.txt")}]}
        write_json(package / "palette-review.json", record)
        h = load_json(package / "handoff.json")
        h["palette_review"] = {"file": "palette-review.json", "sha256": images.file_hash(package / "palette-review.json")}
        seal(package, h)

    def approve(self, package):
        path = self.root / (package.name + "-approval.json")
        approve(package, path)
        return path

    def exception(self, package, approval):
        report = self.inspect(package, approval)
        palette = report["palette_gate"]
        record = {"format": gate.EXCEPTION, "binding": palette["binding"],
                  "negative_pairs": palette["assessment"]["negative_pairs"], "actor": "TEST ONLY",
                  "timestamp_utc": "2026-11-08T00:00:00Z", "statement": "Synthetic owner record only",
                  "reason": "Exercise narrow negative acceptance", "approval_sha256": images.file_hash(approval), "test_only": True}
        path = self.root / "exception.json"
        write_json(path, record)
        return path


    def test_positive_requires_actual_visual_record_and_no_flag_shortcut(self):
        p = self.package()
        report = self.inspect(p)
        self.assertEqual(report["palette_gate"]["assessment"]["status"], "positive")
        self.assertFalse(report["technical"])
        approval = self.approve(p)
        self.assertFalse(self.inspect(p,approval)["technical"])
        self.review(p)
        approval = self.approve(p)
        report = self.inspect(p,approval)
        self.assertTrue(report["palette_gate"]["allowed"])

    def test_negative_exception_is_complete_external_and_keeps_negative_measurement(self):
        p = self.package(colors=["#447799", "#487b9d"])
        self.review(p)
        approval = self.approve(p)
        before = hashes(p)
        report = self.inspect(p, approval)
        self.assertEqual(report["palette_gate"]["assessment"]["status"], "negative")
        self.assertFalse(report["technical"])
        exception = self.exception(p, approval)
        report = self.inspect(p,approval,exception)
        self.assertTrue(report["technical"])
        self.assertEqual(report["palette_gate"]["assessment"]["status"], "negative")
        self.assertEqual(before, hashes(p))

    def test_exception_mutations_and_other_hard_gates_cannot_be_overridden(self):
        p = self.package(colors=["#447799", "#487b9d", "#497c9e"])
        self.review(p)
        approval = self.approve(p)
        path = self.exception(p, approval)
        original = load_json(path)
        self.assertEqual(len(original["negative_pairs"]), 3)
        for key, value in (("negative_pairs", original["negative_pairs"][:-1]), ("test_only", False), ("approval_sha256", "0" * 64),
                           ("statement", ""), ("binding", {**original["binding"], "revision": "r02"})):
            with self.subTest(key=key):
                write_json(path, {**original, key: value})
                with self.assertRaises(InvalidInput):
                    self.inspect(p, approval, path)
        write_json(path, original)
        with self.assertRaisesRegex(InvalidInput, "final approval"):
            self.inspect(p, None, path)
        # A valid exception does not replace the existing hard-gate checks.
        h = load_json(p / "handoff.json")
        for criterion in ("logic", "provenance", "motif", "frame", "difficulty", "reveal_consistency"):
            changed = deepcopy(h)
            changed["gates"][criterion] = "fail"
            write_json(p / "handoff.json", changed)
            with self.subTest(criterion=criterion), self.assertRaisesRegex(InvalidInput, "content gate"):
                self.inspect(p, approval, path)
        write_json(p / "handoff.json", h)

    def test_visual_rejection_borderline_and_explicit_acceptance_stay_separate(self):
        p = self.package(colors=["#447799", "#6a9dbf"])
        self.review(p, "nicht erfüllt")
        report = self.inspect(p)
        self.assertEqual(report["palette_gate"]["assessment"]["pairs"][0]["status"], "borderline")
        self.assertFalse(report["technical"])
        self.review(p, "nicht erfüllt", True)
        report = self.inspect(p)
        self.assertTrue(report["technical"])
        self.assertEqual(report["palette_gate"]["visual_review"]["criteria"]["Q-H02"]["result"], "nicht erfüllt")
        self.review(p, "nicht geprüft", True)
        self.assertFalse(self.inspect(p)["technical"])


    def test_optional_stored_report_is_freshly_verified_not_trusted(self):
        p = self.package()
        self.review(p)
        assessment = self.inspect(p)["palette_gate"]["assessment"]
        for field, value in (("source_fingerprint", "0" * 64), ("status", "negative"), ("empty_cells", 100)):
            write_json(p / "palette.json", {**assessment, field: value})
            h = load_json(p / "handoff.json")
            h["palette_assessment"] = {"file": "palette.json", "sha256": images.file_hash(p / "palette.json")}
            seal(p, h)
            with self.subTest(field=field), self.assertRaisesRegex(InvalidInput, "Stale"):
                self.inspect(p)

    def test_early_import_and_repair_checks_precede_solver_and_keep_negative_drafts(self):
        observed = []
        real_early, real_solve = gate.early, images.solve
        def early(*args, **kwargs):
            result = real_early(*args, **kwargs)
            observed.append(result["status"])
            return result
        def solve(*args, **kwargs):
            self.assertTrue(observed)
            return real_solve(*args, **kwargs)
        with patch.object(gate, "early", side_effect=early), patch.object(images, "solve", side_effect=solve):
            p = self.package(colors=["#447799", "#487b9d"])
        self.assertIn("negative", observed)
        self.assertTrue((p / "production/import/area-raster.png").is_file())
        self.assertIn("negative", (p / "production/import/index.html").read_text(encoding="utf-8"))
        from tools.puzzle_production import repair
        observed.clear()
        def repair_solve(*args, **kwargs):
            self.assertTrue(observed)
            return real_solve(*args, **kwargs)
        with patch.object(gate, "early", side_effect=early), patch.object(repair, "solve", side_effect=repair_solve):
            self.package(repaired=True, name="repair")
        self.assertTrue(observed)
        with self.assertRaises(Aborted):
            real_early([["ink"]], {"source_id": "test", "palette": [{"id": "ink", "rgb": "#000000"}]}, budget=Budget(0))
        self.assertEqual(real_early([["empty"]], {"source_id": "test", "palette": [{"id": "ink", "rgb": "#000000"}]})["status"], "invalid_input")
