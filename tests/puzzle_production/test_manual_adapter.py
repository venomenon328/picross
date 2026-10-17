"""Fixed synthetic manual-source contracts; never load the production fundus."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import Budget, InvalidInput, InvalidProof, digest, load_json, validate_logic, write_json
from tools.puzzle_production.images import file_hash, logic_from_matrix
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify
from tools.puzzle_production.target_adapter import export, inspect, verify_export, MANUAL_FORMAT
from tools.puzzle_production.za1_fixtures import rated_registration as registration
from tools.puzzle_production.content_registry import check_checkout
from tools.puzzle_production.za1_fixtures import FIXTURES, ROOT, approve, seal, isolated_checkout


class ManualAdapterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.package = self.root / "package"
        shutil.copytree(FIXTURES / "direct-mono", self.package)
        p = self.package
        h = load_json(p / "handoff.json")
        reference = load_json(p / "production/import/area-candidate.json")
        before = reference["matrix"]
        matrix = deepcopy(before)
        matrix[1][0] = "empty"
        edit = {"x": 0, "y": 1, "before": "ink", "after": "empty"}
        mask = [[True] * 6 for _ in range(4)]
        mask[1][0] = False
        plan = {"format": "picross-manual-edit-plan-v1", "puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "reference": {"candidate_id": reference["id"], "variant": "area", "bundle": "production/import",
                          "manifest_sha256": file_hash(p / "production/import/manifest.json"), "matrix_hash": digest(before)},
            "authorization": "evidence.txt", "coordinates": "zero based x/y", "edits_in_requested_order": [edit],
            "mask": mask, "budgets": {"max_changes": 1, "max_steps": 1, "max_candidates": 1,
                "solve_seconds": 30, "solve_lines": 100000, "verify_seconds": 30, "verify_lines": 100000},
            "operators": ["remove-ink-only"], "seed": None, "randomness": "none", "rationale": "TEST ONLY fixed edge edit",
            "tool_boundary": "Synthetic manual derivation; not a search"}
        write_json(p / "manual/plan.json", plan)
        logic = logic_from_matrix(matrix, reference["design"])
        proof = solve(validate_logic(logic), Budget())
        self.assertEqual(proof["status"], "solved")
        write_json(p / "manual/logic.json", logic)
        write_json(p / "manual/certificate/proof.json", proof)
        result = verify(validate_logic(logic), proof, Budget())
        result["format"] = "picross-result-v1"
        write_json(p / "manual/certificate/result.json", result)
        raw = {"format": "picross-manual-candidate-v1", "puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "variant": "manual-edge", "source_type": "manual", "matrix": matrix, "matrix_hash": digest(matrix),
            "logic_hash": digest(logic), "design": reference["design"], "plan_sha256": file_hash(p / "manual/plan.json"),
            "source_candidate_id": reference["id"], "history": [{"edit": edit, "parent_matrix_hash": digest(before), "matrix_hash": digest(matrix)}],
            "changes": [edit], "claim": "TEST ONLY"}
        write_json(p / "manual/candidate.json", raw)
        h.update(state="raster_review", content_blockers=["Manual source awaits explicit owner authorization"],
            candidate={"source_type": "manual", "bundle": "manual", "candidate": "manual/candidate.json", "variant": "manual-edge",
                "proof": "manual/certificate/proof.json", "matrix_hash": digest(matrix), "logic_hash": digest(logic)},
            repair={"type": "manual", "reference": "production/import", "reference_variant": "area", "plan": "manual/plan.json", "changes": 1})
        difficulty = load_json(p / "difficulty.json")
        difficulty["logic_hash"] = digest(logic)
        write_json(p / "difficulty.json", difficulty)
        seal(p, h)
        self.authorize()

    def authorize(self):
        p = self.package
        h = load_json(p / "handoff.json")
        seal(p, h)
        h = load_json(p / "handoff.json")
        self.approval = self.root / "approval.json"
        approve(p, self.approval)
        selection = load_json(self.approval)["selection"]
        owner = {"format": "picross-owner-override-v1", "actor": "TEST ONLY", "statement": "Synthetic owner authorization",
            "timestamp_utc": "2026-10-13T00:00:00Z", "puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "package_sha256": None, "handoff_sha256": file_hash(p / "handoff.json"),
            "inventory_sha256": h["inventory"]["sha256"], "selection": selection, "approval_sha256": file_hash(self.approval)}
        write_json(self.root / "owner-override.json", owner)
        self.auth = self.root / "manual-authorization.json"
        write_json(self.auth, {"format": "picross-manual-authorization-v1", "puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "original_zip_sha256": None, "handoff_sha256": file_hash(p / "handoff.json"),
            "inventory_sha256": h["inventory"]["sha256"], "selection": selection,
            "plan_sha256": file_hash(p / "manual/plan.json"), "owner_override": {"file": "owner-override.json", "sha256": file_hash(self.root / "owner-override.json")},
            "superseded_content_blockers": h["content_blockers"]})

    def inspect(self):
        with open_package(self.package, allow_manual_review=True) as package:
            return inspect(package, self.approval, manual_authorization=self.auth)[0]

    def export(self):
        out = self.root / "export"
        export(self.package, out, name="TEST ONLY", revision=1, stem="manual_test", save_slot="manual_test",
               approval_path=self.approval, manual_authorization=self.auth, category_id="voegel",
               categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        return out

    def test_export_offline_recheck_plan_and_synthetic_registration(self):
        original_handoff = (self.package / "handoff.json").read_bytes()
        out = self.export()
        m, report = verify_export(out)
        self.assertEqual(m["format"], MANUAL_FORMAT)
        self.assertTrue(report["technical"] and report["catalog_ready"])
        self.assertEqual(report["source"]["kind"], "manual")
        self.assertEqual((out / "input/handoff.json").read_bytes(), original_handoff)
        self.assertEqual(file_hash(out / m["reveal"]), report["selection"]["reveal"]["sha256"])
        checkout = isolated_checkout(self.root / "checkout")
        before = (checkout / "content/registry.json").read_bytes()
        self.assertEqual(registration(out, checkout)["status"], "planned")
        self.assertEqual((checkout / "content/registry.json").read_bytes(), before)
        self.assertEqual(registration(out, checkout, apply=True)["status"], "registered")
        self.assertEqual(registration(out, checkout, apply=True)["status"], "no-op")
        check_checkout(checkout, replay=True)

    def test_manual_source_needs_explicit_exact_authorization(self):
        with self.assertRaises(InvalidInput), open_package(self.package):
            pass
        with open_package(self.package, allow_manual_review=True) as p, self.assertRaises(InvalidInput):
            inspect(p, self.approval)
        for field, value in [("selection", {}), ("handoff_sha256", "0"*64), ("plan_sha256", "0"*64),
                             ("superseded_content_blockers", [])]:
            self.authorize()
            a = load_json(self.auth)
            a[field] = value
            write_json(self.auth, a)
            with self.subTest(field=field), self.assertRaises(InvalidInput):
                self.inspect()

    def test_fully_rebound_metadata_cannot_hide_protected_cell_or_bad_proof(self):
        plan_path = self.package / "manual/plan.json"
        original = load_json(plan_path)
        for kind in ("protected", "unprotected-extra", "bad-proof"):
            plan = deepcopy(original)
            if kind == "protected": plan["mask"][1][0] = True
            if kind == "unprotected-extra": plan["mask"][2][0] = False
            write_json(plan_path, plan)
            raw = load_json(self.package / "manual/candidate.json")
            raw["plan_sha256"] = file_hash(plan_path)
            write_json(self.package / "manual/candidate.json", raw)
            if kind == "bad-proof":
                proof = load_json(self.package / "manual/certificate/proof.json")
                proof["logic_hash"] = "0"*64
                write_json(self.package / "manual/certificate/proof.json", proof)
            self.authorize()
            with self.subTest(kind=kind), self.assertRaises((InvalidInput, InvalidProof)):
                self.inspect()

    def test_authorization_does_not_waive_hard_gates_or_final_approval(self):
        h = load_json(self.package / "handoff.json")
        h["gates"]["provenance"] = "fail"
        write_json(self.package / "handoff.json", h)
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "Unresolved content gate"):
            self.inspect()
        h["gates"]["provenance"] = "pass"
        write_json(self.package / "handoff.json", h)
        self.authorize()
        a = load_json(self.approval); a["selection"]["matrix_hash"] = "0"*64
        write_json(self.approval, a)
        with self.assertRaises(InvalidInput):
            self.inspect()

    def test_cli_inspect_export_verify_and_plan(self):
        out = self.root / "cli-export"
        checkout = isolated_checkout(self.root / "checkout")
        common = ["--input", str(self.package), "--approval", str(self.approval), "--manual-authorization", str(self.auth)]
        calls = [("inspect", common), ("export", common + ["--name", "TEST ONLY", "--runtime-revision", "1", "--stem", "manual_cli",
                  "--save-slot", "manual_cli", "--category-id", "voegel", "--categories", str(checkout / "content/categories.json"), "--output-dir", str(out)]),
                 ("verify-export", ["--export", str(out)]), ("plan", ["--export", str(out), "--checkout", str(checkout)])]
        for command, args in calls:
            if command == "plan":
                from tools.puzzle_production.za1_fixtures import difficulty_for_export
                checked = self.root / "checked.json"
                write_json(checked,difficulty_for_export(out))
                args += ["--difficulty",str(checked)]
            run = subprocess.run([sys.executable, "-B", "-m", "tools.puzzle_production.target_adapter", command, *args],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_rehashed_export_cannot_forge_runtime_matrix(self):
        out = self.export(); m = load_json(out / "manifest.json")
        data = load_json(out / m["definition"])
        data["solution"][0][0] = 1
        write_json(out / m["definition"], data)
        m["files"][m["definition"]] = file_hash(out / m["definition"])
        write_json(out / "manifest.json", m)
        with self.assertRaises(InvalidInput): verify_export(out)

    def test_owner_evidence_and_completed_production_are_required(self):
        owner_path = self.root / "owner-override.json"
        owner = load_json(owner_path)
        owner["approval_sha256"] = "0" * 64
        write_json(owner_path, owner)
        a = load_json(self.auth); a["owner_override"]["sha256"] = file_hash(owner_path)
        write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "final approval"):
            self.inspect()
        self.authorize()
        result_path = self.package / "manual/certificate/result.json"
        result = load_json(result_path); result.update(status="aborted", certified=False)
        write_json(result_path, result)
        self.authorize()
        with self.assertRaisesRegex(InvalidInput, "not completed"):
            self.inspect()


if __name__ == "__main__":
    unittest.main()
