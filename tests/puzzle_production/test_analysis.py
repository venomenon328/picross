"""SD-A-T01: independent synthetic lines/grids, never catalog inputs."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.analysis import analyze
from tools.puzzle_production.analysis_contract import (AnalysisBudget, measurements,
                                                      parameters, result_data)
from tools.puzzle_production.analysis_rules import deductions
from tools.puzzle_production.analysis_verifier import justified_rules, verify_trace, verify_result
from tools.puzzle_production.analysis_io import analyze_file, check_bundle, runtime_logic
from tools.puzzle_production.contract import (Budget, Clue, InvalidInput, InvalidProof, Puzzle,
                                             digest, load_json, validate_logic, write_json)
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify
from oracle import colored_runs
from test_paired import wire, MONO, COLOR


def mask_union(rows, length):
    out = [0] * length
    for row in rows:
        for i, value in enumerate(row):
            out[i] |= 1 << value
    return out


def combine(domains, rules):
    out = list(domains)
    for values in rules.values():
        out = [a & b for a, b in zip(out, values)]
    return out


def grid(text, names=("ink",)):
    return [["empty" if c == "." else names[int(c)] for c in row] for row in text]


# Fixed independently constructed bit patterns, not a rating reference corpus.
FLOW = grid(("000.0.", "0.0000", ".....0", "...0..", ".00000"))
GENERAL_LINE = grid(("..000..0", "00.0.00.", "00...0..", "..0..0.0",
                     "000000..", "0000000.", ".000000."))
RUNTIME = Path(__file__).parent / "fixtures" / "sd-runtime.json"


class RuleTests(unittest.TestCase):
    def test_every_small_domain_against_exhaustive_independent_oracle(self):
        for color_count, max_length in ((1, 4), (2, 3)):
            for n in range(1, max_length + 1):
                placements = {}
                for values in product(range(color_count + 1), repeat=n):
                    placements.setdefault(colored_runs(values), []).append(values)
                for clue_pairs, legal in placements.items():
                    clues = tuple(Clue(length, 1 << color) for length, color in clue_pairs)
                    for domains in product(range(1, 1 << (color_count + 1)), repeat=n):
                        supported = mask_union([r for r in legal if all(d & (1 << v) for d, v in zip(domains, r))], n)
                        generated = deductions(clues, list(domains), 3, AnalysisBudget())
                        checked = justified_rules(clues, list(domains), 3, AnalysisBudget())
                        self.assertEqual(generated, checked, (clue_pairs, domains))
                        for name, values in generated.items():
                            self.assertTrue(all(not (s & ~v) for s, v in zip(supported, values)),
                                            (name, clue_pairs, domains, supported, values))
                            self.assertTrue(all(not (v & ~d) for d, v in zip(domains, values)))
                        self.assertEqual(generated["R3-support"], supported)

    def test_positive_and_boundary_examples_for_each_subrule(self):
        cases = [
            ((), [3]*5, "R0-empty", [1]*5),
            ((Clue(2, 2), Clue(2, 4)), [7]*4, "R0-packed", [2, 2, 4, 4]),
            ((2, 2), [3]*5, "R0-packed", [2, 2, 1, 2, 2]),
            ((Clue(2, 2), Clue(1, 4)), [7, 2, 2, 7, 7, 4, 7], "R0-cleanup", [1, 2, 2, 1, 1, 4, 1]),
            ((3,), [3]*5, "R1-overlap", [3, 3, 2, 3, 3]),
            ((3,), [2, 3, 3, 3, 3], "R1-anchored", [2, 2, 2, 1, 3]),
            ((3,), [1, 3, 3, 3, 3], "R2-segments", [1, 3, 2, 2, 3]),
        ]
        for clues, domains, rule, expected in cases:
            for derive in (deductions, justified_rules):
                result = derive(clues, domains, int(rule[1]), AnalysisBudget())
                self.assertEqual(result[rule], expected)
        self.assertNotIn("R0-empty", deductions((1,), [3]*5, 0, AnalysisBudget()))
        self.assertNotIn("R0-packed", deductions((2, 2), [3]*6, 0, AnalysisBudget()))
        self.assertNotIn("R0-cleanup", deductions((Clue(2, 2), Clue(1, 4)), [7, 2, 7, 7, 7, 4, 7], 0, AnalysisBudget()))
        self.assertEqual(deductions((3,), [3]*6, 1, AnalysisBudget())["R1-overlap"], [3]*6)
        self.assertEqual(deductions((1, 1), [3, 3, 2, 3, 3], 1, AnalysisBudget())["R1-anchored"], [3, 3, 2, 3, 3])
        # Two different possible owners of the anchor: R2 local consistency
        # misses the global gap obstruction; exact R3 excludes position 1.
        domains = [3, 3, 3, 2, 1, 3, 3]
        self.assertEqual(combine(domains, deductions((1, 2), domains, 2, AnalysisBudget())), domains)
        self.assertEqual(combine(domains, deductions((1, 2), domains, 3, AnalysisBudget())), [3, 1, 3, 2, 1, 3, 3])

    def test_weak_rules_never_call_full_support(self):
        with patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError), \
             patch("tools.puzzle_production.analysis_verifier.justified_support", side_effect=AssertionError):
            for derive in (deductions, justified_rules):
                derive((1, 2), [3, 3, 3, 2, 1, 3, 3], 2, AnalysisBudget())

    def test_eight_colors_contact_gap_and_partial_domains(self):
        colors = tuple(f"c{i}" for i in range(8))
        puzzle = validate_logic(wire([list(colors)], colors))
        trace = analyze(puzzle)
        self.assertEqual(trace["status"], "solved")
        verify_trace(puzzle, trace)
        rule = deductions((Clue(1, 2), Clue(1, 4)), [7]*3, 2, AnalysisBudget())["R2-segments"]
        self.assertEqual(rule, [3, 7, 5])
        self.assertEqual(deductions((1, 1), [3]*2, 0, AnalysisBudget())["R0-packed"], [0, 0])


class WaveTests(unittest.TestCase):
    def test_general_r3_wave_and_earlier_weak_fixpoints(self):
        p = validate_logic(wire(GENERAL_LINE))
        t = analyze(p)
        verify_trace(p, t)
        self.assertIn("R3", [w["family"] for w in t["waves"]])
        self.assertEqual(measurements(p, t)["highest_family_used"], "R3")
        bad = deepcopy(t)
        first_strong = next(i for i, w in enumerate(t["waves"]) if w["family"] == "R3")
        # Omit a preceding R2 wave, even with an otherwise correct strong suffix.
        bad["waves"].pop(first_strong - 1)
        with self.assertRaises(InvalidProof):
            verify_trace(p, bad)

    def test_small_grids_preserve_every_oracle_solution(self):
        for values in product(("empty", "ink"), repeat=6):
            matrix = [list(values[:3]), list(values[3:])]
            p = validate_logic(wire(matrix))
            t = analyze(p)
            verify_trace(p, t)
            self.assertNotEqual(t["status"], "contradiction")
            self.assertTrue(all(d & (1 if value == "empty" else 2)
                                for row, values in zip(t["final_domains"], matrix)
                                for d, value in zip(row, values)))

    def test_weak_fixpoints_and_synchronous_deduplication(self):
        puzzle = Puzzle(3, 2, ((3,), (3,)), ((2,),)*3)
        trace = analyze(puzzle)
        verify_trace(puzzle, trace)
        self.assertEqual([w["family"] for w in trace["waves"]], ["R0"])
        self.assertEqual(len(trace["waves"][0]["lines"]), 5)
        self.assertEqual(len(trace["waves"][0]["changes"]), 6)
        metrics = measurements(puzzle, trace)
        self.assertEqual(metrics["new_singletons"], 6)
        self.assertEqual(metrics["unique_changed_cells"], 6)
        self.assertEqual(metrics["waves"][0]["productive_fraction"], [5, 5])
        p = validate_logic(wire(FLOW))
        t = analyze(p)
        verify_trace(p, t)
        self.assertEqual([w["family"] for w in t["waves"]], ["R0", "R1", "R0", "R2", "R0"])
        with patch("tools.puzzle_production.analysis.next_wave", side_effect=AssertionError), \
             patch("tools.puzzle_production.analysis_rules.deductions", side_effect=AssertionError), \
             patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError):
            verify_trace(p, t)

    def test_partial_color_events_and_global_positions(self):
        p = validate_logic(wire(COLOR, ("blue", "red")))
        t = analyze(p)
        verify_trace(p, t)
        metrics = measurements(p, t)
        self.assertGreater(metrics["partial_change_events"], 0)
        self.assertGreater(metrics["cell_change_events"], metrics["unique_changed_cells"])
        self.assertEqual(metrics["new_singletons"], sum(d.bit_count() == 1 for row in t["final_domains"] for d in row))
        self.assertEqual(sum(w["first_changed_cells"] for w in metrics["waves"]), metrics["unique_changed_cells"])

    def test_symmetries_preserve_scalar_features(self):
        config = {"aggregation": {"format": "sd-aggregation-1", "min_family": 1,
            "max_productive_fraction": [1, 2], "cleanup_remaining_cells": 10}}
        for matrix, colors in ((FLOW, ("ink",)), (GENERAL_LINE, ("ink",)), (COLOR, ("blue", "red"))):
            variants = [matrix, matrix[::-1], [r[::-1] for r in matrix], list(map(list, zip(*matrix)))]
            if len(colors) == 2:
                variants.append([[{"empty": "empty", "blue": "z", "red": "a"}[v] for v in r] for r in matrix])
            reference = None
            for i, cells in enumerate(variants):
                names = ("a", "z") if i == 4 else colors
                p = validate_logic(wire(cells, names))
                t = analyze(p, config)
                verify_trace(p, t)
                m = measurements(p, t)
                # Axis-labelled workload and counts transform; scalar data do not.
                m.pop("workload")
                for wave in m["waves"]:
                    wave.pop("open_lines")
                    wave.pop("productive_lines")
                feature = (t["status"], m)
                if reference is None:
                    reference = feature
                self.assertEqual(feature, reference)

    def test_aborts_discard_entire_wave_and_retain_complete_prefix(self):
        p = validate_logic(wire(FLOW))
        complete = analyze(p)
        for max_lines in (0, 1, p.width + p.height - 1):
            t = analyze(p, budget=AnalysisBudget(max_lines=max_lines))
            self.assertEqual(t["status"], "aborted")
            self.assertEqual(t["waves"], [])
            self.assertEqual(t["final_domains"], p.unknown_grid())
            verify_trace(p, t)
        t = analyze(p, budget=AnalysisBudget(max_lines=p.width+p.height+1))
        self.assertEqual(t["waves"], complete["waves"][:1])
        verify_trace(p, t)
        for budget, reason in ((AnalysisBudget(seconds=0), "time_limit"),
                               (AnalysisBudget(max_rule_work=0), "rule_work_limit"),
                               (AnalysisBudget(max_waves=0), "wave_limit"),
                               (AnalysisBudget(cancelled=lambda: True), "cancelled")):
            t = analyze(p, budget=budget)
            self.assertEqual(t["status"], "aborted")
            self.assertEqual(t["reason"], reason)
            self.assertFalse(result_data(p, t)["line_analysis_complete"])
            verify_trace(p, t)
        with patch("tools.puzzle_production.analysis.BYTE_LIMIT", 1):
            t = analyze(p)
            self.assertEqual(t["reason"], "trace_byte_limit")
            self.assertEqual(t["waves"], [])
        with patch("tools.puzzle_production.analysis.deductions", side_effect=MemoryError):
            self.assertEqual(analyze(p)["reason"], "memory_limit")

    def test_terminal_statuses_and_tampered_complete_trace(self):
        contradiction = Puzzle(1, 1, ((1,),), ((),))
        t = analyze(contradiction)
        self.assertEqual(t["status"], "contradiction")
        self.assertEqual(t["waves"], [])
        verify_trace(contradiction, t)
        p = validate_logic(wire(FLOW))
        t = analyze(p)
        mutations = []
        for key, value in (("analysis_hash", "0"*64), ("analyzer", "stale"), ("status", "solved")):
            bad = deepcopy(t)
            bad[key] = value
            mutations.append(bad)
        bad = deepcopy(t)
        bad["waves"][0]["family"] = "R3"
        mutations.append(bad)
        bad = deepcopy(t)
        bad["waves"][0]["lines"].pop()
        mutations.append(bad)
        bad = deepcopy(t)
        bad["waves"][0]["changes"].append(deepcopy(bad["waves"][0]["changes"][0]))
        mutations.append(bad)
        bad = deepcopy(t)
        bad["waves"][0]["lines"][0]["rules"][0]["changes"][0]["after"] = 0
        mutations.append(bad)
        bad = deepcopy(t)
        bad["waves"] = bad["waves"][:-1]
        mutations.append(bad)
        for bad in mutations:
            with self.assertRaises(InvalidProof):
                verify_trace(p, bad)
        result = result_data(p, t)
        result["metrics"]["new_singletons"] += 1
        with self.assertRaises(InvalidProof):
            verify_result(p, t, result)

    def test_aggregation_is_explicit_exact_and_has_no_rating(self):
        p = Puzzle(3, 2, ((3,), (3,)), ((2,),)*3)
        config = {"aggregation": {"format": "sd-aggregation-1", "min_family": 0,
            "max_productive_fraction": [1, 1], "cleanup_remaining_cells": 6}}
        t = analyze(p, config)
        r = result_data(p, t)
        self.assertIsNone(r["level"])
        self.assertIsNone(r["method"])
        self.assertEqual(r["metrics"]["aggregation"], {"bottleneck_phases": 1, "durations": [1],
            "bottleneck_waves": 1, "longest_bottleneck": 1, "cleanup_suffix_waves": 1})
        self.assertIsNone(result_data(p, analyze(p))["metrics"]["aggregation"])
        self.assertEqual(digest(t), digest(analyze(p, config)))
        for fraction in ([1, 0], [2, 1], [True, 1], [1.0, 2]):
            bad = deepcopy(config)
            bad["aggregation"]["max_productive_fraction"] = fraction
            with self.assertRaises(InvalidInput):
                parameters(bad)


class FileTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.puzzle_production", *map(str, args)],
                              capture_output=True, text=True, timeout=30)

    def test_runtime_cli_new_output_only_and_separate_checker(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "definition.json"
            source.write_bytes(RUNTIME.read_bytes())
            sentinel = root / "registry.json"
            sentinel.write_bytes(b"unchanged\n")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            output = root / "analysis"
            run = self.cli("analyze-difficulty", "--input", source, "--input-kind", "runtime", "--output-dir", output)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            for name, data in before.items():
                self.assertEqual((root / name).read_bytes(), data)
            check = self.cli("check-analysis", "--input", source, "--bundle", output)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertTrue(json.loads(check.stdout)["report_verified"])
            report = load_json(output / "report.json")
            self.assertEqual(report["source"]["production_mode"], "unknown")
            self.assertEqual(report["target_check"], "matched_complete")
            self.assertNotEqual(report["result"]["analysis_hash"], report["source"]["engine_logic_hash"])
            rerun = self.cli("analyze-difficulty", "--input", source, "--output-dir", output)
            self.assertEqual(rerun.returncode, 2)
            second = analyze_file(source, root / "second", kind="runtime")
            self.assertEqual(second["result_hash"], report["result_hash"])
            self.assertEqual(second["result"], report["result"])

    def test_target_matrix_never_enters_deduction(self):
        raw = load_json(RUNTIME)
        p = runtime_logic(raw)
        raw["solution"] = {"not": "a matrix"}
        self.assertEqual(runtime_logic(raw).to_wire(), p.to_wire())
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "bad.json"
            write_json(source, raw)
            with self.assertRaises(InvalidInput):
                analyze_file(source, Path(temp) / "out", kind="runtime")
            trace = load_json(Path(temp) / "out" / "trace.json")
            self.assertEqual(trace, analyze(p))
            self.assertFalse((Path(temp) / "out" / "report.json").exists())

    def test_source_trace_report_and_binding_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "out"
            report = analyze_file(RUNTIME, output, kind="runtime")
            for change in (lambda r: r["result"]["metrics"].update(new_singletons=999),
                           lambda r: r["source"].update(runtime_revision=99),
                           lambda r: r.update(target_check="not_supplied"),
                           lambda r: r["verification"].update(line_analysis_complete=False),
                           lambda r: r["operation"]["analysis_usage"].update(lines=1000001),
                           lambda r: r["files"].update({"../foreign": {}})):
                bad = deepcopy(report)
                change(bad)
                bad["result_hash"] = digest(bad["result"])
                write_json(output / "report.json", bad)
                with self.assertRaises((InvalidProof, InvalidInput)):
                    check_bundle(RUNTIME, output)
            write_json(output / "report.json", report)
            source = root / "changed.json"
            raw = load_json(RUNTIME)
            raw["revision"] += 1
            write_json(source, raw)
            with self.assertRaises(InvalidProof):
                check_bundle(source, output)

    def test_r4_uses_existing_independent_proofs_separately(self):
        p = validate_logic(wire(MONO))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, pair, baseline = (root / name for name in ("input.json", "pair.json", "base.json"))
            write_json(source, p.to_wire())
            write_json(pair, solve(p, profile="paired-lines-mono"))
            write_json(baseline, solve(p))
            report = analyze_file(source, root / "out", proof_path=pair, baseline_path=baseline)
            self.assertTrue(report["result"]["r4"]["required"])
            self.assertFalse(report["result"]["line_analysis_complete"])
            self.assertTrue(report["result"]["deduction_complete"])
            self.assertIsNone(report["result"]["level"])
            self.assertEqual(report["result"]["metrics"]["wave_count"], len(analyze(p)["waves"]))
            check_bundle(source, root / "out")
            write_json(baseline, solve(p, Budget(max_lines=0)))
            incomplete = analyze_file(source, root / "incomplete-baseline", proof_path=pair, baseline_path=baseline)
            self.assertFalse(incomplete["result"]["r4"]["required"])
            self.assertEqual(incomplete["result"]["r4"]["necessity"], "unproven")
            self.assertTrue(incomplete["result"]["deduction_complete"])
            self.assertFalse(incomplete["result"]["line_analysis_complete"])
            check_bundle(source, root / "incomplete-baseline")
            # Old complete proofs still require all forced exclusions.
            old = solve(Puzzle(2, 1, ((2,),), ((1,), (1,))))
            old["steps"][0]["changes"].pop()
            with self.assertRaises(InvalidProof):
                verify(Puzzle(2, 1, ((2,),), ((1,), (1,))), old)
            forged = load_json(pair)
            forged["logic_hash"] = "0"*64
            write_json(pair, forged)
            with self.assertRaises(InvalidProof):
                analyze_file(source, root / "bad", proof_path=pair, baseline_path=baseline)

    def test_cli_statuses_and_verification_budget(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.cli("analyze-difficulty", "--input", RUNTIME, "--input-kind", "runtime",
                           "--output-dir", root / "abort", "--max-lines", 0)
            self.assertEqual(run.returncode, 4, run.stdout)
            report = load_json(root / "abort" / "report.json")
            self.assertEqual(report["result"]["status"], "aborted")
            self.assertFalse(report["result"]["deduction_complete"])
            run = self.cli("analyze-difficulty", "--input", RUNTIME, "--input-kind", "runtime",
                           "--output-dir", root / "verify-abort", "--verify-max-lines", 0)
            self.assertEqual(run.returncode, 4, run.stdout)
            self.assertFalse((root / "verify-abort" / "report.json").exists())
            invalid = root / "invalid.json"
            invalid.write_text('{"width":true}', encoding="utf-8")
            run = self.cli("analyze-difficulty", "--input", invalid, "--output-dir", root / "invalid")
            self.assertEqual(run.returncode, 2)
            run = self.cli("analyze-difficulty", "--input", root / "missing", "--output-dir", root / "error")
            self.assertEqual(run.returncode, 5)
            self.assertEqual(json.loads(run.stdout)["status"], "technical_error")


if __name__ == "__main__":
    unittest.main()
