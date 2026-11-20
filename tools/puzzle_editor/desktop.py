"""Small native setup window; close drains the trusted writer subprocess."""
import argparse
from pathlib import Path
import json
import os
import threading
import sys
import webbrowser

from tools.app_products import PE
from tools.puzzle_production import catalog_io as io
from . import VERSION
from .server import Service
from .settings import Settings


def load_ui():
    # The controller is importable for platform-neutral lifecycle tests.
    # Actual window creation still requires the bundled Tcl/Tk runtime.
    global tk, ttk, filedialog, messagebox
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox


class Window:
    def __init__(self, state, initial=None, port=0):
        load_ui()
        self.state, self.service, self.closing = io.external(state), None, False
        self.stop_failed = False
        self.window = tk.Tk(); self.window.title("Picross · Bestandseditor " + VERSION)
        if sys.platform == "win32":
            self.window.iconbitmap(str(PE.source / PE.icon_resource))
        self.window.geometry("760x490"); self.window.minsize(700, 450)
        self.path, self.port, self.status = tk.StringVar(value=initial or ""), tk.StringVar(value=str(port)), tk.StringVar(value="Vorhandenes lokales Picross-Checkout bewusst auswählen.")
        frame = ttk.Frame(self.window, padding=24); frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Picross · Bestandseditor", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Lokale Dateien pflegen · Git und Veröffentlichung bleiben extern").pack(anchor="w", pady=(5, 18))
        ttk.Label(frame, text="Ausgewähltes bestehendes Checkout").pack(anchor="w")
        row = ttk.Frame(frame); row.pack(fill="x", pady=6)
        self.entry = ttk.Entry(row, textvariable=self.path); self.entry.pack(side="left", fill="x", expand=True)
        self.choose = ttk.Button(row, text="Ordner wählen…", command=self.select); self.choose.pack(side="right", padx=(8, 0))
        line = ttk.Frame(frame); line.pack(fill="x", pady=8)
        ttk.Label(line, text="Port (0 = freier Port)").pack(side="left")
        self.port_entry = ttk.Entry(line, textvariable=self.port, width=8); self.port_entry.pack(side="left", padx=8)
        self.start_button = ttk.Button(line, text="Editor starten", command=self.start); self.start_button.pack(side="left", padx=8)
        self.browser_button = ttk.Button(line, text="Browser öffnen", command=self.open, state="disabled"); self.browser_button.pack(side="left")
        ttk.Button(line, text="Geordnet beenden", command=self.close).pack(side="right")
        ttk.Label(frame, textvariable=self.status, wraplength=670).pack(anchor="w", pady=12)
        from .app_updates import Controller
        self.updates = Controller(self.state, self.selection())
        self.path.trace_add("write", self.selection_changed)
        self.port.trace_add("write", self.selection_changed)
        self.update_status = tk.StringVar(value=self.updates.status)
        ttk.Separator(frame).pack(fill="x", pady=8)
        ttk.Label(frame, textvariable=self.update_status, wraplength=690).pack(anchor="w")
        self.update_controls = ttk.Frame(frame); self.update_controls.pack(fill="x", pady=8)
        self.update_enabled = tk.BooleanVar(value=bool(self.updates.updates and self.updates.updates.enabled))
        self.update_buttons = []
        if self.updates.updates and self.updates.updates.preferences:
            if self.updates.updates.enabled is None:
                self.update_status.set("Automatische App-Updates beim Start ausdrücklich aktivieren oder ablehnen.")
                for label, value in (("Updates aktivieren", True), ("Updates ablehnen", False)):
                    button = ttk.Button(self.update_controls, text=label, command=lambda value=value: self.choose_updates(value))
                    button.pack(side="left", padx=(0,8)); self.update_buttons.append(button)
            self.update_toggle = ttk.Checkbutton(self.update_controls, text="Automatische App-Updates", variable=self.update_enabled,
                command=lambda: self.choose_updates(self.update_enabled.get()))
            self.update_toggle.pack(side="left"); self.update_buttons.append(self.update_toggle)
        self.skip_button = ttk.Button(frame, text="Ohne Update fortfahren", command=self.skip_update)
        self.skip_button.pack(anchor="w")
        self.refresh_update_controls()
        self.ready_thread = None
        self.ready_error = None
        self.window.after_idle(self.confirm_restart)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.after(250, self.poll)

    def selection(self):
        return {"checkout": self.path.get(), "port": self.port.get()}

    def selection_changed(self, *_):
        try: self.updates.select(self.selection())
        except ValueError:
            self.updates.skip()

    def choose_updates(self, enabled):
        self.updates.choose(enabled)
        self.update_enabled.set(self.updates.updates.enabled is True)
        # The explicit first choice is persistent; subsequent changes use the toggle.
        for button in self.update_buttons:
            if button is not self.update_toggle: button.pack_forget()
        self.refresh_update_controls()

    def skip_update(self):
        self.updates.skip()
        self.refresh_update_controls()

    def refresh_update_controls(self):
        blocked = self.updates.waiting or self.closing
        self.start_button.configure(state="disabled" if blocked or self.service else "normal")
        self.browser_button.configure(state="normal" if self.service and not blocked else "disabled")
        self.skip_button.configure(state="normal" if self.updates.waiting and not self.updates.handoff and not self.closing else "disabled")
        for control in (self.entry, self.choose, self.port_entry):
            control.configure(state="disabled" if self.service or self.closing or self.updates.handoff else "normal")
        for button in self.update_buttons:
            button.configure(state="disabled" if self.updates.handoff or self.closing else "normal")

    def confirm_restart(self):
        from .app_updates import restart_ready
        selection = self.selection()
        def confirm():
            try: restart_ready(self.state, selection)
            except Exception as exc: self.ready_error = "Wiederanlauf unbestätigt: " + str(exc)
        self.ready_thread = threading.Thread(target=confirm, name="PE-restart-ready")
        self.ready_thread.start()

    def select(self):
        value = filedialog.askdirectory(title="Bestehendes Picross-Checkout öffnen", mustexist=True, parent=self.window)
        if value: self.path.set(value)

    def start(self):
        if self.service or self.closing or (getattr(self, "updates", None) and self.updates.waiting): return
        try:
            value = self.port.get()
            if not value.isdecimal() or not 0 <= int(value) <= 65535: raise ValueError("Port muss zwischen 0 und 65535 liegen.")
            root = io.external(self.path.get())
            if self.state.is_relative_to(root) or root.is_relative_to(self.state):
                raise ValueError("Einstellungen müssen außerhalb des Inhaltscheckouts liegen.")
            if getattr(self, "updates", None): self.updates.skip()  # First manual start ends this startup attempt.
            self.service = Service(root, state=self.state)
            try: self.service.bind(int(value))
            except OSError:
                if not int(value) or not messagebox.askyesno("Port belegt", "Dieser Port ist nicht verfügbar. Einen freien abweichenden Port wählen?", parent=self.window): raise
                self.service.bind(0)
            self.path.set(str(root)); self.port.set(str(self.service.http.server_port))
            self.service.settings.update(checkout=str(root), port=self.service.http.server_port)
            self.entry.configure(state="disabled"); self.choose.configure(state="disabled"); self.port_entry.configure(state="disabled")
            self.start_button.configure(state="disabled"); self.browser_button.configure(state="normal")
            self.status.set("Bereit · " + self.service.origin + " · " + str(root))
            self.open()
        except Exception as exc:
            if self.service: self.service.close(); self.service = None
            self.status.set(str(exc)); messagebox.showerror("Editorstart nicht möglich", str(exc), parent=self.window)

    def open(self):
        if self.service and not self.closing and not (getattr(self, "updates", None) and self.updates.waiting): webbrowser.open(self.service.url())

    def close(self, confirmed=False):
        if self.closing: return
        if self.service and not confirmed and not messagebox.askokcancel("Editor beenden", "Ungespeicherte Browseränderungen vorher übernehmen oder verwerfen. Laufende Fachoperationen werden vollständig abgewartet. Jetzt beenden?", parent=self.window): return
        self.closing = True
        if getattr(self, "updates", None): self.updates.stopping()
        self.stop_failed = False
        self.status.set("Beenden: laufende Fachoperation wird abgewartet…")
        self.start_button.configure(state="disabled"); self.browser_button.configure(state="disabled")
        def drain():
            try:
                if self.service: self.service.close()
            except Exception as exc:
                self.stop_error = type(exc).__name__+": "+str(exc)
            finally:
                self.drained = True
        self.drained = False
        self.stop_error = None
        self.drain_thread = threading.Thread(target=drain, name="PE-drain")
        self.drain_thread.start()

    def poll(self):
        # A transient status/checkout error must not remove the next lifecycle tick.
        # In particular, closing a confirmation dialog runs a nested Tk event loop.
        destroyed = False
        try:
            if getattr(self, "updates", None) and not self.closing and not self.stop_failed:
                handoff = self.updates.poll()
                if self.updates.updates and self.updates.updates.enabled is not None:
                    self.update_status.set(self.updates.status)
                if self.ready_error: self.update_status.set(self.ready_error)
                if handoff: self.close(confirmed=True)
                self.refresh_update_controls()
            if self.closing and self.drained:
                if self.stop_error is not None:
                    self.closing = False; self.stop_failed = True
                    self.status.set("Beenden unvollständig: "+self.stop_error)
                    messagebox.showerror("Beenden unvollständig", self.stop_error+"\nEigene Restablage: "+str(self.service.work)+"\nNach Klärung erneut geordnet beenden.", parent=self.window)
                    return
                self.window.destroy(); destroyed = True; return
            if self.stop_failed: return
            if self.service and self.service.stopping and not self.closing: self.close(confirmed=True)
            if self.service and not self.closing:
                state = self.service.status()
                if state["job"] and state["job"]["state"] == "running":
                    self.status.set(self.service.origin+" · "+state["job"]["stage"]+" · "+str(state["job"]["elapsed_seconds"])+" s")
                elif state["recovery_required"]:
                    self.status.set("Recovery erforderlich · " + str(self.service.root))
                elif state["job"] and state["job"]["state"] == "error":
                    self.status.set("Fachoperation fehlgeschlagen · " + state["job"]["error"])
                else: self.status.set("Bereit · "+self.service.origin+" · "+str(self.service.root))
        except Exception as exc:
            self.status.set("Status konnte nicht gelesen werden: "+str(exc))
        finally:
            if not destroyed: self.window.after(250, self.poll)


