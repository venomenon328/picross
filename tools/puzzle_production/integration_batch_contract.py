"""Closed BA-B transport forms. Native readers retain all content authority."""
from __future__ import annotations

import re

from . import authoring_package as ap, batch_contract as local, batch_io as bio
from .contract import canonical_bytes, exact_keys, integer

PLAN_LIMIT = 2 * 1024 * 1024
MAX_ATTEMPTS = 4096
MAX_FILES = 512
PREFIX = "picross-integration-batch-"
STATES = local.STATES | {"recovery_required"}
OVERALL = local.OVERALL
EXIT_CODES = {"completed": 0, "invalid_input": 2, "incomplete": 3,
              "aborted": 4, "technical_error": 5}
PHASES = {"register": ("export", "plan", "apply", "reconcile"),
          "background_adopt": ("store", "plan", "adopt", "reconcile")}
INPUTS = {"register": {"package", "handoff", "record", "approval", "external",
                       "manual_authorization", "palette_exception", "difficulty"},
          "background_adopt": {"request", "work"}}
PARAMETERS = {"register": {"name", "runtime_revision", "stem", "save_slot", "category_id",
                            "allow_background", "rebind_difficulty"}, "background_adopt": set()}
BUDGETS = {"register": {"export_seconds", "plan_seconds", "publication_seconds", "recovery_seconds", "reconcile_seconds"},
           "background_adopt": {"store_seconds", "plan_seconds", "adopt_seconds", "recovery_seconds", "reconcile_seconds"}}
RESERVATION = set("format number plan_sha256 job_id puzzle_id operation phase ordinal inputs_sha256 tool_sha256 budgets output_dir".split())
VIEW = set("job_id puzzle_id operation status historical_completed current_verified attempt reached reason next_step".split())
require = bio.require
name = local.name
text = local.text
number = local.number


def nonempty(value, maximum=4096):
    text(value, maximum=maximum)
    require(bool(value.strip()) and "\0" not in value, "Empty or invalid batch text")


def puzzle(value):
    require(isinstance(value, str) and ap.ID.fullmatch(value), "Invalid selected puzzle ID")


def file_ref(value):
    return local.file_ref(value)


def inventory(value):
    local.inventory(value)
    require(len(value) <= MAX_FILES, "Integration inventory exceeds 512 files")


def directory_ref(value):
    exact_keys(value, {"directory", "files"})
    if value["directory"] != ".":
        ap.relative(value["directory"])
    inventory(value["files"])


def source_ref(value, *, directory=False):
    if value is None:
        return
    if directory and isinstance(value, dict) and "directory" in value:
        directory_ref(value)
    else:
        file_ref(value)


def budgets(value, operation):
    exact_keys(value, BUDGETS[operation])
    for key, seconds in value.items():
        number(seconds)
        if operation == "register" and key in ("publication_seconds", "recovery_seconds"):
            require(0 < seconds <= 86400, "Registration override outside finite BA-B allowance")
        else:
            require(seconds == 300 and type(seconds) in (int, float), "Native fixed phase budget must be 300 seconds")


def validate_plan(value):
    value = bio.json_bytes(canonical_bytes(value), PLAN_LIMIT)
    exact_keys(value, {"format", "batch_id", "revision", "previous_plan_sha256", "source_commit", "jobs"})
    require(value["format"] == PREFIX + "plan-v1", "Unknown integration batch plan")
    name(value["batch_id"])
    integer(value["revision"], 1, 1000000, "plan revision")
    if value["revision"] == 1:
        require(value["previous_plan_sha256"] is None, "Initial plan has a predecessor")
    else:
        ap.sha(value["previous_plan_sha256"])
    require(isinstance(value["source_commit"], str) and local.COMMIT.fullmatch(value["source_commit"]), "Invalid tool source commit")
    require(isinstance(value["jobs"], list) and 1 <= len(value["jobs"]) <= 32, "Select 1..32 integration jobs")
    identifiers, jobs = set(), set()
    for job in value["jobs"]:
        exact_keys(job, {"job_id", "puzzle_id", "revision", "operation", "rulebook", "authorization", "inputs",
                         "parameters", "budgets", "max_attempts"})
        name(job["job_id"])
        puzzle(job["puzzle_id"])
        require(job["job_id"] not in jobs and job["puzzle_id"] not in identifiers, "Duplicate job or puzzle across selection")
        jobs.add(job["job_id"]); identifiers.add(job["puzzle_id"])
        require(isinstance(job["revision"], str) and ap.REVISION.fullmatch(job["revision"]), "Invalid production/background revision")
        operation = job["operation"]
        require(isinstance(operation, str) and operation in PHASES, "Unknown integration operation")
        rule = exact_keys(job["rulebook"], {"version", "document_revision", "snapshot"})
        require(rule["version"] in ("0.6.0", "0.7.0", "0.8.0"), "Unsupported rulebook version")
        integer(rule["document_revision"], 1, 1000000, "rulebook revision")
        file_ref(rule["snapshot"])
        source_ref(job["authorization"])
        exact_keys(job["inputs"], INPUTS[operation])
        for key, ref in job["inputs"].items():
            source_ref(ref, directory=key in ("package", "external", "work"))
            if ref is not None and key in ("external", "work"):
                directory_ref(ref)
        exact_keys(job["parameters"], PARAMETERS[operation])
        if operation == "register":
            p = job["parameters"]
            nonempty(p["name"], 256); nonempty(p["category_id"], 128)
            integer(p["runtime_revision"], 1, 1000000, "runtime revision")
            for key in ("stem", "save_slot"):
                require(isinstance(p[key], str) and ap.STEM.fullmatch(p[key]), "Invalid native stem/save slot")
            for key in ("allow_background", "rebind_difficulty"):
                require(type(p[key]) is bool, "Integration option is not a bool")
        elif job["authorization"] is not None:
            require(job["authorization"] == job["inputs"]["request"], "Background authorization must be its unchanged request")
        budgets(job["budgets"], operation)
        exact_keys(job["max_attempts"], set(PHASES[operation]))
        for count in job["max_attempts"].values():
            integer(count, 1, 100, "phase attempt allowance")
    return value


