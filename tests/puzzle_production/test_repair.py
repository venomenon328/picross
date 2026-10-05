"""RP5-A01..A04: source-bound search, cumulative limits and hostile replay."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from tools.puzzle_production import repair
from tools.puzzle_production.contract import Aborted, Budget, InvalidInput, InvalidProof, digest, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, inspect_candidate
from tools.puzzle_production.p1_export import export_p1

ROOT = Path(__file__).resolve().parents[2]


def fixture(root, color=False):
    design = load_json(ROOT / "examples/rp3/design.json")
    design.update(source_id="repair-functional", width=2, height=2, crop=[0, 0, 2, 2], fit="exact",
                  mode="color" if color else "mono", working_mode="faithful",
                  briefing="Technical 2x2 diagonal fixture; no catalogue motif claim.",
                  variants=[{"id": "area-128", "method": "area", "threshold": 128}])
    design["palette"] = [{"id": "red", "rgb": "#000000"}, {"id": "blue", "rgb": "#8888ff"}] if color else \
        [{"id": "ink", "rgb": "#000000"}]
    source = root / "source.png"
    im = Image.new("RGB", (2, 2), "white")
    im.putpixel((0, 0), (0, 0, 0))
    im.putpixel((1, 1), (0, 0, 0))
    im.save(source)
    write_json(root / "design.json", design)
    bundle = root / "reference"
    import_image(source, root / "design.json", bundle)
    c, proof, checked = inspect_candidate(bundle, "area-128")
    assert checked["status"] == "stalled"
    plan = {"format": repair.PLAN_FORMAT, "tool": repair.VERSION,
            "reference": {"candidate_id": c["id"], "manifest_sha256": file_hash(bundle / "manifest.json"), "variant": "area-128"},
            "mask": [[True, False], [True, True]], "rationale": "Protect both foreground cells and the lower empty cell.",
            "config": {"max_changes": 1, "max_steps": 32, "max_candidates": 8, "search_seconds": 30,
                       "final_seconds": 30, "search_lines": 10000, "final_lines": 1000, "seed": 39,
                       "operators": ["single-cell"], "order": "seeded-frontier-v1"}}
    return bundle, plan, c, proof


def rebind(bundle):
    data = load_json(bundle / "repair.json")
    data["files"] = {n: file_hash(bundle / n) for n in data["files"]}
    data["id"] = digest({k: v for k, v in data.items() if k not in ("id", "files")})
    write_json(bundle / "repair.json", data)


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.reference, self.plan, self.candidate, self.original = fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def run_search(self, plan=None, name="repair", **kwargs):
        output = self.root / name
        result = repair.search(self.reference, plan or self.plan, output, **kwargs)
        return output, result

    def test_positive_mono_fresh_final_and_independent_replay(self):
        output, result = self.run_search()
        self.assertEqual(result["status"], "found")
        self.assertTrue(result["certified"])
        self.assertEqual((result["steps"], result["candidates"]), (1, 2))
        self.assertFalse(result["editorial_release"])
        with patch.object(repair, "solve", side_effect=AssertionError("Verifier must not call the solver")):
            replay = repair.inspect_repair(output, self.reference)
        self.assertTrue(replay["certified"])
        self.assertNotEqual(load_json(output / "final-proof.json")["logic_hash"], self.candidate["logic_hash"])
        changes = load_json(output / "repair.json")["changes"]
        self.assertEqual(changes, [{"y": 0, "x": 1, "before": "empty", "after": "ink"}])

    def test_positive_color_same_contract_and_protected_empty(self):
        sub = self.root / "color"
        sub.mkdir()
        reference, plan, _, _ = fixture(sub, color=True)
        output = sub / "repair"
        result = repair.search(reference, plan, output)
        self.assertTrue(result["certified"])
        self.assertTrue(repair.inspect_repair(output, reference)["certified"])
        matrix = load_json(output / "repair.json")["matrix"]
        self.assertEqual((matrix[0][0], matrix[1][0], matrix[1][1]), ("red", "empty", "red"))

    def test_plan_rejects_mask_reference_versions_and_limits(self):
        variants = []
        for mask in ([], [[True]], [[1, False], [True, True]]):
            p = deepcopy(self.plan)
            p["mask"] = mask
            variants.append(p)
        for key, value in (("max_changes", True), ("max_steps", 1025), ("max_candidates", 129),
                           ("search_seconds", float("inf")), ("final_seconds", -1), ("seed", -1)):
            p = deepcopy(self.plan)
            p["config"][key] = value
            variants.append(p)
        p = deepcopy(self.plan)
        p["reference"]["candidate_id"] = "0"*64
        variants.append(p)
        p = deepcopy(self.plan)
        p["tool"] = "future"
        variants.append(p)
        for p in variants:
            with self.subTest(plan=p), self.assertRaises(InvalidInput):
                repair.search(self.reference, p, self.root / "invalid")
        p = deepcopy(self.plan)
        p["reference"]["manifest_sha256"] = "0"*64
        with self.assertRaises(InvalidInput):
            repair.search(self.reference, p, self.root / "wrong-source")

    def test_distance_recolors_and_undo_are_reference_relative(self):
        original = [["red", "empty"]]
        mask = [[False, True]]
        blue = repair.apply_edit(original, {"y": 0, "x": 0, "before": "red", "after": "blue"}, original, mask, 1)
        green = repair.apply_edit(blue, {"y": 0, "x": 0, "before": "blue", "after": "green"}, original, mask, 1)
        undo = repair.apply_edit(green, {"y": 0, "x": 0, "before": "green", "after": "red"}, original, mask, 1)
        self.assertEqual([repair.distance(m, original) for m in (blue, green, undo)], [1, 1, 0])
        with self.assertRaises(InvalidInput):
            repair.apply_edit(original, {"y": 0, "x": 1, "before": "empty", "after": "blue"}, original, mask, 2)

    def test_rejected_proposals_do_not_reset_steps(self):
        p = deepcopy(self.plan)
        p["mask"] = [[False]*2 for _ in range(2)]
        p["config"].update(max_changes=0, max_steps=3)
        output, result = self.run_search(p)
        self.assertEqual((result["status"], result["reason"], result["steps"], result["candidates"]),
                         ("budget_exhausted", "step_limit", 3, 1))
        self.assertEqual([a["outcome"] for a in load_json(output / "repair.json")["attempts"]], ["change_limit"]*3)
        self.assertTrue(repair.inspect_repair(output, self.reference)["accepted"])

    def test_duplicate_undo_consumes_step_without_candidate_reset(self):
        f = repair.Frontier([["red"]], [[False]], 39, [[["empty", "red", "blue"]]])
        score = {"domain_values_remaining": 3, "unresolved_cells": 1, "changed_cells": 0}
        f.add([["red"]], score, ("blue", "red"))
        f.add([["blue"]], {**score, "domain_values_remaining": 2, "changed_cells": 1}, ("blue", "red"))
        proposals = [f.next(), f.next()]
        self.assertTrue(any(edit["after"] == "red" for parent, edit in proposals))
        self.assertEqual([parent for parent, _ in proposals], [1, 1])
        self.assertEqual(f.next()[0], 0)
        self.assertEqual(f.states[1]["cursor"], len(f.proposals))

    def test_no_legal_improvement_candidate_step_and_fully_protected_limits(self):
        for changes, key, value, reason in ((0, "max_steps", 0, "step_limit"),
                                          (1, "max_candidates", 1, "candidate_limit")):
            p = deepcopy(self.plan)
            p["config"].update(max_changes=changes)
            p["config"][key] = value
            output, result = self.run_search(p, name=key)
            self.assertEqual(result["reason"], reason)
            self.assertFalse(repair.inspect_repair(output, self.reference)["certified"])
        p = deepcopy(self.plan)
        p["mask"] = [[True]*2 for _ in range(2)]
        output, result = self.run_search(p, name="protected")
        self.assertEqual(result["reason"], "frontier_exhausted")
        self.assertEqual(load_json(output / "repair.json")["matrix"], self.candidate["matrix"])
        self.assertTrue(repair.inspect_repair(output, self.reference)["accepted"])

    def test_search_work_limit_includes_reference_and_all_candidate_work(self):
        _, _, checked = inspect_candidate(self.reference, "area-128")
        p = deepcopy(self.plan)
        p["config"]["search_lines"] = checked["line_evaluations"]+1
        output, result = self.run_search(p)
        self.assertEqual(result["status"], "aborted")
        self.assertEqual(result["reason"], "work_limit")
        self.assertEqual(result["search_lines"], p["config"]["search_lines"])
        self.assertEqual(result["candidates"], 1)
        self.assertFalse(repair.inspect_repair(output, self.reference)["certified"])

    def test_final_abort_cannot_upgrade_later_replay(self):
        p = deepcopy(self.plan)
        p["config"]["final_lines"] = 0
        output, result = self.run_search(p)
        self.assertEqual((result["status"], result["reason"]), ("aborted", "work_limit"))
        self.assertFalse(result["certified"])
        self.assertFalse(repair.inspect_repair(output, self.reference)["certified"])

    def test_cancel_during_verification_and_completed_final_proof(self):
        real = repair.verify
        calls = 0

        def interrupt(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise Aborted("cancelled")
            return real(*args, **kwargs)

        with patch.object(repair, "verify", side_effect=interrupt):
            output, result = self.run_search()
        self.assertEqual(result["reason"], "cancelled")
        self.assertEqual(load_json(output / "final-proof.json")["status"], "solved")
        self.assertFalse(result["certified"])
        self.assertFalse(repair.inspect_repair(output, self.reference)["certified"])

    def test_time_limit_and_cancel_before_initialization(self):
        p = deepcopy(self.plan)
        p["config"]["search_seconds"] = 0
        with self.assertRaisesRegex(Aborted, "time_limit"):
            self.run_search(p)
        with self.assertRaisesRegex(Aborted, "cancelled"):
            self.run_search(cancelled=lambda: True)
        p = deepcopy(self.plan)
        p["config"]["final_seconds"] = 0
        output, result = self.run_search(p, name="time-final")
        self.assertEqual(result["reason"], "time_limit")
        self.assertFalse(repair.inspect_repair(output, self.reference)["certified"])

    def test_reproducible_identity_proofs_and_step_replay(self):
        a, ra = self.run_search(name="a")
        b, rb = self.run_search(name="b")
        aa, bb = load_json(a / "repair.json"), load_json(b / "repair.json")
        self.assertEqual(aa["id"], bb["id"])
        self.assertEqual(aa["attempts"], bb["attempts"])
        self.assertEqual((a / "final-proof.json").read_bytes(), (b / "final-proof.json").read_bytes())
        self.assertEqual(ra["search_lines"], rb["search_lines"])

    def test_rehashed_parent_history_scores_counter_and_mask_attacks(self):
        edits = [lambda d: d["history"][1].update(parent=1),
                 lambda d: d["history"][1]["edit"].update(before="ink"),
                 lambda d: d["history"][1]["score"].update(domain_losses=999),
                 lambda d: d["attempts"][0].update(outcome="duplicate"),
                 lambda d: d.update(changes=[]), lambda d: d.update(selected=0)]
        for i, edit in enumerate(edits):
            output, _ = self.run_search(name=f"attack-{i}")
            data = load_json(output / "repair.json")
            edit(data)
            write_json(output / "repair.json", data)
            rebind(output)
            with self.subTest(attack=i), self.assertRaises((InvalidInput, InvalidProof)):
                repair.inspect_repair(output, self.reference)
        output, _ = self.run_search(name="counter")
        result = load_json(output / "result.json")
        result["search_lines"] = 0
        write_json(output / "result.json", result)
        rebind(output)
        with self.assertRaises(InvalidInput):
            repair.inspect_repair(output, self.reference)

    def test_rehashed_stale_and_manipulated_proof_and_clues_fail(self):
        for kind in ("stale", "step", "logic", "display"):
            output, _ = self.run_search(name=kind)
            if kind == "stale":
                write_json(output / "final-proof.json", self.original)
            elif kind == "step":
                proof = load_json(output / "candidate-001-proof.json")
                proof["steps"][0]["changes"][0]["after"] = ["empty", "ink"]
                write_json(output / "candidate-001-proof.json", proof)
            elif kind == "logic":
                wire = load_json(output / "final-logic.json")
                wire["row_clues"][0] = []
                write_json(output / "final-logic.json", wire)
            else:
                with Image.open(output / "changes.png") as im:
                    im.putpixel((0, 0), (0, 0, 0))
                    im.save(output / "changes.png")
            rebind(output)
            with self.subTest(kind=kind), self.assertRaises((InvalidInput, InvalidProof)):
                repair.inspect_repair(output, self.reference)

    def test_repair_bundle_explicitly_rejected_by_existing_p1_export(self):
        output, _ = self.run_search()
        with self.assertRaises(InvalidInput):
            export_p1(output, "area-128", ROOT / "examples/rp3/reveal.svg", "Fixture", self.root / "export")

    def test_cli_fresh_process_and_invalid_exit(self):
        write_json(self.root / "plan.json", self.plan)
        command = [sys.executable, "-m", "tools.puzzle_production.repair"]
        run = subprocess.run(command + ["search", "--reference", str(self.reference), "--plan", str(self.root / "plan.json"),
                                        "--output-dir", str(self.root / "cli")], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        replay = subprocess.run(command + ["verify", "--reference", str(self.reference), "--bundle", str(self.root / "cli")],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(replay.returncode, 0, replay.stdout+replay.stderr)
        self.assertEqual(subprocess.run(command + ["search", "--reference", str(self.reference), "--plan", str(self.root / "plan.json"),
                                                   "--output-dir", str(self.root / "cli")], capture_output=True, timeout=30).returncode, 2)


if __name__ == "__main__":
    unittest.main()
