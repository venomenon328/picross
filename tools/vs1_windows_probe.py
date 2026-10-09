"""Download a bound VS delivery and actually launch/test its EXEs on Windows."""
from __future__ import annotations
import argparse
import json
import os
import platform
import re
import subprocess
import time
import zipfile
from pathlib import Path
import p1_preflight as toolchain
import vs1_delivery

ROOT=Path(__file__).resolve().parents[1]

def extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as bundle:
        if len(bundle.namelist()) != len(set(bundle.namelist())):
            raise ValueError("Duplicate archive paths")
        for name in bundle.namelist():
            if not (destination/name).resolve().is_relative_to(destination.resolve()):
                raise ValueError("Unsafe archive path")
        bundle.extractall(destination)

def probe(head: str, run_id: str, output: Path, engine: Path, cache: Path) -> dict:
    if platform.system() != "Windows" or not re.fullmatch(r"[0-9a-f]{40}",head) or not run_id.isdigit():
        raise ValueError("Native Windows, full source head and numeric run required")
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=head or subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip():
        raise ValueError("Probe scripts require a clean checkout of the delivered head")
    if output.exists():
        raise ValueError("Use a fresh output/profile directory")
    output.mkdir(parents=True)
    repository="venomenon328/picross"
    def gh(*args):
        return subprocess.check_output(["gh",*args],cwd=ROOT,timeout=1200)
    artifacts=json.loads(gh("api",f"repos/{repository}/actions/runs/{run_id}/artifacts"))["artifacts"]
    bindings=[]
    for kind in ("vs1-windows-study","vs1-review"):
        meta=next(a for a in artifacts if a["name"]==kind+"-"+head and not a["expired"])
        outer=output/(kind+"-artifact.zip")
        with outer.open("wb") as stream:
            subprocess.run(["gh","api",f"repos/{repository}/actions/artifacts/{meta['id']}/zip"],cwd=ROOT,stdout=stream,check=True,timeout=1200)
        if "sha256:"+toolchain.sha256_file(outer) != meta["digest"]:
            raise ValueError("GitHub artifact digest differs")
        unpacked=output/kind
        extract(outer,unpacked)
        inner=next(unpacked.glob("*.zip"))
        extract(inner,unpacked/"package")
        bindings.append({"name":kind,"artifact_id":meta["id"],"artifact_digest":meta["digest"],
                         "url":f"https://github.com/{repository}/actions/runs/{run_id}/artifacts/{meta['id']}",
                         "inner_zip":inner.name,"inner_sha256":toolchain.sha256_file(inner),"bytes":inner.stat().st_size})
    package=output/"vs1-windows-study/package"
    report=json.loads((package/"vs1-report.json").read_text(encoding="utf-8"))
    if report["source_commit"]!=head or str(report["github_run_id"])!=run_id or report["source_tree_dirty"] or report["modes"]!=["G","V"]:
        raise ValueError("Unexpected source/run/mode identity")
    review=output/"vs1-review/package"
    if json.loads((review/"vs1-report.json").read_text(encoding="utf-8")) != report:
        raise ValueError("Review/player source binding differs")
    for key,name in (("matrix_sha256","vs1-matrix.json"),("gf1_plan_sha256","gf1-plan.json"),("decision_sha256","VS1_DECISION.md")):
        toolchain.verify_sha256(review/name,report[key])
    if report["gf1_baseline_commit"]!=vs1_delivery.GF1_BASE or report["gf1_plan_sha256"]!=toolchain.sha256_file(ROOT/"examples/vs1/gf1-plan.json") or report["decision_sha256"]!=toolchain.sha256_file(ROOT/"docs/VS1_DECISION.md"):
        raise ValueError("Delivered GF1 plan/decision differs from clean source head")
    vs1_delivery.verify(review)
    gf1_pairs=vs1_delivery.verify_gf1_pairs(review)
    vs1_delivery.audit(output/"vs1-windows-study"/bindings[0]["inner_zip"],report["export_files"])
    for name,digest in report["export_files"].items():
        toolchain.verify_sha256(package/name,digest)
    archive=cache/toolchain.EDITORS["Windows"].name
    toolchain.verify_sha256(archive,toolchain.EDITORS["Windows"].sha256)
    with zipfile.ZipFile(archive) as bundle:
        import hashlib
        expected=hashlib.sha256(bundle.read(engine.name)).hexdigest()
        toolchain.verify_sha256(engine,expected)
    profile=output/"profile"
    env=dict(os.environ,APPDATA=str(profile/"appdata"),LOCALAPPDATA=str(profile/"localappdata"))
    for key in ("VS1_TEST_ROOT","P1_TEST_SAVE_ROOT","P1_CAPTURE_DIR"):
        env.pop(key,None)
    sentinel=Path(env["APPDATA"])/"Godot/app_userdata/picross · P1/p1/saves/f01.json"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_bytes(b"normal-p1-save-sentinel")
    sentinel_hash=toolchain.sha256_file(sentinel)
    events=[]
    def launch(label,command,marker):
        start=time.monotonic()
        log=output/(label+".log")
        result=subprocess.run(list(map(str,command)),cwd=package,env=env,capture_output=True,
                              encoding="utf-8",errors="replace",timeout=300,creationflags=subprocess.CREATE_NO_WINDOW)
        text=result.stdout+result.stderr
        engine_log=output/(label+"-engine.log")
        if not text and engine_log.exists(): text=engine_log.read_text(encoding="utf-8")
        log.write_text(text,encoding="utf-8",newline="\n")
        if result.returncode or marker not in text or "SCRIPT ERROR:" in text or "ERROR:" in text:
            raise ValueError((label,result.returncode,text[:4000]))
        events.append({"name":label,"exit_code":result.returncode,"seconds":time.monotonic()-start,"marker":marker,"log_sha256":toolchain.sha256_file(log)})
        print(label,"OK",flush=True)
    for name in ("picross-vs1.exe","picross-vs1.console.exe"):
        label="direct-"+name
        launch(label,[package/name,"--rendering-driver","opengl3","--audio-driver","Dummy","--log-file",output/(label+"-engine.log"),"--","--vs1-smoke"],"VS1_START_OK")
    env["VS1_PROBE_OUTPUT"]=str(output)
    env["VS1_FRAME_SOURCE"]=str(ROOT/"prototypes/p1/tests/vs1_capture.gd")
    for stage in ("write","read","legacy-write","legacy-read","v-write","v-read"):
        env["VS1_STAGE"]=stage
        launch("export-"+stage,[engine,"--main-pack",package/"picross-vs1.exe","--rendering-driver","opengl3","--audio-driver","Dummy","--script",ROOT/"prototypes/p1/tests/vs1_roundtrip.gd"],f"VS1_ROUNDTRIP_{stage.upper().replace('-','_')}_OK")
        if stage=="legacy-write":
            root=Path(json.loads((output/"vs1-export-legacy-write.json").read_text(encoding="utf-8"))["root"])
            state=json.loads((root/"study-view.json").read_text(encoding="utf-8"))
            slot=json.loads((root/"vs10.json").read_text(encoding="utf-8"))
            if state["mode"]!="R" or state["requested_cell"]!=72 or slot["view"]["tool"]!="hand" or slot["view"]["center"]!=[0,0] or slot["view"]["zoom"]!=72:
                raise ValueError("Legacy fixture was overwritten before separate reader")
    env.pop("VS1_STAGE",None)
    env["VS1_GF1_PREFIX"]="delivered"
    for stage in ("write","read"):
        env["VS1_GF1_STAGE"]=stage
        launch("export-gf1-"+stage,[engine,"--main-pack",package/"picross-vs1.exe","--rendering-driver","opengl3","--audio-driver","Dummy","--script",ROOT/"prototypes/p1/tests/vs1_gf1_roundtrip.gd"],f"VS1_GF1_ROUNDTRIP_{stage.upper()}_OK")
    # PR #58's previously delivered player is a real old writer, not a fabricated save.
    old_head="7a0ebf65e1d14b3aa693f155c9de329de21603a5"
    old_run="37840143735"
    old_meta=json.loads(gh("api",f"repos/{repository}/actions/artifacts/11579406468"))
    if old_meta["expired"] or old_meta["name"]!="vs1-windows-study-"+old_head:
        raise ValueError("Bound old player artifact unavailable")
    old_outer=output/"old-vs1-player-artifact.zip"
    with old_outer.open("wb") as stream:
        subprocess.run(["gh","api",f"repos/{repository}/actions/artifacts/{old_meta['id']}/zip"],cwd=ROOT,stdout=stream,check=True,timeout=1200)
    if "sha256:"+toolchain.sha256_file(old_outer)!=old_meta["digest"]:
        raise ValueError("Old GitHub artifact digest differs")
    old_unpacked=output/"old-vs1-player"
    extract(old_outer,old_unpacked)
    old_inner=next(old_unpacked.glob("*.zip"))
    toolchain.verify_sha256(old_inner,"67207ca46056cfae66946df689e1bba2c21b734a7686e4d98c585acd40904eed")
    old_package=old_unpacked/"package"
    extract(old_inner,old_package)
    old_report=json.loads((old_package/"vs1-report.json").read_text(encoding="utf-8"))
    if old_report["source_commit"]!=old_head or str(old_report["github_run_id"])!=old_run:
        raise ValueError("Old player source/run differs")
    vs1_delivery.audit(old_inner,old_report["export_files"])
    for name,digest in old_report["export_files"].items(): toolchain.verify_sha256(old_package/name,digest)
    env["VS1_GF1_PREFIX"]="compatibility"
    for stage,delivered in (("old-write",old_package),("old-read",package)):
        env["VS1_GF1_STAGE"]=stage
        launch("export-gf1-"+stage,[engine,"--main-pack",delivered/"picross-vs1.exe","--rendering-driver","opengl3","--audio-driver","Dummy","--script",ROOT/"prototypes/p1/tests/vs1_gf1_roundtrip.gd"],f"VS1_GF1_ROUNDTRIP_{stage.upper().replace('-','_')}_OK")
    for key in ("VS1_GF1_PREFIX","VS1_GF1_STAGE"): env.pop(key,None)
    launch("export-native-window",[engine,"--main-pack",package/"picross-vs1.exe","--rendering-driver","opengl3","--audio-driver","Dummy","--script",ROOT/"prototypes/p1/tests/vs1_window.gd"],"VS1_WINDOW_OK")
    if toolchain.sha256_file(sentinel)!=sentinel_hash: raise ValueError("Normal save sentinel changed")
    evidence={"source_commit":head,"base_commit":report["base_commit"],"tested_checkout_commit":report["tested_checkout_commit"],
              "github_run_id":run_id,"platform":platform.platform(),"engine_archive_sha256":toolchain.sha256_file(archive),
              "export_files":report["export_files"],"bindings":bindings,"events":events,"sentinel_unchanged":True,"sentinel_sha256":sentinel_hash,
              "script_sha256":{name:toolchain.sha256_file(ROOT/"prototypes/p1/tests"/name) for name in ("vs1_roundtrip.gd","vs1_gf1_roundtrip.gd","vs1_window.gd","vs1_capture.gd")},
              "gf1_comparisons":gf1_pairs,
              "gf1_roundtrips":{p.name:json.loads(p.read_text(encoding="utf-8")) for p in output.glob("*-gf1-*.json")},
              "old_writer":{"source_commit":old_head,"main_integration":vs1_delivery.GF1_BASE,"github_run_id":old_run,"artifact_id":old_meta["id"],"artifact_digest":old_meta["digest"],"inner_sha256":toolchain.sha256_file(old_inner),"export_files":old_report["export_files"]},
              "images":{p.name:toolchain.sha256_file(p) for p in output.glob("vs1-*.png")},
              "environment":json.loads((output/"vs1-export-read.json").read_text(encoding="utf-8")),
              "window":json.loads((output/"vs1-window.json").read_text(encoding="utf-8")),
              "VS-M01":"Incomplete personal protocol; prior integration approved","VS-D01":"CONFIRMED","GF-M01":"OPEN","independent_review":"OPEN"}
    (output/"windows-download-verification.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("VS1_WINDOWS_DOWNLOAD_OK",head,flush=True)
    return evidence

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("head","run"):
        parser.add_argument("--"+name,required=True)
    for name in ("output-dir","engine","cache-dir"):
        parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args()
    probe(args.head,args.run,args.output_dir.resolve(),args.engine.resolve(),args.cache_dir.resolve())

if __name__=="__main__": main()
