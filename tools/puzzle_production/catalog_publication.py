"""AT durable publication and repeatable recovery, shared by all catalog writers.

The journal is the only backup authority. Forward guards require the exact
phase reached by this process; recovery accepts only fully verified own states.
"""
import base64
from copy import deepcopy
import ctypes
import os
from pathlib import Path
import re
import tempfile
from contextlib import contextmanager

from .authoring_package import require, sha
from .contract import canonical_bytes, exact_keys, integer, Aborted
from . import catalog_io as io, reveal_source as reveal

PREFIX = b'{"format":"picross-reveal-adoption-journal-v1",'
NORMAL_LIMIT = 24 * 1024 * 1024
LIMIT = 128 * 1024 * 1024


def staging(root):
    directory = io.safe(root, "content")
    return sorted(p.relative_to(root).as_posix() for p in directory.iterdir()
                  if p.name.startswith(".registration-journal-") and p.name.endswith(".tmp"))


def read_journal(root, name="content/.registration-pending.json"):
    p = io.safe(root, name)
    if not p.exists(): return None
    require(p.is_file(), "Journal must be a regular file")
    size = p.stat().st_size
    if size > LIMIT: raise Aborted("resource_limit: journal exceeds 128 MiB")
    with p.open("rb") as stream: prefix = stream.read(4096)
    require(size <= NORMAL_LIMIT or prefix.startswith(PREFIX), "Only reveal journals may exceed 24 MiB")
    return io.read(root, name, LIMIT if prefix.startswith(PREFIX) else NORMAL_LIMIT)


def journal_bytes(j):
    raw = b'{"format":' + canonical_bytes(j["format"]) + b"," + canonical_bytes({k: v for k, v in j.items() if k != "format"})[1:] + b"\n"
    limit = LIMIT if j["format"] == "picross-reveal-adoption-journal-v1" else NORMAL_LIMIT
    if len(raw) > limit: raise Aborted("resource_limit: transaction journal exceeds byte limit")
    return raw


def binary(raw):
    return {"sha256": io.checksum(raw), "bytes": len(raw), "base64": base64.b64encode(raw).decode("ascii")}


def binary_shape(value):
    exact_keys(value, {"sha256", "bytes", "base64"})
    sha(value["sha256"])
    integer(value["bytes"], 1, reveal.IMAGE_LIMIT, "binary byte count")
    require(isinstance(value["base64"], str) and len(value["base64"]) == 4 * ((value["bytes"] + 2) // 3) and
            len(value["base64"]) <= 44739244, "Invalid Base64 encoded length")


def binary_chunks(value):
    binary_shape(value)
    # A multiple of four, decoding to less than one MiB per temporary buffer.
    for start in range(0, len(value["base64"]), io.CHUNK):
        io.tick()
        encoded = value["base64"][start:start + io.CHUNK]
        raw = base64.b64decode(encoded, validate=True)
        require(base64.b64encode(raw).decode("ascii") == encoded, "Noncanonical Base64")
        yield raw


def decode_binary(value):
    raw = b"".join(binary_chunks(value))
    require(len(raw) == value["bytes"] and io.checksum(raw) == value["sha256"], "Binary journal hash/size differs")
    return raw


def validate_replacements(j, registry):
    replacements = j["replacements"]
    require(isinstance(replacements, dict), "Invalid replacement map")
    if j["operation"] != "reveal-adoption":
        require(not replacements, "This journal cannot replace binaries")
        return
    entries = {"game/" + e["reveal"]: e for e in registry["entries"]}
    require(replacements and set(replacements) <= set(entries), "Invalid reveal replacement paths")
    total = 0
    for name, pair in replacements.items():
        exact_keys(pair, {"old", "new"})
        for value in pair.values():
            binary_shape(value)
            total += value["bytes"]
        require(pair["old"]["sha256"] != pair["new"]["sha256"], "Binary replacement is unchanged")
    if total > 96 * 1024 * 1024: raise Aborted("resource_limit: replacements exceed 96 MiB")
    from .target_adapter import validate_reveal
    with tempfile.TemporaryDirectory(prefix="at-image-check-") as directory:
        for name, pair in replacements.items():
            p = Path(directory) / ("image" + Path(name).suffix)
            entry = entries[name]
            for value in pair.values():
                with p.open("wb") as stream:
                    for block in binary_chunks(value): stream.write(block)
                require(p.stat().st_size == value["bytes"] and io.file_hash(p.parent, p.name, reveal.IMAGE_LIMIT) == value["sha256"], "Binary backup binding differs")
                validate_reveal(p, entry["production"]["width"], entry["production"]["height"])


def sync_directory(path):
    """Flush the directory entry, including on the actual Windows filesystem."""
    if os.name == "nt":
        from ctypes import wintypes as w
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE]
        k.CreateFileW.restype = w.HANDLE
        k.FlushFileBuffers.argtypes = [w.HANDLE]
        k.CloseHandle.argtypes = [w.HANDLE]
        handle = k.CreateFileW(str(path), 0x40000000, 7, None, 3, 0x02000000 | 0x00200000, None)
        if handle == w.HANDLE(-1).value: raise ctypes.WinError(ctypes.get_last_error())
        try:
            if not k.FlushFileBuffers(handle): raise ctypes.WinError(ctypes.get_last_error())
        finally: k.CloseHandle(handle)
    else:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
        try: os.fsync(fd)
        finally: os.close(fd)


