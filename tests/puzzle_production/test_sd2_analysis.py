"""SD2-A-T01: independent synthetic lines/grids, never catalog inputs."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.sd2_analysis import analyze
from tools.puzzle_production.sd2_contract import (AnalysisBudget,
                                                      parameters, result_data)
from tools.puzzle_production.sd2_rules import deductions
from tools.puzzle_production.sd2_verifier import justified_rules, verify_trace, verify_result
from tools.puzzle_production.sd2_io import analyze_file, check_bundle
from tools.puzzle_production.contract import (Aborted, Budget, Clue, InvalidInput, InvalidProof, Puzzle,
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


from tools.puzzle_production.analysis_io import runtime_logic
from tools.puzzle_production.sd2_profiles import profiles, ratio, span_signals, state_signals, bottlenecks
from fractions import Fraction

class RuleTests(unittest.TestCase):
    def test_long_combination_oracles_and_empty_local_sets(self):
        from test_paired import placements
        cases = [((3,), [3, 3, 2, 3, 2, 3, 3], 1),
                 ((1, 2), [3, 3, 3, 2, 1, 3, 3], 1),
                 ((2, 2), [3, 2, 3, 1, 3, 2, 3], 1),
                 ((Clue(2, 2), Clue(1, 4)), [7, 3, 6, 5, 7, 1], 2),
                 ((Clue(1, 4), Clue(2, 2), Clue(1, 4)), [7, 4, 7, 3, 6, 7], 2),
                 ((3,), [1]*6, 1)]
        for clues, domains, colors in cases:
            legal = placements(clues, domains, colors)
            supported = [0]*len(domains)
            for row in legal:
                supported = [a | b for a, b in zip(supported, row)]
            for level in range(4):
                got = deductions(clues, domains, level, AnalysisBudget())
                self.assertEqual(got, justified_rules(clues, domains, level, AnalysisBudget()))
                for rule, values in got.items():
                    self.assertTrue(all(not (s & ~v) for s, v in zip(supported, values)), rule)
                if level == 3:
                    self.assertEqual(got["E3-support"], supported)

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
                        self.assertEqual(generated["E3-support"], supported)

    def test_positive_and_boundary_examples_for_each_subrule(self):
        cases = [
            ((), [3]*5, "E0-empty", [1]*5),
            ((Clue(2, 2), Clue(2, 4)), [7]*4, "E0-packed", [2, 2, 4, 4]),
            ((2, 2), [3]*5, "E0-packed", [2, 2, 1, 2, 2]),
            ((Clue(2, 2), Clue(1, 4)), [7, 2, 2, 7, 7, 4, 7], "E0-cleanup", [1, 2, 2, 1, 1, 4, 1]),
            ((3,), [3]*5, "E1-overlap", [3, 3, 2, 3, 3]),
            ((3,), [2, 3, 3, 3, 3], "E1-anchored", [2, 2, 2, 1, 3]),
            ((3,), [1, 3, 3, 3, 3], "E1-overlap", [1, 3, 2, 2, 3]),
        ]
        for clues, domains, rule, expected in cases:
            for derive in (deductions, justified_rules):
                result = derive(clues, domains, int(rule[1]), AnalysisBudget())
                self.assertEqual(result[rule], expected)
        self.assertNotIn("E0-empty", deductions((1,), [3]*5, 0, AnalysisBudget()))
        self.assertNotIn("E0-packed", deductions((2, 2), [3]*6, 0, AnalysisBudget()))
        self.assertNotIn("E0-cleanup", deductions((Clue(2, 2), Clue(1, 4)), [7, 2, 7, 7, 7, 4, 7], 0, AnalysisBudget()))
        self.assertEqual(deductions((3,), [3]*6, 1, AnalysisBudget())["E1-overlap"], [3]*6)
        self.assertEqual(deductions((1, 1), [3, 3, 2, 3, 3], 1, AnalysisBudget())["E1-anchored"], [3, 3, 2, 3, 3])
        # Two different possible owners of the anchor: E2 local consistency
        # misses the global gap obstruction; exact E3 excludes position 1.
        domains = [3, 3, 3, 2, 1, 3, 3]
        self.assertEqual(combine(domains, deductions((1, 2), domains, 2, AnalysisBudget())), domains)
        self.assertEqual(combine(domains, deductions((1, 2), domains, 3, AnalysisBudget())), [3, 1, 3, 2, 1, 3, 3])

    def test_weak_rules_never_call_full_support(self):
        with patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError), \
             patch("tools.puzzle_production.sd2_verifier.justified_support", side_effect=AssertionError):
            for derive in (deductions, justified_rules):
                derive((1, 2), [3, 3, 3, 2, 1, 3, 3], 2, AnalysisBudget())

    def test_eight_colors_contact_gap_and_partial_domains(self):
        colors = tuple(f"c{i}" for i in range(8))
        puzzle = validate_logic(wire([list(colors)], colors))
        trace = analyze(puzzle)
        self.assertEqual(trace["status"], "solved")
        verify_trace(puzzle, trace)
        rule = deductions((Clue(1, 2), Clue(1, 4)), [7]*3, 2, AnalysisBudget())["E2-combination"]
        self.assertEqual(rule, [3, 7, 5])
        self.assertEqual(deductions((1, 1), [3]*2, 0, AnalysisBudget())["E0-packed"], [0, 0])


class SD2WaveTests(unittest.TestCase):
    def test_separate_deadlines_start_on_use_and_remain_cumulative(self):
        with patch("time.monotonic", return_value=0) as clock:
            analysis = AnalysisBudget(seconds=20)
            checker = AnalysisBudget(seconds=20)
            clock.return_value = 100
            analysis.tick()
            clock.return_value = 110
            analysis.work()
            clock.return_value = 200
            checker.tick()
            with self.assertRaisesRegex(Aborted, "time_limit"):
                analysis.check()
            clock.return_value = 210
            checker.work()
            clock.return_value = 221
            with self.assertRaisesRegex(Aborted, "time_limit"):
                checker.check()

    def test_two_independent_anchors_require_combination(self):
        domains = [3, 3, 2, 3, 2, 3, 3]
        for derive in (deductions, justified_rules):
            self.assertEqual(combine(domains, derive((3,), domains, 1, AnalysisBudget())), domains)
            self.assertEqual(combine(domains, derive((3,), domains, 2, AnalysisBudget())),
                             [1, 1, 2, 2, 2, 1, 1])

    def test_small_grids_and_independent_trace_checker(self):
        for values in product(("empty", "ink"), repeat=6):
            p = validate_logic(wire([list(values[:3]), list(values[3:])]))
            trace = analyze(p)
            with patch("tools.puzzle_production.sd2_rules.deductions", side_effect=AssertionError), \
                 patch("tools.puzzle_production.sd2_analysis.next_wave", side_effect=AssertionError), \
                 patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError):
                verify_trace(p, trace)
            self.assertNotEqual(trace["status"], "contradiction")
            self.assertTrue(all(d & (1 if value == "empty" else 2)
                                for d, value in zip((d for r in trace["final_domains"] for d in r), values)))

    def test_complete_offer_weak_fixpoint_terminal_and_report_rejection(self):
        p = validate_logic(wire(GENERAL_LINE))
        trace = analyze(p)
        verify_trace(p, trace)
        self.assertIn("E3", [w["family"] for w in trace["waves"]])
        mutations = [lambda t: t.update(analysis_hash="0"*64),
                     lambda t: t.update(analyzer="stale"),
                     lambda t: t["waves"][0].update(family="E3"),
                     lambda t: t["waves"][0]["lines"].pop(),
                     lambda t: t["waves"][0]["changes"].append(deepcopy(t["waves"][0]["changes"][0])),
                     lambda t: t["waves"][0]["changes"][0].update(after=True),
                     lambda t: t["waves"].pop(0),
                     lambda t: t["final_domains"][0].__setitem__(0, 0),
                     lambda t: t.update(terminal=t["waves"][0]),
                     lambda t: t.update(extra="unknown")]
        for mutate in mutations:
            bad = deepcopy(trace)
            mutate(bad)
            with self.assertRaises(InvalidProof):
                verify_trace(p, bad)
        report = result_data(p, trace)
        report["profiles"]["demand"]["strong_information_fraction"] = [0, 1]
        with self.assertRaises(InvalidProof):
            verify_result(p, trace, report)
        for broken in (Puzzle(1, 1, ((1,),), ((),)), Puzzle(2, 1, ((3,),), ((1,), (1,)))):
            terminal = analyze(broken)
            self.assertEqual(terminal["status"], "contradiction")
            self.assertEqual(terminal["waves"], [])
            self.assertEqual(terminal["final_domains"], broken.unknown_grid())
            verify_trace(broken, terminal)
            terminal["terminal"]["lines"].pop()
            with self.assertRaises(InvalidProof):
                verify_trace(broken, terminal)

    def test_aborts_discard_whole_wave(self):
        p = validate_logic(wire(FLOW))
        complete = analyze(p)
        for limit in (0, 1, p.width + p.height - 1):
            trace = analyze(p, budget=AnalysisBudget(max_lines=limit))
            self.assertEqual(trace["waves"], [])
            self.assertEqual(trace["status"], "aborted")
            self.assertEqual(trace["final_domains"], p.unknown_grid())
            verify_trace(p, trace)
        trace = analyze(p, budget=AnalysisBudget(max_lines=p.width+p.height+1))
        self.assertEqual(trace["waves"], complete["waves"][:1])
        verify_trace(p, trace)
        for budget, reason in ((AnalysisBudget(seconds=0), "time_limit"),
                               (AnalysisBudget(max_rule_work=0), "rule_work_limit"),
                               (AnalysisBudget(max_waves=0), "wave_limit"),
                               (AnalysisBudget(cancelled=lambda: True), "cancelled")):
            trace = analyze(p, budget=budget)
            self.assertEqual(trace["reason"], reason)
            self.assertIsNone(result_data(p, trace)["level"])
            verify_trace(p, trace)
        with patch("tools.puzzle_production.sd2_analysis.BYTE_LIMIT", 1):
            self.assertEqual(analyze(p)["reason"], "trace_byte_limit")
        with patch("tools.puzzle_production.sd2_analysis.deductions", side_effect=MemoryError):
            self.assertEqual(analyze(p)["reason"], "memory_limit")

    def test_partial_colors_and_symmetry_of_all_scalar_profiles(self):
        for matrix, colors in ((FLOW, ("ink",)), (GENERAL_LINE, ("ink",)), (COLOR, ("blue", "red"))):
            variants = [matrix, matrix[::-1], [r[::-1] for r in matrix], list(map(list, zip(*matrix)))]
            if len(colors) == 2:
                variants.append([[{"empty": "empty", "blue": "z", "red": "a"}[v] for v in r] for r in matrix])
            reference = None
            for i, cells in enumerate(variants):
                p = validate_logic(wire(cells, ("a", "z") if i == 4 else colors))
                trace = analyze(p)
                self.assertEqual(trace, analyze(p))
                verify_trace(p, trace)
                profile = profiles(p, trace)
                work = profile["workload"]
                self.assertEqual(work["new_singletons"], sum(d.bit_count() == 1 for row in trace["final_domains"] for d in row))
                self.assertEqual(sum(w["first_changed_cells"] for w in work["trajectory"]), work["unique_changed_cells"])
                if len(colors) == 2:
                    self.assertGreater(work["partial_change_events"], 0)
                    self.assertGreater(work["cell_change_events"], work["unique_changed_cells"])
                work["structure"].pop("width")
                work["structure"].pop("height")
                actual = (trace["status"], profile)
                if reference is None:
                    reference = actual
                self.assertEqual(actual, reference)

    def test_hand_calculated_profiles_and_color_normalization(self):
        p = Puzzle(3, 2, ((3,), (3,)), ((2,),)*3)
        trace = analyze(p)
        verify_trace(p, trace)
        profile = profiles(p, trace)
        self.assertEqual(len(trace["waves"][0]["lines"]), 5)
        self.assertEqual(profile["demand"]["information_by_family"]["E0"], [1, 1])
        self.assertEqual(profile["search"]["trajectory"][0]["offer"], [1, 1])
        self.assertEqual(profile["search"]["trajectory"][0]["gain"], [1, 1])
        self.assertEqual(profile["workload"]["new_singletons"], 6)
        self.assertEqual(profile["workload"]["fill_spans"], 2)
        self.assertEqual(profile["workload"]["trajectory"][0]["fill_run_lengths"], {"2": 3, "3": 2})
        self.assertEqual(profile["workload"]["structure"]["short_blocks"], 3)
        state = state_signals(p, trace["final_domains"], AnalysisBudget())
        self.assertEqual(state["open_lines"], 0)
        self.assertEqual(state["solved_lines"], 5)
        self.assertIsNone(state["placement_freedom"])
        self.assertIsNone(state["color_options"])
        self.assertIsNone(ratio(0, 0))
        for colors in (("a",), tuple(f"c{i}" for i in range(8))):
            p = validate_logic(wire([list(colors)], colors))
            trace = analyze(p)
            verify_trace(p, trace)
            self.assertEqual(profiles(p, trace)["demand"]["information_by_family"]["E0"], [1, 1])
        stalled = Puzzle(2, 2, ((1,),)*2, ((1,),)*2)
        empty = profiles(stalled, analyze(stalled))
        self.assertIsNone(empty["demand"]["highest_family"])
        self.assertEqual(empty["search"]["bottleneck_phases"], [])
        self.assertEqual(empty["search"]["peak_strain"], [0, 1])
        self.assertEqual(empty["workload"]["unique_changed_cells"], 0)

    def test_spans_and_early_late_recurrent_bottlenecks(self):
        def changes(positions):
            return [{"row": y, "column": x, "before": 3, "after": 2} for y, x in positions]
        long = span_signals(changes([(0, x) for x in range(8)]))
        pieces = span_signals(changes([(0, x*2) for x in range(8)]))
        self.assertEqual((long["fill_spans"], pieces["fill_spans"]), (1, 8))
        self.assertEqual((long["isolated_fills"], pieces["isolated_fills"]), (0, 8))
        series = [{"bottleneck": b, "progress_before": progress, "strain": [9, 16]}
                  for b, progress in ((True, [0, 1]), (True, [1, 4]), (False, [1, 3]),
                                      (True, [1, 2]), (False, [3, 4]), (True, [7, 8]))]
        phases = bottlenecks(series)
        self.assertEqual([p["duration"] for p in phases], [2, 1, 1])
        self.assertEqual([p["stage"] for p in phases], ["early", "late", "late"])
        self.assertEqual([(p["start"], p["end"]) for p in phases], [(0, 2), (3, 4), (5, 6)])


class FileTests(unittest.TestCase):
    def test_closed_formats_limits_and_legacy_rejection(self):
        from tools.puzzle_production.sd2_io import _bytes, _json
        from tools.puzzle_production.analysis_io import check_bundle as old_check
        from tools.puzzle_production.difficulty_rating import require_method
        for raw in (b'{"a":1,"a":2}', b'{"n":NaN}', b'{"n":1e999}', b'"\\ud800"', b'\xef\xbb\xbf{}'):
            with self.assertRaises(InvalidInput):
                _json(raw)
        with self.assertRaises(InvalidInput):
            parameters({"profile": "picross-difficulty-0.4"})
        require_method("picross-difficulty-0.3", {"aggregation": None})
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "out"
            analyze_file(RUNTIME, output, kind="runtime")
            with self.assertRaises(InvalidProof):
                old_check(RUNTIME, output, method="picross-difficulty-0.3")
            (output / "rating.json").write_text('{}\n', encoding="utf-8")
            with self.assertRaises(InvalidProof):
                check_bundle(RUNTIME, output)
            with self.assertRaises(InvalidInput):
                _bytes(RUNTIME, 1)
            with self.assertRaises(InvalidInput):
                analyze_file(RUNTIME, root / "missing-pair", proof_path=root / "proof")

    def test_state_clues_and_profile_work_budget(self):
        p = Puzzle(5, 1, ((1, 1),), ((1,), (1,), (1,), (1,), (1,)))
        state = state_signals(p, p.unknown_grid(), AnalysisBudget())
        self.assertEqual(state["open_blocks"], 7)
        self.assertEqual(state["open_short_blocks"], 7)
        self.assertEqual(state["undetermined_blocks"], 2)
        self.assertEqual(state["undetermined_short_blocks"], 2)
        self.assertEqual(state["open_hint_colors"], 1)
        from tools.puzzle_production.contract import Aborted
        with self.assertRaises(Aborted):
            state_signals(p, p.unknown_grid(), AnalysisBudget(max_rule_work=0))
        solved = Puzzle(3, 2, ((3,),)*2, ((2,),)*3)
        with self.assertRaises(Aborted):
            result_data(solved, analyze(solved), budget=AnalysisBudget(max_rule_work=0))

    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.puzzle_production.sd2_cli", *map(str, args)],
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
            run = self.cli("analyze", "--input", source, "--input-kind", "runtime", "--output-dir", output)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            for name, data in before.items():
                self.assertEqual((root / name).read_bytes(), data)
            check = self.cli("check", "--input", source, "--bundle", output)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertTrue(json.loads(check.stdout)["report_verified"])
            report = load_json(output / "report.json")
            self.assertEqual(report["source"]["production_mode"], "unknown")
            self.assertEqual(report["target_check"], "matched_complete")
            self.assertNotEqual(report["result"]["analysis_hash"], report["source"]["engine_logic_hash"])
            rerun = self.cli("analyze", "--input", source, "--output-dir", output)
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
            for change in (lambda r: r["result"]["profiles"]["workload"].update(new_singletons=999),
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
            self.assertEqual(len(report["result"]["profiles"]["demand"]["trajectory"]), len(analyze(p)["waves"]))
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
            run = self.cli("analyze", "--input", RUNTIME, "--input-kind", "runtime",
                           "--output-dir", root / "abort", "--max-lines", 0)
            self.assertEqual(run.returncode, 4, run.stdout)
            report = load_json(root / "abort" / "report.json")
            self.assertEqual(report["result"]["status"], "aborted")
            self.assertFalse(report["result"]["deduction_complete"])
            run = self.cli("analyze", "--input", RUNTIME, "--input-kind", "runtime",
                           "--output-dir", root / "verify-abort", "--verify-max-lines", 0)
            self.assertEqual(run.returncode, 4, run.stdout)
            self.assertFalse((root / "verify-abort" / "report.json").exists())
            invalid = root / "invalid.json"
            invalid.write_text('{"width":true}', encoding="utf-8")
            run = self.cli("analyze", "--input", invalid, "--output-dir", root / "invalid")
            self.assertEqual(run.returncode, 2)
            run = self.cli("analyze", "--input", root / "missing", "--output-dir", root / "error")
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)["status"], "invalid_input")
