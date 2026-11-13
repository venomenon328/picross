"""Plan/adopt one authorized background revision through the common catalog writer."""
from copy import deepcopy
from pathlib import Path
import os
import re
import signal
import sys
import tempfile

from . import background_request as requests, background_package as package
from . import catalog_background as bg, catalog_io as io, catalog_transaction as tx
from . import catalog_publication as publication
from .authoring_package import require, relative, sha
from .contract import Aborted, InvalidInput, canonical_bytes, digest, exact_keys
from .background_contract import BackgroundError

FORMAT = "picross-background-adoption-plan-v1"
REBIND_FORMAT = "picross-background-adoption-plan-v2"
IMAGE_FORMAT = "picross-background-adoption-plan-v3"
RESULT = "picross-background-adoption-result-v1"
PLAN_LIMIT = 24 * 1024 * 1024
validate_request = requests.validate


def checkpoint(name):
    """Interruption/race boundary; no production success injection."""
    io.tick()


def _publication_error(exc, remaining):
    from .authoring_builder import BuildError
    error = BuildError(str(exc) or "Interrupted background publication", remaining)
    error.aborted = isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError))
    error.code = "interrupted" if error.aborted else "io_error" if isinstance(exc, OSError) else "conflict"
    return error


def source_hashes(snapshot):
    if tx.image_generation(snapshot):
        return tx.image_snapshot(snapshot)["sources"]
    return {**snapshot["retained"], **{name: io.checksum(raw) for name, raw in snapshot["texts"].items()}}


def outside(path, root):
    path = io.external(path)
    require(not path.is_relative_to(root) and not root.is_relative_to(path), "Background plan must be outside checkout")
    return path


def result(status, value=None, request=None, *, error=None, recovery_required=False, remaining=None):
    return {"format": RESULT, "status": status,
            "puzzle_id": request["puzzle_id"] if request else None,
            "revision": request["revision"] if request else None,
            "plan_hash": value["plan_hash"] if value else None,
            "error": error, "recovery_required": recovery_required, "remaining": remaining}


def _target(root, snapshot, request):
    from .content_registry import ROOT
    require((request["format"] == requests.IMAGE_FORMAT) == tx.image_generation(snapshot),
            "Background request generation differs from the current image projection")
    require(request["puzzle_id"] in bg.index(snapshot["registry"]), "Background change requires an existing background target; Legacy retrofit is unsupported")
    entry = next(e for e in snapshot["registry"]["entries"] if e["id"] == request["puzzle_id"])
    require(root != ROOT.resolve() or not entry["production"]["test_only"], "Test-only background cannot enter the real catalog")
    source = bg.load(root, snapshot["registry"], entry)
    return entry, source


def _work_graph(root, request, raw, payload, source, entry, external_root):
    require(requests.read(external_root, requests.record_name(request), require_index=False) == (request, raw, payload),
            "Background working bytes changed")
    require(request["target"] == {"source": bg.ref(bg.path(request["puzzle_id"]), bg.encoded(source)),
                                   "origin_sha256": bg.origin_hash(source),
                                   "image_revision": bg.current(source)["image_revision"]}, "Stale background request target")
    require(request["test_only"] == entry["production"]["test_only"], "Background work changes test_only")
    if request["format"] == requests.IMAGE_FORMAT:
        require(request["context"] == requests.current_context(root, entry), "Stale background reveal context")
    graph = package.validate_change(root, request, source, entry, external_root=external_root)
    expected = {requests.directory(request) + "/" + row["file"] for row in request["files"]}
    used = set(graph["used_files"]) | {requests.directory(request) + "/" + request["authorization"]["evidence"]["file"]}
    require(expected == used, "Background work contains missing or unreferenced files")
    return graph