def rename(source, target, *, replace):
    if os.name == "nt":
        from ctypes import wintypes as w
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.MoveFileExW.argtypes = [w.LPCWSTR, w.LPCWSTR, w.DWORD]
        if not k.MoveFileExW(str(source), str(target), 8 | (1 if replace else 0)):
            raise ctypes.WinError(ctypes.get_last_error())
    elif replace:
        os.replace(source, target)
    else:
        libc = ctypes.CDLL(None, use_errno=True)
        require(hasattr(libc, "renameat2"), "Atomic no-replace rename unavailable")
        libc.renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        if libc.renameat2(-100, os.fsencode(source), -100, os.fsencode(target), 1):
            raise OSError(ctypes.get_errno(), "Atomic no-replace rename failed", str(target))
    sync_directory(target.parent)


def durable_parents(root, name):
    target = io.safe(root, name)
    missing, p = [], target.parent
    while not p.exists(): missing.append(p); p = p.parent
    for p in reversed(missing):
        io.safe(root, p.relative_to(root).as_posix())
        p.mkdir()
        sync_directory(p.parent)
    return io.safe(root, name)


def inventory(j, raw):
    names = sorted(set(j["additions"]) | set(j.get("replacements", {})) |
                   {n for n in j["old"] if j["old"][n] != j["new"][n]} |
                   {"game/data/registry.json"})
    # Runtime is only a write target if publication or recovery actually differs.
    from . import catalog_transaction as tx
    before = io.json_bytes(j["old"][tx.REGISTRY].encode(), 8 * 1024 * 1024)
    restore = j["old"][tx.RUNTIME] if j["operation"] == "reveal-adoption" else tx.projection(j["old"], before).decode()
    if j["old"][tx.RUNTIME] == j["new"][tx.RUNTIME] == restore: names.remove(tx.RUNTIME)
    return {n: (Path(n).parent / (".registration-" + io.checksum(raw) + "-" + str(i) + ".tmp")).as_posix()
            for i, n in enumerate(names)}


def temp_candidates(j, name, additions=None):
    from . import catalog_transaction as tx
    if name in j.get("replacements", {}):
        for v in j['replacements'][name].values(): yield decode_binary(v)
        return
    if name in j["old"]:
        values = [v.encode() for v in (j["old"][name], j["new"][name]) if v is not None]
        if name == tx.RUNTIME and j["operation"] != "reveal-adoption":
            before = io.json_bytes(j["old"][tx.REGISTRY].encode(), 8 * 1024 * 1024)
            values.append(tx.projection(j["old"], before))
        yield from values
    elif additions and name in additions:
        yield io.read(additions[name].parent, additions[name].name, 64 * 1024 * 1024)


