"""Offline PERF-A manufacture and independent resource/image oracles."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import tempfile
import perf_a
import p1_preflight as tc

ROOT = perf_a.ROOT
PLAN = ROOT / "examples/perf_a/atlas-plan.json"
ASSETS = ROOT / "prototypes/p1/perf_a/atlases"
SOURCES = ROOT / "examples/perf_a/sources"


def image_api():
    import PIL
    from PIL import Image, ImageChops
    if PIL.__version__ != "12.3.0":
        raise ValueError("Manufacture/oracles require pinned Pillow 12.3.0")
    return Image, ImageChops


def pixel_hash(image):
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def import_settings(name):
    source = "res://perf_a/atlases/"+name
    target = "res://.godot/imported/"+name+"-"+hashlib.md5(source.encode()).hexdigest()+".ctex"
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


def neutral(black, white, kind, extrusion=2):
    """Viewport captures are premultiplied; encode straight-alpha coefficients."""
    Image, Chops = image_api()
    result = bytearray()
    black_bytes, white_bytes = memoryview(black.tobytes()), memoryview(white.tobytes())
    for i in range(0,len(white_bytes),4):
        if black_bytes[i+3] != white_bytes[i+3]:
            raise ValueError("Basis render coverage differs")
        alpha = white_bytes[i+3]
        if not alpha:
            result.extend((255, 0, 0, 0))
        elif kind == "x":
            result.extend((255, 0, 0, alpha))
        else:
            # Native Canvas transparent targets store premultiplied RGB.
            # B/A = highlight contribution; (W-B)/A = base contribution.
            base = round(max(0, white_bytes[i]-black_bytes[i])*255/alpha)
            highlight = round(black_bytes[i]*255/alpha)
            if base + highlight > 257:
                raise ValueError("Invalid neutral coefficients")
            result.extend((min(255, base), min(255, highlight), 0, alpha))
    image = Image.frombytes("RGBA", white.size, bytes(result))
    # Extend coefficients into two transparent pixels, never alpha. Filtering
    # then interpolates the same ink color rather than a black RGB border.
    coverage = image.getchannel("A").point(lambda a: 255 if a else 0)
    missing = Chops.invert(coverage)
    red, green, blue, alpha = image.split()
    offsets = sorted(((x,y) for x in range(-extrusion,extrusion+1) for y in range(-extrusion,extrusion+1) if x or y), key=lambda p:(p[0]**2+p[1]**2,p))
    for x,y in offsets:
        use = Chops.multiply(missing,Chops.offset(coverage,x,y))
        red.paste(Chops.offset(image.getchannel("R"),x,y),(0,0),use)
        green.paste(Chops.offset(image.getchannel("G"),x,y),(0,0),use)
        missing = Chops.subtract(missing,use)
    return Image.merge("RGBA",(red,green,blue,alpha))


def frame_records(image, plan, level):
    pixels, pad = level["pixels"], plan["padding"]
    pitch = pixels + 2*pad
    records = []
    for variant in range(plan["variants"]):
        for frame in range(plan["frames"]):
            x, y = frame*pitch, variant*pitch
            padded = image.crop((x, y, x+pitch, y+pitch))
            tile = padded.crop((pad, pad, pad+pixels, pad+pixels))
            bbox = tile.getchannel("A").getbbox()
            expected_padded = tuple(v+pad for v in bbox) if bbox else None
            if padded.getchannel("A").getbbox() != expected_padded:
                raise ValueError("Nontransparent padding / adjacent-frame leak")
            records.append(dict(variant=variant, frame=frame,
                elapsed_us=(frame*plan["duration_us"]+plan["frames"]-2)//(plan["frames"]-1),
                region=[x+pad, y+pad, pixels, pixels], alpha_bbox=list(bbox) if bbox else None,
                covered_pixels=sum(a > 0 for a in tile.getchannel("A").get_flattened_data()), pixel_sha256=pixel_hash(tile)))
    return records


def spatial_oracle(image, plan, level, kind):
    """Reject full underdraw/fade, duplicate end variants and X stroke reversal."""
    Image, Chops = image_api()
    records = frame_records(image, plan, level)
    n, pixels, pad = plan["frames"], level["pixels"], plan["padding"]
    pitch = pixels+2*pad
    ends = set()
    for v in range(plan["variants"]):
        row = records[v*n:(v+1)*n]
        if row[0]["covered_pixels"] != 0:
            raise ValueError("Full/old underdrawing at animation start")
        areas = [row[f]["covered_pixels"] for f in (4, 10, 20, n-1)]
        if not 0 < areas[0] < areas[1] < areas[2] <= areas[3]:
            raise ValueError("Spatial progression absent (fade/full target)")
        ends.add(row[-1]["pixel_sha256"])
        if kind == "x":
            def tile(f): return image.crop((f*pitch+pad, v*pitch+pad, f*pitch+pad+pixels, v*pitch+pad+pixels)).getchannel("A")
            early, final = tile(10), tile(n-1)
            # First diagonal occupies NW/SE; second diagonal NE/SW appears later.
            q = pixels//3
            corners = [(0, 0, q, q), (pixels-q, 0, pixels, q), (0, pixels-q, q, pixels), (pixels-q, pixels-q, pixels, pixels)]
            early_sums = [sum(early.crop(b).get_flattened_data()) for b in corners]
            final_sums = [sum(final.crop(b).get_flattened_data()) for b in corners]
            if early_sums[1] or early_sums[2] or not final_sums[1] or not final_sums[2]:
                raise ValueError("X stroke order absent/reversed")
    if len(ends) != (1 if kind == "fill" and level["name"] == "small" else plan["variants"]):
        raise ValueError("End variants duplicated / simplification changed")
    return dict(end_variants=len(ends), spatial_frames=plan["variants"]*n)


def generate(cache, output):
    if platform.system() != "Windows":
        raise ValueError("Reference manufacture is pinned to native Windows/OpenGL")
    Image, _ = image_api()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=False)
    originals, atlases = output / "sources", output / "atlases"
    originals.mkdir(); atlases.mkdir()
    with tempfile.TemporaryDirectory(prefix="picross-perfa-source-") as temporary:
        workspace = Path(temporary)
        engine = perf_a.prepare(cache, workspace)
        project = perf_a.source_project(plan["source_commit"], workspace / "source")
        shutil.copyfile(ROOT / "prototypes/p1/tests/perf_a_source.gd", project / "tests/perf_a_source.gd")
        environment = tc.isolated_environment(workspace / "profile", "Windows")
        environment.update(PERF_A_ATLAS_PLAN=str(PLAN), PERF_A_OUTPUT=str(originals))
        perf_a.run([engine, "--headless", "--path", project, "--import"], environment, output / "import.log")
        perf_a.run([engine, "--path", project, "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", "res://tests/perf_a_source.gd"], environment, output / "source.log", "PERF_A_SOURCE_OK")
        manifest = dict(format="picross-perf-a-atlas-v1", plan=plan, plan_sha256=perf_a.digest(PLAN),
            engine=tc.EXPECTED_VERSION, engine_archive_sha256=tc.EDITORS["Windows"].sha256,
            source_files={p: perf_a.digest(project / p) for p in ("ui/pencil_marks.gd", "ui/board.gd", "ui/grid_view.gd")},
            generator_files={p: perf_a.digest(ROOT / p) for p in ("tools/perf_a_atlas.py", "prototypes/p1/tests/perf_a_source.gd")},
            consumer_contract={p: perf_a.digest(ROOT / "prototypes/p1/perf_a" / p) for p in ("atlas.gd","mask.gdshader")},
            originals=[], atlases=[], usage="Developer-only PERF-A handover. Original project pencil; no third-party artwork. No palette copies. Excluded from player until PERF-B. Mipmaps/repeat/compression/source_color forbidden; linear filter; RGBA coefficients, straight alpha.")
        for p in sorted(originals.glob("*.png")):
            im = Image.open(p).convert("RGBA")
            manifest["originals"].append(dict(file=p.name, sha256=perf_a.digest(p), pixel_sha256=pixel_hash(im), size=list(im.size)))
        for level in plan["levels"]:
            for kind in ("fill", "x"):
                white = Image.open(originals / f"{kind}-{level['name']}-white.png").convert("RGBA")
                black = Image.open(originals / f"fill-{level['name']}-black.png").convert("RGBA") if kind == "fill" else white
                image = neutral(black, white, kind,plan["coefficient_extrusion_px"])
                name = f"{kind}-{level['name']}.png"
                path = atlases / name
                image.save(path, compress_level=9, optimize=False)
                imported = atlases / (name+".import")
                imported.write_text(import_settings(name),encoding="utf-8",newline="\n")
                item = dict(file=name, kind=kind, level=level["name"], size=list(image.size), bytes=path.stat().st_size,
                    decoded_bytes=image.width*image.height*4, sha256=perf_a.digest(path), pixel_sha256=pixel_hash(image),
                    safe_inner=[2*level["pixels"]/level["logical_cell"]]*2+[(level["logical_cell"]-4)*level["pixels"]/level["logical_cell"]]*2,
                    import_sha256=perf_a.digest(imported), frames=frame_records(image, plan, level), oracle=spatial_oracle(image, plan, level, kind))
                manifest["atlases"].append(item)
        manifest["resources"] = dict(png_bytes=sum(a["bytes"] for a in manifest["atlases"]),
            decoded_rgba_bytes=sum(a["decoded_bytes"] for a in manifest["atlases"]), textures=6, materials="one shared shader; palette materials reused by future renderer")
        perf_a.write_json(atlases / "manifest.json", manifest)
    print("PERF_A_ATLASES_OK", manifest["resources"], flush=True)


def verify(assets=ASSETS, sources=SOURCES):
    Image, _ = image_api()
    manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if manifest["plan"] != plan or manifest["plan_sha256"] != perf_a.digest(PLAN):
        raise ValueError("Atlas plan identity differs")
    for path, expected in manifest["generator_files"].items():
        if perf_a.digest(ROOT / path) != expected:
            raise ValueError("Stored manufacturer identity differs")
    for path, expected in manifest["source_files"].items():
        if perf_a.digest(ROOT / "prototypes/p1" / path) != expected:
            raise ValueError("A reference pencil differs from pinned source; rebind explicitly in B")
    for path, expected in manifest["consumer_contract"].items():
        if perf_a.digest(ROOT / "prototypes/p1/perf_a" / path) != expected:
            raise ValueError("Atlas material/identity contract differs")
    if {a["file"] for a in manifest["atlases"]} != {f"{k}-{l}.png" for k in ("fill","x") for l in ("small","medium","large")}:
        raise ValueError("Atlas inventory incomplete")
    for key, folder in (("originals", sources), ("atlases", assets)):
        for item in manifest[key]:
            path = folder / item["file"]
            image = Image.open(path).convert("RGBA")
            if perf_a.digest(path) != item["sha256"] or pixel_hash(image) != item["pixel_sha256"] or list(image.size) != item["size"]:
                raise ValueError("Atlas/source file or decoded pixel identity differs")
            if key == "atlases":
                if perf_a.digest(assets / (item["file"]+".import")) != item["import_sha256"]:
                    raise ValueError("Texture import contract differs")
                level = next(l for l in plan["levels"] if l["name"] == item["level"])
                if frame_records(image, plan, level) != item["frames"] or spatial_oracle(image, plan, level, item["kind"]) != item["oracle"]:
                    raise ValueError("Frame manifest/oracle differs")
                white = Image.open(sources / f"{item['kind']}-{item['level']}-white.png").convert("RGBA")
                black = Image.open(sources / f"fill-{item['level']}-black.png").convert("RGBA") if item["kind"] == "fill" else white
                if pixel_hash(neutral(black,white,item["kind"],plan["coefficient_extrusion_px"])) != item["pixel_sha256"]:
                    raise ValueError("Derivative differs from stored original basis renders")
    return manifest["resources"]


def derive(output, sources=SOURCES):
    """Reconstruct every derivative without Godot or a GPU, from saved originals."""
    Image, _ = image_api()
    output.mkdir(parents=True,exist_ok=False)
    manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["atlases"]:
        white = Image.open(sources / f"{item['kind']}-{item['level']}-white.png").convert("RGBA")
        black = Image.open(sources / f"fill-{item['level']}-black.png").convert("RGBA") if item["kind"]=="fill" else white
        path = output / item["file"]
        neutral(black,white,item["kind"],manifest["plan"]["coefficient_extrusion_px"]).save(path,compress_level=9,optimize=False)
        if perf_a.digest(path) != item["sha256"]:
            raise ValueError("Stored-source reproduction differs")
    print("PERF_A_STORED_SOURCE_REPRODUCTION_OK",flush=True)


def motion_oracle(output, motion, kind):
    Image, Chops = image_api()
    if len(motion) < 4 or any(b["elapsed_us"] <= a["elapsed_us"] for a,b in zip(motion,motion[1:])) or motion[-1]["last_frame"] != 23:
        raise ValueError("Native motion missing elapsed-time progression/end")
    if not any(0 < m["first_frame"] < 23 for m in motion):
        raise ValueError("Native motion only shows endpoints")
    if not any(m["last_state"]=="waiting" and m["last_frame"]==23 for m in motion) or motion[-1]["last_state"]!="rest":
        raise ValueError("Waiting/endframe mapping absent")
    waiting = Image.open(output / f"motion-{kind}-waiting.png").convert("RGBA")
    rest = Image.open(output / f"motion-{kind}-rest.png").convert("RGBA")
    distinct = set()
    for record in motion:
        actual = Image.open(output / record["file"]).convert("RGBA")
        if actual.size != (964,28) or not actual.getchannel("A").getbbox():
            raise ValueError("Native motion empty/not rendered")
        distinct.add(pixel_hash(actual))
        if record["last_state"] == "waiting":
            box = (938,0,962,28)
            if Chops.difference(actual.crop(box),waiting.crop(box)).getbbox():
                raise ValueError("Waiting target differs from endform at 56%")
    if len(distinct) < 4:
        raise ValueError("Native motion stale / spatial progression absent")
    if Chops.difference(actual,rest).getbbox():
        raise ValueError("Native motion does not reach exact resting endforms")
    return len(distinct)


def native_oracle(output, require_restart=True):
    Image, Chops = image_api()
    raw = json.loads((output / "probe.json").read_text(encoding="utf-8"))
    if raw["failures"] or raw["checks"] < 70 or (require_restart and not raw["fresh_process_compared"]):
        raise ValueError("Incomplete native atlas probe/restart")
    comparisons = []
    for lod in ("small", "medium", "large"):
        expected_x = Image.open(output / f"reference-x-{lod}.png").convert("RGBA")
        actual_x = Image.open(output / f"color-x-{lod}.png").convert("RGBA")
        if max(max(c.getextrema()) for c in Chops.difference(expected_x,actual_x).split()) > 4:
            raise ValueError("Native X ink/alpha differs")
        for color in range(4):
            expected = Image.open(output / f"reference-{lod}-{color}.png").convert("RGBA")
            actual = Image.open(output / f"color-{lod}-{color}.png").convert("RGBA")
            difference = Chops.difference(expected, actual)
            maximum = max(max(channel.getextrema()) for channel in difference.split())
            if maximum > 4:
                raise ValueError(f"Native palette/alpha reconstruction differs: {lod}/{color}: {maximum}")
            comparisons.append(dict(level=lod, color=color, maximum_channel_error=maximum))
        end = Image.open(output / f"color-{lod}-0.png").convert("RGBA")
        preview = Image.open(output / f"preview-{lod}.png").convert("RGBA")
        expected_preview = end.point(lambda v: round(v*.56))
        if max(max(c.getextrema()) for c in Chops.difference(expected_preview, preview).split()) > 3:
            raise ValueError("Preview/waiting silhouette or opacity changed")
        wrong = Image.open(output / f"wrong-variant-{lod}.png").convert("RGBA")
        if Chops.difference(end, wrong).getbbox() is None:
            raise ValueError("Wrong-variant negative control not detected")
    tinted = Image.open(output / "wrong-gray-tint.png").convert("RGBA")
    dark = Image.open(output / "color-medium-0.png").convert("RGBA")
    if max(max(c.getextrema()) for c in Chops.difference(dark,tinted).split()) <= 4:
        raise ValueError("Gray-tint negative color oracle not detected")
    for record in raw["records"]:
        size, kind = record["size"], record["kind"]
        name = record["file"]
        if Path(name).name != name or not name.startswith("flat-"+kind+"-"):
            raise ValueError("Invalid native flat capture path")
        alpha = Image.open(output / name).getchannel("A")
        for pixel in range(alpha.width):
            distance = abs((pixel+.5-2)/size-round((pixel+.5-2)/size))*size
            if distance < .45 and (alpha.crop((pixel, 0, pixel+1, alpha.height)).getbbox() or alpha.crop((0,pixel,alpha.width,pixel+1)).getbbox()):
                raise ValueError("Native nonintegral filtering closes cell gap")
    for kind in ("fill","x"):
        alpha = Image.open(output / f"clipped-{kind}.png").getchannel("A")
        # Native scissor rounding may include the boundary pixel. Outside this
        # outward-rounded rectangle every alpha byte must remain exactly zero.
        allowed = Image.new("L",alpha.size)
        allowed.paste(255,(11,13,103,91))
        if Chops.multiply(alpha,Chops.invert(allowed)).getbbox():
            raise ValueError("Atlas native clipping leaks outside viewport")
    motion = raw["motion"]
    motion_images = {kind:motion_oracle(output,[m for m in motion if m["kind"]==kind],kind) for kind in ("fill","x")}
    report = dict(checks=raw["checks"], fresh_process_compared=raw["fresh_process_compared"],
        native_color_comparisons=comparisons, gap_cases=len(raw["records"]), motion_frames=len(motion), distinct_motion_images=motion_images,
        source_rendering_driver=raw["renderer"], video_adapter=raw["video_adapter"],
        texture_memory_bytes=raw["texture_memory_bytes"], negative_controls=["wrong variant", "full underdrawing", "global fade", "reversed X", "duplicate end variants", "changed imported pixels"],
        static_memory_bytes=raw["static_memory_bytes"], smallest_actual_cell=raw["smallest_actual_cell"], largest_actual_cell=raw["largest_actual_cell"],
        manifest_sha256=perf_a.digest(ASSETS / "manifest.json"),
        scripts={p:perf_a.digest(ROOT / p) for p in ("tools/perf_a_atlas.py","prototypes/p1/tests/perf_a_atlas_probe.gd","prototypes/p1/perf_a/atlas.gd","prototypes/p1/perf_a/mask.gdshader")},
        image_sha256={p.name:perf_a.digest(p) for p in sorted(output.glob("*.png"))},
        probe_sha256=perf_a.digest(output / "probe.json"))
    perf_a.write_json(output / "verified.json", report)
    return report


def probe(cache, output):
    if platform.system() != "Windows":
        raise ValueError("Local handover probe requires native Windows")
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="picross-perfa-probe-") as temporary:
        workspace = Path(temporary)
        engine = perf_a.prepare(cache, workspace)
        project = workspace / "p1"
        shutil.copytree(ROOT / "prototypes/p1", project, ignore=shutil.ignore_patterns(".godot", "build"))
        environment = tc.isolated_environment(workspace / "profile", "Windows")
        environment.update(PERF_A_ATLAS_PLAN=str(PLAN), PERF_A_OUTPUT=str(output))
        perf_a.run([engine, "--headless", "--path", project, "--import"], environment, output / "import.log")
        for repetition in range(2):
            perf_a.run([engine, "--path", project, "--rendering-driver", "opengl3", "--audio-driver", "Dummy", "--script", "res://tests/perf_a_atlas_probe.gd"], environment, output / f"probe-{repetition}.log", "PERF_A_ATLAS_PROBE_OK")
            native_oracle(output, require_restart=bool(repetition))
    print("PERF_A_NATIVE_ATLAS_OK", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["generate", "verify", "derive", "probe"])
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.action == "generate":
        generate(args.cache_dir.resolve(), args.output_dir.resolve())
    elif args.action == "probe":
        probe(args.cache_dir.resolve(), args.output_dir.resolve())
    elif args.action == "derive":
        derive(args.output_dir.resolve())
    else:
        print("PERF_A_ATLAS_VERIFY_OK", verify())


if __name__ == "__main__": main()
