"""Bind native Z2 evidence, original P1 comparison and the regular export."""
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

BASE = "c3a5386580d7a0da29b927b41bd692f0cca59274"


def before_project(root: Path, workspace: Path) -> Path:
    archive = subprocess.run(["git", "archive", BASE, "prototypes/p1"], cwd=root,
                             capture_output=True, check=True).stdout
    destination = workspace / "before"
    # Extract only regular project files; no archive paths outside this subtree.
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle.getmembers():
            if member.isfile():
                relative = Path(member.name).relative_to("prototypes/p1")
                if ".." in relative.parts:
                    raise toolchain.PreflightError("Unsafe baseline archive path")
                path = destination / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(bundle.extractfile(member).read())
    for name in ("z2_before_capture.gd", "z2-demo.json"):
        shutil.copyfile(root / "prototypes/p1/tests" / name, destination / "tests" / name)
    return destination


def package(root: Path, output: Path, manifest: dict, windows_zip: Path) -> Path:
    renders = output / "renders"
    paths = sorted(renders.glob("z2-*.png")) + sorted(renders.glob("z2-*.json"))
    binding = dict(source_commit=manifest["source_commit"],
                   tested_checkout_commit=manifest["tested_checkout_commit"],
                   source_tree_dirty=manifest["source_tree_dirty"],
                   base_commit=manifest["base_commit"], comparison_commit=BASE,
                   github_run_id=manifest["github_run_id"], host=manifest["host"],
                   windows_zip=dict(file=windows_zip.name, sha256=toolchain.sha256_file(windows_zip)),
                   book_resources=manifest["book_resources"],
                   images={p.name: toolchain.sha256_file(p) for p in paths},
                   owner_acceptance="OPEN: Z2-M01/M02/M03; independent review also required before merge")
    index = ['<!doctype html><html lang="de"><meta charset="utf-8"><title>Z2 – native Godot-Nachweise</title>',
             '<style>body{font:16px sans-serif;max-width:1200px;margin:40px auto;background:#faf6ed;color:#293e3d}img{max-width:100%;height:auto}figure{margin:32px 0}code{overflow-wrap:anywhere}</style>',
             '<h1>Z2 – native Godot-Nachweise</h1>',
             '<p>PNG-Dateien sind unveränderte Godot-Render oder ausdrücklich bezeichnete 1:1-Ausschnitte. Für Pixelprüfung die Bilddatei in Originalgröße öffnen.</p>',
             '<p>Vorher: regulärer P1 auf ' + BASE + '. Gleiche Fixtures, z1-demo-1-Zellen, Fenster, UI-Skala und gesetzter Zellmaßstab; Anordnung und sichtbarer Ausschnitt sind das Ergebnis des jeweiligen Layouts. Keine Browsermontage.</p>',
             '<p>Quellhead: <code>' + html.escape(manifest["source_commit"]) + '</code>; Windows-ZIP SHA-256: <code>' + binding["windows_zip"]["sha256"] + '</code>.</p>',
             '<p>Eigentümerprobe und unabhängige Abnahme offen. Details und Grenzen: Z2-PRUEFUNG.md; genaue Hashbindung: z2-binding.json.</p>']
    for path in paths:
        if path.suffix == ".png":
            name = html.escape(path.name)
            index.append(f'<figure><figcaption>{name}</figcaption><a href="renders/{name}"><img loading="lazy" src="renders/{name}" alt="{name}"></a></figure>')
    index.append('</html>')
    (output / "z2-binding.json").write_text(json.dumps(binding, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = output / "picross-z2-review.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("index.html", "\n".join(index))
        bundle.write(output / "z2-binding.json", "z2-binding.json")
        bundle.write(root / "docs/Z2_VERIFICATION.md", "Z2-PRUEFUNG.md")
        for path in paths:
            bundle.write(path, "renders/" + path.name)
    return archive
