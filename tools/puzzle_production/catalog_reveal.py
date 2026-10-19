"""Plan and adopt explicitly approved image revisions, without changing puzzles."""
import argparse
from copy import deepcopy
from pathlib import Path
import signal
import sys
import tempfile

from .authoring_package import require, relative, sha
from .contract import Aborted, InvalidInput, canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io, reveal_source as reveal, catalog_transaction as tx
from . import catalog_publication as publication, categories

REQUEST = "picross-reveal-request-v1"
FORMAT = "picross-reveal-plan-v1"
RESULT = "picross-reveal-result-v1"
PLAN_LIMIT = 128 * 1024 * 1024


def text_record(raw):
    return {"text": raw.decode("utf-8"), "sha256": io.checksum(raw)} if raw is not None else None


def source_hashes(snapshot):
    return {**snapshot["retained"], **{n: io.checksum(v) for n, v in snapshot["texts"].items()}}


def selection(ids):
    require(isinstance(ids, list) and 1 <= len(ids) <= 10000, "Select 1..10000 reveal IDs")
    for identifier in ids: reveal.path(identifier)
    require(len(ids) == len(set(ids)), "Duplicate reveal ID")
    return sorted(ids)


def outside(path, root):
    path = io.external(path)
    require(not path.is_relative_to(root) and not root.is_relative_to(path), "Reveal work must be outside checkout")
    return path


def image_input(directory, name, suffix, width, height):
    from .target_adapter import validate_reveal
    relative(name)
    require(Path(name).suffix == suffix, "Reveal image suffix must match registered path")
    raw = io.read(directory, name, reveal.IMAGE_LIMIT)
    validate_reveal(io.safe(directory, name), width, height)
    require(io.read(directory, name, reveal.IMAGE_LIMIT) == raw, "Reveal input changed while validating")
    return raw


def changes(old, new, replacements):
    result = []
    for name in sorted(set(old) | set(replacements)):
        if name in replacements:
            pair = replacements[name]
            result.append({"path": name, "kind": "binary-replace", "old_sha256": pair["old"]["sha256"],
                           "new_sha256": pair["new"]["sha256"], "bytes": pair["new"]["bytes"]})
        elif old[name] != new[name]:
            result.append({"path": name, "kind": "text-add" if old[name] is None else "text-replace",
                           "old_sha256": io.checksum(old[name].encode() if old[name] is not None else None),
                           "new_sha256": io.checksum(new[name].encode()), "bytes": len(new[name].encode())})
    return result


def build(root, ids, requests, input_dir):
    snapshot = tx.capture(root)
    entries = {e["id"]: e for e in snapshot["registry"]["entries"]}
    require(set(ids) <= set(entries), "Unknown reveal ID")
    catalog = io.json_bytes(snapshot["texts"][categories.PATH], 131072)
    rows, writes, replacements, files, total = [], {}, {}, {}, 0
    for identifier in ids:
        io.tick()
        request = requests[identifier]
        entry = entries[identifier]
        suffix = Path(entry["reveal"]).suffix
        image = image_input(input_dir, request["image"], suffix, entry["production"]["width"], entry["production"]["height"])
        previous = io.read(root, "game/" + entry["reveal"], reveal.IMAGE_LIMIT)
        total += len(image) + len(previous)
        if total > 96 * 1024 * 1024: raise Aborted("resource_limit: reveal plan images exceed 96 MiB")
        record = reveal.revise(root, entry, catalog, io.checksum(image), request["approval"], request["provenance"], request["notice_append"])
        old_record = snapshot["texts"][reveal.path(identifier)]
        new_record = canonical_bytes(record) + b"\n"
        notice_path = reveal.identity(entry)["notice"]
        writes[reveal.path(identifier)] = new_record
        writes[notice_path] = record["revisions"][-1]["notice"]["text"].encode()
        replacements["game/" + entry["reveal"]] = {"old": publication.binary(previous), "new": publication.binary(image)}
        old_file, new_file = "previous/" + identifier + suffix, "images/" + identifier + suffix
        files.update({old_file: previous, new_file: image})
        rows.append({"id": identifier, "old_image_revision": record["current"]["image_revision"] - 1,
                     "new_image_revision": record["current"]["image_revision"], "binding_hash": record["bindings"][-1]["binding_hash"],
                     "old_reveal": {"file": old_file, "sha256": io.checksum(previous), "bytes": len(previous)},
                     "new_reveal": {"file": new_file, "sha256": io.checksum(image), "bytes": len(image)},
                     "old_record": text_record(old_record), "new_record": text_record(new_record),
                     "old_notice": text_record(snapshot["texts"][notice_path]), "new_notice": text_record(writes[notice_path])})
    journal = tx.prepare(root, snapshot, writes, operation="reveal-adoption", replacements=replacements)
    sources = source_hashes(snapshot)
    require(len(sources) <= 100000, "Too many reveal plan sources")
    plan = {"format": FORMAT, "ids": ids, "snapshot": {"sources": sources, "namespaces": snapshot["namespaces"]},
            "entries": rows, "writes": changes(journal["old"], journal["new"], replacements)}
    plan["plan_hash"] = digest(plan)
    if len(canonical_bytes(plan)) + 1 > PLAN_LIMIT: raise Aborted("resource_limit: reveal plan exceeds 128 MiB")
    require(source_hashes(tx.capture(root)) == sources and tx.namespaces(root, snapshot["registry"]) == snapshot["namespaces"], "Checkout changed during reveal planning")
    return plan, journal, files


