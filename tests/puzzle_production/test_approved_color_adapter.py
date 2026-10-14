"""Approved-motif fixed-color derivations: synthetic inputs only."""
from copy import deepcopy
import unittest
import zipfile

from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, InvalidProof, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, raster_image
from tools.puzzle_production.target_adapter import export, inspect, verify_export
from tools.puzzle_production.content_registry import registration
from tools.puzzle_production.za1_fixtures import ROOT, approve, seal, isolated_checkout
import test_color_derivation_adapter as color_fixture


class ApprovedColorTests(unittest.TestCase):
    def setUp(self):
        fixture = color_fixture.ColorDerivationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root, self.p = fixture.root, fixture.p
        self.steps, self.base = fixture.steps, fixture.base
        self.auth, self.approval = fixture.auth, fixture.approval
        p = self.p
        # Original motif has a different pixel crop from the exact-cell outputs.
        d = load_json(p / "design.json")
        matrix = load_json(p / "production/import/area-candidate.json")["matrix"]
        from PIL import Image
        raster_image(matrix, d).resize((24, 12), Image.Resampling.NEAREST).save(p / "motifs/source.png")
        d["crop"] = [0, 0, 24, 12]
        write_json(p / "base-design.json", d)
        import_image(p / "motifs/source.png", p / "base-design.json", p / "approved-base")
        self.base.update(bundle="approved-base")
        h = load_json(p / "handoff.json")
        h.pop("editorial_manual_derivation")
        h["approved_parameters"] = [{"width": 6, "height": 3, "mode": "color", "foreground_colors": 4,
                                    "method": "area", "fit": d["fit"], "actual_crop": d["crop"]}]
        h["gates"]["motif"] = "pass"
        h["motif"].update(file="motifs/source.png", sha256=file_hash(p / "motifs/source.png"),
                          approval="motif-approval.json", revision="test-original")
        a = load_json(p / "motif-approval.json")
        a.update(sha256=h["motif"]["sha256"], parameters=h["approved_parameters"][0])
        write_json(p / "motif-approval.json", a)
        provenance = load_json(p / "motifs/source.provenance.json")
        provenance["sha256"] = h["motif"]["sha256"]
        write_json(p / "motifs/source.provenance.json", provenance)
        h["candidate"]["source_type"] = "manual"
        h["repair"] = {"type": "fixed_color_editorial_redraw", "reference": "approved-base",
                       "reference_variant": "area", "plan": "plan-1.json", "record": "edits-1.json"}
        h["blockers"] = ["TEST ONLY historical final-review/export metadata"]
        seal(p, h)
        self.authorize()

    def authorize(self, original_zip=None):
        h = load_json(self.p / "handoff.json")
        seal(self.p, h)
        approve(self.p, self.approval)
        common = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
                  "handoff_sha256": file_hash(self.p / "handoff.json"), "inventory_sha256": h["inventory"]["sha256"],
                  "selection": load_json(self.approval)["selection"], "superseded_content_blockers": h["blockers"],
                  "base": self.base, "steps": self.steps,
                  "approved_motif": {**{k: h["motif"][k] for k in ("file", "sha256", "derived_from_reveal_sha256", "revision")},
                     "parameters": h["approved_parameters"][0],
                     "approval": {"file": "motif-approval.json", "sha256": file_hash(self.p / "motif-approval.json")}}}
        owner = {**common, "format": "picross-owner-override-v4", "actor": "TEST ONLY",
                 "statement": "Synthetic fixed-color authorization only", "timestamp_utc": "2026-10-14T00:00:00Z",
                 "package_sha256": original_zip, "approval_sha256": file_hash(self.approval),
                 "permissions": {"fixed_color_edits": True}}
        write_json(self.root / "owner-override.json", owner)
        write_json(self.auth, {**common, "format": "picross-manual-authorization-v4", "original_zip_sha256": original_zip,
                              "owner_override": {"file": "owner-override.json", "sha256": file_hash(self.root / "owner-override.json")}})

    def inspect(self, approval=True):
        with open_package(self.p, allow_manual_review=True) as p:
            return inspect(p, self.approval if approval else None, manual_authorization=self.auth)[0]

    def test_original_motif_zip_export_and_offline_registration(self):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for f in self.p.rglob("*"):
                if f.is_file(): z.write(f, f.relative_to(self.p).as_posix())
        self.authorize(file_hash(archive))
        original_handoff = (self.p / "handoff.json").read_bytes()
        out = self.root / "export"
        export(archive, out, name="TEST ONLY", revision=1, stem="approved_color", save_slot="approved_color",
               approval_path=self.approval, manual_authorization=self.auth, category_id="voegel",
               categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        manifest, report = verify_export(out)
        self.assertEqual(manifest["format"], "picross-target-export-v3")
        self.assertTrue(report["technical"] and report["catalog_ready"])
        self.assertFalse(report["late_motif_acceptance"])
        self.assertEqual(report["original_motif_gate"], "pass")
        self.assertEqual(report["source"]["changed_cells"], 2)
        self.assertEqual((out / "input/handoff.json").read_bytes(), original_handoff)
        checkout = isolated_checkout(self.root / "checkout")
        self.assertEqual(registration(out, checkout)["status"], "planned")
        self.assertEqual(registration(out, checkout, apply=True)["status"], "registered")

    def test_motif_and_all_content_gates_stay_required(self):
        with self.assertRaisesRegex(InvalidInput, "requires bound final approval"): self.inspect(False)
        for gate in ("motif", "logic", "provenance", "visual", "frame", "difficulty", "reveal_approval", "reveal_consistency"):
            h = load_json(self.p / "handoff.json"); h["gates"][gate] = "fail"
            seal(self.p, h); self.authorize()
            with self.subTest(gate=gate), self.assertRaises(InvalidInput): self.inspect()
            h["gates"][gate] = "pass"; seal(self.p, h)

    def test_rebound_owner_and_original_parameter_bindings(self):
        for field in ("inventory_sha256", "handoff_sha256", "original_zip_sha256"):
            self.authorize(); a = load_json(self.auth); a[field] = "0" * 64; write_json(self.auth, a)
            with self.subTest(field=field), self.assertRaises(InvalidInput): self.inspect()
        self.authorize()
        owner = load_json(self.root / "owner-override.json"); owner["permissions"]["fixed_color_edits"] = 1
        write_json(self.root / "owner-override.json", owner)
        a = load_json(self.auth); a["owner_override"]["sha256"] = file_hash(self.root / "owner-override.json")
        write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "permission scope"): self.inspect()
        # Both authorization and owner are honestly re-bound, but original crop is wrong.
        h = load_json(self.p / "handoff.json"); h["approved_parameters"][0]["actual_crop"] = [0, 0, 6, 3]
        seal(self.p, h); self.authorize()
        with self.assertRaisesRegex(InvalidInput, "approved parameter binding"): self.inspect()

    def test_v3_cannot_be_used_for_approved_manual_source(self):
        a = load_json(self.auth); a["format"] = "picross-manual-authorization-v3"
        a["accepted_motif"] = a.pop("approved_motif"); a["accepted_motif"].pop("approval")
        write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "V3 requires"): self.inspect()

    def test_external_parameter_member_must_match_original_import(self):
        h = load_json(self.p / "handoff.json")
        wrong = deepcopy(h["approved_parameters"][0]); wrong["width"] = 5
        h["approved_parameters"].insert(0, wrong)
        seal(self.p, h); self.authorize()
        with self.assertRaisesRegex(InvalidInput, "approved parameter binding"): self.inspect()

    def test_rebound_mask_edits_proof_and_parent_are_checked(self):
        original = load_json(self.p / "edits-0.json"); original_plan = load_json(self.p / "plan-0.json")
        for kind in ("mask", "before", "search", "matrix", "parent"):
            record, plan = deepcopy(original), deepcopy(original_plan)
            if kind == "mask": plan["protected"][2][2] = False
            if kind == "before": record["edits"][0]["before"] = "gold"
            if kind == "search": plan["search"] = True
            if kind == "matrix": record["matrix_hash"] = "0" * 64
            if kind == "parent": plan["reference"] = {"bundle": "approved-base", "variant": "area", "candidate_id": "0" * 64, "manifest_sha256": "0" * 64}
            plan["edits"] = record["edits"]
            write_json(self.p / "edits-0.json", record); write_json(self.p / "plan-0.json", plan)
            self.steps[0]["record"]["sha256"] = file_hash(self.p / "edits-0.json")
            self.steps[0]["plan"]["sha256"] = file_hash(self.p / "plan-0.json")
            self.authorize()
            with self.subTest(kind=kind), self.assertRaises(InvalidInput): self.inspect()
        write_json(self.p / "edits-0.json", original); write_json(self.p / "plan-0.json", original_plan)
        self.steps[0]["record"]["sha256"] = file_hash(self.p / "edits-0.json")
        self.steps[0]["plan"]["sha256"] = file_hash(self.p / "plan-0.json")
        f = self.p / "child-0/area-proof.json"; proof = load_json(f); proof["logic_hash"] = "0" * 64; write_json(f, proof)
        manifest = load_json(self.p / "child-0/manifest.json"); manifest["files"][f.name] = file_hash(f)
        write_json(self.p / "child-0/manifest.json", manifest); self.authorize()
        with self.assertRaises((InvalidInput, InvalidProof)): self.inspect()


if __name__ == "__main__":
    unittest.main()
