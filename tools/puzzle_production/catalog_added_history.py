"""Source-bound inspection and adoption of registered first-playable dates."""
from copy import deepcopy
from pathlib import Path
import subprocess

from . import catalog_added as added, catalog_io, catalog_rating as rating, catalog_transaction as tx, puzzle_record, puzzle_catalog, categories, current_content as content
from .authoring_package import require, relative
from .contract import canonical_bytes, exact_keys

FORMAT = "picross-puzzle-added-plan-v1"


def receipts(evidence):
    by_id = {}
    keys = set()
    for item in evidence:
        exact_keys(item, {"key","kind","commit","path","content","sha256","reference_time","integration"})
        require(item["kind"] == "direct" and item["integration"] is None and
                isinstance(item["key"], str) and item["key"] and item["key"] not in keys,
                "Invalid or duplicate direct date evidence")
        keys.add(item["key"])
        relative(item["path"])
        if item["commit"] is not None:
            added.commit(item["commit"])
        raw = item["content"].encode()
        receipt = rating.bytes_json(raw, added.LIMIT)
        exact_keys(receipt, {"id","event","success","registered_at"})
        key = rating.identity(receipt["id"])
        moment = added.timestamp(receipt["registered_at"])
        require(receipt["event"] == "first-playable-registration" and receipt["success"] is True and
                moment is not None and moment == item["reference_time"] and
                catalog_io.checksum(raw) == item["sha256"], "Invalid first-registration receipt")
        by_id.setdefault(key, []).append(item)
    return by_id


def plan(root, run, base, *, repository=None, direct=()):
    added.report_path(run)
    added.commit(base)
    root = catalog_io.external(root)
    actual = subprocess.check_output(["git","-C",str(root),"rev-parse","--verify",base+"^{commit}"], text=True).strip()
    require(actual == base, "Unknown history base")
    evidence = sorted(direct, key=lambda item: item["key"])
    selected = receipts(evidence)
    snapshot = tx.capture(root, sorted(selected) if selected else None)
    value = {"format":FORMAT, "run_id":run, "base_commit":base, "sources":tx.image_snapshot(snapshot)["sources"],
             "evidence":evidence, "entries":[{"id":key,"added":r["added"]} for key,r in snapshot["records"].items()]}
    require(len(content.encoded(value)) <= added.REPORT_LIMIT, "Oversized date plan")
    return value


def proposals(value, raw):
    exact_keys(value, {"format","run_id","base_commit","sources","evidence","entries"})
    require(value["format"] == FORMAT and raw == content.encoded(value), "Current canonical date plan required")
    added.commit(value["base_commit"])
    report = added.report_path(value["run_id"])
    selected = receipts(value["evidence"])
    rows = {}
    for row in value["entries"]:
        exact_keys(row, {"id","added"})
        key = rating.identity(row["id"])
        require(key not in rows, "Duplicate date plan ID")
        previous = added.validate_fields(row["added"])
        following = previous
        candidates = selected.get(key, [])
        if previous["added_at"] is None and len({item["reference_time"] for item in candidates}) == 1:
            evidence = min(candidates, key=lambda item:item["key"])
            moment = evidence["reference_time"]
            following = added.validate_fields({"added_at":moment,"provenance":{"kind":"direct","reference_time":moment,
                "commit":evidence["commit"],"evidence":{"path":report,"sha256":catalog_io.checksum(raw)},
                "reason":"Unique direct evidence of the successful first playable registration."}})
        rows[key] = (previous,following)
    require(list(rows) == sorted(rows) and (not selected or rows.keys() == selected.keys()), "Date plan selection differs")
    return rows


def changes(snapshot, rows):
    runtime = deepcopy(snapshot["runtime"])
    result = {}
    for row in runtime["entries"]:
        key = row["id"]
        if key not in rows:
            continue
        previous,following = rows[key]
        record = snapshot["records"][key]
        require(record["added"] == previous, "Previous date differs")
        if following != previous:
            record = {**record,"added":following}
            result[puzzle_record.path(key)] = puzzle_record.encode(record)
            row.update(puzzle_record.runtime_row(record))
    if result:
        result[tx.RUNTIME] = content.encoded(runtime)
    return result


def validate_journal(root, journal, sides, ids, cats):
    old,new = sides["old"],sides["new"]
    reports = [n for n in new if n.startswith(added.ROOT+"/reports/")]
    require(len(reports) == 1, "Expected a single date evidence report")
    report = reports[0]
    value = rating.bytes_json(new[report], added.REPORT_LIMIT)
    rows = proposals(value,new[report])
    require(report == added.report_path(value["run_id"]) and old[report] is None, "Occupied or foreign date report")
    expected = {tx.RUNTIME,categories.PATH,tx.catalog_method.PATH}
    records = {}
    runtime = puzzle_catalog.validate_runtime(rating.bytes_json(old[tx.RUNTIME],content.RUNTIME_LIMIT),cats,ids)
    targets = {puzzle_record.path(k) for k,(a,b) in rows.items() if a != b}
    require(targets and old.keys() == targets | {report,tx.RUNTIME,categories.PATH}, "Foreign date journal targets")
    def read(name, limit):
        expected.add(name)
        return old[name] if name in old else catalog_io.read(root,name,limit)
    for row in runtime["entries"]:
        key = row["id"]
        if key in rows:
            record = puzzle_record.load(root,key,category_catalog=cats,read=read)
            require(puzzle_record.runtime_row(record) == row, "Stale date projection")
            records[key] = record
    require(records.keys() == rows.keys(), "Unknown date plan ID")
    sources = {**journal["retained"],**{n:catalog_io.checksum(v) for n,v in old.items() if n != report}}
    require(sources == value["sources"] and sources.keys() == expected, "Unbound date sources")
    delta = changes({"runtime":runtime,"records":records},rows)
    require(new == {**old,**delta,report:new[report]}, "Date journal differs from approved evidence")
    return sides


def adopt(root, plan_path, *, apply=False, fail_step=None):
    root = catalog_io.external(root)
    raw = rating.read_file(plan_path,added.REPORT_LIMIT)
    value = rating.bytes_json(raw,added.REPORT_LIMIT)
    rows = proposals(value,raw)
    report = added.report_path(value["run_id"])
    snapshot = tx.capture(root,sorted(rows))
    existing = catalog_io.read(root,report,added.REPORT_LIMIT,missing=True)
    if existing is not None:
        require(existing == raw and all(snapshot["records"][key]["added"] == b for key,(a,b) in rows.items()),
                "Occupied date report or changed result")
        return {"status":"no-op","changes":[]}
    require(tx.image_snapshot(snapshot)["sources"] == value["sources"],"Date sources changed since planning")
    delta = changes(snapshot,rows)
    if not delta:
        return {"status":"no-op","changes":[]}
    delta[report] = raw
    if apply:
        journal = tx.record_journal({**snapshot["texts"], report:None}, delta, operation="added-adoption")
        tx.execute(root,journal,fail_step=fail_step)
    return {"status":"adopted" if apply else "planned","changes":sorted(delta)}


def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("plan")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--run", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--repository")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--direct-evidence", type=Path)
    p = commands.add_parser("adopt")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "plan":
        direct = rating.bytes_json(args.direct_evidence.read_bytes(), added.REPORT_LIMIT) if args.direct_evidence else []
        result = plan(args.root, args.run, args.base, repository=args.repository, direct=direct)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream: stream.write(canonical_bytes(result) + b"\n")
        print("Planned", len(result["entries"]), "IDs; no checkout writes")
    else:
        print(adopt(args.root, args.plan, apply=args.apply))


if __name__ == "__main__": main()
