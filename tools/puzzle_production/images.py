"""RP-3 image boundary and deterministic, bounded production pipeline.

Pillow is deliberately imported only here, never by the deduction core.
"""
from __future__ import annotations

import hashlib
import html
import io
import re
import shutil
import tempfile
import time
import uuid
import warnings
from pathlib import Path

from PIL import Image, ImageCms, ImageFilter, ImageOps, __version__, features

from .contract import (Aborted, Budget, InvalidInput, digest, exact_keys, integer,
                       load_json, validate_logic, write_json)
from .solver import solve
from .verifier import verify

VERSION = "rp3-image-1"
PILLOW_VERSION = "12.3.0"
MAX_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 8_000_000
MAX_AXIS = 8192
MAX_VARIANTS = 8
ID = re.compile(r"[a-z][a-z0-9_-]{0,31}\Z")
RGB = re.compile(r"#[0-9a-fA-F]{6}\Z")


def versions() -> dict:
    if __version__ != PILLOW_VERSION:
        raise InvalidInput(f"Image commands require Pillow {PILLOW_VERSION}, found {__version__}")
    return {"tool": VERSION, "pillow": __version__,
            "jpeg": features.version_codec("jpg"),
            "jpeg_turbo": features.version_feature("libjpeg_turbo"),
            "littlecms": features.version_module("littlecms2"),
            "zlib": features.version_codec("zlib")}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish_bundle(stage: Path, output: Path) -> None:
    # mkdtemp is private on Windows. Copy into a normally inherited sibling
    # before publishing, so files remain accessible to the repository owner.
    pending = output.parent / (".rp3-publish-" + uuid.uuid4().hex)
    pending.mkdir()
    try:
        shutil.copytree(stage, pending, dirs_exist_ok=True)
        if output.exists():
            raise InvalidInput("Output appeared during production; refusing to overwrite")
        pending.rename(output)
    finally:
        if pending.exists() and pending.resolve().parent == output.parent.resolve():
            shutil.rmtree(pending)


def rgb(value: object) -> tuple[int, int, int]:
    if not isinstance(value, str) or not RGB.fullmatch(value):
        raise InvalidInput("RGB must be #rrggbb")
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def validate_design(value: object) -> dict:
    d = exact_keys(value, {"format", "source_id", "origin", "rights", "briefing",
                           "working_mode", "width", "height", "crop", "fit",
                           "background", "alpha_below", "mode", "palette", "variants"})
    if d["format"] != "picross-image-design-v1":
        raise InvalidInput("Unsupported image design version")
    if not isinstance(d["source_id"], str) or not ID.fullmatch(d["source_id"]):
        raise InvalidInput("Invalid source_id")
    for key in ("origin", "rights", "briefing"):
        if not isinstance(d[key], str) or not 1 <= len(d[key]) <= 4096:
            raise InvalidInput(f"{key} requires 1..4096 characters")
    if d["working_mode"] not in ("faithful", "free"):
        raise InvalidInput("working_mode must explicitly be faithful or free")
    integer(d["width"], 1, 100, "width")
    integer(d["height"], 1, 100, "height")
    if d["fit"] not in ("contain", "exact"):
        raise InvalidInput("fit must be contain (letterbox) or exact (matching crop ratio)")
    if not isinstance(d["crop"], list) or len(d["crop"]) != 4:
        raise InvalidInput("crop requires [left, top, right, bottom] in oriented source pixels")
    for coord in d["crop"]:
        integer(coord, 0, MAX_AXIS, "crop coordinate")
    if d["crop"][2] <= d["crop"][0] or d["crop"][3] <= d["crop"][1]:
        raise InvalidInput("crop must have positive dimensions")
    rgb(d["background"])
    integer(d["alpha_below"], 1, 255, "alpha_below")
    if d["mode"] not in ("mono", "color"):
        raise InvalidInput("mode must be mono or color")
    palette = d["palette"]
    if not isinstance(palette, list) or not 1 <= len(palette) <= 8:
        raise InvalidInput("Expected 1..8 foreground colors")
    ids, colors = [], []
    for entry in palette:
        exact_keys(entry, {"id", "rgb"})
        if not isinstance(entry["id"], str) or not ID.fullmatch(entry["id"]) or entry["id"] == "empty":
            raise InvalidInput("Invalid foreground ID")
        ids.append(entry["id"])
        colors.append(rgb(entry["rgb"]))
    if len(set(ids)) != len(ids) or len(set(colors)) != len(colors):
        raise InvalidInput("Duplicate foreground ID/RGB")
    if rgb(d["background"]) in colors:
        raise InvalidInput("Empty/background RGB must differ from each foreground, including light colors")
    if d["mode"] == "mono" and ids != ["ink"]:
        raise InvalidInput("Mono mode requires only foreground ink")
    variants = d["variants"]
    if not isinstance(variants, list) or not 1 <= len(variants) <= MAX_VARIANTS:
        raise InvalidInput(f"Expected 1..{MAX_VARIANTS} variants")
    seen = set()
    for v in variants:
        exact_keys(v, {"id", "method", "threshold"})
        if not isinstance(v["id"], str) or not ID.fullmatch(v["id"]) or v["id"] in seen:
            raise InvalidInput("Invalid/duplicate variant ID")
        seen.add(v["id"])
        if v["method"] not in ("area", "contour"):
            raise InvalidInput("Only area and contour variants are supported")
        integer(v["threshold"], 0, 255, "threshold")
    # Palette input order is not a semantic or tie-breaking distinction.
    return {**d, "palette": sorted(palette, key=lambda e: e["id"])}


