"""Immutable HP-I1b2 work records; no raster ZIP or generated human approval."""
from pathlib import Path

from . import authoring_package as ap, background_contract as bc, catalog_io as io
from . import background_package as package
from .contract import InvalidInput, canonical_bytes, exact_keys, integer
from .reveal_retirement import INDEX, index_rows, selection, tree_files

FORMAT = "picross-background-adoption-request-v1"
LIMIT = 2 * 1024 * 1024
MAX_FILES = 256
MAX_BYTES = 96 * 1024 * 1024
FILE_LIMIT = 32 * 1024 * 1024


def encoded(value):
    return canonical_bytes(value) + b"\n"


def directory(value):
    return selection(value["puzzle_id"], value["revision"])


def record_name(value):
    return directory(value) + "/record.json"


def index_row(value):
    return {"puzzle_id": value["puzzle_id"], "revision": value["revision"], "record": record_name(value)}


def ref(name, raw):
    return {"file": name, "sha256": io.checksum(raw), "bytes": len(raw)}


def inventory(value, *, count=MAX_FILES, total=MAX_BYTES, exclude=()):
    ap.require(isinstance(value, list) and len(value) <= count, "Invalid background file inventory")
    names = []
    for item in value:
        try:
            bc._ref(item)
        except bc.BackgroundError as exc:
            raise InvalidInput("Background inventory: " + str(exc)) from exc
        integer(item["bytes"], 0, FILE_LIMIT, "background file bytes")
        ap.require(item["file"] not in exclude, "Background inventory self-reference")
        names.append(item["file"])
    from .authoring_build_contract import names as unique_paths
    unique_paths(names)
    ap.require(names == sorted(names), "Background file inventory must be sorted")
    ap.require(sum(row["bytes"] for row in value) <= total, "Background file inventory exceeds byte limit")
    return value


def validate(value):
    """Closed shape only; physical graph, current target and approvals are separate."""
    try:
        return _validate(value)
    except bc.BackgroundError as exc:
        raise InvalidInput("Background work: " + str(exc)) from exc


def _validate(value):
    value = io.json_bytes(encoded(value), LIMIT)
    exact_keys(value, {"format", "puzzle_id", "revision", "target", "background", "authorization", "files", "test_only"})
    ap.require(value["format"] == FORMAT, "Unsupported background work record format")
    base = directory(value)
    ap.require(type(value["test_only"]) is bool, "Background test_only must be Boolean")
    target = exact_keys(value["target"], {"source", "origin_sha256", "image_revision"})
    bc._ref(target["source"])
    ap.require(target["source"]["file"] == "content/backgrounds/" + value["puzzle_id"] + ".json",
               "Background request targets a different source path")
    integer(target["source"]["bytes"], 1, 1024 * 1024, "background source bytes")
    ap.sha(target["origin_sha256"])
    integer(target["image_revision"], 1, 1_000_000, "background target image revision")
    binding = package.validate_binding(value["background"], package_only=False)
    ap.require(binding["history"] is None, "Background change cannot fetch discarded history")
    inventory(value["files"], exclude=("record.json",))
    files = {row["file"]: row for row in value["files"]}
    for key in ("manifest", "decision", "derivation"):
        stored = binding[key]
        ap.require(stored is not None and stored["storage"] == "external", "Background change requires three external references")
        name = package._join(stored["root"], stored["ref"]["file"])
        ap.require(name.startswith(base + "/"), "Background reference escapes its work revision")
        local = name[len(base) + 1:]
        ap.require(files.get(local) == {**stored["ref"], "file": local}, "Background reference is absent from work inventory")
    bc._human(value["authorization"])
    evidence = value["authorization"]["evidence"]
    ap.require(files.get(evidence["file"]) == evidence, "Background authorization evidence is absent from work inventory")
    return value


def payload(root, value, raw, *, record_present=True):
    """Read exactly one revision, rejecting aliases, links and extra/empty paths."""
    root = io.external(root)
    expected = {row["file"] for row in value["files"]} | ({"record.json"} if record_present else set())
    # tree_files requires a named directory relative to its safe parent.
    found = {name[len(root.name) + 1:] for name in tree_files(root.parent, root.name)}
    ap.require(found == expected, "Background work file inventory differs")
    result = {"record.json": raw}
    for row in value["files"]:
        data = io.read(root, row["file"], FILE_LIMIT)
        ap.require(ref(row["file"], data) == row, "Background work file binding changed: " + row["file"])
        ap.require(not row["file"].casefold().endswith(".zip") and data[:4] not in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
                   "Background work cannot contain an archive")
        result[row["file"]] = data
    if record_present:
        ap.require(io.read(root, "record.json", LIMIT) == raw, "Background work record changed")
    return result


def read(root, record_path, *, require_index=True):
    """Typed index dispatch for the immutable background work family."""
    root = io.external(root)
    record_path = Path(record_path)
    name = record_path.relative_to(root).as_posix() if record_path.is_absolute() else record_path.as_posix()
    raw = io.read(root, name, LIMIT)
    value = validate(io.json_bytes(raw, LIMIT))
    ap.require(name == record_name(value) and raw == encoded(value), "Noncanonical background request bytes or path")
    data = payload(io.safe(root, directory(value)), value, raw)
    if require_index:
        rows = index_rows(io.json_bytes(io.read(root, INDEX, 8 * 1024 * 1024), 8 * 1024 * 1024))
        ap.require(rows.get(directory(value)) == index_row(value), "Background work requires its exact authoring index row")
    return value, raw, data
