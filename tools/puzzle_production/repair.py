"""RP-5: bounded single-cell search and independently checked file replay."""
from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
import math
from pathlib import Path
import time

from .contract import (Aborted, Budget, InvalidInput, InvalidProof, digest,
                       exact_keys, integer, load_json, validate_logic, write_json)
from .images import (file_hash, inspect_candidate, logic_from_matrix,
                     publish_bundle, raster_image)
from .solver import solve
from .verifier import verify

VERSION = "rp5-single-cell-1"
PLAN_FORMAT = "picross-repair-plan-v1"
FORMAT = "picross-repair-v1"
PLAN_BYTES = 256 * 1024
HISTORY_BYTES = 2 * 1024 * 1024
MAX_CANDIDATES = 128
MAX_STEPS = 1024
TOTAL_BYTES = 256 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise InvalidInput(message)


def validate_plan(raw, reference):
    p = exact_keys(raw, {"format", "tool", "reference", "mask", "config", "rationale"})
    require(p["format"] == PLAN_FORMAT and p["tool"] == VERSION, "Unsupported repair plan/tool")
    r = exact_keys(p["reference"], {"candidate_id", "manifest_sha256", "variant"})
    require(r["candidate_id"] == reference["id"] and r["variant"] == reference["variant"]["id"],
            "Plan refers to a different imported candidate")
    require(isinstance(r["manifest_sha256"], str) and len(r["manifest_sha256"]) == 64,
            "Invalid reference manifest hash")
    d = reference["design"]
    mask = p["mask"]
    require(isinstance(mask, list) and len(mask) == d["height"] and all(
        isinstance(row, list) and len(row) == d["width"] and all(type(v) is bool for v in row)
        for row in mask), "Protection mask must be an exact boolean grid")
    require(isinstance(p["rationale"], str) and 1 <= len(p["rationale"]) <= 4096,
            "Missing bounded mask/operator rationale")
    c = exact_keys(p["config"], {"max_changes", "max_steps", "max_candidates", "search_seconds",
                               "final_seconds", "search_lines", "final_lines", "seed", "order", "operators"})
    for name, low, high in (("max_changes", 0, d["width"] * d["height"]),
                            ("max_steps", 0, MAX_STEPS), ("max_candidates", 1, MAX_CANDIDATES),
                            ("search_lines", 0, 1_000_000), ("final_lines", 0, 1_000_000),
                            ("seed", 0, 2**32 - 1)):
        integer(c[name], low, high, name)
    for name, high in (("search_seconds", 600), ("final_seconds", 120)):
        require(type(c[name]) in (int, float) and math.isfinite(c[name]) and 0 <= c[name] <= high,
                f"{name} must be finite in 0..{high}")
    require(c["order"] == "seeded-frontier-v1" and c["operators"] == ["single-cell"],
            "Unsupported search order/operators")
    return deepcopy(p)


def distance(matrix, reference):
    return sum(a != b for row, original in zip(matrix, reference) for a, b in zip(row, original))


def apply_edit(matrix, edit, reference, mask, limit):
    e = exact_keys(edit, {"y", "x", "before", "after"})
    y = integer(e["y"], 0, len(matrix)-1, "edit y")
    x = integer(e["x"], 0, len(matrix[0])-1, "edit x")
    require(not mask[y][x] and e["before"] == matrix[y][x] and e["after"] != e["before"],
            "Protected cell, wrong parent value or no-op edit")
    out = deepcopy(matrix)
    out[y][x] = e["after"]
    require(distance(out, reference) <= limit, "Reference-relative change budget exceeded")
    return out


def metrics(proof, matrix, reference, colors):
    remaining = sum(len(d) for row in proof["final_domains"] for d in row)
    return {"unresolved_cells": sum(len(d) != 1 for row in proof["final_domains"] for d in row),
            "domain_values_remaining": remaining,
            "domain_losses": len(matrix)*len(matrix[0])*(len(colors)+1)-remaining,
            "changed_cells": distance(matrix, reference)}


