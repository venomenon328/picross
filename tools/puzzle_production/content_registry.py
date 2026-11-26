"""Current content registry and unchanged runtime-v9 projection."""
from copy import deepcopy
from pathlib import Path
import os
import tempfile
from . import current_content as current, catalog_io, categories, catalog_rating, catalog_added, catalog_method
from .authoring_package import ID, STEM, require
from .contract import canonical_bytes
from . import operation_diagnostics as diagnostic

RUNTIME = current.RUNTIME
IMAGE_RUNTIME_FORMAT = current.RUNTIME_FORMAT
ROOT = Path(__file__).resolve().parents[2]


def atomic_bytes(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".catalog-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def validate_name(name):
    require(isinstance(name, str) and 1 <= len(name) <= 128 and name.strip(), "Invalid puzzle name")
    return name


@diagnostic.measured("Checkout validation", "checkout_validations")
def check_checkout(root, replay=False, *, check_projection=True, pending_journal=None):
    root = catalog_io.external(root)
    lock = catalog_io.read(root, "content/.registration-pending.json", 128*1024*1024, missing=True)
    require(lock is None or lock == pending_journal, "Interrupted publication requires recovery")
    catalog = categories.load(root/categories.PATH)
    from . import puzzle_catalog, puzzle_record
    ids = puzzle_record.inventory(root)
    rows = []
    for identifier in sorted(ids):
        record = puzzle_record.load(root,identifier,category_catalog=catalog)
        row = puzzle_record.runtime_row(record)
        puzzle_catalog.delivery(lambda n,limit,missing=False: catalog_io.read(root,n,limit,missing=missing),
                                identifier,catalog,row,record=record)
        rows.append(row)
    result = {"format":current.RUNTIME_FORMAT,"entries":rows,"categories":categories.ordered(catalog)}
    puzzle_catalog.validate_runtime(result,catalog,ids)
    if check_projection:
        require(catalog_io.read(root,RUNTIME,current.RUNTIME_LIMIT) == current.encoded(result),"Stale current runtime")
    return {"status":"valid","entries":len(rows),"categories":len(catalog["categories"])}


def check_detail(root,snapshot,identifier):
    from .current_registration import Snapshot
    delivery = Snapshot(root,identifier).delivery
    require(delivery is not None,"Unknown puzzle ID")
    return delivery


def sync_runtime(root):
    from . import catalog_transaction as tx
    return tx.sync_runtime(root)


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
