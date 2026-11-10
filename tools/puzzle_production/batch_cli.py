"""Closed local BA-A CLI: validate, run, resume, and historical status."""
from __future__ import annotations

import argparse
import json
import sys

from . import batch_runner
from .contract import Aborted, InvalidInput


def parser():
    root = argparse.ArgumentParser(description="Explicit local serial production batches; no catalog writer")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "run", "resume"):
        command = commands.add_parser(name)
        command.add_argument("--plan", dest="plan_path", required=True)
        command.add_argument("--source-root", required=True)
        command.add_argument("--repo-root", required=True)
        command.add_argument("--work-root", required=name != "validate")
        command.add_argument("--history-root")
    commands.add_parser("status").add_argument("--work-root", required=True)
    return root


def main(argv=None):
    arguments = vars(parser().parse_args(argv))
    command = arguments.pop("command")
    try:
        result = getattr(batch_runner, command)(**arguments)
        if command == "validate":
            code = 0
        elif command == "status":
            code = batch_runner.EXIT_CODES[result["report"]["status"]]
        else:
            code = batch_runner.EXIT_CODES[result["status"]]
    except batch_runner.BatchTechnicalError as exc:
        result, code = {"status": "technical_error", "error": str(exc)[:4096]}, 5
    except (Aborted, InvalidInput, ValueError, OSError) as exc:
        result, code = {"status": "invalid_input", "error": str(exc)[:4096]}, 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
