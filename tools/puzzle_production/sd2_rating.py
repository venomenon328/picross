"""SD2-B exact reducers. Internal arithmetic only, NEVER proof or rating entrypoints.

Use sd2_rating_io to rate independently rechecked file bundles. In particular,
calling these reducers on a dict does not establish R4 necessity or completeness.
"""
from __future__ import annotations

from fractions import Fraction as F

METHOD_ID = "picross-difficulty-0.4"
FORMULA = "sd2-rating-formula-1"
RATING = "picross-sd2-rating-v1"
CONFIG = {
    "thresholds": [1, 2, 3, 4], "fluent_offer": [1, 2], "fluent_gain": [1, 2],
    "fluent_demand": [1, 4], "context_weight": [1, 4], "context_offset": 3,
    "narrow_offer": [1, 4], "narrow_gain": [1, 4], "recurrence_cap": 4,
    "recurrence_weight": [1, 32], "work_neutral_spans": 40, "work_divisor": 640,
    "work_cap": [1, 4], "work_high_search": [3, 4], "work_boundary_fraction": [1, 2],
    "r4_demand": [9, 2],
}


def _wire(value):
    value = F(value)
    return [value.numerator, value.denominator]


def _level(score):
    return 1 + sum(score >= t for t in CONFIG["thresholds"])


def _boundaries(score):
    lower = max((F(t) for t in CONFIG["thresholds"] if t <= score), default=None)
    upper = min((F(t) for t in CONFIG["thresholds"] if t > score), default=None)
    below = None if lower is None else score - lower
    above = None if upper is None else upper - score
    return {"lower": None if lower is None else _wire(lower),
            "upper": None if upper is None else _wire(upper),
            "distance_lower": None if below is None else _wire(below),
            "distance_upper": None if above is None else _wire(above),
            "nearest_distance": _wire(min(v for v in (below, above) if v is not None))}


def _aggregate(demand, search, work, signals):
    base = demand + search
    score = base + work
    return {"contributions": {"demand": _wire(demand), "search": _wire(search), "workload": _wire(work)},
            "score": _wire(score), "level": _level(score), "without_workload": _wire(base),
            "level_without_workload": _level(base), "boundaries": _boundaries(score), "signals": signals}


def _workload(base, high, search, fluent, raw):
    ceiling = max(_level(base), 3 if high in ("E0", "E1") or search < F(*CONFIG["work_high_search"])
                  else 4 if high == "E2" else 5)
    work = F(0) if fluent else raw if ceiling == 5 else min(
        raw, (ceiling - base) * F(*CONFIG["work_boundary_fraction"]))
    return work, ("fluent" if fluent else "upper_boundary" if work < raw else "none"), ceiling


def _line_rating(profiles):
    demand_profile, search_profile, work_profile = (profiles[k] for k in ("demand", "search", "workload"))
    waves = list(zip(demand_profile["trajectory"], search_profile["trajectory"], strict=True))
    high = demand_profile["highest_family"]
    fluent = high in ("E0", "E1") and all(
        F(*q["offer"]) >= F(*CONFIG["fluent_offer"]) or F(*q["gain"]) >= F(*CONFIG["fluent_gain"])
        for a, q in waves if a["family"] == "E1")
    context = peak = F(0)
    count = longest = run = 0
    for a, q in waves:
        if a["family"] in ("E2", "E3"):
            blocks = a["interacting_blocks"] / (F(*q["offer"]) * q["state"]["open_lines"])
            ambiguous = q["state"]["ambiguous_required_cells"]
            owner_pressure = F(ambiguous, ambiguous + q["state"]["unique_owner_required_cells"] + 1)
            context = max(context, max(F(0), blocks - 1) / (blocks + CONFIG["context_offset"]), owner_pressure)
        if a["family"] != "E0":
            peak = max(peak, F(*q["strain"]))
        narrow = (a["family"] != "E0" and F(*q["offer"]) <= F(*CONFIG["narrow_offer"])
                  and F(*q["gain"]) <= F(*CONFIG["narrow_gain"]))
        run = run + 1 if narrow else 0
        longest = max(longest, run)
        count += narrow
    demand = (F(0) if high == "E0" else F(*CONFIG["fluent_demand"]) if fluent
              else F(int(high[1])) + context * F(*CONFIG["context_weight"]))
    cap = CONFIG["recurrence_cap"]
    search = peak + (min(count, cap) + min(longest, cap)) * F(*CONFIG["recurrence_weight"])
    spans = work_profile["fill_spans"] + work_profile["empty_spans"]
    raw = min(F(*CONFIG["work_cap"]), max(F(0), F(spans - CONFIG["work_neutral_spans"], CONFIG["work_divisor"])))
    work, guard, ceiling = _workload(demand + search, high, search, fluent, raw)
    return _aggregate(demand, search, work, {
        "highest_family": high, "fluent": fluent, "context": _wire(context), "peak_search": _wire(peak),
        "narrow_waves": count, "longest_narrow_run": longest, "spans": spans,
        "raw_workload": _wire(raw), "workload_guard": guard, "workload_ceiling": ceiling})


