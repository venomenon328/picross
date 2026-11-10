"""BA-A's closed adapters to the existing, local production operations.

This module owns no checkpoint, catalog, publication or approval.  In particular,
an output slot is evidence from a real operation, never permission to promote a
handoff or to rewrite a sealed production request.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
from io import BytesIO
import math
from pathlib import Path
import platform
import re
import tempfile
import time

from . import authoring_package as ap, catalog_io as io
from .contract import (Aborted, Budget, InvalidInput, InvalidProof, canonical_bytes,
                       digest, exact_keys, integer, load_json, validate_logic)


def _spec(inputs, nullable, parameters, limits, produce, slots,
          candidate_slots=(), required_decisions=()):
    return {"inputs": tuple(inputs), "nullable": tuple(nullable),
            "parameters": tuple(parameters), "limits": limits, "produce": produce,
            "slots": tuple(slots), "candidate_slots": tuple(candidate_slots),
            "required_decisions": tuple(required_decisions)}


_VARIANT_SLOTS = ("design", "matrix", "logic", "proof", "baseline", "assessment")
_RASTER_DECISIONS = ("motif", "parameters")
OPERATION_SPECS = {
    ("image_import", "produce"): _spec(
        ("image", "design", "approval"), ("approval",), ("profile", "candidates"),
        "logic", True, ("bundle",), _VARIANT_SLOTS, _RASTER_DECISIONS),
    ("candidate_verify", "verify"): _spec(
        ("bundle",), (), ("candidate",), "logic", False, ("bundle",), _VARIANT_SLOTS),
    ("logic_certify", "solve"): _spec(
        ("logic",), (), ("profile", "order"), "logic", True,
        ("logic", "proof", "baseline", "assessment"), required_decisions=_RASTER_DECISIONS),
    ("repair", "search"): _spec(
        ("reference", "plan", "approval"), ("approval",), (), "repair", True,
        ("repair_bundle", "design", "matrix", "logic", "proof", "baseline", "assessment"),
        required_decisions=(*_RASTER_DECISIONS, "repair")),
    ("repair", "verify"): _spec(
        ("reference", "bundle"), (), (), "logic", False,
        ("repair_bundle", "design", "matrix", "logic", "proof", "baseline", "assessment")),
    ("difficulty", "analyze"): _spec(
        ("design", "matrix", "logic", "proof", "baseline", "r4_proof", "r4_baseline"),
        ("baseline", "r4_proof", "r4_baseline"),
        ("puzzle_id", "runtime_revision", "production_mode", "method"), "analysis", True,
        ("candidate", "analysis_bundle", "checked_difficulty"), required_decisions=_RASTER_DECISIONS),
    ("difficulty", "import"): _spec(
        ("candidate", "bundle"), (), ("method",), "analysis", False,
        ("candidate", "analysis_bundle", "checked_difficulty")),
    ("background", "derive"): _spec(
        ("request",), ("request",), (), "fixed", True, ("background_finding", "background_png")),
    ("background", "verify"): _spec(
        ("request", "bundle"), ("request",), (), "fixed", False,
        ("background_finding", "background_png")),
    ("authoring_build", "build"): _spec(
        ("request",), ("request",), (), "fixed", True, ("package", "handoff", "record", "sheet_update")),
}

STAGE_STATUSES = frozenset(("pending", "running", "completed", "waiting_input", "waiting_human",
                            "blocked", "failed", "aborted", "interrupted", "stale"))
_PROFILES = ("full-line-mono", "full-line-color", "paired-lines-mono", "paired-lines-color")
_VARIANT = re.compile(r"[a-z][a-z0-9_-]{0,31}\Z")
_SLOT = re.compile(r"[a-z][a-z0-9_]*(?::[a-z][a-z0-9_-]{0,31})?\Z")
_USAGE = ("lines", "pair_work", "pair_records", "steps", "candidates", "rule_work", "waves")
_LOGIC_LIMITS = ("seconds", "max_lines", "max_pair_work", "max_pair_records")
_ANALYSIS_LIMITS = (*_LOGIC_LIMITS, "max_rule_work", "max_waves")
_REPAIR_LIMITS = ("search_seconds", "final_seconds", "search_lines", "final_lines",
                  "max_steps", "max_candidates", "max_changes")
_ROOT = Path(__file__).resolve().parents[2]
_CORE = {"__init__", "batch_operations", "batch_contract", "batch_io", "batch_runner", "batch_worker",
         "contract", "authoring_package", "authoring_build_contract", "background_io", "background_contract",
         "catalog_io", "operation_diagnostics"}
_LOGIC = {"solver", "verifier", "paired_solver", "paired_verifier", "certification"}
_IMAGES = _LOGIC | {"images", "image_normalization", "palette_gate", "palette_quality"}
_ANALYSIS = _IMAGES | {
    "catalog_analysis", "catalog_rating", "catalog_method", "catalog_difficulty", "target_adapter",
    "catalog_transaction", "catalog_integration", "categories", "analysis", "analysis_contract", "analysis_io", "analysis_rules", "analysis_verifier",
    "sd2_contract", "sd2_analysis", "sd2_rules", "sd2_verifier", "sd2_profiles", "sd2_io",
    "sd2_rating", "sd2_rating_io", "sd2_rating_freeze", "sd2_rating_identity", "sd2_catalog_rating",
    "difficulty_rating", "difficulty_identity",
}
_BACKGROUND = {"background_assets", "background_contract", "background_io", "image_normalization"}
_BUILDER = _ANALYSIS | _BACKGROUND | {
    "authoring_builder", "authoring_build_contract", "background_package", "repair", "accepted_raster",
    "manual_derivation", "color_derivation", "catalog_background", "background_rebind", "reveal_source",
}
_COMMON_NORMS = ("docs/PRODUCTION_BATCH.md",)
_METHOD_FILES = ("content/difficulty-method.json", "tools/puzzle_production/sd2_method_0_4.json",
                 "tools/puzzle_production/sd2_calibration_0_4.json",
                 "tools/puzzle_production/sd2_references_0_4.json",
                 "tools/puzzle_production/sd2_validation_0_4.json",
                 "tools/puzzle_production/sd2_comparison_0_4.json",
                 "tools/puzzle_production/difficulty_method_0_3.json",
                 "tools/puzzle_production/difficulty_references_0_3.json",
                 "tools/puzzle_production/difficulty_calibration_0_3.json")


def _require(condition, message):
    if not condition:
        raise InvalidInput(message)


def _text(value, label, *, nullable=False, maximum=4096):
    if value is None and nullable:
        return
    _require(type(value) is str and 0 < len(value) <= maximum and "\x00" not in value,
             "Invalid " + label)


def _read(path, limit=8 * 1024 * 1024):
    path = io.external(path)
    return io.read(path.parent, path.name, limit)


class _JsonSnapshot:
    """Use the domain's existing strict parser on the bytes securely read once."""

    def __init__(self, raw):
        self.raw = raw

    def open(self, mode):
        _require(mode == "rb", "Read-only JSON snapshot")
        return BytesIO(self.raw)


def _json(path, limit=8 * 1024 * 1024):
    # Catalog JSON's shorter numeric tokens do not admit real RP-3/RP-5 timing
    # floats. Preserve their original bytes and original production parser.
    return load_json(_JsonSnapshot(_read(path, limit)), limit)


