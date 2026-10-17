"""Fixed synthetic ambiguous inputs; no real production puzzle data."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, InvalidProof, digest, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, raster_image
from tools.puzzle_production.target_adapter import export, inspect, verify_export
from tools.puzzle_production.za1_fixtures import rated_registration as registration
from tools.puzzle_production.za1_fixtures import ROOT, make, seal, approve, isolated_checkout


class StalledColorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.p = self.root / "input"
        make(self.p, "pz-test-stalled-color", 4, 3, "color", colors=4)

    def prepare(self, paired=False, after="green"):
        p = self.p
        h, d = load_json(p / "handoff.json"), load_json(p / "design.json")
        matrix = [["green", "empty", "empty", "empty"],
                  ["empty", "green", "empty", "empty"],
                  ["red", "blue", "gold", "empty"]]
        config = {"profile": "paired-lines-color", "max_pair_work": 20000000, "max_pair_records": 250000}
        kwargs = {"profile": config["profile"]} if paired else {}
        raster_image(matrix, d).save(p / "motifs/source.png")
        import_image(p / "motifs/source.png", p / "design.json", p / "stalled-base", **kwargs)
        base = load_json(p / "stalled-base/area-candidate.json")
        self.assertEqual(load_json(p / "stalled-base/area-result.json")["status"], "stalled")
        edited = deepcopy(matrix)
        y, x, value = (2, 1, "red") if after == "ambiguous" else (0, 1, after)
        edited[y][x] = value
        raster_image(edited, d).save(p / "corrected.png")
        import_image(p / "corrected.png", p / "design.json", p / "corrected", **kwargs)
        child = load_json(p / "corrected/area-candidate.json")
        plan = {"format": "picross-editorial-fixed-cell-plan-v2" if paired else "picross-editorial-fixed-cell-plan-v1",
                "puzzle_id": h["puzzle_id"], "revision": h["revision"], "reference_matrix_hash": digest(matrix),
                "reference": {"bundle": "stalled-base", "variant": "area", "candidate_id": base["id"],
                              "manifest_sha256": file_hash(p / "stalled-base/manifest.json")},
                "max_changes": 1, "search": False, "seed": None, "solve_seconds": 30, "verify_seconds": 30,
                "max_lines": 100000, "protected": [[(r, s) != (y, x) for s in range(4)] for r in range(3)],
                "edits": [{"row": y + 1, "column": x + 1, "before": matrix[y][x], "after": value}]}
        if paired:
            plan["certification"] = config
        write_json(p / "fixed-plan.json", plan)
        write_json(p / "fixed-record.json", {"format": "picross-editorial-fixed-cell-derivation-v2" if paired else "picross-editorial-fixed-cell-derivation-v1",
                   "plan": "fixed-plan.json", "reference_matrix_hash": digest(matrix), "matrix_hash": digest(edited),
                   "actual_changed_positions": 1, "search": False, "seed": None, "edits": plan["edits"]})
        h.update(state="raster_review", blockers=[],
                 candidate={"source_type": "manual", "bundle": "corrected", "variant": "area", "proof": "corrected/area-proof.json",
                            "matrix_hash": digest(edited), "logic_hash": child["logic_hash"]},
                 repair={"type": "fixed_color_editorial_redraw", "reference": "stalled-base", "reference_variant": "area",
                         "plan": "fixed-plan.json", "record": "fixed-record.json"})
        h["motif"].update(sha256=file_hash(p / "motifs/source.png"), revision="test-stalled")
        approval = load_json(p / "motif-approval.json")
        approval.update(sha256=h["motif"]["sha256"])
        write_json(p / "motif-approval.json", approval)
        provenance = load_json(p / "motifs/source.provenance.json")
        provenance["sha256"] = h["motif"]["sha256"]
        write_json(p / "motifs/source.provenance.json", provenance)
        difficulty = load_json(p / "difficulty.json")
        difficulty["logic_hash"] = child["logic_hash"]
        if paired:
            h["candidate"]["certification"] = config
            evidence = p / "rulebook.md"
            evidence.write_text("**Version 0.5.0 · synthetic test**\nSynthetic paired test input.\n", encoding="utf-8")
            h["rulebook"] = {"version": "0.5.0", "file": "rulebook.md", "sha256": file_hash(evidence)}
            difficulty.update(method="picross-difficulty-0.2", profile_hash=load_json(p / "corrected/area-proof.json")["profile_hash"],
                              evidence="corrected/area-assessment.json")
        write_json(p / "difficulty.json", difficulty)
        self.base = {"source_type": "import", "bundle": "stalled-base", "variant": "area", "reference_bundle": None,
                     "reference_variant": None, "matrix_hash": digest(matrix)}
        self.steps = [{"record": {"file": "fixed-record.json", "sha256": file_hash(p / "fixed-record.json")},
                       "plan": {"file": "fixed-plan.json", "sha256": file_hash(p / "fixed-plan.json")},
                       "output": {"bundle": "corrected", "variant": "area"}, "protected": plan["protected"]}]
        seal(p, h)
        self.authorize()

    def authorize(self, version=5, permissions=None):
        p = self.p
        h = load_json(p / "handoff.json")
        seal(p, h)
        self.approval = self.root / "approval.json"
        approve(p, self.approval)
        common = {"puzzle_id": h["puzzle_id"], "revision": h["revision"], "handoff_sha256": file_hash(p / "handoff.json"),
                  "inventory_sha256": h["inventory"]["sha256"], "selection": load_json(self.approval)["selection"],
                  "superseded_content_blockers": [], "base": self.base, "steps": self.steps,
                  "approved_motif": {**{k: h["motif"][k] for k in ("file", "sha256", "derived_from_reveal_sha256", "revision")},
                     "parameters": h["approved_parameters"][0],
                     "approval": {"file": "motif-approval.json", "sha256": file_hash(p / "motif-approval.json")}}}
        owner = {**common, "format": f"picross-owner-override-v{version}", "actor": "TEST ONLY",
                 "statement": "Synthetic stalled-base fixed correction, not a human approval", "timestamp_utc": "2026-10-15T00:00:00Z",
                 "package_sha256": None, "approval_sha256": file_hash(self.approval),
                 "permissions": permissions if permissions is not None else {"fixed_color_edits": True, **({"stalled_color_base": True} if version == 5 else {})}}
        write_json(self.root / "owner-override.json", owner)
        self.auth = self.root / "authorization.json"
        write_json(self.auth, {**common, "format": f"picross-manual-authorization-v{version}", "original_zip_sha256": None,
                              "owner_override": {"file": "owner-override.json", "sha256": file_hash(self.root / "owner-override.json")}})

    def inspect(self, approval=True):
        with open_package(self.p, allow_manual_review=True) as p:
            return inspect(p, self.approval if approval else None, manual_authorization=self.auth)[0]

    def test_ambiguous_base_fixed_correction_exports_and_registers(self):
        self.prepare()
        out = self.root / "export"
        export(self.p, out, name="TEST ONLY", revision=1, stem="stalled_color", save_slot="stalled_color",
               approval_path=self.approval, manual_authorization=self.auth, category_id="voegel",
               categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        _, report = verify_export(out)
        self.assertEqual(report["source"]["base_deduction"], {"status": "stalled", "proof_verified": True, "certified": False})
        self.assertTrue(report["technical"] and report["catalog_ready"])
        self.assertEqual(report["source"]["changed_cells"], 1)
        self.assertEqual(registration(out, isolated_checkout(self.root / "checkout"), apply=True)["status"], "registered")

    def test_paired_base_requires_both_independent_fixed_points(self):
        self.prepare(paired=True)
        report = self.inspect()
        self.assertTrue(report["technical"])
        self.assertEqual(report["deduction"]["profile"]["id"], "paired-lines-color")
        directory = self.p / "stalled-base"
        baseline = load_json(directory / "area-baseline-proof.json")
        baseline.update(status="aborted", reason="work_limit")
        write_json(directory / "area-baseline-proof.json", baseline)
        assessment = load_json(directory / "area-assessment.json")
        assessment.update(baseline_status="aborted", baseline_sha256=file_hash(directory / "area-baseline-proof.json"))
        write_json(directory / "area-assessment.json", assessment)
        manifest = load_json(directory / "manifest.json")
        for name in ("area-baseline-proof.json", "area-assessment.json"):
            manifest["files"][name] = file_hash(directory / name)
        write_json(directory / "manifest.json", manifest)
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "verified original line fixed point"):
            self.inspect()

    def test_v4_does_not_accept_stalled_base(self):
        self.prepare()
        self.authorize(version=4)
        with self.assertRaisesRegex(InvalidInput, "base certificate incomplete"):
            self.inspect()

    def test_permission_and_final_approval_are_required(self):
        self.prepare()
        with self.assertRaisesRegex(InvalidInput, "requires bound final approval"):
            self.inspect(False)
        for value in (False, 1):
            self.authorize(permissions={"fixed_color_edits": True, "stalled_color_base": value})
            with self.subTest(value=value), self.assertRaisesRegex(InvalidInput, "permission scope"):
                self.inspect()
        self.authorize(permissions={"fixed_color_edits": True})
        with self.assertRaises(InvalidInput):
            self.inspect()

    def test_forged_base_flags_and_non_solved_child_are_rejected(self):
        self.prepare(after="ambiguous")
        with self.assertRaises(InvalidInput):
            self.inspect()
        path = self.p / "stalled-base/area-result.json"
        result = load_json(path)
        result.update(status="aborted", certified=False)
        write_json(path, result)
        manifest = load_json(self.p / "stalled-base/manifest.json")
        manifest["files"][path.name] = file_hash(path)
        write_json(self.p / "stalled-base/manifest.json", manifest)
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "verified original stalled"):
            self.inspect()

    def test_rebound_mask_and_invalid_parent_proof_remain_rejected(self):
        self.prepare()
        plan = load_json(self.p / "fixed-plan.json")
        original_plan = deepcopy(plan)
        plan["protected"][2][3] = False
        write_json(self.p / "fixed-plan.json", plan)
        self.steps[0]["plan"]["sha256"] = file_hash(self.p / "fixed-plan.json")
        self.authorize()
        with self.assertRaises(InvalidInput):
            self.inspect()
        write_json(self.p / "fixed-plan.json", original_plan)
        self.steps[0]["plan"]["sha256"] = file_hash(self.p / "fixed-plan.json")
        proof = load_json(self.p / "stalled-base/area-proof.json")
        proof["status"] = "solved"
        write_json(self.p / "stalled-base/area-proof.json", proof)
        manifest = load_json(self.p / "stalled-base/manifest.json")
        manifest["files"]["area-proof.json"] = file_hash(self.p / "stalled-base/area-proof.json")
        write_json(self.p / "stalled-base/manifest.json", manifest)
        self.authorize()
        with self.assertRaises((InvalidInput, InvalidProof)):
            self.inspect()