def _main():
    load_ui()
    if getattr(sys, "frozen", False):
        try:
            from .bundle import verify
            verify()
        except Exception as exc:
            notice = tk.Tk(); notice.withdraw()
            messagebox.showerror("Programmpaket unvollständig", "Portable Ausgabe vollständig neu entpacken.\n"+str(exc), parent=notice)
            notice.destroy(); return
    parser = argparse.ArgumentParser(description="Lokaler Picross-Bestandseditor")
    parser.add_argument("--state", type=Path, default=Path(os.environ.get("LOCALAPPDATA", str(Path.home())))/"PicrossPuzzleEditor")
    parser.add_argument("--root"); parser.add_argument("--port", type=int)
    args = parser.parse_args()
    state = io.external(args.state)
    config = Settings(state).read()
    from .app_updates import restored_selection
    selection = restored_selection(args.root or config.get("checkout"), args.port if args.port is not None else config.get("port", 0))
    window = Window(state, selection["checkout"], selection["port"])
    error = None
    try:
        window.window.mainloop()
    except BaseException as exc:
        error = str(exc)
        raise
    finally:
        try:
            window.updates.stopping()
            if getattr(window, "drain_thread", None): window.drain_thread.join()
            if window.service and not getattr(window, "drained", False): window.service.close()
            if window.ready_thread: window.ready_thread.join()
            if window.window.winfo_exists(): window.window.destroy()
        except tk.TclError:
            pass  # Normal successful poll already destroyed the native window.
        except BaseException as exc:
            error = str(exc)
            raise
        finally:
            window.updates.finish(error or getattr(window, "stop_error", None))


def main():
    from tools.production_workspace.install_interlock import InstallInterlock
    interlock = InstallInterlock(app=PE)
    try:
        interlock.acquire()
        _main()
    finally:
        interlock.close()
