"""Small RP-3 adapter: certified square monochrome -> registered F-04 only."""
from __future__ import annotations

import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .contract import Budget, InvalidInput, digest, integer, load_json, write_json
from .images import MAX_BYTES, file_hash, inspect_candidate, normalize, publish_bundle, versions

ADAPTER = "rp3-p1-square-mono-1"
PILOT_ADAPTER = "rp6-p1-square-color-1"


def validate_reveal(path: Path, minimum: int) -> None:
    if path.suffix == ".png":
        image, _, _ = normalize(path)
        if image.width != image.height or image.width < minimum:
            raise InvalidInput("Reveal must be square and independently detailed at >=2 pixels per cell")
        # The PNG extension is intentionally not enabled in P1 in this first profile.
        raise InvalidInput("First registered P1 profile accepts local SVG reveal assets only")
    if path.suffix != ".svg" or path.stat().st_size > MAX_BYTES:
        raise InvalidInput("Reveal requires a local bounded SVG")
    raw = path.read_bytes()
    if b"<!" in raw:
        raise InvalidInput("SVG declarations/entities are unsupported")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise InvalidInput("Damaged SVG reveal") from exc
    allowed = {"svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "defs", "linearGradient", "stop", "title", "desc"}
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] not in allowed:
            raise InvalidInput("Unsupported SVG element")
        for key, value in node.attrib.items():
            if key.rsplit("}", 1)[-1].lower().startswith("on") or "href" in key.lower() or "url(" in value and not re.fullmatch(r"url\(#[a-zA-Z0-9_-]+\)", value):
                raise InvalidInput("External/executable SVG content is unsupported")
    try:
        w, h = float(root.attrib["width"]), float(root.attrib["height"])
    except (KeyError, ValueError) as exc:
        raise InvalidInput("SVG requires explicit numeric square dimensions") from exc
    if root.tag.rsplit("}", 1)[-1] != "svg" or w != h or not minimum <= w <= 8192:
        raise InvalidInput("Reveal must be a square SVG, >=2 pixels per cell and <=8192")


