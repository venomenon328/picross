from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from oracle import grid_solutions
from tools.puzzle_production.contract import (Aborted, Budget, InvalidInput,
                                               InvalidProof, Puzzle, digest,
                                               load_json, validate_logic)
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify

FIXTURES = Path(__file__).parent / "fixtures"


class CoreTests(unittest.TestCase):
    def test_small_mathematical_cases(self):
        for name, status, count in [("deductive", "solved", 1),
                                    ("unique-stalled", "stalled", 1),
                                    ("ambiguous", "stalled", 2),
                                    ("contradictory", "contradiction", 0)]:
            with self.subTest(name=name):
                puzzle = validate_logic(load_json(FIXTURES / (name + ".json")))
                witnesses = grid_solutions(puzzle)
                self.assertEqual(len(witnesses), count)
                proof = solve(puzzle)
                self.assertEqual(proof["status"], status)
                result = verify(puzzle, proof)
                self.assertEqual(result["certified"], status == "solved")
                if status == "solved":
                    actual = [[int(value == ["ink"]) for value in row]
                              for row in proof["final_domains"]]
                    self.assertEqual(actual, [list(row) for row in witnesses[0]])

    def test_rectangles_and_one_dimensional_cases(self):
        puzzles = [Puzzle(1, 1, ((),), ((),)), Puzzle(1, 1, ((1,),), ((1,),)),
                   Puzzle(5, 1, ((1, 2),), ((1,), (), (1,), (1,), ())),
                   Puzzle(1, 5, ((1,), (), (1,), (1,), ()), ((1, 2),)),
                   Puzzle(4, 2, ((2,), (4,)), ((1,), (2,), (2,), (1,)))]
        for puzzle in puzzles:
            with self.subTest(puzzle=puzzle):
                witnesses = grid_solutions(puzzle)
                self.assertEqual(len(witnesses), 1)
                proof = solve(puzzle)
                self.assertTrue(verify(puzzle, proof)["certified"])

    def test_well_formed_contradictions_are_not_format_errors(self):
        for puzzle in [Puzzle(2, 1, ((3,),), ((), ())),
                       Puzzle(1, 1, ((1,),), ((),))]:
            validated = validate_logic(puzzle.to_wire())
            proof = solve(validated)
            self.assertEqual(proof["status"], "contradiction")
            self.assertFalse(verify(validated, proof)["certified"])

    def test_line_orders_have_same_fixpoint(self):
        for name in ("deductive", "unique-stalled", "ambiguous"):
            puzzle = validate_logic(load_json(FIXTURES / (name + ".json")))
            proofs = [solve(puzzle, order=order) for order in
                      ("rows-first", "columns-first", "reverse")]
            for proof in proofs:
                verify(puzzle, proof)
            self.assertEqual(len({digest(p["final_domains"]) for p in proofs}), 1)

    def test_abort_and_cancellation_are_never_certificates(self):
        puzzle = Puzzle(3, 3, ((1,), (3,), (1,)), ((1,), (3,), (1,)))
        for budget in (Budget(max_lines=0), Budget(seconds=0),
                       Budget(cancelled=lambda: True), Budget(max_lines=1)):
            proof = solve(puzzle, budget)
            self.assertEqual(proof["status"], "aborted")
            self.assertFalse(verify(puzzle, proof)["certified"])
        with self.assertRaises(Aborted):
            verify(puzzle, solve(puzzle), Budget(max_lines=0))

    def test_strict_logic_validation_and_hash_identity(self):
        obj = Puzzle(2, 2, ((1,), (1,)), ((1,), (1,))).to_wire()
        a = validate_logic(obj)
        b = validate_logic(dict(reversed(list(obj.items()))))
        self.assertEqual(a.logic_hash, b.logic_hash)
        variants = []
        for key, value in [("width", True), ("height", 0), ("width", 101),
                           ("width", 2.0), ("initial_domain", ["ink"]),
                           ("colors", ["red"]), ("row_clues", [[]]),
                           ("solution", [[0, 1], [1, 0]]), ("motif", "name"),
                           ("image", "target.png")]:
            bad = deepcopy(obj)
            bad[key] = value
            variants.append(bad)
        for clue in ({"length": 0, "color": "ink"},
                     {"length": True, "color": "ink"},
                     {"length": 1, "color": "red"}):
            bad = deepcopy(obj)
            bad["row_clues"][0] = [clue]
            variants.append(bad)
        bad = deepcopy(obj)
        bad["rules"]["same_color_gap"] = True
        variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad), self.assertRaises(InvalidInput):
                validate_logic(bad)