def _build(root, request, raw, payload, *, external_root=None, snapshot=None):
    """Independently derive every persisted plan field from real bound inputs."""
    external_root = root if external_root is None else external_root
    snapshot = tx.capture(root) if snapshot is None else snapshot
    bg.capability(root, required=True)
    entry, source = _target(root, snapshot, request)
    graph = _work_graph(root, request, raw, payload, source, entry, external_root)
    notice = bg.notice_bytes(request["puzzle_id"], graph["candidate"])
    if request["format"] == requests.IMAGE_FORMAT:
        from . import editor_image_source as images
        candidate, png = graph["candidate"], graph["asset_bytes"]
        require(graph["ready"] is True and graph["binding"] == request["background"],
                "Background change requires the freshly checked exact work binding")
        active = {"image_revision": bg.current(source)["image_revision"] + 1,
                  "candidate_revision": candidate["revision"] if candidate else None,
                  "decision": deepcopy(graph["decision"]), "derivation": deepcopy(graph["derivation"]),
                  "provenance": deepcopy(candidate["provenance"]) if candidate else None,
                  "review": deepcopy(candidate["review"]) if candidate else None,
                  "asset": bg.ref(bg.asset_path(entry["id"]), png) if png is not None else None,
                  "notice": bg.ref(bg.notice_path(entry["id"]), notice) if notice is not None else None,
                  "adoption": {"request": bg.ref(requests.record_name(request), raw),
                               **{key: deepcopy(request[key]) for key in
                                  ("revision", "target", "background", "authorization", "context")}}}
        current = (images.adopt_background(source, active) if source["format"] == images.BACKGROUND_FORMAT else
                   images.adopt_background_from_old(root, snapshot["registry"], entry, active))
    else:
        current = bg.build_change(source, entry, request, bg.ref(requests.record_name(request), raw), graph, notice)
    name = bg.path(request["puzzle_id"])
    encoded = bg.encoded(current)
    registry = deepcopy(snapshot["registry"])
    for row in registry["backgrounds"]:
        if row["id"] == request["puzzle_id"]:
            row["source"] = bg.ref(name, encoded)
    writes = {name: encoded, bg.notice_path(request["puzzle_id"]): notice, tx.REGISTRY: bg.encoded(registry)}
    image_path = bg.asset_path(request["puzzle_id"])
    previous = io.read(root, image_path, requests.FILE_LIMIT) if bg.current(source)["asset"] else None
    image = graph["asset_bytes"]
    replacements = {} if previous == image else {image_path: {
        "old": publication.binary(previous) if previous is not None else None,
        "new": publication.binary(image) if image is not None else None}}
    # Reconstruct old plans for a fully checked no-op; adoption gates actual
    # writes on the migrated catalog. v4 snapshots select the PE journal here.
    journal = tx.prepare(root, snapshot, writes, operation="background-adoption", replacements=replacements,
                         generation="background")
    files = {"input/" + requests.directory(request) + "/" + name: data for name, data in payload.items()}
    if previous is not None:
        files["previous/background.png"] = previous
    value = {"format": IMAGE_FORMAT if tx.image_generation(snapshot) else REBIND_FORMAT if source["format"] in bg.REBIND_FORMATS else FORMAT,
             "request": bg.ref("input/" + requests.record_name(request), raw),
             "snapshot": tx.image_snapshot(snapshot) if tx.image_generation(snapshot) else
                         {"sources": source_hashes(snapshot), "namespaces": snapshot["namespaces"]},
             "old": journal["old"], "new": journal["new"],
             "files": [bg.ref(name, data) for name, data in sorted(files.items())]}
    value["plan_hash"] = digest(value)
    validate_plan(value)
    require(source_hashes(tx.capture(root)) == value["snapshot"]["sources"] and
            tx.namespaces(root, snapshot["registry"]) == value["snapshot"]["namespaces"], "Checkout changed during background planning")
    return value, journal, files


