"""Synthetic B/C import, repair, authoring, export and registration boundaries."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tools.puzzle_production import certification, repair, target_adapter
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import Budget, InvalidInput, InvalidProof, digest, load_json, validate_logic, write_json
from tools.puzzle_production.images import import_image, inspect_candidate, file_hash, raster_image, logic_from_matrix
from tools.puzzle_production.za1_fixtures import make, seal, approve, isolated_checkout, ROOT
from tools.puzzle_production.content_registry import registration, check_checkout
from test_paired import MONO, COLOR, wire


def rulebook(root, h):
    # An explicit synthetic snapshot, never an owner approval or old snapshot relabel.
    (root / "rulebook.md").write_text("# Synthetic technical rulebook fixture\n\n**Version 0.5.0 · TEST ONLY**\n", encoding="utf-8")
    h["rulebook"] = {"version": "0.5.0", "file": "rulebook.md", "sha256": file_hash(root / "rulebook.md")}


def difficulty(root, h, proof_path):
    proof = load_json(root / proof_path)
    evidence = proof_path.removesuffix("proof.json") + "assessment.json"
    a = load_json(root / evidence)
    config = {"profile": proof["profile"]["id"], "max_pair_work": 20_000_000, "max_pair_records": 250_000}
    h["candidate"]["certification"] = config
    write_json(root / "difficulty.json", {"method": "picross-difficulty-0.2", "logic_hash": proof["logic_hash"],
        "profile_hash": proof["profile_hash"], "assessment_type": "instrumented" if a["r4_required"] else "editorial_estimate",
        "confidence": "medium" if a["r4_required"] else "low", "level": "L5" if a["r4_required"] else "L1",
        "plausible_range": ["L5", "L5"] if a["r4_required"] else ["L1", "L2"],
        "rule_families": {"R4": "Independently verified line fixpoint and complete pair proof"} if a["r4_required"] else
                         {"R0": "Synthetic full runs; no R4 necessity claimed"},
        "logical_demand": certification.LABEL if a["r4_required"] else None, "evidence": evidence, "time_estimate": None})
    return config


def package(root, color=False, repaired=False):
    matrix = COLOR if color else MONO
    make(root, "pz-test-paired", len(matrix[0]), len(matrix), "color" if color else "mono")
    h = load_json(root / "handoff.json")
    d = load_json(root / "design.json")
    raster_image(matrix, d).save(root / "motifs/source.png")
    sha = file_hash(root / "motifs/source.png")
    h["motif"]["sha256"] = sha
    for path in ("motif-approval.json", "motifs/source.provenance.json"):
        obj = load_json(root / path)
        obj["sha256"] = sha
        write_json(root / path, obj)
    profile = "paired-lines-color" if color else "paired-lines-mono"
    bundle = root / "paired-import"
    import_image(root / "motifs/source.png", root / "design.json", bundle, profile=None if repaired else profile)
    c = load_json(bundle / "area-candidate.json")
    h["candidate"].update(bundle="paired-import", proof="paired-import/area-proof.json",
                           matrix_hash=digest(matrix), logic_hash=c["logic_hash"])
    if repaired:
        config = certification.configuration(validate_logic(wire(matrix, ("blue", "red") if color else ("ink",))), profile)
        plan = {"format": "picross-repair-plan-v2", "tool": "rp5-single-cell-2", "certification": config,
            "reference": {"candidate_id": c["id"], "manifest_sha256": file_hash(bundle / "manifest.json"), "variant": "area"},
            "mask": [[True] * len(matrix[0]) for _ in matrix], "rationale": "Fixed technical paired recertification",
            "config": {"max_changes": 0, "max_steps": 0, "max_candidates": 1, "search_seconds": 30,
                "final_seconds": 30, "search_lines": 100000, "final_lines": 100000,
                "seed": 39, "operators": ["single-cell"], "order": "seeded-frontier-v1"}}
        write_json(root / "plan.json", plan)
        repair.search(bundle, plan, root / "paired-repair")
        r = load_json(root / "paired-repair/repair.json")
        h["candidate"].update(bundle="paired-repair", proof="paired-repair/final-proof.json",
            source_type="repair", repair_id=r["id"], parent_variant="area", variant="candidate-000")
        h["repair"] = {"reference": "paired-import", "reference_variant": "area", "plan": "plan.json"}
    rulebook(root, h)
    difficulty(root, h, h["candidate"]["proof"])
    seal(root, h)
    return h


class PairedProductionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def export_and_register(self, p, name="run", auth=None, approval=None):
        approval = approval or self.root / (name + "-approval.json")
        if not approval.exists():
            approve(p, approval)
        out = self.root / (name + "-export")
        target_adapter.export(p, out, name="TEST ONLY", revision=1, stem="paired_test", save_slot="paired_test",
            approval_path=approval, manual_authorization=auth, category_id="voegel",
            categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        manifest, report = target_adapter.verify_export(out)
        self.assertEqual(manifest["format"], "picross-target-export-v4")
        self.assertTrue(report["technical"] and report["catalog_ready"])
        self.assertIn("paired_verifier.py", report["tool"]["modules"])
        checkout = isolated_checkout(self.root / (name + "-checkout"))
        before = (checkout / "content/registry.json").read_bytes()
        self.assertEqual(registration(out, checkout)["status"], "planned")
        self.assertEqual((checkout / "content/registry.json").read_bytes(), before)
        self.assertEqual(registration(out, checkout, apply=True)["status"], "registered")
        check_checkout(checkout, replay=True)
        return out, report

    def test_import_repair_export_and_registration_mono_color(self):
        for color, repaired in ((False, False), (True, False), (False, True), (True, True)):
            name = f"{color}-{repaired}"
            p = self.root / name
            package(p, color, repaired)
            with open_package(p) as opened:
                report = target_adapter.inspect(opened)[0]
            self.assertTrue(report["technical"])
            self.assertFalse(report["editorial_approved"])
            self.assertTrue(report["deduction"]["assessment"]["r4_required"])
            with self.assertRaisesRegex(InvalidInput, "final_editorial"):
                target_adapter.export(p, self.root / "blocked", name="TEST", revision=1, stem="test", save_slot="test")
            _, report = self.export_and_register(p, name)
            self.assertEqual(report["difficulty"]["level"], "L5")

    def test_false_necessity_old_rulebook_and_profile_downgrades(self):
        p = self.root / "package"
        h = package(p, True)
        original = load_json(p / "difficulty.json")
        for mutate in (lambda d: d.update(method="picross-difficulty-0.1"),
                       lambda d: d.update(level="L4", plausible_range=["L4", "L5"]),
                       lambda d: d.update(profile_hash="0" * 64),
                       lambda d: d.update(evidence="evidence.txt"),
                       lambda d: d.update(rule_families={"R3": "No necessary pairs"})):
            d = deepcopy(original)
            mutate(d)
            write_json(p / "difficulty.json", d)
            seal(p, h)
            with open_package(p) as opened, self.assertRaises(InvalidInput):
                target_adapter.inspect(opened)
        write_json(p / "difficulty.json", original)
        h["rulebook"]["version"] = "0.4.1"
        seal(p, h)
        with open_package(p) as opened, self.assertRaisesRegex(InvalidInput, "0.5.0"):
            target_adapter.inspect(opened)
        h["rulebook"]["version"] = "0.5.0"
        (p / "rulebook.md").write_text("**Version 0.4.1**\n", encoding="utf-8")
        h["rulebook"]["sha256"] = file_hash(p / "rulebook.md")
        seal(p, h)
        with self.assertRaisesRegex(InvalidInput, "snapshot"), open_package(p):
            pass

    def test_file_bound_baseline_and_assessment_rejection(self):
        p = self.root / "package"
        package(p)
        bundle = p / "paired-import"
        for name, mutate in (("area-assessment.json", lambda a: a.update(r4_required=False)),
                              ("area-baseline-proof.json", lambda a: a.update(status="aborted", reason="work_limit"))):
            original = load_json(bundle / name)
            a = deepcopy(original)
            mutate(a)
            write_json(bundle / name, a)
            manifest = load_json(bundle / "manifest.json")
            manifest["files"][name] = file_hash(bundle / name)
            write_json(bundle / "manifest.json", manifest)
            with self.assertRaises((InvalidInput, InvalidProof)):
                inspect_candidate(bundle, "area")
            write_json(bundle / name, original)
            manifest["files"][name] = file_hash(bundle / name)
            write_json(bundle / "manifest.json", manifest)
        m = load_json(bundle / "manifest.json")
        m["format"] = "picross-image-manifest-v1"
        del m["certification"]
        for suffix in ("baseline-proof", "assessment"):
            del m["files"][f"area-{suffix}.json"]
        write_json(bundle / "manifest.json", m)
        with self.assertRaisesRegex(InvalidInput, "Legacy"):
            inspect_candidate(bundle, "area")

    def test_paired_repair_actual_edit_cumulative_budget_and_final_abort(self):
        from test_repair import fixture
        reference, plan, _, _ = fixture(self.root)
        plan.update(format="picross-repair-plan-v2", tool="rp5-single-cell-2",
                    certification={"profile": "paired-lines-mono", "max_pair_work": 20000000, "max_pair_records": 250000})
        out = self.root / "repair"
        result = repair.search(reference, plan, out)
        self.assertTrue(result["certified"])
        self.assertEqual(result["candidates"], 2)
        self.assertTrue(repair.inspect_repair(out, reference)["certified"])
        plan["config"]["final_lines"] = 0
        out = self.root / "aborted-repair"
        result = repair.search(reference, plan, out)
        self.assertEqual(result["status"], "aborted")
        self.assertFalse(repair.inspect_repair(out, reference)["certified"])

    def test_new_profile_alone_does_not_grant_r4(self):
        p = validate_logic(wire([["ink", "ink"], ["ink", "ink"]]))
        cfg = certification.configuration(p, "paired-lines-mono")
        _, result = certification.produce(p, self.root, "", cfg, Budget())
        self.assertTrue(result["certified"])
        self.assertFalse(result["assessment"]["r4_required"])
        self.assertIsNone(result["assessment"]["level"])
        _, checked = certification.inspect(p, self.root, "", cfg)
        self.assertEqual(checked["assessment"]["outcome"], "line_logic_solved")
        # An actual valid pair step still does not prove that pairs were necessary.
        proof = load_json(self.root / "proof.json")
        proof["steps"] = [{"kind": "pair", "axis": "row", "indices": [0, 1], "changes": [
            {"row": y, "column": x, "before": ["empty", "ink"], "after": ["ink"]}
            for y in range(2) for x in range(2)]}]
        write_json(self.root / "proof.json", proof)
        report = load_json(self.root / "assessment.json")
        report["proof_sha256"] = file_hash(self.root / "proof.json")
        write_json(self.root / "assessment.json", report)
        self.assertFalse(certification.inspect(p, self.root, "", cfg)[1]["assessment"]["r4_required"])

    def test_configured_inner_budget_and_aborted_baseline_never_grant_r4(self):
        from tools.puzzle_production.solver import solve
        p = validate_logic(wire(MONO))
        cfg = certification.configuration(p, "paired-lines-mono", 0)
        proof, checked = certification.produce(p, self.root, "limited-", cfg, Budget())
        self.assertEqual(proof["status"], "aborted")
        self.assertFalse(checked["assessment"]["r4_required"])
        cfg = certification.configuration(p, "paired-lines-mono")
        proof, checked = certification.produce(p, self.root, "complete-", cfg, Budget())
        baseline = solve(p, Budget(max_lines=0))
        write_json(self.root / "complete-baseline-proof.json", baseline)
        report = certification.assessment(p, proof, baseline, file_hash(self.root / "complete-proof.json"),
                                          file_hash(self.root / "complete-baseline-proof.json"), True, True)
        write_json(self.root / "complete-assessment.json", report)
        checked = certification.inspect(p, self.root, "complete-", cfg)[1]
        self.assertTrue(checked["certified"])
        self.assertEqual(checked["assessment"]["outcome"], "complete_deduction_without_necessity")
        self.assertFalse(checked["assessment"]["r4_required"])

    def test_paired_reference_cannot_enter_legacy_repair_plan(self):
        from test_repair import fixture
        reference, plan, _, _ = fixture(self.root)
        paired_reference = self.root / "paired-reference"
        import_image(reference / "original.png", reference / "design.json", paired_reference,
                     profile="paired-lines-mono")
        candidate = load_json(paired_reference / (plan["reference"]["variant"] + "-candidate.json"))
        plan["reference"].update(candidate_id=candidate["id"],
                                 manifest_sha256=file_hash(paired_reference / "manifest.json"))
        with self.assertRaisesRegex(InvalidInput, "Paired reference"):
            repair.search(paired_reference, plan, self.root / "forbidden-repair")

    def test_quality_report_keeps_diagnosis_deduction_and_difficulty_separate(self):
        from tools.puzzle_production.quality import assess
        from tools.puzzle_production.diagnosis import diagnose_file, DiagnosisBudget
        from tools.puzzle_production.solver import solve
        input_path, proof_path = self.root / "logic.json", self.root / "line.json"
        p = validate_logic(wire(MONO))
        write_json(input_path, p.to_wire())
        write_json(proof_path, solve(p))
        diagnose_file(input_path, self.root / "unique", DiagnosisBudget())
        report = assess(input_path, proof_path, diagnosis_dir=self.root / "unique")
        self.assertEqual(report["classification"], "reported_unique_without_complete_deduction")
        self.assertFalse(report["diagnosis"]["search_replayed"])
        self.assertIsNone(report["difficulty"]["level"])
        diagnose_file(input_path, self.root / "unknown", DiagnosisBudget(max_nodes=0))
        self.assertEqual(assess(input_path, proof_path, diagnosis_dir=self.root / "unknown")["classification"], "diagnosis_incomplete")
        cfg = certification.configuration(p, "paired-lines-mono")
        certification.produce(p, self.root, "pair-", cfg, Budget())
        report = assess(input_path, self.root / "pair-proof.json", baseline_path=proof_path)
        self.assertEqual(report["classification"], "paired_lines_solved")
        self.assertTrue(report["difficulty"]["r4_required"])
        # Absence of a separately checked weak fixpoint never means necessity.
        self.assertFalse(assess(input_path, self.root / "pair-proof.json")["difficulty"]["r4_required"])
        p = validate_logic(wire([["ink", "empty"], ["empty", "ink"]]))
        write_json(input_path, p.to_wire())
        write_json(proof_path, solve(p))
        diagnose_file(input_path, self.root / "multiple", DiagnosisBudget())
        self.assertEqual(assess(input_path, proof_path, diagnosis_dir=self.root / "multiple")["classification"], "multiple")
        p = validate_logic(wire([["ink", "ink"]]))
        write_json(input_path, p.to_wire())
        write_json(proof_path, solve(p))
        self.assertEqual(assess(input_path, proof_path)["classification"], "line_logic_solved")

    def test_cli_new_profile_and_fresh_verifier_process(self):
        input_path = self.root / "logic.json"
        write_json(input_path, wire(COLOR, ("blue", "red")))
        command = [sys.executable, "-m", "tools.puzzle_production"]
        out = self.root / "certificate"
        run = subprocess.run(command + ["solve", "--input", str(input_path), "--profile", "paired-lines-color",
                             "--output-dir", str(out)], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        fresh = subprocess.run(command + ["verify", "--input", str(input_path), "--proof", str(out / "proof.json")],
                               capture_output=True, text=True, timeout=30)
        self.assertEqual(fresh.returncode, 0, fresh.stdout + fresh.stderr)

    def test_fixed_manual_removal_with_new_bound_certificate(self):
        from test_manual_adapter import ManualAdapterTests
        case = ManualAdapterTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        p = case.package
        h = load_json(p / "handoff.json")
        puzzle = validate_logic(load_json(p / "manual/logic.json"))
        cfg = certification.configuration(puzzle, "paired-lines-mono")
        _, checked = certification.produce(puzzle, p / "manual/certificate", "", cfg, Budget())
        checked["format"] = "picross-result-v1"
        write_json(p / "manual/certificate/result.json", checked)
        plan = load_json(p / "manual/plan.json")
        plan.update(format="picross-manual-edit-plan-v2", certification=cfg)
        write_json(p / "manual/plan.json", plan)
        raw = load_json(p / "manual/candidate.json")
        raw.update(format="picross-manual-candidate-v2", plan_sha256=file_hash(p / "manual/plan.json"))
        write_json(p / "manual/candidate.json", raw)
        rulebook(p, h)
        difficulty(p, h, h["candidate"]["proof"])
        seal(p, h)
        case.authorize()
        _, report = self.export_and_register(p, "manual", case.auth, case.approval)
        self.assertFalse(report["deduction"]["assessment"]["r4_required"])
        d = load_json(p / "difficulty.json")
        d["rule_families"]["R4"] = "Unjustified use of a stronger solver"
        write_json(p / "difficulty.json", d)
        seal(p, h)
        case.authorize()
        with self.assertRaisesRegex(InvalidInput, "necessity"):
            case.inspect()

    def test_fixed_edited_import_preserves_explicit_frame_exception(self):
        from test_edited_import_adapter import EditedImportAdapterTests
        case = EditedImportAdapterTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        p = case.package
        import_image(p / "edited-source.png", p / "production/import/design.json", p / "paired-edited",
                     profile="paired-lines-mono")
        h = load_json(p / "handoff.json")
        h["candidate"].update(bundle="paired-edited", proof="paired-edited/area-proof.json")
        rulebook(p, h)
        cfg = difficulty(p, h, h["candidate"]["proof"])
        plan = load_json(p / "edit-record.json")
        plan.update(format="picross-fixed-mono-import-plan-v2", certification=cfg)
        write_json(p / "edit-record.json", plan)
        seal(p, h)
        case.authorize()
        _, report = self.export_and_register(p, "edited", case.auth, case.approval)
        self.assertTrue(report["frame_exception_accepted"])
        self.assertFalse(report["frame_valid"])

    def test_fixed_color_chain_and_approved_motif_profiles(self):
        from test_color_derivation_adapter import ColorDerivationTests
        from test_approved_color_adapter import ApprovedColorTests
        for cls in (ColorDerivationTests, ApprovedColorTests):
            case = cls()
            case.setUp()
            self.addCleanup(case.doCleanups)
            p = case.p
            h = load_json(p / "handoff.json")
            rulebook(p, h)
            for i in range(2):
                import_image(p / f"source-{i}.png", p / "design.json", p / f"paired-child-{i}", profile="paired-lines-color")
                plan = load_json(p / f"plan-{i}.json")
                cfg = {"profile": "paired-lines-color", "max_pair_work": 20000000, "max_pair_records": 250000}
                plan.update(format="picross-editorial-fixed-cell-plan-v2", certification=cfg)
                write_json(p / f"plan-{i}.json", plan)
                record = load_json(p / f"edits-{i}.json")
                record["format"] = "picross-editorial-fixed-cell-derivation-v2"
                if cls == ColorDerivationTests and i == 0:
                    plan = {"format": "picross-editorial-raster-redraw-plan-v2", "puzzle_id": plan["puzzle_id"],
                        "revision": plan["revision"], "seed": None, "search": False, "certification": cfg,
                        "limits": {"max_changed_positions": 1, "solve_seconds": 30, "verify_seconds": 30, "max_lines": 100000}}
                    write_json(p / f"plan-{i}.json", plan)
                    record.update(format="picross-editorial-raster-redraw-v2", protected=case.steps[i]["protected"],
                                  plan_sha256=file_hash(p / f"plan-{i}.json"))
                write_json(p / f"edits-{i}.json", record)
                case.steps[i]["plan"]["sha256"] = file_hash(p / f"plan-{i}.json")
                case.steps[i]["record"]["sha256"] = file_hash(p / f"edits-{i}.json")
                case.steps[i]["output"]["bundle"] = f"paired-child-{i}"
            h["candidate"].update(bundle="paired-child-1", proof="paired-child-1/area-proof.json")
            difficulty(p, h, h["candidate"]["proof"])
            seal(p, h)
            case.authorize()
            _, report = self.export_and_register(p, cls.__name__, case.auth, case.approval)
            self.assertEqual(report["source"]["changed_cells"], 2)
            self.assertEqual(report["late_motif_acceptance"], cls == ColorDerivationTests)
            plan = load_json(p / "plan-0.json")
            plan.pop("certification")
            write_json(p / "plan-0.json", plan)
            case.steps[0]["plan"]["sha256"] = file_hash(p / "plan-0.json")
            if cls == ColorDerivationTests:
                record = load_json(p / "edits-0.json")
                record["plan_sha256"] = case.steps[0]["plan"]["sha256"]
                write_json(p / "edits-0.json", record)
                case.steps[0]["record"]["sha256"] = file_hash(p / "edits-0.json")
            seal(p, h)
            case.authorize()
            with self.assertRaisesRegex(InvalidInput, "paired plan"):
                case.inspect()


if __name__ == "__main__":
    unittest.main()
