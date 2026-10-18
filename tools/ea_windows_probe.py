"""Verify current CI artifact hashes and exercise its real Windows EXE/PCK."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import zipfile

import p1_preflight as tc
import p1_product as product
from native_results import read, validate_payload
from vs2_windows_probe import extract, direct_start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("head", "run"):
        parser.add_argument("--"+name, required=True)
    for name in ("output-dir", "engine", "cache-dir"):
        parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if platform.system() != "Windows": raise RuntimeError("Native Windows probe required")
    out = args.output_dir.resolve()
    out.mkdir()
    logs = out / "logs"
    logs.mkdir()

    def gh(*command):
        return subprocess.check_output(["gh", *command], cwd=root, timeout=300)

    repo = "repos/venomenon328/picross"
    info = json.loads(gh("api", f"{repo}/actions/runs/{args.run}"))
    if info["head_sha"] != args.head: raise ValueError("Run/source mismatch")
    # A web-only retry omits the already successful product job from filter=latest.
    jobs = json.loads(gh("api", f"{repo}/actions/runs/{args.run}/jobs?filter=all&per_page=100"))["jobs"]
    product_job = max((j for j in jobs if j["name"] == "product / product"), key=lambda j: j["id"])
    if product_job["conclusion"] != "success":
        raise ValueError("Product run has not succeeded")
    attempt = str(product_job["run_attempt"])
    artifacts = json.loads(gh("api", f"{repo}/actions/runs/{args.run}/artifacts"))["artifacts"]
    bindings = []
    for kind in ("player", "technical"):
        meta = next(a for a in artifacts if a["name"] == f"picross-p1-{kind}-{args.head}-{attempt}" and not a["expired"])
        archive = out / (kind+"-artifact.zip")
        archive.write_bytes(gh("api", f"{repo}/actions/artifacts/{meta['id']}/zip"))
        if meta["digest"] != "sha256:"+tc.sha256_file(archive): raise ValueError("Artifact digest mismatch")
        extract(archive, out/kind)
        bindings.append({key:meta[key] for key in ("id", "name", "digest", "size_in_bytes")})
    # CI-C delivers independent groups; verify every original byte and report
    # before using the export group's Windows player, including attempt binding.
    native_result = read(out/"technical/native-result.json")
    identity = native_result["identity"]
    if (identity["source_commit"] != args.head or identity["source_tree_dirty"]
            or str(identity["github_run_id"]) != args.run
            or str(identity["github_run_attempt"]) != attempt):
        raise ValueError("Unexpected native artifact identity/attempt")
    verified = validate_payload(native_result, out/"technical", out/"player")
    inner = next((out/"player").glob("*.zip"))
    package = out/"package"
    extract(inner, package)
    report = json.loads((package/"product-report.json").read_text(encoding="utf-8"))
    technical = read(out/"technical/export/product-report.json")
    for key in ("source_commit", "source_tree_dirty", "base_commit", "tested_checkout_commit", "github_run_id", "export_files"):
        if report[key] != technical[key]: raise ValueError("Player/technical identity mismatch: "+key)
    if report["source_commit"] != args.head or report["source_tree_dirty"] or str(report["github_run_id"]) != args.run:
        raise ValueError("Unexpected source identity")
    for name, digest in report["export_files"].items(): tc.verify_sha256(package/name, digest)
    asset = tc.EDITORS["Windows"]
    tc.verify_sha256(args.cache_dir/asset.name, asset.sha256)
    with zipfile.ZipFile(args.cache_dir/asset.name) as bundle:
        tc.verify_sha256(args.engine, hashlib.sha256(bundle.read(args.engine.name)).hexdigest())
    phases = []
    for name, command, marker in (
        ("exe-headless", ["--headless", "--", "--p1-smoke"], "P1_START_OK"),
        ("exe-native", ["--rendering-driver", "opengl3", "--", "--p1-smoke"], "P1_START_OK"),
    ):
        env = tc.isolated_environment(out/(name+"-profile"), "Windows")
        result = product.run_phase(name, [str(package/"picross-p1.console.exe")]+command, env, 180, logs)
        product.require_clean_output(result, marker)
        phases.append({k:v for k,v in result.items() if k != "output"})
    native_window = direct_start(package/"picross-p1.console.exe", tc.isolated_environment(out/"direct-profile", "Windows"), out, "direct-start")
    native = out/"native"
    native.mkdir()
    env = tc.isolated_environment(out/"pack-profile", "Windows")
    env["EA_PACK_OUTPUT"] = str(native)
    script = root/"game/tests/ea_pack.gd"
    for mode in ("write", "restart"):
        env["EA_PACK_MODE"] = mode
        result = product.run_phase("pack-"+mode, [str(args.engine), "--main-pack", str(package/"picross-p1.pck"),
            "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", str(script), "--", "--p1-capture"], env, 180, logs)
        product.require_clean_output(result, "EA_PACK_OK")
        phases.append({k:v for k,v in result.items() if k != "output"})
    binding = dict(head=args.head, base=report["base_commit"], checkout=report["tested_checkout_commit"], run=args.run,
        platform=platform.platform(), product_job_id=product_job["id"], product_run_attempt=report["github_run_attempt"],
        artifacts=bindings, inner_zip_sha256=tc.sha256_file(inner), export_files=report["export_files"],
        verified_technical_files=verified["files"], native_groups=verified["groups"], phases=phases, native_window=native_window,
        native_pck=[json.loads(p.read_text(encoding="utf-8")) for p in sorted(native.glob("*.json"))],
        probe_sha256=tc.sha256_file(script), engine_sha256=tc.sha256_file(args.engine),
        independent_review="OPEN EA-R01", owner_acceptance="OPEN EA-M01")
    (out/"windows-binding.json").write_text(json.dumps(binding, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print("EA_WINDOWS_OK", args.head)


if __name__ == "__main__": main()
