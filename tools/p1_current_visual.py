"""Validate the current drawing contract without rebuilding historical studies."""
from __future__ import annotations

import json
from pathlib import Path

import p1_preflight as toolchain
from p1_evidence import png_references
import zs2_delivery

def pixel_oracle(renders: Path, inputs, action):
    """Attach the failed oracle's actual native input group to its exception."""
    try:
        return action()
    except Exception as exc:
        exc.p1_failure_images = [renders / name for name in png_references(inputs)]
        raise




def verify_regular_motion(root: Path, renders: Path) -> dict:
    font = root / "game/art/drawing/DelightCoffee-Regular.ttf"
    if toolchain.sha256_file(font) != "4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23":
        raise toolchain.PreflightError("Current Delight Coffee font differs from its bound source")
    current = json.loads((renders / "zs2-after.json").read_text(encoding="utf-8"))
    if (current.get("role") != "after" or current["failures"] != 0
            or current["display"] == "headless" or not current["renderer"]):
        raise toolchain.PreflightError("Failed current native drawing oracle")
    x_sizes = pixel_oracle(renders, current["rework_sequences"],
                          lambda: zs2_delivery.verify_x_sizes(renders, current["rework_sequences"], sizes=(24,)))
    fill_sizes = pixel_oracle(renders, current["fill_sequences"],
                             lambda: zs2_delivery.verify_fill_sizes(renders, current["fill_sequences"], atlas_frames=True, sizes=(24,)))
    wave = pixel_oracle(renders, current["wave_sequence"],
                       lambda: zs2_delivery.verify_wave(renders, current["wave_sequence"]))
    temporary = list(renders.glob("*.png"))
    result = dict(temporary_pngs=len(temporary), temporary_png_bytes=sum(p.stat().st_size for p in temporary), renderer=current["renderer"], x_size_evidence=x_sizes,
                  fill_size_evidence=fill_sizes, wave_evidence=wave)
    # Native original crops have already been read by independent Python
    # spatial/timing oracles; they are temporary test inputs, not deliverables.
    for path in temporary:
        path.unlink()
    return result
