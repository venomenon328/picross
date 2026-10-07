"""Native main/delivery comparison and small, hash-bound GP-48 review artifact."""
from __future__ import annotations

import html
import io
import json
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import p1_preflight as toolchain

BASE = "add7a7e6aa507d54d6e0e2ac8a3a2c5e2d1d6912"


def before_project(root: Path, workspace: Path) -> Path:
    archive = subprocess.run(["git", "archive", BASE, "prototypes/p1"], cwd=root,
                             capture_output=True, check=True).stdout
    destination = workspace / "gp48-before"
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to("prototypes/p1")
            if ".." in relative.parts:
                raise toolchain.PreflightError("Unsafe GP comparison archive path")
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bundle.extractfile(member).read())
    shutil.copyfile(root / "prototypes/p1/tests/gp48_capture.gd",
                    destination / "tests/gp48_capture.gd")
    return destination


def verify_pairs(renders: Path) -> dict:
    reports = {variant: json.loads((renders / f"gp48-{variant}.json").read_text(encoding="utf-8"))
               for variant in ("before", "after")}
    pairs = []
    for before, after in zip(reports["before"]["captures"], reports["after"]["captures"], strict=True):
        expected_fixture = "F-0" + after["case"][1]
        if after["fixture"] != expected_fixture or before["fixture"] != expected_fixture:
            raise toolchain.PreflightError("GP comparison captured the wrong sheet")
        if after["case"].endswith("-drag"):
            axis = after["case"].split("-")[-2]
            if any(record["pan_target"] != axis for record in (before, after)):
                raise toolchain.PreflightError("GP comparison did not capture the intended drag")
        for key in ("case", "fixture", "size", "ui_scale", "cells_sha256", "view", "font_size", "pan_target", "tooltip"):
            if before[key] != after[key]:
                raise toolchain.PreflightError(f"GP comparison {after['case']}: mismatched {key}")
        for record in (before, after):
            if not (renders / record["file"]).is_file():
                raise toolchain.PreflightError("Missing native GP image")
        pairs.append(dict(case=after["case"], before=before["file"], after=after["file"],
                          cells_sha256=after["cells_sha256"], states=after["states"]))
    if len(pairs) != 40:
        raise toolchain.PreflightError(f"Expected 40 GP pairs, got {len(pairs)}")
    for dims, scale in ((1920, 100), (1280, 125)):
        changes = [next(c for c in reports["after"]["captures"]
                        if c["case"] == f"f1-{dims}-ui{scale}-status{state}") for state in range(3)]
        if [c["focus_states"] for c in changes] != [[0], [1], [2]]:
            raise toolchain.PreflightError("GP comparison missed a clue status")
        if any(c["row3_units"] != changes[0]["row3_units"] or c["font_size"] != changes[0]["font_size"]
               for c in changes):
            raise toolchain.PreflightError("A GP status transition moved or resized a clue")
    return dict(comparison_commit=BASE, pairs=pairs, native_reports=reports)


def package(root: Path, output: Path, manifest: dict, windows_zip: Path) -> Path:
    renders = output / "renders"
    comparison = verify_pairs(renders)
    paths = sorted(renders.glob("gp48-*.png")) + sorted(renders.glob("gp48-*.json"))
    binding = {key: manifest[key] for key in ("source_commit", "source_tree_dirty", "base_commit",
                                             "tested_checkout_commit", "github_run_id", "host", "export_files")}
    binding.update(comparison_commit=BASE, windows_zip_sha256=toolchain.sha256_file(windows_zip),
                   files={p.name: toolchain.sha256_file(p) for p in paths}, comparison=comparison,
                   independent_review="GP48 R1 PASSED on 1127b22; combined PR47 review OPEN",
                   owner_trial="GP48-M01 PASSED on 1127b22")
    archive = output / "picross-gp48-review.zip"
    index = ['<!doctype html><html lang="de"><meta charset="utf-8"><title>GP-48 – native Vergleiche</title>',
             '<style>body{font:16px sans-serif;background:#faf6ec;margin:24px;color:#293e3d}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{width:100%}code{overflow-wrap:anywhere}</style>',
             '<h1>GP-48 – native Godot-Vergleiche</h1>',
             '<p>Links Main ' + BASE + '; rechts Lieferhead <code>' + html.escape(manifest["source_commit"]) + '</code>. Identische Spielerzellen, Ansicht und Eingaben; unveränderte native PNGs. Für 1:1-Prüfung Bild öffnen. Technische Bildstände, keine Eigentümerabnahme.</p>']
    for pair in comparison["pairs"]:
        index.append('<h2>' + html.escape(pair["case"]) + '</h2><div class="pair">')
        for key in ("before", "after"):
            name = html.escape(pair[key])
            index.append(f'<a href="renders/{name}"><img loading="lazy" src="renders/{name}" alt="{name}"></a>')
        index.append('</div>')
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("index.html", "\n".join(index) + "\n</html>\n")
        bundle.writestr("report.json", json.dumps(binding, ensure_ascii=False, indent=2) + "\n")
        bundle.write(root / "docs/GP48_VERIFICATION.md", "GP48-PRUEFUNG.md")
        for path in paths:
            bundle.write(path, "renders/" + path.name)
    return archive
