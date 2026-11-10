"""BA-A serial local runner with durable reservations and fresh domain replay.

The checkpoint is a projection of immutable plans/reservations/results. It is
never a proof, authority to produce, or a serialized integration trust context.
"""
from __future__ import annotations

from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
import uuid

from . import batch_contract as bc, batch_io as bio, batch_operations as operations
from . import catalog_io as io
from .contract import Aborted, InvalidInput, canonical_bytes, exact_keys

EXIT_CODES = {"completed": 0, "invalid_input": 2, "incomplete": 3,
              "aborted": 4, "technical_error": 5}
class BatchTechnicalError(RuntimeError):
    """The shared workspace is unsafe; preserve it and stop all scheduling."""


PENDING = re.compile(r"\.batch-pending-[0-9a-f]{32}\.json\Z")
STAGING = re.compile(r"\.batch-attempt-[0-9a-f]{32}\Z")


def _head(repo):
    process = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10, check=False)
    value = process.stdout.strip()
    bio.require(process.returncode == 0 and bc.COMMIT.fullmatch(value), "Missing actual repository HEAD")
    return value


def _source(ref, source):
    path = io.safe(source, ref["file"])
    raw = bio.read(path, bio.MAX_FILE)
    bio.require(len(raw) == ref["bytes"] and bio.sha(raw) == ref["sha256"],
                "Declared source bytes changed: " + ref["file"])
    return {"kind": "file", "root": "source", "file": ref["file"],
            "sha256": ref["sha256"], "bytes": ref["bytes"]}


def _prepare(plan_path, source_root, repo_root, work_root=None, history_root=None):
    source, work, repo, history = bio.roots(source_root, work_root, repo_root, history_root)
    raw = bio.read(plan_path, bc.PLAN_LIMIT)
    plan = bc.validate_plan(bio.json_bytes(raw, bc.PLAN_LIMIT), repo)
    declared = {}
    for job in plan["jobs"]:
        rule = job["rulebook"]
        snapshot = _source(rule["snapshot"], source)
        snapshot_raw = bio.read(io.safe(source, snapshot["file"]))
        pattern = rb"(?m)^\*\*Version " + re.escape(rule["version"].encode()) + rb" \xc2\xb7 Dokumentrevision " + str(rule["document_revision"]).encode() + rb" \xc2\xb7"
        bio.require(re.search(pattern, snapshot_raw), "Rulebook snapshot version/revision mismatch")
        file = "PUZZLE_AUTHORING.md" if rule["version"] == "0.6.0" else "PUZZLE_AUTHORING_0_7_0_PREVIEW.md"
        bio.require(snapshot_raw == bio.read(repo / "docs" / "ai-workflows" / file),
                    "Unknown or unsupported current rulebook snapshot")
        refs = [rule["snapshot"], *job["decisions"].values()]
        for stage in job["stages"]:
            refs.extend(stage["inputs"].values())
        for ref in refs:
            if ref is None or ref["kind"] != "source":
                continue
            binding = _source(ref, source)
            key = ref["file"].casefold()
            bio.require(declared.setdefault(key, binding) == binding, "Conflicting source path/byte declarations")
    actual_head = _head(repo)
    known = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", plan["source_commit"] + "^{commit}"],
                           capture_output=True, timeout=10, check=False)
    bio.require(known.returncode == 0, "Unknown source commit in the selected repository")
    return plan, raw, source, work, repo, history, actual_head


def validate(plan_path, source_root, repo_root, work_root=None, history_root=None):
    plan, raw, *_ = _prepare(plan_path, source_root, repo_root, work_root, history_root)
    return {"status": "valid", "batch_id": plan["batch_id"], "plan_sha256": bio.sha(raw),
            "jobs": len(plan["jobs"]), "stages": sum(len(job["stages"]) for job in plan["jobs"])}


def _plan_ref(plan, raw):
    checksum = bio.sha(raw)
    return {"revision": plan["revision"], "file": f"plans/{plan['revision']:06d}-{checksum}.json",
            "sha256": checksum, "bytes": len(raw)}


def _views(plan):
    return [{"job_id": job["job_id"], "stage_id": stage["stage_id"], "status": "pending",
             "fingerprint": None, "attempt": None, "reused": False, "reason": None,
             "next_step": "run explicitly selected stage"}
            for job in plan["jobs"] for stage in job["stages"]]


def _line(job, stage):
    return job["puzzle_id"], stage["kind"], stage["operation"]