def rank(m):
    # Partial color losses count, even when no additional singleton is obtained.
    return (m["domain_values_remaining"], m["unresolved_cells"], m["changed_cells"])


class Frontier:
    """Best-first parents; worse states remain available, no monotonicity gate."""

    def __init__(self, reference, mask, seed, domains):
        self.reference, self.mask, self.seed = reference, mask, seed
        self.states = []
        # Prioritize actual unresolved cells then their immediate vicinity. The
        # tie order uses canonical SHA-256, independent of Python RNG versions.
        h, w = len(reference), len(reference[0])
        near = [[h+w] * w for _ in range(h)]
        queue = deque()
        for y, row in enumerate(domains):
            for x, d in enumerate(row):
                if len(d) > 1:
                    near[y][x] = 0
                    queue.append((y, x))
        while queue:
            y, x = queue.popleft()
            for a, b in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                if 0 <= a < h and 0 <= b < w and near[a][b] > near[y][x]+1:
                    near[a][b] = near[y][x]+1
                    queue.append((a, b))
        self.near = near
        self.proposals = None

    def add(self, matrix, score, colors):
        if self.proposals is None:
            edits = []
            for y, row in enumerate(matrix):
                for x in range(len(row)):
                    if self.mask[y][x]:
                        continue
                    for after in ("empty", *colors):
                        e = {"y": y, "x": x, "after": after}
                        edits.append((self.near[y][x], digest({"seed": self.seed, "edit": e}), (y, x, after)))
            edits.sort(key=lambda item: item[:2])
            self.proposals = [e for _, _, e in edits]
        self.states.append({"matrix": matrix, "score": score, "cursor": 0})

    def next(self):
        for s in self.states:
            while s["cursor"] < len(self.proposals):
                y, x, after = self.proposals[s["cursor"]]
                if after != s["matrix"][y][x]:
                    break
                s["cursor"] += 1
        available = [(rank(s["score"]), i) for i, s in enumerate(self.states) if s["cursor"] < len(self.proposals)]
        if not available:
            return None
        _, parent = min(available)
        state = self.states[parent]
        y, x, after = self.proposals[state["cursor"]]
        edit = {"y": y, "x": x, "before": state["matrix"][y][x], "after": after}
        state["cursor"] += 1
        return parent, edit


def evaluate(matrix, design, directory, prefix, budget):
    start, lines = time.monotonic(), budget.lines
    puzzle = validate_logic(logic_from_matrix(matrix, design))
    proof = solve(puzzle, budget)
    write_json(directory / f"{prefix}-logic.json", puzzle.to_wire())
    write_json(directory / f"{prefix}-proof.json", proof)
    checked, reason = False, proof["reason"]
    try:
        result = verify(puzzle, load_json(directory / f"{prefix}-proof.json", puzzle.proof_byte_limit), budget)
        checked = result["proof_verified"]
        budget.check()
    except Aborted as exc:
        checked = False
        reason = str(exc)
    if checked and proof["status"] == "solved":
        require(proof["final_domains"] == [[[v] for v in row] for row in matrix],
                "Proven singleton raster differs from repaired matrix")
    return proof, {"status": proof["status"] if checked else "aborted", "proof_verified": checked,
                   "certified": checked and proof["status"] == "solved", "reason": reason,
                   "line_evaluations": budget.lines-lines, "seconds": time.monotonic()-start}


