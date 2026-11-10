"""Closed BA-A transport forms; byte trust is established separately on each run."""
from __future__ import annotations

import math
import re

from . import authoring_package as ap, catalog_io as io
from .contract import InvalidInput, canonical_bytes, exact_keys, integer
from .batch_io import MAX_FILE, MAX_FILES, MAX_JSON, MAX_TOTAL, require, json_bytes

PLAN_LIMIT = 2 * 1024 * 1024
MAX_ATTEMPTS = 4096
NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
STATES = {"pending", "running", "completed", "waiting_input", "waiting_human",
          "blocked", "failed", "aborted", "interrupted", "stale"}
OVERALL = {"completed", "incomplete", "aborted", "invalid_input", "technical_error"}
DECISIONS = {"motif", "parameters", "repair", "background"}
RESERVATION_KEYS = set("number plan_sha256 job_id stage_id puzzle_id kind operation attempt_type "
                       "fingerprint input_bindings tool_binding reserved_limits output_dir".split())
ATTEMPT_KEYS = RESERVATION_KEYS | {"status", "result", "inventory", "seconds", "error"}
VIEW_KEYS = set("job_id stage_id status fingerprint attempt reused reason next_step".split())


def name(value):
    require(isinstance(value, str) and NAME.fullmatch(value), "Invalid batch identifier")
    return value


def text(value, *, nullable=False, maximum=4096):
    require((nullable and value is None) or
            isinstance(value, str) and len(value) <= maximum, "Invalid batch text")
    return value


def number(value, *, nullable=False):
    require((nullable and value is None) or type(value) in (int, float) and
            math.isfinite(value) and value >= 0, "Invalid batch elapsed time")


def file_ref(ref, *, source=False):
    exact_keys(ref, {"file", "sha256", "bytes"} | ({"kind"} if source else set()))
    if source:
        require(ref["kind"] == "source", "Expected a SourceRef")
    ap.relative(ref["file"])
    ap.sha(ref["sha256"])
    integer(ref["bytes"], 0, MAX_FILE, "batch file bytes")
    return ref


def input_ref(value, *, nullable=False):
    if value is None:
        require(nullable, "Missing required batch input")
        return None
    require(isinstance(value, dict), "Invalid batch input ref")
    if value.get("kind") == "source":
        return file_ref(value, source=True)
    exact_keys(value, {"kind", "stage", "slot", "candidate_id"})
    require(value["kind"] == "output", "Unknown batch input kind")
    name(value["stage"])
    name(value["slot"])
    if value["candidate_id"] is not None:
        name(value["candidate_id"])
    return value


