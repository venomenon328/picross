"""SD2-B-T01: complete independent puzzles, exact guards, hostile file replay.

No catalog data. Synthetic profile counterprobes below are ONLY formula tests;
all stage/expectation evidence is independently replayed from complete puzzles.
"""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.contract import (Aborted, Budget, InvalidInput, InvalidProof,
    canonical_bytes, digest, validate_logic, write_json)
from tools.puzzle_production.sd2_analysis import analyze
from tools.puzzle_production.sd2_contract import AnalysisBudget, result_data
from tools.puzzle_production.sd2_io import _binding, _json, analyze_file, check_bundle
from tools.puzzle_production.sd2_verifier import verify_trace
from tools.puzzle_production.sd2_rating import _boundaries, _level, _line_rating, _workload
from tools.puzzle_production.sd2_rating_freeze import frozen_method
from tools.puzzle_production.sd2_rating_io import analyze_and_rate, rate_bundle, check_rating_bundle
from tools.puzzle_production.sd2_rating_identity import METHOD_HASH
from tools.puzzle_production.sd2_reference_checks import reference_evidence
from tools.puzzle_production.solver import solve

ROOT = Path(__file__).resolve().parents[2] / "tools" / "puzzle_production"
REFS = _json((ROOT / "sd2_references_0_4.json").read_bytes())
CASES = {c["id"]: c for c in REFS["cases"]}


