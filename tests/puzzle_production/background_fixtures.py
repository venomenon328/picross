"""Ephemeral HP-W2 inputs: actual synthetic files, never production approvals."""
import copy
import hashlib
import io
import json
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageCms


# Independent transcription of the public profile, not the producer's object.
PROFILE = {
    "id": "picross-background-png2304-v1", "width": 2304, "height": 576,
    "format": "PNG", "mode": "RGBA", "fit": "contain", "anchor": "bottom-center",
    "upscale": True, "resample": "pillow-rgba-premultiplied-lanczos",
    "color_space": "sRGB", "transparent_rgb": "zero", "png_compress_level": 9,
    "png_optimize": False, "metadata": "sRGB-only",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_ref(root, name):
    raw = (Path(root) / name).read_bytes()
    return {"file": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def put(root, name, raw):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return file_ref(root, name)


def put_json(root, name, value):
    return put(root, name, canonical(value) + b"\n")


def image_bytes(image, **kwargs):
    stream = io.BytesIO()
    image.save(stream, format="PNG", **kwargs)
    return stream.getvalue()


def gray_icc():
    """Build a small GRAY ICC from LittleCMS's real white point and sRGB TRC.

    No opaque binary fixture or extra native-library dependency: the ICC tag
    table is reconstructed from the runtime-created profile with a GRAY header,
    a gray kTRC tag and a fresh synthetic description. Its profile ID is unset.
    """
    rgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    entries = {}
    for index in range(struct.unpack_from(">I", rgb, 128)[0]):
        kind, offset, length = struct.unpack_from(">4sII", rgb, 132 + index * 12)
        entries[kind] = rgb[offset:offset + length]
    label = "TEST ONLY synthetic gray with sRGB transfer curve".encode("utf-16-be")
    description = b"mluc\0\0\0\0" + struct.pack(">II", 1, 12) + b"enUS" + struct.pack(">II", len(label), 28) + label
    tags = ((b"desc", description), (b"cprt", entries[b"cprt"]),
            (b"wtpt", entries[b"wtpt"]), (b"kTRC", entries[b"rTRC"]))
    header = bytearray(rgb[:128])
    header[16:20] = b"GRAY"
    header[84:100] = b"\0" * 16
    table = bytearray(struct.pack(">I", len(tags)))
    payload = bytearray()
    start = 132 + len(tags) * 12
    for kind, body in tags:
        table.extend(struct.pack(">4sII", kind, start + len(payload), len(body)))
        payload.extend(body)
        payload.extend(b"\0" * (-len(payload) % 4))
    profile = header + table + payload
    struct.pack_into(">I", profile, 0, len(profile))
    return bytes(profile)


def pixels(size=(5, 7), color=(90, 60, 30, 128)):
    image = Image.new("RGBA", size, color)
    image.putpixel((0, 0), (200, 100, 50, 0))
    image.putpixel((size[0] - 1, size[1] - 1), (40, 50, 60, 255))
    return image


def chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))


def chunks(raw):
    """Read actual PNG chunks without trusting Pillow's metadata dictionary."""
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    result, position = [], 8
    while position < len(raw):
        size = struct.unpack(">I", raw[position:position + 4])[0]
        kind = raw[position + 4:position + 8]
        data = raw[position + 8:position + 8 + size]
        crc = struct.unpack(">I", raw[position + 8 + size:position + 12 + size])[0]
        assert crc == zlib.crc32(kind + data) & 0xffffffff
        result.append((kind, data))
        position += size + 12
    assert position == len(raw)
    return result


def insert_chunk(raw, kind, data):
    return raw[:33] + chunk(kind, data) + raw[33:]


def diagnostic(image):
    histogram = image.getchannel("A").histogram()
    occupied = [value for value, count in enumerate(histogram) if count]
    return {"format": "PNG", "mode": "RGBA", "width": image.width,
            "height": image.height, "alpha": {
                "min": min(occupied), "max": max(occupied),
                "transparent_pixels": histogram[0],
                "partial_pixels": sum(histogram[1:255]),
                "opaque_pixels": histogram[255],
            }}


