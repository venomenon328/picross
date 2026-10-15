"""Artificial test-only Authoring packages; never human catalog approvals."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil

from PIL import Image

from .contract import Budget, digest, load_json, write_json
from .images import file_hash, import_image
from .repair import search

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/puzzle_production/fixtures/authoring"


def seal(root, handoff):
    write_json(root / "inventory.json", {"format": "picross-authoring-file-inventory-v1", "puzzle_id": handoff["puzzle_id"],
        "revision": handoff["revision"], "files": [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": file_hash(p)}
        for p in sorted(root.rglob("*")) if p.is_file() and p.name not in ("inventory.json", "handoff.json", "approval.json")]})
    handoff["inventory"] = {"file": "inventory.json", "sha256": file_hash(root / "inventory.json")}
    write_json(root / "handoff.json", handoff)


def make(root, identifier, width, height, mode, repaired=False, colors=2):
    root.mkdir(parents=True, exist_ok=True)
    d = deepcopy(load_json(ROOT / "tests/puzzle_production/fixtures/image-design.json"))
    d.update(source_id="test-only", width=width, height=height, mode=mode, crop=[0, 0, width, height],
             variants=[{"id": "area", "method": "area", "threshold": 128}], background="#ffffff",
             palette=[{"id": "ink", "rgb": "#202020"}] if mode == "mono" else
                     [{"id": key, "rgb": rgb} for key,rgb in
                      (("red","#d52b2b"),("blue","#2858b8"),("green","#218121"),("gold","#e5aa21"),("violet","#912191"),
                       ("teal","#218181"),("orange","#c86521"),("brown","#654321"),("pink","#c82165"))[:colors]],
             origin="Artificial ZA-1 test-only source", rights="Repository-owned test pixels only",
             briefing="Artificial fixture, no editorial catalog approval")
    source = Image.new("RGB", (width, height), "white")
    for y in range(height):
        for x in range(width):
            if repaired:
                fill = (x, y) in ((0, 0), (1, 1)) or mode == "color" and (x,y) == (width-1,height-1)
            else:
                fill = width == 1 or height == 1 or (x, y) not in ((0, 0), (width-1, 0))
            if fill:
                rgb = "#202020" if mode == "mono" else d["palette"][1 if repaired and (x,y) == (width-1,height-1) else 0 if repaired else x % colors]["rgb"]
                source.putpixel((x, y), tuple(bytes.fromhex(rgb[1:])))
    (root / "motifs").mkdir(exist_ok=True)
    source.save(root / "motifs/source.png")
    (root / "reveals").mkdir(exist_ok=True)
    # Distinct RGB interior, deliberately non-square and independent from matrix silhouette.
    Image.new("RGB", (width*4, height*4), (76, 145, 93)).save(root / "reveals/reveal.png")
    write_json(root / "design.json", d)
    bundle = root / "production/import"
    import_image(root / "motifs/source.png", root / "design.json", bundle)
    c = load_json(bundle / "area-candidate.json")
    if repaired:
        plan = {"format": "picross-repair-plan-v1", "tool": "rp5-single-cell-1", "reference": {
            "candidate_id": c["id"], "manifest_sha256": file_hash(bundle / "manifest.json"), "variant": "area"},
            "mask": [[False]*width for _ in range(height)], "config": {"max_changes": 1, "max_steps": 96,
            "max_candidates": 16, "search_seconds": 30, "final_seconds": 10, "search_lines": 250000,
            "final_lines": 100000, "seed": 39, "order": "seeded-frontier-v1", "operators": ["single-cell"]},
            "rationale": "Test-only repair replay"}
        write_json(root / "plan.json", plan)
        search(bundle, plan, root / "production/repair")
        raw = load_json(root / "production/repair/repair.json")
        matrix, logic_hash = raw["matrix"], raw["history"][raw["selected"]]["logic_hash"]
        candidate = {"bundle": "production/repair", "variant": f"candidate-{raw['selected']:03d}", "proof": "production/repair/final-proof.json",
                     "source_type": "repair", "repair_id": raw["id"], "parent_variant": "area", "matrix_hash": digest(matrix), "logic_hash": logic_hash}
        repair = {"reference": "production/import", "reference_variant": "area", "plan": "plan.json", "replay": "evidence.txt"}
    else:
        matrix, logic_hash = c["matrix"], c["logic_hash"]
        candidate = {"bundle": "production/import", "variant": "area", "proof": "production/import/area-proof.json",
                     "source_type": "import", "matrix_hash": digest(matrix), "logic_hash": logic_hash}
        repair = None
    h = {"format": "picross-authoring-handoff-v2", "puzzle_id": identifier, "revision": "r01", "test_only": True,
         "repo_commit": "039f59d9a94ad6c2fea32a900d03d1d3b8a7df4c", "state": "content_ready",
         "brief": "evidence.txt", "report": "evidence.txt", "decisions": "evidence.txt", "effort": "evidence.txt",
         "candidate": candidate, "repair": repair, "difficulty": "difficulty.json", "content_blockers": [],
         "final_editorial_approval": None, "gates": {k: "pass" for k in ("reveal_approval", "motif", "provenance", "logic", "frame", "visual", "difficulty", "reveal_consistency")}}
    (root / "evidence.txt").write_text("TEST ONLY. Artificial metadata and approvals, no owner statement.\n", encoding="utf-8", newline="\n")
    h["gates"].update(final_editorial="pending", target_export="blocked")
    h["gate_evidence"] = {k: "evidence.txt" for k in h["gates"]}
    h["approved_parameters"] = [{"width": width, "height": height, "mode": mode, "foreground_colors": len(d["palette"]), "fit": d["fit"], "actual_crop": d["crop"], "method": "area"}]
    h["rulebook"] = {"version": "0.4.0", "file": "evidence.txt", "sha256": file_hash(root / "evidence.txt")}
    reveal_sha = file_hash(root / "reveals/reveal.png")
    for kind, file in (("reveal", "reveals/reveal.png"), ("motif", "motifs/source.png")):
        h[kind] = {"file": file, "sha256": file_hash(root / file), "approval": kind+"-approval.json"}
        a = {"type": "human_"+kind+"_approval", "actor": "TEST-ONLY fixture", "timestamp_utc": "2026-10-12T00:00:00Z",
             "statement": "TEST ONLY, not a human approval", "file": file, "sha256": h[kind]["sha256"], "revision": "test-1", "evidence": "evidence.txt"}
        p = {"puzzle_id": identifier, "file": file, "sha256": h[kind]["sha256"], "author": "Test fixture code",
             "usage_basis": "Repository-owned synthetic test pixels; not a catalog asset"}
        if kind == "motif":
            h[kind]["derived_from_reveal_sha256"] = reveal_sha
            a.update(derived_from_reveal_sha256=reveal_sha, parameters={"width": width, "height": height, "mode": mode, "foreground_colors": len(d["palette"]), "method": "area"})
            p["derived_from"] = {"file": "reveals/reveal.png", "sha256": reveal_sha}
        write_json(root / (kind+"-approval.json"), a)
        write_json((root / file).with_suffix(".provenance.json"), p)
    write_json(root / "difficulty.json", {"method": "picross-difficulty-0.1", "assessment_type": "editorial_estimate", "level": "L1",
        "plausible_range": ["L1", "L2"], "confidence": "low", "logic_hash": logic_hash, "rule_families": {"R0": "Artificial full runs"},
        "time_estimate": None, "playtest": "not_performed"})
    seal(root, h)
    return root


def approve(package, destination):
    h = load_json(package / "handoff.json")
    write_json(destination, {"format": "picross-editorial-approval-v1", "actor": "TEST ONLY", "timestamp_utc": "2026-10-12T00:00:00Z",
        "statement": "Artificial positive fixture, never an owner approval", "puzzle_id": h["puzzle_id"], "revision": h["revision"],
        "handoff_sha256": file_hash(package / "handoff.json"), "inventory_sha256": h["inventory"]["sha256"],
        "selection": {"variant": h["candidate"]["variant"], "matrix_hash": h["candidate"]["matrix_hash"], "logic_hash": h["candidate"]["logic_hash"],
                      "reveal": {k: h["reveal"][k] for k in ("file", "sha256")}}, "test_only": True})


def isolated_checkout(root):
    from .content_registry import projection
    catalog = load_json(ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
    registry = load_json(ROOT / "tests/puzzle_production/fixtures/catalog/registry.json")
    for name, value in (("content/categories.json", catalog), ("content/registry.json", registry),
                        ("game/data/registry.json", projection(registry, catalog))):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        write_json(target, value)
    return root


def replay(output, checkout=None):
    from .target_adapter import export, inspect, open_package, verify_export
    from .content_registry import registration, check_checkout
    output.mkdir(parents=True)
    checkout = isolated_checkout(output / "checkout") if checkout is None else checkout
    reports = []
    for package in sorted(FIXTURES.iterdir()):
        if not package.is_dir():
            continue
        h = load_json(package / "handoff.json")
        with open_package(package) as p:
            blocked = inspect(p)[0]
        assert blocked["technical"] and not blocked["catalog_ready"]
        stem = h["puzzle_id"]
        approval = output / (stem+"-approval.json")
        approve(package, approval)
        dest = output / stem
        export(package, dest, name="TEST ONLY " + stem, revision=1, stem=stem, save_slot="slot_"+stem, approval_path=approval,
               category_id="voegel" if "color" in stem else "gemuese-pilze-kraeuter",
               categories_path=checkout / "content/categories.json")
        registration(dest, checkout, apply=True)
        assert registration(dest, checkout, apply=True)["status"] == "no-op"
        reports.append(verify_export(dest)[1])
    check_checkout(checkout, replay=True)
    write_json(output / "replay.json", {"format": "picross-za1-replay-v1", "accepted": True, "reports": reports})
    return reports


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    replay(parser.parse_args().output_dir)
