"""Native setup/status controller; production remains in the standard browser."""
import argparse
import os
import sys
from pathlib import Path
import threading

from .instance import StateLock, existing
from .install_interlock import InstallInterlock
from .runtime import Runtime, PortConflict, build_id, preflight


def arguments(argv):
    parser = argparse.ArgumentParser(description='Picross · Produktionsassistent')
    default = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local' / 'share'))) / 'PicrossProductionWorkspace'
    parser.add_argument('--state', type=Path, default=default)
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--repository', type=Path)
    parser.add_argument('--remote')
    parser.add_argument('--ref', action='append', dest='refs')
    parser.add_argument('--port', type=int, help='Ausdrücklicher Portwechsel; 0 wählt neu, mit getrenntem Browserzustand.')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--headless', action='store_true', help='Beaufsichtigter Prozess-/HTTP-Smoke')
    parser.add_argument('--stop', action='store_true', help='Passende authentisierte Instanz regulär beenden')
    return parser.parse_args(argv)


def error_dialog(message, root=None):
    try:
        from tkinter import messagebox
        messagebox.showerror('Picross · Start nicht möglich', message, parent=root)
    except Exception:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, 'Picross · Start nicht möglich', 0x10)


def setup(root, args, state):
    from tkinter import ttk, filedialog, messagebox
    import tkinter as tk
    from .repository import configure
    accepted = []
    panel = ttk.Frame(root, padding=20); panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='Picross einmal einrichten', font=('Segoe UI', 15)).pack(anchor='w')
    ttk.Label(panel, text='Vorhandenen Projektcheckout wählen. Seine Dateien bleiben erhalten.').pack(anchor='w', pady=(8, 16))
    repository = tk.StringVar(value=str(args.repository or ''))
    ttk.Label(panel, text='Projektcheckout').pack(anchor='w')
    ttk.Entry(panel, textvariable=repository, width=64).pack(fill='x')
    def browse():
        value = filedialog.askdirectory(parent=root, title='Projektcheckout wählen')
        if value:
            repository.set(value)
    ttk.Button(panel, text='Ordner wählen …', command=browse).pack(anchor='w', pady=6)
    mode = tk.StringVar(value='remote' if args.remote else 'local')
    ttk.Radiobutton(panel, text='Nur lokale Gitstände', variable=mode, value='local').pack(anchor='w', pady=(12, 0))
    ttk.Radiobutton(panel, text='Mit bewusst gewähltem Remote aktualisieren', variable=mode, value='remote').pack(anchor='w')
    remote = tk.StringVar(value=args.remote or '')
    ttk.Entry(panel, textvariable=remote, width=64).pack(fill='x', pady=6)
    ttk.Label(panel, text='HTTPS/SSH ohne Passwort oder Token. Bestehende Git-Anmeldung verwenden.').pack(anchor='w')
    ttk.Label(panel, text='Einrichtung und Cache: ' + str(state), wraplength=540).pack(anchor='w', pady=14)
    def accept():
        try:
            if not repository.get().strip() or mode.get() == 'remote' and not remote.get().strip():
                raise ValueError('Quelle fehlt.')
            configure(Path(repository.get().strip()), state, remote=remote.get().strip() if mode.get() == 'remote' else None,
                      refs=args.refs, launcher=True)
        except (OSError, ValueError):
            messagebox.showerror('Einrichtung prüfen', 'Checkout, Remote oder Zustandsordner ungültig. '
                                 'Checkoutwurzel und getrennten eigenen Zustandsordner wählen.', parent=root)
            return
        accepted.append(True); root.quit()
    ttk.Button(panel, text='Einrichtung speichern und starten', command=accept).pack(anchor='w')
    ttk.Button(panel, text='Abbrechen', command=root.quit).pack(anchor='w', pady=8)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()
    panel.destroy()
    return bool(accepted)


def run_headless(args, lock, build):
    from .repository import configure
    if args.setup or not (lock.state / 'config.json').exists():
        if args.repository is None:
            raise ValueError('Ersteinrichtung benötigt --repository oder das native Steuerfenster.')
        configure(args.repository, lock.state, remote=args.remote, refs=args.refs, launcher=True)
    elif args.repository or args.remote or args.refs:
        raise ValueError('Einrichtung existiert bereits. Vorhandenen Zustand unverändert starten.')
    runtime = Runtime(lock, build, no_browser=args.no_browser)
    runtime.start(args.port)
    try:
        runtime.open(); runtime.refresh()
        while not runtime.stop_requested.wait(0.1):
            if runtime.open_requested.is_set():
                runtime.open_requested.clear(); runtime.open()
    except KeyboardInterrupt:
        pass
    finally:
        runtime.request_stop(); runtime.stopped.wait()
    if runtime.error:
        raise ValueError(runtime.error)
    return 0