def validate_plan(value, repo_root, *, check_binding=True):
    from . import batch_operations as operations
    plan = json_bytes(canonical_bytes(value), PLAN_LIMIT)
    exact_keys(plan, {"format", "batch_id", "revision", "previous_plan_sha256", "source_commit", "jobs"})
    require(plan["format"] == "picross-batch-plan-v1", "Unknown batch plan format")
    name(plan["batch_id"])
    integer(plan["revision"], 1, 1_000_000, "batch plan revision")
    if plan["revision"] == 1:
        require(plan["previous_plan_sha256"] is None, "Initial batch plan must have no predecessor")
    else:
        ap.sha(plan["previous_plan_sha256"])
    require(isinstance(plan["source_commit"], str) and COMMIT.fullmatch(plan["source_commit"]),
            "Invalid actual source commit")
    require(isinstance(plan["jobs"], list) and 1 <= len(plan["jobs"]) <= 32, "Batch needs 1..32 explicit jobs")
    jobs, total = set(), 0
    for job in plan["jobs"]:
        exact_keys(job, {"job_id", "puzzle_id", "revision", "background_revision", "rulebook", "decisions", "stages"})
        name(job["job_id"])
        require(job["job_id"] not in jobs, "Duplicate batch job")
        jobs.add(job["job_id"])
        require(isinstance(job["puzzle_id"], str) and ap.ID.fullmatch(job["puzzle_id"]), "Invalid batch puzzle ID")
        require(isinstance(job["revision"], str) and ap.REVISION.fullmatch(job["revision"]), "Invalid production revision")
        require(job["background_revision"] is None or isinstance(job["background_revision"], str)
                and ap.REVISION.fullmatch(job["background_revision"]), "Invalid background revision")
        rule = exact_keys(job["rulebook"], {"version", "document_revision", "snapshot"})
        require(rule["version"] in ("0.6.0", "0.7.0"), "Unsupported batch rulebook")
        integer(rule["document_revision"], 1, 1_000_000, "rulebook document revision")
        file_ref(rule["snapshot"], source=True)
        exact_keys(job["decisions"], DECISIONS)
        for ref in job["decisions"].values():
            if ref is not None:
                file_ref(ref, source=True)
        require(isinstance(job["stages"], list) and 1 <= len(job["stages"]) <= 32, "Job needs 1..32 explicit stages")
        previous = {}
        for stage in job["stages"]:
            exact_keys(stage, {"stage_id", "kind", "operation", "inputs", "parameters", "limits", "max_attempts", "tool_binding"})
            name(stage["stage_id"])
            name(stage["kind"])
            name(stage["operation"])
            require(stage["stage_id"] not in previous, "Duplicate stage ID")
            key = (stage["kind"], stage["operation"])
            require(key in operations.OPERATION_SPECS, "Unsupported batch operation")
            spec = operations.OPERATION_SPECS[key]
            exact_keys(stage["inputs"], set(spec["inputs"]))
            for field, ref in stage["inputs"].items():
                input_ref(ref, nullable=field in spec["nullable"])
                if ref is None or ref["kind"] == "source":
                    continue
                require(ref["stage"] in previous, "Forward/cyclic/cross-job output reference")
                producer = previous[ref["stage"]]
                outputs = operations.OPERATION_SPECS[(producer["kind"], producer["operation"])]
                candidate = ref["candidate_id"]
                require(ref["slot"] in (outputs["candidate_slots"] if candidate is not None else outputs["slots"]),
                        "Unknown output slot or missing candidate ID")
                if candidate is not None:
                    selected = (producer["parameters"].get("candidates") if producer["kind"] == "image_import"
                                else [producer["parameters"].get("candidate")])
                    require(candidate in selected, "Output refers to an unselected variant")
            exact_keys(stage["max_attempts"], {"produce", "revalidate"})
            for count in stage["max_attempts"].values():
                integer(count, 0, 100, "batch attempt allowance")
            requested = "produce" if spec["produce"] else "revalidate"
            require(stage["max_attempts"][requested] > 0, "Requested operation has no attempt allowance")
            operations.validate_operation(stage, repo_root, check_binding=check_binding)
            if key == ("difficulty", "analyze"):
                require(stage["parameters"]["puzzle_id"] == job["puzzle_id"],
                        "Difficulty identity differs from selected job")
            if stage["kind"] in ("image_import", "repair") and "approval" in stage["inputs"]:
                require(stage["inputs"]["approval"] == job["decisions"]["motif"],
                        "Stage approval differs from actual job motif decision")
            if key == ("repair", "search"):
                require(stage["inputs"]["plan"] == job["decisions"]["repair"],
                        "Repair plan differs from explicitly bound repair order")
            previous[stage["stage_id"]] = stage
            total += 1
    require(total <= 256, "Batch exceeds 256 selected stages")
    return plan


def plan_ref(value):
    exact_keys(value, {"revision", "file", "sha256", "bytes"})
    integer(value["revision"], 1, 1_000_000, "plan ref revision")
    file_ref({key: value[key] for key in ("file", "sha256", "bytes")})
    require(value["bytes"] <= PLAN_LIMIT, "Plan ref exceeds byte limit")


