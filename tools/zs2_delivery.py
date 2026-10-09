"""Regular ZS-2 integration: pinned native comparisons and separate movement evidence."""
from __future__ import annotations

import io
import json
import math
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
    from PIL import Image, ImageChops, ImageDraw
    reports = {role: json.loads((renders / f"zs2-{role}.json").read_text(encoding="utf-8"))
               for role in ("before", "study", "after")}
    if any(report["failures"] or len(report["captures"]) != 16 for report in reports.values()):
        raise toolchain.PreflightError("Incomplete/failed ZS2 native matrix")
    pairs = []
    identical_boards = 0
    edge_only_boards = []
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
            difference = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
            if difference.crop(bounds).getbbox():
                # The selected study's 0.2px AA allowance leaked faint X ink.
                # ZS2 reserves 1px. Only the 5px viewport fringe may differ
                # (diagonal AA end caps and their raster rounding included);
                # clues remain exact; raster rounding is bounded below.
                vx, vy, vw, vh = new["viewport"]
                vx, vy = x + vx, y + vy
                allowed = Image.new("L", a.size)
                draw = ImageDraw.Draw(allowed)
                draw.rectangle((math.floor(vx-5), math.floor(vy-5), math.ceil(vx+vw+5), math.ceil(vy+vh+5)), fill=255)
                draw.rectangle((math.ceil(vx+6), math.ceil(vy+6), math.floor(vx+vw-6), math.floor(vy+vh-6)), fill=0)
                forbidden = ImageChops.multiply(difference, ImageChops.invert(allowed).convert("RGB"))
                # Re-triangulated AA lines can round one 8-bit channel step
                # differently along their remainder. Clues allow no tolerance.
                rounding = Image.new("L", a.size)
                ImageDraw.Draw(rounding).rectangle((math.ceil(vx), math.ceil(vy), math.floor(vx+vw)-1, math.floor(vy+vh)-1), fill=1)
                forbidden = ImageChops.subtract(forbidden, rounding.convert("RGB"))
                if forbidden.crop(bounds).getbbox():
                    raise toolchain.PreflightError(f"ZS2 selected board pixels differ outside clipping fringe: {new['case']}")
                edge_only_boards.append(new["case"])
            else:
                identical_boards += 1
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
                identical_selected_boards=identical_boards, clipping_corrected_boards=edge_only_boards,
                raster_rounding_tolerance="1/255 per channel inside raster only; clues exact",
                movements=current["frames"], stroke_evidence=strokes,
                x_size_evidence=verify_x_sizes(renders, current["rework_sequences"]),
                wave_evidence=verify_wave(renders, current['wave_sequence']),
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
    for kind, files in (("review", names), ("strokes", {p.name for pattern in ("zs1-motion-*.png", "zs1-strokes-*.png", "zs2-x-*.png", "zs2-wave-*.png") for p in renders.glob(pattern)})):
        archive = output / f"picross-zs2-{kind}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name in sorted(files):
                bundle.write(renders / name, name)
            bundle.writestr("zs2-report.json", text)
            bundle.write(root / "docs/ZS2_VERIFICATION.md", "PRUEFUNG.md")
            if kind == "strokes":
                index = zs1_delivery.movement_html(evidence).replace("ZS-1", "ZS-2")
                index = index.replace("</html>", x_playback(evidence["x_size_evidence"]) + "</html>")
                wave=evidence['wave_evidence']
                index=index.replace('</html>', '<h2>N02: 17 Umwandlungszellen, rechts nach links</h2><p>0 ms: rechte Zelle beginnt, alle wartenden Ziele zeigen nur das abgeschwächte X. 120 ms: linke Zelle beginnt; 260 ms: vollständig fertig.</p>'+''.join(f"<figure><figcaption>{f['elapsed_ms']} ms</figcaption><img src='{f['file']}'></figure>" for f in wave['frames'])+'</html>')
            else:
                sections = ["<p>Jeweils vorherige reguläre Ansicht, gewählte isolierte Studie, neue reguläre Ansicht. Identische eigene Zellen und Eingaben; PNG bei 100 % prüfen.</p>"]
                for pair in evidence["pairs"]:
                    sections.append("<h2>" + pair["case"] + "</h2><div class='row'>" + "".join(f"<figure><figcaption>{key}</figcaption><a href='{pair[key]}'><img src='{pair[key]}'></a></figure>" for key in ("before", "study", "after")) + "</div>")
                sections.append("<h2>Reguläre Ziffernprobe</h2><img src='zs2-numerals.png'>")
                index = zs1_delivery.html_page("Reguläre Integration", sections).replace("ZS-1", "ZS-2")
            bundle.writestr("index.html", index)
        print(f"ZS2 {kind.upper()} {archive} sha256:{toolchain.sha256_file(archive)}", flush=True)


