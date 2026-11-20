"""Native PG startup and consent. The update worker never starts the player."""
from dataclasses import dataclass, field
import ctypes
from ctypes import wintypes as w
import hashlib
import threading
import time

from tools.app_products import PG
from tools.production_workspace.app_updates import Updates
from tools.production_workspace.instance import StateLock
from tools.production_workspace.update_storage import Preferences, accepted_handoff, atomic_json


@dataclass
class GateRuntime:
    lock: StateLock
    stop_requested: threading.Event = field(default_factory=threading.Event)


class Cancellation:
    """One Windows-owned event. An opt-out cannot be undone for this attempt."""
    def __init__(self, state):
        self.kernel = kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateEventW.argtypes = [ctypes.c_void_p, w.BOOL, w.BOOL, w.LPCWSTR]
        kernel.CreateEventW.restype = w.HANDLE
        kernel.SetEvent.argtypes = [w.HANDLE]
        kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        kernel.WaitForSingleObject.restype = w.DWORD
        kernel.CloseHandle.argtypes = [w.HANDLE]
        binding = hashlib.sha256(str(state).casefold().encode('utf-8')).hexdigest()
        self.handle = kernel.CreateEventW(None, True, False, 'Global\\PicrossGame.UpdateCancel.' + binding)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())

    def set(self):
        if not self.kernel.SetEvent(self.handle):
            raise ctypes.WinError(ctypes.get_last_error())

    def is_set(self):
        return self.kernel.WaitForSingleObject(self.handle, 0) != 258

    def close(self):
        self.kernel.CloseHandle(self.handle)


def window(title):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)
    panel = ttk.Frame(root, padding=20)
    panel.grid(sticky='nsew')
    status = tk.StringVar(root)
    ttk.Label(panel, textvariable=status, wraplength=430, justify='left').grid(sticky='w')
    buttons = ttk.Frame(panel, padding=(0, 14, 0, 0))
    buttons.grid(sticky='w')
    return root, status, buttons


def add_button(panel, caption, command, index):
    from tkinter import ttk

    ttk.Button(panel, text=caption, command=command).grid(row=0, column=index, padx=(0, 6))


def settings(state):
    lock = StateLock(state, app=PG, decision=True)
    if not lock.acquire():
        return
    try:
        if accepted_handoff(lock.directory):
            return
        preferences = Preferences(lock.directory)
        try:
            enabled = preferences.read()
        except (ValueError, OSError):
            enabled = None
        root, status, buttons = window('Picross – Update-Einstellungen')
        status.set({None: 'Automatische Spiel-Updates sind noch nicht aktiviert.',
                    False: 'Automatische Spiel-Updates sind ausgeschaltet.',
                    True: 'Automatische Spiel-Updates sind aktiviert.'}[enabled])

        def choose(value):
            try:
                if value:
                    preferences.write(True)
                else:
                    cancel = Cancellation(state)
                    try:
                        cancel.set()
                        preferences.write(False)
                    finally:
                        cancel.close()
            except (ValueError, OSError):
                status.set('Die Entscheidung konnte nicht sicher gespeichert werden.')
            else:
                root.destroy()

        for index, (caption, value) in enumerate((('Aktivieren', True), ('Ausschalten', False))):
            add_button(buttons, caption, lambda v=value: choose(v), index)
        root.mainloop()
    finally:
        lock.close()


