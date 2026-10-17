"""Manually invoked SD analysis/report verification; no rating publication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis_contract import AnalysisBudget
from .analysis_io import analyze_file, check_bundle
from .contract import Aborted, InvalidInput, InvalidProof, load_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("analyze-difficulty", "check-analysis"):
        child = commands.add_parser(name)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--method", choices=("picross-difficulty-0.3",))
        child.add_argument("--seconds", type=float, default=120)
        child.add_argument("--max-lines", type=int, default=100000)
        child.add_argument("--max-rule-work", type=int, default=20000000)
        child.add_argument("--max-waves", type=int, default=80000)
        child.add_argument("--max-pair-work", type=int, default=20000000)
        child.add_argument("--max-pair-records", type=int, default=250000)
        if name == "analyze-difficulty":
            child.add_argument("--input-kind", choices=("logic", "runtime"), default="logic")
            child.add_argument("--output-dir", type=Path, required=True)
            child.add_argument("--parameters", type=Path)
            child.add_argument("--r4-proof", type=Path)
            child.add_argument("--r4-baseline", type=Path)
            child.add_argument("--verify-seconds", type=float, default=120)
            child.add_argument("--verify-max-lines", type=int, default=100000)
            child.add_argument("--verify-max-rule-work", type=int, default=20000000)
        else:
            child.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        budget = AnalysisBudget(args.seconds, args.max_lines, args.max_rule_work, args.max_waves,
                                max_pair_work=args.max_pair_work, max_pair_records=args.max_pair_records)
        if args.command == "check-analysis":
            result = check_bundle(args.input, args.bundle, budget, method=args.method)
            status = result["status"]
        else:
            verify_budget = AnalysisBudget(args.verify_seconds, args.verify_max_lines,
                args.verify_max_rule_work, max_pair_work=args.max_pair_work, max_pair_records=args.max_pair_records)
            report = analyze_file(args.input, args.output_dir, kind=args.input_kind,
                config=load_json(args.parameters, 4096) if args.parameters else None,
                budget=budget, verify_budget=verify_budget,
                proof_path=args.r4_proof, baseline_path=args.r4_baseline, method=args.method)
            status = report["result"]["status"]
            result = {"format": report["format"], "status": status,
                      "result_hash": report["result_hash"], "report": str(args.output_dir / "report.json"),
                      "line_analysis_complete": report["result"]["line_analysis_complete"],
                      "level": None, "explanation": report["result"]["explanation"]}
            if args.method is not None:
                from .difficulty_rating import RATING_BYTE_LIMIT
                rating = load_json(args.output_dir / "rating.json", RATING_BYTE_LIMIT)
                result.update(method=args.method, rating=str(args.output_dir / "rating.json"),
                              rating_hash=rating["rating_hash"], rating_status=rating["result"]["status"],
                              level=rating["result"]["level"], explanation=rating["result"]["explanation"])
        code = 4 if status == "aborted" else 0
    except Exception as exc:
        status = ("invalid_input" if isinstance(exc, InvalidInput) else
                  "invalid_analysis" if isinstance(exc, InvalidProof) else
                  "aborted" if isinstance(exc, (Aborted, MemoryError)) else "technical_error")
        code = {"invalid_input": 2, "invalid_analysis": 3, "aborted": 4, "technical_error": 5}[status]
        result = {"format": "picross-analysis-error-v1", "status": status,
                  "line_analysis_complete": False, "level": None,
                  "error": type(exc).__name__, "message": str(exc)}
    except KeyboardInterrupt:
        code = 4
        result = {"format": "picross-analysis-error-v1", "status": "aborted",
                  "line_analysis_complete": False, "level": None, "reason": "cancelled"}
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False))
    return code
