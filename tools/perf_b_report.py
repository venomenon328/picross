"""Package the native B comparison without rewriting any historical A evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import perf_b_resources as resources


def digest(data):
    return hashlib.sha256(data).hexdigest()


def case_key(case):
    return (case["fixture"], tuple(case["context"]), case["density"], case["animations"], case["scenario"])


def build(before: Path, after: Path, historical_after: Path, output: Path):
    reports = {role: json.loads((path / "summary.json").read_text())
               for role, path in (("before", before), ("after", after), ("historical-after", historical_after))}
    prior = {case_key(c): c for c in reports["before"]["cases"]}
    pairs = []
    for c in reports["after"]["cases"]:
        b = prior[case_key(c)]
        if b["actual_cell"] != c["actual_cell"]:
            raise ValueError("Comparison geometry differs")
        pairs.append(dict(before=b, after=c))
    if len(pairs) != 120 or any(p["after"]["fixture"] != 2 for p in pairs):
        raise ValueError("Expected all 120 current F02 comparisons")
    for key in ("platform", "windows_system_dpi", "engine_sha256", "harness_sha256", "plan_sha256", "b_plan_sha256"):
        if reports["before"]["binding"][key] != reports["after"]["binding"][key]:
            raise ValueError("Comparison environment/plan differs: " + key)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "b1-windows-raw.zip"
    inventory = {}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for role, directory in (("before", before), ("after", after), ("historical-after", historical_after)):
            for path in sorted(directory.rglob("*")):
                if not path.is_file(): continue
                name = role + "/" + path.relative_to(directory).as_posix()
                data = path.read_bytes()
                info = zipfile.ZipInfo(name, (2026, 10, 11, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, data)
                inventory[name] = dict(bytes=len(data), sha256=digest(data))
    result = dict(format="picross-perf-b-comparison-v1",
                  bindings={k:v["binding"] for k,v in reports.items()},
                  runtime_files=resources.verify_runtime()["runtime_files"],
                  current_cases=pairs,
                  theoretical_stress=[dict(before=prior[case_key(c)], after=c)
                                      for c in reports["historical-after"]["cases"] if c["fixture"] != 2],
                  cpu_scope="Before: original pencil draw only. After: all B layers, board and synchronization, including zero-work frames. Clear-effects queues one board redraw per repetition after warmup; no intervals removed.",
                  catalog_scope="Current product <=50x50. F03/F07 are historical theoretical stress only, measured on the separately bound older B source.",
                  unmeasured=["GPU duration", "presentation timing", "physical input latency"],
                  raw_archive=dict(file=archive.name, bytes=archive.stat().st_size,
                                   sha256=digest(archive.read_bytes()), files=inventory))
    (output / "b1-windows.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8", newline="\n")
    return result


def verify(directory: Path, root=resources.ROOT):
    report = json.loads((directory / "b1-windows.json").read_text(encoding="utf-8"))
    for filename, expected in report["runtime_files"].items():
        if digest((root / "game/ui" / filename).read_bytes()) != expected:
            raise ValueError("Measured runtime changed: " + filename)
    for key, path in (("harness_sha256", "game/tests/perf_b_measure.gd"),
                      ("plan_sha256", "examples/perf_a/plan.json"),
                      ("b_plan_sha256", "examples/perf_b/plan.json")):
        if digest((root / path).read_bytes()) != report["bindings"]["after"][key]:
            raise ValueError("Measured plan/harness changed: " + path)
    entry = report["raw_archive"]
    data = (directory / entry["file"]).read_bytes()
    if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
        raise ValueError("Comparison archive identity differs")
    with zipfile.ZipFile(directory / entry["file"]) as bundle:
        if sorted(bundle.namelist()) != sorted(entry["files"]):
            raise ValueError("Comparison raw inventory differs")
        for filename, expected in entry["files"].items():
            data = bundle.read(filename)
            if len(data) != expected["bytes"] or digest(data) != expected["sha256"]:
                raise ValueError("Comparison raw identity differs: " + filename)
        for role in ("before", "after", "historical-after"):
            binding = json.loads(bundle.read(role + "/binding.json"))
            if binding != report["bindings"][role]:
                raise ValueError("Comparison source binding differs")
            for context in binding["contexts"]:
                if digest(bundle.read(role + "/" + context["directory"] + "/measurements.json")) != context["sha256"]:
                    raise ValueError("Comparison raw measurement binding differs")
        summaries = {role: json.loads(bundle.read(role + "/summary.json")) for role in ("before", "after")}
        prior = {case_key(c): c for c in summaries["before"]["cases"]}
        if report["current_cases"] != [dict(before=prior[case_key(c)], after=c) for c in summaries["after"]["cases"]]:
            raise ValueError("Comparison does not match archived summaries")
    if len(report["current_cases"]) != 120:
        raise ValueError("Incomplete current comparison")
    return dict(report_sha256=digest((directory / "b1-windows.json").read_bytes()),
                archive_sha256=entry["sha256"], before=report["bindings"]["before"]["source_commit"],
                after=report["bindings"]["after"]["source_commit"], current_cases=120,
                theoretical_stress_cases=len(report["theoretical_stress"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("before", "after", "historical-after", "output"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    build(args.before, args.after, args.historical_after, args.output)
    print(json.dumps(verify(args.output), indent=2))