def order(value, job):
    exact_keys(value, {"format", "operation", "puzzle_id", "revision", "actor", "timestamp_utc", "statement", "evidence", "test_only"})
    require(value["format"] == "picross-integration-order-v1", "Unknown integration order")
    require(all(value[k] == job[k] for k in ("operation", "puzzle_id", "revision")), "Integration order does not cover selected operation/identity/revision")
    nonempty(value["actor"]); nonempty(value["statement"])
    ap.timestamp(value["timestamp_utc"])
    file_ref(value["evidence"])
    require(type(value["test_only"]) is bool, "Order test scope must be bool")
    return value


def identity(value):
    exact_keys(value, {"device", "inode"})
    for item in value.values(): integer(item, 0, 2**64-1, "filesystem identity")


def tool_binding(value):
    exact_keys(value, {"files", "python", "pillow", "codecs"})
    inventory(value["files"])
    nonempty(value["python"], 128)
    nonempty(value["pillow"], 128)
    exact_keys(value["codecs"], {"zlib", "littlecms", "jpeg", "jpeg_turbo"})
    for item in value["codecs"].values(): text(item, nullable=True, maximum=128)


def bindings(value):
    exact_keys(value, {"source_root", "repo_root", "target_root", "work_root", "history_root", "work_identity", "target_identity", "tool_binding"})
    for key in ("source_root", "repo_root", "target_root", "work_root"): nonempty(value[key])
    text(value["history_root"], nullable=True)
    identity(value["work_identity"]); identity(value["target_identity"])
    tool_binding(value["tool_binding"])


def owner(value):
    exact_keys(value, {"format", "batch_id", "bindings"})
    require(value["format"] == PREFIX + "owner-v1", "Invalid integration work owner")
    name(value["batch_id"]); bindings(value["bindings"])
    return value


def plan_ref(value):
    local.plan_ref(value)
    require(value["file"] == f"plans/{value['revision']:06d}-{value['sha256']}.json", "Unowned plan path")


def reservation(value):
    exact_keys(value, RESERVATION)
    require(value["format"] == PREFIX + "reservation-v1", "Invalid integration reservation")
    integer(value["number"], 1, MAX_ATTEMPTS, "attempt number")
    integer(value["ordinal"], 1, 100, "phase ordinal")
    name(value["job_id"]); puzzle(value["puzzle_id"])
    require(isinstance(value["operation"], str) and value["operation"] in PHASES and isinstance(value["phase"], str) and
            value["phase"] in PHASES[value["operation"]], "Unknown reserved operation/phase")
    for key in ("plan_sha256", "inputs_sha256", "tool_sha256"): ap.sha(value[key])
    budgets(value["budgets"], value["operation"])
    require(value["output_dir"] == f"attempts/{value['number']:06d}/output", "Unowned attempt output")
    return value


def reached(value):
    if value is None: return
    exact_keys(value, {"entry", "files"})
    require(isinstance(value["entry"], dict), "Reached target requires native entry")
    puzzle(value["entry"].get("id"))
    inventory(value["files"])


