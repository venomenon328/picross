"""Temporary HP-I2-T02 evidence. Never imported by the product or normal CI."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _file(path):
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return dict(file=path.name, bytes=path.stat().st_size, sha256=digest)


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def _logic(project):
    runtime = _json(project / "data/registry.json")
    entries = [{key: value for key, value in entry.items() if key != "background"}
               for entry in runtime["entries"]]
    files = {entry[key] for entry in entries for key in ("definition", "reveal")}
    files |= {name.removesuffix(".png") + ".txt" for name in files if name.startswith("art/")}
    bound = {name: _sha((project / name).read_bytes()) for name in sorted(files) if (project / name).is_file()}
    return dict(categories=runtime["categories"], entries=entries, files=bound)


@contextmanager
def _report_environment(path):
    key = "HP_BACKGROUND_REPORT"
    previous = os.environ.get(key)
    os.environ[key] = str(path)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous


def run_delivery(repo, fixture, work, engine, environment, run_phase, *, cache=None):
    """Build actual Windows/Web fixtures, controlled baseline and regular Web.

    run_phase(label, command, phase_env=env) must fail on nonzero/error output.
    cache contains the ordinary verified toolchain archives. All construction
    files are disposable; only this JSON-serializable report leaves the call.
    """
    repo, work = Path(repo).resolve(), Path(work).resolve()
    if cache is None:
        raise ValueError("T02 requires the verified cache for the ordinary Web builder")
    cache = Path(cache).resolve()
    work.mkdir(parents=True, exist_ok=True)
    if any(work.iterdir()):
        raise ValueError("T02 work directory must be empty")
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "tools"))
    import background_import as bg
    import build_web_player
    from product_fixtures import copy_regression_game, restore_player_catalog
    from PIL import Image

    if Path(build_web_player.__file__).resolve().parents[1] != repo:
        raise ValueError("T02 must use the actual product Web builder")
    checkout = Path(fixture["checkout"]).resolve()
    source = bg.source_inventory(checkout)
    regular_source = bg.source_inventory(repo)
    if len(source["assets"]) != 2:
        raise ValueError("T02 requires exactly the two integrated selected images")
    for row in source["assets"]:
        with Image.open(checkout / "game" / row["asset"]["file"]) as image:
            image.load()
            if image.mode != "RGBA" or image.size != (2304, 576):
                raise ValueError("T02 integrated source does not match PNG2304")
            row["rgba_sha256"] = _sha(image.tobytes())
    phase_summaries = []

    def run(label, args, env=None):
        result = run_phase("hp-i2-t02-" + label, [str(engine), *map(str, args)],
                           phase_env=environment.copy() if env is None else env)
        summary = dict(name=label)
        if isinstance(result, dict):
            summary.update({key: result[key] for key in ("exit_code", "seconds") if key in result})
            if "output" in result:
                raw = result["output"].encode("utf-8")
                summary.update(output_bytes=len(raw), output_sha256=_sha(raw))
        phase_summaries.append(summary)

    def imported(project, expected, label):
        bg.prepare_import(project, expected)
        run(label + "-import", ["--headless", "--path", project, "--import"])
        return bg.verify_import(project, expected)

    def verify_pack_report(path, expected, target):
        report = _json(path)
        if set(report) != {"format", "target", "images", "inventory", "imported_inventory"} or report["format"] != "picross-background-pack-v1" or report["target"] != target:
            raise ValueError("T02 unexpected pack report form")
        rows = {row["id"]: row for row in report["images"]}
        if len(rows) != len(report["images"]) or set(rows) != {row["id"] for row in expected["assets"]}:
            raise ValueError("T02 pack report selection differs")
        names = sorted(Path(row[key]["file"]).name for row in expected["assets"] for key in ("asset", "notice"))
        remaps = sorted(Path(bg.remap_path(row["asset"]["file"])).name for row in expected["assets"])
        if report["inventory"] != names or report["imported_inventory"] != remaps:
            raise ValueError("T02 pack inventories differ")
        for expected_row in expected["assets"]:
            row = rows[expected_row["id"]]
            if (row["asset"] != expected_row["asset"] or row["image_revision"] != expected_row["image_revision"]
                    or row["notice_sha256"] != expected_row["notice"]["sha256"]
                    or row["base_rgba_sha256"] != expected_row.get("rgba_sha256", row["base_rgba_sha256"])
                    or row["mipmap_count"] != 11 or row["decoded_base_bytes"] != 5308416
                    or row["decoded_with_mips_bytes"] != 7077844):
                raise ValueError("T02 actual texture/notice/mipmap report differs")
        return report

    with tempfile.TemporaryDirectory(prefix="hp-i2-t02-", dir=work) as temporary:
        stage = Path(temporary)

        def export(project, expected, label, target):
            output = stage / (label + "-" + target)
            output.mkdir()
            destination = output / ("picross-p1.exe" if target == "windows" else "index.html")
            preset = "P1 Windows x86_64" if target == "windows" else "P1 Web"
            run(label + "-" + target + "-export", ["--headless", "--path", project, "--export-debug", preset, destination])
            pack = destination.with_suffix(".pck")
            if not pack.is_file():
                raise ValueError("T02 exported pack is missing")
            with pack.open("rb") as stream:
                if stream.read(4) != b"GDPC":
                    raise ValueError("T02 exported pack header differs")
            expected_file = output / "source-inventory.json"
            report_file = output / "background-pack.json"
            _write(expected_file, expected)
            count = sum(entry["visible"] for entry in _json(project / "data/registry.json")["entries"])
            env = {**environment, "ZA1_PACK_COUNT": str(count), "HP_BACKGROUND_EXPECTED": str(expected_file),
                   "HP_BACKGROUND_REPORT": str(report_file), "HP_BACKGROUND_PACK_TARGET": target}
            run(label + "-" + target + "-pck", ["--headless", "--main-pack", pack, "--script", repo / "game/tests/content_pack_probe.gd"], env)
            audit = verify_pack_report(report_file, expected, target)
            files = [destination, pack]
            files += [output / "picross-p1.console.exe"] if target == "windows" else [output / "index.js", output / "index.wasm"]
            return dict(files=[_file(path) for path in files], pck=_file(pack), audit=audit)

        selected_project = stage / "selected-game"
        copy_regression_game(repo, selected_project)
        restore_player_catalog(checkout, selected_project, background_inventory=source)
        source_logic = _logic(selected_project)
        selected_import = imported(selected_project, source, "selected")
        selected = {target: export(selected_project, source, "selected", target) for target in ("windows", "web")}

        # A controlled measurement copy of the same four logical entries. This
        # deliberately changes only runtime declarations/resources; it is not a
        # catalog write or an authority/recovery test.
        baseline_project = stage / "without-game"
        shutil.copytree(selected_project, baseline_project, ignore=shutil.ignore_patterns("build"))
        baseline_runtime = _json(baseline_project / "data/registry.json")
        baseline_runtime["format"] = "picross-runtime-registry-v5"
        for entry in baseline_runtime["entries"]:
            del entry["background"]
        # Match the actual projection's canonical serialization so the measured
        # PCK delta does not include an unrelated pretty-printing change.
        (baseline_project / "data/registry.json").write_text(
            json.dumps(baseline_runtime, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8", newline="\n")
        baseline_inventory = dict(format=bg.FORMAT, source_game="",
            registry_sha256=_sha((baseline_project / "data/registry.json").read_bytes()), assets=[])
        bg.restore_sources(checkout, baseline_project, baseline_inventory)
        if _logic(baseline_project) != source_logic:
            raise ValueError("T02 baseline changed logical/reveal/save/runtime identity")
        baseline_import = imported(baseline_project, baseline_inventory, "without")
        baseline = {target: export(baseline_project, baseline_inventory, "without", target) for target in ("windows", "web")}

        # Exercise restoration after actual selected resources/imports existed,
        # then independently build the real regular Web bundle through its normal
        # source-bound builder. The required native.export supplies regular Windows.
        restore_player_catalog(repo, selected_project, background_inventory=regular_source)
        restored_import = imported(selected_project, regular_source, "regular-restored")
        if (selected_project / "data/registry.json").read_bytes() != (repo / "game/data/registry.json").read_bytes():
            raise ValueError("T02 regular runtime was not restored")
        if any((selected_project / path).exists() for path in ("data/fixtures", "art/fixtures")):
            raise ValueError("T02 regular player kept synthetic geometry resources")
        synthetic_ids = set(fixture["ids"].values())
        if synthetic_ids & {entry["id"] for entry in _json(selected_project / "data/registry.json")["entries"]}:
            raise ValueError("T02 regular player retained synthetic catalog entries")
        for identifier in synthetic_ids:
            if list((selected_project / ".godot/imported").glob(identifier + ".png-*")):
                raise ValueError("T02 regular player retained synthetic imported backgrounds")
        regular_bundle = stage / "regular-web"
        regular_report_path = stage / "regular-web-backgrounds.json"
        started = time.perf_counter()
        with _report_environment(regular_report_path):
            web_manifest = build_web_player.build(cache, regular_bundle)
        regular_seconds = time.perf_counter() - started
        if web_manifest["kind"] != "player":
            raise ValueError("T02 regular Web bundle is not an ordinary clean player build")
        web_pack = regular_bundle / "releases" / web_manifest["build_id"] / "index.pck"
        regular_audit = verify_pack_report(regular_report_path, regular_source, "web")
        # Re-read source authority and bytes after every engine/build operation.
        actual_source = bg.source_inventory(checkout)
        if [{k: v for k, v in row.items() if k != "rgba_sha256"} for row in source["assets"]] != actual_source["assets"] or source["registry_sha256"] != actual_source["registry_sha256"]:
            raise ValueError("T02 changed its integration source")
        if bg.source_inventory(repo) != regular_source:
            raise ValueError("T02 changed regular background sources")
        decoded = selected["windows"]["audit"]["images"]
        if selected["web"]["audit"]["images"] != decoded:
            raise ValueError("T02 Web/Windows imported image results differ")
        return dict(format="picross-hp-i2-t02-v1",
            source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
            fixture_ids=fixture["ids"], logical_basis_sha256=_sha(json.dumps(source_logic, sort_keys=True).encode()),
            source_inventory=source, selected_import=selected_import, selected=selected,
            baseline=dict(control="Same logical/reveal/save fields; runtime-v5 copy without background declarations or resources. Not a catalog writer operation.",
                          runtime_sha256=baseline_inventory["registry_sha256"], imports=baseline_import, exports=baseline),
            measurements=dict(source_png_bytes=sum(row["asset"]["bytes"] for row in source["assets"]),
                source_notice_bytes=sum(row["notice"]["bytes"] for row in source["assets"]),
                imported_texture_bytes=selected_import["imported_bytes"],
                decoded_base_bytes=sum(row["decoded_base_bytes"] for row in decoded),
                decoded_with_mips_bytes=sum(row["decoded_with_mips_bytes"] for row in decoded),
                pck_growth_bytes={target: selected[target]["pck"]["bytes"] - baseline[target]["pck"]["bytes"] for target in selected}),
            regular_restoration=dict(runtime_sha256=regular_source["registry_sha256"], imports=restored_import,
                synthetic_sources_and_imports_removed=True, original_source_unchanged=True,
                ordinary_web_builder=True, web_build_id=web_manifest["build_id"], web_source_commit=web_manifest["source_commit"],
                web_build_seconds=regular_seconds, web_pck=_file(web_pack), web_audit=regular_audit),
            phases=phase_summaries,
            limits=["Linux engine inspects exported Windows/Web PCKs; no native Windows executable start or browser interaction.",
                    "PCK growth includes selected textures, notices and runtime bindings in this fixed sample, not a series forecast.",
                    "Web still downloads its complete PCK; on-demand decoding does not reduce network transfer."])
