"""Independent HF budget/text/coverage checks over native measurements."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from p1_preflight import PreflightError, sha256_file


def require(ok, label):
    if not ok:
        raise PreflightError("HF149: " + label)


def slot(record):
    for axis in range(2):
        free = (record["size"][axis] - record["dimensions"][axis] * record["cell"]
                - record["minimum"][axis] * record["pitch"][axis] - 14)
        expected = min(record["demand"][axis], record["minimum"][axis]
                       + max(0, math.floor((free + .000001) / record["pitch"][axis])))
        require(record["reserve"][axis] == expected, "maximal independent capacity")
    require(11.99 <= record["cell"] <= 12, "unreduced chosen cell")


def overlay(record):
    require(record["font"] == "Delight Coffee" and record["heading"] == "Fraunces",
            "actual bundled faces")
    require(record["title_fs"] == round(13 * record["ui"])
            and record["title_fs"] < record["fs"], "smaller UI-scaled heading")
    require(record["fs"] == round(round(16 * record["ui"]) * 1.35), "zoom-independent reading size")
    require(len(record["boxes"]) == len(record["tokens"]), "every whole token")
    _, ty, _, th = record["title_box"]
    padding = 28 * record["ui"]
    previous = None
    for x, y, w, h in record["boxes"]:
        require(y >= ty + th + 9 * record["ui"], "title-number separation")
        require(x >= padding - .01 and y >= padding - .01
                and x + w <= record["rect"][2] - padding + .01
                and y + h <= record["rect"][3] - padding + .01, "safe text inset")
        if previous:
            px, py, pw, ph = previous
            require(x >= px + pw + 9 * record["ui"] or y >= py + ph,
                    "no token overlap across wraps")
        previous = x, y, w, h
    require(set(record["statuses"]) == {0, 1, 2}, "three real H1 states")


def verify(directory: Path) -> dict:
    reports = {stage: json.loads((directory / f"hf-{stage}.json").read_text(encoding="utf-8"))
               for stage in ("write", "read", "native")}
    require(all(r["failures"] == 0 and r["checks"] >= 10 for r in reports.values()), "successful fresh processes")
    native = reports["native"]
    require(native["display"] != "headless" and native["renderer"], "native renderer")
    slots = [r for r in native["records"] if r["kind"] == "slots"]
    require(len(slots) == 144, "both axes, two formats/UI scales and boundary sides")
    for r in slots:
        slot(r)
    views = [r for r in native["records"] if r["kind"] in ("overlay", "complete")]
    expected = {(w, h, u, z, axis) for w, h, u in ((1280,720,1.25),(1920,1080,1),(2560,1440,1.25))
                for z in (20,72) for axis in ("row","column")}
    require(len(views) == len(expected)
            and {(*r["client"],r["ui"],r["zoom"],r["axis"]) for r in views} == expected,
            "exact native scene coverage including genuinely complete lines")
    overlays = [r for r in views if r["kind"] == "overlay"]
    require({r["ui"] for r in overlays} == {1,1.25}
            and {r["axis"] for r in overlays} == {"row","column"}
            and any(r["rows"] > 1 for r in overlays), "overflow on both axes and UI scales")
    for r in overlays:
        overlay(r)
        require((directory / r["file"]).is_file(), "native original image")
    for width in (1280,1920,2560):
        require((directory / f"hf-{width}-single.png").is_file(), "one-line scene sample")
    controls = []
    for label, source, checker, mutation in (
        ("unused fitting slot", slots[0], slot, lambda r: r["reserve"].__setitem__(1,r["reserve"][1]-1)),
        ("overlapping heading", overlays[0], overlay, lambda r: r["boxes"][0].__setitem__(1,r["title_box"][1])),
        ("wrong number face", overlays[0], overlay, lambda r: r.update(font="IBM Plex Sans")),
    ):
        bad = copy.deepcopy(source)
        mutation(bad)
        try:
            checker(bad)
        except PreflightError:
            controls.append(label)
        else:
            raise PreflightError("HF149 negative control escaped: " + label)
    result = {"slot_records":len(slots), "scene_records":len(views), "overlays":len(overlays),
              "fresh_processes":[reports[s]["checks"] for s in ("write","read")],
              "native_checks":native["checks"], "negative_controls":controls,
              "files":{p.name:sha256_file(p) for p in sorted(directory.glob("*.png"))}}
    (directory / "hf-acceptance.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result
