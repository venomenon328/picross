#!/usr/bin/env python3
"""Build/test/export P1 using the verified P1.0 toolchain in a temporary profile."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import p1_preflight as toolchain
import p14_integration
from check_f01 import DATA, verify
from check_f02 import verify as verify_f02

EXPECTED_PROJECT_NAME = "picross · P1"


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
    print(f"RUN {name}", flush=True)
    try:
        process = subprocess.run(command, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise toolchain.PreflightError(f"{name} exceeded {timeout}s") from exc
    output = process.stdout + process.stderr
    (logs / f"{name}.log").write_text(output, encoding="utf-8")
    print(output, flush=True)
    return dict(name=name, exit_code=process.returncode, output=output)


def package(build: Path, output: Path, manifest: dict, readme: str) -> Path:
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
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--process-timeout-seconds", type=int, default=300)
    parser.add_argument("--download-timeout-seconds", type=int, default=1200)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    host = platform.system()
    if host not in toolchain.EDITORS or platform.machine().lower() not in {"amd64", "x86_64"}:
        parser.error("P1 build supports Windows/Linux x86_64 hosts")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    logs = output / "logs"
    logs.mkdir(exist_ok=True)
    try:
        title = project_name(root / "prototypes/p1/project.godot")
        proof_steps = verify(json.loads((DATA / "f01.json").read_text(encoding="utf-8")), json.loads((DATA / "f01-proof.json").read_text(encoding="utf-8")))
        color_proof_steps = verify_f02(json.loads((DATA / "f02.json").read_text(encoding="utf-8")), json.loads((DATA / "f02-proof.json").read_text(encoding="utf-8")))
        metadata = toolchain.request_json(toolchain.RELEASE_API)
        editor = toolchain.EDITORS[host]
        assets = (editor, toolchain.TEMPLATES)
        urls = toolchain.official_asset_urls(metadata, assets)
        hashes = {asset.name: toolchain.download_asset(urls[asset.name], args.cache_dir.resolve() / asset.name, asset.sha256, args.download_timeout_seconds) for asset in assets}
        with tempfile.TemporaryDirectory(prefix="picross-p1-product-") as temporary:
            workspace = Path(temporary).resolve()
            engine = str(toolchain.extract_editor(args.cache_dir.resolve() / editor.name, workspace / "engine", host))
            toolchain.extract_windows_templates(args.cache_dir.resolve() / toolchain.TEMPLATES.name, toolchain.template_directory(workspace, host))
            project = workspace / "p1"
            shutil.copytree(root / "prototypes/p1", project, ignore=shutil.ignore_patterns(".godot", "build"))
            environment = toolchain.isolated_environment(workspace, host)
            results = []

            def phase(name: str, command: list[str], marker: str | None = None) -> None:
                result = run_phase(name, command, environment, args.process_timeout_seconds, logs)
                require_clean_output(result, marker)
                results.append(result)

            phase("version", [engine, "--version"], toolchain.EXPECTED_VERSION)
            base = [engine, "--headless", "--path", str(project)]
            phase("import", base + ["--import"])
            phase("tests", base + ["--script", "res://tests/run_tests.gd"], "P1_TESTS_OK")
            environment["P1_TEST_SAVE_ROOT"] = str(workspace / "roundtrip-saves")
            phase("roundtrip-write", base + ["--script", "res://tests/p13_roundtrip.gd", "--", "--write"], "P1_ROUNDTRIP_WRITE_OK")
            phase("roundtrip-read", base + ["--script", "res://tests/p13_roundtrip.gd", "--", "--read"], "P1_ROUNDTRIP_READ_OK")
            del environment["P1_TEST_SAVE_ROOT"]
            integration_dir = output / "integration"
            integration_dir.mkdir(exist_ok=True)
            integration_plan = integration_dir / "plan.json"
            integration_trace = integration_dir / "trace.jsonl"
            integration_expected = integration_dir / "expected-restart.json"
            plan = p14_integration.write_plan(integration_plan)
            environment.update(P1_TEST_SAVE_ROOT=str(workspace / "integration-saves"),
                               P1_INTEGRATION_PLAN=str(integration_plan),
                               P1_INTEGRATION_TRACE=str(integration_trace),
                               P1_INTEGRATION_EXPECTED=str(integration_expected))
            for start in range(0, 500, 100):
                environment["P1_INTEGRATION_START"] = str(start)
                environment["P1_INTEGRATION_COUNT"] = "100"
                phase(f"integration-{start + 1:03d}-{start + 100:03d}",
                      base + ["--script", "res://tests/p14_integration.gd", "--", "--write"],
                      "P1_INTEGRATION_WRITE_OK")
            oracle = p14_integration.validate_trace(plan, integration_trace)
            final = json.loads((integration_dir / "trace.jsonl.final.json").read_text(encoding="utf-8"))
            for key in ("cells", "history", "cursor", "undo_used"):
                if final[key] != oracle[key]:
                    raise toolchain.PreflightError(f"Integration final {key} differs from independent oracle")
            if oracle["cursor"] >= len(oracle["history"]):
                raise toolchain.PreflightError("Integration ended without required redo branch")
            # The oracle supplies gameplay truth; the trace supplies the exact view to
            # compare across the real process boundary. View assertions run separately.
            integration_expected.write_text(json.dumps({**oracle, "view": final["view"],
                "row_reads": final["row_reads"], "column_reads": final["column_reads"]},
                ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            phase("integration-restart", base + ["--script", "res://tests/p14_integration.gd", "--", "--read"],
                  "P1_INTEGRATION_READ_OK")
            p14_integration.verify_navigation(plan, integration_trace)
            p14_integration.verify_negative_controls(plan, integration_trace)
            integration_summary = p14_integration.summarize(plan, integration_trace, final, host)
            (integration_dir / "summary.json").write_text(json.dumps(integration_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            for key in ("P1_TEST_SAVE_ROOT", "P1_INTEGRATION_PLAN", "P1_INTEGRATION_TRACE", "P1_INTEGRATION_EXPECTED", "P1_INTEGRATION_START", "P1_INTEGRATION_COUNT"):
                del environment[key]
            negative = run_phase("expected-failure", base + ["--script", "res://tests/run_tests.gd", "--", "--force-failure"], environment, args.process_timeout_seconds, logs)
            toolchain.require_expected_failure(negative, "P1_EXPECTED_FAILURE")
            if negative["exit_code"] != 23 or "SCRIPT ERROR:" in negative["output"]:
                raise toolchain.PreflightError("Unexpected negative-test failure")
            results.append(negative)
            phase("controlled-start", base + ["--", "--p1-smoke"], "P1_START_OK")
            h1_files = {}
            for source, name in (("tools/h1_owner_probe.gd", "h1-owner-probe.gd"),
                                 ("tools/h1_owner_probe.ps1", "h1-owner-probe.ps1"),
                                 ("docs/H1_VERIFICATION.md", "H1-PRUEFUNG.md")):
                shutil.copyfile(root / source, output / name)
                h1_files[name] = toolchain.sha256_file(output / name)
            renders = output / "renders"
            renders.mkdir(exist_ok=True)
            environment["P1_CAPTURE_DIR"] = str(renders)
            render_command = [engine, "--path", str(project), "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", "res://tests/capture.gd", "--", "--p1-capture"]
            if host == "Linux":
                if not shutil.which("xvfb-run"):
                    raise toolchain.PreflightError("Real render verification requires xvfb-run on Linux")
                render_command = ["xvfb-run", "-a"] + render_command
                environment["LIBGL_ALWAYS_SOFTWARE"] = "1"
            phase("render-capture", render_command, "P1_CAPTURE_OK")
            build = project / "build/windows"
            build.mkdir(parents=True)
            phase("windows-export", base + ["--export-debug", "P1 Windows x86_64", str(build / "picross-p1.exe")])
            if host == "Windows":
                phase("windows-exported-start", [str(build / "picross-p1.console.exe"), "--headless", "--", "--p1-smoke"], "P1_START_OK")
                phase("windows-exported-gui-start", [str(build / "picross-p1.console.exe"), "--rendering-driver", "opengl3", "--", "--p1-smoke"], "P1_WINDOW_INFO")
            # Build the synthetic worksheet separately, after the production export.
            # Exported players cannot override their main scene via editor --script.
            shutil.copyfile(root / "tools/h1_owner_probe.gd", project / "h1_owner_probe.gd")
            (project / "h1_owner_probe.tscn").write_text(
                '[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://h1_owner_probe.gd" id="1"]\n\n'
                '[node name="H1Probe" type="Control"]\nlayout_mode = 3\nanchors_preset = 15\nanchor_right = 1.0\nanchor_bottom = 1.0\n'
                'grow_horizontal = 2\ngrow_vertical = 2\nscript = ExtResource("1")\n', encoding="utf-8")
            settings = project / "project.godot"
            settings.write_text(settings.read_text(encoding="utf-8").replace(
                'run/main_scene="res://main.tscn"', 'run/main_scene="res://h1_owner_probe.tscn"'), encoding="utf-8")
            phase("h1-probe-import", base + ["--import"])
            phase("h1-owner-probe-start", base + ["--", "--h1-probe-smoke"], "H1_OWNER_PROBE_OK")
            h1_build = workspace / "h1-windows"
            h1_build.mkdir()
            phase("h1-windows-export", base + ["--export-debug", "P1 Windows x86_64", str(h1_build / "picross-h1-probe.exe")])
            if host == "Windows":
                phase("h1-windows-probe-start", [str(h1_build / "picross-h1-probe.console.exe"), "--headless", "--", "--h1-probe-smoke"], "H1_OWNER_PROBE_OK")
            h1_exports = {p.name: toolchain.sha256_file(p) for p in sorted(h1_build.iterdir()) if p.is_file()}
            if set(h1_exports) != {"picross-h1-probe.exe", "picross-h1-probe.console.exe"}:
                raise toolchain.PreflightError("Unexpected/incomplete H1 probe export")
            h1_archive = output / "h1-probe-windows-x86_64.zip"
            with zipfile.ZipFile(h1_archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for name in h1_exports:
                    bundle.write(h1_build / name, name)
                bundle.write(output / "H1-PRUEFUNG.md", "H1-PRUEFUNG.md")
            h1_files[h1_archive.name] = toolchain.sha256_file(h1_archive)
            commit, dirty = toolchain.source_commit(root)
            checkout_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
            owner_probe = output / "owner-probe.ps1"
            shutil.copyfile(root / "tools/p14_owner_probe.ps1", owner_probe)
            manifest = dict(schema=1, source_commit=commit, source_tree_dirty=dirty, tested_checkout_commit=checkout_commit,
                            host=host, engine_version=toolchain.EXPECTED_VERSION, project_name=title, assets=hashes, proof_steps=proof_steps, color_proof_steps=color_proof_steps,
                            artwork_files={name: toolchain.sha256_file(root / "prototypes/p1/art" / name) for name in ("f01.svg", "f02.svg")},
                            fixture_files={name: toolchain.sha256_file(root / "prototypes/p1/data" / name) for name in ("f01.json", "f01-proof.json", "f02.json", "f02-proof.json")},
                            render_files={p.name: toolchain.sha256_file(p) for p in sorted(renders.iterdir()) if p.is_file()},
                            integration=integration_summary,
                            integration_files={p.name: toolchain.sha256_file(p) for p in sorted(integration_dir.iterdir()) if p.is_file()},
                            owner_probe_sha256=toolchain.sha256_file(owner_probe),
                            h1_probe_files=h1_files,
                            h1_probe_export_files=h1_exports,
                            base_commit=subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=root, capture_output=True, text=True, check=True).stdout.strip(),
                            github_run_id=os.environ.get("GITHUB_RUN_ID"),
                            checks=[dict(name=item["name"], exit_code=item["exit_code"]) for item in results],
                            manual_acceptance="NOT RUN: targeted G1/H1 owner probes; owner explicitly authorized both merges after review/technical checks; prior P1 acceptance remains bound to issue 12's artifact")
            archive = package(build, output, manifest, (root / "prototypes/p1/README.md").read_text(encoding="utf-8"))
            print(f"ARTIFACT {archive} sha256:{toolchain.sha256_file(archive)}", flush=True)
            print("P1 PRODUCT PASS", flush=True)
    except (OSError, ValueError, zipfile.BadZipFile, toolchain.PreflightError) as exc:
        print(f"P1 PRODUCT FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