def inventory(value):
    require(isinstance(value, list) and len(value) <= MAX_FILES, "Invalid batch inventory")
    total, names = 0, []
    for item in value:
        file_ref(item)
        total += item["bytes"]
        names.append(item["file"])
    require(total <= MAX_TOTAL and names == sorted(names) and len(set(n.casefold() for n in names)) == len(names),
            "Batch inventory duplicates/order/bytes")
    # Include directory spellings, not just complete leaf paths.
    from .authoring_build_contract import names as namespace
    namespace(names)


def artifact_ref(value):
    require(isinstance(value, dict), "Invalid saved artifact ref")
    if value.get("kind") == "file":
        exact_keys(value, {"kind", "root", "file", "sha256", "bytes"})
        file_ref({key: value[key] for key in ("file", "sha256", "bytes")})
    else:
        exact_keys(value, {"kind", "root", "file", "files"})
        require(value["kind"] == "directory", "Invalid saved artifact kind")
        if value["file"] != "":
            ap.relative(value["file"])
        inventory(value["files"])
    require(value["root"] in ("source", "work"), "Unknown saved artifact root")


def result(value):
    exact_keys(value, {"status", "domain", "certified", "exit_code", "slots", "details"})
    require(isinstance(value["status"], str) and value["status"] in STATES, "Unknown operation status")
    text(value["domain"])
    require(value["certified"] is None or type(value["certified"]) is bool, "Invalid certification status")
    integer(value["exit_code"], 0, 255, "domain exit code")
    require(isinstance(value["slots"], dict) and len(value["slots"]) <= 512, "Invalid operation slots")
    for key, ref in value["slots"].items():
        require(isinstance(key, str) and 1 <= len(key) <= 130 and key.count(":") <= 1, "Invalid slot key")
        for part in key.split(":"):
            name(part)
        artifact_ref(ref)
    d = exact_keys(value["details"], {"reason", "candidates", "method", "state", "usage"})
    for key in ("reason", "method", "state"):
        text(d[key], nullable=True)
    require(isinstance(d["candidates"], list) and len(d["candidates"]) <= 128, "Invalid result candidate list")
    for candidate in d["candidates"]:
        exact_keys(candidate, {"candidate_id", "status", "certified"})
        name(candidate["candidate_id"])
        text(candidate["status"])
        require(type(candidate["certified"]) is bool, "Invalid candidate certification")
    exact_keys(d["usage"], {"lines", "pair_work", "pair_records", "steps", "candidates", "rule_work", "waves"})
    for count in d["usage"].values():
        if count is not None:
            integer(count, 0, 9007199254740991, "actual operation work")


def reservation(value):
    exact_keys(value, RESERVATION_KEYS | {"format"})
    require(value["format"] == "picross-batch-reservation-v1", "Unknown reservation format")
    integer(value["number"], 1, MAX_ATTEMPTS, "attempt number")
    ap.sha(value["plan_sha256"])
    for key in ("job_id", "stage_id", "kind", "operation"):
        name(value[key])
    require(isinstance(value["puzzle_id"], str) and ap.ID.fullmatch(value["puzzle_id"]), "Invalid reservation puzzle")
    require(value["attempt_type"] in ("produce", "revalidate"), "Unknown attempt type")
    ap.sha(value["fingerprint"])
    ap.relative(value["output_dir"])
    require(value["output_dir"] == f"attempts/{value['number']:06d}/output", "Unowned attempt output path")
    bindings = exact_keys(value["input_bindings"], {"inputs", "decisions", "rulebook"})
    require(isinstance(bindings["inputs"], dict), "Invalid input bindings")
    exact_keys(bindings["decisions"], DECISIONS)
    for ref in (*bindings["inputs"].values(), *bindings["decisions"].values(), bindings["rulebook"]):
        if ref is not None:
            artifact_ref(ref)
    limits = exact_keys(value["reserved_limits"], {"produce", "revalidate", "seconds"})
    number(limits["seconds"])
    require(limits["seconds"] > 0, "Missing operation process limit")
    require(isinstance(value["tool_binding"], dict), "Missing reservation tool binding")


