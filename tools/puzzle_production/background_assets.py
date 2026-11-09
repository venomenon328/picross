"""HP-W2 standalone background derivation and reproducible, read-only proof.

This boundary consumes an explicit decision. It neither selects an image nor
certifies rights, visual quality, authoring readiness or runtime integration.
"""
from __future__ import annotations

import argparse
import hashlib
import io as bytes_io
import os
from pathlib import Path
import platform
import signal
import struct
import subprocess
import sys
import zlib

from PIL import Image, ImageFile, PngImagePlugin, __version__, features

from . import background_io as io
from .background_contract import (BackgroundError, MAX_JSON, MAX_PNG, PROFILE,
                                  canonical, digest, load_inputs, parse_json,
                                  validate_request)
from .contract import InvalidInput
from .image_normalization import normalize_bytes

PILLOW_VERSION = "12.3.0"
MAX_AXIS = 8192
MAX_PIXELS = 8_000_000
_ROOT = Path(__file__).resolve().parents[2]
_MODULES = tuple("tools/puzzle_production/" + name + ".py" for name in (
    "__init__", "authoring_package", "background_assets", "background_contract",
    "background_io", "catalog_io", "contract", "image_normalization", "operation_diagnostics"))
# Bind the loaded implementation as well as its current on-disk source. Editing
# modules in an already running process requires a fresh process, not a false
# claim that newly read bytes were the code used by the interpreter.
_LOADED = {name: hashlib.sha256((_ROOT / name).read_bytes()).hexdigest() for name in _MODULES}


def _error(exc, remaining=None):
    if isinstance(exc, BackgroundError):
        error = exc
    elif isinstance(exc, (KeyboardInterrupt, SystemExit)):
        error = BackgroundError("interrupted", "Background operation interrupted")
    elif isinstance(exc, MemoryError):
        error = BackgroundError("resource_exhausted", "Background operation exhausted available memory")
    elif isinstance(exc, OSError):
        error = BackgroundError("io_error", str(exc) or "Filesystem operation failed")
    else:
        error = BackgroundError("internal_error", str(exc) or "Unexpected background tool error")
    message = str(error).replace("\x00", "")[:4096].strip() or "Background operation failed"
    return {"status": error.status, "derivation": None, "output": None,
            "error": {"code": error.code, "message": message, "path": error.path},
            "remaining": remaining}


def _ref(name, raw):
    return {"file": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _tool(budget):
    budget.check()
    if __version__ != PILLOW_VERSION:
        raise BackgroundError("tool_mismatch", f"Background commands require Pillow {PILLOW_VERSION}; found {__version__}")
    versions = {"python": platform.python_version(), "pillow": __version__,
                "zlib": features.version_codec("zlib"),
                "littlecms": features.version_module("littlecms2")}
    if any(not isinstance(value, str) or not value.strip() for value in versions.values()):
        raise BackgroundError("internal_error", "Required codec version is unavailable")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_ROOT,
                                         text=True, stderr=subprocess.PIPE, timeout=10).strip()
        tree = subprocess.check_output(["git", "ls-tree", "-r", "HEAD", "--", *_MODULES],
                                       cwd=_ROOT, text=True, stderr=subprocess.PIPE, timeout=10)
    except (subprocess.SubprocessError, OSError) as exc:
        raise BackgroundError("internal_error", "Cannot bind background tool to its actual Git commit") from exc
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise BackgroundError("internal_error", "Invalid Git commit identity")
    committed = {line.split("\t", 1)[1]: line.split("\t", 1)[0].split()[2]
                 for line in tree.splitlines()}
    reader = io.Reader(_ROOT, budget)
    modules, dirty = [], False
    for name in _MODULES:
        raw = reader.read(name, MAX_JSON)
        sha = hashlib.sha256(raw).hexdigest()
        if sha != _LOADED[name]:
            raise BackgroundError("tool_mismatch", "Loaded tool source changed; restart the process", name)
        git_blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
        dirty = dirty or committed.get(name) != git_blob
        modules.append({"file": name, "sha256": sha})
    reader.recheck()
    budget.check()
    return {"id": "picross-background-1", "commit": commit, "dirty": dirty,
            "versions": versions, "modules": modules}


