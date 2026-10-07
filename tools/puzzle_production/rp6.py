"""Fixed RP-6 pilot: source lock, complete export replay and review bindings."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .contract import digest, load_json, write_json
from .images import file_hash, versions
from .p1_export import export_p1, export_pilot
from .repair import require
from .rp5 import unpack_archive

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "examples/rp6"
BASE = "cd4a8db86e51891f13e305b589837a1a4354c5a2"
PLAN_SHA = "090c0705ab49dd4b56107ee05baffa051225b66e9f24a79dfbf70a33a8c44610"


def plan():
    require(file_hash(PILOT / "plan.json") == PLAN_SHA, "Pilot precommit plan changed")
    data = load_json(PILOT / "plan.json")
    require(data["base_commit"] == BASE and len(data["selection"]) == 6, "Wrong pilot selection")
    for entry in data["selection"]:
        for name, sha in entry["reference_files"].items():
            require(file_hash(ROOT / entry["reference_bundle"] / name) == sha, "Pilot reference changed")
        for name, sha in entry.get("retained_files", {}).items():
            require(file_hash(ROOT / name) == sha, "F-04 compatibility changed")
    require(file_hash(ROOT / "examples/rp5/baseline.zip") == data["repair_archive_sha256"], "Repair archive changed")
    return data


def build_exports(output):
    """New destination only. Rebuild definitions from original proof-bearing sources."""
    data = plan()
    require(not output.exists(), "Use a new pilot output directory")
    output.mkdir(parents=True)
    result = []
    with tempfile.TemporaryDirectory(prefix="rp6-repair-") as tmp:
        repaired = Path(tmp) / "baseline"
        unpack_archive(ROOT / "examples/rp5/baseline.zip", load_json(ROOT / "examples/rp5/archive.json"), repaired)
        for e in data["selection"]:
            start = time.monotonic()
            stem = e["definition_id"].lower().replace("-", "")
            reference = ROOT / e["reference_bundle"]
            if stem == "f04":
                export_p1(reference, e["variant"], ROOT / "prototypes/p1/art/f04.svg", e["name"], output / stem)
            else:
                bundle = repaired / e["repair_bundle"] if e["kind"] == "repair" else reference
                if e["kind"] == "repair":
                    for name, sha in e["repair_files"].items():
                        require(file_hash(bundle / name) == sha, "Repair source changed")
                    raw = load_json(bundle / "repair.json")
                    require(raw["id"] == e["repair_id"] and digest(raw["matrix"]) == e["matrix_hash"], "Wrong final repair")
                export_pilot(bundle, e["variant"], ROOT / f"prototypes/p1/art/{stem}.png", e["name"], output / stem,
                             e["definition_id"], reference=reference if e["kind"] == "repair" else None)
            manifest = load_json(output / stem / "manifest.json")
            for folder, suffix in (("data", ".json"), ("art", ".svg" if stem == "f04" else ".png")):
                relative = f"{folder}/{stem}{suffix}"
                require(file_hash(output / stem / relative) == file_hash(ROOT / "prototypes/p1" / relative), "Registered pilot differs from fresh export")
            result.append({"definition_id": e["definition_id"], "seconds": time.monotonic()-start,
                           "export_manifest_sha256": file_hash(output / stem / "manifest.json"),
                           "source": manifest.get("source", {"kind": "import", "candidate_id": manifest["candidate_id"]} ) if stem == "f04" else manifest["source"]})
    return result


def validate_manifest(manifest, data):
    require(manifest["format"] == "picross-rp6-pilot-v1" and manifest["plan_sha256"] == PLAN_SHA and manifest["base_commit"] == data["base_commit"], "Wrong pilot manifest")
    require(manifest["owner_trials"] == "open" and manifest["phase_decision"] == "open", "Automated replay cannot accept owner gates")
    expected_ids = [e["definition_id"] for e in data["selection"]]
    require([e["definition_id"] for e in manifest["entries"]] == expected_ids, "Missing/duplicate/reordered pilot slots")
    required_files = {"examples/rp6/plan.json", "examples/rp6/artwork/prompts.json", "examples/rp6/artwork/preparation.json", "examples/rp6/owner-protocol.json"}
    required_files.update(p.relative_to(ROOT).as_posix() for p in (PILOT / "exports").rglob("*") if p.is_file())
    for e, locked in zip(manifest["entries"], data["selection"]):
        stem = e["definition_id"].lower().replace("-", "")
        asset = f"prototypes/p1/art/{stem}." + ("svg" if stem == "f04" else "png")
        require(e["asset"] == asset and e["definition"] == f"prototypes/p1/data/{stem}.json" and
                e["revision"] == locked["revision"] and e["source_kind"] == locked["kind"], "Wrong registration/source binding")
        expected_export = "examples/rp3/p1-export/manifest.json" if stem == "f04" else f"examples/rp6/exports/{stem}/manifest.json"
        require(e["candidate_id"] == locked["candidate_id"] and e["repair_id"] == locked.get("repair_id") and
                e["reference_bundle"] == locked["reference_bundle"] and e["dimensions"] == locked["dimensions"] and
                e["export_manifest"] == expected_export and e["certified"] is True, "Wrong pilot provenance")
        require(e["matrix_hash"] == locked["matrix_hash"] and e["editorial_release"] is False,
                "Wrong matrix/release binding")
        require(e["motif_review"]["status"] == "suitable_for_pilot" and e["motif_review"]["actor"] == "implementing_agent",
                "Missing own visual judgment")
        require(isinstance(e["motif_review"].get("judgment"),str) and len(e["motif_review"]["judgment"]) > 20, "Missing pair assessment")
        require(e["motif_review"]["matrix_hash"] == e["matrix_hash"] and
                e["motif_review"]["reveal_sha256"] == file_hash(ROOT / asset), "Stale visual pair review")
        required_files.update({asset, e["definition"], e["pair_view"], e["raster_view"], expected_export})
    require(required_files <= set(manifest["files"]), "Incomplete pilot file inventory")
    for relative, sha in manifest["files"].items():
        path = ROOT / relative
        require(not path.is_symlink() and ROOT.resolve() in path.resolve().parents and ".." not in Path(relative).parts,
                "Unsafe pilot path")
        require(file_hash(path) == sha, "Pilot file changed: " + relative)
    calls = load_json(PILOT / "artwork/prompts.json")["calls"]
    require(all(c["definition_id"] in expected_ids for c in calls) and len(calls) <= 10 and all(sum(c["definition_id"] == e["definition_id"] for c in calls) <= e["image_call_limit"] for e in data["selection"]), "Native call budget exceeded")
    from PIL import Image, ImageChops
    preparation = load_json(PILOT / "artwork/preparation.json")
    require([e["definition_id"] for e in preparation["operations"]] == expected_ids[1:], "Incomplete image preparation")
    for operation in preparation["operations"]:
        source, asset = ROOT / operation["source"], ROOT / operation["asset"]
        require(operation["source"] in manifest["files"] and operation["asset"] in manifest["files"], "Unbound image preparation")
        require(file_hash(source) == operation["source_sha256"] and file_hash(asset) == operation["asset_sha256"], "Image preparation changed")
        if operation["definition_id"] == "F-07":
            with Image.open(source) as original, Image.open(asset) as final:
                expected = Image.new("RGB", (1536,1536), "white")
                require(original.size == (1536,1024), "Unexpected cat source dimensions")
                expected.paste(original.convert("RGB"), (0,256))
                require(final.size == expected.size and ImageChops.difference(expected,final.convert("RGB")).getbbox() is None, "Cat framing stretched/altered")
        else:
            require(file_hash(source) == file_hash(asset), "Byte-copy artwork changed")


def verify_package(output):
    started = time.monotonic()
    require(not output.exists(), "Use new verification output")
    data = plan()
    manifest = load_json(PILOT / "manifest.json")
    validate_manifest(manifest, data)
    fresh = build_exports(output / "exports")
    for e, locked in zip(manifest["entries"], data["selection"]):
        stem = e["definition_id"].lower().replace("-", "")
        # Exact stored export reproduction (v1 retains historical timing fields).
        fresh_manifest = load_json(output / "exports" / stem / "manifest.json")
        if stem != "f04":
            require(load_json(PILOT / "exports" / stem / "manifest.json") == fresh_manifest, "Stored export manifest changed")
        for name, sha in fresh_manifest["files"].items():
            require(file_hash((ROOT / "examples/rp3/p1-export" if stem == "f04" else PILOT / "exports" / stem) / name) == sha,
                    "Stored export payload changed")
        from PIL import Image, ImageChops
        from .images import raster_image
        definition = load_json(ROOT / e["definition"])
        mapping = fresh_manifest["color_mapping"]
        inverse = {value: key for key, value in mapping.items()}
        matrix = [[inverse[v] for v in row] for row in definition["solution"]]
        require(digest(matrix) == locked["matrix_hash"], "Wrong reconstructed final matrix")
        expected = raster_image(matrix, load_json(ROOT / locked["reference_bundle"] / "design.json"))
        with Image.open(ROOT / e["raster_view"]) as actual:
            require(actual.size == expected.size and ImageChops.difference(actual.convert("RGB"),expected.convert("RGB")).getbbox() is None,
                    "Pair view raster differs from certified matrix")
        required = {e["asset"], e["definition"], e["pair_view"]}
        require(required <= set(manifest["files"]), "Missing definition/asset/pair file binding")
    checkout = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    report = {"format": "picross-rp6-verification-v1", "accepted": True,
              "source_commit": os.environ.get("P1_PREFLIGHT_SOURCE_COMMIT", os.environ.get("RP1_SOURCE_HEAD", checkout)),
              "base_commit": os.environ.get("RP1_BASE_COMMIT", BASE), "tested_checkout_commit": checkout,
              "github_run_id": os.environ.get("GITHUB_RUN_ID"),
              "source_tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
              "manifest_sha256": file_hash(PILOT / "manifest.json"), "plan_sha256": PLAN_SHA,
              "host": platform.system(), "python": platform.python_version(), "image_versions": versions(),
              "exports": fresh, "elapsed_seconds": time.monotonic()-started,
              "independent_review": "open", "owner_trials": "open", "phase_decision": "open"}
    write_json(output / "verification.json", report)
    shutil.copyfile(PILOT / "manifest.json", output / "manifest.json")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    require(not args.output_dir.exists(), "Use new verification output")
    report = verify_package(args.output_dir)
    print("RP6_VERIFY_OK", report["elapsed_seconds"])


if __name__ == "__main__":
    main()
