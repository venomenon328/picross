"""0.4 catalog envelopes. Only explicit bundle import verifies deductions.

Routine validation checks bounded data, arithmetic and definition bindings;
it never invokes the analyzer, verifier, solver or raw-profile census.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import time

from .authoring_package import require, sha, file_hash, file_table
from .contract import canonical_bytes, digest, exact_keys, integer
from . import catalog_rating as common, catalog_method
from .sd2_rating import METHOD_ID, RATING, _aggregate, _workload, CONFIG

FORMAT = "picross-catalog-difficulty-v3"
CHECKED = "picross-checked-difficulty-v3"
CONTEXT = "picross-difficulty-context-v2"
RATING_FORMAT = "picross-catalog-sd2-rating-v1"
MODULES = common.MODULES + ("sd2_catalog_rating.py", "catalog_method.py")


def rational(value, *, maximum=10**100):
    require(isinstance(value, list) and len(value) == 2, "Expected SD2 rational")
    integer(value[0], 0, maximum, "SD2 numerator")
    integer(value[1], 1, 10**100, "SD2 denominator")
    number = F(*value)
    require([number.numerator, number.denominator] == value, "Noncanonical SD2 rational")
    return number


def structure(value):
    exact_keys(value, {"width", "height", "cells", "colors", "total_clues", "total_clue_length",
        "clue_length_histogram", "short_blocks", "adjacent_color_changes", "mandatory_gaps", "geometric_slack"})
    for k in ("width", "height"): integer(value[k], 1, 50, k)
    integer(value["colors"], 1, 8, "colors")
    integer(value["cells"], 1, 2500, "cells")
    require(value["cells"] == value["width"] * value["height"], "Wrong SD2 area")
    for k in ("total_clues", "total_clue_length", "short_blocks", "adjacent_color_changes", "mandatory_gaps", "geometric_slack"):
        integer(value[k], 0, 5000, k)
    hist = value["clue_length_histogram"]
    require(isinstance(hist, dict) and len(hist) <= 50, "Invalid clue histogram")
    for k, v in hist.items():
        require(isinstance(k, str) and k in {str(i) for i in range(1, 51)}, "Invalid histogram length")
        integer(v, 1, 5000, "histogram count")
    require(sum(hist.values()) == value["total_clues"] and
            sum(int(k) * v for k, v in hist.items()) == value["total_clue_length"] and
            sum(v for k, v in hist.items() if int(k) <= 2) == value["short_blocks"], "Wrong clue histogram totals")


def compact(value):
    exact_keys(value, {"result_hash", "analysis_hash", "trace_hash", "profiles_hash", "status", "reason",
        "line_analysis_complete", "line_fixpoint_confirmed", "deduction_complete", "r4", "structure", "wave_count", "new_singletons"})
    for k in ("result_hash", "analysis_hash", "trace_hash", "profiles_hash"): sha(value[k])
    from .sd2_contract import REASONS
    require(value["status"] in ("solved", "stalled", "contradiction", "aborted"), "Invalid SD2 status")
    require(value["reason"] in REASONS if value["status"] == "aborted" else value["reason"] is None, "Invalid SD2 reason")
    for k in ("line_analysis_complete", "line_fixpoint_confirmed", "deduction_complete"): common.boolean(value[k])
    common._r4(value["r4"])
    require(value["line_analysis_complete"] == (value["status"] == "solved") and
            value["line_fixpoint_confirmed"] == (value["status"] in ("solved", "stalled")) and
            value["deduction_complete"] == (value["status"] == "solved" or bool(value["r4"] and value["r4"]["proof_status"] == "solved")),
            "Contradictory SD2 completeness")
    require(not value["r4"] or not value["r4"]["required"] or value["status"] == "stalled", "R4 requires stalled SD2")
    structure(value["structure"])
    integer(value["wave_count"], 0, 80000, "SD2 waves")
    integer(value["new_singletons"], 0, value["structure"]["cells"], "SD2 singletons")
    if value["status"] == "solved": require(value["new_singletons"] == value["structure"]["cells"], "Incomplete solved SD2")
    if value["status"] == "stalled": require(value["new_singletons"] < value["structure"]["cells"], "Completed stalled SD2")


def assessment(value, evidence, paired):
    exact_keys(value, {"contributions", "score", "level", "without_workload", "level_without_workload", "boundaries", "signals"})
    for k in ("level", "level_without_workload"): integer(value[k], 1, 5, k)
    exact_keys(value["contributions"], {"demand", "search", "workload"})
    for v in value["contributions"].values(): rational(v)
    for k in ("score", "without_workload"): rational(value[k])
    exact_keys(value["boundaries"], {"lower", "upper", "distance_lower", "distance_upper", "nearest_distance"})
    for v in value["boundaries"].values():
        if v is not None: rational(v)
    s = value["signals"]
    if paired:
        expected = _aggregate(F(*CONFIG["r4_demand"]), F(0), F(0), {
            "r4_required": True, "line_profiles_are_prefix": True,
            "search_and_workload": "fixed_anchor_not_full_pair_measurement"})
    else:
        exact_keys(s, {"highest_family", "fluent", "context", "peak_search", "narrow_waves", "longest_narrow_run",
            "spans", "raw_workload", "workload_guard", "workload_ceiling"})
        high = s["highest_family"]
        require(high in ("E0", "E1", "E2", "E3"), "Invalid SD2 highest family")
        common.boolean(s["fluent"])
        context, peak = rational(s["context"]), rational(s["peak_search"])
        raw = rational(s["raw_workload"])
        require(context < 1 and peak <= 1 and (high not in ("E0", "E1") or context == 0), "Invalid SD2 context/search")
        for k in ("narrow_waves", "longest_narrow_run"): integer(s[k], 0, evidence["wave_count"], k)
        count, longest = s["narrow_waves"], s["longest_narrow_run"]
        require((count == longest == 0) or 1 <= longest <= count, "Invalid SD2 narrow runs")
        integer(s["spans"], 0, evidence["new_singletons"], "SD2 spans")
        integer(s["workload_ceiling"], 1, 5, "SD2 workload ceiling")
        require(s["workload_guard"] in ("fluent", "upper_boundary", "none") and
                (not s["fluent"] or high in ("E0", "E1")) and
                (high != "E0" or s["fluent"] and peak == count == longest == 0), "Invalid SD2 fluent signals")
        demand = F(0) if high == "E0" else F(*CONFIG["fluent_demand"]) if s["fluent"] else F(int(high[1])) + context * F(*CONFIG["context_weight"])
        search = peak + (min(count, CONFIG["recurrence_cap"]) + min(longest, CONFIG["recurrence_cap"])) * F(*CONFIG["recurrence_weight"])
        expected_raw = min(F(*CONFIG["work_cap"]), max(F(0), F(s["spans"] - CONFIG["work_neutral_spans"], CONFIG["work_divisor"])))
        work, guard, ceiling = _workload(demand + search, high, search, s["fluent"], expected_raw)
        require(raw == expected_raw and s["workload_guard"] == guard and s["workload_ceiling"] == ceiling, "Wrong SD2 workload guard")
        expected = _aggregate(demand, search, work, s)
    require(digest(value) == digest(expected), "Inconsistent frozen SD2 assessment")


def rating(value, evidence, identifier):
    exact_keys(value, {"format", "method", "method_hash", "analysis_result_hash", "source", "result", "rating_hash"})
    require(value["format"] == RATING_FORMAT and value["method"] == METHOD_ID and
            len(canonical_bytes(value)) + 1 <= 65536 and value["method_hash"] == catalog_method.method_hash(METHOD_ID), "Invalid SD2 catalog rating/method")
    common.check_hash(value, "rating_hash")
    require(sha(value["analysis_result_hash"]) == evidence["result_hash"], "Wrong SD2 analysis result binding")
    s = exact_keys(value["source"], {"sha256", "bytes", "kind", "engine_logic_hash", "definition_id", "runtime_revision", "production_mode"})
    sha(s["sha256"]); sha(s["engine_logic_hash"])
    integer(s["bytes"], 1, 2 * 1024 * 1024, "SD2 input bytes")
    integer(s["runtime_revision"], 1, 1000000, "SD2 original revision")
    require(s["kind"] == "runtime" and s["definition_id"] == identifier and s["production_mode"] == "unknown", "Wrong SD2 original source")
    r = exact_keys(value["result"], {"format", "method", "method_hash", "analysis_result_hash", "status", "reason", "profile_scope",
        "assessment", "confidence", "estimated_minutes", "explanation"})
    paired = bool(evidence["r4"] and evidence["r4"]["required"])
    rated = evidence["status"] == "solved" or paired
    reason = "required_r4" if paired else "complete_line" if rated else (evidence["reason"] or "analysis_aborted") if evidence["status"] == "aborted" else (
        "contradiction" if evidence["status"] == "contradiction" else "r4_necessity_unproven" if evidence["r4"] else "incomplete_line")
    explanation = "Model estimate from synthetic references; no human calibration or time estimate. " + (
        "Required R4 uses a fixed anchor; line profiles are prefixes, not complete pair measurements." if paired else
        "Demand, search and bounded workload use independently checked line profiles." if rated else
        "No rating: complete line deduction or proved R4 necessity is missing.")
    expected = {"format": RATING, "method": METHOD_ID, "method_hash": value["method_hash"],
        "analysis_result_hash": evidence["result_hash"], "status": "rated" if rated else "unrated", "reason": reason,
        "profile_scope": "line_prefix" if paired else "complete_line" if rated else "incomplete",
        "assessment": r["assessment"], "confidence": "medium" if rated else None, "estimated_minutes": None, "explanation": explanation}
    require(digest(r) == digest(expected), "Invalid SD2 rating result")
    if rated: assessment(r["assessment"], evidence, paired)
    else: require(r["assessment"] is None, "Incomplete SD2 has an assessment")


def validate(value, *, active=True, definition_bytes=None, production_mode=None):
    extras = {"rating_revision", "adoption", "record_hash"} if active else {"analysis_report_hash", "verification_hash", "tool", "checked_hash"}
    exact_keys(value, {"format", "production_mode"} | common.FIELDS | extras)
    require(value["format"] == (FORMAT if active else CHECKED), "Wrong SD2 envelope")
    common.encoded(value)
    common.mode(value["production_mode"])
    if production_mode is not None: require(value["production_mode"] == common.mode(production_mode), "Stale difficulty production mode; new analysis required")
    common.source(value["current_source"]); common.binding(value["logic_binding"])
    compact(value["compact_analysis"])
    require(value["compact_analysis"]["analysis_hash"] == value["logic_binding"]["analysis_hash"], "Wrong SD2 normalized logic binding")
    rating(value["rating"], value["compact_analysis"], value["current_source"]["id"])
    a = value
    if active:
        integer(value["rating_revision"], 1, 1000000, "rating revision")
        a = exact_keys(value["adoption"], {"kind", "previous_record_hash", "analysis_report_hash", "verification_hash", "tool", "report"})
        require(a["kind"] in ("analysis", "rebind"), "Invalid SD2 adoption kind")
        if a["previous_record_hash"] is not None: sha(a["previous_record_hash"])
        if a["report"] is not None:
            from .catalog_analysis import run_id
            exact_keys(a["report"], {"run_id", "result_hash"})
            run_id(a["report"]["run_id"]); sha(a["report"]["result_hash"])
        require(value["rating"]["result"]["status"] == "rated", "Active SD2 must be complete")
    for k in ("analysis_report_hash", "verification_hash"): sha(a[k])
    common.tool(a["tool"], version=2)
    common.check_hash(value, "record_hash" if active else "checked_hash")
    if definition_bytes is not None:
        _, puzzle, source, binding = common.definition(definition_bytes, method=METHOD_ID)
        require(source == value["current_source"] and binding == value["logic_binding"] and
                value["rating"]["source"]["engine_logic_hash"] == puzzle.logic_hash, "Stale SD2 source/logic/matrix binding")
        require(value["production_mode"] != "mono" or len(puzzle.colors) == 1, "Mono mode requires one foreground color")
        from .sd2_profiles import structure as expected_structure
        require(value["compact_analysis"]["structure"] == expected_structure(puzzle), "Wrong SD2 definition workload")
        if value["compact_analysis"]["r4"]:
            from .contract import selected_profile
            r4 = value["compact_analysis"]["r4"]
            require(r4["proof_profile_hash"] == digest(selected_profile(puzzle, "paired-lines-color")) and
                    r4["baseline_profile_hash"] == digest(puzzle.profile), "Wrong SD2 R4 profile binding")
    return value


def project(value):
    r = value["rating"]["result"]
    require(r["status"] == "rated", "Cannot project incomplete SD2")
    level = "L" + str(r["assessment"]["level"])
    return {"method": METHOD_ID, "level": level, "assessment_type": "instrumented", "confidence": "medium",
        "plausible_range": [level, level], "r4_required": r["profile_scope"] == "line_prefix"}


def import_bundle(input_path, bundle, *, budget=None):
    from .catalog_analysis import safe_external
    from .sd2_rating_io import check_rating_bundle
    input_path, bundle = safe_external(input_path), safe_external(bundle)
    require(bundle.is_dir() and {p.name for p in bundle.iterdir()} == {"catalog-context.json", "rating"}, "Invalid SD2 catalog bundle members")
    def snapshot():
        return {"source": file_hash(input_path), "bundle": {n: file_hash(p) for n, p in file_table(bundle, time.monotonic() + 300).items()}}
    before = snapshot()
    raw = common.read_file(input_path, 2 * 1024 * 1024)
    _, _, source, binding = common.definition(raw, method=METHOD_ID)
    context = common.bytes_json(common.read_file(bundle / "catalog-context.json"))
    exact_keys(context, {"format", "production_mode", "source", "method", "method_hash", "context_hash"})
    require(context["format"] == CONTEXT and context["source"] == source and context["method"] == METHOD_ID and
            context["method_hash"] == catalog_method.method_hash(METHOD_ID), "Wrong SD2 catalog context")
    common.check_hash(context, "context_hash"); common.mode(context["production_mode"])
    checked = check_rating_bundle(input_path, bundle / "rating", budget)
    report = common.bytes_json(common.read_file(bundle / "rating/analysis/report.json", 64 * 1024 * 1024), 64 * 1024 * 1024)
    result = report["result"]
    compacted = {k: result[k] for k in ("analysis_hash", "trace_hash", "status", "reason", "line_analysis_complete", "line_fixpoint_confirmed", "deduction_complete", "r4")}
    compacted.update(result_hash=report["result_hash"], profiles_hash=digest(result["profiles"]),
        structure=result["profiles"]["workload"]["structure"], wave_count=len(result["profiles"]["demand"]["trajectory"]),
        new_singletons=result["profiles"]["workload"]["new_singletons"])
    embedded = common.hashed({"format": RATING_FORMAT, "method": METHOD_ID, "method_hash": context["method_hash"],
        "analysis_result_hash": report["result_hash"], "source": report["source"], "result": checked["result"]}, "rating_hash")
    value = common.hashed({"format": CHECKED, "production_mode": context["production_mode"], "current_source": source,
        "logic_binding": binding, "rating": embedded, "compact_analysis": compacted,
        "analysis_report_hash": digest({k: v for k, v in report.items() if k != "operation"}),
        "verification_hash": digest(checked), "tool": common.tool_identity(version=2)}, "checked_hash")
    validate(value, active=False, definition_bytes=raw)
    require(before == snapshot(), "SD2 bundle changed during checked import")
    return value