def describe():
    try:
        tool = _tool(io.Budget())
        return {"profile": parse_json(canonical(PROFILE)), "profile_sha256": digest(PROFILE),
                "tool": tool, "tool_sha256": digest(tool)}
    except (Exception, KeyboardInterrupt, SystemExit) as exc:
        return _error(exc)


def _png(raw, budget):
    """Validate framing, all CRCs and original bit depth before Pillow decode."""
    if len(raw) > MAX_PNG:
        raise BackgroundError("resource_limit", "PNG exceeds 32 MiB")
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise BackgroundError("invalid_image", "Selected original must be PNG")
    position, count, saw_idat, saw_end, idat_ended = 8, 0, False, False, False
    while position < len(raw):
        budget.check()
        if len(raw) - position < 12:
            raise BackgroundError("invalid_image", "Truncated PNG chunk")
        size = struct.unpack_from(">I", raw, position)[0]
        kind = raw[position + 4:position + 8]
        end = position + 12 + size
        if end > len(raw):
            raise BackgroundError("invalid_image", "Truncated PNG chunk payload")
        data = raw[position + 8:position + 8 + size]
        crc = struct.unpack_from(">I", raw, position + 8 + size)[0]
        if zlib.crc32(kind + data) & 0xffffffff != crc:
            raise BackgroundError("invalid_image", "PNG chunk checksum mismatch")
        if kind in (b"acTL", b"fcTL", b"fdAT"):
            raise BackgroundError("invalid_image", "Animated PNG is unsupported")
        if len(kind) != 4 or not all(65 <= c <= 90 or 97 <= c <= 122 for c in kind):
            raise BackgroundError("invalid_image", "Invalid PNG chunk type")
        if not count and kind != b"IHDR":
            raise BackgroundError("invalid_image", "PNG must begin with IHDR")
        if kind == b"IHDR":
            if count or size != 13:
                raise BackgroundError("invalid_image", "Invalid/duplicate PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", data)
            if width == 0 or height == 0:
                raise BackgroundError("invalid_image", "PNG dimensions must be positive")
            if max(width, height) > MAX_AXIS or width * height > MAX_PIXELS:
                raise BackgroundError("resource_limit", "PNG exceeds 8192 pixels/axis or 8000000 decoded pixels")
            valid_depths = {0: (1, 2, 4, 8), 2: (8,), 3: (1, 2, 4, 8), 4: (8,), 6: (8,)}
            if depth not in valid_depths.get(color, ()) or compression or filtering or interlace not in (0, 1):
                raise BackgroundError("invalid_image", "Unsupported PNG bit depth or encoding")
        elif kind == b"IDAT":
            if idat_ended:
                raise BackgroundError("invalid_image", "PNG IDAT chunks are not consecutive")
            saw_idat = True
        elif saw_idat:
            idat_ended = True
        if kind[0] & 32 == 0 and kind not in (b"IHDR", b"PLTE", b"IDAT", b"IEND"):
            raise BackgroundError("invalid_image", "Unknown critical PNG chunk")
        count += 1
        if kind == b"IEND":
            if size or end != len(raw) or not saw_idat:
                raise BackgroundError("invalid_image", "Invalid PNG end or trailing bytes")
            saw_end = True
            break
        position = end
    if not saw_end:
        raise BackgroundError("invalid_image", "Missing PNG end chunk")


def _diagnostic(image):
    histogram = image.getchannel("A").histogram()
    present = [value for value, count in enumerate(histogram) if count]
    if histogram[0] == 0:
        raise BackgroundError("opaque_image", "Image requires at least one fully transparent pixel")
    if histogram[0] == image.width * image.height:
        raise BackgroundError("empty_image", "Image requires at least one visible pixel")
    return {"format": "PNG", "mode": "RGBA", "width": image.width, "height": image.height,
            "alpha": {"min": present[0], "max": present[-1], "transparent_pixels": histogram[0],
                      "partial_pixels": sum(histogram[1:255]), "opaque_pixels": histogram[255]}}


