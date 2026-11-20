"""One opt-in startup operation, owned by the native GUI and its stop lifecycle."""
from tools.app_products import PG, PW
import threading
import subprocess

from . import update_client as client, update_windows as windows
from .update_storage import Preferences, Stage, recover
from .update_verifier import production_trust


class Updates:
    def __init__(self, runtime, *, app=PW, cancelled=None):
        self.runtime = runtime
        self.app = app
        self.app_args = {} if app == PW else {"app": app}
        self.cancelled = threading.Event() if cancelled is None else cancelled
        # GUI owns choose/start/cancel/take; the worker shares only the short
        # helper-spawn/publication transition. Never hold this over network I/O.
        self.transition = threading.Lock()
        self.thread = None
        self.handoff = None
        self.stage = None
        self.started = False
        self.taken = False
        self.status = 'App-Updates sind ausgeschaltet.'
        self.progress = None
        self.enabled = None
        self.identity = None
        self.preferences = None
        self.recovery_attempts = 0
        try:
            self.identity = windows.installation(**self.app_args)
            if runtime.lock.state.is_relative_to(self.identity.executable.parent):
                raise ValueError('Updatezustand muss außerhalb des installierten Programms liegen.')
            self.preferences = Preferences(runtime.lock.directory)
            try:
                self.enabled = self.preferences.read()
            except (ValueError, OSError):
                if app != PG:
                    raise
                self.status = 'Gespeicherte Updateentscheidung ungültig. Bitte erneut entscheiden.'
            previous = recover(runtime.lock.directory, **self.app_args)
            if previous:
                self.status = previous + ' Nächster automatischer Versuch erst nach erneutem Start.'
                self.started = True
            if not production_trust(**self.app_args)['accepted']:
                self.status = 'Updatekanal inaktiv: Vertrauensschlüssel fehlt. Erste vertrauenswürdige Version manuell installieren.'
                self.started = True
        except (ValueError, OSError, KeyError, TypeError):
            self.status = 'App-Updates in diesem Start nicht verfügbar. Installierte App und geschützten Updatezustand prüfen.'
            self.started = True

    def save_preference(self, enabled):
        if self.preferences is None or self.taken or self.runtime.stop_requested.is_set():
            return False
        try:
            self.preferences.write(enabled)
        except (ValueError, OSError):
            self.enabled = False
            self.status = 'Updateentscheidung konnte nicht sicher gespeichert werden. Automatik bleibt aus.'
            return False
        self.enabled = enabled
        return True

    def choose(self, enabled):
        if self.preferences is None or self.taken or self.runtime.stop_requested.is_set():
            return
        if not self.save_preference(enabled):
            self.cancel()
            return
        if not enabled:
            self.cancel()
            self.status = 'App-Updates ausgeschaltet. Ein laufender Download wird verworfen.'
        elif self.started:
            self.status = 'App-Updates aktiviert. Prüfung beim nächsten regulären Start; Kanal muss freigegeben sein.'
        else:
            self.start()

    def start(self):
        if (self.started or self.cancelled.is_set() or self.runtime.stop_requested.is_set() or
                self.enabled is not True or self.identity is None):
            return False
        self.started = True
        self.thread = threading.Thread(target=self._run, name=self.app.key.upper()+'-app-update')
        self.thread.start()
        return True

    @property
    def pending(self):
        with self.transition:
            # A worker can finish between take() and this read. A published
            # handoff must keep the gate closed until the next GUI take().
            return bool(not self.cancelled.is_set() and not self.taken and
                        (self.thread and self.thread.is_alive() or self.handoff))

    def report_progress(self, phase, received, total):
        # Publish a single immutable snapshot for the GUI thread.
        self.progress = (phase, received, total)

    def _run(self):
        try:
            self.status = 'Signierten App-Updatekanal prüfen …'
            metadata, assets = client.discover(self.identity.version, self.cancelled, installation=self.identity, **self.app_args)
            if self.cancelled.is_set():
                raise client.Cancelled()
            if metadata.version == self.identity.version:
                # Discovery checked signed publication identity, not MSI/EXE byte
                # equality. Re-read the actual installed/MSI context before status.
                if windows.installation(**self.app_args) != self.identity:
                    raise client.InstallationMismatch('Installed application changed during check')
                with self.transition:
                    if (self.cancelled.is_set() or self.preferences.read() is not True or
                            self.runtime.stop_requested.is_set()):
                        raise client.Cancelled()
                    self.status = 'Keine neuere Appversion veröffentlicht.'
                return
            self.stage = Stage(self.runtime.lock.directory)
            self.status = 'Geprüfte neuere Appversion herunterladen …'
            progress = {'progress': self.report_progress} if self.app == PG else {}
            candidate = client.download(metadata, assets, self.stage, self.cancelled, **self.app_args, **progress)
            if self.cancelled.is_set() or self.preferences.read() is not True or self.runtime.stop_requested.is_set():
                raise client.Cancelled()
            self.status = 'Vollständigen Kandidaten und unabhängigen Updatehelfer prüfen …'
            handoff = windows.prepare(candidate, self.stage, self.identity, self.runtime,
                                      cancelled=self.cancelled, transition=self.transition, **self.app_args)
            with self.transition:
                self.handoff = handoff
                if self.cancelled.is_set() or self.preferences.read() is not True or self.runtime.stop_requested.is_set():
                    handoff.abort()
                    raise client.Cancelled()
                self.status = ('Spiel-Update bereit …' if self.app == PG else
                               'App-Update bereit. Laufende Arbeit wird geordnet abgeschlossen …')
        except client.Cancelled:
            self.cancelled.set()
            self.status = 'App-Update abgebrochen; vorhandene App bleibt verfügbar.'
        except client.InstallationMismatch:
            self.cancel()
            self.status = ('App-Update nicht bestätigt: Installationsidentität passt nicht zum signierten Release. '
                           'Vorhandene App bleibt verfügbar; Installation prüfen.')
        except Exception:
            self.cancel()
            self.status = ('App-Update nicht möglich: Kanal, Signatur, Version, Download oder Übergabe nicht bestätigt. '
                           'Vorhandene App bleibt verfügbar; beim nächsten Start erneut prüfen oder manuell installieren.')
        finally:
            self.progress = None
            # A started helper owns its lifetime. Pending staging is recovered only
            # after its actual exit; never delete files from under an unknown child.
            if self.stage and self.stage.path.exists() and not (self.runtime.lock.directory / 'update-pending.json').exists():
                try:
                    self.stage.cleanup()
                except (OSError, ValueError):
                    self.status += ' Eigene Updateablage konnte noch nicht entfernt werden.'

    def take(self):
        with self.transition:
            if (self.thread and not self.thread.is_alive() and self.handoff and not self.taken and
                    not self.cancelled.is_set() and self.enabled is True and not self.runtime.stop_requested.is_set()):
                if self.app == PG:
                    try:
                        if self.preferences.read() is not True:
                            return None
                    except (ValueError, OSError):
                        return None
                self.taken = True
                return self.handoff
        return None

    def poll_result(self):
        # Bounded completion cleanup after restart, never a recurring update check.
        if self.recovery_attempts < 10:
            self.recovery_attempts += 1
            if not self.preferences or self.thread is not None:
                return
            try:
                result = recover(self.runtime.lock.directory, **self.app_args)
                if result:
                    self.status = result
            except (OSError, ValueError):
                pass  # The still-running helper may hold its exclusive stage lock.

    def cancel(self):
        with self.transition:
            if self.taken:
                return False  # The GUI now owns the drain/GO or explicit abort.
            self.cancelled.set()
            self.started = True  # Skip/opt-out cannot restart this attempt.
            if self.handoff:
                self.handoff.abort()
            return True

    def close(self):
        if not (self.handoff and self.handoff.committed):
            if self.taken:
                self.handoff.abort()
            else:
                self.cancel()
        if self.thread:
            self.thread.join()  # HTTP time/byte budgets bound exit; no detached downloader.
        if self.handoff and not self.handoff.committed:
            try:
                self.handoff.process.wait(timeout=5)
                recover(self.runtime.lock.directory, **self.app_args)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                pass
