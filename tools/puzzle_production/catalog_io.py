"""Bounded catalog I/O. Paths and open file identities are checked on every read."""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import stat
import time
import ctypes

from .authoring_package import relative, require
from .contract import Aborted, canonical_bytes
from . import operation_diagnostics as diagnostic

CHUNK = 1024 * 1024
_deadline = ContextVar("catalog_deadline", default=None)
_operation_data = ContextVar("catalog_operation_data", default=None)
if os.name == "nt":
    from ctypes import wintypes as _w
    _kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    _long_path = _kernel.GetLongPathNameW
    _long_path.argtypes = [_w.LPCWSTR, _w.LPWSTR, _w.DWORD]
    _attributes = _kernel.GetFileAttributesW
    _attributes.argtypes = [_w.LPCWSTR]
    _attributes.restype = _w.DWORD


@contextmanager
def budget(seconds=300):
    require(type(seconds) in (int, float) and 1 <= seconds <= 300, "Invalid catalog time budget")
    prior = _deadline.get()
    completed = diagnostic.completion.get()
    token = _deadline.set(min(prior, time.monotonic() + seconds) if prior else time.monotonic() + seconds)
    data_token = _operation_data.set({"json": {}, "json_bytes": 0}) if _operation_data.get() is None else None
    try:
        tick()
        yield
        if diagnostic.completion.get() == completed:
            tick()
    finally:
        _deadline.reset(token)
        if data_token is not None:
            _operation_data.reset(data_token)


