"""Standalone, inactive SD2-B rating. Reads only explicitly supplied single inputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contract import Aborted, InvalidInput, InvalidProof
from .sd2_contract import AnalysisBudget
from .sd2_rating_io import analyze_and_rate, rate_bundle, check_rating_bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("analyze", "rate", "check"):
        child = commands.add_parser(name)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--seconds", type=float, default=120)
        child.add_argument("--max-lines", type=int, default=100000)
        child.add_argument("--max-rule-work", type=int, default=20000000)
        child.add_argument("--max-waves", type=int, default=80000)
        child.add_argument("--max-pair-work", type=int, default=20000000)
        child.add_argument("--max-pair-records", type=int, default=250000)
        if name == "check":
            child.add_argument("--bundle", type=Path, required=True)
        else:
            child.add_argument("--output-dir", type=Path, required=True)
        if name == "rate":
            child.add_argument("--analysis-bundle", type=Path, required=True)
        if name == "analyze":
            child.add_argument("--input-kind", choices=("logic", "runtime"), default="logic")
            child.add_argument("--r4-proof", type=Path)
            child.add_argument("--r4-baseline", type=Path)
            child.add_argument("--verify-seconds", type=float, default=120)
            child.add_argument("--verify-max-lines", type=int, default=100000)
            child.add_argument("--verify-max-rule-work", type=int, default=20000000)
    args = parser.parse_args(argv)
    try:
        budget = AnalysisBudget(args.seconds, args.max_lines, args.max_rule_work, args.max_waves,
                                max_pair_work=args.max_pair_work, max_pair_records=args.max_pair_records)
        if args.command == "check":
            report = check_rating_bundle(args.input, args.bundle, budget)
        elif args.command == "rate":
            report = rate_bundle(args.input, args.analysis_bundle, args.output_dir, budget)
        else:
            verify_budget = AnalysisBudget(args.verify_seconds, args.verify_max_lines,
                args.verify_max_rule_work, args.max_waves,
                max_pair_work=args.max_pair_work, max_pair_records=args.max_pair_records)
            report = analyze_and_rate(args.input, args.output_dir, kind=args.input_kind,
                budget=budget, verify_budget=verify_budget,
                proof_path=args.r4_proof, baseline_path=args.r4_baseline)
        result = report["result"]
        result = {**result, "format": "picross-sd2-rating-cli-v1", "command": args.command,
                  "result_hash": report["result_hash"],
                  "level": None if result["assessment"] is None else result["assessment"]["level"]}
        code = 4 if result["reason"] in ("analysis_aborted", "time_limit", "work_limit", "rule_work_limit",
                  "wave_limit", "trace_byte_limit", "cancelled", "memory_limit") else 0
    except Exception as exc:
        status = ("invalid_input" if isinstance(exc, InvalidInput) else
                  "invalid_analysis" if isinstance(exc, InvalidProof) else
                  "aborted" if isinstance(exc, (Aborted, MemoryError)) else "technical_error")
        code = {"invalid_input": 2, "invalid_analysis": 3, "aborted": 4, "technical_error": 5}[status]
        result = {"format": "picross-sd2-rating-error-v1", "status": status, "level": None,
                  "error": type(exc).__name__, "message": str(exc)}
    except KeyboardInterrupt:
        code = 4
        result = {"format": "picross-sd2-rating-error-v1", "status": "aborted", "level": None, "reason": "cancelled"}
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
