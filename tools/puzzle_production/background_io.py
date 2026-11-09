"""HP-W2 bounded reads and cooperative, non-replacing directory publication.

No package discovery, ZIP reader, catalog mutation or automatic recovery lives
here. Every input is named by the caller and checked again before publication.
"""
from __future__ import annotations

from contextlib import contextmanager
import ctypes
import errno
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time
import uuid

from . import catalog_io
from .contract import InvalidInput
from .background_contract import (BackgroundError, MAX_BYTES, MAX_FILES,
                                  canonical, relative)

SECONDS = 300
CHUNK = 1024 * 1024


class Budget:
    """One cumulative cooperative deadline, including repeated verification."""

    def __init__(self):
        self.deadline = time.monotonic() + SECONDS

    def check(self):
        if time.monotonic() >= self.deadline:
            raise BackgroundError("deadline_exceeded", "Background operation exceeded 300 seconds")


def safe(root, name):
    relative(name)
    try:
        return catalog_io.safe(root, name)
    except InvalidInput as exc:
        raise BackgroundError("unsafe_path", str(exc), name) from exc


def external(path):
    try:
        return catalog_io.external(path)
    except (InvalidInput, TypeError, ValueError) as exc:
        raise BackgroundError("unsafe_path", "Unsafe explicit filesystem path") from exc


def identity(info):
    return catalog_io.signature(info)


def _active_tree(path):
    # Reject both descendants and the enclosing roots of a known active tree.
    # This inspects markers only, never walks or loads a production catalog.
    for parent in (path, *path.parents):
        if (parent / "project.godot").exists():
            return True
        if (parent / "registry.json").exists() and parent.name == "content":
            return True
    return ((path / "game" / "project.godot").exists() or
            (path / "content" / "registry.json").exists())


def roots(source, output):
    source, output = external(source), external(output)
    for path in (source, output):
        if not path.is_dir():
            raise BackgroundError("missing_file", "Explicit root must be an existing directory")
        if _active_tree(path):
            raise BackgroundError("unsafe_path", "Background roots must be outside active game/catalog trees")
    if source.is_relative_to(output) or output.is_relative_to(source):
        raise BackgroundError("unsafe_path", "Source and output roots must not overlap")
    return source, output


