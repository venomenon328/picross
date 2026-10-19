"""EA native motion/geometry/input and independent process restart evidence."""
import json
import time
from pathlib import Path

from product_fixtures import copy_regression_game
from p1_preflight import PreflightError


def run(root, workspace, output, engine, environment, phase, python_phase, host):
    directory = output / "ea"
    directory.mkdir()
    project = workspace / "ea/game"
    copy_regression_game(root, project)
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
    phase("ea-import", [engine, "--headless", "--path", str(project), "--import"], phase_env=env)
    reports = []
    for mode in ("native", "restart"):
        env["EA_MODE"] = mode
        command = [engine, "--path", str(project), "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
                   "--script", "res://tests/ea_probe.gd", "--", "--p1-capture"]
        if host == "Linux":
            command = ["xvfb-run", "-a"] + command
            env["LIBGL_ALWAYS_SOFTWARE"] = "1"
        phase("ea-"+mode, command, "EA_PROBE_OK", phase_env=env)
        report = json.loads((directory / (mode+".json")).read_text(encoding="utf-8"))
        if report["failures"] or not report["checks"]:
            raise PreflightError("EA native assertions failed")
        reports.append(report)
    return python_phase("ea-image-processing", lambda: prepare_images(directory, reports))


def prepare_images(directory, reports):
    # Lossless animated PNG, actual native frames/timestamps; no interpolated art.
    from PIL import Image
    sequence = reports[0]["sequence"]
    if len(sequence) < 10:
        raise PreflightError("EA motion sequence is incomplete")
    began = time.perf_counter()
    frames = [Image.open(directory / frame["file"]).convert("RGB") for frame in sequence]
    read_seconds = time.perf_counter()-began
    durations = [max(1, round((b["seconds"]-a["seconds"])*1000)) for a,b in zip(sequence, sequence[1:])]+[1000]
    began = time.perf_counter()
    frames[0].save(directory / "motion.apng", save_all=True, append_images=frames[1:], duration=durations, loop=0, format="PNG")
    write_seconds = time.perf_counter()-began
    for frame in frames: frame.close()
    image_costs = dict(input_frames=len(sequence), read_decode_seconds=read_seconds,
        apng_write_seconds=write_seconds, output_bytes=(directory / "motion.apng").stat().st_size,
        durations_ms=durations, format="picross-ea-image-costs-v1")
    (directory / "image-costs.json").write_text(json.dumps(image_costs, indent=2)+"\n", encoding="utf-8")
    # The APNG contains all frames. Keep only five additional static phase samples.
    selected = {min(range(len(sequence)), key=lambda i:abs(sequence[i]["seconds"]-t)) for t in (0, .5, 1.1, 1.65, 2.15)}
    retained = [directory / sequence[i]["file"] for i in sorted(selected)]
    return dict(test_only=True, reports=reports, image_costs=image_costs, animation="motion.apng"), retained + sorted(directory.glob("final-*.png")) + sorted(directory.glob("rectangle-*.png")) + sorted(directory.glob("at-*.png")) + sorted(directory.glob("*.json")) + [directory / "motion.apng"]
