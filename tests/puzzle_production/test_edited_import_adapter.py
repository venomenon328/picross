"""Fixed synthetic edited imports; no production puzzle inputs."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, InvalidProof, digest, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, raster_image
from tools.puzzle_production.target_adapter import export, inspect, verify_export
from tools.puzzle_production.content_registry import registration
from tools.puzzle_production.za1_fixtures import FIXTURES, ROOT, approve, seal, isolated_checkout


class EditedImportAdapterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.package = p = self.root / "package"
        shutil.copytree(FIXTURES / "direct-mono", p)
        h = load_json(p / "handoff.json")
        d = load_json(p / "production/import/design.json")
        before = [["empty", "ink", "ink", "ink", "ink", "empty"] for _ in range(4)]
        before[1][0], before[1][2] = "ink", "empty"
        raster_image(before, d).save(p / "motifs/source.png")
        for name in ("motif-approval.json", "motifs/source.provenance.json"):
            raw = load_json(p / name)
            raw["sha256"] = file_hash(p / "motifs/source.png")
            write_json(p / name, raw)
        h["motif"]["sha256"] = file_hash(p / "motifs/source.png")
        import_image(p / "motifs/source.png", p / "production/import/design.json", p / "reference")
        reference = load_json(p / "reference/area-candidate.json")
        matrix = deepcopy(before)
        matrix[1][0], matrix[1][2] = "empty", "ink"
        raster_image(matrix, d).save(p / "edited-source.png")
        import_image(p / "edited-source.png", p / "production/import/design.json", p / "edited")
        selected = load_json(p / "edited/area-candidate.json")
        self.reference = {"bundle": "reference", "variant": "area", "candidate_id": reference["id"],
                          "matrix_hash": digest(before), "manifest_sha256": file_hash(p / "reference/manifest.json")}
        plan = {"puzzle_id": h["puzzle_id"], "revision": h["revision"], "reference": self.reference,
                "max_changes": 2, "seed": None, "search": False, "solve_seconds": 30, "verify_seconds": 30,
                "solve_lines": 100000, "verify_lines": 100000,
                "edits": [{"column": 1, "row": 2, "before": "ink", "after": "empty"},
                          {"column": 3, "row": 2, "before": "empty", "after": "ink"}],
                "protected": [[(x, y) not in ((0, 1), (2, 1)) for x in range(6)] for y in range(4)]}
        write_json(p / "edit-record.json", plan)
        h.update(state="blocked", manual_edit_record="edit-record.json", content_blockers=["TEST ONLY fixed edit/frame metadata"],
                 candidate={"source_type": "import", "bundle": "edited", "variant": "area", "proof": "edited/area-proof.json",
                            "matrix_hash": digest(matrix), "logic_hash": selected["logic_hash"]}, repair=None)
        h["gates"]["frame"] = "fail"
        difficulty = load_json(p / "difficulty.json")
        difficulty["logic_hash"] = selected["logic_hash"]
        write_json(p / "difficulty.json", difficulty)
        seal(p, h)
        self.approval = self.root / "approval.json"
        self.auth = self.root / "manual-authorization.json"
        self.authorize()

    def authorize(self, *, frame=True, original_zip=None):
        p = self.package
        h = load_json(p / "handoff.json")
        seal(p, h)
        h = load_json(p / "handoff.json")
        approve(p, self.approval)
        common = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
                  "handoff_sha256": file_hash(p / "handoff.json"), "inventory_sha256": h["inventory"]["sha256"],
                  "selection": load_json(self.approval)["selection"], "plan_sha256": file_hash(p / "edit-record.json"),
                  "reference": self.reference, "superseded_content_blockers": h["content_blockers"]}
        owner = {**common, "format": "picross-owner-override-v2", "actor": "TEST ONLY",
                 "statement": "Synthetic fixed edits and frame exception, not a human approval",
                 "timestamp_utc": "2026-10-13T00:00:00Z", "package_sha256": original_zip,
                 "approval_sha256": file_hash(self.approval),
                 "permissions": {"fixed_mono_edits": True, "frame_exception": frame}}
        write_json(self.root / "owner-override.json", owner)
        write_json(self.auth, {**common, "format": "picross-manual-authorization-v2", "original_zip_sha256": original_zip,
                              "frame_exception": frame, "owner_override": {"file": "owner-override.json",
                                  "sha256": file_hash(self.root / "owner-override.json")}})

    def inspect(self, approval=True):
        with open_package(self.package, allow_manual_review=True) as p:
            return inspect(p, self.approval if approval else None, manual_authorization=self.auth)[0]

    def export(self, source=None):
        out = self.root / "export"
        export(source or self.package, out, name="TEST ONLY", revision=1, stem="edited_test", save_slot="edited_test",
               approval_path=self.approval, manual_authorization=self.auth, category_id="voegel",
               categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        return out

    def test_zip_export_offline_plan_and_register_preserve_originals(self):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for f in self.package.rglob("*"):
                if f.is_file(): z.write(f, f.relative_to(self.package).as_posix())
        self.authorize(original_zip=file_hash(archive))
        original = (self.package / "handoff.json").read_bytes()
        out = self.export(archive)
        m, r = verify_export(out)
        self.assertEqual(m["format"], "picross-target-export-v3")
        self.assertTrue(r["technical"] and r["catalog_ready"] and r["frame_exception_accepted"])
        self.assertFalse(r["frame_valid"] or r["frame"]["left"] or r["frame"]["right"])
        self.assertEqual(r["source"]["changed_cells"], 2)
        self.assertEqual((out / "input/handoff.json").read_bytes(), original)
        checkout = isolated_checkout(self.root / "checkout")
        self.assertEqual(registration(out, checkout)["status"], "planned")
        self.assertEqual(registration(out, checkout, apply=True)["status"], "registered")

    def test_exception_requires_explicit_owner_scope_and_final_approval(self):
        with self.assertRaises(InvalidInput), open_package(self.package): pass
        self.authorize(frame=False)
        with self.assertRaisesRegex(InvalidInput, "Unresolved content gate: frame"): self.inspect()
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "requires bound final approval"): self.inspect(approval=False)
        owner = load_json(self.root / "owner-override.json")
        owner["permissions"]["fixed_mono_edits"] = False
        write_json(self.root / "owner-override.json", owner)
        a = load_json(self.auth); a["owner_override"]["sha256"] = file_hash(self.root / "owner-override.json")
        write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "scope mismatch"): self.inspect()

    def test_bad_input_selection_plan_and_reference_bindings(self):
        for key, value in (("handoff_sha256", "0"*64), ("inventory_sha256", "0"*64), ("original_zip_sha256", "0"*64),
                           ("plan_sha256", "0"*64), ("selection", {}), ("superseded_content_blockers", [])):
            self.authorize()
            a = load_json(self.auth); a[key] = value; write_json(self.auth, a)
            with self.subTest(key=key), self.assertRaises(InvalidInput): self.inspect()
        self.reference["manifest_sha256"] = "0"*64
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "reference mismatch"): self.inspect()

    def test_rebound_protection_coordinates_edits_and_budgets(self):
        path = self.package / "edit-record.json"
        baseline = load_json(path)
        for kind in ("protected", "extra-unprotected", "wrong-before", "duplicate", "invalid-color", "bool-coordinate", "budget", "search"):
            plan = deepcopy(baseline)
            if kind == "protected": plan["protected"][1][0] = True
            if kind == "extra-unprotected": plan["protected"][2][2] = False
            if kind == "wrong-before": plan["edits"][1]["before"] = "ink"
            if kind == "duplicate": plan["edits"][1] = plan["edits"][0].copy()
            if kind == "invalid-color": plan["edits"][1]["after"] = "red"
            if kind == "bool-coordinate": plan["edits"][0]["row"] = True
            if kind == "budget": plan["max_changes"] = 1
            if kind == "search": plan["search"] = True
            write_json(path, plan); self.authorize()
            with self.subTest(kind=kind), self.assertRaises(InvalidInput): self.inspect()

    def test_no_other_gate_or_bad_proof_can_be_waived(self):
        h = load_json(self.package / "handoff.json")
        h["gates"]["provenance"] = "fail"
        write_json(self.package / "handoff.json", h); self.authorize()
        with self.assertRaisesRegex(InvalidInput, "Unresolved content gate: provenance"): self.inspect()
        h["gates"]["provenance"] = "pass"
        write_json(self.package / "handoff.json", h)
        f = self.package / "edited/area-proof.json"
        proof = load_json(f); proof["logic_hash"] = "0"*64; write_json(f, proof)
        manifest = load_json(self.package / "edited/manifest.json")
        manifest["files"][f.name] = file_hash(f); write_json(self.package / "edited/manifest.json", manifest)
        self.authorize()
        with self.assertRaises((InvalidInput, InvalidProof)): self.inspect()

    def test_rebound_child_import_cannot_change_extra_cells(self):
        # A fully legitimate new RP-3 bundle still must equal exactly the fixed edits.
        from PIL import Image
        source = self.package / "edited-source.png"
        im = Image.open(source); im.putpixel((2, 2), (255, 255, 255)); im.save(source)
        child = self.package / "edited-extra"
        import_image(source, self.package / "production/import/design.json", child)
        h = load_json(self.package / "handoff.json")
        c = load_json(child / "area-candidate.json")
        h["candidate"].update(bundle="edited-extra", proof="edited-extra/area-proof.json", matrix_hash=digest(c["matrix"]), logic_hash=c["logic_hash"])
        write_json(self.package / "handoff.json", h); self.authorize()
        with self.assertRaisesRegex(InvalidInput, "other cells or design"): self.inspect()


if __name__ == "__main__":
    unittest.main()
