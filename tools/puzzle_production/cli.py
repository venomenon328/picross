"""Headless JSON CLI. Certification is issued only after independent replay."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

from .contract import (Aborted, Budget, InvalidInput, InvalidProof, LOGIC_BYTE_LIMIT,
                       digest, load_json, validate_logic, write_json)
from .solver import solve
from .verifier import verify


EXIT = {"solved": 0, "stalled": 0, "contradiction": 0, "invalid_input": 2,
        "invalid_proof": 3, "aborted": 4, "technical_error": 5}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("solve", "verify"):
        child = sub.add_parser(command)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--seconds", type=float, default=120)
        child.add_argument("--max-lines", type=int, default=100_000)
        if command == "solve":
            child.add_argument("--output-dir", type=Path, required=True)
            child.add_argument("--order", choices=("rows-first", "columns-first", "reverse"),
                               default="rows-first")
        else:
            child.add_argument("--proof", type=Path, required=True)
            child.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report_path = (args.output_dir / "result.json" if args.command == "solve"
                   else args.report)
    started = time.perf_counter()
    timings = {}
    try:
        if sys.version_info < (3, 11):
            raise InvalidInput("Python 3.11 or newer is required")
        budget = Budget(args.seconds, args.max_lines)
        puzzle = validate_logic(load_json(args.input, max_bytes=LOGIC_BYTE_LIMIT))
        if args.command == "verify" and report_path:
            if (report_path.exists() or report_path.resolve() in
                    (args.input.resolve(), args.proof.resolve())):
                raise InvalidInput("Verification report must be a new, separate file")
        if args.command == "solve":
            # Refuse stale certificates and accidental input overwrites on reruns.
            if any((args.output_dir / name).exists()
                   for name in ("proof.json", "result.json")):
                raise InvalidInput("Output directory already has puzzle output; use a new directory")
            at = time.perf_counter()
            proof = solve(puzzle, budget, args.order)
            timings["solve_seconds"] = time.perf_counter() - at
            solver_lines = budget.lines
            at = time.perf_counter()
            proof_path = args.output_dir / "proof.json"
            write_json(proof_path, proof)
            timings["serialization_seconds"] = time.perf_counter() - at
            if proof["status"] == "aborted":
                result = {"status": "aborted", "certified": False,
                          "proof_verified": False, "reason": proof["reason"],
                          "logic_hash": puzzle.logic_hash, "profile": puzzle.profile,
                          "profile_hash": digest(puzzle.profile)}
            else:
                at = time.perf_counter()
                result = verify(puzzle, load_json(proof_path, puzzle.proof_byte_limit), budget)
                timings["verification_seconds"] = time.perf_counter() - at
            result["solver_line_evaluations"] = solver_lines
        else:
            try:
                proof = load_json(args.proof, puzzle.proof_byte_limit)
            except InvalidInput as exc:
                raise InvalidProof(str(exc)) from exc
            at = time.perf_counter()
            result = verify(puzzle, proof, budget)
            timings["verification_seconds"] = time.perf_counter() - at
        result.update({"format": "picross-result-v1", "timings": timings})
        result["timings"]["total_seconds"] = time.perf_counter() - started
        if report_path:
            write_json(report_path, result)
    except (InvalidInput, InvalidProof, Aborted, MemoryError, OSError,
            RuntimeError, ValueError, TypeError, KeyboardInterrupt) as exc:
        if isinstance(exc, InvalidInput):
            status = "invalid_input"
        elif isinstance(exc, InvalidProof):
            status = "invalid_proof"
        elif isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError)):
            status = "aborted"
        else:
            status = "technical_error"
        result = {"format": "picross-result-v1", "status": status,
                  "certified": False, "proof_verified": False,
                  "error": type(exc).__name__, "message": str(exc)}
        # Do not overwrite existing outputs (including possibly the input itself).
        if report_path and not report_path.exists():
            try:
                write_json(report_path, result)
            except OSError:
                pass
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return EXIT[result["status"]]
