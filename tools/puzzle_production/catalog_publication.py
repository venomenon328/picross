"""Durable filesystem primitives shared by the current operation writers."""
NORMAL_LIMIT = 128 * 1024 * 1024
LIMIT = NORMAL_LIMIT
EDITOR_PREFIX = b"PICROSS-EDITOR-CHANGE-JOURNAL-V2\n"
PREFIXES = ()
import base64

from copy import deepcopy

import ctypes

import io as streams

import os

from pathlib import Path

import re

import tempfile

from contextlib import contextmanager

from types import SimpleNamespace

from .authoring_package import require, sha

from .contract import canonical_bytes, exact_keys, integer, Aborted, InvalidInput

from . import catalog_io as io, reveal_source as reveal

from . import operation_diagnostics as diagnostic

def staging(root):
    directory = io.safe(root, "content")
    return sorted(p.relative_to(root).as_posix() for p in directory.iterdir()
                  if (p.name.startswith(".registration-journal-") and p.name.endswith(".tmp"))
                  or p.name == ".editor-change-journal.tmp")

def read_journal(root, name="content/.registration-pending.json"):
    p = io.safe(root, name)
    if not p.exists(): return None
    require(p.is_file(), "Journal must be a regular file")
    size = p.stat().st_size
    if size > LIMIT: raise Aborted("resource_limit: journal exceeds 128 MiB")
    with p.open("rb") as stream: prefix = stream.read(4096)
    binary = prefix.startswith(PREFIXES) or prefix.startswith(EDITOR_PREFIX)
    require(size <= NORMAL_LIMIT or binary, "Only declared binary journals may exceed 24 MiB")
    raw = io.read(root, name, LIMIT if binary else NORMAL_LIMIT)
    active = diagnostic.frame.get()
    if active is not None and hasattr(active, "journal_raw"):
        require(raw == active.journal_raw, "Journal changed after recovery classification")
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
        require(start + io.CHUNK >= len(value["base64"]) or "=" not in encoded,
                "Noncanonical intermediate Base64 padding")
        raw = base64.b64decode(encoded, validate=True)
        require(base64.b64encode(raw).decode("ascii") == encoded, "Noncanonical Base64")
        yield raw

def decode_binary(value):
    raw = b"".join(binary_chunks(value))
    require(len(raw) == value["bytes"] and io.checksum(raw) == value["sha256"], "Binary journal hash/size differs")
    return raw

def _validate_background_image(path):
    """Check an actual HP-W2 output, independently of its declared metadata."""
    from PIL import Image, ImageFile
    from . import background_assets as assets
    from .background_contract import BackgroundError, MAX_PNG
    raw = io.read(path.parent, path.name, MAX_PNG)
    try:
        assets._png(raw, SimpleNamespace(check=io.tick))
        require(not ImageFile.LOAD_TRUNCATED_IMAGES, "Strict PNG decoding was disabled")
        with Image.open(streams.BytesIO(raw), formats=("PNG",)) as image:
            image.verify()
        with Image.open(streams.BytesIO(raw), formats=("PNG",)) as image:
            require(image.mode == "RGBA" and image.size in ((2304, 576), (2304, 768)) and image.info == {"srgb": 0},
                    "Background binary does not match the fixed PNG profile")
            image.load()
            assets._diagnostic(image)
            pixels = image.tobytes()
            for offset in range(0, len(pixels), 4 * 65536):
                io.tick()
                block = pixels[offset:offset + 4 * 65536]
                require(all(block[i + 3] or block[i:i + 3] == b"\0\0\0" for i in range(0, len(block), 4)),
                        "Background transparent RGB is not zero")
    except (BackgroundError, OSError, ValueError, SyntaxError) as exc:
        raise InvalidInput("Invalid background journal image: " + str(exc)) from exc

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

def journal_bytes(value):
    import zlib
    require(value["format"] == "picross-editor-change-journal-v2", "Use the current operation writer")
    raw = canonical_bytes(value) + b"\n"
    require(len(raw) <= LIMIT, "Editor journal exceeds 128 MiB")
    return EDITOR_PREFIX + zlib.compress(raw, level=6)
