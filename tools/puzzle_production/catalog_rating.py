"""SD-C compact evidence, strict structural validation and source binding.

Only import_bundle replays evidence. All other functions validate data and
arithmetic, not deductions. Hashes are provenance, never signatures.
"""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

from .authoring_package import ID, require, sha
from .contract import canonical_bytes, digest, exact_keys, integer, load_json
from .analysis_contract import RULE_IDS, REASONS, analysis_input
from .analysis_io import runtime_logic, check_target
from .difficulty_rating import (METHOD_ID, RATING_FORMAT, frozen_method,
                                logical_level, size_effect)

FORMAT = "picross-catalog-difficulty-v1"
CHECKED = "picross-checked-difficulty-v1"
LIMIT = 96 * 1024
FIELDS = {"current_source", "logic_binding", "rating", "compact_analysis"}
MODULES = ("catalog_rating.py", "catalog_analysis.py", "catalog_transaction.py", "catalog_integration.py")
METRICS = {"wave_count", "family_waves", "family_line_applications", "rule_applications",
           "highest_family_used", "unique_changed_cells", "unique_partial_cells",
           "cell_change_events", "new_singletons", "partial_change_events", "removed_values",
           "simple_fraction_all_cells", "simple_fraction_determined", "r0_fraction_all_cells",
           "aggregation", "workload"}


def bytes_json(raw, limit=LIMIT):
    require(isinstance(raw, bytes) and len(raw) <= limit, "Difficulty file exceeds resource limit")
    def unique_pairs(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, "Duplicate difficulty JSON key: " + key)
            result[key] = item
        return result
    def constant(value):
        raise ValueError("Nonfinite difficulty JSON: " + value)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs, parse_constant=constant)
    canonical_bytes(value)  # also rejects overflowed floats
    return value


def encoded(value):
    raw = canonical_bytes(value) + b"\n"
    require(len(raw) <= LIMIT, "Difficulty file exceeds 96 KiB")
    return raw


def read_file(path, limit=LIMIT):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "Difficulty file exceeds resource limit")
    return raw


def hashed(value, field):
    return {**value, field: digest(value)}


def check_hash(value, field):
    require(sha(value[field]) == digest({k: v for k, v in value.items() if k != field}),
            "Wrong difficulty " + field)


def identity(value):
    require(isinstance(value, str) and ID.fullmatch(value), "Invalid difficulty puzzle ID")
    return value


def path(identifier):
    return "content/difficulty/" + identity(identifier) + "/rating.json"


def source(value):
    exact_keys(value, {"id", "runtime_revision", "definition_sha256"})
    identity(value["id"])
    integer(value["runtime_revision"], 1, 1000000, "rating runtime revision")
    sha(value["definition_sha256"])
    return value


def binding(value):
    exact_keys(value, {"analysis_hash", "matrix_hash"})
    for v in value.values(): sha(v)
    return value


def definition(raw):
    data = bytes_json(raw, 2 * 1024 * 1024)
    puzzle = runtime_logic(data)
    identity(data["id"])
    # Pure matrix/clue consistency; unknown domains supply no deduction claims.
    check_target(data, "runtime", puzzle, {"status": "stalled", "final_domains": puzzle.unknown_grid()})
    return (data, puzzle,
            {"id": data["id"], "runtime_revision": data["revision"],
             "definition_sha256": hashlib.sha256(raw).hexdigest()},
            {"analysis_hash": digest(analysis_input(puzzle)), "matrix_hash": digest(data["solution"])})


def tool_identity():
    return {"id": "picross-catalog-difficulty", "version": 1,
            "modules": {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in MODULES}}


def tool(value):
    exact_keys(value, {"id", "version", "modules"})
    require(value["id"] == "picross-catalog-difficulty", "Unknown catalog rating tool")
    integer(value["version"], 1, 1, "catalog rating tool version")
    exact_keys(value["modules"], set(MODULES))
    for v in value["modules"].values(): sha(v)


def boolean(value):
    require(type(value) is bool, "Expected difficulty boolean")


def fraction(value, *, reduced=True, undefined=False):
    require(isinstance(value, list) and len(value) == 2, "Expected difficulty fraction")
    integer(value[0], 0, 100000000, "numerator")
    integer(value[1], 0 if undefined else 1, 100000000, "denominator")
    if value == [0, 0] and undefined: return None
    require(value[1] > 0 and value[0] <= value[1], "Invalid difficulty fraction")
    f = Fraction(*value)
    if reduced: require(value == [f.numerator, f.denominator], "Noncanonical difficulty fraction")
    return f


