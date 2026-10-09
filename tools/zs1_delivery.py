"""Small native ZS-1 delivery; separate player, comparison and stroke ZIPs."""
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
        for key in ("fixture", "size", "ui_scale", "cells_sha256", "board", "grid", "viewport", "pan_target", "tooltip"):
            if old[key] != record[key]:
                raise toolchain.PreflightError(f"ZS1 {record['case']}: changed {key}")
        if old["view"] != record["view"]:
            # E3/N07 deliberately changes only the horizontal row-clue slot pitch.
            # The same physical drag can therefore snap to another valid semantic
            # row read. All cell-view fields and the untouched column reads must
            # remain identical; no other capture may change its semantic view.
            e3_row_snap = record["font_choice"] == 2 and record["case"] in {
                "hint-row-tooltip", "hint-column-drag", "hint-column-tooltip"
            }
            if not e3_row_snap:
                raise toolchain.PreflightError(f"ZS1 {record['case']}: changed view")
            for view_key in ("center", "zoom", "overview", "active_color", "tool", "column_clue_reads"):
                if old["view"][view_key] != record["view"][view_key]:
                    raise toolchain.PreflightError(f"ZS1 {record['case']}: changed view/{view_key}")
            if old["view"]["row_clue_reads"] == record["view"]["row_clue_reads"]:
                raise toolchain.PreflightError("ZS1 N07 row drag did not exercise compact-slot snap")
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
    candidates = {(item["font_choice"], item["case"]): item for item in study["captures"]}
    for case in baseline:
        first, second = candidates[1, case], candidates[2, case]
        with Image.open(renders / first["file"]) as a, Image.open(renders / second["file"]) as b:
            x, y, w, h = first["grid"]
            box = (int(x), int(y), int(x+w), int(y+h))
            if not case.endswith("tooltip") and ImageChops.difference(a.crop(box).convert("RGB"), b.crop(box).convert("RGB")).getbbox():
                raise toolchain.PreflightError(f"ZS1 fonts changed cell rendering: {case}")
            x, y, w, h = first["board"]
            box = (int(x), int(y), int(x+w), int(y+h))
            if not ImageChops.difference(a.crop(box).convert("RGB"), b.crop(box).convert("RGB")).getbbox():
                raise toolchain.PreflightError(f"ZS1 fonts produced identical clue pixels: {case}")
    if len(study["frames"]) != 1 or len(study["measurements"]) != 1:
        raise toolchain.PreflightError("Missing ZS1 movement/load evidence")
    if {item["font_choice"] for item in study["specimens"]} != {0, 1, 2}:
        raise toolchain.PreflightError("Missing ZS1 native numeral specimen")
    expected = {1: ("Bakso Daging", "56372bf12a6e4fa47a655ff9b2c4cc73172ddd387b3a047093d3e637d081790e", ["…", "–"]),
                2: ("Chalkboard", "163d5acb0c4cc2f54a603501836fda2dcdd1d09579a8d1f790ab882d86175c4d", ["…", "–"])}
    for specimen in study["specimens"]:
        if specimen["font_choice"]:
            family, digest, fallback = expected[specimen["font_choice"]]
            font = specimen["font"]
            if (font["family"], font["sha256"], font["plex_punctuation"], font["digits_native"]) != (family, digest, fallback, True):
                raise toolchain.PreflightError("ZS1 actual native candidate identity/fallback mismatch")
    for specimen in study["specimens"]:
        if not (renders / specimen["file"]).is_file():
            raise toolchain.PreflightError("Missing ZS1 specimen image")
    for motion in study["frames"]:
        if not (motion["preview_static"] and motion["off_same_end"] and motion["second_gesture_ms"] < 210):
            raise toolchain.PreflightError("ZS1 movement contract failed")
        for frame in motion["timeline"]:
            if not (renders / frame["file"]).is_file():
                raise toolchain.PreflightError("Missing ZS1 timed frame")
        early = next(frame for frame in motion["timeline"] if frame["label"] == "parallel-commit-0")
        settled = next(frame for frame in motion["timeline"] if frame["label"] == "settled")
        if not 0 < early["after_commit_ms"] < 210:
            raise toolchain.PreflightError("ZS1 renderer missed the actual commit effect")
        with Image.open(renders / early["file"]) as a, Image.open(renders / settled["file"]) as b:
            if not ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox():
                raise toolchain.PreflightError("ZS1 native commit effect is not visible")
    stroke_evidence = verify_strokes(renders, study["stroke_frames"])
    return dict(baseline=BASE, identical_regular_board_cases=len(baseline),
                comparison_images=len(study["captures"]), identical_candidate_grid_cases=12, distinct_candidate_clue_cases=14, movements=study["frames"],
                stroke_evidence=stroke_evidence, font_comparison=study["specimens"],
                measurements=study["measurements"], renderer=study["renderer"])


