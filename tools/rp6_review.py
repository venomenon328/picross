"""Small RP-6 review artifact; keeps motif spoilers outside the player ZIP."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from p1_preflight import PreflightError, sha256_file


def package(root: Path, output: Path, product: dict, archive: Path) -> Path:
    destination = output / "rp6-review"
    destination.mkdir()
    sources = [root / "examples/rp6/plan.json", root / "examples/rp6/manifest.json",
               root / "examples/rp6/README.md", root / "docs/RP6_VERIFICATION.md",
               root / "examples/rp6/effort.json",
               root / "docs/RP6_OWNER_TRIAL.md", root / "examples/rp6/owner-protocol.json"]
    sources += sorted((root / "examples/rp6/views").glob("*"))
    sources += sorted((root / "examples/rp6/artwork").glob("*"))
    pilot = json.loads((root / "examples/rp6/manifest.json").read_text(encoding="utf-8"))
    for entry in pilot["entries"]:
        sources += [root / entry["asset"], root / entry["definition"], root / entry["export_manifest"]]
    for source in set(sources):
        path = destination / source.relative_to(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
    render_files = sorted((output / "renders").glob("rp6-*"))
    if len([p for p in render_files if p.suffix == ".png"]) != 60:
        raise PreflightError("RP-6 requires ten native captures for each of six pilots")
    (destination / "renders").mkdir()
    for source in render_files:
        shutil.copyfile(source, destination / "renders" / source.name)
    shutil.copyfile(output / "rp6/verification.json", destination / "verification.json")
    shutil.copyfile(output / "product-report.json", destination / "product-report.json")
    (destination / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>RP-6 Review · Motivspoiler</title>'
        '<h1>RP-6 Review · Motivspoiler</h1><p>Eigene Sichturteile und technische Belege; '
        'unabhängiges Review, Eigentümerproben und Phasenentscheidung offen.</p>'
        '<p><a href="examples/rp6/manifest.json">Pilotmanifest</a> · '
        '<a href="product-report.json">Produktreport</a> · '
        '<a href="report.json">Commit-/ZIP-/Dateihashes</a></p>' +
        ''.join(f'<p><a href="{e["pair_view"]}">{e["definition_id"]} Raster/Reveal</a></p>' for e in pilot["entries"]) +
        ''.join(f'<p><a href="renders/{p.name}">{p.name}</a></p>' for p in render_files), encoding="utf-8")
    report = {key: product[key] for key in ("source_commit", "source_tree_dirty", "tested_checkout_commit", "base_commit", "github_run_id", "export_files", "checks", "manual_acceptance")}
    report.update(windows_zip=archive.name, windows_zip_sha256=sha256_file(archive),
                  pilot_manifest_sha256=sha256_file(root / "examples/rp6/manifest.json"),
                  files={p.relative_to(destination).as_posix(): sha256_file(p) for p in sorted(destination.rglob("*")) if p.is_file()})
    (destination / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    return destination
