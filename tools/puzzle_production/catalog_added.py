"""KU-B authoritative added dates. Pure validation; never reads Git or analyzes puzzles."""
from datetime import datetime, timezone
import hashlib
import re

from .authoring_package import require, sha
from .contract import canonical_bytes, exact_keys
from . import catalog_rating as rating

FORMAT = "picross-added-v1"
LIMIT = 64 * 1024
REPORT_LIMIT = 8 * 1024 * 1024
ROOT = "content/added"


def timestamp(value):
    if value is None:
        return None
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value),
            "Invalid added UTC timestamp")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def commit(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), "Invalid added source commit")
    return value


def path(identifier):
    return ROOT + "/" + rating.identity(identifier) + ".json"


def report_path(run):
    from .catalog_analysis import run_id
    return ROOT + "/reports/" + run_id(run) + ".json"


def validate(value, identifier=None):
    exact_keys(value, {"format", "id", "added_at", "provenance"})
    require(value["format"] == FORMAT, "Unsupported added format")
    rating.identity(value["id"])
    require(identifier is None or value["id"] == identifier, "Wrong added ID")
    timestamp(value["added_at"])
    p = exact_keys(value["provenance"], {"kind", "reference_time", "commit", "evidence", "reason"})
    require(p["kind"] in ("registration", "direct", "git-snapshot", "unknown"), "Invalid added provenance")
    require(timestamp(p["reference_time"]) == value["added_at"] and
            (value["added_at"] is None) == (p["kind"] == "unknown"), "Conflicting added provenance")
    require(isinstance(p["reason"], str) and 0 < len(p["reason"]) <= 2048 and
            p["reason"] == p["reason"].strip() and not any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in p["reason"]),
            "Invalid added provenance reason")
    if p["commit"] is not None: commit(p["commit"])
    require(p["kind"] != "git-snapshot" or p["commit"] is not None, "Missing snapshot commit")
    if p["kind"] == "registration":
        require(p["evidence"] is None and p["commit"] is None, "Registration cannot invent historical evidence")
    else:
        e = exact_keys(p["evidence"], {"path", "sha256"})
        require(isinstance(e["path"], str) and e["path"].startswith(ROOT + "/reports/") and
                e["path"].endswith(".json") and report_path(e["path"].split("/")[-1][:-5]) == e["path"], "Invalid added evidence path")
        sha(e["sha256"])
    require(len(canonical_bytes(value)) + 1 <= LIMIT, "Oversized added record")
    return value


def encoded(value):
    return canonical_bytes(validate(value)) + b"\n"


def registration(identifier):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {"format": FORMAT, "id": identifier, "added_at": now,
            "provenance": {"kind": "registration", "reference_time": now, "commit": None,
                           "evidence": None, "reason": "Successful first playable registration in the shared transaction."}}


def source_paths(root, *registries, extra_reports=()):
    """Inspect the whole namespace, including aliases and Windows reparse points."""
    from .content_update import path_in
    allowed = {path(e["id"]) for r in registries for e in r["entries"]}
    reports = set(extra_reports)
    records = {}
    for name in sorted(allowed):
        p = path_in(root, name)
        require(not p.exists() or p.is_file(), "Added source must be a regular file")
        if p.exists():
            raw = rating.read_file(p, LIMIT)
            record = validate(rating.bytes_json(raw, LIMIT), p.stem)
            require(raw == encoded(record), "Noncanonical added source")
            records[name] = record
            if record["provenance"]["evidence"]:
                reports.add(record["provenance"]["evidence"]["path"])
    directory = path_in(root, ROOT)
    if directory.exists():
        require(directory.is_dir(), "Added namespace must be a directory")
        for p in directory.iterdir():
            name = p.relative_to(root).as_posix()
            path_in(root, name)
            if name == ROOT + "/reports":
                require(p.is_dir(), "Added reports must be a directory")
                for report in p.iterdir():
                    n = report.relative_to(root).as_posix()
                    require(n in reports and path_in(root, n).is_file(), "Unknown added evidence file: " + n)
            else:
                require(name in allowed and p.is_file(), "Unknown added source: " + name)
    return records, reports


def load_sources(root, registry):
    records, reports = source_paths(root, registry)
    # Report validation is structural and byte-bound, never a Git lookup.
    from .content_update import path_in
    from .catalog_added_history import validate_plan, record_for
    loaded = {}
    for name in reports:
        raw = rating.read_file(path_in(root, name), REPORT_LIMIT)
        plan = validate_plan(rating.bytes_json(raw, REPORT_LIMIT))
        require(raw == canonical_bytes(plan) + b"\n", "Noncanonical added report")
        require(report_path(plan["run_id"]) == name, "Added report path mismatch")
        loaded[name] = (raw, plan)
    for name, record in records.items():
        evidence = record["provenance"]["evidence"]
        if evidence:
            raw, plan = loaded[evidence["path"]]
            require(hashlib.sha256(raw).hexdigest() == evidence["sha256"] and
                    record == record_for(plan, record["id"], raw), "Added evidence differs from source record")
    return {r["id"]: r for r in records.values()}
