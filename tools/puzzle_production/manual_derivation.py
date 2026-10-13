"""Explicitly authorized, fixed mono cell removals; no search or code in inputs."""
from copy import deepcopy
from pathlib import Path
import time

from .authoring_package import file_hash, require, sha, string, timestamp
from .contract import exact_keys, integer, load_json, digest, validate_logic
from .images import inspect_candidate, logic_from_matrix
from .repair import apply_edit
from .verifier import verify

AUTH_FORMAT = "picross-manual-authorization-v1"
OWNER_FILE = "owner-override.json"
AUTH_FILE = "manual-authorization.json"


def authorization(package, path):
    """Check human evidence and exact bindings; never grant a blanket waiver."""
    require(path is not None, "Manual source requires explicit manual authorization")
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "Unsafe/missing manual authorization")
    a = exact_keys(load_json(path, 256 * 1024), {
        "format", "puzzle_id", "revision", "original_zip_sha256", "handoff_sha256",
        "inventory_sha256", "selection", "plan_sha256", "owner_override", "superseded_content_blockers"})
    require(a["format"] == AUTH_FORMAT, "Unsupported manual authorization")
    h = package.handoff
    original = package.derivation["original_zip_sha256"] if package.derivation else package.archive_sha256
    if a["original_zip_sha256"] is not None:
        sha(a["original_zip_sha256"])
    require(a["puzzle_id"] == h["puzzle_id"] and a["revision"] == h["revision"] and
            a["original_zip_sha256"] == original and
            a["handoff_sha256"] == file_hash(package.file("handoff.json")) and
            a["inventory_sha256"] == h["inventory"]["sha256"], "Manual authorization input binding mismatch")
    c = h["candidate"]
    selection = {k: c[k] for k in ("variant", "matrix_hash", "logic_hash")}
    selection["reveal"] = {k: h["reveal"][k] for k in ("file", "sha256")}
    require(a["selection"] == selection, "Manual authorization selection mismatch")
    repair = h.get("repair")
    require(isinstance(repair, dict) and repair.get("type") == "manual", "Missing manual plan reference")
    require(file_hash(package.file(repair.get("plan"))) == sha(a["plan_sha256"]), "Manual authorization plan mismatch")
    blockers = a["superseded_content_blockers"]
    require(isinstance(blockers, list) and len(blockers) <= 32 and
            all(isinstance(b, str) and 1 <= len(b) <= 4096 for b in blockers) and
            blockers == h.get("content_blockers", []), "Manual authorization blocker scope mismatch")
    ref = exact_keys(a["owner_override"], {"file", "sha256"})
    require(ref["file"] == OWNER_FILE, "Invalid owner override filename")
    owner_path = path.parent / OWNER_FILE
    require(owner_path.is_file() and not owner_path.is_symlink() and
            file_hash(owner_path) == sha(ref["sha256"]), "Owner override file binding mismatch")
    owner = load_json(owner_path, 256 * 1024)
    require(isinstance(owner, dict) and owner.get("format") == "picross-owner-override-v1", "Unsupported owner override")
    for key in ("actor", "statement"):
        string(owner.get(key), "owner override " + key)
    timestamp(owner.get("timestamp_utc"))
    require(all(owner.get(k) == a[k] for k in ("puzzle_id", "revision", "handoff_sha256", "inventory_sha256", "selection")) and
            owner.get("package_sha256") == original, "Owner override does not bind manual input")
    sha(owner.get("approval_sha256"))
    return {"record": a, "path": path, "sha256": file_hash(path), "owner": owner, "owner_path": owner_path}


