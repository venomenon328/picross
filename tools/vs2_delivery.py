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
    environment["VS2_CAPTURE_DIR"] = str(renders)
    command = ["res://tests/vs2_tests.gd" if part == "res://tests/capture.gd" else part for part in render_command]
    try:
        phase("vs2-regular-matrix",command,"VS2_TESTS_OK")
    finally:
        environment.pop("VS2_CAPTURE_DIR",None)
    return verify(renders)

def verify(renders: Path) -> dict:
    report = json.loads((renders/"vs2-matrix.json").read_text(encoding="utf-8"))
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
    for picture in report["pictures"]:
        if Path(picture["file"]).name != picture["file"] or toolchain.sha256_file(renders/picture["file"]) != picture["sha256"]:
            raise toolchain.PreflightError("VS2 native image binding differs")
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