def x_regions(size):
    # Independent image regions; no production path, seed or stroke code imported.
    return [(int(size*a), int(size*.15), int(size*b), int(size*.48)) for a,b in ((.15,.48),(.52,.85))]


def verify_wave(renders, record):
    from PIL import Image, ImageChops
    if record['start']!=[17,2] or record['end']!=[1,2] or record['effective_cells']!=17:
        raise toolchain.PreflightError('ZS2 reversed wave evidence changed')
    def read(name):
        with Image.open(renders/name) as p:
            if p.size!=(408,24):raise toolchain.PreflightError('ZS2 wave crop changed')
            return p.convert('RGB')
    blank,preview=read(record['blank']),read(record['preview'])
    images={f['elapsed_ms']:read(f['file']) for f in record['frames']}
    if list(images)!=[0,8,70,120,140,260]:raise toolchain.PreflightError('ZS2 wave timeline incomplete')
    def same(a,b,cell):
        # The live gesture counter overlaps the top 4px of this row. Compare
        # cell ink below that UI edge; an old fill/X would still be detected.
        bounds=(cell*24+2,5,cell*24+22,22)
        return not ImageChops.difference(a.crop(bounds),b.crop(bounds)).getbbox()
    if not same(images[0],blank,16) or not all(same(images[0],preview,i) for i in range(16)):
        raise toolchain.PreflightError('ZS2 waiting targets/first cell disagree with reverse gesture')
    if not same(images[120],blank,0) or not same(images[140],images[260],16):
        raise toolchain.PreflightError('ZS2 native starts are not bounded by 120ms')
    if any(same(images[260],preview,i) or same(preview,blank,i) for i in range(17)):
        raise toolchain.PreflightError('ZS2 wave lacks distinct preview/final X targets')
    return dict(record,checks=['waiting cells equal target preview, no old fills','rightmost starts first','leftmost starts at 120ms','rightmost complete at 140ms','all final at 260ms'])


def x_order(images, blank, size):
    from PIL import ImageChops
    if ImageChops.difference(images[0], blank).getbbox():
        raise toolchain.PreflightError("ZS2 active X starts with a full underdrawing")
    distance=lambda a,b:max(abs(x-y) for x,y in zip(a,b))
    fractions=[]
    for bounds in x_regions(size):
        x0,y0,x1,y1=bounds
        pixels=[(x,y) for y in range(y0,y1) for x in range(x0,x1)
                if distance(blank.getpixel((x,y)),images[140].getpixel((x,y)))>18]
        if not pixels:raise toolchain.PreflightError("ZS2 native X quadrant has no visible ink")
        fractions.append({ms:sum(distance(picture.getpixel(p),images[140].getpixel(p))<6 for p in pixels)/len(pixels)
                          for ms,picture in images.items()})
    if fractions[0][70]<.9 or fractions[1][70]>.05 or fractions[1][140]<.9:
        raise toolchain.PreflightError("ZS2 native X does not write first stroke before second")
    return fractions