def _render(raw, budget):
    _png(raw, budget)
    if ImageFile.LOAD_TRUNCATED_IMAGES:
        raise BackgroundError("internal_error", "Strict Pillow decoding was disabled by the host process")
    try:
        with Image.open(bytes_io.BytesIO(raw), formats=("PNG",)) as probe:
            if "icc_profile" in probe.info and not probe.info["icc_profile"]:
                raise BackgroundError("invalid_image", "Empty PNG ICC profile")
            probe.verify()
        normal, _, _ = normalize_bytes(raw, max_bytes=MAX_PNG, max_axis=MAX_AXIS, max_pixels=MAX_PIXELS)
    except (InvalidInput, OSError, ValueError, SyntaxError) as exc:
        raise BackgroundError("invalid_image", str(exc) or "Invalid source PNG") from exc
    budget.check()
    source_diagnostic = _diagnostic(normal)
    width, height = normal.size
    if width * 576 >= height * 2304:
        fit = (2304, max(1, height * 2304 // width))
    else:
        fit = (max(1, width * 576 // height), 576)
    scaled = (normal if normal.size == fit else
              normal.convert("RGBa").resize(fit, Image.Resampling.LANCZOS).convert("RGBA"))
    rgba = bytearray(scaled.tobytes())
    for index in range(0, len(rgba), 4):
        if rgba[index + 3] == 0:
            rgba[index:index + 3] = b"\0\0\0"
    scaled = Image.frombytes("RGBA", fit, bytes(rgba))
    canvas = Image.new("RGBA", (2304, 576), (0, 0, 0, 0))
    canvas.paste(scaled, ((2304 - fit[0]) // 2, 576 - fit[1]))
    _diagnostic(canvas)
    budget.check()
    info = PngImagePlugin.PngInfo()
    info.add(b"sRGB", b"\0")
    encoded = bytes_io.BytesIO()
    canvas.save(encoded, format="PNG", pnginfo=info, compress_level=9, optimize=False)
    result = encoded.getvalue()
    _png(result, budget)
    with Image.open(bytes_io.BytesIO(result), formats=("PNG",)) as actual:
        actual.load()
        if actual.mode != "RGBA" or actual.size != (2304, 576) or actual.info != {"srgb": 0}:
            raise BackgroundError("internal_error", "PNG encoder did not preserve the fixed profile")
        output_diagnostic = _diagnostic(actual)
    budget.check()
    return result, {"source": source_diagnostic, "output": output_diagnostic,
                    "upscaled": fit[0] > width or fit[1] > height}


def _prepare(request, reader, tool, budget):
    manifest, decision, candidate = load_inputs(request, reader)
    png, diagnostics = None, {"source": None, "output": None, "upscaled": None}
    if candidate is not None:
        png, diagnostics = _render(reader.read_ref(request["source"], MAX_PNG), budget)
    derivation = {"format": "picross-background-derivation-v1", "request_sha256": digest(request),
                  "request": request, "puzzle_id": manifest["puzzle_id"], "job_id": manifest["job_id"],
                  "background_revision": manifest["revision"],
                  "manifest": request["manifest"], "decision": request["decision"],
                  "outcome": decision["outcome"], "candidate_id": decision["candidate_id"],
                  "source": request["source"], "profile": request["profile"],
                  "profile_sha256": digest(request["profile"]), "tool": tool, "tool_sha256": digest(tool),
                  "output": _ref("background.png", png) if png is not None else None,
                  "diagnostics": diagnostics, "test_only": manifest["test_only"]}
    raw = canonical(derivation) + b"\n"
    if len(raw) > MAX_JSON:
        raise BackgroundError("resource_limit", "Derivation exceeds 2 MiB")
    return raw, png


def _check_output(directory, report, png, budget, *, conflict=False):
    try:
        directory = io.external(directory)
        if not directory.is_dir():
            raise BackgroundError("invalid_binding", "Output directory is missing or not a directory")
        expected = {"derivation.json": report}
        if png is not None:
            expected["background.png"] = png
        if {entry.name for entry in directory.iterdir()} != set(expected):
            raise BackgroundError("invalid_binding", "Output file set is incomplete, foreign or has extra entries")
        reader = io.Reader(directory, budget)
        for name, value in expected.items():
            actual = reader.read(name, MAX_JSON if name.endswith(".json") else MAX_PNG)
            if name == "derivation.json":
                decoded = parse_json(actual, name)
                if (isinstance(decoded, dict) and isinstance(decoded.get("format"), str) and
                        decoded["format"] != "picross-background-derivation-v1"):
                    raise BackgroundError("unsupported_format", "Unsupported declared derivation format", name)
            if actual != value:
                raise BackgroundError("invalid_binding", "Output does not match fresh deterministic derivation", name)
        reader.recheck()
        if {entry.name for entry in directory.iterdir()} != set(expected):
            raise BackgroundError("source_changed", "Output file set changed during verification")
    except BackgroundError as exc:
        if conflict and exc.status in ("invalid_input", "conflict"):
            raise BackgroundError("target_conflict", str(exc), exc.path) from exc
        raise
    return {"derivation": _ref("derivation.json", report),
            "output": _ref("background.png", png) if png is not None else None}


def _verification_tool(request, reader, current):
    """Keep producer provenance while requiring the same executable bytes/codecs."""
    report = parse_json(reader.read("derivation.json", MAX_JSON), "derivation.json")
    if not isinstance(report, dict):
        raise BackgroundError("invalid_binding", "Derivation must be an object", "derivation.json")
    if isinstance(report.get("format"), str) and report["format"] != "picross-background-derivation-v1":
        raise BackgroundError("unsupported_format", "Unsupported declared derivation format", "derivation.json")
    original = report.get("tool")
    if not isinstance(original, dict) or set(original) != {"id", "commit", "dirty", "versions", "modules"}:
        raise BackgroundError("invalid_binding", "Invalid original tool object", "derivation.json")
    commit = original["commit"]
    if (not isinstance(commit, str) or len(commit) != 40 or
            any(c not in "0123456789abcdef" for c in commit) or type(original["dirty"]) is not bool):
        raise BackgroundError("invalid_binding", "Invalid original tool provenance", "derivation.json")
    if (report.get("tool_sha256") != digest(original) or
            report["tool_sha256"] != request["expected_tool_sha256"] or
            report.get("request_sha256") != digest(request) or
            canonical(report.get("request")) != canonical(request)):
        raise BackgroundError("invalid_binding", "Original request/tool binding differs", "derivation.json")
    if any(original[key] != current[key] for key in ("id", "versions", "modules")):
        raise BackgroundError("tool_mismatch", "Original tool differs from the actual implementation/codecs")
    return original


def _run(request, source_root, output, *, verifying, budget=None, request_reader=None):
    stage, published, remaining, made_parents = None, None, None, []
    result = None
    try:
        budget = budget if budget is not None else io.Budget()
        request = validate_request(request)
        tool = _tool(budget)
        if not verifying and request["expected_tool_sha256"] != digest(tool):
            raise BackgroundError("tool_mismatch", "Requested tool hash differs from the actual implementation/codecs")
        source_root, output = io.roots(source_root, output)
        output_identity = io.identity(output.lstat())[:2]

        def output_unchanged():
            budget.check()
            try:
                current = io.identity(io.external(output).lstat())[:2]
            except (FileNotFoundError, BackgroundError) as exc:
                raise BackgroundError("target_conflict", "Explicit output root changed") from exc
            if current != output_identity:
                raise BackgroundError("target_conflict", "Explicit output root identity changed")

        reader = io.Reader(source_root, budget)
        report_reader = io.Reader(output, budget) if verifying else None
        producer = _verification_tool(request, report_reader, tool) if verifying else tool
        report, png = _prepare(request, reader, producer, budget)
        if verifying:
            output_unchanged()
            refs = _check_output(output, report, png, budget)
            report_reader.recheck()
            reader.recheck()
            if request_reader is not None:
                request_reader.recheck()
            if _tool(budget) != tool:
                raise BackgroundError("tool_mismatch", "Tool changed during verification")
            return {"status": "verified", **refs, "error": None, "remaining": None}
        target = io.safe(output, request["output"])
        output_unchanged()
        with io.writer(output):
            output_unchanged()
            if target.exists():
                refs = _check_output(target, report, png, budget, conflict=True)
                reader.recheck()
                if request_reader is not None:
                    request_reader.recheck()
                if _tool(budget) != tool:
                    raise BackgroundError("tool_mismatch", "Tool changed during derivation")
                return {"status": "reused", **refs, "error": None, "remaining": None}
            stage = io.Stage(output, digest(request))
            stage.prepare()
            if png is not None:
                stage.write("background.png", png)
            stage.write("derivation.json", report)
            _check_output(stage.payload, report, png, budget)
            io.parents(output, target, made_parents)
            # Re-resolve the exact destination after all reads/writes. Publish
            # itself is also no-replace against a last-moment target race.
            io.safe(output, request["output"])
            reader.recheck()
            if request_reader is not None:
                request_reader.recheck()
            if _tool(budget) != tool:
                raise BackgroundError("tool_mismatch", "Tool changed before publication")
            output_unchanged()
            budget.check()
            io.publish_directory(stage.payload, target)
            published = target
            refs = _check_output(target, report, png, budget)
            result = {"status": "derived" if png is not None else "none", **refs,
                      "error": None, "remaining": None}
    except (Exception, KeyboardInterrupt, SystemExit) as exc:
        result = _error(exc, str(published.absolute()) if published is not None and published.exists() else None)
    finally:
        if stage is not None:
            remaining = stage.cleanup()
        for parent in reversed(made_parents):
            try:
                parent.rmdir()
            except OSError:
                # Nonempty/published/foreign parents are never removed. A
                # failed cleanup of our unpublished parent remains visible.
                if published is None and remaining is None and parent.exists():
                    remaining = str(parent.absolute())
    if remaining:
        if result is not None and result["error"] is not None:
            result["remaining"] = remaining
        else:
            result = _error(BackgroundError("io_error", "Owned stage could not be completely cleaned up"), remaining)
    return result


def derive(request, source_root, output_root):
    return _run(request, source_root, output_root, verifying=False)


def verify(request, source_root, output_directory):
    return _run(request, source_root, output_directory, verifying=True)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise BackgroundError("invalid_request", message)


def main(argv=None):
    handlers = {}

    def interrupted(signum, frame):
        raise BackgroundError("interrupted", "Background operation interrupted by signal")

    try:
        for signum in (signal.SIGINT, signal.SIGTERM):
            handlers[signum] = signal.signal(signum, interrupted)
        parser = _Parser(description=__doc__, add_help=False)
        commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
        commands.add_parser("describe", add_help=False)
        for name, output_option in (("derive", "--output-root"), ("verify", "--output-dir")):
            sub = commands.add_parser(name, add_help=False)
            sub.add_argument("--request", required=True)
            sub.add_argument("--source-root", required=True)
            sub.add_argument(output_option, required=True)
        args = parser.parse_args(argv)
        if args.command == "describe":
            result = describe()
        else:
            request_path = io.external(args.request)
            budget = io.Budget()
            request_reader = io.Reader(request_path.parent, budget)
            request = parse_json(request_reader.read(request_path.name, MAX_JSON), request_path.name)
            request_reader.recheck()
            result = _run(request, args.source_root,
                          args.output_root if args.command == "derive" else args.output_dir,
                          verifying=args.command == "verify", budget=budget, request_reader=request_reader)
    except (Exception, KeyboardInterrupt, SystemExit) as exc:
        result = _error(exc)
    finally:
        for signum, prior in handlers.items():
            signal.signal(signum, prior)
    print(canonical(result).decode("utf-8"))
    return {"invalid_input": 2, "conflict": 2, "aborted": 4, "technical_error": 5}.get(result.get("status"), 0)


if __name__ == "__main__":
    sys.exit(main())