def search(reference_dir, plan, output, cancelled=None):
    require(not output.exists(), "Use a fresh repair output directory")
    start = time.monotonic()
    # Validate the small plan before allocating the search data structures.
    r = exact_keys(plan.get("reference"), {"candidate_id", "manifest_sha256", "variant"})
    raw = load_json(reference_dir / f'{r["variant"]}-candidate.json') if isinstance(r["variant"], str) and \
        r["variant"].isascii() and r["variant"].replace("-", "").replace("_", "").isalnum() else None
    require(raw is not None, "Invalid reference variant path")
    plan = validate_plan(plan, raw)
    config = plan["config"]
    budget = Budget(config["search_seconds"], config["search_lines"], cancelled)
    require(file_hash(reference_dir / "manifest.json") == r["manifest_sha256"], "Reference manifest changed")
    reference, original_proof, reference_checked = inspect_candidate(reference_dir, r["variant"], budget)
    budget.check()
    matrix, design = reference["matrix"], reference["design"]
    colors = tuple(e["id"] for e in design["palette"])
    stage = output.with_name(output.name + ".staging")
    require(not stage.exists(), "Staging directory already exists")
    stage.mkdir(parents=True)
    write_json(stage / "plan.json", plan)
    history, attempts, seen = [], [], set()
    frontier = Frontier(matrix, plan["mask"], config["seed"], original_proof["final_domains"])
    status, reason, selected = "budget_exhausted", "frontier_exhausted", None

    def add(state, parent, edit):
        index = len(history)
        proof, evaluation = evaluate(state, design, stage, f"candidate-{index:03d}", budget)
        score = metrics(proof, state, matrix, colors)
        history.append({"parent": parent, "edit": edit, "matrix_hash": digest(state),
                        "logic_hash": digest(logic_from_matrix(state, design)), "score": score,
                        "evaluation": evaluation})
        seen.add(digest(state))
        frontier.add(state, score, colors)
        return index, evaluation

    try:
        index, evaluation = add(matrix, None, None)
        while True:
            budget.check()
            if evaluation["status"] == "aborted":
                raise Aborted(evaluation["reason"] or "cancelled")
            if evaluation["certified"]:
                selected = index
                status, reason = "found", None
                break
            if len(history) >= config["max_candidates"]:
                reason = "candidate_limit"
                break
            if len(attempts) >= config["max_steps"]:
                reason = "step_limit"
                break
            proposal = frontier.next()
            if proposal is None:
                break
            parent, edit = proposal
            state = frontier.states[parent]["matrix"]
            trial = deepcopy(state)
            trial[edit["y"]][edit["x"]] = edit["after"]
            attempt = {"parent": parent, "edit": edit, "outcome": None, "candidate": None}
            attempts.append(attempt)
            if distance(trial, matrix) > config["max_changes"]:
                attempt["outcome"] = "change_limit"
                continue
            if digest(trial) in seen:
                attempt["outcome"] = "duplicate"
                continue
            trial = apply_edit(state, edit, matrix, plan["mask"], config["max_changes"])
            attempt["outcome"] = "evaluated"
            index, evaluation = add(trial, parent, edit)
            attempt["candidate"] = index
    except (Aborted, KeyboardInterrupt, MemoryError) as exc:
        status, reason = "aborted", str(exc) if isinstance(exc, Aborted) else type(exc).__name__
        if attempts and attempts[-1]["outcome"] == "evaluated" and attempts[-1]["candidate"] is None:
            attempts[-1]["outcome"] = "evaluation_aborted"

    search_seconds = time.monotonic()-start
    final = None
    if status == "found":
        final_budget = Budget(config["final_seconds"], config["final_lines"], cancelled)
        try:
            final_budget.check()
            proof, final = evaluate(frontier.states[selected]["matrix"], design, stage, "final", final_budget)
            if not final["certified"]:
                status, reason = "aborted", final["reason"] or "final_verification_aborted"
        except (Aborted, KeyboardInterrupt, MemoryError) as exc:
            status, reason = "aborted", str(exc) if isinstance(exc, Aborted) else type(exc).__name__
            final = {"status": "aborted", "certified": False, "proof_verified": False, "reason": reason,
                     "line_evaluations": final_budget.lines, "seconds": time.monotonic()-(final_budget.deadline-config["final_seconds"])}
    best = min(range(len(history)), key=lambda i: (rank(history[i]["score"]), i)) if history else None
    chosen = selected if selected is not None else best
    final_matrix = frontier.states[chosen]["matrix"] if chosen is not None else matrix
    changes = [{"y": y, "x": x, "before": matrix[y][x], "after": v}
               for y, row in enumerate(final_matrix) for x, v in enumerate(row) if v != matrix[y][x]]
    core = {"format": FORMAT, "tool": VERSION, "plan_hash": digest(plan), "reference": r,
            "history": [{k: v for k, v in h.items() if k != "evaluation"} for h in history],
            "attempts": attempts, "selected": chosen, "matrix": final_matrix, "changes": changes}
    result = {"status": status, "reason": reason, "certified": status == "found" and bool(final and final["certified"]),
              "candidates": len(history) + sum(a["outcome"] == "evaluation_aborted" for a in attempts),
              "steps": len(attempts), "search_lines": budget.lines,
              "reference_lines": reference_checked["line_evaluations"],
              "search_seconds": search_seconds, "final": final, "total_seconds": time.monotonic()-start,
              "evaluations": [h["evaluation"] for h in history], "editorial_release": False}
    write_json(stage / "result.json", result)
    make_views(stage, matrix, final_matrix, plan["mask"], design, changes, status)
    write_json(stage / "manifest.json", {"format": "picross-repair-manifest-v1", "repair_id": digest(core)})
    files = {p.name: file_hash(p) for p in stage.iterdir() if p.is_file()}
    require(sum(p.stat().st_size for p in stage.iterdir()) <= TOTAL_BYTES, "Repair bundle exceeds 256 MiB")
    write_json(stage / "repair.json", {"id": digest(core), **core, "files": files})
    publish_bundle(stage, output)
    return result


