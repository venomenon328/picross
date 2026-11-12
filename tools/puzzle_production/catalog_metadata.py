"""Current puzzle metadata and category edits through the shared catalog writer.

Reading a v4 view only opens the two authoring indexes. Planning and applying
deliberately use the full source-bound transaction path; no player saves, image
derivation or production proof generation belongs to this module.
"""
from __future__ import annotations

from copy import deepcopy
import uuid

from . import catalog_io as io, catalog_transaction as tx, categories
from . import content_registry as registry
from .authoring_package import require
from .contract import canonical_bytes, exact_keys

PLAN_FORMAT = "picross-editor-metadata-plan-v1"
VIEW_FORMAT = "picross-metadata-view-v1"
PLAN_LIMIT = 32 * 1024 * 1024
MAX_OPERATIONS = 10000


def _bytes(value):
    return canonical_bytes(value) + b"\n"


def _catalog(texts):
    return categories.validate(io.json_bytes(texts[categories.PATH], categories.MAX_BYTES))


def _metadata(value, catalog, texts):
    definitions = None
    if value["format"] != registry.METADATA_FORMAT:
        definitions = {e["id"]: texts["game/" + e["definition"]] for e in value["entries"]}
    return registry.current_metadata(value, catalog, definitions=definitions)


def _unlocked(root):
    from . import catalog_publication
    require(not io.safe(root, tx.LOCK).exists() and not catalog_publication.staging(root),
            "Interrupted registration: recovery required")


def _index_state(root):
    state = []
    for name in (categories.PATH, registry.REGISTRY):
        info = io.safe(root, name).lstat()
        state.append((io.signature(info), info.st_ctime_ns))
    return state


class MetadataView:
    """Detached, ID-indexed authoring view; repeated lookups perform no I/O."""

    def __init__(self, root):
        root = io.external(root)
        _unlocked(root)
        before = _index_state(root)
        catalog = categories.validate(io.json_bytes(
            io.read(root, categories.PATH, categories.MAX_BYTES), categories.MAX_BYTES))
        value = registry.validate(io.json_bytes(
            io.read(root, registry.REGISTRY, 8 * 1024 * 1024), 8 * 1024 * 1024), catalog)
        self._entries = registry.current_metadata(value, catalog, root=root)
        self._categories = categories.ordered(catalog)
        require(_index_state(root) == before, "Catalog changed while reading metadata")
        _unlocked(root)

    def lookup(self, identifier):
        require(isinstance(identifier, str) and identifier in self._entries, "Unknown puzzle ID")
        return deepcopy(self._entries[identifier])

    def document(self):
        return {"format": VIEW_FORMAT, "categories": deepcopy(self._categories),
                "entries": [deepcopy(self._entries[key]) for key in sorted(self._entries)]}


def view(root):
    return MetadataView(root).document()


def _operations(value, *, expanded=False, catalog=None):
    require(isinstance(value, list) and len(value) <= MAX_OPERATIONS,
            "Metadata operations must be a list of at most 10000 entries")
    result = deepcopy(value)
    occupied = {e["id"] for e in catalog["categories"]} if catalog is not None else set()
    for item in result:
        require(isinstance(item, dict) and isinstance(item.get("op"), str), "Invalid metadata operation")
        op = item["op"]
        if op == "set_metadata":
            require({"op", "id"} < set(item) <= {"op", "id", "name", "category_id"},
                    "set_metadata needs an ID and name and/or category_id")
        elif op == "category_create":
            exact_keys(item, {"op", "name", "id"} if expanded else {"op", "name"})
            if not expanded:
                identifier = "cat-" + uuid.uuid4().hex
                while identifier in occupied:
                    identifier = "cat-" + uuid.uuid4().hex
                item["id"] = identifier
                occupied.add(identifier)
        elif op == "category_rename":
            exact_keys(item, {"op", "id", "name"})
        elif op == "category_delete":
            require({"op", "id"} <= set(item) <= {"op", "id", "reassign_to"},
                    "Invalid category_delete fields")
        else:
            require(False, "Unsupported metadata operation: " + op)
        require(isinstance(item.get("id"), str), "Metadata operation needs a string ID")
    return result


def _edit(before, catalog, operations):
    after, target = deepcopy(before), deepcopy(catalog)
    rows = {row["id"]: row for row in after["metadata"]}
    for item in operations:
        op, identifier = item["op"], item["id"]
        if op == "set_metadata":
            require(identifier in rows, "Unknown puzzle ID: " + identifier)
            for key in ("name", "category_id"):
                if key in item:
                    rows[identifier][key] = item[key]
        elif op == "category_create":
            require(not any(e["id"] == identifier for e in target["categories"]), "Category ID already exists")
            order = max((e["order"] for e in target["categories"]), default=0) + 1
            target["categories"].append({"id": identifier, "name": item["name"], "order": order})
        elif op == "category_rename":
            categories.lookup(target, identifier)["name"] = item["name"]
        else:
            categories.lookup(target, identifier)
            replacement = item.get("reassign_to")
            if replacement is not None:
                require(replacement != identifier, "Replacement category must be different")
                categories.lookup(target, replacement)
            affected = [row for row in rows.values() if row["category_id"] == identifier]
            require(not affected or replacement is not None, "Occupied category requires explicit complete reassignment")
            for row in affected:
                row["category_id"] = replacement
            target["categories"] = [e for e in target["categories"] if e["id"] != identifier]
        # Check each step, so malformed transient requests cannot hide in a batch.
        registry.validate(after, target)
        require(len(_bytes(target)) <= categories.MAX_BYTES, "Categories exceed byte limit")
    return after, target