def _within(new, old):
    if isinstance(old, dict):
        return isinstance(new, dict) and set(new) == set(old) and all(_within(new[k], old[k]) for k in old)
    if type(old) in (int, float):
        return type(new) in (int, float) and 0 <= new <= old
    return new == old


def _budget_history(plans):
    limits = {}
    for plan in plans:
        current = {}
        for job in plan["jobs"]:
            for stage in job["stages"]:
                line = _line(job, stage)
                bound = {"limits": stage["limits"], "max_attempts": stage["max_attempts"]}
                bio.require(current.setdefault(line, bound) == bound,
                            "Conflicting budgets for the same puzzle/operation line")
                if line in limits:
                    bio.require(_within(bound, limits[line]),
                                "Budget/attempt expansion needs a new explicit authorized order line")
                limits[line] = bound
    return limits


@contextmanager
def _shared_work():
    try:
        yield
    except BatchTechnicalError:
        raise
    except (Aborted, InvalidInput, ValueError, OSError) as exc:
        raise BatchTechnicalError(str(exc)) from exc


def _owner(work, source, repo, history, batch_id):
    return {"format": "picross-batch-owner-v1", "batch_id": batch_id,
            "work_identity": bio.identity(work), "source_root": str(source),
            "source_identity": bio.identity(source), "repo_root": str(repo),
            "history_root": str(history) if history else None}


def _read_owner(work):
    owner = bio.json_read(work / "owner.json")
    exact_keys(owner, {"format", "batch_id", "work_identity", "source_root", "source_identity", "repo_root", "history_root"})
    bio.require(owner["format"] == "picross-batch-owner-v1", "Unowned batch work root")
    bc.name(owner["batch_id"])
    for key in ("work_identity", "source_identity"):
        exact_keys(owner[key], {"device", "inode"})
        bio.require(all(type(value) is int and value >= 0 for value in owner[key].values()), "Invalid root identity")
    for key in ("source_root", "repo_root", "history_root"):
        value = owner[key]
        bio.require((key == "history_root" and value is None) or isinstance(value, str) and Path(value).is_absolute(),
                    "Invalid batch root binding")
    bio.require(owner["work_identity"] == bio.identity(work), "Batch root identity changed")
    return owner


def _namespace(work):
    allowed = {"owner.json", "plans", "attempts", "checkpoint.json", "report.json", ".batch-writer.lock", ".batch-worker.lock"}
    for item in work.iterdir():
        bio.require(item.name in allowed or PENDING.fullmatch(item.name), "Unknown file in owned batch root: " + item.name)
        io.safe(work, item.name)
    for directory in ("plans", "attempts"):
        bio.require((work / directory).is_dir(), "Missing batch metadata directory")
        for item in (work / directory).iterdir():
            io.safe(work / directory, item.name)
            if STAGING.fullmatch(item.name):
                bio.require(item.is_dir(), "Invalid staged attempt directory")
                for child in item.iterdir():
                    io.safe(item, child.name)
                    bio.require(child.is_file() and (child.name == "reservation.json" or PENDING.fullmatch(child.name)),
                                "Unknown file in staged attempt")


def _find_stage(plan, job_id, stage_id):
    jobs = [job for job in plan["jobs"] if job["job_id"] == job_id]
    bio.require(len(jobs) == 1, "Ledger names an unknown job")
    stages = [stage for stage in jobs[0]["stages"] if stage["stage_id"] == stage_id]
    bio.require(len(stages) == 1, "Ledger names an unknown stage")
    return jobs[0], stages[0]


def _source_binding(ref):
    return {"kind": "file", "root": "source", "file": ref["file"], "sha256": ref["sha256"], "bytes": ref["bytes"]}


