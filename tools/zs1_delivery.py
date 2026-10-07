"""Small native ZS-1 delivery; current-main baseline, separate player/review ZIPs."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import p1_preflight as toolchain

BASE = "ec99954268f1ad959d9ea779dbbd9e28edf7d8fa"


def before_project(root: Path, workspace: Path) -> Path:
    archive = subprocess.run(["git", "archive", BASE, "prototypes/p1"], cwd=root,
                             capture_output=True, check=True).stdout
    destination = workspace / "zs1-before"
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to("prototypes/p1")
            if ".." in relative.parts:
                raise toolchain.PreflightError("Unsafe ZS1 baseline path")
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bundle.extractfile(member).read())
    for relative in ("tests/zs1_capture.gd", "study/samples.gd"):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / "prototypes/p1" / relative, target)
    return destination


def capture(root, project, workspace, output, engine, render_command, environment, phase):
    renders = output / "zs1-renders"
    renders.mkdir()
    old = environment["P1_CAPTURE_DIR"]
    environment["P1_CAPTURE_DIR"] = str(renders)
    command = ["res://tests/zs1_capture.gd" if part == "res://tests/capture.gd" else part
               for part in render_command]
    phase("zs1-tests", [engine, "--headless", "--path", str(project), "--script",
                        "res://tests/zs1_tests.gd", "--", "--p1-capture"], "ZS1_TESTS_OK")
    phase("zs1-native-study", command, "ZS1_CAPTURE_OK")
    before = before_project(root, workspace)
    phase("zs1-baseline-import", [engine, "--headless", "--path", str(before), "--import"])
    environment["ZS1_BASELINE"] = "1"
    try:
        phase("zs1-native-baseline", [str(before) if part == str(project) else part for part in command], "ZS1_CAPTURE_OK")
    finally:
        environment.pop("ZS1_BASELINE", None)
        environment["P1_CAPTURE_DIR"] = old
    return verify(renders)


def verify(renders: Path) -> dict:
    from PIL import Image, ImageChops
    original = json.loads((renders / "zs1-baseline.json").read_text(encoding="utf-8"))
    study = json.loads((renders / "zs1-study.json").read_text(encoding="utf-8"))
    if original["failures"] or study["failures"]:
        raise toolchain.PreflightError("ZS1 native assertions failed")
    baseline = {item["case"]: item for item in original["captures"]}
    if len(baseline) != 14 or len(study["captures"]) != 42:
        raise toolchain.PreflightError("Incomplete ZS1 comparison matrix")
    for record in study["captures"]:
        old = baseline[record["case"]]
        for key in ("fixture", "size", "ui_scale", "cells_sha256", "view", "board", "grid", "viewport", "pan_target", "tooltip"):
            if old[key] != record[key]:
                raise toolchain.PreflightError(f"ZS1 {record['case']}: changed {key}")
        if not record["spoiler_free"]:
            raise toolchain.PreflightError("ZS1 comparison leaked reveal")
        with Image.open(renders / old["file"]) as a, Image.open(renders / record["file"]) as b:
            if a.size != b.size:
                raise toolchain.PreflightError("ZS1 image dimensions differ")
            if record["style"] == 0:
                x, y, w, h = record["board"]
                box = (int(x), int(y), int(x+w), int(y+h))
                if ImageChops.difference(a.crop(box).convert("RGB"), b.crop(box).convert("RGB")).getbbox():
                    raise toolchain.PreflightError(f"ZS1 regular baseline pixels changed: {record['case']}")
    if len(study["frames"]) != 2 or len(study["measurements"]) != 2:
        raise toolchain.PreflightError("Missing ZS1 movement/load evidence")
    if {item["style"] for item in study["specimens"]} != {0, 1, 2}:
        raise toolchain.PreflightError("Missing ZS1 native numeral specimen")
    for specimen in study["specimens"]:
        if not (renders / specimen["file"]).is_file():
            raise toolchain.PreflightError("Missing ZS1 specimen image")
    for motion in study["frames"]:
        if not (motion["preview_static"] and motion["off_same_end"] and motion["second_gesture_ms"] < 140):
            raise toolchain.PreflightError("ZS1 movement contract failed")
        for frame in motion["timeline"]:
            if not (renders / frame["file"]).is_file():
                raise toolchain.PreflightError("Missing ZS1 timed frame")
        early = next(frame for frame in motion["timeline"] if frame["label"] == "parallel-commit-0")
        settled = next(frame for frame in motion["timeline"] if frame["label"] == "settled")
        if not 0 < early["after_commit_ms"] < 140:
            raise toolchain.PreflightError("ZS1 renderer missed the actual commit effect")
        with Image.open(renders / early["file"]) as a, Image.open(renders / settled["file"]) as b:
            if not ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox():
                raise toolchain.PreflightError("ZS1 native commit effect is not visible")
    return dict(baseline=BASE, identical_regular_board_cases=len(baseline),
                comparison_images=len(study["captures"]), movements=study["frames"],
                measurements=study["measurements"], renderer=study["renderer"])


def export(project, workspace, output, base, phase, host):
    settings = project / "project.godot"
    presets = project / "export_presets.cfg"
    original = settings.read_text(encoding="utf-8")
    original_preset = presets.read_text(encoding="utf-8")
    study_settings = original.replace('run/main_scene="res://main.tscn"', 'run/main_scene="res://study/main.tscn"')
    study_settings = study_settings.replace('config/name="picross · P1"', 'config/name="picross · ZS-1"')
    if study_settings == original or 'run/main_scene="res://study/main.tscn"' not in study_settings:
        raise toolchain.PreflightError("Study entry point was not set")
    build = workspace / "zs1-windows"
    build.mkdir()
    try:
        settings.write_text(study_settings, encoding="utf-8")
        presets.write_text(original_preset.replace('tests/*,data/*proof*,study/*', 'tests/*,data/*proof*'), encoding="utf-8")
        phase("zs1-export-import", base + ["--import"])
        phase("zs1-separate-start", base + ["--", "--zs1-smoke"], "ZS1_STUDY_OK")
        phase("zs1-windows-export", base + ["--export-debug", "P1 Windows x86_64", str(build / "picross-zs1.exe")])
        if host == "Windows":
            phase("zs1-exported-start", [str(build / "picross-zs1.console.exe"), "--headless", "--", "--zs1-smoke"], "ZS1_STUDY_OK")
            phase("zs1-exported-gui-start", [str(build / "picross-zs1.console.exe"), "--rendering-driver", "opengl3", "--", "--zs1-smoke"], "ZS1_STUDY_OK")
    finally:
        settings.write_text(original, encoding="utf-8")
        presets.write_text(original_preset, encoding="utf-8")
    files = {p.name: toolchain.sha256_file(p) for p in build.iterdir() if p.is_file()}
    if set(files) != {"picross-zs1.exe", "picross-zs1.console.exe"}:
        raise toolchain.PreflightError("Incomplete/unexpected ZS1 export")
    return build, files


def package(root: Path, output: Path, build: Path, files: dict, product: dict, evidence: dict):
    manifest = {key: product[key] for key in ("source_commit", "source_tree_dirty", "tested_checkout_commit", "base_commit", "github_run_id", "host", "engine_version", "assets")}
    manifest.update(specification_commit="c82ae74f794936bca93d45f5f505ba283e971227",
                    export_files=files, evidence=evidence, owner_acceptance="OPEN ZS1-M01; independent review and merge authorization OPEN")
    renders = output / "zs1-renders"
    manifest["render_files"] = {p.name: toolchain.sha256_file(p) for p in sorted(renders.iterdir()) if p.is_file()}
    report = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (output / "zs1-report.json").write_text(report, encoding="utf-8")
    player = output / "picross-zs1-windows-x86_64.zip"
    with zipfile.ZipFile(player, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in files:
            bundle.write(build / name, name)
        bundle.writestr("README.txt", f"ZS-1 · Quellhead {manifest['source_commit']}\n\n" + (root / "docs/ZS1_OWNER_TRIAL.md").read_text(encoding="utf-8"))
        bundle.writestr("zs1-report.json", report)
        for path in (root / "prototypes/p1/art/book").glob("*-OFL.txt"):
            bundle.write(path, "licenses/" + path.name)
        bundle.write(root / "prototypes/p1/art/book/manifest.json", "licenses/resources.json")
    with zipfile.ZipFile(player) as bundle:
        for name, digest in files.items():
            import hashlib
            if hashlib.sha256(bundle.read(name)).hexdigest() != digest:
                raise toolchain.PreflightError("ZS1 player ZIP audit failed")
    review = output / "picross-zs1-review.zip"
    # Original-main renders remain temporary after the pixel comparison.
    # Ship the identical study baseline plus both styles, without duplicate PNGs.
    names = {item["file"] for item in json.loads((renders / "zs1-study.json").read_text(encoding="utf-8"))["captures"]}
    names.update(p.name for p in renders.glob("zs1-motion-*.png"))
    names.update(p.name for p in renders.glob("zs1-numerals-*.png"))
    names.update({"zs1-baseline.json", "zs1-study.json"})
    with zipfile.ZipFile(review, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in sorted(names):
            bundle.write(renders / name, name)
        bundle.writestr("zs1-report.json", report)
        bundle.write(root / "docs/ZS1_VERIFICATION.md", "PRUEFUNG.md")
        bundle.write(root / "docs/ZS1_DECISION.md", "ENTSCHEIDUNG.md")
        bundle.writestr("index.html", review_html(evidence))
    print(f"ZS1 PLAYER {player} sha256:{toolchain.sha256_file(player)}", flush=True)
    print(f"ZS1 REVIEW {review} sha256:{toolchain.sha256_file(review)}", flush=True)


def review_html(evidence: dict) -> str:
    sections = []
    for case in ("f01-work", "f02-color", "f03-small", "f02-compact", "f01-1600", "f01-z150", "f03-z300", "hint-row-drag", "hint-row-tooltip", "hint-column-drag", "hint-column-tooltip", "status-0", "status-1", "status-2"):
        sections.append(f"<h2>{case}</h2><div class='row'>" + "".join(
            f"<figure><figcaption>{label}</figcaption><a href='zs1-{style}-{case}.png'><img src='zs1-{style}-{case}.png'></a></figure>"
            for style, label in enumerate(("Baseline", "Tinte", "Stift"))) + "</div>")
    sections.append("<h2>Ziffernprobe (künstliche Schriftmuster)</h2>" + "".join(f"<figure><img src='zs1-numerals-{i}.png'></figure>" for i in range(3)))
    for motion in evidence["movements"]:
        sections.append(f"<h2>Bewegung Variante {motion['style']}</h2><p>Zweite Geste: {motion['second_gesture_ms']:.2f} ms nach Commit; native 1:1-Ausschnitte. Zeiten sind Messwerte, keine Einzelbild-FPS-Zusage.</p>")
        for frame in motion["timeline"]:
            sections.append(f"<figure><figcaption>{frame['label']} · {frame['after_commit_ms']:.2f} ms</figcaption><img src='{frame['file']}'></figure>")
    return "<!doctype html><html lang='de'><meta charset='utf-8'><title>ZS-1 · native Vergleiche</title><style>body{font:16px system-ui;background:#faf6ec;color:#343f42;margin:24px}.row{display:flex}figure{margin:8px}.row figure{width:32%}.row img{width:100%}img{max-width:100%}h2{margin-top:40px}</style><h1>ZS-1 · native Vergleiche</h1><p>PNG anklicken und bei 100 % betrachten. Diese Seite ist nur der Nachweisindex; die bedienbare Studie liegt im separaten Windows-ZIP. Eigentümerwahl offen.</p>" + "".join(sections) + "</html>"
