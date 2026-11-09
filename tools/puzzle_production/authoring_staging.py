"""Private HP-I1a stages: exclusive writes and ownership-checked cleanup."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import uuid

from . import authoring_package as ap, catalog_io as io
from .contract import Aborted, InvalidInput, canonical_bytes


class StageError(OSError):
    """A retained private stage is an error, even after a completed publication."""

    def __init__(self, message, remaining, status="technical_error"):
        super().__init__(message + ("; remaining: " + remaining if remaining is not None else ""))
        self.remaining = remaining
        self.status = status


class _ForeignStage(InvalidInput):
    pass


def _identity(info):
    return info.st_dev, info.st_ino


def _observation(info):
    return io.signature(info), info.st_ctime_ns


class OwnedStage:
    """Keep live ownership of exact paths, including partially written own bytes.

    A caller may atomically move a complete owned subtree out of this directory.
    Missing owned files then require no deletion. Unknown paths, changed bytes or
    replaced inodes are preserved; cleanup never adopts or recursively erases
    them. The marker is operational and is never moved into a published subtree.
    """

    def __init__(self, parent, prefix, owner):
        self.marker = canonical_bytes({"owner": owner, "pid": os.getpid(), "token": uuid.uuid4().hex}) + b"\n"
        parent = io.external(parent) if parent is not None else None
        self.root = Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
        self.directories = {"": _identity(self.root.lstat())}
        self.files = {}

    def __enter__(self):
        try:
            self._write("owner.json", self.marker)
        except (Exception, KeyboardInterrupt) as exc:
            self.__exit__(type(exc), exc, exc.__traceback__)
            raise
        return self

    @staticmethod
    def _parts(relative):
        # Internal prefixes are added to already bounded public paths. Validate
        # their components without making a valid 240-byte input fail because
        # its private stage is named external/<input> or export/<input>.
        ap.string(relative, "stage relative path", 512)
        parts = relative.split("/")
        for part in parts:
            ap.relative(part)
        return parts

    def _root_guard(self):
        if _identity(io.external(self.root).lstat()) != self.directories[""]:
            raise _ForeignStage("Private stage root was replaced")

    def _path(self, relative):
        self._root_guard()
        path, parts = self.root, self._parts(relative)
        for index, part in enumerate(parts):
            path = io.safe(path, part)
            key = "/".join(parts[:index + 1])
            if key in self.directories and path.exists():
                if _identity(path.lstat()) != self.directories[key]:
                    raise _ForeignStage("Private stage directory was replaced: " + key)
        return path

    def mkdir(self, relative):
        parts = self._parts(relative)
        for index in range(1, len(parts) + 1):
            key = "/".join(parts[:index])
            path = self._path(key)
            if key not in self.directories:
                path.mkdir()
                self.directories[key] = _identity(path.lstat())
            elif not path.is_dir():
                raise _ForeignStage("Missing owned stage directory: " + key)
        return path

    def _write(self, relative, raw):
        ap.require(isinstance(raw, bytes), "Stage payload must be bytes")
        parts = self._parts(relative)
        if len(parts) > 1:
            self.mkdir("/".join(parts[:-1]))
        path = self._path(relative)
        with path.open("xb") as stream:
            # Track only after exclusive creation: a foreign existing file is
            # never mistaken for an interrupted own write, even if identical.
            identity = _identity(os.fstat(stream.fileno()))
            self.files[relative] = raw, identity, False
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.files[relative] = raw, identity, True
        return path

    def write(self, relative, raw):
        ap.require(relative != "owner.json", "Private ownership marker is reserved")
        return self._write(relative, raw)

    def _checked(self, relative, *, partial=False):
        path = self._path(relative)
        if relative not in self.files:
            raise _ForeignStage("Unknown private stage file: " + relative)
        expected, identity, completed = self.files[relative]
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or _identity(before) != identity or
                before.st_size > len(expected)):
            raise _ForeignStage("Private stage file was replaced or changed: " + relative)
        actual = io.read(path.parent, path.name, len(expected))
        after = path.lstat()
        if _observation(before) != _observation(after):
            raise _ForeignStage("Private stage file changed during cleanup check: " + relative)
        if (not expected.startswith(actual) if partial and not completed else expected != actual):
            raise _ForeignStage("Private stage file bytes changed: " + relative)
        return path, _observation(after)

    def replace(self, relative, raw):
        ap.require(relative != "owner.json" and isinstance(raw, bytes), "Invalid private stage replacement")
        path, observed = self._checked(relative)
        with path.open("r+b") as stream:
            if io.signature(os.fstat(stream.fileno())) != observed[0]:
                raise _ForeignStage("Private stage replacement source changed: " + relative)
            identity = _identity(os.fstat(stream.fileno()))
            self.files[relative] = raw, identity, False
            stream.truncate(0)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.files[relative] = raw, identity, True
        self._checked(relative)
        return path

    def _cleanup(self):
        if not os.path.lexists(self.root):
            return
        self._root_guard()
        files, directories = [], []
        for parent, dirs, leaves in os.walk(self.root, followlinks=False):
            for name in dirs + leaves:
                relative = (Path(parent) / name).relative_to(self.root).as_posix()
                path = self._path(relative)
                info = path.lstat()
                if stat.S_ISDIR(info.st_mode):
                    if self.directories.get(relative) != _identity(info):
                        raise _ForeignStage("Unknown private stage directory: " + relative)
                    directories.append(relative)
                else:
                    _, observed = self._checked(relative, partial=True)
                    files.append((relative, observed))
        # Check the complete tree before deleting any byte. Recheck each open
        # identity immediately before removal; a new foreign entry prevents the
        # final rmdir and is left at the explicitly reported remaining path.
        for relative, observed in files:
            path = self._path(relative)
            if _observation(path.lstat()) != observed:
                raise _ForeignStage("Private stage file changed before cleanup: " + relative)
            path.unlink()
        for relative in sorted(directories, key=lambda value: value.count("/"), reverse=True):
            self._path(relative).rmdir()
        self._root_guard()
        self.root.rmdir()

    def __exit__(self, kind, error, traceback):
        try:
            self._cleanup()
        except (Exception, KeyboardInterrupt) as cleanup_error:
            remaining = str(self.root.absolute()) if os.path.lexists(self.root) else None
            aborted = isinstance(error, (Aborted, KeyboardInterrupt, MemoryError)) or isinstance(
                cleanup_error, (Aborted, KeyboardInterrupt, MemoryError))
            status = ("aborted" if aborted else "conflict" if isinstance(cleanup_error,
                      (_ForeignStage, InvalidInput)) else "technical_error")
            detail = ("; original operation: " + str(error)) if error is not None else ""
            raise StageError("Private stage retained: " + str(cleanup_error) + detail,
                             remaining, status) from cleanup_error
        return False
