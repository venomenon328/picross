"""Fixed nine-reference RP-5 comparison; originals and new results stay separate."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import os
import subprocess
import time

from .contract import Budget, digest, load_json, write_json
from .images import file_hash
from .repair import (PLAN_BYTES, PLAN_FORMAT, VERSION, inspect_repair, make_views,
                     require, search, validate_plan)

ROOT = Path(__file__).resolve().parents[2]
RP4 = ROOT / "examples/rp4"
RP5 = ROOT / "examples/rp5"
BASE = "80ae2c19eb6f85bbac58a247badf65b3e0669132"
ANCHORS = {
    "inputs.json": "21f2f9f5b719f6eb244e3617f351faa9a1d9741d95b68e5a23ee243d791bbe43",
    "baseline/production.json": "63568a23fe97f3465a419e46a4dbf202b4a252ac88c59f358a1a0269a9ac2d3e",
    "reviews.json": "1e7328f772a970e52809e6bde5d0167984143a87971fa1f479f81eb99b128615",
}
# Half-open source-cell rectangles, chosen after opening the RP-4 contact sheets.
# These are deliberately conservative around important colored AND empty details.
SELECTION = [
    ("i02-direct-60x40", "area-128", 2, [[25, 5, 34, 30], [4, 24, 53, 27], [10, 28, 50, 34]],
     "Mast, empty sail gap, sail/hull separator and central hull protected; small wave/outer contour edits only."),
    ("i03-direct-40x40", "area-128", 2, [[18, 20, 23, 39], [10, 27, 30, 35], [10, 3, 30, 20]],
     "Stem, leaf connections, inner empty wedges and central flower protected; outer leaf/flower pixels may change."),
    ("a01-direct-40x40", "area-128", 2, [[12, 2, 29, 15], [11, 32, 29, 37]],
     "Eyes, face, beak, empty facial details and feet/branch contacts protected; feather contours may change."),
    ("a01-direct-100x100", "area-128", 8, [[30, 4, 70, 38], [29, 79, 73, 93]],
     "Large eyes/face/beak and foot/branch contacts protected; eight cells cap changes in textured plumage."),
    ("p01-stylized-40x40", "area-176", 4, [[20, 1, 37, 18], [18, 20, 40, 40], [10, 14, 30, 24]],
     "Face, camera, wrist and tripod including empty leg gaps protected; four jacket/outer-head pixels maximum. Mono reveal still required."),
    ("p02-direct-100x100", "area-128", 4, [[26, 13, 69, 59], [25, 46, 43, 75], [53, 52, 71, 77], [0, 0, 100, 16], [0, 83, 100, 100]],
     "Cup rim/interior, handle and its interior, spoon and contain padding protected; saucer/table texture may change."),
    ("p02-stylized-100x100", "area-128", 4, [[27, 18, 72, 59], [29, 52, 48, 75], [52, 49, 74, 76]],
     "Cup rim/interior, handle including empty interior and spoon protected; outer saucer/background pixels may change."),
    ("h02-direct-50x50", "area-128", 1, [[12, 1, 36, 31], [8, 15, 36, 31], [28, 31, 50, 50]],
     "Face, neck ring, overlap with suit and helmet/visor protected; one noncritical background/suit pixel maximum."),
    ("h02-stylized-50x50", "area-128", 4, [[12, 1, 32, 30], [8, 17, 32, 32], [28, 32, 50, 50]],
     "Face, neck ring, their empty boundaries and helmet/visor protected; up to four suit/background cells."),
]


def source_binding():
    checkout = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    return {"source_commit": os.environ.get("RP1_SOURCE_HEAD", checkout), "tested_checkout_commit": checkout,
            "base_commit": os.environ.get("RP1_BASE_COMMIT", BASE), "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "source_tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())}


def freeze(output):
    require(not (RP5 / "plans.json").exists(), "Plans already fixed; do not loosen after a result")
    RP5.mkdir(parents=True, exist_ok=True)
    trials = []
    for trial, variant, changes, rectangles, rationale in SELECTION:
        reference_dir = RP4 / "baseline" / trial
        c = load_json(reference_dir / f"{variant}-candidate.json")
        d = c["design"]
        mask = [[False]*d["width"] for _ in range(d["height"])]
        for x0, y0, x1, y1 in rectangles:
            require(0 <= x0 < x1 <= d["width"] and 0 <= y0 < y1 <= d["height"], "Bad protection rectangle")
            for y in range(y0, y1):
                for x in range(x0, x1):
                    mask[y][x] = True
        plan = {"format": PLAN_FORMAT, "tool": VERSION,
                "reference": {"candidate_id": c["id"], "manifest_sha256": file_hash(reference_dir / "manifest.json"), "variant": variant},
                "mask": mask, "rationale": rationale,
                "config": {"max_changes": changes, "max_steps": 96, "max_candidates": 16,
                           "search_seconds": 30, "final_seconds": 10, "search_lines": 250000, "final_lines": 100000,
                           "seed": 39, "order": "seeded-frontier-v1", "operators": ["single-cell"]}}
        validate_plan(plan, c)
        path = RP5 / "plans" / f"{trial}.json"
        write_json(path, plan)
        mask_dir = output / trial
        mask_dir.mkdir(parents=True)
        make_views(mask_dir, c["matrix"], c["matrix"], mask, d, [], "plan-fixed-before-search")
        trials.append({"trial": trial, "variant": variant, "plan": f"plans/{trial}.json", "sha256": file_hash(path),
                       "rectangles_xyxy": rectangles, "protected_cells": sum(sum(row) for row in mask),
                       "protected_empty_cells": sum(mask[y][x] and v == "empty" for y, row in enumerate(c["matrix"]) for x, v in enumerate(row))})
    lock = {"format": "picross-rp5-plans-v1", "base_commit": BASE, "rp4_anchors": ANCHORS,
            "trials": trials, "human_minutes": None, "human_effort_status": "not_observed"}
    write_json(RP5 / "plans.json", lock)
    return lock


def plans():
    lock = load_json(RP5 / "plans.json", PLAN_BYTES)
    require(lock["format"] == "picross-rp5-plans-v1" and lock["rp4_anchors"] == ANCHORS, "Wrong RP-4 binding")
    for name, sha in ANCHORS.items():
        require(file_hash(RP4 / name) == sha, "RP-4 baseline changed")
    require([(t["trial"], t["variant"]) for t in lock["trials"]] == [(s[0], s[1]) for s in SELECTION],
            "Dropped/reordered comparison reference")
    out = []
    for t in lock["trials"]:
        require(t["plan"] == f'plans/{t["trial"]}.json' and file_hash(RP5 / t["plan"]) == t["sha256"], "Fixed plan changed")
        p = load_json(RP5 / t["plan"], PLAN_BYTES)
        c = load_json(RP4 / "baseline" / t["trial"] / f'{t["variant"]}-candidate.json')
        validate_plan(p, c)
        out.append((t, p))
    return lock, out


def comparison(repairs, reviews=None):
    production = load_json(RP4 / "baseline/production.json")
    old_reviews = load_json(RP4 / "reviews.json")
    selected = {t[0] for t in SELECTION}
    rows = []
    for trial in production["trials"]:
        for entry in trial["candidates"]:
            variant = entry["variant"]
            original = entry["technical"]
            visual = old_reviews[trial["id"]]["variants"][variant]
            row = {"trial": trial["id"], "variant": variant, "original": original,
                   "original_motif": visual, "selected_for_repair": trial["id"] in selected and variant ==
                   next((t[1] for t in SELECTION if t[0] == trial["id"]), None), "repair": None}
            if row["selected_for_repair"]:
                row["repair"] = repairs[trial["id"]]
                if reviews:
                    row["repair_visual"] = reviews[trial["id"]]
            rows.append(row)
    require(len(rows) == 48 and sum(r["selected_for_repair"] for r in rows) == 9, "Incomplete comparison")
    new_certificates = sum(r["repair"]["result"]["certified"] for r in rows if r["repair"])
    usable = sum(r["repair"]["result"]["certified"] and r.get("repair_visual", {}).get("verdict") == "retained"
                 for r in rows if r["repair"])
    return {"format": "picross-rp5-comparison-v1", "rp4_anchors": ANCHORS, "original_candidates": 48,
            "selected": 9, "not_selected": 39, "original_certified": 19, "original_usable": 14,
            "new_certificates": new_certificates, "new_usable_variants": usable,
            "status_counts": dict(Counter(r["result"]["status"] for r in repairs.values())),
            "human_minutes": None, "human_effort_status": "not_observed", "human_productivity_per_hour": None,
            "manual_cell_corrections": 0, "independent_review": "open", "rows": rows}


def produce(output):
    lock, trial_plans = plans()
    require(not output.exists(), "Use fresh RP-5 production output")
    output.mkdir(parents=True)
    repairs = {}
    for t, p in trial_plans:
        trial = t["trial"]
        result = search(RP4 / "baseline" / trial, p, output / trial)
        inspected = inspect_repair(output / trial, RP4 / "baseline" / trial)
        require(inspected["accepted"], "Repair replay failed")
        raw = load_json(output / trial / "repair.json")
        repairs[trial] = {"repair_id": raw["id"], "repair_sha256": file_hash(output / trial / "repair.json"),
                          "matrix_hash": digest(raw["matrix"]), "changes": raw["changes"], "result": result,
                          "plan_sha256": t["sha256"], "view_sha256": file_hash(output / trial / "view.png")}
        print(trial, result["status"], result["reason"], len(raw["changes"]), flush=True)
    report = comparison(repairs)
    report.update(source_binding(), plans_sha256=file_hash(RP5 / "plans.json"))
    write_json(output / "comparison.json", report)
    return report


def verify_package(output):
    start = time.monotonic()
    lock, trial_plans = plans()
    baseline = RP5 / "baseline"
    original = load_json(baseline / "comparison.json")
    reviews = load_json(RP5 / "reviews.json")
    require(set(reviews) == {t["trial"] for t, _ in trial_plans}, "Missing RP-5 visual review")
    repairs = {}
    checked = []
    for t, p in trial_plans:
        require(time.monotonic()-start < 300, "RP-5 replay exceeds 300 seconds")
        trial = t["trial"]
        bundle = baseline / trial
        require(load_json(bundle / "plan.json") == p, "Production used a different frozen plan")
        fresh = inspect_repair(bundle, RP4 / "baseline" / trial, Budget(60, 1_000_000))
        raw = load_json(bundle / "repair.json")
        result = load_json(bundle / "result.json")
        record = next(r["repair"] for r in original["rows"] if r["trial"] == trial and r["selected_for_repair"])
        expected = {"repair_id": raw["id"], "repair_sha256": file_hash(bundle / "repair.json"), "matrix_hash": digest(raw["matrix"]),
                    "changes": raw["changes"], "result": result, "plan_sha256": t["sha256"], "view_sha256": file_hash(bundle / "view.png")}
        require(record == expected, "Original repair comparison no longer matches written bundle")
        review = reviews[trial]
        require(review["repair_id"] == raw["id"] and review["view_sha256"] == expected["view_sha256"] and
                review["repair_sha256"] == expected["repair_sha256"] and review["plan_sha256"] == t["sha256"] and
                review["verdict"] in ("retained", "damaged") and review["review_kind"] == "implementer_visual_inspection" and
                bool(review["reviewer"]) and bool(review["notes"]), "Unbound/unsupported visual judgment")
        repairs[trial] = expected
        checked.append(fresh)
    current = comparison(repairs, reviews)
    # Original results were recorded before sight judgments; never rewrite them.
    require(all(original[k] == current[k] for k in ("rp4_anchors", "original_candidates", "selected", "not_selected",
                                                   "original_certified", "original_usable", "new_certificates", "status_counts")),
            "Changed original comparison totals")
    require(not output.exists(), "Use fresh RP-5 verification output")
    output.mkdir(parents=True)
    current.update(source_binding(), accepted=True, plans_sha256=file_hash(RP5 / "plans.json"),
                   comparison_sha256=file_hash(baseline / "comparison.json"), reviews_sha256=file_hash(RP5 / "reviews.json"),
                   elapsed_seconds=time.monotonic()-start, fresh_repairs=checked)
    write_json(output / "verification.json", current)
    return current


def main(argv=None):
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("freeze", "produce", "verify"))
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(argv)
    result = {"freeze": freeze, "produce": produce, "verify": verify_package}[args.command](args.output_dir)
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "trials", "fresh_repairs")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