def verify_x_sizes(renders, records):
    from PIL import Image, ImageChops
    if [r['cell_size'] for r in records]!=[12,24,36]:raise toolchain.PreflightError("Missing normal/small/large X")
    result=[]
    for record in records:
        size=record['cell_size']
        def read(name):
            with Image.open(renders/name) as p:
                if p.size!=(size,size):raise toolchain.PreflightError("Scaled X evidence")
                return p.convert('RGB')
        blank=read(record['blank'])
        images={f['elapsed_ms']:read(f['file']) for f in record['controlled']}
        if list(images)!=[0,21,49,70,98,119,140]:raise toolchain.PreflightError("Incomplete X timeline")
        fractions=x_order(images,blank,size)
        fade={ms:Image.blend(blank,images[140],ms/140) for ms in images}
        reverse=dict(images);reverse[70]=images[70].copy()
        for region,source in zip(x_regions(size),(blank,images[140])):reverse[70].paste(source.crop(region),region[:2])
        for label,mutant in (('global fade',fade),('reversed strokes',reverse)):
            try:x_order(mutant,blank,size)
            except toolchain.PreflightError:pass
            else:raise toolchain.PreflightError('ZS2 negative control accepted '+label)
        live=record['live']
        if len(live)<8 or any(a['elapsed_ms']>b['elapsed_ms'] for a,b in zip(live,live[1:])):
            raise toolchain.PreflightError("Invalid real-time X frames")
        early=[f for f in live if 0<f['elapsed_ms']<70]
        second=[f for f in live if 70<f['elapsed_ms']<140]
        if not early or not second or live[-1]['elapsed_ms']<140:
            raise toolchain.PreflightError("Real-time capture missed an X stroke")
        # Early native frame must visibly differ both from blank and from final.
        if not any(ImageChops.difference(read(f['file']),blank).getbbox() and
                   ImageChops.difference(read(f['file']),images[140]).getbbox() for f in early):
            raise toolchain.PreflightError("No spatial movement visible at native cell size")
        if ImageChops.difference(read(live[-1]['file']),images[140]).getbbox():
            raise toolchain.PreflightError("Real-time X ends differently from controlled X")
        with Image.open(renders/record['context']) as context:
            x,y,w,h=record['crop']
            if context.size!=(1920,1080) or ImageChops.difference(context.crop((x,y,x+w,y+h)).convert('RGB'),images[140]).getbbox():
                raise toolchain.PreflightError("X crop does not match native game context")
        result.append(dict(record,quadrant_progress=fractions,negative_controls=['global fade rejected','reversed strokes rejected']))
    return result


def x_playback(records):
    sections=['<h2>ZS2-N01: X in nativer Spielgröße, Echtzeit</h2><p>12 / 24 / 36 px; unvergrößerte Originalpixel. Wiedergabe verwendet die gemessenen Frameabstände. Vollbild-PNG und kontrollierte Zeiten separat prüfen; keine Mausabnahme.</p>']
    for r in records:
        size=r['cell_size']
        sections.append(f"<p>{size} px · <a href='{r['context']}'>1920×1080 Spielkontext</a> · <button onclick='playX({size})'>Echtzeit abspielen</button></p><img id='x{size}' src='{r['blank']}' width='{size}' height='{size}'>")
        sections.append('<div class="row">'+''.join(f"<figure><figcaption>{f['elapsed_ms']} ms</figcaption><img style='width:auto' src='{f['file']}'></figure>" for f in r['controlled'])+'</div>')
    sections.append('<script>const sequences='+json.dumps(records)+''';
const pending={};
async function playX(size){clearTimeout(pending[size]);const r=sequences.find(s=>s.cell_size===size),img=document.getElementById('x'+size);await Promise.all(r.live.map(f=>new Promise(resolve=>{const p=new Image();p.onload=resolve;p.onerror=resolve;p.src=f.file})));img.src=r.blank;
const start=performance.now();let i=0;function tick(){if(i>=r.live.length)return;const f=r.live[i++];pending[size]=setTimeout(()=>{img.src=f.file;tick()},Math.max(0,f.elapsed_ms-(performance.now()-start)))}tick()}
</script>''')
    return ''.join(sections)
