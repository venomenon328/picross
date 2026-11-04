"""EA native motion/geometry/input and independent process restart evidence."""
import json
import hashlib
import shutil
import time
from pathlib import Path

from p1_preflight import PreflightError
from native_results import bind_files


def copy_imported_base(base, project):
    """Copy immutable inputs, never share a writable project or a save profile."""
    began = time.perf_counter()
    inventory = bind_files(base)
    shutil.copytree(base, project)
    if bind_files(project) != inventory:
        raise PreflightError("EA imported base copy differs")
    return inventory, dict(base_sha256=hashlib.sha256(
        json.dumps(inventory, sort_keys=True).encode()).hexdigest(),
        files=len(inventory), bytes=sum(row['bytes'] for row in inventory),
        copy_seconds=time.perf_counter()-began)


def run(root, workspace, output, engine, environment, run_phase, python_phase, host, imported_base):
    directory = output / "ea"
    directory.mkdir()
    project = workspace / "ea/game"
    inventory, reuse = copy_imported_base(imported_base, project)
    from web_tests.fixtures import adapt
    adapt(project)
    from at_fixtures import install
    binding = install(project)
    (directory/'at-fixture.json').write_text(json.dumps(binding,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    # Deliberately different from the 50x30 raster: a real imported portrait.
    (project / "art/fixtures/t09.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="800">'
        '<rect width="300" height="800" fill="#6c9aab"/>'
        '<circle cx="150" cy="400" r="100" fill="#ffffff"/></svg>\n', encoding="utf-8", newline="\n")
    saves = workspace / "ea-saves"
    saves.mkdir()
    env = environment.copy()
    env.update(P1_TEST_SAVE_ROOT=str(saves), EA_OUTPUT=str(directory))
    run_phase("ea-import", [engine, "--headless", "--path", str(project), "--import"], phase_env=env)
    reports = []
    for mode in ("native", "restart"):
        env["EA_MODE"] = mode
        if host == "Linux":
            env["LIBGL_ALWAYS_SOFTWARE"] = "1"
        run_phase("ea-"+mode, (["xvfb-run", "-a"] if host == "Linux" else []) +
                  [engine, "--path", str(project), "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
                   "--script", "res://tests/ea_probe.gd", "--", "--p1-capture"], "EA_PROBE_OK", phase_env=env)
        report = json.loads((directory / (mode+".json")).read_text(encoding="utf-8"))
        if report["failures"] or not report["checks"]:
            raise PreflightError("EA native assertions failed")
        reports.append(report)
    began = time.perf_counter()
    if bind_files(imported_base) != inventory:
        raise PreflightError("EA immutable imported base changed")
    reuse.update(base_unchanged=True, verification_seconds=time.perf_counter()-began)
    summary = dict(test_only=True, reports=reports)
    selected = sorted(directory.glob("*.json")) + sorted(directory.glob("at-*.png"))
    summary['import_reuse'] = reuse
    return summary, selected
