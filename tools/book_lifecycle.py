#!/usr/bin/env python3
"""Run the current short book/help/product lifecycle; no study or browser."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import p1_preflight as tc
from p1_product import run_phase, require_clean_output
from product_fixtures import copy_regression_game
from p1_evidence import source_identity
from book_contract import SOURCES


def run_lifecycle(cache: Path, output: Path) -> dict:
    """Current help/product route; no complete study or material gallery."""
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output must be empty")
    logs = output / "logs"
    logs.mkdir(parents=True)
    host = platform.system()
    editor = tc.EDITORS[host]
    urls = tc.official_asset_urls(tc.request_json(tc.RELEASE_API), (editor,))
    tc.download_asset(urls[editor.name], cache / editor.name, editor.sha256, 1200)
    report = dict(package="HIL-1-T01", scope="help-and-product-lifecycle", **source_identity(ROOT),
                  host=host, platform=platform.platform(), engine=tc.EXPECTED_VERSION,
                  phases=[], sources={name:tc.sha256_file(ROOT/name) for name in SOURCES})
    with tempfile.TemporaryDirectory(prefix="picross-help-lifecycle-") as temp:
        work = Path(temp)
        engine = str(tc.extract_editor(cache / editor.name, work / "engine", host))
        project = work / "game"
        copy_regression_game(ROOT, project)
        env = tc.isolated_environment(work, host)
        integration = work / "integration"
        integration.mkdir()
        env["BOOK_INTEGRATION_OUTPUT"] = str(integration)
        def phase(name, args, marker=None, render=False):
            command = [engine, *args]
            if render and host == "Linux":
                command = ["xvfb-run", "-a", *command]
                env["LIBGL_ALWAYS_SOFTWARE"] = "1"
            result = run_phase("book-"+name, command, env, 300, logs)
            report["phases"].append({k:v for k,v in result.items() if k != "output"})
            require_clean_output(result, marker)
        base = ["--path", str(project), "--audio-driver", "Dummy"]
        phase("version", ["--version"], tc.EXPECTED_VERSION)
        phase("import", ["--headless", *base, "--import"])
        phase("integration", [*base, "--rendering-driver", "opengl3", "--script",
              "res://tests/book_integration.gd", "--", "--p1-capture"], "BOOK_INTEGRATION_OK", True)
        for name in sorted({"integration/integration.json"}):
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(work/name, target)
    report["files"] = {p.relative_to(output).as_posix():dict(bytes=p.stat().st_size, sha256=tc.sha256_file(p))
                       for p in sorted(output.rglob("*")) if p.is_file()}
    report["inventory_cost"] = dict(files=len(report["files"]), bytes=sum(f["bytes"] for f in report["files"].values()),
                                  pngs=0)
    (output/"report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    run_lifecycle(args.cache_dir.resolve(), args.output_dir.resolve())
