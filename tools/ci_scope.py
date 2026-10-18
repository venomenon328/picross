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


FORMAT = "picross-ci-selection-v2"
JOBS = ("docs", "product", "production", "preflight", "web", "delivery")
FLAGS = ("product", "production", "preflight", "integration", "pilots", "visual", "perf_b", "web", "delivery")
SHA = re.compile(r"[0-9a-f]{40}\Z")
ZERO = "0" * 40

# Audited computation-only modules and their fixed synthetic tests. Importing a
# common schema does not exempt that schema: contract, catalog, export, fixtures
# and package entry points deliberately stay outside this exact list.
ANALYSIS_PATHS = frozenset({
    "tools/puzzle_production/" + name for name in (
        "analysis.py", "analysis_cli.py", "analysis_contract.py", "analysis_io.py",
        "analysis_rules.py", "analysis_verifier.py", "solver.py", "paired_solver.py",
        "difficulty_identity.py", "difficulty_rating.py", "difficulty_method_0_3.json",
        "difficulty_calibration_0_3.json", "difficulty_references_0_3.json",
    )
} | {"tests/puzzle_production/" + name for name in (
    "test_analysis.py", "test_difficulty_rating.py", "test_lines.py", "test_color_lines.py",
)})
DELIVERY_PATHS = frozenset({"tools/deploy_web.py", "tools/web_tests/ssh_reference.py"})
BROWSER_PATHS = frozenset({"tools/web_tests/" + name for name in (
    "browser.py", "browser_runtime.py", "smoke.py", "fixtures.py", "probe.gd",
)})
WEB_SHARED_PATHS = frozenset({
    "tools/build_web_player.py", "tools/web_bundle.py", "tools/test_web_delivery.py",
    "tools/web_tests/serve.py", "game/web/shell.html", "game/web/storage.js",
    "game/export_presets.cfg", "game/project.godot",
})


