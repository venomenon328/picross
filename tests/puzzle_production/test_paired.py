"""Fixed technical oracles for #139 B/C, never production puzzle inputs."""
from copy import deepcopy
from itertools import product, combinations
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.puzzle_production.contract import (Aborted, Budget, Clue, InvalidInput, InvalidProof,
                                             Puzzle, load_json, validate_logic)
from tools.puzzle_production.solver import solve
from tools.puzzle_production.verifier import verify
from tools.puzzle_production.paired_solver import crossing_relation, pair_support
from tools.puzzle_production.paired_verifier import justified_relation, justified_pair


def wire(matrix, colors=("ink",)):
    def clues(line):
        result, last = [], "empty"
        for v in line:
            if v != "empty":
                if v == last:
                    result[-1]["length"] += 1
                else:
                    result.append({"length": 1, "color": v})
            last = v
        return result
    mono = colors == ("ink",)
    return {"format": "picross-logic-v1" if mono else "picross-logic-v2",
            "width": len(matrix[0]), "height": len(matrix), "colors": list(colors),
            "empty": "empty", "initial_domain": ["empty", *colors],
            "rules": {"id": "mono-gap-v1", "same_color_gap": 1} if mono else
                     {"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0},
            "row_clues": [clues(r) for r in matrix],
            "column_clues": [clues(r) for r in zip(*matrix)]}


MONO = [["empty"] * 4, ["empty"] * 4,
        ["empty", "ink", "ink", "empty"], ["ink", "empty", "empty", "ink"]]
COLOR = [[{".": "empty", "R": "red", "B": "blue"}[v] for v in r]
         for r in ("RBR..", "R...R", "...BR", "..RR.")]


def placements(clues, domains, colors):
    expected = [(c.length, c.color) if isinstance(c, Clue) else (c, 2) for c in clues]
    values = [1 << i for i in range(colors + 1)]
    out = []
    for seq in product(values, repeat=len(domains)):
        if any(not d & v for d, v in zip(domains, seq)):
            continue
        runs = []
        last = 1
        for v in seq:
            if v != 1:
                if v == last:
                    runs[-1] = (runs[-1][0] + 1, v)
                else:
                    runs.append((1, v))
            last = v
        if runs == expected:
            out.append(seq)
    return out


class PairedTests(unittest.TestCase):
    def test_required_examples_and_transposes(self):
        for matrix, colors, unknown in ((MONO, ("ink",), 8), (COLOR, ("blue", "red"), 12)):
            for cells in (matrix, list(map(list, zip(*matrix)))):
                p = validate_logic(wire(cells, colors))
                baseline = solve(p)
                self.assertEqual(verify(p, baseline)["status"], "stalled")
                self.assertEqual(sum(len(d) > 1 for r in baseline["final_domains"] for d in r), unknown)
                profile = "paired-lines-mono" if colors == ("ink",) else "paired-lines-color"
                proof = solve(p, profile=profile)
                with patch("tools.puzzle_production.paired_solver.pair_support", side_effect=AssertionError("solver called")), \
                     patch("tools.puzzle_production.solver.line_support", side_effect=AssertionError("solver called")):
                    checked = verify(p, proof)
                self.assertTrue(checked["certified"])
                self.assertEqual(proof["final_domains"], [[[v] for v in r] for r in cells])
                self.assertTrue(any(s["kind"] == "pair" for s in proof["steps"]))

    def test_two_position_relations_against_exhaustive_oracle(self):
        # All color clue lists induced by length-4 lines, with partial domains.
        clues_seen = {}
        for values in product(("empty", "a", "b"), repeat=4):
            p = validate_logic(wire([values], ("a", "b")))
            clues_seen[p.rows[0]] = None
        for clues in clues_seen:
            for domains in ([7] * 4, [3, 6, 5, 7], [1, 2, 4, 3]):
                legal = placements(clues, domains, 2)
                for i, j in combinations(range(4), 2):
                    expected = {(r[i], r[j]) for r in legal}
                    for routine in (crossing_relation, justified_relation):
                        self.assertEqual(routine(clues, domains, i, j, Budget()), expected)

    def test_pair_projections_against_small_full_enumeration(self):
        for matrix, colors in ((MONO, ("ink",)), (COLOR, ("blue", "red"))):
            p = validate_logic(wire(matrix, colors))
            for grid in (p.unknown_grid(), [[sum(1 << (["empty", *p.colors].index(v)) for v in d)
                                          for d in r] for r in solve(p)["final_domains"]]):
                for axis, count in (("row", p.height), ("column", p.width)):
                    for i, j in combinations(range(count), 2):
                        lines = [p.line(grid, axis, k) for k in (i, j)]
                        candidates = [placements(c, d, len(colors)) for c, d in lines]
                        relations = []
                        for x in range(len(lines[0][1])):
                            c, d = p.line(grid, "column" if axis == "row" else "row", x)
                            relations.append({(s[i], s[j]) for s in placements(c, d, len(colors))})
                        expected = [[0] * len(lines[0][1]) for _ in range(2)]
                        for a, b in product(*candidates):
                            if all((av, bv) in r for av, bv, r in zip(a, b, relations)):
                                for k, seq in enumerate((a, b)):
                                    for x, v in enumerate(seq):
                                        expected[k][x] |= v
                        for routine in (pair_support, justified_pair):
                            self.assertEqual(routine(p, grid, axis, i, j, Budget()), expected)

    def test_tampered_steps_bindings_and_statuses(self):
        p = validate_logic(wire(COLOR, ("blue", "red")))
        original = solve(p, profile="paired-lines-color")
        index = next(i for i, s in enumerate(original["steps"]) if s["kind"] == "pair")
        mutations = [lambda q: q["steps"][index]["indices"].reverse(),
                     lambda q: q["steps"][index]["changes"].pop(),
                     lambda q: q["steps"][index]["changes"][0].update(before=["empty"]),
                     lambda q: q["steps"][index]["changes"][0].update(after=["empty"]),
                     lambda q: q["steps"][index]["changes"][0].update(row=True),
                     lambda q: q["steps"].insert(index + 1, deepcopy(q["steps"][index])),
                     lambda q: q.update(logic_hash="0" * 64),
                     lambda q: q["profile"].update(search=True),
                     lambda q: q.update(format="picross-proof-v2"),
                     lambda q: q.update(status="stalled"),
                     lambda q: q["steps"][index].update(relations=[])]
        for mutate in mutations:
            bad = deepcopy(original)
            mutate(bad)
            with self.assertRaises(InvalidProof):
                verify(p, bad)
        baseline = solve(p)
        bad = deepcopy(original)
        line_steps = []
        for step in baseline["steps"]:
            changes = []
            for change in step["changes"]:
                y, x = (step["index"], change["offset"]) if step["axis"] == "row" else (change["offset"], step["index"])
                changes.append({"row": y, "column": x, "before": change["before"], "after": change["after"]})
            line_steps.append({"kind": "line", "axis": step["axis"], "indices": [step["index"]], "changes": changes})
        bad.update(steps=line_steps, final_domains=baseline["final_domains"], status="stalled")
        with self.assertRaisesRegex(InvalidProof, "paired-line fixpoint"):
            verify(p, bad)

    def test_nonadjacent_pairs_and_pair_contradiction(self):
        separated = [MONO[2], MONO[0], MONO[3], MONO[1]]
        for cells, axis in ((separated, "row"), (list(map(list, zip(*separated))), "column")):
            p = validate_logic(wire(cells))
            proof = solve(p, profile="paired-lines-mono")
            self.assertTrue(verify(p, proof)["certified"])
            grid = [[sum(1 << (["empty", *p.colors].index(v)) for v in d)
                     for d in r] for r in solve(p)["final_domains"]]
            before = [p.line(grid, axis, k)[1] for k in (0, 2)]
            projected = pair_support(p, grid, axis, 0, 2, Budget())
            self.assertNotEqual(projected, before)
            self.assertEqual(projected, justified_pair(p, grid, axis, 0, 2, Budget()))
        p = Puzzle(4, 4, ((1,),) * 4, ((1, 1),) * 4)
        self.assertEqual(verify(p, solve(p))["status"], "stalled")
        proof = solve(p, profile="paired-lines-mono")
        self.assertEqual(proof["contradiction"], {"kind": "pair", "axis": "row", "indices": [0, 1]})
        self.assertEqual(verify(p, proof)["status"], "contradiction")
        bad = deepcopy(solve(validate_logic(wire(MONO)), profile="paired-lines-mono"))
        bad.update(status="contradiction", contradiction=proof["contradiction"])
        with self.assertRaisesRegex(InvalidProof, "compatible relation"):
            verify(validate_logic(wire(MONO)), bad)

    def test_exact_inner_work_and_memory_boundaries(self):
        p = validate_logic(wire(COLOR, ("blue", "red")))
        for routine in (pair_support, justified_pair):
            measured = Budget()
            expected = routine(p, p.unknown_grid(), "row", 0, 1, measured)
            self.assertEqual(measured.pair_records, 0)
            for kind, used in (("max_pair_work", measured.pair_work), ("max_pair_records", measured.pair_peak_records)):
                self.assertGreater(used, 1)
                exact = Budget(**{kind: used})
                self.assertEqual(routine(p, p.unknown_grid(), "row", 0, 1, exact), expected)
                limited = Budget(**{kind: used - 1})
                with self.assertRaises(Aborted):
                    routine(p, p.unknown_grid(), "row", 0, 1, limited)
                self.assertEqual(limited.pair_records, 0)

    def test_size_color_and_file_limits(self):
        import tempfile
        colors = tuple("abcdefgh")
        p = validate_logic(wire([list(colors) + ["empty"] * 92], colors))
        proof = solve(p, profile="paired-lines-color")
        self.assertTrue(verify(p, proof)["certified"])
        for data in (wire([["empty"] * 101]), wire([["empty"]], tuple("abcdefghi"))):
            with self.assertRaises(InvalidInput):
                validate_logic(data)
        excessive = deepcopy(proof)
        excessive["steps"] *= p.max_proof_steps + 1
        with self.assertRaisesRegex(InvalidProof, "step count"):
            verify(p, excessive)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "oversized.json"
            with path.open("wb") as stream:
                stream.truncate(p.proof_byte_limit + 1)
            with self.assertRaises(InvalidInput):
                load_json(path, p.proof_byte_limit)

    def test_budget_limits_and_no_partial_projection(self):
        p = validate_logic(wire(MONO))
        for options in ({"max_pair_work": 0}, {"max_pair_work": 20}, {"max_pair_records": 0},
                        {"max_pair_records": 15}, {"max_lines": 0}, {"seconds": 0}):
            proof = solve(p, Budget(**options), profile="paired-lines-mono")
            self.assertEqual(proof["status"], "aborted")
            self.assertFalse(verify(p, proof)["certified"])
        proof = solve(p, profile="paired-lines-mono")
        for options in ({"max_pair_work": 0}, {"max_pair_work": 30}, {"max_pair_records": 0}):
            with self.assertRaises(Aborted):
                verify(p, proof, Budget(**options))

    def test_ambiguity_contradiction_one_dimensional_and_legacy(self):
        ambiguous = validate_logic(wire([["ink", "empty"], ["empty", "ink"]]))
        self.assertEqual(verify(ambiguous, solve(ambiguous, profile="paired-lines-mono"))["status"], "stalled")
        for matrix, colors in (([["ink", "empty", "ink"]], ("ink",)),
                               ([["empty"], ["a"], ["b"]], ("a", "b"))):
            p = validate_logic(wire(matrix, colors))
            profile = "paired-lines-mono" if colors == ("ink",) else "paired-lines-color"
            self.assertTrue(verify(p, solve(p, profile=profile))["certified"])
        data = wire([["ink"]])
        data["column_clues"] = [[]]
        p = validate_logic(data)
        self.assertEqual(verify(p, solve(p, profile="paired-lines-mono"))["status"], "contradiction")
        path = Path(__file__).parent / "fixtures"
        p = validate_logic(load_json(path / "deductive.json"))
        self.assertEqual(solve(p)["format"], "picross-proof-v1")


if __name__ == "__main__":
    unittest.main()