def _profile(value):
    exact_keys(value, {"highest_family", "strong_information_fraction", "simple_information_fraction",
        "peak_strain", "bottleneck_waves", "bottleneck_phases", "longest_bottleneck",
        "recurrence_bonus", "demand", "cleanup_suffix_waves", "fluent_r1", "localized_combination"})
    require(value["highest_family"] in ("R0", "R1", "R2", "R3"), "Invalid profile family")
    for k in ("strong_information_fraction", "simple_information_fraction", "peak_strain", "recurrence_bonus", "demand"):
        fraction(value[k])
    require(Fraction(*value["strong_information_fraction"]) + Fraction(*value["simple_information_fraction"]) == 1,
            "Contradictory information fractions")
    for k in ("bottleneck_waves", "bottleneck_phases", "longest_bottleneck", "cleanup_suffix_waves"):
        integer(value[k], 0, 80000, k)
    c, p, d = (value[k] for k in ("bottleneck_waves", "bottleneck_phases", "longest_bottleneck"))
    require((c == p == d == 0) or 1 <= p <= c and 1 <= d <= c, "Contradictory bottleneck counts")
    bonus = Fraction(min(c, 4) + min(d, 4), 32)
    require(Fraction(*value["recurrence_bonus"]) == bonus and
            Fraction(*value["demand"]) == min(1, Fraction(*value["peak_strain"]) + bonus), "Wrong profile demand")
    for k in ("fluent_r1", "localized_combination"): boolean(value[k])
    require(not value["fluent_r1"] or value["highest_family"] == "R1", "Wrong fluent family")
    require(not value["localized_combination"] or value["highest_family"] == "R2" and
            Fraction(*value["strong_information_fraction"]) <= Fraction(1, 8), "Wrong local combination")
    if value["highest_family"] in ("R0", "R1"):
        require(value["strong_information_fraction"] == [0, 1] and value["demand"] == [0, 1], "Strong simple profile")


def _r4(value):
    if value is None: return
    from .certification import LABEL
    exact_keys(value, {"required", "label", "necessity", "proof", "baseline", "proof_profile_hash",
        "baseline_profile_hash", "proof_status", "baseline_status", "proof_verified", "baseline_verified", "instrumentation"})
    for k in ("required", "proof_verified", "baseline_verified"): boolean(value[k])
    require(value["proof_verified"] and value["baseline_verified"] and
            value["instrumentation"] == "separate_R4_evidence_not_synchronous_waves", "Unchecked R4")
    for k in ("proof", "baseline"):
        exact_keys(value[k], {"sha256", "bytes"}); sha(value[k]["sha256"])
        integer(value[k]["bytes"], 1, 64 * 1024 * 1024, "R4 file bytes")
    for k in ("proof_profile_hash", "baseline_profile_hash"): sha(value[k])
    for k in ("proof_status", "baseline_status"):
        require(value[k] in ("solved", "stalled", "contradiction", "aborted"), "Invalid R4 status")
    required = value["baseline_status"] == "stalled" and value["proof_status"] == "solved"
    require(value["required"] == required and value["label"] == (LABEL if required else None) and
            value["necessity"] == ("required" if required else "not_required" if value["baseline_status"] == "solved" else "unproven"),
            "Contradictory R4 necessity")


