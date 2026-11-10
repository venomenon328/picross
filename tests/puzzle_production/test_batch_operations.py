"""BA-A's seven adapter families, exercised with real tiny domain artifacts."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import batch_operations as operations
from tools.puzzle_production import analysis_io, catalog_analysis, catalog_rating, background_assets, images, repair
from tools.puzzle_production.analysis_contract import AnalysisBudget
from tools.puzzle_production.contract import InvalidInput, load_json
from tests.puzzle_production.batch_fixtures import (
    ANALYSIS_LIMITS, BatchFixture, LOGIC_LIMITS, METHOD, ROOT, VARIANT, domain_ref, output_ref, put, source_ref, stamps,
)


class BatchOperationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ba-a-adapters-")
        self.addCleanup(temporary.cleanup)
        self.fixture = BatchFixture(Path(temporary.name))
        self.results = {}

    def execute(self, job, stage):
        resolved = {}
        for key, ref in stage["inputs"].items():
            if ref is None:
                resolved[key] = None
            elif ref["kind"] == "source":
                resolved[key] = self.fixture.source / ref["file"]
            else:
                slot = ref["slot"] + (":" + ref["candidate_id"] if ref["candidate_id"] is not None else "")
                resolved[key] = Path(self.results[(job["job_id"], ref["stage"])]["slots"][slot]["path"])
        decisions = {key: self.fixture.source / ref["file"] if ref is not None else None
                     for key, ref in job["decisions"].items()}
        output = self.fixture.root / "operation-output" / job["job_id"] / stage["stage_id"]
        output.mkdir(parents=True)
        result = operations.execute_operation(stage, resolved, output, ROOT, self.fixture.source,
                                              decisions=decisions)
        operations.validate_result(result)
        self.results[(job["job_id"], stage["stage_id"])] = result
        return result, resolved, decisions, output

    def test_all_fixed_operations_use_actual_files_and_domain_verifiers(self):
        fixture = self.fixture
        job = fixture.add_job("raster", background=True)
        imported, *_ = self.execute(job, fixture.image_stage(job))
        self.assertEqual(imported["domain"], "produced")
        checked_stage = fixture.stage(job, "inspect", "candidate_verify", "verify",
                                      {"bundle": output_ref("import", "bundle")}, {"candidate": VARIANT})
        checked, *_ = self.execute(job, checked_stage)
        bundle = Path(checked["slots"]["bundle"]["path"])
        self.assertTrue(images.inspect_candidate(bundle, VARIANT)[2]["certified"])
        solve_stage = fixture.solve_stage(job, logic=output_ref("inspect", "logic", VARIANT))
        solved, *_ = self.execute(job, solve_stage)
        self.assertEqual((solved["domain"], solved["certified"]), ("solved", True))
        analyzed, *_ = self.execute(job, fixture.difficulty_stage(job, producer="inspect"))
        checked_difficulty = load_json(Path(analyzed["slots"]["checked_difficulty"]["path"]))
        self.assertEqual(checked_difficulty["format"], "picross-checked-difficulty-v3")
        self.assertEqual(checked_difficulty["rating"]["method"], METHOD)
        self.assertEqual(checked_difficulty["production_mode"], "mono")
        rating_stage = fixture.stage(job, "rating-import", "difficulty", "import",
                                     {"candidate": output_ref("difficulty", "candidate"),
                                      "bundle": output_ref("difficulty", "analysis_bundle")}, {"method": METHOD})
        rating, *_ = self.execute(job, rating_stage)
        independent = catalog_rating.import_bundle(Path(analyzed["slots"]["candidate"]["path"]),
                                                    Path(analyzed["slots"]["analysis_bundle"]["path"]))
        self.assertEqual(load_json(Path(rating["slots"]["checked_difficulty"]["path"])), independent)
        self.assertIsNone(rating["certified"], "a rating is not a certification or owner decision")

        request = fixture.background(job)
        derived, *_ = self.execute(job, fixture.stage(job, "background", "background", "derive", {"request": request}))
        self.assertIn("background_png", derived["slots"])
        verification = fixture.stage(job, "background-verify", "background", "verify",
                                     {"request": request, "bundle": output_ref("background", "background_finding")})
        verified, *_ = self.execute(job, verification)
        self.assertEqual(verified["domain"], "verified")
        original_request = load_json(fixture.source / request["file"])
        self.assertEqual(background_assets.verify(original_request, fixture.source,
                                                  Path(derived["slots"]["background_finding"]["path"]).parent)["status"],
                         "verified")

        repair_job = fixture.add_job("repair", pattern="stalled")
        reference, plan, original_plan = fixture.repair_reference(repair_job)
        bounded = {key: original_plan["config"][key] for key in
                   ("search_seconds", "final_seconds", "search_lines", "final_lines", "max_steps", "max_candidates", "max_changes")}
        search = fixture.stage(repair_job, "search", "repair", "search",
                               {"reference": reference, "plan": plan, "approval": repair_job["decisions"]["motif"]},
                               limits={"produce": bounded, "revalidate": LOGIC_LIMITS})
        repaired, *_ = self.execute(repair_job, search)
        self.assertEqual((repaired["domain"], repaired["certified"]), ("found", True))
        replay_stage = fixture.stage(repair_job, "replay", "repair", "verify",
                                     {"reference": reference, "bundle": output_ref("search", "repair_bundle")})
        replay, *_ = self.execute(repair_job, replay_stage)
        self.assertTrue(replay["certified"])
        self.assertTrue(repair.inspect_repair(Path(repaired["slots"]["repair_bundle"]["path"]),
                                              (fixture.source / reference["file"]).parent)["certified"])
        self.assertEqual(load_json(Path(repaired["slots"]["matrix"]["path"])),
                         [["ink", "ink"], ["empty", "ink"]])

        build_job = fixture.add_job("builder")
        build_stage = fixture.stage(build_job, "build", "authoring_build", "build",
                                    {"request": fixture.builder_request(build_job)})
        built, *_ = self.execute(build_job, build_stage)
        self.assertEqual(set(built["slots"]), {"package", "handoff", "record", "sheet_update"})
        self.assertEqual(load_json(Path(built["slots"]["handoff"]["path"]))["state"], "brief_ready")
        record = load_json(Path(built["slots"]["record"]["path"]))
        self.assertIsNone(record["integration"])
        self.assertIsNone(record["source_commit"])
        self.assertFalse(record["verification"]["technical"])
        self.assertTrue(Path(built["slots"]["package"]["path"]).is_file())
        self.assertEqual(set(operations.OPERATION_SPECS),
                         {(s["kind"], s["operation"]) for j in fixture.plan["jobs"] for s in j["stages"]})

    def test_historical_03_import_revalidates_originals_without_new_analysis_or_mode(self):
        fixture = self.fixture
        job = fixture.add_job("historical")
        data = fixture.data[job["job_id"]]
        legacy = "picross-difficulty-0.3"
        candidate = catalog_analysis.candidate(
            *(load_json(fixture.source / data[key]["file"]) for key in ("design", "matrix", "logic")),
            job["puzzle_id"], 1)
        candidate_ref = put(fixture.source, data["prefix"] + "/candidate.json", candidate)
        candidate_path = fixture.source / candidate_ref["file"]
        for context in (True, False):
            with self.subTest(context=context):
                label = "with-context" if context else "without-context"
                bundle = fixture.source / data["prefix"] / label
                budgets = {"budget": AnalysisBudget(**ANALYSIS_LIMITS),
                           "verify_budget": AnalysisBudget(**ANALYSIS_LIMITS)}
                if context:
                    catalog_analysis.analyze_single(candidate_path, bundle, production_mode="mono",
                                                    method=legacy, **budgets)
                else:
                    analysis_io.analyze_file(candidate_path, bundle, kind="runtime", method=legacy, **budgets)
                expected = catalog_rating.import_bundle(candidate_path, bundle,
                                                        budget=AnalysisBudget(**ANALYSIS_LIMITS))
                marker = "catalog-context.json" if context else "report.json"
                bundle_ref = source_ref(fixture.source, (bundle / marker).relative_to(fixture.source).as_posix())
                stage = fixture.stage(job, label, "difficulty", "import",
                                      {"candidate": candidate_ref, "bundle": bundle_ref}, {"method": legacy})
                source_before = stamps(fixture.source)
                result, inputs, decisions, output = self.execute(job, stage)
                self.assertEqual((result["status"], result["domain"], result["exit_code"]),
                                 ("completed", expected["rating"]["result"]["status"], 0), result["details"]["reason"])
                self.assertEqual(result["details"]["method"], legacy)
                self.assertIsNone(result["certified"])
                checked = load_json(Path(result["slots"]["checked_difficulty"]["path"]))
                self.assertEqual(checked, expected)
                self.assertEqual(checked["format"], catalog_rating.CHECKED if context else catalog_rating.LEGACY_CHECKED)
                if context:
                    self.assertEqual(checked["production_mode"], "mono")
                else:
                    self.assertNotIn("production_mode", checked)
                output_before = stamps(output)
                replay_output = fixture.root / (label + "-revalidation")
                replay_output.mkdir()
                fresh = operations.revalidate_operation(stage, inputs, result, replay_output, ROOT,
                                                        fixture.source, decisions=decisions)
                operations.validate_result(fresh)
                self.assertEqual((fresh["status"], fresh["domain"], fresh["exit_code"]),
                                 ("completed", result["domain"], 0))
                self.assertEqual(fresh["slots"], result["slots"])
                self.assertEqual(stamps(fixture.source), source_before)
                self.assertEqual(stamps(output), output_before)
        analyze = fixture.difficulty_stage(job, stage_id="historical-analysis-denied")
        analyze["parameters"]["method"] = legacy
        with self.assertRaises(InvalidInput):
            operations.validate_operation(analyze, ROOT)

    def test_none_preserves_originals_and_never_materializes_a_png(self):
        fixture = self.fixture
        job = fixture.add_job("none", background=True)
        request = fixture.background(job, none=True)
        stage = fixture.stage(job, "background", "background", "derive", {"request": request})
        result, inputs, decisions, _ = self.execute(job, stage)
        self.assertEqual(result["domain"], "none")
        self.assertEqual(set(result["slots"]), {"background_finding"})
        original = Path(result["slots"]["background_finding"]["path"]).parent
        before = stamps(original)
        output = fixture.root / "revalidation"
        output.mkdir()
        validated = operations.revalidate_operation(stage, inputs, result, output, ROOT, fixture.source,
                                                    decisions=decisions)
        operations.validate_result(validated)
        self.assertEqual(stamps(original), before)
        self.assertEqual(set(validated["slots"]), {"background_finding"})
        self.assertFalse(list(original.glob("*.png")))
        for case in ("rejected", "missing", "corrupt", "legacy"):
            with self.subTest(background=case):
                job = fixture.add_job("bg-" + case, background=True)
                request_ref = fixture.background(job)
                request = load_json(fixture.source / request_ref["file"])
                if case == "rejected":
                    from tools.puzzle_production.background_contract import validate_decision
                    decision = load_json(fixture.source / job["decisions"]["background"]["file"])
                    statement = "TEST ONLY: Reject all offered synthetic candidates."
                    decision.update(outcome="rejected", candidate_id=None, original=None, profile=None,
                                    statement=statement)
                    decision["evidence"] = domain_ref(put(fixture.source, decision["evidence"]["file"], statement.encode()))
                    self.assertEqual(validate_decision(decision)["outcome"], "rejected")
                    decision_ref = put(fixture.source, job["decisions"]["background"]["file"], decision)
                    job["decisions"]["background"] = decision_ref
                    request.update(decision=domain_ref(decision_ref), source=None)
                elif case == "legacy":
                    request["format"] = "picross-background-derive-request-v0"
                else:
                    source = fixture.source / request["source"]["file"]
                    if case == "missing":
                        source.unlink()
                    else:
                        source.write_bytes(b"TEST ONLY damaged source; no valid PNG\n")
                request_ref = put(fixture.source, request_ref["file"], request)
                native_output = fixture.root / ("native-invalid-" + case)
                native_output.mkdir()
                native = background_assets.derive(request, fixture.source, native_output)
                self.assertEqual(native["status"], "invalid_input")
                rejected, *_ = self.execute(job, fixture.stage(job, "background", "background", "derive", {"request": request_ref}))
                self.assertEqual((rejected["status"], rejected["domain"], rejected["exit_code"]),
                                 ("failed", native["status"], 2))
                self.assertNotIn("background_png", rejected["slots"])
                self.assertNotIn("background_finding", rejected["slots"])

    def test_exit_zero_and_valid_proofs_do_not_upgrade_stalled_or_contradictory_results(self):
        for name in ("solved", "stalled", "contradiction"):
            with self.subTest(domain=name):
                job = self.fixture.add_job(name, pattern=name)
                result, *_ = self.execute(job, self.fixture.solve_stage(job))
                self.assertEqual((result["status"], result["domain"], result["exit_code"]), ("completed", name, 0))
                self.assertEqual(result["certified"], name == "solved")
        job = self.fixture.add_job("uncertified-import", pattern="stalled")
        result, *_ = self.execute(job, self.fixture.image_stage(job))
        self.assertEqual((result["domain"], result["exit_code"]), ("produced", 0))
        self.assertFalse(result["details"]["candidates"][0]["certified"])
        aborted = self.fixture.add_job("aborted")
        limits = {"produce": {**LOGIC_LIMITS, "max_lines": 0}, "revalidate": LOGIC_LIMITS}
        result, *_ = self.execute(aborted, self.fixture.solve_stage(aborted, limits=limits))
        self.assertEqual((result["status"], result["domain"], result["exit_code"]), ("aborted", "aborted", 4))
        self.assertFalse(result["certified"])

    def test_explicit_runtime_r4_proofs_are_separate_from_the_production_proofs(self):
        fixture = self.fixture
        job = fixture.add_job("paired", pattern="paired")
        inputs = fixture.paired_inputs(job)
        parameters = {"puzzle_id": job["puzzle_id"], "runtime_revision": 1,
                      "production_mode": "mono", "method": METHOD}
        missing = deepcopy(inputs)
        missing.update(r4_proof=None, r4_baseline=None)
        unrated, *_ = self.execute(job, fixture.stage(job, "without-r4", "difficulty", "analyze", missing, parameters))
        unrated_value = load_json(Path(unrated["slots"]["checked_difficulty"]["path"]))
        self.assertEqual(unrated_value["rating"]["result"]["reason"], "incomplete_line")
        rated, *_ = self.execute(job, fixture.stage(job, "with-r4", "difficulty", "analyze", inputs, parameters))
        rated_value = load_json(Path(rated["slots"]["checked_difficulty"]["path"]))
        self.assertTrue(catalog_rating.project(rated_value)["r4_required"])
        self.assertEqual(rated_value["rating"]["result"]["assessment"]["level"], 5)
        self.assertIsNone(rated["certified"])
        original = load_json(fixture.source / inputs["proof"]["file"])
        normalized = load_json(fixture.source / inputs["r4_proof"]["file"])
        self.assertNotEqual(original["logic_hash"], normalized["logic_hash"])
        partial = deepcopy(inputs)
        partial["r4_baseline"] = None
        waiting, *_ = self.execute(job, fixture.stage(job, "partial-r4", "difficulty", "analyze", partial, parameters))
        self.assertEqual(waiting["status"], "waiting_input")
        self.assertEqual(set(waiting["slots"]), {"candidate"})
        candidate = Path(waiting["slots"]["candidate"]["path"])
        self.assertEqual(catalog_rating.definition(candidate.read_bytes())[2]["id"], job["puzzle_id"])

    def test_builder_cannot_publish_and_wrong_motif_cannot_authorize_raster_work(self):
        fixture = self.fixture
        job = fixture.add_job("restricted")
        stage = fixture.image_stage(job)
        original = load_json(fixture.source / job["decisions"]["motif"]["file"])
        original["sha256"] = "0" * 64
        changed = put(fixture.source, job["decisions"]["motif"]["file"], original)
        job["decisions"]["motif"] = stage["inputs"]["approval"] = changed
        rejected, *_ = self.execute(job, stage)
        self.assertEqual((rejected["status"], rejected["domain"], rejected["exit_code"]),
                         ("failed", "invalid_input", 2))
        request_ref = fixture.builder_request(job)
        request = load_json(fixture.source / request_ref["file"])
        request["target"] = "repository"
        changed = put(fixture.source, request_ref["file"], request)
        build = fixture.stage(job, "publish-denied", "authoring_build", "build", {"request": changed})
        with patch("tools.puzzle_production.authoring_builder.build", side_effect=AssertionError("must reject before builder")):
            rejected, *_ = self.execute(job, build)
        self.assertEqual((rejected["status"], rejected["domain"], rejected["exit_code"]),
                         ("failed", "invalid_input", 2))


if __name__ == "__main__":
    unittest.main()
