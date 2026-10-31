#!/usr/bin/env python3
"""Build and verify the isolated #493 B-A study; never launches a browser."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from copy import deepcopy
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import p1_preflight as tc
from p1_product import run_phase, require_clean_output, player_extras
from build_web_player import extract_web_templates
from product_fixtures import install_runtime_fixtures
from p1_evidence import source_identity

STUDY = "study/book"


def fixtures() -> dict:
    """Reuse T01/T06/T08 shapes; T08 becomes a 40x30 rectangle, no real puzzles."""
    with tempfile.TemporaryDirectory(prefix="book-fixtures-") as temp:
        project = Path(temp)
        install_runtime_fixtures(ROOT, project)
        catalog = json.loads((project / "data/registry.json").read_text())
        definitions, entries = [], []
        for key in ("t01", "t06", "t08"):
            entry = next(e.copy() for e in catalog["entries"] if e["key"] == key)
            data = json.loads((project / entry["definition"]).read_text())
            if key == "t08":
                data["solution"] = data["solution"][:30]
                data["height"] = 30
                data["rows"] = data["rows"][:30]
                def hints(line):
                    result, previous = [], 0
                    for value in line:
                        if value:
                            if value == previous:
                                result[-1]["length"] += 1
                            else:
                                result.append(dict(length=1, color=value))
                        previous = value
                    return result
                data["columns"] = [hints(line) for line in zip(*data["solution"])]
            entry.update(category_id="technical")
            definitions.append(data)
            entries.append(entry)
        for index in range(3, 27):
            entry = deepcopy(entries[index % 3])
            entry.update(id=f"T-{index+10:02d}", key=f"t{index+10:02d}", save_slot=f"t{index+10:02d}")
            entries.append(entry)
        instances = []
        for index, entry in enumerate(entries):
            key = entry['key']
            entry.update(definition=f"data/{key}.json", reveal=f"art/{key}.svg")
            data = deepcopy(definitions[index % 3])
            data['id'] = entry['id']
            data['reveal'].update(definition_id=entry['id'], image=f"res://{STUDY}/{entry['reveal']}",
                                  name="VERBORGENER STUDIENNAME " + key)
            instances.append(data)
        return dict(registry=dict(format=catalog["format"], categories=[dict(id="technical", name="Technische Muster", order=1)], entries=entries), definitions=instances)


def write_fixtures() -> None:
    target = ROOT / "game" / STUDY
    inputs = fixtures()
    (target / "fixtures.json").write_text(json.dumps(inputs['registry'], ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    # Explicit synthetic spoiler sentinel; never shown before valid completion.
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><path d="M16 16H112V112H16Z" fill="#d933c5"/></svg>\n'
    for entry, data in zip(inputs['registry']['entries'], inputs['definitions'], strict=True):
        for path, text in ((entry['definition'], json.dumps(data, ensure_ascii=False, separators=(",", ":"))+'\n'), (entry['reveal'], svg)):
            destination = target / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding='utf-8', newline='\n')


def prepare(project: Path) -> None:
    shutil.copytree(ROOT / "game", project, ignore=shutil.ignore_patterns(".godot", "build", "content"))
    settings = project / "project.godot"
    settings.write_text(settings.read_text(encoding="utf-8").replace('run/main_scene="res://main.tscn"', 'run/main_scene="res://study/book/main.tscn"').replace('config/name="picross · P1"', 'config/name="picross · Buchstudie B-A"'), encoding="utf-8", newline="\n")


def run(cache: Path, output: Path, native_only: bool = False) -> dict:
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output must be empty")
    output.mkdir(parents=True, exist_ok=True)
    logs = output / "logs"
    logs.mkdir()
    host = platform.system()
    editor = tc.EDITORS[host]
    assets = (editor,) if native_only else (editor, tc.TEMPLATES)
    urls = tc.official_asset_urls(tc.request_json(tc.RELEASE_API), assets)
    for asset in assets:
        tc.download_asset(urls[asset.name], cache / asset.name, asset.sha256, 1200)
    report = dict(package="B-A-N02-T01", **source_identity(ROOT),
                  host=host, platform=platform.platform(), python=platform.python_version(),
                  engine=tc.EXPECTED_VERSION, phases=[], browser="not requested; not started")
    report["sources"] = {p.relative_to(ROOT).as_posix(): tc.sha256_file(p) for p in sorted((ROOT / "game" / STUDY).rglob("*")) if p.is_file()}
    report["sources"]["tools/book_study.py"] = tc.sha256_file(Path(__file__))
    material = ROOT / "game/art/book/bp2-a-inventarband.png"
    report["material_source"] = dict(file=material.relative_to(ROOT).as_posix(), sha256=tc.sha256_file(material), bytes=material.stat().st_size)
    if report["material_source"]["sha256"] != "957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a":
        raise ValueError("The bound original A material changed")
    paper = ROOT / 'game' / STUDY / 'paper.png'
    paper_metadata = json.loads(paper.with_suffix('.json').read_text(encoding='utf-8'))
    if tc.sha256_file(paper) != paper_metadata['sha256'] or paper.stat().st_size != paper_metadata['bytes']:
        raise ValueError('Organic paper source differs from its provenance')
    report['organic_paper'] = dict(paper_metadata)
    with tempfile.TemporaryDirectory(prefix="picross-book-study-") as temp:
        work = Path(temp)
        engine = str(tc.extract_editor(cache / editor.name, work / "engine", host))
        project = work / "game"
        prepare(project)
        env = tc.isolated_environment(work, host)
        env["BOOK_STUDY_OUTPUT"] = str(output)
        def phase(name, args, marker=None, render=False):
            command = [engine, *args]
            if render and host == "Linux":
                command = ["xvfb-run", "-a", *command]
                env["LIBGL_ALWAYS_SOFTWARE"] = "1"
            result = run_phase("book-" + name, command, env, 300, logs)
            report["phases"].append({k: v for k, v in result.items() if k != "output"})
            require_clean_output(result, marker)
        base = ["--path", str(project), "--audio-driver", "Dummy"]
        phase("version", ["--version"], tc.EXPECTED_VERSION)
        phase("import", ["--headless", *base, "--import"])
        imported = project / '.godot/imported/paper.png-d97cf9011e5b971689c7f26fae3c148d.ctex'
        report['organic_paper']['imported_texture'] = dict(bytes=imported.stat().st_size, sha256=tc.sha256_file(imported))
        report['organic_paper']['import_settings_sha256'] = tc.sha256_file(project / STUDY / 'paper.png.import')
        phase("native", [*base, "--rendering-driver", "opengl3", "--script", "res://study/book/verify.gd", "--", "--p1-capture"], "BOOK_STUDY_OK", True)
        started = time.monotonic()
        report["handoff_pixels"] = verify_handoffs(output)
        report["pixel_verification_seconds"] = time.monotonic() - started
        phase("movie", [*base, "--rendering-driver", "opengl3", "--write-movie", str(output / "opening.avi"), "--fixed-fps", "30", "--script", "res://study/book/verify.gd", "--", "--movie", "--p1-capture"], "BOOK_STUDY_MOVIE_OK", True)
        if not native_only:
            export_all(work, project, cache, output, env, phase, base, report)
    report["files"] = {p.relative_to(output).as_posix(): dict(bytes=p.stat().st_size, sha256=tc.sha256_file(p)) for p in sorted(output.rglob("*")) if p.is_file()}
    report["inventory_cost"] = dict(files=len(report["files"]), bytes=sum(row["bytes"] for row in report["files"].values()),
                                  pngs=sum(name.endswith('.png') for name in report["files"]), movie_bytes=report["files"]["opening.avi"]["bytes"])
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def export_all(work, project, cache, output, env, phase, base, report):
    templates = tc.template_directory(work, platform.system())
    tc.extract_windows_templates(cache / tc.TEMPLATES.name, templates)
    extract_web_templates(cache / tc.TEMPLATES.name, templates)
    settings = project / "project.godot"
    study_settings = settings.read_bytes()
    preset = project / "export_presets.cfg"
    regular_presets = preset.read_bytes()
    from product_fixtures import restore_player_catalog
    restore_player_catalog(ROOT, project)
    settings.write_bytes((ROOT / "game/project.godot").read_bytes())
    phase("regular-import", ["--headless", *base, "--import"])
    expected_count = sum(e["visible"] for e in json.loads((ROOT / "content/registry.json").read_text(encoding="utf-8"))["entries"])
    env["ZA1_PACK_COUNT"] = str(expected_count)
    report["regular_packages"] = {}
    for label, export_preset, name in (("windows", "P1 Windows x86_64", "picross-p1.exe"), ("web", "P1 Web", "index.html")):
        target = work / "regular" / label / name
        target.parent.mkdir(parents=True)
        phase("regular-" + label, ["--headless", *base, "--export-debug", export_preset, str(target)])
        pack = target.with_suffix(".pck")
        phase("regular-" + label + "-content", ["--headless", "--main-pack", str(pack), "--script", str(ROOT / "game/tests/content_pack_probe.gd")], "CONTENT_PACK_OK")
        env["BOOK_EXPECT_STUDY"] = "0"
        phase("regular-" + label + "-isolation", ["--headless", "--main-pack", str(pack), "--script", str(ROOT / "game/study/book/pack_probe.gd")], "BOOK_PACK_OK")
        report["regular_packages"][label] = {p.name: dict(bytes=p.stat().st_size, sha256=tc.sha256_file(p)) for p in target.parent.iterdir() if p.is_file()}
    settings.write_bytes(study_settings)
    preset.write_text(study_presets(), encoding="utf-8", newline="\n")
    report["study_web_features"] = dict(renderer="gl_compatibility", threads=False, extensions=False, browser_probe="not requested")
    env["BOOK_EXPECT_STUDY"] = "1"
    for label, export_preset, name in (("windows", "Book study Windows", "book-study.exe"), ("web", "Book study Web", "index.html")):
        target = output / label / name
        target.parent.mkdir()
        phase("study-" + label, ["--headless", *base, "--export-debug", export_preset, str(target)])
        pack = target.with_suffix(".pck")
        phase("study-" + label + "-pack", ["--headless", "--main-pack", str(pack), "--script", str(ROOT / "game/study/book/pack_probe.gd")], "BOOK_PACK_OK")
        for relative, source in player_extras(ROOT, work).items():
            if not relative.startswith("licenses/"): continue
            destination = target.parent / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        guide = (ROOT / "game/study/book/README.md").read_text(encoding="utf-8")
        guide = guide.replace("../../../docs/BOOK_STUDY.md", f"https://github.com/venomenon328/picross/blob/{report['source_commit']}/docs/BOOK_STUDY.md")
        (target.parent / "STUDIE.md").write_text(guide, encoding="utf-8", newline="\n")
        shutil.copyfile(ROOT/'game'/STUDY/'paper.json',target.parent/'licenses/Study-paper.json')
    if platform.system() == "Windows":
        native = output / "windows/book-study.exe"
        result = run_phase("book-windows-exported-motion", [str(native), "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--quit-after", "1200", "--", "--book-study-proof"], env, 90, output / "logs")
        require_clean_output(result, "BOOK_PACK_MOTION_OK")
        report["phases"].append({k: v for k, v in result.items() if k != "output"})
    else:
        report["windows_start"] = "not executed on Linux; native Windows probe remains open"
    preset.write_bytes(regular_presets)


def study_presets() -> str:
    """Separate build configuration; regular presets in the repository stay exact."""
    legacy = [p.relative_to(ROOT / "game").as_posix() + ("/*" if p.is_dir() else "")
              for p in sorted((ROOT / "game/study").iterdir()) if p.name != "book"]
    exclusions = ["tests/*", "full_view_study/*", "data/*", "art/content/*", "perf_a/*", "web/*",
                  "ui/pencil_marks.gd", "study/book/verify.gd", "study/book/pack_probe.gd", *legacy]
    common = '''runnable=false
export_filter="all_resources"
include_filter="study/book/fixtures.json,study/book/data/*.json,study/book/art/*.svg,study/book/paper.json,art/book/*.json,art/book/*.txt,art/drawing/delight-coffee/*,art/drawing/tidy-hand/*"
''' + 'exclude_filter="' + ','.join(exclusions) + '"\nscript_export_mode=2\n'
    return '[preset.0]\nname="Book study Windows"\nplatform="Windows Desktop"\n' + common + '''
[preset.0.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false
debug/export_console_wrapper=1
codesign/enable=false
texture_format/s3tc_bptc=true
texture_format/etc2_astc=false

[preset.1]
name="Book study Web"
platform="Web"
''' + common + '''
[preset.1.options]
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/custom_html_shell="res://study/book/shell.html"
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
progressive_web_app/enabled=false
'''


def verify_handoffs(output: Path) -> dict:
    from PIL import Image, ImageChops, ImageStat
    report = json.loads((output / "native.json").read_text(encoding="utf-8"))
    def comparison(first, second):
        if first.size != second.size or first.mode != second.mode:
            raise ValueError("Handoff image format changed")
        diff = ImageChops.difference(first, second)
        maximum = max(end for start, end in diff.getextrema())
        means = ImageStat.Stat(diff).mean
        if maximum > 4 or max(means) > 0.1:
            raise ValueError(f"Visible handoff pixel difference: max={maximum}, mean={means}")
        return dict(max_channel_delta=maximum, mean_channel_delta=means, pixels=first.width*first.height)
    results = {}
    for sample in report["handoffs"]:
        with Image.open(output / sample["texture"]) as first, Image.open(output / sample["direct"]) as second:
            results[sample["direct"]] = comparison(first, second)
            if len(results) == 1:
                for kind, mutated in (("shift", ImageChops.offset(second, 1, 0)), ("alpha", second.copy())):
                    if kind == "alpha":
                        mutated.putpixel((0, 0), (0, 0, 0, 0))
                    try:
                        comparison(first, mutated)
                    except ValueError:
                        pass
                    else:
                        raise ValueError("Handoff gate accepted a shifted/alpha-mutated counterexample")
    if set(results) != {'work-1280.png','work-1920.png','work-2560.png','return-handoff-direct.png'}:
        raise ValueError("Three work configurations and the catalog return handoff required")
    return dict(samples=results, negative_controls="one-pixel displacement and alpha mutation rejected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-fixtures", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--native-only", action="store_true")
    args = parser.parse_args()
    if args.write_fixtures:
        write_fixtures()
    else:
        if args.cache_dir is None or args.output_dir is None: parser.error("cache and output are required")
        run(args.cache_dir.resolve(), args.output_dir.resolve(), args.native_only)