def inspect_manual(package, budget):
    """Reconstruct every authorized edit, all hints and the written final proof."""
    h = package.handoff
    c, repair = h["candidate"], h["repair"]
    reference_dir = package.bundle(repair.get("reference"))
    reference, _, _ = inspect_candidate(reference_dir, repair.get("reference_variant"), budget)
    design, before = reference["design"], reference["matrix"]
    require(design["mode"] == "mono", "Manual removal contract is monochrome only")
    plan_path = package.file(repair.get("plan"))
    plan = exact_keys(load_json(plan_path, 256 * 1024), {
        "format", "puzzle_id", "revision", "reference", "authorization", "coordinates",
        "edits_in_requested_order", "mask", "budgets", "operators", "seed", "randomness", "rationale", "tool_boundary"})
    require(plan["format"] == "picross-manual-edit-plan-v1" and
            plan["puzzle_id"] == h["puzzle_id"] and plan["revision"] == h["revision"], "Manual plan identity mismatch")
    ref = plan["reference"]
    require(isinstance(ref, dict) and ref.get("candidate_id") == reference["id"] and
            ref.get("variant") == repair["reference_variant"] and ref.get("bundle") == repair["reference"] and
            ref.get("manifest_sha256") == file_hash(reference_dir / "manifest.json") and
            ref.get("matrix_hash") == digest(before), "Manual reference binding mismatch")
    require(plan["operators"] == ["remove-ink-only"] and plan["seed"] is None,
            "Unsupported manual operators/randomness")
    for key in ("coordinates", "randomness", "rationale", "tool_boundary"):
        string(plan[key], "manual plan " + key)
    package.file(plan["authorization"])
    limits = exact_keys(plan["budgets"], {"max_changes", "max_steps", "max_candidates", "solve_seconds",
                                         "solve_lines", "verify_seconds", "verify_lines"})
    cells = design["width"] * design["height"]
    integer(limits["max_changes"], 1, cells, "manual changes")
    integer(limits["max_steps"], 1, cells, "manual steps")
    require(type(limits["max_candidates"]) is int and limits["max_candidates"] == 1, "Manual derivation is one fixed candidate")
    for key in ("solve_seconds", "verify_seconds"):
        integer(limits[key], 1, 120, key)
    for key in ("solve_lines", "verify_lines"):
        integer(limits[key], 1, 1000000, key)
    mask = plan["mask"]
    require(isinstance(mask, list) and len(mask) == design["height"] and all(
        isinstance(row, list) and len(row) == design["width"] and all(type(v) is bool for v in row)
        for row in mask), "Invalid manual protection mask")
    edits = plan["edits_in_requested_order"]
    require(isinstance(edits, list) and 1 <= len(edits) <= min(limits["max_changes"], limits["max_steps"]),
            "Manual edit budget exceeded")
    raw = exact_keys(package.json(c.get("candidate")), {"format", "puzzle_id", "revision", "variant", "source_type",
        "matrix", "matrix_hash", "logic_hash", "design", "plan_sha256", "source_candidate_id", "history", "changes", "claim"})
    require(raw["format"] == "picross-manual-candidate-v1" and raw["source_type"] == "manual" and
            raw["puzzle_id"] == h["puzzle_id"] and raw["revision"] == h["revision"] and
            raw["variant"] == c["variant"] and raw["design"] == design and raw["source_candidate_id"] == reference["id"] and
            raw["plan_sha256"] == file_hash(plan_path), "Manual candidate identity mismatch")
    matrix, history, changed = deepcopy(before), [], set()
    for edit in edits:
        budget.check()
        exact_keys(edit, {"x", "y", "before", "after"})
        x = integer(edit["x"], 0, design["width"]-1, "manual x")
        y = integer(edit["y"], 0, design["height"]-1, "manual y")
        require((x, y) not in changed and edit["before"] == "ink" and edit["after"] == "empty",
                "Manual edits must be distinct ink removals")
        changed.add((x, y))
        parent = digest(matrix)
        matrix = apply_edit(matrix, edit, before, mask, limits["max_changes"])
        history.append({"edit": edit, "parent_matrix_hash": parent, "matrix_hash": digest(matrix)})
    require({(x, y) for y, row in enumerate(mask) for x, protected in enumerate(row) if not protected} == changed,
            "Manual mask must protect every other position")
    changes = [{"x": x, "y": y, "before": before[y][x], "after": value}
               for y, row in enumerate(matrix) for x, value in enumerate(row) if value != before[y][x]]
    require(raw["history"] == history and raw["changes"] == changes and raw["matrix"] == matrix and
            raw["matrix_hash"] == digest(matrix) and type(repair.get("changes")) is int and
            repair["changes"] == len(changes), "Manual replay/matrix mismatch")
    logic = logic_from_matrix(matrix, design)
    require(raw["logic_hash"] == digest(logic) and
            package.json(c["bundle"] + "/logic.json") == logic, "Manual clues differ from replayed matrix")
    require(c["proof"] == c["bundle"] + "/certificate/proof.json", "Manual proof selection mismatch")
    puzzle = validate_logic(logic)
    proof = load_json(package.file(c["proof"]), puzzle.proof_byte_limit)
    budget.deadline = min(budget.deadline, time.monotonic() + limits["verify_seconds"])
    budget.max_lines = min(budget.max_lines, budget.lines + limits["verify_lines"])
    # The existing independent DAG verifier receives hints/domains, never the matrix.
    checked = verify(puzzle, proof, budget)
    require(checked["certified"] and checked["status"] == "solved" and
            proof["final_domains"] == [[[v] for v in row] for row in matrix], "Manual final certificate differs from matrix")
    recorded = package.json(c["bundle"] + "/certificate/result.json")
    require(isinstance(recorded, dict) and recorded.get("format") == "picross-result-v1" and
            recorded.get("status") == "solved" and recorded.get("certified") is True and
            recorded.get("proof_verified") is True and recorded.get("logic_hash") == puzzle.logic_hash and
            recorded.get("profile_hash") == checked["profile_hash"], "Manual production certificate was not completed")
    source = {"kind": "manual", "variant": c["variant"], "candidate_sha256": file_hash(package.file(c["candidate"])),
              "reference": {"variant": repair["reference_variant"], "candidate_id": reference["id"]},
              "plan_sha256": file_hash(plan_path), "changed_cells": len(changes)}
    return design, matrix, proof, checked, source, reference_dir
