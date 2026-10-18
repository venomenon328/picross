"""Progressive evidence and size measurements for the current P1 CI scope."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import p1_preflight as toolchain



def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_identity(root: Path) -> dict:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=root, capture_output=True,
                              text=True, check=True).stdout.strip()

    checkout = git("rev-parse", "HEAD")
    source = os.environ.get("P1_PREFLIGHT_SOURCE_COMMIT", checkout)
    base = os.environ.get("P1_BASE_COMMIT")
    if not base and os.environ.get("GITHUB_ACTIONS") == "true":
        raise toolchain.PreflightError("CI must supply its exact P1_BASE_COMMIT")
    if not base:
        try:
            base = git("merge-base", "HEAD", "origin/main")
        except subprocess.CalledProcessError:
            base = None
    for name, value in (("source", source), ("base", base), ("checkout", checkout)):
        if value is not None and not re.fullmatch(r"[0-9a-f]{40}", value):
            raise toolchain.PreflightError(f"Invalid {name} commit identity")
    return dict(source_commit=source, source_tree_dirty=bool(git("status", "--porcelain")),
                base_commit=base, tested_checkout_commit=checkout,
                base_identity_reason="explicit CI/caller base" if os.environ.get("P1_BASE_COMMIT")
                else "local merge-base" if base else "local origin/main unavailable",
                github_run_id=os.environ.get("GITHUB_RUN_ID"),
                github_run_attempt=os.environ.get("GITHUB_RUN_ATTEMPT"),
                github_event_name=os.environ.get("GITHUB_EVENT_NAME"))


def bound_log(path: Path) -> dict:
    data = path.read_bytes()
    original = len(data)
    return dict(file=str(path.name), original_bytes=original, retained_bytes=len(data),
                abbreviated=original != len(data), sha256=toolchain.sha256_file(path))


def png_references(value) -> set[str]:
    """Image paths declared by native reports, including crop/context fields."""
    if isinstance(value, str):
        return {value} if value.endswith(".png") else set()
    children = value.values() if isinstance(value, dict) else value if isinstance(value, list) else ()
    return {name for child in children for name in png_references(child)}


def native_failure_sources(output: Path, phase: str, pixel_inputs=()) -> tuple[list[Path], list[Path]]:
    """Rebuild partial evidence selection when run_visual did not return."""
    reports = sorted(output.glob("renders/*.json")) + sorted(output.glob("drawing-renders/*.json")) + sorted(output.glob("vs2-renders/*.json")) + sorted(output.glob("v1-renders/*.json")) + sorted(output.glob("v2-renders/*.json")) + sorted(output.glob("v3-renders/*.json"))
    reports += sorted(output.glob("perf-b/*.json"))
    for area in ("kat2", "ea", "za1"):
        reports += sorted(output.glob(area+"/*.json"))
    primary = ("render-report-" + phase[len("render-"):] + ".json" if phase.startswith("render-")
               else phase.removesuffix("-render") + "-renders.json" if phase.startswith("rp6-")
               else "z2-renders.json" if phase == "current-book-capture"
               else "zs2-after.json" if phase.startswith("current-drawing-")
               else "v2-write.json" if phase.startswith("vs2-v2-") or phase == "current-vs2-complete"
               else "v1-focused.json" if phase == "vs2-v1-focused"
               else "probe.json" if phase.startswith("perf-b-") else None)
    bound, phase_images, native_failures = set(), set(), set()
    for path in reports:
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # Retain the incomplete report itself for diagnosis.
        def existing(names):
            found = set()
            for name in names:
                relative = Path(name)
                candidate = path.parent / relative
                if (not relative.is_absolute() and ".." not in relative.parts and candidate.is_file()
                        and candidate.resolve().is_relative_to(path.parent.resolve())):
                    found.add(candidate)
            return found
        images = existing(png_references(report))
        bound.update(images)
        if path.name == primary:
            phase_images.update(images)
            if isinstance(report, dict):
                native_failures.update(existing(png_references(report.get("failure_captures", []))))
    # An oracle may nominate its actual input group, but never add an image not
    # declared by a completed native report (or escape its output directory).
    oracle_inputs = {Path(path) for path in pixel_inputs} & bound
    priority = oracle_inputs or native_failures or phase_images
    partial = list(output.glob("renders/failure-*.png"))
    # A failed crop/animation phase may have renamed its original frame before
    # the compact summary exists. Keep these real inputs for diagnosis as well.
    for area, prefix in (('kat2', 'kat2-'), ('ea', 'ea-'), ('za1', 'za1-')):
        if phase.startswith(prefix):
            partial += list(output.glob(area+'/*.png')) + list(output.glob(area+'/*.apng'))
    return list(set(reports) | bound | set(partial)), list(priority | set(partial))


class Evidence:
    def __init__(self, output: Path, host: str, scope: dict[str, bool], technical: Path | None = None):
        self.output = output
        self.technical = technical or output / "technical"
        self.logs = self.technical / "logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.began = time.monotonic()
        self.report = dict(schema=2, status="running", started_at=now(), host=host,
                           engine_version=toolchain.EXPECTED_VERSION, checks=[], scope={})
        for name, enabled in scope.items():
            self.report["scope"][name] = dict(
                enabled=enabled, status="pending" if enabled else "not_applicable",
                reason="selected by caller or conservative manual default" if enabled
                else f"caller selected --no-{name}; this coverage was not executed")
        self.report["historical_evidence"] = dict(
            status="not_applicable", reason="Issue #63: historical studies and reference builds run only at their bound historical commits")
        self.flush()

    def flush(self) -> None:
        if self.report["status"] == "running":
            self.report["elapsed_seconds"] = round(time.monotonic() - self.began, 3)
        text = json.dumps(self.report, ensure_ascii=False, indent=2) + "\n"
        for path in (self.output / "product-report.json", self.technical / "product-report.json"):
            temporary = path.with_suffix(".json.tmp")
            temporary.write_text(text, encoding="utf-8", newline="\n")
            temporary.replace(path)

    def start(self, name: str) -> dict:
        record = dict(name=name, status="running", started_at=now())
        self.report["checks"].append(record)
        self.report["active_phase"] = name
        self.flush()
        return record

    def complete(self, record: dict, result: dict, error: Exception | None = None) -> None:
        record.update({key: value for key, value in result.items() if key != "output"})
        record.update(status="failure" if error else "success", finished_at=now())
        if error:
            record["error"] = str(error)
        self.report.pop("active_phase", None)
        self.flush()

    def scope_done(self, name: str) -> None:
        self.report["scope"][name]["status"] = "success"
        self.flush()

    def scope_start(self, name: str) -> None:
        self.report["scope"][name]["status"] = "running"
        self.flush()

    def finish(self, error: Exception | None = None) -> None:
        incomplete = [name for name, item in self.report["scope"].items()
                      if item["enabled"] and item["status"] != "success"]
        missing = toolchain.PreflightError("Required coverage incomplete: " + ", ".join(incomplete)) if error is None and incomplete else None
        error = error or missing
        self.report.update(status="failure" if error else "success", finished_at=now(),
                           elapsed_seconds=round(time.monotonic() - self.began, 3))
        if error:
            self.report["failure"] = dict(type=type(error).__name__, message=str(error))
            for item in self.report["scope"].values():
                if item["status"] == "running":
                    item.update(status="failure", reason="scope did not complete successfully")
                elif item["status"] == "pending":
                    item.update(status="not_run", reason="run failed before this scope completed")
        self.flush()
        if missing:
            raise missing

    def retain_files(self, sources: list[Path], priority_sources=(), allow_partial=False) -> None:
        """Select native originals; never resize an image or replace an assertion."""
        began = time.monotonic()
        selection_root = self.technical / "selected"
        if selection_root.exists():
            shutil.rmtree(selection_root)
        selected, omitted = [], []
        image_bytes = 0
        priority = set(priority_sources)
        for path in sorted(set(sources), key=lambda p: (
                p not in priority, "failure" not in p.name, p.suffix == ".png",
                p.stat().st_size if p.is_file() else 0, str(p))):
            if not path.is_file() or path.stat().st_size == 0:
                if allow_partial:
                    omitted.append(dict(file=path.relative_to(self.output).as_posix(),
                                        reason='missing/empty during failed run'))
                    continue
                raise toolchain.PreflightError("Missing/empty selected evidence: " + str(path))
            relative = path.relative_to(self.output)
            size = path.stat().st_size
            target = self.technical / "selected" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            if path.suffix == ".png":
                image_bytes += size
            selected.append(dict(file=relative.as_posix(), bytes=size, sha256=toolchain.sha256_file(path),
                                 failure_priority=path in priority, priority=path in priority))
        self.report["selected_evidence"] = dict(files=selected, omitted=omitted,
                                                 image_bytes=image_bytes, selection_seconds=round(time.monotonic()-began, 6))
        self.flush()

    def measure_size(self, player: Path | None = None) -> dict:
        technical = sum(p.stat().st_size for p in self.technical.rglob("*") if p.is_file())
        player_bytes = player.stat().st_size if player and player.is_file() else 0
        return dict(technical_bytes=technical, player_bytes=player_bytes,
                    total_bytes=technical + player_bytes)
