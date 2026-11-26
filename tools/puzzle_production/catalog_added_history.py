"""Source-bound inspection and adoption of registered first-playable dates."""
import subprocess

from . import catalog_added as added, catalog_io, catalog_rating as rating, catalog_transaction as tx, puzzle_record
from .authoring_package import require
from .contract import canonical_bytes, exact_keys

FORMAT = "picross-puzzle-added-plan-v1"


def plan(root,run,base,*,repository=None,direct=()):
    """Every registered record already carries its date or its established unknown provenance."""
    added.report_path(run)
    added.commit(base)
    root = catalog_io.external(root)
    actual = subprocess.check_output(["git","-C",str(root),"rev-parse","--verify",base+"^{commit}"],text=True).strip()
    require(actual == base,"Unknown history base")
    for evidence in direct:
        receipt = rating.bytes_json(evidence["content"].encode(),added.LIMIT)
        exact_keys(receipt,{"id","event","success","registered_at"})
        rating.identity(receipt["id"])
        require(receipt["event"] == "first-playable-registration" and receipt["success"] is True
                and added.timestamp(receipt["registered_at"]) == evidence["reference_time"]
                and catalog_io.checksum(evidence["content"].encode()) == evidence["sha256"],"Invalid direct evidence")
    snapshot = tx.capture(root,None)
    return {"format":FORMAT,"run_id":run,"base_commit":base,"sources":tx.image_snapshot(snapshot)["sources"],
            "entries":[{"id":key,"added":r["added"]} for key,r in snapshot["records"].items()]}


def adopt(root,plan_path,*,apply=False,fail_step=None):
    raw = rating.read_file(plan_path,added.REPORT_LIMIT)
    value = rating.bytes_json(raw,added.REPORT_LIMIT)
    exact_keys(value,{"format","run_id","base_commit","sources","entries"})
    require(value["format"] == FORMAT and raw == canonical_bytes(value)+b"\n","Current canonical date plan required")
    require(value == plan(root,value["run_id"],value["base_commit"]),"Date source changed since planning")
    return {"status":"no-op","changes":[]}


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
