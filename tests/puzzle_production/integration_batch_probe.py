"""One-time BA-B-T01 real CLI evidence, deliberately not a permanent CI job.

Run after the final clean product commit exists, using the pinned image Python:
  python -m tests.puzzle_production.integration_batch_probe --output-dir <empty-own-dir>

The private child entry invokes the actual CLI in a separate process. Its
instrumentation logs real native calls and can SIGKILL that same process after
a native publication or at an existing native transaction checkpoint. It never
stubs a success, manufactures a pending journal, or adds a product fault flag.
Only the six agreed text originals survive; generated PNGs/ZIPs/native bundles
are checked in the own temporary run and cleaned by its context manager.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time

from PIL import __version__ as pillow_version

from tests.puzzle_production.integration_batch_fixtures import (
    ROOT, checksum, encoded, stamps, walkthrough_fixture,
)


ARTIFACTS = ("batch-plan.json", "checkpoint.json", "report.json", "cli.log",
             "operations.jsonl", "manifest.json")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def append_event(path, event):
    # Preserve the actual native return before a deliberately unbooked SIGKILL.
    with Path(path).open("ab") as stream:
        stream.write(encoded(jsonable(event)))
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def own_native_temporaries(path):
    """Keep killed native-call temporaries inside the own disposable run."""
    path.mkdir()
    previous = tempfile.tempdir
    tempfile.tempdir = str(path)
    try:
        yield
    finally:
        tempfile.tempdir = previous


def refs(snapshot, root):
    return [{"root": root, "file": name, "bytes": len(raw), "sha256": checksum(raw),
             "mtime_ns": modified} for name, (raw, modified) in sorted(snapshot.items())]


def verify_retained(root, snapshot, *, except_names=()):
    for name, (raw, modified) in snapshot.items():
        if name in except_names:
            continue
        path = Path(root) / name
        require(path.is_file() and path.read_bytes() == raw and path.stat().st_mtime_ns == modified,
                "Original bytes or mtime changed: " + name)


def job(report, identifier):
    return next(row for row in report["jobs"] if row["job_id"] == identifier)


def child(argv):
    """Instrument real calls only inside this explicitly synthetic test process."""
    from tools.puzzle_production import catalog_background_change as background_change
    from tools.puzzle_production import catalog_publication, content_registry
    from tools.puzzle_production import operation_diagnostics, target_adapter
    from tools.puzzle_production import integration_batch_cli

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--fault", choices=("register-complete", "background-complete", "journal-complete", "P3"))
    parser.add_argument("--puzzle")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    options = parser.parse_args(argv)
    arguments = options.arguments
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    active_writer = None
    sequence = 0

    def record(event, **values):
        append_event(options.events, {"event": event, "pid": os.getpid(),
                                      "command": arguments[0], **values})

    def diagnostic():
        current = operation_diagnostics.current.get()
        return current.result() if current is not None else None

    def kill(boundary, **values):
        require(os.name == "posix", "The selected T01 hard-kill environment must be POSIX")
        record("SIGKILL", boundary=boundary, puzzle_id=options.puzzle,
               diagnostics=diagnostic(), **values)
        os.kill(os.getpid(), signal.SIGKILL)
        raise AssertionError("SIGKILL unexpectedly returned")

    def traced(module, name, label):
        original = getattr(module, name)

        @wraps(original)
        def call(*args, **kwargs):
            nonlocal active_writer, sequence
            sequence += 1
            number = sequence
            identifier = None
            if label == "registration":
                manifest = json.loads((Path(args[0]) / "manifest.json").read_bytes())
                identifier = manifest["definition_id"]
                if kwargs.get("apply") is True:
                    active_writer = identifier
            record("native_start", sequence=number, operation=label,
                   args=jsonable(args), kwargs=jsonable(kwargs), puzzle_id=identifier)
            started = time.monotonic()
            try:
                result = original(*args, **kwargs)
            except BaseException as exc:
                record("native_error", sequence=number, operation=label,
                       error={"type": type(exc).__name__, "message": str(exc)},
                       diagnostics=diagnostic(), elapsed_seconds=time.monotonic() - started)
                raise
            finally:
                if label == "registration":
                    active_writer = None
            extra = {}
            if label == "background_plan":
                # The native result is compact; retain the actual complete text
                # plan as well, without copying any bundled image bytes.
                extra["plan"] = json.loads((Path(args[2]) / "plan.json").read_bytes())
            record("native_return", sequence=number, operation=label, native=result,
                   diagnostics=diagnostic(), elapsed_seconds=time.monotonic() - started, **extra)
            if (options.fault == "register-complete" and label == "registration"
                    and kwargs.get("apply") is True and identifier == options.puzzle
                    and result.get("status") == "registered"):
                kill("native-register-return-before-batch-booking", native=result)
            if (options.fault == "background-complete" and label == "background_adopt"
                    and result.get("puzzle_id") == options.puzzle and result.get("status") == "adopted"):
                kill("native-adopt-return-before-batch-booking", native=result)
            return result

        setattr(module, name, call)

    for module, name, label in ((target_adapter, "export", "export"),
                                (content_registry, "registration", "registration"),
                                (background_change, "store", "background_store"),
                                (background_change, "plan", "background_plan"),
                                (background_change, "adopt", "background_adopt")):
        traced(module, name, label)
    original_checkpoint = catalog_publication.checkpoint

    def checkpoint(phase, name=None):
        original_checkpoint(phase, name)
        if options.fault == phase and active_writer == options.puzzle:
            kill("native-" + phase, native_target=name)

    catalog_publication.checkpoint = checkpoint
    return integration_batch_cli.main(arguments)


class CliProbe:
    def __init__(self, fixture, operations):
        self.fixture = fixture
        self.operations = operations
        self.log = []
        self.environment = dict(os.environ)
        temporary = str(fixture.root.parent / "native-temporary")
        self.environment.update(TMPDIR=temporary, TEMP=temporary, TMP=temporary)

    def arguments(self, command):
        args = [command, "--work-root", str(self.fixture.work)]
        if command != "status":
            args += ["--plan", str(self.fixture.path), "--source-root", str(self.fixture.source),
                     "--repo-root", str(self.fixture.repo), "--target-root", str(self.fixture.target)]
        return args

    def invoke(self, command, exits, *, fault=None, puzzle=None):
        argv = [sys.executable, "-m", __name__ if __name__ != "__main__" else
                "tests.puzzle_production.integration_batch_probe", "_child", "--events", str(self.operations)]
        if fault is not None:
            argv += ["--fault", fault, "--puzzle", puzzle]
        argv += ["--", *self.arguments(command)]
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=180, check=False,
                                env=self.environment)
        response = None
        if result.stdout:
            try:
                response = json.loads(result.stdout)
            except (ValueError, UnicodeDecodeError) as exc:
                raise RuntimeError("CLI did not return one JSON response: " + result.stdout.decode(errors="replace")) from exc
        self.log.append({"event": "cli", "argv": argv, "exit_code": result.returncode,
                         "stdout": response, "stdout_bytes": len(result.stdout),
                         "stdout_sha256": checksum(result.stdout),
                         "stderr": result.stderr.decode("utf-8", errors="replace")})
        rows = (response or {}).get("jobs", [])
        rows = rows if isinstance(rows, list) else []
        detail = {"exit_code": result.returncode, "status": (response or {}).get("status"),
                  "error": (response or {}).get("error"),
                  "jobs": [{key: value.get(key) for key in ("job_id", "status", "reason")}
                           for value in rows],
                  "stderr": result.stderr.decode("utf-8", errors="replace")[-4096:]}
        require(result.returncode in exits, "Unexpected CLI exit: " + json.dumps(detail, ensure_ascii=False))
        if fault is not None:
            require(result.returncode == -signal.SIGKILL, "Requested process was not actually SIGKILLed")
            checkpoint = json.loads((self.fixture.work / "checkpoint.json").read_bytes())
            pending = [a["reservation"] for a in checkpoint["attempts"] if a["result"] is None]
            latest = checkpoint["attempts"][-1]
            reservation = latest["reservation"]
            require(latest["result"] is None and reservation["puzzle_id"] == puzzle
                    and reservation["phase"] == ("adopt" if fault == "background-complete" else "apply"),
                    "No matching durably consumed unbooked attempt after actual process kill")
            saved = self.fixture.work / "attempts" / f"{reservation['number']:06d}" / "reservation.json"
            require(json.loads(saved.read_bytes()) == reservation, "Checkpoint reservation differs from its original ledger")
            self.log.append({"event": "durable_interruption", "fault": fault, "puzzle_id": puzzle,
                             "observed_latest": reservation, "unbooked_reservations": pending})
            return checkpoint
        require(response is not None, "Normal CLI returned no JSON")
        return response

    def recover(self):
        argv = [sys.executable, "-m", "tools.puzzle_production.target_adapter", "recover-registration",
                "--checkout", str(self.fixture.target)]
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=120, check=False,
                                env=self.environment)
        response = json.loads(result.stdout)
        self.log.append({"event": "explicit_native_recovery", "argv": argv, "exit_code": result.returncode,
                         "stdout": response, "stderr": result.stderr.decode("utf-8", errors="replace")})
        append_event(self.operations, {"event": "explicit_native_recovery", "native": response,
                                       "exit_code": result.returncode})
        require(result.returncode == 0 and response.get("status") == "rolled-back", "Explicit native recovery did not finish")
        return response


def run_probe(output, *, development=False, product_commit=None):
    from tools.puzzle_production import catalog_background, catalog_publication, catalog_transaction, content_registry
    output = Path(output).absolute()
    require(output.is_dir() and not output.is_symlink() and not list(output.iterdir()),
            "Evidence output must be an explicitly selected empty directory")
    require(os.name == "posix", "The selected actual SIGKILL probe requires POSIX")
    require(pillow_version == "12.3.0", "Use the pinned Pillow 12.3.0 environment")
    head = git("rev-parse", "HEAD")
    require(product_commit is None or product_commit == head, "Explicit product commit differs from actual HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=all"))
    require(development or not dirty, "Final T01 requires the committed clean product tree; --development is provisional only")
    real_data_before = git("status", "--porcelain", "--untracked-files=all", "--", "content", "game")
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="ba-b-t01-owned-", dir=output.parent) as temporary, \
            own_native_temporaries(Path(temporary) / "native-temporary"):
        home = Path(temporary)
        fixture = walkthrough_fixture(home / "fixture")
        operations = home / "operations.jsonl"
        append_event(operations, {"event": "native_fixture_preparation",
                                   "purpose": "Own synthetic prerequisites prepared before BA-B; not runner analysis or activation",
                                   "activation": fixture.activation,
                                   "existing_registration": fixture.existing_registration,
                                   "checked_difficulty": [{"puzzle_id": value["id"],
                                                           "native": json.loads(value["difficulty_path"].read_bytes())}
                                                          for value in fixture.packages.values()]})
        cli = CliProbe(fixture, operations)
        originals = stamps(fixture.source)
        validation = cli.invoke("validate", {0})
        require(validation.get("status") == "valid", "Original integration plan did not validate")

        cli.invoke("run", {-signal.SIGKILL}, fault="register-complete", puzzle="pz-ba-b-selected")
        require(not (fixture.target / catalog_transaction.LOCK).exists(), "Published register retained a pending journal")
        cli.invoke("resume", {-signal.SIGKILL}, fault="background-complete", puzzle="pz-ba-b-existing")
        require(not (fixture.target / catalog_transaction.LOCK).exists(), "Published background retained a pending journal")
        prefix = stamps(fixture.target, control=False)

        for fault, expected in (("journal-complete", "staging"), ("P3", "pending")):
            cli.invoke("resume", {-signal.SIGKILL}, fault=fault, puzzle="pz-ba-b-none")
            require(bool(catalog_publication.staging(fixture.target)) if expected == "staging" else
                    (fixture.target / catalog_transaction.LOCK).is_file(), "Real native interrupted state was not retained")
            interrupted = stamps(fixture.target, control=False)
            stopped = cli.invoke("resume", {3})
            require(job(stopped, "none")["status"] == "recovery_required", "Resume did not report explicit native recovery")
            require(stamps(fixture.target, control=False) == interrupted, "Stopped resume changed pending native bytes")
            verify_retained(fixture.target, prefix)
            cli.recover()
            require(stamps(fixture.target, control=False) == prefix, "Recovery did not preserve the exact prior prefix")

        final = cli.invoke("resume", {0})
        require(final["status"] == "completed", "Final resume did not complete all three jobs")
        require(all(row["historical_completed"] and row["current_verified"] for row in final["jobs"]),
                "Final report does not distinguish current confirmation from historical success")
        verify_retained(fixture.target, prefix,
                        except_names=(catalog_transaction.REGISTRY, catalog_transaction.RUNTIME))
        verify_retained(fixture.source, originals)
        before_noop = stamps(fixture.target, control=False)
        events_before = operations.read_bytes().count(b"\n")
        final = cli.invoke("resume", {0})
        require(stamps(fixture.target, control=False) == before_noop, "Final resume rewrote unchanged target bytes or mtimes")
        new_events = [json.loads(line) for line in operations.read_bytes().splitlines()[events_before:]]
        require(not any(row.get("operation") == "background_adopt" for row in new_events),
                "Booked background was incorrectly re-adopted against its stale full-catalog plan")
        verified_registry = content_registry.check_checkout(fixture.target, replay=True)
        active_method = json.loads((fixture.target / "content/difficulty-method.json").read_bytes())
        require(active_method["method"] == "picross-difficulty-0.4", "The synthetic target lost its actual active 0.4 method")
        require({row["id"] for row in verified_registry["entries"]} ==
                {"pz-ba-b-selected", "pz-ba-b-existing", "pz-ba-b-none"},
                "The actual final native reader did not confirm the three synthetic targets")
        outcomes = []
        for identifier, outcome in (("pz-ba-b-selected", "selected"), ("pz-ba-b-none", "none"),
                                    ("pz-ba-b-existing", "selected")):
            entry = next(row for row in verified_registry["entries"] if row["id"] == identifier)
            source = catalog_background.load(fixture.target, verified_registry, entry)
            active = catalog_background.current(source)
            require(active["decision"]["outcome"] == outcome, "Final background choice differs from the approved original")
            require((active["asset"] is None) == (outcome == "none"), "Explicit none produced an active PNG")
            if outcome == "none":
                require(not (fixture.target / catalog_background.asset_path(identifier)).exists(),
                        "Explicit none left a background image in the target")
            if identifier == "pz-ba-b-existing":
                require(active["image_revision"] == 2 and active["adoption"]["revision"] == "bg-r01",
                        "The final source does not bind the actual new background revision")
            outcomes.append({"puzzle_id": identifier, "outcome": outcome,
                             "image_revision": active["image_revision"], "asset": active["asset"]})
        append_event(operations, {"event": "final_native_catalog_reader", "native": verified_registry,
                                   "active_method": active_method})
        before_status = stamps(fixture.work)
        historical = cli.invoke("status", {3})
        require(historical["fresh"] is False and stamps(fixture.work) == before_status,
                "Historical status mutated work or claimed a fresh target check")
        verify_retained(fixture.source, originals)
        require(git("status", "--porcelain", "--untracked-files=all", "--", "content", "game") == real_data_before,
                "Probe changed real product content/game data")

        # Include the complete durable native results and RI objects, even where
        # the current-prefix reader intentionally does not call an old writer.
        for attempt in final["attempts"]:
            append_event(operations, {"event": "durable_attempt", **attempt})
        native_events = [json.loads(line) for line in operations.read_bytes().splitlines()]
        registrations = [row for row in native_events if row["event"] == "native_return"
                         and row.get("operation") == "registration" and row["native"].get("status") == "registered"]
        require(len(registrations) == 2, "Resume performed an unexpected successful mutating registration")
        kills = [row for row in native_events if row["event"] == "SIGKILL"]
        require(len(kills) == 4, "Missing one of the four actual process boundary interruptions")
        require(final["execution_seconds"] is None and final["elapsed_seconds"] is None
                and final["human_seconds"] is None and final["waiting_seconds"] is None,
                "Unknown crash or human intervals were reported as measured durations")
        plans = [row["native"] for row in native_events if row["event"] == "native_return"
                 and row.get("operation") == "registration" and row["native"].get("status") == "planned"]
        require(any(value["id"] == "pz-ba-b-none" and
                    "pz-ba-b-selected" in {entry["id"] for entry in value["before"]["entries"]}
                    for value in plans), "The later fresh native plan did not see the earlier registration")
        files = {"batch-plan.json": fixture.path.read_bytes(),
                 "checkpoint.json": (fixture.work / "checkpoint.json").read_bytes(),
                 "report.json": (fixture.work / "report.json").read_bytes(),
                 "cli.log": b"".join(encoded(row) for row in cli.log),
                 "operations.jsonl": operations.read_bytes()}
        require(json.loads(files["report.json"]) == final, "Final CLI and disk report originals differ")
        manifest = {"format": "picross-ba-b-t01-evidence-v1", "test_only": True,
                    "product_commit": head, "test_commit": head, "source_dirty": dirty,
                    "provisional": development, "started_utc": started,
                    "finished_utc": datetime.now(timezone.utc).isoformat(),
                    "environment": {"platform": platform.platform(), "python": sys.version,
                                    "pillow": pillow_version, "executable": sys.executable},
                    "artifact_names": list(ARTIFACTS),
                    "files": [{"file": name, "bytes": len(raw), "sha256": checksum(raw)}
                              for name, raw in sorted(files.items())],
                    "scenarios": ["actual approved test_only selected and none ZIPs with checked active 0.4 difficulty",
                                  "sequential native registration plans see the successful predecessor",
                                  "native registration return then actual SIGKILL before batch booking",
                                  "native authorized store-plan-adopt return then actual SIGKILL before booking",
                                  "actual staging stop, unchanged resume rejection, separate native recovery",
                                  "actual pending-journal stop, unchanged resume rejection, separate native recovery",
                                  "background success before later successful registration and final fresh resume",
                                  "original byte/mtime retention and no-op target byte/mtime identity",
                                  "historical status has fresh=false; real product content/game unchanged"],
                    "process_interruptions": [{key: row.get(key) for key in ("boundary", "puzzle_id", "pid")} for row in kills],
                    "verified_background_outcomes": outcomes,
                    "active_difficulty_method": active_method["method"],
                    "original_files": refs(originals, "source"),
                    "successful_prefix_files": refs(prefix, "target"),
                    "final_noop_files": refs(before_noop, "target"),
                    "final_status": final["status"], "retained_generated_images_or_zips": False,
                    "owner_or_game_acceptance": False}
        files["manifest.json"] = encoded(manifest)
        for name in ARTIFACTS:
            with (output / name).open("xb") as stream:
                stream.write(files[name])
        require({path.name for path in output.iterdir()} == set(ARTIFACTS), "Unexpected retained evidence file")
    return manifest


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "_child":
        return child(argv[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--product-commit")
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_probe(args.output_dir, development=args.development, product_commit=args.product_commit)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"status": "verified", "product_commit": result["product_commit"],
                      "provisional": result["provisional"], "files": list(ARTIFACTS),
                      "final_batch_status": result["final_status"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
