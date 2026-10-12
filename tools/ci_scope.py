"""Select the current CI contract and reject missing/failed required results.

Only the Python standard library is needed. Compare exact event base/head trees;
base-only divergence can add checks, but never hides a changed PR path. Renames
are deliberately represented as deletion plus addition so both paths count.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


FORMAT = "picross-ci-selection-v1"
JOBS = ("docs", "product", "production", "preflight")
FLAGS = ("product", "production", "preflight", "integration", "pilots", "visual", "perf_b")
SHA = re.compile(r"[0-9a-f]{40}\Z")
ZERO = "0" * 40


def classify(paths: list[str], force: str = "auto") -> dict:
    selected = {key: False for key in FLAGS}
    reasons = {key: [] for key in FLAGS}

    def add(keys, reason):
        for key in keys:
            selected[key] = True
            if reason not in reasons[key]:
                reasons[key].append(reason)

    for path in sorted(set(paths)):
        original = path
        # Both sides of the one-time project rename retain their obligations.
        if path.startswith("prototypes/p1/"):
            path = "game/" + path.removeprefix("prototypes/p1/")
        if path.startswith(("tools/perf_b", "tools/test_perf_b", "game/art/cells/")) or path in {
            "game/ui/cell_atlas.gd", "game/ui/atlas_marks.gd", "game/ui/atlas_mask.gdshader",
            "game/tests/perf_b_probe.gd", "game/tests/perf_b_cases.gd", "tools/cell_atlas_reference.json",
        }:
            add(("product", "visual", "perf_b"), original)
            continue
        # Some Markdown is a hash-bound production input (e.g. RP4 SELECTION).
        # Route those contracts before treating normative prose as docs-only.
        if path.startswith(("examples/rp", "examples/vs1/")):
            add(("production", "product", "pilots", "visual", "perf_b"), path)
            continue
        if PurePosixPath(path).suffix.lower() == ".md" and (
            path.startswith(("docs/", "game/", "tools/")) or "/" not in path
        ):
            continue
        if path.startswith(".github/") or path in {
            "tools/ci_scope.py", "tools/test_ci_scope.py",
            "tools/p1_product.py", "tools/test_p1_product.py",
            "tools/p1_preflight.py", "tools/test_p1_preflight.py",
            "tools/za1_product.py",
            "tools/kat2_product.py", "tools/test_kat2_product.py",
        } or path.startswith("tools/p1_preflight_smoke/"):
            add(FLAGS, path)
        elif path.startswith(("tools/puzzle_production/", "tests/puzzle_production/",
                              "examples/rp", "examples/vs1/", "content/")):
            add(("production", "product", "pilots", "visual", "perf_b"), path)
        elif path.startswith("game/full_view_study/cases/") or path == "game/full_view_study/catalog.json":
            # These are still the certified technical cases for regular VS2.
            # Verify their production contracts without rebuilding the study.
            add(("production", "product", "visual", "perf_b"), path)
        elif path.startswith("game/"):
            add(("product", "visual", "perf_b"), path)
            if path.startswith(("game/data/", "game/fixtures/", "game/puzzles/")) or path in {
                "game/tests/rp6_probe.gd", "game/tests/rp6_capture.gd",
                "game/tests/rp3_probe.gd", "game/tests/rp3_capture.gd",
            } or re.match(r"game/art/f0[4-9](?:[./_-]|$)", path):
                add(("production", "pilots"), path)
            if not (path.startswith("game/art/") or path in {
                "game/ui/pencil_marks.gd", "game/tests/capture.gd",
                "game/tests/zs2_capture.gd",
            }):
                add(("integration",), path)
        elif path.startswith("docs/design/book_inventory/"):
            add(("product", "visual", "perf_b"), path)
        elif path.startswith("tools/book_inventory/"):
            # Reusable helper tests still run in docs; archived deliveries do not.
            add(("product", "visual", "perf_b"), path)
        elif path in {"tools/check_docs.py", "tools/test_check_docs.py"}:
            continue
        elif path.startswith(("tools/z2_resources", "tools/test_z2_resources")):
            add(("product", "visual", "perf_b"), path)
        elif path.startswith(("tools/rp4_windows_check", "tools/test_rp4_windows")):
            add(("production",), path)
        else:
            add(FLAGS, "unclassified: " + path)

    # Dispatch may widen the actual diff selection, never suppress it.
    forced = {
        "auto": (), "all": FLAGS,
        "runtime": ("product", "integration"),
        "visual": ("product", "visual", "perf_b"),
        "production": ("production", "product", "pilots", "visual", "perf_b"),
        "perf-b": ("product", "visual", "perf_b"),
        "toolchain": FLAGS,
    }
    if force not in forced:
        raise ValueError("Unknown requested scope: " + force)
    add(forced[force], "explicit scope: " + force)
    return {"format": FORMAT, "selected": {"docs": True, **selected},
            "reasons": {"docs": ["documents, tool contracts and full diff"], **reasons},
            "changed_paths": sorted(set(paths)), "requested_scope": force}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], timeout=90)


def validate_sha(value: str) -> str:
    if not SHA.fullmatch(value):
        raise ValueError("Expected a complete hexadecimal commit ID")
    return value


def apply_event_policy(plan: dict, event: str) -> dict:
    plan["event"] = event
    plan["not_applicable_reason"] = "not applicable to the complete changed path set"
    if event == "push":
        # Preserve the existing main-push contract: docs plus changed production
        # checks. Product integration is established by the PR/test-merge run.
        for key in ("product", "preflight", "integration", "pilots", "visual", "perf_b"):
            plan["selected"][key] = False
        plan["not_applicable_reason"] = "main integrity run; product and toolchain verification belong to the PR"
    return plan


def make_plan(base: str, head: str, force: str, fetch: bool = False, event: str = "local") -> dict:
    head = validate_sha(head)
    if base and base != ZERO:
        validate_sha(base)
    if fetch:
        refs = list(dict.fromkeys([head] + ([base] if base and base != ZERO else [])))
        git("fetch", "--no-tags", "--depth=1", "origin", *refs)
    if not base or base == ZERO:
        paths = git("ls-tree", "-rz", "--name-only", head).decode("utf-8").split("\0")
        git("show", "--format=", "--check", head)
    else:
        paths = git("diff", "--no-renames", "--name-only", "-z", base, head).decode("utf-8").split("\0")
        git("diff", "--check", base, head)
    plan = apply_event_policy(classify([path for path in paths if path], force), event)
    plan.update({"source_head": head, "base_commit": base or None,
                 "tested_checkout": git("rev-parse", "HEAD").decode().strip(),
                 "comparison": "exact-base-to-head-trees-no-renames",
                 "run_id": os.environ.get("GITHUB_RUN_ID"),
                 "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT")})
    return plan


def evaluate(plan: dict, results: dict) -> list[dict]:
    if plan.get("format") != FORMAT or not isinstance(plan.get("selected"), dict):
        raise ValueError("Missing or invalid selection report")
    if any(not isinstance(plan["selected"].get(key), bool) for key in FLAGS):
        raise ValueError("Missing or invalid coverage selection")
    if any(plan["selected"][key] for key in ("integration", "pilots", "visual", "perf_b")) and not plan["selected"]["product"]:
        raise ValueError("Selected product coverage without its required job")
    rows = []
    for job in JOBS:
        required = plan["selected"].get(job)
        if not isinstance(required, bool) or (job == "docs" and not required):
            raise ValueError("Invalid requirement for " + job)
        actual = results.get(job, {}).get("result", "missing")
        expected = "success" if required else "skipped"
        rows.append({"job": job, "required": required, "result": actual,
                     "accepted": actual == expected,
                     "reason": plan.get("reasons", {}).get(job, []) if required else
                     [plan.get("not_applicable_reason", "not applicable to the complete changed path set")]})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--base", default="")
    plan_parser.add_argument("--head", required=True)
    plan_parser.add_argument("--scope", default="auto")
    plan_parser.add_argument("--fetch", action="store_true")
    plan_parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
    plan_parser.add_argument("--output", type=Path, required=True)
    finish = commands.add_parser("finish")
    finish.add_argument("--plan", default=os.environ.get("CI_PLAN", ""))
    finish.add_argument("--results", default=os.environ.get("CI_RESULTS", ""))
    args = parser.parse_args()
    if args.command == "plan":
        result = make_plan(args.base, args.head, args.scope, args.fetch, args.event)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
                for key in FLAGS:
                    stream.write(f"{key}={str(result['selected'][key]).lower()}\n")
                stream.write("plan=" + json.dumps(result, ensure_ascii=True, separators=(",", ":")) + "\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    rows = evaluate(json.loads(args.plan), json.loads(args.results))
    report = {"format": "picross-ci-result-v1", "accepted": all(row["accepted"] for row in rows),
              "jobs": rows}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write("## Required CI results\n\n| Job | Required | Result | Accepted |\n| --- | --- | --- | --- |\n")
            for row in rows:
                stream.write(f"| {row['job']} | {row['required']} | {row['result']} | {row['accepted']} |\n")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
