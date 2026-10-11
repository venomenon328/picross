"""Bound native PERF-A experiments; no regular renderer substitution."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
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


def prepare(cache, workspace):
    archive = cache / tc.EDITORS[platform.system()].name
    tc.verify_sha256(archive, tc.EDITORS[platform.system()].sha256)
    return tc.extract_editor(archive, workspace / "engine", platform.system())


def source_project(ref, workspace):
    payload = subprocess.check_output(["git", "archive", ref, "prototypes/p1"], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(payload)) as bundle:
        bundle.extractall(workspace, filter="data")
    return workspace / "prototypes/p1"


def baseline(cache, output, only=None):
    if platform.system() != "Windows":
        raise ValueError("Baseline requires native Windows")
    output.mkdir(parents=True, exist_ok=False)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    result = dict(format="picross-perf-a-baseline-v1", platform=platform.platform(),
                  plan_sha256=digest(PLAN), harness_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  scripts={p.name: digest(p) for p in (Path(__file__), ROOT / "prototypes/p1/tests/perf_a_baseline.gd")}, roles={})
    with tempfile.TemporaryDirectory(prefix="picross-perfa-") as temporary:
        workspace = Path(temporary)
        engine = prepare(cache, workspace)
        result["engine_sha256"] = digest(engine)
        result["engine_archive_sha256"] = digest(cache / tc.EDITORS["Windows"].name)
        for role in ("baseline", "integrated_base"):
            source = plan[role]
            project = source_project(source, workspace / role)
            shutil.copyfile(ROOT / "prototypes/p1/tests/perf_a_baseline.gd", project / "tests/perf_a_baseline.gd")
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
    print("PERF_A_WINDOWS_BASELINE_OK", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["baseline"])
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--only-context", type=int)
    args = parser.parse_args()
    baseline(args.cache_dir.resolve(), args.output_dir.resolve(), args.only_context)


if __name__ == "__main__":
    main()