class Startup:
    """GUI-thread owner of first work, skip and update-drain decisions.

    Construct only after authenticated HTTP readiness. Network work lives in
    Updates; external control requests only set Runtime events, never call us.
    """
    def __init__(self, runtime, updates, browser_error):
        self.runtime, self.updates, self.browser_error = runtime, updates, browser_error
        self.begun = self.waiting = self.working = self.closing = False
        self.handoff = None

    def begin(self):
        if self.begun:
            return
        self.begun = True
        if self.runtime.stop_requested.is_set():
            self.stop()
            return
        self.waiting = bool(self.updates and self.updates.start())
        if not self.waiting:
            self.work()

    def open(self):
        if not self.working or self.closing or self.runtime.stop_requested.is_set():
            return
        try:
            self.runtime.open()
        except (OSError, ValueError):
            self.browser_error()

    def work(self):
        if self.working or self.closing or self.runtime.stop_requested.is_set():
            return
        self.waiting = False
        self.working = True  # Claim before browser error dialogs can reenter Tk.
        self.runtime.open_requested.clear()  # Coalesce a second start into first open.
        self.open()
        if not self.closing and not self.runtime.stop_requested.is_set():
            self.runtime.refresh()

    def skip(self):
        if self.waiting and not self.closing and self.updates.cancel():
            self.work()

    def stop(self):
        self.closing = True
        self.waiting = False
        if self.updates and self.handoff is None:
            self.updates.cancel()
        self.runtime.request_stop()

    def poll(self):
        if self.runtime.stop_requested.is_set() and not self.closing:
            self.stop()
        if self.closing:
            return
        if self.updates:
            self.handoff = self.updates.take()
            if self.handoff:
                self.stop()
                return
            if self.waiting and not self.updates.pending:
                self.work()
        if self.runtime.open_requested.is_set():
            self.runtime.open_requested.clear()
            self.open()  # While gated, a second start cannot bypass the decision.


