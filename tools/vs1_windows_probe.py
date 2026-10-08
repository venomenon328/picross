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
    launch("export-native-window",[engine,"--main-pack",package/"picross-vs1.exe","--rendering-driver","opengl3","--audio-driver","Dummy","--script",ROOT/"prototypes/p1/tests/vs1_window.gd"],"VS1_WINDOW_OK")
    if toolchain.sha256_file(sentinel)!=sentinel_hash: raise ValueError("Normal save sentinel changed")
    evidence={"source_commit":head,"base_commit":report["base_commit"],"tested_checkout_commit":report["tested_checkout_commit"],
              "github_run_id":run_id,"platform":platform.platform(),"engine_archive_sha256":toolchain.sha256_file(archive),
              "export_files":report["export_files"],"bindings":bindings,"events":events,"sentinel_unchanged":True,"sentinel_sha256":sentinel_hash,
              "script_sha256":{name:toolchain.sha256_file(ROOT/"prototypes/p1/tests"/name) for name in ("vs1_roundtrip.gd","vs1_window.gd")},
              "images":{p.name:toolchain.sha256_file(p) for p in output.glob("vs1-export-*.png")},
              "environment":json.loads((output/"vs1-export-read.json").read_text(encoding="utf-8")),
              "window":json.loads((output/"vs1-window.json").read_text(encoding="utf-8")),
              "VS-M01":"OPEN","VS-D01":"OPEN","independent_review":"OPEN"}
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