def _check_reservation(reservation, plans, earlier):
    bc.reservation(reservation)
    bio.require(reservation["plan_sha256"] in plans, "Reservation has no bound original plan")
    plan = plans[reservation["plan_sha256"]]
    job, stage = _find_stage(plan, reservation["job_id"], reservation["stage_id"])
    for key, expected in (("puzzle_id", job["puzzle_id"]), ("kind", stage["kind"]),
                          ("operation", stage["operation"]), ("tool_binding", stage["tool_binding"])):
        bio.require(reservation[key] == expected, "Reservation differs from its original plan: " + key)
    bindings = reservation["input_bindings"]
    exact_keys(bindings["inputs"], set(stage["inputs"]))
    bio.require(bindings["rulebook"] == _source_binding(job["rulebook"]["snapshot"]), "Reservation rulebook changed")
    for key, ref in job["decisions"].items():
        bio.require(bindings["decisions"][key] == (_source_binding(ref) if ref else None), "Reservation decision changed")
    for field, declared in stage["inputs"].items():
        observed = bindings["inputs"][field]
        if declared is None or declared["kind"] == "source":
            bio.require(observed == (_source_binding(declared) if declared else None), "Reservation source changed")
        else:
            key = declared["slot"] + (":" + declared["candidate_id"] if declared["candidate_id"] else "")
            matches = [old for old in earlier if old["job_id"] == job["job_id"]
                       and old["stage_id"] == declared["stage"] and old["result"] is not None
                       and old["result"]["slots"].get(key) == observed]
            bio.require(matches, "Reservation output ref has no actual earlier same-job producer")
    expected = operations.reservation_limits(stage, reservation["attempt_type"])
    bio.require(reservation["reserved_limits"] == expected, "Reservation budgets differ from the bound operation")
    bio.require(reservation["fingerprint"] == _fingerprint(job, stage, bindings), "Reservation fingerprint changed")


def _pending(reservation):
    return {**{key: reservation[key] for key in bc.RESERVATION_KEYS},
            "status": "interrupted", "result": None, "inventory": [], "seconds": None,
            "error": "Interrupted after durable reservation; no committed result"}


def _history(work, repo, *, incoming=None):
    _namespace(work)
    original = bio.read(work / "checkpoint.json")
    checkpoint = bc.checkpoint(bio.json_bytes(original, bio.MAX_JSON))
    plans, previous = {}, None
    for index, ref in enumerate(checkpoint["plans"], 1):
        raw = bio.read(io.safe(work, ref["file"]), bc.PLAN_LIMIT)
        bio.require(len(raw) == ref["bytes"] and bio.sha(raw) == ref["sha256"], "Stored original plan changed")
        plan = bc.validate_plan(bio.json_bytes(raw, bc.PLAN_LIMIT), repo, check_binding=False)
        bio.require(ref == _plan_ref(plan, raw) and plan["batch_id"] == checkpoint["batch_id"] and
                    plan["revision"] == index and plan["previous_plan_sha256"] == previous,
                    "Broken batch plan chain")
        plans[ref["sha256"]] = plan
        previous = ref["sha256"]
    names = {Path(ref["file"]).name for ref in checkpoint["plans"]}
    if incoming is not None:
        names.add(Path(incoming["file"]).name)
    bio.require({p.name for p in (work / "plans").iterdir() if not PENDING.fullmatch(p.name)} <= names, "Unaccounted original plan file")
    _budget_history(list(plans.values()))
    entries = sorted((p for p in (work / "attempts").iterdir() if not STAGING.fullmatch(p.name)), key=lambda p: p.name)
    bio.require(len(entries) <= bc.MAX_ATTEMPTS, "Too many attempt ledgers")
    recovered = []
    for number, folder in enumerate(entries, 1):
        bio.require(folder.name == f"{number:06d}" and io.safe(work, "attempts/" + folder.name).is_dir(),
                    "Noncontiguous or invalid attempt directory")
        bio.require({p.name for p in folder.iterdir() if not PENDING.fullmatch(p.name)} <= {"reservation.json", "result.json", "output"},
                    "Unknown file in attempt ledger")
        for item in folder.iterdir():
            io.safe(folder, item.name)
        reservation = bio.json_read(folder / "reservation.json")
        bio.require(reservation["number"] == number, "Reservation number changed")
        _check_reservation(reservation, plans, recovered)
        if (folder / "result.json").exists():
            actual = bio.json_read(folder / "result.json")
            bc.attempt(actual)
            bio.require({key: actual[key] for key in bc.RESERVATION_KEYS} ==
                        {key: reservation[key] for key in bc.RESERVATION_KEYS}, "Result changed reservation")
        else:
            actual = _pending(reservation)
        if number <= len(checkpoint["attempts"]):
            saved = checkpoint["attempts"][number - 1]
            if saved["status"] == "running":
                bio.require({key: saved[key] for key in bc.RESERVATION_KEYS} ==
                            {key: actual[key] for key in bc.RESERVATION_KEYS} and saved["result"] is None,
                            "Checkpoint running reservation changed")
            else:
                bio.require(saved == actual, "Checkpoint contradicts immutable attempt ledger")
        recovered.append(actual)
    bio.require(len(checkpoint["attempts"]) <= len(recovered), "Checkpoint history was truncated on disk")
    current = plans[checkpoint["plan"]["sha256"]]
    expected_views = {(job["job_id"], stage["stage_id"]) for job in current["jobs"] for stage in job["stages"]}
    bio.require({(s["job_id"], s["stage_id"]) for s in checkpoint["stages"]} == expected_views,
                "Checkpoint stage selection differs from its plan")
    for view in checkpoint["stages"]:
        if view["attempt"] is None:
            bio.require(view["status"] != "completed" and not view["reused"], "Forged stage success without attempt")
            continue
        item = recovered[view["attempt"] - 1]
        bio.require((item["job_id"], item["stage_id"], item["fingerprint"]) ==
                    (view["job_id"], view["stage_id"], view["fingerprint"]), "Checkpoint stage points to unrelated attempt")
        if view["status"] == "completed":
            bio.require(item["status"] == "completed" and item["result"]["status"] == "completed",
                        "Forged checkpoint completion")
        bio.require(not view["reused"] or item["attempt_type"] == "revalidate", "Forged reuse claim")
    bio.require(checkpoint["status"] != "completed" or all(s["status"] == "completed" for s in checkpoint["stages"]),
                "Forged checkpoint overall completion")
    checkpoint["attempts"] = recovered
    return checkpoint, original, plans