def _file(path):
    path = io.external(path)
    raw = _read(path, ap.MAX_ZIP)
    return {"kind": "file", "path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _binding(path, name):
    f = _file(path)
    return {"file": name, "sha256": f["sha256"], "bytes": f["bytes"]}


def _directory(path):
    path = io.external(path)
    files = ap.file_table(path, time.monotonic() + ap.SECONDS)
    entries = [_binding(files[n], n) for n in sorted(files)]
    _require(sum(e["bytes"] for e in entries) <= ap.MAX_TOTAL, "Batch inventory exceeds 512 MiB")
    return {"kind": "directory", "path": str(path), "files": entries}


def _bundle(path, marker):
    path = io.external(path)
    if path.is_file():
        _require(path.name == marker, "Bundle source must name " + marker)
        path = path.parent
    _require(path.is_dir(), "Missing bundle directory")
    _directory(path)  # Guard every member, including members not consumed by the domain parser.
    _read(path / marker)
    return path


def _write(root, name, value):
    path = io.safe(root, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical_bytes(value) + b"\n"
    with path.open("xb") as stream:
        stream.write(raw)
    return _file(path)


def _tool_paths(kind):
    groups = {"logic_certify": _LOGIC, "image_import": _IMAGES, "candidate_verify": _IMAGES,
              "repair": _IMAGES | {"repair"}, "difficulty": _ANALYSIS,
              "background": _BACKGROUND, "authoring_build": _BUILDER}
    modules = sorted("tools/puzzle_production/" + n + ".py" for n in _CORE | groups[kind])
    norms = list(_COMMON_NORMS)
    if kind in ("image_import", "candidate_verify", "logic_certify", "repair", "difficulty", "authoring_build"):
        norms.append("docs/PUZZLE_PRODUCTION.md")
    if kind in ("image_import", "logic_certify", "repair", "difficulty", "authoring_build"):
        norms.append("docs/ai-workflows/PUZZLE_AUTHORING.md")
    if kind in ("difficulty", "authoring_build"):
        norms.extend((*_METHOD_FILES, "docs/SD2_INTEGRATION.md", "docs/SD2_ANALYZER.md"))
    if kind in ("background", "authoring_build"):
        norms.append("docs/PUZZLE_BACKGROUNDS.md")
    return modules, sorted(set(norms))


# Freeze source bytes when this adapter is loaded, including core modules that
# imported it. A later plan must not describe edited on-disk modules while the
# parent process still executes the earlier implementation. Conditional domain
# imports are admitted only while their files still match this same snapshot.
_LOADED_MODULES = {name: hashlib.sha256(_read(_ROOT / name)).hexdigest()
                   for name in sorted({name for kind, _ in OPERATION_SPECS for name in _tool_paths(kind)[0]})}


def expected_tool_binding(kind, operation, repo_root):
    _text(kind, "operation kind", maximum=128)
    _text(operation, "operation name", maximum=128)
    _require((kind, operation) in OPERATION_SPECS, "Unsupported batch operation")
    repo = io.external(repo_root)
    _require(repo == _ROOT, "Batch code and selected repository differ")
    modules, norms = _tool_paths(kind)
    bindings = [_binding(io.safe(repo, n), n) for n in modules]
    _require(all(item["sha256"] == _LOADED_MODULES[item["file"]] for item in bindings),
             "Relevant batch implementation changed in the running process; start a fresh process")
    versions = {}
    if kind == "background":
        from .background_assets import describe
        description = describe()
        _require("tool" in description, "Cannot establish the actual background tool: " + str(description.get("error")))
        versions = description["tool"]["versions"]
    elif kind != "logic_certify":
        from .images import versions as image_versions
        versions = image_versions()
    return {"format": "picross-batch-tool-v1", "python": platform.python_version(),
            "modules": bindings, "versions": versions,
            "norms": [_binding(io.safe(repo, n), n) for n in norms]}


def _validate_tool(value):
    exact_keys(value, {"format", "python", "modules", "versions", "norms"})
    _require(value["format"] == "picross-batch-tool-v1", "Unsupported batch tool format")
    _text(value["python"], "Python binding", maximum=128)
    for field in ("modules", "norms"):
        entries = value[field]
        _require(type(entries) is list and 1 <= len(entries) <= 256, "Invalid tool file bindings")
        names = []
        for item in entries:
            exact_keys(item, {"file", "sha256", "bytes"})
            ap.relative(item["file"])
            ap.sha(item["sha256"])
            integer(item["bytes"], 1, ap.MAX_ZIP, "tool bytes")
            names.append(item["file"])
        _require(names == sorted(set(names)) and len({n.casefold() for n in names}) == len(names),
                 "Tool bindings must be unique and sorted without aliases")
    _require(type(value["versions"]) is dict and set(value["versions"]) in (
        set(), {"tool", "pillow", "jpeg", "jpeg_turbo", "littlecms", "zlib"},
        {"python", "pillow", "littlecms", "zlib"}), "Invalid codec bindings")
    for item in value["versions"].values():
        _text(item, "codec version", nullable=True, maximum=128)


def _validate_limits(value, kind):
    if kind == "fixed":
        exact_keys(value, {"seconds"})
        _require(type(value["seconds"]) is int and value["seconds"] == 300, "Fixed operation budget is 300 seconds")
        return
    keys = _REPAIR_LIMITS if kind == "repair" else _ANALYSIS_LIMITS if kind == "analysis" else _LOGIC_LIMITS
    exact_keys(value, set(keys))
    for name in keys:
        v = value[name]
        if name.endswith("seconds"):
            high = 600 if name == "search_seconds" else 120 if name == "final_seconds" else math.inf
            _require(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= high,
                     "Invalid finite operation time: " + name)
        else:
            upper = {"max_pair_work": 100_000_000, "max_rule_work": 100_000_000,
                     "max_waves": 80_000, "max_steps": 1024, "max_candidates": 128,
                     "max_changes": 10000}.get(name, 1_000_000)
            integer(v, 1 if name == "max_candidates" else 0, upper, name)


def validate_operation(stage, repo_root, *, check_binding=True):
    exact_keys(stage, {"stage_id", "kind", "operation", "inputs", "parameters", "limits",
                       "max_attempts", "tool_binding"})
    _text(stage["kind"], "operation kind", maximum=128)
    _text(stage["operation"], "operation name", maximum=128)
    key = (stage["kind"], stage["operation"])
    _require(key in OPERATION_SPECS, "Unsupported batch operation")
    spec = OPERATION_SPECS[key]
    exact_keys(stage["inputs"], set(spec["inputs"]))
    for name, ref in stage["inputs"].items():
        _require(ref is not None or name in spec["nullable"], "Unexpected null input: " + name)
    p = exact_keys(stage["parameters"], set(spec["parameters"]))
    if "profile" in p:
        _require(p["profile"] in _PROFILES, "An explicit supported profile is required")
    if key == ("image_import", "produce"):
        ids = p["candidates"]
        _require(type(ids) is list and 1 <= len(ids) <= 8 and all(
            type(v) is str and _VARIANT.fullmatch(v) for v in ids) and len(set(ids)) == len(ids),
            "Invalid explicit import candidates")
    if key == ("candidate_verify", "verify"):
        _require(type(p["candidate"]) is str and _VARIANT.fullmatch(p["candidate"]), "Invalid candidate ID")
    if key == ("logic_certify", "solve"):
        _require(p["order"] in ("rows-first", "columns-first", "reverse"), "Invalid line order")
        _require(not p["profile"].startswith("paired-") or p["order"] == "rows-first",
                 "Paired certification uses rows-first")
    if stage["kind"] == "difficulty":
        methods = ("picross-difficulty-0.3", "picross-difficulty-0.4") if key[1] == "import" else ("picross-difficulty-0.4",)
        _require(p["method"] in methods, "Unsupported explicit difficulty method for this operation")
        if key[1] == "analyze":
            _require(type(p["puzzle_id"]) is str and ap.ID.fullmatch(p["puzzle_id"]), "Invalid difficulty puzzle ID")
            integer(p["runtime_revision"], 1, 1_000_000, "runtime_revision")
            _require(p["production_mode"] in ("mono", "color"), "Invalid production mode")
    limits = exact_keys(stage["limits"], {"produce", "revalidate"})
    if spec["produce"]:
        _validate_limits(limits["produce"], spec["limits"])
    else:
        _require(limits["produce"] is None, "Read-only operation must have produce=null")
    _validate_limits(limits["revalidate"], "logic" if spec["limits"] == "repair" else spec["limits"])
    attempts = exact_keys(stage["max_attempts"], {"produce", "revalidate"})
    for name in attempts:
        integer(attempts[name], 0, 100, "max_attempts." + name)
    _require(attempts["produce" if spec["produce"] else "revalidate"] > 0,
             "Operation needs an explicit positive attempt allowance")
    _validate_tool(stage["tool_binding"])
    reservation_limits(stage, "produce" if spec["produce"] else "revalidate")
    if check_binding:
        _require(stage["tool_binding"] == expected_tool_binding(*key, repo_root), "Batch tool binding differs")
    return stage


def reservation_limits(stage, attempt_type):
    """Bound real API fanout, including mandatory fresh output inspection.

    A producer reservation contains both budgets, but spends one producer attempt.
    This never resets the caller's persistent attempt accounting.
    """
    _require(attempt_type in ("produce", "revalidate"), "Invalid attempt type")
    p, r = stage["limits"]["produce"], stage["limits"]["revalidate"]
    spec = OPERATION_SPECS[stage["kind"], stage["operation"]]
    _require(attempt_type != "produce" or spec["produce"], "Read-only operation cannot produce")
    if attempt_type == "revalidate":
        fanout = len(stage["parameters"]["candidates"]) if stage["kind"] == "image_import" else 1
        if (stage["kind"], stage["operation"]) == ("difficulty", "analyze"):
            fanout = 2  # Production certificate and full independent analysis import.
        seconds = r["seconds"] * fanout
        _require(math.isfinite(seconds + 30), "Combined operation reservation must remain finite")
        return {"produce": None, "revalidate": deepcopy(r), "seconds": seconds + 30}
    kind = stage["kind"]
    if kind == "image_import":
        # Palette, solver and independent verifier per declared variant, followed
        # by fresh bundle inspection. Each upstream call has its own Budget.
        seconds = len(stage["parameters"]["candidates"]) * (3 * p["seconds"] + r["seconds"])
    elif kind == "repair":
        seconds = p["search_seconds"] + p["final_seconds"] + r["seconds"]
    elif kind == "logic_certify":
        seconds = p["seconds"] + r["seconds"]
    elif kind == "difficulty":
        # Original production proof; one analyzer; its verification plus the
        # complete checked import. The API itself owns these independent frames.
        seconds = p["seconds"] + 3 * r["seconds"]
    else:
        seconds = p["seconds"]
    _require(math.isfinite(seconds + 30), "Combined operation reservation must remain finite")
    return {"produce": deepcopy(p), "revalidate": deepcopy(r), "seconds": seconds + 30}


def _result(domain, *, status="completed", certified=None, slots=None, reason=None,
            candidates=(), method=None, state=None, usage=None, exit_code=0):
    result = {"status": status, "domain": domain, "certified": certified, "exit_code": exit_code,
              "slots": slots or {}, "details": {"reason": reason, "candidates": list(candidates),
                  "method": method, "state": state, "usage": {k: (usage or {}).get(k) for k in _USAGE}}}
    return validate_result(result)


def validate_result(result):
    exact_keys(result, {"status", "domain", "certified", "exit_code", "slots", "details"})
    _text(result["status"], "batch stage result status", maximum=128)
    _require(result["status"] in STAGE_STATUSES, "Invalid batch stage result status")
    _text(result["domain"], "domain status", maximum=128)
    _require(result["certified"] is None or type(result["certified"]) is bool, "Invalid certification")
    integer(result["exit_code"], 0, 255, "operation exit code")
    details = exact_keys(result["details"], {"reason", "candidates", "method", "state", "usage"})
    for name in ("reason", "method", "state"):
        _text(details[name], name, nullable=True)
    _require(type(details["candidates"]) is list and len(details["candidates"]) <= 128, "Invalid candidate results")
    seen = set()
    for row in details["candidates"]:
        exact_keys(row, {"candidate_id", "status", "certified"})
        _text(row["candidate_id"], "candidate result ID", maximum=128)
        _text(row["status"], "candidate domain status", maximum=128)
        _require(row["candidate_id"] not in seen and type(row["certified"]) is bool, "Invalid duplicate candidate result")
        seen.add(row["candidate_id"])
    exact_keys(details["usage"], set(_USAGE))
    for value in details["usage"].values():
        if value is not None:
            integer(value, 0, 10**15, "usage counter")
    _require(type(result["slots"]) is dict and len(result["slots"]) <= 64, "Invalid slots")
    for name, slot in result["slots"].items():
        _require(type(name) is str and _SLOT.fullmatch(name), "Invalid fixed slot name")
        base, _, variant = name.partition(":")
        _require(base in {s for spec in OPERATION_SPECS.values() for s in spec["slots"]}
                 or bool(variant) and base in _VARIANT_SLOTS, "Unknown output slot")
        _require(not variant or base in _VARIANT_SLOTS, "This output slot is not candidate-specific")
        _require(type(slot) is dict and slot.get("kind") in ("file", "directory"), "Invalid slot descriptor")
        exact_keys(slot, {"kind", "path", "sha256", "bytes"} if slot["kind"] == "file" else {"kind", "path", "files"})
        _text(slot["path"], "slot path")
        _require(Path(slot["path"]).is_absolute(), "Adapter slot path must be absolute")
        if slot["kind"] == "file":
            ap.sha(slot["sha256"])
            integer(slot["bytes"], 0, ap.MAX_ZIP, "slot bytes")
        else:
            _require(type(slot["files"]) is list and len(slot["files"]) <= ap.MAX_FILES, "Invalid slot inventory")
            names = []
            for item in slot["files"]:
                exact_keys(item, {"file", "sha256", "bytes"})
                ap.relative(item["file"])
                ap.sha(item["sha256"])
                integer(item["bytes"], 0, ap.MAX_ZIP, "inventory bytes")
                names.append(item["file"])
            _require(names == sorted(set(names)) and len({n.casefold() for n in names}) == len(names),
                     "Inventory must be unique and sorted")
            _require(sum(e["bytes"] for e in slot["files"]) <= ap.MAX_TOTAL, "Inventory byte limit")
    return result


def _decision_path(root, name):
    ap.relative(name)
    return io.safe(root, name)


def validate_decisions(stage, resolved_inputs, decisions, source_root):
    """Read existing authoring statements; never infer approval from free prose.

    Handoff paths retain their original package-relative meaning. The batch plan
    binds the original handoff file and original motif approval independently.
    RP-5's plan is an explicit bounded instruction, not a new approval format.
    """
    spec = OPERATION_SPECS[stage["kind"], stage["operation"]]
    decisions = {} if decisions is None else decisions
    _require(type(decisions) is dict and set(decisions) <= {"motif", "parameters", "repair", "background"},
             "Unknown batch decision")
    missing = [name for name in spec["required_decisions"] if decisions.get(name) is None]
    if missing:
        return _result("waiting_human", status="waiting_human", reason="Missing original decision: " + ", ".join(missing), exit_code=3)
    if not spec["required_decisions"]:
        return None
    source = io.external(source_root)
    hp, approval_path = io.external(decisions["parameters"]), io.external(decisions["motif"])
    _require(hp.is_relative_to(source) and approval_path.is_relative_to(source), "Decision escapes source root")
    h, approval = _json(hp), _json(approval_path)
    from .authoring_build_contract import HANDOFF_KEYS
    _require(type(h) is dict and h.get("format") in ("picross-authoring-handoff-v2", "picross-authoring-handoff-v3")
             and set(h) <= HANDOFF_KEYS | ({"background"} if h.get("format") == "picross-authoring-handoff-v3" else set()),
             "Parameters must bind an existing original Authoring handoff")
    ap.string(h.get("authorization"), "authoring authorization")
    _require(type(h.get("motif")) is dict, "Missing original handoff motif")
    motif = h["motif"]
    _require(_decision_path(hp.parent, motif.get("approval")) == approval_path,
             "Parameter handoff and original motif approval differ")
    motif_path = _decision_path(hp.parent, motif.get("file"))
    _require(type(approval) is dict and approval.get("type") == "human_motif_approval",
             "Missing original human_motif_approval")
    for name in ("actor", "statement", "revision"):
        ap.string(approval.get(name), "motif approval " + name)
    ap.timestamp(approval.get("timestamp_utc"))
    actual_sha = _file(motif_path)["sha256"]
    _require(approval.get("file") == motif.get("file") and approval.get("sha256") == actual_sha
             and motif.get("sha256") == actual_sha, "Motif approval does not bind the actual original image")
    ap.sha(approval.get("derived_from_reveal_sha256"))
    _require(approval.get("derived_from_reveal_sha256") == motif.get("derived_from_reveal_sha256"),
             "Motif/reveal source binding differs")
    _read(_decision_path(hp.parent, approval.get("evidence")))
    reveal = h.get("reveal")
    _require(type(reveal) is dict, "Missing original approved reveal binding")
    reveal_sha = _file(_decision_path(hp.parent, reveal.get("file")))["sha256"]
    _require(reveal.get("sha256") == reveal_sha == approval["derived_from_reveal_sha256"],
             "Motif does not derive from the actual approved reveal revision")
    reveal_approval = _json(_decision_path(hp.parent, reveal.get("approval")))
    _require(type(reveal_approval) is dict and reveal_approval.get("type") == "human_reveal_approval"
             and reveal_approval.get("file") == reveal["file"] and reveal_approval.get("sha256") == reveal_sha,
             "Original reveal approval binding differs")
    for name in ("actor", "statement", "revision"):
        ap.string(reveal_approval.get(name), "reveal approval " + name)
    ap.timestamp(reveal_approval.get("timestamp_utc"))
    _read(_decision_path(hp.parent, reveal_approval.get("evidence")))
    params = h.get("approved_parameters")
    _require(type(params) is list and 1 <= len(params) <= 32, "Missing explicit approved parameters")
    for p in params:
        _require(type(p) is dict, "Invalid approved parameter corridor")
        for name in ("width", "height", "foreground_colors"):
            integer(p.get(name), 1, 4096, "approved " + name)
        _require(p.get("mode") in ("mono", "color") and type(p.get("method")) is str
                 and type(p.get("fit")) is str and type(p.get("actual_crop")) is list
                 and len(p["actual_crop"]) == 4 and all(type(v) is int for v in p["actual_crop"]),
                 "Invalid approved mode/method/fit/crop")
    corridor = approval.get("parameters")
    _require(type(corridor) is dict, "Missing motif parameter binding")
    for name in ("width", "height", "foreground_colors"):
        integer(corridor.get(name), 1, 4096, "motif approval " + name)
    _require(any(all(p.get(k) == corridor.get(k) for k in
                    ("width", "height", "mode", "foreground_colors", "method")) for p in params),
             "Motif and handoff parameter decisions disagree")
    inputs, kind = resolved_inputs, stage["kind"]
    if "approval" in inputs:
        if inputs["approval"] is None:
            return _result("waiting_human", status="waiting_human", reason="Missing bound motif approval", exit_code=3)
        _require(io.external(inputs["approval"]) == approval_path, "Operation approval differs from motif decision")
    if kind == "image_import":
        _require(_file(inputs["image"])["sha256"] == actual_sha, "Import image is not the approved motif")
        design = _json(inputs["design"], 64 * 1024)
        variants = stage["parameters"]["candidates"]
    elif kind == "repair":
        _require(io.external(inputs["plan"]) == io.external(decisions["repair"]),
                 "Repair operation and explicit plan decision differ")
        plan = _json(inputs["plan"], 256 * 1024)
        ref = _bundle(inputs["reference"], "manifest.json")
        manifest = _json(ref / "manifest.json")
        _require(manifest.get("original") in ("original.png", "original.jpg"), "Invalid import original")
        _require(_file(ref / manifest["original"])["sha256"] == actual_sha, "Repair source is not the approved motif")
        variant = plan.get("reference", {}).get("variant")
        _require(type(variant) is str and _VARIANT.fullmatch(variant), "Invalid repair reference variant")
        candidate = _json(ref / (variant + "-candidate.json"))
        from .repair import validate_plan
        validated = validate_plan(plan, candidate)
        _require({k: validated["config"][k] for k in _REPAIR_LIMITS} == stage["limits"]["produce"],
                 "Batch repair limits must match the unchanged RP-5 plan")
        design, variants = candidate["design"], [variant]
    elif kind == "difficulty":
        design = _json(inputs["design"], 64 * 1024)
        ref = stage["inputs"]["matrix"]
        variants = [ref["candidate_id"]] if isinstance(ref, dict) and ref.get("candidate_id") is not None else None
    else:
        puzzle = validate_logic(_json(inputs["logic"], 2 * 1024 * 1024))
        mode = "mono" if puzzle.format == "picross-logic-v1" else "color"
        _require(any(p["width"] == puzzle.width and p["height"] == puzzle.height and p["mode"] == mode
                     and p["foreground_colors"] == len(puzzle.colors) for p in params)
                 and corridor["width"] == puzzle.width and corridor["height"] == puzzle.height
                 and corridor.get("mode") == mode and corridor["foreground_colors"] == len(puzzle.colors),
                 "Logic lies outside approved dimensions/mode/color count")
        return None
    from .images import validate_design
    design = validate_design(design)
    variants = [v["id"] for v in design["variants"] if v["method"] == corridor.get("method")] if variants is None else variants
    _require(bool(variants), "No approved design variant")
    for identifier in variants:
        variant = next((v for v in design["variants"] if v["id"] == identifier), None)
        _require(variant is not None and all(corridor.get(k) == design[k] for k in ("width", "height", "mode"))
                 and corridor["foreground_colors"] == len(design["palette"])
                 and corridor.get("method") == variant["method"], "Design differs from the motif parameter approval")
        _require(any(all(p.get(k) == design[k] for k in ("width", "height", "mode", "fit"))
                     and p["foreground_colors"] == len(design["palette"])
                     and p["actual_crop"] == design["crop"] and p["method"] == variant["method"] for p in params),
                 "Design lies outside the approved parameter corridor")
    return None


@contextmanager
def _workspace(output_root, source_root):
    output, source = io.external(output_root), io.external(source_root)
    _require(output.is_dir() and source.is_dir(), "Source/output roots must exist")
    _require(not output.is_relative_to(source) and not source.is_relative_to(output), "Source/output roots overlap")
    for name in ("game", "content"):
        _require(not output.is_relative_to(_ROOT / name), "Batch output overlaps the active repository data")
    # Existing ZIP/history readers use tempfile without a dir argument. The
    # serial isolated worker redirects their temporary files into its own root.
    temporary = io.safe(output, "_tmp")
    _require(not temporary.exists(), "Unowned adapter temporary directory")
    temporary.mkdir()
    previous = tempfile.tempdir
    tempfile.tempdir = str(temporary)
    try:
        yield output
    finally:
        tempfile.tempdir = previous
        if temporary.is_dir() and not any(temporary.iterdir()):
            temporary.rmdir()


def _logic_budget(limits):
    return Budget(**{k: limits[k] for k in _LOGIC_LIMITS})


def _usage(budget):
    return {"lines": budget.lines, "pair_work": budget.pair_work,
            "pair_records": budget.pair_peak_records}


def _checked_slots(slots):
    for slot in slots.values():
        actual = _file(slot["path"]) if slot["kind"] == "file" else _directory(slot["path"])
        _require(actual == slot, "Saved output bytes or inventory changed")


def _input_paths(stage, inputs):
    exact_keys(inputs, set(OPERATION_SPECS[stage["kind"], stage["operation"]]["inputs"]))
    return {name: io.external(path) if path is not None else None for name, path in inputs.items()}


def _import_result(directory, variants, limits, output, *, domain):
    from .images import inspect_candidate
    slots, candidates, totals = {"bundle": _directory(directory)}, [], {"lines": 0, "pair_work": 0, "pair_records": 0}
    for variant in variants:
        budget = _logic_budget(limits)
        candidate, proof, checked = inspect_candidate(directory, variant, budget)
        original = _json(directory / (variant + "-result.json"))
        # A stronger replay cannot turn an originally aborted producer into a
        # completed production certificate.
        certified = bool(checked["certified"] and original.get("certified") is True
                         and original.get("proof_verified") is True and original.get("status") == "solved")
        status = original["status"] if original.get("status") == "aborted" else checked["status"]
        candidates.append({"candidate_id": variant, "status": status, "certified": certified})
        slots["design:" + variant] = _file(directory / "design.json")
        slots["matrix:" + variant] = _write(output, "projections/" + variant + "-matrix.json", candidate["matrix"])
        slots["logic:" + variant] = _file(directory / (variant + "-logic.json"))
        slots["proof:" + variant] = _file(directory / (variant + "-proof.json"))
        if proof["format"] == "picross-proof-v3":
            slots["baseline:" + variant] = _file(directory / (variant + "-baseline-proof.json"))
            slots["assessment:" + variant] = _file(directory / (variant + "-assessment.json"))
        for name, value in _usage(budget).items():
            totals[name] = max(totals[name], value) if name == "pair_records" else totals[name] + value
    return _result(domain or candidates[0]["status"], certified=all(c["certified"] for c in candidates), slots=slots,
                   candidates=candidates, usage={**totals, "candidates": len(candidates)})


def _solve(stage, inputs, output):
    from . import certification
    from .solver import solve
    from .verifier import verify
    logic = _json(inputs["logic"], 2 * 1024 * 1024)
    puzzle = validate_logic(logic)
    limits, params = stage["limits"], stage["parameters"]
    budget, replay = _logic_budget(limits["produce"]), _logic_budget(limits["revalidate"])
    config = certification.configuration(puzzle, params["profile"],
                                         limits["produce"]["max_pair_work"], limits["produce"]["max_pair_records"])
    if config:
        proof, checked = certification.produce(puzzle, output, "", config, budget, replay)
    else:
        proof = solve(puzzle, budget, params["order"], profile=params["profile"])
        _write(output, "proof.json", proof)
        try:
            checked = verify(puzzle, _json(output / "proof.json", puzzle.proof_byte_limit), replay)
        except Aborted as exc:
            checked = {"status": "aborted", "certified": False, "proof_verified": False, "reason": str(exc)}
    slots = {"logic": _file(inputs["logic"]), "proof": _file(output / "proof.json")}
    if config:
        slots.update(baseline=_file(output / "baseline-proof.json"), assessment=_file(output / "assessment.json"))
    usage = {k: (max(_usage(budget)[k], _usage(replay)[k]) if k == "pair_records"
                 else _usage(budget)[k] + _usage(replay)[k]) for k in _usage(budget)}
    aborted = checked["status"] == "aborted"
    return _result(checked["status"], status="aborted" if aborted else "completed", certified=checked["certified"],
                   slots=slots, reason=checked.get("reason"), usage=usage, exit_code=4 if aborted else 0)


def _solve_recheck(stage, inputs, saved):
    from . import certification
    from .verifier import verify
    puzzle = validate_logic(_json(inputs["logic"], 2 * 1024 * 1024))
    budget = _logic_budget(stage["limits"]["revalidate"])
    slots = saved["slots"]
    _require(slots["logic"] == _file(inputs["logic"]), "Saved solve logic differs")
    proof_path = Path(slots["proof"]["path"])
    config = certification.configuration(puzzle, stage["parameters"]["profile"],
        stage["limits"]["produce"]["max_pair_work"], stage["limits"]["produce"]["max_pair_records"])
    if config:
        _require(proof_path.name == "proof.json" and slots.get("baseline", {}).get("path") == str(proof_path.parent / "baseline-proof.json")
                 and slots.get("assessment", {}).get("path") == str(proof_path.parent / "assessment.json"),
                 "Paired solve must retain its original production files")
        _, checked = certification.inspect(puzzle, proof_path.parent, "", config, budget)
    else:
        proof = _json(proof_path, puzzle.proof_byte_limit)
        certification.require_legacy(puzzle, proof)
        checked = verify(puzzle, proof, budget)
    _require(checked["status"] == saved["domain"] and bool(checked["certified"]) == saved["certified"],
             "Fresh solve verification differs from saved result")
    return _result(saved["domain"], status=saved["status"], certified=saved["certified"], slots=slots,
                   reason=saved["details"]["reason"], usage=_usage(budget), exit_code=saved["exit_code"])


def _repair_result(directory, reference, limits, output):
    from .repair import inspect_repair
    budget = _logic_budget(limits)
    checked = inspect_repair(directory, reference, budget)
    raw, recorded = _json(directory / "repair.json"), _json(directory / "result.json")
    slots = {"repair_bundle": _directory(directory)}
    certified = checked["certified"] and checked["status"] == "found" and recorded.get("certified") is True
    if certified:
        variant = raw["reference"]["variant"]
        _require(type(variant) is str and _VARIANT.fullmatch(variant), "Invalid repair reference variant")
        candidate = _json(reference / (variant + "-candidate.json"))
        slots.update(design=_write(output, "projections/design.json", candidate["design"]),
                     matrix=_write(output, "projections/matrix.json", raw["matrix"]),
                     logic=_file(directory / "final-logic.json"), proof=_file(directory / "final-proof.json"))
        if raw["format"] == "picross-repair-v2":
            slots.update(baseline=_file(directory / "final-baseline-proof.json"),
                         assessment=_file(directory / "final-assessment.json"))
    return _result(checked["status"], certified=bool(certified), slots=slots,
                   reason=recorded.get("reason"), usage={**_usage(budget), "steps": checked["steps"],
                                                       "candidates": checked["candidates"]})


def _active_method(repo_root, method):
    from . import catalog_method
    active = catalog_method.current(catalog_method.load(repo_root))
    _require(method == catalog_method.NEW and active["method"] == method
             and active["method_hash"] == catalog_method.method_hash(method),
             "Explicit difficulty method does not match the active 0.4 freeze")


def _production_proof(inputs, limits):
    from . import certification
    from .images import logic_from_matrix, validate_design
    from .verifier import verify
    design = validate_design(_json(inputs["design"], 64 * 1024))
    matrix, logic = _json(inputs["matrix"]), _json(inputs["logic"], 2 * 1024 * 1024)
    puzzle = validate_logic(logic)
    _require(validate_logic(logic_from_matrix(matrix, design)).to_wire() == puzzle.to_wire(),
             "Difficulty design/matrix/logic disagree")
    budget = _logic_budget(limits)
    proof = _json(inputs["proof"], puzzle.proof_byte_limit)
    if proof.get("format") == "picross-proof-v3":
        if inputs["baseline"] is None:
            return None, _result("waiting_input", status="waiting_input", reason="Paired production proof needs its original line baseline", exit_code=3)
        baseline = _json(inputs["baseline"], puzzle.proof_byte_limit)
        certification.require_legacy(puzzle, baseline)
        baseline_checked = verify(puzzle, baseline, budget)
        _require(baseline_checked["status"] in ("solved", "stalled"), "Production baseline did not complete")
    else:
        _require(inputs["baseline"] is None, "Line-only production has no paired baseline")
        certification.require_legacy(puzzle, proof)
    checked = verify(puzzle, proof, budget)
    if not checked["certified"] or checked["status"] != "solved":
        return None, _result(checked["status"], status="blocked", certified=False,
                             reason="Difficulty needs a complete independently verified production proof", exit_code=3)
    _require(proof["final_domains"] == [[[v] for v in row] for row in matrix], "Production proof does not establish the candidate matrix")
    return (design, matrix, logic), None


def _difficulty_bundle(path, method):
    path = io.external(path)
    directory = path if path.is_dir() else path.parent
    context = io.safe(directory, "catalog-context.json")
    marker = "catalog-context.json" if context.exists() else "report.json"
    _require(marker != "report.json" or method == "picross-difficulty-0.3",
             "Only a historical 0.3 bundle may omit its production-mode context")
    return _bundle(path, marker)


def _difficulty_budget(method, limits):
    if method == "picross-difficulty-0.3":
        from .analysis_contract import AnalysisBudget
    else:
        from .sd2_contract import AnalysisBudget
    return AnalysisBudget(**limits)


def _difficulty_result(candidate, bundle, checked, output, *, method, checked_slot=None):
    from . import catalog_rating
    formats = (("picross-checked-difficulty-v1", "picross-checked-difficulty-v2")
               if method == "picross-difficulty-0.3" else ("picross-checked-difficulty-v3",))
    _require(checked.get("format") in formats and catalog_rating.method(checked) == method,
             "Native checked bundle differs from the explicitly declared method")
    rating = checked["rating"]["result"]
    compact = checked["compact_analysis"]
    slot = checked_slot or _write(output, "checked-difficulty.json", checked)
    if checked_slot:
        _require(_read(checked_slot["path"]) == catalog_rating.encoded(checked), "Saved checked difficulty differs from fresh import")
    return _result(rating["status"], reason=rating["reason"], method=method,
                   slots={"candidate": _file(candidate), "analysis_bundle": _directory(bundle), "checked_difficulty": slot},
                   usage={"waves": compact["metrics"]["wave_count"] if method == "picross-difficulty-0.3" else compact["wave_count"]})


def _difficulty(stage, inputs, output, repo_root):
    from . import catalog_analysis, catalog_rating, certification
    from .sd2_contract import AnalysisBudget
    method = stage["parameters"]["method"]
    replay = stage["limits"]["revalidate"]
    if stage["operation"] == "import":
        candidate, bundle = inputs["candidate"], _difficulty_bundle(inputs["bundle"], method)
        checked = catalog_rating.import_bundle(candidate, bundle, budget=_difficulty_budget(method, replay))
        return _difficulty_result(candidate, bundle, checked, output, method=method)
    _active_method(repo_root, method)
    production, blocked = _production_proof(inputs, replay)
    if blocked is not None:
        return blocked
    design, matrix, logic = production
    p = stage["parameters"]
    _require(design["mode"] == p["production_mode"], "Difficulty production mode differs from original design")
    value = catalog_analysis.candidate(design, matrix, logic, p["puzzle_id"], p["runtime_revision"])
    candidate = Path(_write(output, "candidate.json", value)["path"])
    r4, baseline = inputs["r4_proof"], inputs["r4_baseline"]
    if (r4 is None) != (baseline is None):
        return _result("waiting_input", status="waiting_input", slots={"candidate": _file(candidate)},
                       reason="R4 analysis requires both explicitly bound runtime proof and baseline", exit_code=3)
    if r4 is not None:
        # These are independently supplied originals. Replacing ink/color IDs
        # inside a production proof would change the certificate and is forbidden.
        _, runtime, _, _ = catalog_rating.definition(_read(candidate), method=method)
        r4_value, baseline_value = _json(r4, runtime.proof_byte_limit), _json(baseline, runtime.proof_byte_limit)
        certification.require_legacy(runtime, baseline_value)
        _require(r4_value.get("format") == "picross-proof-v3" and
                 r4_value.get("logic_hash") == baseline_value.get("logic_hash") == runtime.logic_hash,
                 "R4 originals must bind the actual normalized runtime candidate")
    bundle = output / "analysis"
    checked = catalog_analysis.analyze_single(candidate, bundle, production_mode=p["production_mode"],
        budget=AnalysisBudget(**stage["limits"]["produce"]), verify_budget=AnalysisBudget(**replay),
        proof=r4, baseline=baseline, method=method)
    return _difficulty_result(candidate, bundle, checked, output, method=method)


def _difficulty_recheck(stage, inputs, saved, output, repo_root):
    from . import catalog_analysis, catalog_rating
    method = stage["parameters"]["method"]
    if stage["operation"] == "analyze":
        _active_method(repo_root, method)
        production, blocked = _production_proof(inputs, stage["limits"]["revalidate"])
        _require(blocked is None, "Production proof no longer qualifies for difficulty")
        p = stage["parameters"]
        expected = catalog_analysis.candidate(*production, p["puzzle_id"], p["runtime_revision"])
        candidate = Path(saved["slots"]["candidate"]["path"])
        _require(_json(candidate) == expected, "Saved runtime candidate differs from production inputs")
        bundle = _bundle(saved["slots"]["analysis_bundle"]["path"], "catalog-context.json")
        for field, name in (("r4_proof", "r4-proof.json"), ("r4_baseline", "r4-baseline.json")):
            copied = bundle / "rating/analysis" / name
            _require((inputs[field] is not None) == copied.is_file(), "R4 analysis source presence differs")
            if inputs[field] is not None:
                _require(_read(inputs[field], 64 * 1024 * 1024) == _read(copied, 64 * 1024 * 1024), "R4 analysis originals changed")
    else:
        candidate, bundle = inputs["candidate"], _difficulty_bundle(inputs["bundle"], method)
    checked = catalog_rating.import_bundle(candidate, bundle, budget=_difficulty_budget(method, stage["limits"]["revalidate"]))
    fresh = _difficulty_result(candidate, bundle, checked, output, method=method,
                               checked_slot=saved["slots"]["checked_difficulty"])
    _require(fresh["domain"] == saved["domain"], "Fresh difficulty status differs")
    return fresh


def _background(stage, inputs, output, source_root, decisions, *, existing=None):
    from . import background_assets, background_contract
    request = background_contract.validate_request(_json(inputs["request"]))
    if decisions and decisions.get("background") is not None:
        actual = io.external(decisions["background"])
        bound = io.safe(source_root, request["decision"]["file"])
        _require(actual == bound and _file(actual)["sha256"] == request["decision"]["sha256"]
                 and _file(actual)["bytes"] == request["decision"]["bytes"], "Background decision and original request differ")
    if existing is not None or stage["operation"] == "verify":
        directory = _bundle(existing if existing is not None else inputs["bundle"], "derivation.json")
        if existing is not None and stage["operation"] == "verify":
            _require(directory == _bundle(inputs["bundle"], "derivation.json"), "Saved background bundle differs from input")
        checked = background_assets.verify(request, source_root, directory)
    else:
        checked = background_assets.derive(request, source_root, output)
        directory = io.safe(output, request["output"])
    if checked["error"] is not None:
        error = checked["error"]
        status = "aborted" if checked["status"] in ("aborted", "interrupted") else "failed"
        return _result(checked["status"], status=status, reason=error["message"],
                       exit_code={"invalid_input": 2, "conflict": 2, "aborted": 4, "technical_error": 5}.get(checked["status"], 5))
    slots = {"background_finding": _file(directory / "derivation.json")}
    if checked["output"] is not None:
        slots["background_png"] = _file(directory / "background.png")
    report = _json(directory / "derivation.json")
    return _result(checked["status"], slots=slots, state=report["outcome"])


def _builder(stage, inputs, output, source_root, history_root):
    from . import authoring_builder as builder
    from .authoring_build_contract import validate_request
    request = validate_request(_json(inputs["request"]))
    _require(request["target"] == "local", "Batch builder supports only target=local")
    result = builder.build(request, source_root, output, publish_to=None, history_repo=history_root)
    _require(result["indexed"] is False, "Batch builder must not publish a repository index")
    directory = io.external(result["directory"])
    _require(directory.is_relative_to(output), "Builder output escapes its owned root")
    return _result(result["status"], state=request["handoff"]["state"], slots={
        "package": _file(directory / "package.zip"), "handoff": _file(directory / "handoff.json"),
        "record": _file(directory / "record.json"), "sheet_update": _write(output, "sheet-update.json", result["sheet"])})


def _builder_recheck(inputs, saved, source_root, history_root):
    from . import authoring_builder as builder
    from .authoring_build_contract import validate_request, BACKGROUND_FORMAT
    request = validate_request(_json(inputs["request"]))
    _require(request["target"] == "local", "Batch builder supports only target=local")
    _require(request["format"] == BACKGROUND_FORMAT or history_root is None, "History is supported only by build request v2")
    slots = saved["slots"]
    directory = Path(slots["package"]["path"]).parent
    _require(slots["package"]["path"] == str(directory / "package.zip")
             and slots["handoff"]["path"] == str(directory / "handoff.json")
             and slots["record"]["path"] == str(directory / "record.json"), "Builder original revision binding differs")
    with io.budget(ap.SECONDS):
        deadline = time.monotonic() + ap.SECONDS
        builder.verify_sources(source_root, request)
        original_hash = digest(request)
        entries = [{"path": f["path"], "bytes": f["bytes"], "sha256": f["sha256"]}
                   for f in sorted(request["files"], key=lambda f: f["path"])]
        h = request["handoff"]
        inventory = builder.json_data({"format": "picross-authoring-file-inventory-v1", "puzzle_id": h["puzzle_id"],
            "revision": h["revision"], "excludes": ["inventory.json", "handoff.json"], "files": entries})
        h["inventory"] = {"file": "inventory.json", "sha256": hashlib.sha256(inventory).hexdigest()}
        handoff = builder.json_data(h)
        _require(_read(directory / "handoff.json") == handoff, "Builder handoff differs from its unchanged request")
        expected = {e["path"]: {k: e[k] for k in ("bytes", "sha256")} for e in entries}
        expected.update({name: {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                         for name, raw in (("inventory.json", inventory), ("handoff.json", handoff))})
        verified = builder.verify_zip(directory / "package.zip", expected, handoff, request, deadline, history_repo=history_root)
        external = {name: directory / name for name in request["external"]}
        background = request["format"] == BACKGROUND_FORMAT
        inspected = builder.inspect_zip(directory / "package.zip", external, h["state"], deadline,
            **({"allow_background": True, "history_repo": history_root} if background else {}))
        bg = verified["background"]
        if background and inspected is not None:
            inspected, bg = inspected
        _require(not external or inspected is not None, "External authorizations require content_ready inspection")
        record = builder.record_for(request, h["puzzle_id"] + "/" + h["revision"],
                                    _read(directory / "package.zip", ap.MAX_ZIP), handoff, inspected, bg)
        record["build_request_sha256"] = original_hash
        _require(_read(directory / "record.json") == builder.json_data(record), "Saved builder record differs from fresh phase inspection")
        _require(_json(slots["sheet_update"]["path"]) == builder.sheet_from_record(record, bg), "Saved sheet projection differs")
        revision = {Path(slots[n]["path"]).name: {k: slots[n][k] for k in ("sha256", "bytes")}
                    for n in ("package", "handoff", "record")}
        revision.update({n: {k: f[k] for k in ("sha256", "bytes")} for n, f in request["external"].items()})
        builder.verify_revision(directory, revision)
        builder.verify_sources(source_root, request)
    return _result("reused", slots=slots, state=h["state"])


def _input_snapshot(stage, inputs, decisions):
    snapshot = {}
    for name, path in inputs.items():
        if path is None:
            snapshot["input:" + name] = None
        elif name in ("bundle", "reference"):
            snapshot["input:" + name] = _directory(path if path.is_dir() else path.parent)
        else:
            snapshot["input:" + name] = _file(path)
    for name in OPERATION_SPECS[stage["kind"], stage["operation"]]["required_decisions"]:
        if decisions and decisions.get(name) is not None:
            snapshot["decision:" + name] = _file(decisions[name])
    if stage["kind"] == "background" and decisions and decisions.get("background") is not None:
        snapshot["decision:background"] = _file(decisions["background"])
    return snapshot


def _operation_result(stage, result):
    validate_result(result)
    spec = OPERATION_SPECS[stage["kind"], stage["operation"]]
    for name in result["slots"]:
        base, _, variant = name.partition(":")
        _require(base in (spec["candidate_slots"] if variant else spec["slots"]), "Slot belongs to another operation")
        if variant:
            permitted = (stage["parameters"]["candidates"] if stage["kind"] == "image_import"
                         else [stage["parameters"]["candidate"]])
            _require(variant in permitted, "Slot was not explicitly selected")
    _checked_slots(result["slots"])
    return result


def _error_result(exc, kind):
    from .background_contract import BackgroundError
    if isinstance(exc, BackgroundError):
        return _result(exc.status, status="aborted" if exc.status == "aborted" else "failed", certified=False,
                       reason=exc.message, exit_code={"invalid_input": 2, "conflict": 2, "aborted": 4, "technical_error": 5}[exc.status])
    aborted = isinstance(exc, (Aborted, MemoryError, KeyboardInterrupt)) or getattr(exc, "aborted", False)
    if aborted:
        domain, status, code = "aborted", "aborted", 4
    elif isinstance(exc, InvalidProof):
        domain, status, code = "invalid_proof", "failed", 3
    elif isinstance(exc, (InvalidInput, ImportError)):
        domain, status, code = "invalid_input", "failed", 2
    else:
        domain, status, code = "technical_error", "failed", 5
    # These two existing command boundaries classify all non-abort input/IO/
    # proof failures as input errors. Preserve that corresponding CLI result.
    if kind in ("difficulty", "authoring_build") and not aborted:
        domain, code = "invalid_input", 2
    reason = str(exc).replace("\x00", "").strip()[:4096] or type(exc).__name__
    return _result(domain, status=status, certified=False, reason=reason, exit_code=code)


def execute_operation(stage, resolved_inputs, output_root, repo_root, source_root,
                      history_root=None, *, decisions=None):
    """Execute one allowed operation, producing only under the owned output root."""
    try:
        validate_operation(stage, repo_root)
        inputs = _input_paths(stage, resolved_inputs)
        gate = validate_decisions(stage, inputs, decisions, source_root)
        if gate is not None:
            return gate
        if "request" in inputs and inputs["request"] is None:
            return _result("waiting_input", status="waiting_input", reason="Missing complete original request", exit_code=3)
        before = _input_snapshot(stage, inputs, decisions)
        with _workspace(output_root, source_root) as output:
            kind, operation = stage["kind"], stage["operation"]
            if kind == "image_import":
                from .images import import_image, validate_design
                design = validate_design(_json(inputs["design"], 64 * 1024))
                variants = stage["parameters"]["candidates"]
                _require([v["id"] for v in design["variants"]] == variants,
                         "Declared candidates must exactly match the unchanged design's ordered variants")
                limits = stage["limits"]["produce"]
                bundle = output / "bundle"
                produced = import_image(inputs["image"], inputs["design"], bundle, limits["seconds"], limits["max_lines"],
                    profile=stage["parameters"]["profile"], max_pair_work=limits["max_pair_work"], max_pair_records=limits["max_pair_records"])
                result = _import_result(bundle, variants, stage["limits"]["revalidate"], output, domain=produced["status"])
                # The upstream producer does not report complete aggregate work
                # (palette and per-variant budgets are separate). Do not present
                # the last replay counters as total producer consumption.
                result["details"]["usage"] = {k: len(variants) if k == "candidates" else None for k in _USAGE}
            elif kind == "candidate_verify":
                bundle = _bundle(inputs["bundle"], "manifest.json")
                result = _import_result(bundle, [stage["parameters"]["candidate"]], stage["limits"]["revalidate"], output, domain=None)
            elif kind == "logic_certify":
                result = _solve(stage, inputs, output)
            elif kind == "repair":
                reference = _bundle(inputs["reference"], "manifest.json")
                if operation == "search":
                    from .repair import search
                    bundle = output / "repair"
                    native = search(reference, _json(inputs["plan"], 256 * 1024), bundle)
                else:
                    bundle = _bundle(inputs["bundle"], "manifest.json")
                    native = None
                result = _repair_result(bundle, reference, stage["limits"]["revalidate"], output)
                if native is not None:
                    result["details"]["usage"] = {k: native.get(k) if k in ("steps", "candidates") else None for k in _USAGE}
                    if native["status"] == "aborted":
                        result.update(status="aborted", exit_code=4)
            elif kind == "difficulty":
                result = _difficulty(stage, inputs, output, repo_root)
            elif kind == "background":
                result = _background(stage, inputs, output, source_root, decisions)
            elif kind == "authoring_build":
                result = _builder(stage, inputs, output, source_root, history_root)
            else:
                raise InvalidInput("Unsupported batch operation")
            _require(before == _input_snapshot(stage, inputs, decisions), "Original inputs changed during operation")
            _require(stage["tool_binding"] == expected_tool_binding(kind, operation, repo_root),
                     "Relevant operation tool or norm changed during execution")
            return _operation_result(stage, result)
    except (Exception, KeyboardInterrupt) as exc:
        return _error_result(exc, stage.get("kind") if isinstance(stage, dict) else None)


def _retain_original_slots(fresh, saved):
    _require(set(fresh["slots"]) == set(saved["slots"]), "Fresh operation output slots differ")
    for name, slot in fresh["slots"].items():
        old = saved["slots"][name]
        _require({k: v for k, v in slot.items() if k != "path"} == {k: v for k, v in old.items() if k != "path"},
                 "Original output differs from fresh operation projection: " + name)
    _require(fresh["certified"] == saved["certified"], "Fresh certification differs from saved result")
    fresh["slots"] = deepcopy(saved["slots"])
    return fresh


def revalidate_operation(stage, resolved_inputs, saved_result, output_root, repo_root,
                         source_root, history_root=None, *, decisions=None):
    """Freshly inspect actual original artifacts; retain their paths and bytes.

    New projection files, where needed for comparison, are private evidence of
    this attempt. They do not replace the original slots or invalidate consumers.
    """
    try:
        validate_operation(stage, repo_root)
        validate_result(saved_result)
        _checked_slots(saved_result["slots"])
        inputs = _input_paths(stage, resolved_inputs)
        gate = validate_decisions(stage, inputs, decisions, source_root)
        if gate is not None:
            return gate
        before = _input_snapshot(stage, inputs, decisions)
        with _workspace(output_root, source_root) as output:
            kind, operation = stage["kind"], stage["operation"]
            if kind in ("image_import", "candidate_verify"):
                bundle = _bundle(saved_result["slots"]["bundle"]["path"], "manifest.json")
                if kind == "image_import":
                    manifest = _json(bundle / "manifest.json")
                    _require(_json(inputs["design"], 64 * 1024) == _json(bundle / "design.json")
                             and _file(inputs["image"])["sha256"] == _file(bundle / manifest["original"])["sha256"],
                             "Original image/design and saved import differ")
                    variants = stage["parameters"]["candidates"]
                else:
                    _require(bundle == _bundle(inputs["bundle"], "manifest.json"), "Saved candidate bundle differs from input")
                    variants = [stage["parameters"]["candidate"]]
                result = _import_result(bundle, variants, stage["limits"]["revalidate"], output, domain=saved_result["domain"])
                _require(result["details"]["candidates"] == saved_result["details"]["candidates"], "Fresh candidate findings differ")
                result = _retain_original_slots(result, saved_result)
            elif kind == "logic_certify":
                result = _solve_recheck(stage, inputs, saved_result)
            elif kind == "repair":
                reference = _bundle(inputs["reference"], "manifest.json")
                bundle = _bundle(saved_result["slots"]["repair_bundle"]["path"], "manifest.json")
                if operation == "search":
                    _require(_json(inputs["plan"], 256 * 1024) == _json(bundle / "plan.json", 256 * 1024),
                             "Saved repair plan differs from current input")
                else:
                    _require(bundle == _bundle(inputs["bundle"], "manifest.json"), "Saved repair bundle differs from input")
                result = _retain_original_slots(_repair_result(bundle, reference, stage["limits"]["revalidate"], output), saved_result)
                _require(result["domain"] == saved_result["domain"], "Fresh repair finding differs")
                result.update(status=saved_result["status"], exit_code=saved_result["exit_code"])
            elif kind == "difficulty":
                result = _retain_original_slots(_difficulty_recheck(stage, inputs, saved_result, output, repo_root), saved_result)
            elif kind == "background":
                result = _background(stage, inputs, output, source_root, decisions,
                                     existing=saved_result["slots"]["background_finding"]["path"])
                if result["status"] == "completed":
                    result = _retain_original_slots(result, saved_result)
            elif kind == "authoring_build":
                result = _builder_recheck(inputs, saved_result, source_root, history_root)
            else:
                raise InvalidInput("Unsupported batch operation")
            _require(before == _input_snapshot(stage, inputs, decisions), "Original inputs changed during revalidation")
            _require(stage["tool_binding"] == expected_tool_binding(kind, operation, repo_root),
                     "Relevant operation tool or norm changed during revalidation")
            return _operation_result(stage, result)
    except (Exception, KeyboardInterrupt) as exc:
        return _error_result(exc, stage.get("kind") if isinstance(stage, dict) else None)
