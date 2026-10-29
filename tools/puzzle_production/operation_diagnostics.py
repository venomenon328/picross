"""RI-A observations and cooperative operation frames; never catalog authority."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import argparse
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

from .authoring_package import require
from .contract import Aborted, canonical_bytes, exact_keys

FORMAT = "picross-ri-a-operation-v1"
current = ContextVar("ri_diagnostics", default=None)
frame = ContextVar("ri_frame", default=None)
completion = ContextVar("ri_completion", default=0)


def seconds(value, *, now=None):
    if value is None:
        return None
    require(type(value) in (int, float), "Operation seconds must be a finite positive number")
    try:
        valid = value > 0 and math.isfinite(value) and math.isfinite((time.monotonic() if now is None else now) + value)
    except OverflowError:
        valid = False
    require(valid, "Operation seconds/deadline must be finite and positive")
    return value


def cli_seconds(value):
    try:
        return seconds(float(value))
    except (ValueError, OverflowError) as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def count(name, amount=1, work=None):
    d = current.get()
    if d is not None:
        d.counters[name] = d.counters.get(name, 0) + amount
        if work is not None:
            d.last_progress = {"elapsed_seconds": time.monotonic() - d.started, "work": work}


@contextmanager
def phase(name):
    d = current.get()
    if d is None:
        yield
        return
    parent = "/".join(d.stack) or None
    key = (parent, name)
    row = d.phases.setdefault(key, {"name": name, "parent": parent, "inclusive": True, "calls": 0, "seconds": 0.0})
    row["calls"] += 1
    at = time.monotonic()
    d.stack.append(name)
    d.emit()
    try:
        yield
    finally:
        row["seconds"] += time.monotonic() - at
        d.stack.pop()


def measured(name, counter=None):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if counter:
                count(counter)
            with phase(name):
                result = function(*args, **kwargs)
            count("completed_steps", work=name)
            return result
        return wrapped
    return decorate


def candidate_check(function, *args, **kwargs):
    """Count the actual complete source check, including a composite repair."""
    count("full_candidate_proof_checks")
    with phase("Candidate/Proof"):
        return function(*args, **kwargs)


class Diagnostics:
    def __init__(self, command, parameters=None, *, stderr=None):
        self.command = command
        self.started = time.monotonic()
        self.operation_class = {"register": "registration", "recover-registration": "unclassified-recovery"}.get(command, command)
        self.outcome = "blocked-before-mutation"
        self.limits = []
        self.phases = {}
        self.stack = []
        self.counters = {}
        self.last_progress = {"elapsed_seconds": 0.0, "work": "call started"}
        self.last_message = -math.inf
        self.stderr = stderr
        self.journal_state = {"journal": "not-inspected", "lock": "not-inspected"}
        self.environment = {"os": platform.platform(), "python": sys.version, "tool_commit": None,
                            "parameters": parameters or {}, "catalog_entries": None, "package_files": None}
        self.missing = ["filesystem type", "nested proof calls within composite candidate checks",
                        "I/O outside catalog_io (read/hash counters cover catalog_io only)"]

    def emit(self, *, event="progress", force=False):
        now = time.monotonic() - self.started
        if self.stderr is None or not force and now - self.last_message < 30:
            return
        stalled = now - self.last_progress["elapsed_seconds"] >= 30
        active = frame.get()
        phase_name = (active.kind + '/' + active.segment) if active is not None else '/'.join(self.stack) or 'Finish'
        try:
            print(f"{self.command}/{self.operation_class} phase={phase_name} "
                  f"elapsed={now:.3f}s event={event} steps={self.counters.get('completed_steps', 0)} "
                  f"files={self.counters.get('published_files', 0)} "
                  f"{'no proven progress for 30s; ' if stalled else ''}last={self.last_progress['work']}", file=self.stderr)
        except (OSError, ValueError):
            if 'stderr progress delivery failed' not in self.missing:
                self.missing.append('stderr progress delivery failed')
        self.last_message = now

    def result(self):
        missing = list(self.missing)
        missing += [key for key, value in self.environment.items() if value is None]
        return {"format": FORMAT, "command": self.command, "operation_class": self.operation_class,
                "outcome": self.outcome, "limits": self.limits,
                "elapsed_seconds": time.monotonic() - self.started,
                "phases": list(self.phases.values()), "counters": dict(self.counters),
                "last_progress": dict(self.last_progress), "environment": self.environment,
                "missing_measurements": missing, "journal_state": dict(self.journal_state)}


@contextmanager
def observe(diagnostics):
    token = current.set(diagnostics)
    try:
        yield diagnostics
    finally:
        current.reset(token)


class Frame:
    def __init__(self, kind, limit, origin, *, started=None, recovery_seconds=None):
        self.started = time.monotonic() if started is None else started
        self.seconds = seconds(limit, now=self.started)
        self.deadline = self.started + limit
        parent = frame.get()
        self.parent_deadline = parent.deadline if parent is not None and not parent.complete else math.inf
        if parent is not None and not parent.complete:
            self.deadline = min(self.deadline, parent.deadline)
        self.kind = kind
        self.complete = False
        self.warned = False
        self.recovery_seconds = recovery_seconds
        self.segment = "Prevalidation" if kind == "Publication" else "Classification"
        self.segment_started = self.started
        d = current.get()
        if d:
            from . import catalog_io as io
            outer = io._deadline.get()
            d.limits.append({"phase": kind, "warning_seconds": 300, "protection_seconds": limit,
                             "origin": origin, "start_elapsed_seconds": self.started - d.started,
                             "effective_seconds": min(self.deadline, outer if outer is not None else math.inf) - self.started,
                             "recovery_seconds": (1800 if recovery_seconds is None else recovery_seconds) if kind == "Publication" else limit,
                             "recovery_origin": "registration-default" if kind == "Publication" and recovery_seconds is None else "override" if kind == "Publication" else origin})

    def next_segment(self, name=None):
        now = time.monotonic()
        d = current.get()
        if d:
            key = (self.kind, self.segment)
            row = d.phases.setdefault(key, {"name": self.segment, "parent": self.kind, "inclusive": True, "calls": 0, "seconds": 0.0})
            row["calls"] += 1
            row["seconds"] += now - self.segment_started
        if name is not None:
            self.segment = name
            self.segment_started = now

    def classified_limit(self, limit, origin):
        from . import catalog_io as io
        self.seconds = seconds(limit, now=self.started)
        self.deadline = min(self.started + limit, self.parent_deadline)
        d = current.get()
        if d:
            outer = io._deadline.get()
            d.limits[-1].update(protection_seconds=limit, origin=origin, recovery_seconds=limit, recovery_origin=origin,
                                effective_seconds=min(self.deadline, outer if outer is not None else math.inf) - self.started)
        io.tick()

    def tick(self):
        if self.complete:
            return
        now = time.monotonic()
        d = current.get()
        if not self.warned and now - self.started >= 300:
            self.warned = True
            if d:
                d.emit(event=self.kind + "-warning-300s", force=True)
            else:
                print(f"{self.kind}: warning after {now - self.started:.3f}s; operation unfinished", file=sys.stderr)
        if d:
            d.emit()
        if now >= self.deadline:
            raise Aborted("resource_limit: " + self.kind + " time budget exhausted")


@contextmanager
def operation(kind, limit, origin, *, started=None, recovery_seconds=None):
    value = Frame(kind, limit, origin, started=started, recovery_seconds=recovery_seconds)
    token = frame.set(value)
    completed = completion.get()
    try:
        with phase(kind):
            from . import catalog_io as io
            io.tick()
            yield value
            if completion.get() == completed:
                io.tick()
    finally:
        value.next_segment()
        frame.reset(token)


def durable(outcome, *, lock_state="durably-removed"):
    f = frame.get()
    if f:
        f.complete = True
        completion.set(completion.get() + 1)
    d = current.get()
    if d:
        d.outcome = outcome
        d.journal_state = {"journal": "removed", "lock": lock_state}


def boundary(name, target=None):
    # Fault injection checkpoint remains separate, so patched checkpoints cannot
    # remove budget enforcement or manufacture completion.
    from . import catalog_io as io
    io.tick()
    count("phase_boundaries", work=name + (": " + target if target else ""))
    f = frame.get()
    if f is not None and name.startswith(("P", "R")) and name[:2] != f.segment:
        f.next_segment(name[:2])
    d = current.get()
    if d:
        d.emit(event=name)


def classify(root):
    """Read original bounded bytes; do not trust a free-standing operation tag."""
    from . import catalog_io as io, catalog_transaction as tx, catalog_publication as pub
    raw = pub.read_journal(root)
    staged = raw is None
    name = None
    if staged:
        remnants = pub.staging(root)
        require(len(remnants) == 1, "Missing/ambiguous journal staging; preserve files")
        name = remnants[0]
        raw = pub.read_journal(root, name)
    d = current.get()
    if d:
        d.outcome = "recovery-required"
        d.journal_state = {"journal": "staging-unvalidated" if staged else "present-unvalidated", "lock": "absent" if staged else "present"}
    j = io.json_bytes(raw, pub.LIMIT)
    require(isinstance(j, dict), "Invalid recovery journal")
    fmt = j.get("format")
    if fmt == "picross-registration-journal-v2" and not staged:
        exact_keys(j, {"format", "targets", "files", "old", "new", "categories"})
        require(isinstance(j["targets"], list) and len(j["targets"]) == 4 and
                all(isinstance(j[k], dict) for k in ("files", "old", "new")) and
                isinstance(j["categories"], str), "Invalid registration v2 journal")
        require(all(isinstance(v, str) for v in j["targets"]) and
                all(set(j[side]) == {tx.REGISTRY, tx.RUNTIME} and all(isinstance(v, str) for v in j[side].values())
                    for side in ("old", "new")), "Invalid registration v2 indexes")
        op = "registration"
    elif fmt == "picross-content-update-journal-v1" and not staged:
        # The historical decoder still enforces its complete closed schema.
        op = "update"
    else:
        maps = (tx.FORMATS, tx.AT_FORMATS, tx.PREVIOUS_FORMATS, tx.LEGACY_FORMATS)
        op = j.get("operation")
        require(isinstance(op, str) and any(m.get(op) == fmt for m in maps), "Unsupported recovery journal format/operation")
        exact_keys(j, {"format", "operation", "old", "new", "retained", "additions", "report_run"} |
                   ({"replacements"} if tx.modern(j) else set()))
        require(all(isinstance(j[k], dict) for k in ("old", "new", "retained", "additions")), "Invalid recovery journal maps")
    if staged:
        require(tx.modern(j) and raw == pub.journal_bytes(j) and
                name == "content/.registration-journal-" + io.checksum(raw) + ".tmp", "Incomplete/foreign journal staging")
    d = current.get()
    if d:
        d.operation_class = op + "-recovery"
        d.journal_state = {"journal": "complete-staging" if staged else "present", "lock": "absent" if staged else "present"}
    return op, raw, name


def report_target(path, excluded):
    from . import catalog_io as io
    target = io.external(path)
    require(target.parent.is_dir() and not target.exists(), "Operation report needs an existing safe parent and a new file")
    for item in excluded:
        if item is None:
            continue
        source = io.external(item)
        require(target != source and not target.is_relative_to(source), "Operation report overlaps checkout/export/catalog input")
    return target


def write_report(target, value):
    from . import catalog_io as io, catalog_publication as pub
    target = io.external(target)
    require(not target.exists(), "Operation report already exists")
    fd, name = tempfile.mkstemp(prefix=".ri-report-", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical_bytes(value) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        pub.rename(io.external(temporary), io.external(target), replace=False)
    finally:
        temporary.unlink(missing_ok=True)


def source_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2],
                                       stderr=subprocess.DEVNULL, text=True, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return None
