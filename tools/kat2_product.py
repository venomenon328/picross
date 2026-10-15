"""Bounded native KAT-2 evidence in disposable projects/profiles; all fixtures test_only."""
from copy import deepcopy
import json
from pathlib import Path
import shutil

import p1_preflight as toolchain
from product_fixtures import copy_regression_game, install_runtime_fixtures


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")


def fixture(project: Path, saves: Path, mode: str) -> dict:
    """Synthetic load only: no 300 solver/production runs and no real approvals."""
    registry_path = project / "data/registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if mode == "empty":
        registry["entries"] = []
        registry["categories"] = []
    elif mode == "invalid":
        registry["entries"][0]["category_id"] = "missing-test-only-category"
    elif mode == "large":
        source = json.loads((project / "data/fixtures/t01.json").read_text(encoding="utf-8"))
        old_save = json.loads((project / "tests/fixtures/runtime/t01.json").read_text(encoding="utf-8"))
        registry["entries"] = []
        for index in range(300):
            identifier, stem = f"pz-test-kat2-{index:03d}", f"kat2_{index:03d}"
            data = deepcopy(source)
            data.update(id=identifier, test_only=True)
            data["reveal"].update(definition_id=identifier, name=f"TEST ONLY Motiv {index}", image=f"res://art/{stem}.svg")
            write_json(project / f"data/{stem}.json", data)
            shutil.copyfile(project / "art/fixtures/t01.svg", project / f"art/{stem}.svg")
            registry["entries"].append(dict(id=identifier, key=stem, save_slot=stem, definition=f"data/{stem}.json",
                reveal=f"art/{stem}.svg", visible=True, category_id="gebaeude-bauwerke" if index < 250 else "voegel"))
            if index % 2 == 0:
                saved = deepcopy(old_save)
                cells = [n if n > 0 else -1 for row in data["solution"] for n in row]
                changes = [dict(index=i, before=-1, after=n) for i, n in enumerate(cells) if n > 0]
                saved.update(definition_id=identifier, definition_revision=data["revision"], cells=cells,
                             history=[changes], cursor=1, undo_used=False, completed=True)
                write_json(saves / f"{stem}.json", saved)
    elif mode != "regular":
        raise ValueError("Unknown KAT2 fixture mode")
    write_json(registry_path, registry)
    marker = dict(format="picross-kat2-fixture-v1", test_only=True, mode=mode,
                  entries=len(registry["entries"]), categories=len(registry["categories"]))
    write_json(project / "tests/kat2-fixture.json", marker)
    return marker


def run(root, workspace, output, engine, environment, phase, python_phase, host):
    directory = output / "kat2"
    directory.mkdir()
    reports = []
    for mode in ("regular", "restart", "large", "empty", "invalid", "adapter", "information", "kb"):
        project = workspace / ("kat2-" + mode) / "game"
        copy_regression_game(root, project)
        saves = workspace / ("kat2-" + ("regular" if mode == "restart" else mode) + "-saves")
        saves.mkdir(exist_ok=mode == "restart")
        if mode == "adapter":
            from tools.puzzle_production.za1_fixtures import isolated_checkout, make, approve
            from tools.puzzle_production.target_adapter import export
            checkout = project.parent
            isolated_checkout(checkout)
            categories_path = checkout / "content/categories.json"
            categories = json.loads(categories_path.read_text(encoding="utf-8"))
            categories["categories"].append(dict(id="test-only-kat2-extra", name="Zusätzliche Testkategorie mit einer besonders langen deutschen Bezeichnung für die datenbasierte Katalogdarstellung", order=50))
            write_json(categories_path, categories)
            # Regenerate the empty-of-new-content projection before normal registration.
            from tools.puzzle_production.content_registry import projection, registration
            from tools.puzzle_production.contract import write_json as write_canonical
            registry = json.loads((checkout / "content/registry.json").read_text(encoding="utf-8"))
            write_canonical(project / "data/registry.json", projection(registry, categories))
            package = workspace / "kat2-adapter-input"
            make(package, "pz-test-direct-mono", 4, 3, "mono")
            approval = workspace / "kat2-adapter-approval.json"
            approve(package, approval)
            exported = workspace / "kat2-adapter-export"
            python_phase("kat2-adapter-export", lambda: export(package, exported, approval_path=approval,
                name="TEST ONLY Motiv", revision=1, stem="kat2_adapter", save_slot="kat2_adapter",
                category_id="test-only-kat2-extra", categories_path=categories_path))
            python_phase("kat2-adapter-register", lambda: registration(exported, checkout, apply=True))
            install_runtime_fixtures(root, project, append=True)
        else:
            fixture(project, saves, "regular" if mode in ("restart", "information", "kb") else mode)
        env = environment.copy()
        env.update(P1_TEST_SAVE_ROOT=str(saves), KAT2_OUTPUT=str(directory), KAT2_MODE=mode)
        phase("kat2-" + mode + "-import", [engine, "--headless", "--path", str(project), "--import"], phase_env=env)
        command = [engine, "--path", str(project), "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
                   "--script", "res://tests/kat2_probe.gd", "--", "--p1-capture"]
        if host == "Linux":
            command = ["xvfb-run", "-a"] + command
            env["LIBGL_ALWAYS_SOFTWARE"] = "1"
        phase("kat2-" + mode, command, "KAT2_PROBE_OK", phase_env=env)
        report = json.loads((directory / (mode + ".json")).read_text(encoding="utf-8"))
        if report["failures"] or not report["checks"]:
            raise toolchain.PreflightError("KAT2 native assertions failed")
        if mode == "information":
            after_quit = {p.name: toolchain.sha256_file(p) for p in (saves / "error-quit").iterdir() if p.is_file()}
            if not report["quit_slot_hashes"] or after_quit != report["quit_slot_hashes"]:
                raise toolchain.PreflightError("Catalog information quit changed damaged or foreign slot bytes")
            report["regular_quit"] = "success; process exit 0 and all slot bytes unchanged"
            write_json(directory / (mode + ".json"), report)
        reports.append(report)
    # Keep compact native images without repeating the large paper background.
    # Full framebuffer originals remain local; crops preserve exact native pixels.
    from PIL import Image
    crops = []
    for report in reports:
        for capture in report["captures"]:
            path = directory / capture["file"]
            context = path.with_name(path.stem + "-context.png")
            path.rename(context)
            with Image.open(context) as image:
                regions = dict(capture["regions"])
                for name, rectangle in regions.items():
                    target = path.with_name(path.stem + "-" + name + ".png")
                    image.crop(rectangle).save(target, optimize=True)
                    crops.append(dict(file=target.name, source=capture["file"], region=rectangle))
    summary = dict(format="picross-kat2-product-v1", test_only=True, reports=reports,
                   crops=crops, crop="Native control rectangles and one tight layout; no resizing. Full contexts remain local.")
    write_json(directory / "summary.json", summary)
    return summary, sorted(p for p in directory.iterdir() if not p.name.endswith("-context.png"))
