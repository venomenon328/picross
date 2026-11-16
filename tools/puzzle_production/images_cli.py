"""Explicit local PE-A2 image plans, publication and shared recovery."""
import argparse
import json
import sys

from . import catalog_images as images, editor_change as edit, editor_cli
from .contract import Aborted, InvalidInput


def parser():
    result = argparse.ArgumentParser(description="Maintain prepared images of existing puzzles")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("view", "plan", "apply", "recover"):
        command = commands.add_parser(name)
        command.add_argument("--target-root", required=True)
        if name == "view": command.add_argument("--id", required=True)
        if name == "plan": command.add_argument("--request", required=True)
        if name == "plan": command.add_argument("--output", required=True)
        if name == "apply": command.add_argument("--plan", required=True)
        if name in ("plan", "apply"): command.add_argument("--seconds", type=float, default=300)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "view": result = edit.detail(args.target_root, args.id)
        elif args.command == "plan": result = editor_cli.plan_file(args.target_root, args.request, args.output)
        elif args.command == "apply":
            value = editor_cli.read(args.plan)
            result = edit.apply(args.target_root, value)
        else: result = images.recover(args.target_root)
        code = 0
    except Aborted as exc:
        result, code = {"status": "aborted", "error": str(exc)}, 4
    except (InvalidInput, ValueError, OSError, TypeError, KeyError) as exc:
        result, code = {"status": "invalid_input", "error": str(exc)}, 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