def _fingerprint(job, stage, bindings):
    spec = operations.OPERATION_SPECS[(stage["kind"], stage["operation"])]
    relevant = set(spec["required_decisions"])
    if stage["kind"] == "background":
        relevant.add("background")
    value = {"puzzle_id": job["puzzle_id"], "kind": stage["kind"], "operation": stage["operation"],
             "inputs": bindings["inputs"], "parameters": stage["parameters"],
             "decisions": {key: bindings["decisions"][key] for key in sorted(relevant)},
             "rulebook": bindings["rulebook"], "tool_binding": stage["tool_binding"]}
    return bio.sha(canonical_bytes(value))


def _bindings(job, stage, available, source):
    inputs = {}
    for field, ref in stage["inputs"].items():
        if ref is None:
            inputs[field] = None
        elif ref["kind"] == "source":
            inputs[field] = _source(ref, source)
        else:
            key = ref["slot"] + (":" + ref["candidate_id"] if ref["candidate_id"] else "")
            result = available.get((job["job_id"], ref["stage"]))
            if result is None or key not in result["slots"]:
                return None, "Required preceding output is unavailable: " + ref["stage"] + "/" + key
            inputs[field] = result["slots"][key]
    return {"inputs": inputs,
            "decisions": {key: _source(ref, source) if ref else None for key, ref in job["decisions"].items()},
            "rulebook": _source(job["rulebook"]["snapshot"], source)}, None


def _check_bindings(bindings, source, work):
    for ref in (*bindings["inputs"].values(), *bindings["decisions"].values(), bindings["rulebook"]):
        if ref is not None:
            bio.artifact_path(ref, source, work)


def _job_identity(job, stage, bindings, source, work):
    spec = operations.OPERATION_SPECS[(stage["kind"], stage["operation"])]
    if "parameters" in spec["required_decisions"]:
        handoff = bio.json_read(bio.artifact_path(bindings["decisions"]["parameters"], source, work))
        bio.require(isinstance(handoff, dict) and handoff.get("puzzle_id") == job["puzzle_id"],
                    "Parameter decision belongs to a different puzzle")
    if stage["kind"] == "background":
        from . import background_contract as bg
        try:
            path = bio.artifact_path(bindings["inputs"]["request"], source, work)
            request = bg.validate_request(bg.parse_json(bio.read(path, bg.MAX_JSON)))
            ref = request["manifest"]
            raw = bio.read(io.safe(source, ref["file"]), bg.MAX_JSON)
            bio.require(len(raw) == ref["bytes"] and bio.sha(raw) == ref["sha256"],
                        "Background manifest bytes changed")
            manifest = bg.validate_manifest(bg.parse_json(raw))
            bio.require(manifest["puzzle_id"] == job["puzzle_id"] and
                        manifest["revision"] == job["background_revision"],
                        "Background identity/revision differs from selected job")
        except bg.BackgroundError as exc:
            raise InvalidInput(str(exc)) from exc