def check_stroke_pixels(images):
    """Independent spatial oracle on native pixels; no renderer geometry imports."""
    def distance(a, b):
        return max(abs(x-y) for x, y in zip(a, b))

    preview, final = images[0], images[210]
    import zs_hatching
    fills = {ms: picture.crop((0, 0, 72, 72)) for ms, picture in images.items()}
    zs_hatching.check_hatching(fills, fills[0], 72)
    zs_hatching.negative_controls(fills, fills[0], 72)
    # Upper-left X quadrant belongs only to stroke 1; upper-right only to 2.
    fractions = {}
    for name, bounds in (("first", (87, 13, 104, 30)), ("second", (115, 13, 132, 29))):
        x0, y0, x1, y1 = bounds
        pixels = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
                  if distance(preview.getpixel((x, y)), final.getpixel((x, y))) > 20]
        if len(pixels) < 8:
            raise toolchain.PreflightError("ZS1 X evidence contains too few stroke pixels")
        fractions[name] = {}
        for ms in (30, 75, 105, 150, 180):
            fractions[name][ms] = sum(distance(images[ms].getpixel(p), final.getpixel(p)) < 6 for p in pixels) / len(pixels)
        if name == "first" and fractions[name][105] < 0.90:
            raise toolchain.PreflightError("ZS1 first X stroke incomplete at 105ms")
        if name == "second" and (fractions[name][105] > 0.05 or fractions[name][180] < 0.9):
            raise toolchain.PreflightError("ZS1 second X stroke must follow the first")
    return fractions


