"""Separate B envelope around an immutable, independently checked A-v1 bundle."""
from __future__ import annotations

from .contract import InvalidInput, InvalidProof, digest, exact_keys
from .sd2_contract import AnalysisBudget, BYTE_LIMIT
from .sd2_io import _binding, _bytes, _json, _safe_path, _write, analyze_file, check_bundle
from .sd2_rating import _rating_result, _report
from .sd2_rating_freeze import frozen_method
from .sd2_rating_identity import METHOD_HASH

BUNDLE = "picross-sd2-rating-bundle-v1"
_ALLOWED = {"input.json", "logic.json", "trace.json", "report.json", "r4-proof.json", "r4-baseline.json"}
_REQUIRED = {"input.json", "logic.json", "trace.json", "report.json"}


def _snapshot(directory):
    _safe_path(directory)
    if not directory.is_dir():
        raise InvalidInput("Expected an A analysis bundle directory")
    names = {p.name for p in directory.iterdir()}
    if names not in (_REQUIRED, _ALLOWED):
        raise InvalidProof("Unexpected or missing A bundle members")
    return {name: _bytes(directory / name, BYTE_LIMIT) for name in sorted(names)}


def _verified(input_path, directory, budget):
    before = _snapshot(directory)
    checked = check_bundle(input_path, directory, budget)
    if before != _snapshot(directory):
        raise InvalidProof("Analysis bundle changed during independent verification")
    report = _json(before["report.json"])
    if report["result_hash"] != checked["result_hash"] or digest(report["result"]) != checked["result_hash"]:
        raise InvalidProof("Checked A result and rating input differ")
    result = _rating_result(report["result"], checked["result_hash"], METHOD_HASH)
    budget.check()
    return {"format": BUNDLE, "result": result, "result_hash": digest(result),
            "analysis_files": {name: _binding(raw) for name, raw in before.items()}}


def _new_output(output):
    _safe_path(output)
    if output.exists() or output.is_symlink():
        raise InvalidInput("Rating output must be a new directory")
    output.mkdir(parents=True, exist_ok=False)


def _finish(output, report):
    # Both are derived only after complete fresh verification. Never overwrite.
    markdown = _report(report["result"])
    if len(markdown) > 1024 * 1024:
        raise InvalidInput("SD2 rating report exceeds 1 MiB")
    with (output / "report.md").open("xb") as stream:
        stream.write(markdown)
    _write(output / "rating.json", report)
    return report


def rate_bundle(input_path, directory, output, budget=None):
    budget = budget if budget is not None else AnalysisBudget()
    frozen_method(budget)
    snapshot = _snapshot(directory)
    _new_output(output)
    analysis = output / "analysis"
    analysis.mkdir()
    for name, raw in snapshot.items():
        with (analysis / name).open("xb") as stream:
            stream.write(raw)
    return _finish(output, _verified(input_path, analysis, budget))


def analyze_and_rate(input_path, output, *, kind="logic", budget=None, verify_budget=None,
                     proof_path=None, baseline_path=None):
    budget = budget if budget is not None else AnalysisBudget()
    verify_budget = verify_budget if verify_budget is not None else AnalysisBudget()
    # Identity files are statically bounded. Starting this clock here would
    # incorrectly charge the following analysis time to the separate verifier.
    frozen_method()
    _new_output(output)
    analyze_file(input_path, output / "analysis", kind=kind, budget=budget,
                 verify_budget=verify_budget, proof_path=proof_path, baseline_path=baseline_path)
    return _finish(output, _verified(input_path, output / "analysis", verify_budget))


def check_rating_bundle(input_path, directory, budget=None):
    budget = budget if budget is not None else AnalysisBudget()
    frozen_method(budget)
    _safe_path(directory)
    if not directory.is_dir():
        raise InvalidInput("Expected a B rating bundle directory")
    if {p.name for p in directory.iterdir()} != {"analysis", "rating.json", "report.md"}:
        raise InvalidProof("Unexpected or missing B bundle members")
    raw = _bytes(directory / "rating.json", BYTE_LIMIT)
    report = exact_keys(_json(raw), {"format", "result", "result_hash", "analysis_files"}, InvalidProof)
    expected = _verified(input_path, directory / "analysis", budget)
    if digest(report) != digest(expected):
        raise InvalidProof("Rating differs from independently verified reconstruction")
    if _bytes(directory / "report.md", 1024 * 1024) != _report(expected["result"]):
        raise InvalidProof("Markdown rating report differs from reconstruction")
    if raw != _bytes(directory / "rating.json", BYTE_LIMIT):
        raise InvalidProof("Rating changed during verification")
    budget.check()
    return {"format": "picross-sd2-rating-check-v1", "result": expected["result"],
            "result_hash": expected["result_hash"], "rating_verified": True,
            "analysis_verified": True, "operational_measurements_verified": False}
