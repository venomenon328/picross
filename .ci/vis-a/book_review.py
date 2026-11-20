"""One VIS-A review run on the regular root. Retire with the #728 evidence request."""
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
import background_import
import p1_preflight as tc
from product_background_fixtures import write_image
from product_fixtures import copy_regression_game


def prepare(project):
    copy_regression_game(ROOT, project)
    registry_file = project / "data/registry.json"
    registry = json.loads(registry_file.read_bytes())
    # Reuse the valid completed T02 history and geometry with an isolated v8 identity.
    item = registry["entries"][1]
    ident = "pz-vis-a"
    background = f"art/backgrounds/{ident}.png"
    image = write_image(project / background)
    asset = dict(file=background, bytes=image["source_bytes"], sha256=image["source_sha256"])
    item.update(id=ident, name="Đà Nẵng", added_at=None, background=dict(status="selected", image_revision=1, asset=asset))
    registry.update(format="picross-runtime-registry-v8", entries=[item])
    definition_file = project / item["definition"]
    definition = json.loads(definition_file.read_bytes())
    item["reveal"] = str(Path(item["reveal"]).with_suffix(".png")).replace(os.sep, "/")
    registry_file.write_text(json.dumps(registry), encoding="utf-8")
    definition["id"] = definition["reveal"]["definition_id"] = ident
    definition["reveal"]["image"] = "res://"+item["reveal"]
    definition_file.write_text(json.dumps(definition), encoding="utf-8")
    art = Image.new("RGBA",(256,256))
    draw = ImageDraw.Draw(art)
    draw.ellipse((22,22,234,234), fill=(80,135,165,110))
    draw.ellipse((58,58,198,198), fill=(222,172,65,255))
    art.save(project / item["reveal"])
    inventory = dict(format=background_import.FORMAT, registry_sha256=background_import._hash(registry_file.read_bytes()),
                     assets=[dict(id=ident, image_revision=1, asset=asset, notice=None)])
    background_import.prepare_import(project, inventory)
    saved = json.loads((project / "tests/fixtures/runtime" / (item["key"]+".json")).read_bytes())
    saved["definition_id"] = ident
    return item["save_slot"], saved


def review(output, cache=None, *, local_engine=None):
    output.mkdir(parents=True, exist_ok=True)
    host = platform.system()
    with TemporaryDirectory(prefix="vis-a-",dir=output.parent) as sandbox:
        workspace = Path(sandbox)
        project = workspace / "game"
        key, saved = prepare(project)
        engine = local_engine
        if engine is None:
            archive = tc.EDITORS[host]
            tc.verify_sha256(cache / archive.name, archive.sha256)
            engine = str(tc.extract_editor(cache / archive.name,workspace / "engine",host))
        env = tc.isolated_environment(workspace,host)
        saves = workspace / "saves"
        saves.mkdir()
        (saves / (key+".json")).write_text(json.dumps(saved), encoding="utf-8")
        env.update(VIS_A_OUTPUT=str(output), P1_TEST_SAVE_ROOT=str(saves), LIBGL_ALWAYS_SOFTWARE="1")
        base = [engine, "--path", str(project)]
        subprocess.run(base + ["--headless","--import"],env=env,check=True,timeout=180,stdout=subprocess.DEVNULL)
        command = base + ["--resolution","1920x1080","--script",str(Path(__file__).with_name("review.gd")),"--","--p1-capture"]
        if host == "Linux":
            command = ["xvfb-run","-a","-s","-screen 0 1920x1080x24"] + command
        result = subprocess.run(command,env=env,timeout=180,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log = result.stdout.decode("utf-8", errors="replace")
        print(log, flush=True)
        if result.returncode or "VIS_A_BOOK_OK" not in log or "SCRIPT ERROR" in log or "ERROR:" in log:
            raise ValueError("VIS-A book scenario failed")
    with Image.open(output/"capture.png") as captured, Image.open(output/"direct.png") as direct:
        delta = ImageChops.difference(captured.convert("RGB"), direct.convert("RGB"))
        peak = max(high for _,high in delta.getextrema())
        mean = sum(ImageStat.Stat(delta).mean)/3
        print("VIS_A_HANDOVER", peak, mean)
        if peak > 4 or mean > 0.1:
            raise ValueError("Capture/direct handover differs")
    frames = []
    for path in sorted(output.glob("motion-*.png")):
        with Image.open(path) as frame:
            frames.append(frame.convert("RGB").resize((768,432),Image.Resampling.LANCZOS))
    frames[0].save(output/"motion.gif",save_all=True,append_images=frames[1:],duration=350,loop=0)


if __name__ == "__main__":
    review(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve() if len(sys.argv)>2 else None,
           local_engine=os.environ.get("VIS_A_LOCAL_ENGINE"))
