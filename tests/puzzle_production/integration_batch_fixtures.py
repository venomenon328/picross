"""Tiny real BA-B inputs, shared by selected tests and the one-time CLI probe.

All pixels, judgments and integration orders are explicitly synthetic/test_only.
The fixture prepares actual approved native ZIPs and checked 0.4 difficulty
inputs before BA-B starts. No real catalog content is copied or analyzed, and
the integration runner never creates these decisions, requests or ratings.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from tests.puzzle_production.background_change_fixtures import create_work
from tests.puzzle_production.test_background_content import BackgroundContentTests
from tools.puzzle_production import catalog_analysis, catalog_background as background
from tools.puzzle_production import catalog_method, content_registry, target_adapter
from tools.puzzle_production.contract import write_json
from tools.puzzle_production.za1_fixtures import ROOT, isolated_checkout, make, seal


METHOD = "picross-difficulty-0.4"
REGISTER_BUDGETS = {"export_seconds": 300, "plan_seconds": 300,
                    "reconcile_seconds": 300, "publication_seconds": 1800,
                    "recovery_seconds": 1800}
BACKGROUND_BUDGETS = {"store_seconds": 300, "plan_seconds": 300,
                      "adopt_seconds": 300, "recovery_seconds": 300,
                      "reconcile_seconds": 300}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def checksum(raw):
    return hashlib.sha256(raw).hexdigest()


def file_ref(root, name):
    raw = (Path(root) / name).read_bytes()
    return {"file": name, "sha256": checksum(raw), "bytes": len(raw)}


def directory_ref(root, name):
    directory = Path(root) / name
    return {"directory": name,
            "files": [file_ref(directory, p.relative_to(directory).as_posix())
                      for p in sorted(directory.rglob("*")) if p.is_file()]}


def stamps(root, *, control=True):
    """Actual bytes and nanosecond mtimes, not an inferred no-write claim."""
    root = Path(root)
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file()
            and (control or ".picross-integration-batches" not in p.relative_to(root).parts)}


def put(root, name, value):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else encoded(value))
    return file_ref(root, name)


class IntegrationFixture:
    """One existing background target plus selected/none registration inputs."""

    def __init__(self, root, *, batch_id="ba-b-synthetic"):
        self.root = Path(root).absolute()
        self.root.mkdir(parents=True, exist_ok=True)
        self.source = self.root / "source"
        self.source.mkdir()
        self.target = isolated_checkout(self.root / "target")
        # The native store uses a verified Git root only for its cooperative
        # authoring lock. This creates an empty own test repository, not a copy
        # or mutation of the product repository and not a runner Git operation.
        subprocess.run(["git", "init", "--quiet", str(self.target)], check=True,
                       capture_output=True, timeout=15)
        self.work = self.root / "work"  # run deliberately requires a new root.
        self.repo = ROOT
        self.path = self.root / "batch-plan.json"
        self.preparation = self.root / "preparation"
        self.preparation.mkdir()
        self.packages = {}
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                               text=True).strip()
        self.plan = {"format": "picross-integration-batch-plan-v1", "batch_id": batch_id,
                     "revision": 1, "previous_plan_sha256": None,
                     "source_commit": self.commit, "jobs": []}
        self.case = BackgroundContentTests()
        self.case.root = self.preparation
        self.case.counter = 0
        write_json(self.target / background.CAPABILITY, {
            "format": background.CAPABILITY_FORMAT,
            "runtime_format": background.RUNTIME_FORMAT,
            "profile_id": "picross-background-png2304-v1", "enabled": True})
        # isolated_checkout intentionally retains the historical implicit 0.3
        # default. Activate 0.4 only in this own test catalog, before the runner.
        activation = catalog_method.plan(self.target, catalog_method.OLD, METHOD,
                                          catalog_method.method_hash(METHOD))
        self.activation = catalog_method.adopt(self.target, activation)
        existing = self.package("existing", "selected")
        self.existing_registration = content_registry.registration(
            existing["export"], self.target, apply=True, difficulty=existing["difficulty_path"])
        self.add_register("selected", "selected")
        self.add_background("background")
        self.add_register("none", "none")
        self.save()

    def rulebook(self, name):
        raw = (ROOT / "docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md").read_bytes()
        match = re.search(r"\*\*Version 0\.7\.0 · Dokumentrevision (\d+) ·", raw.decode("utf-8"))
        if match is None:
            raise RuntimeError("Current opt-in rulebook has no actual version/revision")
        return {"version": "0.7.0", "document_revision": int(match.group(1)),
                "snapshot": put(self.source, name, raw)}

    def package(self, name, choice):
        identifier = "pz-ba-b-" + name
        directory = make(self.preparation / (name + "-package"), identifier, 3, 3, "mono")
        _, handoff = self.case.background(directory, choice=choice, ready=True, state="content_ready")
        rulebook = self.rulebook(name + "/rulebook.md")
        # This is new fixture construction, before its original ZIP and final
        # approval are sealed. Never relabel a previously sealed source.
        (directory / "rulebook.md").write_bytes((self.source / rulebook["snapshot"]["file"]).read_bytes())
        handoff["repo_commit"] = self.commit
        handoff["rulebook"]["sha256"] = rulebook["snapshot"]["sha256"]
        seal(directory, handoff)
        archive = self.case.archive(directory, name + ".zip")
        approval = self.case.approval(directory, archive, name=name + "-approval.json")
        prefix = self.source / name
        shutil.copy2(archive, prefix / "original.zip")
        shutil.copy2(approval, prefix / "approval.json")
        shutil.copy2(directory / "handoff.json", prefix / "handoff.json")
        parameters = {"name": "TEST ONLY BA-B " + name, "runtime_revision": 1,
                      "stem": "ba_b_" + name, "save_slot": "ba_b_" + name,
                      "category_id": "voegel", "allow_background": True,
                      "rebind_difficulty": False}
        export = self.preparation / (name + "-export")
        manifest = target_adapter.export(
            prefix / "original.zip", export, name=parameters["name"],
            revision=parameters["runtime_revision"], stem=parameters["stem"],
            save_slot=parameters["save_slot"], category_id=parameters["category_id"],
            categories_path=self.target / "content/categories.json",
            approval_path=prefix / "approval.json", allow_background=True)
        checked = catalog_analysis.analyze_single(
            export / manifest["definition"], self.preparation / (name + "-analysis"),
            production_mode="mono", method=METHOD)
        difficulty = put(self.source, name + "/checked-difficulty.json", checked)
        data = {"id": identifier, "revision": handoff["revision"], "choice": choice,
                "rulebook": rulebook, "parameters": parameters,
                "package": file_ref(self.source, name + "/original.zip"),
                "handoff": file_ref(self.source, name + "/handoff.json"),
                "approval": file_ref(self.source, name + "/approval.json"),
                "difficulty": difficulty, "difficulty_path": self.source / difficulty["file"],
                "export": export}
        self.packages[name] = data
        return data

    def add_register(self, name, choice):
        data = self.package(name, choice)
        statement = ("TEST ONLY: Integrate the synthetic " + data["id"] + " revision "
                     + data["revision"] + ". This constructed statement is not an owner approval.\n")
        evidence = put(self.source, name + "/integration-statement.txt", statement.encode("utf-8"))
        order = {"format": "picross-integration-order-v1", "operation": "register",
                 "puzzle_id": data["id"], "revision": data["revision"],
                 "actor": "TEST ONLY BA-B fixture", "timestamp_utc": "2026-11-11T00:00:00Z",
                 "statement": statement.strip(), "evidence": evidence, "test_only": True}
        job = {"job_id": name, "puzzle_id": data["id"], "revision": data["revision"],
               "operation": "register", "rulebook": deepcopy(data["rulebook"]),
               "authorization": put(self.source, name + "/integration-order.json", order),
               "inputs": {**{key: deepcopy(data[key]) for key in ("package", "handoff", "approval", "difficulty")},
                          "record": None, "manual_authorization": None, "palette_exception": None,
                          "external": None},
               "parameters": deepcopy(data["parameters"]), "budgets": deepcopy(REGISTER_BUDGETS),
               "max_attempts": {phase: 12 for phase in ("export", "plan", "apply", "reconcile")}}
        self.plan["jobs"].append(job)
        return job

    def add_background(self, name):
        work = create_work(self.case, self.target, self.preparation / "change", install=False)
        destination = self.source / name / "work"
        shutil.copytree(work.source_root, destination)
        request = file_ref(self.source, name + "/work/record.json")
        job = {"job_id": name, "puzzle_id": work.request["puzzle_id"], "revision": work.request["revision"],
               "operation": "background_adopt", "rulebook": self.rulebook(name + "/rulebook.md"),
               "authorization": request,
               "inputs": {"request": deepcopy(request), "work": directory_ref(self.source, name + "/work")},
               "parameters": {}, "budgets": deepcopy(BACKGROUND_BUDGETS),
               "max_attempts": {phase: 12 for phase in ("store", "plan", "adopt", "reconcile")}}
        self.plan["jobs"].append(job)
        return job

    def save(self):
        self.path.write_bytes(encoded(self.plan))
        return self.path

    def clone(self, root):
        """Copy the same own synthetic inputs; do not produce another corpus."""
        root = Path(root).absolute()
        shutil.copytree(self.root, root)
        other = object.__new__(type(self))
        other.__dict__ = dict(self.__dict__)
        for name in ("root", "source", "target", "work", "path", "preparation"):
            old = getattr(self, name)
            setattr(other, name, root / old.relative_to(self.root))
        other.plan = deepcopy(self.plan)
        other.packages = deepcopy(self.packages)
        for data in other.packages.values():
            for name in ("export", "difficulty_path"):
                data[name] = root / data[name].relative_to(self.root)
        other.case = BackgroundContentTests()
        other.case.root = other.preparation
        other.case.counter = self.case.counter
        return other

    def arguments(self):
        return {"plan_path": self.path, "source_root": self.source, "repo_root": self.repo,
                "target_root": self.target, "work_root": self.work, "history_root": None}


def walkthrough_fixture(root):
    return IntegrationFixture(root)
