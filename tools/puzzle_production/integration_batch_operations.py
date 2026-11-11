"""BA-B's fixed synchronous native calls and read-only reached-target bindings.

The runner owns authorization, immutable inputs, attempts and diagnostics. This
module neither retries a writer nor turns an observed status into permission.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import platform
import sys

from . import authoring_package as ap, background_request as requests, batch_io as bio
from . import catalog_added as added, catalog_background as bg, catalog_background_change as change
from . import catalog_io as io, catalog_publication as publication, catalog_rating as rating
from . import catalog_transaction as tx, categories, content_registry as registry, content_update
from . import images, integration_batch_contract as contract, reveal_source as reveal, target_adapter

_ROOT = Path(__file__).resolve().parents[2]
_PREFIX = "tools/puzzle_production/"
_ENTRY_MODULES = {"__init__", "integration_batch_operations", "integration_batch_contract",
                  "integration_batch_runner", "integration_batch_cli"}
_NORMS = {
    "docs/PRODUCTION_BATCH.md", "docs/PUZZLE_INTEGRATION.md", "docs/ZA1_ADAPTER.md",
    "docs/PUZZLE_PRODUCTION.md", "docs/PUZZLE_BACKGROUNDS.md", "docs/PUZZLE_QUALITY.md",
    "docs/ai-workflows/PUZZLE_AUTHORING.md", "docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md",
    "docs/REVEAL_TRANSPARENCY.md", "docs/CATEGORIES.md", "docs/SD_CATALOG.md",
    "docs/SD2_INTEGRATION.md", "docs/SD2_ANALYZER.md",
}
_METHODS = {"content/difficulty-method.json", *(
    _PREFIX + name for name in (
        "difficulty_method_0_3.json", "difficulty_calibration_0_3.json", "difficulty_references_0_3.json",
        "sd2_method_0_4.json", "sd2_calibration_0_4.json", "sd2_references_0_4.json",
        "sd2_validation_0_4.json", "sd2_comparison_0_4.json"))}


def _read(root, name, limit=ap.MAX_ZIP):
    return io.read(root, name, limit)


def _ref(root, name):
    return bg.ref(name, _read(root, name))


# Freeze source bytes before conditional native imports. Later calls may not
# describe edited disk files while still executing an older imported module.
# Only the transitive closure below becomes part of a saved tool binding.
_FROZEN_MODULES = {path.stem: _read(_ROOT, _PREFIX + path.name)
                   for path in sorted((_ROOT / _PREFIX).glob("*.py"))}


def _dependencies(raw):
    result = set()
    for node in ast.walk(ast.parse(raw)):
        if isinstance(node, ast.ImportFrom):
            if node.level == 1:
                if node.module:
                    result.add(node.module.split(".")[0])
                else:
                    result.update(alias.name.split(".")[0] for alias in node.names)
            elif not node.level and node.module == "tools.puzzle_production":
                result.update(alias.name.split(".")[0] for alias in node.names)
            elif not node.level and node.module and node.module.startswith("tools.puzzle_production."):
                result.add(node.module.split(".")[2])
        elif isinstance(node, ast.Import):
            result.update(alias.name.split(".")[2] for alias in node.names
                          if alias.name.startswith("tools.puzzle_production."))
    return result


def _modules():
    pending, result = set(_ENTRY_MODULES), set()
    while pending:
        name = pending.pop()
        ap.require(name in _FROZEN_MODULES, "Missing integration tool module; start a complete fresh process: " + name)
        if name in result:
            continue
        result.add(name)
        pending.update(_dependencies(_FROZEN_MODULES[name]) - result)
    return sorted(result)


def tool_binding(repo):
    """Bind current relevant code/norm/method bytes and the executing codecs."""
    repo = bio.external(repo)
    ap.require(repo == _ROOT, "Executing integration modules and selected repository differ")
    bound = []
    for name in _modules():
        relative = _PREFIX + name + ".py"
        raw = _read(repo, relative)
        ap.require(raw == _FROZEN_MODULES[name],
                   "Integration implementation changed in the running process; start a fresh process: " + relative)
        module = sys.modules.get("tools.puzzle_production" if name == "__init__" else "tools.puzzle_production." + name)
        if module is not None:
            location = getattr(module, "__file__", None)
            ap.require(location is not None and io.external(location) == repo / relative,
                       "Loaded integration module belongs to another checkout: " + relative)
        bound.append(bg.ref(relative, raw))
    bound.extend(_ref(repo, name) for name in sorted(_NORMS | _METHODS))
    versions = images.versions()
    value = {"files": sorted(bound, key=lambda item: item["file"]),
             "python": platform.python_version(), "pillow": versions["pillow"],
             "codecs": {key: versions[key] for key in ("zlib", "littlecms", "jpeg", "jpeg_turbo")}}
    contract.tool_binding(value)
    return value


def _input(source, ref):
    if ref is None:
        return None
    name = ref.get("directory", ref.get("file"))
    return source if name == "." else io.safe(source, name)


def _background_reconcile(target, plan_path, seconds):
    """Classify an intact booked old bundle or use the native no-op-only path.

    The runner first verifies this previously successful plan's original byte
    inventory. An exact old state is only a rollback observation, never success
    or authority to publish the old plan again.
    """
    with io.budget(seconds):
        path = change.outside(plan_path, target)
        if path.is_dir():
            path = path / "plan.json"
        value, raw, files = change.load_plan(path)
        snapshot = tx.capture(target)
        old = {name: text.encode() if text is not None else None for name, text in value["old"].items()}

        def exact_old(current):
            return (current["texts"] == old and change.source_hashes(current) == value["snapshot"]["sources"] and
                    current["namespaces"] == value["snapshot"]["namespaces"])

        if exact_old(snapshot):
            record = value["request"]["file"].removeprefix("input/")
            original = requests.read(path.parent / "input", record, require_index=False)
            ap.require(requests.read(target, record) == original, "Background work differs from the booked old plan")
            ap.require(change.load_plan(path) == (value, raw, files), "Background rollback plan changed during readback")
            ap.require(exact_old(tx.capture(target)), "Background old state changed during rollback confirmation")
            return {"status": "rollback-confirmed", "id": original[0]["puzzle_id"], "plan_hash": value["plan_hash"]}
        return change.adopt(target, path, seconds=seconds, no_op_only=True)


def execute(phase, job, source, target, output, history, *, export_dir=None, plan_path=None):
    """Make one allowed native call or a strictly read-only rollback observation.

    All selected original refs and tool bytes are checked by the runner before
    and after this call. Native readers/writers still perform their own checks.
    Output roots are already reserved and owned by that same synchronous caller.
    """
    operation = job["operation"]
    ap.require(operation in contract.PHASES and phase in contract.PHASES[operation],
               "Unknown integration operation/phase")
    source, target, output = io.external(source), io.external(target), io.external(output)
    history = io.external(history) if history is not None else None
    inputs = {key: _input(source, ref) for key, ref in job["inputs"].items()}
    budgets = job["budgets"]
    if operation == "register":
        parameters = job["parameters"]
        if phase == "export":
            ap.require(inputs["package"] is not None, "Missing prepared original package")
            with io.budget(budgets["export_seconds"]):
                return target_adapter.export(
                    inputs["package"], io.safe(output, "export"), name=parameters["name"],
                    revision=parameters["runtime_revision"], stem=parameters["stem"], save_slot=parameters["save_slot"],
                    approval_path=inputs["approval"], category_id=parameters["category_id"],
                    categories_path=io.safe(target, categories.PATH), manual_authorization=inputs["manual_authorization"],
                    palette_exception=inputs["palette_exception"], allow_background=parameters["allow_background"],
                    external_root=inputs["external"], history_repo=history if parameters["allow_background"] else None)
        ap.require(export_dir is not None, "Registration requires its preserved complete export")
        export_dir = io.external(export_dir)
        options = {"difficulty": inputs["difficulty"], "rebind_difficulty": parameters["rebind_difficulty"]}
        if phase == "apply":
            # The native transaction owns separate publication and recovery
            # frames. An outer 300-second frame would truncate its recovery.
            return registry.registration(export_dir, target, apply=True, **options,
                                         publication_seconds=budgets["publication_seconds"],
                                         recovery_seconds=budgets["recovery_seconds"])
        with io.budget(budgets[phase + "_seconds"]):
            return registry.registration(export_dir, target, apply=False, **options)
    if phase == "store":
        ap.require(inputs["request"] is not None and inputs["work"] is not None, "Missing prepared background work")
        return change.store(target, inputs["request"], inputs["work"])
    if phase == "plan":
        ap.require(inputs["request"] is not None, "Missing background request")
        path = inputs["request"]
        request = requests.validate(io.json_bytes(io.read(path.parent, path.name, requests.LIMIT), requests.LIMIT))
        return change.plan(target, requests.record_name(request), io.safe(output, "plan"), seconds=budgets["plan_seconds"])
    ap.require(plan_path is not None, "Background adoption requires its preserved complete native plan")
    if phase == "reconcile":
        return _background_reconcile(target, io.external(plan_path), budgets["reconcile_seconds"])
    return change.adopt(target, io.external(plan_path), seconds=budgets["adopt_seconds"])


def _request_files(target, source):
    """Read current work when present; absence never reconstructs retired work."""
    active = bg.current(source)
    if "adoption" not in active:
        return {}, None
    adoption = active["adoption"]
    record_name = adoption["request"]["file"]
    directory = record_name.rsplit("/", 1)[0]
    rows = requests.index_rows(io.json_bytes(io.read(target, requests.INDEX, 8 * 1024 * 1024), 8 * 1024 * 1024))
    if not io.safe(target, directory).exists() and directory not in rows:
        return {}, None
    read = requests.read(target, record_name)
    request, raw, payload = read
    ap.require(bg.ref(record_name, raw) == adoption["request"] and
               all(request[key] == adoption[key] for key in ("revision", "target", "background", "authorization")) and
               request["test_only"] == bg.initial(source)["test_only"],
               "Current background work differs from the adopted source")
    return {directory + "/" + name: raw for name, raw in payload.items()}, (record_name, read)


def reached(target, puzzle_id, snapshot=None):
    """Return job-specific current refs after a complete fresh catalog read.

    A supplied snapshot must be the caller's current in-process tx.capture,
    never a serialized checkpoint or old native plan. Its global reader is not
    repeated per job. Global registry/index bytes are deliberately not returned
    as job refs: later independent jobs may legitimately change those files.
    """
    target = io.external(target)
    with io.budget(300):
        snapshot = tx.capture(target) if snapshot is None else snapshot
        current_registry = snapshot["registry"]
        entry = next((item for item in current_registry["entries"] if item["id"] == puzzle_id), None)
        ap.require(entry is not None, "Reached target is absent from the current catalog")
        ap.require(io.read(target, tx.REGISTRY, 8 * 1024 * 1024) == snapshot["texts"][tx.REGISTRY],
                   "Catalog changed since the fresh reached-target snapshot")
        names = {"game/" + entry["definition"], "game/" + entry["reveal"], content_update.notice_path(entry)}
        for name in (rating.path(puzzle_id), added.path(puzzle_id), reveal.path(puzzle_id), bg.path(puzzle_id)):
            if snapshot["texts"].get(name) is not None:
                names.add(name)
        package = entry["production"]["package"] + "/"
        names.update(name for name in snapshot["namespaces"]["packages"] if name.startswith(package))
        added_raw = snapshot["texts"].get(added.path(puzzle_id))
        if added_raw is not None:
            record = added.validate(io.json_bytes(added_raw, added.LIMIT), puzzle_id)
            if record["provenance"]["evidence"] is not None:
                names.add(record["provenance"]["evidence"]["path"])
        background = bg.load(target, current_registry, entry)
        work, request_read = {}, None
        if background is not None:
            active = bg.current(background)
            for key in ("asset", "notice"):
                if active[key] is not None:
                    names.add(active[key]["file"])
            work, request_read = _request_files(target, background)
        references = {}
        for name in sorted(names):
            raw = _read(target, name)
            if name in snapshot["texts"]:
                ap.require(raw == snapshot["texts"][name], "Reached target text changed: " + name)
            else:
                ap.require(name in snapshot["retained"] and io.checksum(raw) == snapshot["retained"][name],
                           "Reached target retained bytes changed: " + name)
            references[name] = bg.ref(name, raw)
        references.update((name, bg.ref(name, raw)) for name, raw in work.items())
        if request_read is not None:
            ap.require(requests.read(target, request_read[0]) == request_read[1],
                       "Reached background work changed during readback")
        ap.require(tx.read(target, tx.LOCK) is None and not publication.staging(target),
                   "Interrupted registration: recovery required")
        ap.require(io.read(target, tx.REGISTRY, 8 * 1024 * 1024) == snapshot["texts"][tx.REGISTRY] and
                   tx.namespaces(target, current_registry) == snapshot["namespaces"],
                   "Catalog changed during reached-target readback")
        value = {"entry": deepcopy(entry), "files": [references[name] for name in sorted(references)]}
        contract.reached(value)
        return value
