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

from web_tests.contract import (coverage, browser_request, requested_groups,
                                validate_request, BROWSER_SCOPES)
import native_contract
import production_contract

FORMAT = "picross-ci-selection-v6"
JOBS = ("docs", "product", "production", "preflight", "web", "delivery")
FLAGS = ("product", "production", "preflight", "integration", "pilots", "visual", "perf_b", "web", "delivery")
SHA = re.compile(r"[0-9a-f]{40}\Z")
ZERO = "0" * 40
INERT_SNAPSHOT = '7b7ea9ce6b5dc2e3ea024207a605cce31847f66b'

# Audited computation-only modules and their fixed synthetic tests. Importing a
# common schema does not exempt that schema: contract, catalog, export, fixtures
# and package entry points deliberately stay outside this exact list.
ANALYSIS_PATHS = frozenset({
    "tools/puzzle_production/" + name for name in (
        "analysis.py", "analysis_cli.py", "analysis_contract.py", "analysis_io.py",
        "analysis_rules.py", "analysis_verifier.py", "solver.py", "paired_solver.py",
        "difficulty_identity.py", "difficulty_rating.py", "difficulty_method_0_3.json",
        "difficulty_calibration_0_3.json", "difficulty_references_0_3.json",
        "sd2_analysis.py", "sd2_cli.py", "sd2_contract.py", "sd2_io.py",
        "sd2_profiles.py", "sd2_rules.py", "sd2_verifier.py", "sd2_rating.py",
        "sd2_rating_cli.py", "sd2_rating_freeze.py", "sd2_rating_identity.py",
        "sd2_rating_io.py", "sd2_reference_checks.py", "sd2_method_0_4.json",
        "sd2_references_0_4.json", "sd2_calibration_0_4.json",
        "sd2_validation_0_4.json", "sd2_comparison_0_4.json",
    )
} | {"tests/puzzle_production/" + name for name in (
    "test_analysis.py", "test_difficulty_rating.py", "test_lines.py", "test_color_lines.py",
    "test_sd2_analysis.py", "test_sd2_rating.py",
)})
DELIVERY_PATHS = frozenset({"tools/deploy_web.py", "tools/web_tests/ssh_reference.py"})
BROWSER_PATHS = frozenset({"tools/web_tests/" + name for name in (
    "browser.py", "browser_actions.py", "browser_runtime.py", "smoke.py", "fixtures.py", "probe.gd",
    "group_catalog.py", "group_input.py", "group_completion.py", "group_persistence.py", "timing.py",
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
    if re.fullmatch(r"content/added/pz-[a-z0-9][a-z0-9-]{0,59}\.json", path):
        return True
    if re.fullmatch(r"content/difficulty/pz-[a-z0-9][a-z0-9-]{0,59}/rating\.json", path):
        return True
    if re.fullmatch(r"content/reveals/pz-[a-z0-9][a-z0-9-]{0,59}\.json", path):
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


def inert_path(path: str) -> bool:
    """Audited evidence formats in the six reader-free CI2-E classes only.

    This predicate alone grants no exception: make_plan also requires an
    existing regular old side and regular/deleted new side in tree metadata.
    New files, executable modes, links and code never inherit this shortcut.
    """
    return (re.fullmatch(r"(?:docs/evidence/(?:hz-a|hz-b|hz-c|at-a)/|"
                         r"docs/design/at_b_integration/|"
                         r"content/authoring/pz-[a-z0-9][a-z0-9-]{0,59}/at-b-r01/)"
                         r"[a-zA-Z0-9_ /.-]+\.(?:gz|jpg|json|log|md|png|txt|zip)", path) is not None
            and all(part not in {'.', '..'} and not part.startswith('.') for part in path.split('/')))


def approved_inert_paths(fetch: bool) -> set[str]:
    """Bind the exception to the audited tree, without a growing file manifest.

    Trees and commit metadata suffice; no evidence blobs are read or fetched.
    New names in these directories do not silently become approved evidence.
    """
    if fetch:
        git('fetch', '--filter=blob:none', '--no-tags', '--depth=1', 'origin', INERT_SNAPSHOT)
    paths = git('ls-tree', '-rz', '--name-only', INERT_SNAPSHOT, '--',
                'docs/evidence', 'docs/design/at_b_integration', 'content/authoring')
    return {p for p in paths.decode('utf-8').split('\0') if inert_path(p)}


def classify(paths: list[str], force: str = "auto", browser_scope: str = "none",
             inert_paths: list[str] | None = None) -> dict:
    request = browser_request(browser_scope)
    inert_paths = sorted(inert_paths or [])
    if len(set(inert_paths)) != len(inert_paths) or any(p not in paths or not inert_path(p) for p in inert_paths):
        raise ValueError('Invalid inert metadata selection')
    selected = {key: False for key in FLAGS}
    reasons = {key: [] for key in FLAGS}

    def add(keys, reason):
        for key in keys:
            if key == 'web':
                continue  # No path or general scope can authorize a browser.
            selected[key] = True
            if reason not in reasons[key]:
                reasons[key].append(reason)

    for path in sorted(set(paths)):
        original = path
        if path in inert_paths:
            continue
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
        if path in native_contract.PATHS and path.startswith("tools/"):
            add(("product",), original)
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
            "tools/ci_scope.py", "tools/test_ci_scope.py", "tools/test_ci2_a.py",
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
        **{"native-"+g: ("product",) for g in native_contract.GROUPS},
    }
    if force not in forced:
        raise ValueError("Unknown requested scope: " + force)
    add(forced[force], "explicit scope: " + force)
    content_only = bool(paths) and all(content_path(path) for path in paths) and force == "auto" and request is None
    native_groups = native_contract.select_groups(reasons["product"])
    for flag, group in (("integration", "history"), ("pilots", "adapters"), ("visual", "graphics"), ("perf_b", "graphics")):
        selected[flag] = group in native_groups
        reasons[flag] = reasons["product"] if selected[flag] else []
    browser_groups = requested_groups(request)
    production_groups = production_contract.select_groups(reasons['production'])
    selected['web'] = bool(browser_groups)
    reasons['web'] = ['explicit browser scope: ' + browser_scope] if request else []
    return {"native_groups": native_groups, "native_expected": native_contract.coverage(native_groups),
            "production_groups": production_groups, "production_expected": production_contract.coverage(production_groups),
            "browser_request": request, "inert_paths": inert_paths,
            "browser_groups": browser_groups, "browser_expected": coverage(browser_groups),
            "format": FORMAT, "content_only": content_only, "selected": {"docs": True, **selected},
            "reasons": {"docs": ["documents, tool contracts and full diff"], **reasons},
            "changed_paths": sorted(set(paths)), "requested_scope": force}


def git(*args: str, input: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", *args], input=input, timeout=90)


def fetch_diff_blobs(base: str, head: str, excluded: list[str] | None = None) -> None:
    """Batch the missing old/new blobs before checking a partial-clone diff.

    Raw tree metadata does not open blobs. Object lookup explicitly disables
    lazy fetching: otherwise hundreds of individual network round trips can
    exhaust the diff's timeout before it has checked the complete change.
    Content-only selection never calls this function.
    """
    if base and base != ZERO:
        raw = git("diff", "--raw", "--no-renames", "--no-abbrev", "-z", base, head)
    else:
        raw = git("diff-tree", "--root", "-r", "-m", "--no-commit-id",
                  "--no-renames", "--no-abbrev", "-z", head)
    objects = set()
    entries = raw.split(b"\0")
    for header, path in zip(entries[0::2], entries[1::2]):
        if path.decode('utf-8') in (excluded or []):
            continue
        old_mode, new_mode, old_oid, new_oid, _ = header.lstrip(b":").split()
        for mode, oid in ((old_mode, old_oid), (new_mode, new_oid)):
            if mode not in {b"000000", b"160000"}:  # Gitlinks are commits, not diff blobs.
                objects.add(validate_sha(oid.decode("ascii")))
    if not objects:
        return
    object_input = ("\n".join(sorted(objects)) + "\n").encode("ascii")
    rows = git("--no-lazy-fetch", "cat-file", "--batch-check=%(objectname) %(objecttype)",
               input=object_input).decode("ascii").splitlines()
    missing = []
    if len(rows) != len(objects):
        raise ValueError("Incomplete diff object lookup")
    for oid, row in zip(sorted(objects), rows):
        if row == oid + " missing":
            missing.append(oid)
        elif row != oid + " blob":
            raise ValueError("Invalid diff blob: " + row)
    if missing:
        # Stdin avoids command-line length limits. Fetch errors remain fatal;
        # no refs, checkout, selection rules or whitespace checks are changed.
        git("-c", "fetch.negotiationAlgorithm=noop", "fetch", "--no-tags",
            "--no-write-fetch-head", "--recurse-submodules=no", "--filter=blob:none",
            "--stdin", "origin", input=("\n".join(missing) + "\n").encode("ascii"))


def validate_sha(value: str) -> str:
    if not SHA.fullmatch(value):
        raise ValueError("Expected a complete hexadecimal commit ID")
    return value


def apply_event_policy(plan: dict, event: str) -> dict:
    plan["event"] = event
    plan["not_applicable_reason"] = "not applicable to the complete changed path set"
    if event == "push":
        # Automatic main integration repeats only the short integrity path.
        # Deliberate manual scopes on main are unaffected by this event rule.
        for key in FLAGS:
            plan["selected"][key] = False
        plan["native_groups"] = []
        plan["native_expected"] = {}
        plan['production_groups'] = []
        plan['production_expected'] = {}
        plan["browser_groups"] = []
        plan["browser_expected"] = {}
        plan["not_applicable_reason"] = "automatic main integrity run; full suites belong to PR or explicit dispatch"
    return plan


def make_plan(base: str, head: str, force: str, fetch: bool = False, event: str = "local",
              browser_scope: str = "none") -> dict:
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
    paths = [path for path in paths if path]
    inert = []
    if base and base != ZERO and any(inert_path(p) for p in paths):
        raw = git('diff', '--raw', '--no-renames', '--no-abbrev', '-z', base, head).decode().split('\0')
        for header, path in zip(raw[0::2], raw[1::2]):
            old_mode, new_mode = header.lstrip(':').split()[:2]
            if inert_path(path) and (old_mode not in {'000000', '100644'} or new_mode not in {'000000', '100644'}):
                raise ValueError('Inert evidence requires regular non-executable files: ' + path)
            if inert_path(path) and old_mode == '100644' and new_mode in {'100644', '000000'}:
                inert.append(path)
        if inert:
            approved = approved_inert_paths(fetch)
            inert = [p for p in inert if p in approved]
    if event not in {'workflow_dispatch', 'local'} and browser_scope != 'none':
        raise ValueError('Browser request requires workflow_dispatch')
    plan = apply_event_policy(classify(paths, force, browser_scope, inert), event)
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
        if fetch:
            fetch_diff_blobs(base, head, inert)
        # The same inert paths are omitted from blob fetching and whitespace
        # checks. Every active rename side and text/code path remains checked.
        if base and base != ZERO:
            if inert:
                active = [p for p in paths if p not in inert]
                # Bound argv size even for large cleanup/mixed diffs. Each path
                # remains literal and is checked against the same exact trees.
                for start in range(0, len(active), 20):
                    git('diff', '--no-renames', '--check', base, head, '--',
                        *[':(top,literal)' + p for p in active[start:start+20]])
            else:
                git("diff", "--no-renames", "--check", base, head)
        else:
            git("show", "--format=", "--check", head)
        plan["diff_check"] = "active-whitespace-check; inert-tree-metadata" if inert else "full-whitespace-check"
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
    request = plan.get('browser_request')
    scope = request.get('scope') if isinstance(request, dict) else 'none'
    expected_plan = classify(paths, plan["requested_scope"], scope, plan.get('inert_paths'))
    if "event" in plan:
        if plan["event"] not in {"push", "pull_request", "workflow_dispatch", "local"}:
            raise ValueError("Unknown selection event")
        expected_plan = apply_event_policy(expected_plan, plan["event"])
        if plan['event'] not in {'workflow_dispatch', 'local'} and request is not None:
            raise ValueError('Automatic event cannot authorize browser work')
    if expected_plan["content_only"] and plan.get("diff_check") == "tree-metadata-only; production evidence reviewed before delivery":
        expected_plan["reasons"]["docs"] = ["content-only: changed paths and regular file modes; no puzzle certification or test suite"]
    for field in ("selected", "reasons", "content_only", "browser_groups", "browser_expected", "native_groups", "native_expected", "production_groups", "production_expected", "browser_request", "inert_paths"):
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
                     ['not requested'] if job == 'web' and not required else
                     [plan.get("not_applicable_reason", "not applicable to the complete changed path set")]})
    return rows


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def native_groups_output(groups: list[str]) -> str:
    """Unambiguous nonempty GitHub job output, including the empty selection."""
    return json.dumps(groups, ensure_ascii=True, separators=(",", ":"))


def validate_binding(plan: dict, binding: dict, outputs: dict) -> None:
    """Cross-check the artifact against this gate's event and scheduler outputs."""
    for key in ("source_head", "base_commit", "tested_checkout", "run_id", "run_attempt", "event"):
        if not binding.get(key) or plan.get(key) != binding[key]:
            raise ValueError("Missing or mismatched selection binding: " + key)
    for key in ("source_head", "base_commit", "tested_checkout"):
        validate_sha(binding[key])
    # GitHub can reuse successful jobs on a failed-job retry within this exact
    # run. Bind to the producer's attempt, never to an artifact from another run.
    if (not re.fullmatch(r"[1-9][0-9]*", binding["run_attempt"]) or
            not re.fullmatch(r"[1-9][0-9]*", binding.get("gate_attempt", "")) or
            int(binding["run_attempt"]) > int(binding["gate_attempt"])):
        raise ValueError("Invalid selection/gate attempt ordering")
    if plan.get("comparison") != "exact-base-to-head-trees-no-renames":
        raise ValueError("Invalid comparison contract")
    expected_diff = ("tree-metadata-only; production evidence reviewed before delivery"
                     if plan["content_only"] else "active-whitespace-check; inert-tree-metadata" if plan['inert_paths'] else "full-whitespace-check")
    if plan.get("diff_check") != expected_diff:
        raise ValueError("Missing or inconsistent diff verification")
    if (set(outputs) != set(FLAGS) | {"selection_attempt", "native_groups", "production_groups", "browser_request"} or
            outputs['browser_request'] != request_output(plan['browser_request']) or
            outputs["selection_attempt"] != binding["run_attempt"] or
            outputs["native_groups"] != native_groups_output(plan["native_groups"]) or any(
            outputs[key] != str(plan["selected"][key]).lower() for key in FLAGS)):
        raise ValueError("Selection artifact and scheduled job outputs disagree")
    if outputs['production_groups'] != production_contract.output(plan['production_groups']):
        raise ValueError('Selection artifact and scheduled production groups disagree')


def request_output(request):
    return json.dumps(request, ensure_ascii=True, separators=(',', ':'))


def validate_original_event(plan):
    """Read the runner's original webhook, never a downloaded plan's inputs."""
    event = os.environ['GITHUB_EVENT_NAME']
    payload = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'),
                         object_pairs_hook=unique_object)
    validate_request(plan, event, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--base", default="")
    plan_parser.add_argument("--head", required=True)
    plan_parser.add_argument("--scope", default="auto")
    plan_parser.add_argument('--browser-scope', choices=BROWSER_SCOPES, default='none')
    plan_parser.add_argument("--fetch", action="store_true")
    plan_parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
    plan_parser.add_argument("--output", type=Path, required=True)
    finish = commands.add_parser("finish")
    finish.add_argument("--web-evidence", type=Path)
    finish.add_argument("--native-evidence", type=Path)
    finish.add_argument("--native-player", type=Path)
    finish.add_argument('--production-evidence', type=Path)
    finish.add_argument("--plan", default=os.environ.get("CI_PLAN", ""))
    finish.add_argument("--plan-file", type=Path)
    finish.add_argument("--results", default=os.environ.get("CI_RESULTS", ""))
    finish.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            validate_original_event({'browser_request': browser_request(args.browser_scope), 'requested_scope': args.scope})
        result = make_plan(args.base, args.head, args.scope, args.fetch, args.event, args.browser_scope)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
                for key in FLAGS:
                    stream.write(f"{key}={str(result['selected'][key]).lower()}\n")
                stream.write(f"content_only={str(result['content_only']).lower()}\n")
                stream.write("native_groups=" + native_groups_output(result["native_groups"]) + "\n")
                stream.write('production_groups=' + production_contract.output(result['production_groups']) + '\n')
                stream.write('browser_request=' + request_output(result['browser_request']) + '\n')
                stream.write(f"selection_attempt={result['run_attempt']}\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    plan = args.plan_file.read_text(encoding="utf-8") if args.plan_file else args.plan
    plan = json.loads(plan, object_pairs_hook=unique_object)
    rows = evaluate(plan, json.loads(args.results, object_pairs_hook=unique_object))
    if os.environ.get("GITHUB_ACTIONS") == "true":
        validate_original_event(plan)
        validate_binding(plan, json.loads(os.environ.get("CI_BINDING", "{}"), object_pairs_hook=unique_object),
                         json.loads(os.environ.get("CI_OUTPUTS", "{}"), object_pairs_hook=unique_object))
    report = {"format": "picross-ci-result-v6", "accepted": all(row["accepted"] for row in rows),
              'browser_status': 'requested' if plan['browser_request'] else 'not requested',
              "selection": plan, "jobs": rows}
    if plan['selected']['production']:
        try:
            if not args.production_evidence:
                raise ValueError('Selected production requires actual Fachtest evidence')
            from production_results import validate_all
            report['production'] = validate_all(plan, args.production_evidence,
                json.loads(os.environ.get('CI_PRODUCTION_OUTPUTS', '{}'), object_pairs_hook=unique_object),
                os.environ.get('GITHUB_RUN_ATTEMPT', plan.get('run_attempt')))
        except (ValueError, OSError, KeyError, TypeError) as error:
            report['accepted'] = False
            report['production_error'] = str(error)
    if plan['selected']['product']:
        try:
            if not args.native_evidence:
                raise ValueError('Selected product requires actual native evidence')
            from native_results import validate_all
            report['native'] = validate_all(plan, args.native_evidence, args.native_player,
                json.loads(os.environ.get('CI_NATIVE_OUTPUTS', '{}'), object_pairs_hook=unique_object),
                os.environ.get('GITHUB_RUN_ATTEMPT', plan.get('run_attempt')))
        except (ValueError, OSError, KeyError, TypeError) as error:
            report['accepted'] = False
            report['native_error'] = str(error)
    if plan['selected']['web']:
        try:
            if not args.web_evidence:
                raise ValueError('Selected web requires actual browser evidence')
            from web_tests.results import validate_all
            report['browsers'] = validate_all(plan, args.web_evidence,
                json.loads(os.environ.get('CI_WEB_OUTPUTS', '{}'), object_pairs_hook=unique_object),
                os.environ.get('GITHUB_RUN_ATTEMPT', plan.get('run_attempt')))
        except (ValueError, OSError, KeyError, TypeError) as error:
            report['accepted'] = False
            report['browser_error'] = str(error)
    if os.environ.get("GITHUB_REPOSITORY") and plan.get("run_id"):
        report["run_url"] = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{plan['run_id']}"
        report["gate_attempt"] = os.environ.get("GITHUB_RUN_ATTEMPT")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write("## Required CI results\n\n| Job | Required | Result | Accepted |\n| --- | --- | --- | --- |\n")
            for row in rows:
                stream.write(f"| {row['job']} | {row['required']} | {row['result']} | {row['accepted']} |\n")
            if report.get('native_error'):
                stream.write('\nNative evidence rejected: '+report['native_error']+'\n')
            if report.get('production_error'):
                stream.write('\nFachtest evidence rejected: '+report['production_error']+'\n')
            if report.get('production'):
                stream.write('\nFachtest groups: '+', '.join(report['production']['groups'])+
                             '; all selected tests, integrations and delivered bytes verified.\n')
            if report.get('native'):
                stream.write('\nNative groups: '+', '.join(report['native']['groups'])+'; all required delivered bytes verified.\n')
            if report.get('browser_error'):
                stream.write('\nBrowser evidence rejected: '+report['browser_error']+'\n')
            for browser in report.get('browsers', []):
                stream.write(f"\n{browser['browser']}: {browser['scenarios']} scenarios in "
                             f"{', '.join(browser['groups'])}; producer attempt {browser['attempt']}.\n")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
