"""Download the bound regular VS2 player and test its actual Windows/PCK paths."""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import platform
import re
import struct
import subprocess
import time
import zipfile
from pathlib import Path
import p1_preflight as toolchain
import vs2_delivery
from p1_product import player_extras
from gp48_delivery import verify_player_package
from vs1_windows_probe import extract

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "venomenon328/picross"
OLD_HEAD = "8b762dd9aaf976361cba44e3b25004e09edde348"
OLD_RUN = "37921979562"


def embedded_pack(executable: Path) -> dict:
    data = executable.read_bytes()
    # Godot appends the pack length (uint64 LE) and GDPC magic after the pack.
    if data[-4:] != b"GDPC":
        raise ValueError("Missing embedded PCK footer")
    length = struct.unpack("<Q", data[-12:-4])[0]
    start = len(data) - 12 - length
    if start < 0 or data[start:start+4] != b"GDPC":
        raise ValueError("Invalid embedded PCK bounds/header")
    return dict(offset=start, bytes=length, sha256=hashlib.sha256(data[start:-12]).hexdigest())


def direct_start(executable: Path, env: dict, output: Path, label: str) -> dict:
    """No arguments or player test entry point; inspect only our owned window."""
    from PIL import Image
    user = ctypes.windll.user32
    kernel = ctypes.windll.kernel32
    user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    owned = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    @callback_type
    def visit(hwnd, _):
        if not user.IsWindowVisible(hwnd): return True
        pid = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        handle = kernel.OpenProcess(0x1000, False, pid.value)
        if handle:
            name = ctypes.create_unicode_buffer(32768)
            size = wintypes.DWORD(len(name))
            if kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(size)):
                if Path(name.value).resolve() == executable.with_name("picross-p1.exe").resolve():
                    owned.append((hwnd, pid.value))
            kernel.CloseHandle(handle)
        return True
    process = subprocess.Popen([str(executable)], cwd=executable.parent, env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    started = time.monotonic()
    deadline = started+30
    while time.monotonic() < deadline and not owned:
        user.EnumWindows(visit, 0)
        time.sleep(0.1)
    if len(owned) != 1:
        process.terminate()
        raise ValueError((label, "Expected exactly one owned native player window", owned))
    hwnd, pid = owned[0]
    client = wintypes.RECT()
    user.GetClientRect(hwnd, ctypes.byref(client))
    width, height = client.right, client.bottom
    if width < 1280 or height < 720:
        raise ValueError("Unexpected regular startup client")
    path = output/(label+".png")
    # Capture only the verified owned HWND, even when another application
    # covers it. Desktop screenshots could accidentally include user content.
    gdi = ctypes.windll.gdi32
    user.GetDC.restype = wintypes.HDC
    user.GetDC.argtypes = [wintypes.HWND]
    user.PrintWindow.argtypes = [wintypes.HWND,wintypes.HDC,wintypes.UINT]
    user.ReleaseDC.argtypes = [wintypes.HWND,wintypes.HDC]
    gdi.CreateCompatibleDC.restype = wintypes.HDC
    gdi.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi.CreateCompatibleBitmap.argtypes = [wintypes.HDC,ctypes.c_int,ctypes.c_int]
    gdi.SelectObject.restype = wintypes.HANDLE
    gdi.SelectObject.argtypes = [wintypes.HDC,wintypes.HANDLE]
    gdi.DeleteObject.argtypes = [wintypes.HANDLE]
    gdi.DeleteDC.argtypes = [wintypes.HDC]
    gdi.GetDIBits.argtypes = [wintypes.HDC,wintypes.HBITMAP,wintypes.UINT,wintypes.UINT,ctypes.c_void_p,ctypes.c_void_p,wintypes.UINT]
    dc = user.GetDC(hwnd)
    memory = gdi.CreateCompatibleDC(dc)
    bitmap = gdi.CreateCompatibleBitmap(dc,width,height)
    previous = gdi.SelectObject(memory,bitmap)
    captured = None
    capture_attempts = 0
    dpi = user.GetDpiForWindow(hwnd)
    try:
        # BITMAPINFOHEADER: top-down, uncompressed BGRA.
        header = struct.pack('<IiiHHIIiiII',40,width,-height,1,32,0,width*height*4,0,0,0,0)
        pixels = ctypes.create_string_buffer(width*height*4)
        # HWND creation precedes the first rendered frame. Keep the original
        # startup deadline and blank-image assertion, but wait for that frame.
        while time.monotonic() < deadline:
            if not user.IsWindow(hwnd):
                raise ValueError("Owned player window closed before its first frame")
            capture_attempts += 1
            gdi.SelectObject(memory,bitmap)
            if not user.PrintWindow(hwnd,memory,3):
                raise ValueError("Owned window capture failed")
            gdi.SelectObject(memory,previous)
            if gdi.GetDIBits(memory,bitmap,0,height,pixels,header,0)!=height:
                raise ValueError("Owned window bitmap read failed")
            captured = Image.frombytes('RGB',(width,height),pixels.raw,'raw','BGRX')
            if len(captured.getcolors(width*height)) >= 16:
                break
            time.sleep(0.1)
        else:
            raise ValueError("Owned window capture stayed blank within startup deadline")
        frame_ready_seconds = round(time.monotonic()-started,3)
        captured.save(path)
    finally:
        gdi.SelectObject(memory,previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(memory)
        user.ReleaseDC(hwnd,dc)
        user.PostMessageW(hwnd,0x0010,0,0)
    user.PostMessageW(hwnd, 0x0010, 0, 0)
    process.wait(timeout=30)
    deadline = time.monotonic()+30
    while user.IsWindow(hwnd) and time.monotonic() < deadline: time.sleep(0.1)
    if user.IsWindow(hwnd) or process.returncode:
        raise ValueError("Player did not close normally")
    return dict(name=label, executable=executable.name, arguments=[], exit_code=process.returncode,
                client=[width,height], dpi=dpi, windows_scale=dpi/96, pid=pid,
                frame_ready_seconds=frame_ready_seconds, capture_attempts=capture_attempts,
                capture_method="PrintWindow: owned client only", screenshot=path.name, screenshot_sha256=toolchain.sha256_file(path))


def probe(head: str, run_id: str, output: Path, engine: Path, cache: Path) -> dict:
    if platform.system() != "Windows" or not re.fullmatch(r"[0-9a-f]{40}",head) or not run_id.isdigit():
        raise ValueError("Native Windows, full source head and numeric run required")
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=head or subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip():
        raise ValueError("Probe scripts require a clean delivered source head")
    if output.exists(): raise ValueError("Use a fresh evidence/profile directory")
    output.mkdir(parents=True)
    def gh(*args): return subprocess.check_output(["gh",*args],cwd=ROOT,timeout=1200)
    def download(run, kind, source, packed=True):
        run_info=json.loads(gh("api",f"repos/{REPOSITORY}/actions/runs/{run}"))
        if run_info["conclusion"]!="success": raise ValueError("Product run is not successful")
        artifacts=json.loads(gh("api",f"repos/{REPOSITORY}/actions/runs/{run}/artifacts"))["artifacts"]
        meta=next(a for a in artifacts if a["name"]==kind+"-"+source and not a["expired"])
        stem=("old-" if source==OLD_HEAD else "")+kind
        outer=output/(stem+"-artifact.zip")
        with outer.open("wb") as stream:
            subprocess.run(["gh","api",f"repos/{REPOSITORY}/actions/artifacts/{meta['id']}/zip"],cwd=ROOT,stdout=stream,check=True,timeout=1200)
        if "sha256:"+toolchain.sha256_file(outer)!=meta["digest"]: raise ValueError("Artifact digest differs")
        destination=output/stem
        extract(outer,destination)
        binding=dict(name=meta["name"],artifact_id=meta["id"],artifact_digest=meta["digest"],
                     url=f"https://github.com/{REPOSITORY}/actions/runs/{run}/artifacts/{meta['id']}")
        if not packed:
            return destination, binding
        inner=next(destination.glob("*.zip"))
        extract(inner,destination/"package")
        binding.update(inner_zip=inner.name,inner_sha256=toolchain.sha256_file(inner),bytes=inner.stat().st_size)
        return destination/"package",binding
    package,player_binding=download(run_id,"picross-p1-player",head)
    review,review_binding=download(run_id,"picross-p1-technical",head,packed=False)
    report=json.loads((package/"product-report.json").read_text(encoding="utf-8"))
    review_report=json.loads((review/"product-report.json").read_text(encoding="utf-8"))
    for key in ("source_commit","source_tree_dirty","base_commit","tested_checkout_commit","github_run_id","export_files"):
        if report[key]!=review_report[key]: raise ValueError("Evidence/player identity differs: "+key)
    expected_base=subprocess.check_output(["git","merge-base",head,"origin/main"],cwd=ROOT,text=True).strip()
    if report["source_commit"]!=head or report["source_tree_dirty"] or str(report["github_run_id"])!=run_id or report["base_commit"]!=expected_base or report["status"]!="success":
        raise ValueError("Unexpected product identity")
    extras_dir=output/"package-inputs"
    extras_dir.mkdir()
    expected={"picross-p1.exe","picross-p1.console.exe","README.txt","product-report.json"} | set(player_extras(ROOT,extras_dir))
    player_zip=package.parent/player_binding["inner_zip"]
    verify_player_package(player_zip,report,expected)
    for entry in review_report["selected_evidence"]["files"]:
        relative=Path(entry["file"])
        if relative.is_absolute() or ".." in relative.parts: raise ValueError("Unsafe evidence path")
        toolchain.verify_sha256(review/"selected"/relative,entry["sha256"])
    matrix=json.loads((review/"selected/vs2-renders/vs2-matrix.json").read_text(encoding="utf-8"))
    vs2_delivery.verify_records(matrix)
    if review_report["visual"]["vs2"]["v2"]["plan_sha256"] != toolchain.sha256_file(ROOT / "examples/vs2/v2-plan.json"):
        raise ValueError("Delivered V2 plan identity differs")
    if review_report["visual"]["vs2"]["records"]!=304 or review_report["visual"]["vs2"]["rendered"]!=23:
        raise ValueError("Missing current native VS2 coverage")
    archive=cache/toolchain.EDITORS["Windows"].name
    toolchain.verify_sha256(archive,toolchain.EDITORS["Windows"].sha256)
    with zipfile.ZipFile(archive) as bundle: toolchain.verify_sha256(engine,hashlib.sha256(bundle.read(engine.name)).hexdigest())
    old,old_binding=download(OLD_RUN,"picross-p1-player",OLD_HEAD)
    old_report=json.loads((old/"product-report.json").read_text(encoding="utf-8"))
    if old_report["source_commit"]!=OLD_HEAD or str(old_report["github_run_id"])!=OLD_RUN or old_report["source_tree_dirty"]:
        raise ValueError("Wrong genuine old writer")
    for name,digest in old_report["export_files"].items(): toolchain.verify_sha256(old/name,digest)
    profile=output/"profile"
    env=toolchain.isolated_environment(profile,"Windows")
    for key in ("P1_TEST_SAVE_ROOT","P1_CAPTURE_DIR","VS1_TEST_ROOT"): env.pop(key,None)
    env["VS2_PROBE_OUTPUT"]=str(output)
    study=Path(env["APPDATA"])/"Godot/app_userdata/picross · P1/vs1/revision-1/study-view.json"
    study.parent.mkdir(parents=True)
    study.write_bytes(b"untouched historical study sentinel")
    study_hash=toolchain.sha256_file(study)
    events=[]
    def launch(label,delivered,script,marker):
        log=output/(label+".log")
        command=[str(engine),"--main-pack",str(delivered/"picross-p1.exe"),"--rendering-driver","opengl3","--audio-driver","Dummy","--script",str(ROOT/"prototypes/p1/tests"/script)]
        result=subprocess.run(command,cwd=delivered,env=env,capture_output=True,encoding="utf-8",errors="replace",timeout=300,creationflags=subprocess.CREATE_NO_WINDOW)
        text=result.stdout+result.stderr
        log.write_text(text,encoding="utf-8",newline="\n")
        if result.returncode or marker not in text or "ERROR:" in text:
            raise ValueError((label,result.returncode,text[:5000]))
        events.append(dict(name=label,exit_code=result.returncode,marker=marker,log_sha256=toolchain.sha256_file(log)))
        print(label,"OK",flush=True)
    # Fresh, real old partial saves and real old completed first sheet.
    # Both delivered executables run without any arguments in all three cases.
    for state in ("fresh","partial","completed"):
        if state!="fresh":
            env["VS2_STAGE"]="legacy-write"
            env["VS2_COMPLETE_FIRST"]="1" if state=="completed" else "0"
            env.pop("VS2_PACK_AUDIT",None)
            launch("old-writer-"+state,old,"vs2_roundtrip.gd","VS2_ROUNDTRIP_LEGACY_WRITE_OK")
        for name in ("picross-p1.exe","picross-p1.console.exe"):
            events.append(direct_start(package/name,env,output,"direct-"+state+"-"+name))
            print("direct",state,name,"OK",flush=True)
        if state!="fresh":
            env.update(VS2_STAGE="legacy-read",VS2_PACK_AUDIT="1")
            launch("new-reader-"+state,package,"vs2_roundtrip.gd","VS2_ROUNDTRIP_LEGACY_READ_OK")
    for stage in ("write","read"):
        env.update(VS2_STAGE=stage,VS2_PACK_AUDIT="1")
        launch("new-"+stage,package,"vs2_roundtrip.gd","VS2_ROUNDTRIP_"+stage.upper()+"_OK")
    env.pop("VS2_STAGE",None)
    launch("native-window",package,"vs2_window.gd","VS2_WINDOW_OK")
    env["VS2_V2_CAPTURE_DIR"] = str(output)
    for stage in ("write", "read"):
        env["VS2_V2_STAGE"] = stage
        launch("v2-" + stage, package, "vs2_v2_tests.gd", "VS2_V2_" + stage.upper() + "_OK")
    v2 = vs2_delivery.verify_v2(output)
    if toolchain.sha256_file(study)!=study_hash: raise ValueError("Historical study data changed")
    packs={"picross-p1.exe":embedded_pack(package/"picross-p1.exe")}
    console=package/"picross-p1.console.exe"
    if console.read_bytes()[-4:]==b"GDPC":
        packs[console.name]=embedded_pack(console)
        if packs["picross-p1.exe"]["sha256"]!=packs[console.name]["sha256"]:
            raise ValueError("EXE pair embeds different packs")
    else:
        # Official Godot console shim starts the same-name regular EXE; its
        # actual owned native process is checked by the no-argument launches.
        packs[console.name]=dict(console_shim=True,load_target="picross-p1.exe",sha256=packs["picross-p1.exe"]["sha256"])
    evidence=dict(source_commit=head,base_commit=report["base_commit"],tested_checkout_commit=report["tested_checkout_commit"],github_run_id=run_id,
                  plan_sha256=toolchain.sha256_file(ROOT/"examples/vs2/v1-plan.json"),
                  plan_amendment_sha256=toolchain.sha256_file(ROOT/"examples/vs2/v1-plan-amendment.json"),
                  v2_plan_sha256=toolchain.sha256_file(ROOT/"examples/vs2/v2-plan.json"),v2=v2,
                  platform=platform.platform(),bindings=[player_binding,review_binding],export_files=report["export_files"],embedded_packs=packs,
                  engine_archive_sha256=toolchain.sha256_file(archive),engine_sha256=toolchain.sha256_file(engine),events=events,
                  old_writer=dict(source_commit=OLD_HEAD,main_integration=vs2_delivery.BASE,github_run_id=OLD_RUN,binding=old_binding,export_files=old_report["export_files"]),
                  scripts={name:toolchain.sha256_file(ROOT/"prototypes/p1/tests"/name) for name in ("vs2_window.gd","vs2_roundtrip.gd","vs2_measurements.gd","vs2_v1_cases.gd","vs2_v2_cases.gd","vs2_v2_tests.gd")},
                  matrix_records=len(matrix["records"]),historical_comparison="not repeated under CI policy #63",
                  rounds={p.name:json.loads(p.read_text(encoding="utf-8")) for p in output.glob("vs2-*.json")},
                  images={p.name:toolchain.sha256_file(p) for p in output.glob("*.png")},
                  study_sentinel_unchanged=True,study_sentinel_sha256=study_hash,independent_review="OPEN",VS2_M01="OPEN",merge_authorized=False)
    target=output/"windows-download-verification.json"
    target.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("VS2_WINDOWS_DOWNLOAD_OK",head,flush=True)
    return evidence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("head","run"): parser.add_argument("--"+name,required=True)
    for name in ("output-dir","engine","cache-dir"): parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args()
    probe(args.head,args.run,args.output_dir.resolve(),args.engine.resolve(),args.cache_dir.resolve())


if __name__=="__main__": main()
