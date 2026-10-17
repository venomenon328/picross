"""Explicit SD-C candidate, analysis/import, preview and adoption commands.

Never called by runtime/build/registry paths. Full analysis bundles stay in the
explicit workspace; only compact ratings and reports can enter the checkout.
"""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import re

from .authoring_package import require, sha
from .contract import Aborted, InvalidInput, InvalidProof, canonical_bytes, digest, exact_keys, load_json
from . import catalog_rating as rating, catalog_transaction as tx, catalog_difficulty
from .analysis_contract import AnalysisBudget
from .difficulty_rating import METHOD_ID, frozen_method

FORMAT = "picross-catalog-difficulty-report-v1"
REPORT_LIMIT = 16 * 1024 * 1024


def run_id(value):
    from .authoring_package import relative
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value), "Invalid difficulty run ID")
    relative(value)
    return value


def safe_external(path):
    absolute = path.absolute()
    return tx.safe(Path(absolute.anchor), absolute.relative_to(absolute.anchor).as_posix())


def work_directory(path, checkout=None):
    target = safe_external(path)
    roots = [Path(__file__).resolve().parents[2]]
    if checkout is not None: roots.append(checkout.resolve())
    for root in roots:
        require(not target.resolve().is_relative_to(root/"game") and
                not target.resolve().is_relative_to(root/"content/difficulty"), "Work directory overlaps runtime or permanent difficulty data")
    return target


