"""Lazy RP-3 CLI; failures never grant export or overwrite earlier bundles."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contract import Aborted, InvalidInput, InvalidProof


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    image = sub.add_parser("import-image")
    image.add_argument("--input", type=Path, required=True)
    image.add_argument("--design", type=Path, required=True)
    export = sub.add_parser("export-p1")
    export.add_argument("--bundle", type=Path, required=True)
    export.add_argument("--variant", required=True)
    export.add_argument("--reveal", type=Path, required=True)
    export.add_argument("--name", required=True)
    export.add_argument("--revision", type=int, default=1)
    for p in (image, export):
        p.add_argument("--output-dir", type=Path, required=True)
        p.add_argument("--seconds", type=float, default=120)
        p.add_argument("--max-lines", type=int, default=100_000)
    args = parser.parse_args(argv)
    try:
        from .images import import_image
        from .p1_export import export_p1
        if args.command == "import-image":
            result = import_image(args.input, args.design, args.output_dir, args.seconds, args.max_lines)
        else:
            result = export_p1(args.bundle, args.variant, args.reveal, args.name, args.output_dir,
                               args.revision, args.seconds, args.max_lines)
        code = 0
    except (InvalidInput, InvalidProof, Aborted, MemoryError, KeyboardInterrupt,
            ImportError, OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        if isinstance(exc, (Aborted, MemoryError, KeyboardInterrupt)):
            status, code = "aborted", 4
        elif isinstance(exc, InvalidProof):
            status, code = "invalid_proof", 3
        elif isinstance(exc, (InvalidInput, ImportError)):
            status, code = "invalid_input", 2
        else:
            status, code = "technical_error", 5
        result = {"status": status, "certified": False, "error": type(exc).__name__, "message": str(exc)}
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False))
    return code
