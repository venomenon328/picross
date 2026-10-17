"""Frozen SD-B scoring of independently verified SD-A data; no catalog access.

The reducers are pure arithmetic, not proof checkers. File callers must first
verify the complete analysis bundle, including any claimed R4 evidence.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction
from pathlib import Path

from .analysis_contract import ANALYZER, RULES
from .contract import InvalidInput, InvalidProof, canonical_bytes, digest, load_json
from .difficulty_identity import METHOD_HASH

METHOD_ID = "picross-difficulty-0.3"
RATING_FORMAT = "picross-difficulty-rating-v1"
RATING_BYTE_LIMIT = 65536
_ROOT = Path(__file__).parent


def frozen_method():
    """Fail closed on changed configuration, references or implementation bytes."""
    method = load_json(_ROOT / "difficulty_method_0_3.json", RATING_BYTE_LIMIT)
    if digest(method) != METHOD_HASH:
        raise InvalidInput("Unknown or changed difficulty method configuration")
    references = load_json(_ROOT / "difficulty_references_0_3.json", 512 * 1024)
    if digest(references) != method["references"]["hash"]:
        raise InvalidInput("Changed difficulty calibration references")
    calibration = load_json(_ROOT / "difficulty_calibration_0_3.json", RATING_BYTE_LIMIT)
    if digest(calibration) != method["calibration"]["hash"]:
        raise InvalidInput("Changed difficulty calibration evidence")
    for name, expected in method["implementation"].items():
        if hashlib.sha256((_ROOT / name).read_bytes()).hexdigest() != expected:
            raise InvalidInput(f"Changed frozen difficulty implementation: {name}")
    return method


def require_method(method_id, config):
    if method_id != METHOD_ID:
        raise InvalidInput("Unknown difficulty method")
    method = frozen_method()
    if digest(config) != digest(method["analysis_parameters"]):
        raise InvalidInput("Difficulty 0.3 requires its exact frozen analysis parameters")
    return method


def _fraction(value):
    return Fraction(*value)


def _wire(value):
    return [value.numerator, value.denominator]


def profile(metrics, config):
    """Reduce checked nonempty productive waves; never use operational counters."""
    waves = metrics["waves"]
    area = metrics["workload"]["cells"]
    colors = metrics["workload"]["colors"]
    peak = Fraction(0)
    count = phases = longest = duration = 0
    fluent = localized = True
    strong_removed = 0
    highest = 0
    for wave in waves:
        family = int(wave["family"][1])
        highest = max(highest, family)
        offer = _fraction(wave["productive_fraction"])
        gain = sum((Fraction(a - b, a - 1) for a, b in wave["domain_cardinalities"]),
                   Fraction(0)) / wave["open_cells_before"]
        if family == 1:
            fluent &= offer >= _fraction(config["fluent_offer"]) or gain >= _fraction(config["fluent_gain"])
        if family >= 2:
            strong_removed += wave["removed_values"]
            localized &= (offer >= _fraction(config["local_offer"])
                          and gain >= _fraction(config["local_gain"]))
            peak = max(peak, (1 - offer) * (1 - gain))
        narrow = (family >= 2 and offer <= _fraction(config["narrow_offer"])
                  and gain <= _fraction(config["narrow_gain"]))
        if narrow:
            count += 1
            phases += duration == 0
            duration += 1
            longest = max(longest, duration)
        else:
            duration = 0
    strong = Fraction(strong_removed, area * colors)
    bonus = (min(count, config["recurrence_cap"]) * _fraction(config["frequency_weight"])
             + min(longest, config["recurrence_cap"]) * _fraction(config["duration_weight"]))
    cleanup = 0
    for wave in reversed(waves):
        if wave["family"] != "R0":
            break
        cleanup += 1
    return {"highest_family": f"R{highest}", "strong_information_fraction": _wire(strong),
            "simple_information_fraction": _wire(1 - strong), "peak_strain": _wire(peak),
            "bottleneck_waves": count, "bottleneck_phases": phases,
            "longest_bottleneck": longest, "recurrence_bonus": _wire(bonus),
            "demand": _wire(min(Fraction(1), peak + bonus)),
            "cleanup_suffix_waves": cleanup,
            "fluent_r1": highest == 1 and fluent,
            "localized_combination": highest == 2 and localized
                and strong <= _fraction(config["local_information"])}


def logical_level(features, config):
    family = int(features["highest_family"][1])
    if family == 0 or features["fluent_r1"]:
        return 1
    if family == 1 or features["localized_combination"]:
        return 2
    severe = _fraction(features["demand"]) >= _fraction(config["severe_demand"])
    return family + 1 + int(severe)


def size_effect(area, level, features, config):
    pressure = min(_fraction(config["size_cap"]), max(Fraction(0),
        Fraction(area - config["size_neutral_cells"], config["size_divisor"])))
    adjustment = 0
    if level == 2 and pressure >= _fraction(config["size_easy_threshold"]):
        adjustment = 1
    elif level in (3, 4) and features is not None:
        demand = _fraction(features["demand"])
        if (int(features["highest_family"][1]) >= level - 1
                and demand >= _fraction(config["size_min_demand"])
                and demand + pressure >= _fraction(config["severe_demand"])):
            adjustment = 1
    return _wire(pressure), adjustment


def rating_result(analysis, method):
    """Pure reconstruction; analysis MUST originate from verified result_data."""
    if (analysis["analyzer"] != ANALYZER or analysis["rules"] != RULES
            or digest(analysis["parameters"]) != digest(method["analysis_parameters"])):
        raise InvalidProof("Wrong analyzer/rules/parameters for frozen rating")
    r4 = analysis["r4"]
    required = bool(r4 and r4["required"] and r4["necessity"] == "required"
                    and r4["baseline_status"] == "stalled" and r4["proof_status"] == "solved"
                    and r4["baseline_verified"] and r4["proof_verified"]
                    and analysis["status"] == "stalled" and analysis["line_fixpoint_confirmed"])
    complete = analysis["status"] == "solved" and analysis["line_analysis_complete"]
    valid = complete or required
    workload = {k: analysis["metrics"]["workload"][k] for k in ("width", "height", "cells")}
    reason = None if valid else (
        "analysis_aborted" if analysis["status"] == "aborted" else
        "line_contradiction" if analysis["status"] == "contradiction" else
        "r4_necessity_unproven" if r4 and r4["necessity"] == "unproven" else "analysis_incomplete")
    features = profile(analysis["metrics"], method["configuration"]) if complete else None
    base = 5 if required else logical_level(features, method["configuration"]) if complete else None
    pressure, adjustment = size_effect(workload["cells"], base, features,
                                       method["configuration"]) if valid else (None, None)
    level = base + adjustment if valid else None
    return {"status": "rated" if valid else "unrated", "reason": reason,
            "assessment_type": "instrumented" if valid else None,
            "logical_level": base, "size_pressure": pressure, "size_adjustment": adjustment,
            "level": level, "confidence": "medium" if valid else None,
            "estimated_minutes": None, "r4_required": required,
            "logical_demand": r4["label"] if required else None, "profile": features,
            "workload": workload, "uncertainty": {"model": "rule_based_estimate",
                "human_calibration": "not_performed", "technical": "verified_complete" if valid else "incomplete"},
            "explanation": (f"Logische Basis {base}; Größenbeitrag {adjustment}; Stufe {level}. "
                            "Instrumentierte Modellschätzung, nicht menschlich kalibriert."
                            if valid else f"Keine Einstufung: {reason}.")}


def rating_data(report, method):
    """Construct from the freshly checked v1 report, never from caller flags alone."""
    data = {"format": RATING_FORMAT, "method": method, "method_hash": digest(method),
            "analysis_result_hash": report["result_hash"], "source": report["source"],
            "result": rating_result(report["result"], method)}
    return {**data, "rating_hash": digest(data)}


def write_rating(directory, report, method):
    rating = rating_data(report, method)
    data = canonical_bytes(rating) + b"\n"
    if len(data) > RATING_BYTE_LIMIT:
        raise InvalidInput("Rating exceeds 64 KiB")
    with (directory / "rating.json").open("xb") as stream:
        stream.write(data)
    return rating


def check_rating(directory, report, method):
    path = directory / "rating.json"
    if path.is_symlink() or not path.is_file():
        raise InvalidProof("Missing rating or symlink rating")
    actual = load_json(path, RATING_BYTE_LIMIT)
    expected = rating_data(report, method)
    # Canonical equality checks ALL types, fields and bindings, even rehashed edits.
    if digest(actual) != digest(expected):
        raise InvalidProof("Rating differs from frozen method or checked analysis")
    return {"rating_verified": True, "rating_hash": expected["rating_hash"],
            "level": expected["result"]["level"]}
