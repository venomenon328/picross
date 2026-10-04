from copy import deepcopy
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from oracle import colored_placements, colored_runs, support
from tools.puzzle_production.contract import (
    Budget, COLOR_LOGIC_FORMAT, Clue, InvalidInput, InvalidProof, LOGIC_BYTE_LIMIT,
    MAX_COLORS, Puzzle, canonical_bytes, digest, load_json, validate_logic,
)
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify

FIXTURES = Path(__file__).parent / "fixtures"


def from_grid(grid, colors=("blue", "green", "red", "yellow")):
    def clues(cells):
        return tuple(Clue(length, 1 << color) for length, color in colored_runs(cells))
    return validate_logic(Puzzle(len(grid[0]), len(grid), tuple(clues(row) for row in grid),
                                 tuple(clues(row[x] for row in grid) for x in range(len(grid[0]))),
                                 colors, COLOR_LOGIC_FORMAT).to_wire())


def oracle_support(clues, domains, colors):
    hints = tuple((c.length, c.color.bit_length() - 1) for c in clues)
    return support(colored_placements(len(domains), hints, colors), domains)


class ColorCoreTests(unittest.TestCase):
    def test_partial_exclusion_is_necessary_at_crossing(self):
        p = validate_logic(load_json(FIXTURES / "color-propagation.json"))
        proof = solve(p)
        self.assertTrue(verify(p, proof)["certified"])
        # Row 0 has red(1), blue(2); blue is present, but cannot be at (0,0).
        self.assertEqual(proof["steps"][0]["changes"][0],
                         {"offset": 0, "before": ["empty", "blue", "red"],
                          "after": ["empty", "red"]})
        # After the first four row deductions, column 0 sees [E/R,E/B,E/R,E/R].
        # Independently enumerate its placements. Restoring JUST (0,0)'s blue
        # option removes the deductions at both (0,0) AND (1,0).
        self.assertEqual(oracle_support(p.columns[0], [5, 3, 5, 5], 2), [1, 2, 4, 4])
        self.assertEqual(oracle_support(p.columns[0], [7, 3, 5, 5], 2), [3, 3, 4, 4])
        self.assertEqual(proof["steps"][4]["axis"], "column")
        self.assertEqual(proof["steps"][4]["index"], 0)
        # Counterfactual: iterate ALL lines with the independent exhaustive oracle,
        # but preserve only singleton conclusions. The model never completes.
        grid = p.unknown_grid()
        changed = True
        while changed:
            changed = False
            for axis, count in (("row", p.height), ("column", p.width)):
                for i in range(count):
                    clues, domains = p.line(grid, axis, i)
                    for offset, mask in enumerate(oracle_support(clues, domains, 2)):
                        if mask != domains[offset] and mask.bit_count() == 1:
                            y, x = (i, offset) if axis == "row" else (offset, i)
                            grid[y][x] = mask
                            changed = True
        self.assertEqual(grid, [[7, 7, 2, 7], [7, 7, 4, 7], [4, 2, 1, 1], [7, 7, 1, 7]])
        self.assertGreater(sum(m.bit_count() > 1 for row in grid for m in row), 0)

    def test_four_colors_rectangles_and_axis_boundaries(self):
        grids = [[[0]], [[1, 2, 3, 4, 0, 4, 4]],
                 [[(x // 2) % 5 for x in range(100)]],
                 [[(y // 2) % 5] for y in range(100)],
                 [[1, 2, 3, 4, 0], [1, 2, 3, 4, 4]]]
        for grid in grids:
            p = from_grid(grid)
            proof = solve(p)
            self.assertTrue(verify(p, proof)["certified"])
            self.assertEqual(proof["final_domains"],
                             [[["empty" if v == 0 else p.colors[v - 1]] for v in row] for row in grid])

    def test_status_orders_metadata_and_partial_abort(self):
        p = validate_logic(load_json(FIXTURES / "color-propagation.json"))
        stalled = from_grid([[1, 0], [0, 1]])
        bad = from_grid([[1]]).to_wire()
        bad["column_clues"] = [[{"length": 1, "color": "red"}]]
        for puzzle, status in ((p, "solved"), (stalled, "stalled"),
                               (validate_logic(bad), "contradiction")):
            proofs = [solve(puzzle, order=order) for order in
                      ("rows-first", "columns-first", "reverse")]
            for proof in proofs:
                self.assertEqual(proof["status"], status)
                self.assertEqual(verify(puzzle, proof)["certified"], status == "solved")
            if status != "contradiction":
                self.assertEqual(len({digest(q["final_domains"]) for q in proofs}), 1)
        for budget in (Budget(max_lines=1), Budget(seconds=0), Budget(cancelled=lambda: True)):
            partial = solve(p, budget)
            self.assertEqual(partial["status"], "aborted")
            self.assertFalse(verify(p, partial)["certified"])
        # Image/motif metadata stays outside the strict logic input.
        records = [{"logic": p.to_wire(), "image": "before.png", "motif": "old"},
                   {"logic": p.to_wire(), "image": "after.png", "motif": "renamed"}]
        self.assertEqual(solve(validate_logic(records[0]["logic"])),
                         solve(validate_logic(records[1]["logic"])))
        with self.assertRaises(InvalidInput):
            validate_logic(records[0])

    def test_palette_normalization_and_strict_boundaries(self):
        p = from_grid([[1, 2, 3, 4]])
        obj = p.to_wire()
        obj["colors"].reverse()
        obj["initial_domain"] = ["empty", *obj["colors"]]
        self.assertEqual(validate_logic(obj).logic_hash, p.logic_hash)
        names = tuple("c" + str(i) + "x" * 30 for i in range(MAX_COLORS))
        p1 = from_grid([[1, 0, 1]], ("red",))
        self.assertTrue(verify(p1, solve(p1))["certified"])
        p8 = from_grid([list(range(1, 9))], names)
        self.assertTrue(verify(p8, solve(p8))["certified"])
        for key, value in (("colors", []), ("colors", ["red"] * 2),
                           ("colors", ["c" + str(i) for i in range(9)]),
                           ("colors", ["empty"]), ("colors", ["Bad"]),
                           ("colors", ["x" * 33]), ("initial_domain", ["blue"]),
                           ("format", "picross-logic-v3")):
            bad = deepcopy(p.to_wire()); bad[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(InvalidInput):
                validate_logic(bad)
        for key, value in (("same_color_gap", 0), ("different_color_gap", 1),
                           ("different_color_gap", False), ("id", "mono-gap-v1")):
            bad = p.to_wire(); bad["rules"][key] = value
            with self.assertRaises(InvalidInput):
                validate_logic(bad)
        # Maximum accepted clue count and ID lengths fit the unchanged input cap.
        maximum = p8.to_wire(); maximum.update(width=100, height=100)
        maximum["row_clues"] = maximum["column_clues"] = [
            [{"length": 100, "color": names[i % 8]} for i in range(100)] for _ in range(100)]
        self.assertLess(len(canonical_bytes(maximum)) + 1, LOGIC_BYTE_LIMIT)
        self.assertEqual(validate_logic(maximum).max_proof_steps, 80_000)
        # Conservative canonical proof size: every cell loses each value singly,
        # one change per step, longest IDs, full final domains (an overestimate).
        # Pad even the short reserved empty ID to 32 characters: whichever value
        # is retained/removed, this overestimates every domain's byte length.
        names9 = ["empty".ljust(32, "x"), *names]
        cell_steps = [{"axis": "column", "index": 99,
                       "changes": [{"offset": 99, "before": names9[:k], "after": names9[:k - 1]}]}
                      for k in range(9, 1, -1)]
        upper = 10_000 * (sum(len(canonical_bytes(s)) + 1 for s in cell_steps)
                          + len(canonical_bytes(names9)) + 1) + 4096
        self.assertLess(upper, p8.proof_byte_limit)
        self.assertGreater(upper, 8 * 1024 * 1024)

    def test_unmodified_rp1_reference(self):
        # Generated with the old core at main@b18a234 BEFORE any RP-2 edits.
        proof_path = FIXTURES / "rp1-proof.json"
        self.assertEqual(hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                         "4886034235a2681ce4d7699ab212d978b1de9f7be3396d4edc034ff2c880a12d")
        p = validate_logic(load_json(FIXTURES / "deductive.json"))
        self.assertEqual(p.logic_hash, "dc6699f16ee7df3960bad1e8b457acfaa7605bd407fcfaaf8e083687c453d241")
        proof = load_json(proof_path)
        self.assertTrue(verify(p, proof)["certified"])
        self.assertEqual(solve(p), proof)


class ColorProofAttackTests(unittest.TestCase):
    def setUp(self):
        self.p = validate_logic(load_json(FIXTURES / "color-propagation.json"))
        self.proof = solve(self.p)

    def test_color_binding_and_exclusion_attacks(self):
        attacks = [lambda q: q.update(format="picross-proof-v1"),
                   lambda q: q.update(logic_hash="0" * 64),
                   lambda q: q.update(profile_hash="0" * 64),
                   lambda q: q["profile"].update(id="full-line-mono"),
                   lambda q: q["profile"].update(version=True),
                   lambda q: q["profile"].update(search=True),
                   lambda q: q["steps"][0]["changes"][0].update(after=["empty", "blue"]),
                   lambda q: q["steps"][0]["changes"][0].update(after=["red"]),
                   lambda q: q["steps"][0]["changes"].pop(),
                   lambda q: q["steps"][0]["changes"][0].update(before=["empty", "red"]),
                   lambda q: q.update(status="contradiction", contradiction={"axis": "row", "index": 0}),
                   lambda q: q["steps"].pop(),
                   lambda q: q["final_domains"][0].__setitem__(1, ["blue"]),
                   lambda q: q.update(steps=[q["steps"][0]] * (self.p.max_proof_steps + 1))]
        for attack in attacks:
            q = deepcopy(self.proof); attack(q)
            with self.assertRaises(InvalidProof):
                verify(self.p, q)
        for field in ("palette", "rule"):
            obj = self.p.to_wire()
            if field == "palette":
                obj["colors"].append("yellow"); obj["initial_domain"].append("yellow")
            else:
                obj["format"] = "picross-logic-v1"
                obj["colors"] = ["ink"]; obj["initial_domain"] = ["empty", "ink"]
                obj["rules"] = {"id": "mono-gap-v1", "same_color_gap": 1}
                for line in obj["row_clues"] + obj["column_clues"]:
                    for c in line:
                        c["color"] = "ink"
            with self.assertRaises(InvalidProof):
                verify(validate_logic(obj), self.proof)

    def test_partial_trace_is_not_a_fixpoint_or_complete(self):
        q = solve(self.p, Budget(max_lines=1))
        self.assertTrue(verify(self.p, q)["proof_verified"])
        self.assertGreater(len(q["steps"]), 0)
        q.update(status="stalled", reason=None)
        with self.assertRaisesRegex(InvalidProof, "Not a true fixpoint"):
            verify(self.p, q)
        q.update(status="solved")
        with self.assertRaises(InvalidProof):
            verify(self.p, q)

    def test_independence_and_direct_color_run_check(self):
        with patch("tools.puzzle_production.solver.solve", side_effect=AssertionError), \
                patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError):
            self.assertTrue(verify(self.p, self.proof)["certified"])
        p = from_grid([[1, 2, 3, 4]])
        # Wrong lengths, then correct lengths but swapped colors.
        for masks in ([2] * 4, [4, 2, 8, 16]):
            q = solve(p)
            values = [[p.colors[mask.bit_length() - 2]] for mask in masks]
            q["steps"] = [{"axis": "row", "index": 0, "changes": [
                {"offset": x, "before": ["empty", *p.colors], "after": values[x]}
                for x in range(4)]}]
            q["final_domains"] = [values]
            with patch("tools.puzzle_production.verifier.justified_support", return_value=masks):
                with self.assertRaisesRegex(InvalidProof, "violates the clues"):
                    verify(p, q)
