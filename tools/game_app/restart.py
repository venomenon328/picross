"""PG's private, one-use launcher authentication and game observation."""
import ctypes
from ctypes import wintypes as w
import hashlib
import hmac
import os
from pathlib import Path
import time

from tools.app_products import PG
from tools.production_workspace.instance import data, mac
from tools.production_workspace.release_manifest import hex_string, require, shape, strict_json
from tools.production_workspace.update_storage import accepted_handoff, read_small
from tools.production_workspace.update_windows import installation, sha

from .player import play, process_image

ENV = tuple('PICROSS_PG_RESTART_' + name for name in ('PIPE', 'KEY', 'PID', 'STAGE'))


def line(pipe):
    import msvcrt

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.PeekNamedPipe.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD,
                                    ctypes.c_void_p, ctypes.POINTER(w.DWORD), ctypes.c_void_p]
    handle = msvcrt.get_osfhandle(pipe.fileno())
    deadline = time.monotonic() + 15
    raw = bytearray()
    while len(raw) < 1024 and time.monotonic() < deadline:
        available = w.DWORD()
        require(kernel.PeekNamedPipe(handle, None, 0, None, ctypes.byref(available), None),
                'Updatehelfer nicht erreichbar.')
        if available.value:
            character = pipe.read(1)
            if character == b'\n':
                return bytes(raw)
            require(character, 'Wiederanlauf abgebrochen.')
            raw += character
        else:
            time.sleep(0.01)
    raise ValueError('Wiederanlauf nicht rechtzeitig bestätigt.')


def verify_helper(pipe, pid, expected):
    import msvcrt

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetNamedPipeServerProcessId.argtypes = [w.HANDLE, ctypes.POINTER(w.ULONG)]
    kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    kernel.OpenProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    owner = w.ULONG()
    require(kernel.GetNamedPipeServerProcessId(msvcrt.get_osfhandle(pipe.fileno()), ctypes.byref(owner))
            and owner.value == pid, 'Fremder PG-Wiederanlaufhelfer.')
    process = kernel.OpenProcess(0x1000, False, pid)
    require(process, 'Updatehelfer nicht prüfbar.')
    try:
        require(process_image(pid, process) == expected, 'Fremdes Updateprogramm.')
    finally:
        kernel.CloseHandle(process)


def restart(directory, build, state):
    name, key, pid, nonce = (os.environ.pop(field, '') for field in ENV)
    require(all(hex_string(value, 48) for value in (name, key, nonce)) and
            pid.isascii() and pid.isdecimal() and 0 < int(pid) <= 0xFFFFFFFF,
            'Ungültiger PG-Wiederanlauf.')
    identity = installation(app=PG)
    updates = state / '.updates'
    require(read_small(updates / 'update-accepted.json') == {'nonce': nonce}
            and accepted_handoff(updates), 'PG-Übergabe nicht aktiv.')
    helper = updates / 'update-staging' / nonce / 'UpdateHelper.exe'
    with open(r'\\.\pipe\PicrossPGReady-' + name, 'r+b', buffering=0) as pipe:
        verify_helper(pipe, int(pid), helper)
        challenge = line(pipe).decode('ascii')
        require(hex_string(challenge, 48), 'Ungültige PG-Challenge.')
        binding = {
            'pid': os.getpid(),
            'commit': identity.commit,
            'challenge': challenge,
            'state': hashlib.sha256(str(state).encode('utf-8')).hexdigest(),
            'preference': sha(updates / 'app-updates.json'),
            'version': identity.version,
            'fingerprint': identity.payload_fingerprint,
        }
        pipe.write(data({**binding, 'proof': mac(key, 'pg-ready:', binding)}) + b'\n')
        go = strict_json(line(pipe))
        shape(go, 'proof', 'Ungültige PG-Startfreigabe')
        require(hex_string(go['proof'], 64) and
                hmac.compare_digest(go['proof'], mac(key, 'pg-play:', binding)),
                'Spielstartfreigabe nicht authentisiert.')

        def confirm(process, window):
            observed = {**binding, 'player': process.pid, 'window': window}
            # Even an EOF now leaves the one started child running until it exits.
            try:
                pipe.write(data({**observed, 'proof': mac(key, 'pg-started:', observed)}) + b'\n')
            except OSError:
                pass

        play(directory, build, confirm)