def wire(rows, colors=("ink",)):
    def clues(line):
        out, last = [], "."
        for value in line:
            if value != ".":
                if value == last:
                    out[-1]["length"] += 1
                else:
                    out.append({"length": 1, "color": colors[int(value)]})
            last = value
        return out
    return {"format": "picross-logic-v1" if colors == ("ink",) else "picross-logic-v2",
            "width": len(rows[0]), "height": len(rows), "colors": list(colors), "empty": "empty",
            "initial_domain": ["empty", *colors],
            "rules": {"id": "mono-gap-v1", "same_color_gap": 1} if colors == ("ink",) else
                {"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0},
            "row_clues": [clues(row) for row in rows], "column_clues": [clues(row) for row in zip(*rows)]}


def transforms(rows):
    for transpose in (False, True):
        matrix = ["".join(row) for row in zip(*rows)] if transpose else rows
        for flip_y in (False, True):
            for flip_x in (False, True):
                yield [row[::-1] if flip_x else row for row in (matrix[::-1] if flip_y else matrix)]


def checked_profiles(logic):
    puzzle = validate_logic(logic)
    trace = analyze(puzzle)
    verify_trace(puzzle, trace)
    if trace["status"] != "solved":
        raise AssertionError("Expected complete independent line proof")
    return result_data(puzzle, trace)["profiles"]


class ReferenceTests(unittest.TestCase):
    def test_complete_calibration_and_separate_validation_replay(self):
        for split, count in (("calibration", 20), ("validation", 16)):
            with self.subTest(split=split):
                actual = reference_evidence(split)
                frozen = _json((ROOT / f"sd2_{split}_0_4.json").read_bytes())
                self.assertEqual(actual, frozen)
                self.assertEqual(len(actual["cases"]), count)
                self.assertTrue(actual["all_expectations_met"])
                self.assertTrue(actual["all_orders_met"])
                self.assertEqual({c["assessment"]["level"] for c in actual["cases"]}, {1, 2, 3, 4, 5})
                for level in range(1, 6):
                    self.assertGreaterEqual(sum(c["assessment"]["level"] == level for c in actual["cases"]), 2)
                self.assertTrue(any(c["assessment"]["level"] == 5 and c["reason"] == "complete_line" for c in actual["cases"]))
                self.assertTrue(any(c["reason"] == "required_r4" for c in actual["cases"]))

    def test_prebound_groups_provenance_and_no_symmetry_leakage(self):
        self.assertFalse(REFS["provenance"]["catalog_used"])
        self.assertIsNone(REFS["provenance"]["human_data"])
        seen = {}
        for case in CASES.values():
            self.assertTrue(case["origin"] and case["selection_reason"])
            self.assertEqual(case["logic"], wire(case["rows"], tuple(case["logic"]["colors"])))
            orbit = []
            for rows in transforms(case["rows"]):
                # Canonical first-use color labels also catch ID permutations.
                colors = {}
                orbit.append(tuple("".join("." if v == "." else str(colors.setdefault(v, len(colors)))
                                          for v in row) for row in rows))
            key = min(orbit)
            self.assertNotIn(key, seen, (case["id"], seen.get(key)))
            seen[key] = case["id"]

    def test_whole_puzzle_dihedral_and_color_id_invariance(self):
        for identifier in ("s40401-10", "s40401-1574", "s40401-888", "s40405-5280"):
            case = CASES[identifier]
            expected = _line_rating(checked_profiles(case["logic"]))
            for index, rows in enumerate(transforms(case["rows"])):
                with self.subTest(case=identifier, transform=index):
                    colors = tuple(case["logic"]["colors"])
                    actual = _line_rating(checked_profiles(wire(rows, colors)))
                    self.assertEqual(actual, expected)
                    if len(colors) > 1:
                        raw = wire(rows, ("blue", "red"))
                        raw["colors"].reverse()
                        raw["initial_domain"] = ["empty", *raw["colors"]]
                        self.assertEqual(_line_rating(checked_profiles(raw)), expected)

    def test_large_direct_and_color_packing_stay_l1(self):
        for identifier in ("full-50", "bands-40", "packed-colors", "s40401-1080"):
            rating = _line_rating(checked_profiles(CASES[identifier]["logic"]))
            self.assertEqual(rating["level"], 1)
            self.assertEqual(rating["contributions"]["workload"], [0, 1])

    def test_comparison_calibration_only_matches_chosen_implementation(self):
        comparison = _json((ROOT / "sd2_comparison_0_4.json").read_bytes())
        evidence = _json((ROOT / "sd2_calibration_0_4.json").read_bytes())
        self.assertEqual(comparison["reference_hash"], digest(REFS))
        self.assertEqual({c["id"] for c in comparison["cases"]}, {c["id"] for c in evidence["cases"]})
        for candidate, checked in zip(comparison["cases"], evidence["cases"], strict=True):
            chosen = candidate["results"]["chosen"]
            self.assertEqual(chosen["score"], checked["assessment"]["score"])
            self.assertEqual(chosen["level"], checked["assessment"]["level"])


class ArithmeticTests(unittest.TestCase):
    def test_exact_boundaries_no_float_epsilon(self):
        epsilon = F(1, 10**30)
        for threshold in range(1, 5):
            self.assertEqual(_level(threshold - epsilon), threshold)
            self.assertEqual(_level(F(threshold)), threshold + 1)
            self.assertEqual(_level(threshold + epsilon), threshold + 1)
            self.assertEqual(_boundaries(F(threshold))["distance_lower"], [0, 1])
            self.assertEqual(_boundaries(threshold - epsilon)["distance_upper"], [1, 10**30])
        self.assertIsNone(_boundaries(F(0))["lower"])
        self.assertIsNone(_boundaries(F(9, 2))["upper"])

    def test_workload_neighbor_ceiling_monotonicity_and_fluent_guard(self):
        for high, demand in (("E1", F(1)), ("E2", F(9, 4)), ("E3", F(13, 4))):
            for search in (F(0), F(3, 5), F(3, 4), F(4, 5), F(5, 4)):
                base = demand + search
                previous = base
                for raw in (F(0), F(1, 100), F(1, 10), F(1, 4)):
                    work, _, _ = _workload(base, high, search, False, raw)
                    score = base + work
                    self.assertLessEqual(_level(score) - _level(base), 1)
                    self.assertGreaterEqual(score, previous)
                    self.assertLessEqual(work, F(1, 4))
                    if search < F(3, 4) and _level(base) < 4:
                        self.assertLess(_level(score), 4)
                    if high == "E1":
                        self.assertLess(_level(score), 4)
                    previous = score
        # Genuine isolated neighbor movement remains possible, without reaching L4/5.
        work, _, _ = _workload(F(19, 10), "E1", F(9, 10), False, F(1, 4))
        self.assertEqual(_level(F(19, 10) + work), 3)
        self.assertEqual(_workload(F(3, 4), "E1", F(1, 2), True, F(1, 4))[0], 0)

    def test_late_spike_not_diluted_by_trivial_waves(self):
        profile = checked_profiles(CASES["s40405-5280"]["logic"])
        expected = _line_rating(profile)
        e0 = next(i for i, a in enumerate(profile["demand"]["trajectory"]) if a["family"] == "E0")
        for placement in ("before", "after"):
            altered = deepcopy(profile)
            for key in ("demand", "search", "workload"):
                padding = [deepcopy(profile[key]["trajectory"][e0]) for _ in range(400)]
                altered[key]["trajectory"] = (padding + altered[key]["trajectory"] if placement == "before"
                                               else altered[key]["trajectory"] + padding)
            altered["demand"]["strong_information_fraction"] = [1, 10**9]
            altered["workload"]["fill_spans"] += 100000
            rating = _line_rating(altered)
            self.assertEqual(rating["contributions"]["demand"], expected["contributions"]["demand"])
            self.assertEqual(rating["contributions"]["search"], expected["contributions"]["search"])
            self.assertEqual(rating["level"], 5)

    def test_fluid_exact_half_alternatives_and_context_not_raw_counts(self):
        profile = checked_profiles(CASES["s40401-10"]["logic"])
        for field in ("offer", "gain"):
            altered = deepcopy(profile)
            for demand, search in zip(altered["demand"]["trajectory"], altered["search"]["trajectory"]):
                if demand["family"] != "E1":
                    continue
                search.update(offer=[0, 1], gain=[0, 1], strain=[1, 2])
                search[field] = [1, 2]
            altered["workload"]["fill_spans"] = 1000000
            altered["workload"]["structure"].update(colors=1000, cells=1000000, short_blocks=100000)
            self.assertEqual(_line_rating(altered)["level"], 1)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input.json"
        write_json(self.source, CASES["s40401-10"]["logic"])

    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.puzzle_production.sd2_rating_cli", *map(str, args)],
                              capture_output=True, text=True, check=False)

    def test_independent_file_roundtrip_determinism_and_raw_compatibility(self):
        raw = self.root / "raw"
        original = analyze_file(self.source, raw)
        before = {p.name: p.read_bytes() for p in raw.iterdir()}
        first = rate_bundle(self.source, raw, self.root / "first")
        second = analyze_and_rate(self.source, self.root / "second")
        self.assertEqual(first["result"], second["result"])
        self.assertEqual(first["result_hash"], second["result_hash"])
        self.assertEqual((self.root / "first" / "report.md").read_bytes(), (self.root / "second" / "report.md").read_bytes())
        self.assertTrue(check_rating_bundle(self.source, self.root / "first")["rating_verified"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in raw.iterdir()})
        self.assertIsNone(original["result"]["method"])
        self.assertIsNone(original["result"]["level"])
        check_bundle(self.source, raw)
        (raw / "rating.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(InvalidProof):
            check_bundle(self.source, raw)
        with self.assertRaises(InvalidProof):
            rate_bundle(self.source, raw, self.root / "badraw")
        with self.assertRaises(InvalidInput):
            analyze_and_rate(self.source, self.root / "first")

    def test_rating_and_markdown_tamper_even_with_self_hash(self):
        output = self.root / "rated"
        report = analyze_and_rate(self.source, output)
        changes = [lambda x: x["result"]["assessment"].update(level=5),
                   lambda x: x["result"]["assessment"]["contributions"].update(search=[0, 1]),
                   lambda x: x["result"]["assessment"]["boundaries"].update(nearest_distance=[0, 1]),
                   lambda x: x["result"].update(confidence="high"),
                   lambda x: x["result"].update(estimated_minutes=12),
                   lambda x: x["result"].update(method_hash="0" * 64),
                   lambda x: x["result"].update(profile_scope="line_prefix"),
                   lambda x: x.update(approved=True),
                   lambda x: x["analysis_files"].update({"../outside": {}})]
        for mutate in changes:
            with self.subTest(change=changes.index(mutate)):
                bad = deepcopy(report)
                mutate(bad)
                bad["result_hash"] = digest(bad["result"])
                write_json(output / "rating.json", bad)
                with self.assertRaises(InvalidProof):
                    check_rating_bundle(self.source, output)
        write_json(output / "rating.json", report)
        (output / "report.md").write_text("forged explanation", encoding="utf-8")
        with self.assertRaises(InvalidProof):
            check_rating_bundle(self.source, output)

    def test_forged_raw_profile_and_trace_are_rechecked(self):
        output = self.root / "rated"
        envelope = analyze_and_rate(self.source, output)
        raw_path = output / "analysis" / "report.json"
        original = _json(raw_path.read_bytes())
        for mutate in (lambda x: x["result"]["profiles"]["demand"].update(highest_family="E3"),
                       lambda x: x["result"].update(deduction_complete=True, status="stalled"),
                       lambda x: x.update(target_check="matched_complete")):
            bad = deepcopy(original)
            mutate(bad)
            bad["result_hash"] = digest(bad["result"])
            write_json(raw_path, bad)
            with self.assertRaises(InvalidProof):
                rate_bundle(self.source, output / "analysis", self.root / f"forged-{len(list(self.root.iterdir()))}")
        write_json(raw_path, original)
        trace_path = output / "analysis" / "trace.json"
        trace = _json(trace_path.read_bytes())
        trace["waves"][0]["changes"].pop()
        write_json(trace_path, trace)
        original["files"]["trace.json"] = _binding(trace_path.read_bytes())
        original["result"]["trace_hash"] = digest(trace)
        original["result_hash"] = digest(original["result"])
        write_json(raw_path, original)
        envelope["analysis_files"]["trace.json"] = _binding(trace_path.read_bytes())
        envelope["analysis_files"]["report.json"] = _binding(raw_path.read_bytes())
        write_json(output / "rating.json", envelope)
        with self.assertRaises(InvalidProof):
            check_rating_bundle(self.source, output)

    def test_closed_files_source_identity_and_changed_during_check(self):
        output = self.root / "rated"
        analyze_and_rate(self.source, output)
        for directory in (output, output / "analysis"):
            extra = directory / "extra"
            extra.write_text("unexpected", encoding="utf-8")
            with self.assertRaises(InvalidProof):
                check_rating_bundle(self.source, output)
            extra.unlink()
        self.source.write_bytes(self.source.read_bytes() + b" ")
        with self.assertRaises(InvalidProof):
            check_rating_bundle(self.source, output)
        write_json(self.source, CASES["s40401-10"]["logic"])
        def racing(*args, **kwargs):
            result = check_bundle(*args, **kwargs)
            path = output / "analysis" / "trace.json"
            path.write_bytes(path.read_bytes() + b" ")
            return result
        with patch("tools.puzzle_production.sd2_rating_io.check_bundle", side_effect=racing):
            with self.assertRaises(InvalidProof):
                check_rating_bundle(self.source, output)

    def test_r4_necessity_required_and_complete_proof_is_not_enough(self):
        case = CASES["s40405-65"]
        write_json(self.source, case["logic"])
        puzzle = validate_logic(case["logic"])
        baseline, proof = self.root / "baseline.json", self.root / "proof.json"
        write_json(proof, solve(puzzle, profile="paired-lines-mono"))
        write_json(baseline, solve(puzzle))
        report = analyze_and_rate(self.source, self.root / "r4", proof_path=proof, baseline_path=baseline)
        self.assertEqual(report["result"]["assessment"]["level"], 5)
        self.assertEqual(report["result"]["profile_scope"], "line_prefix")
        self.assertIn("prefix", (self.root / "r4" / "report.md").read_text())
        check_rating_bundle(self.source, self.root / "r4")
        for limits in ({"max_pair_work": 0}, {"max_pair_records": 0}):
            with self.assertRaises(Aborted):
                check_rating_bundle(self.source, self.root / "r4", AnalysisBudget(**limits))
        write_json(baseline, solve(puzzle, Budget(max_lines=0)))
        incomplete = analyze_and_rate(self.source, self.root / "unproved", proof_path=proof, baseline_path=baseline)
        raw = _json((self.root / "unproved" / "analysis" / "report.json").read_bytes())
        self.assertTrue(raw["result"]["deduction_complete"])
        self.assertIsNone(incomplete["result"]["assessment"])
        self.assertEqual(incomplete["result"]["reason"], "r4_necessity_unproven")
        check_rating_bundle(self.source, self.root / "unproved")
        missing = analyze_and_rate(self.source, self.root / "stalled")
        self.assertIsNone(missing["result"]["assessment"])
        with self.assertRaises(InvalidInput):
            analyze_and_rate(self.source, self.root / "missing-pair", proof_path=proof)
        bad = _json(proof.read_bytes())
        bad["logic_hash"] = "0" * 64
        write_json(proof, bad)
        with self.assertRaises(InvalidProof):
            analyze_and_rate(self.source, self.root / "wrong-pair", proof_path=proof, baseline_path=baseline)

    def test_r4_rotated_whole_puzzle_still_requires_independent_pair_proof(self):
        rows = ["".join(row) for row in zip(*CASES["s40495-109"]["rows"])][::-1]
        puzzle = validate_logic(wire(rows))
        write_json(self.source, puzzle.to_wire())
        baseline, proof = self.root / "baseline.json", self.root / "proof.json"
        write_json(proof, solve(puzzle, profile="paired-lines-mono"))
        write_json(baseline, solve(puzzle))
        report = analyze_and_rate(self.source, self.root / "r4", proof_path=proof, baseline_path=baseline)
        self.assertEqual(report["result"]["reason"], "required_r4")
        self.assertEqual(report["result"]["assessment"]["score"], [9, 2])
        check_rating_bundle(self.source, self.root / "r4")

    def test_contradiction_and_all_analysis_abort_reasons_never_rate(self):
        broken = deepcopy(CASES["s40401-10"]["logic"])
        broken["row_clues"] = [[] for _ in broken["row_clues"]]
        write_json(self.source, broken)
        result = analyze_and_rate(self.source, self.root / "contradiction")["result"]
        self.assertEqual(result["reason"], "contradiction")
        self.assertIsNone(result["assessment"])
        check_rating_bundle(self.source, self.root / "contradiction")
        write_json(self.source, CASES["s40401-10"]["logic"])
        for budget, reason in ((AnalysisBudget(seconds=0), "time_limit"),
                               (AnalysisBudget(max_rule_work=0), "rule_work_limit"),
                               (AnalysisBudget(max_waves=0), "wave_limit"),
                               (AnalysisBudget(cancelled=lambda: True), "cancelled")):
            result = analyze_and_rate(self.source, self.root / reason, budget=budget)["result"]
            self.assertEqual(result["reason"], reason)
            self.assertIsNone(result["assessment"])
            self.assertIsNone(result["confidence"])
        for target, value, reason in (("BYTE_LIMIT", 1, "trace_byte_limit"),
                                     ("deductions", MemoryError, "memory_limit")):
            with patch("tools.puzzle_production.sd2_analysis." + target,
                       **({"new": value} if target == "BYTE_LIMIT" else {"side_effect": value})):
                result = analyze_and_rate(self.source, self.root / reason)["result"]
            self.assertEqual(result["reason"], reason)
            self.assertIsNone(result["assessment"])

    def test_runtime_target_is_separate_and_inputs_are_read_only(self):
        fixture = Path(__file__).parent / "fixtures" / "sd-runtime.json"
        self.source.write_bytes(fixture.read_bytes())
        sentinel = self.root / "registry.json"
        sentinel.write_bytes(b"explicit-input-only\n")
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        report = analyze_and_rate(self.source, self.root / "runtime", kind="runtime")
        self.assertEqual(report["result"]["assessment"]["level"], 1)
        check_rating_bundle(self.source, self.root / "runtime")
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in before})
        raw = _json(self.source.read_bytes())
        raw["solution"] = {"wrong": "shape"}
        write_json(self.source, raw)
        with self.assertRaises(InvalidInput):
            analyze_and_rate(self.source, self.root / "bad-target", kind="runtime")
        self.assertFalse((self.root / "bad-target" / "rating.json").exists())
        self.assertEqual((self.root / "runtime" / "analysis" / "trace.json").read_bytes(),
                         (self.root / "bad-target" / "analysis" / "trace.json").read_bytes())

    def test_file_limits_missing_members_and_invalid_json_are_fail_closed(self):
        output = self.root / "rated"
        analyze_and_rate(self.source, output)
        rating = (output / "rating.json").read_bytes()
        for malformed in (b"[]", b"{}", b'{"format":1,"format":2}'):
            (output / "rating.json").write_bytes(malformed)
            with self.assertRaises((InvalidInput, InvalidProof)):
                check_rating_bundle(self.source, output)
        (output / "rating.json").write_bytes(rating)
        with patch("tools.puzzle_production.sd2_rating_io.BYTE_LIMIT", 1):
            with self.assertRaises(InvalidInput):
                check_rating_bundle(self.source, output)
        (output / "report.md").write_bytes(b"x" * (1024 * 1024 + 1))
        with self.assertRaises(InvalidInput):
            check_rating_bundle(self.source, output)
        (output / "analysis" / "trace.json").unlink()
        with self.assertRaises(InvalidProof):
            check_rating_bundle(self.source, output)
        self.source.write_bytes(b" " * (2 * 1024 * 1024 + 1))
        with self.assertRaises(InvalidInput):
            analyze_and_rate(self.source, self.root / "oversized-input")

    def test_cli_success_report_rate_check_and_exit_codes(self):
        run = self.cli("analyze", "--input", self.source, "--output-dir", self.root / "cli")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)["level"], 2)
        self.assertEqual(json.loads(run.stdout)["format"], "picross-sd2-rating-cli-v1")
        self.assertEqual(json.loads(run.stdout)["command"], "analyze")
        checked = self.cli("check", "--input", self.source, "--bundle", self.root / "cli")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        copied = self.cli("rate", "--input", self.source, "--analysis-bundle", self.root / "cli" / "analysis",
                          "--output-dir", self.root / "copy")
        self.assertEqual(copied.returncode, 0, copied.stdout + copied.stderr)
        self.assertEqual(json.loads(copied.stdout)["result_hash"], json.loads(run.stdout)["result_hash"])
        for name, args, code in (("analysis-abort", ["--max-lines", "0"], 4),
                                 ("verify-abort", ["--verify-max-lines", "0"], 4),
                                 ("invalid", ["--seconds", "nan"], 2)):
            run = self.cli("analyze", "--input", self.source, "--output-dir", self.root / name, *args)
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)
            self.assertIsNone(json.loads(run.stdout)["level"])
        self.assertFalse((self.root / "verify-abort" / "rating.json").exists())
        for path, content in (("duplicate", b'{"format":1,"format":2}'), ("bom", b'\xef\xbb\xbf{}'),
                              ("nonfinite", b'{"x":NaN}'), ("surrogate", b'{"x":"\\ud800"}')):
            source = self.root / path
            source.write_bytes(content)
            run = self.cli("analyze", "--input", source, "--output-dir", self.root / (path + "-out"))
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertFalse((self.root / (path + "-out") / "rating.json").exists())
        (self.root / "cli" / "report.md").write_text("bad", encoding="utf-8")
        self.assertEqual(self.cli("check", "--input", self.source, "--bundle", self.root / "cli").returncode, 3)

    def test_checker_budgets_cancel_memory_technical_and_deadline_start(self):
        output = self.root / "rated"
        analyze_and_rate(self.source, output)
        for limits in ({"seconds": 0}, {"max_lines": 0}, {"max_rule_work": 0}):
            with self.assertRaises(Aborted):
                check_rating_bundle(self.source, output, AnalysisBudget(**limits))
        from tools.puzzle_production.sd2_rating_cli import main
        import io
        from contextlib import redirect_stdout
        for error, code in ((MemoryError(), 4), (KeyboardInterrupt(), 4), (RuntimeError("test"), 5)):
            with patch("tools.puzzle_production.sd2_rating_cli.check_rating_bundle", side_effect=error):
                out = io.StringIO()
                with redirect_stdout(out):
                    actual = main(["check", "--input", str(self.source), "--bundle", str(output)])
                self.assertEqual(actual, code)
                self.assertIsNone(json.loads(out.getvalue())["level"])
        budget = AnalysisBudget(seconds=5)
        budget.deadline = -1  # A/B deadline begins at first check, not construction.
        budget.check()

    def test_analysis_does_not_spend_the_separate_verification_deadline(self):
        verify_budget = AnalysisBudget()
        def inspect_start(*args, **kwargs):
            self.assertFalse(verify_budget.started, "Analysis time must not consume the verification deadline")
            return analyze(*args, **kwargs)
        with patch("tools.puzzle_production.sd2_analysis.analyze", side_effect=inspect_start):
            analyze_and_rate(self.source, self.root / "separate-clocks", verify_budget=verify_budget)
        self.assertTrue(verify_budget.started)

    def test_links_rejected_without_reading_target(self):
        from tools.puzzle_production import sd2_io
        original = Path.lstat
        def as_link(path):
            if path == self.source:
                from types import SimpleNamespace
                return SimpleNamespace(st_mode=0o120777, st_file_attributes=0)
            return original(path)
        with patch.object(Path, "lstat", as_link):
            with self.assertRaises(InvalidInput):
                sd2_io._bytes(self.source, 10000)


