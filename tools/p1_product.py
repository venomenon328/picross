#!/usr/bin/env python3
"""Verify the current P1 product with bounded, change-selected CI evidence."""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import p1_preflight as toolchain
import p14_integration
import z2_resources
import gp48_delivery
import p1_current_visual
import vs2_delivery
from p1_evidence import Evidence, bound_log, native_failure_sources, source_identity
from check_f01 import DATA, verify
from check_f02 import verify as verify_f02

EXPECTED_PROJECT_NAME = "picross · P1"
RENDER_STAGES = ("layout", "views", "cells-f1", "cells-f2", "gestures", "hints", "axis", "h1")


def project_name(project_file: Path) -> str:
    for line in project_file.read_text(encoding="utf-8").splitlines():
        if line.startswith('config/name="') and line.endswith('"'):
            value = line[len('config/name="'):-1]
            if value != EXPECTED_PROJECT_NAME:
                raise toolchain.PreflightError(f"Unexpected project name: {value!r}")
            return value
    raise toolchain.PreflightError("Missing project name")


def require_clean_output(result: dict, marker: str | None = None) -> None:
    toolchain.require_success(result, marker)
    if "SCRIPT ERROR:" in result["output"] or "ERROR:" in result["output"]:
        raise toolchain.PreflightError(f"{result['name']} logged an engine error")


def run_phase(name: str, command: list[str], environment: dict, timeout: int, logs: Path) -> dict:
    """Write live diagnostic output even if the runner is cancelled mid-phase."""
    print(f"RUN {name}", flush=True)
    started = time.monotonic()
    path = logs / f"{name}.log"
    timed_out = False
    with path.open("wb") as stream:
        try:
            process = subprocess.run(command, env=environment, stdout=stream,
                                     stderr=subprocess.STDOUT, timeout=timeout, check=False)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = None
            stream.write(f"\n{name} exceeded {timeout}s\n".encode())
    output = path.read_bytes().decode("utf-8", errors="replace")
    print(output[-4000:], flush=True)
    if len(output) > 4000:
        print(f"[{name}: console tail only; diagnostic log retained separately]", flush=True)
    return dict(name=name, exit_code=exit_code, output=output,
                seconds=round(time.monotonic() - started, 3), timed_out=timed_out,
                log=bound_log(path))


def package(build: Path, output: Path, manifest: dict, readme: str, extras: dict[str, Path] | None = None) -> Path:
    required = {"picross-p1.exe", "picross-p1.console.exe"}
    files = {path.name for path in build.iterdir() if path.is_file()}
    if not required <= files or files - required - {"picross-p1.pck"}:
        raise toolchain.PreflightError(f"Unexpected/incomplete Windows export: {sorted(files)}")
    if any((build / name).stat().st_size == 0 for name in files):
        raise toolchain.PreflightError("Empty Windows export file")
    manifest["export_files"] = {name: toolchain.sha256_file(build / name) for name in sorted(files)}
    report = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (output / "product-report.json").write_text(report, encoding="utf-8", newline="\n")
    archive = output / "picross-p1-windows-x86_64.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in sorted(files):
            bundle.write(build / name, name)
        bundle.writestr("README.txt", f"Quellcommit: {manifest['source_commit']}\nArbeitsbaum verändert: {manifest['source_tree_dirty']}\n\n" + readme)
        bundle.writestr("product-report.json", report)
        for name, path in (extras or {}).items():
            bundle.write(path, name)
    return archive


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--process-timeout-seconds", type=int, default=300)
    parser.add_argument("--download-timeout-seconds", type=int, default=1200)
    for name, description in (
        ("integration", "500 actions and the independent cross-process restart oracle"),
        ("pilots", "all six pilot playthroughs across real processes"),
        ("visual", "current compact native pixel and animation checks"),
    ):
        parser.add_argument("--" + name, action=argparse.BooleanOptionalAction, default=True,
                            help=description + " (manual default: enabled)")
    return parser.parse_args(argv)


