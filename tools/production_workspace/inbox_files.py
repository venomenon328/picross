"""Read untrusted synchronized files and retire only their verified Windows handles."""
from contextlib import contextmanager
import hashlib
import os
import stat

from tools.puzzle_production import catalog_io as io
from tools.puzzle_production.authoring_package import require


class Waiting(Exception):
    """The sync provider has not made the complete bytes readable yet."""


def destination(binding, child):
    from pathlib import Path
    root = io.external(Path(binding['directory']))
    folder = io.safe(root, child) if child else root
    if not folder.exists():
        raise Waiting('Wartet auf den synchronisierten Rätselordner.' if child else 'Wartet auf den synchronisierten Eingang.')
    require(folder.is_dir(), 'Das gebundene Ziel ist kein Verzeichnis.')
    return folder


def identity(info):
    return [str(info.st_dev), str(info.st_ino), info.st_size, str(info.st_mtime_ns)]


def entries(root):
    with os.scandir(root) as listing:
        for count, entry in enumerate(listing):
            require(count < 1024, 'Zu viele Einträge im privaten Eingangsordner.')
            yield entry


def source_path(root, name):
    from tools.puzzle_production.authoring_package import relative
    relative(name)
    require('/' not in name, 'Einfacher Quelldateiname erforderlich.')
    directory = io.external(root)
    path = directory / name
    if os.name == 'nt' and path.exists():
        matches = [entry.name for entry in entries(directory) if entry.name.casefold() == name.casefold()]
        require(matches == [name], 'Quellname ist ein Windows-Alias.')
    return path


def read(root, name, limit, expected=None):
    path = source_path(root, name)
    try:
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and not getattr(before, 'st_file_attributes', 0) & 1024 and before.st_size <= limit,
                'Dateityp oder Größe außerhalb der Lieferbindung.')
        if os.name == 'nt':
            with locked_windows_file(path, deleting=False) as (stream, _):
                if identity(os.fstat(stream.fileno())) != identity(before):
                    raise Waiting
                raw = stream.read(limit + 1)
        else:
            raw = io.read(root, name, limit)
        after = path.lstat()
        if identity(before) != identity(after) or len(raw) != before.st_size or expected and len(raw) < expected['bytes']:
            raise Waiting
        observed = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'identity': identity(after)}
        if expected:
            require(all(observed[k] == expected[k] for k in ('bytes', 'sha256')), 'Vollständige Datei weicht von der Lieferbindung ab.')
        return raw, observed
    except OSError as exc:
        raise Waiting from exc


@contextmanager
def locked_windows_file(path, *, deleting=True):
    import ctypes
    from ctypes import wintypes as w
    import msvcrt

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE]
    create.restype = w.HANDLE
    # Neither a competing writer nor a rename/delete can be admitted between
    # byte comparison and disposition. Never follow a final reparse point.
    access = 0x80000000 | (0x10000 if deleting else 0)
    handle = create(str(path), access, 1, None, 3, 0x00200000, None)
    if handle == w.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(w.HANDLE(handle))
        raise
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_ino and not info.st_file_attributes & 1024,
                'Reguläres identifizierbares Windows-Original erforderlich.')
        if info.st_nlink != 1:
            # DriveFS reports zero links on its FAT32-compatible streaming volume.
            # Accept that representation only when the opened volume lacks hardlinks.
            flags = w.DWORD()
            get_volume = kernel.GetVolumeInformationByHandleW
            get_volume.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, w.LPDWORD, w.LPDWORD, w.LPDWORD, w.LPWSTR, w.DWORD]
            require(info.st_nlink == 0 and get_volume(handle, None, 0, None, None, ctypes.byref(flags), None, 0)
                    and not flags.value & 0x00400000, 'Hardlinkfreiheit des Originals nicht bestätigt.')
        def remove():
            dispose = kernel.SetFileInformationByHandle
            dispose.argtypes = [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD]
            flag = ctypes.c_ubyte(1)
            if not dispose(handle, 4, ctypes.byref(flag), ctypes.sizeof(flag)):
                raise ctypes.WinError(ctypes.get_last_error())
        yield stream, remove


def retire(root, name, expected):
    path = source_path(root, name)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    require(stat.S_ISREG(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
            'Eingangsdatei wurde ersetzt. Sie bleibt erhalten.')
    require(os.name == 'nt', 'Bereinigung benötigt Windows-Dateibindung.')
    with locked_windows_file(path) as (stream, remove):
        info = os.fstat(stream.fileno())
        require(identity(info) == expected['identity'] and
                not getattr(info, 'st_file_attributes', 0) & 1024 and stat.S_ISREG(info.st_mode),
                'Eingangsdatei wurde ersetzt. Sie bleibt erhalten.')
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        require(digest == expected['sha256'] and identity(path.lstat()) == expected['identity'],
                'Eingangsdatei wurde verändert. Sie bleibt erhalten.')
        remove()
