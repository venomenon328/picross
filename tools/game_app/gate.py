"""Native PG startup and consent. The update worker never starts the player."""
from dataclasses import dataclass, field
import ctypes
from ctypes import wintypes as w
import hashlib
import threading

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


class LauncherWindow:
    def __init__(self, version, play, choose, skip, close):
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

        settings_panel = ttk.LabelFrame(panel, text='Automatische Updates', padding=padding // 2)
        settings_panel.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(padding, 0))
        settings_panel.columnconfigure(0, weight=1)
        self.preference = ttk.Label(settings_panel)
        self.preference.grid(row=0, column=0, sticky='w')
        self.setting = ttk.Button(settings_panel, command=choose)
        self.setting.grid(row=0, column=1, sticky='e')

        actions = ttk.Frame(panel)
        actions.grid(row=5, column=0, columnspan=2, sticky='e', pady=(padding, 0))
        self.skip = ttk.Button(actions, text='Ohne Update spielen', command=skip)
        self.skip.grid(row=0, column=0, padx=(0, padding // 2))
        self.primary = ttk.Button(actions, command=play)
        self.primary.grid(row=0, column=1)
        self.primary.focus_set()
        root.bind('<Return>', lambda _: self.primary.invoke())
        self.mode = None

    def controls(self, enabled, available, *, idle, checking):
        self.preference.configure(text={True: 'Ein', False: 'Aus', None: 'Noch keine Entscheidung'}[enabled])
        self.setting.configure(text='Updates ausschalten' if enabled is True else 'Updates aktivieren',
                               state='normal' if available and (idle or checking) else 'disabled')
        self.primary.configure(text='Ohne Updates spielen' if available and enabled is None else 'Spielen',
                               state='normal' if idle else 'disabled')
        if checking:
            self.skip.grid()
        else:
            self.skip.grid_remove()

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
        self.owner = owner
        self.updates = updates
        self.available = updates is not None and updates.preferences is not None
        self.decision = StateLock(state, app=PG, decision=True) if self.available else None
        self.enabled = updates.enabled if self.available else False
        self.channel_status = updates.status if updates is not None and updates.started else ''
        self.requested = False
        self.result = None
        self.handoff = None
        self.stop_status = ''
        self.view = LauncherWindow(version, self.play, self.toggle,
                                   lambda: self.stop('play'), lambda: self.stop('close'))
        self.root = self.view.root

    def initial_status(self):
        if self.channel_status:
            return self.channel_status
        if not self.available:
            return 'Updatezustand nicht verfügbar. Du kannst die installierte Fassung spielen.'
        if self.enabled is None:
            return 'Updates sind zunächst aus. Du kannst sie hier aktivieren oder direkt offline spielen.'
        if self.enabled:
            return 'Beim Spielen wird zuerst nach signierten Updates gesucht.'
        return 'Bereit zum Spielen. Automatische Updates sind ausgeschaltet.'

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

    def controls(self, *, idle=False, checking=False):
        self.view.controls(self.enabled, self.available, idle=idle, checking=checking)

    def toggle(self):
        if not self.available or self.result is not None or self.handoff is not None:
            return
        if self.requested:
            if self.enabled is True:
                saved = self.save(False)
                message = ('Updates ausgeschaltet. Die installierte Fassung startet …' if saved else
                           'Ausschalten konnte nicht gespeichert werden. Diese Prüfung wird abgebrochen.')
                self.stop('play', message)
            return
        saved = self.save(self.enabled is not True)
        self.controls(idle=True)
        if saved:
            self.view.show(self.initial_status())

    def play(self):
        if self.requested or self.result is not None:
            return
        self.requested = True
        self.controls()
        if self.available and self.enabled is None:
            if not self.save(False):
                self.finish('Die Updateentscheidung konnte nicht gespeichert werden. '
                            'Die installierte Fassung startet offline …')
                return
        if self.enabled is True:
            try:
                if not self.decision.acquire():
                    self.finish('Update-Einstellungen sind bereits geöffnet. Die installierte Fassung startet offline …')
                    return
                self.updates.enabled = self.updates.preferences.read()
                if self.updates.start():
                    self.controls(checking=True)
                    self.view.show('Signierten Updatekanal prüfen …', busy=True)
                    self.root.after(75, self.poll)
                    return
            except (ValueError, OSError):
                pass
            finally:
                self.decision.close()
            self.finish(self.channel_status or 'Updateprüfung nicht verfügbar. Die installierte Fassung startet …')
            return
        self.finish(self.channel_status)

    def finish(self, message):
        self.result = 'play'
        self.controls()
        if message:
            self.view.show(message)
            self.root.after(2000, self.root.destroy)
        else:
            self.root.destroy()

    def stop(self, action, message=''):
        if self.handoff is not None:
            return
        if action == 'close':
            self.result = 'close'
            if self.owner is not None:
                self.owner.stop_requested.set()
            if self.updates is not None:
                self.updates.cancel()
            self.root.destroy()
        elif self.requested and self.result is None and self.updates.cancel():
            self.result = 'play'
            self.stop_status = message
            self.controls()
            self.view.show('Updateprüfung wird beendet …')

    def take(self):
        if self.result is not None:
            return False
        try:
            if not self.decision.acquire():
                return False
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
            self.stop_status = 'Spiel-Update konnte nicht übernommen werden. Die installierte Fassung startet …'
        finally:
            if self.handoff is None:
                self.decision.close()
        return False

    def poll(self):
        if self.updates.thread.is_alive():
            if self.result is None:
                progress = self.updates.progress
                if self.updates.cancelled.is_set():
                    self.view.show(self.updates.status)
                elif progress and progress[0] == 'download':
                    self.view.show('Update herunterladen …', progress[1:])
                elif progress:
                    self.view.show('Heruntergeladenes Update prüfen …', busy=True)
                else:
                    self.view.show(self.updates.status, busy=True)
        elif self.result == 'play':
            self.finish(self.stop_status)
            return
        elif self.updates.pending:
            if self.take():
                self.controls()
                self.root.destroy()
                return
        else:
            status = ('Updateversuch verworfen. Die installierte Fassung startet …'
                      if self.updates.handoff else self.updates.status)
            self.finish(status)
            return
        self.root.after(75, self.poll)

    def run(self):
        self.controls(idle=True)
        self.view.show(self.initial_status())
        try:
            self.root.mainloop()
            if self.handoff is not None:
                self.handoff.go()
            return self.result
        finally:
            if self.decision is not None:
                self.decision.close()


def startup(state, directory, play, *, version):
    # An unpacked image can still use the fixed player without touching the
    # user's update state. Updates also checks the actual MSI/product binding.
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
            if StartupGate(state, None, None, version).run() == 'play':
                play()
            return
        owner = GateRuntime(lock)
        updates = Updates(owner, app=PG, cancelled=cancelled)
        try:
            gate = StartupGate(state, owner, updates, version)
        except (ValueError, OSError):
            gate = StartupGate(state, None, None, version)
        action = gate.run()
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