def bounded(function):
    """Give a complete catalog API call one scope, including nested checks."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        with budget():
            return function(*args, **kwargs)
    return wrapped


def tick():
    operation = diagnostic.frame.get()
    if operation is not None:
        if operation.complete:
            return
        operation.tick()
    elif diagnostic.current.get() is not None:
        diagnostic.current.get().emit()
    if _deadline.get() is not None and time.monotonic() >= _deadline.get():
        raise Aborted("resource_limit: catalog time budget exhausted")


def safe(root, name):
    diagnostic.count("path_checks")
    # Reuse immutable Path syntax, never a filesystem observation or validation.
    root = (root if isinstance(root, Path) else Path(root)).absolute()
    require(not str(root).startswith(('\\\\', '//')), 'Network/device catalog paths are unsupported')
    relative(name)
    current = root.anchor
    last_existing = current
    parts = (*root.parts[1:], *name.split("/"))
    for index, part in enumerate(parts):
        tick()
        diagnostic.count("path_components")
        target = current + ('' if current.endswith(os.sep) else os.sep) + part
        if os.name != "nt":
            # Only names are needed. Path.iterdir constructs a Path for every
            # sibling at every guard/read, even though none is opened here.
            # Enumerate the same directory afresh; no path/identity result cache.
            # Listing also checks presence; a preliminary exists/stat adds no
            # identity check. Every component is still freshly lstat'ed below.
            try:
                names = os.listdir(current)
            except (FileNotFoundError, NotADirectoryError):
                pass
            else:
                folded = part.casefold()
                matches = [name for name in names if name.casefold() == folded]
                require(not matches or matches == [part], "Catalog path case collision: " + target)
        current = target
        if os.name == "nt":
            # Freshly inspect every ancestor, including its reparse attribute.
            # Directory identity/inode is not part of this predicate: lstat
            # opens a handle just to obtain fields that we never consume here.
            # Files still receive the complete lstat/hardlink checks below.
            diagnostic.count("windows_attribute_checks")
            attributes = _attributes(current)
            if attributes == 0xffffffff:
                error = ctypes.get_last_error()
                if error in (2, 3):  # Same missing-component policy as lstat.
                    continue
                raise ctypes.WinError(error)
            require(not attributes & 1024, "Unsafe catalog link/reparse path: " + current)
            if attributes & 16:
                last_existing = current
                continue
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 1024),
                "Unsafe catalog link/reparse path: " + str(current))
        last_existing = current
        require(stat.S_ISDIR(info.st_mode) or index == len(parts) - 1 and stat.S_ISREG(info.st_mode),
                "Unsafe catalog file type: " + str(current))
        if stat.S_ISREG(info.st_mode):
            require(info.st_nlink == 1, "Catalog hardlink is unsupported: " + str(current))
    if os.name == "nt":
        # One query returns the actual spelling of every existing component.
        output = ctypes.create_unicode_buffer(32768)
        length = _long_path(str(last_existing), output, len(output))
        require(0 < length < len(output) and output.value[2:] == str(last_existing)[2:], "Catalog path case collision: " + str(last_existing))
    checked = Path(current)
    require(checked.is_relative_to(root), "Catalog path escapes root")
    return checked


def external(path):
    path = Path(path).absolute()
    return safe(Path(path.anchor), path.relative_to(path.anchor).as_posix())


def signature(info):
    # Windows Python 3.13 stat/fstat can expose creation/change time differently.
    # Compare ctime only within each API, while identity/size/mtime cross-check
    # the pathname and opened handle.
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_nlink


def read(root, name, limit, *, missing=False):
    diagnostic.count("safe_reads")
    path = safe(root, name)
    try:
        before = path.lstat()
    except FileNotFoundError:
        require(missing, "Missing catalog file: " + name)
        return None
    require(stat.S_ISREG(before.st_mode), "Catalog source is not regular: " + name)
    if before.st_size > limit:
        raise Aborted("resource_limit: catalog file exceeds byte limit: " + name)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        require(signature(before) == signature(opened), "Catalog source changed while opening: " + name)
        chunks, size = [], 0
        while True:
            tick()
            block = stream.read(min(CHUNK, limit + 1 - size))
            if not block:
                break
            size += len(block)
            diagnostic.count("bytes_read", len(block), work="read: " + name)
            if size > limit:
                raise Aborted("resource_limit: catalog file exceeds byte limit: " + name)
            chunks.append(block)
        after_handle = os.fstat(stream.fileno())
        require(signature(opened) == signature(after_handle) and opened.st_ctime_ns == after_handle.st_ctime_ns,
                "Catalog source changed while reading: " + name)
    after = safe(root, name).lstat()
    require(signature(before) == signature(after) and before.st_ctime_ns == after.st_ctime_ns, "Catalog source changed after reading: " + name)
    return b"".join(chunks)


def checksum(raw):
    if raw is not None:
        diagnostic.count("bytes_hashed", len(raw))
        diagnostic.count("hash_calls")
    return hashlib.sha256(raw).hexdigest() if raw is not None else None


def file_hash(root, name, limit=64 * 1024 * 1024):
    return checksum(read(root, name, limit))


def export_limit(root, name):
    """The sole large-file exception is a declared v6 original ZIP.

    This is a bounded read policy, not export verification. The full consumer
    still checks the manifest, every file and the original production proofs.
    No basename, caller-supplied flag or arbitrary ZIP earns the exception.
    """
    from .authoring_package import MAX_FILE, MAX_ZIP, sha
    from .contract import exact_keys, integer
    if name != "input/package.zip":
        return MAX_FILE
    raw = read(root, "manifest.json", 8 * 1024 * 1024, missing=True)
    if raw is None:
        return MAX_FILE
    manifest = json_bytes(raw, 8 * 1024 * 1024)
    if not isinstance(manifest, dict) or manifest.get("format") != "picross-target-export-v6":
        return MAX_FILE
    inputs = exact_keys(manifest.get("input"), {"original_package", "external_root", "discarded_files"})
    original = exact_keys(inputs["original_package"], {"file", "sha256", "bytes"})
    require(original["file"] == name and inputs["external_root"] == "external" and
            isinstance(manifest.get("files"), dict) and manifest["files"].get(name) == sha(original["sha256"]),
            "Original ZIP exception requires its exact v6 manifest binding")
    integer(original["bytes"], 1, MAX_ZIP, "original ZIP byte count")
    return MAX_ZIP


def json_bytes(raw, limit):
    require(isinstance(raw, bytes), "Catalog JSON must be bytes")
    if len(raw) > limit:
        raise Aborted("resource_limit: catalog JSON exceeds byte limit")
    tick()
    data = _operation_data.get()
    if data is not None and raw in data["json"]:
        diagnostic.count("json_reuses")
        # Only pure parsing of these exact bytes is reused. Each caller owns
        # its object; no mutation can contaminate another reader or operation.
        return deepcopy(data["json"][raw])
    text = raw.decode("utf-8")
    require(not text.startswith("\ufeff"), "Catalog JSON BOM is unsupported")
    # Bound nesting before json.loads allocates containers. Braces in strings do
    # not count, including escaped quotes and backslashes.
    depth, quoted, escaped = 0, False, False
    for i, char in enumerate(text):
        if i % CHUNK == 0:
            tick()
        if quoted:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == '"': quoted = False
        elif char == '"': quoted = True
        elif char in "[{":
            depth += 1
            require(depth <= 32, "Catalog JSON depth exceeds 32")
        elif char in "]}": depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate catalog JSON key: " + key)
            result[key] = value
        return result

    def number(token, convert):
        require(len(token) <= 16, "Catalog JSON numeric token exceeds 16 characters")
        return convert(token)

    def constant(token):
        raise ValueError("Nonfinite catalog JSON: " + token)

    value = json.loads(text, object_pairs_hook=pairs, parse_int=lambda t: number(t, int),
                       parse_float=lambda t: number(t, float), parse_constant=constant)
    canonical_bytes(value)  # Reject nonfinite floats and unpaired Unicode surrogates.
    if data is not None and len(raw) <= 1024*1024 and data["json_bytes"] + len(raw) <= 16*1024*1024:
        data["json"][raw] = deepcopy(value)
        data["json_bytes"] += len(raw)
    return value
