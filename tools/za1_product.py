"""Isolated data registration, regular native play and actual PCK evidence for ZA-1."""
from pathlib import Path
import json
import shutil
import hashlib
import time
import tempfile

import p1_preflight as toolchain
from native_results import bind_files


def require_inventory(project, inventory):
    if bind_files(project) != inventory:
        raise toolchain.PreflightError("ZA-1 prepared import inventory differs")


def prepare_imports(imported_base, workspace):
    """Snapshot only the just-imported inputs, before any native test runs."""
    began = time.perf_counter()
    inventory = bind_files(imported_base)
    project = workspace / "za1-checkout/game"
    shutil.copytree(imported_base, project)
    require_inventory(project, inventory)
    require_inventory(imported_base, inventory)
    return inventory, dict(inventory_sha256=hashlib.sha256(
        json.dumps(inventory, sort_keys=True).encode()).hexdigest(),
        files=len(inventory), bytes=sum(row['bytes'] for row in inventory),
        source_unchanged_at_copy=True, preparation_seconds=time.perf_counter()-began)


def audit_pack(root, engine, executable, environment, run_phase, count, label, *, background_inventory=None):
    pack = executable.with_suffix(".pck")
    if not pack.is_file() or pack.stat().st_size <= 4:
        raise toolchain.PreflightError("Missing/empty separate player PCK")
    with pack.open("rb") as stream:
        if stream.read(4) != b"GDPC":
            raise toolchain.PreflightError("Invalid separate player PCK header")
    env = environment.copy()
    env["ZA1_PACK_COUNT"] = str(count)
    env["HP_BACKGROUND_PACK_TARGET"] = "windows"
    with tempfile.TemporaryDirectory(prefix="picross-pack-backgrounds-") as temporary:
        if background_inventory is not None:
            expected = Path(temporary) / "expected.json"
            expected.write_text(json.dumps(background_inventory), encoding="utf-8")
            env["HP_BACKGROUND_EXPECTED"] = str(expected)
        run_phase(label, [engine, "--headless", "--main-pack", str(pack), "--script",
                      str(root / "game/tests/content_pack_probe.gd")], "CONTENT_PACK_OK", phase_env=env)
    return {"status": "success", "selected": count, "executable_sha256": toolchain.sha256_file(executable),
            "pack_file": pack.name, "pack_sha256": toolchain.sha256_file(pack), "pack_bytes": pack.stat().st_size,
            "method": "external native probe against actual separate PCK"}


def run(root, workspace, output, engine, environment, run_phase, python_phase, host, prepared):
    from tools.puzzle_production.za1_fixtures import replay, isolated_checkout
    from tools.puzzle_production.content_registry import check_checkout
    checkout = workspace / "za1-checkout"
    from product_fixtures import install_runtime_fixtures
    inventory, reuse = prepared
    began = time.perf_counter()
    require_inventory(checkout / "game", inventory)
    reuse.update(prepared_unchanged=True, verification_seconds=time.perf_counter()-began)
    isolated_checkout(checkout)
    python_phase("za1-test-only-registration", lambda: replay(workspace / "za1-replay", checkout))
    project = checkout / "game"
    check_checkout(checkout)
    install_runtime_fixtures(root, project, append=True)
    directory = output / "za1"
    directory.mkdir()
    saves = workspace / "za1-saves"
    env = environment.copy()
    env.update(P1_TEST_SAVE_ROOT=str(saves), ZA1_OUTPUT=str(directory))
    run_phase("za1-import", [engine,"--headless","--path",str(project),"--import"], phase_env=env)
    guards = env.copy()
    guards["P1_TEST_SAVE_ROOT"] = str(workspace / "za1-save-guards")
    run_phase("za1-save-recovery",[engine,"--headless","--path",str(project),"--script","res://tests/za1_save_cases.gd"],"ZA1_SAVE_OK",phase_env=guards)
    command = [engine,"--path",str(project),"--rendering-driver","opengl3","--audio-driver","Dummy"]
    if host == "Linux":
        command = ["xvfb-run","-a"]+command
        env["LIBGL_ALWAYS_SOFTWARE"] = "1"
    checks = []
    env.update(ZA1_ID="pz-test-direct-mono", ZA1_STAGE="seed")
    run_phase("za1-seed-old-slots", command + ["--script","res://tests/za1_probe.gd","--","--p1-capture"], "ZA1_PROBE_OK",phase_env=env)
    for key in ("pz-test-direct-mono", "pz-test-direct-color"):
        env["ZA1_ID"] = key
        stages = ("partial","finish","read","oldreset","reset") if key.endswith("color") else ("partial","finish","read","reset")
        for stage in stages:
            changed_slot = "t01" if stage == "oldreset" else "slot_"+key
            before = {p.name:toolchain.sha256_file(p) for p in saves.glob("*")
                      if p.is_file() and not p.name.startswith(changed_slot+".")}
            env["ZA1_STAGE"] = stage
            run_phase("za1-"+key+"-"+stage, command + ["--script","res://tests/za1_probe.gd","--","--p1-capture"], "ZA1_PROBE_OK",phase_env=env)
            if any(not (saves/n).is_file() or toolchain.sha256_file(saves/n) != h for n,h in before.items()):
                raise toolchain.PreflightError("ZA-1 changed a foreign save during "+stage)
            result = json.loads((directory/(key+"-"+stage+".json")).read_text())
            if result["failures"]: raise toolchain.PreflightError("ZA-1 probe failure")
            checks.append({"id":key,"stage":stage,"checks":result["checks"],"unchanged_slots":before})
    build = project / "build/windows"
    build.mkdir(parents=True)
    run_phase("za1-windows-export",[engine,"--headless","--path",str(project),"--export-debug","P1 Windows x86_64",str(build/"picross-p1.exe")],phase_env=env)
    pack = audit_pack(root,engine,build/"picross-p1.exe",env,run_phase,
                      sum(e["visible"] for e in json.loads((project / "data/registry.json").read_text(encoding="utf-8"))["entries"]),"za1-pck-resources")
    if host == "Windows":
        run_phase("za1-windows-exported-start",[str(build/"picross-p1.console.exe"),"--headless","--","--p1-smoke"],"P1_START_OK",phase_env=env)
    summary = {"format":"picross-za1-product-v1","test_only":True,"registered":4,"regular_processes":10,
               "checks":checks,"pck":pack,"windows_exported_start":host == "Windows",
               "import_reuse":reuse}
    (directory/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    # Actual native pixels are asserted in-process; only functional reports leave it.
    return summary, sorted(directory.glob("*.json"))