def attempt(value):
    exact_keys(value, ATTEMPT_KEYS)
    reservation({"format": "picross-batch-reservation-v1", **{key: value[key] for key in RESERVATION_KEYS}})
    require(value["status"] in ("running", "completed", "failed", "aborted", "interrupted"), "Invalid attempt status")
    if value["result"] is not None:
        result(value["result"])
    inventory(value["inventory"])
    number(value["seconds"], nullable=True)
    text(value["error"], nullable=True)
    require(value["status"] != "completed" or value["result"] is not None, "Completed attempt lacks actual result")


def stage_view(value):
    exact_keys(value, VIEW_KEYS)
    name(value["job_id"])
    name(value["stage_id"])
    require(isinstance(value["status"], str) and value["status"] in STATES, "Invalid stage status")
    if value["fingerprint"] is not None:
        ap.sha(value["fingerprint"])
    if value["attempt"] is not None:
        integer(value["attempt"], 1, MAX_ATTEMPTS, "stage attempt")
    require(type(value["reused"]) is bool, "Invalid reuse status")
    text(value["reason"], nullable=True)
    text(value["next_step"], nullable=True)


def checkpoint(value):
    exact_keys(value, {"format", "batch_id", "plan", "plans", "attempts", "stages", "status"})
    require(value["format"] == "picross-batch-checkpoint-v1", "Unknown checkpoint format")
    name(value["batch_id"])
    plan_ref(value["plan"])
    require(isinstance(value["plans"], list) and value["plans"], "Missing batch plan history")
    for item in value["plans"]:
        plan_ref(item)
    require(value["plan"] == value["plans"][-1], "Checkpoint current plan differs from its chain")
    require(isinstance(value["attempts"], list) and len(value["attempts"]) <= MAX_ATTEMPTS, "Invalid attempt history")
    for index, item in enumerate(value["attempts"], 1):
        attempt(item)
        require(item["number"] == index, "Noncontiguous attempt history")
    require(isinstance(value["stages"], list) and len(value["stages"]) <= 256, "Invalid checkpoint stages")
    seen = set()
    for item in value["stages"]:
        stage_view(item)
        key = item["job_id"], item["stage_id"]
        require(key not in seen, "Duplicate checkpoint stage")
        seen.add(key)
        require(item["attempt"] is None or item["attempt"] <= len(value["attempts"]), "Unknown stage attempt")
    require(isinstance(value["status"], str) and value["status"] in OVERALL, "Invalid checkpoint overall status")
    return value


def report(value):
    exact_keys(value, {"format", "batch_id", "plan", "source_commit", "status", "jobs", "attempts",
                       "elapsed_seconds", "execution_seconds", "verification_seconds", "human_seconds", "next_step"})
    require(value["format"] == "picross-batch-report-v1", "Unknown report format")
    name(value["batch_id"])
    plan_ref(value["plan"])
    require(isinstance(value["source_commit"], str) and COMMIT.fullmatch(value["source_commit"]), "Invalid report provenance")
    require(isinstance(value["status"], str) and value["status"] in OVERALL, "Invalid report status")
    require(isinstance(value["jobs"], list) and len(value["jobs"]) <= 32, "Invalid report jobs")
    for job in value["jobs"]:
        exact_keys(job, {"job_id", "status", "stages"})
        name(job["job_id"])
        require(isinstance(job["status"], str) and job["status"] in OVERALL, "Invalid job status")
        require(isinstance(job["stages"], list), "Invalid job stages")
        for stage in job["stages"]:
            stage_view(stage)
    require(isinstance(value["attempts"], list) and len(value["attempts"]) <= MAX_ATTEMPTS, "Invalid report attempt list")
    for item in value["attempts"]:
        attempt(item)
    for key in ("elapsed_seconds", "execution_seconds", "verification_seconds"):
        number(value[key], nullable=True)
    require(value["human_seconds"] is None, "Unmeasured human time must be null")
    text(value["next_step"])
    return value
