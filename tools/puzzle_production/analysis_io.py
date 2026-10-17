"""Explicit single-input SD bundles. Never reads registries or production packages."""
from __future__ import annotations

import hashlib
import math
import re
import time

from .analysis_contract import (AnalysisBudget, BYTE_LIMIT, REPORT, analysis_input,
                                parameters, result_data)
from .contract import (InvalidInput, InvalidProof, LOGIC_BYTE_LIMIT, canonical_bytes,
                       digest, exact_keys, integer, load_json, selected_profile, validate_logic, wire_grid)


def _bytes(path, limit):
    if path.is_symlink():
        raise InvalidInput("Analysis inputs and bundle members must not be symlinks")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise InvalidInput(f"File exceeds {limit} bytes")
    return raw


def _binding(raw):
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _write(path, value):
    raw = canonical_bytes(value) + b"\n"
    if len(raw) > BYTE_LIMIT:
        raise InvalidInput("Analysis artifact exceeds 64 MiB")
    with path.open("xb") as stream:
        stream.write(raw)
    return _binding(raw)


def runtime_logic(raw):
    """Extract hints only. No access to the solution, assets, registry or mode."""
    exact_keys(raw, {"schema", "id", "revision", "width", "height", "palette",
                     "solution", "rows", "columns", "reveal"})
    integer(raw["schema"], 2, 2, "runtime schema")
    width = integer(raw["width"], 1, 50, "runtime width")
    height = integer(raw["height"], 1, 50, "runtime height")
    integer(raw["revision"], 1, 1_000_000, "runtime revision")
    if not isinstance(raw["id"], str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", raw["id"]):
        raise InvalidInput("Invalid runtime identity")
    palette = raw["palette"]
    if not isinstance(palette, list) or not 1 <= len(palette) <= 8:
        raise InvalidInput("Expected 1..8 runtime foreground colors")
    ids = []
    for entry in palette:
        exact_keys(entry, {"id", "color", "symbol"})
        ids.append(integer(entry["id"], 1, len(palette), "runtime color ID"))
        if not isinstance(entry["color"], str) or not re.fullmatch(r"[0-9a-fA-F]{6}", entry["color"]):
            raise InvalidInput("Invalid runtime RGB")
        if not isinstance(entry["symbol"], str) or len(entry["symbol"]) != 1:
            raise InvalidInput("Invalid runtime symbol")
    if sorted(ids) != list(range(1, len(palette) + 1)):
        raise InvalidInput("Runtime IDs must be exactly 1..K")
    colors = [f"c{i}" for i in range(1, len(palette) + 1)]

    def clues(lines, count):
        if not isinstance(lines, list) or len(lines) != count:
            raise InvalidInput("Wrong runtime clue line count")
        result = []
        for line in lines:
            if not isinstance(line, list) or len(line) > 100:
                raise InvalidInput("Invalid runtime clue line")
            row = []
            for clue in line:
                exact_keys(clue, {"length", "color"})
                color = integer(clue["color"], 1, len(colors), "clue color")
                length = integer(clue["length"], 1, 100, "clue length")
                row.append({"length": length, "color": f"c{color}"})
            result.append(row)
        return result

    return validate_logic({"format": "picross-logic-v2", "width": width, "height": height,
        "colors": colors, "empty": "empty", "initial_domain": ["empty", *colors],
        "rules": {"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0},
        "row_clues": clues(raw["rows"], height), "column_clues": clues(raw["columns"], width)})


def source_logic(raw, kind):
    if kind == "runtime":
        return runtime_logic(raw)
    if kind != "logic":
        raise InvalidInput("Input kind must be logic or runtime")
    return validate_logic(raw)


def source_binding(raw_bytes, raw, puzzle, kind):
    return {**_binding(raw_bytes), "kind": kind, "engine_logic_hash": puzzle.logic_hash,
            "definition_id": raw["id"] if kind == "runtime" else None,
            "runtime_revision": raw["revision"] if kind == "runtime" else None,
            "production_mode": "unknown" if kind == "runtime" else
                               "mono" if puzzle.format == "picross-logic-v1" else "color"}


def check_target(raw, kind, puzzle, trace):
    if kind != "runtime":
        return "not_supplied"
    # Deliberately called after deduction, never from runtime_logic/analyze.
    matrix = raw["solution"]
    if not isinstance(matrix, list) or len(matrix) != puzzle.height:
        raise InvalidInput("Invalid runtime solution shape")
    masks = []
    for row in matrix:
        if not isinstance(row, list) or len(row) != puzzle.width:
            raise InvalidInput("Invalid runtime solution shape")
        masks.append([1 << integer(v, 0, len(puzzle.colors), "solution color") for v in row])
    from .verifier import _matches_clues
    for axis, count in (("row", puzzle.height), ("column", puzzle.width)):
        for i in range(count):
            clues, cells = puzzle.line(masks, axis, i)
            if not _matches_clues(cells, clues):
                raise InvalidInput("Runtime solution does not match the input clues")
    if any(not (mask & target) for row, targets in zip(trace["final_domains"], masks)
           for mask, target in zip(row, targets)):
        raise InvalidProof("Deduced domains exclude the separately checked target")
    return "matched_complete" if trace["status"] == "solved" else "compatible_partial"


def check_r4(puzzle, trace, proof, baseline, proof_binding, baseline_binding, budget):
    from .certification import LABEL, require_legacy
    from .verifier import verify
    if proof is None and baseline is None:
        return None
    if proof is None or baseline is None:
        raise InvalidInput("R4 requires both explicit proof and line baseline")
    if not isinstance(proof, dict) or not isinstance(baseline, dict):
        raise InvalidProof("R4 proof and baseline must be objects")
    require_legacy(puzzle, baseline)
    profile = "paired-lines-mono" if puzzle.format == "picross-logic-v1" else "paired-lines-color"
    if proof.get("format") != "picross-proof-v3" or proof.get("profile") != selected_profile(puzzle, profile):
        raise InvalidProof("R4 evidence requires the matching paired profile")
    base = verify(puzzle, baseline, budget)
    pair = verify(puzzle, proof, budget)
    needed = base["status"] == "stalled" and pair["certified"]
    if needed and trace["status"] != "stalled":
        raise InvalidProof("R4 necessity needs a completed, matching SD line fixpoint")
    if base["status"] in ("solved", "stalled") and trace["status"] in ("solved", "stalled"):
        if base["status"] != trace["status"] or digest(baseline["final_domains"]) != digest(
                wire_grid(trace["final_domains"], puzzle.colors)):
            raise InvalidProof("Independent line baseline and SD fixpoint disagree")
    return {"required": needed, "label": LABEL if needed else None,
            "necessity": "required" if needed else "not_required" if base["status"] == "solved" else "unproven",
            "proof": proof_binding, "baseline": baseline_binding,
            "proof_profile_hash": proof["profile_hash"], "baseline_profile_hash": baseline["profile_hash"],
            "proof_status": pair["status"], "baseline_status": base["status"],
            "proof_verified": True, "baseline_verified": True,
            "instrumentation": "separate_R4_evidence_not_synchronous_waves"}


def analyze_file(input_path, output, *, kind="logic", config=None, budget=None,
                 verify_budget=None, proof_path=None, baseline_path=None):
    from .analysis import analyze
    from .analysis_verifier import verify_trace
    config = parameters(config)
    budget = budget if budget is not None else AnalysisBudget()
    verify_budget = verify_budget if verify_budget is not None else AnalysisBudget()
    if (proof_path is None) != (baseline_path is None):
        raise InvalidInput("Supply both R4 files or neither")
    if output.exists() or output.is_symlink():
        raise InvalidInput("Analysis output must be a new directory")
    started = time.monotonic()
    raw_bytes = _bytes(input_path, LOGIC_BYTE_LIMIT)
    output.mkdir(parents=True, exist_ok=False)
    (output / "input.json").write_bytes(raw_bytes)
    raw = load_json(output / "input.json", LOGIC_BYTE_LIMIT)
    puzzle = source_logic(raw, kind)
    files = {"input.json": _binding(raw_bytes)}
    files["logic.json"] = _write(output / "logic.json", analysis_input(puzzle))
    trace = analyze(puzzle, config, budget)
    files["trace.json"] = _write(output / "trace.json", trace)
    # File replay verifies the actual stored trace, not just the in-memory object.
    stored = load_json(output / "trace.json", BYTE_LIMIT)
    checked = verify_trace(puzzle, stored, verify_budget)
    target = check_target(raw, kind, puzzle, stored)
    proof = baseline = None
    for path, name in ((proof_path, "r4-proof.json"), (baseline_path, "r4-baseline.json")):
        if path is not None:
            data = _bytes(path, puzzle.proof_byte_limit)
            (output / name).write_bytes(data)
            files[name] = _binding(data)
    if proof_path is not None:
        proof = load_json(output / "r4-proof.json", puzzle.proof_byte_limit)
        baseline = load_json(output / "r4-baseline.json", puzzle.proof_byte_limit)
    r4 = check_r4(puzzle, stored, proof, baseline, files.get("r4-proof.json"),
                 files.get("r4-baseline.json"), verify_budget)
    result = result_data(puzzle, stored, r4)
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
    from .analysis_verifier import verify_result
    budget = budget if budget is not None else AnalysisBudget()
    report_path = directory / "report.json"
    _bytes(report_path, BYTE_LIMIT)
    report = exact_keys(load_json(report_path, BYTE_LIMIT), {
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
    for name in expected_names:
        if digest(files[name]) != digest(_binding(_bytes(directory / name, BYTE_LIMIT))):
            raise InvalidProof(f"Wrong file binding: {name}")
    raw_bytes = _bytes(input_path, LOGIC_BYTE_LIMIT)
    if raw_bytes != _bytes(directory / "input.json", LOGIC_BYTE_LIMIT):
        raise InvalidProof("Source bytes changed")
    raw = load_json(directory / "input.json", LOGIC_BYTE_LIMIT)
    kind = report["source"].get("kind")
    puzzle = source_logic(raw, kind)
    if digest(report["source"]) != digest(source_binding(raw_bytes, raw, puzzle, kind)):
        raise InvalidProof("Wrong source identity")
    if digest(load_json(directory / "logic.json", LOGIC_BYTE_LIMIT)) != digest(analysis_input(puzzle)):
        raise InvalidProof("Wrong normalized analysis input")
    trace = load_json(directory / "trace.json", BYTE_LIMIT)
    proof = baseline = None
    if "r4-proof.json" in files:
        proof = load_json(directory / "r4-proof.json", puzzle.proof_byte_limit)
        baseline = load_json(directory / "r4-baseline.json", puzzle.proof_byte_limit)
    r4 = check_r4(puzzle, trace, proof, baseline, files.get("r4-proof.json"), files.get("r4-baseline.json"), budget)
    checked = verify_result(puzzle, trace, report["result"], budget, r4)
    if digest(report["verification"]) != digest(checked):
        raise InvalidProof("Conflicting verification fields")
    if report["target_check"] != check_target(raw, kind, puzzle, trace):
        raise InvalidProof("Conflicting target binding")
    budget.check()
    return {"format": "picross-analysis-check-v1", **checked, "result_hash": report["result_hash"],
            "file_bindings_verified": True, "report_verified": True,
            "operational_measurements_verified": False}
