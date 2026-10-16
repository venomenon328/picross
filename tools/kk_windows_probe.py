"""Bind native KK routes and, optionally, the downloaded CI EXE/PCK to a clean head."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

import kat2_product
import p1_preflight as tc
import p1_product as product


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--head", required=True)
    parser.add_argument("--run", help="Successful CI run; also downloads and starts its actual Windows player")
    for name in ("output-dir", "engine", "cache-dir"):
        parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    if platform.system() != "Windows":
        raise RuntimeError("Native Windows required")
    root = Path(__file__).resolve().parents[1]
    identity = product.source_identity(root)
    if identity["source_commit"] != args.head or identity["source_tree_dirty"]:
        raise ValueError("Native source must be the requested clean head")
    crops = root/"docs/evidence/kk/native-crops.json"
    expected = json.loads(crops.read_text(encoding="utf-8"))
    for name, digest in expected["runtime_files"].items():
        tc.verify_sha256(root/name, digest)
    out = args.output_dir.resolve()
    out.mkdir(parents=True)
    logs = out / "logs"
    logs.mkdir()
    asset = tc.EDITORS["Windows"]
    tc.official_asset_urls(tc.request_json(tc.RELEASE_API), (asset, tc.TEMPLATES))
    for pinned in (asset, tc.TEMPLATES):
        tc.verify_sha256(args.cache_dir/pinned.name, pinned.sha256)
    with zipfile.ZipFile(args.cache_dir/asset.name) as bundle:
        tc.verify_sha256(args.engine, hashlib.sha256(bundle.read(args.engine.name)).hexdigest())
    phases = []

    with tempfile.TemporaryDirectory(prefix="picross-kk-windows-") as temporary:
        workspace = Path(temporary)
        environment = tc.isolated_environment(workspace, "Windows")

        def phase(name, command, marker=None, phase_env=None):
            result = product.run_phase(name, command, phase_env or environment, 300, logs)
            product.require_clean_output(result, marker)
            phases.append({key:value for key,value in result.items() if key != "output"})

        def python_phase(name, action):
            result = action()
            phases.append(dict(name=name, exit_code=0))
            return result

        phase("version", [str(args.engine), "--version"], tc.EXPECTED_VERSION)
        summary, files = kat2_product.run(root, workspace, out, str(args.engine),
                                         environment, phase, python_phase, "Windows")
    for capture in expected["captures"]:
        tc.verify_sha256(crops.parent/capture["file"], capture["sha256"])
        tc.verify_sha256(out/"kat2"/capture["file"], capture["sha256"])
    player = None
    if args.run:
        # Reuse the existing digest/inventory/source checks, real EXE starts,
        # owned HWND capture and EA PCK write/restart regression unchanged.
        subprocess.run([sys.executable, str(root/"tools/ea_windows_probe.py"),
            "--head", args.head, "--run", args.run, "--engine", str(args.engine),
            "--cache-dir", str(args.cache_dir), "--output-dir", str(out/"ci-build")],
            cwd=root, check=True)
        player = json.loads((out/"ci-build/windows-binding.json").read_text(encoding="utf-8"))
    binding = dict(**identity, platform=platform.platform(), engine=tc.EXPECTED_VERSION,
        engine_sha256=tc.sha256_file(args.engine), run=args.run, phases=phases,
        committed_native_crops=dict(manifest_sha256=tc.sha256_file(crops),
                                    reproduced=len(expected["captures"])),
        reports=[{key:report[key] for key in ("mode", "checks", "failures", "adapter", "display_server")}
                 for report in summary["reports"]],
        files=[dict(file=p.relative_to(out).as_posix(), bytes=p.stat().st_size, sha256=tc.sha256_file(p))
               for p in files], player=player,
        independent_review="OPEN KK-R01", owner_acceptance="OPEN KK-M01")
    (out/"windows-binding.json").write_text(json.dumps(binding, ensure_ascii=False, indent=2)+"\n",
                                          encoding="utf-8", newline="\n")
    print("KK_WINDOWS_OK", args.head, "CI player started" if player else "native source only; CI player pending")


if __name__ == "__main__":
    main()
