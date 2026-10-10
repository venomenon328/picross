"""Native current-main/delivery comparison for Issue #50 zoom workspace."""
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
    archive = subprocess.run(
        ["git", "archive", BASE, "prototypes/p1"],
        cwd=root, capture_output=True, check=True,
    ).stdout
    destination = workspace / "zv50-before"
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to("prototypes/p1")
            if ".." in relative.parts:
                raise toolchain.PreflightError("Unsafe ZV50 comparison archive path")
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bundle.extractfile(member).read())
    shutil.copyfile(
        root / "prototypes/p1/tests/zv50_capture.gd",
        destination / "tests/zv50_capture.gd",
    )
    shutil.copyfile(root / "prototypes/p1/tests/vs2_measurements.gd",
                    destination / "tests/vs2_measurements.gd")
    return destination


def _by_case(report: dict) -> dict[str, dict]:
    return {record["case"]: record for record in report["captures"]}


def verify_pairs(renders: Path) -> dict:
    reports = {
        variant: json.loads((renders / f"zv50-{variant}.json").read_text(encoding="utf-8"))
        for variant in ("before", "after")
    }
    before = _by_case(reports["before"])
    after = _by_case(reports["after"])
    if set(before) != set(after) or len(after) != 8:
        raise toolchain.PreflightError("Unexpected ZV50 capture matrix")
    if after and "full_view" in next(iter(after.values())):
        return verify_full_view(renders,before,after,reports)
    pairs = []
    for case in after:
        old, new = before[case], after[case]
        for key in ("case", "fixture", "size", "ui_scale", "pitch", "cells_sha256"):
            if old[key] != new[key]:
                raise toolchain.PreflightError(f"ZV50 {case}: mismatched {key}")
        for record in (old, new):
            if not (renders / record["file"]).is_file():
                raise toolchain.PreflightError("Missing native ZV50 image")
            if record["grid"][1] + record["grid"][3] > record["tools_top"] - 3:
                raise toolchain.PreflightError(f"ZV50 {case}: grid overlaps tools")
        pairs.append(
            dict(
                case=case,
                before=old["file"],
                after=new["file"],
                before_grid=old["grid"],
                after_grid=new["grid"],
                before_viewport=old["viewport"],
                after_viewport=new["viewport"],
                before_visible_cells=old["visible_cells"],
                after_visible_cells=new["visible_cells"],
                full_before=old["full_grid"],
                full_after=new["full_grid"],
            )
        )
    for case, expected in (
        ("f04-1920-ui100-z133", 640.0),
        ("f04-1920-ui100-z150", 720.0),
    ):
        if not after[case]["full_grid"] or min(after[case]["grid"][2:]) < expected - 0.1:
            raise toolchain.PreflightError(
                f"ZV50 {case}: delivery does not keep the full grid visible"
            )
        if before[case]["full_grid"]:
            raise toolchain.PreflightError(
                f"ZV50 {case}: baseline unexpectedly already full"
            )
    standard = "f04-1920-ui100-z100"
    if (
        before[standard]["grid"] != after[standard]["grid"]
        or before[standard]["viewport"] != after[standard]["viewport"]
    ):
        raise toolchain.PreflightError("ZV50 standard 100% geometry changed")
    overflow = after["f04-1920-ui100-z167"]
    if (
        overflow["full_grid"]
        or overflow["grid"][2] < 799.9
        or overflow["grid"][3] >= 799.9
    ):
        raise toolchain.PreflightError(
            "ZV50 167% case does not demonstrate the first tested vertical overflow"
        )
    if (
        after["f02-1920-ui100-z100"]["viewport"]
        != before["f02-1920-ui100-z100"]["viewport"]
    ):
        raise toolchain.PreflightError("ZV50 F02 100% historical viewport changed")
    if (
        after["f02-1920-ui100-z108"]["viewport"][2]
        <= before["f02-1920-ui100-z108"]["viewport"][2]
    ):
        raise toolchain.PreflightError(
            "ZV50 F02 zoom did not gain horizontal workspace"
        )
    if (
        after["f03-1920-ui100-z100"]["viewport"]
        != before["f03-1920-ui100-z100"]["viewport"]
    ):
        raise toolchain.PreflightError("ZV50 F03 reference viewport changed")
    return dict(comparison_commit=BASE, pairs=pairs, native_reports=reports)


