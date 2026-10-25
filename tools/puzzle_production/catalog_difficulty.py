"""KE: spoiler-free projection of existing assessments, never a new assessment."""
from .authoring_package import require

LEVELS = ("L1", "L2", "L3", "L4", "L5")
METHODS = ("picross-difficulty-0.1", "picross-difficulty-0.2")


def project(raw):
    # The old registry explicitly allowed an empty difficulty object.
    require(isinstance(raw, dict), "Invalid catalog difficulty")
    if not raw:
        return None
    require(raw.get("method") in METHODS and raw.get("level") in LEVELS and
            raw.get("assessment_type") in ("editorial_estimate", "instrumented") and
            raw.get("confidence") in ("low", "medium", "high"), "Invalid catalog difficulty assessment")
    span = raw.get("plausible_range")
    require(isinstance(span, list) and len(span) == 2 and
            all(level in LEVELS for level in span) and span[0] <= raw["level"] <= span[1],
            "Invalid catalog difficulty range")
    families = raw.get("rule_families")
    require(isinstance(families, dict) and families and
            all(k in ("R0", "R1", "R2", "R3", "R4") and isinstance(v, str) and v.strip()
                for k, v in families.items()), "Invalid catalog difficulty rule families")
    paired = "R4" in families
    if "r4_required" in raw:
        require(type(raw["r4_required"]) is bool and raw["r4_required"] == paired,
                "Contradictory catalog difficulty R4 flag")
    if paired:
        require(raw["method"] == METHODS[1] and raw["level"] == "L5" and span == ["L5", "L5"] and
                raw["assessment_type"] == "instrumented" and raw["confidence"] == "medium" and
                raw.get("logical_demand") == "linienübergreifend / besonders hoher logischer Anspruch",
                "Invalid necessary R4 assessment")
    return {**{k: raw[k] for k in ("method", "level", "assessment_type", "confidence")},
            "plausible_range": span.copy(), "r4_required": paired}


def validate_projection(value, *, version=4):
    """Exactly the six-field runtime contract, including the 0.3 point estimate."""
    from .contract import exact_keys
    require(type(version) is int and version in (2, 3, 4, 5), "Unsupported runtime difficulty version")
    if value is None: return None
    exact_keys(value, {"method", "level", "assessment_type", "confidence", "plausible_range", "r4_required"})
    require(type(value["r4_required"]) is bool and value["level"] in LEVELS, "Invalid runtime difficulty")
    if value["method"] == "picross-difficulty-0.3" or version == 5 and value["method"] == "picross-difficulty-0.4":
        require(value["assessment_type"] == "instrumented" and value["confidence"] == "medium" and
                value["plausible_range"] == [value["level"], value["level"]] and
                (not value["r4_required"] or value["level"] == "L5"), "Invalid 0.3 projection")
    else:
        project({**value, "rule_families": {"R4" if value["r4_required"] else "R0": "typed projection"},
                 "logical_demand": "linienübergreifend / besonders hoher logischer Anspruch" if value["r4_required"] else None})
    return value
