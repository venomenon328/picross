"""One-off paired KAT-2 pages timeout diagnosis, not a selected-module pass."""
import argparse, json, os, platform, shutil, subprocess, sys, tempfile, time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--root", type=Path, required=True)
p.add_argument("--cache", type=Path, required=True)
p.add_argument("--expected-head", required=True)
a = p.parse_args()
root, cache = a.root.resolve(), a.cache.resolve()
assert subprocess.check_output(["git","rev-parse","HEAD"], cwd=root, text=True).strip() == a.expected_head
assert not subprocess.check_output(["git","status","--porcelain"], cwd=root, text=True).strip()
sys.path[:0] = [str(root / "tools"), str(root)]
os.chdir(root)
import p1_preflight as tc
from p1_product import run_phase, require_clean_output
from product_fixtures import copy_regression_game
from kat2_product import fixture
from native_results import validate_catalog_cases
began = time.monotonic()
editor = tc.EDITORS["Linux"]
urls = tc.official_asset_urls(tc.request_json(tc.RELEASE_API), (editor,))
tc.download_asset(urls[editor.name], cache / editor.name, editor.sha256, 1200)
with tempfile.TemporaryDirectory(prefix="hp-i2-pages-control-") as temp:
    work = Path(temp)
    engine = str(tc.extract_editor(cache / editor.name, work / "engine", "Linux"))
    environment = tc.isolated_environment(work, "Linux")
    environment["LIBGL_ALWAYS_SOFTWARE"] = "1"
    version = subprocess.check_output([engine,"--version"], env=environment, text=True).strip()
    assert version == tc.EXPECTED_VERSION
    project, saves, output, logs = [work / x for x in ("game","saves","output","logs")]
    for directory in (saves, output, logs):
        directory.mkdir()
    copy_regression_game(root, project)
    if (root / "tools/background_import.py").exists():
        import background_import
        background_import.prepare_import(project)
    shutil.copyfile(root / "game/art/content/yin_yang_001.png", project / "tests/fixtures/ke-reveal.png")
    imports = run_phase("import", [engine,"--headless","--path",str(project),"--import"], environment, 300, logs)
    require_clean_output(imports)
    fixture(project, saves, "pages")
    environment.update(P1_TEST_SAVE_ROOT=str(saves), KAT2_OUTPUT=str(output), KAT2_MODE="pages")
    imports = run_phase("kat2-pages-import", [engine,"--headless","--path",str(project),"--import"], environment, 300, logs)
    require_clean_output(imports)
    # Diagnostic ceiling only. Product's existing 300-second guard remains unchanged.
    result = run_phase("kat2-pages", ["xvfb-run","-a",engine,"--path",str(project),
        "--rendering-driver","opengl3","--audio-driver","Dummy","--script","res://tests/kat2_probe.gd","--","--p1-capture"],
        environment, 600, logs)
    print("HP_I2_PAGES_DIAGNOSTIC_PROCESS", json.dumps({k:v for k,v in result.items() if k != "output"}), flush=True)
    require_clean_output(result, "KAT2_PROBE_OK")
    report = json.loads((output / "pages.json").read_text())
    assert report["checks"] > 0 and not report["failures"]
    validate_catalog_cases(report)
    print("HP_I2_PAGES_DIAGNOSTIC_REPORT", json.dumps({
        "source_head":a.expected_head,"engine":version,"host":platform.platform(),"logical_cpus":os.cpu_count(),
        "process_seconds":result["seconds"],"elapsed_seconds":time.monotonic()-began,
        "scope":"Only existing pages fixture; not native.catalog success; diagnostic 600s ceiling",
        "report":report}), flush=True)
assert not subprocess.check_output(["git","status","--porcelain"], cwd=root, text=True).strip()
print("HP_I2_PAGES_DIAGNOSTIC_CLEAN", a.expected_head, flush=True)
