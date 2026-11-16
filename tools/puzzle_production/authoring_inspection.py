"""Current integration CLI and creative authoring inspection."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
import re
import signal
import sys
import threading

from .authoring_package import (ID, STEM, Package, open_package, require, sha,
                                string, timestamp, relative)
from .contract import (Aborted, Budget, InvalidInput, InvalidProof, digest,
                       exact_keys, integer, load_json, validate_logic, write_json)
from .images import (MAX_BYTES, file_hash, inspect_candidate, logic_from_matrix,
                     normalize, publish_bundle, versions)
from . import categories
from . import operation_diagnostics as diagnostic
from . import palette_gate

ADAPTER = "authoring-p1-rect-color-1"
BACKGROUND_INSPECTION = "picross-authoring-content-inspection-v1"

def tool_identity(legacy=False, manual=False, color=False, paired=False, accepted_raster=False, palette=False,
                  background=False, fixed=False):
    root = Path(__file__).resolve().parents[2]
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                         timeout=10, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        commit = None
    files = ["authoring_package.py", "authoring_inspection.py", "image_validation.py",
             "images.py", "repair.py", "contract.py", "verifier.py"]
    if not legacy:
        files.append("categories.py")
    if manual:
        files.append("manual_derivation.py")
    if color:
        files.append("color_derivation.py")
    if paired:
        files.extend(("certification.py", "paired_verifier.py"))
    if accepted_raster:
        files.append("accepted_raster.py")
    if palette:
        files.extend(("palette_quality.py", "palette_gate.py"))
    if background:
        files.extend(("background_package.py", "background_assets.py", "background_contract.py", "background_io.py",
                      "background_export.py", "authoring_staging.py", "authoring_workflow.py"))
    if fixed:
        files.extend(('fixed_raster.py', 'raster_parameters.py'))
    return {"adapter": ADAPTER, "commit": commit, "versions": versions(),
            "modules": {n: file_hash(Path(__file__).with_name(n)) for n in files}}


from .image_validation import validate_reveal


def _outer_presentation(package, checked):
    """A late declaration binds the sealed input; an original choice is reusable."""
    decision = checked["decision"]
    if decision is None:
        return
    old = package.handoff["background"]["decision"]
    if old is not None and checked["binding"]["decision"]["ref"] == old["ref"]:
        return
    if decision["carried_from"] is not None:
        return  # The complete predecessor graph preserves the original human bytes.
    h = package.handoff
    require(package.archive_sha256 is not None and decision["presented_package"] == {
        "puzzle_id": h["puzzle_id"], "revision": h["revision"],
        "original_zip_sha256": package.archive_sha256,
        "handoff_sha256": file_hash(package.file("handoff.json")),
        "inventory_sha256": h["inventory"]["sha256"]},
        "Late background declaration requires this exact presented original package")


def final_approval(package, selection, approval_path=None):
    h = package.handoff
    if approval_path is None:
        ref = h.get("final_editorial_approval")
        if ref is None:
            return None
        approval_path = package.file(ref)
    background = package.background_enabled
    if background:
        from . import catalog_io as io
        approval_path = io.external(approval_path)
        approval_bytes = io.read(approval_path.parent, approval_path.name, 128 * 1024)
        value = io.json_bytes(approval_bytes, 128 * 1024)
    else:
        value = load_json(approval_path)
    a = exact_keys(value, {"format", "actor", "timestamp_utc", "statement", "puzzle_id",
                 "revision", "handoff_sha256", "inventory_sha256", "selection", "test_only"} |
                 ({"original_zip_sha256", "background"} if background else set()))
    require(a["format"] == ("picross-editorial-approval-v2" if background else "picross-editorial-approval-v1"),
            "Unsupported final editorial approval")
    for key in ("actor", "statement"):
        string(a[key], "final approval " + key)
    timestamp(a["timestamp_utc"])
    require(a["puzzle_id"] == h["puzzle_id"] and a["revision"] == h["revision"] and
            a["handoff_sha256"] == file_hash(package.file("handoff.json")) and
            a["inventory_sha256"] == h["inventory"]["sha256"] and a["selection"] == selection,
            "Final editorial approval does not bind this handoff/selection")
    require(type(a["test_only"]) is bool and a["test_only"] == h.get("test_only", False),
            "Test-only approval scope mismatch")
    result = {"record": a, "sha256": hashlib.sha256(approval_bytes).hexdigest() if background else file_hash(approval_path),
              "path": approval_path}
    if background:
        require(package.archive_sha256 is not None and package.derivation is None and
                sha(a["original_zip_sha256"]) == package.archive_sha256,
                "Background final approval requires the exact unchanged original ZIP")
        from .background_package import validate_external
        b = exact_keys(a["background"], {"manifest", "decision", "derivation", "outcome", "candidate_id",
                                         "original", "output", "profile_sha256"})
        binding = {k: b[k] for k in ("manifest", "decision", "derivation")}
        binding["history"] = h["background"]["history"]
        checked = validate_external(package.root, h, binding, history_repo=package.history_repo,
                                    deadline=package.deadline, external_root=package.external_root,
                                    transport=package.transport)
        require(checked["ready"] and checked["status"] in ("selected", "none"),
                "Final approval requires a ready selected background or explicit none")
        require(binding["manifest"]["ref"] == h["background"]["manifest"]["ref"],
                "Final approval background differs from original work manifest")
        decision, derivation = checked["decision"], checked["derivation"]
        require(b["outcome"] == decision["outcome"] == derivation["outcome"] and
                b["candidate_id"] == decision["candidate_id"] == derivation["candidate_id"] and
                b["original"] == decision["original"] == derivation["source"] and
                b["output"] == derivation["output"] and b["profile_sha256"] == derivation["profile_sha256"],
                "Final approval background selection/profile/output binding differs")
        _outer_presentation(package, checked)
        require(io.read(approval_path.parent, approval_path.name, 128 * 1024) == approval_bytes,
                "Final approval changed during inspection")
        result["background"] = checked
    return result


def inspect_authoring(package: Package, approval_path=None, *, legacy=False, manual_authorization=None,
            palette_exception=None, allow_background=False, background_binding=None):
    h = package.handoff
    background = package.background_enabled
    require(not background or allow_background and not legacy,
            "Background content requires explicit read-only inspection admission")
    require(background_binding is None or background and allow_background,
            "Outer background binding requires explicit background inspection")
    palette = h["rulebook"]["version"] == "0.6.0" or background
    require(not palette or not legacy, "Authoring 0.6.0 requires export v5")
    require(palette or palette_exception is None, "Palette exception requires authoring 0.6.0 or admitted 0.7.0")
    for name in ("brief", "report", "decisions", "effort"):
        package.file(h.get(name))
    require(type(h.get("test_only", False)) is bool, "Invalid test-only marker")
    gates = h.get("gates")
    required = ("reveal_approval", "motif", "provenance", "logic", "frame", "visual", "difficulty", "reveal_consistency")
    require(isinstance(gates, dict) and all(v in ("pending", "pass", "fail", "blocked") for v in gates.values()),
            "Invalid gate statuses")
    evidence = h.get("gate_evidence")
    require(isinstance(evidence, dict), "Gate evidence missing")
    manual = isinstance(h.get("candidate"), dict) and h["candidate"].get("source_type") == "manual"
    edited_import = h.get("manual_edit_record") is not None
    color_import = h.get("editorial_manual_derivation") is not None
    approved_color = isinstance(h.get("repair"), dict) and h["repair"].get("type") == "fixed_color_editorial_redraw"
    color_chain = color_import or approved_color
    auth = None
    late_raster = False
    if manual or edited_import or color_chain:
        require(not legacy, "Manual derivation requires export v3")
        from .manual_derivation import authorization, IMPORT_AUTH_FORMAT
        auth = authorization(package, manual_authorization)
        late_raster = auth["record"]["format"] == "picross-manual-authorization-v6"
        require((auth["record"]["format"] == IMPORT_AUTH_FORMAT) == edited_import and
                (auth["record"]["format"] == "picross-manual-authorization-v3") == color_import and
                (auth["record"]["format"] in ("picross-manual-authorization-v4", "picross-manual-authorization-v5")) == approved_color,
                "Manual authorization/source version mismatch")
    else:
        require(manual_authorization is None, "Manual authorization requires a manual source")
        if not background:
            require(h.get("content_blockers", []) == [], "Unresolved content blockers")
    if background:
        permitted = set(package.background["blockers"]) | {"final_editorial: missing bound human final approval"}
        if auth is not None:
            # The existing authorization reader already bound these exact
            # superseded statements and permissions to this input/owner record.
            # All actual hard gates and source proofs still run below.
            permitted.update(auth["record"]["superseded_content_blockers"])
        for field in ("content_blockers", "blockers"):
            blockers = h.get(field, [])
            require(isinstance(blockers, list) and all(isinstance(v, str) and v in permitted for v in blockers),
                    "Unresolved content blockers outside background/final approval")
    frame_exception = bool(edited_import and auth["record"]["frame_exception"])
    for gate in required:
        require(gates.get(gate) == "pass" or gate == "frame" and frame_exception and gates.get(gate) == "fail" or
                gate == "motif" and (color_import or late_raster) and gates.get(gate) == "pending",
                "Unresolved content gate: " + gate)
        if not (gate == "motif" and (color_import or late_raster)):
            package.file(evidence.get(gate))
    for kind in ("reveal", "motif"):
        record = h.get(kind)
        package.bound(record)
        if late_raster and kind == "reveal":
            from .accepted_raster import historical_reveal
            historical_reveal(package, auth["record"]["historical_reveal"])
            continue
        if not (kind == "motif" and (color_import or late_raster)):
            package.approval(record, kind)
        package.provenance(record, kind)
    require(h["motif"].get("derived_from_reveal_sha256") == h["reveal"]["sha256"], "Wrong motif/reveal derivation")
    c = h.get("candidate")
    require(isinstance(c, dict), "Missing selected candidate")
    bundle = package.bundle(c.get("bundle"))
    kind = c.get("source_type")
    budget = Budget(min(120, max(0, package.deadline - time.monotonic())), 1_000_000)
    if late_raster:
        from .accepted_raster import inspect_source
        design, matrix, proof, checked, source, reference = diagnostic.candidate_check(inspect_source, package, budget)
        expected_proof = c["bundle"] + "/" + c["variant"] + "-proof.json"
    elif color_chain:
        from .color_derivation import inspect_chain
        design, matrix, proof, checked, source, reference = diagnostic.candidate_check(inspect_chain, package, auth, budget)
        expected_proof = c["bundle"] + "/" + c["variant"] + "-proof.json"
    elif edited_import:
        from .manual_derivation import inspect_edited_import
        design, matrix, proof, checked, source, reference = diagnostic.candidate_check(inspect_edited_import, package, auth, budget)
        expected_proof = c["bundle"] + "/" + c["variant"] + "-proof.json"
    elif kind == "fixed":
        from .fixed_raster import inspect_package
        design, matrix, proof, checked, source, reference = diagnostic.candidate_check(inspect_package, package, budget)
        expected_proof = c['bundle'] + '/proof.json'
    elif kind == "import":
        require(h.get("repair") is None, "Ambiguous import/repair origin")
        candidate, proof, checked = diagnostic.candidate_check(inspect_candidate, bundle, c.get("variant"), budget)
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
        checked = diagnostic.candidate_check(inspect_repair, bundle, reference, budget)
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
    elif kind == "manual":
        from .manual_derivation import inspect_manual
        design, matrix, proof, checked, source, reference = diagnostic.candidate_check(inspect_manual, package, budget)
        expected_proof = c["bundle"] + "/certificate/proof.json"
    else:
        raise InvalidInput("Unsupported/ambiguous candidate source_type")
    require(c.get("proof") == expected_proof, "Handoff proof selection differs")
    paired = proof["format"] == "picross-proof-v3"
    if paired:
        require(not legacy and h["rulebook"]["version"] in ("0.5.0", "0.6.0", "0.7.0", "0.8.0") and
                c.get("certification") == checked.get("certification") and c.get("certification") is not None,
                "Paired proof requires explicit authoring 0.5.0 profile binding")
    logic = logic_from_matrix(matrix, design)
    require(c.get("matrix_hash") == digest(matrix) and c.get("logic_hash") == digest(logic), "Selected matrix/logic binding differs")
    require(proof["final_domains"] == [[[v] for v in row] for row in matrix], "Proof enddomains differ")
    manifest = load_json(reference / "manifest.json")
    require(file_hash(reference / manifest["original"]) == h["motif"]["sha256"], "Import source is not the approved motif")
    params = ([auth["record"]["accepted_motif" if color_import or late_raster else "approved_motif"]["parameters"]]
              if color_chain or late_raster else h.get("approved_parameters"))
    require(isinstance(params, list) and params, "Missing explicit approved parameters")
    from . import raster_parameters
    modern_parameters = any(isinstance(p, dict) and p.get('format') == raster_parameters.FORMAT for p in params)
    if modern_parameters:
        require(h['rulebook']['version'] == '0.8.0' and kind in ('import', 'fixed'), 'New corridor requires regular 0.8 import/fixed source')
        corridor = raster_parameters.binding(params, package.approval(h['motif'], 'motif'))
        raster_parameters.result(corridor, design, matrix)
        if kind == 'import':
            require(raster_parameters.import_entry(design, matrix, c['variant']) in corridor['imports'], 'Import outside approved corridor')
    for p in ([] if modern_parameters else params):
        require(isinstance(p,dict), "Invalid approved parameters")
        for key in ("width","height","foreground_colors"):
            integer(p.get(key),1,4096,"approved "+key)
        require(isinstance(p.get("method"),str) and isinstance(p.get("fit"),str) and
                isinstance(p.get("actual_crop"),list) and len(p["actual_crop"]) == 4 and
                all(type(v) is int for v in p["actual_crop"]), "Invalid approved method/fit/crop")
    variant = source["reference"]["variant"] if kind in ("repair", "manual", "fixed") or edited_import else c["variant"]
    v = next(v for v in design["variants"] if v["id"] == variant)
    require(modern_parameters or any(isinstance(p, dict) and p.get("width") == design["width"] and p.get("height") == design["height"] and
                p.get("mode") == design["mode"] and p.get("foreground_colors") == len(design["palette"]) and
                p.get("method") == v["method"] and p.get("fit") == design["fit"] and
                p.get("actual_crop") == design["crop"] for p in params), "Selected design lies outside approved parameter binding")
    motif_approval = auth["record"]["accepted_motif"] if color_import or late_raster else package.json(h["motif"]["approval"])
    corridor = motif_approval.get("parameters")
    require(isinstance(corridor,dict), "Missing motif parameter corridor")
    for key in (() if modern_parameters else ("width","height","foreground_colors")):
        integer(corridor.get(key),1,4096,"motif approval "+key)
    require(modern_parameters or isinstance(corridor, dict) and all(corridor.get(k) == design[k] for k in ("width", "height", "mode")) and
            corridor.get("foreground_colors") == len(design["palette"]) and corridor.get("method") == v["method"],
            "Motif approval parameter corridor differs")
    color_limit = 4 if legacy else 8
    require(1 <= design["width"] <= 50 and 1 <= design["height"] <= 50 and 1 <= len(design["palette"]) <= color_limit,
            f"Target profile requires 1..50 per axis and 1..{color_limit} foreground colors; no conversion")
    left = any(row[0] != "empty" for row in matrix)
    right = any(row[-1] != "empty" for row in matrix)
    top, bottom = (any(v != "empty" for v in row) for row in (matrix[0], matrix[-1]))
    frame_valid = (left or right) and (top or bottom)
    require(frame_valid or frame_exception, "Authoring frame rule failed: (left OR right) AND (top OR bottom)")
    reveal = validate_reveal(package.file(h["reveal"]["file"]), design["width"], design["height"])
    difficulty = package.json(h.get("difficulty"))
    require(isinstance(difficulty, dict) and difficulty.get("method") in
            (("picross-difficulty-0.2",) if paired else ("picross-difficulty-0.1", "picross-difficulty-0.2")) and
            difficulty.get("assessment_type") in ("editorial_estimate", "instrumented") and
            difficulty.get("level") in ("L1", "L2", "L3", "L4", "L5") and
            difficulty.get("confidence") in ("low", "medium", "high") and difficulty.get("logic_hash") == digest(logic),
            "Invalid difficulty binding")
    levels = difficulty.get("plausible_range")
    require(isinstance(levels, list) and len(levels) == 2 and all(v in ("L1", "L2", "L3", "L4", "L5") for v in levels) and
            levels[0] <= difficulty["level"] <= levels[1] and isinstance(difficulty.get("rule_families"), dict) and
            difficulty["rule_families"], "Missing difficulty uncertainty/reasoning")
    require(all(k in (("R0","R1","R2","R3","R4") if paired else ("R0","R1","R2","R3")) and isinstance(v,str) and bool(v.strip())
                for k,v in difficulty["rule_families"].items()), "Invalid difficulty rule reasoning")
    if difficulty["method"] == "picross-difficulty-0.2":
        require(h["rulebook"]["version"] in ("0.5.0", "0.6.0", "0.7.0", "0.8.0"),
                "Difficulty 0.2 requires authoring 0.5.0/0.6.0 or admitted 0.7.0")
    if paired:
        from .certification import LABEL
        assessment = checked.get("assessment")
        require(isinstance(assessment, dict) and assessment["proof_verified"] and assessment["baseline_verified"] and
                assessment["outcome"] in ("paired_lines_solved", "line_logic_solved"),
                "Missing completed independent baseline/paired assessment")
        assessment_path = expected_proof.removesuffix("proof.json") + "assessment.json"
        require(difficulty.get("evidence") == assessment_path and package.json(assessment_path) == assessment and
                difficulty.get("profile_hash") == proof["profile_hash"], "Difficulty evidence/profile mismatch")
        if assessment["r4_required"]:
            require("R4" in difficulty["rule_families"] and difficulty["level"] == "L5" and levels == ["L5", "L5"] and
                    difficulty["assessment_type"] == "instrumented" and difficulty["confidence"] == "medium" and
                    difficulty.get("logical_demand") == LABEL, "Necessary R4 requires explicit L5/high logical demand")
        else:
            require("R4" not in difficulty["rule_families"], "Used paired profile does not prove R4 necessity")
    if difficulty.get("evidence") is not None:
        package.file(difficulty["evidence"])
    selection = {"variant": c["variant"], "matrix_hash": digest(matrix), "logic_hash": digest(logic),
                 "reveal": {"file": h["reveal"]["file"], "sha256": h["reveal"]["sha256"]}}
    approval = final_approval(package, selection, approval_path)
    if edited_import or color_chain or late_raster:
        require(approval is not None, "Edited import requires bound final approval")
    if auth is not None and approval is not None:
        require(auth["owner"]["approval_sha256"] == approval["sha256"], "Owner override final approval binding mismatch")
    report = {"format": "picross-target-inspection-v1", "adapter": ADAPTER, "technical": True,
              "editorial_approved": approval is not None, "catalog_ready": approval is not None, "registered": False,
              "blockers": [] if approval else ["final_editorial: missing bound human final approval"],
              "puzzle_id": h["puzzle_id"], "package_revision": h["revision"], "selection": selection,
              "handoff_sha256": file_hash(package.file("handoff.json")), "inventory_sha256": h["inventory"]["sha256"],
              "original_zip_sha256": (package.derivation or {}).get("original_zip_sha256") if package.derivation else package.archive_sha256,
              "source": source, "width": design["width"], "height": design["height"], "mode": design["mode"],
              "difficulty": difficulty, "frame": {"left": left, "right": right, "top": top, "bottom": bottom},
              "fresh_verification": checked, "reveal": reveal, "tool": tool_identity(legacy, manual or edited_import or color_chain, color_chain, paired, late_raster, palette, background, kind == 'fixed'),
              "checked_at_utc": datetime.now(timezone.utc).isoformat(), "test_only": h.get("test_only", False)}
    if not legacy:
        report.update(format="picross-target-inspection-v2", category_id=None,
                      category_ready=False, catalog_ready=False)
    if auth is not None:
        report.update(format="picross-target-inspection-v3", manual_authorization_sha256=auth["sha256"],
                      owner_override_sha256=auth["record"]["owner_override"]["sha256"])
    if paired:
        report.update(format="picross-target-inspection-v4", deduction={"profile": proof["profile"],
                      "profile_hash": proof["profile_hash"], "assessment": assessment})
    if edited_import:
        report.update(frame_valid=frame_valid, frame_exception_accepted=frame_exception and not frame_valid)
    if color_import or late_raster:
        report.update(original_state=h["state"], original_motif_gate=gates["motif"],
                      late_motif_acceptance=True, accepted_motif=auth["record"]["accepted_motif"],
                      superseded_content_blockers=auth["record"]["superseded_content_blockers"])
    if late_raster:
        report["historical_reveal_binding"] = auth["record"]["historical_reveal"]
    if approved_color:
        report.update(original_state=h["state"], original_motif_gate=gates["motif"],
                      late_motif_acceptance=False, approved_motif=auth["record"]["approved_motif"],
                      superseded_content_blockers=auth["record"]["superseded_content_blockers"])
    if palette:
        gate = palette_gate.inspect(package, design, matrix, logic, source, reference, approval, palette_exception, budget)
        report.update(format="picross-target-inspection-v5", palette_gate=gate, technical=gate["allowed"])
        if not gate["allowed"]:
            report["blockers"].append("palette: current measurement/visual acceptance or bound exception required")
            report["catalog_ready"] = False
    if background:
        current = approval["background"] if approval is not None else package.background
        if background_binding is not None:
            from .background_package import validate_external
            supplied = validate_external(package.root, h, background_binding, history_repo=package.history_repo,
                                         deadline=package.deadline, external_root=package.external_root,
                                         transport=package.transport)
            _outer_presentation(package, supplied)
            require(approval is None or supplied["binding"] == current["binding"],
                    "Supplied background binding differs from final approval")
            current = supplied
        package.effective_background = current
        require(h["state"] != "content_ready" or package.background["ready"],
                "content_ready requires background readiness in the original package")
        report["blockers"].extend(current["blockers"])
        from .authoring_workflow import is_current
        report.update(format='picross-authoring-content-inspection-v2' if is_current(h) else BACKGROUND_INSPECTION, original_state=h["state"],
                      effective_state=("blocked" if not report["technical"] else
                                       "editorially_approved" if approval is not None else
                                       "content_ready" if current["ready"] else
                                       "background_review" if is_current(h) and h['background'] is not None else "raster_ready"),
                      background={k: current[k] for k in ("status", "ready", "binding")},
                      integration_ready=False, catalog_ready=False)
    return report, design, matrix, logic, approval


def categorize(report, catalog, category_id):
    require(report.get("format") not in (BACKGROUND_INSPECTION, 'picross-authoring-content-inspection-v2'),
            "Background content inspection does not admit catalog integration")
    categories.lookup(catalog, category_id)
    report.update(category_id=category_id, category_ready=True,
                  catalog_ready=report["editorial_approved"] and report["technical"])


def definition(report, design, matrix, logic, name, revision, stem):
    require(report.get("format") != BACKGROUND_INSPECTION,
            "Background content inspection does not admit target export")
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


def source_provenances(package, report):
    if "historical_reveal_binding" in report:
        from .accepted_raster import historical_reveal
        reveal = historical_reveal(package, report["historical_reveal_binding"])
    else:
        reveal = package.provenance(package.handoff["reveal"], "reveal")
    return [reveal, package.provenance(package.handoff["motif"], "motif")]


def player_notice(package, report=None):
    p = (source_provenances(package, report)[0] if report is not None else
         package.provenance(package.handoff["reveal"], "reveal"))
    return "\n".join(("Production ID: " + package.handoff["puzzle_id"], "Artwork: " + p["author"],
                      "Usage basis: " + p["usage_basis"], ""))


def checked_status(report):
    return "found" if report["source"]["kind"] == "repair" else "solved"



# Creative inspection API; it cannot export or register catalog content.
inspect = inspect_authoring