def _summary(journal):
    sides = {}
    for side in ("old", "new"):
        texts = {name: text.encode() if text is not None else None for name, text in journal[side].items()}
        catalog = _catalog(texts)
        value = registry.validate(io.json_bytes(texts[registry.REGISTRY], 8 * 1024 * 1024), catalog)
        sides[side] = {"puzzle": _metadata(value, catalog, texts),
                       "category": {e["id"]: e for e in catalog["categories"]}}
    changes = []
    for kind in ("puzzle", "category"):
        before, after = sides["old"][kind], sides["new"][kind]
        for identifier in sorted(set(before) | set(after)):
            if before.get(identifier) != after.get(identifier):
                changes.append({"kind": kind, "id": identifier,
                                "before": before.get(identifier), "after": after.get(identifier)})
    files = sorted(name for name in journal["old"] if journal["old"][name] != journal["new"][name])
    return changes, files


def _plan(root, snapshot, after, catalog, operations, operation):
    changes = {}
    if after != snapshot["registry"]:
        changes[registry.REGISTRY] = _bytes(after)
    if catalog != _catalog(snapshot["texts"]):
        changes[categories.PATH] = _bytes(catalog)
    journal = tx.prepare(root, snapshot, changes, operation=operation, generation="metadata")
    preview, files = _summary(journal)
    result = {"format": PLAN_FORMAT, "operation": operation, "operations": operations,
              "changes": preview, "files": files, "journal": journal}
    require(len(_bytes(result)) <= PLAN_LIMIT, "Metadata plan exceeds 32 MiB")
    return result


def plan(root, operations):
    """Prepare an edit without writing any content or generating a save revision."""
    root = io.external(root)
    snapshot = tx.capture(root)
    registry.require_current(snapshot["registry"])
    catalog = _catalog(snapshot["texts"])
    expanded = _operations(operations, catalog=catalog)
    after, target = _edit(snapshot["registry"], catalog, expanded)
    return _plan(root, snapshot, after, target, expanded, "metadata")


def plan_migration(root):
    """Explicit v2/v3 to v4 migration, with all other sources left byte-identical."""
    root = io.external(root)
    snapshot = tx.capture(root)
    before = snapshot["registry"]
    catalog = _catalog(snapshot["texts"])
    after = deepcopy(before)
    if before["format"] != registry.METADATA_FORMAT:
        metadata = _metadata(before, catalog, snapshot["texts"])
        after.update(format=registry.METADATA_FORMAT,
                     metadata=[metadata[key] for key in sorted(metadata)],
                     backgrounds=deepcopy(before.get("backgrounds", [])))
    registry.validate(after, catalog)
    return _plan(root, snapshot, after, catalog, [], "metadata-migration")


def apply(root, value, *, fail_step=None):
    """Revalidate a reviewed plan and publish through the existing guarded writer."""
    root = io.external(root)
    _unlocked(root)
    value = io.json_bytes(_bytes(value), PLAN_LIMIT)
    exact_keys(value, {"format", "operation", "operations", "changes", "files", "journal"})
    require(value["format"] == PLAN_FORMAT and value["operation"] in ("metadata", "metadata-migration"),
            "Unsupported metadata plan")
    journal = value["journal"]
    require(isinstance(journal, dict) and journal.get("operation") == value["operation"] and
            journal.get("format") == tx.PE_FORMATS[value["operation"]], "Wrong metadata journal binding")
    tx.validate_journal(root, journal, before_write=True)
    operations = _operations(value["operations"], expanded=True)
    old_texts = {name: text.encode() if text is not None else None for name, text in journal["old"].items()}
    before = io.json_bytes(old_texts[registry.REGISTRY], 8 * 1024 * 1024)
    catalog = _catalog(old_texts)
    if value["operation"] == "metadata":
        registry.require_current(before)
        after, target = _edit(before, catalog, operations)
        require(io.json_bytes(journal["new"][registry.REGISTRY].encode(), 8 * 1024 * 1024) == after and
                io.json_bytes(journal["new"][categories.PATH].encode(), categories.MAX_BYTES) == target,
                "Metadata operations differ from the bound proposed result")
    else:
        require(not operations, "Migration cannot contain metadata edits")
    changes, files = _summary(journal)
    require(value["changes"] == changes and value["files"] == files, "Metadata plan preview differs from its journal")
    # The shared guard includes unchanged bytes, missing sidecars and namespaces.
    tx.guard(root, journal, old_only=True)
    _unlocked(root)
    if not files:
        return {"status": "noop", "changes": [], "files": []}
    tx.execute(root, journal, fail_step=fail_step)
    return {"status": "migrated" if value["operation"] == "metadata-migration" else "updated",
            "changes": changes, "files": files}


def recover(root):
    return tx.recover(io.external(root))
