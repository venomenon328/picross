"""ZA-1: inspect, export and recheck Authoring-v2 inputs for the regular game."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
import re

from .authoring_package import (ID, STEM, Package, open_package, require, sha,
                                string, timestamp, relative)
from .contract import (Aborted, Budget, InvalidInput, InvalidProof, digest,
                       exact_keys, integer, load_json, validate_logic, write_json)
from .images import (MAX_BYTES, file_hash, inspect_candidate, logic_from_matrix,
                     normalize, publish_bundle, versions)

ADAPTER = "authoring-p1-rect-color-1"
FORMAT = "picross-target-export-v1"


def tool_identity():
    root = Path(__file__).resolve().parents[2]
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                         timeout=10, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        commit = None
    files = ["authoring_package.py", "target_adapter.py", "content_registry.py",
             "images.py", "repair.py", "contract.py", "verifier.py"]
    return {"adapter": ADAPTER, "commit": commit, "versions": versions(),
            "modules": {n: file_hash(Path(__file__).with_name(n)) for n in files}}


def validate_reveal(path, width, height):
    """Additive rectangle profile; old v1/v2 validators retain their semantics."""
    require(path.stat().st_size <= MAX_BYTES, "Reveal exceeds image byte limit")
    if path.suffix == ".png":
        image, meta, _ = normalize(path)
        require(meta["format"] == "PNG" and meta["orientation"] == 1,
                "Reveal requires an oriented PNG; no implicit conversion")
        w, h = image.size
    else:
        require(path.suffix == ".svg", "Reveal requires PNG or bounded local SVG")
        raw = path.read_bytes()
        require(b"<!" not in raw, "SVG declarations/entities unsupported")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise InvalidInput("Damaged SVG") from exc
        allowed = {"svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
                   "defs", "linearGradient", "stop", "title", "desc"}
        require(len(list(root.iter())) <= 10000, "SVG element limit")
        for node in root.iter():
            require(node.tag.rsplit("}", 1)[-1] in allowed, "Unsupported SVG element")
            for key, value in node.attrib.items():
                require(not key.rsplit("}", 1)[-1].lower().startswith("on") and "href" not in key.lower() and
                        not any(v in value.lower() for v in ("@import", "javascript:", "http:", "https:", "file:", "data:")) and
                        (not re.search(r"url\s*\(", value, re.I) or re.fullmatch(r"url\(#[a-zA-Z0-9_-]+\)", value)),
                        "External/executable SVG content unsupported")
        try:
            w, h = float(root.attrib["width"]), float(root.attrib["height"])
        except (KeyError, ValueError) as exc:
            raise InvalidInput("SVG requires explicit numeric dimensions") from exc
        require(root.tag.rsplit("}", 1)[-1] == "svg", "Not an SVG root")
    require(math.isfinite(w) and math.isfinite(h) and 2 * width <= w <= 8192 and
            2 * height <= h <= 8192 and w * h <= 8_000_000,
            "Reveal requires >=2 pixels per cell/axis within image limits")
    return {"width": w, "height": h, "sha256": file_hash(path)}


def final_approval(package, selection, approval_path=None):
    h = package.handoff
    if approval_path is None:
        ref = h.get("final_editorial_approval")
        if ref is None:
            return None
        approval_path = package.file(ref)
    a = exact_keys(load_json(approval_path), {"format", "actor", "timestamp_utc", "statement", "puzzle_id",
                 "revision", "handoff_sha256", "inventory_sha256", "selection", "test_only"})
    require(a["format"] == "picross-editorial-approval-v1", "Unsupported final editorial approval")
    for key in ("actor", "statement"):
        string(a[key], "final approval " + key)
    timestamp(a["timestamp_utc"])
    require(a["puzzle_id"] == h["puzzle_id"] and a["revision"] == h["revision"] and
            a["handoff_sha256"] == file_hash(package.file("handoff.json")) and
            a["inventory_sha256"] == h["inventory"]["sha256"] and a["selection"] == selection,
            "Final editorial approval does not bind this handoff/selection")
    require(type(a["test_only"]) is bool and a["test_only"] == h.get("test_only", False),
            "Test-only approval scope mismatch")
    return {"record": a, "sha256": file_hash(approval_path), "path": approval_path}


def inspect(package: Package, approval_path=None):
    h = package.handoff
    for name in ("brief", "report", "decisions", "effort"):
        package.file(h.get(name))
    require(type(h.get("test_only", False)) is bool, "Invalid test-only marker")
    gates = h.get("gates")
    required = ("reveal_approval", "motif", "provenance", "logic", "frame", "visual", "difficulty", "reveal_consistency")
    require(isinstance(gates, dict) and all(v in ("pending", "pass", "fail", "blocked") for v in gates.values()),
            "Invalid gate statuses")
    evidence = h.get("gate_evidence")
    require(isinstance(evidence, dict), "Gate evidence missing")
    for gate in required:
        require(gates.get(gate) == "pass", "Unresolved content gate: " + gate)
        package.file(evidence.get(gate))
    require(h.get("content_blockers", []) == [], "Unresolved content blockers")
    for kind in ("reveal", "motif"):
        record = h.get(kind)
        package.bound(record)
        package.approval(record, kind)
        package.provenance(record, kind)
    require(h["motif"].get("derived_from_reveal_sha256") == h["reveal"]["sha256"], "Wrong motif/reveal derivation")
    c = h.get("candidate")
    require(isinstance(c, dict), "Missing selected candidate")
    bundle = package.bundle(c.get("bundle"))
    kind = c.get("source_type")
    budget = Budget(min(120, max(0, package.deadline - time.monotonic())), 1_000_000)
    if kind == "import":
        require(h.get("repair") is None, "Ambiguous import/repair origin")
        candidate, proof, checked = inspect_candidate(bundle, c.get("variant"), budget)
        design, matrix = candidate["design"], candidate["matrix"]
        expected_proof = c["bundle"] + "/" + c["variant"] + "-proof.json"
        result = load_json(bundle / (c["variant"] + "-result.json"))
        require(result.get("status") == "solved" and result.get("certified") is True and
                result.get("proof_verified") is True, "Original import did not complete certification")
        require(checked["status"] == "solved" and checked["certified"], "Import is not certified solved")
        source = {"kind": kind, "candidate_id": candidate["id"], "variant": c["variant"]}
        reference = bundle
    elif kind == "repair":
        from .repair import inspect_repair
        r = h.get("repair")
        require(isinstance(r, dict), "Missing repair reference")
        reference = package.bundle(r.get("reference"))
        # RP-5 has its own bounded replay contract, including ALL parents/proofs.
        budget.deadline = min(budget.deadline, time.monotonic() + 60)
        checked = inspect_repair(bundle, reference, budget)
        raw = load_json(bundle / "repair.json")
        require(checked["status"] == "found" and checked["certified"], "Repair originally unfinished/uncertified")
        require(c.get("repair_id") == raw["id"] and c.get("variant") == f"candidate-{raw['selected']:03d}" and
                c.get("parent_variant") == raw["reference"]["variant"] == r.get("reference_variant"),
                "Selected repair candidate differs from import reference/selection")
        require(digest(package.json(r.get("plan"))) == digest(load_json(bundle / "plan.json")), "Repair plan binding differs")
        design, matrix = load_json(reference / "design.json"), raw["matrix"]
        proof = load_json(bundle / "final-proof.json", validate_logic(logic_from_matrix(matrix, design)).proof_byte_limit)
        expected_proof = c["bundle"] + "/final-proof.json"
        source = {"kind": kind, "repair_id": raw["id"], "variant": c["variant"], "reference": raw["reference"]}
    else:
        raise InvalidInput("Unsupported/ambiguous candidate source_type")
    require(c.get("proof") == expected_proof, "Handoff proof selection differs")
    logic = logic_from_matrix(matrix, design)
    require(c.get("matrix_hash") == digest(matrix) and c.get("logic_hash") == digest(logic), "Selected matrix/logic binding differs")
    require(proof["final_domains"] == [[[v] for v in row] for row in matrix], "Proof enddomains differ")
    manifest = load_json(reference / "manifest.json")
    require(file_hash(reference / manifest["original"]) == h["motif"]["sha256"], "Import source is not the approved motif")
    params = h.get("approved_parameters")
    require(isinstance(params, list) and params, "Missing explicit approved parameters")
    for p in params:
        require(isinstance(p,dict), "Invalid approved parameters")
        for key in ("width","height","foreground_colors"):
            integer(p.get(key),1,4096,"approved "+key)
        require(isinstance(p.get("method"),str) and isinstance(p.get("fit"),str) and
                isinstance(p.get("actual_crop"),list) and len(p["actual_crop"]) == 4 and
                all(type(v) is int for v in p["actual_crop"]), "Invalid approved method/fit/crop")
    variant = source["reference"]["variant"] if kind == "repair" else c["variant"]
    v = next(v for v in design["variants"] if v["id"] == variant)
    require(any(isinstance(p, dict) and p.get("width") == design["width"] and p.get("height") == design["height"] and
                p.get("mode") == design["mode"] and p.get("foreground_colors") == len(design["palette"]) and
                p.get("method") == v["method"] and p.get("fit") == design["fit"] and
                p.get("actual_crop") == design["crop"] for p in params), "Selected design lies outside approved parameter binding")
    motif_approval = package.json(h["motif"]["approval"])
    corridor = motif_approval.get("parameters")
    require(isinstance(corridor,dict), "Missing motif parameter corridor")
    for key in ("width","height","foreground_colors"):
        integer(corridor.get(key),1,4096,"motif approval "+key)
    require(isinstance(corridor, dict) and all(corridor.get(k) == design[k] for k in ("width", "height", "mode")) and
            corridor.get("foreground_colors") == len(design["palette"]) and corridor.get("method") == v["method"],
            "Motif approval parameter corridor differs")
    require(1 <= design["width"] <= 50 and 1 <= design["height"] <= 50 and 1 <= len(design["palette"]) <= 4,
            "Target profile requires 1..50 per axis and 1..4 foreground colors; no conversion")
    left = any(row[0] != "empty" for row in matrix)
    right = any(row[-1] != "empty" for row in matrix)
    top, bottom = (any(v != "empty" for v in row) for row in (matrix[0], matrix[-1]))
    require((left or right) and (top or bottom), "Authoring frame rule failed: (left OR right) AND (top OR bottom)")
    reveal = validate_reveal(package.file(h["reveal"]["file"]), design["width"], design["height"])
    difficulty = package.json(h.get("difficulty"))
    require(isinstance(difficulty, dict) and difficulty.get("method") == "picross-difficulty-0.1" and
            difficulty.get("assessment_type") in ("editorial_estimate", "instrumented") and
            difficulty.get("level") in ("L1", "L2", "L3", "L4", "L5") and
            difficulty.get("confidence") in ("low", "medium", "high") and difficulty.get("logic_hash") == digest(logic),
            "Invalid difficulty binding")
    levels = difficulty.get("plausible_range")
    require(isinstance(levels, list) and len(levels) == 2 and all(v in ("L1", "L2", "L3", "L4", "L5") for v in levels) and
            levels[0] <= difficulty["level"] <= levels[1] and isinstance(difficulty.get("rule_families"), dict) and
            difficulty["rule_families"], "Missing difficulty uncertainty/reasoning")
    require(all(k in ("R0","R1","R2","R3") and isinstance(v,str) and bool(v.strip())
                for k,v in difficulty["rule_families"].items()), "Invalid difficulty rule reasoning")
    if difficulty.get("evidence") is not None:
        package.file(difficulty["evidence"])
    selection = {"variant": c["variant"], "matrix_hash": digest(matrix), "logic_hash": digest(logic),
                 "reveal": {"file": h["reveal"]["file"], "sha256": h["reveal"]["sha256"]}}
    approval = final_approval(package, selection, approval_path)
    report = {"format": "picross-target-inspection-v1", "adapter": ADAPTER, "technical": True,
              "editorial_approved": approval is not None, "catalog_ready": approval is not None, "registered": False,
              "blockers": [] if approval else ["final_editorial: missing bound human final approval"],
              "puzzle_id": h["puzzle_id"], "package_revision": h["revision"], "selection": selection,
              "handoff_sha256": file_hash(package.file("handoff.json")), "inventory_sha256": h["inventory"]["sha256"],
              "original_zip_sha256": (package.derivation or {}).get("original_zip_sha256") if package.derivation else package.archive_sha256,
              "source": source, "width": design["width"], "height": design["height"], "mode": design["mode"],
              "difficulty": difficulty, "frame": {"left": left, "right": right, "top": top, "bottom": bottom},
              "fresh_verification": checked, "reveal": reveal, "tool": tool_identity(),
              "checked_at_utc": datetime.now(timezone.utc).isoformat(), "test_only": h.get("test_only", False)}
    return report, design, matrix, logic, approval


def definition(report, design, matrix, logic, name, revision, stem):
    integer(revision, 1, 1_000_000, "explicit runtime revision")
    string(name, "explicit motif name", 128)
    require(isinstance(stem, str) and Path(stem).name == stem and STEM.fullmatch(Path(stem).stem) and
            Path(stem).suffix in (".png", ".svg"), "Invalid explicit file stem")
    mapping = {"empty": 0, **{color: i+1 for i, color in enumerate(logic["colors"])}}
    adapt = lambda lines: [[{"length": c["length"], "color": mapping[c["color"]]} for c in line] for line in lines]
    return {"schema": 2, "id": report["puzzle_id"], "revision": revision, "width": design["width"], "height": design["height"],
            "palette": [{"id": mapping[e["id"]], "color": e["rgb"][1:].lower(), "symbol": chr(64+mapping[e["id"]])}
                        for e in sorted(design["palette"], key=lambda e: mapping[e["id"]])],
            "solution": [[mapping[v] for v in row] for row in matrix], "rows": adapt(logic["row_clues"]), "columns": adapt(logic["column_clues"]),
            "reveal": {"version": 1, "definition_id": report["puzzle_id"], "name": name, "image": "res://art/content/"+stem}}, mapping


def player_notice(package):
    p = package.provenance(package.handoff["reveal"], "reveal")
    return "\n".join(("Production ID: " + package.handoff["puzzle_id"], "Artwork: " + p["author"],
                      "Usage basis: " + p["usage_basis"], ""))


def export(source, output, *, name, revision, stem, save_slot, approval_path=None):
    require(not output.exists(), "Export output exists; use a new path")
    require(isinstance(save_slot, str) and STEM.fullmatch(save_slot), "Invalid explicit save slot")
    relative(save_slot+".json")
    with open_package(source) as package:
        report, design, matrix, logic, approval = inspect(package, approval_path)
        require(approval is not None, "Export blocked: final_editorial approval missing")
        reveal_source = package.file(package.handoff["reveal"]["file"])
        require(isinstance(stem, str) and STEM.fullmatch(stem), "Invalid explicit file stem")
        relative(stem+".json")
        filename = stem + reveal_source.suffix
        data, mapping = definition(report, design, matrix, logic, name, revision, filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="za1-export-", dir=output.parent) as temp:
            stage = Path(temp) / "export"
            inputs = stage / "input"
            inputs.mkdir(parents=True)
            for path in sorted(package.used - {"derivation.json"}):
                target = inputs / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(package.file(path), target)
            write_json(inputs / "derivation.json", {"format": "picross-authoring-derivation-v1",
                "original_zip_sha256": report["original_zip_sha256"], "handoff_sha256": report["handoff_sha256"],
                "inventory_sha256": report["inventory_sha256"], "files": hashes(inputs)})
            shutil.copyfile(approval["path"], stage / "approval.json")
            definition_path = "runtime/data/content/" + stem + ".json"
            reveal_path = "runtime/art/content/" + filename
            write_json(stage / definition_path, data)
            (stage / reveal_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(reveal_source, stage / reveal_path)
            (stage / ("runtime/art/content/"+stem+".txt")).write_text(player_notice(package), encoding="utf-8", newline="\n")
            write_json(stage / "inspection.json", report)
            write_json(stage / "usage.txt", {"production_id": report["puzzle_id"], "sources": [package.provenance(package.handoff[k], k) for k in ("reveal", "motif")]})
            manifest = {"format": FORMAT, "adapter": ADAPTER, "definition_id": report["puzzle_id"],
                        "runtime_revision": revision, "package_revision": report["package_revision"], "save_slot": save_slot,
                        "stem": stem, "definition": definition_path, "reveal": reveal_path, "color_mapping": mapping,
                        "selection": report["selection"], "handoff_sha256": report["handoff_sha256"],
                        "inventory_sha256": report["inventory_sha256"], "approval_sha256": approval["sha256"],
                        "technical": True, "editorial_approved": True, "catalog_ready": True, "registered": False,
                        "test_only": report["test_only"], "files": hashes(stage)}
            write_json(stage / "manifest.json", manifest)
            verify_export(stage)
            publish_bundle(stage, output)
    return manifest


def hashes(root):
    return {p.relative_to(root).as_posix(): file_hash(p) for p in sorted(root.rglob("*")) if p.is_file()}


def verify_export(directory):
    from .authoring_package import file_table
    files = file_table(directory, time.monotonic()+300)
    m = exact_keys(load_json(directory / "manifest.json"), {"format", "adapter", "definition_id", "runtime_revision", "package_revision",
        "save_slot", "stem", "definition", "reveal", "color_mapping", "selection", "handoff_sha256", "inventory_sha256", "approval_sha256",
        "technical", "editorial_approved", "catalog_ready", "registered", "test_only", "files"})
    require(m["format"] == FORMAT and m["adapter"] == ADAPTER and isinstance(m["files"], dict) and
            set(files) == set(m["files"]) | {"manifest.json"}, "Invalid/incomplete target export")
    for name, expected in m["files"].items():
        require(file_hash(files[name]) == sha(expected), "Altered export file")
    with open_package(directory / "input") as package:
        report, design, matrix, logic, approval = inspect(package, directory / "approval.json")
        require(approval is not None and m["approval_sha256"] == approval["sha256"], "Missing final export approval")
        require(m["stem"] + Path(m["reveal"]).suffix == Path(m["reveal"]).name and STEM.fullmatch(m["stem"]) and
                STEM.fullmatch(m["save_slot"]), "Invalid export mapping")
        relative(m["save_slot"]+".json")
        require(m["definition"] == "runtime/data/content/"+m["stem"]+".json" and
                m["reveal"] == "runtime/art/content/"+m["stem"]+Path(package.handoff["reveal"]["file"]).suffix,
                "Invalid runtime export paths")
        d = load_json(files[m["definition"]])
        expected, mapping = definition(report, design, matrix, logic, d["reveal"]["name"], m["runtime_revision"], Path(m["reveal"]).name)
        require(d == expected and mapping == m["color_mapping"] and file_hash(files[m["reveal"]]) == report["selection"]["reveal"]["sha256"],
                "Written runtime content differs from certified input")
        require(load_json(directory / "usage.txt") == {"production_id": report["puzzle_id"],
                "sources": [package.provenance(package.handoff[k], k) for k in ("reveal", "motif")]}, "Usage notice differs from input provenance")
        require((directory / ("runtime/art/content/"+m["stem"]+".txt")).read_text(encoding="utf-8") == player_notice(package), "Missing/changed player notice")
        require(m["definition_id"] == report["puzzle_id"] and m["package_revision"] == report["package_revision"] and
                all(m[k] == report[k] for k in ("selection", "handoff_sha256", "inventory_sha256", "test_only")) and
                all(m[k] is True for k in ("technical", "editorial_approved", "catalog_ready")) and m["registered"] is False,
                "Invalid export gates/identity")
        stored = load_json(directory / "inspection.json")
        require(isinstance(stored, dict) and set(stored) == set(report) and
                all(stored[k] == report[k] for k in report if k not in ("checked_at_utc", "tool", "fresh_verification")),
                "Inspection record differs")
        timestamp(stored["checked_at_utc"])
        tool = exact_keys(stored["tool"], {"adapter", "commit", "versions", "modules"})
        require(tool["adapter"] == ADAPTER and isinstance(tool["modules"], dict) and
                set(tool["modules"]) == set(report["tool"]["modules"]) and
                (tool["commit"] is None or isinstance(tool["commit"], str) and re.fullmatch(r"[0-9a-f]{40}",tool["commit"])), "Invalid inspection tool identity")
        for value in tool["modules"].values(): sha(value)
        require(isinstance(stored["fresh_verification"], dict) and stored["fresh_verification"].get("certified") is True and
                stored["fresh_verification"].get("status") == checked_status(report), "Invalid stored fresh verification")
    return m, report


def checked_status(report):
    return "found" if report["source"]["kind"] == "repair" else "solved"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("inspect", "export"):
        p = sub.add_parser(cmd)
        p.add_argument("--input", type=Path, required=True)
        p.add_argument("--approval", type=Path)
        if cmd == "inspect":
            p.add_argument("--report", type=Path)
        else:
            p.add_argument("--output-dir", type=Path, required=True)
            p.add_argument("--name", required=True)
            p.add_argument("--runtime-revision", type=int, required=True)
            p.add_argument("--stem", required=True)
            p.add_argument("--save-slot", required=True)
    for cmd in ("verify-export", "plan", "register"):
        p = sub.add_parser(cmd)
        p.add_argument("--export", type=Path, required=True)
        if cmd != "verify-export":
            p.add_argument("--checkout", type=Path, required=True)
    recovery = sub.add_parser("recover-registration")
    recovery.add_argument("--checkout", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            with open_package(args.input) as package:
                result = inspect(package, args.approval)[0]
            if args.report:
                require(not args.report.exists(), "Inspection output exists")
                write_json(args.report, result)
        elif args.command == "export":
            result = export(args.input, args.output_dir, name=args.name, revision=args.runtime_revision,
                            stem=args.stem, save_slot=args.save_slot, approval_path=args.approval)
        elif args.command == "verify-export":
            result = verify_export(args.export)[1]
        elif args.command == "recover-registration":
            from .content_registry import recover
            result = recover(args.checkout)
        else:
            from .content_registry import registration
            result = registration(args.export, args.checkout, apply=args.command == "register")
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (InvalidInput, InvalidProof, Aborted, OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(json.dumps({"status": "blocked", "catalog_ready": False, "registered": False, "error": str(exc)}))
        return 4 if isinstance(exc, Aborted) else 2


if __name__ == "__main__":
    raise SystemExit(main())
