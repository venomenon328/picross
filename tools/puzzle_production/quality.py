"""Report diagnosis, proven deduction and technique necessity on separate axes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contract import (Aborted, Budget, InvalidInput, InvalidProof, LOGIC_BYTE_LIMIT,
                       load_json, validate_logic, write_json)
from .certification import LABEL, file_sha, require_legacy
from .verifier import verify


def assess(input_path, proof_path, *, baseline_path=None, diagnosis_dir=None, budget=None):
    budget = budget if budget is not None else Budget()
    puzzle = validate_logic(load_json(input_path, LOGIC_BYTE_LIMIT))
    proof = load_json(proof_path, puzzle.proof_byte_limit)
    checked = verify(puzzle, proof, budget)
    paired = proof["format"] == "picross-proof-v3"
    baseline = None
    evidence = {"input_sha256": file_sha(input_path), "proof_sha256": file_sha(proof_path)}
    if baseline_path is not None:
        raw = load_json(baseline_path, puzzle.proof_byte_limit)
        require_legacy(puzzle, raw)
        baseline = verify(puzzle, raw, budget)
        evidence["baseline_sha256"] = file_sha(baseline_path)
    diagnosis = None
    if diagnosis_dir is not None:
        from .diagnosis import check_diagnosis
        diagnosis = check_diagnosis(input_path, diagnosis_dir, budget)
        evidence["diagnosis_sha256"] = file_sha(diagnosis_dir / "diagnosis.json")
    needed = bool(paired and checked["certified"] and baseline and baseline["status"] == "stalled")
    if checked["certified"]:
        if diagnosis and diagnosis["confirmed_status"] == "multiple":
            raise InvalidInput("Contradictory complete deduction and multiple-solution evidence")
        classification = ("paired_lines_solved" if needed else "line_logic_solved"
                          if not paired or baseline and baseline["certified"] else
                          "complete_deduction_necessity_unproven")
    elif diagnosis and diagnosis["confirmed_status"] == "multiple":
        classification = "multiple"
    elif diagnosis and diagnosis["reported_status"] == "unique":
        classification = "reported_unique_without_complete_deduction"
    elif diagnosis and diagnosis["reported_status"] == "unknown":
        classification = "diagnosis_incomplete"
    else:
        classification = "no_complete_deduction"
    budget.check()
    return {"format": "picross-quality-report-v1", "logic_hash": puzzle.logic_hash,
            "classification": classification, "diagnosis": diagnosis,
            "deduction": checked, "baseline": baseline, "evidence": evidence,
            "difficulty": {"method": "picross-difficulty-0.2", "r4_required": needed,
                "level": "L5" if needed else None, "logical_demand": LABEL if needed else None,
                "confidence": "medium" if needed else None, "r0_r3_analysis": "not_performed"},
            "workload": {"width": puzzle.width, "height": puzzle.height, "cells": puzzle.width * puzzle.height},
            "estimated_minutes": None, "editorial_approved": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("assess",))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--diagnosis", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--seconds", type=float, default=120)
    parser.add_argument("--max-lines", type=int, default=100000)
    parser.add_argument("--max-pair-work", type=int, default=20000000)
    parser.add_argument("--max-pair-records", type=int, default=250000)
    args = parser.parse_args(argv)
    from .diagnosis_verifier import InvalidDiagnosis
    try:
        if args.report and (args.report.exists() or args.report.resolve() in
                            {p.resolve() for p in (args.input, args.proof, args.baseline) if p}):
            raise InvalidInput("Assessment report requires a new separate path")
        result = assess(args.input, args.proof, baseline_path=args.baseline, diagnosis_dir=args.diagnosis,
                        budget=Budget(args.seconds, args.max_lines, max_pair_work=args.max_pair_work,
                                      max_pair_records=args.max_pair_records))
        if args.report:
            write_json(args.report, result)
        code = 0
    except (InvalidInput, InvalidProof, InvalidDiagnosis, Aborted, OSError, MemoryError, KeyboardInterrupt) as exc:
        code = 4 if isinstance(exc, (Aborted, MemoryError, KeyboardInterrupt)) else 3 if isinstance(exc, (InvalidProof, InvalidDiagnosis)) else 2
        result = {"format": "picross-quality-error-v1", "certified": False, "error": type(exc).__name__, "message": str(exc)}
    print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    return code