class BackgroundFixture:
    """Closed selected/none data with independently hashed local file bytes."""

    def __init__(self, root, description, *, none=False, image=None):
        self.root = Path(root)
        self.source = self.root / "source"
        self.output = self.root / "output"
        self.source.mkdir(parents=True)
        self.output.mkdir()
        statement = ("TEST ONLY: Synthetic explicit waiver of the background and of "
                     "initial candidate production." if none else
                     "TEST ONLY: Synthetic selection of candidate A and the fixed profile.")
        human = {"actor": "Synthetic test actor", "timestamp_utc": "2026-01-01T12:00:00Z",
                 "statement": statement,
                 "evidence": put(self.source, "evidence/decision.txt", statement.encode())}
        self.manifest = {
            "format": "picross-background-work-v1", "puzzle_id": "pz-hp-synthetic",
            "job_id": "hp-synthetic", "revision": "bg01",
            "created_utc": "2026-01-01T12:00:00Z",
            "context": {"summary": "TEST ONLY synthetic context; no real puzzle.",
                        "protected_features": [], "excluded_subjects": [],
                        "reveal": None, "reveal_approval": None},
            "briefing": "TEST ONLY synthetic pixels exercise the standalone file contract.",
            "candidate_policy": {"count": 0 if none else 3,
                                 "exception": copy.deepcopy(human) if none else None},
            "presentation": {"status": "pending" if none else "offered", "evidence": None},
            "candidates": [], "test_only": True,
        }
        if not none:
            self.manifest["context"].update(
                reveal=put(self.source, "context/reveal.png", image_bytes(pixels((2, 2)))),
                reveal_approval=put(self.source, "evidence/reveal.txt",
                                    b"TEST ONLY synthetic reveal approval statement."))
            self.manifest["presentation"]["evidence"] = put(
                self.source, "evidence/presentation.txt",
                b"TEST ONLY isolated original/A-b01.png, B-b01.png and C-b01.png offered.")
            rights = put(self.source, "evidence/rights.txt",
                         b"TEST ONLY repository-generated synthetic pixel fixtures; no attribution.")
            prompt = put(self.source, "evidence/prompt.txt",
                         b"TEST ONLY deterministic test pixel construction, not image generation.")
            for index, candidate_id in enumerate(("A", "B", "C")):
                original = image if index == 0 and image is not None else pixels(
                    (5 + index, 7 - index), (90, 60 + index * 30, 30, 128))
                ref = put(self.source, f"original/{candidate_id}-b01.png", image_bytes(original))
                self.manifest["candidates"].append({
                    "id": candidate_id, "revision": "b01",
                    "description": f"TEST ONLY synthetic pixel arrangement {candidate_id}.",
                    "original": ref,
                    "provenance": {"author": "HP-W2 synthetic tests", "source": "Generated test pixels",
                                   "usage_basis": "Repository-owned synthetic test construction",
                                   "rights_status": "resolved", "attribution": None,
                                   "evidence": [copy.deepcopy(rights)]},
                    "generation": {"tool": "synthetic-fixture", "model": None,
                                   "prompt": copy.deepcopy(prompt), "parameters": [], "seed": None,
                                   "unknown": [{"field": "model", "reason": "not_recorded"},
                                               {"field": "seed", "reason": "not_exposed"}]},
                    "review": None,
                })
        self.decision = {
            "format": "picross-background-decision-v1", "puzzle_id": self.manifest["puzzle_id"],
            "job_id": self.manifest["job_id"], "revision": "d01", "background_revision": "bg01",
            "manifest": None, "outcome": "none" if none else "selected",
            "candidate_id": None if none else "A",
            "original": None if none else copy.deepcopy(self.manifest["candidates"][0]["original"]),
            "profile": None if none else {"id": PROFILE["id"], "sha256": digest(PROFILE)},
            **human, "presented_package": None, "previous_decision": None,
            "carried_from": None, "accepted_deviations": [], "test_only": True,
        }
        self.request = {"format": "picross-background-derive-request-v1", "manifest": None,
                        "decision": None, "source": None, "profile": copy.deepcopy(PROFILE),
                        "expected_tool_sha256": description["tool_sha256"], "output": "derived/bg01"}
        self.refresh()

    @property
    def target(self):
        return self.output / self.request["output"]

    def refresh(self):
        self.request["manifest"] = put_json(self.source, "work/bg01.json", self.manifest)
        self.decision["manifest"] = copy.deepcopy(self.request["manifest"])
        self.refresh_decision()

    def refresh_decision(self):
        self.request["decision"] = put_json(self.source, "decisions/d01.json", self.decision)
        self.request["source"] = copy.deepcopy(self.decision["original"])

    def replace_source(self, raw):
        ref = put(self.source, "original/A-b01.png", raw)
        self.manifest["candidates"][0]["original"] = ref
        self.decision["original"] = copy.deepcopy(ref)
        self.refresh()

    def request_file(self):
        put_json(self.root, "request.json", self.request)
        return self.root / "request.json"
