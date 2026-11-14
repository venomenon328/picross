"""Explicit local PE-A3 raster view, plan, apply and recovery."""
import argparse
import json
from pathlib import Path

from . import editor_change as edit, editor_cli, content_registry
from .contract import Aborted


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("view","plan","apply","recover"):
        part = commands.add_parser(command)
        part.add_argument("--checkout",type=Path,required=True)
        if command == "view": part.add_argument("--id",required=True)
        if command == "plan":
            part.add_argument("--request",type=Path,required=True)
            part.add_argument("--output-dir",type=Path,required=True)
        if command == "apply": part.add_argument("--bundle",type=Path,required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "view": value = edit.detail(args.checkout,args.id)
        elif args.command == "plan":
            args.output_dir.mkdir(parents=True, exist_ok=False)
            value = editor_cli.plan_file(args.checkout,args.request,args.output_dir/"plan.json")
        elif args.command == "apply": value = edit.apply(args.checkout,editor_cli.read(args.bundle/"plan.json"))
        else: value = content_registry.recover(args.checkout)
        print(json.dumps(value,ensure_ascii=False,allow_nan=False))
        return 0
    except (Aborted,KeyboardInterrupt) as exc:
        print(json.dumps({"status":"aborted","error":str(exc)}))
        return 4
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"status":"error","error":str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
