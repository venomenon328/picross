"""Explicit KU-B historical plan/adoption. Git access belongs only to plan()."""
from copy import deepcopy
import hashlib

from . import catalog_io
from .authoring_package import require, sha, relative
from .contract import exact_keys, canonical_bytes
from . import catalog_added as added, catalog_rating as rating

LEGACY_FORMAT = "picross-added-plan-v1"
FORMAT = "picross-added-plan-v2"


def hashed(raw):
    return hashlib.sha256(raw).hexdigest() if raw is not None else None


def source_hashes(snapshot, plan_format=FORMAT):
    from . import catalog_transaction as tx
    if plan_format != FORMAT: snapshot = tx.historical_snapshot(snapshot)
    return {**snapshot["retained"], **{n: hashed(b) for n, b in snapshot["texts"].items()}}


def validate_plan(plan):
    exact_keys(plan, {"format", "run_id", "base_commit", "sources", "evidence", "entries"})
    require(plan["format"] in (FORMAT, LEGACY_FORMAT) and len(canonical_bytes(plan)) + 1 <= added.REPORT_LIMIT, "Invalid added plan format/size")
    added.report_path(plan["run_id"])
    added.commit(plan["base_commit"])
    require(isinstance(plan["sources"], dict) and len(plan["sources"]) <= (80003 if plan["format"] == FORMAT else 100003), "Invalid added source map")
    for n, h in plan["sources"].items():
        relative(n)
        if h is not None: sha(h)
    require(isinstance(plan["evidence"], list), "Invalid added evidence list")
    evidence = {}
    for e in plan["evidence"]:
        exact_keys(e, {"key", "kind", "commit", "path", "content", "sha256", "reference_time", "integration"})
        require(isinstance(e["key"], str) and e["key"] and e["key"] not in evidence and
                e["kind"] in ("checkout", "direct", "git-snapshot"), "Invalid added evidence identity")
        added.commit(e["commit"]); relative(e["path"]); added.timestamp(e["reference_time"])
        require(isinstance(e["content"], str) and sha(e["sha256"]) == hashed(e["content"].encode()), "Wrong added evidence hash")
        require(e["integration"] is None or isinstance(e["integration"], dict), "Invalid added integration evidence")
        if e["kind"] == "git-snapshot":
            integration = exact_keys(e["integration"], {"kind", "base_commit", "merge_commit", "pull_request", "categories", "runtime", "bindings"})
            require(integration["kind"] in ("main", "pull-request") and integration["base_commit"] == plan["base_commit"], "Invalid snapshot integration")
            added.commit(integration["merge_commit"])
            if integration["kind"] == "main":
                require(e["commit"] == integration["merge_commit"] and integration["pull_request"] is None, "Invalid main snapshot")
            else:
                pr = exact_keys(integration["pull_request"], {"number", "url", "state", "mergedAt", "mergeCommit", "headRefOid", "commits"})
                require(pr["state"] == "MERGED" and pr["mergeCommit"] == {"oid": integration["merge_commit"]} and
                        isinstance(pr["mergedAt"], str) and type(pr["number"]) is int and pr["number"] > 0 and
                        isinstance(pr["url"], str) and isinstance(pr["commits"], list) and
                        any(c.get("oid") == e["commit"] for c in pr["commits"]), "Unbound historical PR snapshot")
                added.commit(pr["headRefOid"])
            require(isinstance(integration["categories"], str) and isinstance(integration["runtime"], str) and isinstance(integration["bindings"], dict), "Invalid snapshot payload")
            from . import content_registry as cr, categories
            registry = rating.bytes_json(e["content"].encode(), added.REPORT_LIMIT)
            catalog = rating.bytes_json(integration["categories"].encode(), 131072)
            production = {"format": registry.get("format"), "entries": [r for r in registry.get("entries", []) if r.get("production") is not None]}
            cr.validate(production, catalog)
            runtime = rating.bytes_json(integration["runtime"].encode(), added.REPORT_LIMIT)
            require(runtime.get("format") in ("picross-runtime-registry-v2", "picross-runtime-registry-v3", "picross-runtime-registry-v4") and
                    runtime.get("categories") == categories.ordered(catalog), "Invalid historical runtime categories/version")
            runtime_ids = {r["id"]: r for r in runtime["entries"]}
            require(len(runtime_ids) == len(runtime["entries"]), "Duplicate snapshot runtime ID")
            by_id = {r["id"]: r for r in production["entries"]}
            for identifier, bindings in integration["bindings"].items():
                require(identifier in by_id, "Foreign snapshot binding")
                row = by_id[identifier]; p = row["production"]
                require(bindings == {p["package"] + "/manifest.json": p["package_sha256"],
                                    "game/" + row["definition"]: p["definition_sha256"], "game/" + row["reveal"]: p["reveal_sha256"]} and
                        all(runtime_ids.get(identifier, {}).get(k) == row[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")), "Invalid historical playable binding")
        elif e["kind"] == "direct":
            receipt = exact_keys(rating.bytes_json(e["content"].encode(), added.LIMIT), {"id", "event", "success", "registered_at"})
            rating.identity(receipt["id"])
            require(receipt["event"] == "first-playable-registration" and receipt["success"] is True and
                    added.timestamp(receipt["registered_at"]) == e["reference_time"], "Invalid direct first-registration receipt")
        evidence[e["key"]] = e
    require(isinstance(plan["entries"], list) and len(plan["entries"]) <= 10000, "Invalid added entries")
    ids = []
    for row in plan["entries"]:
        exact_keys(row, {"id", "old", "old_record", "proposed", "kind", "reference_time", "commit", "evidence", "reason"})
        ids.append(rating.identity(row["id"]))
        added.timestamp(row["old"]); added.timestamp(row["proposed"])
        if row["old_record"] is not None:
            require(isinstance(row["old_record"], str), "Invalid old added record")
            previous = added.validate(rating.bytes_json(row["old_record"].encode(), added.LIMIT), row["id"])
            require(previous["added_at"] == row["old"], "Wrong old added value")
        require(plan["sources"].get(added.path(row["id"])) == hashed(row["old_record"].encode() if row["old_record"] else None),
                "Wrong old added source binding")
        if row["old_record"] is not None:
            p = previous["provenance"]
            require(row["proposed"] == row["old"] and row["evidence"] is None and
                    all(row[k] == p[k] for k in ("kind", "reference_time", "commit", "reason")), "Existing added metadata must be retained")
            continue
        if row["evidence"] is not None:
            require(row["evidence"] in evidence, "Missing added evidence")
            e = evidence[row["evidence"]]
            require(e["kind"] == row["kind"] and e["commit"] == row["commit"] and
                    e["reference_time"] == row["proposed"], "Conflicting added source evidence")
            if row["kind"] == "git-snapshot":
                snapshot = rating.bytes_json(e["content"].encode(), added.REPORT_LIMIT)
                require(any(x.get("id") == row["id"] and x.get("visible") is True for x in snapshot.get("entries", [])),
                        "Snapshot does not show a visible ID")
                require(row["id"] in e["integration"]["bindings"], "Missing playable snapshot binding")
            elif row["kind"] == "direct":
                require(rating.bytes_json(e["content"].encode(), added.LIMIT)["id"] == row["id"], "Direct evidence belongs to another ID")
        else:
            require(row["kind"] == "unknown", "Known date requires evidence")
        # Validate the record shape without a circular plan hash.
        _record(row, added.report_path(plan["run_id"]), "0" * 64)
    require(ids == sorted(set(ids)), "Added plan IDs must be unique and ordered")
    require([e["key"] for e in plan["evidence"]] == sorted(evidence), "Added evidence must be ordered")
    return plan


def _record(row, name, checksum):
    return added.validate({"format": added.FORMAT, "id": row["id"], "added_at": row["proposed"],
        "provenance": {"kind": row["kind"], "reference_time": row["reference_time"], "commit": row["commit"],
                       "evidence": {"path": name, "sha256": checksum}, "reason": row["reason"]}})


def record_for(plan, identifier, raw):
    row = next((r for r in plan["entries"] if r["id"] == identifier), None)
    require(row is not None, "ID absent from added report")
    if row["old_record"] is not None:
        return added.validate(rating.bytes_json(row["old_record"].encode(), added.LIMIT), identifier)
    return _record(row, added.report_path(plan["run_id"]), hashed(raw))


def validate_delta(j, before):
    from . import catalog_transaction as tx
    name = added.report_path(j["report_run"])
    require(j["old"][name] is None and isinstance(j["new"][name], str), "Added report must be new")
    raw = j["new"][name].encode()
    plan = validate_plan(rating.bytes_json(raw, added.REPORT_LIMIT))
    require(plan["run_id"] == j["report_run"] and [r["id"] for r in plan["entries"]] == [e["id"] for e in before["entries"]],
            "Added plan catalog selection changed")
    captured = {"retained": j["retained"], "texts": {n: b.encode() if b is not None else None
                for n, b in j["old"].items() if n != name}}
    require(source_hashes(captured, plan["format"]) == plan["sources"], "Added plan sources changed")
    for row in plan["entries"]:
        n = added.path(row["id"])
        require(j["old"][n] == row["old_record"] and j["new"][n].encode() == added.encoded(record_for(plan, row["id"], raw)),
                "Wrong added adoption delta")


def adopt(root, plan_path, *, apply=False, fail_step=None):
    from . import catalog_transaction as tx
    root = catalog_io.external(root)
    raw = rating.read_file(plan_path, added.REPORT_LIMIT)
    plan = validate_plan(rating.bytes_json(raw, added.REPORT_LIMIT))
    require(raw == canonical_bytes(plan) + b"\n", "Added plan must be canonical")
    snapshot = tx.capture(root)
    if plan["format"] != FORMAT: tx.historical_snapshot(snapshot)
    require([e["id"] for e in snapshot["registry"]["entries"]] == [r["id"] for r in plan["entries"]], "Added catalog changed")
    name = added.report_path(plan["run_id"])
    changes = {added.path(r["id"]): added.encoded(record_for(plan, r["id"], raw)) for r in plan["entries"]}
    existing = tx.read(root, name)
    if existing is not None:
        require(existing == raw and all(snapshot["texts"][n] == b for n, b in changes.items()), "Added adoption changed; create a new plan")
        original = deepcopy(snapshot)
        original["retained"].pop(name, None)
        for row in plan["entries"]:
            original["texts"][added.path(row["id"])] = row["old_record"].encode() if row["old_record"] else None
        e = next((e for e in plan["evidence"] if e["key"] == "checkout-runtime"), None)
        require(e is not None and e["sha256"] == plan["sources"][tx.RUNTIME], "Missing original runtime evidence")
        original["texts"][tx.RUNTIME] = e["content"].encode()
        require(source_hashes(original, plan["format"]) == plan["sources"], "Added sources changed since adoption")
        return {"status": "no-op", "changes": []}
    require(source_hashes(snapshot, plan["format"]) == plan["sources"], "Added sources changed since plan")
    if all(snapshot["texts"][n] == b for n, b in changes.items()):
        return {"status": "no-op", "changes": []}
    changes[name] = raw
    journal = tx.prepare(root, snapshot, changes, operation="added-adoption", report_run=plan["run_id"])
    require(plan_path.read_bytes() == raw, "Added plan changed during preparation")
    if apply: tx.execute(root, journal, fail_step=fail_step)
    return {"status": "adopted" if apply else "planned-adoption", "changes": sorted(changes)}


def plan(root, run, base, *, repository=None, direct=()):
    """Read-only editorial reconstruction; no checkout, analysis or production replay.

    GitHub is consulted only when explicitly supplied, to bind squash PR history.
    Direct evidence is explicit reviewed input, never inferred from file mtimes.
    """
    import json
    import re
    import subprocess
    from datetime import datetime, timezone
    from . import catalog_transaction as tx, content_registry as cr, categories

    root = catalog_io.external(root)
    snapshot = tx.capture(root)
    added.commit(base); added.report_path(run)
    existing = tx.read(root, added.report_path(run))
    if existing is not None:
        prior = validate_plan(rating.bytes_json(existing, added.REPORT_LIMIT))
        require(prior["base_commit"] == base, "Existing added plan has another history base")
        require(adopt(root, root / added.report_path(run))["status"] == "no-op", "Existing added plan is stale")
        return prior

    def git(*args, optional=False):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
        require(optional or result.returncode == 0, "Historical Git read failed: " + result.stderr.decode(errors="replace"))
        return result.stdout if result.returncode == 0 else None

    def show(commit, name): return git("show", commit + ":" + name, optional=True)

    require(git("rev-parse", base).decode().strip() == base, "Unknown history base")
    identifiers = {e["id"] for e in snapshot["registry"]["entries"]}
    candidates = {identifier: [] for identifier in identifiers}
    evidence = {"checkout-runtime": {"key": "checkout-runtime", "kind": "checkout", "commit": base,
        "path": tx.RUNTIME, "content": snapshot["texts"][tx.RUNTIME].decode(), "sha256": hashed(snapshot["texts"][tx.RUNTIME]),
        "reference_time": None, "integration": None}}
    seen = set()

    def scan(commit, integration, wanted):
        if commit in seen: return set()
        seen.add(commit)
        raw = show(commit, tx.REGISTRY)
        cats = show(commit, categories.PATH)
        runtime_raw = show(commit, tx.RUNTIME)
        if raw is None or cats is None or runtime_raw is None: return set()
        registry = rating.bytes_json(raw, 8 * 1024 * 1024)
        if registry.get("format") != cr.FORMAT: return set()
        # Retired F-xx prototype entries had a null production field. Validate
        # the categorized production subset without executing historical code.
        production = {"format": cr.FORMAT, "entries": [e for e in registry["entries"] if e.get("production") is not None]}
        cr.validate(production, rating.bytes_json(cats, 131072))
        runtime = rating.bytes_json(runtime_raw, 8 * 1024 * 1024)
        require(runtime.get("format") in ("picross-runtime-registry-v2", "picross-runtime-registry-v3", "picross-runtime-registry-v4"), "Unsupported historical runtime")
        runtime_ids = {e["id"]: e for e in runtime["entries"]}
        require(len(runtime_ids) == len(runtime["entries"]), "Duplicate historical runtime ID")
        date = datetime.fromisoformat(git("show", "-s", "--format=%cI", commit).decode().strip()).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        found = set()
        bindings = {}
        for entry in production["entries"]:
            if entry["id"] not in wanted or not entry["visible"]: continue
            projected = runtime_ids.get(entry["id"], {})
            if any(projected.get(k) != entry[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")): continue
            p = entry["production"]
            paths = {p["package"] + "/manifest.json": p["package_sha256"],
                     "game/" + entry["definition"]: p["definition_sha256"], "game/" + entry["reveal"]: p["reveal_sha256"]}
            if not all(hashed(show(commit, n)) == h for n, h in paths.items()): continue
            bindings[entry["id"]] = paths
            found.add(entry["id"])
        if found:
            key = "git-" + commit
            evidence[key] = {"key": key, "kind": "git-snapshot", "commit": commit, "path": tx.REGISTRY,
                "content": raw.decode(), "sha256": hashed(raw), "reference_time": date,
                "integration": {**integration, "categories": cats.decode(), "runtime": runtime_raw.decode(), "bindings": bindings}}
            for identifier in found: candidates[identifier].append((date, key))
        return found

    commits = git("log", "--reverse", "--format=%H", base, "--", tx.REGISTRY).decode().splitlines()
    introduced = set()
    for commit in commits:
        found = scan(commit, {"kind": "main", "base_commit": base, "merge_commit": commit, "pull_request": None}, identifiers - introduced)
        first = found - introduced
        introduced |= found
        if not first or repository is None: continue
        subject = git("show", "-s", "--format=%s", commit).decode()
        match = re.search(r"\(#([0-9]+)\)$", subject)
        if not match: continue
        number = match.group(1)
        result = subprocess.run(["gh", "pr", "view", number, "--repo", repository, "--json",
                                 "number,url,state,mergedAt,mergeCommit,headRefOid,commits"], capture_output=True)
        require(result.returncode == 0, "Cannot verify historical PR " + number)
        pr = json.loads(result.stdout)
        require(pr["state"] == "MERGED" and pr["mergeCommit"]["oid"] == commit and pr["mergedAt"], "Historical PR integration mismatch")
        # Fetch immutable objects if they were not retained by the local clone.
        if git("cat-file", "-e", pr["headRefOid"] + "^{commit}", optional=True) is None:
            git("fetch", "origin", "refs/pull/" + number + "/head:refs/ku-b-history/" + number)
        for item in pr["commits"]:
            oid = item["oid"]
            require(git("merge-base", "--is-ancestor", oid, pr["headRefOid"], optional=True) is not None, "PR source is not an ancestor of bound head")
            scan(oid, {"kind": "pull-request", "base_commit": base, "merge_commit": commit, "pull_request": pr}, first)
    # A direct receipt must name the ID and the successful first playable event.
    # Multiple conflicting direct times deliberately produce unknown, not fallback.
    for e in direct:
        require(e["kind"] == "direct" and e["key"] not in evidence, "Duplicate/invalid direct evidence")
        evidence[e["key"]] = e
    rows = []
    used = {"checkout-runtime"} | {e["key"] for e in direct}
    for identifier in sorted(identifiers):
        previous = snapshot["texts"][added.path(identifier)]
        if previous is not None:
            current = added.validate(rating.bytes_json(previous, added.LIMIT), identifier)
            p = current["provenance"]
            rows.append({"id": identifier, "old": current["added_at"], "old_record": previous.decode(),
                         "proposed": current["added_at"], "evidence": None,
                         **{k: p[k] for k in ("kind", "reference_time", "commit", "reason")}})
            continue
        receipts = []
        for e in direct:
            receipt = rating.bytes_json(e["content"].encode(), added.LIMIT)
            exact_keys(receipt, {"id", "event", "success", "registered_at"})
            require(receipt["event"] == "first-playable-registration" and receipt["success"] is True and
                    added.timestamp(receipt["registered_at"]) == e["reference_time"], "Invalid direct registration receipt")
            if receipt["id"] == identifier: receipts.append(e)
        if receipts and len({e["reference_time"] for e in receipts}) == 1:
            selected = min(receipts, key=lambda e: e["key"])
            reason = "Unique direct successful first playable registration receipt; priority 1."
        elif receipts:
            selected = None
            reason = "Conflicting direct first-registration receipts; no unique UTC event can be established."
        elif candidates[identifier]:
            _, key = min(candidates[identifier])
            selected = evidence[key]
            reason = "No direct UTC first-registration receipt found in reviewed sources; earliest verified visible integrated catalog snapshot including bound PR history. Commit UTC is a reconstructed reference, not tool execution time."
        else:
            selected = None
            reason = "No direct successful first-registration receipt and no valid visible integrated catalog snapshot for this ID in the bound history."
        if selected: used.add(selected["key"])
        rows.append({"id": identifier, "old": None, "old_record": None,
            "proposed": selected["reference_time"] if selected else None, "kind": selected["kind"] if selected else "unknown",
            "reference_time": selected["reference_time"] if selected else None, "commit": selected["commit"] if selected else None,
            "evidence": selected["key"] if selected else None, "reason": reason})
    return validate_plan({"format": FORMAT, "run_id": run, "base_commit": base, "sources": source_hashes(snapshot),
        "evidence": [evidence[key] for key in sorted(used)], "entries": rows})


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