def _absolute_result(result, source, work):
    result = copy.deepcopy(result)
    for key, ref in result["slots"].items():
        path = bio.artifact_path(ref, source, work)
        slot = {k: v for k, v in ref.items() if k not in ("root", "file")}
        slot["path"] = str(path)
        result["slots"][key] = slot
    return result


def _check_saved_outputs(saved, attempts, work):
    owners = {saved["number"]}
    for ref in saved["result"]["slots"].values():
        if ref["root"] == "work":
            match = re.match(r"^attempts/([0-9]{6})/output(?:/|$)", ref["file"])
            bio.require(match is not None, "Saved slot has no producing attempt owner")
            owners.add(int(match.group(1)))
    for number in sorted(owners):
        bio.require(1 <= number <= len(attempts), "Unknown output owner")
        owner = attempts[number - 1]
        bio.require(owner["status"] == "completed", "Unfinished attempt cannot own a reusable output")
        bio.require(bio.inventory(io.safe(work, owner["output_dir"])) == owner["inventory"],
                    "Saved original output inventory changed/missing/extra")


def _normalize_result(result, source, work):
    operations.validate_result(result)
    result = copy.deepcopy(result)
    for key, slot in result["slots"].items():
        ref = bio.artifact(slot["path"], source, work)
        expected = {k: v for k, v in slot.items() if k != "path"}
        observed = {k: v for k, v in ref.items() if k not in ("root", "file")}
        bio.require(expected == observed, "Producer slot bytes differ from fresh inventory")
        result["slots"][key] = ref
    bc.result(result)
    return result


@contextmanager
def _signals():
    state = {"stop": False}
    old = {}
    if threading.current_thread() is threading.main_thread():
        def stop(_signum, _frame):
            state["stop"] = True
        for sig in (signal.SIGINT, signal.SIGTERM):
            old[sig] = signal.signal(sig, stop)
    try:
        yield state
    finally:
        for sig, handler in old.items():
            signal.signal(sig, handler)


