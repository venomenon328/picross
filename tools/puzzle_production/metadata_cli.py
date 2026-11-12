"""Local PE-A1 metadata CLI. Plans are explicit inputs to the shared writer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import catalog_io as io, catalog_metadata as metadata, operation_diagnostics as diagnostic
from .contract import Aborted, InvalidInput


def parser():
    root = argparse.ArgumentParser(description="Read and explicitly edit existing puzzle metadata and categories")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("view", "plan", "plan-migration", "apply", "recover"):
        command = commands.add_parser(name)
        command.add_argument("--target-root", required=True)
        if name == "plan":
            command.add_argument("--operations", required=True, help="JSON array of explicit metadata/category operations")
        if name == "apply":
            command.add_argument("--plan", required=True, help="Previously reviewed metadata plan JSON")
        if name in ("view", "plan", "plan-migration"):
            command.add_argument("--output", help="New UTF-8 JSON file outside the target checkout; otherwise stdout")
    return root


def _input(name):
    path = io.external(Path(name))
    return io.json_bytes(io.read(path.parent, path.name, metadata.PLAN_LIMIT), metadata.PLAN_LIMIT)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        output = diagnostic.report_target(args.output, [args.target_root, getattr(args, "operations", None)]) if getattr(args, "output", None) else None
        if args.command == "view":
            result = metadata.view(args.target_root)
        elif args.command == "plan":
            result = metadata.plan(args.target_root, _input(args.operations))
        elif args.command == "plan-migration":
            result = metadata.plan_migration(args.target_root)
        elif args.command == "apply":
            result = metadata.apply(args.target_root, _input(args.plan))
        else:
            result = metadata.recover(args.target_root)
        if output is not None:
            diagnostic.write_report(output, result)
            result = {"status": "written", "output": str(output)}
        code = 0
    except Aborted as exc:
        result, code = {"status": "aborted", "error": str(exc)}, 4
    except (InvalidInput, ValueError, OSError, TypeError, KeyError) as exc:
        result, code = {"status": "invalid_input", "error": str(exc)}, 2
    # ASCII stdout also works with legacy Windows redirection; --output always
    # writes canonical UTF-8/LF bytes independently of the console code page.
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
