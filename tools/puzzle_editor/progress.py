"""Operation observations, kept outside content/plan/journal identities."""
import os
import time

from tools.puzzle_production import operation_diagnostics as diagnostic
from tools.puzzle_production import catalog_io as io, catalog_transaction as tx


class Progress(diagnostic.Diagnostics):
    def __init__(self, action, directory):
        super().__init__(action)
        self.directory = directory
        self.segment = None
        self.last_update = 0
        self.last_stage = None
        self.cpu_started = time.process_time()

    def begin_segment(self, name):
        self.segment = name
        self.emit(force=True)

    def stage(self):
        return "/".join(filter(None, (self.segment, diagnostic.phase_path(self)))) or self.command

    def emit(self, *, event="progress", force=False):
        now, stage = time.monotonic(), self.stage()
        if not force and now - self.last_update < .25:
            return
        self.last_update, self.last_stage = now, stage
        # Own process-private directory; atomic replacement lets status polling
        # observe complete records. No content access or budget renewal here.
        import json
        value = {"stage": stage, "elapsed_seconds": round(now-self.started, 3)}
        temporary = self.directory / "progress.tmp"
        try:
            temporary.write_text(json.dumps(value)+"\n", encoding="utf-8")
            os.replace(temporary, self.directory / "progress.json")
        except OSError:
            # Telemetry cannot abort a guarded publication or rollback.
            pass

    def summary(self):
        return {"stage": self.last_stage or self.stage(),
                "wall_seconds": round(time.monotonic()-self.started, 6),
                "cpu_seconds": round(time.process_time()-self.cpu_started, 6),
                "budget_seconds": 300,
                "phases": [{**row, "seconds": round(row["seconds"], 6)} for row in self.phases.values()],
                "counters": dict(self.counters)}


def state(root):
    """A cheap diagnostic observation, never permission to write/recover."""
    from .server import pending
    try:
        recovery = pending(root)
    except Exception:
        return "Zustand unbekannt; Quellen/Journal prüfen"
    if recovery:
        return "recovery_required; Journal/Staging erhalten"
    try:
        raw = io.read(root, tx.RUNTIME, 8*1024*1024)
        value = io.json_bytes(raw, 8*1024*1024)
        version = value.get("format")
        if version not in ("picross-runtime-registry-v7", "picross-runtime-registry-v8"):
            version = "unbekannt"
    except Exception:
        version = "unbekannt"
    return "Runtime " + version + "; kein Journal/Staging"


def public_error(error, root, directory):
    from .server import CODE
    text = str(error)
    # Only selected program/data/work roots can occur in these workers. Preserve
    # relative source names while removing private absolute locations.
    for path, label in ((directory.parent, "<Arbeitsdaten>"), (root, "<Checkout>"), (CODE, "<Programm>")):
        text = text.replace(str(path), label).replace(path.as_posix(), label)
    return text[:1400]
