"""Temporary HP-I2 actual synthetic integration; outside the product branch.

Run with the repository's pinned Pillow 12.3.0 environment. This constructs new
TEST ONLY originals, derives and verifies real HP-W2 outputs, then uses the real
export/registration and independent image-adoption paths. No approval success
stub, source-v3 fabrication, production corpus or in-place original rewrite.
The caller owns the returned isolated directory until cleanup_fixture is called.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch


OWNER_FILE = "hp-i2-fixture-owner.json"
OWNER_FORMAT = "picross-hp-i2-temporary-integration-v1"
IDS = {"a": "pz-hp-i2-a", "b": "pz-hp-i2-b", "none": "pz-hp-i2-none",
       "legacy": "pz-hp-i2-legacy"}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _file(path: Path) -> dict:
    raw = path.read_bytes()
    return {"file": str(path), "bytes": len(raw), "sha256": _sha(raw)}


def _tree(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): _sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8")


def _progress(message: str) -> None:
    print("HP-I2 fixture: " + message, file=sys.stderr, flush=True)


def build_fixture(source_root: Path, output_root: Path) -> dict:
    """Create a new owned output root; never overwrite or delete existing work.

    Returns JSON-serializable paths, actual binding report and separate image-only
    adoption proof. `checkout` is a minimal real content checkout/game overlay;
    combine its game directory with an isolated product game copy for rendering.
    Every registration uses wasserwelt and identical 20x20 mono logical geometry.
    """
    source_root, output_root = Path(source_root).resolve(), Path(output_root).resolve()
    if (output_root == source_root or output_root.is_relative_to(source_root)
            or source_root.is_relative_to(output_root)):
        raise ValueError("Fixture output must be outside the product repository")
    if output_root.exists():
        raise ValueError("Fixture output already exists; use a new path")
    sys.path.insert(0, str(source_root))
    sys.path.insert(1, str(source_root / "tests/puzzle_production"))
    import PIL
    from PIL import Image
    from tools import background_import, product_background_fixtures as drawings
    from tools.puzzle_production import background_assets as assets
    from tools.puzzle_production import catalog_background as bg
    from tools.puzzle_production import catalog_background_change as change
    from tools.puzzle_production import content_registry as registry, target_adapter as adapter
    from tools.puzzle_production.contract import load_json, write_json
    from tools.puzzle_production.za1_fixtures import ROOT, approve, isolated_checkout, make, rated_registration
    from tests.puzzle_production import test_background_content as content_fixtures
    from tests.puzzle_production.background_change_fixtures import create_work

    if PIL.__version__ != "12.3.0":
        raise RuntimeError("HP-W2 needs pinned Pillow 12.3.0, got " + PIL.__version__)
    if ROOT.resolve() != source_root:
        raise RuntimeError("Imported fixture code does not belong to the requested source root")
    output_root.mkdir(parents=True)
    _write(output_root / OWNER_FILE, {"format": OWNER_FORMAT, "output_root": str(output_root),
                                    "source_root": str(source_root), "test_only": True})
    source_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip()
    case = content_fixtures.BackgroundContentTests()
    case.root, case.counter = output_root / "work", 0
    case.root.mkdir()
    checkout = isolated_checkout(output_root / "checkout")
    capability = {"format": bg.CAPABILITY_FORMAT, "runtime_format": bg.RUNTIME_FORMAT,
                  "profile_id": "picross-background-png2304-v1", "enabled": True}
    write_json(checkout / bg.CAPABILITY, capability)
    assert "wasserwelt" in {c["id"] for c in load_json(checkout / "content/categories.json")["categories"]}
    records, protected = [], {}
    original_fixture = content_fixtures.BackgroundFixture

    # These constructors make fresh synthetic inputs before their final archive.
    # Once archived, original package, approval and export bytes are immutable.
    for kind in ("legacy", "a", "b", "none"):
        identifier = IDS[kind]
        _progress("constructing " + identifier)
        source = make(case.root / (kind + "-package"), identifier, 20, 20, "mono")
        if kind != "legacy":
            def selected_fixture(root, description, **kwargs):
                image = (Image.frombytes("RGBA", drawings.SIZE, drawings.pixels(kind))
                         if kind in ("a", "b") else None)
                return original_fixture(root, description, image=image, **kwargs)
            with patch.object(content_fixtures, "BackgroundFixture", selected_fixture):
                case.background(source, choice="none" if kind == "none" else "selected",
                                ready=True, state="content_ready")
        archive = case.archive(source, kind + "-original.zip")
        approval = case.root / (kind + "-approval.json")
        if kind == "legacy":
            approve(source, approval)
        else:
            approval = case.approval(source, archive, name=kind + "-approval.json")
        original = {"package": _tree(source), "archive": _sha(archive.read_bytes()),
                    "approval": _sha(approval.read_bytes())}
        exported = output_root / (kind + "-export")
        _progress("exporting and registering " + identifier)
        manifest = adapter.export(archive, exported, name="TEST ONLY HP-I2 " + kind.upper(), revision=1,
                                  stem="hp_i2_" + kind, save_slot="hp_i2_" + kind,
                                  approval_path=approval, category_id="wasserwelt",
                                  categories_path=checkout / "content/categories.json",
                                  allow_background=kind != "legacy")
        assert manifest["test_only"] is True
        checked, inspection = adapter.verify_export(exported)
        assert checked == manifest and inspection["technical"] and inspection["editorial_approved"]
        export_before = _tree(exported)
        registration = rated_registration(exported, checkout, apply=True)
        assert registration["status"] == "registered", registration
        assert original == {"package": _tree(source), "archive": _sha(archive.read_bytes()),
                            "approval": _sha(approval.read_bytes())}
        assert export_before == _tree(exported)
        if kind != "legacy":
            assert (exported / "input/package.zip").read_bytes() == archive.read_bytes()
        protected[kind] = {"source": source, "archive": archive, "approval": approval,
                           "export": exported, "original": original, "export_hashes": export_before}
        records.append({"kind": kind, "id": identifier, "test_only": True,
                        "original": _file(archive), "approval": _file(approval),
                        "handoff": _file(source / "handoff.json"),
                        "inventory": _file(source / "inventory.json"),
                        "export": str(exported), "export_manifest": _file(exported / "manifest.json"),
                        "export_format": manifest["format"], "registration": registration,
                        "original_bytes_unchanged": True})

    _progress("checking full synthetic checkout and runtime/source inventory")
    registry.check_checkout(checkout, replay=True)
    inventory = background_import.source_inventory(checkout)
    runtime_path = checkout / "game/data/registry.json"
    runtime = load_json(runtime_path)
    assert runtime["format"] == "picross-runtime-registry-v6"
    runtime_entries = {e["id"]: e for e in runtime["entries"]}
    assert set(runtime_entries) == set(IDS.values())
    logic_signatures, decoded = [], []
    for record in records:
        entry = runtime_entries[record["id"]]
        definition_path = checkout / "game" / entry["definition"]
        definition = load_json(definition_path)
        assert (definition["width"], definition["height"]) == (20, 20)
        logic = {k: definition[k] for k in ("width", "height", "palette", "solution", "rows", "columns")}
        logic_signatures.append(_sha(json.dumps(logic, sort_keys=True).encode()))
        expected = "selected" if record["kind"] in ("a", "b") else record["kind"]
        assert entry["background"]["status"] == expected
        assert entry["category_id"] == "wasserwelt"
        record.update(runtime_entry=entry, definition=_file(definition_path),
                      runtime_revision=definition["revision"], reveal=_file(checkout / "game" / entry["reveal"]))
        if expected == "selected":
            path = checkout / "game" / entry["background"]["asset"]["file"]
            with Image.open(path) as image:
                image.load()
                assert image.mode == "RGBA" and image.size == drawings.SIZE
                rgba = image.tobytes()
                alpha = image.getchannel("A").histogram()
            decoded.append({"id": record["id"], "variant": record["kind"], "path": str(path),
                            "image_revision": entry["background"]["image_revision"],
                            "source": _file(path), "size": list(drawings.SIZE),
                            "rgba_bytes": len(rgba), "rgba_sha256": _sha(rgba),
                            "transparent_pixels": alpha[0], "partial_pixels": sum(alpha[1:255]),
                            "opaque_pixels": alpha[255]})
    assert len(set(logic_signatures)) == 1
    assert decoded[0]["rgba_sha256"] != decoded[1]["rgba_sha256"]
    expected_path = output_root / "background-inventory.json"
    _write(expected_path, inventory)

    # Real independent image-only adoption in a separate clone. The baseline
    # remains the common A1/B1/none/legacy fixture for native and PCK observations.
    _progress("proving separate authorized image-only store/plan/adopt")
    baseline_hashes = _tree(checkout)
    changed = output_root / "image-change-checkout"
    shutil.copytree(checkout, changed)
    subprocess.run(["git", "init", "--quiet", "-b", "main", str(changed)], check=True)
    before_registry = load_json(changed / registry.REGISTRY)
    before_entry = next(e for e in before_registry["entries"] if e["id"] == IDS["a"])
    before_runtime = deepcopy(runtime_entries[IDS["a"]])
    before_source = load_json(changed / bg.path(IDS["a"]))
    preserved = {"definition": _file(changed / "game" / before_entry["definition"]),
                 "reveal": _file(changed / "game" / before_entry["reveal"])}
    work = create_work(case, changed, output_root / "change-work", "bg-hp-i2-r02", "selected",
                       image=Image.frombytes("RGBA", drawings.SIZE, drawings.pixels("b")), install=False)
    assert work.request["puzzle_id"] == IDS["a"]
    request_hash = _sha((work.source_root / "record.json").read_bytes())
    stored = change.store(changed, work.source_root / "record.json", work.source_root)
    assert stored["status"] == "stored", stored
    plan_path = output_root / "image-change-plan"
    planned = change.plan(changed, work.record_path, plan_path)
    assert planned["status"] == "planned", planned
    adopted = change.adopt(changed, plan_path)
    assert adopted["status"] == "adopted", adopted
    registry.check_checkout(changed, replay=True)
    after_registry = load_json(changed / registry.REGISTRY)
    after_entry = next(e for e in after_registry["entries"] if e["id"] == IDS["a"])
    after_runtime = next(e for e in load_json(changed / "game/data/registry.json")["entries"] if e["id"] == IDS["a"])
    after_source = load_json(changed / bg.path(IDS["a"]))
    assert before_entry == after_entry
    assert {k: v for k, v in before_runtime.items() if k != "background"} == {
        k: v for k, v in after_runtime.items() if k != "background"}
    assert bg.initial(after_source) == before_source
    assert after_runtime["background"]["image_revision"] == before_runtime["background"]["image_revision"] + 1
    assert after_runtime["background"]["asset"]["sha256"] != before_runtime["background"]["asset"]["sha256"]
    for key in preserved:
        assert _file(Path(preserved[key]["file"])) == preserved[key]
    assert _sha((work.source_root / "record.json").read_bytes()) == request_hash
    assert _tree(checkout) == baseline_hashes
    for item in protected.values():
        assert item["original"] == {"package": _tree(item["source"]),
            "archive": _sha(item["archive"].read_bytes()), "approval": _sha(item["approval"].read_bytes())}
        assert item["export_hashes"] == _tree(item["export"])

    image_change = {"checkout": str(changed), "id": IDS["a"], "test_only": True,
                    "source_format_before": before_source["format"], "source_format_after": after_source["format"],
                    "request": _file(work.source_root / "record.json"),
                    "plan": _file(plan_path / "plan.json"), "store": stored, "plan_result": planned, "adopt": adopted,
                    "registry_entry_unchanged": True, "runtime_except_background_unchanged": True,
                    "original_source_preserved": True, "baseline_unchanged": True,
                    "definition": preserved["definition"], "reveal": preserved["reveal"],
                    "save_slot_before": before_runtime["save_slot"], "save_slot_after": after_runtime["save_slot"],
                    "runtime_revision_before": load_json(Path(preserved["definition"]["file"]))["revision"],
                    "runtime_revision_after": load_json(changed / "game" / after_entry["definition"])["revision"],
                    "background_before": before_runtime["background"], "background_after": after_runtime["background"],
                    "updated_runtime_entry": after_runtime,
                    "updated_asset_path": str(changed / "game" / after_runtime["background"]["asset"]["file"])}
    _write(output_root / "image-change-proof.json", image_change)
    result = {"format": OWNER_FORMAT, "test_only": True, "created_utc": datetime.now(timezone.utc).isoformat(),
              "source_root": str(source_root), "source_head": source_head,
              "pillow_version": PIL.__version__, "hp_w2_tool": assets.describe(),
              "fixture_builder": _file(Path(__file__).resolve()),
              "generator": _file(source_root / "tools/product_background_fixtures.py"),
              "output_root": str(output_root), "checkout": str(checkout), "game_overlay": str(checkout / "game"),
              "runtime_path": str(runtime_path), "runtime": _file(runtime_path),
              "ids": IDS, "category_id": "wasserwelt", "size": [20, 20], "mode": "mono",
              "shared_logic_sha256": logic_signatures[0], "registrations": records,
              "background_inventory": inventory, "background_inventory_path": str(expected_path),
              "normalized_images": decoded, "image_change": image_change,
              "all_originals_unchanged": True,
              "scope": "Actual synthetic integration and image-only adoption; no owner or player acceptance.",
              "cleanup": {"owner_file": str(output_root / OWNER_FILE), "method": "cleanup_fixture(output_root)",
                          "remaining": str(output_root)}}
    report_path = output_root / "fixture-report.json"
    result["report_path"] = str(report_path)
    _write(report_path, result)
    _progress("complete: " + str(report_path))
    return result


def cleanup_fixture(output_root: Path) -> dict:
    """Remove only this helper's explicitly owned isolated output after review."""
    output_root = Path(output_root).resolve()
    marker = output_root / OWNER_FILE
    owner = json.loads(marker.read_text(encoding="utf-8"))
    if owner != {"format": OWNER_FORMAT, "output_root": str(output_root),
                 "source_root": owner.get("source_root"), "test_only": True}:
        raise ValueError("Fixture cleanup owner marker differs")
    source_root = Path(owner["source_root"]).resolve()
    if (output_root == source_root or output_root.is_relative_to(source_root)
            or source_root.is_relative_to(output_root) or output_root.is_symlink()):
        raise ValueError("Refusing fixture cleanup outside its isolated ownership")
    shutil.rmtree(output_root)
    return {"removed": str(output_root), "remaining": None}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    built = build_fixture(args.source_root, args.output_root)
    print(json.dumps({k: built[k] for k in ("checkout", "runtime_path", "ids", "report_path",
                                          "background_inventory_path")}, sort_keys=True))