def run_gui(args, lock, build):
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk(); root.title('Picross · Produktionsassistent'); root.minsize(620, 320)
    if os.name == 'nt':
        root.iconbitmap(str(Path(__file__).parent / 'assets/launcher.ico'))
    runtime = None
    updates = None
    controller = None
    try:
        setup_start = args.setup or not (lock.state / 'config.json').exists()
        if args.setup or not (lock.state / 'config.json').exists():
            if not setup(root, args, lock.state):
                return 0
        elif args.repository or args.remote or args.refs:
            raise ValueError('Einrichtung existiert bereits. Vorhandenen Zustand unverändert starten.')
        panel = ttk.Frame(root, padding=20); panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='Picross Produktionsassistent', font=('Segoe UI', 15)).pack(anchor='w')
        status = tk.StringVar(value='Programm und Einrichtung werden geprüft …')
        ttk.Label(panel, textvariable=status, wraplength=540).pack(anchor='w', pady=16)
        ttk.Label(panel, text='Minimieren lässt den Assistenten laufen. Schließen beendet ihn geordnet.').pack(anchor='w')
        ready, startup = threading.Event(), {}
        runtime = Runtime(lock, build, no_browser=args.no_browser)
        def start(port):
            try:
                runtime.start(port)
            except Exception as exc:
                startup['error'] = exc
            finally:
                ready.set()
        def launch(port):
            ready.clear(); startup.clear()
            threading.Thread(target=start, args=(port,), name='PW-start').start()
        open_button = ttk.Button(panel, text='Im Browser öffnen', command=runtime.open_requested.set, state='disabled')
        open_button.pack(anchor='w', pady=(16, 6))
        closing = False
        def stop():
            nonlocal closing
            closing = True; open_button.configure(state='disabled')
            if controller:
                controller.stop()
            status.set('Beenden: eigene Anfragen und Git-Arbeit laufen aus. Eine begonnene Entfernung wird nicht abgebrochen.')
            if ready.is_set() and 'error' not in startup:
                runtime.request_stop()
        ttk.Button(panel, text='Assistent beenden', command=stop).pack(anchor='w')
        root.protocol('WM_DELETE_WINDOW', stop)
        launched = False
        update_status = None
        decision = None
        skip_button = None
        def show_updates():
            nonlocal updates, update_status, decision, skip_button
            if setup_start or closing or os.name != 'nt' or not getattr(sys, 'frozen', False):
                return
            from .app_updates import Updates
            updates = Updates(runtime)
            box = ttk.LabelFrame(panel, text='Automatische App-Updates', padding=10)
            box.pack(fill='x', pady=12)
            update_status = tk.StringVar(value=updates.status)
            ttk.Label(box, textvariable=update_status, wraplength=540).pack(anchor='w')
            decision = ttk.Frame(box); decision.pack(anchor='w', pady=6)
            enabled = tk.BooleanVar(value=updates.enabled is True)
            def toggle():
                updates.choose(enabled.get()); enabled.set(updates.enabled is True)
            def choose(value):
                updates.choose(value)
                for child in decision.winfo_children():
                    child.destroy()
                enabled.set(updates.enabled is True)
                ttk.Checkbutton(decision, text='Automatische App-Updates aktivieren', variable=enabled, command=toggle).pack(anchor='w')
            if updates.preferences is not None:
                if updates.enabled is None:
                    ttk.Label(decision, text='Automatische App-Updates aktivieren?').pack(anchor='w')
                    ttk.Label(decision, text='Nach Prüfung werden neuere Versionen geladen; die App beendet laufende Arbeit und startet neu.', wraplength=520).pack(anchor='w')
                    ttk.Button(decision, text='Ablehnen', command=lambda: choose(False)).pack(side='left')
                    ttk.Button(decision, text='Aktivieren', command=lambda: choose(True)).pack(side='left', padx=8)
                else:
                    ttk.Checkbutton(decision, text='Automatische App-Updates aktivieren', variable=enabled, command=toggle).pack(anchor='w')
            skip_button = ttk.Button(box, text='Ohne Update fortfahren', command=lambda: controller.skip())
            skip_button.pack(anchor='w', pady=6)
            def recover_tick():
                updates.poll_result()
                if updates.recovery_attempts < 10:
                    root.after(1000, recover_tick)
            root.after(1000, recover_tick)
        def tick():
            nonlocal launched, controller
            if ready.is_set() and not launched:
                if 'error' in startup:
                    error = startup['error']
                    if isinstance(error, PortConflict) and not closing:
                        if messagebox.askretrycancel('Port belegt', str(error) + '\n\nDieselbe Adresse erneut versuchen?', parent=root):
                            launch(args.port); root.after(100, tick); return
                        if messagebox.askyesno('Port ausdrücklich wechseln', 'Neuen freien Port wählen? Browseroptionen und Entwürfe sind dort getrennt.', parent=root):
                            args.port = 0; launch(0); root.after(100, tick); return
                    error_dialog(str(error) if isinstance(error, ValueError) else 'Einrichtung nicht lesbar oder Zustand nicht beschreibbar. Pfade und Rechte prüfen.', root)
                    root.quit(); return
                launched = True
                if closing:
                    runtime.request_stop()
                else:
                    show_updates()
                    controller = Startup(runtime, updates, lambda: error_dialog(
                        'Standardbrowser nicht erreichbar. Standardbrowser einrichten und erneut öffnen.', root))
                    controller.begin()
            if launched:
                if runtime.stop_requested.is_set() and not closing:
                    stop()
                if controller and not closing:
                    if runtime.open_requested.is_set():
                        root.deiconify(); root.lift()
                    controller.poll()
                    if controller.closing:
                        stop()
                    open_button.configure(state='normal' if controller.working and not closing else 'disabled')
                if updates:
                    update_status.set(updates.status)
                    skip_button.configure(state='normal' if controller.waiting and not closing else 'disabled')
                    if closing:
                        for child in decision.winfo_children():
                            if isinstance(child, (ttk.Button, ttk.Checkbutton)):
                                child.configure(state='disabled')
                if runtime.stopped.is_set():
                    if runtime.error:
                        error_dialog(runtime.error, root)
                    elif runtime.service.removal_result:
                        messagebox.showinfo('Ergebnis der laufenden Entfernung', runtime.service.removal_result, parent=root)
                    update_handoff = controller.handoff if controller else None
                    if update_handoff:
                        if runtime.error:
                            update_handoff.abort()
                        else:
                            try:
                                update_handoff.commit(runtime)
                            except (OSError, ValueError):
                                update_handoff.abort()
                                error_dialog('Updateübergabe nicht bestätigt. Assistent danach manuell starten.', root)
                    root.quit(); return
                if not closing:
                    if controller and controller.waiting:
                        status.set('App-Update vor Arbeitsbeginn prüfen. Browser und Git warten; ohne Update fortfahren ist möglich.')
                    else:
                        update = runtime.service.status()['update']
                        status.set('Bereit. Quellen werden im Hintergrund gesucht …' if update['state'] == 'running' else
                                   'Bereit. ' + (update['error'] or 'Browser-Tab schließen beendet den Assistenten nicht.'))
            root.after(100, tick)
        launch(args.port); root.after(100, tick); root.mainloop()
        return 0
    finally:
        if updates:
            updates.close()
        if runtime and runtime.thread and runtime.thread.is_alive():
            runtime.request_stop(); runtime.stopped.wait()
        root.destroy()


def main(argv=None, *, console=False):
    import sys
    lock = None
    installation = InstallInterlock()
    args = arguments(argv)
    try:
        installation.acquire()
        preflight(gui=not args.headless or getattr(sys, 'frozen', False))
        build = build_id()
        lock = StateLock(args.state)
        if not lock.acquire():
            existing(lock, build, 'stop' if args.stop else 'open')
            return 0
        if args.stop:
            raise ValueError('Keine laufende passende Instanz. Historische CMD mit Strg+C beenden.')
        return run_headless(args, lock, build) if args.headless else run_gui(args, lock, build)
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else 'Start nicht möglich. Gesamtes App-Paket neu entpacken, Einrichtung und Zugriffsrechte prüfen.'
        if (console or args.headless) and sys.stderr is not None:
            print(message, file=sys.stderr)
        elif not args.headless:
            error_dialog(message)
        return 2
    finally:
        if lock:
            lock.close()
        installation.close()
