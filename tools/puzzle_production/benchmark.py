"""Isolated mono/color reference runs, fresh proof replay and Linux peak RSS."""
from __future__ import annotations

import argparse
import hashlib
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from .contract import COLOR_LOGIC_FORMAT, Clue, Puzzle, digest, load_json, write_json

TIME_BUDGET_SECONDS = 120
RSS_BUDGET_MIB = 512
ADDRESS_SPACE_LIMIT_MIB = 1024


def reference(size: int) -> Puzzle:
    """Nested centered bars: varying runs plus nontrivial empty/filled propagation.

    Rows are 2,4,...,size,...,4,2 wide. All columns are contiguous bars too.
    Only clues are passed to the core. No stored target is read by either core.
    """
    grid = []
    for y in range(size):
        length = 2 * (min(y, size - 1 - y) + 1)
        start = (size - length) // 2
        grid.append([int(start <= x < start + length) for x in range(size)])
    rows = tuple((sum(row),) for row in grid)
    columns = tuple((sum(row[x] for row in grid),) for x in range(size))
    return Puzzle(size, size, rows, columns)


def long_line_reference() -> Puzzle:
    # 20 singletons in 100 cells: C(81,20) possible row placements. A square
    # of the same hints retains this row unchanged at a true unknown fixpoint.
    return Puzzle(100, 100, ((1,) * 20,) * 100, ((1,) * 20,) * 100)