def check_temps(root, j, raw, *, additions=None):
    temps = inventory(j, raw)
    present = set()
    for name, temporary in temps.items():
        data = io.read(root, temporary, 64 * 1024 * 1024, missing=True)
        if data is None: continue
        if name in j.get('replacements',{}) or name in j['old'] or additions and name in additions:
            require(any(candidate.startswith(data) for candidate in temp_candidates(j,name,additions)), "Foreign transaction temporary bytes: " + temporary)
        else:
            # Interrupted package additions have no backup bytes in the journal;
            # only complete, hash-bound temporaries are recoverable.
            require(io.checksum(data) == j["additions"][name], "Unverifiable package temporary: " + temporary)
        present.add(temporary)
    return present


def guard(root, j, *, raw=None, expected=None, old_only=False, additions=None):
    from . import catalog_transaction as tx, catalog_rating as rating, catalog_added as added
    registries = [io.json_bytes(j[s][tx.REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new")]
    raw = journal_bytes(j) if raw is None else raw
    if not old_only: require(read_journal(root) == raw, "Journal changed; preserve all transaction files")
    temps = check_temps(root, j, raw, additions=additions)
    require(not old_only or not temps, "Transaction temporary already exists")
    reveal.source_paths(root, *registries, temporary=temps)
    rating.source_paths(root, *registries, temporary=temps)
    reports = {n for n in j["retained"] if n.startswith(added.ROOT + "/reports/")}
    if j["operation"] == "added-adoption": reports |= tx.report_names(j["report_run"], j["operation"])
    added.source_paths(root, *registries, extra_reports=reports, temporary=temps)
    allowed_sd = {n for n in j["retained"] if n.startswith("content/difficulty/reports/")} | tx.report_names(j["report_run"], j["operation"])
    sd = io.safe(root, "content/difficulty/reports")
    if sd.exists():
        require(all(p.relative_to(root).as_posix() in allowed_sd | temps for p in sd.rglob("*") if p.is_file()), "Foreign difficulty report appeared")
    for n, old in j["old"].items():
        current = tx.read(root, n)
        candidates = [old]
        if not old_only:
            candidates.append(j["new"][n])
            if n == tx.RUNTIME and j["operation"] != "reveal-adoption": candidates.append(tx.projection(j["old"], registries[0]).decode())
        require(current in [v.encode() if v is not None else None for v in candidates], "Transaction target changed; preserve journal: " + n)
        if expected is not None: require(io.checksum(current) == expected[n], "Transaction phase changed: " + n)
    for n, pair in j.get("replacements", {}).items():
        checksum = io.file_hash(root, n, reveal.IMAGE_LIMIT)
        require(checksum in ([pair["old"]["sha256"]] if old_only else [v["sha256"] for v in pair.values()]), "Foreign/missing reveal; preserve journal: " + n)
        if expected is not None: require(checksum == expected[n], "Binary publication phase changed: " + n)
    for n, h in j["retained"].items():
        require(io.file_hash(root, n) == h, "Retained source changed; preserve journal: " + n)
    for n, h in j["additions"].items():
        data = io.read(root, n, 64 * 1024 * 1024, missing=True)
        require(data is None if old_only else data is None or io.checksum(data) == h, "Foreign addition; preserve journal: " + n)
        if expected is not None: require(io.checksum(data) == expected[n], "Addition publication phase changed: " + n)
    packages = {e["production"]["package"] for r in registries for e in r["entries"]}
    allowed_packages = set(j["retained"]) | set(j["additions"]) | temps
    for name in packages:
        p = io.safe(root, name)
        if p.exists():
            for child in p.rglob("*"):
                n = child.relative_to(root).as_posix()
                child = io.safe(root, n)
                require(not child.is_file() or n in allowed_packages, "Transaction package changed; unexpected file: " + n)
    return temps


def checkpoint(phase, name=None):
    """Fault boundary for process-based tests; inert in production."""


@contextmanager
def addition_temporary(path):
    """Package hashes cannot prove arbitrary partial bytes after a hard kill.

    Keep incomplete package bytes OS-owned: delete-on-close on Windows, unnamed
    O_TMPFILE on Linux. Only complete, flushed bytes survive under the journal's
    deterministic name. Image/text replacements still retain their exact prefixes.
    """
    if os.name=='nt':
        import msvcrt
        from ctypes import wintypes as w
        k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,w.LPVOID,w.DWORD,w.DWORD,w.HANDLE]
        k.CreateFileW.restype=w.HANDLE
        k.SetFileInformationByHandle.argtypes=[w.HANDLE,ctypes.c_int,w.LPVOID,w.DWORD]
        handle=k.CreateFileW(str(path),0xC0010000,7,None,1,0x04200100,None)
        if handle==w.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
        fd=msvcrt.open_osfhandle(handle,os.O_RDWR|os.O_BINARY)
        def keep():
            flags=w.DWORD(8)  # FileDispositionInfoEx: clear only the on-close bit.
            if not k.SetFileInformationByHandle(handle,21,ctypes.byref(flags),4):raise ctypes.WinError(ctypes.get_last_error())
    else:
        require(hasattr(os,'O_TMPFILE'),'Recoverable package temporary unavailable')
        fd=os.open(path.parent,os.O_RDWR|os.O_TMPFILE,0o644)
        def keep():
            libc=ctypes.CDLL(None,use_errno=True)
            libc.linkat.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_int]
            if libc.linkat(-100,os.fsencode('/proc/self/fd/'+str(fd)),-100,os.fsencode(path),0x400):
                raise OSError(ctypes.get_errno(),'Complete package temporary publication failed',str(path))
    with os.fdopen(fd,'w+b') as stream:
        yield stream,keep


def addition_preflight(root, temps):
    # Exercise support on every actual target directory before publishing a lock
    # or active file. These exclusive empty probes are removed before P0.
    for temporary in sorted(set(temps)):
        path=durable_parents(root,temporary)
        require(not path.exists(),'Transaction temporary already exists')
        with addition_temporary(path) as (stream,keep):
            stream.flush();os.fsync(stream.fileno());keep()
        require(io.read(root,temporary,0)==b'','Package temporary probe changed')
        path.unlink();sync_directory(path.parent)


def write(root, name, data, temporary, guard_fn, *, package_addition=False):
    target = durable_parents(root, name)
    if data is None:
        guard_fn()
        io.safe(root, name).unlink(missing_ok=True)
        sync_directory(target.parent)
        return
    tmp = io.safe(root, temporary)
    if package_addition:
        with addition_temporary(tmp) as (stream,keep):
            for offset in range(0,len(data),io.CHUNK):
                io.tick();stream.write(data[offset:offset+io.CHUNK]);checkpoint('temp-prefix',name)
            stream.flush();os.fsync(stream.fileno());stream.seek(0)
            for offset in range(0,len(data),io.CHUNK):
                io.tick();require(stream.read(io.CHUNK)==data[offset:offset+io.CHUNK],'Package temporary readback differs')
            keep()
        require(io.read(root,temporary,64*1024*1024)==data,'Complete package temporary differs')
        checkpoint('temp-complete',name);guard_fn()
        rename(io.safe(root,temporary),io.safe(root,name),replace=False)
        return
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "wb") as stream:
        for offset in range(0, len(data), io.CHUNK):
            io.tick(); stream.write(data[offset:offset + io.CHUNK])
            checkpoint("temp-prefix", name)
        stream.flush(); os.fsync(stream.fileno())
    require(io.read(root, temporary, 64 * 1024 * 1024) == data, "Temporary readback differs")
    checkpoint("temp-complete", name)
    guard_fn()
    target = io.safe(root, name)
    rename(io.safe(root, temporary), target, replace=target.exists())


