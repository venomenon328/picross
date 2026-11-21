"""Current content registry and unchanged runtime-v9 projection."""
from copy import deepcopy
from pathlib import Path
import os
import tempfile
from . import current_content as current, catalog_io, categories, catalog_rating, catalog_added, catalog_method
from .authoring_package import ID, STEM, require
from .contract import canonical_bytes
from . import operation_diagnostics as diagnostic

REGISTRY, RUNTIME = current.REGISTRY, current.RUNTIME
FORMAT = BACKGROUND_FORMAT = METADATA_FORMAT = current.FORMAT
METADATA_RUNTIME_FORMAT = IMAGE_RUNTIME_FORMAT = current.RUNTIME_FORMAT
ROOT = Path(__file__).resolve().parents[2]


def atomic_bytes(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".catalog-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def validate(registry, catalog):
    return current.validate(registry, catalog)


def validate_entries(entries, catalog=None):
    return current.entries(entries, catalog)


def validate_name(name):
    require(isinstance(name, str) and 1 <= len(name) <= 128 and name.strip(), "Invalid puzzle name")
    return name


def require_current(registry):
    require(isinstance(registry, dict) and registry.get("format") == FORMAT, "Current content authority required")


def current_metadata(registry, catalog, root=None, *, definitions=None):
    validate(registry, catalog)
    return {row["id"]: deepcopy(row) for row in registry["metadata"]}


def projection(registry, catalog, root=None, *, ratings=None, added=None, backgrounds=None, reveals=None, catalogs=None, version=None):
    validate(registry, catalog)
    require(version is None or version == 9, "Runtime v9 required")
    if root is not None and all(v is None for v in (ratings, added, backgrounds, reveals, catalogs)):
        rows = [current.runtime_row(current.selected(root, registry, e["id"])) for e in registry["entries"]]
    else:
        require(all(v is not None for v in (ratings, added, backgrounds, reveals, catalogs)), "Projection requires complete current data")
        meta = {row["id"]: row for row in registry["metadata"]}
        rows = [{**{k: e[k] for k in ("id", "key", "save_slot", "definition", "visible")},
                 "catalog_reveal": catalogs[e["id"]], "reveal": reveals[e["id"]], "name": meta[e["id"]]["name"], "category_id": meta[e["id"]]["category_id"],
                 "difficulty": catalog_rating.project(ratings[e["id"]]), "added_at": added[e["id"]]["added_at"],
                 "background": backgrounds[e["id"]]} for e in registry["entries"]]
    result = {"format": IMAGE_RUNTIME_FORMAT, "categories": categories.ordered(catalog), "entries": rows}
    require(len(current.encoded(result)) <= current.RUNTIME_LIMIT, "Runtime exceeds byte limit")
    return result


@diagnostic.measured("Checkout validation", "checkout_validations")
def check_checkout(root, replay=False, *, check_projection=True, pending_journal=None):
    root = catalog_io.external(root)
    lock = catalog_io.read(root, "content/.registration-pending.json", 128*1024*1024, missing=True)
    require(lock is None or lock == pending_journal, "Interrupted publication requires recovery")
    catalog = categories.load(root/categories.PATH)
    registry = validate(catalog_io.json_bytes(catalog_io.read(root, REGISTRY, 8*1024*1024), 8*1024*1024), catalog)
    result = projection(registry, catalog, root)
    if check_projection:
        require(catalog_io.read(root, RUNTIME, current.RUNTIME_LIMIT) == current.encoded(result), "Stale current runtime")
    return {"status": "valid", "entries": len(registry["entries"]), "categories": len(catalog["categories"])}


def check_detail(root, snapshot, identifier):
    delivery = current.selected(root, snapshot["registry"], identifier)
    runtime = catalog_io.json_bytes(snapshot["texts"][RUNTIME], current.RUNTIME_LIMIT)
    require(next(e for e in runtime["entries"] if e["id"] == identifier) == current.runtime_row(delivery), "Stale selected runtime")
    return delivery


def sync_runtime(root):
    from . import catalog_transaction as tx
    snapshot = tx.capture(root, allow_stale=True)
    catalog = catalog_io.json_bytes(snapshot["texts"][categories.PATH], categories.MAX_BYTES)
    expected = current.encoded(projection(snapshot["registry"], catalog, root))
    if snapshot["texts"][RUNTIME] != expected:
        tx.execute(root, tx.prepare(root, snapshot, {}, operation="sync"))
    return {"status": "projected", "entries": len(snapshot["registry"]["entries"]), "categories": len(catalog["categories"])}


def registration(export_dir, root, *, apply=False, fail_step=None, publication_seconds=None, recovery_seconds=None):
    from .catalog_integration import integrate
    return integrate(export_dir, root, apply=apply, fail_step=fail_step,
                     publication_seconds=publication_seconds, recovery_seconds=recovery_seconds)


@catalog_io.bounded
def _recovery_kind(root):
    from . import current_registration, editor_change, catalog_transaction
    from .catalog_publication import EDITOR_PREFIX
    for name in (editor_change.LOCK, editor_change.STAGE):
        path = catalog_io.safe(root, name)
        if path.exists():
            with path.open("rb") as stream: prefix = stream.read(len(EDITOR_PREFIX))
            if prefix == EDITOR_PREFIX: return "editor"
            break
    raw = catalog_io.read(root, current_registration.LOCK, 128*1024*1024, missing=True)
    if raw is None: raw = catalog_io.read(root, catalog_transaction.STAGE, 128*1024*1024, missing=True)
    if raw is not None and catalog_io.json_bytes(raw, 128*1024*1024).get("format") == catalog_transaction.FORMAT:
        return "catalog"
    return "registration"


def recover(root, *, recovery_seconds=None):
    from . import current_registration, editor_change, catalog_transaction
    diagnostic.seconds(recovery_seconds)
    root = catalog_io.external(root)
    kind = _recovery_kind(root)
    if kind in ("editor", "catalog"):
        require(recovery_seconds is None, "This operation has its own recovery budget")
        with catalog_io.budget(300):
            return (editor_change if kind == "editor" else catalog_transaction).recover(root)
    return current_registration.recover(root, recovery_seconds=recovery_seconds)