def _rating_result(analysis, analysis_hash, method_hash):
    """Only call after fresh independent A/R4 verification and byte binding."""
    r4 = analysis["r4"]
    needed = (analysis["status"] == "stalled" and analysis["line_fixpoint_confirmed"]
              and r4 is not None and r4["required"] and r4["necessity"] == "required"
              and r4["baseline_status"] == "stalled" and r4["proof_status"] == "solved"
              and r4["baseline_verified"] and r4["proof_verified"])
    assessment = None
    if analysis["status"] == "solved" and analysis["line_analysis_complete"]:
        assessment = _line_rating(analysis["profiles"])
        reason, scope = "complete_line", "complete_line"
    elif needed:
        assessment = _aggregate(F(*CONFIG["r4_demand"]), F(0), F(0), {
            "r4_required": True, "line_profiles_are_prefix": True,
            "search_and_workload": "fixed_anchor_not_full_pair_measurement"})
        reason, scope = "required_r4", "line_prefix"
    else:
        reason = (analysis["reason"] or "analysis_aborted") if analysis["status"] == "aborted" else (
            "contradiction" if analysis["status"] == "contradiction" else
            "r4_necessity_unproven" if r4 else "incomplete_line")
        scope = "incomplete"
    return {"format": RATING, "method": METHOD_ID, "method_hash": method_hash,
            "analysis_result_hash": analysis_hash, "status": "rated" if assessment is not None else "unrated",
            "reason": reason, "profile_scope": scope, "assessment": assessment,
            "confidence": "medium" if assessment is not None else None, "estimated_minutes": None,
            "explanation": ("Model estimate from synthetic references; no human calibration or time estimate. "
                + ("Required R4 uses a fixed anchor; line profiles are prefixes, not complete pair measurements."
                   if needed else "Demand, search and bounded workload use independently checked line profiles."
                   if assessment is not None else "No rating: complete line deduction or proved R4 necessity is missing."))}


def _report(result):
    def number(value):
        return "-" if value is None else str(value[0]) if value[1] == 1 else f"{value[0]}/{value[1]}"
    lines = ["# SD2 difficulty model", "", f"Method: {result['method']}",
             f"Method hash: {result['method_hash']}", f"Analysis result: {result['analysis_result_hash']}",
             f"Status: {result['status']} ({result['reason']})", f"Profile scope: {result['profile_scope']}", ""]
    rating = result["assessment"]
    if rating is not None:
        lines += ["| Contribution | Exact value |", "| --- | --- |"]
        lines += [f"| {key} | {number(value)} |" for key, value in rating["contributions"].items()]
        lines += ["", f"Score: {number(rating['score'])}; level: {rating['level']} / 5.",
                  f"Without workload: {number(rating['without_workload'])}; level: {rating['level_without_workload']}.",
                  f"Lower boundary: {number(rating['boundaries']['lower'])}; distance: {number(rating['boundaries']['distance_lower'])}.",
                  f"Upper boundary: {number(rating['boundaries']['upper'])}; distance: {number(rating['boundaries']['distance_upper'])}.",
                  f"Nearest boundary distance: {number(rating['boundaries']['nearest_distance'])}.", ""]
    lines += [f"Confidence: {result['confidence'] or 'unrated'}. Estimated minutes: unavailable.", result["explanation"], ""]
    return "\n".join(lines).encode("utf-8")
