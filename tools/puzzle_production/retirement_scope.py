"""PW-PERF-E invocation-only bytes and selected authority. No persistent cache."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import os
import ctypes
from . import catalog_io as io, catalog_transaction as tx
from . import content_registry as cr, categories, reveal_source as reveal, catalog_background as bg
from . import catalog_added as added, catalog_publication as publication
from .authoring_package import require
from .contract import canonical_bytes


if os.name == "nt":
    from ctypes import wintypes
    class _BasicInfo(ctypes.Structure):
        _fields_ = [(name, ctypes.c_longlong) for name in
                    ("creation", "access", "write", "change")] + [("attributes", wintypes.DWORD)]
    _kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    _open = _kernel.CreateFileW
    _open.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                      wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    _open.restype = wintypes.HANDLE
    _info = _kernel.GetFileInformationByHandleEx
    _info.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    _info.restype = wintypes.BOOL
    _close = _kernel.CloseHandle
    _close.argtypes = [wintypes.HANDLE]
    _close.restype = wintypes.BOOL


def change_time(path, stat):
    # Python's Windows st_ctime is creation time, not NTFS ChangeTime. Restoring
    # mtime after an equal-size write must never authorize cached source bytes.
    if os.name != "nt": return stat.st_ctime_ns
    handle = _open(str(path), 0x80, 7, None, 3, 0, None)  # attributes only
    if handle == ctypes.c_void_p(-1).value: raise ctypes.WinError(ctypes.get_last_error())
    try:
        info = _BasicInfo()
        if not _info(handle, 0, ctypes.byref(info), ctypes.sizeof(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        return info.change
    finally: _close(handle)


class Reads:
    def __init__(self, root):
        self.root, self.data, self.identities, self.hashes = root, {}, {}, {}
        self.bytes = 0
        self.backgrounds = {}
        self.lock = None

    def identity(self, name):
        p = io.safe(self.root, name)
        try: info = p.lstat()
        except FileNotFoundError: return None
        return io.signature(info) + (change_time(p, info), info.st_mode)

    def guard(self, name):
        require(self.identity(name) == self.identities[name], 'Retirement source changed: ' + name)

    def read(self, root, name, limit, *, missing=False):
        path = Path(root).absolute()/name
        # Method validation also reads frozen implementation inputs outside
        # this catalog. Keep their independent safe reader and fresh checks;
        # they are not cached or treated as selected catalog dependencies.
        if not path.is_relative_to(self.root):
            return io._read(root, name, limit, missing=missing)
        name = path.relative_to(self.root).as_posix()
        if name not in self.data:
            before = self.identity(name)
            raw = io._read(self.root, name, limit, missing=missing)
            require(self.identity(name) == before, 'Retirement source changed while reading: ' + name)
            self.bytes += len(raw or b'')
            require(self.bytes <= 512*1024*1024, 'Retirement selected inputs exceed 512 MiB')
            self.data[name], self.identities[name] = raw, before
        else: self.guard(name)
        raw = self.data[name]
        require(raw is not None or missing, 'Missing catalog file: ' + name)
        require(raw is None or len(raw) <= limit, 'Retirement input exceeds reader limit: ' + name)
        return raw

    def checksum(self, raw):
        if raw is None: return None
        key = id(raw)
        if key not in self.hashes: self.hashes[key] = (raw, io._checksum(raw))
        return self.hashes[key][1]

    def forget(self, name):
        self.data.pop(name, None); self.identities.pop(name, None)

    def pending(self):
        require(not publication.staging(self.root), 'Interrupted publication: recovery required')
        raw = io.read(self.root, tx.LOCK, 24*1024*1024, missing=True)
        require(raw == self.lock, 'Interrupted publication: recovery required')

    def acquire(self, ids, commit):
        self.recheck()
        raw = canonical_bytes({'format':'picross-retirement-lock-v1','ids':list(ids),'integrated_commit':commit})+b'\n'
        target = io.safe(self.root, tx.LOCK)
        fd = os.open(target, os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0), 0o644)
        with os.fdopen(fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        self.lock = raw
        self.forget(tx.LOCK)
        self.recheck()

    def release(self):
        require(self.lock is not None, 'Retirement does not own a lock')
        self.recheck()
        io.safe(self.root, tx.LOCK).unlink()
        self.forget(tx.LOCK)
        self.lock = None

    def recheck(self):
        self.pending()
        for name in self.data: self.guard(name)


@contextmanager
def operation(root):
    require(io._retirement_reads.get() is None, 'Nested retirement is unsupported')
    reads = Reads(root)
    token = io._retirement_reads.set(reads)
    try: yield reads
    finally: io._retirement_reads.reset(token)


def capture(root, ids):
    from .current_registration import Snapshot
    snapshots=[Snapshot(root,identifier) for identifier in ids]
    texts={}
    for snapshot in snapshots:
        require(snapshot.delivery is not None,"Unknown selected delivery")
        texts.update(snapshot.raw)
    return {"registry":snapshots[0].registry,"texts":texts,"retained":{},"namespaces":{}}
