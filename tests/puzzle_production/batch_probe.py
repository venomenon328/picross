"""One-time BA-A-T01 CLI evidence; deliberately absent from permanent CI jobs.

Run with the pinned image environment after the reviewed product commit exists:
  python -m tests.puzzle_production.batch_probe --output-dir <empty-own-dir>

Only the six agreed JSON/log originals survive. Generated images, source inputs,
proof workspaces and local ZIPs live in an owned TemporaryDirectory. This is a
synthetic development probe, not a real content or owner-approval workflow.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

from tools.puzzle_production.contract import load_json
from tests.puzzle_production.batch_fixtures import (
    METHOD, ROOT, artifact_path, checksum, encoded, stage_result, stamps, walkthrough_fixture,
)


ARTIFACTS = ("plan-initial.json", "plan-resume.json", "checkpoint.json", "report.json", "cli.log", "manifest.json")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def compact(report):
    attempts = {a["number"]: a for a in report.get("attempts", [])}
    states = []
    for job in report.get("jobs", []):
        for stage in job["stages"]:
            attempt = attempts.get(stage["attempt"], {})
            result = attempt.get("result") or {}
            states.append({"job": job["job_id"], "stage": stage["stage_id"], "status": stage["status"],
                           "attempt": stage["attempt"], "reused": stage["reused"], "reason": stage["reason"],
                           "domain": result.get("domain"), "certified": result.get("certified")})
    return {"status": report.get("status"), "states": states,
            "attempts": len(attempts), "human_seconds": report.get("human_seconds")}


class CliProbe:
    def __init__(self, fixture):
        self.fixture = fixture
        self.log = []

    def argv(self, command):
        args = [sys.executable, "-m", "tools.puzzle_production.batch_cli", command,
                "--work-root", str(self.fixture.work)]
        if command != "status":
            args += ["--plan", str(self.fixture.path), "--source-root", str(self.fixture.source), "--repo-root", str(ROOT)]
        return args

    def event(self, name, **values):
        self.log.append({"event": name, **values})

    def invoke(self, command, exits):
        argv = self.argv(command)
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=120, check=False)
        try:
            response = json.loads(result.stdout)
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError("CLI did not return one JSON response: " + result.stderr.decode(errors="replace")) from exc
        report = response.get("report", response)
        self.event("cli", argv=argv, exit_code=result.returncode,
                   stdout_bytes=len(result.stdout), stdout_sha256=checksum(result.stdout),
                   stderr=result.stderr.decode("utf-8", errors="replace"), fresh=response.get("fresh"),
                   result=compact(report) if "jobs" in report and isinstance(report["jobs"], list) else response)
        require(result.returncode in exits, "Unexpected CLI exit: " + json.dumps(response, ensure_ascii=False))
        return response

    def hard_interruption(self):
        require(os.name == "posix", "T01 hard process-group interruption requires the selected POSIX test environment")
        argv = self.argv("run")
        process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
        checkpoint = None
        observed = None
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline and process.poll() is None:
                path = self.fixture.work / "checkpoint.json"
                if path.is_file():
                    checkpoint = json.loads(path.read_bytes())
                    running = [a for a in checkpoint["attempts"] if a["status"] == "running"]
                    if running:
                        observed = running[-1]
                        reservation = self.fixture.work / "attempts" / f"{observed['number']:06d}" / "reservation.json"
                        require(reservation.is_file(), "Running attempt was not durably reserved")
                        require(load_json(reservation)["fingerprint"] == observed["fingerprint"],
                                "Reservation/checkpoint mismatch at actual interruption")
                        os.killpg(process.pid, signal.SIGKILL)
                        break
                time.sleep(0.005)
            stdout, stderr = process.communicate(timeout=10)
            require(observed is not None, "No durable running attempt observed before process exit")
            require(process.returncode == -signal.SIGKILL, "Process was not actually killed by SIGKILL")
            self.event("hard_interruption", argv=argv, exit_code=process.returncode,
                       signal="SIGKILL", observed_attempt=observed["number"],
                       attempt_type=observed["attempt_type"], reserved_limits=observed["reserved_limits"],
                       checkpoint_status=observed["status"], stdout_bytes=len(stdout),
                       stdout_sha256=checksum(stdout), stderr=stderr.decode("utf-8", errors="replace"))
            return observed["number"]
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=10)


def protected_files(fixture, report):
    result = []
    for job_id, stage_id in (("selected", "import"), ("selected", "solve"),
                              ("selected", "difficulty"), ("waiting", "solve")):
        state, attempt = stage_result(report, job_id, stage_id)
        require(state["status"] == "completed", "Expected successful protected stage: " + job_id + "/" + stage_id)
        root = fixture.work / attempt["output_dir"]
        for name, (raw, modified) in stamps(root).items():
            result.append({"job_id": job_id, "stage_id": stage_id,
                           "file": (root / name).relative_to(fixture.work).as_posix(),
                           "bytes": len(raw), "sha256": checksum(raw), "mtime_ns": modified})
    return result


def verify_protected(fixture, refs):
    for ref in refs:
        path = fixture.work / ref["file"]
        raw = path.read_bytes()
        require(len(raw) == ref["bytes"] and checksum(raw) == ref["sha256"] and path.stat().st_mtime_ns == ref["mtime_ns"],
                "Unchanged branch was rewritten: " + ref["file"])


def produce_counts(report):
    counts = {}
    for attempt in report["attempts"]:
        if attempt["attempt_type"] == "produce":
            key = attempt["job_id"] + "/" + attempt["stage_id"]
            counts[key] = counts.get(key, 0) + 1
    return counts


def run_probe(output, *, development=False, product_commit=None):
    output = Path(output).absolute()
    require(output.is_dir() and not output.is_symlink() and not list(output.iterdir()),
            "Evidence output must be an explicitly selected empty directory")
    head = git("rev-parse", "HEAD")
    require(product_commit is None or product_commit == head, "Explicit product commit differs from actual checkout HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=all"))
    require(development or not dirty, "Final T01 originals require the committed clean product tree; use --development only for a provisional trial")
    repository_data_before = git("status", "--porcelain", "--untracked-files=all", "--", "content", "game")
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="ba-a-t01-owned-") as temporary:
        fixture = walkthrough_fixture(Path(temporary))
        cli = CliProbe(fixture)
        validation = cli.invoke("validate", {0})
        require(validation["status"] == "valid" and validation["jobs"] >= 3, "Initial CLI plan did not validate three jobs")
        interrupted_number = cli.hard_interruption()
        initial = cli.invoke("resume", {3})
        require(initial["status"] == "incomplete", "Open input/human gates disappeared")
        crashed = next(a for a in initial["attempts"] if a["number"] == interrupted_number)
        require(crashed["status"] == "interrupted" and crashed["seconds"] is None,
                "Hard interruption was not recorded with consumed attempt and unknown time")
        require(stage_result(initial, "none", "build")[0]["status"] == "waiting_input", "Missing original build request was fabricated")
        require(stage_result(initial, "waiting", "background")[0]["status"] == "waiting_human", "Open background decision was fabricated")
        _, solved = stage_result(initial, "selected", "solve")
        require(solved["result"]["certified"] is True, "Tiny original raster was not independently certified")
        _, difficulty = stage_result(initial, "selected", "difficulty")
        checked = load_json(artifact_path(fixture, difficulty["result"]["slots"]["checked_difficulty"]))
        require(checked["rating"]["method"] == METHOD and checked["production_mode"] == "mono", "Wrong rating method/mode")
        _, selected_bg = stage_result(initial, "selected", "background")
        _, none_bg = stage_result(initial, "none", "background")
        require("background_png" in selected_bg["result"]["slots"], "Selected background has no actual PNG")
        require("background_png" not in none_bg["result"]["slots"], "None background incorrectly produced a PNG")
        original_counts = produce_counts(initial)

        # Alter a real intermediate proof, then execute another real CLI resume.
        proof = artifact_path(fixture, solved["result"]["slots"]["proof"])
        original_proof = proof.read_bytes()
        damaged = json.loads(original_proof)
        damaged["logic_hash"] = "0" * 64
        proof.write_bytes(encoded(damaged))
        tampered_sha = checksum(proof.read_bytes())
        tampered = cli.invoke("resume", {3})
        state, failed = stage_result(tampered, "selected", "solve")
        require(state["status"] == "failed" and failed is not None, "Tampered proof was not rejected")
        require(stage_result(tampered, "selected", "difficulty")[0]["status"] == "blocked", "Dependent rating consumed the invalid proof")
        require(checksum(proof.read_bytes()) == tampered_sha, "Runner rewrote the damaged original")
        proof.write_bytes(original_proof)
        cli.event("tampering_detected_and_original_restored", file=proof.relative_to(fixture.work).as_posix(),
                  original_sha256=checksum(original_proof), tampered_sha256=tampered_sha,
                  failed_attempt=failed["number"], failure=state["reason"],
                  restored_sha256=checksum(proof.read_bytes()))

        # The successor simultaneously supplies an actual new image decision for
        # one job and the complete, explicit delayed build request of another.
        # No hidden intermediate plan revision or builder-request generator runs
        # inside the product runner.
        selected, none, _ = fixture.plan["jobs"]
        finding = artifact_path(fixture, none_bg["result"]["slots"]["background_finding"])
        build_ref = fixture.builder_request(none, finding=finding)
        none["stages"][-1]["inputs"]["request"] = build_ref
        background_ref = fixture.background(selected, revision="bg02", color=(20, 90, 180, 128))
        selected["stages"][-1]["inputs"]["request"] = background_ref
        protected = protected_files(fixture, initial)
        fixture.successor()
        final = cli.invoke("resume", {3})
        require(final["status"] == "incomplete", "The remaining actual human gate must still be visible")
        verify_protected(fixture, protected)
        final_counts = produce_counts(final)
        for key in ("selected/import", "selected/solve", "selected/difficulty", "waiting/solve"):
            require(final_counts[key] == original_counts[key], "Image-only change repeated unchanged logical production: " + key)
        require(final_counts["selected/background"] == original_counts["selected/background"] + 1,
                "Changed actual background source did not produce a new derivative")
        state, built = stage_result(final, "none", "build")
        require(state["status"] == "completed" and built["result"]["domain"] == "built", "Explicit later local build did not finish")
        package = artifact_path(fixture, built["result"]["slots"]["package"])
        handoff = load_json(artifact_path(fixture, built["result"]["slots"]["handoff"]))
        record = load_json(artifact_path(fixture, built["result"]["slots"]["record"]))
        require(handoff["gates"]["final_editorial"] == "pending" and handoff["gates"]["target_export"] == "blocked"
                and record["integration"] is None, "Local builder created an outer approval or integration")
        require(stage_result(final, "waiting", "background")[0]["status"] == "waiting_human", "Actual human gate was lost")
        before_status = stamps(fixture.work)
        historical = cli.invoke("status", {3})
        require(historical["fresh"] is False and stamps(fixture.work) == before_status, "Status mutated or freshly certified historical work")
        require(git("status", "--porcelain", "--untracked-files=all", "--", "content", "game") == repository_data_before,
                "The probe changed real content/game data")

        cli.event("image_only_change_preserved_originals", protected_files=protected,
                  produce_counts_before=original_counts, produce_counts_after=final_counts,
                  new_background_request=background_ref)
        cli.event("late_explicit_local_build", request=build_ref,
                  package={"file": package.relative_to(fixture.work).as_posix(), "bytes": package.stat().st_size,
                           "sha256": checksum(package.read_bytes())},
                  final_editorial=handoff["gates"]["final_editorial"], target_export=handoff["gates"]["target_export"])
        files = {"plan-initial.json": (fixture.root / "plan-initial.json").read_bytes(),
                 "plan-resume.json": (fixture.root / "plan-resume.json").read_bytes(),
                 "checkpoint.json": (fixture.work / "checkpoint.json").read_bytes(),
                 "report.json": (fixture.work / "report.json").read_bytes(),
                 "cli.log": b"".join(encoded(event) for event in cli.log)}
        require(json.loads(files["report.json"]) == final, "CLI final report and original disk report differ")
        manifest = {"format": "picross-ba-a-t01-evidence-v1", "test_only": True,
                    "product_commit": head, "test_commit": head, "source_dirty": dirty,
                    "provisional": development, "started_utc": started,
                    "finished_utc": datetime.now(timezone.utc).isoformat(),
                    "python": sys.version.split()[0], "artifact_names": list(ARTIFACTS),
                    "files": [{"file": name, "bytes": len(raw), "sha256": checksum(raw)} for name, raw in sorted(files.items())],
                    "scenarios": ["three explicit synthetic jobs", "SIGKILL after durable reservation and real CLI resume",
                                  "actual solved raster and production-mode picross-difficulty-0.4",
                                  "selected PNG and explicit none without PNG", "real open human gate and missing request",
                                  "tampered intermediate proof rejected; exact original restored",
                                  "image-only successor preserves logic/rating/independent originals and spent budgets",
                                  "explicit late v2 local package build; outer decisions remain open",
                                  "read-only historical status; real content/game unchanged"],
                    "final_status": final["status"], "interrupted_attempt": interrupted_number,
                    "produce_counts_before_image_change": original_counts, "produce_counts_after_image_change": final_counts,
                    "preserved_files": protected, "remaining": compact(final),
                    "retained_generated_images_or_zips": False}
        files["manifest.json"] = encoded(manifest)
        for name in ARTIFACTS:
            with (output / name).open("xb") as stream:
                stream.write(files[name])
        require({p.name for p in output.iterdir()} == set(ARTIFACTS), "Evidence directory contains unexpected files")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--product-commit")
    parser.add_argument("--development", action="store_true", help="Provisional dirty-tree trial, not final A01 evidence")
    args = parser.parse_args(argv)
    try:
        result = run_probe(args.output_dir, development=args.development, product_commit=args.product_commit)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"status": "verified", "product_commit": result["product_commit"],
                      "provisional": result["provisional"], "files": list(ARTIFACTS), "final_batch_status": result["final_status"]},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