def _compact(value):
    exact_keys(value, {"result_hash", "trace_hash", "metrics_hash", "status", "reason", "line_analysis_complete",
                      "line_fixpoint_confirmed", "deduction_complete", "r4", "metrics"})
    for k in ("result_hash", "trace_hash", "metrics_hash"): sha(value[k])
    require(value["status"] in ("solved", "stalled", "contradiction", "aborted"), "Invalid compact status")
    require(value["reason"] in REASONS if value["status"] == "aborted" else value["reason"] is None, "Invalid compact reason")
    for k in ("line_analysis_complete", "line_fixpoint_confirmed", "deduction_complete"): boolean(value[k])
    _r4(value["r4"])
    require(value["line_analysis_complete"] == (value["status"] == "solved") and
            value["line_fixpoint_confirmed"] == (value["status"] in ("solved", "stalled")) and
            value["deduction_complete"] == (value["status"] == "solved" or bool(value["r4"] and value["r4"]["proof_status"] == "solved")),
            "Contradictory analysis completeness")
    if value["r4"] and value["r4"]["required"]:
        require(value["status"] == "stalled", "R4 requires stalled SD baseline")
    m = exact_keys(value["metrics"], METRICS)
    w = exact_keys(m["workload"], {"width", "height", "cells", "colors", "clue_count", "clue_length_sum", "total_clues", "total_clue_length"})
    for k in ("width", "height"): integer(w[k], 1, 50, k)
    integer(w["cells"], 1, 2500, "cells"); integer(w["colors"], 1, 8, "colors")
    require(w["cells"] == w["width"] * w["height"], "Wrong workload area")
    for k, total in (("clue_count", "total_clues"), ("clue_length_sum", "total_clue_length")):
        exact_keys(w[k], {"row", "column"})
        for n in w[k].values(): integer(n, 0, 250000, k)
        integer(w[total], 0, 500000, total)
        require(w[total] == sum(w[k].values()), "Wrong workload total")
    for k in METRICS - {"workload", "family_waves", "family_line_applications", "rule_applications", "highest_family_used",
                         "simple_fraction_all_cells", "simple_fraction_determined", "r0_fraction_all_cells", "aggregation"}:
        integer(m[k], 0, 8000000, k)
    integer(m["wave_count"], 0, 80000, "waves")
    for k in ("unique_changed_cells", "unique_partial_cells", "new_singletons"): integer(m[k], 0, w["cells"], k)
    for k in ("family_waves", "family_line_applications", "rule_applications"):
        exact_keys(m[k], set(RULE_IDS) if k == "rule_applications" else {"R0", "R1", "R2", "R3"})
        for n in m[k].values(): integer(n, 0, 8000000, k)
    require(sum(m["family_waves"].values()) == m["wave_count"] and
            m["highest_family_used"] == max((k for k, n in m["family_waves"].items() if n), default=None), "Wrong family summary")
    for family, waves in m["family_waves"].items():
        applications = m["family_line_applications"][family]
        rules = [n for rule,n in m["rule_applications"].items() if rule.startswith(family + "-")]
        require(waves <= applications <= waves * (w["width"] + w["height"]) and
                applications <= sum(rules) <= applications * len(rules), "Contradictory family/rule frequencies")
    require(m["aggregation"] is None and m["cell_change_events"] == m["new_singletons"] + m["partial_change_events"] and
            m["unique_partial_cells"] <= m["unique_changed_cells"] <= m["cell_change_events"] and
            m["new_singletons"] <= m["unique_changed_cells"] and
            m["cell_change_events"] <= m["removed_values"] <= w["cells"] * w["colors"], "Contradictory compact metrics")
    for k, denominator in (("simple_fraction_all_cells", w["cells"]), ("simple_fraction_determined", m["new_singletons"]),
                           ("r0_fraction_all_cells", w["cells"])):
        fraction(m[k], reduced=False, undefined=True)
        require(m[k][1] == denominator, "Wrong compact fraction denominator")
    require(m["simple_fraction_all_cells"][0] == m["simple_fraction_determined"][0] and
            m["r0_fraction_all_cells"][0] <= m["simple_fraction_all_cells"][0], "Contradictory simple counts")
    if value["status"] == "solved":
        require(m["new_singletons"] == w["cells"], "Incomplete solved metrics")
    if value["status"] == "stalled":
        require(m["new_singletons"] < w["cells"], "Completed stalled metrics")


