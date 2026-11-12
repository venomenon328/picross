"""Launch external Git/browser with the system DLL search, without a console."""
from contextlib import contextmanager
import os
import subprocess
import sys
import threading
import webbrowser

_launch_lock = threading.RLock()


def external_environment():
    env = os.environ.copy()
    bundle = getattr(sys, '_MEIPASS', None)
    if bundle:
        env['PATH'] = os.pathsep.join(p for p in env.get('PATH', '').split(os.pathsep)
                                     if not os.path.normcase(p).startswith(os.path.normcase(bundle)))
    return env


@contextmanager
def system_dlls():
    # PyInstaller installs a process-wide DLL directory on Windows. Restore it
    # immediately after CreateProcess/ShellExecute, not after the child exits.
    with _launch_lock:
        if os.name != 'nt' or not getattr(sys, 'frozen', False):
            yield
            return
        import ctypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        buffer = ctypes.create_unicode_buffer(32768)
        kernel.GetDllDirectoryW(len(buffer), buffer)
        kernel.SetDllDirectoryW(None)
        try:
            yield
        finally:
            kernel.SetDllDirectoryW(buffer.value or None)


def run(arguments, *, timeout=30, env=None, **kwargs):
    with system_dlls():
        process = subprocess.Popen(arguments, env=env or external_environment(),
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                   stdin=subprocess.DEVNULL, **kwargs)
    try:
        out, err = process.communicate(timeout=timeout)
    except BaseException:
        process.kill()  # Only this exact child; never a PID taken from state.
        process.communicate()
        raise
    return subprocess.CompletedProcess(arguments, process.returncode, out, err)


def open_browser(url):
    # url is constructed by Runtime, never received from a control request.
    with system_dlls():
        if os.name == 'nt':
            os.startfile(url)
            return True
        return webbrowser.open(url)
