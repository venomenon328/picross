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
from check_f01 import DATA, verify
from check_f02 import verify as verify_f02


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
            negative = run_phase("expected-failure", base + ["--script", "res://tests/run_tests.gd", "--", "--force-failure"], environment, args.process_timeout_seconds, logs)
            toolchain.require_expected_failure(negative, "P1_EXPECTED_FAILURE")
            if negative["exit_code"] != 23 or "SCRIPT ERROR:" in negative["output"]:
                raise toolchain.PreflightError("Unexpected negative-test failure")
            results.append(negative)
            phase("controlled-start", base + ["--", "--p1-smoke"], "P1_START_OK")
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
            commit, dirty = toolchain.source_commit(root)
            checkout_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
            manifest = dict(schema=1, source_commit=commit, source_tree_dirty=dirty, tested_checkout_commit=checkout_commit,
                            host=host, engine_version=toolchain.EXPECTED_VERSION, assets=hashes, proof_steps=proof_steps, color_proof_steps=color_proof_steps,
                            render_files={p.name: toolchain.sha256_file(p) for p in sorted(renders.iterdir()) if p.is_file()},
                            base_commit=subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=root, capture_output=True, text=True, check=True).stdout.strip(),
                            github_run_id=os.environ.get("GITHUB_RUN_ID"),
                            checks=[dict(name=item["name"], exit_code=item["exit_code"]) for item in results],
                            manual_acceptance="OPEN: owner M-01/M-02/M-03/M-06 mouse, motif and actual Windows scaling before overall P1 merge; prior K-06 had change requests")
            archive = package(build, output, manifest, (root / "prototypes/p1/README.md").read_text(encoding="utf-8"))
            print(f"ARTIFACT {archive} sha256:{toolchain.sha256_file(archive)}", flush=True)
            print("P1 PRODUCT PASS", flush=True)
    except (OSError, ValueError, zipfile.BadZipFile, toolchain.PreflightError) as exc:
        print(f"P1 PRODUCT FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