def _rating(rating, compact, identifier):
    exact_keys(rating, {"format", "method", "method_hash", "analysis_result_hash", "source", "result", "rating_hash"})
    require(len(canonical_bytes(rating)) + 1 <= 65536 and rating["format"] == RATING_FORMAT, "Invalid SD-B rating")
    method = frozen_method()
    require(digest(rating["method"]) == digest(method) == sha(rating["method_hash"]), "Unknown difficulty method")
    require(sha(rating["analysis_result_hash"]) == compact["result_hash"], "Wrong analysis result binding")
    check_hash(rating, "rating_hash")
    s = exact_keys(rating["source"], {"sha256", "bytes", "kind", "engine_logic_hash", "definition_id", "runtime_revision", "production_mode"})
    sha(s["sha256"]); sha(s["engine_logic_hash"])
    integer(s["bytes"], 1, 2 * 1024 * 1024, "source size")
    integer(s["runtime_revision"], 1, 1000000, "original revision")
    require(s["kind"] == "runtime" and s["definition_id"] == identifier and s["production_mode"] == "unknown", "Wrong rating source")
    r = exact_keys(rating["result"], {"status", "reason", "assessment_type", "logical_level", "size_pressure", "size_adjustment",
        "level", "confidence", "estimated_minutes", "r4_required", "logical_demand", "profile", "workload", "uncertainty", "explanation"})
    boolean(r["r4_required"])
    paired = bool(compact["r4"] and compact["r4"]["required"])
    valid = compact["status"] == "solved" or paired
    reason = None if valid else ("analysis_aborted" if compact["status"] == "aborted" else
        "line_contradiction" if compact["status"] == "contradiction" else
        "r4_necessity_unproven" if compact["r4"] and compact["r4"]["necessity"] == "unproven" else "analysis_incomplete")
    features = r["profile"]
    if valid and not paired:
        _profile(features)
        require(features["highest_family"] == compact["metrics"]["highest_family_used"] and
                features["bottleneck_waves"] <= compact["metrics"]["wave_count"] and
                features["cleanup_suffix_waves"] <= compact["metrics"]["family_waves"]["R0"], "Profile/metrics disagree")
    else:
        require(features is None, "Unexpected line profile")
    base = 5 if paired else logical_level(features, method["configuration"]) if valid else None
    workload = {k: compact["metrics"]["workload"][k] for k in ("width", "height", "cells")}
    pressure, adjustment = size_effect(workload["cells"], base, features, method["configuration"]) if valid else (None, None)
    level = base + adjustment if valid else None
    expected = {"status": "rated" if valid else "unrated", "reason": reason,
        "assessment_type": "instrumented" if valid else None, "logical_level": base, "size_pressure": pressure,
        "size_adjustment": adjustment, "level": level, "confidence": "medium" if valid else None,
        "estimated_minutes": None, "r4_required": paired, "logical_demand": compact["r4"]["label"] if paired else None,
        "profile": features, "workload": workload, "uncertainty": {"model": "rule_based_estimate", "human_calibration": "not_performed",
        "technical": "verified_complete" if valid else "incomplete"},
        "explanation": (f"Logische Basis {base}; Größenbeitrag {adjustment}; Stufe {level}. "
                        "Instrumentierte Modellschätzung, nicht menschlich kalibriert." if valid else f"Keine Einstufung: {reason}.")}
    require(digest(r) == digest(expected), "Inconsistent frozen rating result")


def validate(value, *, active=True, definition_bytes=None):
    extras = {"rating_revision", "adoption", "record_hash"} if active else {"analysis_report_hash", "verification_hash", "tool", "checked_hash"}
    exact_keys(value, {"format"} | FIELDS | extras)
    require(value["format"] == (FORMAT if active else CHECKED), "Unknown catalog difficulty format")
    encoded(value)
    source(value["current_source"]); binding(value["logic_binding"])
    _compact(value["compact_analysis"])
    _rating(value["rating"], value["compact_analysis"], value["current_source"]["id"])
    if active:
        integer(value["rating_revision"], 1, 1000000, "rating revision")
        a = exact_keys(value["adoption"], {"kind", "previous_record_hash", "analysis_report_hash", "verification_hash", "tool", "report"})
        require(a["kind"] in ("analysis", "rebind"), "Unknown adoption kind")
        if a["previous_record_hash"] is not None: sha(a["previous_record_hash"])
        if a["report"] is not None:
            from .catalog_analysis import run_id
            exact_keys(a["report"], {"run_id", "result_hash"})
            run_id(a["report"]["run_id"]); sha(a["report"]["result_hash"])
        require(value["rating"]["result"]["status"] == "rated", "Active difficulty must be complete")
    else:
        a = value
    for k in ("analysis_report_hash", "verification_hash"): sha(a[k])
    tool(a["tool"])
    check_hash(value, "record_hash" if active else "checked_hash")
    if definition_bytes is not None:
        data, puzzle, current, logic = definition(definition_bytes)
        require(value["current_source"] == current and value["logic_binding"] == logic and
                value["rating"]["source"]["engine_logic_hash"] == puzzle.logic_hash, "Stale difficulty source/logic/matrix binding")
        w = value["compact_analysis"]["metrics"]["workload"]
        require((w["width"], w["height"], w["colors"]) == (puzzle.width, puzzle.height, len(puzzle.colors)), "Wrong rating workload")
        for axis, lines in (("row", data["rows"]), ("column", data["columns"])):
            require(w["clue_count"][axis] == sum(map(len, lines)) and w["clue_length_sum"][axis] ==
                    sum(c["length"] for line in lines for c in line), "Wrong rating clue workload")
        if value["compact_analysis"]["r4"]:
            from .contract import selected_profile
            r4 = value["compact_analysis"]["r4"]
            require(r4["proof_profile_hash"] == digest(selected_profile(puzzle, "paired-lines-color")) and
                    r4["baseline_profile_hash"] == digest(puzzle.profile), "Wrong compact R4 profiles")
    return value


