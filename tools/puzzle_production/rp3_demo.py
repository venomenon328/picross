"""Reproduce file import/export and validate all shipped P1 bindings in CI."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from .contract import InvalidInput, load_json, write_json


def demonstrate(root: Path, output: Path) -> dict:
    # Lazy image dependency: importing the product harness still needs only stdlib.
    from .images import file_hash, import_image, inspect_candidate
    from .p1_export import export_p1
    source = root / "examples/rp3"
    import_image(source / "source.png", source / "design.json", output / "production")
    shipped, _, shipped_check = inspect_candidate(source / "production", "area-128")
    regenerated, _, check = inspect_candidate(output / "production", "area-128")
    semantic_fields = ("matrix", "logic_hash", "design", "variant", "source_id")
    if (any(shipped[k] != regenerated[k] for k in semantic_fields) or
            not shipped_check["certified"] or not check["certified"]):
        raise InvalidInput("Real imported candidate differs from shipped certified candidate")
    export_p1(output / "production", "area-128", source / "reveal.svg", "Fliegenpilz", output / "p1-export")
    export_p1(source / "production", "area-128", source / "reveal.svg", "Fliegenpilz", output / "shipped-p1-export")
    for relative in ("data/f04.json", "art/f04.svg"):
        if (file_hash(output / "p1-export" / relative) != file_hash(root / "prototypes/p1" / relative) or
                file_hash(output / "p1-export" / relative) != file_hash(source / "p1-export" / relative)):
            raise InvalidInput("Registered P1 content differs from newly imported/proven export")
    committed_export = load_json(source / "p1-export/manifest.json")
    for relative, sha in committed_export["files"].items():
        path = source / "p1-export" / relative
        if path.resolve().parent not in ((source / "p1-export").resolve(), (source / "p1-export/data").resolve(), (source / "p1-export/art").resolve()) or file_hash(path) != sha:
            raise InvalidInput("Altered or unsafe committed P1 export")
    for key in ("candidate_id", "logic_hash", "revision", "color_mapping", "technical"):
        if committed_export[key] != load_json(output / "shipped-p1-export/manifest.json")[key]:
            raise InvalidInput(f"Committed export {key} differs from fresh verification")
    checkout = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    base = os.environ.get("RP1_BASE_COMMIT") or subprocess.check_output(
        ["git", "merge-base", "HEAD", "origin/main"], cwd=root, text=True).strip()
    report = {"format": "picross-rp3-demonstration-v1", "accepted": True,
              "source_commit": os.environ.get("RP1_SOURCE_HEAD") or os.environ.get("P1_PREFLIGHT_SOURCE_COMMIT") or checkout,
              "tested_checkout_commit": checkout, "base_commit": base,
              "source_tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()),
              "github_run_id": os.environ.get("GITHUB_RUN_ID"), "candidate_id": shipped["id"], "technical": check,
              "regenerated_candidate_id": regenerated["id"], "producer_versions": shipped["versions"],
              "current_versions": regenerated["versions"], "cross_build_pixel_and_raster_verified": True,
              "registered_files": {p: file_hash(root / "prototypes/p1" / p) for p in ("data/f04.json", "art/f04.svg")},
              "source_files": {p.name: file_hash(p) for p in sorted(source.iterdir()) if p.is_file()},
              "production_manifest_sha256": file_hash(output / "production/manifest.json"),
              "export_manifest_sha256": file_hash(output / "p1-export/manifest.json"),
              "motif_review": "separate visual inspection; not general motif acceptance", "owner_solution": "not performed; RP-6 gate"}
    write_json(output / "rp3-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = demonstrate(Path(__file__).resolve().parents[2], args.output_dir)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"accepted": False, "message": str(exc)}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
