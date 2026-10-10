"""VS2 regular delivery and explicit frozen developer-reference replay."""
from __future__ import annotations
import io
import json
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
import p1_preflight as toolchain

BASE = "fad885344874534629365917a2ab6a8d311cd3a7"

def capture_current(project, workspace, output, engine, render_command, environment, phase):
    """Current VS2 coverage; historical imports remain explicit separate replays."""
    environment["VS2_PROBE_OUTPUT"] = str(output)
    environment["P1_TEST_SAVE_ROOT"] = str(workspace / "vs2-current-saves")
    try:
        for stage in ("write", "read"):
            environment["VS2_STAGE"] = stage
            phase("vs2-roundtrip-" + stage,
                  [engine, "--headless", "--path", str(project), "--script", "res://tests/vs2_roundtrip.gd"],
                  "VS2_ROUNDTRIP_" + stage.upper() + "_OK")
    finally:
        for key in ("VS2_STAGE", "VS2_PROBE_OUTPUT", "P1_TEST_SAVE_ROOT"):
            environment.pop(key, None)
    phase("vs2-gf1-tests", [engine, "--headless", "--path", str(project), "--script",
                          "res://tests/vs2_gf1_tests.gd"], "VS2_GF1_TESTS_OK")
    renders = output / "vs2-renders"
    renders.mkdir()
    environment["VS2_CAPTURE_DIR"] = str(renders)
    command = ["res://tests/vs2_tests.gd" if part == "res://tests/capture.gd" else part
               for part in render_command]
    try:
        phase("vs2-regular-matrix", command, "VS2_TESTS_OK")
    finally:
        environment.pop("VS2_CAPTURE_DIR", None)
    report = verify(renders)
    focused_dir = output / "v1-renders"
    focused_dir.mkdir()
    environment["VS2_V1_CAPTURE_DIR"] = str(focused_dir)
    try:
        phase("vs2-v1-focused", ["res://tests/vs2_v1_tests.gd" if part == "res://tests/capture.gd" else part
                                for part in render_command], "VS2_V1_OK")
    finally:
        environment.pop("VS2_V1_CAPTURE_DIR", None)
    focused = json.loads((focused_dir / "v1-focused.json").read_text(encoding="utf-8"))
    import vs2_v1_verify
    v1 = vs2_v1_verify.verify(report, focused)
    for picture in focused["pictures"] + focused["glyphs"]:
        if Path(picture["file"]).name != picture["file"]:
            raise toolchain.PreflightError("Unsafe V1 image path")
        toolchain.verify_sha256(focused_dir/picture["file"], picture["sha256"])
    (focused_dir / "v1-acceptance.json").write_text(json.dumps(v1,indent=2)+"\n",encoding="utf-8")
    selected = [renders / "vs2-matrix.json", output / "vs2-write.json", output / "vs2-read.json",
                focused_dir / "v1-focused.json", focused_dir / "v1-acceptance.json"]
    selected += [focused_dir / name for name in ("v1-F-01-fit.png", "v1-F-01-work.png", "v1-VS09-work.png", "v1-VS08-fit.png", "v1-VS04-fit.png", "v1-recovery-1280-ui125.png")]
    selected += [focused_dir / g["file"] for g in focused["glyphs"]]
    v2_dir = output / "v2-renders"
    v2_dir.mkdir()
    environment["VS2_V2_CAPTURE_DIR"] = str(v2_dir)
    try:
        for stage in ("write", "read"):
            environment["VS2_V2_STAGE"] = stage
            phase("vs2-v2-" + stage,
                  ["res://tests/vs2_v2_tests.gd" if part == "res://tests/capture.gd" else part
                   for part in render_command], "VS2_V2_" + stage.upper() + "_OK")
    finally:
        environment.pop("VS2_V2_CAPTURE_DIR", None)
        environment.pop("VS2_V2_STAGE", None)
    v2 = verify_v2(v2_dir)
    v2["plan_sha256"] = toolchain.sha256_file(Path(__file__).resolve().parents[1] / "examples/vs2/v2-plan.json")
    v2["scripts"] = {name: toolchain.sha256_file(project / "tests" / name)
                     for name in ("vs2_v2_tests.gd", "vs2_v2_cases.gd")}
    selected += list(v2_dir.glob("*.json"))
    selected += [v2_dir / p["file"] for p in v2["write"]["pictures"]]
    font = project / "art/drawing/BaksoDaging-Regular.ttf"
    toolchain.verify_sha256(font, "56372bf12a6e4fa47a655ff9b2c4cc73172ddd387b3a047093d3e637d081790e")
    v3_dir = output / "v3-renders"
    v3_dir.mkdir()
    environment["VS2_V3_CAPTURE_DIR"] = str(v3_dir)
    try:
        phase("vs2-v3-current", ["res://tests/vs2_v3_tests.gd" if part == "res://tests/capture.gd" else part
              for part in render_command], "VS2_V3_OK")
    finally:
        environment.pop("VS2_V3_CAPTURE_DIR", None)
    v3 = verify_v3(v3_dir)
    v3["sidebar_plan_sha256"] = toolchain.sha256_file(Path(__file__).resolve().parents[1] / "examples/vs2/sl65-plan.json")
    v3["plan_sha256"] = toolchain.sha256_file(Path(__file__).resolve().parents[1] / "examples/vs2/v3-plan.json")
    v3["font_sha256"] = toolchain.sha256_file(font)
    selected += list(v3_dir.glob("*.json")) + [v3_dir / p["file"] for p in v3["pictures"]]
    return dict(records=len(report["records"]), failures=report["failures"],
                rendered=len(report["pictures"]), v1=v1, v2=v2, v3=v3,
                historical_comparison="not run; CI policy #63",
                legacy_reader="separate downloaded Windows old-writer/new-reader probe"), selected


