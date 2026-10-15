"""Synthetic exhaustive oracles and adversarial diagnosis evidence tests."""
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production.contract import (Puzzle, digest,
                                            load_json, validate_logic, write_json)
from tools.puzzle_production.diagnosis import (DiagnosisBudget, check_diagnosis,
                                              diagnose, diagnose_file, file_binding)
from tools.puzzle_production.diagnosis_cli import main
from tools.puzzle_production.diagnosis_verifier import (InvalidDiagnosis,
                                                       WITNESS_FORMAT, verify_witness)
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify

FIXTURES = Path(__file__).parent / "fixtures"


def oracle_clues(line):
    """Independent group enumeration over complete semantic cell values."""
    return tuple((len(list(group)), color) for color, group in itertools.groupby(line)
                 if color != "empty")


def logic_from_clues(width, height, rows, columns, colors):
    wire = Puzzle(width, height, ((),) * height, ((),) * width).to_wire()
    if colors != ("ink",):
        wire.update(format="picross-logic-v2", colors=list(colors),
                    initial_domain=["empty", *colors],
                    rules={"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0})
    wire["row_clues"] = [[{"length": n, "color": c} for n, c in line] for line in rows]
    wire["column_clues"] = [[{"length": n, "color": c} for n, c in line] for line in columns]
    return validate_logic(wire)


def color_version(puzzle):
    wire = puzzle.to_wire()
    wire.update(format="picross-logic-v2", colors=["blue", "ink"],
                initial_domain=["empty", "blue", "ink"],
                rules={"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0})
    return validate_logic(wire)


class SearchTests(unittest.TestCase):
    def test_exhaustive_small_mono_and_color_oracles(self):
        # Enumerate every clue combination as well as every full matrix. Includes
        # globally inconsistent puzzles whose individual lines are all feasible.
        for width, height, colors in ((2, 3, ("ink",)), (2, 2, ("blue", "red"))):
            values = ("empty", *colors)
            solutions = {}
            for cells in itertools.product(values, repeat=width * height):
                rows = tuple(oracle_clues(cells[y * width:(y + 1) * width])
                             for y in range(height))
                columns = tuple(oracle_clues(cells[x::width]) for x in range(width))
                solutions.setdefault((rows, columns), []).append(cells)
            row_options = sorted({oracle_clues(line) for line in
                                  itertools.product(values, repeat=width)})
            col_options = sorted({oracle_clues(line) for line in
                                  itertools.product(values, repeat=height)})
            for rows in itertools.product(row_options, repeat=height):
                for columns in itertools.product(col_options, repeat=width):
                    expected = solutions.get((rows, columns), [])
                    puzzle = logic_from_clues(width, height, rows, columns, colors)
                    result = diagnose(puzzle)
                    self.assertEqual(result["status"], "no_solution" if not expected else
                                     "unique" if len(expected) == 1 else "multiple",
                                     (rows, columns))
                    self.assertEqual(result["search_complete"], len(expected) < 2)
                    self.assertEqual(len(result["witnesses"]), min(2, len(expected)))
                    for witness in result["witnesses"]:
                        cells = tuple(value for row in witness["matrix"] for value in row)
                        self.assertIn(cells, expected)

    def test_unique_despite_independently_verified_line_fixpoint(self):
        mono = validate_logic(load_json(FIXTURES / "unique-stalled.json"))
        for puzzle in (mono, color_version(mono)):
            original = puzzle.to_wire()
            proof = solve(puzzle)
            self.assertEqual(proof["status"], "stalled")
            self.assertFalse(verify(puzzle, proof)["certified"])
            result = diagnose(puzzle)
            self.assertEqual(result["status"], "unique")
            self.assertGreater(result["statistics"]["nodes"], 1)
            self.assertFalse(result["certified"])
            incomplete = diagnose(puzzle, DiagnosisBudget(max_nodes=2))
            self.assertEqual(incomplete["status"], "unknown")
            self.assertEqual(len(incomplete["witnesses"]), 1)
            self.assertFalse(incomplete["search_complete"])
            self.assertEqual(puzzle.to_wire(), original)
            self.assertEqual(solve(puzzle), proof)

    def test_exhaustive_unsatisfiability_after_line_fixpoint_and_deeper_search(self):
        # Every individual unknown line has full support, but totals disagree.
        impossible = Puzzle(4, 4, ((1,),) * 4, ((1, 1),) * 4)
        multiple = Puzzle(4, 4, ((1,),) * 4, ((1,),) * 4)
        for base, status in ((impossible, "no_solution"), (multiple, "multiple")):
            for puzzle in (base, color_version(base)):
                proof = solve(puzzle)
                self.assertEqual(verify(puzzle, proof)["status"], "stalled")
                result = diagnose(puzzle)
                self.assertEqual(result["status"], status)
                self.assertGreater(result["statistics"]["nodes"], 1)
                result = diagnose(puzzle, DiagnosisBudget(max_nodes=1))
                self.assertEqual(result["status"], "unknown")

    def test_cumulative_deterministic_budgets_before_and_after_one_solution(self):
        mono = Puzzle(2, 2, ((1,), (1,)), ((1,), (1,)))
        for puzzle in (mono, color_version(mono)):
            for budget in (DiagnosisBudget(max_nodes=0), DiagnosisBudget(max_lines=0)):
                result = diagnose(puzzle, budget)
                self.assertEqual(result["status"], "unknown")
                self.assertEqual(result["witnesses"], [])
            one = diagnose(puzzle, DiagnosisBudget(max_nodes=2))
            self.assertEqual(one["status"], "unknown")
            self.assertEqual(one["reason"], "node_limit")
            self.assertEqual(len(one["witnesses"]), 1)
            self.assertFalse(one["search_complete"])
            # All search and witness work consumes the SAME line counter.
            used = one["statistics"]["line_evaluations"]
            limited = diagnose(puzzle, DiagnosisBudget(max_lines=used))
            self.assertEqual(limited["status"], "unknown")
            self.assertEqual(limited["reason"], "work_limit")
            self.assertEqual(len(limited["witnesses"]), 1)
            # Exhaustion during necessary witness checking cannot count that witness.
            during_check = diagnose(puzzle, DiagnosisBudget(max_lines=used - 1))
            self.assertEqual(during_check["witnesses"], [])
            self.assertEqual(during_check["status"], "unknown")
            self.assertGreater(during_check["statistics"]["witness_line_evaluations"], 0)

    def test_time_cancellation_memory_and_internal_error(self):
        puzzle = Puzzle(1, 1, ((1,),), ((1,),))
        for budget, reason in ((DiagnosisBudget(seconds=0), "time_limit"),
                               (DiagnosisBudget(cancelled=lambda: True), "cancelled")):
            self.assertEqual(diagnose(puzzle, budget)["reason"], reason)
        with patch("tools.puzzle_production.diagnosis.line_support", side_effect=MemoryError):
            self.assertEqual(diagnose(puzzle)["reason"], "memory_limit")
        with patch("tools.puzzle_production.diagnosis.line_support", side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                diagnose(puzzle)

    def test_1d_rectangles_full_tool_limits_and_color_spacing(self):
        for values in (("red", "blue"), ("red", "empty", "red"),
                       ("red", "empty", "blue"), ("empty",),
                       tuple("c" + str(i) for i in range(8)), ("red",) * 100):
            colors = tuple(sorted(set(values) - {"empty"})) or ("red",)
            for vertical in (False, True):
                matrix = [[value] for value in values] if vertical else [list(values)]
                width, height = len(matrix[0]), len(matrix)
                puzzle = logic_from_clues(width, height,
                                         tuple(oracle_clues(row) for row in matrix),
                                         tuple(oracle_clues(col) for col in zip(*matrix)), colors)
                result = diagnose(puzzle)
                self.assertEqual(result["status"], "unique")
                self.assertEqual(result["witnesses"][0]["matrix"], matrix)
        # Same-color blocks cannot touch; this is well-formed but impossible.
        puzzle = logic_from_clues(2, 1, (((1, "red"), (1, "red")),),
                                 (((1, "red"),),) * 2, ("red",))
        self.assertEqual(diagnose(puzzle)["status"], "no_solution")
        self.assertEqual(diagnose(Puzzle(100, 100, ((),) * 100, ((),) * 100))["status"], "unique")

    def test_existing_profile_and_proof_compatibility(self):
        puzzle = validate_logic(load_json(FIXTURES / "deductive.json"))
        proof = load_json(FIXTURES / "rp1-proof.json")
        before = digest(proof)
        self.assertTrue(verify(puzzle, proof)["certified"])
        self.assertEqual(diagnose(puzzle)["status"], "unique")
        self.assertEqual(digest(proof), before)
        self.assertEqual(digest(puzzle.profile),
                         "e49e4cd74c4c4c02e08170ce670a40f48b82490a6bea52c3c764143d7a0af4b0")


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="picross-139-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.input = self.root / "logic.json"
        self.puzzle = Puzzle(2, 2, ((1,), (1,)), ((1,), (1,)))
        write_json(self.input, self.puzzle.to_wire())
        self.bundle = self.root / "diagnosis"

    def invoke(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.puzzle_production", *args],
                              capture_output=True, text=True, timeout=30)

    def test_fresh_cli_bundle_and_separate_witness_process(self):
        proc = self.invoke("diagnose", "--input", str(self.input), "--output-dir", str(self.bundle))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = load_json(self.bundle / "diagnosis.json")
        self.assertEqual(report["status"], "multiple")
        self.assertEqual(report["input"], file_binding(self.bundle / "input.json"))
        proc = self.invoke("check-diagnosis", "--input", str(self.input), "--bundle", str(self.bundle))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["confirmed_status"], "multiple")
        self.assertFalse(json.loads(proc.stdout)["search_replayed"])
        before = (self.bundle / "diagnosis.json").read_bytes()
        self.assertEqual(self.invoke("diagnose", "--input", str(self.input), "--output-dir",
                                     str(self.bundle)).returncode, 2)
        self.assertEqual((self.bundle / "diagnosis.json").read_bytes(), before)

    def test_file_reports_for_all_statuses_mono_and_color(self):
        for i, base in enumerate((self.puzzle, Puzzle(1, 1, ((1,),), ((1,),)),
                                  Puzzle(1, 1, ((1,),), ((),)))):
            for j, puzzle in enumerate((base, color_version(base))):
                write_json(self.input, puzzle.to_wire())
                for limited in (False, True):
                    bundle = self.root / f"case-{i}-{j}-{limited}"
                    result = diagnose_file(self.input, bundle,
                                           DiagnosisBudget(max_nodes=0 if limited else 1000))
                    self.assertEqual(result["status"], "unknown" if limited else
                                     ("multiple", "unique", "no_solution")[i])
                    checked = check_diagnosis(self.input, bundle)
                    self.assertEqual(checked["reported_status"], result["status"])
                    self.assertEqual(checked["confirmed_status"],
                                     "multiple" if result["status"] == "multiple" else None)

    def test_tampered_identical_wrongly_bound_witnesses(self):
        result = diagnose_file(self.input, self.bundle)
        path = self.bundle / "solution-2.json"
        original = load_json(path)
        first = load_json(self.bundle / "solution-1.json")
        for change in (lambda w: w["matrix"][0].__setitem__(0, "empty"),
                       lambda w: w.__setitem__("logic_hash", "0" * 64),
                       lambda w: w.__setitem__("matrix", first["matrix"]),
                       lambda w: w["matrix"][0].__setitem__(0, True)):
            witness = deepcopy(original)
            change(witness)
            write_json(path, witness)
            # First detect byte tampering, then check semantics even if rehashed.
            with self.assertRaises(InvalidDiagnosis):
                check_diagnosis(self.input, self.bundle)
            changed = deepcopy(result)
            changed["witnesses"][1] = file_binding(path)
            write_json(self.bundle / "diagnosis.json", changed)
            with self.assertRaises(InvalidDiagnosis):
                check_diagnosis(self.input, self.bundle)
            write_json(self.bundle / "diagnosis.json", result)
        write_json(path, original)
        self.input.write_bytes(self.input.read_bytes() + b"\n")
        with self.assertRaises(InvalidDiagnosis):
            check_diagnosis(self.input, self.bundle)

    def test_malformed_report_bindings_and_budget_metadata(self):
        result = diagnose_file(self.input, self.bundle)
        mutations = [
            lambda r: r.__setitem__("status", []),
            lambda r: r.__setitem__("reason", {}),
            lambda r: r.__setitem__("search_complete", True),
            lambda r: r["tool"].__setitem__("version", True),
            lambda r: r["witnesses"][0].__setitem__("file", "../logic.json"),
            lambda r: r["witnesses"][0].__setitem__("bytes", True),
            lambda r: r["budgets"].__setitem__("max_nodes", 0),
            lambda r: r["statistics"].__setitem__("witness_line_evaluations", 0),
        ]
        for mutation in mutations:
            changed = deepcopy(result)
            mutation(changed)
            write_json(self.bundle / "diagnosis.json", changed)
            with self.assertRaises(InvalidDiagnosis):
                check_diagnosis(self.input, self.bundle)
        (self.bundle / "diagnosis.json").write_text('{"format":NaN}', encoding="utf-8")
        self.assertEqual(self.invoke("check-diagnosis", "--input", str(self.input),
                                     "--bundle", str(self.bundle)).returncode, 3)

    def test_written_witness_is_checked_before_it_can_support_a_verdict(self):
        real_load = load_json

        def corrupt_loaded(path, limit):
            witness = real_load(path, limit)
            witness["matrix"][0] = ["ink", "ink"]
            return witness

        with patch("tools.puzzle_production.diagnosis.load_evidence", side_effect=corrupt_loaded):
            with self.assertRaises(RuntimeError):
                diagnose_file(self.input, self.bundle)
        self.assertFalse((self.bundle / "diagnosis.json").exists())

    def test_invalid_inputs_budgets_stale_paths_and_errors(self):
        for args in (("--max-nodes", "-1"), ("--max-lines", "1000001"),
                     ("--seconds", "nan")):
            self.assertEqual(self.invoke("diagnose", "--input", str(self.input),
                                         "--output-dir", str(self.bundle), *args).returncode, 2)
        for data in (b'{"solution":[]}', b'{"width":1,"width":2}', b'{"x":NaN}'):
            self.input.write_bytes(data)
            self.assertEqual(self.invoke("diagnose", "--input", str(self.input),
                                         "--output-dir", str(self.root / hashlib.sha256(data).hexdigest())).returncode, 2)
        write_json(self.input, self.puzzle.to_wire())
        for exception, code in ((RuntimeError("fault"), 5), (MemoryError(), 4)):
            with patch("tools.puzzle_production.diagnosis_cli.diagnose_file", side_effect=exception):
                self.assertEqual(main(["diagnose", "--input", str(self.input),
                                       "--output-dir", str(self.bundle)]), code)
        proc = self.invoke("diagnose", "--input", str(self.input), "--output-dir",
                           str(self.bundle), "--max-nodes", "2")
        self.assertEqual(proc.returncode, 4)
        self.assertEqual(len(json.loads(proc.stdout)["witnesses"]), 1)

    def test_witness_checker_is_independent_of_search(self):
        with patch("tools.puzzle_production.diagnosis.line_support", side_effect=AssertionError):
            witness = {"format": WITNESS_FORMAT, "logic_hash": self.puzzle.logic_hash,
                       "matrix": [["ink", "empty"], ["empty", "ink"]]}
            self.assertEqual(verify_witness(self.puzzle, witness), witness["matrix"])


if __name__ == "__main__":
    unittest.main()
