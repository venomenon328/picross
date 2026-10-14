"""Separate complete domain search; produces no deduction steps or certificate."""
from __future__ import annotations

from collections import deque
import hashlib
from pathlib import Path
import time

from .contract import (Aborted, Budget, InvalidInput, LOGIC_BYTE_LIMIT, Puzzle,
                       digest, domain_values, exact_keys, integer, load_json,
                       validate_logic, write_json)
from .diagnosis_verifier import (InvalidDiagnosis, WITNESS_FORMAT, load_evidence,
                                validate_measurements, verify_witness)
from .solver import line_support

REPORT_FORMAT = "picross-uniqueness-v1"
TOOL = {"id": "picross-uniqueness", "version": 1}
METHOD = {"id": "domain-dfs-line-support", "version": 1,
          "branch_order": "smallest-domain-row-major",
          "value_order": "empty-then-sorted-palette", "search": True}
WITNESS_BYTE_LIMIT = 512 * 1024
REPORT_BYTE_LIMIT = 64 * 1024
ABORT_REASONS = {"node_limit", "work_limit", "time_limit", "cancelled", "memory_limit"}


class DiagnosisBudget(Budget):
    """One cumulative budget for all branches and necessary witness checking."""

    def __init__(self, seconds=120, max_lines=100_000, max_nodes=100_000,
                 cancelled=None):
        super().__init__(seconds, max_lines, cancelled)
        integer(max_nodes, 0, 1_000_000, "max_nodes")
        self.seconds = seconds
        self.max_nodes = max_nodes
        self.nodes = 0
        self.witness_lines = 0

    def node(self):
        self.check()
        if self.nodes >= self.max_nodes:
            raise Aborted("node_limit")
        self.nodes += 1


def diagnose(puzzle: Puzzle, budget: DiagnosisBudget | None = None) -> dict:
    """Return a diagnosis with independently checked in-memory witnesses.

    Use diagnose_file for a fresh file-bound bundle. No target matrix is accepted.
    """
    return _diagnose(puzzle, budget if budget is not None else DiagnosisBudget())


def _diagnose(puzzle, budget, store=None):
    puzzle = validate_logic(puzzle.to_wire())
    started = time.monotonic()
    grid = puzzle.unknown_grid()
    trail, frames, witnesses = [], [], []
    queue = [("row", y) for y in range(puzzle.height)]
    queue += [("column", x) for x in range(puzzle.width)]

    def assign(y, x, mask):
        if grid[y][x] != mask:
            trail.append((y, x, grid[y][x]))
            grid[y][x] = mask

    def propagate(lines):
        pending = set(lines)
        work = deque(lines)
        while work:
            budget.tick()
            axis, index = work.popleft()
            pending.remove((axis, index))
            clues, domains = puzzle.line(grid, axis, index)
            support = line_support(clues, domains)
            if not all(support):
                return False
            for offset, (before, after) in enumerate(zip(domains, support)):
                if before == after:
                    continue
                y, x = (index, offset) if axis == "row" else (offset, index)
                assign(y, x, after)
                cross = ("column", x) if axis == "row" else ("row", y)
                if cross not in pending:
                    pending.add(cross)
                    work.append(cross)
        return True

    reason, status, complete = "exhausted", "no_solution", False
    try:
        while True:
            budget.node()
            if propagate(queue):
                choice = min(((mask.bit_count(), y, x) for y, row in enumerate(grid)
                              for x, mask in enumerate(row) if mask.bit_count() > 1),
                             default=None)
                if choice is None:
                    witness = {"format": WITNESS_FORMAT, "logic_hash": puzzle.logic_hash,
                               "matrix": [[domain_values(mask, puzzle.colors)[0]
                                           for mask in row] for row in grid]}
                    # The file path checks the bytes actually written, not just grid flags.
                    if store is not None:
                        witness = store(len(witnesses) + 1, witness)
                    before = budget.lines
                    try:
                        matrix = verify_witness(puzzle, witness, budget)
                    except InvalidDiagnosis as exc:
                        raise RuntimeError("Search produced an invalid witness") from exc
                    finally:
                        budget.witness_lines += budget.lines - before
                    if any(matrix == old["matrix"] for old in witnesses):
                        raise RuntimeError("Search produced a duplicate solution")
                    witnesses.append(witness)
                    if len(witnesses) == 2:
                        status, reason = "multiple", "two_solutions"
                        break
                else:
                    _, y, x = choice
                    frames.append([y, x, grid[y][x], len(trail)])

            # Iterative DFS with a reversible trail: no recursion or copied grid per node.
            while frames:
                y, x, remaining, checkpoint = frames[-1]
                while len(trail) > checkpoint:
                    py, px, old = trail.pop()
                    grid[py][px] = old
                if not remaining:
                    frames.pop()
                    continue
                bit = remaining & -remaining
                frames[-1][2] = remaining ^ bit
                assign(y, x, bit)
                queue = [("row", y), ("column", x)]
                break
            else:
                budget.check()
                complete = True
                status = "unique" if witnesses else "no_solution"
                break
    except (Aborted, KeyboardInterrupt, MemoryError) as exc:
        status = "unknown"
        reason = (str(exc) if isinstance(exc, Aborted) else
                  "cancelled" if isinstance(exc, KeyboardInterrupt) else "memory_limit")
    return {"format": REPORT_FORMAT, "tool": dict(TOOL), "method": dict(METHOD),
            "logic_hash": puzzle.logic_hash, "status": status,
            "search_complete": complete, "reason": reason, "certified": False,
            "budgets": {"seconds": budget.seconds, "max_lines": budget.max_lines,
                        "max_nodes": budget.max_nodes},
            "statistics": {"nodes": budget.nodes, "line_evaluations": budget.lines,
                           "witness_line_evaluations": budget.witness_lines,
                           "elapsed_seconds": time.monotonic() - started},
            "witnesses": witnesses}


