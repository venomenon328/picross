"""Bind a fresh Actions download to native Windows HF source/PCK evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import zipfile

import hf149_verify
import p1_preflight as toolchain
from vs2_windows_probe import extract

ROOT = Path(__file__).resolve().parents[1]
REPO = "venomenon328/picross"


def run(head: str, run_id: str, engine: Path, cache: Path, output: Path) -> dict:
    if platform.system() != "Windows" or output.exists():
        raise ValueError("Native Windows and fresh output directory required")
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if git("rev-parse","HEAD") != head or git("status","--porcelain"):
        raise ValueError("Clean delivered source head required")
    archive = cache / toolchain.EDITORS["Windows"].name
    toolchain.verify_sha256(archive,toolchain.EDITORS["Windows"].sha256)
    import hashlib
    with zipfile.ZipFile(archive) as bundle:
        toolchain.verify_sha256(engine,hashlib.sha256(bundle.read(engine.name)).hexdigest())
    output.mkdir(parents=True)
    def gh(*args):
        return subprocess.check_output(["gh",*args],cwd=ROOT,timeout=1200)
    info = json.loads(gh("api",f"repos/{REPO}/actions/runs/{run_id}"))
    if info["conclusion"] != "success" or info["head_sha"] != head:
        raise ValueError("Successful exact-head run required")
    artifacts = json.loads(gh("api",f"repos/{REPO}/actions/runs/{run_id}/artifacts"))["artifacts"]
    bindings = []
    for kind in ("player","technical"):
        meta = next(a for a in artifacts if a["name"] == f"picross-p1-{kind}-{head}" and not a["expired"])
        archive = output / f"{kind}-artifact.zip"
        archive.write_bytes(gh("api",f"repos/{REPO}/actions/artifacts/{meta['id']}/zip"))
        if "sha256:"+toolchain.sha256_file(archive) != meta["digest"]:
            raise ValueError("Artifact digest mismatch")
        extract(archive,output/kind)
        bindings.append({k:meta[k] for k in ("id","name","digest","size_in_bytes")})
    inner = next((output/"player").glob("*.zip"))
    package = output / "package"
    extract(inner,package)
    report = json.loads((package/"product-report.json").read_text(encoding="utf-8"))
    technical = json.loads((output/"technical/product-report.json").read_text(encoding="utf-8"))
    for key in ("source_commit","source_tree_dirty","base_commit","tested_checkout_commit","github_run_id","export_files"):
        if report[key] != technical[key]: raise ValueError("Player/technical identity mismatch")
    if report["source_commit"] != head or report["source_tree_dirty"] or str(report["github_run_id"]) != run_id:
        raise ValueError("Wrong delivered source/run")
    # Event/selection base and actual merge parent can differ when main moves.
    # Preserve both, and verify the actual checked-out integration via Git.
    git("fetch","--no-tags","origin",report["tested_checkout_commit"])
    parents = git("show","-s","--format=%P",report["tested_checkout_commit"]).split()
    if len(parents) != 2 or parents[1] != head:
        raise ValueError("Wrong tested integration parents")
    git("merge-base","--is-ancestor",report["base_commit"],parents[0])
    for name,digest in report["export_files"].items(): toolchain.verify_sha256(package/name,digest)
    for item in technical["selected_evidence"]["files"]:
        path = Path(item["file"])
        if path.is_absolute() or ".." in path.parts: raise ValueError("Unsafe evidence path")
        toolchain.verify_sha256(output/"technical/selected"/path,item["sha256"])
    ci_hf = hf149_verify.verify(output/"technical/selected/hf149")
    profile = output/"profile"
    env = toolchain.isolated_environment(profile,"Windows")
    logs = output/"logs"
    logs.mkdir()
    phases = []
    def phase(name,command,marker,environment):
        result = subprocess.run(command,env=environment,cwd=package,capture_output=True,timeout=300)
        log = result.stdout+result.stderr
        (logs/(name+".log")).write_bytes(log)
        decoded = log.decode("utf-8",errors="replace")
        if result.returncode or marker not in decoded or "SCRIPT ERROR:" in decoded or "ERROR:" in decoded:
            raise ValueError(name+" failed; see "+str(logs))
        phases.append({"name":name,"exit_code":result.returncode,"log":name+".log"})
    phase("exe-headless",[str(package/"picross-p1.console.exe"),"--headless","--","--p1-smoke"],"P1_START_OK",env)
    phase("exe-native",[str(package/"picross-p1.exe"),"--rendering-driver","opengl3","--","--p1-smoke"],"P1_WINDOW_INFO",env)
    native = output/"hf149"
    native.mkdir()
    env["HF149_OUTPUT"] = str(native)
    command = [str(engine),"--main-pack",str(package/"picross-p1.pck"),"--script",str(ROOT/"game/tests/hf149_probe.gd")]
    for stage in ("write","read"):
        stage_env = toolchain.isolated_environment(output/(stage+"-profile"),"Windows")
        stage_env.update(HF149_OUTPUT=str(native),HF149_STAGE=stage)
        phase("pck-"+stage,command+["--headless"],"HF149_"+stage.upper()+"_OK",stage_env)
    phase("pck-native",command+["--rendering-driver","opengl3","--audio-driver","Dummy"],"HF149_NATIVE_OK",env)
    native_hf = hf149_verify.verify(native)
    measurements = json.loads((native/"hf-native.json").read_text(encoding="utf-8"))
    from PIL import Image
    expected = {"font_sha256":toolchain.sha256_file(ROOT/"game/art/drawing/DelightCoffee-Regular.ttf"),
                "heading_sha256":toolchain.sha256_file(ROOT/"game/art/book/Fraunces.ttf")}
    for kind,filename in (("frame","frame-preview.png"),("paper","bp2-a-inventarband.png")):
        with Image.open(ROOT/"game/art/book"/filename) as image:
            expected[kind+"_rgba_sha256"] = hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()
    if measurements["resources"] != expected:
        raise ValueError("Actual PCK font/frame/paper pixels differ")
    result = {"head":head,"base":parents[0],"selection_base":report["base_commit"],
              "checkout":report["tested_checkout_commit"],"run":run_id,
              "artifacts":bindings,"inner_sha256":toolchain.sha256_file(inner),"exports":report["export_files"],
              "phases":phases,"ci_hf":ci_hf,"windows_hf":native_hf,"resources":expected,
              "host":platform.platform(),"display":{k:measurements[k] for k in ("dpi","screen_scale","screen","renderer")},
              "owner_acceptance":"HF-M01 remains separate and open"}
    (output/"windows-proof.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("head","run"): parser.add_argument("--"+name,required=True)
    for name in ("engine","cache-dir","output-dir"): parser.add_argument("--"+name,required=True,type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.head,args.run,args.engine.resolve(),args.cache_dir.resolve(),args.output_dir.resolve()),indent=2))
