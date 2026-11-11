"""Closed serial integration CLI: no arbitrary commands, Git or recovery loop."""
from __future__ import annotations

import argparse
import json
import sys

from . import integration_batch_runner as runner
from .contract import Aborted, InvalidInput


def parser():
    root = argparse.ArgumentParser(description="Explicit authorized serial native integrations in one checkout")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "run", "resume"):
        command = commands.add_parser(name)
        command.add_argument("--plan", dest="plan_path", required=True)
        command.add_argument("--source-root", required=True)
        command.add_argument("--repo-root", required=True)
        command.add_argument("--target-root", required=True)
        command.add_argument("--work-root", required=name != "validate")
        command.add_argument("--history-root")
    commands.add_parser("status").add_argument("--work-root", required=True)
    return root


def main(argv=None):
    arguments = vars(parser().parse_args(argv))
    command = arguments.pop("command")
    try:
        result = getattr(runner, command)(**arguments)
        code = 0 if command == "validate" else runner.EXIT_CODES[(result["report"] if command == "status" else result)["status"]]
    except runner.BatchTechnicalError as exc:
        result, code = {"status": "technical_error", "error": str(exc)[:4096]}, 5
    except Aborted as exc:
        result, code = {"status": "aborted", "error": str(exc)[:4096]}, 4
    except (InvalidInput, ValueError, OSError) as exc:
        result, code = {"status": "invalid_input", "error": str(exc)[:4096]}, 2
    except Exception as exc:
        result, code = {"status": "technical_error", "error": type(exc).__name__ + ": " + str(exc)[:3900]}, 5
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