def cleanup_temps(root, j, raw, guard_fn):
    for temporary in sorted(check_temps(root, j, raw)):
        guard_fn()
        target = io.safe(root, temporary)
        target.unlink(); sync_directory(target.parent)


def execute(root, j, additions=None, *, fail_step=None, under_lock=None):
    with io.budget(300):
        return _execute(root,j,additions,fail_step=fail_step,under_lock=under_lock)


def _execute(root, j, additions=None, *, fail_step=None, under_lock=None):
    from . import catalog_transaction as tx
    from .content_registry import check_checkout
    additions = additions or {}
    tx.validate_journal(root, j, before_write=True)
    raw = journal_bytes(j)
    temps = inventory(j, raw)
    require(not staging(root) and read_journal(root) is None, "Interrupted registration: recovery required")
    # Exercise the actual directory durability primitive before active mutation.
    for n in {tx.LOCK, *temps}:
        p = io.safe(root, n).parent
        while not p.exists(): p = p.parent
        sync_directory(p)
    if os.name != "nt": require(hasattr(ctypes.CDLL(None), "renameat2"), "Atomic no-replace rename unavailable")
    addition_preflight(root,[temps[n] for n in j['additions']])
    checkpoint("P0")
    stage_name = "content/.registration-journal-" + io.checksum(raw) + ".tmp"
    stage = io.safe(root, stage_name)
    with stage.open("xb") as stream:
        for offset in range(0, len(raw), io.CHUNK):
            stream.write(raw[offset:offset + io.CHUNK]); checkpoint("journal-prefix")
        stream.flush(); os.fsync(stream.fileno())
    require(read_journal(root, stage_name) == raw, "Journal staging readback differs")
    checkpoint("journal-complete")
    rename(stage, io.safe(root, tx.LOCK), replace=False)
    checkpoint("P1")
    expected = {n: io.checksum(v.encode() if v is not None else None) for n, v in j["old"].items()}
    expected.update({n: pair["old"]["sha256"] for n, pair in j["replacements"].items()})
    expected.update({n: None for n in j["additions"]})
    guard_fn = lambda: guard(root, j, raw=raw, expected=expected, additions=additions)
    # A failed P2 foreign-source guard preserves the published journal.
    guard_fn()
    try:
        if under_lock: under_lock()
        checkpoint("P2")
        for i, n in enumerate(sorted(j["additions"])):
            guard_fn()
            data = io.read(additions[n].parent, additions[n].name, 64 * 1024 * 1024)
            require(io.checksum(data) == j["additions"][n], "Staged package changed")
            write(root, n, data, temps[n], guard_fn,package_addition=True)
            expected[n] = io.checksum(data)
            checkpoint("P3", n)
            if i == 0 and fail_step == "crash": raise InterruptedError("Injected registration interruption")
            if i == 0 and fail_step == "files": raise OSError("Injected registration interruption")
        for n, pair in sorted(j["replacements"].items()):
            guard_fn(); write(root, n, decode_binary(pair["new"]), temps[n], guard_fn)
            expected[n] = pair["new"]["sha256"]; checkpoint("P3", n)
        if fail_step == "crash-package": raise InterruptedError("Injected update crash after package")
        if j["operation"] == "registration":
            from .target_adapter import verify_export
            before, after = (io.json_bytes(j[s][tx.REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
            verify_export(io.safe(root, tx._delta(j, before, after)))
        names = sorted(n for n in j["new"] if n != tx.RUNTIME and j["old"][n] != j["new"][n])
        if j["old"][tx.RUNTIME] != j["new"][tx.RUNTIME]: names.append(tx.RUNTIME)
        for n in names:
            guard_fn()
            data = j["new"][n].encode() if j["new"][n] is not None else None
            write(root, n, data, temps[n], guard_fn); expected[n] = io.checksum(data)
            checkpoint("P5" if n == tx.RUNTIME else "P4", n)
            if fail_step == "crash-" + n or n == tx.REGISTRY and fail_step == "crash-index" or n == tx.RUNTIME and fail_step == "crash-runtime": raise InterruptedError("Injected transaction interruption: " + n)
            if fail_step == n or n == tx.REGISTRY and fail_step == "index": raise OSError("Injected update failure: " + n)
        if tx.RUNTIME not in names:
            # P5 still has a boundary when the projection is byte-identical.
            # Keep interruption coverage without manufacturing a runtime write.
            checkpoint("P5", tx.RUNTIME)
            if fail_step in ("crash-"+tx.RUNTIME,"crash-runtime"): raise InterruptedError("Injected transaction interruption: "+tx.RUNTIME)
            if fail_step == tx.RUNTIME: raise OSError("Injected update failure: "+tx.RUNTIME)
        guard_fn(); check_checkout(root, replay=j['operation']=='registration', pending_journal=raw); guard_fn()
        cleanup_temps(root, j, raw, guard_fn)
        checkpoint("P6"); guard_fn()
        io.safe(root, tx.LOCK).unlink(); sync_directory(root / "content")
    except InterruptedError:
        raise
    except BaseException:
        # A separate recovery budget is deliberately independent of the expired
        # forward budget, and foreign data still blocks before rollback writes.
        token = io._deadline.set(None)
        try:
            with io.budget(300): recover(root)
        finally: io._deadline.reset(token)
        raise


def recover(root):
    from . import catalog_transaction as tx
    from .content_registry import check_checkout
    raw = read_journal(root)
    if raw is None:
        remnants = staging(root)
        require(len(remnants) == 1, "Missing/ambiguous journal staging; preserve files")
        raw = read_journal(root, remnants[0])
        j = io.json_bytes(raw, LIMIT)
        require(tx.modern(j) and raw == journal_bytes(j) and remnants[0] == "content/.registration-journal-" + io.checksum(raw) + ".tmp", "Incomplete/foreign journal staging")
        tx.validate_journal(root, j, before_write=True)
        guard(root, j, raw=raw, old_only=True)
        require(read_journal(root) is None and read_journal(root, remnants[0]) == raw, "Journal appeared/changed during staging recovery")
        io.safe(root, remnants[0]).unlink(); sync_directory(root / "content")
        return {"status": "rolled-back", "registered": False}
    j = io.json_bytes(raw, LIMIT)
    require(tx.modern(j) and raw == journal_bytes(j), "Noncanonical transaction journal")
    _, runtime = tx.validate_journal(root, j)
    guard_fn = lambda: guard(root, j, raw=raw)
    guard_fn(); checkpoint("R0")
    cleanup_temps(root, j, raw, guard_fn)
    temps = inventory(j, raw)
    for n, pair in sorted(j["replacements"].items()):
        guard_fn()
        if io.file_hash(root, n, reveal.IMAGE_LIMIT) != pair["old"]["sha256"]:
            write(root, n, decode_binary(pair["old"]), temps[n], guard_fn)
        checkpoint("R1-binary", n)
    for n in sorted(j["old"]):
        if n == tx.RUNTIME: continue
        data = j["old"][n].encode() if j["old"][n] is not None else None
        guard_fn()
        if tx.read(root, n) != data: write(root, n, data, temps[n], guard_fn)
        checkpoint("R1-text", n)
    for n in sorted(j["additions"], reverse=True):
        guard_fn()
        target = io.safe(root, n)
        if target.exists(): target.unlink(); sync_directory(target.parent)
        checkpoint("R1-addition", n)
    guard_fn()
    if tx.read(root, tx.RUNTIME) != runtime.encode(): write(root, tx.RUNTIME, runtime.encode(), temps[tx.RUNTIME], guard_fn)
    checkpoint("R1-runtime")
    guard_fn(); check_checkout(root, pending_journal=raw); guard_fn()
    require(all(tx.read(root, n) == (v.encode() if v is not None else None) for n, v in {**j["old"], tx.RUNTIME: runtime}.items()) and
            all(not io.safe(root, n).exists() for n in j["additions"]), "Recovery goal differs")
    cleanup_temps(root, j, raw, guard_fn)
    checkpoint("R2"); guard_fn()
    io.safe(root, tx.LOCK).unlink(); sync_directory(root / "content")
    return {"status": "rolled-back", "registered": False}
