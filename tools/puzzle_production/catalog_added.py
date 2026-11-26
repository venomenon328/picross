"""KU-B authoritative added dates. Pure validation; never reads Git or analyzes puzzles."""
from datetime import datetime, timezone
import re

from .authoring_package import require, sha
from .contract import canonical_bytes, exact_keys
from . import catalog_rating as rating

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


def report_path(run):
    from .catalog_analysis import run_id
    return ROOT + "/reports/" + run_id(run) + ".json"


def validate_fields(value):
    exact_keys(value, {"added_at", "provenance"})
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


def registration(identifier):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    rating.identity(identifier)
    return {"added_at": now,
            "provenance": {"kind": "registration", "reference_time": now, "commit": None,
                           "evidence": None, "reason": "Successful first playable registration in the shared transaction."}}
