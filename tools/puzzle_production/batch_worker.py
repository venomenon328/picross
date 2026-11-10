"""Private finite BA-A worker. Only the closed in-process adapter allowlist runs."""
from __future__ import annotations

from pathlib import Path
from contextlib import contextmanager
import math
import os
import sys
import threading
import time

from . import batch_io as bio, batch_operations as operations, catalog_io as io
from .contract import Aborted, canonical_bytes, exact_keys


@contextmanager
def lifetime(parent_pid, seconds):
    """A parent's hard exit cannot release a still-running worker into a new run."""
    bio.require(type(parent_pid) is int and parent_pid > 0 and type(seconds) in (int, float)
                and math.isfinite(seconds) and seconds > 0, "Invalid worker lifetime")
    handle, kernel = None, None
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x00100000, False, parent_pid)
        bio.require(bool(handle), "Original parent process is unavailable")
        alive = lambda: kernel.WaitForSingleObject(handle, 0) == 0x00000102
    else:
        alive = lambda: os.getppid() == parent_pid
    stopped = threading.Event()
    deadline = time.monotonic() + seconds
    def watch():
        while not stopped.is_set():
            if not alive() or time.monotonic() >= deadline:
                os._exit(4)  # OS closes the worker lock; incomplete own output stays visible.
            stopped.wait(0.05)
    bio.require(alive(), "Original parent process has ended")
    watcher = threading.Thread(target=watch, name="batch-lifetime", daemon=True)
    watcher.start()
    try:
        yield alive
    finally:
        stopped.set()
        watcher.join(timeout=1)
        if handle:
            kernel.CloseHandle(handle)


def main():
    try:
        raw = sys.stdin.buffer.read(bio.MAX_JSON + 1)
        payload = bio.json_bytes(raw, bio.MAX_JSON)
        exact_keys(payload, {"format", "stage", "inputs", "decisions", "output_root", "repo_root",
                             "source_root", "history_root", "saved_result", "work_root", "parent_pid", "seconds"})
        bio.require(payload["format"] == "picross-batch-worker-v1", "Unknown worker transport")
        repo, source, output = (bio.external(payload[key]) for key in ("repo_root", "source_root", "output_root"))
        history = bio.external(payload["history_root"]) if payload["history_root"] else None
        stage = payload["stage"]
        operations.validate_operation(stage, repo)
        spec = operations.OPERATION_SPECS[(stage["kind"], stage["operation"])]
        exact_keys(payload["inputs"], set(spec["inputs"]))
        exact_keys(payload["decisions"], {"motif", "parameters", "repair", "background"})
        inputs = {key: io.external(value) if value is not None else None for key, value in payload["inputs"].items()}
        decisions = {key: io.external(value) if value is not None else None for key, value in payload["decisions"].items()}
        work = bio.external(payload["work_root"])
        bio.require(output.is_relative_to(work / "attempts"), "Worker output has no owned attempt")
        with lifetime(payload["parent_pid"], payload["seconds"]) as alive, bio.writer(work, name=".batch-worker.lock"):
            bio.require(alive(), "Original parent ended before operation")
            if payload["saved_result"] is None:
                result = operations.execute_operation(stage, inputs, output, repo, source, history,
                                                      decisions=decisions)
            else:
                operations.validate_result(payload["saved_result"])
                result = operations.revalidate_operation(stage, inputs, payload["saved_result"], output,
                                                         repo, source, history, decisions=decisions)
        operations.validate_result(result)
        response = {"result": result, "error": None, "aborted": False}
    except Aborted as exc:
        response = {"result": None, "error": str(exc)[:4096], "aborted": True}
    except Exception as exc:
        response = {"result": None, "error": type(exc).__name__ + ": " + str(exc)[:4000], "aborted": False}
    raw = canonical_bytes(response) + b"\n"
    bio.require(len(raw) <= bio.MAX_JSON, "Worker response exceeds bounded transport")
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
