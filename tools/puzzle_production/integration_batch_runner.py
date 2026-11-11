"""Serial BA-B orchestration, durable attempts, and read-only reconciliation.

No subprocess owns a domain operation. The checkout OS lock lives for exactly
the process making the native calls; no orphan worker can outlive that owner.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from io import BytesIO
import os
from pathlib import Path
import re
import signal
import subprocess
import threading
import time
import zipfile

from . import batch_io as bio, catalog_io as io, catalog_publication as publication
from . import catalog_transaction as tx, background_request as requests
from . import integration_batch_contract as bc
from . import integration_batch_operations as operations
from . import operation_diagnostics as diagnostic
from .contract import Aborted, InvalidInput, canonical_bytes, exact_keys

EXIT_CODES = bc.EXIT_CODES
CONTROL = ".picross-integration-batches"
PENDING = re.compile(r"\.batch-pending-[0-9a-f]{32}\.json\Z")


class BatchTechnicalError(RuntimeError):
    """Untrusted shared bookkeeping: preserve all bytes and stop scheduling."""


def checkpoint(name):
    """A deterministic test observation boundary; never supplies a success."""
    io.tick()


def _hash(value):
    return bio.sha(canonical_bytes(value))


def _head(repo):
    result = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                            capture_output=True, text=True, timeout=10, check=False)
    value = result.stdout.strip()
    bio.require(result.returncode == 0 and bc.local.COMMIT.fullmatch(value), "Missing actual tool checkout HEAD")
    return value


def _file(ref, source):
    path = io.safe(source, ref["file"])
    raw = bio.read(path, bio.MAX_FILE)
    bio.require(len(raw) == ref["bytes"] and bio.sha(raw) == ref["sha256"],
                "Declared original bytes changed: " + ref["file"])
    return path, raw


def _ref(ref, source):
    if ref is None:
        return None
    if "directory" in ref:
        path = source if ref["directory"] == "." else io.safe(source, ref["directory"])
        bio.require(bio.inventory(path) == ref["files"], "Original bundle inventory changed: " + ref["directory"])
        return path
    return _file(ref, source)[0]


def _metadata(job, source):
    """Cheap identity/authority checks; the native export still checks proofs."""
    inputs = job["inputs"]
    if job["operation"] == "background_adopt":
        if inputs["request"] is None:
            return
        request_path, raw = _file(inputs["request"], source)
        request = requests.validate(bio.json_bytes(raw, requests.LIMIT))
        bio.require(request["puzzle_id"] == job["puzzle_id"] and request["revision"] == job["revision"],
                    "Background request differs from selected identity/revision")
        work = _ref(inputs["work"], source)
        if work is not None:
            requests.payload(work, request, raw, record_present=(work / "record.json").exists())
        return
    order = None
    if job["authorization"] is not None:
        _, raw = _file(job["authorization"], source)
        order = bc.order(bio.json_bytes(raw), job)
        _file(order["evidence"], source)
    package = _ref(inputs["package"], source)
    if package is None:
        return
    if package.is_dir():
        handoff_raw = bio.read(io.safe(package, "handoff.json"))
    else:
        try:
            with zipfile.ZipFile(BytesIO(bio.read(package, bio.MAX_FILE))) as archive:
                names = [item.filename for item in archive.infolist() if not item.is_dir()]
                # Preserve ZA-1's optional single enclosing ZIP directory. This
                # reads metadata only; native open_files still checks the complete
                # ZIP namespace, types, decoded sizes and CRC before publication.
                roots = {name.split("/")[0] for name in names}
                entry = "handoff.json" if "handoff.json" in names else next(iter(roots)) + "/handoff.json" if len(roots) == 1 else None
                bio.require(entry is not None and names.count(entry) == 1, "Package needs one native handoff.json under its single root")
                info = archive.getinfo(entry)
                bio.require(info.file_size <= bio.MAX_JSON, "Package handoff exceeds bounded JSON")
                handoff_raw = archive.read(info)
        except Aborted:
            raise
        except (zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError) as exc:
            raise InvalidInput("Malformed original package ZIP: " + str(exc)[:1024]) from exc
    handoff = bio.json_bytes(handoff_raw)
    bio.require(isinstance(handoff, dict) and handoff.get("puzzle_id") == job["puzzle_id"] and
                handoff.get("revision") == job["revision"], "Package identity/revision differs from selected job")
    if inputs["handoff"] is not None:
        bio.require(_file(inputs["handoff"], source)[1] == handoff_raw, "Separate handoff is not the original package handoff")
    if order is not None:
        bio.require(order["test_only"] == handoff.get("test_only", False), "Integration order test scope differs from package")
    if inputs["approval"] is not None:
        approval = bio.json_bytes(_file(inputs["approval"], source)[1])
        bio.require(isinstance(approval, dict) and all(approval.get(k) == job[k] for k in ("puzzle_id", "revision")),
                    "Declared final approval covers another identity/revision")
    if inputs["record"] is not None:
        record = bio.json_bytes(_file(inputs["record"], source)[1])
        bio.require(isinstance(record, dict) and record.get("format") in ("picross-authoring-record-v1", "picross-authoring-record-v2") and
                    all(record.get(k) == job[k] for k in ("puzzle_id", "revision")), "Declared authoring record covers another original")
    rule = handoff.get("rulebook", {})
    bio.require(isinstance(rule, dict), "Package rulebook must be an object")
    # Historical native forms remain native. If a package declares these
    # current authoring versions, its original rule snapshot must agree.
    if rule.get("version") in ("0.6.0", "0.7.0"):
        bio.require(rule["version"] == job["rulebook"]["version"] and
                    rule.get("sha256") == job["rulebook"]["snapshot"]["sha256"],
                    "Package rulebook differs from the actual batch snapshot")
    return handoff


def _check_job(job, source):
    rule = job["rulebook"]
    _, raw = _file(rule["snapshot"], source)
    pattern = rb"(?m)^\*\*Version " + re.escape(rule["version"].encode()) + rb" \xc2\xb7 Dokumentrevision " + str(rule["document_revision"]).encode() + rb" \xc2\xb7"
    bio.require(re.search(pattern, raw), "Rulebook original version/document revision mismatch")
    _ref(job["authorization"], source)
    for ref in job["inputs"].values():
        _ref(ref, source)
    _metadata(job, source)


def _roots(source_root, repo_root, target_root, work_root, history_root):
    source, repo, target = (bio.external(x) for x in (source_root, repo_root, target_root))
    history = bio.external(history_root) if history_root is not None else None
    work = io.external(work_root) if work_root is not None else None
    if work is not None:
        for other in (source, repo, target, history):
            if other is not None:
                a, b = str(work).casefold(), str(other).casefold()
                bio.require(a != b and not a.startswith(b + os.sep) and not b.startswith(a + os.sep),
                            "Integration work root overlaps an input/tool/target/history root")
    return source, repo, target, work, history


def _prepare(plan_path, source_root, repo_root, target_root, work_root=None, history_root=None):
    source, repo, target, work, history = _roots(source_root, repo_root, target_root, work_root, history_root)
    path = bio.external(plan_path, directory=False)
    if work is not None:
        bio.require(not path.is_relative_to(work), "Original plan cannot be inside the writable work root")
    raw = bio.read(path, bc.PLAN_LIMIT)
    plan = bc.validate_plan(bio.json_bytes(raw, bc.PLAN_LIMIT))
    # Check the complete selection before any domain writer or attempt begins.
    for job in plan["jobs"]:
        _check_job(job, source)
    actual_head = _head(repo)
    known = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", plan["source_commit"] + "^{commit}"],
                           capture_output=True, timeout=10, check=False, env={**os.environ, "GIT_NO_LAZY_FETCH": "1"})
    bio.require(known.returncode == 0, "Unknown original tool provenance commit")
    tool = operations.tool_binding(repo)
    bc.tool_binding(tool)
    return plan, raw, source, repo, target, work, history, actual_head, tool


def validate(plan_path, source_root, repo_root, target_root, work_root=None, history_root=None):
    plan, raw, *rest = _prepare(plan_path, source_root, repo_root, target_root, work_root, history_root)
    return {"status": "valid", "batch_id": plan["batch_id"], "plan_sha256": bio.sha(raw),
            "jobs": len(plan["jobs"]), "tool_binding": rest[-1], "fresh": True}


def _plan_ref(plan, raw):
    sha = bio.sha(raw)
    return {"revision": plan["revision"], "file": f"plans/{plan['revision']:06d}-{sha}.json", "sha256": sha, "bytes": len(raw)}


def _input_hash(job):
    return _hash({k: v for k, v in job.items() if k not in ("job_id", "budgets", "max_attempts")})


def _view(job):
    return {"job_id": job["job_id"], "puzzle_id": job["puzzle_id"], "operation": job["operation"],
            "status": "pending", "historical_completed": False, "current_verified": False,
            "attempt": None, "reached": None, "reason": None, "next_step": "Execute explicitly selected native operation"}


def _bindings(source, repo, target, work, history, tool):
    return {"source_root": str(source), "repo_root": str(repo), "target_root": str(target), "work_root": str(work),
            "history_root": str(history) if history else None, "work_identity": bio.identity(work),
            "target_identity": bio.identity(target), "tool_binding": tool}


@contextmanager
def _control(target):
    root = io.safe(target, CONTROL)
    try:
        root.mkdir()
        bio.sync_directory(target)
    except FileExistsError:
        bio.external(root)
    with bio.writer(root):
        owner = {"format": bc.PREFIX + "control-v1", "target_root": str(target), "target_identity": bio.identity(target)}
        path = root / "owner.json"
        if path.exists():
            bio.require(bio.json_read(path) == owner, "Foreign checkout control owner")
        else:
            bio.require({p.name for p in root.iterdir()} <= {".batch-writer.lock"}, "Unowned checkout control directory")
            bio.write_json_new(path, owner)
        for name in ("claims", "anchors"):
            child = io.safe(root, name)
            child.mkdir(exist_ok=True)
        yield root


def _claim(control, job, work):
    ref = job["authorization"]
    if ref is None: return
    lineage = _hash({"puzzle_id": job["puzzle_id"], "operation": job["operation"], "authorization_sha256": ref["sha256"]})
    expected = {"format": bc.PREFIX + "claim-v1", "lineage": lineage, "puzzle_id": job["puzzle_id"],
                "operation": job["operation"], "authorization_sha256": ref["sha256"],
                "work_root": str(work), "work_identity": bio.identity(work)}
    path = io.safe(control, "claims/" + lineage + ".json")
    if path.exists():
        bio.require(bio.json_read(path) == expected, "Order lineage already belongs to another work root; allowance cannot reset")
    else:
        bio.write_json_new(path, expected)


def _budget_history(plans):
    seen = {}
    for plan in plans.values():
        for job in plan["jobs"]:
            key = job["puzzle_id"], job["operation"]
            current = {**job["budgets"], **job["max_attempts"]}
            if key in seen:
                bio.require(all(current[k] <= seen[key][k] for k in current), "Plan revision cannot refill or expand an existing order allowance")
            seen[key] = current


def _journal(target):
    pending = io.safe(target, tx.LOCK)
    return {"pending": tx.LOCK if pending.exists() else None, "staging": publication.staging(target)}


def _safe_target(target):
    # Use exactly the native shared admission check, including staging journals.
    state = _journal(target)
    bio.require(state["pending"] is None and not state["staging"], "Interrupted registration: recovery required (journal or staging)")
    return state


def _anchor_value(cp, work, *, count=None, omit_result=None):
    count = len(cp["attempts"]) if count is None else count
    reservations, results, acknowledged = [], [], []
    for n in range(1, count + 1):
        folder = work / "attempts" / f"{n:06d}"
        reservations.append(bio.sha(bio.read(folder / "reservation.json")))
        path = folder / "result.json"
        acknowledged.append(cp["attempts"][n-1]["result"] is not None and n != omit_result)
        results.append(bio.sha(bio.read(path)) if path.exists() and n != omit_result else None)
    return {"format": bc.PREFIX + "anchor-v1", "batch_id": cp["batch_id"], "work_root": str(work),
            "work_identity": bio.identity(work), "plan_sha256": cp["plan"]["sha256"], "attempts": count,
            "reservations_sha256": _hash(reservations), "results_sha256": _hash(results),
            "acknowledged_sha256": _hash(acknowledged)}


class _Ledger:
    def __init__(self, cp, work, control, expected=None, anchor_expected=None):
        self.cp, self.work, self.control = cp, work, control
        self.expected, self.anchor_expected = expected, anchor_expected
        self.anchor_path = io.safe(control, "anchors/" + cp["batch_id"] + ".json")

    def save(self):
        bc.checkpoint(self.cp)
        checkpoint("before-checkpoint-publication")
        self.expected = bio.replace_json(self.work / "checkpoint.json", self.cp, self.expected)
        checkpoint("before-anchor-publication")
        self.anchor_expected = bio.replace_json(self.anchor_path, _anchor_value(self.cp, self.work), self.anchor_expected)

    def reserve(self, job, phase, tool):
        earlier = [a for a in self.cp["attempts"] if (a["reservation"]["puzzle_id"], a["reservation"]["operation"], a["reservation"]["phase"]) ==
                   (job["puzzle_id"], job["operation"], phase)]
        ordinal = len(earlier) + 1
        bio.require(ordinal <= job["max_attempts"][phase], "budget_exhausted: " + phase)
        number = len(self.cp["attempts"]) + 1
        bio.require(number <= bc.MAX_ATTEMPTS, "budget_exhausted: attempt ledger limit")
        reservation = {"format": bc.PREFIX + "reservation-v1", "number": number,
                       "plan_sha256": self.cp["plan"]["sha256"], "job_id": job["job_id"], "puzzle_id": job["puzzle_id"],
                       "operation": job["operation"], "phase": phase, "ordinal": ordinal,
                       "inputs_sha256": _input_hash(job), "tool_sha256": _hash(tool), "budgets": deepcopy(job["budgets"]),
                       "output_dir": f"attempts/{number:06d}/output"}
        bc.reservation(reservation)
        folder = io.safe(self.work, f"attempts/{number:06d}")
        folder.mkdir()
        bio.sync_directory(folder.parent)
        bio.write_json_new(folder / "reservation.json", reservation)
        output = io.safe(self.work, reservation["output_dir"])
        output.mkdir()
        bio.sync_directory(folder)
        attempt = {"reservation": reservation, "result": None}
        self.cp["attempts"].append(attempt)
        self.cp["status"] = "incomplete"
        self.save()  # Native execution cannot precede all three durable records.
        checkpoint("after-reservation")
        return attempt, output

    def book(self, attempt, result):
        bc.result(result)
        folder = self.work / "attempts" / f"{attempt['reservation']['number']:06d}"
        checkpoint("before-result-publication")
        bio.write_json_new(folder / "result.json", result)
        attempt["result"] = result
        self.save()
        checkpoint("after-result-publication")


def _namespace(work):
    allowed = {"owner.json", "plans", "attempts", "checkpoint.json", "report.json"}
    for path in work.iterdir():
        io.safe(work, path.name)
        bio.require(path.name in allowed or PENDING.fullmatch(path.name), "Unknown file in integration work root")


def _history(work, control, incoming=None):
    _namespace(work)
    owner = bc.owner(bio.json_read(work / "owner.json"))
    bio.require(owner["bindings"]["work_root"] == str(work) and owner["bindings"]["work_identity"] == bio.identity(work), "Work ownership changed")
    raw = bio.read(work / "checkpoint.json")
    cp = bc.checkpoint(bio.json_bytes(raw))
    bio.require(cp["bindings"] == owner["bindings"] and cp["batch_id"] == owner["batch_id"], "Checkpoint owner mismatch")
    plans, previous = {}, None
    for index, ref in enumerate(cp["plans"], 1):
        plan_raw = bio.read(io.safe(work, ref["file"]), bc.PLAN_LIMIT)
        bio.require(len(plan_raw) == ref["bytes"] and bio.sha(plan_raw) == ref["sha256"], "Original plan bytes changed")
        plan = bc.validate_plan(bio.json_bytes(plan_raw, bc.PLAN_LIMIT))
        bio.require(_plan_ref(plan, plan_raw) == ref and plan["revision"] == index and plan["previous_plan_sha256"] == previous and
                    plan["batch_id"] == cp["batch_id"], "Broken integration plan chain")
        plans[ref["sha256"]] = plan; previous = ref["sha256"]
    allowed_plans = {Path(p["file"]).name for p in cp["plans"]}
    if incoming is not None: allowed_plans.add(Path(incoming["file"]).name)
    bio.require({p.name for p in (work / "plans").iterdir() if not PENDING.fullmatch(p.name)} <= allowed_plans, "Unaccounted plan history")
    _budget_history(plans)
    folders = sorted((work / "attempts").iterdir(), key=lambda p: p.name)
    bio.require(len(folders) <= bc.MAX_ATTEMPTS, "Attempt history exceeds bound")
    attempts = []
    observed_results = {}
    saved_attempts = cp["attempts"]
    for n, folder in enumerate(folders, 1):
        bio.require(folder.name == f"{n:06d}" and io.safe(work, "attempts/" + folder.name).is_dir(), "Missing/noncontiguous ledger")
        for child in folder.iterdir():
            io.safe(folder, child.name)
            bio.require(child.name in {"reservation.json", "result.json", "output"} or PENDING.fullmatch(child.name), "Foreign ledger file")
        reservation = bc.reservation(bio.json_read(folder / "reservation.json"))
        bio.require(reservation["number"] == n and reservation["plan_sha256"] in plans, "Reservation not bound to original plan")
        plan = plans[reservation["plan_sha256"]]
        job = next((j for j in plan["jobs"] if j["job_id"] == reservation["job_id"]), None)
        bio.require(job is not None and all(job[k] == reservation[k] for k in ("puzzle_id", "operation", "budgets")) and
                    _input_hash(job) == reservation["inputs_sha256"] and reservation["tool_sha256"] == _hash(cp["bindings"]["tool_binding"]),
                    "Reservation contradicts its actual original bindings")
        ordinal = 1 + sum((a["reservation"]["puzzle_id"], a["reservation"]["operation"], a["reservation"]["phase"]) ==
                          (reservation["puzzle_id"], reservation["operation"], reservation["phase"]) for a in attempts)
        bio.require(reservation["ordinal"] == ordinal <= job["max_attempts"][reservation["phase"]], "Forged or refilled allowance")
        result = bc.result(bio.json_read(folder / "result.json")) if (folder / "result.json").exists() else None
        actual = {"reservation": reservation, "result": result}; bc.attempt(actual)
        if n <= len(saved_attempts):
            saved = saved_attempts[n-1]
            bio.require(saved["reservation"] == reservation and (saved["result"] is None or saved == actual), "Checkpoint contradicts immutable result ledger")
        observed_results[n] = result
        # An immutable result file can precede checkpoint/anchor publication.
        # A file alone is not an acknowledged result and cannot become a saved
        # success merely because a new process can parse it.
        if n > len(saved_attempts) or saved_attempts[n-1]["result"] is None:
            actual = {"reservation": reservation, "result": None}
        attempts.append(actual)
    bio.require(len(cp["attempts"]) <= len(attempts), "Truncated integration attempt history")
    current = plans[cp["plan"]["sha256"]]
    bio.require([(j["job_id"], j["puzzle_id"], j["operation"]) for j in cp["jobs"]] ==
                [(j["job_id"], j["puzzle_id"], j["operation"]) for j in current["jobs"]], "Checkpoint selection differs")
    cp["attempts"] = attempts
    anchor_path = io.safe(control, "anchors/" + cp["batch_id"] + ".json")
    anchor_raw = bio.read(anchor_path); anchor = bio.json_bytes(anchor_raw)
    exact_keys(anchor, set(_anchor_value(cp, work)))
    count = anchor["attempts"]
    bio.require(type(count) is int and 0 <= count <= len(attempts) <= count + 1, "External anchor detects truncated/foreign ledger")
    bio.require(all(observed_results[n] is None for n in range(count + 1, len(attempts) + 1)),
                "A not-yet-anchored reservation cannot have a native result")
    anchor_plans = [cp["plan"]["sha256"]]
    if len(cp["plans"]) > 1 and not any(a["reservation"]["plan_sha256"] == cp["plan"]["sha256"] for a in attempts):
        # A successor checkpoint can precede its anchor. No reservation for
        # that revision can exist before the anchor is published; only the
        # exact direct predecessor and otherwise identical ledger may lag.
        anchor_plans.append(cp["plans"][-2]["sha256"])

    def anchored(omit_result=None):
        expected = _anchor_value(cp, work, count=count, omit_result=omit_result)
        return any(anchor == {**expected, "plan_sha256": plan_hash} for plan_hash in anchor_plans)

    if not anchored():
        # Exactly one book may have updated the checkpoint before the external
        # anchor, including a non-last member of a pre-reserved reader group.
        candidates = [n for n in range(1, count + 1) if observed_results[n] is not None and anchored(n)]
        bio.require(len(candidates) == 1, "External ledger anchor changed or history was truncated")
        attempts[candidates[0]-1]["result"] = None
    for index, view in enumerate(cp["jobs"]):
        if view["historical_completed"]:
            bio.require(view["attempt"] is not None and view["attempt"] <= len(attempts), "Forged success without attempt")
            a = attempts[view["attempt"]-1]
            current_job = current["jobs"][index]
            bio.require(a["reservation"]["puzzle_id"] == view["puzzle_id"] and a["reservation"]["operation"] == current_job["operation"] and
                        a["reservation"]["inputs_sha256"] == _input_hash(current_job), "Forged historical operation/input binding")
            if a["result"] is None:
                cp["jobs"][index] = _view(current_job)
                cp["jobs"][index].update(status="interrupted", reason="Unanchored result file is not a completion proof",
                                         next_step="Perform the appropriate native read-only reconciliation")
                cp["status"] = "incomplete"
            else:
                bio.require(a["result"]["reached"] == view["reached"] and view["reached"] is not None and
                            a["result"]["status"] == "completed", "Forged historical target success")
    _writer_barriers(cp, current)
    return _Ledger(cp, work, control, raw, anchor_raw), plans


@contextmanager
def _signals():
    state = {"stop": False}
    old = {}
    if threading.current_thread() is threading.main_thread():
        def stop(signum, _frame):
            # One cooperative interruption lets the native writer complete its
            # own separately budgeted rollback. SIGKILL remains a hard crash.
            if not state["stop"]:
                state["stop"] = True
                raise Aborted("interrupted: signal " + str(signum))
        for sig in (signal.SIGINT, signal.SIGTERM):
            old[sig] = signal.signal(sig, stop)
    try:
        yield state
    finally:
        for sig, handler in old.items(): signal.signal(sig, handler)


def _line_attempts(cp, job):
    return [a for a in cp["attempts"] if a["reservation"]["puzzle_id"] == job["puzzle_id"] and
            a["reservation"]["operation"] == job["operation"] and a["reservation"]["inputs_sha256"] == _input_hash(job)]


def _successful_target(attempt):
    result = attempt["result"]
    return result is not None and result["status"] == "completed" and result["reached"] is not None


def _historical_views(cp, plan):
    views = []
    for job in plan["jobs"]:
        view = _view(job)
        successful = [a for a in _line_attempts(cp, job) if _successful_target(a)]
        if successful:
            attempt = successful[-1]
            view.update(status="stale", historical_completed=True, current_verified=False,
                        attempt=attempt["reservation"]["number"], reached=deepcopy(attempt["result"]["reached"]),
                        reason="Historical completion requires fresh target reconciliation", next_step="Read-only current target reconciliation")
        views.append(view)
    return views


def _writer_barriers(cp, plan):
    """A successor cannot discard or overtake an unresolved native writer."""
    completed = {a["reservation"]["inputs_sha256"] for a in cp["attempts"] if _successful_target(a)}
    pending = {a["reservation"]["inputs_sha256"] for a in cp["attempts"]
               if a["reservation"]["phase"] in ("store", "apply", "adopt") and
               (a["result"] is None or a["result"]["status"] != "completed") and
               a["reservation"]["inputs_sha256"] not in completed}
    selected = [_input_hash(job) for job in plan["jobs"]]
    for binding in pending:
        bio.require(binding in selected, "Successor cannot omit or replace an unresolved writer")
        before = selected[:selected.index(binding)]
        bio.require(all(value in completed for value in before), "Successor cannot overtake an unresolved writer with a new job")


def _success(phase, operation, native):
    if not isinstance(native, dict): return False
    status = native.get("status")
    if phase == "export": return str(native.get("format", "")).startswith("picross-target-export-v")
    if phase == "store": return status in ("stored", "no-op")
    if phase == "plan": return status in ("planned", "no-op")
    if operation == "register":
        return (status in ("registered", "no-op") and native.get("registered") is True) or phase == "reconcile" and status == "planned"
    return status in ("adopted", "no-op") or phase == "reconcile" and status == "rollback-confirmed"


def _finished(phase, operation, native):
    if not isinstance(native, dict): return False
    if operation == "register":
        return phase in ("plan", "apply", "reconcile") and native.get("registered") is True and native.get("status") in ("registered", "no-op")
    return phase in ("adopt", "reconcile") and native.get("status") in ("adopted", "no-op")


def _native_error(native):
    error = native.get("error") if isinstance(native, dict) else None
    return str(error or "Native operation did not reach its required result")[:4096]


def _remaining(value):
    if value is None: return []
    if isinstance(value, (str, Path)): return [str(value)]
    bio.require(isinstance(value, (list, tuple)) and all(isinstance(p, (str, Path)) for p in value), "Invalid native remaining paths")
    return [str(p) for p in value]


def _result(number, diagnostics, started, *, native=None, error=None, status="completed", reached=None, output=None, remaining=None):
    result = {"format": bc.PREFIX + "result-v1", "number": number, "status": status,
              "native": native, "diagnostics": diagnostics.result(),
              "elapsed_seconds": time.monotonic() - started, "error": error,
              "exit_code": 0 if status == "completed" else 4 if status == "aborted" else 3 if status == "recovery_required" else 2 if status == "blocked" else 5,
              "reached": reached, "output_files": bio.inventory(output) if output is not None else [],
              "remaining": remaining or []}
    return bc.result(result)


def _complete_view(view, attempt):
    view.update(status="completed", historical_completed=True, current_verified=True,
                attempt=attempt["reservation"]["number"], reached=deepcopy(attempt["result"]["reached"]),
                reason=None, next_step="Checkout target confirmed; Git publication remains a separate authorized task")


def _call(ledger, job, view, phase, source, repo, target, history, tool, *, export_dir=None, plan_path=None):
    _safe_target(target)
    _check_job(job, source)
    bio.require(operations.tool_binding(repo) == tool, "Relevant tool bytes changed during batch")
    try:
        attempt, output = ledger.reserve(job, phase, tool)
    except InvalidInput as exc:
        if str(exc).startswith("budget_exhausted"):
            view.update(status="blocked", current_verified=False, reason=str(exc), next_step="Explicitly resolve exhausted order allowance; no automatic retry")
            ledger.save()
            return None
        raise
    view.update(status="running", current_verified=False, attempt=attempt["reservation"]["number"], reason=None,
                next_step="Wait for the current native operation")
    ledger.save()
    diagnostics = diagnostic.Diagnostics("integration-batch-" + phase,
        {"job_id": job["job_id"], "puzzle_id": job["puzzle_id"], "operation": job["operation"], "phase": phase})
    diagnostics.environment["tool_commit"] = _head(repo)
    started = time.monotonic()
    native, reached, error, status, remaining = None, None, None, "completed", []
    try:
        with diagnostic.observe(diagnostics):
            checkpoint("before-native-call")
            native = operations.execute(phase, job, source, target, output, history, export_dir=export_dir, plan_path=plan_path)
            checkpoint("after-native-call")
            if not _success(phase, job["operation"], native):
                status = "recovery_required" if native.get("recovery_required") else "blocked"
                error = _native_error(native)
                remaining = _remaining(native.get("remaining"))
            else:
                if _finished(phase, job["operation"], native):
                    reached = operations.reached(target, job["puzzle_id"])
                _check_job(job, source)
                bio.require(operations.tool_binding(repo) == tool, "Relevant tool bytes changed during native call")
                diagnostics.outcome = diagnostics.outcome if diagnostics.outcome != "blocked-before-mutation" else native.get("status", "exported")
    except (Aborted, KeyboardInterrupt) as exc:
        error, status = str(exc)[:4096] or "interrupted", "aborted"
        remaining = _remaining(getattr(exc, "remaining", None))
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)[:3900]
        status = "aborted" if getattr(exc, "aborted", False) else "blocked" if isinstance(exc, InvalidInput) or getattr(exc, "code", None) == "conflict" else "failed"
        remaining = _remaining(getattr(exc, "remaining", None))
    journal = _journal(target)
    if journal["pending"] is not None or journal["staging"]:
        status = "recovery_required"
        error = error or "Native journal/staging requires separately authorized recovery"
        remaining += ([journal["pending"]] if journal["pending"] else []) + journal["staging"]
    diagnostics.journal_state = {"journal": "present" if journal["pending"] else "absent",
                                 "lock": "journal-staging" if journal["staging"] else "no-staging"}
    # A successful native P6 remains in native/diagnostics even if later byte
    # reconciliation failed. Never relabel it as a rollback.
    result = _result(attempt["reservation"]["number"], diagnostics, started, native=native, error=error,
                     status=status, reached=reached, output=output, remaining=sorted(set(remaining)))
    ledger.book(attempt, result)
    if _successful_target(attempt):
        _complete_view(view, attempt)
    elif status != "completed":
        view.update(status=status, current_verified=False, reason=error,
                    next_step="Run separately authorized native recovery, then explicit resume" if status == "recovery_required" else
                              "Inspect preserved native result and originals; resume only after resolving the blocker")
    else:
        view.update(status="pending", current_verified=False, next_step="Continue the next fixed native phase")
    ledger.save()
    return attempt


def _output(attempt, work, suffix, *, check=True):
    path = io.safe(work, attempt["reservation"]["output_dir"])
    if check and attempt["result"] is not None:
        bio.require(bio.inventory(path) == attempt["result"]["output_files"], "Saved native output changed or contains foreign bytes")
    return io.safe(path, suffix)


def _latest(attempts, phase, *, successful=False):
    found = [a for a in attempts if a["reservation"]["phase"] == phase and
             (not successful or a["result"] is not None and a["result"]["status"] == "completed")]
    return found[-1] if found else None


def _reconcile_completed(ledger, plan, source, repo, target, tool):
    selected = [(job, view) for job, view in zip(plan["jobs"], ledger.cp["jobs"]) if view["historical_completed"]]
    if not selected: return True
    reservations = []
    for job, view in selected:
        _check_job(job, source)
        try:
            attempt, output = ledger.reserve(job, "reconcile", tool)
        except InvalidInput as exc:
            if not str(exc).startswith("budget_exhausted"): raise
            view.update(status="blocked", current_verified=False, reason=str(exc), next_step="Resolve the finite reconciliation allowance")
            ledger.save(); return False
        reservations.append((job, view, attempt, output))
    snapshot = None
    for index, (job, view, attempt, output) in enumerate(reservations):
        diagnostics = diagnostic.Diagnostics("integration-batch-reconcile-completed", {"puzzle_id": job["puzzle_id"]})
        diagnostics.environment["tool_commit"] = _head(repo)
        started = time.monotonic(); native = None; current = None; error = None; failure = "blocked"
        try:
            with diagnostic.observe(diagnostics), io.budget(300):
                if index == 0:
                    snapshot = tx.capture(target)  # Exactly one full current catalog read for this group.
                current = operations.reached(target, job["puzzle_id"], snapshot=snapshot)
                bio.require(current == view["reached"], "stale: reached job target changed after its historical success")
                _check_job(job, source)
                bio.require(operations.tool_binding(repo) == tool, "stale: relevant tool bytes changed")
                native = {"status": "reconciled", "id": job["puzzle_id"], "reached": current}
                diagnostics.outcome = "reconciled"
        except (Aborted, KeyboardInterrupt) as exc:
            error, failure = str(exc)[:4096] or "interrupted", "aborted"
        except (InvalidInput, ValueError) as exc:
            error = str(exc)[:4096]
        except Exception as exc:
            error, failure = type(exc).__name__ + ": " + str(exc)[:3900], "failed"
        result = _result(attempt["reservation"]["number"], diagnostics, started, native=native, error=error,
                         status="completed" if error is None else failure, reached=current if error is None else None, output=output)
        ledger.book(attempt, result)
        if error is not None:
            view.update(status="stale" if failure == "blocked" else failure, current_verified=False, reason=error,
                        next_step="Diagnose the preserved target and actual interruption/error; do not restore historical images or metadata")
            ledger.save(); return False
        _complete_view(view, attempt)
        ledger.save()
    return True


def _execute_job(ledger, job, view, source, repo, target, history, tool, *, resumed):
    if job["authorization"] is None:
        view.update(status="waiting_human", reason="Missing actual integration/background authorization",
                    next_step="Provide the already declared matching original order in an explicit successor plan")
        return
    inputs = job["inputs"]
    required = ("package",) if job["operation"] == "register" else ("request", "work")
    if any(inputs[key] is None for key in required):
        view.update(status="waiting_input", reason="Missing prepared original input",
                    next_step="Provide the complete unchanged native original through a successor plan")
        return
    if job["operation"] == "register" and inputs["approval"] is None:
        handoff = _metadata(job, source)
        if handoff.get("final_editorial_approval") is None:
            view.update(status="waiting_human", reason="Missing actual final editorial approval",
                        next_step="Provide the original matching final approval; no export or integration before that declaration")
            return
    history_attempts = _line_attempts(ledger.cp, job)
    if job["operation"] == "register":
        export = _latest(history_attempts, "export", successful=True)
        if export is None:
            # Neither a self-consistent foreign export nor an unbooked local
            # export is bound to this job. Preserve it, consume a remaining
            # local export allowance on this explicit resume, and only use the
            # newly produced, durably inventoried native result.
            export = _call(ledger, job, view, "export", source, repo, target, history, tool)
            if export is None or export["result"]["status"] != "completed": return
        export_dir = _output(export, ledger.work, "export")
        unbooked = _latest(history_attempts, "apply")
        if resumed and unbooked is not None and not _successful_target(unbooked):
            checked = _call(ledger, job, view, "reconcile", source, repo, target, history, tool, export_dir=export_dir)
            if checked is None or checked["result"]["status"] != "completed" or view["status"] == "completed": return
            # A freshly checked planned (not no-op) result proves a valid old
            # checkout after external/native rollback. Only this explicit
            # resume may spend a remaining new attempt, never an internal retry.
        planned = _call(ledger, job, view, "plan", source, repo, target, history, tool, export_dir=export_dir)
        if planned is None or planned["result"]["status"] != "completed" or view["status"] == "completed": return
        _call(ledger, job, view, "apply", source, repo, target, history, tool, export_dir=export_dir)
        return
    unbooked = _latest(history_attempts, "adopt")
    if resumed and unbooked is not None and not _successful_target(unbooked):
        previous_plan = _latest(history_attempts, "plan", successful=True)
        if previous_plan is None:
            view.update(status="interrupted", reason="Interrupted adoption lacks its immutable native plan bundle",
                        next_step="Diagnose the preserved plan/ledger; no automatic new adoption")
            return
        plan_path = _output(previous_plan, ledger.work, "plan")
        checked = _call(ledger, job, view, "reconcile", source, repo, target, history, tool, plan_path=plan_path)
        if checked is None or checked["result"]["status"] != "completed" or checked["result"]["native"].get("status") != "rollback-confirmed":
            return
        # Only this explicitly requested resume, after a complete native old
        # snapshot confirmation, may consume a remaining fresh plan/adopt try.
    stored = _latest(history_attempts, "store", successful=True)
    if stored is None:
        stored = _call(ledger, job, view, "store", source, repo, target, history, tool)
        if stored is None or stored["result"]["status"] != "completed": return
    planned = _call(ledger, job, view, "plan", source, repo, target, history, tool)
    if planned is None or planned["result"]["status"] != "completed": return
    _call(ledger, job, view, "adopt", source, repo, target, history, tool,
          plan_path=_output(planned, ledger.work, "plan"))


def _report(cp, plan, target, elapsed, *, fresh=True, journal=None):
    def total(reconcile):
        selected = [a for a in cp["attempts"] if (a["reservation"]["phase"] == "reconcile") == reconcile]
        if any(a["result"] is None or a["result"]["elapsed_seconds"] is None for a in selected): return None
        return sum(a["result"]["elapsed_seconds"] for a in selected)
    unknown = any(a["result"] is None for a in cp["attempts"])
    value = {"format": bc.PREFIX + "report-v1", "batch_id": cp["batch_id"], "plan": cp["plan"],
             "source_commit": plan["source_commit"], "tool_binding": cp["bindings"]["tool_binding"],
             "status": cp["status"], "exit_code": EXIT_CODES[cp["status"]], "jobs": deepcopy(cp["jobs"]),
             "attempts": deepcopy(cp["attempts"]), "journal": journal if journal is not None else _journal(target),
             "elapsed_seconds": None if unknown or not fresh else elapsed,
             "execution_seconds": total(False), "reconciliation_seconds": total(True),
             "waiting_seconds": None, "human_seconds": None, "fresh": fresh,
             "next_step": "Independent review of the reached checkout; no Git/Main assertion" if cp["status"] == "completed" else
                          "Resolve the first reported blocker, perform native recovery only under its own authorization, then explicitly resume"}
    if not fresh:
        value.update(status="incomplete", exit_code=3, next_step="Explicit resume performs fresh target reconciliation; this status is only historical")
        for view in value["jobs"]:
            view["current_verified"] = False
            if view["historical_completed"]:
                view.update(status="stale", reason="Historical status; current target has not been read",
                            next_step="Explicit resume performs fresh read-only reconciliation")
    return bc.report(value)


def _prior_elapsed(cp, work):
    path = work / "report.json"
    if not path.exists(): return None if cp["attempts"] else 0.0
    previous = bc.report(bio.json_read(path))
    if previous["attempts"] != cp["attempts"] or previous["batch_id"] != cp["batch_id"]:
        return None  # The prior process did not report its whole observed tail.
    return previous["elapsed_seconds"]


def _execute(ledger, plan, source, repo, target, history, actual_head, tool, *, resumed, started):
    cp = ledger.cp
    previous_elapsed = _prior_elapsed(cp, ledger.work)
    cp["jobs"] = _historical_views(cp, plan)
    had_unfinished = any(not view["historical_completed"] for view in cp["jobs"])
    cp["status"] = "incomplete"
    ledger.save()
    with _signals() as signal_state:
        try:
            state = _journal(target)
            if state["pending"] is not None or state["staging"]:
                view = next((v for v in cp["jobs"] if not v["historical_completed"]), cp["jobs"][0])
                view.update(status="recovery_required", current_verified=False, reason="Native pending/staging journal blocks all batch writers",
                            next_step="Separately authorized native recovery, then explicit resume")
            elif _reconcile_completed(ledger, plan, source, repo, target, tool):
                for job, view in zip(plan["jobs"], cp["jobs"]):
                    if signal_state["stop"]: break
                    if view["status"] == "completed": continue
                    _execute_job(ledger, job, view, source, repo, target, history, tool, resumed=resumed)
                    ledger.save()
                    if view["status"] != "completed": break
                if had_unfinished and not signal_state["stop"] and all(view["status"] == "completed" for view in cp["jobs"]):
                    _reconcile_completed(ledger, plan, source, repo, target, tool)
            cp["status"] = "aborted" if signal_state["stop"] or any(v["status"] == "aborted" for v in cp["jobs"]) else "technical_error" if any(v["status"] == "failed" for v in cp["jobs"]) else (
                "completed" if all(v["status"] == "completed" and v["current_verified"] for v in cp["jobs"]) else "incomplete")
        except (Aborted, KeyboardInterrupt) as exc:
            cp["status"] = "aborted"
            view = next((v for v in cp["jobs"] if v["status"] != "completed"), None)
            if view is not None: view.update(status="aborted", reason=str(exc)[:4096], next_step="Inspect native journal and explicitly resume")
        except (InvalidInput, OSError, ValueError) as exc:
            raise BatchTechnicalError(str(exc)) from exc
    ledger.save()
    result = _report(cp, plan, target, None if previous_elapsed is None else previous_elapsed + time.monotonic() - started)
    path = ledger.work / "report.json"
    old = bio.read(path) if path.exists() else None
    bio.replace_json(path, result, old)
    return result


def run(plan_path, source_root, repo_root, target_root, work_root, history_root=None):
    started = time.monotonic()
    plan, raw, source, repo, target, work, history, actual_head, tool = _prepare(
        plan_path, source_root, repo_root, target_root, work_root, history_root)
    bio.require(plan["revision"] == 1 and plan["source_commit"] == actual_head, "New run needs an initial plan at the actual tool HEAD")
    bio.require(not work.exists() and work.parent.is_dir(), "Run needs a new work root under an existing safe parent")
    with _control(target) as control:
        work.mkdir(); bio.sync_directory(work.parent)
        bindings = _bindings(source, repo, target, work, history, tool)
        bio.write_json_new(work / "owner.json", {"format": bc.PREFIX + "owner-v1", "batch_id": plan["batch_id"], "bindings": bindings})
        for folder in ("plans", "attempts"): (work / folder).mkdir()
        for job in plan["jobs"]: _claim(control, job, work)
        ref = _plan_ref(plan, raw)
        bio.write_new(work / ref["file"], raw)
        cp = {"format": bc.PREFIX + "checkpoint-v1", "batch_id": plan["batch_id"], "plan": ref, "plans": [ref],
              "bindings": bindings, "attempts": [], "jobs": [_view(job) for job in plan["jobs"]], "status": "incomplete"}
        ledger = _Ledger(cp, work, control)
        bio.require(not ledger.anchor_path.exists(), "Batch name already has a durable checkout history")
        try:
            ledger.save()
            return _execute(ledger, plan, source, repo, target, history, actual_head, tool, resumed=False, started=started)
        except (InvalidInput, OSError, ValueError) as exc:
            raise BatchTechnicalError(str(exc)) from exc


def resume(plan_path, source_root, repo_root, target_root, work_root, history_root=None):
    started = time.monotonic()
    plan, raw, source, repo, target, work, history, actual_head, tool = _prepare(
        plan_path, source_root, repo_root, target_root, work_root, history_root)
    bio.external(work)
    with _control(target) as control:
        try:
            ref = _plan_ref(plan, raw)
            ledger, plans = _history(work, control, incoming=ref)
            expected = _bindings(source, repo, target, work, history, tool)
            bio.require(ledger.cp["bindings"] == expected, "stale: explicit roots, identity, or relevant loaded tool bytes changed")
            _writer_barriers(ledger.cp, plan)
            if ref != ledger.cp["plan"]:
                previous = ledger.cp["plan"]
                bio.require(plan["batch_id"] == ledger.cp["batch_id"] and plan["revision"] == previous["revision"] + 1 and
                            plan["previous_plan_sha256"] == previous["sha256"] and plan["source_commit"] == actual_head,
                            "Successor plan must bind the exact previous original and current tool HEAD")
                plans[ref["sha256"]] = plan
                _budget_history(plans)
                # Complete an already validated direct predecessor lag before
                # publishing another plan; two crashes cannot skip an anchor.
                ledger.save()
                destination = work / ref["file"]
                if destination.exists(): bio.require(bio.read(destination) == raw, "Foreign successor original")
                else: bio.write_new(destination, raw)
                ledger.cp["plan"] = ref; ledger.cp["plans"].append(ref)
                ledger.cp["jobs"] = _historical_views(ledger.cp, plan)
                ledger.cp["status"] = "incomplete"
            for job in plan["jobs"]: _claim(control, job, work)
            ledger.save()
            return _execute(ledger, plan, source, repo, target, history, actual_head, tool, resumed=True, started=started)
        except (InvalidInput, OSError, ValueError) as exc:
            raise BatchTechnicalError(str(exc)) from exc


def status(work_root):
    work = bio.external(work_root)
    # Historical status is strictly read-only, including locks/control files.
    owner = bc.owner(bio.json_read(work / "owner.json"))
    target = Path(owner["bindings"]["target_root"])
    control = io.safe(target, CONTROL)
    try:
        ledger, plans = _history(work, control)
        plan = plans[ledger.cp["plan"]["sha256"]]
        report_path = work / "report.json"
        previous = bc.report(bio.json_read(report_path)) if report_path.exists() else None
        journal = previous["journal"] if previous else {"pending": None, "staging": []}
        answer = _report(ledger.cp, plan, target, None, fresh=False, journal=journal)
        for view in answer["jobs"]:
            view["current_verified"] = False
            if view["historical_completed"]:
                view["status"] = "stale"
                view["reason"] = "Historical status; current target has not been read"
                view["next_step"] = "Explicit resume performs fresh read-only reconciliation"
        answer.update(status="incomplete", exit_code=3, next_step="Explicit resume performs fresh target reconciliation; this status is only historical")
        bc.report(answer)
        return {"fresh": False, "report": answer}
    except (InvalidInput, OSError, ValueError) as exc:
        raise BatchTechnicalError(str(exc)) from exc
