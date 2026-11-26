"""One bounded first-registration transaction and its own recovery."""
import base64
from copy import deepcopy
import os
from pathlib import Path

from . import catalog_io as io, current_content as content, categories
from . import catalog_publication as publication, operation_diagnostics as diagnostics
from .authoring_package import require
from .contract import exact_keys, InvalidInput, Aborted
from . import catalog_rating as rating, catalog_added as added, catalog_method
from .sparse_registration import TrackedPaths
from . import puzzle_record, puzzle_catalog

FORMAT = "picross-puzzle-registration-journal-v1"
LOCK = "content/.registration-pending.json"
STAGE = "content/.registration-journal-current.tmp"
LIMIT = 128*1024*1024
SHARED = (content.RUNTIME, categories.PATH, catalog_method.PATH,
          "game/data/background-capability.json")


def checkpoint(phase, name=None):
    """Fault injection seam; deadline checking is outside the seam."""


def boundary(phase, name=None):
    diagnostics.boundary(phase, name)
    checkpoint(phase, name)


def pack(raw):
    return base64.b64encode(raw).decode("ascii") if raw is not None else None


def unpack(value):
    if value is None: return None
    require(isinstance(value, str) and len(value) <= 4*((content.LIMIT+2)//3), "Oversized journal side")
    raw = base64.b64decode(value, validate=True)
    require(len(raw) <= content.LIMIT and pack(raw) == value, "Noncanonical journal side")
    return raw


def pending(root):
    return io.safe(root, LOCK).exists() or bool(publication.staging(root))


class Snapshot:
    @io.bounded
    def __init__(self, root, identifier):
        self.root = io.external(root)
        self.identifier = rating.identity(identifier)
        self.raw = {}
        self.tracked = TrackedPaths(self.root)
        for name in (LOCK, STAGE):
            self.tracked.check(name)
        require(not pending(self.root), "Pending publication requires recovery")
        ids = puzzle_record.inventory(self.root, self.tracked)
        self.catalog, self.runtime = puzzle_catalog.index(self.read, ids)
        self.ids = ids
        self.read(catalog_method.PATH, catalog_method.LIMIT, missing=True)
        self.read(SHARED[-1], 4096)
        self.existing = next((row for row in self.runtime["entries"] if row["id"] == identifier), None)
        self.delivery = puzzle_catalog.delivery(self.read, identifier, self.catalog, self.existing) if self.existing else None
        self.recheck()

    def read(self, name, limit=content.LIMIT, *, missing=False):
        self.tracked.check(name)
        if name not in self.raw:
            self.raw[name] = io.read(self.root, name, limit, missing=missing)
        return self.raw[name]

    def json(self, name, limit=8*1024*1024):
        return io.json_bytes(self.read(name, limit), limit)

    def recheck(self, *, locked=False):
        self.tracked.recheck()
        require(locked or puzzle_record.inventory(self.root,self.tracked) == self.ids, "Record inventory changed")
        require(locked or not pending(self.root), "Concurrent publication")
        for name, raw in self.raw.items():
            require(io.read(self.root, name, content.LIMIT, missing=True) == raw, "Changed dependency: "+name)


def prepare(snapshot, changes):
    require(snapshot.existing is None, "Occupied ID requires a revision operation")
    sides = {}
    for name, new in changes.items():
        old = snapshot.read(name, missing=True)
        if old != new: sides[name] = {"old": pack(old), "new": pack(new)}
    value = {"format": FORMAT, "id": snapshot.identifier,
             "dependencies": {n: io.checksum(raw) for n, raw in snapshot.raw.items() if n not in sides},
             "files": sides}
    validate(value)
    size = len(content.encoded(value))
    require(size <= LIMIT, f"Registration journal {size} exceeds {LIMIT} bytes")
    snapshot.recheck()
    return value


def validate(value):
    exact_keys(value, {"format", "id", "dependencies", "files"})
    require(value["format"] == FORMAT, "Only current registration recovery is supported")
    identifier = rating.identity(value["id"])
    require(isinstance(value["files"], dict) and len(value["files"]) in (7,9) and
            isinstance(value["dependencies"], dict) and len(value["dependencies"]) <= 8, "Invalid journal inventory")
    sides = {}
    for name, pair in value["files"].items():
        content.relative(name); exact_keys(pair, {"old", "new"})
        sides[name] = (unpack(pair["old"]), unpack(pair["new"]))
        require(sides[name][0] != sides[name][1] and sides[name][1] is not None, "Invalid registration side")
    record_path = puzzle_record.path(identifier)
    require(record_path in sides and content.RUNTIME in sides, "Missing new record or runtime")
    require(all(old is None for name,(old,new) in sides.items() if name != content.RUNTIME),
            "Registration may not replace occupied content")
    require(set(value["dependencies"]) == set(SHARED)-{content.RUNTIME}, "Foreign recovery dependency")
    for checksum in value["dependencies"].values():
        if checksum is not None: content.sha(checksum)
    before, after = (io.json_bytes(raw,content.RUNTIME_LIMIT) for raw in sides[content.RUNTIME])
    cats = {"format":categories.FORMAT, "categories":after["categories"]}
    require(before["categories"] == after["categories"], "Foreign category mutation")
    old_ids = [row["id"] for row in before["entries"]]
    require(identifier not in old_ids, "ID already registered")
    puzzle_catalog.validate_runtime(before,cats,old_ids)
    puzzle_catalog.validate_runtime(after,cats,[*old_ids,identifier])
    require([row for row in after["entries"] if row["id"] != identifier] == before["entries"],
            "Foreign runtime mutation")
    row = next(row for row in after["entries"] if row["id"] == identifier)
    def read(name, limit, *, missing=False):
        raw = sides.get(name,(None,None))[1]
        require(raw is not None and len(raw) <= limit or raw is None and missing, "Missing or oversized delivery: "+name)
        return raw
    delivery = puzzle_catalog.delivery(read,identifier,cats,row)
    record = delivery["record"]
    require(all(record[k]["image_revision"] == 1 for k in ("reveal","background")) and
            record["difficulty"]["rating_revision"] == 1, "First registration requires initial revisions")
    require(record["added"]["provenance"]["kind"] == "registration", "First registration date required")
    require(set(sides) == {content.RUNTIME,*delivery["files"]} and all(delivery["files"].values()),
            "Foreign or incomplete registration write inventory")
    return sides


def temporary(name, checksum):
    path = Path(name)
    return (path.parent / ("."+path.name+".ri-one-"+checksum+".tmp")).as_posix()


def write(root, name, old, new, journal_raw, *, guard=None):
    """Every write has a fresh compare and a durable atomic rename."""
    target = io.safe(root, name)
    require(io.read(root, name, content.LIMIT, missing=True) == old, "Foreign current target: "+name)
    require(io.read(root, LOCK, LIMIT) == journal_raw, "Writer lock changed")
    if new is None:
        boundary("before-remove", name)
        if guard is not None: guard()
        require(io.read(root,name,content.LIMIT,missing=True)==old and io.read(root,LOCK,LIMIT)==journal_raw, "Changed removal target")
        target.unlink()
        publication.sync_directory(target.parent)
    else:
        publication.durable_parents(root, name)
        temp_name = temporary(name, io.checksum(journal_raw))
        temp = io.safe(root, temp_name)
        boundary("before-write", name)
        with temp.open("xb") as stream:
            require(stream.write(new) == len(new), "Short current write")
            stream.flush(); os.fsync(stream.fileno())
        boundary("before-rename", name)
        require(io.read(root, name, content.LIMIT, missing=True) == old and io.read(root, LOCK, LIMIT) == journal_raw,
                "Current target or lock changed before publication")
        if guard is not None: guard()
        publication.rename(temp, target, replace=old is not None)
    require(io.read(root, name, content.LIMIT, missing=True) == new, "Current readback differs: "+name)
    boundary("after-write", name)


def _publish(snapshot, journal, *, publication_seconds=None, recovery_seconds=None, fail_step=None, source_check=None):
    diagnostics.seconds(publication_seconds); diagnostics.seconds(recovery_seconds)
    root = snapshot.root
    sides = validate(journal)
    raw = content.encoded(journal)
    for name in sides:
        snapshot.tracked.check(temporary(name, io.checksum(raw)))
    require(len(raw) <= LIMIT, f"Registration journal {len(raw)} exceeds {LIMIT} bytes")
    with diagnostics.operation("Publication", publication_seconds or 1800,
                               "override" if publication_seconds is not None else "registration-default",
                               recovery_seconds=recovery_seconds):
        snapshot.recheck()
        boundary("before-journal")
        with publication.owned_journal(root,STAGE,LOCK,raw,lambda: recover(root,recovery_seconds=recovery_seconds)):
            boundary("after-journal")
            expected=dict(snapshot.raw)
            def guard():
                snapshot.tracked.recheck()
                require(io.read(root,LOCK,LIMIT)==raw,"Writer lock changed")
                for path,data in expected.items():
                    require(io.read(root,path,content.LIMIT,missing=True)==data,"Changed current dependency: "+path)
                if source_check is not None: source_check()
            try:
                snapshot.recheck(locked=True)
                guard()
            except Exception:
                # Nothing was written. Do not retain a stale plan over another edit.
                require(io.read(root, LOCK, LIMIT) == raw, "Writer lock changed")
                io.safe(root, LOCK).unlink(); publication.sync_directory(root/"content")
                raise
            for step, name in enumerate(sorted(sides, key=lambda n: (n == content.RUNTIME, n)), 1):
                guard()
                write(root, name, *sides[name], raw, guard=guard)
                expected[name]=sides[name][1]
                if fail_step == step: raise RuntimeError("Injected current publication interruption")
            guard()
            for name, (_, new) in sides.items():
                require(io.read(root, name, content.LIMIT) == new, "Final readback differs")
            require(io.read(root, LOCK, LIMIT) == raw, "Writer lock changed")
            io.safe(root, LOCK).unlink(); publication.sync_directory(root/"content")
            diagnostics.durable("registered")
        return {"status": "registered", "registered": True, "id": journal["id"]}


def execute(snapshot, journal, *, publication_seconds=None, recovery_seconds=None, fail_step=None, source_check=None):
    return _publish(snapshot,journal,publication_seconds=publication_seconds,recovery_seconds=recovery_seconds,
                    fail_step=fail_step,source_check=source_check)


def recover(root, *, recovery_seconds=None):
    diagnostics.seconds(recovery_seconds)
    root = io.external(root)
    with diagnostics.operation("Recovery", recovery_seconds or 1800,
                               "override" if recovery_seconds is not None else "registration-default"):
        tracked = TrackedPaths(root)
        for control in (LOCK, STAGE):
            tracked.check(control)
        name = LOCK if io.safe(root, LOCK).exists() else STAGE
        raw = io.read(root, name, LIMIT, missing=True)
        if raw is None:
            require(not publication.staging(root), "Unknown staging data requires inspection")
            diagnostics.durable("no-op")
            return {"status": "no-op", "registered": False}
        value = io.json_bytes(raw, LIMIT)
        sides = validate(value)
        require(content.encoded(value) == raw, "Noncanonical current journal")
        for path in (*sides, *value['dependencies']):
            tracked.check(path)
        current, temps = {}, {}
        for target, pair in sides.items():
            current[target] = io.read(root, target, content.LIMIT, missing=True)
            require(current[target] in pair, "Foreign target blocks recovery: "+target)
            temp_name = temporary(target, io.checksum(raw))
            tracked.check(temp_name)
            temp = io.read(root, temp_name, content.LIMIT, missing=True)
            if temp is not None:
                require(any(data is not None and data.startswith(temp) for data in pair), "Foreign temporary blocks recovery")
                temps[temp_name] = temp
        for target, checksum in value["dependencies"].items():
            require(io.checksum(io.read(root, target, content.LIMIT, missing=True)) == checksum, "Foreign recovery dependency: "+target)
        require(io.read(root, name, LIMIT) == raw, "Recovery lock changed")
        if name == STAGE:
            require(all(current[n] == pair[0] for n, pair in sides.items()), "Unpublished journal with changed targets")
            publication.rename(io.safe(root, STAGE), io.safe(root, LOCK), replace=False)
        for target, temp in temps.items():
            require(io.read(root, target, content.LIMIT) == temp, "Recovery temporary changed")
            io.safe(root, target).unlink(); publication.sync_directory(io.safe(root, target).parent)
        def guard():
            tracked.recheck()
            require(io.read(root,LOCK,LIMIT)==raw,"Recovery lock changed")
            for path,data in current.items():
                require(io.read(root,path,content.LIMIT,missing=True)==data,"Foreign recovery target: "+path)
            for path,checksum in value["dependencies"].items():
                require(io.checksum(io.read(root,path,content.LIMIT,missing=True))==checksum,"Foreign recovery dependency: "+path)
        guard()
        # Disable the visible new row first during rollback, then restore data.
        for target in sorted(sides, key=lambda n: (n != content.RUNTIME, n)):
            if current[target] != sides[target][0]:
                guard()
                write(root, target, current[target], sides[target][0], raw, guard=guard)
                current[target]=sides[target][0]
        guard()
        require(io.read(root, LOCK, LIMIT) == raw, "Recovery journal changed")
        io.safe(root, LOCK).unlink(); publication.sync_directory(root/"content")
        diagnostics.durable("rolled-back")
        return {"status": "rolled-back", "registered": False}
