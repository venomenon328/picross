"""Explicit, snapshot-bound production default; importing this module activates nothing."""
import argparse
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from pathlib import Path

from .authoring_package import require, sha, relative
from .contract import Aborted, InvalidInput, canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io
from . import operation_diagnostics as diagnostic

OLD = "picross-difficulty-0.3"
NEW = "picross-difficulty-0.4"
METHODS = (OLD, NEW)
PATH = "content/difficulty-method.json"
FORMAT = "picross-difficulty-default-v1"
LEGACY_PLAN = "picross-difficulty-activation-plan-v1"
PLAN = "picross-difficulty-activation-plan-v2"
IMAGE_PLAN = "picross-difficulty-activation-plan-v3"
LIMIT = 4096
PLAN_LIMIT = 16 * 1024 * 1024
_batch = ContextVar("catalog_method_read_batch", default=None)


def _check_inputs(root, files):
    with diagnostic.phase("Method byte binding"):
        require(all(io.read(root, name, 64*1024*1024) == raw for name, raw in files.items()),
                "Changed frozen difficulty method inputs")
    diagnostic.count("method_byte_revalidations")


@contextmanager
def _read_batch():
    if _batch.get() is not None:
        yield
        return
    data_token = io._operation_data.set({"json": {}, "json_bytes": 0}) if io._operation_data.get() is None else None
    used = {}
    token = _batch.set(used)
    try:
        yield
        # No active content writes inside these readers. A changed method
        # invalidates the whole result before any caller can consume it.
        for key, files in used.items():
            _check_inputs(key[2], files)
    finally:
        _batch.reset(token)
        if data_token is not None: io._operation_data.reset(data_token)


