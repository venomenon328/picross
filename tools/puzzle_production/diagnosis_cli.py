"""CLI for separate uniqueness diagnosis and independent witness checking."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contract import Aborted, Budget, InvalidInput
from .diagnosis import DiagnosisBudget, check_diagnosis, diagnose_file
from .diagnosis_verifier import InvalidDiagnosis


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("diagnose", "check-diagnosis"):
        child = sub.add_parser(name)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--seconds", type=float, default=120)
        child.add_argument("--max-lines", type=int, default=100_000)
        if name == "diagnose":
            child.add_argument("--output-dir", type=Path, required=True)
            child.add_argument("--max-nodes", type=int, default=100_000)
        else:
            child.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "diagnose":
            result = diagnose_file(args.input, args.output_dir,
                                   DiagnosisBudget(args.seconds, args.max_lines, args.max_nodes))
        else:
            result = check_diagnosis(args.input, args.bundle, Budget(args.seconds, args.max_lines))
        code = 4 if result.get("status") == "unknown" else 0
    except (InvalidInput, InvalidDiagnosis, Aborted, MemoryError, KeyboardInterrupt,
            OSError, RuntimeError, ValueError, TypeError) as exc:
        if isinstance(exc, InvalidInput):
            status, code = "invalid_input", 2
        elif isinstance(exc, InvalidDiagnosis):
            status, code = "invalid_diagnosis", 3
        elif isinstance(exc, (Aborted, MemoryError, KeyboardInterrupt)):
            status, code = "unknown", 4
        else:
            status, code = "technical_error", 5
        result = {"format": "picross-uniqueness-error-v1", "status": status,
                  "certified": False, "error": type(exc).__name__, "message": str(exc)}
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return code
