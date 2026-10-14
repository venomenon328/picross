"""Externally accepted, sealed fixed-color derivations; no search or gate waiver."""
from copy import deepcopy
import time

from .authoring_package import file_hash, require, sha, string, timestamp
from .contract import digest, exact_keys, integer, load_json
from .images import inspect_candidate

FORMAT = "picross-manual-authorization-v3"


def authorization(package, path, raw):
    a = exact_keys(raw, {"format", "puzzle_id", "revision", "original_zip_sha256", "handoff_sha256",
        "inventory_sha256", "selection", "owner_override", "superseded_content_blockers",
        "accepted_motif", "base", "steps"})
    h, c = package.handoff, package.handoff.get("candidate")
    require(isinstance(c, dict) and c.get("source_type") == "import" and h.get("repair") is None and
            isinstance(h.get("editorial_manual_derivation"), str) and h.get("manual_edit_record") is None and
            h.get("state") == "raster_review", "V3 requires a sealed fixed-color review import")
    original = package.derivation["original_zip_sha256"] if package.derivation else package.archive_sha256
    if a["original_zip_sha256"] is not None:
        sha(a["original_zip_sha256"])
    selection = {k: c[k] for k in ("variant", "matrix_hash", "logic_hash")}
    selection["reveal"] = {k: h["reveal"][k] for k in ("file", "sha256")}
    require(a["puzzle_id"] == h["puzzle_id"] and a["revision"] == h["revision"] and
            a["original_zip_sha256"] == original and a["selection"] == selection and
            a["handoff_sha256"] == file_hash(package.file("handoff.json")) and
            a["inventory_sha256"] == h["inventory"]["sha256"], "Color authorization input binding mismatch")
    require(h.get("content_blockers", []) == [] and a["superseded_content_blockers"] == h.get("blockers", []) and
            isinstance(a["superseded_content_blockers"], list) and len(a["superseded_content_blockers"]) <= 32 and
            all(isinstance(b, str) and 1 <= len(b) <= 4096 for b in a["superseded_content_blockers"]),
            "Color authorization blocker scope mismatch")
    motif = exact_keys(a["accepted_motif"], {"file", "sha256", "derived_from_reveal_sha256", "revision", "parameters"})
    require(all(motif[k] == h["motif"].get(k) for k in ("file", "sha256", "derived_from_reveal_sha256")),
            "External motif binding mismatch")
    string(motif["revision"], "accepted motif revision", 32)
    require(h["motif"].get("revision", motif["revision"]) == motif["revision"] and
            isinstance(motif["parameters"], dict) and motif["parameters"] in h.get("proposed_parameters", []),
            "External motif parameter binding mismatch")
    require(h["gates"].get("motif") == "pending" and h["motif"].get("approval") is None and
            h.get("approved_parameters") == [], "V3 only closes pending motif metadata")
    base = exact_keys(a["base"], {"source_type", "bundle", "variant", "reference_bundle", "reference_variant", "matrix_hash"})
    require(base["source_type"] in ("import", "repair"), "Unsupported color derivation base")
    sha(base["matrix_hash"])
    string(base["variant"], "base variant", 32)
    package.bundle(base["bundle"])
    if base["source_type"] == "repair":
        package.bundle(base["reference_bundle"])
        string(base["reference_variant"], "base reference variant", 32)
    else:
        require(base["reference_bundle"] is None and base["reference_variant"] is None, "Ambiguous color import base")
    require(isinstance(a["steps"], list) and 1 <= len(a["steps"]) <= 8, "Invalid fixed-color chain length")
    for step in a["steps"]:
        exact_keys(step, {"record", "plan", "output"})
        for key in ("record", "plan"):
            exact_keys(step[key], {"file", "sha256"})
            package.bound(step[key])
        exact_keys(step["output"], {"bundle", "variant"})
        package.bundle(step["output"]["bundle"])
        string(step["output"]["variant"], "step variant", 32)
    require(a["steps"][-1]["record"]["file"] == h["editorial_manual_derivation"] and
            a["steps"][-1]["output"] == {k: c[k] for k in ("bundle", "variant")}, "Color chain final selection mismatch")
    require(package.json(a["steps"][-1]["plan"]["file"]).get("revision") == h["revision"],
            "Color final plan revision mismatch")
    ref = exact_keys(a["owner_override"], {"file", "sha256"})
    require(ref["file"] == "owner-override.json", "Invalid owner override filename")
    owner_path = path.parent / ref["file"]
    require(owner_path.is_file() and not owner_path.is_symlink() and file_hash(owner_path) == sha(ref["sha256"]),
            "Color owner file binding mismatch")
    owner = load_json(owner_path, 256 * 1024)
    common = set(a) - {"format", "original_zip_sha256", "owner_override"}
    exact_keys(owner, common | {"format", "actor", "statement", "timestamp_utc", "package_sha256", "approval_sha256", "permissions"})
    require(owner["format"] == "picross-owner-override-v3" and all(owner[k] == a[k] for k in common) and
            owner["package_sha256"] == original, "Color owner input binding mismatch")
    for key in ("actor", "statement"):
        string(owner[key], "color owner " + key)
    timestamp(owner["timestamp_utc"])
    sha(owner["approval_sha256"])
    permissions = exact_keys(owner["permissions"], {"fixed_color_edits", "late_motif_acceptance"})
    require(all(v is True for v in permissions.values()), "Color owner permission scope mismatch")
    return {"record": a, "path": path, "sha256": file_hash(path), "owner": owner, "owner_path": owner_path}


