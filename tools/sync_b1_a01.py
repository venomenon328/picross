"""Single-use Windows evidence for SYNC-B1-A01 at the checked-out product commit."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile

root = Path.cwd()
sys.path[:0] = [str(root), str(root / "tools")]
import background_import
import p1_preflight as tc
import p1_product
import product_fixtures

sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
assert platform.system() == "Windows" and sha == sys.argv[1]
output = Path(os.environ["RUNNER_TEMP"]) / "sync-b1-a01-windows.zip"
with tempfile.TemporaryDirectory(prefix="sync-b1-a01-") as tmp:
    work = Path(tmp)
    env = tc.isolated_environment(work, "Windows")
    env.update(TEMP=str(work), TMP=str(work), TMPDIR=str(work))
    files = work / "originals"
    files.mkdir()
    project = work / "game"
    product_fixtures.copy_regression_game(root, project)
    background_import.prepare_import(project)
    asset = tc.EDITORS["Windows"]
    url = tc.official_asset_urls(tc.request_json(tc.RELEASE_API), (asset,))[asset.name]
    archive = work / asset.name
    tc.download_asset(url, archive, asset.sha256, 300)
    engine = tc.extract_editor(archive, work / "editor", "Windows")
    base = [str(engine), "--headless", "--path", str(project)]

    def run(name, command, marker=None):
        result = subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        raw = result.stdout
        (files / (name + ".log")).write_bytes(raw)
        log = raw.decode("utf-8", errors="strict")
        if result.returncode or (marker and marker not in log) or any(x in log for x in ("SCRIPT ERROR:", "ERROR:", "FAIL:")):
            raise ValueError(name + ": " + log[-4000:])
        print(name, "passed", flush=True)

    shutil.copyfile(Path(__file__).with_name("sync_b1_focus.gd"), project / "tests/focus.gd")
    run("version", [str(engine), "--version"], tc.EXPECTED_VERSION)
    with p1_product.import_settings(base + ["--import"]):
        run("import", base + ["--import"])
    link = p1_product.prepare_profile_link(env,work,"Windows")
    try:
        run("profile",base + ["--script","res://tests/focus.gd"],"SYNC_B1_CORE_OK")
    finally:
        link.rmdir()
    summary = p1_product.run_integration(files, work, env, base, run, "Windows")
    run("guest",base + ["--","--p1-smoke"],"P1_START_OK")
    (files/"binding.json").write_text(json.dumps(dict(product=sha, proof=os.environ["GITHUB_SHA"],
        run=os.environ["GITHUB_RUN_ID"], attempt=os.environ["GITHUB_RUN_ATTEMPT"],
        windows=platform.platform(), godot=tc.EXPECTED_VERSION, editor_archive_sha256=asset.sha256,
        appdata=env["APPDATA"], localappdata=env["LOCALAPPDATA"], history=summary),indent=2)+"\n",encoding="utf-8")
    names = ["binding.json","version.log","profile.log","integration-writer.log","integration-reader.log","guest.log",
             *("integration/"+name for name in ("plan.json","trace.jsonl","foreign-slots.json","writer-account.json",
                "reader-account.json","writer-save.json","reader-save.json","writer-journal.json","reader-journal.json","summary.json"))]
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as bundle:
        for name in names:
            bundle.write(files/name,name)
    print(output.name, output.stat().st_size, hashlib.sha256(output.read_bytes()).hexdigest())