def validate_plan(value):
    value = io.json_bytes(bg.encoded(value), PLAN_LIMIT)
    exact_keys(value, {"format", "request", "snapshot", "old", "new", "files", "plan_hash"})
    require(value["format"] in (FORMAT, REBIND_FORMAT, IMAGE_FORMAT), "Unsupported background plan format")
    require(sha(value["plan_hash"]) == digest({k: v for k, v in value.items() if k != "plan_hash"}), "Wrong background plan hash")
    from .background_contract import _ref
    _ref(value["request"])
    require(value["request"]["file"].startswith("input/content/authoring/") and
            value["request"]["file"].endswith("/record.json") and value["request"]["bytes"] <= requests.LIMIT,
            "Wrong bundled background request path")
    snap = exact_keys(value["snapshot"], {"sources", "namespaces"})
    require(isinstance(snap["sources"], dict) and len(snap["sources"]) <= 100000, "Invalid background source snapshot")
    for name, checksum in snap["sources"].items():
        relative(name)
        if checksum is not None: sha(checksum)
    exact_keys(snap["namespaces"], {"reveals", "difficulty", "added", "packages", "backgrounds", "background_assets"} |
               ({"reveal_assets"} if value["format"] == IMAGE_FORMAT else set()))
    for names in snap["namespaces"].values():
        require(isinstance(names, list) and len(names) <= 100000 and all(isinstance(n, str) for n in names) and
                names == sorted(set(names)), "Invalid background namespace snapshot")
        for name in names: relative(name)
    for side in ("old", "new"):
        require(isinstance(value[side], dict) and len(value[side]) <= 100000, "Invalid background text view")
        for name, text in value[side].items():
            relative(name)
            require(text is None or isinstance(text, str), "Invalid background text or absence")
    require(set(value["old"]) == set(value["new"]), "Background text views have different keys")
    requests.inventory(value["files"], count=requests.MAX_FILES + 2, total=128 * 1024 * 1024, exclude=("plan.json",))
    require(value["request"] in value["files"], "Background plan does not bind request bytes")
    return value


def load_plan(path):
    path = io.external(path)
    if path.is_dir(): path = io.safe(path, "plan.json")
    require(path.name == "plan.json", "Background plan filename must be plan.json")
    raw = io.read(path.parent, path.name, PLAN_LIMIT)
    value = validate_plan(io.json_bytes(raw, PLAN_LIMIT))
    require(raw == bg.encoded(value), "Noncanonical background plan bytes")
    found = {name[len(path.parent.name) + 1:] for name in requests.tree_files(path.parent.parent, path.parent.name)}
    require(found == {"plan.json"} | {row["file"] for row in value["files"]}, "Background plan inventory differs")
    files = {}
    for row in value["files"]:
        data = io.read(path.parent, row["file"], requests.FILE_LIMIT)
        require(bg.ref(row["file"], data) == row, "Background plan file binding changed: " + row["file"])
        files[row["file"]] = data
    request, request_raw, payload = requests.read(path.parent / "input", value["request"]["file"].removeprefix("input/"), require_index=False)
    require(bg.ref(value["request"]["file"], request_raw) == value["request"], "Bundled request differs")
    expected = {"input/" + requests.directory(request) + "/" + name for name in payload}
    old_source = value["old"].get(bg.path(request["puzzle_id"]))
    require(isinstance(old_source, str), "Plan lacks its old background source")
    from . import content_registry, categories
    registry_text, category_text = value["old"].get(tx.REGISTRY), value["old"].get(categories.PATH)
    require(isinstance(registry_text, str) and isinstance(category_text, str), "Plan lacks catalog text bindings")
    registry = content_registry.validate(io.json_bytes(registry_text.encode(), 8 * 1024 * 1024),
                                        io.json_bytes(category_text.encode(), 131072))
    entry = next((e for e in registry["entries"] if e["id"] == request["puzzle_id"]), None)
    require(entry is not None, "Plan lacks its background target entry")
    previous_source = bg._source(None, registry, entry, value["old"])
    require(previous_source is not None, "Plan lacks its background source")
    image_plan = value["format"] == IMAGE_FORMAT
    old_runtime = io.json_bytes(value["old"][tx.RUNTIME].encode(), 8 * 1024 * 1024)
    require(image_plan == (old_runtime.get("format") == "picross-runtime-registry-v8") and
            image_plan == (request["format"] == requests.IMAGE_FORMAT), "Background plan/request projection differs")
    if not image_plan:
        require((previous_source.get("format") in bg.REBIND_FORMATS) == (value["format"] == REBIND_FORMAT),
                "Background plan generation differs from source")
    prior = bg.current(previous_source)
    require(isinstance(prior, dict), "Invalid old current background source object")
    if prior.get("asset") is not None: expected.add("previous/background.png")
    require(set(files) == expected, "Background plan contains unbound or duplicate inputs")
    return value, raw, files