def result(value):
    exact_keys(value, set("format number status native diagnostics elapsed_seconds error exit_code reached output_files remaining".split()))
    require(value["format"] == PREFIX + "result-v1", "Invalid integration result")
    integer(value["number"], 1, MAX_ATTEMPTS, "result attempt")
    require(isinstance(value["status"], str) and value["status"] in {"completed", "blocked", "failed", "aborted", "interrupted", "recovery_required"}, "Unknown result status")
    require(value["native"] is None or isinstance(value["native"], dict), "Native result must remain an object")
    if isinstance(value["native"], dict) and value["native"].get("status") == "reconciled":
        exact_keys(value["native"], {"status", "id", "reached"})
        puzzle(value["native"]["id"]); reached(value["native"]["reached"])
    if isinstance(value["native"], dict) and value["native"].get("status") == "rollback-confirmed":
        exact_keys(value["native"], {"status", "id", "plan_hash"})
        puzzle(value["native"]["id"]); ap.sha(value["native"]["plan_hash"])
    require(isinstance(value["diagnostics"], dict) and value["diagnostics"].get("format") == "picross-ri-a-operation-v1", "Missing actual RI diagnostics")
    require(value["status"] != "completed" or value["native"] is not None, "Success lacks native result")
    number(value["elapsed_seconds"], nullable=True); text(value["error"], nullable=True)
    integer(value["exit_code"], 0, 255, "native exit code")
    reached(value["reached"]); inventory(value["output_files"])
    require(isinstance(value["remaining"], list) and len(value["remaining"]) <= 512, "Invalid remaining paths")
    for path in value["remaining"]: nonempty(path)
    return value


def attempt(value):
    exact_keys(value, {"reservation", "result"})
    reservation(value["reservation"])
    if value["result"] is not None:
        result(value["result"])
        require(value["result"]["number"] == value["reservation"]["number"], "Result/reservation mismatch")


def job_view(value):
    exact_keys(value, VIEW)
    name(value["job_id"]); puzzle(value["puzzle_id"])
    require(isinstance(value["operation"], str) and value["operation"] in PHASES and isinstance(value["status"], str) and
            value["status"] in STATES, "Invalid job state")
    for key in ("historical_completed", "current_verified"):
        require(type(value[key]) is bool, "Invalid target verification flag")
    if value["attempt"] is not None: integer(value["attempt"], 1, MAX_ATTEMPTS, "job attempt")
    reached(value["reached"])
    text(value["reason"], nullable=True); text(value["next_step"], nullable=True)
    require(not value["current_verified"] or value["historical_completed"], "Current success lacks historical result")
    require(value["status"] != "completed" or value["historical_completed"] and value["current_verified"] and value["reached"] is not None,
            "Completed job lacks a confirmed reached target")


def attempts(value):
    require(isinstance(value, list) and len(value) <= MAX_ATTEMPTS, "Invalid attempt list")
    for i, item in enumerate(value, 1):
        attempt(item)
        require(item["reservation"]["number"] == i, "Noncontiguous attempt sequence")


def jobs(value):
    require(isinstance(value, list) and len(value) <= 32, "Invalid job views")
    seen = set()
    for item in value:
        job_view(item)
        require(item["puzzle_id"] not in seen, "Duplicate target view")
        seen.add(item["puzzle_id"])


def checkpoint(value):
    exact_keys(value, {"format", "batch_id", "plan", "plans", "bindings", "attempts", "jobs", "status"})
    require(value["format"] == PREFIX + "checkpoint-v1", "Invalid integration checkpoint")
    name(value["batch_id"]); plan_ref(value["plan"]); bindings(value["bindings"])
    require(isinstance(value["plans"], list) and 1 <= len(value["plans"]) <= 1000000, "Invalid plan chain")
    for item in value["plans"]: plan_ref(item)
    require(value["plan"] == value["plans"][-1], "Checkpoint current plan differs")
    attempts(value["attempts"]); jobs(value["jobs"])
    require(isinstance(value["status"], str) and value["status"] in OVERALL, "Invalid overall status")
    require(value["status"] != "completed" or all(j["status"] == "completed" for j in value["jobs"]), "Forged overall completion")
    return value


def report(value):
    exact_keys(value, set("format batch_id plan source_commit tool_binding status exit_code jobs attempts journal elapsed_seconds execution_seconds reconciliation_seconds waiting_seconds human_seconds fresh next_step".split()))
    require(value["format"] == PREFIX + "report-v1", "Invalid integration report")
    name(value["batch_id"]); plan_ref(value["plan"]); tool_binding(value["tool_binding"])
    require(isinstance(value["source_commit"], str) and local.COMMIT.fullmatch(value["source_commit"]), "Invalid report commit")
    require(isinstance(value["status"], str) and value["status"] in OVERALL and type(value["exit_code"]) is int and value["exit_code"] == EXIT_CODES[value["status"]], "Report status/exit differ")
    jobs(value["jobs"]); attempts(value["attempts"])
    require(value["status"] != "completed" or value["fresh"] is True and all(j["status"] == "completed" and j["current_verified"] for j in value["jobs"]),
            "Completed report requires a freshly confirmed complete selection")
    exact_keys(value["journal"], {"pending", "staging"})
    text(value["journal"]["pending"], nullable=True)
    require(isinstance(value["journal"]["staging"], list), "Invalid journal staging view")
    for item in value["journal"]["staging"]: text(item)
    for key in ("elapsed_seconds", "execution_seconds", "reconciliation_seconds"): number(value[key], nullable=True)
    require(value["waiting_seconds"] is None and value["human_seconds"] is None, "Unmeasured waiting/human time must be null")
    require(type(value["fresh"]) is bool, "Invalid freshness flag")
    nonempty(value["next_step"])
    return value
