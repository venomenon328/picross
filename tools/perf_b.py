"""Native B comparison: unchanged A inputs, both sources freshly executed."""
from __future__ import annotations
import argparse
import ctypes
import json
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
import perf_a as a
import p1_preflight as tc

ROOT = a.ROOT


def compare(cache, output, role, source, theoretical_stress=False):
    if platform.system() != "Windows":
        raise ValueError("Native Windows comparison required")
    output.mkdir(parents=True, exist_ok=False)
    plan = json.loads(a.PLAN.read_text())
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    report = dict(source_commit=source, role=role, platform=platform.platform(),
                  windows_system_dpi=ctypes.windll.user32.GetDpiForSystem(),
                  plan_sha256=a.digest(a.PLAN), b_plan_sha256=a.digest(ROOT / "examples/perf_b/plan.json"),
                  adapter_sha256=a.digest(__file__), harness_sha256=a.digest(ROOT / "game/tests/perf_b_measure.gd"), contexts=[])
    with tempfile.TemporaryDirectory(prefix="picross-perfb-") as temporary:
        workspace = Path(temporary)
        engine = a.prepare(cache, workspace)
        report["engine_sha256"] = a.digest(engine)
        project = a.source_project(source, workspace / "source")
        shutil.copyfile(ROOT / "game/tests/perf_b_measure.gd", project / "tests/perf_b_measure.gd")
        env = tc.isolated_environment(workspace / "profile", "Windows")
        env["PERF_A_PLAN"] = str(a.PLAN)
        a.run([engine, "--headless", "--path", project, "--import"], env, output / "import.log")
        # Owner decision: 50x50 maximum. Historical 100x100 is optional theory
        # only, and must never silently select different current catalog slots.
        contexts = [(1, i) for i in range(10)]
        if theoretical_stress:
            main = (project / "ui/main.gd").read_text(encoding="utf-8")
            if "Definition.CATALOG_IDS" in main:
                raise ValueError("Theoretical F03/F07 requires a historical catalog source")
            contexts += [(2, 3), (6, 3)]
        report["theoretical_stress"] = theoretical_stress
        for fixture, ci in contexts:
            target = output / f"f{fixture+1:02d}-{ci}"
            target.mkdir()
            env.update(PERF_A_OUTPUT=str(target), PERF_A_CONTEXT=str(ci), PERF_A_OVERVIEW="0", PERF_B_FIXTURE=str(fixture))
            a.run([engine, "--path", project, "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", "res://tests/perf_b_measure.gd"], env, target / "native.log", "PERF_B_MEASURE_OK")
            raw = json.loads((target / "measurements.json").read_text())
            if raw["failures"] or len(raw["records"]) != 36:
                raise ValueError("Incomplete native comparison")
            if fixture == 1:
                definition = json.loads((project / "data/f02.json").read_text())
                for density in plan["densities"]:
                    a.verify_save(json.loads((target / f"synthetic-{density}.json").read_text()), definition)
            report["contexts"].append(dict(directory=target.name, sha256=a.digest(target / "measurements.json"), **{k:v for k,v in raw.items() if k != "records"}))
            a.write_json(output / "binding.json", report)
            print(role, target.name, "OK actual px", raw["actual_cell"], flush=True)
    summarize(output)


def summarize(output):
    report = json.loads((output / "binding.json").read_text())
    cases = []
    for context in report["contexts"]:
        path = output / context["directory"] / "measurements.json"
        if a.digest(path) != context["sha256"]:
            raise ValueError("Raw comparison binding changed")
        raw = json.loads(path.read_text())
        for density in ("sparse", "dense"):
            for animations in (False, True):
                for scenario in ("hover", "fill", "x"):
                    records = [r for r in raw["records"] if (r["density"], r["animations"], r["scenario"]) == (density, animations, scenario)]
                    if len(records) != 3 or any(len(r["all_layer_cpu_per_frame_us"]) != 36 for r in records):
                        raise ValueError("Missing repetitions or zero-work intervals")
                    cases.append(dict(fixture=raw["fixture"], context=raw["requested_context"], actual_cell=raw["actual_cell"], density=density, animations=animations, scenario=scenario,
                        **{name:a.distribution([v for r in records for v in r[key]]) for name,key in [("wall_us","frame_intervals_us"),("layer_cpu_us","all_layer_cpu_per_frame_us"),("dispatch_us","dispatch_cpu_us")]},
                        stats=[dict(before=r["initial_stats"],after=r["final_stats"],draws=r["draw_signals"]) for r in records],
                        static_bytes=[r["static_memory_bytes"] for r in records], texture_bytes=[r["texture_memory_bytes"] for r in records]))
    a.write_json(output / "summary.json", dict(binding=report, cases=cases, unmeasured=["GPU duration", "presentation timing", "physical input latency"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=["before", "after"])
    parser.add_argument("--source", required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--theoretical-stress", action="store_true")
    args = parser.parse_args()
    compare(args.cache_dir.resolve(), args.output_dir.resolve(), args.role, args.source, args.theoretical_stress)
