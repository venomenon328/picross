"""Regular ZS-2 integration: pinned native comparisons and separate movement evidence."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import p1_preflight as toolchain
import zs1_delivery

BASE = "985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f"
FONT_SHA256 = "163d5acb0c4cc2f54a603501836fda2dcdd1d09579a8d1f790ab882d86175c4d"


def before_project(root: Path, workspace: Path) -> Path:
    raw = subprocess.run(["git", "archive", BASE, "prototypes/p1"], cwd=root,
                         capture_output=True, check=True).stdout
    destination = workspace / "zs2-before"
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to("prototypes/p1")
            if ".." in relative.parts or relative.is_absolute():
                raise toolchain.PreflightError("Unsafe ZS2 comparison path")
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.extractfile(member).read())
    for name in ("zs1_capture.gd", "zs2_capture.gd"):
        shutil.copyfile(root / "prototypes/p1/tests" / name, destination / "tests" / name)
    return destination


def capture(root, project, workspace, output, engine, render_command, environment, phase):
    font = root / "prototypes/p1/art/drawing/Chalkboard-Regular.ttf"
    if toolchain.sha256_file(font) != FONT_SHA256 or font.read_bytes() != (root / "prototypes/p1/study/fonts/Chalkboard-Regular.ttf").read_bytes():
        raise toolchain.PreflightError("Selected font differs from the bound ZS1 original")
    renders = output / "zs2-renders"
    renders.mkdir()
    old = environment["P1_CAPTURE_DIR"]
    environment["P1_CAPTURE_DIR"] = str(renders)
    command = ["res://tests/zs2_capture.gd" if part == "res://tests/capture.gd" else part for part in render_command]
    try:
        phase("zs2-regular-tests", [engine, "--headless", "--path", str(project), "--script",
                                   "res://tests/zs2_tests.gd", "--", "--p1-capture"], "ZS2_TESTS_OK")
        environment["ZS2_VARIANT"] = "after"
        phase("zs2-regular-capture", command, "ZS2_CAPTURE_OK")
        before = before_project(root, workspace)
        phase("zs2-reference-import", [engine, "--headless", "--path", str(before), "--import"])
        for role in ("before", "study"):
            environment["ZS2_VARIANT"] = role
            phase("zs2-" + role + "-capture", [str(before) if part == str(project) else part for part in command], "ZS2_CAPTURE_OK")
    finally:
        environment.pop("ZS2_VARIANT", None)
        environment["P1_CAPTURE_DIR"] = old
    return verify(renders)


def verify(renders: Path) -> dict:
    from PIL import Image, ImageChops
    reports = {role: json.loads((renders / f"zs2-{role}.json").read_text(encoding="utf-8"))
               for role in ("before", "study", "after")}
    if any(report["failures"] or len(report["captures"]) != 16 for report in reports.values()):
        raise toolchain.PreflightError("Incomplete/failed ZS2 native matrix")
    pairs = []
    for old, chosen, new in zip(*(reports[role]["captures"] for role in ("before", "study", "after")), strict=True):
        for key in ("case", "fixture", "size", "ui_scale", "cells_sha256", "board", "grid", "viewport", "pan_target", "tooltip"):
            if old[key] != new[key] or chosen[key] != new[key]:
                raise toolchain.PreflightError(f"ZS2 {new['case']}: changed {key}")
        for key in ("view", "font_size", "font", "font_metrics"):
            if chosen[key] != new[key]:
                raise toolchain.PreflightError(f"ZS2 selected study differs in {key}")
        # Compact row slots intentionally alter the snap from the same physical
        # drag; all other semantic navigation and grid fields remain identical.
        for key in old["view"]:
            if key == "row_clue_reads" and new["case"] in {"hint-row-tooltip", "hint-column-drag", "hint-column-tooltip"}:
                continue
            if old["view"][key] != new["view"][key]:
                raise toolchain.PreflightError(f"ZS2 baseline changed view/{key}")
        if new["font"] != "Chalkboard" or not all(r["spoiler_free"] for r in (old, chosen, new)):
            raise toolchain.PreflightError("ZS2 font/spoiler contract")
        x, y, w, h = new["board"]
        bounds = (int(x), int(y), int(x+w), int(y+h))
        with Image.open(renders / chosen["file"]) as a, Image.open(renders / new["file"]) as b, Image.open(renders / old["file"]) as c:
            if a.size != b.size or b.size != c.size:
                raise toolchain.PreflightError("ZS2 capture dimensions differ")
            if ImageChops.difference(a.crop(bounds).convert("RGB"), b.crop(bounds).convert("RGB")).getbbox():
                raise toolchain.PreflightError(f"ZS2 selected board pixels differ: {new['case']}")
            if not ImageChops.difference(c.crop(bounds).convert("RGB"), b.crop(bounds).convert("RGB")).getbbox():
                raise toolchain.PreflightError("ZS2 regular rendering was not integrated")
        pairs.append({"case": new["case"], "before": old["file"], "study": chosen["file"], "after": new["file"]})
    current = reports["after"]
    if len(current["frames"]) != 1 or {m["fixture"] for m in current["measurements"]} != {"F-03", "F-07"}:
        raise toolchain.PreflightError("Missing ZS2 motion/large color load")
    for motion in current["frames"]:
        if not (motion["preview_static"] and motion["off_same_end"] and motion["second_gesture_ms"] < 140):
            raise toolchain.PreflightError("ZS2 real-time motion failed")
        early = next(f for f in motion["timeline"] if f["label"] == "parallel-commit-0")
        final = next(f for f in motion["timeline"] if f["label"] == "settled")
        if not 0 < early["after_commit_ms"] < 140:
            raise toolchain.PreflightError("ZS2 missed live commit effect")
        with Image.open(renders / early["file"]) as a, Image.open(renders / final["file"]) as b:
            if not ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox():
                raise toolchain.PreflightError("ZS2 live effect is invisible")
    strokes = zs1_delivery.verify_strokes(renders, current["stroke_frames"])
    return dict(reference_commit=BASE, font_sha256=FONT_SHA256, pairs=pairs,
                identical_selected_boards=len(pairs), movements=current["frames"], stroke_evidence=strokes,
                measurements=current["measurements"], renderer=current["renderer"])


def package(root: Path, output: Path, product: dict, evidence: dict):
    renders = output / "zs2-renders"
    report = {key: product[key] for key in ("source_commit", "source_tree_dirty", "base_commit", "tested_checkout_commit", "github_run_id", "host", "engine_version", "export_files")}
    report.update(evidence=evidence, files={p.name: toolchain.sha256_file(p) for p in sorted(renders.iterdir()) if p.is_file()},
                  owner_trial="OPEN ZS2-M01", independent_review="OPEN", merge_authorized=False)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    (output / "zs2-report.json").write_text(text, encoding="utf-8")
    names = {pair[key] for pair in evidence["pairs"] for key in ("before", "study", "after")}
    names.update({"zs2-numerals.png", "zs2-before.json", "zs2-study.json", "zs2-after.json"})
    for kind, files in (("review", names), ("strokes", {p.name for p in renders.glob("zs1-motion-*.png")} | {p.name for p in renders.glob("zs1-strokes-*.png")})):
        archive = output / f"picross-zs2-{kind}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name in sorted(files):
                bundle.write(renders / name, name)
            bundle.writestr("zs2-report.json", text)
            bundle.write(root / "docs/ZS2_VERIFICATION.md", "PRUEFUNG.md")
            if kind == "strokes":
                index = zs1_delivery.movement_html(evidence).replace("ZS-1", "ZS-2")
            else:
                sections = ["<p>Jeweils vorherige reguläre Ansicht, gewählte isolierte Studie, neue reguläre Ansicht. Identische eigene Zellen und Eingaben; PNG bei 100 % prüfen.</p>"]
                for pair in evidence["pairs"]:
                    sections.append("<h2>" + pair["case"] + "</h2><div class='row'>" + "".join(f"<figure><figcaption>{key}</figcaption><a href='{pair[key]}'><img src='{pair[key]}'></a></figure>" for key in ("before", "study", "after")) + "</div>")
                sections.append("<h2>Reguläre Ziffernprobe</h2><img src='zs2-numerals.png'>")
                index = zs1_delivery.html_page("Reguläre Integration", sections).replace("ZS-1", "ZS-2")
            bundle.writestr("index.html", index)
        print(f"ZS2 {kind.upper()} {archive} sha256:{toolchain.sha256_file(archive)}", flush=True)