def normalize(path: Path) -> tuple[Image.Image, dict, bytes]:
    versions()
    with path.open("rb") as stream:
        original = stream.read(MAX_BYTES + 1)
    if len(original) > MAX_BYTES:
        raise InvalidInput(f"Image exceeds {MAX_BYTES} encoded bytes")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(original), formats=("PNG", "JPEG")) as source:
                fmt, size, mode = source.format, source.size, source.mode
                if max(size) > MAX_AXIS or size[0] * size[1] > MAX_PIXELS:
                    raise InvalidInput(f"Source exceeds {MAX_AXIS} pixels/axis or {MAX_PIXELS} decoded pixels")
                if getattr(source, "n_frames", 1) != 1:
                    raise InvalidInput("Animated/multiple-frame PNG is unsupported")
                if mode not in ("1", "L", "LA", "P", "RGB", "RGBA", "CMYK"):
                    raise InvalidInput(f"Unsupported source pixel mode {mode}; no silent high-depth conversion")
                orientation = source.getexif().get(274, 1)
                if orientation not in range(1, 9):
                    raise InvalidInput("Invalid EXIF orientation")
                icc = source.info.get("icc_profile")
                gamma = source.info.get("gamma")
                srgb = source.info.get("srgb")
                if not icc and gamma is not None and srgb is None and abs(gamma - 0.45455) > 0.0001:
                    raise InvalidInput("Non-sRGB PNG gamma requires an ICC profile")
                source.load()  # Strict decoding; LOAD_TRUNCATED_IMAGES stays false.
                oriented = ImageOps.exif_transpose(source)
                alpha = oriented.convert("RGBA").getchannel("A")
                if icc:
                    profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
                    # P/1/alpha are converted to their actual RGB components; CMYK
                    # and grayscale keep their profile's input mode.
                    input_mode = mode if mode in ("CMYK", "L") else "RGB"
                    color = ImageCms.profileToProfile(oriented.convert(input_mode), profile,
                              ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB")
                    treatment = "ICC to sRGB, perceptual intent"
                else:
                    if mode == "CMYK":
                        raise InvalidInput("Unprofiled CMYK JPEG is unsupported; supply ICC")
                    color = oriented.convert("RGB")
                    treatment = "untagged/sRGB RGB or gray interpreted as sRGB"
                color.putalpha(alpha)
                # Deliberately drop EXIF/ICC/text after the explicit transform.
                normalized = Image.frombytes("RGBA", color.size, color.tobytes())
                metadata = {"format": fmt, "source_size": list(size), "source_mode": mode,
                            "orientation": orientation, "normalized_size": list(normalized.size),
                            "color_treatment": treatment, "icc_sha256": hashlib.sha256(icc).hexdigest() if icc else None,
                            "alpha": "preserved, composited against design background only during rasterization"}
                return normalized, metadata, original
    except InvalidInput:
        raise
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError,
            Image.DecompressionBombWarning, ImageCms.PyCMSError) as exc:
        raise InvalidInput(f"Damaged/unsupported PNG or JPEG: {exc}") from exc


