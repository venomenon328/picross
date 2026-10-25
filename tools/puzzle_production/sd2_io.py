"""Explicit single-input SD bundles. Never reads registries or production packages."""
from __future__ import annotations

import hashlib
import json
import math
import stat
import time

from .sd2_contract import (AnalysisBudget, BYTE_LIMIT, REPORT, analysis_input,
                                parameters, result_data)
from .contract import (InvalidInput, InvalidProof, LOGIC_BYTE_LIMIT, canonical_bytes,
                       digest, exact_keys, integer)
from .analysis_io import source_logic, source_binding, check_target, check_r4


def _safe_path(path):
    for component in (path, *path.parents):
        if not component.exists() and not component.is_symlink():
            continue
        info = component.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise InvalidInput("SD2 paths must not contain links or reparse points")


def _bytes(path, limit):
    _safe_path(path)
    if not path.is_file():
        raise InvalidInput("Expected a regular SD2 input file")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise InvalidInput(f"File exceeds {limit} bytes")
    return raw


def _binding(raw):
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _json(raw):
    """Parse the exact bytes whose binding was checked, without reopening a path."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InvalidInput(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise InvalidInput(f"Non-JSON constant: {value}")

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        canonical_bytes(result)
        return result
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InvalidInput(f"Invalid SD2 JSON: {exc}") from exc


def _load(path, limit):
    return _json(_bytes(path, limit))


def _write(path, value):
    raw = canonical_bytes(value) + b"\n"
    if len(raw) > BYTE_LIMIT:
        raise InvalidInput("Analysis artifact exceeds 64 MiB")
    with path.open("xb") as stream:
        stream.write(raw)
    return _binding(raw)


def analyze_file(input_path, output, *, kind="logic", config=None, budget=None,
                 verify_budget=None, proof_path=None, baseline_path=None):
    from .sd2_analysis import analyze
    from .sd2_verifier import verify_trace
    config = parameters(config)
    budget = budget if budget is not None else AnalysisBudget()
    verify_budget = verify_budget if verify_budget is not None else AnalysisBudget()
    if (proof_path is None) != (baseline_path is None):
        raise InvalidInput("Supply both R4 files or neither")
    if output.exists() or output.is_symlink():
        raise InvalidInput("Analysis output must be a new directory")
    _safe_path(output)
    started = time.monotonic()
    raw_bytes = _bytes(input_path, LOGIC_BYTE_LIMIT)
    output.mkdir(parents=True, exist_ok=False)
    (output / "input.json").write_bytes(raw_bytes)
    raw = _json(raw_bytes)
    puzzle = source_logic(raw, kind)
    files = {"input.json": _binding(raw_bytes)}
    files["logic.json"] = _write(output / "logic.json", analysis_input(puzzle))
    trace = analyze(puzzle, config, budget)
    files["trace.json"] = _write(output / "trace.json", trace)
    # File replay verifies the actual stored trace, not just the in-memory object.
    stored_bytes = _bytes(output / "trace.json", BYTE_LIMIT)
    if _binding(stored_bytes) != files["trace.json"]:
        raise InvalidProof("Stored trace changed before verification")
    stored = _json(stored_bytes)
    checked = verify_trace(puzzle, stored, verify_budget)
    target = check_target(raw, kind, puzzle, stored)
    proof = baseline = None
    for path, name in ((proof_path, "r4-proof.json"), (baseline_path, "r4-baseline.json")):
        if path is not None:
            data = _bytes(path, puzzle.proof_byte_limit)
            (output / name).write_bytes(data)
            files[name] = _binding(data)
    if proof_path is not None:
        proof = _load(output / "r4-proof.json", puzzle.proof_byte_limit)
        baseline = _load(output / "r4-baseline.json", puzzle.proof_byte_limit)
    r4 = check_r4(puzzle, stored, proof, baseline, files.get("r4-proof.json"),
                 files.get("r4-baseline.json"), verify_budget)
    result = result_data(puzzle, stored, r4, verify_budget)
    for name, binding in files.items():
        if _binding(_bytes(output / name, BYTE_LIMIT)) != binding:
            raise InvalidProof("Bundle changed during analysis")
    verify_budget.check()
    report = {"format": REPORT, "result": result, "result_hash": digest(result),
        "source": source_binding(raw_bytes, raw, puzzle, kind), "files": files,
        "verification": checked, "target_check": target,
        "operation": {"analysis_limits": budget.limits(), "verification_limits": verify_budget.limits(),
                      "analysis_usage": budget.usage(), "verification_usage": verify_budget.usage(),
                      "elapsed_seconds": time.monotonic() - started}}
    _write(output / "report.json", report)
    return report


def _check_operation(operation):
    """Check schema/limits, without claiming to reproduce elapsed hardware work."""
    exact_keys(operation, {"analysis_limits", "verification_limits", "analysis_usage",
                           "verification_usage", "elapsed_seconds"}, InvalidProof)
    elapsed = operation["elapsed_seconds"]
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
        raise InvalidProof("Invalid elapsed time")
    for prefix in ("analysis", "verification"):
        limits = exact_keys(operation[prefix + "_limits"], {"seconds", "max_lines", "max_rule_work",
            "max_waves", "max_pair_work", "max_pair_records"}, InvalidProof)
        try:
            if type(limits["seconds"]) not in (int, float):
                raise InvalidInput("Invalid seconds")
            AnalysisBudget(**limits)
        except (InvalidInput, TypeError, ValueError) as exc:
            raise InvalidProof("Invalid recorded resource limits") from exc
        usage = exact_keys(operation[prefix + "_usage"],
            {"lines", "rule_work", "pair_work", "pair_peak_records"}, InvalidProof)
        for field, bound in (("lines", "max_lines"), ("rule_work", "max_rule_work"),
                             ("pair_work", "max_pair_work"), ("pair_peak_records", "max_pair_records")):
            integer(usage[field], 0, limits[bound], field, InvalidProof)


def check_bundle(input_path, directory, budget=None):
    from .sd2_verifier import verify_result
    budget = budget if budget is not None else AnalysisBudget()
    report_path = directory / "report.json"
    report = exact_keys(_load(report_path, BYTE_LIMIT), {
        "format", "result", "result_hash", "source", "files", "verification", "target_check", "operation"}, InvalidProof)
    if not isinstance(report["result"], dict) or not isinstance(report["source"], dict):
        raise InvalidProof("Result and source must be objects")
    _check_operation(report["operation"])
    if report["format"] != REPORT or report["result_hash"] != digest(report["result"]):
        raise InvalidProof("Wrong report format/result hash")
    files = report["files"]
    expected_names = {"input.json", "logic.json", "trace.json"}
    if report["result"].get("r4") is not None:
        expected_names |= {"r4-proof.json", "r4-baseline.json"}
    exact_keys(files, expected_names, InvalidProof)
    _safe_path(directory)
    if {p.name for p in directory.iterdir()} != expected_names | {"report.json"}:
        raise InvalidProof("Unexpected or missing SD2 bundle members")
    data = {}
    for name in expected_names:
        limit = LOGIC_BYTE_LIMIT if name in ("input.json", "logic.json") else BYTE_LIMIT
        data[name] = _bytes(directory / name, limit)
        if digest(files[name]) != digest(_binding(data[name])):
            raise InvalidProof(f"Wrong file binding: {name}")
    raw_bytes = _bytes(input_path, LOGIC_BYTE_LIMIT)
    if raw_bytes != data["input.json"]:
        raise InvalidProof("Source bytes changed")
    raw = _json(data["input.json"])
    kind = report["source"].get("kind")
    puzzle = source_logic(raw, kind)
    if digest(report["source"]) != digest(source_binding(raw_bytes, raw, puzzle, kind)):
        raise InvalidProof("Wrong source identity")
    if digest(_json(data["logic.json"])) != digest(analysis_input(puzzle)):
        raise InvalidProof("Wrong normalized analysis input")
    trace = _json(data["trace.json"])
    proof = baseline = None
    if "r4-proof.json" in files:
        if any(len(data[name]) > puzzle.proof_byte_limit for name in ("r4-proof.json", "r4-baseline.json")):
            raise InvalidProof("R4 proof exceeds its legacy byte limit")
        proof = _json(data["r4-proof.json"])
        baseline = _json(data["r4-baseline.json"])
    r4 = check_r4(puzzle, trace, proof, baseline, files.get("r4-proof.json"), files.get("r4-baseline.json"), budget)
    checked = verify_result(puzzle, trace, report["result"], budget, r4)
    if digest(report["verification"]) != digest(checked):
        raise InvalidProof("Conflicting verification fields")
    if report["target_check"] != check_target(raw, kind, puzzle, trace):
        raise InvalidProof("Conflicting target binding")
    budget.check()
    return {"format": "picross-sd2-check-v1", **checked, "result_hash": report["result_hash"],
            "file_bindings_verified": True, "report_verified": True,
            "operational_measurements_verified": False}