def export_p1(bundle: Path, variant: str, reveal: Path, name: str, output: Path,
              revision: int = 1, seconds: float = 120, max_lines: int = 100_000) -> dict:
    integer(revision, 1, 1_000_000, "revision")
    if not isinstance(name, str) or not 1 <= len(name) <= 128:
        raise InvalidInput("Reveal name requires 1..128 characters")
    c, proof, checked = inspect_candidate(bundle, variant, Budget(seconds, max_lines))
    d = c["design"]
    if d["mode"] != "mono" or d["width"] != d["height"]:
        raise InvalidInput("First P1 profile supports square monochrome candidates only")
    if not checked["certified"] or checked["status"] != "solved":
        raise InvalidInput("P1 export requires a complete independently verified deduction proof")
    if not any(v != "empty" for row in c["matrix"] for v in row):
        raise InvalidInput("Empty raster has no first P1 motif")
    validate_reveal(reveal, 2 * d["width"])
    if output.exists():
        raise InvalidInput("P1 output already exists; use a new directory")
    from .images import logic_from_matrix
    logic = logic_from_matrix(c["matrix"], d)
    mapping = {"empty": 0, **{color: i + 1 for i, color in enumerate(logic["colors"])}}
    adapt = lambda lines: [[{"length": h["length"], "color": mapping[h["color"]]} for h in line] for line in lines]
    definition = {"schema": 2, "id": "F-04", "revision": revision,
                  "width": d["width"], "height": d["height"],
                  "palette": [{"id": mapping[e["id"]], "color": e["rgb"].lstrip("#").lower(), "symbol": "A"} for e in d["palette"]],
                  "solution": [[mapping[v] for v in row] for row in c["matrix"]],
                  "rows": adapt(logic["row_clues"]), "columns": adapt(logic["column_clues"]),
                  "reveal": {"version": 1, "definition_id": "F-04", "name": name, "image": "res://art/f04.svg"}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rp3-export-", dir=output.parent) as temp:
        stage = Path(temp) / "export"
        (stage / "data").mkdir(parents=True)
        (stage / "art").mkdir()
        write_json(stage / "data/f04.json", definition)
        shutil.copyfile(reveal, stage / "art/f04.svg")
        write_json(stage / "proof.json", proof)
        write_json(stage / "logic.json", logic)
        manifest = {"format": "picross-p1-export-v1", "adapter": ADAPTER, "versions": versions(),
                    "definition_id": "F-04", "revision": revision, "candidate_id": c["id"],
                    "source_id": c["source_id"], "normalized_sha256": c["normalized_sha256"],
                    "production_manifest_sha256": file_hash(bundle / "manifest.json"),
                    "logic_hash": c["logic_hash"], "color_mapping": mapping, "technical": checked,
                    "motif_review": "open; compare source/raster/reveal", "owner_solution": "RP-6 gate, not performed",
                    "files": {p.relative_to(stage).as_posix(): file_hash(p) for p in sorted(stage.rglob("*")) if p.is_file()}}
        write_json(stage / "manifest.json", manifest)
        publish_bundle(stage, output)
    return {"status": "exported", "definition_id": "F-04", "candidate_id": c["id"], "certified": True}


def validate_pilot_reveal(path: Path, minimum: int) -> None:
    """Bounded SVG or normalized, square PNG; no implicit stretch or conversion."""
    if path.suffix == ".svg":
        validate_reveal(path, minimum)
        return
    if path.suffix != ".png":
        raise InvalidInput("Pilot reveal requires SVG or PNG")
    image, metadata, _ = normalize(path)
    if (metadata["format"] != "PNG" or image.width != image.height or
            image.width < minimum or metadata["orientation"] != 1):
        raise InvalidInput("Pilot PNG must be square, oriented and >=2 pixels per cell")


def export_pilot(bundle: Path, variant: str, reveal: Path, name: str, output: Path,
                 definition_id: str, *, reference: Path | None = None,
                 revision: int = 1, seconds: float = 120, max_lines: int = 100_000) -> dict:
    """Additive pilot profile; a repair always traverses the complete RP-5 replay."""
    from .images import logic_from_matrix
    integer(revision, 1, 1_000_000, "revision")
    if definition_id not in {"F-05", "F-06", "F-07", "F-08", "F-09"}:
        raise InvalidInput("Unregistered pilot definition ID")
    if not isinstance(name, str) or not 1 <= len(name) <= 128:
        raise InvalidInput("Reveal name requires 1..128 characters")
    if reference is None:
        c, proof, checked = inspect_candidate(bundle, variant, Budget(seconds, max_lines))
        design, matrix = c["design"], c["matrix"]
        source = {"kind": "import", "candidate_id": c["id"],
                  "manifest_sha256": file_hash(bundle / "manifest.json")}
        certified = checked["certified"] and checked["status"] == "solved"
    else:
        from .repair import inspect_repair
        checked = inspect_repair(bundle, reference, Budget(60, 1_000_000))
        raw = load_json(bundle / "repair.json")
        if variant != raw["reference"]["variant"]:
            raise InvalidInput("Repair variant differs from original reference")
        design = load_json(reference / "design.json")
        matrix = raw["matrix"]
        certified = checked["certified"] and checked["status"] == "found"
        if not certified:
            raise InvalidInput("Pilot repair requires found and complete final certification")
        from .contract import validate_logic
        puzzle = validate_logic(logic_from_matrix(matrix, design))
        proof = load_json(bundle / "final-proof.json", puzzle.proof_byte_limit)
        source = {"kind": "repair", "repair_id": raw["id"], "reference": raw["reference"],
                  "repair_sha256": file_hash(bundle / "repair.json"),
                  "manifest_sha256": file_hash(bundle / "manifest.json")}
    if not certified:
        raise InvalidInput("Pilot export requires complete independent certification")
    if (design["width"] != design["height"] or len(design["palette"]) > 4 or
            not any(v != "empty" for row in matrix for v in row)):
        raise InvalidInput("Pilot supports nonempty square rasters with 1..4 foreground colors")
    if proof["final_domains"] != [[[v] for v in row] for row in matrix]:
        raise InvalidInput("Final proof differs from pilot matrix")
    validate_pilot_reveal(reveal, 2 * design["width"])
    if output.exists():
        raise InvalidInput("Pilot output already exists; use a new directory")
    logic = logic_from_matrix(matrix, design)
    mapping = {"empty": 0, **{color: i+1 for i, color in enumerate(logic["colors"])}}
    adapt = lambda lines: [[{"length": h["length"], "color": mapping[h["color"]]} for h in line] for line in lines]
    stem = definition_id.lower().replace("-", "")
    asset = f"art/{stem}{reveal.suffix}"
    definition = {"schema": 2, "id": definition_id, "revision": revision,
                  "width": design["width"], "height": design["height"],
                  "palette": [{"id": mapping[e["id"]], "color": e["rgb"].lstrip("#").lower(),
                               "symbol": chr(64 + mapping[e["id"]])} for e in design["palette"]],
                  "solution": [[mapping[v] for v in row] for row in matrix],
                  "rows": adapt(logic["row_clues"]), "columns": adapt(logic["column_clues"]),
                  "reveal": {"version": 1, "definition_id": definition_id, "name": name, "image": "res://" + asset}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rp6-export-", dir=output.parent) as temp:
        stage = Path(temp) / "export"
        (stage / "data").mkdir(parents=True)
        (stage / "art").mkdir()
        write_json(stage / f"data/{stem}.json", definition)
        shutil.copyfile(reveal, stage / asset)
        write_json(stage / "proof.json", proof)
        write_json(stage / "logic.json", logic)
        manifest = {"format": "picross-p1-export-v2", "adapter": PILOT_ADAPTER,
                    "definition_id": definition_id, "revision": revision, "source": source,
                    "matrix_hash": digest(matrix), "logic_hash": digest(logic), "color_mapping": mapping,
                    "certified": True, "editorial_release": False,
                    "files": {p.relative_to(stage).as_posix(): file_hash(p) for p in sorted(stage.rglob("*")) if p.is_file()}}
        write_json(stage / "manifest.json", manifest)
        publish_bundle(stage, output)
    return manifest
