"""Explicit, snapshot-bound production default; importing this module activates nothing."""
import argparse
from pathlib import Path

from .authoring_package import require, sha, relative
from .contract import Aborted, InvalidInput, canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io

OLD = "picross-difficulty-0.3"
NEW = "picross-difficulty-0.4"
METHODS = (OLD, NEW)
PATH = "content/difficulty-method.json"
FORMAT = "picross-difficulty-default-v1"
PLAN = "picross-difficulty-activation-plan-v1"
LIMIT = 4096
PLAN_LIMIT = 16 * 1024 * 1024


def method_hash(method):
    require(method in METHODS, "Unsupported difficulty method")
    if method == OLD:
        from .difficulty_rating import frozen_method
    else:
        from .sd2_rating_freeze import frozen_method
    return digest(frozen_method())


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


def source_hashes(snapshot):
    return {**snapshot["retained"], **{n: io.checksum(raw) for n, raw in snapshot["texts"].items()}}


def validate_plan(value):
    from .catalog_rating import check_hash
    exact_keys(value, {"format", "expected", "target", "sources", "result_hash"})
    require(value["format"] == PLAN and len(canonical_bytes(value)) + 1 <= PLAN_LIMIT, "Invalid activation plan format/size")
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
    return validate_plan(rating.hashed({"format": PLAN, "expected": before,
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
    sources = source_hashes(snapshot)
    if previous and previous["activation_hash"] == value["result_hash"]:
        require(all(previous[k] == v for k, v in value["target"].items()) and
                previous["previous_record_hash"] == value["expected"]["record_hash"] and
                previous["revision"] == value["expected"]["revision"] + 1 and
                snapshot["texts"][PATH] == canonical_bytes(previous) + b"\n", "Foreign activation result")
        sources[PATH] = value["sources"][PATH]
        require(sources == value["sources"], "Checkout changed since activation")
        return {"status": "no-op", "method": previous["method"]}
    require(current(previous) == value["expected"] and sources == value["sources"], "Stale activation plan")
    record = record_for(value, previous)
    journal = tx.prepare(root, snapshot, {PATH: canonical_bytes(record) + b"\n"}, operation="method-activation")
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
