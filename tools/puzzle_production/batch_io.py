"""BA-A bounded local I/O; no catalog writer or implicit source discovery."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

from . import authoring_package as ap, catalog_io as io
from .contract import Aborted, InvalidInput, canonical_bytes

MAX_FILE = ap.MAX_ZIP
MAX_TOTAL = ap.MAX_TOTAL
MAX_FILES = ap.MAX_FILES
MAX_JSON = 16 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise InvalidInput(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    info = io.external(path).lstat()
    return {"device": info.st_dev, "inode": info.st_ino}


def external(path, *, directory=True):
    checked = io.external(path)
    require(checked.is_dir() if directory else checked.is_file(),
            "Missing explicit " + ("directory: " if directory else "file: ") + str(checked))
    return checked


def read(path, limit=MAX_JSON):
    path = io.external(path)
    try:
        return io.read(path.parent, path.name, limit)
    except Aborted as exc:
        raise InvalidInput(str(exc)) from exc


def json_bytes(raw, limit=MAX_JSON):
    """Bounded JSON, preserving real finite timer floats from domain producers."""
    require(isinstance(raw, bytes) and len(raw) <= limit, "Batch JSON byte limit")
    text = raw.decode("utf-8")
    require(not text.startswith("\ufeff"), "Batch JSON BOM is unsupported")
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            require(depth <= 32, "Batch JSON depth exceeds 32")
        elif char in "]}":
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate batch JSON key: " + key)
            result[key] = value
        return result

    def number(token, convert):
        require(len(token) <= 128, "Batch numeric token exceeds 128 characters")
        return convert(token)

    def nonfinite(token):
        raise InvalidInput("Nonfinite batch number: " + token)

    value = json.loads(text, object_pairs_hook=pairs, parse_int=lambda s: number(s, int),
                       parse_float=lambda s: number(s, float), parse_constant=nonfinite)
    canonical_bytes(value)
    return value


def json_read(path, limit=MAX_JSON):
    return json_bytes(read(path, limit), limit)


def sync_directory(path):
    # Windows MoveFileEx below requests durable rename. POSIX also fsyncs parent.
    if os.name != "nt":
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _write_raw_new(path, raw):
    path = io.external(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def write_new(path, raw):
    """Publish complete immutable bytes atomically, without replacing a target."""
    path = io.external(path)
    require(not path.exists(), "Immutable batch file already exists: " + str(path))
    pending = io.safe(path.parent, ".batch-pending-" + uuid.uuid4().hex + ".json")
    _write_raw_new(pending, raw)
    publish_new(pending, path)


def publish_new(pending, path):
    pending, path = io.external(pending), io.external(path)
    require(not path.exists(), "Immutable batch destination already exists")
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        move = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
        move.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        move.restype = wintypes.BOOL
        if not move(str(pending), str(path), 0x8):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        from .background_io import publish_directory
        from .background_contract import BackgroundError
        try:
            publish_directory(pending, path)  # renameat2 NOREPLACE also handles regular files.
        except BackgroundError as exc:
            raise InvalidInput(str(exc)) from exc
    sync_directory(path.parent)


def write_json_new(path, value):
    write_new(path, canonical_bytes(value) + b"\n")


def replace_json(path, value, expected):
    """Replace only our observed bytes; an interrupted pending write stays inert."""
    path = io.external(path)
    raw = canonical_bytes(value) + b"\n"
    require(len(raw) <= MAX_JSON, "Batch JSON exceeds 16 MiB")
    before = read(path) if path.exists() else None
    require(before == expected, "Concurrent batch checkpoint/report change")
    pending = io.safe(path.parent, ".batch-pending-" + uuid.uuid4().hex + ".json")
    _write_raw_new(pending, raw)
    # Read again after staging. OS lock handles cooperative writers, this guard
    # detects changes from a noncooperating editor before publication.
    require((read(path) if path.exists() else None) == expected,
            "Concurrent batch change before publication")
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        move = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
        move.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        move.restype = wintypes.BOOL
        if not move(str(pending), str(path), 0x1 | 0x8):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        os.replace(pending, path)
    sync_directory(path.parent)
    require(read(path) == raw, "Batch publication readback mismatch")
    return raw


@contextmanager
def writer(root, *, name=".batch-writer.lock"):
    """Separate stable OS-held lock; never delete another subsystem's lock."""
    root = external(root)
    require(name in (".batch-writer.lock", ".batch-worker.lock"), "Unknown batch lock")
    path = io.safe(root, name)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600)
    locked = False
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                io.signature(info) == io.signature(path.lstat()), "Unsafe batch lock")
        try:
            if os.name == "nt":
                import msvcrt
                if not info.st_size:
                    os.write(fd, b"\0")
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except (BlockingIOError, PermissionError) as exc:
            raise InvalidInput("Batch writer lock is held") from exc
        require(identity(path) == {"device": info.st_dev, "inode": info.st_ino},
                "Batch lock inode changed")
        yield
    finally:
        if locked:
            if os.name == "nt":
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def roots(source, work, repo, history=None):
    source, repo = external(source), external(repo)
    work = io.external(work) if work is not None else None
    history = external(history) if history is not None else None
    if work is not None:
        for other in (source, repo, history):
            if other is None:
                continue
            a, b = str(work).casefold(), str(other).casefold()
            require(a != b and not a.startswith(b + os.sep) and not b.startswith(a + os.sep),
                    "Batch work root overlaps a read-only source/repository/history root")
        for ancestor in (work, *work.parents):
            require(not (ancestor / "project.godot").exists() and
                    not (ancestor.name == "content" and (ancestor / "registry.json").exists()),
                    "Batch output is inside an active game/catalog tree")
    return source, work, repo, history