class Reader:
    """Read named regular files, accounting the actual selected reference graph.

    Only identities and hashes are retained. A repeated read or recheck opens
    the file afresh; successful validation is never a file-content cache.
    """

    def __init__(self, root, budget=None):
        self.root = external(root)
        self.budget = budget if budget is not None else Budget()
        self.root_id = identity(self.root.lstat())[:2]
        self.seen = {}
        self.total = 0

    def _root_check(self):
        self.budget.check()
        try:
            current = identity(external(self.root).lstat())[:2]
        except (FileNotFoundError, BackgroundError) as exc:
            raise BackgroundError("source_changed", "Previously checked source root disappeared or became unsafe") from exc
        if current != self.root_id:
            raise BackgroundError("source_changed", "Source root identity changed")

    def read(self, name, limit):
        self._root_check()
        previous = self.seen.get(name)
        try:
            path = safe(self.root, name)
        except BackgroundError as exc:
            if previous:
                raise BackgroundError("source_changed", "Previously checked source path became unsafe", name) from exc
            raise
        try:
            before = path.lstat()
        except FileNotFoundError as exc:
            code = "source_changed" if previous else "missing_file"
            raise BackgroundError(code, "Declared file is missing", name) from exc
        if not stat.S_ISREG(before.st_mode):
            raise BackgroundError("unsafe_path", "Declared input is not a regular file", name)
        if before.st_size > limit:
            code = "source_changed" if previous else "resource_limit"
            raise BackgroundError(code, "File exceeds its encoded byte limit", name)
        if previous is None:
            if len(self.seen) >= MAX_FILES or self.total + before.st_size > MAX_BYTES:
                raise BackgroundError("resource_limit", "Selected reference graph exceeds 256 files / 96 MiB", name)
        elif identity(before) != previous[0] or before.st_ctime_ns != previous[1]:
            raise BackgroundError("source_changed", "Previously checked source identity changed", name)
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(path, flags)
        except FileNotFoundError as exc:
            raise BackgroundError("source_changed", "Source disappeared while opening", name) from exc
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if identity(opened) != identity(before):
                raise BackgroundError("source_changed", "Source changed while opening", name)
            chunks, size = [], 0
            while True:
                self.budget.check()
                block = stream.read(min(CHUNK, limit + 1 - size))
                if not block:
                    break
                size += len(block)
                if size > limit or (previous is None and self.total + size > MAX_BYTES):
                    raise BackgroundError("resource_limit", "Actual read exceeds the byte budget", name)
                chunks.append(block)
            final_handle = os.fstat(stream.fileno())
            if identity(opened) != identity(final_handle) or opened.st_ctime_ns != final_handle.st_ctime_ns:
                raise BackgroundError("source_changed", "Source changed during reading", name)
        try:
            after = safe(self.root, name).lstat()
        except (FileNotFoundError, BackgroundError) as exc:
            raise BackgroundError("source_changed", "Source path changed during reading", name) from exc
        if identity(before) != identity(after) or before.st_ctime_ns != after.st_ctime_ns or size != before.st_size:
            raise BackgroundError("source_changed", "Source changed after reading", name)
        raw = b"".join(chunks)
        if name.casefold().endswith(".zip") or raw[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
            raise BackgroundError("unsafe_path", "Embedded ZIP inputs are unsupported", name)
        sha = hashlib.sha256(raw).hexdigest()
        self.budget.check()
        if previous is not None and (sha != previous[2] or size != previous[3]):
            raise BackgroundError("source_changed", "Previously checked source bytes changed", name)
        if previous is None:
            self.seen[name] = (identity(after), after.st_ctime_ns, sha, size, limit)
            self.total += size
        return raw

    def read_ref(self, ref, limit):
        name = ref["file"]
        previous = self.seen.get(name)
        if ref["bytes"] > limit:
            raise BackgroundError("resource_limit", "Declared file exceeds its byte limit", name)
        if previous and (ref["sha256"] != previous[2] or ref["bytes"] != previous[3]):
            raise BackgroundError("target_conflict", "Contradictory references occupy the same source path", name)
        raw = self.read(name, limit)
        if len(raw) != ref["bytes"] or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
            raise BackgroundError("invalid_binding", "Declared source hash or byte count does not match", name)
        return raw

    def recheck(self):
        self._root_check()
        for name, observed in tuple(self.seen.items()):
            self.read(name, observed[4])
        self.budget.check()


@contextmanager
def writer(root):
    """Stable, OS-held root lock. Never unlink a lock inode other writers use."""
    path = safe(root, ".background-writer.lock")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    locked = False
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or identity(path.lstat()) != identity(info):
            raise BackgroundError("unsafe_path", "Unsafe writer lock", path.name)
        try:
            if os.name == "nt":
                import msvcrt
                if info.st_size == 0:
                    os.write(fd, b"\0")
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except (BlockingIOError, PermissionError) as exc:
            raise BackgroundError("target_conflict", "Output root writer lock is held", path.name) from exc
        # Verify path still identifies the locked inode, rather than an unlinked
        # predecessor that would not protect subsequent cooperative writers.
        if identity(safe(root, path.name).lstat())[:2] != identity(os.fstat(fd))[:2]:
            raise BackgroundError("target_conflict", "Writer lock path changed", path.name)
        yield
    finally:
        if locked:
            if os.name == "nt":
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def write_file(path, raw):
    with Path(path).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def publish_directory(stage, target):
    """Atomic no-replace publication, including a non-cooperating target race."""
    try:
        if os.name == "nt":
            os.rename(stage, target)  # Windows refuses an existing destination.
        elif sys.platform.startswith("linux"):
            libc = ctypes.CDLL(None, use_errno=True)
            rename = getattr(libc, "renameat2", None)
            if rename is None:
                raise OSError(errno.ENOSYS, "Atomic no-replace directory publication unavailable")
            rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
            rename.restype = ctypes.c_int
            if rename(-100, os.fsencode(stage), -100, os.fsencode(target), 1) != 0:
                code = ctypes.get_errno()
                raise OSError(code, os.strerror(code))
        else:
            raise OSError(errno.ENOSYS, "Atomic no-replace directory publication unavailable")
    except OSError as exc:
        if exc.errno in (errno.EEXIST, errno.ENOTEMPTY):
            raise BackgroundError("target_conflict", "Output appeared before publication") from exc
        raise


class Stage:
    """Ownership marker stays outside the published two-file payload."""

    def __init__(self, root, request_sha256):
        self.root = Path(tempfile.mkdtemp(prefix=".hp-w2-stage-", dir=root))
        self.root_id = identity(self.root.lstat())[:2]
        self.marker = canonical({"owner": "picross-background-1", "token": uuid.uuid4().hex,
                                 "pid": os.getpid(), "request_sha256": request_sha256}) + b"\n"
        self.payload = self.root / "payload"
        self.files = {"owner.json": self.marker}

    def prepare(self):
        write_file(self.root / "owner.json", self.marker)
        self.payload.mkdir()

    def write(self, name, raw):
        relative(name)
        self.files["payload/" + name] = raw
        write_file(safe(self.payload, name), raw)

    def cleanup(self):
        if not self.root.exists():
            return None
        try:
            if identity(external(self.root).lstat())[:2] != self.root_id:
                return str(self.root.absolute())
            # This live object proves creation/identity. On failure a writer can
            # leave a prefix of its intended bytes. Unknown files, links or
            # different bytes are retained for explicit ownership review.
            for parent, directories, leaves in os.walk(self.root, followlinks=False):
                for name in directories + leaves:
                    path = Path(parent) / name
                    rel = path.relative_to(self.root).as_posix()
                    safe(self.root, rel)
                    if path.is_dir():
                        if rel != "payload":
                            return str(self.root.absolute())
                    else:
                        expected = self.files.get(rel)
                        if expected is None or path.stat().st_size > len(expected):
                            return str(self.root.absolute())
                        with path.open("rb") as stream:
                            actual = stream.read(len(expected) + 1)
                        if not expected.startswith(actual):
                            return str(self.root.absolute())
            shutil.rmtree(self.root)
        except (OSError, BackgroundError):
            return str(self.root.absolute())
        return None


def parents(root, target, created=None):
    """Create only missing output parents; callers can remove their empty dirs."""
    created = [] if created is None else created
    current = Path(root)
    for part in target.parent.relative_to(root).parts:
        current = safe(current, part)
        try:
            current.mkdir()
            created.append(current)
        except FileExistsError:
            if not current.is_dir():
                raise BackgroundError("target_conflict", "Output parent is occupied")
    return created