def replay(matrix, design, record, plan, budget):
    """Read the two historical fixed-record formats without rewriting their bytes."""
    require(record.get("format") in ("picross-editorial-raster-redraw-v1", "picross-editorial-fixed-cell-derivation-v1") and
            record.get("search") is False and record.get("seed") is None and
            plan.get("search") is False and plan.get("seed") is None, "Color edits cannot search")
    require(record.get("reference_matrix_hash") == digest(matrix), "Color chain parent mismatch")
    if record["format"] == "picross-editorial-raster-redraw-v1":
        require(plan.get("format") == "picross-editorial-raster-redraw-plan-v1", "Invalid redraw plan")
        maximum = plan["limits"]["max_changed_positions"]
        mask = record.get("protected")
        limits = plan["limits"]
    else:
        require(plan.get("format") == "picross-editorial-fixed-cell-plan-v1" and
                plan.get("edits") == record.get("edits") and
                plan.get("reference_matrix_hash") == record["reference_matrix_hash"], "Invalid fixed-color plan")
        maximum, mask = plan.get("max_changes"), plan.get("protected")
        limits = plan
    seconds = integer(limits.get("verify_seconds"), 1, 120, "color verify seconds")
    lines = integer(limits.get("max_lines"), 1, 1000000, "color verify lines")
    integer(limits.get("solve_seconds"), 1, 120, "color solve seconds")
    budget.deadline = min(budget.deadline, time.monotonic() + seconds)
    budget.max_lines = min(budget.max_lines, budget.lines + lines)
    integer(maximum, 1, design["width"] * design["height"], "fixed-color change budget")
    require(isinstance(mask, list) and len(mask) == design["height"] and all(isinstance(row, list) and
            len(row) == design["width"] and all(type(v) is bool for v in row) for row in mask), "Invalid color protection mask")
    edits = record.get("edits")
    require(isinstance(edits, list) and 1 <= len(edits) <= maximum, "Color edit budget exceeded")
    result, changed = deepcopy(matrix), set()
    values = {"empty", *(entry["id"] for entry in design["palette"])}
    for edit in edits:
        budget.check()
        exact_keys(edit, {"column", "row", "before", "after"})
        x = integer(edit["column"], 1, design["width"], "color column") - 1
        y = integer(edit["row"], 1, design["height"], "color row") - 1
        require((x, y) not in changed and not mask[y][x] and edit["before"] in values and edit["after"] in values and
                edit["before"] != edit["after"] and result[y][x] == edit["before"], "Invalid/protected color edit")
        result[y][x] = edit["after"]
        changed.add((x, y))
    require(changed == {(x, y) for y, row in enumerate(mask) for x, protected in enumerate(row) if not protected},
            "Color mask must protect every other position")
    require(record.get("matrix_hash") == digest(result) and record.get("actual_changed_positions") == len(changed),
            "Color replay result mismatch")
    return result, len(changed)


def inspect_chain(package, auth, budget):
    a, h = auth["record"], package.handoff
    base = a["base"]
    bundle = package.bundle(base["bundle"])
    if base["source_type"] == "repair":
        from .repair import inspect_repair
        reference = package.bundle(base["reference_bundle"])
        checked = inspect_repair(bundle, reference, budget)
        raw = load_json(bundle / "repair.json")
        require(checked["certified"] and checked["status"] == "found" and
                base["variant"] == f"candidate-{raw['selected']:03d}" and
                raw["reference"]["variant"] == base["reference_variant"], "Color repair base mismatch")
        design, matrix = load_json(reference / "design.json"), raw["matrix"]
    else:
        candidate, _, _ = inspect_candidate(bundle, base["variant"], budget)
        design, matrix = candidate["design"], candidate["matrix"]
    require(design["mode"] == "color" and 1 <= len(design["palette"]) <= 4 and
            1 <= design["width"] <= 50 and 1 <= design["height"] <= 50 and
            digest(matrix) == base["matrix_hash"], "Color base design/matrix mismatch")
    chain = []
    for step in a["steps"]:
        record, plan = package.json(step["record"]["file"]), package.json(step["plan"]["file"])
        require(plan.get("puzzle_id") == h["puzzle_id"], "Color plan identity mismatch")
        if record["format"] == "picross-editorial-raster-redraw-v1":
            require(record.get("plan_sha256") == step["plan"]["sha256"], "Color redraw plan binding mismatch")
        else:
            require(record.get("plan") == step["plan"]["file"], "Color fixed plan binding mismatch")
        matrix, count = replay(matrix, design, record, plan, budget)
        out = step["output"]
        directory = package.bundle(out["bundle"])
        current, proof, checked = inspect_candidate(directory, out["variant"], budget)
        require(current["matrix"] == matrix and all(current["design"][k] == design[k] for k in
                ("width", "height", "mode", "palette", "background", "alpha_below", "fit")), "Color child changes other cells or design")
        result = load_json(directory / (out["variant"] + "-result.json"))
        require(result.get("status") == "solved" and result.get("certified") is True and
                result.get("proof_verified") is True and checked["certified"] and checked["status"] == "solved" and
                proof["final_domains"] == [[[v] for v in row] for row in matrix], "Color child certificate incomplete")
        chain.append({"record_sha256": step["record"]["sha256"], "matrix_hash": digest(matrix), "changed_cells": count})
    source = {"kind": "manual", "variant": h["candidate"]["variant"], "candidate_id": current["id"],
              "reference": {"variant": h["candidate"]["variant"]}, "chain": chain,
              "changed_cells": sum(s["changed_cells"] for s in chain)}
    # Parameter/source checks below the replay bind the final accepted pixel source.
    return current["design"], matrix, proof, checked, source, directory
