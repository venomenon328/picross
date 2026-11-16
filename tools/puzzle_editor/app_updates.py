"""PE native lifecycle adapter; all update authority stays in the shared client."""
import os
import hashlib
import json
import time
from pathlib import Path
import secrets
import threading
from types import SimpleNamespace

from tools.app_products import PE
from tools.production_workspace.app_updates import Updates
from tools.production_workspace.instance import StateLock, data, mac
from tools.production_workspace import update_windows as windows
from tools.production_workspace.update_storage import no_links


class Controller:
    def __init__(self, state, selection=None):
        self.status = "App-Updates nur in der installierten Windows-Ausgabe verfügbar."
        self.updates = None
        self.runtime = None
        self.handoff = None
        self.waiting = False
        lock = None
        try:
            windows.installation(app=PE)
            no_links(state)
            lock = StateLock(state, app=PE)
            if not lock.acquire():
                self.status = "Eine andere PE-Instanz verwendet diesen Updatezustand. Vorhandenen Editor verwenden."
                return
            self.runtime = SimpleNamespace(lock=lock, stop_requested=threading.Event(),
                stopped=threading.Event(), error=None, no_browser=True,
                metadata={"instance": secrets.token_hex(24)},
                selection=selection_data(selection or {"checkout": "", "port": "0"}))
            self.updates = Updates(self.runtime, app=PE)
            self.waiting = self.updates.enabled is None and self.updates.preferences is not None
            self.waiting = self.updates.start() or self.waiting
        except (ValueError, OSError, KeyError, TypeError):
            if lock: lock.close()
            self.runtime = None

    def select(self, selection):
        if self.runtime:
            self.runtime.selection = selection_data(selection)

    def choose(self, enabled):
        if self.updates and self.handoff is None:
            self.updates.choose(enabled)
            self.waiting = self.updates.pending

    def skip(self):
        if self.updates and self.handoff is None and self.updates.cancel():
            self.waiting = False

    def poll(self):
        if self.updates:
            self.handoff = self.handoff or self.updates.take()
            if self.handoff and self.handoff.selection != self.runtime.selection:
                self.handoff.abort()
                self.handoff = None
                self.updates.cancelled.set()
                self.updates.status = "Auswahl geändert; App-Update verworfen. Vorhandenen Editor starten."
                self.waiting = False
            if self.handoff:
                self.waiting = True
            elif self.updates.enabled is not None or self.updates.cancelled.is_set():
                self.waiting = self.updates.pending
            self.updates.poll_result()
            self.status = self.updates.status
        return self.handoff

    def stopping(self):
        if self.runtime:
            self.runtime.stop_requested.set()
        if self.updates and self.handoff is None:
            self.updates.cancel()

    def finish(self, error=None):
        """Called after Tk destruction and service/drain thread completion, before GO."""
        if not self.runtime:
            return
        try:
            self.stopping()
            self.runtime.error = error
            if self.updates and self.updates.thread:
                self.updates.thread.join()
            if self.handoff and error is None:
                self.runtime.stopped.set()
                self.handoff.commit(self.runtime)
        finally:
            if self.updates:
                self.updates.close()
            self.runtime.lock.close()


def selection_data(selection):
    if (not isinstance(selection, dict) or set(selection) != {"checkout", "port"} or
            not all(isinstance(v, str) for v in selection.values()) or
            len(selection["checkout"]) > 8192 or len(selection["port"]) > 16):
        raise ValueError("Ungültige Wiederanlaufauswahl.")
    return data(selection).decode("ascii")


def restored_selection(initial, port):
    raw = os.environ.pop("PICROSS_PE_READY_SELECTION", None)
    if raw is None:
        return {"checkout": initial or "", "port": str(port)}
    if not all(len(os.environ.get(k, "")) == 48 for k in ("PICROSS_PE_READY_NONCE", "PICROSS_PE_READY_KEY")):
        raise ValueError("Ungebundene Wiederanlaufauswahl.")
    result = json.loads(raw)
    if selection_data(result) != raw:
        raise ValueError("Nichtkanonische Wiederanlaufauswahl.")
    return result


def restart_ready(state, selection):
    """Respond only from a running native window; never start the editor service."""
    nonce = os.environ.pop("PICROSS_PE_READY_NONCE", "")
    key = os.environ.pop("PICROSS_PE_READY_KEY", "")
    if not nonce and not key:
        return
    if any(len(v) != 48 or any(c not in "0123456789abcdef" for c in v) for v in (nonce, key)):
        raise ValueError("Ungültige Wiederanlaufbindung.")
    identity = windows.installation(app=PE)
    with open("\\\\.\\pipe\\PicrossPEReady-" + nonce, "r+b", buffering=0) as pipe:
        import ctypes
        from ctypes import wintypes
        import msvcrt
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.PeekNamedPipe.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
                                        ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        handle = msvcrt.get_osfhandle(pipe.fileno())
        deadline = time.monotonic() + 10
        challenge = bytearray()
        while len(challenge) <= 48:
            available = wintypes.DWORD()
            if time.monotonic() > deadline or not kernel.PeekNamedPipe(handle, None, 0, None, ctypes.byref(available), None):
                raise ValueError("Wiederanlaufchallenge nicht rechtzeitig bestätigt.")
            if not available.value:
                time.sleep(0.01)
                continue
            char = pipe.read(1)
            if char == b"\n": break
            if not char: raise ValueError("Wiederanlaufhelfer nicht erreichbar.")
            challenge.extend(char)
        challenge = challenge.decode("ascii")
        if len(challenge) != 48 or any(c not in "0123456789abcdef" for c in challenge):
            raise ValueError("Ungültige Wiederanlaufchallenge.")
        path = no_links(Path(state) / "config.json")
        reply = {"pid": os.getpid(), "commit": identity.commit, "state": hashlib.sha256(str(state).encode("utf-8")).hexdigest(),
                 "selection": hashlib.sha256(selection_data(selection).encode("ascii")).hexdigest(),
                 "challenge": challenge, "config": windows.sha(path) if path.exists() else None}
        reply["proof"] = mac(key, "pe-ready:", reply)
        pipe.write(data(reply) + b"\n")
