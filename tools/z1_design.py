"""Z1 evidence and separate export, called inside the pinned product workspace."""
from __future__ import annotations

import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

import p1_preflight as toolchain


def design_dependencies(project: Path) -> set[Path]:
    """Audit the entire static dependency closure of the independent scene."""
    pending = [project / "design/design.gd"]
    found = set()
    while pending:
        path = pending.pop()
        if path in found:
            continue
        found.add(path)
        text = path.read_text(encoding="utf-8")
        if any(word in text for word in ('user://', 'save_store.gd', 'ui/main.gd', 'OS.execute', 'OS.create_process')):
            raise toolchain.PreflightError(f"Z1 persistence/start-path dependency: {path.name}")
        for dependency in re.findall(r'(?:preload|load)\("res://([^"\n]+\.gd)"\)', text):
            pending.append(project / dependency)
    return found


def compare_pairs(report: dict) -> None:
    indexed = {item["file"]: item for item in report["captures"]}
    for suffix in ("f02-1920x1080", "f02-2560x1440", "f01-1920x1080", "f03-1920x1080"):
        first, second = (indexed[f"v{v}-{suffix}.png"] for v in (1, 2))
        for key in ("state_sha256", "history_sha256", "clues_sha256", "logical_size", "ui_scale", "cell_size", "view", "board_rect", "grid_viewport", "palette"):
            if first[key] != second[key]:
                raise toolchain.PreflightError(f"Unfair Z1 comparison {suffix}/{key}")
        if not all(item["miniature_matches_visible_cells"] for item in (first, second)):
            raise toolchain.PreflightError("Z1 miniature mismatch")


def verify(root: Path, project: Path, engine: str, environment: dict, host: str, output: Path, phase) -> dict:
    dependencies = design_dependencies(project)
    destination = output / "z1"
    renders = destination / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    commit, dirty = toolchain.source_commit(root)
    original_environment = environment.copy()
    environment.update(toolchain.isolated_environment(project.parent / "z1-check-profile", host))
    env_keys = {"Z1_CAPTURE_DIR": str(renders), "Z1_SOURCE_COMMIT": commit}
    environment.update(env_keys)
    base = [engine, "--path", str(project)]
    phase("z1-scene-tests", base + ["--headless", "--script", "res://tests/z1_capture.gd", "--", "--z1-capture", "--z1-tests-only"], "Z1_TESTS_OK")
    render = base + ["--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", "res://tests/z1_capture.gd", "--", "--z1-capture"]
    if host == "Linux":
        render = ["xvfb-run", "-a"] + render
    phase("z1-render", render, "Z1_CAPTURE_OK")
    report = json.loads((renders / "z1-render-report.json").read_text(encoding="utf-8"))
    compare_pairs(report)
    environment.clear()
    environment.update(original_environment)
    return dict(source_commit=commit, source_tree_dirty=dirty,
                tested_checkout_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                base_commit=subprocess.check_output(["git", "merge-base", "HEAD", "origin/main"], cwd=root, text=True).strip(),
                github_run_id=os.environ.get("GITHUB_RUN_ID"), host=host,
                engine_version=toolchain.EXPECTED_VERSION,
                checks=report["checks"], failures=report["failures"],
                dependency_files={p.relative_to(project).as_posix(): toolchain.sha256_file(p) for p in sorted(dependencies)},
                fixtures={p.name: toolchain.sha256_file(p) for p in sorted((project / "data").glob("*.json"))},
                render_files={p.name: toolchain.sha256_file(p) for p in sorted(renders.iterdir()) if p.is_file()},
                comparison="Eight core images: all pairwise state, clue, palette, geometry, scale and zoom fields equal",
                windows_start="pending" if host == "Windows" else "not run on Linux",
                owner_acceptance="not performed; neither variant selected")


def export(root: Path, project: Path, workspace: Path, engine: str, host: str, output: Path, manifest: dict, phase) -> None:
    settings = project / "project.godot"
    old_settings = settings.read_text(encoding="utf-8")
    # Only the temporary copy changes; restore even if export verification fails.
    replacement, count = re.subn(r'run/main_scene="[^"]+"', 'run/main_scene="res://design/main.tscn"', old_settings)
    if count != 1:
        raise toolchain.PreflightError("Z1 temporary main scene not unique")
    build = workspace / "z1-windows"
    build.mkdir()
    base = [engine, "--headless", "--path", str(project)]
    try:
        settings.write_text(replacement, encoding="utf-8", newline="\n")
        phase("z1-export-import", base + ["--import"])
        phase("z1-source-start", base + ["--", "--z1-smoke"], "Z1_START_OK")
        phase("z1-windows-export", base + ["--export-debug", "P1 Windows x86_64", str(build / "picross-z1.exe")])
        if host == "Windows":
            phase("z1-windows-headless-start", [str(build / "picross-z1.console.exe"), "--headless", "--", "--z1-smoke"], "Z1_START_OK")
            phase("z1-windows-opengl-start", [str(build / "picross-z1.console.exe"), "--rendering-driver", "opengl3", "--", "--z1-smoke"], "Z1_START_OK")
            manifest["windows_start"] = "headless and OpenGL executed successfully in isolated profile; not owner acceptance"
    finally:
        settings.write_text(old_settings, encoding="utf-8", newline="\n")
    manifest["export_files"] = {p.name: toolchain.sha256_file(p) for p in sorted(build.iterdir()) if p.is_file()}
    if set(manifest["export_files"]) != {"picross-z1.exe", "picross-z1.console.exe"}:
        raise toolchain.PreflightError("Unexpected/incomplete Z1 Windows export")
    destination = output / "z1"
    report = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (destination / "z1-report.json").write_text(report, encoding="utf-8", newline="\n")
    review = root / "docs/design/Z1_DESIGN_REVIEW.md"
    (destination / review.name).write_bytes(review.read_bytes())
    readme = (root / "prototypes/p1/design/README.md").read_text(encoding="utf-8")
    readme = f"Quellcommit: {manifest['source_commit']}\nArbeitsbaum verändert: {manifest['source_tree_dirty']}\n\n" + readme
    (destination / "START.txt").write_text(readme, encoding="utf-8", newline="\n")
    archive = destination / "picross-z1-windows-x86_64.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in manifest["export_files"]:
            bundle.write(build / name, name)
        bundle.writestr("START.txt", readme)
        bundle.writestr("z1-report.json", report)
        bundle.write(root / "prototypes/p1/design/ASSETS.md", "ASSETS.md")
        bundle.write(root / "prototypes/p1/design/licenses/OpenSans.txt", "licenses/OpenSans.txt")
    print(f"Z1 ARTIFACT {archive} sha256:{toolchain.sha256_file(archive)}", flush=True)