def inventory(root):
    """Full fresh inventory, rejecting extra aliases, links and nonregular files."""
    root = external(root)
    result, spelling, total = [], {}, 0
    def fail(error):
        raise error

    for current, directories, files in os.walk(root, followlinks=False, onerror=fail):
        for name in sorted(directories + files):
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            checked = io.safe(root, relative)
            info = checked.lstat()
            key = relative.casefold()
            require(key not in spelling, "Batch inventory case alias")
            spelling[key] = relative
            require(len(spelling) <= MAX_FILES * 2, "Batch inventory namespace limit")
            if stat.S_ISDIR(info.st_mode):
                continue
            require(stat.S_ISREG(info.st_mode), "Batch inventory nonregular file")
            raw = read(checked, MAX_FILE)
            total += len(raw)
            require(total <= MAX_TOTAL and len(result) < MAX_FILES, "Batch inventory resource limit")
            result.append({"file": relative, "sha256": sha(raw), "bytes": len(raw)})
    return sorted(result, key=lambda item: item["file"])


def artifact(path, source, work):
    path = io.external(path)
    matches = [(name, root) for name, root in (("source", source), ("work", work))
               if root is not None and path.is_relative_to(root)]
    require(len(matches) == 1, "Output slot escapes explicit source/work roots")
    scope, root = matches[0]
    relative = path.relative_to(root).as_posix()
    if path.is_dir():
        return {"kind": "directory", "root": scope, "file": "" if relative == "." else relative,
                "files": inventory(path)}
    raw = read(path, MAX_FILE)
    return {"kind": "file", "root": scope, "file": relative, "sha256": sha(raw), "bytes": len(raw)}


def artifact_path(ref, source, work, *, check=True):
    root = {"source": source, "work": work}[ref["root"]]
    require(root is not None, "Missing artifact root")
    path = root if ref["kind"] == "directory" and ref["file"] == "" else io.safe(root, ref["file"])
    if check:
        require(artifact(path, source, work) == ref, "Artifact missing/changed/extra bytes: " + ref["file"])
    return path
