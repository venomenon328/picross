"""Fixed synthetic color chains, including re-bound corrupt inputs; no real puzzles."""
from copy import deepcopy
from pathlib import Path
import tempfile
import shutil
import unittest
import zipfile

from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, InvalidProof, digest, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, raster_image
from tools.puzzle_production.target_adapter import export, inspect, verify_export
from tools.puzzle_production.content_registry import registration
from tools.puzzle_production.za1_fixtures import FIXTURES, ROOT, make, approve, seal, isolated_checkout


class ColorDerivationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.p = p = self.root / "package"
        make(p, "pz-test-color-chain", 6, 3, "color", colors=4)
        h = load_json(p / "handoff.json")
        d = load_json(p / "design.json")
        before = load_json(p / "production/import/area-candidate.json")["matrix"]
        self.base = {"source_type": "import", "bundle": "production/import", "variant": "area",
                     "reference_bundle": None, "reference_variant": None, "matrix_hash": digest(before)}
        self.steps = []
        for i, (x, after) in enumerate(((0, "blue"), (1, "empty"))):
            matrix = deepcopy(before)
            matrix[1][x] = after
            source = p / f"source-{i}.png"
            raster_image(matrix, d).save(source)
            directory = p / f"child-{i}"
            import_image(source, p / "design.json", directory)
            plan = {"format": "picross-editorial-fixed-cell-plan-v1", "puzzle_id": h["puzzle_id"],
                    "revision": h["revision"], "reference_matrix_hash": digest(before), "max_changes": 1,
                    "search": False, "seed": None, "solve_seconds": 30, "verify_seconds": 30, "max_lines": 100000,
                    "protected": [[(xx, y) != (x, 1) for xx in range(6)] for y in range(3)],
                    "edits": [{"column": x + 1, "row": 2, "before": before[1][x], "after": after}]}
            write_json(p / f"plan-{i}.json", plan)
            write_json(p / f"edits-{i}.json", {"format": "picross-editorial-fixed-cell-derivation-v1",
                "reference_matrix_hash": digest(before), "matrix_hash": digest(matrix), "search": False,
                "seed": None, "edits": plan["edits"], "actual_changed_positions": 1, "plan": f"plan-{i}.json"})
            self.steps.append({"record": {"file": f"edits-{i}.json", "sha256": file_hash(p / f"edits-{i}.json")},
                               "plan": {"file": f"plan-{i}.json", "sha256": file_hash(p / f"plan-{i}.json")},
                               "output": {"bundle": f"child-{i}", "variant": "area"}})
            before = matrix
        c = load_json(p / "child-1/area-candidate.json")
        h.update(state="raster_review", editorial_manual_derivation="edits-1.json", approved_parameters=[],
                 proposed_parameters=h["approved_parameters"], blockers=["TEST ONLY pending exact correction acceptance"],
                 candidate={"source_type": "import", "bundle": "child-1", "variant": "area", "proof": "child-1/area-proof.json",
                            "matrix_hash": digest(before), "logic_hash": c["logic_hash"]})
        h["gates"]["motif"] = "pending"
        h["motif"].update(file="source-1.png", sha256=file_hash(p / "source-1.png"), approval=None, revision="test-corrected")
        provenance = load_json(p / "motifs/source.provenance.json")
        provenance.update(file="source-1.png", sha256=h["motif"]["sha256"])
        write_json(p / "source-1.provenance.json", provenance)
        difficulty = load_json(p / "difficulty.json")
        difficulty["logic_hash"] = c["logic_hash"]
        write_json(p / "difficulty.json", difficulty)
        seal(p, h)
        self.auth, self.approval = self.root / "manual-authorization.json", self.root / "approval.json"
        self.authorize()

    def authorize(self, original_zip=None):
        p = self.p
        h = load_json(p / "handoff.json")
        seal(p, h)
        approve(p, self.approval)
        common = {"puzzle_id": h["puzzle_id"], "revision": h["revision"], "handoff_sha256": file_hash(p / "handoff.json"),
                  "inventory_sha256": h["inventory"]["sha256"], "selection": load_json(self.approval)["selection"],
                  "superseded_content_blockers": h["blockers"], "base": self.base, "steps": self.steps,
                  "accepted_motif": {**{k: h["motif"][k] for k in ("file", "sha256", "derived_from_reveal_sha256", "revision")},
                                     "parameters": h["proposed_parameters"][0]}}
        owner = {**common, "format": "picross-owner-override-v3", "actor": "TEST ONLY", "statement": "Synthetic acceptance only",
                 "timestamp_utc": "2026-10-14T00:00:00Z", "package_sha256": original_zip,
                 "approval_sha256": file_hash(self.approval), "permissions": {"fixed_color_edits": True, "late_motif_acceptance": True}}
        write_json(self.root / "owner-override.json", owner)
        write_json(self.auth, {**common, "format": "picross-manual-authorization-v3", "original_zip_sha256": original_zip,
                              "owner_override": {"file": "owner-override.json", "sha256": file_hash(self.root / "owner-override.json")}})

    def inspect(self, approval=True):
        with open_package(self.p, allow_manual_review=True) as p:
            return inspect(p, self.approval if approval else None, manual_authorization=self.auth)[0]

    def test_zip_export_offline_registration_preserves_original_review(self):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for f in self.p.rglob("*"):
                if f.is_file(): z.write(f, f.relative_to(self.p).as_posix())
        self.authorize(file_hash(archive))
        before = (self.p / "handoff.json").read_bytes()
        out = self.root / "export"
        export(archive, out, name="TEST ONLY", revision=1, stem="color_chain", save_slot="color_chain",
               approval_path=self.approval, manual_authorization=self.auth, category_id="voegel",
               categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        manifest, report = verify_export(out)
        self.assertEqual(manifest["format"], "picross-target-export-v3")
        self.assertTrue(report["technical"] and report["catalog_ready"] and report["late_motif_acceptance"])
        self.assertEqual(report["original_motif_gate"], "pending")
        self.assertEqual(report["source"]["changed_cells"], 2)
        self.assertEqual(len(report["source"]["chain"]), 2)
        self.assertEqual((out / "input/handoff.json").read_bytes(), before)
        checkout = isolated_checkout(self.root / "checkout")
        self.assertEqual(registration(out, checkout)["status"], "planned")
        self.assertEqual(registration(out, checkout, apply=True)["status"], "registered")

    def test_explicit_auth_final_acceptance_and_all_other_gates_required(self):
        with self.assertRaises(InvalidInput), open_package(self.p): pass
        with open_package(self.p, allow_manual_review=True) as p, self.assertRaises(InvalidInput): inspect(p, self.approval)
        with self.assertRaisesRegex(InvalidInput, "requires bound final approval"): self.inspect(False)
        for gate in ("frame", "logic", "provenance", "visual", "difficulty", "reveal_approval", "reveal_consistency"):
            h = load_json(self.p / "handoff.json")
            h["gates"][gate] = "fail"
            seal(self.p, h); self.authorize()
            with self.subTest(gate=gate), self.assertRaisesRegex(InvalidInput, "Unresolved content gate"): self.inspect()
            h["gates"][gate] = "pass"; seal(self.p, h)

    def test_input_owner_and_parameter_bindings(self):
        for key, value in (("handoff_sha256", "0"*64), ("inventory_sha256", "0"*64),
                           ("original_zip_sha256", "0"*64), ("selection", {}), ("superseded_content_blockers", [])):
            self.authorize()
            a = load_json(self.auth); a[key] = value; write_json(self.auth, a)
            with self.subTest(key=key), self.assertRaises(InvalidInput): self.inspect()
        self.authorize()
        owner = load_json(self.root / "owner-override.json")
        owner["permissions"]["late_motif_acceptance"] = 1
        write_json(self.root / "owner-override.json", owner)
        a = load_json(self.auth); a["owner_override"]["sha256"] = file_hash(self.root / "owner-override.json")
        write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "permission scope"): self.inspect()
        self.authorize()
        a = load_json(self.auth); a["accepted_motif"]["parameters"]["fit"] = "stretch"; write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "parameter binding"): self.inspect()

    def test_rebound_chain_cannot_hide_edits_masks_or_invalid_values(self):
        original = load_json(self.p / "edits-0.json")
        plan_original = load_json(self.p / "plan-0.json")
        for kind in ("wrong-before", "unknown-color", "bool-coordinate", "extra-unprotected", "protected", "budget", "search", "parent", "result", "duplicate"):
            record, plan = deepcopy(original), deepcopy(plan_original)
            if kind == "wrong-before": record["edits"][0]["before"] = "gold"
            if kind == "unknown-color": record["edits"][0]["after"] = "unknown"
            if kind == "bool-coordinate": record["edits"][0]["row"] = True
            if kind == "extra-unprotected": plan["protected"][2][2] = False
            if kind == "protected": plan["protected"][1][0] = True
            if kind == "budget": plan["max_changes"] = 0
            if kind == "search": record["search"] = True
            if kind == "parent": record["reference_matrix_hash"] = "0"*64
            if kind == "result": record["matrix_hash"] = "0"*64
            if kind == "duplicate": record["edits"] *= 2; plan["max_changes"] = 2
            plan["edits"] = record["edits"]
            write_json(self.p / "edits-0.json", record); write_json(self.p / "plan-0.json", plan)
            self.steps[0]["record"]["sha256"] = file_hash(self.p / "edits-0.json")
            self.steps[0]["plan"]["sha256"] = file_hash(self.p / "plan-0.json")
            self.authorize()
            with self.subTest(kind=kind), self.assertRaises(InvalidInput): self.inspect()

    def test_redraw_record_uses_bound_plan_and_exact_mask(self):
        old = load_json(self.p / "plan-0.json")
        plan = {"format": "picross-editorial-raster-redraw-plan-v1", "puzzle_id": old["puzzle_id"],
                "revision": old["revision"], "seed": None, "search": False,
                "limits": {"max_changed_positions": 1, "solve_seconds": 30, "verify_seconds": 30, "max_lines": 100000}}
        write_json(self.p / "plan-0.json", plan)
        record = load_json(self.p / "edits-0.json")
        record.update(format="picross-editorial-raster-redraw-v1", protected=old["protected"],
                      plan_sha256=file_hash(self.p / "plan-0.json"))
        write_json(self.p / "edits-0.json", record)
        for key, name in (("record", "edits-0.json"), ("plan", "plan-0.json")):
            self.steps[0][key]["sha256"] = file_hash(self.p / name)
        self.authorize()
        self.assertTrue(self.inspect()["technical"])
        record["plan_sha256"] = "0"*64
        write_json(self.p / "edits-0.json", record)
        self.steps[0]["record"]["sha256"] = file_hash(self.p / "edits-0.json")
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "plan binding"): self.inspect()

    def test_repaired_base_is_reconstructed_before_fixed_color_edits(self):
        p = self.root / "repair-package"
        shutil.copytree(FIXTURES / "repair-color", p)
        self.p = p
        h = load_json(p / "handoff.json")
        d = load_json(p / "production/import/design.json")
        raw = load_json(p / "production/repair/repair.json")
        before = raw["matrix"]
        self.base = {"source_type": "repair", "bundle": "production/repair", "variant": f"candidate-{raw['selected']:03d}",
                     "reference_bundle": "production/import", "reference_variant": raw["reference"]["variant"], "matrix_hash": digest(before)}
        color = d["palette"][0]["id"]
        matrix = [[color] * d["width"] for _ in range(d["height"])]
        edits = [{"column": x+1, "row": y+1, "before": v, "after": color}
                 for y, row in enumerate(before) for x, v in enumerate(row) if v != color]
        raster_image(matrix, d).save(p / "corrected.png")
        import_image(p / "corrected.png", p / "production/import/design.json", p / "corrected")
        c = load_json(p / "corrected/area-candidate.json")
        plan = {"format": "picross-editorial-fixed-cell-plan-v1", "puzzle_id": h["puzzle_id"], "revision": h["revision"],
                "reference_matrix_hash": digest(before), "edits": edits, "max_changes": len(edits),
                "protected": [[v == color for v in row] for row in before], "seed": None, "search": False,
                "solve_seconds": 30, "verify_seconds": 30, "max_lines": 100000}
        write_json(p / "fixed-plan.json", plan)
        write_json(p / "fixed-record.json", {"format": "picross-editorial-fixed-cell-derivation-v1", "plan": "fixed-plan.json",
            "reference_matrix_hash": digest(before), "matrix_hash": digest(matrix), "actual_changed_positions": len(edits),
            "edits": edits, "seed": None, "search": False})
        self.steps = [{"record": {"file": "fixed-record.json", "sha256": file_hash(p / "fixed-record.json")},
                       "plan": {"file": "fixed-plan.json", "sha256": file_hash(p / "fixed-plan.json")},
                       "output": {"bundle": "corrected", "variant": "area"}}]
        params = h["approved_parameters"]
        h.update(state="raster_review", repair=None, approved_parameters=[], proposed_parameters=params,
                 editorial_manual_derivation="fixed-record.json", blockers=["TEST ONLY late correction acceptance"],
                 candidate={"source_type": "import", "bundle": "corrected", "variant": "area", "proof": "corrected/area-proof.json",
                            "matrix_hash": digest(matrix), "logic_hash": c["logic_hash"]})
        h["gates"]["motif"] = "pending"
        h["motif"].update(file="corrected.png", sha256=file_hash(p / "corrected.png"), approval=None, revision="test-corrected")
        provenance = load_json(p / "motifs/source.provenance.json")
        provenance.update(file="corrected.png", sha256=h["motif"]["sha256"])
        write_json(p / "corrected.provenance.json", provenance)
        difficulty = load_json(p / "difficulty.json"); difficulty["logic_hash"] = c["logic_hash"]
        write_json(p / "difficulty.json", difficulty)
        seal(p, h); self.authorize()
        self.assertTrue(self.inspect()["technical"])
        self.base["reference_variant"] = "wrong"
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "repair base mismatch"): self.inspect()

    def test_legitimate_child_import_cannot_change_an_unlisted_cell(self):
        d = load_json(self.p / "design.json")
        matrix = load_json(self.p / "child-0/area-candidate.json")["matrix"]
        matrix[2][5] = "gold"
        raster_image(matrix, d).save(self.p / "extra.png")
        import_image(self.p / "extra.png", self.p / "design.json", self.p / "extra")
        self.steps[0]["output"]["bundle"] = "extra"
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "other cells or design"): self.inspect()

    def test_bad_intermediate_proof_is_rejected(self):
        f = self.p / "child-0/area-proof.json"
        proof = load_json(f); proof["logic_hash"] = "0"*64; write_json(f, proof)
        manifest = load_json(self.p / "child-0/manifest.json")
        manifest["files"][f.name] = file_hash(f); write_json(self.p / "child-0/manifest.json", manifest)
        self.authorize()
        with self.assertRaises((InvalidInput, InvalidProof)): self.inspect()


if __name__ == "__main__":
    unittest.main()