def content_path(path: str) -> bool:
    """Only inert authoring/adapter outputs; never runtime code or shared art."""
    if path in {"content/categories.json", "content/registry.json", "content/authoring/index.json",
                "content/authoring/README.md", "game/data/registry.json"}:
        return True
    if re.fullmatch(r"game/data/content/[a-z][a-z0-9_-]{0,63}\.json", path):
        return True
    if re.fullmatch(r"game/art/content/[a-z][a-z0-9_-]{0,63}\.(png|svg|txt)", path):
        return True
    if re.fullmatch(r"content/difficulty/pz-[a-z0-9][a-z0-9-]{0,59}/rating\.json", path):
        return True
    match = re.fullmatch(r"content/difficulty/reports/([a-z][a-z0-9-]{0,63})/report\.(json|md)", path)
    if match:
        return match[1] not in {"con", "prn", "aux", "nul", *(f"{p}{n}" for p in ("com", "lpt") for n in range(1, 10))}
    parts = PurePosixPath(path).parts
    return (len(parts) >= 5 and parts[:2] in (("content", "authoring"), ("content", "packages"))
            and re.fullmatch(r"pz-[a-z0-9][a-z0-9-]{0,59}", parts[2]) is not None
            and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}", parts[3]) is not None
            and all(part not in {".", ".."} and not part.startswith(".") for part in parts[3:])
            and "\\" not in path and PurePosixPath(path).suffix.lower() in
            {".json", ".png", ".jpg", ".jpeg", ".svg", ".txt", ".md", ".html", ".zip"})


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
        if content_path(path):
            continue
        # Both sides of the one-time project rename retain their obligations.
        if path.startswith("prototypes/p1/"):
            path = "game/" + path.removeprefix("prototypes/p1/")
        if path in ANALYSIS_PATHS:
            add(("production",), "audited analysis/solver/rating: " + original)
            continue
        if path == ".github/pull_request_template.md":
            continue
        if path in DELIVERY_PATHS:
            add(("delivery",), original)
            continue
        if path in BROWSER_PATHS:
            add(("web",), original)
            continue
        if path in WEB_SHARED_PATHS:
            add(("web", "delivery"), original)
            if not path.startswith("game/"):
                continue
        if path.startswith(("tools/perf_b", "tools/test_perf_b", "game/art/cells/")) or path in {
            "game/ui/cell_atlas.gd", "game/ui/atlas_marks.gd", "game/ui/atlas_mask.gdshader",
            "game/tests/perf_b_probe.gd", "game/tests/perf_b_cases.gd", "tools/cell_atlas_reference.json",
        }:
            add(("product", "visual", "perf_b"), original)
            if path.startswith("game/"):
                add(("web",), original)
            continue
        # Some Markdown is a hash-bound production input (e.g. RP4 SELECTION).
        # Route those contracts before treating normative prose as docs-only.
        if path.startswith(("examples/rp", "examples/vs1/")):
            add(("production", "product", "pilots", "visual", "perf_b", "web", "delivery"), path)
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
            add(("production", "product", "pilots", "visual", "perf_b", "web", "delivery"), path)
        elif path.startswith("game/full_view_study/cases/") or path == "game/full_view_study/catalog.json":
            # These are still the certified technical cases for regular VS2.
            # Verify their production contracts without rebuilding the study.
            add(("production", "product", "visual", "perf_b", "web"), path)
        elif path.startswith("game/"):
            add(("product", "visual", "perf_b", "web"), path)
            if path.startswith(("game/data/", "game/fixtures/", "game/puzzles/")) or path in {
                "game/tests/rp6_probe.gd", "game/tests/rp6_capture.gd",
                "game/tests/rp3_probe.gd", "game/tests/rp3_capture.gd",
            }:
                add(("production", "pilots"), path)
            if not (path.startswith("game/art/") or path in {
                "game/ui/pencil_marks.gd", "game/tests/capture.gd",
                "game/tests/zs2_capture.gd",
            }):
                add(("integration",), path)
        elif path.startswith("docs/design/book_inventory/"):
            add(("product", "visual", "perf_b", "web"), path)
        elif path.startswith("tools/book_inventory/"):
            # Reusable helper tests still run in docs; archived deliveries do not.
            add(("product", "visual", "perf_b", "web"), path)
        elif path in {"tools/check_docs.py", "tools/test_check_docs.py"}:
            continue
        elif path.startswith(("tools/z2_resources", "tools/test_z2_resources")):
            add(("product", "visual", "perf_b", "web"), path)
        elif path.startswith(("tools/rp4_windows_check", "tools/test_rp4_windows")):
            add(("production",), path)
        else:
            add(FLAGS, "unclassified: " + path)

    # Dispatch may widen the actual diff selection, never suppress it.
    forced = {
        "auto": (), "all": FLAGS,
        "runtime": ("product", "integration", "web"),
        "visual": ("product", "visual", "perf_b", "web"),
        "production": ("production", "product", "pilots", "visual", "perf_b", "web", "delivery"),
        "perf-b": ("product", "visual", "perf_b", "web"),
        "toolchain": FLAGS,
    }
    if force not in forced:
        raise ValueError("Unknown requested scope: " + force)
    add(forced[force], "explicit scope: " + force)
    content_only = bool(paths) and all(content_path(path) for path in paths) and force == "auto"
    return {"format": FORMAT, "content_only": content_only, "selected": {"docs": True, **selected},
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
        for key in ("product", "preflight", "integration", "pilots", "visual", "perf_b", "web", "delivery"):
            plan["selected"][key] = False
        plan["not_applicable_reason"] = "main integrity run; product and toolchain verification belong to the PR"
    return plan


def make_plan(base: str, head: str, force: str, fetch: bool = False, event: str = "local") -> dict:
    head = validate_sha(head)
    if base and base != ZERO:
        validate_sha(base)
    if fetch:
        refs = list(dict.fromkeys([head] + ([base] if base and base != ZERO else [])))
        git("fetch", "--filter=blob:none", "--no-tags", "--depth=1", "origin", *refs)
    if not base or base == ZERO:
        paths = git("ls-tree", "-rz", "--name-only", head).decode("utf-8").split("\0")
    else:
        paths = git("diff", "--no-renames", "--name-only", "-z", base, head).decode("utf-8").split("\0")
    plan = apply_event_policy(classify([path for path in paths if path], force), event)
    if plan["content_only"] and base and base != ZERO:
        # Tree metadata only: do not fetch/open ZIPs, images, proofs or the corpus.
        raw = git("diff", "--raw", "--no-renames", "--no-abbrev", "-z", base, head).decode().split("\0")
        for header, path in zip(raw[0::2], raw[1::2]):
            old_mode, new_mode = header.lstrip(":").split()[:2]
            if old_mode not in {"000000", "100644"} or new_mode not in {"000000", "100644"}:
                raise ValueError("Content delivery requires regular non-executable files: " + path)
        plan["reasons"]["docs"] = ["content-only: changed paths and regular file modes; no puzzle certification or test suite"]
        plan["diff_check"] = "tree-metadata-only; production evidence reviewed before delivery"
    else:
        plan["content_only"] = False
        if base and base != ZERO:
            git("diff", "--check", base, head)
        else:
            git("show", "--format=", "--check", head)
        plan["diff_check"] = "full-whitespace-check"
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
    if not isinstance(plan.get("content_only"), bool):
        raise ValueError("Missing content-only selection")
    if plan["content_only"] and (any(plan["selected"][key] for key in FLAGS) or
                                not plan.get("changed_paths") or
                                not all(content_path(p) for p in plan["changed_paths"]) or
                                plan.get("requested_scope") != "auto"):
        raise ValueError("Inconsistent content-only selection")
    if any(plan["selected"][key] for key in ("integration", "pilots", "visual", "perf_b")) and not plan["selected"]["product"]:
        raise ValueError("Selected product coverage without its required job")
    paths = plan.get("changed_paths")
    if not isinstance(paths, list) or any(not isinstance(p, str) or not p for p in paths):
        raise ValueError("Missing or invalid changed paths")
    if paths != sorted(set(paths)) or plan.get("requested_scope") is None:
        raise ValueError("Duplicate paths or missing requested scope")
    expected_plan = classify(paths, plan["requested_scope"])
    if "event" in plan:
        if plan["event"] not in {"push", "pull_request", "workflow_dispatch", "local"}:
            raise ValueError("Unknown selection event")
        expected_plan = apply_event_policy(expected_plan, plan["event"])
    if expected_plan["content_only"] and plan.get("diff_check") == "tree-metadata-only; production evidence reviewed before delivery":
        expected_plan["reasons"]["docs"] = ["content-only: changed paths and regular file modes; no puzzle certification or test suite"]
    for field in ("selected", "reasons", "content_only"):
        if plan.get(field) != expected_plan[field]:
            raise ValueError("Inconsistent selection field: " + field)
    if not isinstance(results, dict) or set(results) != set(JOBS):
        raise ValueError("Missing or unexpected job results")
    rows = []
    for job in JOBS:
        required = plan["selected"].get(job)
        if not isinstance(required, bool) or (job == "docs" and not required):
            raise ValueError("Invalid requirement for " + job)
        if not isinstance(results[job], dict) or set(results[job]) != {"result"}:
            raise ValueError("Invalid job result: " + job)
        actual = results[job]["result"]
        expected = "success" if required else "skipped"
        rows.append({"job": job, "required": required, "result": actual,
                     "accepted": actual == expected,
                     "reason": plan.get("reasons", {}).get(job, []) if required else
                     [plan.get("not_applicable_reason", "not applicable to the complete changed path set")]})
    return rows


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def validate_binding(plan: dict, binding: dict, outputs: dict) -> None:
    """Cross-check the artifact against this gate's event and scheduler outputs."""
    for key in ("source_head", "base_commit", "tested_checkout", "run_id", "run_attempt", "event"):
        if not binding.get(key) or plan.get(key) != binding[key]:
            raise ValueError("Missing or mismatched selection binding: " + key)
    for key in ("source_head", "base_commit", "tested_checkout"):
        validate_sha(binding[key])
    if plan.get("comparison") != "exact-base-to-head-trees-no-renames":
        raise ValueError("Invalid comparison contract")
    expected_diff = ("tree-metadata-only; production evidence reviewed before delivery"
                     if plan["content_only"] else "full-whitespace-check")
    if plan.get("diff_check") != expected_diff:
        raise ValueError("Missing or inconsistent diff verification")
    if set(outputs) != set(FLAGS) or any(
            outputs[key] != str(plan["selected"][key]).lower() for key in FLAGS):
        raise ValueError("Selection artifact and scheduled job outputs disagree")


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
    finish.add_argument("--plan-file", type=Path)
    finish.add_argument("--results", default=os.environ.get("CI_RESULTS", ""))
    finish.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        result = make_plan(args.base, args.head, args.scope, args.fetch, args.event)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
                for key in FLAGS:
                    stream.write(f"{key}={str(result['selected'][key]).lower()}\n")
                stream.write(f"content_only={str(result['content_only']).lower()}\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    plan = args.plan_file.read_text(encoding="utf-8") if args.plan_file else args.plan
    plan = json.loads(plan, object_pairs_hook=unique_object)
    rows = evaluate(plan, json.loads(args.results, object_pairs_hook=unique_object))
    if os.environ.get("GITHUB_ACTIONS") == "true":
        validate_binding(plan, json.loads(os.environ.get("CI_BINDING", "{}"), object_pairs_hook=unique_object),
                         json.loads(os.environ.get("CI_OUTPUTS", "{}"), object_pairs_hook=unique_object))
    report = {"format": "picross-ci-result-v2", "accepted": all(row["accepted"] for row in rows),
              "selection": plan, "jobs": rows}
    if os.environ.get("GITHUB_REPOSITORY") and plan.get("run_id"):
        report["run_url"] = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{plan['run_id']}"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write("## Required CI results\n\n| Job | Required | Result | Accepted |\n| --- | --- | --- | --- |\n")
            for row in rows:
                stream.write(f"| {row['job']} | {row['required']} | {row['result']} | {row['accepted']} |\n")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