def package(root: Path, output: Path, manifest: dict, windows_zip: Path) -> Path:
    renders = output / "renders"
    comparison = verify_pairs(renders)
    paths = sorted(renders.glob("zv50-*.png")) + sorted(renders.glob("zv50-*.json"))
    binding = {
        key: manifest[key]
        for key in (
            "source_commit", "source_tree_dirty", "base_commit",
            "tested_checkout_commit", "github_run_id", "host", "export_files",
        )
    }
    binding.update(
        comparison_commit=BASE,
        windows_zip_sha256=toolchain.sha256_file(windows_zip),
        files={p.name: toolchain.sha256_file(p) for p in paths},
        comparison=comparison,
        owner_trial=(
            "NOT PERFORMED; owner explicitly waived this gate "
            "for the requested #50 merge"
        ),
        independent_review=(
            "NOT PERFORMED; owner explicitly waived this gate "
            "for the requested #50 merge"
        ),
    )
    archive = output / "picross-zv50-review.zip"
    index = [
        '<!doctype html><html lang="de"><meta charset="utf-8">'
        '<title>ZV-50 – Zoom-Arbeitsfläche</title>',
        '<style>body{font:16px sans-serif;background:#faf6ec;margin:24px;'
        'color:#293e3d}.pair{display:grid;grid-template-columns:1fr 1fr;'
        'gap:12px}img{width:100%}code{overflow-wrap:anywhere}</style>',
        "<h1>ZV-50 – native Godot-Vergleiche</h1>",
        "<p>Links Main <code>" + BASE + "</code>; rechts Lieferhead <code>"
        + html.escape(manifest["source_commit"])
        + "</code>. Identische Zellen, Zielzooms, Clientflächen und UI-Skalen; "
        "die Rastergeometrie darf sich genau gemäß #50 unterscheiden.</p>",
    ]
    for pair in comparison["pairs"]:
        index.append("<h2>" + html.escape(pair["case"]) + '</h2><div class="pair">')
        for key in ("before", "after"):
            name = html.escape(pair[key])
            index.append(
                f'<a href="renders/{name}"><img loading="lazy" '
                f'src="renders/{name}" alt="{name}"></a>'
            )
        index.append("</div>")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("index.html", "\n".join(index) + "\n</html>\n")
        bundle.writestr(
            "report.json",
            json.dumps(binding, ensure_ascii=False, indent=2) + "\n",
        )
        bundle.write(root / "docs/ZV50_VERIFICATION.md", "ZV50-PRUEFUNG.md")
        for path in paths:
            bundle.write(path, "renders/" + path.name)
    return archive


def verify_full_view(renders,before,after,reports):
    pairs=[]
    for case,new in after.items():
        old=before[case]
        for key in ('case','fixture','size','ui_scale','cells_sha256'):
            if old[key]!=new[key]: raise toolchain.PreflightError('ZV50/VS2 changed '+key)
        if new['full_view']['layout_valid'] and not new['full_grid']:
            raise toolchain.PreflightError('VS2 must replace old ZV50 clipping by full grid')
        if new['grid'][1]+new['grid'][3]>new['tools_top']-3:
            raise toolchain.PreflightError('VS2 grid overlaps tools')
        for r in (old,new):
            if not (renders/r['file']).is_file(): raise toolchain.PreflightError('Missing ZV50 native image')
        pairs.append(dict(case=case,before=old['file'],after=new['file'],before_grid=old['grid'],after_grid=new['grid'],full_before=old['full_grid'],full_after=new['full_grid']))
    return dict(comparison_commit=BASE,pairs=pairs,native_reports=reports,contract='VS2 supersedes fixed standard box and allowed 167% clipping; whole frame fits at every offered scale')