def color_reference(size: int) -> Puzzle:
    """Four-color woven bars, with internal touching color changes in BOTH axes.

    Independently generated clue fixture; the target never enters solve/verify.
    Each foreground bar contains multiple ordered length/color blocks.
    """
    grid = []
    for y in range(size):
        length = 2 * (min(y, size - 1 - y) + 1)
        start = (size - length) // 2
        grid.append([1 + ((x // 5 + y // 7) % 4) if start <= x < start + length else 0
                     for x in range(size)])

    return _color_puzzle(grid)


def _color_puzzle(grid) -> Puzzle:
    def clues(cells):
        result, previous, length = [], 0, 0
        for value in list(cells) + [0]:
            if value != previous:
                if previous:
                    result.append(Clue(length, 1 << previous))
                previous, length = value, 0
            length += 1
        return tuple(result)

    return Puzzle(len(grid[0]), len(grid), tuple(clues(row) for row in grid),
                  tuple(clues(row[x] for row in grid) for x in range(len(grid[0]))),
                  ("blue", "green", "red", "yellow"), COLOR_LOGIC_FORMAT)


def color_long_line_reference() -> Puzzle:
    # 20 alternating four-color blocks in length 100, no required separators:
    # C(100,20) placements per line; color order and joint domains still matter.
    # Offset colors in rows/columns from a known feasible sparse diagonal grid.
    # The core gets only the clues, not this existence witness.
    return _color_puzzle([[1 + ((x + y) // 5) % 4 if (x + y) % 5 == 0 else 0
                           for x in range(100)] for y in range(100)])


def _worker(args) -> int:
    from .cli import main
    enforced = None
    if sys.platform.startswith("linux"):
        import resource
        limit = ADDRESS_SPACE_LIMIT_MIB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        enforced = {"kind": "RLIMIT_AS", "bytes": limit}
    at = time.perf_counter()
    cli_args = [args.worker, "--input", str(args.input)]
    if args.worker == "solve":
        cli_args += ["--output-dir", str(args.case_dir)]
    else:
        cli_args += ["--proof", str(args.case_dir / "proof.json"),
                     "--report", str(args.case_dir / "fresh-verification.json")]
    code = main(cli_args)
    elapsed = time.perf_counter() - at
    peak = None
    if sys.platform.startswith("linux"):
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    write_json(args.metrics, {"exit_code": code, "elapsed_seconds": elapsed,
                             "peak_rss_bytes": peak,
                             "rss_measurement": "getrusage(RUSAGE_SELF).ru_maxrss KiB -> bytes"
                             if peak is not None else "unavailable on this platform",
                             "enforced_os_limit": enforced})
    return code


def _git(*args) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _run_worker(command, timeout):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def _processor() -> str:
    if sys.platform.startswith("linux"):
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.partition(":")[2].strip()
    return platform.processor()


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "format": "picross-benchmark-v2", "source_head": os.environ.get(
            "RP1_SOURCE_HEAD", _git("rev-parse", "HEAD")),
        "checkout_commit": _git("rev-parse", "HEAD"),
        "base_commit": os.environ.get("RP1_BASE_COMMIT"),
        "git_status": _git("status", "--porcelain"),
        "machine": {"platform": platform.platform(), "python": sys.version,
                    "implementation": platform.python_implementation(),
                    "processor": _processor(), "cpu_count": os.cpu_count()},
        "budgets": {"solve_serialization_fresh_verify_seconds": TIME_BUDGET_SECONDS,
                    "peak_rss_mib_per_process": RSS_BUDGET_MIB,
                    "enforced_linux_address_space_mib": ADDRESS_SPACE_LIMIT_MIB},
        "cases": [], "accepted": False,
    }
    fixtures = [("bars-40", reference(40), "solved"),
                ("bars-100", reference(100), "solved"),
                ("sparse-100", long_line_reference(), "stalled"),
                ("color-woven-40", color_reference(40), "solved"),
                ("color-woven-100", color_reference(100), "solved"),
                ("color-sparse-100", color_long_line_reference(), "stalled")]
    failed = False
    for name, puzzle, expected in fixtures:
        case_dir = output / name
        case_dir.mkdir(parents=True, exist_ok=True)
        input_path = case_dir / "logic.json"
        write_json(input_path, puzzle.to_wire())
        case = {"name": name, "dimensions": [puzzle.width, puzzle.height],
                "logic_hash": puzzle.logic_hash, "expected_status": expected,
                "logic_format": puzzle.format, "profile": puzzle.profile,
                "profile_hash": digest(puzzle.profile),
                "processes": [], "accepted": False}
        if name == "sparse-100":
            case["placements_per_unknown_line"] = math.comb(81, 20)
        if name == "color-sparse-100":
            case["placements_per_unknown_line"] = math.comb(100, 20)
        total_started = time.perf_counter()
        try:
            for mode in ("solve", "verify"):
                remaining = TIME_BUDGET_SECONDS - (time.perf_counter() - total_started)
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(mode, TIME_BUDGET_SECONDS)
                metrics = case_dir / (mode + "-metrics.json")
                proc = _run_worker(
                    [sys.executable, "-m", "tools.puzzle_production.benchmark",
                     "--worker", mode, "--input", str(input_path),
                     "--case-dir", str(case_dir), "--metrics", str(metrics)],
                    timeout=remaining)
                (case_dir / (mode + ".log")).write_text(
                    proc.stdout + proc.stderr, encoding="utf-8", newline="\n")
                if not metrics.exists():
                    raise RuntimeError(f"{mode} process died: exit {proc.returncode}")
                measured = load_json(metrics)
                case["processes"].append({"mode": mode, **measured})
                if proc.returncode or measured["exit_code"]:
                    raise RuntimeError(f"{mode} failed with exit {proc.returncode}")
            case["wall_seconds_including_process_startup"] = time.perf_counter() - total_started
            result = load_json(case_dir / "result.json")
            fresh = load_json(case_dir / "fresh-verification.json")
            case["result"] = result
            case["fresh_verification"] = fresh
            case["proof_sha256"] = hashlib.sha256((case_dir / "proof.json").read_bytes()).hexdigest()
            proof = load_json(case_dir / "proof.json", puzzle.proof_byte_limit)
            case["partial_domain_changes"] = sum(
                len(change["after"]) > 1 for step in proof["steps"] for change in step["changes"])
            rss_ok = all(p["peak_rss_bytes"] is not None and
                         p["peak_rss_bytes"] <= RSS_BUDGET_MIB * 1024 * 1024
                         for p in case["processes"])
            case["accepted"] = bool(
                rss_ok and case["wall_seconds_including_process_startup"] <= TIME_BUDGET_SECONDS
                and result["status"] == fresh["status"] == expected
                and result["proof_verified"] and fresh["proof_verified"]
                and result["certified"] == fresh["certified"] == (expected == "solved")
                and result["logic_hash"] == fresh["logic_hash"] == puzzle.logic_hash
                and result["profile_hash"] == fresh["profile_hash"] == digest(puzzle.profile)
                and result["profile"] == fresh["profile"] == puzzle.profile
                and result["solver_line_evaluations"] >= puzzle.width + puzzle.height
                and (expected != "solved" or result["steps"] > 0)
                and (not name.startswith("color-") or case["partial_domain_changes"] > 0))
        except (subprocess.TimeoutExpired, RuntimeError, OSError, ValueError) as exc:
            case["failure"] = {"status": "aborted" if isinstance(exc, subprocess.TimeoutExpired)
                               else "technical_error", "message": str(exc)}
        failed |= not case["accepted"]
        report["cases"].append(case)
        write_json(output / "benchmark.json", report)
    report["accepted"] = not failed
    write_json(output / "benchmark.json", report)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/puzzle-production"))
    parser.add_argument("--worker", choices=("solve", "verify"))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--case-dir", type=Path)
    parser.add_argument("--metrics", type=Path)
    args = parser.parse_args(argv)
    if args.worker:
        return _worker(args)
    report = run(args.output_dir)
    print(f"RP1/RP2-A05 accepted={report['accepted']}; report={args.output_dir / 'benchmark.json'}")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
