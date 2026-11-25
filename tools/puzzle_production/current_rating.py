"""Current assessment envelope without producer/tool/receipt requirements."""
from copy import deepcopy
from .contract import exact_keys, digest, integer
from .authoring_package import require
from .raster_parameters import require_color_count, used_foreground
from . import catalog_rating as common, catalog_method

FORMAT = "picross-current-difficulty-v1"
FIELDS = {"format","method","production_mode","current_source","logic_binding",
          "rating","compact_analysis","rating_revision","record_hash"}


def validate(value, *, definition_bytes=None, production_mode=None, active=False):
    exact_keys(value,FIELDS)
    require(value["format"]==FORMAT and value["method"] in catalog_method.METHODS,"Unknown current assessment")
    common.mode(value["production_mode"])
    require(production_mode is None or production_mode==value["production_mode"],"Assessment mode differs")
    common.source(value["current_source"]); common.binding(value["logic_binding"])
    integer(value["rating_revision"],1,1000000,"rating revision")
    common.check_hash(value,"record_hash")
    if value["method"]==catalog_method.NEW:
        from . import sd2_catalog_rating as method
        method.compact(value["compact_analysis"])
        require(value["compact_analysis"]["analysis_hash"]==value["logic_binding"]["analysis_hash"],"Assessment logic differs")
        method.rating(value["rating"],value["compact_analysis"],value["current_source"]["id"])
        color_count = value["compact_analysis"]["structure"]["colors"]
    else:
        common._compact(value["compact_analysis"])
        common._rating(value["rating"],value["compact_analysis"],value["current_source"]["id"])
        color_count = value["compact_analysis"]["metrics"]["workload"]["colors"]
    if not active:
        require_color_count(value["production_mode"], color_count)
    require(value["rating"]["result"]["status"]=="rated","Complete current assessment required")
    if definition_bytes is not None:
        data,puzzle,source,logic=common.definition(definition_bytes,method=value["method"])
        require(value["current_source"]==source and value["logic_binding"]==logic and
                value["rating"]["source"]["engine_logic_hash"]==puzzle.logic_hash,"Stale assessment definition")
        if not active:
            require_color_count(value["production_mode"], len(used_foreground(data["solution"])))
        else:
            require(value["production_mode"] != "mono" or len(puzzle.colors) == 1,
                    "Mono assessment has multiple colors")
        if value["method"]==catalog_method.NEW:
            from .sd2_profiles import structure
            require(value["compact_analysis"]["structure"]==structure(puzzle),"Assessment geometry differs")
        else:
            workload=value["compact_analysis"]["metrics"]["workload"]
            require((workload["width"],workload["height"],workload["colors"])==
                    (puzzle.width,puzzle.height,len(puzzle.colors)),"Assessment geometry differs")
            for axis,lines in (("row",data["rows"]),("column",data["columns"])):
                require(workload["clue_count"][axis]==sum(map(len,lines)) and
                        workload["clue_length_sum"][axis]==sum(c["length"] for line in lines for c in line),
                        "Assessment clues differ")
        if value["compact_analysis"]["r4"]:
            from .contract import selected_profile
            r4=value["compact_analysis"]["r4"]
            require(r4["proof_profile_hash"]==digest(selected_profile(puzzle,"paired-lines-color")) and
                    r4["baseline_profile_hash"]==digest(puzzle.profile),"Assessment R4 profile differs")
    return value


def _assessment(value, method):
    result = {"format": FORMAT, "method": method, "rating_revision": 1,
              **{k: deepcopy(value[k]) for k in common.FIELDS | {"production_mode"}}}
    result["record_hash"] = digest(result)
    return validate(result)


def from_checked(value):
    """Extract the current assessment produced by the existing analyzer."""
    common.validate(value, active=False)
    return _assessment(value, common.method(value))


def from_paired_proofs(definition_bytes, baseline_bytes, proof_bytes, production_mode, final_budget):
    """Build a current SD2 rating with R4 verification on the repair budget."""
    from .analysis_io import check_r4, check_target, source_binding
    from .contract import Aborted
    from .sd2_analysis import analyze
    from .sd2_catalog_rating import compact_rating
    from .sd2_contract import AnalysisBudget, result_data
    from .sd2_io import _binding, _json
    from .sd2_rating import _rating_result
    from .sd2_verifier import verify_trace

    method = catalog_method.NEW
    method_hash = catalog_method.method_hash(method)
    definition, puzzle, source, logic = common.definition(definition_bytes, method=method)
    require_color_count(production_mode, len(used_foreground(definition["solution"])))

    trace = analyze(puzzle)
    analysis_verification = AnalysisBudget()
    verify_trace(puzzle, trace, analysis_verification)
    check_target(definition, "runtime", puzzle, trace)
    try:
        r4 = check_r4(puzzle, trace, _json(proof_bytes), _json(baseline_bytes),
                      _binding(proof_bytes), _binding(baseline_bytes), final_budget)
    except Aborted as exc:
        raise Aborted(f"r4_verifier_{exc}") from exc

    result = result_data(puzzle, trace, r4, analysis_verification)
    analysis_verification.check()
    result_hash = digest(result)
    rating_source = source_binding(definition_bytes, definition, puzzle, "runtime")
    rating, compact = compact_rating(result, result_hash, rating_source, method_hash,
                                     _rating_result(result, result_hash, method_hash))
    return _assessment({"current_source": source, "logic_binding": logic, "rating": rating,
                        "compact_analysis": compact, "production_mode": production_mode}, method)


def active(value,previous=None):
    validate(value)
    if previous is not None:
        common.validate(previous)
        if all(value[k]==previous.get(k) for k in common.FIELDS|{"production_mode"}):return previous
    result=deepcopy(value)
    result["rating_revision"]=previous["rating_revision"]+1 if previous else 1
    result["record_hash"]=digest({k:v for k,v in result.items() if k!="record_hash"})
    return validate(result)
