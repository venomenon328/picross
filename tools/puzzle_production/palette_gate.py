"""Authoring 0.6.0 final palette boundary; no solver, cache or authorization.

Every caller supplies freshly reconstructed production inputs. Editorial
records remain statements by their recorded actors, never numeric test passes.
"""
from pathlib import Path

from . import palette_quality as quality
from .authoring_package import file_hash, require, string, timestamp
from .contract import Budget, InvalidInput, canonical_bytes, digest, exact_keys, load_json

EXPORT = "picross-target-export-v5"
EXCEPTION = "picross-palette-editorial-exception-v1"
EXCEPTION_FILE = "palette-exception.json"
VISUAL = "picross-palette-visual-review-v1"
CRITERIA = {"Q-R04", "Q-H01", "Q-H02"}


def early(matrix, design, identity=None, budget=None):
    """Diagnostic only: retain even empty/negative drafts, never skip solving.

    RP-5 and fixed edits lack an image candidate identity at this point. Their
    provisional fingerprint is explicitly distinct from the final ZA-1 binding.
    """
    budget = Budget() if budget is None else budget
    if identity is None:
        identity = {"id": digest({"matrix": matrix, "design": design}), "revision": 1,
                    "source_id": design["source_id"], "normalized_sha256": "0" * 64}
    try:
        report = quality.assess(matrix, design["palette"], identity, budget)
        quality.verify_assessment(report, matrix, design["palette"], identity, budget)
        return report
    except InvalidInput as exc:
        # An empty contour draft is a legitimate RP diagnostic, not a palette pass.
        return {"format": "picross-palette-error-v1", "status": "invalid_input", "message": str(exc)}


def same(actual, expected, message):
    require(canonical_bytes(actual) == canonical_bytes(expected), message)


def visual_review(package, matrix, logic, assessment):
    h = package.handoff
    ref = h.get("palette_review")
    if ref is None:
        return None, False
    exact_keys(ref, {"file", "sha256"})
    require(ref["file"] in package.entries, "Palette visual review must be inventoried")
    value = load_json(package.bound(ref), 128 * 1024)
    exact_keys(value, {"format", "puzzle_id", "revision", "matrix_hash", "logic_hash", "palette_sha256", "criteria"})
    same({k: value[k] for k in ("format", "puzzle_id", "revision", "matrix_hash", "logic_hash", "palette_sha256")},
         {"format": VISUAL, "puzzle_id": h["puzzle_id"], "revision": h["revision"],
          "matrix_hash": digest(matrix), "logic_hash": digest(logic), "palette_sha256": assessment["palette_sha256"]},
         "Stale palette visual review")
    exact_keys(value["criteria"], CRITERIA)
    allowed = True
    for judgment in value["criteria"].values():
        exact_keys(judgment, {"result", "accepted", "actor", "timestamp_utc", "statement", "reason", "evidence"})
        require(judgment["result"] in ("erfüllt", "Warnung", "nicht erfüllt", "nicht geprüft") and
                type(judgment["accepted"]) is bool, "Invalid palette visual judgment")
        for field in ("actor", "statement", "reason"):
            string(judgment[field], "visual " + field)
        timestamp(judgment["timestamp_utc"])
        require(isinstance(judgment["evidence"], list) and 1 <= len(judgment["evidence"]) <= 32,
                "Missing palette visual evidence")
        for evidence in judgment["evidence"]:
            exact_keys(evidence, {"file", "sha256"})
            require(evidence["file"] in package.entries, "Palette visual evidence must be inventoried")
            package.bound(evidence)
        allowed &= (judgment["result"] == "erfüllt" or
                    judgment["result"] in ("Warnung", "nicht erfüllt") and judgment["accepted"])
    return value, bool(allowed)


def exception_record(package, path, binding, assessment, approval):
    require(assessment["status"] == "negative" and approval is not None,
            "Palette exception requires negative pairs and actual final approval")
    target = quality._safe_path(Path(path))
    require(not target.is_relative_to(package.root.resolve()), "Palette exception must be outside sealed input")
    require(target.is_file() and target.stat().st_nlink == 1, "Palette exception must be a regular unaliased file")
    value = load_json(target, 128 * 1024)
    exact_keys(value, {"format", "binding", "negative_pairs", "actor", "timestamp_utc", "statement",
                       "reason", "approval_sha256", "test_only"})
    same(value["format"], EXCEPTION, "Unsupported palette exception")
    same(value["binding"], binding, "Stale palette exception binding")
    same(value["negative_pairs"], assessment["negative_pairs"], "Palette exception must bind every negative pair")
    same(value["approval_sha256"], approval["sha256"], "Palette exception final approval differs")
    same(value["test_only"], package.handoff.get("test_only", False), "Palette exception scope differs")
    for field in ("actor", "statement", "reason"):
        string(value[field], "palette exception " + field)
    timestamp(value["timestamp_utc"])
    return {"record": value, "sha256": file_hash(target)}


def inspect(package, design, matrix, logic, source, reference, approval, exception_path, budget):
    """Fresh final producer AND independent assessment reader on real inputs."""
    h = package.handoff
    identity = {"id": source.get("candidate_id", digest(source)), "revision": 1,
                "source_id": design["source_id"],
                "normalized_sha256": file_hash(reference / "normalized.png")}
    assessment = quality.assess(matrix, design["palette"], identity, budget)
    quality.verify_assessment(assessment, matrix, design["palette"], identity, budget)
    if h.get("palette_assessment") is not None:
        exact_keys(h["palette_assessment"], {"file", "sha256"})
        quality.verify_assessment(package.json(h["palette_assessment"]["file"]), matrix,
                                  design["palette"], identity, budget)
        package.bound(h["palette_assessment"])
    binding = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
               "candidate": {k: h["candidate"][k] for k in ("bundle", "variant", "source_type")},
               "source": source, "matrix_hash": digest(matrix), "logic_hash": digest(logic),
               "palette_sha256": assessment["palette_sha256"], "source_fingerprint": assessment["source_fingerprint"],
               "rulebook": {k: h["rulebook"][k] for k in ("version", "file", "sha256")},
               "handoff_sha256": file_hash(package.file("handoff.json")),
               "inventory_sha256": h["inventory"]["sha256"],
               "original_zip_sha256": (package.derivation or {}).get("original_zip_sha256")
                                      if package.derivation else package.archive_sha256}
    review, visually_allowed = (visual_review(package, matrix, logic, assessment) if design["mode"] == "color"
                                else (None, True))
    exception = (exception_record(package, exception_path, binding, assessment, approval)
                 if exception_path is not None else None)
    budget.check()
    return {"assessment": assessment, "binding": binding, "visual_review": review, "exception": exception,
            "allowed": bool(visually_allowed and (assessment["status"] == "positive" or exception is not None))}
