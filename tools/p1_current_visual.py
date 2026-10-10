"""Validate the current drawing contract without rebuilding historical studies."""
from __future__ import annotations

import json
from pathlib import Path

import p1_preflight as toolchain
from p1_evidence import png_references
import zs1_delivery
import zs2_delivery

CURRENT_CASES = {
    "f01-work", "f02-color", "f03-small", "f02-compact", "f01-1600",
    "f01-z150", "f03-z300", "f07-color100", "f07-small",
    "hint-row-drag", "hint-row-tooltip", "hint-column-drag", "hint-column-tooltip",
    "status-0", "status-1", "status-2",
}


def pixel_oracle(renders: Path, inputs, action):
    """Attach the failed oracle's actual native input group to its exception."""
    try:
        return action()
    except Exception as exc:
        exc.p1_failure_images = [renders / name for name in png_references(inputs)]
        raise


def verify_regular_motion(root: Path, renders: Path) -> dict:
    from PIL import Image, ImageChops

    font = root / "prototypes/p1/art/drawing/Chalkboard-Regular.ttf"
    if toolchain.sha256_file(font) != zs2_delivery.FONT_SHA256:
        raise toolchain.PreflightError("Current Chalkboard font differs from its bound source")
    current = json.loads((renders / "zs2-after.json").read_text(encoding="utf-8"))
    captures = current["captures"]
    if (current.get("role") != "after" or current["failures"] != 0
            or len(captures) != len(CURRENT_CASES)
            or {item["case"] for item in captures} != CURRENT_CASES):
        raise toolchain.PreflightError("Incomplete/failed current drawing matrix")
    if current["display"] == "headless" or not current["renderer"]:
        raise toolchain.PreflightError("Current drawing evidence requires a native renderer")
    for item in captures:
        if item["font"] != "Chalkboard" or item["spoiler_free"] is not True:
            raise toolchain.PreflightError("Current font/spoiler contract failed")
        with Image.open(renders / item["file"]) as picture:
            if list(picture.size) != item["size"]:
                raise toolchain.PreflightError("Current drawing capture dimensions differ")
    if len(current["frames"]) != 1 or {m["fixture"] for m in current["measurements"]} != {"F-03", "F-07"}:
        raise toolchain.PreflightError("Missing current motion/large color load")
    for motion in current["frames"]:
        if not (motion["preview_static"] and motion["off_same_end"] and motion["second_gesture_ms"] < 210):
            raise toolchain.PreflightError("Current real-time animation failed")
        early = next(f for f in motion["timeline"] if f["label"] == "parallel-commit-0")
        final = next(f for f in motion["timeline"] if f["label"] == "settled")
        if not 0 < early["after_commit_ms"] < 210:
            raise toolchain.PreflightError("Current animation missed live commit effect")
        with Image.open(renders / early["file"]) as a, Image.open(renders / final["file"]) as b:
            if not ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox():
                raise toolchain.PreflightError("Current live effect is invisible")
    # These independent pixel oracles operate on the current renderer only.
    # No historical project, before image or isolated study is imported/executed.
    strokes = pixel_oracle(renders, current["stroke_frames"],
                          lambda: zs1_delivery.verify_strokes(renders, current["stroke_frames"]))
    x_sizes = pixel_oracle(renders, current["rework_sequences"],
                          lambda: zs2_delivery.verify_x_sizes(renders, current["rework_sequences"]))
    fill_sizes = pixel_oracle(renders, current["fill_sequences"],
                             lambda: zs2_delivery.verify_fill_sizes(renders, current["fill_sequences"]))
    wave = pixel_oracle(renders, current["wave_sequence"],
                       lambda: zs2_delivery.verify_wave(renders, current["wave_sequence"]))
    return dict(font_sha256=zs2_delivery.FONT_SHA256, cases=sorted(CURRENT_CASES),
                renderer=current["renderer"], movements=current["frames"],
                stroke_evidence=strokes, x_size_evidence=x_sizes,
                fill_size_evidence=fill_sizes, wave_evidence=wave,
                measurements=current["measurements"])


def selected_motion_files(renders: Path) -> list[Path]:
    """Keep native animation crops plus two current contexts, within the global cap."""
    selected = [renders / name for name in (
        "zs2-after.json", "current-drawing-report.json", "zs2-numerals.png",
        "zs2-after-f02-color.png", "zs2-after-f07-small.png")]
    for pattern in ("zs1-motion-*.png", "zs1-strokes-*.png", "zs2-x-*.png",
                    "zs2-fill-*.png", "zs2-wave-*.png"):
        selected.extend(path for path in renders.glob(pattern) if not path.name.endswith("-context.png"))
    return selected