def make_views(directory, before, after, mask, design, changes, status):
    from PIL import Image, ImageDraw
    for name, matrix in (("before", before), ("after", after)):
        raster_image(matrix, design).save(directory / f"{name}.png")
    diff = Image.new("RGB", (design["width"], design["height"]), "white")
    protection = diff.copy()
    for y, row in enumerate(mask):
        for x, protected in enumerate(row):
            if protected:
                protection.putpixel((x, y), (60, 120, 190))
    for e in changes:
        diff.putpixel((e["x"], e["y"]), (210, 0, 120))
    diff.save(directory / "changes.png")
    protection.save(directory / "mask.png")
    scale = min(10, max(4, 400//max(design["width"], design["height"])))
    w, h = design["width"]*scale, design["height"]*scale
    panel = Image.new("RGB", (4*(w+16), h+42), "#eeeeee")
    draw = ImageDraw.Draw(panel)
    for i, name in enumerate(("before", "after", "changes", "mask")):
        draw.text((i*(w+16)+8, 8), name, fill="black")
        with Image.open(directory / f"{name}.png") as im:
            panel.paste(im.resize((w, h), Image.Resampling.NEAREST), (i*(w+16)+8, 30))
    panel.save(directory / "view.png")
    directory.joinpath("index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>RP-5 repair</title>'
        '<style>img{image-rendering:pixelated;min-width:300px}body{font:16px sans-serif}</style>'
        f'<h1>RP-5: {status}</h1><p>No editorial release. Pink: every changed cell. Blue: protected cells.</p>'
        '<img src="view.png" alt="Before, after, all changes, protection mask">'
        '<p><a href="repair.json">Full parent/edit history</a> <a href="result.json">Measured results</a></p>\n',
        encoding="utf-8", newline="\n")


def inspect_repair(directory, reference_dir, budget=None):
    """Reconstruct parents, exact deterministic proposals and each written proof."""
    budget = budget if budget is not None else Budget(600, 1_000_000)
    raw = exact_keys(load_json(directory / "repair.json", HISTORY_BYTES),
                     {"id", "format", "tool", "plan_hash", "reference", "history", "attempts", "selected", "matrix", "changes", "files"})
    require(raw["format"] == FORMAT and raw["tool"] == VERSION, "Unsupported repair bundle")
    require(isinstance(raw["files"], dict) and 1 <= len(raw["files"]) <= 2*MAX_CANDIDATES+12,
            "Invalid repair file count")
    total_bytes = 0
    for name, sha in raw["files"].items():
        require(isinstance(name, str) and Path(name).name == name and "\\" not in name,
                "Unsafe repair filename")
        path = directory / name
        total_bytes += path.stat().st_size
        require(total_bytes <= TOTAL_BYTES, "Repair bundle exceeds 256 MiB")
        require(not path.is_symlink() and path.resolve().parent == directory.resolve() and file_hash(path) == sha,
                "Missing/altered repair file")
    core = {k: v for k, v in raw.items() if k not in ("id", "files")}
    require(raw["id"] == digest(core), "Repair identity mismatch")
    p = load_json(directory / "plan.json", PLAN_BYTES)
    r = exact_keys(raw["reference"], {"candidate_id", "manifest_sha256", "variant"})
    require(file_hash(reference_dir / "manifest.json") == r["manifest_sha256"], "Reference bytes changed")
    reference, original, reference_checked = inspect_candidate(reference_dir, r["variant"], budget)
    p = validate_plan(p, reference)
    require(digest(p) == raw["plan_hash"] and p["reference"] == r, "Plan/reference binding mismatch")
    config, matrix, design = p["config"], reference["matrix"], reference["design"]
    colors = tuple(e["id"] for e in design["palette"])
    history, attempts = raw["history"], raw["attempts"]
    require(isinstance(history, list) and len(history) <= config["max_candidates"] and
            isinstance(attempts, list) and len(attempts) <= config["max_steps"], "Search counters exceed plan")
    result = exact_keys(load_json(directory / "result.json", HISTORY_BYTES),
                        {"status", "reason", "certified", "candidates", "steps", "search_lines", "reference_lines", "search_seconds", "final",
                         "total_seconds", "evaluations", "editorial_release"})
    started = len(history)+sum(a.get("outcome") == "evaluation_aborted" for a in attempts)
    integer(started, 0, config["max_candidates"], "started candidates")
    require(result["candidates"] == started and result["steps"] == len(attempts) and
            result["editorial_release"] is False and isinstance(result["evaluations"], list) and
            len(result["evaluations"]) == len(history), "Inconsistent result counters/release")
    integer(result["search_lines"], 0, config["search_lines"], "cumulative search lines")
    require(result["reference_lines"] == reference_checked["line_evaluations"], "Wrong reference work count")
    for name in ("search_seconds", "total_seconds"):
        require(type(result[name]) in (int, float) and math.isfinite(result[name]) and result[name] >= 0,
                "Invalid measured time")
    frontier = Frontier(matrix, p["mask"], config["seed"], original["final_domains"])
    seen, fresh = set(), []
    expected_files = {"plan.json", "result.json", "manifest.json", "before.png", "after.png", "changes.png", "mask.png", "view.png", "index.html"}
    require(load_json(directory / "manifest.json") == {"format": "picross-repair-manifest-v1", "repair_id": raw["id"]},
            "Wrong repair manifest; this is not an image import")

    def check_candidate(i, state, parent, edit):
        h = exact_keys(history[i], {"parent", "edit", "matrix_hash", "logic_hash", "score"})
        require(h["parent"] == parent and h["edit"] == edit and h["matrix_hash"] == digest(state),
                "Wrong candidate parent/edit/matrix")
        wire = logic_from_matrix(state, design)
        require(h["logic_hash"] == digest(wire), "Stale candidate logic")
        prefix = f"candidate-{i:03d}"
        expected_files.update((f"{prefix}-logic.json", f"{prefix}-proof.json"))
        require(load_json(directory / f"{prefix}-logic.json") == wire, "Clues differ from reconstructed candidate")
        puzzle = validate_logic(wire)
        proof = load_json(directory / f"{prefix}-proof.json", puzzle.proof_byte_limit)
        checked = verify(puzzle, proof, budget)
        require(not checked["certified"] or proof["final_domains"] == [[[v] for v in row] for row in state],
                "Proof belongs to another final matrix")
        score = metrics(proof, state, matrix, colors)
        require(h["score"] == score, "Forged logical/visual score")
        e = exact_keys(result["evaluations"][i], {"status", "proof_verified", "certified", "reason", "line_evaluations", "seconds"})
        require(type(e["certified"]) is bool and type(e["proof_verified"]) is bool and
                e["certified"] == (e["proof_verified"] and checked["certified"]), "Forged original certification")
        require((e["proof_verified"] and e["status"] == checked["status"] and e["reason"] == proof["reason"]) or
                (not e["proof_verified"] and e["status"] == "aborted" and e["reason"] in
                 ("time_limit", "work_limit", "cancelled")), "Inconsistent evaluation status")
        integer(e["line_evaluations"], 0, config["search_lines"], "evaluation lines")
        require(type(e["seconds"]) in (int, float) and math.isfinite(e["seconds"]) and e["seconds"] >= 0,
                "Invalid evaluation time")
        require(e["status"] != "aborted" or i == len(history)-1 and result["status"] == "aborted",
                "Search continued after an aborted evaluation")
        fresh.append(checked)
        seen.add(digest(state))
        frontier.add(state, score, colors)

    if history:
        check_candidate(0, matrix, None, None)
    next_candidate = 1
    for n, a in enumerate(attempts):
        require(not any(e["certified"] for e in result["evaluations"][:next_candidate]),
                "Search continued after a certified candidate")
        a = exact_keys(a, {"parent", "edit", "outcome", "candidate"})
        proposal = frontier.next()
        require(proposal is not None and proposal == (a["parent"], a["edit"]), "Altered deterministic proposal history")
        state = deepcopy(frontier.states[a["parent"]]["matrix"])
        state[a["edit"]["y"]][a["edit"]["x"]] = a["edit"]["after"]
        if distance(state, matrix) > config["max_changes"]:
            expected = "change_limit"
        elif digest(state) in seen:
            expected = "duplicate"
        else:
            expected = "evaluated"
        if a["outcome"] == "evaluation_aborted":
            require(expected == "evaluated" and n == len(attempts)-1 and a["candidate"] is None and
                    result["status"] == "aborted", "Invalid interrupted evaluation")
            continue
        require(a["outcome"] == expected, "Forged rejected/duplicate proposal")
        if expected == "evaluated":
            require(a["candidate"] == next_candidate and next_candidate < len(history), "Missing/reordered candidate")
            state = apply_edit(frontier.states[a["parent"]]["matrix"], a["edit"], matrix, p["mask"], config["max_changes"])
            check_candidate(next_candidate, state, a["parent"], a["edit"])
            next_candidate += 1
        else:
            require(a["candidate"] is None, "Rejected proposal cannot be evaluated")
    require(next_candidate == len(history) if history else not attempts, "Unbound candidates")
    require(result["search_lines"] >= result["reference_lines"] + sum(e["line_evaluations"] for e in result["evaluations"]),
            "Cumulative work reset between candidates")
    chosen = raw["selected"]
    if history:
        integer(chosen, 0, len(history)-1, "selected candidate")
        end = frontier.states[chosen]["matrix"]
        solved = [i for i, e in enumerate(result["evaluations"]) if e["certified"]]
        expected_chosen = solved[0] if solved else min(range(len(history)), key=lambda i: (rank(history[i]["score"]), i))
        require(chosen == expected_chosen, "Wrong selected/best candidate")
    else:
        require(chosen is None and result["status"] == "aborted", "Empty search must be aborted")
        end = matrix
    require(raw["matrix"] == end and distance(end, matrix) <= config["max_changes"], "Wrong output matrix")
    changes = [{"y": y, "x": x, "before": matrix[y][x], "after": v}
               for y, row in enumerate(end) for x, v in enumerate(row) if v != matrix[y][x]]
    require(raw["changes"] == changes and all(not p["mask"][e["y"]][e["x"]] for e in changes),
            "Incomplete changes view or protected output")
    for name, state in (("before", matrix), ("after", end)):
        from PIL import Image
        with Image.open(directory / f"{name}.png") as im:
            require(im.mode == "RGB" and im.size == (design["width"], design["height"]) and
                    im.tobytes() == raster_image(state, design).tobytes(), "Wrong comparison image")
    # Rebuild every display, including protection/diff pixels, rather than trust hashes alone.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        make_views(Path(tmp), matrix, end, p["mask"], design, changes, result["status"])
        for name in ("changes.png", "mask.png", "view.png"):
            with Image.open(directory / name) as a, Image.open(Path(tmp) / name) as b:
                require(a.mode == b.mode and a.size == b.size and a.tobytes() == b.tobytes(), "Altered change/mask display")
    certified = False
    if (directory / "final-proof.json").exists():
        expected_files.update(("final-logic.json", "final-proof.json"))
        wire = logic_from_matrix(end, design)
        require(load_json(directory / "final-logic.json") == wire, "Stale final logic")
        puzzle = validate_logic(wire)
        proof = load_json(directory / "final-proof.json", puzzle.proof_byte_limit)
        final = verify(puzzle, proof, budget)
        require(not final["certified"] or proof["final_domains"] == [[[v] for v in row] for row in end],
                "Final proof matrix mismatch")
        certified = final["certified"]
        recorded = exact_keys(result["final"], {"status", "certified", "proof_verified", "reason", "line_evaluations", "seconds"})
        integer(recorded["line_evaluations"], 0, config["final_lines"], "final cumulative lines")
        require(type(recorded["seconds"]) in (int, float) and math.isfinite(recorded["seconds"]) and recorded["seconds"] >= 0,
                "Invalid final time")
        require(type(recorded["certified"]) is bool and type(recorded["proof_verified"]) is bool and
                recorded["certified"] == (recorded["proof_verified"] and certified) and
                ((recorded["proof_verified"] and recorded["status"] == final["status"] and recorded["reason"] == proof["reason"]) or
                 (not recorded["proof_verified"] and recorded["status"] == "aborted" and recorded["reason"] is not None)),
                "Forged final verification status")
    require(result["status"] in ("found", "budget_exhausted", "aborted") and type(result["certified"]) is bool,
            "Invalid repair result")
    require(result["certified"] == (result["status"] == "found") and
            (not result["certified"] or certified and result["final"] and result["final"]["certified"] is True and
             result["final"]["proof_verified"] is True and result["reason"] is None), "No completed independent final certificate")
    if result["status"] == "budget_exhausted":
        require(not any(e["certified"] for e in result["evaluations"]) and result["final"] is None,
                "Unfinished search cannot have a final certificate")
        reason = "candidate_limit" if len(history) == config["max_candidates"] else \
            "step_limit" if len(attempts) == config["max_steps"] else "frontier_exhausted"
        require(result["reason"] == reason and (reason != "frontier_exhausted" or frontier.next() is None),
                "Search falsely claims budget/frontier exhaustion")
    elif result["status"] == "aborted":
        require(result["reason"] in ("time_limit", "work_limit", "cancelled", "KeyboardInterrupt", "MemoryError", "final_verification_aborted"),
                "Missing supported abort reason")
    require(set(raw["files"]) == expected_files, "Incomplete/excessive repair file bindings")
    return {"accepted": True, "repair_id": raw["id"], "certified": result["certified"],
            "status": result["status"], "candidates": started, "steps": len(attempts),
            "reference_id": reference["id"], "matrix_hash": digest(end), "fresh_candidates": fresh,
            "editorial_release": False}


def main(argv=None):
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("search")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("--bundle", type=Path, required=True)
    check.add_argument("--report", type=Path)
    for p in (run, check):
        p.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "search":
            result = search(args.reference, load_json(args.plan, PLAN_BYTES), args.output_dir)
            code = 4 if result["status"] == "aborted" else 0
        else:
            result = inspect_repair(args.bundle, args.reference)
            if args.report:
                write_json(args.report, result)
            code = 0
    except (InvalidInput, InvalidProof, Aborted, OSError, ValueError, RuntimeError, MemoryError, KeyboardInterrupt) as exc:
        code = 2 if isinstance(exc, InvalidInput) else 3 if isinstance(exc, InvalidProof) else \
            4 if isinstance(exc, (Aborted, MemoryError, KeyboardInterrupt)) else 5
        result = {"status": {2: "invalid_input", 3: "invalid_proof", 4: "aborted", 5: "technical_error"}[code],
                  "certified": False, "error": type(exc).__name__, "message": str(exc)}
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
