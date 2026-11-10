"""One-time HP-I2 T01/T02 producer on a separate, product-bound review ref."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--product-head", required=True)
    args = parser.parse_args()
    repo, work, output, cache = (p.resolve() for p in (args.root, args.work, args.output, args.cache))
    scripts = Path(__file__).resolve().parent
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True).strip()
    if head != args.product_head or status:
        raise ValueError("T01/T02 require the exact clean product checkout")
    if platform.system() != "Linux" or not shutil.which("xvfb-run"):
        raise ValueError("This one-time producer requires Linux native Xvfb/Mesa")
    if work.exists() or output.exists():
        raise ValueError("Evidence work and delivery paths must be new")
    work.mkdir(parents=True)
    output.mkdir(parents=True)
    write(work / "OWNER.json", {"purpose":"HP-I2-T01-T02", "product_head":head, "disposable":True})
    sys.path[:0] = [str(repo), str(repo / "tools"), str(scripts)]
    os.chdir(repo)
    from hp_i2_fixtures import build_fixture
    from hp_i2_delivery import run_delivery
    import background_import as backgrounds
    from product_fixtures import copy_regression_game, restore_player_catalog
    import p1_preflight as tc
    from build_web_player import extract_web_templates
    from p1_product import run_phase as phase, require_clean_output
    began = time.monotonic()
    phase_rows = []
    logs = work / "logs"
    logs.mkdir()
    environment = tc.isolated_environment(work, "Linux")
    environment["LIBGL_ALWAYS_SOFTWARE"] = "1"

    def run_phase(label, command, *, phase_env=None):
        started = time.monotonic()
        print("HP_I2_PHASE " + label, flush=True)
        native_book = label.startswith("t01-") and "--headless" not in command
        phase_logs = logs / label if native_book else logs
        phase_logs.mkdir(exist_ok=True)
        # Retain the established natural, timing-sensitive regular-book Mesa pool.
        phase_name = "book-integration" if native_book else label
        result = phase(phase_name, list(map(str, command)), phase_env or environment, 600, phase_logs)
        require_clean_output(result)
        log_path = phase_logs / (phase_name + ".log")
        phase_rows.append({"label":label, "seconds":round(time.monotonic()-started, 6),
            "status":"success", "log_sha256":sha(log_path) if log_path.is_file() else None,
            "process_costs":result.get("process_costs"),
            "memory_note":"Child-process high-water RSS is cumulative for this producer, not reclaimed texture/GPU bytes."})
        return result

    try:
        editor = tc.EDITORS["Linux"]
        urls = tc.official_asset_urls(tc.request_json(tc.RELEASE_API), (editor, tc.TEMPLATES))
        for asset in (editor, tc.TEMPLATES):
            tc.download_asset(urls[asset.name], cache / asset.name, asset.sha256, 1200)
        engine = str(tc.extract_editor(cache / editor.name, work / "engine", "Linux"))
        templates = tc.template_directory(work, "Linux")
        tc.extract_windows_templates(cache / tc.TEMPLATES.name, templates)
        extract_web_templates(cache / tc.TEMPLATES.name, templates)
        version = subprocess.check_output([engine, "--version"], env=environment, text=True).strip()
        if version != tc.EXPECTED_VERSION:
            raise ValueError("Pinned engine version differs")
        fixture = build_fixture(repo, work / "fixture")
        checkout = Path(fixture["checkout"])
        inventory = fixture["background_inventory"]
        project = work / "native-game"
        copy_regression_game(repo, project)
        restore_player_catalog(checkout, project, background_inventory=inventory)
        backgrounds.prepare_import(project, inventory)
        shutil.copyfile(scripts / "hp_i2_probe.gd", project / "tests/hp_i2_probe.gd")
        run_phase("t01-import", [engine, "--headless", "--path", project, "--import"])
        imported = backgrounds.verify_import(project, inventory)
        run_phase("t01-parse", [engine, "--headless", "--path", project, "--script", "res://tests/hp_i2_probe.gd", "--check-only"])
        native = work / "native-output"
        native.mkdir()
        cases = []
        for width, height in ((1280,720),(1920,1080),(2560,1440),(3840,2160)):
            label = str(width)
            case_env = tc.isolated_environment(work / ("native-profile-"+label), "Linux")
            case_env.update(LIBGL_ALWAYS_SOFTWARE="1", HP_I2_OUTPUT=str(native), HP_I2_CASE=label)
            run_phase("t01-"+label, ["xvfb-run", "-a", "-s", "-screen 0 3840x2160x24 -nolisten tcp",
                engine, "--path", project, "--resolution", f"{width}x{height}", "--position", "0,0",
                "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script",
                "res://tests/hp_i2_probe.gd", "--", "--p1-capture"], phase_env=case_env)
            report = json.loads((native / ("T01-"+label+".json")).read_text())
            if not report["passed"] or not report["assertions"]:
                raise ValueError("T01 failed or empty: " + label)
            cases.append(report)
        pngs = sorted(native.glob("*.png"))
        expected_pngs = [
            "01-1280x720-ui100-selected-fit.png", "02-1920x1080-ui125-selected-fit.png",
            "03-2560x1440-ui100-selected-fit.png", "04-2560x1440-ui100-selected-zoom.png",
            "05-2560x1440-ui100-none-control.png", "06-3840x2160-ui100-selected-fit.png"]
        if [p.name for p in pngs] != expected_pngs:
            raise ValueError("T01 must produce exactly the six approved originals")
        for path in pngs:
            shutil.copyfile(path, output / path.name)
            if sha(path) != sha(output / path.name):
                raise ValueError("Original delivery differs")
        write(output / "T01.json", {"format":"hp-i2-t01-delivery/v1", "product_head":head, "passed":True,
            "engine":version, "cases":cases, "import":imported,
            "scope":"Unmodified regular main.tscn, natural timing, injected native engine Mouse/Wheel/Escape/Tab events; no browser or Windows start.",
            "resource_limit":"Own current/stale request/texture/capture references; no process/GPU allocator reclamation assertion."})
        t02 = run_delivery(repo, fixture, work / "t02", engine, environment, run_phase, cache=cache)
        t02.update(product_head=head, engine=version, integration=fixture)
        write(output / "T02.json", t02)
        if subprocess.check_output(["git","status","--porcelain"],cwd=repo,text=True).strip():
            raise ValueError("Evidence modified product sources")
        descriptions = {capture["file"]:capture for case in cases for capture in case["captures"]}
        files = []
        for path in sorted(output.iterdir()):
            files.append({"file":path.name,"bytes":path.stat().st_size,"sha256":sha(path),"product_head":head,
                "scenario":descriptions.get(path.name, {}).get("scenario",path.stem),
                "resolution":descriptions.get(path.name, {}).get("resolution"),
                "ui_scale":descriptions.get(path.name, {}).get("ui_scale")})
        manifest = {"format":"hp-i2-originals/v1", "product_head":head,
            "product_tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],cwd=repo,text=True).strip(),
            "review_ref":os.environ.get("GITHUB_REF"), "review_head":os.environ.get("GITHUB_SHA"),
            "run_id":os.environ.get("GITHUB_RUN_ID"), "run_attempt":os.environ.get("GITHUB_RUN_ATTEMPT"),
            "created_utc":datetime.now(timezone.utc).isoformat(), "retention_days":7,
            "spec_url":"https://github.com/venomenon328/picross/issues/561#issuecomment-6770077470",
            "engine":version,"host":platform.platform(),"renderer":"Godot compatibility/OpenGL3; Mesa software via LIBGL_ALWAYS_SOFTWARE=1",
            "elapsed_seconds":round(time.monotonic()-began,6), "phases":phase_rows,
            "producer_files":[{"file":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(scripts.iterdir()) if p.suffix in (".py",".gd")],
            "files":files, "passed":True,
            "limits":"Linux native originals and engine events, actual Windows/Web export and PCK audits. No browser interaction, Windows startup, shipping of synthetic content or independent HP-I2-A01 acceptance."}
        write(output / "manifest.json", manifest)
        print("HP_I2_EVIDENCE_OK " + json.dumps({"head":head,"files":len(files)+1,"seconds":manifest["elapsed_seconds"]}),flush=True)
        return 0
    finally:
        marker = json.loads((work / "OWNER.json").read_text())
        if marker != {"purpose":"HP-I2-T01-T02", "product_head":head, "disposable":True}:
            raise ValueError("Unexpected evidence work ownership")
        shutil.rmtree(work)

if __name__ == "__main__":
    raise SystemExit(main())