def _write_files(root, files):
    from .authoring_builder import write_new
    for name, raw in sorted(files.items()):
        target = io.safe(root, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        write_new(target, raw)
    for child in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        publication.sync_directory(child)
    publication.sync_directory(root)


def plan(root, record_path, output, *, seconds=300):
    from .authoring_builder import publish_directory
    with io.budget(seconds):
        root, output = io.external(root), io.external(output)
        outside(output, root)
        require(output.parent.is_dir() and not output.exists(), "Background output must be new under an existing safe parent")
        request, raw, payload = requests.read(root, record_path)
        value, _, files = _build(root, request, raw, payload)
        with tempfile.TemporaryDirectory(prefix=".hp-i1b2-plan-", dir=output.parent) as temporary:
            stage = Path(temporary)
            (stage / "owner.json").write_bytes(bg.encoded({"purpose": "HP-I1b2 unpublished plan", "pid": os.getpid(), "request_sha256": io.checksum(raw)}))
            bundle = stage / "bundle"
            bundle.mkdir()
            _write_files(bundle, {**files, "plan.json": bg.encoded(value)})
            require(load_plan(bundle) == (value, bg.encoded(value), files), "Written background plan differs")
            again, _, written = _build(root, request, raw, payload, external_root=bundle / "input")
            require(again == value and written == files, "Written background plan fails fresh derivation")
            checkpoint("before-plan-publication")
            require(requests.read(root, record_path) == (request, raw, payload), "Background work changed before plan publication")
            require(load_plan(bundle) == (value, bg.encoded(value), files), "Plan changed before publication")
            fresh = tx.capture(root)
            require(source_hashes(fresh) == value["snapshot"]["sources"] and
                    fresh["namespaces"] == value["snapshot"]["namespaces"], "Checkout changed before plan publication")
            published = False
            try:
                publish_directory(bundle, io.external(output))
                published = True
                publication.sync_directory(output.parent)
                require(load_plan(output) == (value, bg.encoded(value), files), "Published background plan differs")
            except BaseException as exc:
                if published: raise _publication_error(exc, str(output)) from exc
                raise
        return result("planned", value, request)


def _old_view(root, stage, value, files, request):
    """Reconstruct the complete old catalog; trust neither plan views nor flags."""
    image = bg.asset_path(request["puzzle_id"])
    for name, checksum in sorted(value["snapshot"]["sources"].items()):
        if name in value["old"]:
            text = value["old"][name]
            raw = text.encode() if text is not None else None
        elif name == image:
            raw = files.get("previous/background.png")
        else:
            raw = tx.read(root, name)
        require(io.checksum(raw) == checksum, "Stale background plan source: " + name)
        if raw is not None:
            target = io.safe(stage, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)


def _current_expected(value, journal, new):
    sources = dict(value["snapshot"]["sources"])
    namespaces = deepcopy(value["snapshot"]["namespaces"])
    if not new: return sources, namespaces
    for name, text in journal["new"].items():
        sources[name] = io.checksum(text.encode() if text is not None else None)
    for name, pair in journal["replacements"].items():
        if pair["new"] is None:
            if value["format"] == IMAGE_FORMAT: sources[name] = None
            else: sources.pop(name, None)
        else: sources[name] = pair["new"]["sha256"]
    # The complete registry/source reader fixes all background namespace paths.
    registry = io.json_bytes(journal["new"][tx.REGISTRY].encode(), 8 * 1024 * 1024)
    assets = set()
    for entry in registry["entries"]:
        if entry["id"] in bg.index(registry):
            source = bg.validate(io.json_bytes(journal["new"][bg.path(entry["id"])].encode(), bg.LIMIT), entry)
            current = bg.current(source)
            if current["asset"] is not None:
                assets.update((current["asset"]["file"], current["notice"]["file"]))
    namespaces["background_assets"] = sorted(assets)
    return sources, namespaces


def adopt(root, plan_path, *, seconds=300, integrated_commit=None, fail_step=None, no_op_only=False):
    """Replay the complete native checks; optionally forbid any publication."""
    require(type(no_op_only) is bool, "Background no_op_only must be boolean")
    with io.budget(seconds):
        root = io.external(root)
        path = outside(plan_path, root)
        if path.is_dir(): path = path / "plan.json"
        value, raw, files = load_plan(path)
        input_root = path.parent / "input"
        request, request_raw, payload = requests.read(input_root, value["request"]["file"].removeprefix("input/"), require_index=False)
        snapshot = tx.capture(root)
        entry, _ = _target(root, snapshot, request)
        old = {n: text.encode() if text is not None else None for n, text in value["old"].items()}
        new = {n: text.encode() if text is not None else None for n, text in value["new"].items()}
        is_target = snapshot["texts"] == new
        require(is_target or snapshot["texts"] == old, "Stale or partial background plan text sources")
        if integrated_commit is not None:
            require(isinstance(integrated_commit, str) and re.fullmatch(r"[0-9a-f]{40}", integrated_commit),
                    "Use the full verified Main commit")
            require(is_target, "An integrated Main proof is for background no-op only")
        previous = bg.validate(io.json_bytes(old[bg.path(request["puzzle_id"])], bg.LIMIT), entry)
        known = set(source_hashes(snapshot))
        if value["format"] != IMAGE_FORMAT:
            known.discard(bg.asset_path(request["puzzle_id"]))
            if bg.current(previous)["asset"] is not None: known.add(bg.asset_path(request["puzzle_id"]))
        require(set(value["snapshot"]["sources"]) == known, "Background plan source set differs from the complete target view")
        with tempfile.TemporaryDirectory(prefix="hp-i1b2-old-") as temporary:
            stage = Path(temporary)
            _old_view(root, stage, value, files, request)
            rebuilt, journal, reproduced_files = _build(stage, request, request_raw, payload, external_root=input_root)
            require(rebuilt == value and reproduced_files == files, "Background plan differs from independently derived operations")
            expected_sources, expected_namespaces = _current_expected(value, journal, is_target)
            require(source_hashes(snapshot) == expected_sources and snapshot["namespaces"] == expected_namespaces,
                    "Stale background plan retained sources or namespaces")
            def bundle_check():
                require(load_plan(path) == (value, raw, files), "Background plan changed during adoption")
            def work_check():
                bundle_check()
                require(requests.read(root, requests.record_name(request)) == (request, request_raw, payload),
                        "Background work changed during adoption")
                checkpoint("work-checked")
            directory = io.safe(root, requests.directory(request))
            rows = requests.index_rows(io.json_bytes(io.read(root, requests.INDEX, 8 * 1024 * 1024), 8 * 1024 * 1024))
            absent = not directory.exists() and requests.directory(request) not in rows
            if absent:
                require(is_target and integrated_commit is not None, "Missing background work requires an exact Main proof for no-op only")
                from .background_retirement import prove
                proofs = prove(root, [(request["puzzle_id"], request["revision"])], integrated_commit, snapshot=snapshot)
                proof = proofs[0]
                require(proof["absent"] and proof["current"] and proof["request"] == request and
                        proof["request_ref"] == bg.ref(requests.record_name(request), request_raw), "Background cleanup Main proof differs")
                bundle_check()
            else:
                work_check()
            require(source_hashes(tx.capture(root)) == expected_sources and
                    tx.namespaces(root, snapshot["registry"]) == expected_namespaces, "Checkout changed before background adoption")
            if is_target: return result("no-op", value, request)
            require(not no_op_only, "Background no-op-only check requires the exact adopted target")
            require(not absent, "Missing work cannot authorize background publication")
            from .content_registry import require_current
            require_current(snapshot["registry"])
            tx.execute(root, journal, fail_step=fail_step, source_check=work_check)
        return result("adopted", value, request)


def store(root, record_path, source_root):
    """Publish complete immutable work plus one index row; never author approvals."""
    from . import authoring_builder as builder
    with io.budget(300):
        root, record_path, source_root = io.external(root), io.external(record_path), io.external(source_root)
        outside(source_root, root)
        raw = io.read(record_path.parent, record_path.name, requests.LIMIT)
        request = requests.validate(io.json_bytes(raw, requests.LIMIT))
        require(raw == bg.encoded(request), "Noncanonical background request bytes")
        payload = requests.payload(source_root, request, raw, record_present=(source_root / "record.json").exists())
        gitdir = builder.git_root(root)
        before = io.read(root, requests.INDEX, 8 * 1024 * 1024, missing=True)
        index = builder.index_value(before) if before is not None else {"format": "picross-authoring-index-v1", "entries": []}
        row = requests.index_row(request)
        existing = requests.index_rows(index).get(requests.directory(request))
        target = io.safe(root, requests.directory(request))
        require((target.exists() and existing == row) or (not target.exists() and existing is None),
                "Partial or conflicting background work publication")
        if target.exists():
            with builder.writer(gitdir / "authoring-builder.lock"):
                require(io.read(root, requests.INDEX, 8 * 1024 * 1024, missing=True) == before,
                        "Authoring index changed before background storage no-op")
                require(io.read(record_path.parent, record_path.name, requests.LIMIT) == raw and
                        requests.payload(source_root, request, raw, record_present=(source_root / "record.json").exists()) == payload,
                        "Background input changed before storage no-op")
                require(requests.read(root, row["record"]) == (request, raw, payload), "Conflicting background work revision")
                bg.capability(root, required=True)
                _target(root, tx.capture(root), request)
                # Storage idempotence does not re-authorize an adopted/superseded target.
                return result("no-op", request=request)
        with tempfile.TemporaryDirectory(prefix=".hp-i1b2-store-", dir=root.parent) as temporary:
            stage = Path(temporary)
            (stage / "owner.json").write_bytes(bg.encoded({"purpose": "HP-I1b2 unpublished work", "pid": os.getpid(), "request_sha256": io.checksum(raw)}))
            simulation = stage / "checkout"
            simulation.mkdir()
            _write_files(simulation, {requests.directory(request) + "/" + n: data for n, data in payload.items()})
            planned, _, _ = _build(root, request, raw, payload, external_root=simulation)
            with builder.writer(gitdir / "authoring-builder.lock"):
                require(io.read(root, requests.INDEX, 8 * 1024 * 1024, missing=True) == before, "Authoring index changed before background publication")
                require(io.read(record_path.parent, record_path.name, requests.LIMIT) == raw and
                        requests.payload(source_root, request, raw, record_present=(source_root / "record.json").exists()) == payload,
                        "Background input changed before publication")
                if target.exists():
                    require(requests.read(root, row["record"]) == (request, raw, payload), "Conflicting background work revision")
                    return result("no-op", request=request)
                checkpoint("before-work-publication")
                require(io.read(record_path.parent, record_path.name, requests.LIMIT) == raw and
                        requests.payload(source_root, request, raw, record_present=(source_root / "record.json").exists()) == payload,
                        "Background input changed before work publication")
                fresh = tx.capture(root)
                require(source_hashes(fresh) == planned["snapshot"]["sources"] and
                        fresh["namespaces"] == planned["snapshot"]["namespaces"], "Background target changed before work publication")
                from .content_registry import require_current
                require_current(fresh["registry"])
                target.parent.mkdir(parents=True, exist_ok=True)
                published = False
                try:
                    builder.publish_directory(io.safe(simulation, requests.directory(request)), io.safe(root, requests.directory(request)))
                    published = True
                    publication.sync_directory(target.parent)
                    require(io.read(root, requests.INDEX, 8 * 1024 * 1024, missing=True) == before, "Authoring index changed after background publication")
                    require(requests.read(root, row["record"], require_index=False) == (request, raw, payload), "Published background work differs")
                    updated = {**index, "entries": [*index["entries"], row]}
                    index_stage = stage / "index.json"
                    builder.write_new(index_stage, bg.encoded(updated))
                    checkpoint("before-index-publication")
                    require(io.read(root, requests.INDEX, 8 * 1024 * 1024, missing=True) == before, "Concurrent authoring index change")
                    publication.rename(index_stage, io.safe(root, requests.INDEX), replace=before is not None)
                    publication.sync_directory(io.safe(root, requests.INDEX).parent)
                    require(requests.read(root, row["record"]) == (request, raw, payload), "Background work publication not confirmed")
                except BaseException as exc:
                    if published: raise _publication_error(exc, str(target)) from exc
                    raise
        return result("stored", request=request)


def main(argv=None):
    from .catalog_reveal import Parser, Once
    parser = Parser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("store", "plan", "adopt"):
        p = sub.add_parser(command, allow_abbrev=False)
        p.add_argument("--root", required=True, type=Path, action=Once)
        if command != "adopt": p.add_argument("--record", required=True, type=Path, action=Once)
        if command == "store": p.add_argument("--source-root", required=True, type=Path, action=Once)
        else: p.add_argument("--seconds", type=int, default=300, action=Once)
        if command == "plan": p.add_argument("--output", required=True, type=Path, action=Once)
        if command == "adopt":
            p.add_argument("--plan", required=True, type=Path, action=Once)
            p.add_argument("--integrated-commit", action=Once)
    args = None
    def interrupted(signum, frame): raise Aborted("interrupted: signal " + str(signum))
    for signum in (signal.SIGINT, signal.SIGTERM): signal.signal(signum, interrupted)
    try:
        args = parser.parse_args(argv)
        if args.command == "store": answer = store(args.root, args.record, args.source_root)
        elif args.command == "plan": answer = plan(args.root, args.record, args.output, seconds=args.seconds)
        else: answer = adopt(args.root, args.plan, seconds=args.seconds, integrated_commit=args.integrated_commit)
        code = 0
    except (ValueError, OSError, Aborted, BackgroundError, KeyboardInterrupt, MemoryError) as exc:
        aborted = isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError)) or getattr(exc, "aborted", False)
        pending = False
        if args:
            try:
                checked_root = io.external(args.root)
                pending = (checked_root / tx.LOCK).exists()
                pending = pending or bool(publication.staging(checked_root))
            except (ValueError, OSError, Aborted):
                pass  # An invalid root must not replace the original structured error.
        answer = result("aborted" if aborted else "invalid_input", error={"code": getattr(exc, "code", "invalid_input"),
                        "message": str(exc)[:2048] or "Interrupted"}, recovery_required=pending, remaining=getattr(exc, "remaining", None))
        code = 4 if aborted else 2
    print(canonical_bytes(answer).decode())
    return code


if __name__ == "__main__": sys.exit(main())