def bound_validation(function):
    """Deduplicate pure method validation in one byte-bound read-only view."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        with _read_batch():
            return function(*args, **kwargs)
    return wrapped


@diagnostic.measured("Method freeze", "method_validations")
def method_hash(method):
    require(method in METHODS, "Unsupported difficulty method")
    if method == OLD:
        from . import difficulty_rating as implementation
    else:
        from . import sd2_rating_freeze as implementation
    data = io._operation_data.get()
    if data is None:
        return digest(implementation.frozen_method())
    root = implementation._ROOT
    key = ("method", method, root)
    batch = _batch.get()
    if batch is not None and key in batch:
        diagnostic.count("method_view_reuses")
        return data[key][1]
    prior = data.get(key)
    if prior is not None:
        # Always reopen every actual method/config/reference/implementation
        # file with identity guards. No mtime/path or successful-check cache.
        _check_inputs(root, prior[0])
        if batch is not None: batch[key] = prior[0]
        return prior[1]
    name = "difficulty_method_0_3.json" if method == OLD else "sd2_method_0_4.json"
    raw = io.read(root, name, 64*1024*1024)
    value = io.json_bytes(raw, 64*1024*1024)
    identity = implementation.METHOD_HASH
    require(digest(value) == identity, "Unknown or changed difficulty method configuration")
    names = {name, *value["implementation"]}
    names.update(("difficulty_references_0_3.json", "difficulty_calibration_0_3.json") if method == OLD else value["artifacts"])
    before = {n: io.read(root, n, 64*1024*1024) for n in sorted(names)}
    validated = implementation.frozen_method()
    require(all(io.read(root, n, 64*1024*1024) == b for n, b in before.items()),
            "Difficulty method changed during validation")
    result = digest(validated)
    require(result == identity and before[name] == raw, "Difficulty method configuration changed during validation")
    data[key] = (before, result)
    if batch is not None: batch[key] = before
    diagnostic.count("full_method_validations")
    return result


def validate(value):
    from . import catalog_rating as rating
    exact_keys(value, {"format", "revision", "method", "method_hash", "previous_record_hash", "activation_hash", "record_hash"})
    require(value["format"] == FORMAT and len(canonical_bytes(value)) + 1 <= LIMIT, "Invalid production default format/size")
    integer(value["revision"], 1, 1000000, "default revision")
    require(sha(value["method_hash"]) == method_hash(value["method"]), "Wrong production default method")
    if value["revision"] == 1:
        require(value["previous_record_hash"] is None, "First default has a predecessor")
    else:
        sha(value["previous_record_hash"])
    sha(value["activation_hash"])
    rating.check_hash(value, "record_hash")
    return value


def from_bytes(raw):
    if raw is None: return None
    return validate(io.json_bytes(raw, LIMIT))


def load(root):
    directory = io.safe(root, "content")
    for entry in directory.iterdir():
        require(entry.name.casefold() != "difficulty-method.json" or entry.name == "difficulty-method.json",
                "Aliased production default source")
    return from_bytes(io.read(root, PATH, LIMIT, missing=True))


def current(record):
    if record is not None: validate(record)
    method = record["method"] if record else OLD
    return {"method": method, "method_hash": method_hash(method), "record_hash": record["record_hash"] if record else None,
            "revision": record["revision"] if record else 0}


def source_hashes(snapshot, plan_format=None):
    from . import catalog_transaction as tx
    if plan_format is None:
        plan_format = IMAGE_PLAN if tx.image_generation(snapshot) else PLAN
    require((plan_format == IMAGE_PLAN) == tx.image_generation(snapshot),
            "Activation plan generation differs from the current image projection")
    if plan_format == IMAGE_PLAN:
        return tx.image_snapshot(snapshot)["sources"]
    if plan_format == LEGACY_PLAN:
        snapshot = tx.pre_background_snapshot(snapshot)
    return {**snapshot["retained"], **{n: io.checksum(raw) for n, raw in snapshot["texts"].items()}}


def validate_plan(value):
    from .catalog_rating import check_hash
    exact_keys(value, {"format", "expected", "target", "sources", "result_hash"})
    require(value["format"] in (IMAGE_PLAN, PLAN, LEGACY_PLAN) and len(canonical_bytes(value)) + 1 <= PLAN_LIMIT, "Invalid activation plan format/size")
    exact_keys(value["expected"], {"method", "method_hash", "record_hash", "revision"})
    exact_keys(value["target"], {"method", "method_hash"})
    for side in ("expected", "target"):
        require(value[side]["method_hash"] == method_hash(value[side]["method"]), "Activation method freeze differs")
    require(value["expected"]["method"] != value["target"]["method"], "Default is already the target method")
    if value["expected"]["record_hash"] is not None: sha(value["expected"]["record_hash"])
    integer(value["expected"]["revision"], 0, 1000000, "expected default revision")
    require((value["expected"]["record_hash"] is None) == (value["expected"]["revision"] == 0), "Unbound expected default revision")
    sources = value["sources"]
    require(isinstance(sources, dict) and PATH in sources and len(sources) <= 80004, "Invalid activation sources")
    for name, checksum in sources.items():
        relative(name)
        if checksum is not None: sha(checksum)
    check_hash(value, "result_hash")
    return value


def plan(root, expected, target, target_hash):
    from . import catalog_transaction as tx, catalog_rating as rating
    snapshot = tx.capture(root)
    before = current(from_bytes(snapshot["texts"][PATH]))
    require(before["method"] == expected, "Unexpected current production default")
    return validate_plan(rating.hashed({"format": IMAGE_PLAN if tx.image_generation(snapshot) else PLAN, "expected": before,
        "target": {"method": target, "method_hash": target_hash}, "sources": source_hashes(snapshot)}, "result_hash"))


def record_for(plan, previous):
    from .catalog_rating import hashed
    return validate(hashed({"format": FORMAT, "revision": previous["revision"] + 1 if previous else 1,
        **plan["target"], "previous_record_hash": previous["record_hash"] if previous else None,
        "activation_hash": plan["result_hash"]}, "record_hash"))


def adopt(root, value, *, apply=True, fail_step=None):
    from . import catalog_transaction as tx
    value = validate_plan(value)
    snapshot = tx.capture(root)
    previous = from_bytes(snapshot["texts"][PATH])
    sources = source_hashes(snapshot, value["format"])
    if previous and previous["activation_hash"] == value["result_hash"]:
        require(all(previous[k] == v for k, v in value["target"].items()) and
                previous["previous_record_hash"] == value["expected"]["record_hash"] and
                previous["revision"] == value["expected"]["revision"] + 1 and
                snapshot["texts"][PATH] == canonical_bytes(previous) + b"\n", "Foreign activation result")
        sources[PATH] = value["sources"][PATH]
        require(sources == value["sources"], "Checkout changed since activation")
        return {"status": "no-op", "method": previous["method"]}
    require(current(previous) == value["expected"] and sources == value["sources"], "Stale activation plan")
    from .content_registry import require_current
    if apply: require_current(snapshot["registry"])
    record = record_for(value, previous)
    journal = tx.prepare(root, snapshot, {PATH: canonical_bytes(record) + b"\n"}, operation="method-activation",
                         generation="background" if value["format"] in (IMAGE_PLAN, PLAN) else "sd2")
    if apply: tx.execute(root, journal, fail_step=fail_step)
    return {"status": "activated" if apply else "planned-activation", "method": record["method"], "record_hash": record["record_hash"]}


def main(argv=None):
    import json
    from .catalog_analysis import write_new, work_directory, safe_external
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--checkout", type=Path, required=True)
    p.add_argument("--expected-method", choices=METHODS, required=True)
    p.add_argument("--target-method", choices=METHODS, required=True)
    p.add_argument("--target-method-hash", required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("adopt")
    p.add_argument("--checkout", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = io.external(args.checkout)
        if args.command == "plan":
            result = plan(root, args.expected_method, args.target_method, args.target_method_hash)
            write_new(work_directory(args.output, root), canonical_bytes(result) + b"\n")
        else:
            path = safe_external(args.plan)
            raw = io.read(path.parent, path.name, PLAN_LIMIT)
            result = adopt(root, io.json_bytes(raw, PLAN_LIMIT))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (InvalidInput, Aborted, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 4 if isinstance(exc, Aborted) else 2


if __name__ == "__main__":
    raise SystemExit(main())
