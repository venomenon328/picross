"""Targeted record and category metadata edits through the shared catalog writer."""
from __future__ import annotations

from copy import deepcopy
import uuid

from . import catalog_io as io, catalog_transaction as tx, categories
from . import content_registry as registry, puzzle_record, puzzle_catalog
from .authoring_package import require
from .contract import canonical_bytes, exact_keys

PLAN_FORMAT = "picross-puzzle-metadata-plan-v1"
VIEW_FORMAT = "picross-metadata-view-v1"
PLAN_LIMIT = 32 * 1024 * 1024
MAX_OPERATIONS = 10000


def _bytes(value):
    return canonical_bytes(value) + b"\n"


def _unlocked(root):
    from . import catalog_publication
    require(not io.safe(root, tx.LOCK).exists() and not catalog_publication.staging(root),
            "Interrupted registration: recovery required")


def _index_state(root):
    state = []
    for name in (categories.PATH, registry.RUNTIME):
        info = io.safe(root, name).lstat()
        state.append((io.signature(info), info.st_ctime_ns))
    return state


class MetadataView:
    """Detached, ID-indexed authoring view; repeated lookups perform no I/O."""

    def __init__(self, root):
        root = io.external(root)
        _unlocked(root)
        before = _index_state(root)
        catalog, runtime = puzzle_catalog.inspect(root)
        self._entries = {r["id"]:{k:r[k] for k in ("id","name","category_id")} for r in runtime["entries"]}
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


def _edit(before, catalog, operations, *, validate_registry):
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
        validate_registry(after, target)
        require(len(_bytes(target)) <= categories.MAX_BYTES, "Categories exceed byte limit")
    return after, target


def _state(runtime):
    return {"metadata":[{k:row[k] for k in ("id","name","category_id")} for row in runtime["entries"]]}


def _validate_metadata(value,cats):
    categories.validate(cats)
    for row in value["metadata"]:
        registry.validate_name(row["name"])
        categories.lookup(cats,row["category_id"])


PLAN_FORMAT = "picross-puzzle-metadata-plan-v1"


@io.bounded
def plan(root, operations, *, _snapshot=None):
    root = io.external(root)
    _unlocked(root)
    texts = {}
    def read(name,limit):
        if name not in texts:
            texts[name] = io.read(root,name,limit)
        return texts[name]
    ids = puzzle_record.inventory(root)
    cats, runtime = puzzle_catalog.index(read,ids)
    before = _state(runtime)
    expanded = _operations(operations,catalog=cats,expanded=_snapshot=="expanded")
    after,target = _edit(before,cats,expanded,validate_registry=_validate_metadata)
    new = {}
    result = deepcopy(runtime)
    result["categories"] = categories.ordered(target)
    changes = []
    for row, old, updated in zip(result["entries"],before["metadata"],after["metadata"],strict=True):
        if old == updated:
            continue
        key = row["id"]
        record = puzzle_record.load(root,key,category_catalog=cats,read=read)
        require(puzzle_record.runtime_row(record) == row, "Selected metadata projection differs")
        record.update(name=updated["name"],category_id=updated["category_id"])
        new[puzzle_record.path(key)] = puzzle_record.encode(record)
        row.update(updated)
        changes.append({"kind":"puzzle","id":key,"before":old,"after":updated})
    a,b = ({r["id"]:r for r in cat["categories"]} for cat in (cats,target))
    changes += [{"kind":"category","id":k,"before":a.get(k),"after":b.get(k)} for k in sorted(a.keys()|b.keys()) if a.get(k)!=b.get(k)]
    if target != cats:
        new[categories.PATH] = _bytes(target)
    if result != runtime:
        new[registry.RUNTIME] = _bytes(result)
    journal = tx.record_journal(texts,new,operation="metadata")
    require(puzzle_record.inventory(root) == ids and all(io.read(root,n,tx.LIMIT) == v for n,v in texts.items()),
            "Metadata sources changed")
    _unlocked(root)
    return {"format":PLAN_FORMAT,"operation":"metadata","operations":expanded,"changes":changes,
            "files":sorted(new),"journal":journal}


@io.bounded
def apply(root,value,*,fail_step=None):
    root = io.external(root)
    exact_keys(value, {"format","operation","operations","changes","files","journal"})
    require(value["format"] == PLAN_FORMAT and value["operation"] == "metadata", "Invalid metadata plan")
    _operations(value["operations"],expanded=True)
    # Reproduce the exact proposal against the current source bytes; preserve generated category IDs.
    fresh = plan(root,value["operations"],_snapshot="expanded")
    require(value == fresh, "Metadata plan differs from current request or sources")
    if not value["files"]:
        return {"status":"noop","changes":[],"files":[]}
    tx.execute(root,value["journal"],fail_step=fail_step)
    return {"status":"updated","changes":value["changes"],"files":value["files"]}


def recover(root):
    return tx.recover(io.external(root))