def file_binding(path: Path) -> dict:
    data = path.read_bytes()
    return {"file": path.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def diagnose_file(input_path: Path, output_dir: Path,
                  budget: DiagnosisBudget | None = None) -> dict:
    """Snapshot exact input bytes, search, check saved witnesses, write a new report."""
    budget = budget if budget is not None else DiagnosisBudget()
    # Never reuse a directory, even an empty one. Invalid input can leave a
    # snapshot for diagnosis, but never a successful report.
    with input_path.open("rb") as stream:
        source = stream.read(LOGIC_BYTE_LIMIT + 1)
    if len(source) > LOGIC_BYTE_LIMIT:
        raise InvalidInput("Logic file exceeds its byte limit")
    if output_dir.exists() or output_dir.is_symlink():
        raise InvalidInput("Diagnosis output must be a new directory")
    output_dir.mkdir(parents=True, exist_ok=False)
    snapshot = output_dir / "input.json"
    snapshot.write_bytes(source)
    puzzle = validate_logic(load_json(snapshot, LOGIC_BYTE_LIMIT))
    input_binding = file_binding(snapshot)
    saved = []

    def store(index, witness):
        path = output_dir / f"solution-{index}.json"
        write_json(path, witness)
        binding = file_binding(path)
        loaded = load_evidence(path, WITNESS_BYTE_LIMIT)
        if binding != file_binding(path):
            raise RuntimeError("Witness changed while loading")
        saved.append(binding)
        return loaded

    result = _diagnose(puzzle, budget, store)
    # Only fully checked witnesses are referenced. An interrupted candidate may
    # remain in the fresh directory, but is never claimed as evidence.
    result["witnesses"] = saved[:len(result["witnesses"])]
    for binding in [input_binding, *result["witnesses"]]:
        if binding != file_binding(output_dir / binding["file"]):
            raise RuntimeError("Diagnosis evidence changed after validation")
    result["input"] = input_binding
    write_json(output_dir / "diagnosis.json", result)
    return result


def check_diagnosis(input_path: Path, bundle: Path, budget: Budget | None = None) -> dict:
    """Check file bindings/existence witnesses; does NOT replay exhaustive search."""
    budget = budget if budget is not None else Budget()
    puzzle = validate_logic(load_json(input_path, LOGIC_BYTE_LIMIT))
    obj = load_evidence(bundle / "diagnosis.json", REPORT_BYTE_LIMIT)
    exact_keys(obj, {"format", "tool", "method", "logic_hash", "status",
                            "search_complete", "reason", "certified", "budgets",
                            "statistics", "witnesses", "input"}, InvalidDiagnosis)
    if (obj["format"] != REPORT_FORMAT or digest(obj["tool"]) != digest(TOOL) or
            digest(obj["method"]) != digest(METHOD) or obj["logic_hash"] != puzzle.logic_hash or
            obj["certified"] is not False):
        raise InvalidDiagnosis("Wrong diagnosis format, method or logic binding")
    bindings = obj["witnesses"]
    if not isinstance(bindings, list) or len(bindings) > 2:
        raise InvalidDiagnosis("Expected at most two solution bindings")
    status = obj["status"]
    if (not isinstance(status, str) or
            status not in {"unique", "multiple", "no_solution", "unknown"} or
            obj["search_complete"] is not (status in {"unique", "no_solution"}) or
            (status == "unique" and len(bindings) != 1) or
            (status == "multiple" and len(bindings) != 2) or
            (status == "no_solution" and bindings) or
            (status == "unknown" and len(bindings) > 1) or
            not isinstance(obj["reason"], str) or
            obj["reason"] not in (ABORT_REASONS if status == "unknown" else
                                 {"two_solutions"} if status == "multiple" else {"exhausted"})):
        raise InvalidDiagnosis("Inconsistent diagnosis status/evidence")
    validate_measurements(obj, puzzle)

    def bound(name, binding, limit):
        path = bundle / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
            raise InvalidDiagnosis("Missing, unsafe or excessive evidence file")
        if digest(binding) != digest(file_binding(path)):
            raise InvalidDiagnosis("Evidence file binding mismatch")
        return path

    snapshot = bound("input.json", obj["input"], LOGIC_BYTE_LIMIT)
    # Require the exact original input, not merely an equivalent normalized object.
    if input_path.read_bytes() != snapshot.read_bytes():
        raise InvalidDiagnosis("Diagnosis is bound to different input bytes")
    matrices = []
    for i, binding in enumerate(bindings):
        path = bound(f"solution-{i + 1}.json", binding, WITNESS_BYTE_LIMIT)
        matrix = verify_witness(puzzle, load_evidence(path, WITNESS_BYTE_LIMIT), budget)
        if matrix in matrices:
            raise InvalidDiagnosis("Identical witnesses do not establish ambiguity")
        matrices.append(matrix)
    budget.check()
    return {"format": "picross-uniqueness-check-v1", "logic_hash": puzzle.logic_hash,
            "file_bindings_verified": True, "witnesses_verified": len(matrices),
            "reported_status": status, "confirmed_status": "multiple" if len(matrices) == 2 else None,
            "search_replayed": False, "certified": False}