def rasterize(normalized: Image.Image, design: dict, variant: dict) -> list[list[str]]:
    l, t, r, b = design["crop"]
    if r > normalized.width or b > normalized.height:
        raise InvalidInput("Crop exceeds the oriented source")
    w, h = design["width"], design["height"]
    if design["fit"] == "exact" and (r - l) * h != (b - t) * w:
        raise InvalidInput("Crop and target aspect ratios differ; choose explicit contain or adjust crop")
    image = normalized.crop((l, t, r, b))
    if design["fit"] == "contain":
        # Integer geometry, centered padding. No stretch or hidden crop.
        if image.width * h > image.height * w:
            target = (w, max(1, image.height * w // image.width))
        else:
            target = (max(1, image.width * h // image.height), h)
    else:
        target = (w, h)
    background = Image.new("RGBA", image.size, (*rgb(design["background"]), 255))
    composed = Image.alpha_composite(background, image).convert("RGB").resize(target, Image.Resampling.BOX)
    alpha = image.getchannel("A").resize(target, Image.Resampling.BOX)
    canvas = Image.new("RGB", (w, h), rgb(design["background"]))
    coverage = Image.new("L", (w, h), 0)
    offset = ((w - target[0]) // 2, (h - target[1]) // 2)
    canvas.paste(composed, offset)
    coverage.paste(alpha, offset)
    luminance = canvas.convert("L")
    edges = luminance.filter(ImageFilter.FIND_EDGES) if variant["method"] == "contour" else None
    choices = [("empty", rgb(design["background"]))] + [(e["id"], rgb(e["rgb"])) for e in design["palette"]]
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            if coverage.getpixel((x, y)) < design["alpha_below"]:
                value = "empty"
            elif edges is not None and (x in (0, w - 1) or y in (0, h - 1) or edges.getpixel((x, y)) <= variant["threshold"]):
                # FIND_EDGES keeps source pixels at the border; those are not edges.
                value = "empty"
            elif design["mode"] == "mono":
                value = "ink" if edges is not None or luminance.getpixel((x, y)) < variant["threshold"] else "empty"
            else:
                pixel = canvas.getpixel((x, y))
                value = min(choices, key=lambda e: sum((a - b) ** 2 for a, b in zip(pixel, e[1])))[0]
            row.append(value)
        result.append(row)
    return result


def logic_from_matrix(matrix: list[list[str]], design: dict) -> dict:
    def hints(line):
        runs, previous = [], "empty"
        for value in line:
            if value != "empty":
                if value == previous:
                    runs[-1]["length"] += 1
                else:
                    runs.append({"length": 1, "color": value})
            previous = value
        return runs
    mono = design["mode"] == "mono"
    colors = [e["id"] for e in design["palette"]]
    wire = {"format": "picross-logic-v1" if mono else "picross-logic-v2",
            "width": design["width"], "height": design["height"], "colors": colors,
            "empty": "empty", "initial_domain": ["empty", *colors],
            "rules": {"id": "mono-gap-v1", "same_color_gap": 1} if mono else
                     {"id": "color-gap-v1", "same_color_gap": 1, "different_color_gap": 0},
            "row_clues": [hints(line) for line in matrix],
            "column_clues": [hints(list(line)) for line in zip(*matrix)]}
    return validate_logic(wire).to_wire()


def candidate(normalized_hash: str, design: dict, variant: dict, matrix: list) -> dict:
    data = {"format": "picross-image-candidate-v1", "revision": 1,
            "source_id": design["source_id"], "normalized_sha256": normalized_hash,
            "versions": versions(), "design": design, "variant": variant,
            "matrix": matrix, "logic_hash": digest(logic_from_matrix(matrix, design))}
    return {"id": digest(data), **data}


def raster_image(matrix: list, design: dict) -> Image.Image:
    colors = {"empty": rgb(design["background"]), **{e["id"]: rgb(e["rgb"]) for e in design["palette"]}}
    image = Image.new("RGB", (design["width"], design["height"]))
    image.putdata([colors[v] for row in matrix for v in row])
    return image


def inspect_candidate(directory: Path, variant_id: str, budget: Budget | None = None) -> tuple[dict, dict, dict]:
    """Rebuild identity/hints and freshly replay the written proof, ignoring flags."""
    manifest = load_json(directory / "manifest.json")
    if manifest.get("format") != "picross-image-manifest-v1":
        raise InvalidInput("Unsupported production manifest")
    if manifest.get("versions") != versions() or manifest.get("original") not in ("original.png", "original.jpg"):
        raise InvalidInput("Wrong image tool versions/original path")
    if not isinstance(manifest.get("files"), dict):
        raise InvalidInput("Missing production file bindings")
    for name, sha in manifest["files"].items():
        path = directory / name
        if (not isinstance(name, str) or Path(name).name != name or "\\" in name or path.is_symlink() or
                path.resolve().parent != directory.resolve() or file_hash(path) != sha):
            raise InvalidInput("Missing, altered or unsafe production file")
    if variant_id not in [v["id"] for v in manifest["design"]["variants"]]:
        raise InvalidInput("Unknown candidate variant")
    d = validate_design(manifest["design"])
    required = {manifest["original"], "normalized.png", "design.json", "index.html", "briefing.txt"}
    required.update(f'{v["id"]}-{suffix}' for v in d["variants"] for suffix in
                    ("candidate.json", "logic.json", "proof.json", "result.json", "raster.png"))
    if set(manifest["files"]) != required or d != load_json(directory / "design.json"):
        raise InvalidInput("Incomplete/inconsistent production file bindings")
    image, meta, _ = normalize(directory / manifest["original"])
    encoded = io.BytesIO()
    image.save(encoded, format="PNG")
    if (hashlib.sha256(encoded.getvalue()).hexdigest() != file_hash(directory / "normalized.png") or
            meta != manifest["normalization"]):
        raise InvalidInput("Normalization no longer matches original and tool versions")
    c = load_json(directory / f"{variant_id}-candidate.json")
    variant = next(v for v in d["variants"] if v["id"] == variant_id)
    expected = candidate(file_hash(directory / "normalized.png"), d, variant, rasterize(image, d, variant))
    if c != expected:
        raise InvalidInput("Candidate differs from imported source/parameters; regenerate proof")
    encoded = io.BytesIO()
    raster_image(c["matrix"], d).save(encoded, format="PNG")
    if hashlib.sha256(encoded.getvalue()).hexdigest() != file_hash(directory / f"{variant_id}-raster.png"):
        raise InvalidInput("Comparison raster differs from the candidate matrix")
    wire = logic_from_matrix(c["matrix"], d)
    if wire != load_json(directory / f"{variant_id}-logic.json"):
        raise InvalidInput("Stored clues differ from the final matrix")
    puzzle = validate_logic(wire)
    proof = load_json(directory / f"{variant_id}-proof.json", puzzle.proof_byte_limit)
    verified = verify(puzzle, proof, budget)
    if verified["certified"] and proof["final_domains"] != [[[v] for v in row] for row in c["matrix"]]:
        raise InvalidInput("Proven final raster differs from export matrix")
    return c, proof, verified


def comparison(directory: Path, manifest: dict, records: list[dict]) -> None:
    esc = lambda v: html.escape(str(v), quote=True)
    parts = ['<!doctype html><html lang="de"><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<title>RP-3 Produktionsvergleich</title><style>',
             'body{font:16px system-ui;margin:24px;color:#243b3b;background:#faf6ed}h1{font-size:26px}',
             '.images{display:flex;gap:24px;flex-wrap:wrap}figure{margin:0 0 24px}img.source{width:320px;height:320px;object-fit:contain;background:#ddd}',
             'img.cells{image-rendering:pixelated;width:400px;max-width:90vw}pre{white-space:pre-wrap;overflow-wrap:anywhere}',
             'table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:4px}section{border-top:2px solid #999;margin-top:32px}',
             '</style><h1>RP-3 Produktionsvergleich</h1>',
             '<p>Produktionsansicht mit Motivspoiler. Technische Zertifizierung, Motivqualität und redaktionelle Freigabe sind getrennt. Motiv-/Spielabnahme: offen.</p>',
             f'<p>Quelle: {esc(manifest["design"]["source_id"])} · Datei: {esc(manifest["original_filename"])}</p>',
             f'<p>Original SHA-256: {esc(manifest["files"][manifest["original"]])}<br>Normalisiert SHA-256: {esc(manifest["files"]["normalized.png"])}</p>',
             '<div class="images">',
             f'<figure><figcaption>Original (Orientierung nach Browser)</figcaption><img class="source" src="{manifest["original"]}" alt="Originaldatei"></figure>',
             '<figure><figcaption>Normalisiert: sRGB / EXIF angewendet / Alpha erhalten</figcaption><img class="source" src="normalized.png" alt="Normalisierung"></figure></div>',
             '<h2>Entwurf, Herkunft und Normalisierung</h2>',
             '<pre>' + esc(manifest["design"]) + '\n' + esc(manifest["normalization"]) + '\n' + esc(versions()) + '</pre>']
    for record in records:
        c, status, wire = record["candidate"], record["status"], record["logic"]
        name = c["variant"]["id"]
        parts.extend([f'<section><h2>{esc(name)} · {esc(status["status"])}</h2>',
                      '<pre>' + esc(status) + '</pre>', '<pre>Kandidat: ' + esc(c["id"]) + '\n' + esc(c["variant"]) + '</pre>',
                      f'<div class="images"><figure><figcaption>1 Pixel je Zelle ({wire["width"]}×{wire["height"]}); Datei in Originalgröße öffnen</figcaption><a href="{name}-raster.png"><img src="{name}-raster.png" alt="Raster bei Zellauflösung"></a></figure>',
                      f'<figure><figcaption>Vergrößert ohne Zwischenfarben</figcaption><img class="cells" src="{name}-raster.png" alt="Diskretes Raster vergrößert"></figure></div>'])
        for axis, lines in (("Zeilen", wire["row_clues"]), ("Spalten", wire["column_clues"])):
            parts.append(f'<h3>{axis}</h3><table><tr><th>Linie</th><th>Vollständige Hinweise (Länge:Farb-ID)</th></tr>')
            for i, line in enumerate(lines):
                parts.append(f'<tr><td>{i + 1}</td><td>{esc(" ".join(str(h["length"])+":"+h["color"] for h in line) or "–")}</td></tr>')
            parts.append('</table>')
        parts.append('</section>')
    parts.append('</html>')
    (directory / "index.html").write_text('\n'.join(parts) + '\n', encoding="utf-8", newline="\n")


def import_image(source: Path, design_path: Path, output: Path, seconds: float = 120, max_lines: int = 100_000) -> dict:
    Budget(seconds, max_lines)  # Validate budgets before creating any output.
    d = validate_design(load_json(design_path, 64 * 1024))
    image, normalization, original = normalize(source)
    if output.exists():
        raise InvalidInput("Output already exists; use a new directory to avoid stale certificates")
    output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    with tempfile.TemporaryDirectory(prefix="rp3-", dir=output.parent) as temp:
        stage = Path(temp) / "bundle"
        stage.mkdir()
        original_name = "original.png" if normalization["format"] == "PNG" else "original.jpg"
        (stage / original_name).write_bytes(original)
        image.save(stage / "normalized.png")
        write_json(stage / "design.json", d)
        for variant in d["variants"]:
            c = candidate(file_hash(stage / "normalized.png"), d, variant, rasterize(image, d, variant))
            wire = logic_from_matrix(c["matrix"], d)
            name = variant["id"]
            write_json(stage / f"{name}-candidate.json", c)
            write_json(stage / f"{name}-logic.json", wire)
            raster_image(c["matrix"], d).save(stage / f"{name}-raster.png")
            puzzle = validate_logic(wire)
            started = time.perf_counter()
            proof = solve(puzzle, Budget(seconds, max_lines))
            write_json(stage / f"{name}-proof.json", proof)
            try:
                status = verify(puzzle, load_json(stage / f"{name}-proof.json", puzzle.proof_byte_limit), Budget(seconds, max_lines))
            except Aborted as exc:
                status = {"status": "aborted", "certified": False, "proof_verified": False, "reason": str(exc)}
            if status["certified"] and proof["final_domains"] != [[[v] for v in row] for row in c["matrix"]]:
                raise InvalidInput("Proven final raster differs from intended matrix")
            status["elapsed_seconds"] = time.perf_counter() - started
            write_json(stage / f"{name}-result.json", status)
            records.append({"candidate": c, "logic": wire, "status": status})
        manifest = {"format": "picross-image-manifest-v1", "versions": versions(), "design": d,
                    "original": original_name, "original_filename": source.name, "normalization": normalization,
                    "limits": {"encoded_bytes": MAX_BYTES, "decoded_pixels": MAX_PIXELS, "source_axis": MAX_AXIS,
                               "variants": MAX_VARIANTS, "seconds_per_solver_or_verifier": seconds, "max_lines": max_lines},
                    "candidates": [{"variant": r["candidate"]["variant"]["id"], "id": r["candidate"]["id"], "technical": r["status"],
                                    "motif_review": "open", "editorial_release": "open"} for r in records],
                    "files": {p.name: file_hash(p) for p in sorted(stage.iterdir())}}
        comparison(stage, manifest, records)
        (stage / "briefing.txt").write_text(d["briefing"] + '\n\nWorking mode: ' + d["working_mode"] + '\nMotif and gameplay review: open\n', encoding="utf-8", newline="\n")
        manifest["files"].update({n: file_hash(stage / n) for n in ("index.html", "briefing.txt")})
        write_json(stage / "manifest.json", manifest)
        publish_bundle(stage, output)
    return {"status": "produced", "output": str(output), "candidates": manifest["candidates"]}