def verify_v3(directory: Path) -> dict:
    report = json.loads((directory / "v3-report.json").read_text(encoding="utf-8"))
    expected_cases = {(sheet, w, h, ui, mode, fit) for sheet in ("F-01", "F-02", "F-08")
                      for w, h in ((1280, 720), (1600, 900), (1920, 1080), (2560, 1440))
                      for ui in (1.0, 1.25) for mode in ("G", "V") for fit in (False, True)}
    actual_cases = {(r["id"], *r["client"], r["ui"], r["mode"], r["fit"]) for r in report["records"]}
    if report["failures"] or len(report["records"]) != 96 or actual_cases != expected_cases or report["checks"] < 1000:
        raise toolchain.PreflightError("Incomplete/failed V3 native coverage")
    expected = {"v3-tight-rail.png", "v3-F01-work.png", "v3-F08-work.png", "v3-title.png", "v3-fills-five.png"}
    expected.update(['v3-sl-720-125-color-G.png', 'v3-sl-720-100-mono-V.png', 'v3-sl-900-100-color-V.png', 'v3-sl-900-125-mono-G.png', 'v3-sl-1440-125-color-V.png', 'v3-sl-720-125-recovery.png', 'v3-sidebar-detail.png'])
    metadata = json.loads((Path(__file__).resolve().parents[1] / "prototypes/p1/art/book/frames.json").read_text(encoding="utf-8"))
    if report.get("sidebar_assets") != metadata or len(report.get("frame_pixels", [])) != 3 or any(p["changed_pixels"] <= 100 for p in report["frame_pixels"]):
        raise toolchain.PreflightError("Missing/mismatched SL frame resources or actual render usage")
    if {p["file"] for p in report["pictures"]} != expected or len(report["pictures"]) != len(expected):
        raise toolchain.PreflightError("Missing V3 targeted native pictures")
    for picture in report["pictures"]:
        toolchain.verify_sha256(directory / picture["file"], picture["sha256"])
    return report


def verify_v2(directory: Path) -> dict:
    reports = {stage: json.loads((directory / ("v2-" + stage + ".json")).read_text(encoding="utf-8"))
               for stage in ("write", "read")}
    expected = {"v2-projection-1.png", "v2-projection-4.png", "v2-mono-work.png",
                "v2-five-crossing.png", "v2-color-work.png", "v2-mini-palette.png"}
    for stage, report in reports.items():
        if report["failures"] or report["checks"] < (100 if stage == "write" else 8):
            raise toolchain.PreflightError("Incomplete/failed V2 " + stage)
        for picture in report["pictures"]:
            if Path(picture["file"]).name != picture["file"]:
                raise toolchain.PreflightError("Unsafe V2 image path")
            toolchain.verify_sha256(directory / picture["file"], picture["sha256"])
    if {p["file"] for p in reports["write"]["pictures"]} != expected or len(reports["write"]["pictures"]) != len(expected):
        raise toolchain.PreflightError("Incomplete V2 native image coverage")
    if len(reports["write"]["scenarios"]) != 19 or len(set(reports["write"]["scenarios"])) != 19 or reports["read"]["scenarios"] != ["fresh process redo restores X"]:
        raise toolchain.PreflightError("Incomplete V2 transition coverage")
    return reports