class ProofAttackTests(unittest.TestCase):
    def setUp(self):
        self.puzzle = Puzzle(3, 3, ((1,), (3,), (1,)), ((1,), (3,), (1,)))
        self.proof = solve(self.puzzle)
        self.assertTrue(verify(self.puzzle, self.proof)["certified"])

    def reject(self, mutate):
        proof = deepcopy(self.proof)
        mutate(proof)
        with self.assertRaises(InvalidProof):
            verify(self.puzzle, proof)

    def test_manipulated_binding_steps_start_and_end(self):
        self.reject(lambda p: p.update(logic_hash="0" * 64))
        self.reject(lambda p: p.update(profile_hash="0" * 64))
        self.reject(lambda p: p["profile"].update(search=True))
        self.reject(lambda p: p["profile"].update(version=True))
        self.reject(lambda p: p.update(initial_domains=p["final_domains"]))
        self.reject(lambda p: p["steps"][0]["changes"][0].update(after=["empty"]))
        self.reject(lambda p: p["steps"][0]["changes"][0].update(before=["ink"]))
        self.reject(lambda p: p["steps"][0].update(index=True))
        self.reject(lambda p: p["steps"][0]["changes"][0].update(offset=0.0))
        self.reject(lambda p: p["steps"].pop())
        self.reject(lambda p: p["steps"].reverse())
        self.reject(lambda p: p["final_domains"][0].__setitem__(0, ["ink"]))
        self.reject(lambda p: p.update(status="contradiction", contradiction={"axis": "row", "index": 0}))
        changed = Puzzle(3, 3, ((2,), (3,), (1,)), self.puzzle.columns)
        with self.assertRaises(InvalidProof):
            verify(changed, self.proof)

    def test_correct_truncated_trace_is_not_a_fixpoint(self):
        partial = solve(self.puzzle, Budget(max_lines=2))
        self.assertEqual(partial["status"], "aborted")
        self.assertGreater(len(partial["steps"]), 0)
        self.assertTrue(verify(self.puzzle, partial)["proof_verified"])
        partial.update(status="stalled", reason=None)
        with self.assertRaisesRegex(InvalidProof, "Not a true fixpoint"):
            verify(self.puzzle, partial)
        partial.update(status="solved")
        with self.assertRaises(InvalidProof):
            verify(self.puzzle, partial)

    def test_no_steps_no_start_assumptions(self):
        self.reject(lambda p: p.update(steps=[]))
        self.reject(lambda p: p.update(status="stalled"))
        self.reject(lambda p: p.update(status="aborted", reason=None))

    def test_verification_does_not_call_solver(self):
        with patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError), \
                patch("tools.puzzle_production.solver.solve", side_effect=AssertionError):
            self.assertTrue(verify(self.puzzle, self.proof)["certified"])

    def test_complete_end_grid_is_checked_against_clues(self):
        # Poison only the checker's support routine to let a fake complete grid
        # through replay. Direct run extraction must still reject the end raster.
        fake = deepcopy(self.proof)
        fake["steps"] = []
        fake["final_domains"] = [[["ink"]] * 3 for _ in range(3)]
        fake["steps"] = [
            {"axis": "row", "index": y,
             "changes": [{"offset": x, "before": ["empty", "ink"], "after": ["ink"]}
                         for x in range(3)]} for y in range(3)]
        with patch("tools.puzzle_production.verifier.justified_support", return_value=[2] * 3):
            with self.assertRaisesRegex(InvalidProof, "violates the clues"):
                verify(self.puzzle, fake)