def write_new(path, data):
    path = safe_external(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream: stream.write(data)


def candidate(design, matrix, logic, identifier, revision):
    from .images import validate_design, logic_from_matrix
    from .target_adapter import definition
    from .contract import validate_logic
    design = validate_design(design)
    puzzle = validate_logic(logic)
    normalized = puzzle.to_wire()
    require(digest(validate_logic(logic_from_matrix(matrix, design)).to_wire()) == digest(normalized), "Candidate matrix/logic disagree")
    value, _ = definition({"puzzle_id": rating.identity(identifier)}, design, matrix, normalized,
                          "Vorläufiger SD-Eingang", revision, "sd_provisional.svg")
    rating.definition(canonical_bytes(value) + b"\n")
    return value


def analyze_single(input_path, output, *, budget=None, verify_budget=None, proof=None, baseline=None):
    from .analysis_io import analyze_file
    input_path = safe_external(input_path)
    output = work_directory(output)
    import_limits = verify_budget.limits() if verify_budget is not None else {}
    analyze_file(input_path, output, kind="runtime", method=METHOD_ID, budget=budget,
                 verify_budget=verify_budget, proof_path=safe_external(proof) if proof else None,
                 baseline_path=safe_external(baseline) if baseline else None)
    # Import independently verifies the actual finished bundle; ordinary
    # integration thereafter only checks its compact data and bindings.
    return rating.import_bundle(input_path, output, budget=AnalysisBudget(**import_limits))


def _distribution(rows, key):
    counts = {**dict.fromkeys(catalog_difficulty.LEVELS, 0), "unrated": 0}
    for row in rows: counts[row[key]["level"] if row[key] else "unrated"] += 1
    return counts


def validate_report(report):
    exact_keys(report, {"format", "run_id", "result", "result_hash", "operation"})
    require(report["format"] == FORMAT and len(canonical_bytes(report)) + 1 <= REPORT_LIMIT, "Invalid difficulty report format/size")
    run_id(report["run_id"])
    r = exact_keys(report["result"], {"selection", "source_commit", "method_hash", "snapshot", "entries", "distribution"})
    require(r["selection"] in ("ids", "all") and isinstance(r["source_commit"], str) and
            re.fullmatch(r"[0-9a-f]{40}", r["source_commit"]), "Invalid report selection/commit")
    require(sha(r["method_hash"]) == digest(frozen_method()), "Wrong report method")
    exact_keys(r["snapshot"], {tx.REGISTRY, tx.RUNTIME, "content/categories.json"})
    for h in r["snapshot"].values(): sha(h)
    rows = r["entries"]
    require(isinstance(rows, list) and len(rows) <= 10000, "Invalid report entries")
    ids = []
    for row in rows:
        exact_keys(row, {"id", "current_source", "logic_binding", "old", "proposed", "status", "reason", "rating_hash", "checked_hash", "previous_record_hash"})
        ids.append(rating.identity(row["id"]))
        for k in ("old", "proposed"): catalog_difficulty.validate_projection(row[k])
        for k in ("rating_hash", "checked_hash", "previous_record_hash"):
            if row[k] is not None: sha(row[k])
        if row["current_source"] is not None:
            rating.source(row["current_source"])
            require(row["current_source"]["id"] == row["id"], "Report ID binding differs")
        if row["logic_binding"] is not None: rating.binding(row["logic_binding"])
        require(row["status"] in ("rated", "unrated", "invalid_input", "technical_error"), "Invalid report status")
        if row["status"] in ("rated", "unrated"):
            require(all(row[k] is not None for k in ("current_source", "logic_binding", "rating_hash", "checked_hash")), "Missing checked report binding")
        if row["status"] == "rated":
            require(row["reason"] is None and row["proposed"] is not None and row["proposed"]["method"] == METHOD_ID, "Invalid rated report row")
        else:
            require(row["proposed"] is None and isinstance(row["reason"], str) and 1 <= len(row["reason"]) <= 2048, "Missing open-case reason")
    require(ids == sorted(set(ids)), "Report IDs must be unique and sorted")
    expected = {k: _distribution(rows, k) for k in ("old", "proposed")}
    require(digest(r["distribution"]) == digest(expected), "Wrong report distribution")
    require(sha(report["result_hash"]) == digest(r), "Wrong report result hash")
    op = exact_keys(report["operation"], {"created_utc", "phase"})
    require(op["phase"] in ("preview", "adopted") and isinstance(op["created_utc"], str) and
            re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", op["created_utc"]), "Invalid report operation")
    datetime.strptime(op["created_utc"], "%Y-%m-%dT%H:%M:%SZ")
    return report


def markdown(report):
    validate_report(report)
    r = report["result"]
    lines = ["# Schwierigkeitsbericht " + report["run_id"], "", "Phase: " + report["operation"]["phase"],
             "", "Quellcommit: `" + r["source_commit"] + "`", "", "Methode: `" + METHOD_ID + "` / `" + r["method_hash"] + "`",
             "", "Ergebnis: `" + report["result_hash"] + "`", "",
             "Verteilung nur beobachtend; keine Änderung der eingefrorenen Grenzen.", "",
             "| ID | Alt | Vorschlag | Status / Grund |", "| --- | --- | --- | --- |"]
    for row in r["entries"]:
        reason = (row["reason"] or "vollständig geprüft").replace("|", "\\|").replace("\n", " ").replace("\r", " ")
        lines.append(f"| {row['id']} | {row['old']['level'] if row['old'] else 'Nicht eingestuft'} | "
                     f"{row['proposed']['level'] if row['proposed'] else 'offen'} | {row['status']}: {reason} |")
    lines += ["", "Verteilung (Alt / Vorschlag):", ""]
    for level in (*catalog_difficulty.LEVELS, "unrated"):
        lines.append(f"- {level}: {r['distribution']['old'][level]} / {r['distribution']['proposed'][level]}")
    lines += ["", "## Bindungen je ID", ""]
    for row in r["entries"]:
        lines += ["### " + row["id"], "", "```json", json.dumps({k: v for k, v in row.items() if k not in ("old", "proposed", "reason", "status")},
                  ensure_ascii=False, sort_keys=True, indent=2), "```", ""]
    return "\n".join(lines)


def preview(root, output, run, source_commit, *, ids=None, all_entries=False, checked_inputs=None,
            r4_inputs=None, limits=None, verify_limits=None):
    root = root.resolve()
    require(bool(ids) != bool(all_entries), "Choose explicit IDs or all")
    run_id(run)
    require(isinstance(source_commit, str) and re.fullmatch(r"[0-9a-f]{40}", source_commit), "Explicit source commit required")
    output = work_directory(output, root)
    require(not output.exists(), "Preview output already exists")
    snapshot = tx.capture(root)
    entries = {e["id"]: e for e in snapshot["registry"]["entries"]}
    selected = sorted(entries) if all_entries else sorted(ids)
    require(len(selected) == len(set(selected)) and all(i in entries for i in selected), "Duplicate or unknown selected ID")
    require(set(checked_inputs or {}) <= set(selected) and set(r4_inputs or {}) <= set(selected), "Input outside explicit selection")
    output.mkdir(parents=True)
    rows = []
    for identifier in selected:
        e = entries[identifier]
        raw = snapshot["texts"]["game/" + e["definition"]]
        prior_raw = snapshot["texts"][rating.path(identifier)]
        prior = rating.validate(rating.bytes_json(prior_raw), definition_bytes=raw) if prior_raw is not None else None
        row = {"id": identifier, "current_source": None, "logic_binding": None,
               "old": rating.project(prior) if prior else catalog_difficulty.project(e["production"]["difficulty"]),
               "proposed": None, "status": "invalid_input", "reason": None, "rating_hash": None, "checked_hash": None,
               "previous_record_hash": prior["record_hash"] if prior else None}
        try:
            _, _, row["current_source"], row["logic_binding"] = rating.definition(raw)
            if checked_inputs is not None:
                require(identifier in checked_inputs, "Missing checked input for selected ID")
                value = checked_inputs[identifier]
                value = load_json(safe_external(value), rating.LIMIT) if isinstance(value, Path) else value
                rating.validate(value, active=False, definition_bytes=raw)
            else:
                source = output / "inputs" / (identifier + ".json")
                write_new(source, raw)
                pair = (r4_inputs or {}).get(identifier, (None, None))
                value = analyze_single(source, output / "bundles" / identifier,
                    budget=AnalysisBudget(**(limits or {})), verify_budget=AnalysisBudget(**(verify_limits or {})), baseline=pair[0], proof=pair[1])
            write_new(output / "checked" / (identifier + ".json"), rating.encoded(value))
            result = value["rating"]["result"]
            row.update(status=result["status"], reason=result["reason"], proposed=rating.project(value) if result["status"] == "rated" else None,
                       rating_hash=value["rating"]["rating_hash"], checked_hash=value["checked_hash"])
        except (InvalidInput, InvalidProof, Aborted, ValueError, OSError) as exc:
            row.update(status="technical_error" if isinstance(exc, (OSError, Aborted)) else "invalid_input", reason=str(exc)[:2048] or type(exc).__name__)
        rows.append(row)
    result = {"selection": "all" if all_entries else "ids", "source_commit": source_commit, "method_hash": digest(frozen_method()),
              "snapshot": {n: hashlib.sha256(snapshot["texts"][n]).hexdigest() for n in (tx.REGISTRY, tx.RUNTIME, "content/categories.json")},
              "entries": rows, "distribution": {k: _distribution(rows, k) for k in ("old", "proposed")}}
    report = validate_report({"format": FORMAT, "run_id": run, "result": result, "result_hash": digest(result),
        "operation": {"created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "phase": "preview"}})
    write_new(output / "report.json", canonical_bytes(report) + b"\n")
    write_new(output / "report.md", markdown(report).encode())
    return report


def adopt(root, workspace, *, apply=False, fail_step=None):
    root = root.resolve()
    workspace = work_directory(workspace, root)
    report_bytes = rating.read_file(safe_external(workspace / "report.json"), REPORT_LIMIT)
    report = validate_report(rating.bytes_json(report_bytes, REPORT_LIMIT))
    require(safe_external(workspace / "report.md").read_bytes() == markdown(report).encode(), "Preview Markdown differs")
    snapshot = tx.capture(root)
    entries = {e["id"]: e for e in snapshot["registry"]["entries"]}
    rows = report["result"]["entries"]
    if report["result"]["selection"] == "all": require(sorted(entries) == [r["id"] for r in rows], "Catalog selection changed")
    changes = {}
    externals = {workspace / "report.json": report_bytes, workspace / "report.md": markdown(report).encode()}
    same = True
    for row in rows:
        require(row["id"] in entries, "Selected ID disappeared")
        e = entries[row["id"]]
        raw = snapshot["texts"]["game/" + e["definition"]]
        if row["current_source"] is not None:
            _, _, current, logic = rating.definition(raw)
            require(current == row["current_source"] and logic == row["logic_binding"], "Selected definition changed since preview")
        prior_raw = snapshot["texts"][rating.path(row["id"])]
        prior = rating.validate(rating.bytes_json(prior_raw), definition_bytes=raw) if prior_raw else None
        if row["status"] != "rated":
            require((prior["record_hash"] if prior else None) == row["previous_record_hash"], "Active rating changed since preview")
            continue
        p = safe_external(workspace / "checked" / (row["id"] + ".json"))
        externals[p] = rating.read_file(p)
        checked = rating.validate(rating.bytes_json(externals[p]), active=False, definition_bytes=raw)
        require(checked["checked_hash"] == row["checked_hash"] and checked["rating"]["rating_hash"] == row["rating_hash"] and
                rating.project(checked) == row["proposed"], "Checked preview input changed")
        value = rating.active_record(checked, prior, report={"run_id": report["run_id"], "result_hash": report["result_hash"]})
        if prior != value:
            same = False
            require((prior["record_hash"] if prior else None) == row["previous_record_hash"], "Active rating changed since preview")
            changes[rating.path(row["id"])] = rating.encoded(value)
    final = deepcopy(report)
    final["operation"]["phase"] = "adopted"
    prefix = "content/difficulty/reports/" + report["run_id"] + "/report."
    durable = {prefix + "json": canonical_bytes(final) + b"\n", prefix + "md": markdown(final).encode()}
    existing = {n: tx.read(root, n) for n in durable}
    if same and existing == durable:
        return {"status": "no-op", "changes": [], "report_hash": report["result_hash"]}
    require(all(v is None for v in existing.values()), "Report run already exists; use a new run ID")
    require(all(hashlib.sha256(snapshot["texts"][n]).hexdigest() == h for n, h in report["result"]["snapshot"].items()),
            "Checkout changed since preview")
    changes.update(durable)
    journal = tx.prepare(root, snapshot, changes, operation="adoption", report_run=report["run_id"])
    require(all(safe_external(p).read_bytes() == b for p, b in externals.items()), "Preview inputs changed during planning")
    plan = {"status": "planned-adoption", "changes": sorted(n for n in journal["new"] if journal["old"][n] != journal["new"][n]),
            "report_hash": report["result_hash"], "open_ids": [r["id"] for r in rows if r["status"] != "rated"]}
    if apply: tx.execute(root, journal, fail_step=fail_step)
    return {**plan, "status": "adopted" if apply else "planned-adoption"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    defaults = {"seconds": 120, "max_lines": 100000, "max_rule_work": 20000000,
                "max_waves": 80000, "max_pair_work": 20000000, "max_pair_records": 250000}
    def budgets(p, prefixes=("", "verify_")):
        for prefix in prefixes:
            for name, default in defaults.items():
                p.add_argument("--" + (prefix + name).replace("_", "-"), type=float if name == "seconds" else int, default=default)
    def limits(prefix=""):
        return {name: getattr(args, prefix + name) for name in defaults}
    p = sub.add_parser("candidate")
    for n in ("design", "matrix", "logic", "output"): p.add_argument("--" + n, type=Path, required=True)
    p.add_argument("--puzzle-id", required=True); p.add_argument("--runtime-revision", type=int, required=True)
    for cmd in ("analyze", "import", "rebind"):
        p = sub.add_parser(cmd)
        p.add_argument("--input", type=Path, required=True)
        p.add_argument("--output", type=Path, required=True)
        if cmd == "analyze":
            budgets(p)
            p.add_argument("--work-dir", type=Path, required=True)
            p.add_argument("--r4-baseline", type=Path); p.add_argument("--r4-proof", type=Path)
        elif cmd == "import":
            p.add_argument("--bundle", type=Path, required=True)
            budgets(p, ("",))
        else: p.add_argument("--rating", type=Path, required=True)
    for cmd in ("preview", "preview-checked"):
        p = sub.add_parser(cmd)
        p.add_argument("--checkout", type=Path, required=True)
        p.add_argument("--work-dir", type=Path, required=True)
        p.add_argument("--run-id", required=True); p.add_argument("--source-commit", required=True)
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument("--id", action="append"); group.add_argument("--all", action="store_true")
        if cmd == "preview-checked": p.add_argument("--checked", nargs=2, action="append", required=True, metavar=("ID", "PATH"))
        else:
            p.add_argument("--r4", nargs=3, action="append", metavar=("ID", "BASELINE", "PROOF"))
            budgets(p)
    for cmd in ("plan-adoption", "adopt"):
        p = sub.add_parser(cmd)
        p.add_argument("--checkout", type=Path, required=True); p.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "candidate":
            result = candidate(*(load_json(safe_external(getattr(args, n))) for n in ("design", "matrix", "logic")), args.puzzle_id, args.runtime_revision)
            write_new(work_directory(args.output), canonical_bytes(result) + b"\n")
        elif args.command in ("analyze", "import", "rebind"):
            if args.command == "analyze":
                result = analyze_single(args.input, args.work_dir, proof=args.r4_proof, baseline=args.r4_baseline,
                                        budget=AnalysisBudget(**limits()), verify_budget=AnalysisBudget(**limits("verify_")))
            elif args.command == "import":
                result = rating.import_bundle(safe_external(args.input), work_directory(args.bundle), budget=AnalysisBudget(**limits()))
            else:
                value = load_json(safe_external(args.rating), rating.LIMIT)
                if value.get("format") == rating.FORMAT: value = rating.checked_from_active(value)
                result = rating.rebind_checked(value, safe_external(args.input).read_bytes())
            write_new(work_directory(args.output), rating.encoded(result))
        elif args.command in ("preview", "preview-checked"):
            supplied = args.checked if args.command == "preview-checked" else args.r4
            require(not supplied or len({row[0] for row in supplied}) == len(supplied), "Duplicate per-ID input")
            checked = {i: Path(p) for i, p in supplied} if args.command == "preview-checked" else None
            r4 = {i: (Path(b), Path(p)) for i, b, p in supplied or []} if args.command == "preview" else None
            result = preview(args.checkout, args.work_dir, args.run_id, args.source_commit, ids=args.id,
                             all_entries=args.all, checked_inputs=checked, r4_inputs=r4,
                             limits=limits() if args.command == "preview" else None,
                             verify_limits=limits("verify_") if args.command == "preview" else None)
        else:
            result = adopt(args.checkout, args.work_dir, apply=args.command == "adopt")
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (InvalidInput, InvalidProof, Aborted, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 4 if isinstance(exc, Aborted) else 2


if __name__ == "__main__":
    raise SystemExit(main())