def _worker(stage, bindings, output, repo, source, history, saved, work, reserved, signal_state):
    resolved = {key: str(bio.artifact_path(ref, source, work)) if ref else None
                for key, ref in bindings["inputs"].items()}
    decisions = {key: str(bio.artifact_path(ref, source, work)) if ref else None
                 for key, ref in bindings["decisions"].items()}
    payload = {"format": "picross-batch-worker-v1", "stage": stage, "inputs": resolved,
               "decisions": decisions, "output_root": str(output), "repo_root": str(repo),
               "source_root": str(source), "history_root": str(history) if history else None,
               "saved_result": _absolute_result(saved, source, work) if saved else None,
               "work_root": str(work), "parent_pid": os.getpid(), "seconds": reserved["seconds"]}
    raw = canonical_bytes(payload)
    bio.require(len(raw) <= bio.MAX_JSON, "Worker input exceeds transport limit")
    started = time.monotonic()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.Popen([sys.executable, "-m", "tools.puzzle_production.batch_worker"],
                               cwd=repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    aborted, first = False, True
    try:
        while True:
            if signal_state["stop"] or time.monotonic() - started >= reserved["seconds"]:
                aborted = True
                process.kill()
            try:
                stdout, stderr = process.communicate(input=raw if first else None, timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                first = False
        elapsed = time.monotonic() - started
        if aborted:
            return None, "Signal or reserved process deadline ended operation", elapsed, True
        bio.require(len(stdout) <= bio.MAX_JSON and len(stderr) <= bio.MAX_JSON, "Worker output exceeds transport limit")
        if process.returncode == 4:
            return None, "Worker lifetime/deadline ended operation", elapsed, True
        if process.returncode != 0:
            return None, "Worker exited " + str(process.returncode) + ": " + stderr.decode("utf-8", "replace")[-2000:], elapsed, False
        response = bio.json_bytes(stdout, bio.MAX_JSON)
        exact_keys(response, {"result", "error", "aborted"})
        bio.require(type(response["aborted"]) is bool and (response["error"] is None or isinstance(response["error"], str)),
                    "Invalid worker response")
        return response["result"], response["error"], elapsed, response["aborted"]
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)


def _overall(stages, *, stopped=False):
    if stopped or any(stage["status"] == "aborted" for stage in stages):
        return "aborted"
    return "completed" if all(stage["status"] == "completed" for stage in stages) else "incomplete"


def _report(checkpoint, plan, source_commit, elapsed):
    jobs = []
    for job in plan["jobs"]:
        stages = [copy.deepcopy(stage) for stage in checkpoint["stages"] if stage["job_id"] == job["job_id"]]
        jobs.append({"job_id": job["job_id"], "status": _overall(stages), "stages": stages})
    def total(kind):
        values = [item["seconds"] for item in checkpoint["attempts"] if item["attempt_type"] == kind]
        return None if any(value is None for value in values) else sum(values)
    result = {"format": "picross-batch-report-v1", "batch_id": plan["batch_id"], "plan": checkpoint["plan"],
              "source_commit": source_commit, "status": checkpoint["status"], "jobs": jobs,
              "attempts": copy.deepcopy(checkpoint["attempts"]), "elapsed_seconds": elapsed,
              "execution_seconds": total("produce"), "verification_seconds": total("revalidate"),
              "human_seconds": None,
              "next_step": "Technical selection completed; content approval and integration remain separate" if checkpoint["status"] == "completed"
              else "Resolve the reported inputs/decisions/errors within the remaining explicitly authorized budgets"}
    return bc.report(result)


def _builder_conflict(job, stage, bindings, attempts, plans):
    if stage["kind"] != "authoring_build" or bindings["inputs"]["request"] is None:
        return False
    current = bindings["inputs"]["request"]
    for old in attempts:
        if old["kind"] != "authoring_build" or old["puzzle_id"] != job["puzzle_id"] or old["status"] != "completed":
            continue
        old_job, _ = _find_stage(plans[old["plan_sha256"]], old["job_id"], old["stage_id"])
        previous = old["input_bindings"]["inputs"]["request"]
        if old_job["revision"] == job["revision"] and previous["sha256"] != current["sha256"]:
            return True
    return False


def _prior_elapsed(work, checkpoint, expected, *, initial=False):
    """Only complete invocation reports can extend the total observed duration."""
    path = work / "report.json"
    if not path.exists():
        return 0 if initial else None
    previous = bc.report(bio.json_read(path))
    old = bc.checkpoint(bio.json_bytes(expected, bio.MAX_JSON))
    views = [stage for job in previous["jobs"] for stage in job["stages"]]
    if (previous["batch_id"] != checkpoint["batch_id"] or previous["plan"] != old["plan"] or
            previous["status"] != old["status"] or views != old["stages"] or
            previous["attempts"] != checkpoint["attempts"]):
        return None  # A crash or unreported invocation left an unmeasured interval.
    return previous["elapsed_seconds"]


def _execute(plan, checkpoint, expected, plans, source, work, repo, history, actual_head, *, initial=False):
    previous_elapsed = _prior_elapsed(work, checkpoint, expected, initial=initial)
    started, available = time.monotonic(), {}
    checkpoint["stages"] = _views(plan)
    checkpoint["status"] = "incomplete"
    expected = bio.replace_json(work / "checkpoint.json", bc.checkpoint(checkpoint), expected)
    with _signals() as signals:
        for view in checkpoint["stages"]:
            if signals["stop"]:
                break
            job, stage = _find_stage(plan, view["job_id"], view["stage_id"])
            bio.require(_read_owner(work) == _owner(work, source, repo, history, plan["batch_id"]), "Owned root binding changed")
            spec = operations.OPERATION_SPECS[(stage["kind"], stage["operation"])]
            shared_phase, shared_error = False, False
            try:
                bindings, reason = _bindings(job, stage, available, source)
                if bindings is None:
                    view.update(status="blocked", reason=reason, next_step="Complete the required preceding stage")
                    continue
                missing = [key for key in spec["required_decisions"] if bindings["decisions"][key] is None]
                if missing:
                    view.update(status="waiting_human", reason="Missing actual decision: " + ", ".join(missing),
                                next_step="Supply the actual bound human decision in a successor plan")
                    continue
                if "request" in bindings["inputs"] and bindings["inputs"]["request"] is None:
                    human = stage["kind"] == "background"
                    view.update(status="waiting_human" if human else "waiting_input", reason="No complete original request supplied",
                                next_step="Supply the actual request in a successor plan")
                    continue
                _check_bindings(bindings, source, work)
                _job_identity(job, stage, bindings, source, work)
                fingerprint = _fingerprint(job, stage, bindings)
                view["fingerprint"] = fingerprint
                if stage["kind"] == "authoring_build":
                    request = bio.json_read(bio.artifact_path(bindings["inputs"]["request"], source, work))
                    bio.require(isinstance(request, dict) and isinstance(request.get("handoff"), dict) and
                                request["handoff"].get("puzzle_id") == job["puzzle_id"] and
                                request["handoff"].get("revision") == job["revision"], "Builder identity/revision differs from selected job")
                    bio.require(not _builder_conflict(job, stage, bindings, checkpoint["attempts"], plans),
                                "target_conflict: already built production revision has different request bytes")
                prior = [item for item in checkpoint["attempts"] if item["puzzle_id"] == job["puzzle_id"]
                         and item["kind"] == stage["kind"] and item["operation"] == stage["operation"]
                         and item["fingerprint"] == fingerprint and item["status"] == "completed"
                         and item["result"] is not None and item["result"]["status"] == "completed"]
                saved = prior[-1] if prior else None
                kind = "revalidate" if saved or not spec["produce"] else "produce"
                used = sum(item["puzzle_id"] == job["puzzle_id"] and item["kind"] == stage["kind"]
                           and item["operation"] == stage["operation"] and item["attempt_type"] == kind
                           for item in checkpoint["attempts"])
                if used >= stage["max_attempts"][kind]:
                    view.update(status="blocked", reason="budget_exhausted: " + kind,
                                next_step="A new explicit authorized order is required; resume cannot expand this budget")
                    continue
                number = len(checkpoint["attempts"]) + 1
                bio.require(number <= bc.MAX_ATTEMPTS, "Batch attempt ledger limit exhausted")
                directory = io.safe(work, f"attempts/{number:06d}")
                shared_phase = True
                output = directory / "output"
                reservation = {"format": "picross-batch-reservation-v1", "number": number,
                               "plan_sha256": checkpoint["plan"]["sha256"], "job_id": job["job_id"], "stage_id": stage["stage_id"],
                               "puzzle_id": job["puzzle_id"], "kind": stage["kind"], "operation": stage["operation"],
                               "attempt_type": kind, "fingerprint": fingerprint, "input_bindings": bindings,
                               "tool_binding": stage["tool_binding"], "reserved_limits": operations.reservation_limits(stage, kind),
                               "output_dir": output.relative_to(work).as_posix()}
                bc.reservation(reservation)
                staging = io.safe(work, "attempts/.batch-attempt-" + uuid.uuid4().hex)
                staging.mkdir()
                bio.sync_directory(work / "attempts")
                bio.write_json_new(staging / "reservation.json", reservation)
                bio.publish_new(staging, directory)
                attempt = _pending(reservation)
                attempt.update(status="running", error=None)
                checkpoint["attempts"].append(attempt)
                view.update(status="running", attempt=number, reused=False, reason=None, next_step="Wait for the reserved technical operation")
                expected = bio.replace_json(work / "checkpoint.json", bc.checkpoint(checkpoint), expected)
                # Execution can start only after durable ledger AND checkpoint.
                output.mkdir()
                try:
                    if saved:
                        _check_saved_outputs(saved, checkpoint["attempts"], work)
                    result, error, seconds, aborted = _worker(stage, bindings, output, repo, source, history,
                                                            saved["result"] if saved else None, work,
                                                            reservation["reserved_limits"], signals)
                    _check_bindings(bindings, source, work)
                    if result is not None:
                        result = _normalize_result(result, source, work)
                    attempt.update(status="aborted" if aborted else "failed" if error else "completed",
                                   result=result, seconds=seconds, error=error,
                                   inventory=bio.inventory(output))
                    bio.require(error is not None or aborted or result is not None, "Worker reported no result and no failure")
                except (Aborted, InvalidInput, ValueError, OSError) as exc:
                    attempt.update(status="failed", result=None, seconds=None, error=str(exc)[:4096],
                                   inventory=bio.inventory(output))
                bc.attempt(attempt)
                bio.write_json_new(directory / "result.json", attempt)
                status = attempt["result"]["status"] if attempt["status"] == "completed" else attempt["status"]
                view.update(status=status, reused=bool(saved) and status == "completed",
                            reason=attempt["error"] or (attempt["result"]["details"]["reason"] if attempt["result"] else None),
                            next_step="Technical result available; no content approval implied" if status == "completed"
                            else "Resolve the reported technical result before dependent steps")
                if status == "completed":
                    available[(job["job_id"], stage["stage_id"])] = attempt["result"]
                shared_phase = False
            except (Aborted, InvalidInput, ValueError, OSError) as exc:
                # Checkpoint publication/ledger inconsistency is shared state:
                # detect it below, never continue over an uncommitted attempt.
                if view["status"] == "running" or shared_phase:
                    shared_error = True
                    raise BatchTechnicalError(str(exc)) from exc
                view.update(status="failed", reason=str(exc)[:4096], next_step="Correct the explicit input; preserve existing outputs")
            finally:
                if not shared_error:
                    checkpoint["status"] = _overall(checkpoint["stages"], stopped=signals["stop"])
                    expected = bio.replace_json(work / "checkpoint.json", bc.checkpoint(checkpoint), expected)
        checkpoint["status"] = _overall(checkpoint["stages"], stopped=signals["stop"])
    expected = bio.replace_json(work / "checkpoint.json", bc.checkpoint(checkpoint), expected)
    elapsed = None if previous_elapsed is None else previous_elapsed + time.monotonic() - started
    report = _report(checkpoint, plan, actual_head, elapsed)
    previous = bio.read(work / "report.json") if (work / "report.json").exists() else None
    bio.replace_json(work / "report.json", report, previous)
    return report


def run(plan_path, source_root, work_root, repo_root, history_root=None):
    plan, raw, source, work, repo, history, actual_head = _prepare(plan_path, source_root, repo_root, work_root, history_root)
    bio.require(plan["revision"] == 1 and plan["source_commit"] == actual_head, "New run needs an initial plan at actual HEAD")
    _budget_history([plan])
    if not work.exists():
        work.mkdir()
    bio.require(work.is_dir() and not list(work.iterdir()), "run needs a new empty own work root")
    with _shared_work(), bio.writer(work):
        bio.write_json_new(work / "owner.json", _owner(work, source, repo, history, plan["batch_id"]))
        (work / "plans").mkdir()
        (work / "attempts").mkdir()
        ref = _plan_ref(plan, raw)
        bio.write_new(io.safe(work, ref["file"]), raw)
        checkpoint = {"format": "picross-batch-checkpoint-v1", "batch_id": plan["batch_id"],
                      "plan": ref, "plans": [ref], "attempts": [], "stages": _views(plan), "status": "incomplete"}
        expected = bio.replace_json(work / "checkpoint.json", bc.checkpoint(checkpoint), None)
        return _execute(plan, checkpoint, expected, {ref["sha256"]: plan}, source, work, repo, history, actual_head,
                        initial=True)


def resume(plan_path, source_root, work_root, repo_root, history_root=None):
    plan, raw, source, work, repo, history, actual_head = _prepare(plan_path, source_root, repo_root, work_root, history_root)
    bio.external(work)
    # Read-only ownership check before even opening our stable lock.
    bio.require(_read_owner(work) == _owner(work, source, repo, history, plan["batch_id"]), "Resume root does not belong to this order")
    with _shared_work(), bio.writer(work):
        with bio.writer(work, name=".batch-worker.lock"):
            pass  # A surviving worker must finish/exit before any new scheduling.
        incoming = _plan_ref(plan, raw)
        checkpoint, expected, plans = _history(work, repo, incoming=incoming)
        bio.require(checkpoint["batch_id"] == plan["batch_id"], "Resume batch identity mismatch")
        if incoming != checkpoint["plan"]:
            bio.require(plan["revision"] == checkpoint["plan"]["revision"] + 1 and
                        plan["previous_plan_sha256"] == checkpoint["plan"]["sha256"] and
                        plan["source_commit"] == actual_head, "Successor plan must bind exact previous bytes and current HEAD")
            _budget_history([*plans.values(), plan])
            destination = io.safe(work, incoming["file"])
            if destination.exists():
                bio.require(bio.read(destination, bc.PLAN_LIMIT) == raw, "Interrupted plan publication has different bytes")
            else:
                bio.write_new(destination, raw)
            checkpoint["plans"].append(incoming)
            checkpoint["plan"] = incoming
            checkpoint["stages"] = _views(plan)
            checkpoint["status"] = "incomplete"
            plans[incoming["sha256"]] = plan
        return _execute(plan, checkpoint, expected, plans, source, work, repo, history, actual_head)


def status(work_root):
    work = bio.external(work_root)
    owner = _read_owner(work)
    with _shared_work():
        checkpoint, _, plans = _history(work, Path(owner["repo_root"]))
        plan = plans[checkpoint["plan"]["sha256"]]
        return {"fresh": False, "report": _report(checkpoint, plan, plan["source_commit"], None)}