def project(value):
    r = value["rating"]["result"]
    require(r["status"] == "rated", "Cannot project incomplete rating")
    level = "L" + str(r["level"])
    return {"method": METHOD_ID, "level": level, "assessment_type": "instrumented", "confidence": "medium",
            "plausible_range": [level, level], "r4_required": r["r4_required"]}


def import_bundle(input_path, bundle, *, budget=None):
    from .analysis_io import check_bundle
    from .catalog_analysis import safe_external
    from .authoring_package import file_table, file_hash
    input_path, bundle = safe_external(input_path), safe_external(bundle)
    inputs = {"source": file_hash(input_path), "bundle": {n: file_hash(p) for n, p in file_table(bundle, time.monotonic() + 300).items()}}
    checked = check_bundle(input_path, bundle, budget, method=METHOD_ID)
    report = load_json(bundle / "report.json", 64 * 1024 * 1024)
    rating = load_json(bundle / "rating.json", 65536)
    _, _, current, logic = definition(input_path.read_bytes())
    result = report["result"]
    compact = {k: result[k] for k in ("trace_hash", "status", "reason", "line_analysis_complete", "line_fixpoint_confirmed", "deduction_complete", "r4")}
    compact.update(result_hash=report["result_hash"], metrics_hash=digest(result["metrics"]),
                   metrics={k: v for k, v in result["metrics"].items() if k != "waves"})
    value = hashed({"format": CHECKED, "current_source": current, "logic_binding": logic, "rating": rating,
                    "compact_analysis": compact, "analysis_report_hash": digest({k: v for k,v in report.items() if k != "operation"}),
                    "verification_hash": digest(checked),
                    "tool": tool_identity()}, "checked_hash")
    value = validate(value, active=False, definition_bytes=input_path.read_bytes())
    require(inputs == {"source": file_hash(input_path), "bundle": {n: file_hash(p) for n, p in file_table(bundle, time.monotonic() + 300).items()}},
            "Analysis bundle changed during checked import")
    return value


def rebind_checked(value, raw):
    validate(value, active=False)
    _, _, current, logic = definition(raw)
    require(value["current_source"]["id"] == current["id"] and value["logic_binding"] == logic, "Rebind changes logic or target matrix")
    new = deepcopy(value)
    new["current_source"] = current
    new.pop("checked_hash")
    return validate(hashed(new, "checked_hash"), active=False, definition_bytes=raw)


def active_record(checked, previous=None, *, report=None, kind="analysis"):
    validate(checked, active=False)
    require(checked["rating"]["result"]["status"] == "rated", "New integration requires a complete 0.3 rating")
    if previous is not None:
        validate(previous)
        if all(previous[k] == checked[k] for k in FIELDS): return previous
    value = {"format": FORMAT, "rating_revision": 1 if previous is None else previous["rating_revision"] + 1,
             **{k: deepcopy(checked[k]) for k in FIELDS}, "adoption": {
                 "kind": kind, "previous_record_hash": previous["record_hash"] if previous else None,
                 **{k: deepcopy(checked[k]) for k in ("analysis_report_hash", "verification_hash", "tool")}, "report": report}}
    return validate(hashed(value, "record_hash"))


def checked_from_active(value):
    validate(value)
    return validate(hashed({"format": CHECKED, **{k: deepcopy(value[k]) for k in FIELDS},
        **{k: deepcopy(value["adoption"][k]) for k in ("analysis_report_hash", "verification_hash", "tool")}}, "checked_hash"), active=False)


def load_sources(root, registry):
    from .content_update import path_in
    records = {}
    for entry in registry["entries"]:
        target = path_in(root, path(entry["id"]))
        if target.exists():
            require(target.is_file(), "Difficulty source must be a regular file")
            raw = path_in(root, "game/" + entry["definition"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == entry["production"]["definition_sha256"], "Definition differs from registry")
            records[entry["id"]] = validate(bytes_json(read_file(target)), definition_bytes=raw)
    return records
