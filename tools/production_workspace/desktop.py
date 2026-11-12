"""Native setup/status controller; production remains in the standard browser."""
import argparse
import os
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


def run_gui(args, lock, build):
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk(); root.title('Picross · Produktionsassistent'); root.minsize(620, 320)
    if os.name == 'nt':
        root.iconbitmap(str(Path(__file__).parent / 'assets/launcher.ico'))
    runtime = None
    try:
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
            status.set('Beenden: eigene Anfragen und Git-Arbeit laufen aus. Eine begonnene Entfernung wird nicht abgebrochen.')
            if ready.is_set() and 'error' not in startup:
                runtime.request_stop()
        ttk.Button(panel, text='Assistent beenden', command=stop).pack(anchor='w')
        root.protocol('WM_DELETE_WINDOW', stop)
        launched = False
        def tick():
            nonlocal launched
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
                    try:
                        runtime.open()
                    except (OSError, ValueError):
                        error_dialog('Standardbrowser nicht erreichbar. Standardbrowser einrichten und erneut öffnen.', root)
                    runtime.refresh(); open_button.configure(state='normal')
            if launched:
                if runtime.stop_requested.is_set() and not closing:
                    stop()
                if runtime.open_requested.is_set() and not closing:
                    runtime.open_requested.clear()
                    try:
                        runtime.open(); root.deiconify(); root.lift()
                    except (OSError, ValueError):
                        error_dialog('Windows-Standardbrowser prüfen und erneut öffnen.', root)
                if runtime.stopped.is_set():
                    if runtime.error:
                        error_dialog(runtime.error, root)
                    elif runtime.service.removal_result:
                        messagebox.showinfo('Ergebnis der laufenden Entfernung', runtime.service.removal_result, parent=root)
                    root.quit(); return
                if not closing:
                    update = runtime.service.status()['update']
                    status.set('Bereit. Quellen werden im Hintergrund gesucht …' if update['state'] == 'running' else
                               'Bereit. ' + (update['error'] or 'Browser-Tab schließen beendet den Assistenten nicht.'))
            root.after(100, tick)
        launch(args.port); root.after(100, tick); root.mainloop()
        return 0
    finally:
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
