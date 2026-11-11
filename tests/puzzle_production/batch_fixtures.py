"""Small, ephemeral BA-A inputs; every statement is explicitly TEST ONLY.

These generators use the actual import/background contracts. They never read a
catalog puzzle, write the repository, publish a package, or create an approval
on behalf of a real owner. The one-time probe and the small regressions share
the same reproducible sources instead of keeping generated PNGs or ZIPs.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image

from tools.puzzle_production import background_assets, images
from tools.puzzle_production import authoring_build_contract as build_contract
from tools.puzzle_production.contract import Puzzle, load_json
from tests.puzzle_production.background_fixtures import BackgroundFixture


ROOT = Path(__file__).resolve().parents[2]
VARIANT = "area-128"
METHOD = "picross-difficulty-0.4"
LOGIC_LIMITS = {"seconds": 10, "max_lines": 1000,
                "max_pair_work": 10000, "max_pair_records": 1000}
ANALYSIS_LIMITS = {**LOGIC_LIMITS, "max_rule_work": 100000, "max_waves": 1000}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def checksum(raw):
    return hashlib.sha256(raw).hexdigest()


def source_ref(root, name):
    raw = (Path(root) / name).read_bytes()
    return {"kind": "source", "file": name, "sha256": checksum(raw), "bytes": len(raw)}


def domain_ref(ref):
    return {key: value for key, value in ref.items() if key != "kind"}


def put(root, name, value):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else encoded(value))
    return source_ref(root, name)


def output_ref(stage, slot, candidate_id=None):
    return {"kind": "output", "stage": stage, "slot": slot, "candidate_id": candidate_id}


def stamps(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in Path(root).rglob("*") if p.is_file()}


def stage_result(report, job_id, stage_id):
    state = next(s for j in report["jobs"] if j["job_id"] == job_id
                 for s in j["stages"] if s["stage_id"] == stage_id)
    attempt = next((a for a in report["attempts"] if a["number"] == state["attempt"]), None)
    return state, attempt


def artifact_path(fixture, ref):
    return (fixture.source if ref["root"] == "source" else fixture.work) / ref["file"]


class BatchFixture:
    def __init__(self, root, batch_id="ba-a-synthetic"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.source = self.root / "source"
        self.work = self.root / "work"
        self.source.mkdir()
        self.work.mkdir()
        self.repo = ROOT
        self.data = {}
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                         text=True).strip()
        self.plan = {"format": "picross-batch-plan-v1", "batch_id": batch_id,
                     "revision": 1, "previous_plan_sha256": None,
                     "source_commit": commit, "jobs": []}
        self.path = self.root / "plan-initial.json"

    def rulebook(self, name, version):
        # BA-A remains a separate local generation; never relabel current 0.8 rules.
        raw = ("**Version 0.6.0 · Dokumentrevision 1 · TEST ONLY**\n"
               "Synthetic BA-A snapshot; not a production rulebook.\n").encode("utf-8") if version == "0.6.0" else (
                   ROOT / "docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md").read_bytes()
        revision = int(re.search(r"\*\*Version " + re.escape(version) +
                                 r" · Dokumentrevision (\d+) ·", raw.decode()).group(1))
        return {"version": version, "document_revision": revision,
                "snapshot": put(self.source, name, raw)}

    def add_job(self, name, *, pattern="solved", background=False):
        prefix = "jobs/" + name
        directory = self.source / prefix
        directory.mkdir(parents=True)
        identifier = "pz-ba-a-" + name
        rulebook = self.rulebook(prefix + "/rulebook.md", "0.6.0")
        design = load_json(ROOT / "tests/puzzle_production/fixtures/image-design.json")
        matrix = ([["ink", "empty"], ["empty", "ink"]] if pattern == "stalled" else
                  [["empty"] * 4, ["empty"] * 4,
                   ["empty", "ink", "ink", "empty"], ["ink", "empty", "empty", "ink"]] if pattern == "paired"
                  else [["ink", "ink"], ["empty", "empty"]])
        height, width = len(matrix), len(matrix[0])
        design.update(source_id="test-ba-a-" + name, width=width, height=height,
                      crop=[0, 0, width, height], fit="exact", mode="mono",
                      palette=[{"id": "ink", "rgb": "#000000"}],
                      variants=[{"id": VARIANT, "method": "area", "threshold": 128}],
                      briefing="TEST ONLY tiny synthetic BA-A input; no catalog motif.")
        motif = Image.new("RGB", (width, height), "white")
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value == "ink":
                    motif.putpixel((x, y), (0, 0, 0))
        motif.save(directory / "motif.png")
        Image.new("RGB", (3, 2), (80, 150, 90)).save(directory / "reveal.png")
        motif_ref = source_ref(self.source, prefix + "/motif.png")
        reveal_ref = source_ref(self.source, prefix + "/reveal.png")
        put(self.source, prefix + "/evidence.txt",
            b"TEST ONLY synthetic development statements; never an owner approval.\n")
        approved = {"width": width, "height": height, "mode": "mono", "foreground_colors": 1,
                    "fit": "exact", "actual_crop": [0, 0, width, height], "method": "area"}
        for kind, ref in (("motif", motif_ref), ("reveal", reveal_ref)):
            approval = {"type": "human_" + kind + "_approval", "file": kind + ".png",
                        "sha256": ref["sha256"], "revision": "test-only-1",
                        "actor": "TEST ONLY synthetic actor", "timestamp_utc": "2026-11-10T00:00:00Z",
                        "statement": "TEST ONLY synthetic development evidence, not a human decision.",
                        "evidence": "evidence.txt"}
            provenance = {"puzzle_id": identifier, "file": kind + ".png", "sha256": ref["sha256"],
                          "author": "BA-A synthetic fixture code", "usage_basis": "Repository-owned test pixels"}
            if kind == "motif":
                approval.update(derived_from_reveal_sha256=reveal_ref["sha256"], parameters=approved)
                provenance["derived_from"] = {"file": "reveal.png", "sha256": reveal_ref["sha256"]}
            put(self.source, prefix + "/" + kind + "-approval.json", approval)
            put(self.source, prefix + "/" + kind + ".provenance.json", provenance)
        handoff = {"format": "picross-authoring-handoff-v2", "puzzle_id": identifier, "revision": "r01",
                   "repo_commit": self.plan["source_commit"], "state": "raster_review", "inventory": None,
                   "rulebook": {"version": "0.6.0", "file": "rulebook.md", "sha256": rulebook["snapshot"]["sha256"]},
                   "brief": "evidence.txt", "approved_parameters": [approved],
                   "reveal": {"file": "reveal.png", "sha256": reveal_ref["sha256"], "approval": "reveal-approval.json"},
                   "motif": {"file": "motif.png", "sha256": motif_ref["sha256"], "approval": "motif-approval.json",
                             "derived_from_reveal_sha256": reveal_ref["sha256"]},
                   "candidate": None, "repair": None,
                   "gates": {"reveal_approval": "pass", "motif": "pass", "final_editorial": "pending", "target_export": "blocked"},
                   "blockers": [], "test_only": True,
                   "next_action": "TEST ONLY run the explicitly bounded technical fixture stages.",
                   "authorization": "TEST ONLY synthetic development input; no real production authorized."}
        params = put(self.source, prefix + "/parameters.json", handoff)
        wire = (Puzzle(2, 2, ((2,), ()), ((), ())).to_wire() if pattern == "contradiction"
                else images.logic_from_matrix(matrix, design))
        data = {"prefix": prefix, "design": put(self.source, prefix + "/design.json", design),
                "matrix": put(self.source, prefix + "/matrix.json", matrix),
                "logic": put(self.source, prefix + "/logic.json", wire), "image": motif_ref,
                "handoff": handoff}
        job = {"job_id": name, "puzzle_id": identifier, "revision": "r01",
               "background_revision": "bg01" if background else None,
               "rulebook": self.rulebook(prefix + "/background-rulebook.md", "0.7.0") if background else rulebook,
               "decisions": {"motif": source_ref(self.source, prefix + "/motif-approval.json"),
                             "parameters": params, "repair": None, "background": None}, "stages": []}
        self.data[name] = data
        self.plan["jobs"].append(job)
        return job

    def stage(self, job, stage_id, kind, operation, inputs, parameters=None, *, limits=None,
              produce_attempts=4, revalidate_attempts=12):
        from tools.puzzle_production import batch_operations as operations
        readonly = operation in ("verify", "import")
        budget = (ANALYSIS_LIMITS if kind == "difficulty" else
                  {"seconds": 300} if kind in ("background", "authoring_build") else LOGIC_LIMITS)
        value = {"stage_id": stage_id, "kind": kind, "operation": operation,
                 "inputs": deepcopy(inputs), "parameters": deepcopy(parameters or {}),
                 "limits": deepcopy(limits or {"produce": None if readonly else budget, "revalidate": budget}),
                 "max_attempts": {"produce": 0 if readonly else produce_attempts, "revalidate": revalidate_attempts},
                 "tool_binding": operations.expected_tool_binding(kind, operation, self.repo)}
        job["stages"].append(value)
        return value

    def image_stage(self, job, stage_id="import"):
        data = self.data[job["job_id"]]
        return self.stage(job, stage_id, "image_import", "produce",
                          {"image": data["image"], "design": data["design"], "approval": job["decisions"]["motif"]},
                          {"profile": "full-line-mono", "candidates": [VARIANT]})

    def solve_stage(self, job, stage_id="solve", logic=None, **kwargs):
        return self.stage(job, stage_id, "logic_certify", "solve",
                          {"logic": logic or self.data[job["job_id"]]["logic"]},
                          {"profile": "full-line-mono", "order": "rows-first"}, **kwargs)

    def difficulty_stage(self, job, stage_id="difficulty", producer="import", solver="solve"):
        return self.stage(job, stage_id, "difficulty", "analyze",
                          {"design": output_ref(producer, "design", VARIANT),
                           "matrix": output_ref(producer, "matrix", VARIANT),
                           "logic": output_ref(solver, "logic"), "proof": output_ref(solver, "proof"), "baseline": None,
                           "r4_proof": None, "r4_baseline": None},
                          {"puzzle_id": job["puzzle_id"], "runtime_revision": 1,
                           "production_mode": "mono", "method": METHOD})

    def paired_inputs(self, job):
        """Separate real production and normalized-runtime R4 certificates."""
        from tools.puzzle_production import catalog_analysis, catalog_rating, certification
        from tools.puzzle_production.contract import Budget, validate_logic
        from tools.puzzle_production.solver import solve
        from tools.puzzle_production.verifier import verify
        data = self.data[job["job_id"]]
        prefix = data["prefix"] + "/paired"
        directory = self.source / prefix
        directory.mkdir()
        design, matrix, logic = (load_json(self.source / data[key]["file"])
                                 for key in ("design", "matrix", "logic"))
        original = validate_logic(logic)
        config = certification.configuration(original, "paired-lines-mono")
        _, checked = certification.produce(original, directory, "original-", config,
                                            Budget(seconds=10, max_lines=10000))
        assert checked["certified"] and checked["assessment"]["r4_required"]
        candidate = catalog_analysis.candidate(design, matrix, logic, job["puzzle_id"], 1)
        candidate_ref = put(self.source, prefix + "/candidate.json", candidate)
        runtime = catalog_rating.definition((self.source / candidate_ref["file"]).read_bytes())[1]
        baseline = solve(runtime, Budget(seconds=10, max_lines=10000))
        proof = solve(runtime, Budget(seconds=10, max_lines=10000), profile="paired-lines-color")
        assert baseline["status"] == "stalled" and proof["status"] == "solved"
        assert verify(runtime, baseline)["proof_verified"] and verify(runtime, proof)["certified"]
        return {"design": data["design"], "matrix": data["matrix"], "logic": data["logic"],
                "proof": source_ref(self.source, prefix + "/original-proof.json"),
                "baseline": source_ref(self.source, prefix + "/original-baseline-proof.json"),
                "r4_proof": put(self.source, prefix + "/runtime-proof.json", proof),
                "r4_baseline": put(self.source, prefix + "/runtime-baseline.json", baseline)}

    def background(self, job, *, none=False, offered=False, revision="bg01", color=None):
        prefix = self.data[job["job_id"]]["prefix"] + "/background/" + revision
        image = None
        if color is not None:
            from tests.puzzle_production.background_fixtures import pixels
            image = pixels(color=color)
        with tempfile.TemporaryDirectory(prefix="ba-a-bg-source-") as temporary:
            fixture = BackgroundFixture(Path(temporary) / "fixture", background_assets.describe(), none=none, image=image)
            fixture.manifest.update(puzzle_id=job["puzzle_id"], job_id=job["job_id"], revision=revision)
            fixture.decision.update(puzzle_id=job["puzzle_id"], job_id=job["job_id"], background_revision=revision,
                                    revision="d" + revision[2:])
            # HP-W2 references are relative to its explicit source root. Each
            # synthetic job therefore gets unique real paths under the batch root.
            def rebase(value):
                if isinstance(value, dict):
                    return {k: prefix + "/" + v if k == "file" and isinstance(v, str)
                            else rebase(v) for k, v in value.items()}
                if isinstance(value, list):
                    return [rebase(v) for v in value]
                return value
            for path in fixture.source.rglob("*"):
                if path.is_file() and not path.relative_to(fixture.source).parts[0] in ("work", "decisions"):
                    put(self.source, prefix + "/" + path.relative_to(fixture.source).as_posix(), path.read_bytes())
            manifest = rebase(fixture.manifest)
            manifest_ref = put(self.source, prefix + "/work/" + revision + ".json", manifest)
            if offered:
                self.data[job["job_id"]]["background_offer"] = manifest_ref
                job["decisions"]["background"] = None
                return None
            decision = rebase(fixture.decision)
            decision["manifest"] = domain_ref(manifest_ref)
            decision_ref = put(self.source, prefix + "/decisions/" + decision["revision"] + ".json", decision)
            request = deepcopy(fixture.request)
            request.update(manifest=domain_ref(manifest_ref), decision=domain_ref(decision_ref),
                           source=deepcopy(decision["original"]), output="derived/" + revision)
            request_ref = put(self.source, prefix + "/request.json", request)
        job["decisions"]["background"] = decision_ref
        job["background_revision"] = revision
        self.data[job["job_id"]]["background"] = {"prefix": prefix, "request": request,
                                                  "request_ref": request_ref, "manifest": manifest_ref,
                                                  "decision": decision_ref}
        return request_ref

    def repair_reference(self, job):
        data = self.data[job["job_id"]]
        prefix = data["prefix"]
        target = self.source / prefix / "reference"
        images.import_image(self.source / data["image"]["file"], self.source / data["design"]["file"], target,
                            seconds=10, max_lines=1000)
        candidate, _, checked = images.inspect_candidate(target, VARIANT)
        assert checked["status"] == "stalled", "repair fixture must genuinely start stalled"
        plan = {"format": "picross-repair-plan-v1", "tool": "rp5-single-cell-1",
                "reference": {"candidate_id": candidate["id"], "manifest_sha256": checksum((target / "manifest.json").read_bytes()),
                              "variant": VARIANT}, "mask": [[True, False], [True, True]],
                "rationale": "TEST ONLY protect the original diagonal and one empty cell.",
                "config": {"max_changes": 1, "max_steps": 32, "max_candidates": 8,
                           "search_seconds": 10, "final_seconds": 10, "search_lines": 1000,
                           "final_lines": 1000, "seed": 39, "operators": ["single-cell"], "order": "seeded-frontier-v1"}}
        plan_ref = put(self.source, prefix + "/repair-plan.json", plan)
        job["decisions"]["repair"] = plan_ref
        return source_ref(self.source, prefix + "/reference/manifest.json"), plan_ref, plan

    def builder_request(self, job, *, finding=None, background_png=None):
        prefix = "build-requests/" + job["job_id"]
        version = "0.7.0" if finding is not None else "0.6.0"
        rulebook = self.rulebook(prefix + "/rulebook.md", version)
        put(self.source, prefix + "/brief.txt", b"TEST ONLY explicit later local package request.\n")
        handoff = {"format": "picross-authoring-handoff-v3" if finding is not None else "picross-authoring-handoff-v2",
                   "puzzle_id": job["puzzle_id"], "revision": job["revision"], "repo_commit": self.plan["source_commit"],
                   "state": "brief_ready", "inventory": None, "brief": "brief.txt", "approved_parameters": [],
                   "reveal": None, "motif": None, "candidate": None, "repair": None,
                   "rulebook": {"version": version, "file": "rulebook.md", "sha256": rulebook["snapshot"]["sha256"]},
                   "gates": {"reveal_approval": "pending", "motif": "pending", "final_editorial": "pending", "target_export": "blocked"},
                   "blockers": [], "test_only": True,
                   "next_action": "TEST ONLY retain the still-open owner decisions; do not publish.",
                   "authorization": "TEST ONLY synthetic local build request, no real production or export."}
        files = []
        def member(path, source):
            ref = source_ref(self.source, source)
            files.append({"path": path, "source": source, "sha256": ref["sha256"], "bytes": ref["bytes"]})
        member("brief.txt", prefix + "/brief.txt")
        member("rulebook.md", prefix + "/rulebook.md")
        if finding is not None:
            bg = self.data[job["job_id"]]["background"]
            for source in sorted((self.source / bg["prefix"]).rglob("*")):
                if source.is_file() and source.name != "request.json":
                    relative = source.relative_to(self.source).as_posix()
                    member("background/" + relative, relative)
            for path in (finding, background_png):
                if path is not None:
                    name = "outputs/bg01/" + Path(path).name
                    put(self.source, prefix + "/" + name, Path(path).read_bytes())
                    member(name, prefix + "/" + name)
            handoff["background"] = {
                "manifest": {"storage": "package", "root": "background", "ref": domain_ref(bg["manifest"])},
                "decision": {"storage": "package", "root": "background", "ref": domain_ref(bg["decision"])},
                "derivation": {"storage": "package", "root": "outputs", "ref": {
                    **domain_ref(source_ref(self.source, prefix + "/outputs/bg01/derivation.json")),
                    "file": "bg01/derivation.json"}}, "history": None}
            handoff["gates"] = {key: handoff["gates"].get(key, "pending") for key in build_contract.BACKGROUND_GATES}
            handoff["gate_evidence"] = {key: None for key in build_contract.BACKGROUND_GATES}
            for gate, field in (("background_choice", "decision"), ("background_asset", "derivation")):
                # A selected synthetic image has a genuine technical derivative,
                # but this fixture intentionally has no Q-HG content reviews.
                # Only explicit none is ready without those visual judgments.
                if gate == "background_asset" and load_json(self.source / bg["decision"]["file"])["outcome"] != "none":
                    continue
                handoff["gates"][gate] = "pass"
                stored = handoff["background"][field]
                handoff["gate_evidence"][gate] = stored["root"] + "/" + stored["ref"]["file"]
        request = {"format": build_contract.BACKGROUND_FORMAT if finding is not None else build_contract.FORMAT,
                   "handoff": handoff, "document_revision": rulebook["document_revision"], "files": files,
                   "target": "local", "category_id": None, "reveal_options": [], "external": {}}
        return put(self.source, prefix + "/request.json", request)

    def write_plan(self, name=None):
        if name is not None:
            self.path = self.root / name
        self.path.write_bytes(encoded(self.plan))
        return self.path

    def successor(self, name="plan-resume.json"):
        self.plan["previous_plan_sha256"] = checksum(self.path.read_bytes())
        self.plan["revision"] += 1
        return self.write_plan(name)


def walkthrough_fixture(root):
    fixture = BatchFixture(root, "ba-a-t01")
    selected = fixture.add_job("selected", background=True)
    fixture.image_stage(selected)
    fixture.solve_stage(selected, logic=output_ref("import", "logic", VARIANT))
    fixture.difficulty_stage(selected)
    request = fixture.background(selected)
    fixture.stage(selected, "background", "background", "derive", {"request": request})
    none = fixture.add_job("none", background=True)
    fixture.stage(none, "background", "background", "derive", {"request": fixture.background(none, none=True)})
    fixture.stage(none, "build", "authoring_build", "build", {"request": None})
    waiting = fixture.add_job("waiting", background=True)
    fixture.solve_stage(waiting)
    fixture.background(waiting, offered=True)
    fixture.stage(waiting, "background", "background", "derive", {"request": None})
    fixture.write_plan()
    return fixture