def verify_strokes(renders: Path, records: list) -> dict:
    from PIL import Image
    if [item["elapsed_ms"] for item in records] != [0, 30, 75, 105, 150, 180, 210]:
        raise toolchain.PreflightError("ZS1 stroke timeline incomplete")
    images = {}
    for item in records:
        with Image.open(renders / item["file"]) as picture:
            images[item["elapsed_ms"]] = picture.convert("RGB")
        if images[item["elapsed_ms"]].size != (144, 72):
            raise toolchain.PreflightError("ZS1 stroke crop changed")
    fractions = check_stroke_pixels(images)
    # Mutate actual evidence: both a uniform fade and reverse stroke order must fail.
    fade = {ms: Image.blend(images[0], images[210], ms / 210) for ms in images}
    reverse = dict(images)
    reverse[105] = images[105].copy()
    reverse[105].paste(images[0].crop((87, 13, 104, 30)), (87, 13))
    reverse[105].paste(images[210].crop((115, 13, 132, 29)), (115, 13))
    for label, mutant in (("uniform fade", fade), ("reversed X strokes", reverse)):
        try:
            check_stroke_pixels(mutant)
        except toolchain.PreflightError:
            continue
        raise toolchain.PreflightError(f"ZS1 negative control accepted {label}")
    return dict(frames=records, x_progress=fractions, negative_controls=["uniform fade rejected", "reversed X strokes rejected"],
                timing="Controlled clock through real native renderer; separate real-time sequence measures wall time")


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
                    owner_decision="https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659",
                    font_owner_decision="https://github.com/venomenon328/picross/pull/55#issuecomment-6042067344",
                    font_input=json.loads((root / "docs/zs1-font-input.json").read_text(encoding="utf-8")),
                    export_files=files, evidence=evidence, owner_acceptance="ZS1-M01 PASSED after PR55 merge 985cf08e; current ZS2-M01 and independent review OPEN")
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
        bundle.write(root / "docs/ZS1_FONT_INPUT.md", "FONTSTATUS.md")
        bundle.write(root / "prototypes/p1/study/fonts/NOTICES.md", "licenses/study-fonts-NOTICES.md")
    with zipfile.ZipFile(player) as bundle:
        for name, digest in files.items():
            import hashlib
            if hashlib.sha256(bundle.read(name)).hexdigest() != digest:
                raise toolchain.PreflightError("ZS1 player ZIP audit failed")
    review = output / "picross-zs1-review.zip"
    # Original-main renders remain temporary after the pixel comparison.
    # Ship the identical study baseline and selected pencil, without duplicate PNGs.
    names = {item["file"] for item in json.loads((renders / "zs1-study.json").read_text(encoding="utf-8"))["captures"]}
    names.update(p.name for p in renders.glob("zs1-numerals-*.png"))
    names.update({"zs1-baseline.json", "zs1-study.json"})
    with zipfile.ZipFile(review, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in sorted(names):
            bundle.write(renders / name, name)
        bundle.writestr("zs1-report.json", report)
        bundle.write(root / "docs/ZS1_VERIFICATION.md", "PRUEFUNG.md")
        bundle.write(root / "docs/ZS1_DECISION.md", "ENTSCHEIDUNG.md")
        bundle.writestr("index.html", review_html(evidence))
    movement = output / "picross-zs1-strokes.zip"
    with zipfile.ZipFile(movement, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for pattern in ("zs1-motion-*.png", "zs1-strokes-*.png"):
            for path in sorted(renders.glob(pattern)):
                bundle.write(path, path.name)
        bundle.writestr("zs1-report.json", report)
        bundle.writestr("index.html", movement_html(evidence))
    print(f"ZS1 PLAYER {player} sha256:{toolchain.sha256_file(player)}", flush=True)
    print(f"ZS1 REVIEW {review} sha256:{toolchain.sha256_file(review)}", flush=True)
    print(f"ZS1 STROKES {movement} sha256:{toolchain.sha256_file(movement)}", flush=True)


def review_html(evidence: dict) -> str:
    sections = []
    for case in ("f01-work", "f02-color", "f03-small", "f02-compact", "f01-1600", "f01-z150", "f03-z300", "hint-row-drag", "hint-row-tooltip", "hint-column-drag", "hint-column-tooltip", "status-0", "status-1", "status-2"):
        sections.append(f"<h2>{case}</h2><div class='row'>" + "".join(
            f"<figure><figcaption>{label}</figcaption><a href='zs1-{style}-{case}.png'><img src='zs1-{style}-{case}.png'></a></figure>"
            for style, label in ((0, "Bisherige Baseline · Plex"), (1, "Stift / neues X · Bakso Daging"), (2, "Stift / neues X · Chalkboard"))) + "</div>")
    sections.append("<h2>Ziffernproben: Plex-Referenz, Bakso Daging, Chalkboard</h2>" + "".join(f"<figure><img src='zs1-numerals-{i}.png'></figure>" for i in (0, 1, 2)))
    return html_page("Native Vergleiche · zwei Eigentümerfonts", sections)


def movement_html(evidence: dict) -> str:
    sections = ["<p>Native 72-px-Zellen: links Füllung, rechts X. Kontrollierte Effektuhr im unveränderten Zeichenpfad; keine Messung realer Framezeiten.</p>"]
    for frame in evidence["stroke_evidence"]["frames"]:
        sections.append(f"<figure><figcaption>{frame['elapsed_ms']} ms von 210 ms</figcaption><img src='{frame['file']}'></figure>")
    sections.append("<p>Negativkontrollen: gleichmäßiges Fade und vertauschte X-Zugfolge abgelehnt.</p>")
    for motion in evidence["movements"]:
        sections.append(f"<h2>Bewegung Variante {motion['style']}</h2><p>Zweite Geste: {motion['second_gesture_ms']:.2f} ms nach Commit; native 1:1-Ausschnitte. Zeiten sind Messwerte, keine Einzelbild-FPS-Zusage.</p>")
        for frame in motion["timeline"]:
            sections.append(f"<figure><figcaption>{frame['label']} · {frame['after_commit_ms']:.2f} ms</figcaption><img src='{frame['file']}'></figure>")
    return html_page("Nativer Strichaufbau und Echtzeitfolge", sections)


def html_page(title: str, sections: list[str]) -> str:
    return "<!doctype html><html lang='de'><meta charset='utf-8'><title>ZS-1</title><style>body{font:16px system-ui;background:#faf6ec;color:#343f42;margin:24px}.row{display:flex}figure{margin:8px}.row figure{width:32%}.row img{width:100%}img{max-width:100%}h2{margin-top:40px}</style>" + f"<h1>ZS-1 · {title}</h1><p>PNG bei 100 % betrachten. Nachweisindex, keine Spielimplementierung. ZS1-M01 abgeschlossen; aktuelle ZS2-M01-Abnahme separat offen.</p>" + "".join(sections) + "</html>"