def result(status, plan=None, *, error=None, recovery_required=False):
    return {"format": RESULT, "status": status, "plan_hash": plan["plan_hash"] if plan else None,
            "ids": plan["ids"] if plan else [], "changes": plan["writes"] if plan and status != "no-op" else [],
            "error": error, "recovery_required": recovery_required}


def plan(root, ids, input_path, output, *, seconds=300):
    with io.budget(seconds):
        root = io.external(root)
        ids = selection(ids)
        input_path, output = outside(input_path, root), outside(output, root)
        require(not output.exists(), "Reveal output directory must be new")
        require(not output.is_relative_to(input_path.parent) and not input_path.parent.is_relative_to(output), "Reveal input/output directories overlap")
        raw = io.read(input_path.parent, input_path.name, 8 * 1024 * 1024)
        request = exact_keys(io.json_bytes(raw, 8 * 1024 * 1024), {"format", "entries"})
        require(request["format"] == REQUEST and isinstance(request["entries"], list), "Invalid reveal request")
        requests = {}
        for row in request["entries"]:
            exact_keys(row, {"id", "image", "approval", "provenance", "notice_append"})
            reveal.path(row['id'])
            require(row["id"] not in requests, "Duplicate reveal request ID")
            requests[row["id"]] = row
        require(selection(list(requests)) == ids, "Reveal selection differs from request")
        value, _, files = build(root, ids, requests, input_path.parent)
        require(io.read(input_path.parent, input_path.name, 8 * 1024 * 1024) == raw, "Reveal request changed")
        output.mkdir(parents=True, exist_ok=False)
        for name, data in {"plan.json": canonical_bytes(value) + b"\n", **files}.items():
            target = io.safe(output, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream: stream.write(data)
        return result("planned", value)


def validate_plan(value):
    exact_keys(value, {"format", "ids", "snapshot", "entries", "writes", "plan_hash"})
    require(value["format"] == FORMAT and value["ids"] == selection(value["ids"]), "Invalid reveal plan")
    require(sha(value["plan_hash"]) == digest({k: v for k, v in value.items() if k != "plan_hash"}), "Wrong reveal plan hash")
    snap = exact_keys(value["snapshot"], {"sources", "namespaces"})
    require(isinstance(snap["sources"], dict) and len(snap["sources"]) <= 100000, "Invalid reveal source map")
    for name, h in snap["sources"].items():
        relative(name)
        if h is not None: sha(h)
    exact_keys(snap["namespaces"], {"reveals", "difficulty", "added", "packages"})
    for paths in snap["namespaces"].values():
        require(isinstance(paths, list) and len(paths) <= 100000 and all(isinstance(n,str) for n in paths) and
                paths == sorted(set(paths)), "Invalid reveal namespace snapshot")
        for name in paths: relative(name)
    require(isinstance(value["entries"], list) and len(value["entries"]) == len(value["ids"]), "Invalid reveal entries")
    for identifier, row in zip(value["ids"], value["entries"]):
        exact_keys(row, {"id", "old_image_revision", "new_image_revision", "binding_hash", "old_reveal", "new_reveal", "old_record", "new_record", "old_notice", "new_notice"})
        require(identifier == row["id"], "Wrong reveal entry order")
        integer(row["old_image_revision"], 0, 255, "old image revision")
        integer(row["new_image_revision"], 1, 256, "new image revision")
        require(row["new_image_revision"] == row["old_image_revision"] + 1, "Wrong image revision delta")
        sha(row["binding_hash"])
        for side, prefix in (("old", "previous/"), ("new", "images/")):
            image = exact_keys(row[side + "_reveal"], {"file", "sha256", "bytes"})
            integer(image["bytes"], 1, reveal.IMAGE_LIMIT, "reveal image bytes"); sha(image["sha256"])
            require(image["file"] in [prefix + identifier + ext for ext in (".png", ".svg")], "Wrong plan image path")
            for kind in ("record", "notice"):
                record = row[side + "_" + kind]
                if kind == "record" and side == "old" and record is None: continue
                exact_keys(record, {"text", "sha256"})
                require(isinstance(record["text"], str) and io.checksum(record["text"].encode()) == sha(record["sha256"]), "Invalid plan text binding")
                require(len(record["text"].encode()) <= (reveal.LIMIT if kind == "record" else 65536), "Plan text exceeds source limit")
    require(isinstance(value["writes"], list), "Invalid reveal write list")
    for row in value["writes"]:
        exact_keys(row, {"path", "kind", "old_sha256", "new_sha256", "bytes"})
        relative(row["path"]); sha(row["new_sha256"])
        if row["old_sha256"] is not None: sha(row["old_sha256"])
        integer(row["bytes"], 1, reveal.IMAGE_LIMIT, "planned write bytes")
        require(row["kind"] in ("binary-replace", "text-add", "text-replace"), "Invalid reveal write kind")
    return value


def validate_delta(j, before, root):
    """Enforce append-only history and fixed definitions/metadata independently."""
    mutable, expected_images = set(), set()
    catalog = io.json_bytes(j["old"][categories.PATH].encode(), 131072)
    for entry in before["entries"]:
        name = reveal.path(entry["id"])
        if j["old"][name] == j["new"][name]: continue
        require(j["new"][name] is not None, "Cannot delete reveal history")
        new = reveal.validate(io.json_bytes(j["new"][name].encode(), reveal.LIMIT), catalog)
        old = reveal.validate(io.json_bytes(j["old"][name].encode(), reveal.LIMIT), catalog) if j["old"][name] is not None else None
        require(new["id"] == entry["id"] and new["identity"] == reveal.identity(entry), "Reveal delta changes identity")
        n = reveal.identity(entry)["notice"]
        if old:
            require(all(new[k] == old[k] for k in ("origin", "identity", "bindings")) and
                    new["revisions"][:-1] == old["revisions"] and len(new["revisions"]) == len(old["revisions"]) + 1 and
                    new["record_revision"] == old["record_revision"] + 1, "Reveal delta rewrites history")
            previous = old["revisions"][-1]["reveal_sha256"]
        else:
            original, _, integrated, _ = reveal.package(root, entry)
            definition = io.json_bytes(j['old']['game/' + entry['definition']].encode(), 2 * 1024 * 1024)
            expected_origin = {'entry': original, 'runtime_revision': definition['revision'],
                               'notice': reveal.make_notice(j['old'][n].encode()), 'receipt': integrated}
            require(len(new["revisions"]) == len(new["bindings"]) == new["record_revision"] == 1 and
                    new["origin"] == expected_origin, "Invalid first reveal origin")
            previous = entry["production"]["reveal_sha256"]
        revision = new["revisions"][-1]
        require(revision["binding_hash"] == new["bindings"][-1]["binding_hash"] and
                revision["previous_reveal_sha256"] == previous and revision["notice"]["text"] == j["new"][n] and
                j["new"][n].startswith(j["old"][n]), "Invalid active reveal delta")
        image = "game/" + entry["reveal"]
        expected_images.add(image)
        pair = j["replacements"].get(image)
        require(pair is not None and pair["old"]["sha256"] == previous and pair["new"]["sha256"] == revision["reveal_sha256"], "Reveal binary delta differs")
        mutable |= {name, n}
    require(expected_images == set(j["replacements"]) and expected_images, "Reveal replacement set differs")
    return mutable


def load_plan(path):
    raw = io.read(path.parent, path.name, PLAN_LIMIT)
    value = validate_plan(io.json_bytes(raw, PLAN_LIMIT))
    require(path.name == "plan.json" and raw == canonical_bytes(value) + b"\n", "Noncanonical reveal plan file")
    expected = {"plan.json"} | {row[side + "_reveal"]["file"] for row in value["entries"] for side in ("old", "new")}
    found = set()
    for p in path.parent.rglob("*"):
        name = p.relative_to(path.parent).as_posix()
        p = io.safe(path.parent, name)
        require(p.is_file() or name in ("images", "previous"), "Unexpected reveal plan directory")
        if p.is_file(): found.add(name)
    require(found == expected, "Reveal plan file inventory differs")
    total = 0
    for row in value["entries"]:
        for side in ("old", "new"):
            ref = row[side + "_reveal"]
            raw_image = io.read(path.parent, ref["file"], reveal.IMAGE_LIMIT)
            require(len(raw_image) == ref["bytes"] and io.checksum(raw_image) == ref["sha256"], "Plan image binding changed")
            total += len(raw_image)
    if total > 96 * 1024 * 1024: raise Aborted("resource_limit: reveal plan images exceed 96 MiB")
    return value, raw


def adopt(root, path, *, seconds=300, fail_step=None):
    with io.budget(seconds):
        root = io.external(root)
        path = outside(path, root)
        value, raw = load_plan(path)
        snapshot = tx.capture(root)
        entries = {e["id"]: e for e in snapshot["registry"]["entries"]}
        require(set(value["ids"]) <= set(entries), "Stale reveal selection")
        old_texts = deepcopy(snapshot["texts"])
        original_hashes = source_hashes(snapshot)
        target = True
        requests = {}
        for row in value["entries"]:
            entry = entries[row["id"]]
            record_name, notice_name = reveal.path(row["id"]), reveal.identity(entry)["notice"]
            for name, kind in ((record_name, "record"), (notice_name, "notice")):
                previous = row["old_" + kind]
                previous = previous["text"].encode() if previous is not None else None
                current = row["new_" + kind]["text"].encode()
                require(snapshot["texts"][name] in (previous, current), "Stale reveal source: " + name)
                target &= snapshot["texts"][name] == current
                old_texts[name] = previous; original_hashes[name] = io.checksum(previous)
            image_name = "game/" + entry["reveal"]
            require(snapshot["retained"][image_name] in (row["old_reveal"]["sha256"], row["new_reveal"]["sha256"]), "Stale reveal image")
            target &= snapshot["retained"][image_name] == row["new_reveal"]["sha256"]
            original_hashes[image_name] = row["old_reveal"]["sha256"]
            record = reveal.validate(io.json_bytes(row["new_record"]["text"].encode(), reveal.LIMIT),
                                     io.json_bytes(snapshot['texts'][categories.PATH], 131072))
            revision = record["revisions"][-1]
            prior_notice, next_notice = row["old_notice"]["text"], row["new_notice"]["text"]
            require(next_notice == prior_notice or next_notice.startswith(prior_notice + "\n"), "Notice is not an exact append")
            requests[row["id"]] = {"id": row["id"], "image": row["new_reveal"]["file"],
                                    "approval": revision["approval"], "provenance": revision["provenance"],
                                    "notice_append": None if next_notice == prior_notice else next_notice[len(prior_notice) + 1:]}
        require(original_hashes == value["snapshot"]["sources"], "Stale reveal plan sources")
        # A mixture is never a repetition. With no lock it is also not a valid
        # old checkout, so compare all selected targets to the complete old view.
        if not target:
            require(source_hashes(snapshot) == original_hashes, "Partial reveal target is not a no-op")
        with tempfile.TemporaryDirectory(prefix="at-old-check-") as directory:
            stage = Path(directory)
            old_images = {"game/" + entries[row["id"]]["reveal"]: row["old_reveal"]["file"] for row in value["entries"]}
            for name in sorted(set(old_texts) | set(snapshot["retained"])):
                data = (old_texts[name] if name in old_texts else io.read(path.parent, old_images[name], reveal.IMAGE_LIMIT)
                        if name in old_images else tx.read(root, name))
                if data is not None:
                    p = stage / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
            reconstructed, journal, _ = build(stage, value["ids"], requests, path.parent)
            require(reconstructed == value, "Reveal plan differs from independently derived operations")
            # Bind source-root policy explicitly; temporary validation never
            # authorizes synthetic approvals in the real catalog.
            from .content_registry import ROOT
            require(root != ROOT.resolve() or all(not entries[i]["production"]["test_only"] for i in value["ids"]), "Test-only reveals cannot enter the real catalog")
            def fresh():
                require(load_plan(path) == (value, raw), "Reveal plan changed during adoption")
            fresh()
            require(source_hashes(tx.capture(root)) == source_hashes(snapshot) and tx.namespaces(root, snapshot["registry"]) == snapshot["namespaces"], "Checkout changed before adoption")
            if target: return result("no-op", value)
            publication.execute(root, journal, fail_step=fail_step, under_lock=fresh)
        return result("adopted", value)


class Parser(argparse.ArgumentParser):
    def error(self, message): raise InvalidInput(message)


class Once(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        seen = getattr(namespace, '_once', set())
        require(self.dest not in seen, 'Duplicate option: ' + str(option_string))
        seen.add(self.dest); setattr(namespace, '_once', seen); setattr(namespace, self.dest, value)


def main(argv=None):
    parser = Parser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "adopt"):
        p = sub.add_parser(command, allow_abbrev=False)
        p.add_argument("--checkout", type=Path, required=True, action=Once)
        p.add_argument("--seconds", type=int, default=300, action=Once)
        if command == "plan":
            p.add_argument("--id", action="append", required=True)
            p.add_argument("--input", type=Path, required=True, action=Once)
            p.add_argument("--output-dir", type=Path, required=True, action=Once)
        else: p.add_argument("--plan", type=Path, required=True, action=Once)
    args = None
    def interrupted(signum, frame): raise Aborted("interrupted: signal " + str(signum))
    for s in (signal.SIGTERM, signal.SIGINT): signal.signal(s, interrupted)
    try:
        args = parser.parse_args(argv)
        answer = plan(args.checkout, args.id, args.input, args.output_dir, seconds=args.seconds) if args.command == "plan" else adopt(args.checkout, args.plan, seconds=args.seconds)
        code = 0
    except (ValueError, OSError, Aborted, KeyboardInterrupt, MemoryError) as exc:
        aborted = isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError))
        message = str(exc)[:2048] or "Interrupted"
        error = ("interrupted" if isinstance(exc, KeyboardInterrupt) or message.startswith("interrupted:") else "resource_limit") if aborted else (
            "io_error" if isinstance(exc, OSError) else "stale" if "stale" in message.lower() else "conflict" if any(w in message.lower() for w in ("changed", "foreign", "collision")) else "invalid_input")
        pending = bool(args and ((args.checkout / tx.LOCK).exists() or list((args.checkout / "content").glob(".registration-journal-*.tmp"))))
        answer = result("aborted" if aborted else "invalid_input", error={"code": error, "message": message}, recovery_required=pending)
        code = 4 if aborted else 2
    print(canonical_bytes(answer).decode("utf-8"))
    return code


if __name__ == "__main__": sys.exit(main())