class FreezeTests(unittest.TestCase):
    def test_new_freeze_and_old_freeze_sources_unchanged(self):
        from tools.puzzle_production.difficulty_rating import frozen_method as legacy_method
        from tools.puzzle_production.difficulty_identity import METHOD_HASH as legacy_hash
        method, legacy = frozen_method(), legacy_method()
        self.assertEqual(digest(method), METHOD_HASH)
        self.assertEqual(legacy_hash, "8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79")
        self.assertEqual(len(legacy["implementation"]), 13)
        for name, expected in legacy["implementation"].items():
            self.assertEqual(method["implementation"][name], expected)
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)
        self.assertNotIn("sd2_rating_identity.py", method["implementation"])

    def test_changed_manifest_artifacts_or_sources_fail_closed(self):
        method = frozen_method()
        names = ["sd2_method_0_4.json", *method["artifacts"], *method["implementation"]]
        from tools.puzzle_production import sd2_rating_freeze
        original = sd2_rating_freeze._bytes
        for changed in names:
            def read(path, limit):
                raw = original(path, limit)
                if path.name != changed:
                    return raw
                if path.suffix == ".json":
                    obj = _json(raw)
                    obj["tampered"] = True
                    return canonical_bytes(obj)
                return raw + b"# changed\n"
            with self.subTest(file=changed), patch.object(sd2_rating_freeze, "_bytes", side_effect=read):
                with self.assertRaises(InvalidInput):
                    frozen_method()


if __name__ == "__main__":
    unittest.main()
