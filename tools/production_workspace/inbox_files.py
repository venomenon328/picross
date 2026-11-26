"""Read untrusted synchronized files and retire only their verified Windows handles."""
from contextlib import contextmanager
import hashlib
import os
import stat

from tools.puzzle_production import catalog_io as io
from tools.puzzle_production.authoring_package import require


class Waiting(Exception):
    """The sync provider has not made the complete bytes readable yet."""


def identity(info):
    return [str(info.st_dev), str(info.st_ino), info.st_size, str(info.st_mtime_ns)]


def read(root, name, limit, expected=None):
    path = io.safe(root, name)
    try:
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit,
                'Dateityp oder Größe außerhalb der Lieferbindung.')
        raw = io.read(root, name, limit)
        after = path.lstat()
        if identity(before) != identity(after) or expected and len(raw) < expected['bytes']:
            raise Waiting
        observed = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'identity': identity(after)}
        if expected:
            require(all(observed[k] == expected[k] for k in ('bytes', 'sha256')), 'Vollständige Datei weicht von der Lieferbindung ab.')
        return raw, observed
    except OSError as exc:
        raise Waiting from exc


@contextmanager
def locked_windows_file(path):
    import ctypes
    from ctypes import wintypes as w
    import msvcrt

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE]
    create.restype = w.HANDLE
    # Neither a competing writer nor a rename/delete can be admitted between
    # byte comparison and disposition. Never follow a final reparse point.
    handle = create(str(path), 0x80000000 | 0x10000, 1, None, 3, 0x00200000, None)
    if handle == w.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(w.HANDLE(handle))
        raise
    with os.fdopen(fd, 'rb') as stream:
        def remove():
            dispose = kernel.SetFileInformationByHandle
            dispose.argtypes = [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD]
            flag = ctypes.c_ubyte(1)
            if not dispose(handle, 4, ctypes.byref(flag), ctypes.sizeof(flag)):
                raise ctypes.WinError(ctypes.get_last_error())
        yield stream, remove


def retire(root, name, expected):
    path = io.safe(root, name)
    if not path.exists():
        return
    require(os.name == 'nt', 'Bereinigung benötigt Windows-Dateibindung.')
    with locked_windows_file(path) as (stream, remove):
        info = os.fstat(stream.fileno())
        require(identity(info) == expected['identity'] and info.st_nlink == 1 and
                not getattr(info, 'st_file_attributes', 0) & 1024 and stat.S_ISREG(info.st_mode),
                'Eingangsdatei wurde ersetzt. Sie bleibt erhalten.')
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        require(digest == expected['sha256'] and identity(path.lstat()) == expected['identity'],
                'Eingangsdatei wurde verändert. Sie bleibt erhalten.')
        remove()
