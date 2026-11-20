"""Open only the bound Godot player and hold its protected files to real exit."""
from contextlib import contextmanager, ExitStack
import ctypes
from ctypes import wintypes as w
import hashlib
import os
from pathlib import Path
import subprocess
import time

from tools.production_workspace.processes import external_environment, system_dlls
from tools.production_workspace.release_manifest import require
from tools.production_workspace.update_storage import no_links


@contextmanager
def protected_file(path, digest, size):
    import msvcrt

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p,
                                   w.DWORD, w.DWORD, w.HANDLE]
    kernel.CreateFileW.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    handle = kernel.CreateFileW(str(no_links(path)), 0x80000000, 1, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    with os.fdopen(descriptor, 'rb') as stream:
        require(os.fstat(stream.fileno()).st_size == size and
                hashlib.file_digest(stream, 'sha256').hexdigest() == digest,
                'Picross-Spieldateien fehlen oder sind beschädigt.')
        yield


def process_image(pid, process_handle):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetProcessId.argtypes = [w.HANDLE]
    kernel.GetProcessId.restype = w.DWORD
    kernel.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR,
                                                  ctypes.POINTER(w.DWORD)]
    text, length = ctypes.create_unicode_buffer(32768), w.DWORD(32768)
    require(kernel.GetProcessId(process_handle) == pid and
            kernel.QueryFullProcessImageNameW(process_handle, 0, text, ctypes.byref(length)),
            'Spielprozess konnte nicht gebunden werden.')
    return Path(text.value)


def visible_window(pid):
    user = ctypes.WinDLL('user32', use_last_error=True)
    callback = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    user.EnumWindows.argtypes = [callback, w.LPARAM]
    user.GetWindowThreadProcessId.argtypes = [w.HWND, ctypes.POINTER(w.DWORD)]
    user.IsWindowVisible.argtypes = [w.HWND]
    handles = []

    @callback
    def collect(window, _):
        owner = w.DWORD()
        user.GetWindowThreadProcessId(window, ctypes.byref(owner))
        if owner.value == pid and user.IsWindowVisible(window):
            handles.append(window)
            return False
        return True

    user.EnumWindows(collect, 0)
    return handles[0] if handles else None


def observe(process, expected):
    deadline = time.monotonic() + 30
    while process.poll() is None and time.monotonic() < deadline:
        if window := visible_window(process.pid):
            if process_image(process.pid, int(process._handle)) == expected and process.poll() is None:
                return window
        time.sleep(0.05)
    raise ValueError('Sichtbares Fenster des unveränderten Spielprozesses unbestätigt.')


def play(directory, build, confirm=None):
    player = no_links(directory / 'picross-p1.exe')
    with ExitStack() as files:
        for prefix, path in (('player', player), ('pck', directory / 'picross-p1.pck')):
            files.enter_context(protected_file(path, build[prefix + '_sha256'], build[prefix + '_bytes']))
        with system_dlls():
            process = subprocess.Popen([str(player)], cwd=directory, env=external_environment(),
                                       stdin=subprocess.DEVNULL, close_fds=True)
        with process:
            if confirm is not None:
                confirm(process, observe(process, player))
            if process.wait() != 0:
                raise ValueError('Picross wurde mit einem Fehler beendet. Bitte erneut starten.')
