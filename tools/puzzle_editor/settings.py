"""Atomic program preferences, outside the selected content checkout."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import threading
import uuid

from tools.puzzle_production import catalog_io as io
from tools.puzzle_production.authoring_package import require

_lock = threading.RLock()


class Settings:
    def __init__(self, directory=None):
        self.directory = io.external(directory or Path(os.environ.get("LOCALAPPDATA", str(Path.home())))/"PicrossPuzzleEditor")

    def read(self):
        raw = io.read(self.directory, "config.json", 4096, missing=True)
        value = io.json_bytes(raw, 4096) if raw else {"checkout": "", "port": 0}
        require(isinstance(value, dict) and set(value) in ({"checkout", "port"}, {"checkout", "port", "theme"}), "Invalid editor settings")
        value.setdefault("theme", "light")
        require(isinstance(value["checkout"], str) and type(value["port"]) is int and 0 <= value["port"] <= 65535
                and value["theme"] in ("light", "dark"), "Invalid editor settings values")
        return value

    @contextmanager
    def locked(self):
        with _lock:
            self.directory.mkdir(parents=True, exist_ok=True)
            with io.safe(self.directory, ".settings.lock").open("a+b") as stream:
                if os.name == "nt":
                    import msvcrt
                    stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                try: yield
                finally:
                    if os.name == "nt":
                        stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                    else: fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def update(self, **changes):
        require(set(changes) <= {"theme", "checkout", "port"}, "Unknown editor setting")
        with self.locked():
            value = {**self.read(), **changes}
            require(value["theme"] in ("light", "dark") and isinstance(value["checkout"], str)
                    and type(value["port"]) is int and 0 <= value["port"] <= 65535, "Invalid editor setting")
            temporary = io.safe(self.directory, ".settings-"+uuid.uuid4().hex+".tmp")
            try:
                with temporary.open("xb") as stream:
                    stream.write((json.dumps(value, ensure_ascii=False)+"\n").encode()); stream.flush(); os.fsync(stream.fileno())
                os.replace(temporary, io.safe(self.directory, "config.json"))
            finally: temporary.unlink(missing_ok=True)
            return value