def run_integration(output: Path, workspace: Path, environment: dict, base: list[str], phase, host: str) -> dict:
    directory = output / "integration"
    directory.mkdir()
    plan_path, trace = directory / "plan.json", directory / "trace.jsonl"
    expected = directory / "expected-restart.json"
    plan = p14_integration.write_plan(plan_path)
    environment.update(P1_TEST_SAVE_ROOT=str(workspace / "integration-saves"),
                       P1_INTEGRATION_PLAN=str(plan_path), P1_INTEGRATION_TRACE=str(trace),
                       P1_INTEGRATION_EXPECTED=str(expected))
    try:
        for start in range(0, 500, 100):
            environment.update(P1_INTEGRATION_START=str(start), P1_INTEGRATION_COUNT="100")
            phase(f"integration-{start + 1:03d}-{start + 100:03d}",
                  base + ["--script", "res://tests/p14_integration.gd", "--", "--write"],
                  "P1_INTEGRATION_WRITE_OK")
        oracle = p14_integration.validate_trace(plan, trace)
        final = json.loads((directory / "trace.jsonl.final.json").read_text(encoding="utf-8"))
        for key in ("cells", "history", "cursor", "undo_used"):
            if final[key] != oracle[key]:
                raise toolchain.PreflightError(f"Integration final {key} differs from independent oracle")
        if oracle["cursor"] >= len(oracle["history"]):
            raise toolchain.PreflightError("Integration ended without required redo branch")
        expected.write_text(json.dumps({**oracle, "view": final["view"],
            "row_reads": final["row_reads"], "column_reads": final["column_reads"]},
            ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        phase("integration-restart", base + ["--script", "res://tests/p14_integration.gd", "--", "--read"],
              "P1_INTEGRATION_READ_OK")
        p14_integration.verify_navigation(plan, trace)
        p14_integration.verify_negative_controls(plan, trace)
        summary = p14_integration.summarize(plan, trace, final, host)
        (directory / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return summary
    finally:
        for key in ("P1_TEST_SAVE_ROOT", "P1_INTEGRATION_PLAN", "P1_INTEGRATION_TRACE",
                    "P1_INTEGRATION_EXPECTED", "P1_INTEGRATION_START", "P1_INTEGRATION_COUNT"):
            environment.pop(key, None)


def run_pilots(workspace: Path, environment: dict, base: list[str], phase) -> dict:
    pilot_saves = workspace / "rp6-saves"
    environment["P1_TEST_SAVE_ROOT"] = str(pilot_saves)
    slot_checks = []
    try:
        for index in range(3, 9):
            environment["RP6_INDEX"] = str(index)
            for stage in ("partial", "finish", "read"):
                untouched = {p.name: toolchain.sha256_file(p) for p in pilot_saves.glob("*")
                             if p.is_file() and not p.name.startswith(("f01.", f"f{index+1:02d}."))}
                environment["RP6_STAGE"] = stage
                phase(f"rp6-f{index+1:02d}-{stage}", base + ["--script", "res://tests/rp6_probe.gd"],
                      "RP6_" + stage.upper() + "_OK")
                if any(not (pilot_saves / name).is_file() or toolchain.sha256_file(pilot_saves / name) != digest
                       for name, digest in untouched.items()):
                    raise toolchain.PreflightError("Another pilot save changed")
                slot_checks.append(dict(index=index, stage=stage, unchanged_files=untouched))
            if index == 3:
                isolation_control = run_pilot_isolation_control(workspace, environment, base, phase)
    finally:
        for key in ("P1_TEST_SAVE_ROOT", "RP6_STAGE", "RP6_INDEX"):
            environment.pop(key, None)
    return dict(pilots=6, processes=18, separate_slot_checks=slot_checks,
                foreign_slot_control=isolation_control,
                production_replay="not repeated here; authoritative puzzle-production job")


def require_foreign_slot_failure(result: dict) -> None:
    """Accept only the semantic F01 guard, with a natively valid loaded save."""
    output = result["output"]
    errors = [line.strip() for line in output.splitlines() if "ERROR:" in line]
    if (result["exit_code"] != 4
            or errors != ["ERROR: RP3_FAIL: isolated F04 preserves F01 cells after restart"]
            or "RP6_F01_SAVE status=loaded unknown=399" not in output
            or not re.search(r"RP6_RESULT index=3 stage=read checks=\d+ failures=1\b", output)
            or "RP6_READ_OK" in output):
        raise toolchain.PreflightError("Foreign-slot control did not fail solely on valid changed F01 cells")


def run_pilot_isolation_control(workspace: Path, environment: dict, base: list[str], phase) -> dict:
    """Re-read F04 once with a valid changed F01 in a disposable profile copy."""
    original = environment["P1_TEST_SAVE_ROOT"]
    original_stage = environment["RP6_STAGE"]
    control = workspace / "rp6-isolation-control"
    shutil.copytree(original, control)
    try:
        environment["P1_TEST_SAVE_ROOT"] = str(control)
        environment["RP6_STAGE"] = "foreign_write"
        phase("rp6-f04-foreign-slot-write", base + ["--script", "res://tests/rp6_probe.gd"],
              "RP6_FOREIGN_WRITE_OK")
        environment["RP6_STAGE"] = "read"
        phase("rp6-f04-foreign-slot-control", base + ["--script", "res://tests/rp6_probe.gd"],
              validator=require_foreign_slot_failure)
    finally:
        environment["P1_TEST_SAVE_ROOT"] = original
        environment["RP6_STAGE"] = original_stage
    return dict(status="success", processes=2, slot="F-01", native_load="loaded",
                unknown_cells=399, expected_exit=4, expected_failures=1)


def run_visual(output: Path, workspace: Path, project: Path, engine: str,
               environment: dict, phase, python_phase, host: str, pilots: bool) -> tuple[dict, list[Path]]:
    renders = output / "renders"
    renders.mkdir()
    environment["P1_CAPTURE_DIR"] = str(renders)
    command = [engine, "--path", str(project), "--rendering-driver", "opengl3",
               "--audio-driver", "Dummy", "--script", "res://tests/capture.gd",
               "--", "--p1-capture", "--ci-compact"]
    if host == "Linux":
        if not shutil.which("xvfb-run"):
            raise toolchain.PreflightError("Real render verification requires xvfb-run on Linux")
        command = ["xvfb-run", "-a"] + command
        environment["LIBGL_ALWAYS_SOFTWARE"] = "1"
    try:
        reports = []
        for stage in RENDER_STAGES:
            environment["P1_RENDER_STAGE"] = stage
            phase("render-" + stage, command, "P1_CAPTURE_OK")
            report = json.loads((renders / f"render-report-{stage}.json").read_text(encoding="utf-8"))
            if (report.get("failed") or report.get("compact") is not True
                    or report["rendered_count"] < 1
                    or report["retained_count"] != len(report["captures"])
                    or report["retained_count"] > report["rendered_count"]):
                raise toolchain.PreflightError(f"Incomplete compact native stage: {stage}")
            reports.append(report)
        environment.pop("P1_RENDER_STAGE", None)
        combined = dict(stages=len(reports), pixel_checks=sum(r["pixel_checks"] for r in reports),
                        rendered_count=sum(r["rendered_count"] for r in reports),
                        retained_count=sum(r["retained_count"] for r in reports),
                        captures=[c for r in reports for c in r["captures"]], compact=True)
        (renders / "render-report.json").write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")
        # Current contrast, tooltip blocking and recovery layout assertions.
        # No Z2 historical project, comparison or archive is produced.
        z2_command = ["res://tests/z2_capture.gd" if arg == "res://tests/capture.gd" else arg for arg in command]
        phase("current-book-capture", z2_command, "Z2_CAPTURE_OK")
        if pilots:
            environment["P1_TEST_SAVE_ROOT"] = str(workspace / "rp6-saves")
            pilot_command = ["res://tests/rp6_capture.gd" if arg == "res://tests/capture.gd" else arg for arg in command]
            for index in range(3, 9):
                environment["RP6_INDEX"] = str(index)
                phase(f"rp6-f{index+1:02d}-render", pilot_command, "RP6_CAPTURE_OK")
            environment.pop("P1_TEST_SAVE_ROOT", None)
            environment.pop("RP6_INDEX", None)
        current = output / "drawing-renders"
        current.mkdir()
        environment["P1_CAPTURE_DIR"] = str(current)
        environment["ZS2_VARIANT"] = "after"
        current_command = ["res://tests/zs2_capture.gd" if arg == "res://tests/capture.gd" else arg for arg in command]
        phase("current-drawing-capture", current_command, "ZS2_CAPTURE_OK")
        motion = python_phase("current-drawing-pixel-oracles",
                              lambda: p1_current_visual.verify_regular_motion(Path(__file__).resolve().parents[1], current))
        (current / "current-drawing-report.json").write_text(json.dumps(motion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        selected = [renders / entry["file"] for entry in combined["captures"]]
        selected += list(renders.glob("*.json"))
        selected += p1_current_visual.selected_motion_files(current)
        vs2, vs2_files = vs2_delivery.capture_current(
            project, workspace, output, engine, command, environment, phase)
        selected += vs2_files
        if pilots:
            selected += [renders / "rp6-f07-completion-1920-ui100.png"]
        return dict(compact=combined, drawing=motion, vs2=vs2,
                    pilot_native="success" if pilots else "not selected; --no-pilots"), selected
    finally:
        for key in ("P1_CAPTURE_DIR", "P1_RENDER_STAGE", "ZS2_VARIANT", "RP6_INDEX", "P1_TEST_SAVE_ROOT"):
            environment.pop(key, None)


def player_extras(root: Path, output: Path) -> dict[str, Path]:
    extras = {}
    for source, filename in (
        ("tools/p14_owner_probe.ps1", "owner-probe.ps1"),
        ("tools/rp6_owner.ps1", "rp6-owner.ps1"),
        ("tools/zv50_owner.ps1", "zv50-owner.ps1"),
    ):
        path = output / filename
        path.write_text((root / source).read_text(encoding="utf-8"), encoding="utf-8-sig", newline="\n")
        extras[filename] = path
    for name, source in (
        ("RP6-SPIELPROBE.md", "docs/RP6_OWNER_TRIAL.md"),
        ("ZV50-SPIELPROBE.md", "docs/ZV50_OWNER_TRIAL.md"),
        ("VS2-SPIELPROBE.md", "docs/VS2_OWNER_TRIAL.md"),
        ("licenses/resources.json", "prototypes/p1/art/book/manifest.json"),
        ("licenses/Chalkboard-NOTICES.md", "prototypes/p1/art/drawing/NOTICES.md"),
    ):
        extras[name] = root / source
    for path in sorted((root / "prototypes/p1/art/book").glob("*.txt")):
        extras["licenses/" + path.name] = path
    return extras


def package_player(build: Path, output: Path, manifest: dict, root: Path) -> tuple[Path, dict]:
    """Use the same real delivery inputs in Product and the fast docs contract."""
    extras = player_extras(root, output)
    archive = package(build, output, manifest,
                      (root / "docs/VS2_OWNER_TRIAL.md").read_text(encoding="utf-8"), extras)
    expected = {"picross-p1.exe", "picross-p1.console.exe", "README.txt", "product-report.json", *extras}
    return archive, gp48_delivery.verify_player_package(archive, manifest, expected_files=expected)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    host = platform.system()
    if host not in toolchain.EDITORS or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise SystemExit("P1 build supports Windows/Linux x86_64 hosts")
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit("Output directory must be empty; preserve previous evidence in its own directory")
    output.mkdir(parents=True, exist_ok=True)
    evidence = Evidence(output, host, dict(core=True, integration=args.integration,
                                          pilots=args.pilots, visual=args.visual, export=True))
    selected = []

    def python_phase(name, action):
        record = evidence.start(name)
        began = time.monotonic()
        try:
            result = action()
        except Exception as exc:
            evidence.complete(record, dict(seconds=round(time.monotonic() - began, 3)), exc)
            raise
        evidence.complete(record, dict(seconds=round(time.monotonic() - began, 3), exit_code=0))
        return result

    try:
        evidence.report.update(source_identity(root))
        evidence.scope_start("core")
        evidence.report["project_name"] = project_name(root / "prototypes/p1/project.godot")
        evidence.report["book_resources"] = python_phase("current-resource-hashes", z2_resources.verify)
        evidence.report["proof_steps"] = python_phase("f01-certificate", lambda: verify(
            json.loads((DATA / "f01.json").read_text(encoding="utf-8")),
            json.loads((DATA / "f01-proof.json").read_text(encoding="utf-8"))))
        evidence.report["color_proof_steps"] = python_phase("f02-certificate", lambda: verify_f02(
            json.loads((DATA / "f02.json").read_text(encoding="utf-8")),
            json.loads((DATA / "f02-proof.json").read_text(encoding="utf-8"))))
        editor = toolchain.EDITORS[host]

        def assets():
            metadata = toolchain.request_json(toolchain.RELEASE_API)
            urls = toolchain.official_asset_urls(metadata, (editor, toolchain.TEMPLATES))
            return {asset.name: toolchain.download_asset(urls[asset.name],
                    args.cache_dir.resolve() / asset.name, asset.sha256, args.download_timeout_seconds)
                    for asset in (editor, toolchain.TEMPLATES)}
        evidence.report["assets"] = python_phase("verified-toolchain-assets", assets)
        with tempfile.TemporaryDirectory(prefix="picross-p1-product-") as temporary:
            workspace = Path(temporary).resolve()
            engine = str(toolchain.extract_editor(args.cache_dir.resolve() / editor.name, workspace / "engine", host))
            toolchain.extract_windows_templates(args.cache_dir.resolve() / toolchain.TEMPLATES.name,
                                                toolchain.template_directory(workspace, host))
            project = workspace / "p1"
            shutil.copytree(root / "prototypes/p1", project, ignore=shutil.ignore_patterns(".godot", "build"))
            environment = toolchain.isolated_environment(workspace, host)

            def phase(name: str, command: list[str], marker: str | None = None,
                      expected_failure: bool = False, validator=None):
                record = evidence.start(name)
                result = {}
                try:
                    result = run_phase(name, command, environment, args.process_timeout_seconds, evidence.logs)
                    if result["timed_out"]:
                        raise toolchain.PreflightError(f"{name} exceeded {args.process_timeout_seconds}s")
                    if expected_failure:
                        toolchain.require_expected_failure(result, "P1_EXPECTED_FAILURE")
                        if result["exit_code"] != 23 or "SCRIPT ERROR:" in result["output"] or "ERROR:" in result["output"]:
                            raise toolchain.PreflightError("Unexpected negative-test failure")
                        result["expected_failure"] = True
                    elif validator is not None:
                        validator(result)
                        result["expected_failure"] = True
                    else:
                        require_clean_output(result, marker)
                except Exception as exc:
                    evidence.complete(record, result, exc)
                    raise
                evidence.complete(record, result)

            phase("version", [engine, "--version"], toolchain.EXPECTED_VERSION)
            base = [engine, "--headless", "--path", str(project)]
            phase("import", base + ["--import"])
            phase("tests", base + ["--script", "res://tests/run_tests.gd"], "P1_TESTS_OK")
            phase("current-drawing-tests", base + ["--script", "res://tests/zs2_tests.gd", "--", "--p1-capture"], "ZS2_TESTS_OK")
            phase("expected-failure", base + ["--script", "res://tests/run_tests.gd", "--", "--force-failure"],
                  expected_failure=True)
            environment["P1_TEST_SAVE_ROOT"] = str(workspace / "roundtrip-saves")
            for stage in ("write", "read"):
                phase("roundtrip-" + stage, base + ["--script", "res://tests/p13_roundtrip.gd", "--", "--" + stage],
                      "P1_ROUNDTRIP_" + stage.upper() + "_OK")
            environment.pop("P1_TEST_SAVE_ROOT")
            phase("controlled-start", base + ["--", "--p1-smoke"], "P1_START_OK")
            evidence.scope_done("core")
            if args.integration:
                evidence.scope_start("integration")
                evidence.report["integration"] = run_integration(output, workspace, environment, base, phase, host)
                selected += [output / "integration/summary.json"]
                evidence.scope_done("integration")
            if args.pilots:
                evidence.scope_start("pilots")
                evidence.report["pilots"] = run_pilots(workspace, environment, base, phase)
                evidence.scope_done("pilots")
            if args.visual:
                evidence.scope_start("visual")
                evidence.report["visual"], visual_files = run_visual(
                    output, workspace, project, engine, environment, phase, python_phase, host, args.pilots)
                selected += visual_files
                evidence.scope_done("visual")
            evidence.scope_start("export")
            build = project / "build/windows"
            build.mkdir(parents=True)
            phase("windows-export", base + ["--export-debug", "P1 Windows x86_64", str(build / "picross-p1.exe")])
            if host == "Windows":
                phase("windows-exported-start", [str(build / "picross-p1.console.exe"), "--headless", "--", "--p1-smoke"], "P1_START_OK")
                phase("windows-exported-gui-start", [str(build / "picross-p1.console.exe"),
                      "--rendering-driver", "opengl3", "--", "--p1-smoke"], "P1_WINDOW_INFO")
            evidence.scope_done("export")
            evidence.report["manual_acceptance"] = "Automated current CI evidence only; owner acceptance and merge/release authorization are separate."
            evidence.retain_files(selected)
            evidence.enforce_budget()
            evidence.finish()
            package_began = time.monotonic()
            archive, delivery = package_player(build, output, evidence.report, root)
            delivery.update(packaging_seconds=round(time.monotonic() - package_began, 3),
                            total_seconds=round(time.monotonic() - evidence.began, 3))
            evidence.flush()
            audit = evidence.technical / "player-audit.json"
            audit.write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            budget = evidence.enforce_budget(archive)
            print("EVIDENCE_BYTES " + json.dumps(budget, sort_keys=True), flush=True)
            print(f"ARTIFACT {archive} sha256:{toolchain.sha256_file(archive)}", flush=True)
            print("P1 PRODUCT PASS", flush=True)
    except Exception as exc:
        failure_log = evidence.logs / "failure.log"
        failure_log.write_text(traceback.format_exc(), encoding="utf-8")
        bound_log(failure_log)
        failed_phase = evidence.report["checks"][-1]["name"] if evidence.report["checks"] else ""
        failure_files, priority = native_failure_sources(
            output, failed_phase, getattr(exc, "p1_failure_images", ()))
        evidence.retain_files(selected + failure_files, priority_sources=priority)
        evidence.finish(exc)
        print(f"P1 PRODUCT FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