def reference_project(root: Path, workspace: Path) -> Path:
    target = workspace / "vs2-zs2-reference"
    if target.exists():
        return target
    raw = subprocess.check_output(["git", "archive", BASE, "prototypes/p1"], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to("prototypes/p1")
            if ".." in relative.parts or relative.is_absolute():
                raise toolchain.PreflightError("Unsafe reference path")
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.extractfile(member).read())
    return target

def capture(root, project, workspace, output, engine, render_command, environment, phase):
    reference = reference_project(root, workspace)
    shutil.copyfile(root / "prototypes/p1/tests/vs2_roundtrip.gd", reference / "tests/vs2_roundtrip.gd")
    phase("vs2-reference-import", [engine,"--headless","--path",str(reference),"--import"])
    environment["VS2_PROBE_OUTPUT"] = str(output)
    # The old process really writes Schema 1 before the new process reads it.
    for stage, source in (("legacy-write",reference),("legacy-read",project),("write",project),("read",project)):
        environment["VS2_STAGE"] = stage
        phase("vs2-roundtrip-"+stage,[engine,"--headless","--path",str(source),"--script","res://tests/vs2_roundtrip.gd"],"VS2_ROUNDTRIP_"+stage.upper().replace("-","_")+"_OK")
    for key in ("VS2_STAGE","VS2_PROBE_OUTPUT"):
        environment.pop(key,None)
    phase("vs2-gf1-tests",[engine,"--headless","--path",str(project),"--script","res://tests/vs2_gf1_tests.gd"],"VS2_GF1_TESTS_OK")
    renders = output / "vs2-renders"
    renders.mkdir()
    for path in (output/"renders").glob("h1-vs2-1920x1080-ui*-G-*.png"):
        shutil.copyfile(path,renders/path.name)
    shutil.copyfile(output/"renders/render-report-h1.json",renders/"vs2-h1-regular.json")
    environment["VS2_CAPTURE_DIR"] = str(renders)
    command = ["res://tests/vs2_tests.gd" if part == "res://tests/capture.gd" else part for part in render_command]
    try:
        phase("vs2-regular-matrix",command,"VS2_TESTS_OK")
    finally:
        environment.pop("VS2_CAPTURE_DIR",None)
    evidence = verify(renders)
    historical = json.loads((output/"vs1-renders/vs1-matrix.json").read_text(encoding="utf-8"))
    comparisons=[]
    for current in evidence["records"]:
        if not current["corpus"] or current["client"] != [1920,1080] or current["mode"]!="G" or current["id"] not in {"VS04","VS08","VS09"}: continue
        old=next(r for r in historical["records"] if (r["id"],r["client"],r["ui_scale"],r["mode"]) == (current["id"],current["client"],current["ui_scale"],current["mode"]))
        comparisons.append(dict(id=current["id"],ui_scale=current["ui_scale"],reference_commit=BASE,
                                old={k:old[k] for k in ("board_rect","cell_pitch","reserve_slots","font_px","horizontal_budget_px")},
                                regular={k:current[k] for k in ("board_rect","cell_pitch","reserve_slots","font_px","horizontal_budget_px")}))
        if current["id"]=="VS08" and (current["reserve_slots"][0]!=13 or current["axis_counts"]["row"]["hidden_numbers"]):
            raise toolchain.PreflightError("Regular 1080 VS08 does not show all 13 row hints")
    if len(comparisons)!=6: raise toolchain.PreflightError("Missing GF1 regular/reference geometry comparisons")
    evidence["reference_comparisons"]=comparisons
    (renders/"vs2-matrix.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return evidence

def verify_records(report: dict) -> None:
    expected = {(corpus,index,w,ui,mode) for corpus,count in ((False,9),(True,10)) for index in range(count) for w in (1280,1600,1920,2560) for ui in (1.0,1.25) for mode in ("G","V")}
    actual = {(r["corpus"], int(r["id"].replace("F-","").replace("VS",""))-1,r["client"][0],r["ui_scale"],r["mode"]) for r in report["records"]}
    if report["failures"] or actual != expected or len(report["records"]) != 304:
        raise toolchain.PreflightError("Incomplete/failed VS2 regular matrix")
    for record in report["records"]:
        if record["layout_valid"] and not record["grid_fit"]:
            raise toolchain.PreflightError("VS2 frame does not fit")
        if record["mode"] == "V" and record["hidden_tokens"]:
            raise toolchain.PreflightError("VS2 V hides hints")
        if record["status"] == "geometric_fit_owner_open" and (record["clipped_glyphs"] or record["glyph_collisions"] or record["cell_pitch"] < 16):
            raise toolchain.PreflightError("VS2 false positive legibility status")


def verify(renders: Path) -> dict:
    report = json.loads((renders/"vs2-matrix.json").read_text(encoding="utf-8"))
    verify_records(report)
    for picture in report["pictures"]:
        if Path(picture["file"]).name != picture["file"] or toolchain.sha256_file(renders/picture["file"]) != picture["sha256"]:
            raise toolchain.PreflightError("VS2 native image binding differs")
        if any(edge["minimum_ink_pixels"] < 1 for edge in picture.get("frame_pixels",{}).values()):
            raise toolchain.PreflightError("VS2 rendered frame edge missing")
        if picture["file"].startswith(("regular-","corpus-")) and set(picture.get("frame_pixels",{})) != {"top","bottom","left","right"}:
            raise toolchain.PreflightError("VS2 rendered frame evidence incomplete")
    expected_images = {"album.png","options.png"}
    expected_images.update(f"regular-F-{i:02d}-G-ui{ui}.png" for i in (1,7) for ui in (100,125))
    expected_images.update(f"corpus-VS{i:02d}-{mode}-ui{ui}.png" for i in (4,8,9) for mode in ("G","V") for ui in (100,125))
    expected_images.update(f"rectangular-VS{i:02d}-reveal.png" for i in (1,3,5,7,9))
    if {p["file"] for p in report["pictures"]} != expected_images or len(report["pictures"]) != len(expected_images):
        raise toolchain.PreflightError("VS2 native image coverage incomplete")
    return report

def package(root, output, product, evidence):
    report = {key:product[key] for key in ("source_commit","source_tree_dirty","base_commit","tested_checkout_commit","github_run_id","host","engine_version","export_files")}
    report.update(reference_commit=BASE, plan_sha256=toolchain.sha256_file(root/"examples/vs2/plan.json"),
                  files={p.name:toolchain.sha256_file(p) for p in (output/"vs2-renders").iterdir() if p.is_file()},
                  independent_review="OPEN",VS2_M01="OPEN",merge_authorized=False)
    with zipfile.ZipFile(output/"picross-vs2-review.zip","w",compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("vs2-report.json",json.dumps(report,ensure_ascii=False,indent=2)+"\n")
        for path in (output/"vs2-renders").iterdir():
            if path.is_file(): bundle.write(path,path.name)
        for pattern in ("vs2-*.json","*-expected.json"):
            for path in output.glob(pattern): bundle.write(path,path.name)
        for path in (output/"logs").glob("vs2-*.log"): bundle.write(path,"logs/"+path.name)
        for name in ("VS2_VERIFICATION.md","VS2_OWNER_TRIAL.md"): bundle.write(root/"docs"/name,name)
        bundle.write(root/"examples/vs2/plan.json","plan.json")
        images="".join(f"<figure><figcaption>{p['file']}</figcaption><a href='{p['file']}'><img src='{p['file']}' loading='lazy'></a></figure>" for p in evidence["pictures"])
        bundle.writestr("index.html","<!doctype html><html lang='de'><meta charset='utf-8'><title>VS2</title><style>body{font:16px system-ui;margin:32px;background:#faf6ec}img{max-width:100%}</style><h1>Reguläre Vollsicht</h1><p>Native logische Flächen; PNG für 1:1 öffnen. Einschränkungen stehen je Fall in vs2-matrix.json. Persönliche VS2-M01 und unabhängiges Review offen.</p>"+images+"</html>")
