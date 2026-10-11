"""Bound native PERF-A experiments; no regular renderer substitution."""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import math
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
import p1_preflight as tc

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "examples/perf_a/plan.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run(command, env, log, marker=None):
    result = subprocess.run(list(map(str, command)), env=env, capture_output=True,
                            encoding="utf-8", errors="replace", timeout=300,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    text = result.stdout + result.stderr
    Path(log).write_text(text, encoding="utf-8", newline="\n")
    if result.returncode or "ERROR:" in text or (marker and marker not in text):
        raise ValueError((result.returncode, str(log), text[-5000:]))


def distribution(values):
    if not values:
        return dict(n=0, p50=None, p95=None, p99=None, maximum=None)
    ordered = sorted(values)
    return dict(n=len(values), **{"p"+str(p): ordered[max(0, math.ceil(len(values)*p/100)-1)] for p in (50, 95, 99)}, maximum=ordered[-1])


def verify_save(data, definition):
    """Independent baseline oracle: replay the actual saved transaction."""
    if data["schema"] != 1 or data["definition_id"] != definition["id"] or data["definition_revision"] != definition["revision"]:
        raise ValueError("Wrong synthetic save identity")
    if (data["width"], data["height"]) != (40, 40) or data["completed"]:
        raise ValueError("Wrong load dimensions/completion")
    cells = [-1]*1600
    for action in data["history"][:data["cursor"]]:
        seen = set()
        for change in action:
            i = change["index"]
            if i in seen or not 0 <= i < 1600 or cells[i] != change["before"] or change["before"] == change["after"] or change["after"] not in (-1, 0, 1, 2, 3, 4):
                raise ValueError("Invalid synthetic history")
            seen.add(i)
            cells[i] = change["after"]
    if cells != data["cells"] or any(v != -1 for v in cells[1520:]):
        raise ValueError("Synthetic matrix/history or free input rows differ")
    return dict(fills=sum(v > 0 for v in cells), x=cells.count(0), unknown=cells.count(-1))


def summarize(output):
    report = json.loads((output / "baseline.json").read_text(encoding="utf-8"))
    summary = dict(plan_sha256=report["plan_sha256"], source_heads={k: v["source_commit"] for k, v in report["roles"].items()}, cases=[])
    definition = json.loads((ROOT / "game/data/f02.json").read_text(encoding="utf-8"))
    for role, data in report["roles"].items():
        for context in data["contexts"]:
            directory = output / context["directory"]
            if digest(directory / "measurements.json") != context["sha256"]:
                raise ValueError("Baseline raw data identity differs")
            raw = json.loads((directory / "measurements.json").read_text(encoding="utf-8"))
            for density in ("dense", "sparse"):
                verify_save(json.loads((directory / ("synthetic-"+density+".json")).read_text(encoding="utf-8")), definition)
                for animations in (False, True):
                    for scenario in ("hover", "fill", "x"):
                        records = [r for r in raw["records"] if (r["density"], r["animations"], r["scenario"]) == (density, animations, scenario)]
                        if len(records) != 3 or {r["repetition"] for r in records} != {0, 1, 2} or any(len(r["frame_intervals_us"]) != 36 for r in records):
                            raise ValueError("Missing baseline repetitions/raw samples")
                        summary["cases"].append(dict(role=role, context=context["requested_context"], actual_cell=raw["actual_cell"], overview=raw["overview_actual"], density=density, animations=animations, scenario=scenario,
                            frames_us=distribution([v for r in records for v in r["frame_intervals_us"]]),
                            mark_build_us=distribution([v for r in records for v in r["mark_build_cpu_us"]]),
                            dispatch_us=distribution([v for r in records for v in r["dispatch_cpu_us"]]),
                            draws=[r["draw_signals"] for r in records], peak_effects=max(v for r in records for v in r["active_effects"]),
                            static_memory_bytes=[r["static_memory_bytes"] for r in records], texture_memory_bytes=[r["texture_memory_bytes"] for r in records]))
    write_json(output / "summary.json", summary)
    return summary


def prepare(cache, workspace):
    archive = cache / tc.EDITORS[platform.system()].name
    tc.verify_sha256(archive, tc.EDITORS[platform.system()].sha256)
    return tc.extract_editor(archive, workspace / "engine", platform.system())


def source_project(ref, workspace):
    project_path = "game" if subprocess.check_output(["git", "ls-tree", "--name-only", ref, "game"], cwd=ROOT).strip() else "prototypes/p1"
    payload = subprocess.check_output(["git", "archive", ref, project_path], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(payload)) as bundle:
        bundle.extractall(workspace, filter="data")
    return workspace / project_path


def baseline(cache, output, only=None):
    if platform.system() != "Windows":
        raise ValueError("Baseline requires native Windows")
    output.mkdir(parents=True, exist_ok=False)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    result = dict(format="picross-perf-a-baseline-v1", platform=platform.platform(),
                  plan_sha256=digest(PLAN), harness_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  scripts={p.name: digest(p) for p in (Path(__file__), ROOT / "game/tests/perf_a_baseline.gd")}, roles={})
    user = ctypes.windll.user32
    user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    result["windows_system_dpi"] = user.GetDpiForSystem()
    result["windows_system_scale"] = result["windows_system_dpi"]/96
    with tempfile.TemporaryDirectory(prefix="picross-perfa-") as temporary:
        workspace = Path(temporary)
        engine = prepare(cache, workspace)
        result["engine_sha256"] = digest(engine)
        result["engine_archive_sha256"] = digest(cache / tc.EDITORS["Windows"].name)
        for role in ("baseline", "integrated_base"):
            source = plan[role]
            project = source_project(source, workspace / role)
            shutil.copyfile(ROOT / "game/tests/perf_a_baseline.gd", project / "tests/perf_a_baseline.gd")
            env = tc.isolated_environment(workspace / (role + "-profile"), "Windows")
            env.update(PERF_A_PLAN=str(PLAN))
            run([engine, "--headless", "--path", project, "--import"], env, output / (role + "-import.log"))
            role_data = dict(source_commit=source, renderer_files={p: digest(project / "ui" / p) for p in ("pencil_marks.gd", "drawing_board.gd", "full_view_board.gd", "board.gd")}, contexts=[])
            contexts = [(i, False) for i in range(len(plan["contexts"])) if only is None or i == only]
            if only is None and role == "integrated_base":
                contexts += [(3, True), (4, True)]
            for ci, overview in contexts:
                target = output / f"{role}-{ci}-overview{int(overview)}"
                target.mkdir()
                env.update(PERF_A_OUTPUT=str(target), PERF_A_CONTEXT=str(ci), PERF_A_OVERVIEW=str(int(overview)))
                run([engine, "--path", project, "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", "res://tests/perf_a_baseline.gd"], env, target / "native.log", "PERF_A_BASELINE_OK")
                measurement = json.loads((target / "measurements.json").read_text(encoding="utf-8"))
                if measurement["failures"] or len(measurement["records"]) != 36:
                    raise ValueError("Invalid measurement coverage")
                role_data["contexts"].append(dict(directory=target.name, sha256=digest(target / "measurements.json"), **{k: v for k, v in measurement.items() if k != "records"}))
                print(role, ci, overview, "OK", measurement["actual_cell"], flush=True)
            result["roles"][role] = role_data
    write_json(output / "baseline.json", result)
    summarize(output)
    print("PERF_A_WINDOWS_BASELINE_OK", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["baseline", "summarize"])
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--only-context", type=int)
    args = parser.parse_args()
    if args.action == "baseline":
        baseline(args.cache_dir.resolve(), args.output_dir.resolve(), args.only_context)
    else:
        summarize(args.output_dir.resolve())


if __name__ == "__main__":
    main()