class StartupGate:
    def __init__(self, state, owner, updates):
        self.state = state
        self.owner = owner
        self.updates = updates
        self.decision = StateLock(state, app=PG, decision=True)
        self.result = None
        self.handoff = None
        self.until = None
        self.root, self.status, self.buttons = window('Picross – Spiel-Updates')
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.stop('close'))

    def choose(self, enabled):
        if self.result is not None:
            return
        if not self.decision.acquire():
            self.status.set('Die Update-Einstellungen sind geöffnet. Bitte zuerst dort entscheiden.')
            return
        try:
            self.updates.choose(enabled)
        finally:
            self.decision.close()
        if self.updates.enabled is False:
            self.stop('play')
        else:
            self.controls(False)

    def controls(self, first):
        for button in self.buttons.winfo_children():
            button.destroy()
        actions = (('Aktivieren', lambda: self.choose(True)), ('Ablehnen', lambda: self.choose(False))) if first else (
            ('Ohne Update spielen', lambda: self.stop('play')), ('Updates ausschalten', lambda: self.choose(False)))
        for index, (caption, callback) in enumerate(actions):
            add_button(self.buttons, caption, callback, index)

    def stop(self, action):
        if self.handoff is not None:
            return
        if action == 'close':
            self.owner.stop_requested.set()
        if self.updates.cancel():
            self.result = action
            self.status.set('Updateprüfung wird beendet …')

    def take(self):
        if not self.decision.acquire():
            return False
        try:
            try:
                enabled = self.updates.preferences.read()
            except (ValueError, OSError):
                enabled = None
            if enabled is not True:
                self.stop('play')
                return False
            self.handoff = self.updates.take()
            if self.handoff:
                atomic_json(self.decision.directory / 'update-accepted.json', {'nonce': self.handoff.nonce})
                return True
        except (ValueError, OSError):
            if self.handoff:
                self.handoff.abort()
                self.handoff = None
            self.result = 'play'
            self.status.set('Spiel-Update konnte nicht übernommen werden.')
        finally:
            if self.handoff is None:
                self.decision.close()
        return False

    def poll(self):
        thread = self.updates.thread
        if self.result is not None:
            if not thread or not thread.is_alive():
                self.root.destroy()
                return
        elif self.updates.enabled is not None or self.updates.preferences is None:
            self.status.set(self.updates.status)
            if not thread or not thread.is_alive():
                if self.updates.pending:
                    if self.take():
                        self.root.destroy()
                        return
                else:
                    if self.until is None:
                        self.until = time.monotonic() + 2
                    if time.monotonic() >= self.until:
                        self.result = 'play'
                        self.root.destroy()
                        return
        self.root.after(75, self.poll)

    def run(self):
        first = self.updates.enabled is None and self.updates.preferences is not None
        self.controls(first)
        self.status.set('Automatisch vor dem Spielen nach signierten Updates suchen?' if first else self.updates.status)
        self.root.after(75, self.poll)
        try:
            self.root.mainloop()
            if self.handoff is not None:
                self.handoff.go()
            return self.result
        finally:
            self.decision.close()


def unavailable():
    """A state failure cannot authorize a request or prevent ordinary play."""
    root, status, _ = window('Picross – Spiel-Updates')
    status.set('Updatezustand nicht verfügbar. Die installierte Fassung startet …')
    play = False

    def proceed():
        nonlocal play
        play = True
        root.destroy()

    root.after(2000, proceed)
    root.mainloop()
    return play


def startup(state, directory, play):
    # The actual MSI/product binding is checked by Updates. An unpacked image
    # can still use the fixed player without touching the user's update state.
    if directory != state.parent / 'Programs' / PG.install_directory:
        play()
        return
    lock = None
    updates = None
    cancelled = None
    try:
        try:
            lock = StateLock(state, app=PG)
            if not lock.acquire() or accepted_handoff(lock.directory):
                return
            cancelled = Cancellation(state)
        except (ValueError, OSError):
            if unavailable():
                play()
            return
        owner = GateRuntime(lock)
        updates = Updates(owner, app=PG, cancelled=cancelled)
        if updates.enabled is False and not updates.started:
            play()
            return
        updates.start()
        action = StartupGate(state, owner, updates).run()
        updates.close()
        updates = None
        if action == 'play':
            play()
    finally:
        if updates is not None:
            updates.close()
        if cancelled is not None:
            cancelled.close()
        if lock is not None:
            lock.close()
