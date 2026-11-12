"""Shared EXE/CMD lifecycle; data checkouts have no executable authority."""
import hashlib
import importlib
from io import BytesIO
import json
import os
from pathlib import Path
import secrets
import threading
import sys

from .instance import PROTOCOL, control, data

ROOT = Path(__file__).parent


def build_id():
    manifest = ROOT / 'build.json'
    if manifest.is_file():
        return json.loads(manifest.read_text(encoding='utf-8'))['commit']
    digest = hashlib.sha256()
    for file in sorted(ROOT.rglob('*')):
        if file.suffix in ('.py', '.js', '.css', '.html', '.ico') and '__pycache__' not in file.parts:
            digest.update(file.relative_to(ROOT).as_posix().encode())
            digest.update(file.read_bytes())
    return digest.hexdigest()


def preflight(gui=False):
    try:
        for module in ('presentation', 'repository', 'server', 'current_view', 'motifs'):
            importlib.import_module('tools.production_workspace.' + module)
        importlib.import_module('tools.puzzle_production.authoring_workflow')
        from PIL import Image, __version__
        if __version__ != '12.3.0':
            raise RuntimeError('Pillowversion')
        for fmt in ('PNG', 'JPEG'):
            stream = BytesIO()
            Image.new('RGB', (2, 2), (30, 90, 80)).save(stream, format=fmt)
            stream.seek(0)
            with Image.open(stream) as image:
                image.load()
                if image.size != (2, 2):
                    raise RuntimeError('Bilddekodierung')
        for name in ('index.html', 'app.js', 'workflow.js', 'style.css'):
            if not (ROOT / 'ui' / name).read_bytes():
                raise RuntimeError('UI-Ressource')
        manifest = ROOT / 'build.json'
        if manifest.exists():
            for name, expected in json.loads(manifest.read_text(encoding='utf-8'))['resources'].items():
                if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                    raise RuntimeError('Ressourcenbindung')
        if gui:
            import tkinter
            import tkinter.ttk
            # Actual Tcl initialization, not merely importability.
            interpreter = tkinter.Tcl()
            interpreter.eval('info patchlevel')
            if getattr(sys, 'frozen', False):
                for name in ('_tk_data/tk.tcl', '_tk_data/ttk/ttk.tcl'):
                    if not (Path(sys._MEIPASS) / name).is_file():
                        raise RuntimeError('Tk-Ressource fehlt')
    except Exception as exc:
        raise ValueError('Programmpaket unvollständig oder inkompatibel. Den gesamten App-Ordner neu entpacken; '
                         'im Entwicklerfallback die dokumentierte Python-/Pillowumgebung verwenden.') from exc
    from .sources import git
    try:
        git(ROOT, '--version')  # Also exercises the global --no-lazy-fetch option.
    except (ValueError, OSError) as exc:
        raise ValueError('Git fehlt oder unterstützt --no-lazy-fetch nicht. Aktuelles Git für Windows installieren '
                         'und den Starter erneut öffnen. Die bestehende Git-Anmeldung bleibt zuständig.') from exc


class PortConflict(ValueError):
    pass


class Runtime:
    def __init__(self, lock, build, *, no_browser=False):
        self.lock, self.build, self.no_browser = lock, build, no_browser
        self.server = self.service = self.thread = None
        self.open_requested, self.stop_requested, self.stopped = (threading.Event() for _ in range(3))
        self.stop_thread = None
        self.error = None

    def start(self, port=None):
        from .repository import Repository
        from .server import Server, Service
        address = self.lock.directory / 'address.json'
        if address.exists():
            value = json.loads(address.read_text(encoding='utf-8'))
            if set(value) != {'format', 'port'} or value['format'] != PROTOCOL or type(value['port']) is not int or not 1 <= value['port'] <= 65535:
                raise ValueError('Gespeicherte Launcheradresse ist ungültig. Eigenen Launcherzustand prüfen.')
            saved = value['port']
        else:
            saved = 0
        if port is not None and not 0 <= port <= 65535:
            raise ValueError('Port muss zwischen 0 und 65535 liegen.')
        self.service = Service(Repository(self.lock.state))
        try:
            self.server = Server(self.service, saved if port is None else port)
        except OSError as exc:
            raise PortConflict('Gespeicherter Port ist fremd belegt oder nicht verfügbar. Fremden Dienst regulär beenden '
                               'und wiederholen, oder ausdrücklich einen neuen Port wählen. Ein Portwechsel hat getrennte Browseroptionen/Entwürfe.') from exc
        self.metadata = {'protocol': PROTOCOL, 'build': self.build, 'instance': secrets.token_hex(24),
                         'key': secrets.token_urlsafe(32), 'port': self.server.server_address[1], 'pid': os.getpid()}
        self.server.lifecycle = self
        try:
            temporary = address.with_suffix('.tmp')
            temporary.write_bytes(data({'format': PROTOCOL, 'port': self.metadata['port']}))
            temporary.replace(address)
            self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.1}, name='PW-http')
            self.thread.start()
            self.lock.publish(self.metadata)
            control(self.metadata, 'identify')  # Authenticate our readiness before any browser opening.
        except BaseException:
            if self.thread:
                self.server.shutdown(); self.thread.join()
            self.server.server_close()
            raise

    def open(self):
        from .processes import open_browser
        control(self.metadata, 'identify')
        if not self.no_browser and not open_browser(self.server.origin + '/#' + self.service.secret):
            raise ValueError('Standardbrowser konnte nicht geöffnet werden. Windows-Standardbrowser einrichten und erneut öffnen.')

    def refresh(self):
        self.service.start_refresh()

    def request_stop(self):
        if self.stop_thread is not None:
            return
        self.stop_requested.set()
        self.service.begin_stop()
        self.stop_thread = threading.Thread(target=self._stop, name='PW-stop')
        self.stop_thread.start()

    def _stop(self):
        try:
            self.server.shutdown()
            self.thread.join()
            self.server.server_close()  # Joins actual requests, including a P2 transaction.
            if self.service.update_thread:
                self.service.update_thread.join()
            self.lock.close()
        except Exception:
            self.error = 'Beendigung nicht vollständig bestätigt. Instanzzustand und laufende eigene Arbeit prüfen.'
        finally:
            self.stopped.set()
