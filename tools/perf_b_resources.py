"""Current cell texture/import contract; independent of historical manufacture."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = "tools/cell_atlas_reference.json"
NAMES = {f"{kind}-{level}.png" for kind in ("fill", "x") for level in ("small", "medium", "large")}
PIXELS = {"small": 32, "medium": 64, "large": 96}


def import_settings(name):
    source = "res://art/cells/" + name
    target = "res://.godot/imported/" + name + "-" + hashlib.md5(source.encode()).hexdigest() + ".ctex"
    return f'''[remap]

importer="texture"
type="CompressedTexture2D"
path="{target}"
metadata={{
"vram_texture": false
}}

[deps]

source_file="{source}"
dest_files=["{target}"]

[params]

compress/mode=0
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
process/fix_alpha_border=false
process/premult_alpha=false
process/hdr_as_srgb=false
process/size_limit=0
detect_3d/compress_to=1
'''


def verify_runtime(root=ROOT):
    reference = root / REFERENCE
    manifest = json.loads(reference.read_text(encoding="utf-8"))
    fixed = dict(format="picross-cell-atlas-reference-v1", render_version="pencil-atlas-1",
                 variants=16, frames=24, duration_us=210000, padding=2, decoded_bytes=48906240)
    if any(manifest.get(key) != value for key, value in fixed.items()):
        raise ValueError("Current atlas mapping contract differs")
    items = manifest.get("atlases", [])
    if len(items) != 6 or {item.get("file") for item in items} != NAMES:
        raise ValueError("Current atlas reference inventory differs")
    directory = root / "game/art/cells"
    expected_files = NAMES | {name + ".import" for name in NAMES}
    if {p.name for p in directory.iterdir()} != expected_files:
        raise ValueError("Current atlas resource inventory differs")
    result = {}
    total = 0
    for item in items:
        name = item["file"]  # Exact inventory above prevents traversal and duplicates.
        kind, level = name.removesuffix(".png").split("-")
        size = [(PIXELS[level] + 4) * 24, (PIXELS[level] + 4) * 16]
        decoded = size[0] * size[1] * 4
        if (item.get("kind") != kind or item.get("level") != level or item.get("size") != size
                or item.get("decoded_bytes") != decoded):
            raise ValueError("Current atlas dimensions/memory contract differs")
        for key in ("sha256", "pixel_sha256", "import_sha256"):
            if not isinstance(item.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", item[key]):
                raise ValueError("Invalid current atlas hash binding")
        path = directory / name
        if path.is_symlink() or path.with_suffix(".png.import").is_symlink():
            raise ValueError("Current atlas resource must be a regular file")
        data = path.read_bytes()
        if len(data) != item.get("bytes") or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("Current atlas bytes differ: " + name)
        if data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR" or list(struct.unpack(">II", data[16:24])) != size or data[24:29] != bytes([8, 6, 0, 0, 0]):
            raise ValueError("Current atlas PNG encoding/dimensions differ")
        settings = path.with_suffix(".png.import").read_bytes()
        if settings != import_settings(name).encode("utf-8") or hashlib.sha256(settings).hexdigest() != item["import_sha256"]:
            raise ValueError("Current atlas import contract differs: " + name)
        result[name] = item["sha256"]
        total += decoded
    if total != fixed["decoded_bytes"]:
        raise ValueError("Current atlas total memory differs")
    return dict(atlases=result, reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                decoded_bytes=total,
                runtime_files={p: hashlib.sha256((root / "game/ui" / p).read_bytes()).hexdigest()
                               for p in ("atlas_marks.gd", "atlas_mask.gdshader", "cell_atlas.gd", "drawing_board.gd")})
