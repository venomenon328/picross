"""Reproduce the fixed synthetic B set; no arbitrary input or catalog discovery.

Evidence contains no method hash (avoids a freeze cycle). This internal test
helper generates real complete A bundles and independently rechecks each one.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

from .contract import InvalidProof, digest, validate_logic
from .sd2_contract import AnalysisBudget, BYTE_LIMIT, analysis_input
from .sd2_io import _bytes, _json, _write, analyze_file, check_bundle
from .sd2_rating import _rating_result
from .solver import solve

_ROOT = Path(__file__).parent


def reference_evidence(split):
    if split not in ("calibration", "validation"):
        raise ValueError("Expected a fixed reference split")
    refs = _json(_bytes(_ROOT / "sd2_references_0_4.json", BYTE_LIMIT))
    groups = {}
    for case in refs["cases"]:
        if groups.setdefault(case["group"], case["split"]) != case["split"]:
            raise InvalidProof("Reference group leaked across splits")
    results = []
    for case in refs["cases"]:
        if case["split"] != split:
            continue
        puzzle = validate_logic(case["logic"])
        if puzzle.logic_hash != case["logic_hash"] or digest(analysis_input(puzzle)) != case["analysis_hash"]:
            raise InvalidProof("Reference identity changed")
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.json"
            _write(source, case["logic"])
            paths = {}
            proof_hashes = None
            pair = None
            if case["pattern"] == "pair":
                baseline = solve(puzzle)
                pair = solve(puzzle, profile="paired-lines-mono" if len(puzzle.colors) == 1 else "paired-lines-color")
                proof_hashes = {"baseline": digest(baseline), "pair": digest(pair)}
                for name, obj in (("baseline", baseline), ("proof", pair)):
                    paths[name + "_path"] = root / (name + ".json")
                    _write(paths[name + "_path"], obj)
            bundle = root / "analysis"
            report = analyze_file(source, bundle, **paths)
            checked = check_bundle(source, bundle, AnalysisBudget())
            trace = _json(_bytes(bundle / "trace.json", BYTE_LIMIT))
            if checked["result_hash"] != report["result_hash"]:
                raise InvalidProof("Reference result failed fresh file replay")
            if digest(trace) != case["curation_evidence"]["trace_hash"] or proof_hashes != case["curation_evidence"]["proof_hashes"]:
                raise InvalidProof("Reference deduction differs from pre-score curation")
            expected = [["empty" if c == "." else puzzle.colors[int(c)] for c in row] for row in case["rows"]]
            actual = pair["final_domains"] if pair else [
                [[v for j, v in enumerate(["empty", *puzzle.colors]) if mask & (1 << j)] for mask in row]
                for row in trace["final_domains"]]
            if actual != [[[v] for v in row] for row in expected]:
                raise InvalidProof("Reference full deduction differs from its construction")
            result = _rating_result(report["result"], checked["result_hash"], "evidence-before-freeze")
            assessment = result["assessment"]
            results.append({"id": case["id"], "group": case["group"], "expected_level": case["expected_level"],
                "matches_expectation": assessment is not None and assessment["level"] == case["expected_level"],
                "analysis_result_hash": checked["result_hash"], "trace_hash": digest(trace),
                "profiles_hash": digest(report["result"]["profiles"]), "proof_hashes": proof_hashes,
                "final_matrix_hash": digest(expected), "reason": result["reason"],
                "profile_scope": result["profile_scope"], "assessment": assessment})
    by_id = {c["id"]: c for c in results}
    orders = []
    for order in refs["expected_orders"]:
        if order["lower"] not in by_id:
            continue
        lower, upper = (by_id[order[k]]["assessment"] for k in ("lower", "upper"))
        orders.append({**order, "satisfied": Fraction(*lower["score"]) < Fraction(*upper["score"])})
    return {"format": "picross-sd2-evidence-v1", "split": split, "reference_hash": digest(refs),
            "human_data": None, "all_expectations_met": all(c["matches_expectation"] for c in results),
            "all_orders_met": all(o["satisfied"] for o in orders), "cases": results, "orders": orders}
