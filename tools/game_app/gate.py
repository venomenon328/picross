"""Native PG startup and consent. The update worker never starts the player."""
from dataclasses import dataclass, field
import ctypes
from ctypes import wintypes as w
import hashlib
import threading
import queue

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
        status.set({None: 'Automatische Update-Suche ist noch nicht aktiviert.',
                    False: 'Automatische Update-Suche ist ausgeschaltet.',
                    True: 'Automatische Update-Suche ist aktiviert.'}[enabled])

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


class LauncherWindow:
    def __init__(self, version, play, choose, install, close):
        import tkinter as tk
        from tkinter import font, ttk

        root = self.root = tk.Tk()
        root.title('Picross')
        root.protocol('WM_DELETE_WINDOW', close)
        root.resizable(False, False)
        scale = root.winfo_fpixels('1i') / 96
        width = round(520 * scale)
        padding = round(20 * scale)
        wrap = width - 2 * padding
        root.grid_columnconfigure(0, minsize=width)
        root.maxsize(width, root.winfo_screenheight())

        panel = ttk.Frame(root, padding=padding)
        panel.grid(sticky='nsew')
        panel.columnconfigure(0, weight=1)

        title = font.nametofont('TkDefaultFont').copy()
        title.configure(size=20, weight='bold')
        self.title_font = title
        ttk.Label(panel, text='Picross', font=title).grid(row=0, column=0, sticky='w')
        ttk.Label(panel, text=f'Version {version}').grid(row=0, column=1, sticky='se')

        panel.rowconfigure(1, minsize=4 * font.nametofont('TkDefaultFont').metrics('linespace') + padding)
        self.status = ttk.Label(panel, wraplength=wrap, justify='left')
        self.status.grid(row=1, column=0, columnspan=2, sticky='nw', pady=(padding, 0))
        self.bar = ttk.Progressbar(panel)
        self.bar.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.amount = ttk.Label(panel)
        self.amount.grid(row=3, column=0, columnspan=2, sticky='w')
        panel.rowconfigure(2, minsize=self.bar.winfo_reqheight())
        panel.rowconfigure(3, minsize=self.amount.winfo_reqheight())
        self.bar.grid_remove()

        settings_panel = ttk.LabelFrame(panel, text='Automatische Update-Suche', padding=padding // 2)
        settings_panel.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(padding, 0))
        settings_panel.columnconfigure(0, weight=1)
        self.preference = ttk.Label(settings_panel)
        self.preference.grid(row=0, column=0, sticky='w')
        self.setting = ttk.Button(settings_panel, command=choose)
        self.setting.grid(row=0, column=1, sticky='e')

        actions = ttk.Frame(panel)
        actions.grid(row=5, column=0, columnspan=2, sticky='e', pady=(padding, 0))
        self.install = ttk.Button(actions, text='Update installieren', command=install)
        self.install.grid(row=0, column=0, padx=(0, padding // 2))
        self.primary = ttk.Button(actions, command=play)
        self.primary.grid(row=0, column=1)
        self.primary.focus_set()
        self.mode = None

    def controls(self, enabled, available, *, interactive, offered):
        label = {True: 'Ein', False: 'Aus', None: 'Noch keine Entscheidung'}[enabled]
        self.preference.configure(text=label if available else 'Nicht verfügbar')
        self.setting.configure(text='Suche ausschalten' if enabled is True else 'Suche aktivieren',
                               state='normal' if available and interactive else 'disabled')
        self.primary.configure(text='Ohne Updates spielen' if available and enabled is None else 'Spielen',
                               state='normal' if interactive else 'disabled')
        if offered and interactive:
            self.install.grid()
        else:
            self.install.grid_remove()

    def show(self, status, progress=None, *, busy=False):
        self.status.configure(text=status)
        mode = 'determinate' if progress else 'indeterminate' if busy else None
        if mode != self.mode:
            self.bar.stop()
            self.mode = mode
            if mode is None:
                self.bar.grid_remove()
            else:
                self.bar.configure(mode=mode, maximum=100, value=0)
                self.bar.grid()
                if mode == 'indeterminate':
                    self.bar.start()
        if progress:
            received, total = progress
            percent = 100 * received // total
            self.bar.configure(value=percent)
            self.amount.configure(text=f'{percent} % · {received / 1048576:.1f} / {total / 1048576:.1f} MiB'.replace('.', ','))
        else:
            self.amount.configure(text='')


class StartupGate:
    def __init__(self, state, owner, updates, version):
        self.state = state
        self.owner = owner
        self.result = None
        self.handoff = None
        self.restarting = False
        self.installing = False
        self.timer = None
        self.drain = None
        self.cancel_status = None
        self.configure_updates(updates)
        self.view = LauncherWindow(version, self.play, self.toggle, self.install, lambda: self.stop('close'))
        self.root = self.view.root

    def configure_updates(self, updates):
        self.updates = updates
        self.available = updates is not None and updates.preferences is not None
        self.decision = None
        if self.available:
            try:
                self.decision = StateLock(self.state, app=PG, decision=True)
            except (ValueError, OSError):
                self.available = False
        self.enabled = updates.enabled if self.available else False

    def initial_status(self):
        if self.updates and (self.updates.started or self.updates.recovery):
            return self.updates.status
        if not self.available:
            return 'Updatezustand nicht verfügbar. Du kannst die installierte Fassung spielen.'
        if self.enabled is None:
            return 'Du kannst die Update-Suche aktivieren oder direkt offline spielen.'
        return 'Bereit zum Spielen.'

    def save(self, enabled):
        try:
            if not self.decision.acquire():
                self.view.show('Die Update-Einstellungen sind bereits geöffnet. Bitte zuerst dort schließen.')
                return False
            saved = self.updates.save_preference(enabled)
            self.enabled = self.updates.enabled
            if saved:
                return True
        except (ValueError, OSError):
            pass
        finally:
            self.decision.close()
        self.view.show('Updateentscheidung konnte nicht sicher gespeichert werden. Automatik bleibt für diesen Start aus.')
        self.enabled = False
        return False

    def controls(self):
        self.view.controls(self.enabled, self.available, interactive=self.interactive,
                           offered=bool(self.updates and self.updates.offer and self.enabled is True))

    @property
    def interactive(self):
        return self.result is None and self.handoff is None and not self.restarting

    def search(self):
        if not self.interactive or not self.available or self.enabled is not True:
            return
        if self.updates.start():
            self.view.show('Signierten Updatekanal prüfen …', busy=True)
            self.timer = self.root.after(75, self.poll)

    def toggle(self):
        if not self.available or not self.interactive:
            return
        enable = self.enabled is not True
        saved = self.save(enable)
        if not enable and self.updates.started:
            self.updates.cancel()
            self.cancel_status = ('Automatische Update-Suche ausgeschaltet.' if saved else
                                  'Ausschalten nicht gespeichert. Dieser Updateversuch wurde verworfen.')
        self.controls()
        if saved:
            if enable and self.updates.started:
                self.cancel_status = 'Update-Suche aktiviert. Erneute Prüfung beim nächsten Öffnen.'
            self.view.show(self.cancel_status or ('Automatische Update-Suche aktiviert.' if enable else
                                                  'Automatische Update-Suche ausgeschaltet.'))
            if enable:
                self.search()

    def install(self):
        if self.interactive and self.enabled is True and self.updates.install_offer():
            self.installing = True
            self.controls()
            self.view.show('Update herunterladen …', busy=True)
            self.timer = self.root.after(75, self.poll)

    def play(self):
        if not self.interactive:
            return
        if self.available and self.enabled is None:
            if not self.save(False):
                self.result = 'play'
                self.controls()
                self.view.show('Updateentscheidung nicht gespeichert. Die installierte Fassung startet offline …')
                self.root.after(1500, self.destroy)
                return
        self.stop('play')

    def destroy(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.view.bar.stop()
        self.root.destroy()

    def stop(self, action):
        if not self.interactive:
            return
        self.result = action
        if self.owner is not None:
            self.owner.stop_requested.set()
        if self.updates is not None:
            self.updates.cancel()
        self.controls()
        if self.installing:
            self.view.show('Updateversuch wird beendet …', busy=True)
            # Wait for the discarded download and any still-uncommitted READY
            # helper to release their files before dispatching the player.
            self.drain = threading.Thread(target=self.updates.close, name='PG-update-cancel')
            self.drain.start()
            if self.timer is None:
                self.timer = self.root.after(75, self.poll)
        else:
            self.destroy()

    def take(self):
        if not self.interactive or not self.installing:
            return False
        try:
            if not self.decision.acquire():
                self.updates.cancel()
                self.view.show('Update-Einstellungen geöffnet. Installation verworfen.')
                return False
            if self.updates.preferences.read() is not True:
                self.enabled = False
                self.updates.cancel()
                self.view.show('Update-Suche ausgeschaltet. Installation verworfen.')
                return False
            self.handoff = self.updates.take()
            if self.handoff:
                atomic_json(self.decision.directory / 'update-accepted.json', {'nonce': self.handoff.nonce})
                return True
            self.updates.cancel()
            self.view.show('Zustimmung zur Installation konnte nicht bestätigt werden.')
        except (ValueError, OSError):
            if self.handoff:
                self.handoff.abort()
                self.handoff = None
            self.updates.cancel()
            self.view.show('Spiel-Update konnte nicht übernommen werden.')
        finally:
            if self.handoff is None:
                self.decision.close()
        return False

    def poll(self):
        self.timer = None
        if self.drain is not None:
            if self.drain.is_alive():
                self.timer = self.root.after(75, self.poll)
            else:
                self.destroy()
            return
        if self.updates.thread.is_alive():
            if self.result is None:
                progress = self.updates.progress
                if self.enabled is False and self.updates.cancelled.is_set():
                    self.view.show('Updateversuch wird beendet …', busy=True)
                elif progress and progress[0] == 'download':
                    self.view.show('Update herunterladen …', progress[1:])
                elif progress:
                    self.view.show('Heruntergeladenes Update prüfen …', busy=True)
                else:
                    self.view.show(self.updates.status, busy=not self.updates.cancelled.is_set())
            self.timer = self.root.after(75, self.poll)
            return
        if self.result is not None:
            self.destroy()
            return
        if self.updates.pending:
            if self.take():
                self.controls()
                self.destroy()
                return
        else:
            self.view.show(self.cancel_status or self.updates.status)
        self.installing = False
        self.controls()

    def run(self, on_visible=None):
        self.restarting = on_visible is not None
        self.controls()
        self.view.show('Installation wird bestätigt …' if self.restarting else self.initial_status())

        def mapped(event):
            if event.widget is self.root:
                self.root.unbind('<Map>', binding)
                self.root.after_idle(on_visible or self.search)

        binding = self.root.bind('<Map>', mapped)
        try:
            self.root.mainloop()
            if self.handoff is not None:
                self.handoff.go()
            return self.result
        finally:
            if self.decision is not None:
                self.decision.close()


def startup(state, directory, play, *, version, confirm_launcher=None):
    # An unpacked image can still use the fixed player without touching the
    # user's update state. Updates also checks the actual MSI/product binding.
    if directory != state.parent / 'Programs' / PG.install_directory:
        if confirm_launcher is not None:
            raise ValueError('Installierter Launcher erforderlich.')
        play()
        return
    lock = None
    updates = None
    cancelled = None
    try:
        try:
            lock = StateLock(state, app=PG)
            if not lock.acquire() or (confirm_launcher is None and accepted_handoff(lock.directory)):
                return
            cancelled = Cancellation(state)
        except (ValueError, OSError):
            if confirm_launcher is not None:
                raise
            if StartupGate(state, None, None, version).run() == 'play':
                play()
            return
        owner = GateRuntime(lock)
        if confirm_launcher is None:
            updates = Updates(owner, app=PG, cancelled=cancelled)
        gate = StartupGate(state, owner, updates, version)

        def authenticate():
            # Tk returns the native outer frame of this mapped root, including on Windows.
            window = int(gate.root.wm_frame(), 0)
            outcome = queue.Queue()

            def wait_for_helper():
                try:
                    outcome.put(confirm_launcher(window))
                except (ValueError, OSError, KeyError, TypeError):
                    outcome.put(None)

            thread = threading.Thread(target=wait_for_helper, name='PG-launcher-restart')
            thread.start()

            def completed():
                nonlocal updates
                if thread.is_alive():
                    gate.root.after(75, completed)
                    return
                nonce = None if outcome.empty() else outcome.get_nowait()
                if nonce:
                    updates = Updates(owner, app=PG, cancelled=cancelled, expected_nonce=nonce)
                if (not updates or not updates.recovery or updates.recovery.nonce != nonce or
                        updates.recovery.status != 'installed'):
                    gate.view.show('Wiederanlauf unbestätigt. Bitte schließen und die Installation prüfen.')
                    gate.root.protocol('WM_DELETE_WINDOW', gate.root.destroy)
                    return
                gate.configure_updates(updates)
                gate.restarting = False
                gate.controls()
                gate.view.show(updates.status)
                gate.search()

            completed()

        action = gate.run(authenticate if confirm_launcher is not None else None)
        if action == 'play':
            play()
    finally:
        if updates is not None:
            updates.close()
        if cancelled is not None:
            cancelled.close()
        if lock is not None:
            lock.close()
