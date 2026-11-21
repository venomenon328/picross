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

from . import authoring_package as ap, batch_io as bio
from . import catalog_added as added, catalog_background as bg, catalog_background_change as change
from . import catalog_io as io, catalog_publication as publication, catalog_rating as rating
from . import catalog_transaction as tx, categories, content_registry as registry
from . import images, integration_batch_contract as contract, reveal_source as reveal, target_adapter

_ROOT = Path(__file__).resolve().parents[2]
_PREFIX = "tools/puzzle_production/"
_ENTRY_MODULES = {"__init__", "integration_batch_operations", "integration_batch_contract",
                  "integration_batch_runner", "integration_batch_cli"}
_NORMS = {
    "docs/production/PUZZLE_INTEGRATION_SINGLE_PATH.md", "docs/tools/PRODUCTION_BATCH.md",
    "docs/production/PUZZLE_INTEGRATION.md", "docs/production/ZA1_ADAPTER.md",
    "docs/production/PUZZLE_PRODUCTION.md", "docs/production/PUZZLE_BACKGROUNDS.md", "docs/production/PUZZLE_QUALITY.md",
    "docs/production/REVEAL_TRANSPARENCY.md", "docs/tools/PUZZLE_EDITOR.md", "docs/game/CATEGORIES.md",
    "docs/difficulty/SD_CATALOG.md", "docs/difficulty/SD2_INTEGRATION.md", "docs/difficulty/SD2_ANALYZER.md",
}
from .authoring_rulebook import PATHS as _RULE_PATHS
_NORMS.update(_RULE_PATHS)

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
    import resvg_py
    versions = images.versions()
    value = {"files": sorted(bound, key=lambda item: item["file"]),
             "python": platform.python_version(), "pillow": versions["pillow"],
             "codecs": {key: versions[key] for key in ("zlib", "littlecms", "jpeg", "jpeg_turbo")}}
    value["codecs"].update(resvg_py=resvg_py.__version__, resvg=resvg_py.__resvg_version__)
    contract.tool_binding(value)
    return value


def _input(source, ref):
    if ref is None:
        return None
    name = ref.get("directory", ref.get("file"))
    return source if name == "." else io.safe(source, name)


def _background_reconcile(target,plan_path,seconds):
    return change.adopt(target,plan_path,seconds=seconds,no_op_only=True)


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
        if phase == "export":
            ap.require(inputs["current"] is not None, "Missing final current input")
            with io.budget(budgets["export_seconds"]):
                return target_adapter.export(inputs["current"], io.safe(output, "export"))
        ap.require(export_dir is not None, "Registration requires its preserved current input")
        export_dir = io.external(export_dir)
        if phase == "apply":
            # The native transaction owns separate publication and recovery
            # frames. An outer 300-second frame would truncate its recovery.
            return registry.registration(export_dir, target, apply=True,
                                         publication_seconds=budgets["publication_seconds"],
                                         recovery_seconds=budgets["recovery_seconds"])
        with io.budget(budgets[phase + "_seconds"]):
            return registry.registration(export_dir, target, apply=False)
    if phase == "store":
        ap.require(inputs["request"] is not None and inputs["work"] is not None, "Missing prepared background work")
        return change.store(target, inputs["request"], inputs["work"])
    if phase == "plan":
        ap.require(inputs["request"] is not None, "Missing background request")
        return change.plan(target, inputs["request"], io.safe(output,"plan"), seconds=budgets["plan_seconds"])

    ap.require(plan_path is not None, "Background adoption requires its preserved complete native plan")
    if phase == "reconcile":
        return _background_reconcile(target, io.external(plan_path), budgets["reconcile_seconds"])
    return change.adopt(target, io.external(plan_path), seconds=budgets["adopt_seconds"])


def reached(target, puzzle_id, snapshot=None):
    """Fresh shared indices and selected delivery only, including resume."""
    from .current_registration import Snapshot, SHARED
    from .current_content import ref
    current = Snapshot(target, puzzle_id)
    ap.require(current.delivery is not None, "Reached target is absent")
    value = {"entry": deepcopy(current.existing),
             "files": [ref(name, raw) for name, raw in sorted(current.raw.items())
                       if name not in SHARED and raw is not None]}
    current.recheck()
    contract.reached(value)
    return value
