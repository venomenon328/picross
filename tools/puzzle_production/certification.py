"""Versioned file-bound paired certification and R4 necessity, outside the game."""
from __future__ import annotations

import hashlib

from .contract import (Aborted, Budget, InvalidInput, PAIRED_IDS, digest, exact_keys,
                       integer, load_json, selected_profile, write_json)
from .verifier import verify

ASSESSMENT_LIMIT = 64 * 1024
LABEL = "linienübergreifend / besonders hoher logischer Anspruch"


def configuration(puzzle, profile, max_pair_work=20_000_000, max_pair_records=250_000):
    chosen = selected_profile(puzzle, profile)
    if chosen == puzzle.profile:
        return None
    return validate_config({"profile": chosen["id"], "max_pair_work": max_pair_work,
                            "max_pair_records": max_pair_records}, puzzle)


def validate_config(raw, puzzle=None):
    c = exact_keys(raw, {"profile", "max_pair_work", "max_pair_records"})
    if c["profile"] not in PAIRED_IDS:
        raise InvalidInput("Certification requires an explicit paired profile")
    integer(c["max_pair_work"], 0, 100_000_000, "max_pair_work")
    integer(c["max_pair_records"], 0, 1_000_000, "max_pair_records")
    if puzzle is not None:
        selected_profile(puzzle, c["profile"])
    return dict(c)


def bounded_budget(seconds, max_lines, config, cancelled=None):
    c = validate_config(config)
    return Budget(seconds, max_lines, cancelled, max_pair_work=c["max_pair_work"],
                  max_pair_records=c["max_pair_records"])


def file_sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def names(prefix):
    return {kind: f"{prefix}{kind}.json" for kind in ("proof", "baseline-proof", "assessment")}


def assessment(puzzle, proof, baseline, proof_sha, baseline_sha, verified, baseline_verified):
    needed = bool(verified and baseline_verified and proof["status"] == "solved" and baseline["status"] == "stalled")
    outcome = ("paired_lines_solved" if needed else "line_logic_solved"
               if verified and baseline_verified and proof["status"] == baseline["status"] == "solved"
               else "complete_deduction_without_necessity" if verified and proof["status"] == "solved"
               else "no_complete_deduction")
    return {"format": "picross-deduction-assessment-v1", "method": "picross-difficulty-0.2",
            "logic_hash": puzzle.logic_hash, "profile_hash": proof["profile_hash"],
            "proof_sha256": proof_sha, "baseline_sha256": baseline_sha,
            "proof_status": proof["status"], "proof_verified": verified,
            "baseline_status": baseline["status"], "baseline_verified": baseline_verified,
            "outcome": outcome, "r4_required": needed, "level": "L5" if needed else None,
            "label": LABEL if needed else None, "confidence": "medium" if needed else None,
            "instrumentation": "R4 necessity only; R0-R3 not classified; no human calibration",
            "diagnosis": "not_run", "estimated_minutes": None}


def produce(puzzle, directory, prefix, config, solver_budget, verifier_budget=None):
    """Write both unknown-start proofs; necessity is derived only after file replay."""
    from .solver import solve  # Reading/rechecking certificates never imports a solver.
    c = validate_config(config, puzzle)
    verifier_budget = solver_budget if verifier_budget is None else verifier_budget
    for budget in (solver_budget, verifier_budget):
        budget.max_pair_work = min(budget.max_pair_work, c["max_pair_work"])
        budget.max_pair_records = min(budget.max_pair_records, c["max_pair_records"])
    paths = {k: directory / v for k, v in names(prefix).items()}
    baseline = solve(puzzle, solver_budget)
    write_json(paths["baseline-proof"], baseline)
    baseline_verified = False
    try:
        verify(puzzle, load_json(paths["baseline-proof"], puzzle.proof_byte_limit), verifier_budget)
        baseline_verified = True
    except Aborted:
        pass
    proof = solve(puzzle, solver_budget, profile=c["profile"])
    write_json(paths["proof"], proof)
    try:
        checked = verify(puzzle, load_json(paths["proof"], puzzle.proof_byte_limit), verifier_budget)
    except Aborted as exc:
        checked = {"status": "aborted", "certified": False, "proof_verified": False, "reason": str(exc),
                   "logic_hash": puzzle.logic_hash, "profile": proof["profile"], "profile_hash": proof["profile_hash"]}
    report = assessment(puzzle, proof, baseline, file_sha(paths["proof"]), file_sha(paths["baseline-proof"]),
                        checked["proof_verified"], baseline_verified)
    write_json(paths["assessment"], report)
    checked["assessment"] = report
    return proof, checked


def inspect(puzzle, directory, prefix, config, budget=None):
    c = validate_config(config, puzzle)
    budget = bounded_budget(120, 100_000, c) if budget is None else budget
    # A surrounding replay may be tighter. Never reset its consumed counters.
    budget.max_pair_work = min(budget.max_pair_work, c["max_pair_work"])
    budget.max_pair_records = min(budget.max_pair_records, c["max_pair_records"])
    paths = {k: directory / v for k, v in names(prefix).items()}
    proof = load_json(paths["proof"], puzzle.proof_byte_limit)
    baseline = load_json(paths["baseline-proof"], puzzle.proof_byte_limit)
    if (proof.get("format") != "picross-proof-v3" or proof.get("profile") != selected_profile(puzzle, c["profile"]) or
            baseline.get("format") != puzzle.proof_format or baseline.get("profile") != puzzle.profile):
        raise InvalidInput("Production proof/profile or independent baseline mismatch")
    baseline_checked = verify(puzzle, baseline, budget)
    checked = verify(puzzle, proof, budget)
    recorded = load_json(paths["assessment"], ASSESSMENT_LIMIT)
    if not isinstance(recorded, dict) or any(type(recorded.get(k)) is not bool for k in ("proof_verified", "baseline_verified")):
        raise InvalidInput("Invalid assessment verification flags")
    expected = assessment(puzzle, proof, baseline, file_sha(paths["proof"]), file_sha(paths["baseline-proof"]),
                          recorded["proof_verified"] and checked["proof_verified"],
                          recorded["baseline_verified"] and baseline_checked["proof_verified"])
    if digest(recorded) != digest(expected):
        raise InvalidInput("Assessment differs from independent necessity evidence")
    if not recorded["proof_verified"]:
        checked.update(status="aborted", certified=False, proof_verified=False)
    checked["assessment"] = expected
    checked["certification"] = c
    checked["line_evaluations"] += baseline_checked["line_evaluations"]
    return proof, checked


def require_legacy(puzzle, proof):
    if proof.get("format") != puzzle.proof_format or proof.get("profile") != puzzle.profile:
        raise InvalidInput("Legacy production contract cannot authorize a paired proof")
