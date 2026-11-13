"""PE-A2 prepared images and preferences through the shared catalog writer.

Public plans contain only declarations, references and detached previews. Apply
rebuilds every proposed byte from its closed bundle and freshly bound checkout.
"""
from copy import deepcopy
from pathlib import Path

from .authoring_package import require, relative, sha
from .contract import canonical_bytes, digest, exact_keys
from . import catalog_io as io, catalog_transaction as tx, catalog_publication as publication
from . import catalog_background as bg, content_registry as registry, categories, reveal_source as reveal
from . import editor_image_source as source, editor_image_input as inputs

REQUEST = "picross-editor-images-request-v1"
PLAN = "picross-editor-images-plan-v1"
MIGRATION = "picross-editor-image-migration-plan-v1"
PLAN_LIMIT = 32 * 1024 * 1024
REQUEST_LIMIT = 128 * 1024


def encoded(value):
    return canonical_bytes(value) + b"\n"


def _outside(path, root):
    path = io.external(path)
    require(not path.is_relative_to(root) and not root.is_relative_to(path), "Image work must be outside the target checkout")
    return path


def validate_request(value):
    exact_keys(value, {"format", "id", "metadata", "reveal", "background", "decision"})
    require(value["format"] == REQUEST, "Unsupported editor image request")
    reveal.path(value["id"])
    source.decision(value["decision"])
    require(any(value[key] is not None for key in ("metadata", "reveal", "background")), "Request contains no requested fields")
    if value["metadata"] is not None:
        require(isinstance(value["metadata"], dict) and set(value["metadata"]) and
                set(value["metadata"]) <= {"name", "category_id"}, "Invalid metadata fields")
        if "name" in value["metadata"]: registry.validate_name(value["metadata"]["name"])
        if "category_id" in value["metadata"]:
            require(isinstance(value["metadata"]["category_id"], str) and categories.ID.fullmatch(value["metadata"]["category_id"]),
                    "Invalid current category ID")
    for kind in ("reveal", "background"):
        part = value[kind]
        if part is None: continue
        exact_keys(part, {"asset", "provenance"} | ({"status"} if kind == "background" else set()))
        if kind == "background": require(part["status"] in ("standard", "selected", "none"), "Unknown background preference")
        if kind == "background" and part["status"] != "selected":
            require(part["asset"] is None and part["provenance"] is None, "Image-free preference has image input")
        else:
            bg._ref(part["asset"], limit=reveal.IMAGE_LIMIT)
            require(part["asset"]["bytes"] > 0, "Image input is empty")
            reveal.provenance(part["provenance"])
    require(len(encoded(value)) <= REQUEST_LIMIT, "Editor image request exceeds 128 KiB")
    return value


def _source(texts, name):
    raw = texts.get(name)
    if isinstance(raw, str): raw = raw.encode()
    return io.json_bytes(raw, source.LIMIT) if raw is not None else None


def _summary(texts, identifier):
    raw = texts[tx.REGISTRY]
    if isinstance(raw, str): raw = raw.encode()
    value = io.json_bytes(raw, 8 * 1024 * 1024)
    raw = texts[tx.RUNTIME]
    if isinstance(raw, str): raw = raw.encode()
    runtime = io.json_bytes(raw, 8 * 1024 * 1024)
    return {"entry": next(e for e in value["entries"] if e["id"] == identifier),
            "metadata": next(e for e in value["metadata"] if e["id"] == identifier),
            "reveal": _source(texts, reveal.path(identifier)), "background": _source(texts, bg.path(identifier)),
            "runtime": next(e for e in runtime["entries"] if e["id"] == identifier)}


def _hash_plan(value):
    value["plan_hash"] = digest(value)
    require(len(encoded(value)) <= PLAN_LIMIT, "Editor image plan exceeds 32 MiB")
    return value


def _pair(root, path, raw, replacements):
    before = io.read(root, path, reveal.IMAGE_LIMIT, missing=True)
    if before != raw:
        replacements[path] = {"old": publication.binary(before) if before is not None else None,
                              "new": publication.binary(raw) if raw is not None else None}


def _construct(root, snapshot, request, request_raw, input_root):
    registry.require_current(snapshot["registry"])
    require(tx.image_generation(snapshot), "Explicit image migration required: run images_cli plan-migration first")
    validate_request(request)
    identifier = request["id"]
    entries = {e["id"]: e for e in snapshot["registry"]["entries"]}
    require(identifier in entries, "Unknown puzzle ID")
    entry = entries[identifier]
    catalog = io.json_bytes(snapshot["texts"][categories.PATH], categories.MAX_BYTES)
    after = deepcopy(snapshot["registry"])
    if request["metadata"] is not None:
        next(row for row in after["metadata"] if row["id"] == identifier).update(request["metadata"])
    changes, replacements, files = {}, {}, {}
    if request["reveal"] is not None:
        part = request["reveal"]
        raw = inputs.reveal_input(input_root, part["asset"], entry)
        files["input/" + part["asset"]["file"]] = raw
        target = Path("game/" + entry["reveal"]).with_suffix(Path(part["asset"]["file"]).suffix).as_posix()
        record = source.manual_reveal(root, entry, catalog, bg.ref(target, raw), part["provenance"], request["decision"])
        if record != _source(snapshot["texts"], reveal.path(identifier)):
            changes[reveal.path(identifier)] = encoded(record)
            changes[reveal.identity(entry)["notice"]] = record["current"]["notice"]["text"].encode()
        previous = tx.active_reveal(entry, snapshot["texts"])
        if previous != target: _pair(root, previous, None, replacements)
        _pair(root, target, raw, replacements)
    if request["background"] is not None:
        part = request["background"]
        raw = inputs.background_input(input_root, part["asset"]) if part["status"] == "selected" else None
        if raw is not None:
            name = "input/" + part["asset"]["file"]
            require(name not in files or files[name] == raw, "Conflicting input image refs")
            files[name] = raw
        asset = bg.ref(bg.asset_path(identifier), raw) if raw is not None else None
        record = source.manual_background(root, snapshot["registry"], entry, part["status"], asset,
                                          part["provenance"], request["decision"])
        previous = _source(snapshot["texts"], bg.path(identifier))
        if record != previous:
            changes[bg.path(identifier)] = encoded(record)
            after["backgrounds"] = sorted([row for row in after["backgrounds"] if row["id"] != identifier] +
                [{"id": identifier, "source": bg.ref(bg.path(identifier), changes[bg.path(identifier)])}], key=lambda row: row["id"])
            prefix = snapshot["texts"].get(bg.notice_path(identifier))
            if prefix is None and record["origin"]["notice"] is not None: prefix = record["origin"]["notice"]["text"].encode()
            changes[bg.notice_path(identifier)] = source.manual_notice(prefix or b"", part["provenance"], request["decision"]) if raw is not None else None
        _pair(root, bg.asset_path(identifier), raw, replacements)
    registry.validate(after, catalog)
    if after != snapshot["registry"]: changes[tx.REGISTRY] = encoded(after)
    journal = tx.prepare(root, snapshot, changes, operation="editor-images", replacements=replacements, generation="images")
    changed = sorted({name for name in journal["old"] if journal["old"][name] != journal["new"][name]} | set(replacements))
    plan = _hash_plan({"format": PLAN, "request": bg.ref("request.json", request_raw),
        "snapshot": tx.image_snapshot(snapshot), "old": _summary(journal["old"], identifier),
        "new": _summary(journal["new"], identifier), "files": changed})
    files["request.json"] = request_raw
    for pair in replacements.values():
        if pair["old"] is not None: files["previous/" + pair["old"]["sha256"] + ".bin"] = publication.decode_binary(pair["old"])
    return plan, journal, files


def _write_bundle(output, files):
    require(not output.exists(), "Image plan output directory must be new")
    output.mkdir(parents=True)
    # This is an explicitly selected work output, never active product data.
    for name, raw in files.items():
        target = io.safe(output, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream: stream.write(raw)


def plan(root, request_path, output, *, seconds=300, _snapshot=None):
    with io.budget(seconds):
        root = io.external(root)
        request_path, output = _outside(request_path, root), _outside(output, root)
        require(not output.is_relative_to(request_path.parent) and not request_path.parent.is_relative_to(output),
                "Image input and plan output overlap")
        raw = io.read(request_path.parent, request_path.name, REQUEST_LIMIT)
        request = validate_request(io.json_bytes(raw, REQUEST_LIMIT))
        snapshot = tx.capture(root) if _snapshot is None else _snapshot
        result, journal, files = _construct(root, snapshot, request, raw, request_path.parent)
        tx.recheck(root, snapshot)
        require(io.read(request_path.parent, request_path.name, REQUEST_LIMIT) == raw, "Request changed during planning")
        for part in (request["reveal"], request["background"]):
            if part is not None and part["asset"] is not None:
                require(inputs.read_ref(request_path.parent, part["asset"]) == files["input/" + part["asset"]["file"]], "Input changed during planning")
        _write_bundle(output, {**files, "plan.json": encoded(result)})
        return result


def plan_migration(root, output=None, *, seconds=300):
    with io.budget(seconds):
        root = io.external(root)
        snapshot = tx.capture(root)
        registry.require_current(snapshot["registry"])
        journal = tx.prepare(root, snapshot, {}, operation="editor-image-migration", generation="images")
        result = _hash_plan({"format": MIGRATION, "snapshot": tx.image_snapshot(snapshot),
            "old": io.json_bytes(journal["old"][tx.RUNTIME].encode(), 8 * 1024 * 1024),
            "new": io.json_bytes(journal["new"][tx.RUNTIME].encode(), 8 * 1024 * 1024),
            "files": [tx.RUNTIME] if journal["old"][tx.RUNTIME] != journal["new"][tx.RUNTIME] else []})
        if output is not None:
            output = _outside(output, root)
            require(not output.exists(), "Migration plan output must be new")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("xb") as stream: stream.write(encoded(result))
        return result


def _validate_plan(value):
    require(isinstance(value, dict) and value.get("format") in (PLAN, MIGRATION), "Unsupported image plan")
    exact_keys(value, {"format", "snapshot", "old", "new", "files", "plan_hash"} | ({"request"} if value["format"] == PLAN else set()))
    require(sha(value["plan_hash"]) == digest({key: row for key, row in value.items() if key != "plan_hash"}), "Image plan hash differs")
    exact_keys(value["snapshot"], {"sources", "namespaces"})
    require(isinstance(value["snapshot"]["sources"], dict), "Invalid image plan sources")
    for name, checksum in value["snapshot"]["sources"].items():
        relative(name)
        if checksum is not None: sha(checksum)
    exact_keys(value["snapshot"]["namespaces"], {"reveals", "difficulty", "added", "packages", "backgrounds", "background_assets", "reveal_assets"})
    for names in value["snapshot"]["namespaces"].values():
        require(isinstance(names, list) and all(isinstance(name, str) for name in names) and names == sorted(set(names)), "Invalid image plan namespace")
        for name in names: relative(name)
    require(isinstance(value["files"], list) and all(isinstance(name, str) for name in value["files"]) and value["files"] == sorted(set(value["files"])), "Invalid image plan files")
    for name in value["files"]: relative(name)
    if value["format"] == PLAN:
        for side in ("old", "new"): exact_keys(value[side], {"entry", "metadata", "reveal", "background", "runtime"})
        entry = value["old"]["entry"]
        registry.validate_entries([entry])
        require(value["new"]["entry"] == entry, "Image plan changes production entry")
        identifier = entry["id"]
        allowed = {tx.REGISTRY, tx.RUNTIME, reveal.path(identifier), bg.path(identifier),
                   reveal.identity(entry)["notice"], bg.notice_path(identifier)} | tx.image_candidates({"entries": [entry]})
        require(set(value["files"]) <= allowed, "Image plan contains unrelated changed files")
        for side in ("old", "new"):
            require(all(isinstance(value[side][key], dict) and value[side][key].get("id") == identifier
                        for key in ("metadata", "runtime")), "Image plan row identity differs")
        bg._ref(value["request"], name="request.json", limit=REQUEST_LIMIT)
    else:
        for side in ("old", "new"): exact_keys(value[side], {"format", "categories", "entries"})
        require(value["old"]["format"] in (registry.METADATA_RUNTIME_FORMAT, registry.IMAGE_RUNTIME_FORMAT) and
                {**value["old"], "format": registry.IMAGE_RUNTIME_FORMAT} == value["new"],
                "Image migration preview is not lossless v7/v8 to v8")
        require(value["files"] == ([tx.RUNTIME] if value["old"] != value["new"] else []),
                "Image migration preview has another file delta")
    return value


def _bundle(plan_path, value):
    root = plan_path.parent
    request_raw = io.read(root, "request.json", REQUEST_LIMIT)
    require(bg.ref("request.json", request_raw) == value["request"], "Bound request differs")
    request = validate_request(io.json_bytes(request_raw, REQUEST_LIMIT))
    require(value["old"]["entry"]["id"] == value["new"]["entry"]["id"] == request["id"], "Image plan ID differs")
    expected = {"plan.json", "request.json"}
    for part in (request["reveal"], request["background"]):
        if part is not None and part["asset"] is not None:
            inputs.read_ref(root / "input", part["asset"])
            expected.add("input/" + part["asset"]["file"])
    for name in value["files"]:
        checksum = value["snapshot"]["sources"].get(name)
        if checksum is not None and name in tx.image_candidates({"entries": [value["old"]["entry"]]}):
            previous = "previous/" + checksum + ".bin"
            require(io.checksum(io.read(root, previous, reveal.IMAGE_LIMIT)) == checksum, "Previous image backup differs")
            expected.add(previous)
    actual = set()
    directories = set()
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        checked = io.safe(root, name)
        if checked.is_file(): actual.add(name)
        else: directories.add(name)
    parents = {p.as_posix() for name in expected for p in Path(name).parents if p.as_posix() != "."}
    require(actual == expected and directories <= parents, "Image plan bundle has missing or foreign files")
    return request, request_raw


def _manual_transition(kind, entry, old, new, definition_ref, old_notice_hash):
    """The same closed source transition for publication and repeated plans."""
    identifier = entry["id"]
    source.validate(new)
    require(new["format"] == (source.REVEAL_FORMAT if kind == "reveal" else source.BACKGROUND_FORMAT) and
            new["id"] == identifier and new["current"]["authority"]["kind"] == "manual", "Wrong manual source authority")
    if source.is_editor(old):
        source.transition(old, new, operation="editor-images")
    else:
        require(new["origin"]["source"] == old and new["origin"]["entry"] == new["binding"]["entry"] and
                new["origin"]["identity"] == new["binding"]["identity"], "First image wrapper changes its real origin")
        require(new["record_revision"] == max(old.get("record_revision", 0) if old else 0, source._old_image_revision(old)) + 1 and
                new["current"]["image_revision"] == source._old_image_revision(old) + 1, "First image wrapper skips revision")
        notice = new["origin"]["notice"]
        require((notice["sha256"] if notice is not None else None) == old_notice_hash,
                "First image wrapper changes original attribution")
        if kind == "reveal" and old is not None:
            previous = old["revisions"][-1]
            require(("game/" + entry["reveal"], previous["reveal_sha256"], previous["provenance"]) !=
                    (new["current"]["asset"]["file"], new["current"]["asset"]["sha256"], new["current"]["provenance"]),
                    "Unchanged reveal cannot create a first manual wrapper")
        elif kind == "background" and old is not None:
            previous = bg.current(old)
            require((previous["decision"]["outcome"], previous["asset"], previous["provenance"]) !=
                    (new["current"]["status"], new["current"]["asset"], new["current"]["authority"]["provenance"]),
                    "Unchanged background cannot create a first manual wrapper")
    require(new["binding"]["identity"]["definition"] == definition_ref, "Manual image binding changes definition")


def _already_applied(root, snapshot, value, request, bundle):
    identifier = request["id"]
    if _summary(snapshot["texts"], identifier) != value["new"]: return False
    old, current = value["old"], tx.image_snapshot(snapshot)
    entry = old["entry"]
    catalog = io.json_bytes(snapshot["texts"][categories.PATH], categories.MAX_BYTES)
    original, historical_notice, _, _ = reveal.package(root, entry)
    definition_raw = snapshot["texts"]["game/" + entry["definition"]]
    definition = io.json_bytes(definition_raw, 2 * source.LIMIT)
    binding = source.validate_binding({"entry": original, "identity": {"key": entry["key"], "save_slot": entry["save_slot"],
        "definition": bg.ref("game/" + entry["definition"], definition_raw), "runtime_revision": definition["revision"]}}, identifier)
    old_reveal, old_background = old["reveal"], old["background"]
    reveal_asset = {"file": "game/" + entry["reveal"], "sha256": entry["production"]["reveal_sha256"]}
    reveal_notice = None
    if old_reveal is not None:
        reveal.validate(old_reveal, catalog, historical_categories=True)
        if old_reveal["format"] == source.REVEAL_FORMAT:
            require(old_reveal["binding"] == binding, "Old reveal preview changes its actual production binding")
            reveal_asset, reveal_notice = (old_reveal["current"][key] for key in ("asset", "notice"))
        else:
            last = old_reveal["bindings"][-1]
            require(last["entry"] == original and last["runtime_revision"] == definition["revision"],
                    "Old reveal preview changes its retained production binding")
            reveal_asset["sha256"] = old_reveal["revisions"][-1]["reveal_sha256"]
            reveal_notice = old_reveal["revisions"][-1]["notice"]
    background_asset, background_notice = None, None
    if old_background is not None:
        bg.validate(old_background, entry)
        require(bg.effective(old_background)["identity"] == binding["identity"], "Old background preview changes definition identity")
        if old_background["format"] == source.BACKGROUND_FORMAT:
            require(old_background["binding"] == binding, "Old background preview changes its actual production binding")
        elif old_background["format"] in bg.REBIND_FORMATS:
            require(old_background["events"][-1]["binding"]["entry"] == original,
                    "Old background preview changes its retained production binding")
        else:
            require(bg.initial(old_background)["origin"]["export_manifest_sha256"] == original["production"]["package_sha256"],
                    "Old background preview changes its original export anchor")
        background_asset, background_notice = (bg.current(old_background)[key] for key in ("asset", "notice"))

    reverted = deepcopy(snapshot["registry"])
    reverted["metadata"] = [old["metadata"] if row["id"] == identifier else row for row in reverted["metadata"]]
    reverted["backgrounds"] = [row for row in reverted["backgrounds"] if row["id"] != identifier]
    if old_background is not None:
        reverted["backgrounds"].append({"id": identifier, "source": bg.ref(bg.path(identifier), encoded(old_background))})
        reverted["backgrounds"].sort(key=lambda row: row["id"])
    registry.validate(reverted, catalog)
    # Projection needs source data, not reconstructed historical notice bytes.
    # A v5 selected->none plan intentionally retains only the old notice Ref.
    texts = {name: raw.decode() if raw is not None else None for name, raw in snapshot["texts"].items()}
    texts[tx.REGISTRY] = encoded(reverted).decode()
    for kind, name in (("reveal", reveal.path(identifier)), ("background", bg.path(identifier))):
        texts[name] = encoded(old[kind]).decode() if old[kind] is not None else None
    runtime = tx.projection(texts, reverted, version=8)
    require(next(row for row in io.json_bytes(runtime, 8 * 1024 * 1024)["entries"] if row["id"] == identifier) == old["runtime"],
            "Old image preview differs from its derived runtime projection")
    inverse = deepcopy(current)
    inverse["sources"].update({tx.REGISTRY: io.checksum(encoded(reverted)), tx.RUNTIME: io.checksum(runtime),
        reveal.path(identifier): io.checksum(texts[reveal.path(identifier)].encode() if texts[reveal.path(identifier)] is not None else None),
        bg.path(identifier): io.checksum(texts[bg.path(identifier)].encode() if texts[bg.path(identifier)] is not None else None),
        reveal.identity(entry)["notice"]: reveal_notice["sha256"] if reveal_notice is not None else historical_notice,
        bg.notice_path(identifier): background_notice["sha256"] if background_notice is not None else None})
    for name in tx.image_candidates({"entries": [entry]}): inverse["sources"][name] = None
    for asset in (reveal_asset, background_asset):
        if asset is not None: inverse["sources"][asset["file"]] = asset["sha256"]
    for field, prefix in (("reveals", reveal.ROOT + "/"), ("backgrounds", bg.PATH + "/"),
                          ("background_assets", bg.ASSET_PATH + "/"), ("reveal_assets", "game/art/content/")):
        inverse["namespaces"][field] = sorted(name for name, checksum in inverse["sources"].items()
            if checksum is not None and name.startswith(prefix))
    if inverse != value["snapshot"]: return False
    for asset in (reveal_asset, background_asset):
        if asset is not None and "bytes" in asset and current["sources"].get(asset["file"]) == asset["sha256"]:
            bg._bound(asset, io.read(root, asset["file"], reveal.IMAGE_LIMIT), limit=reveal.IMAGE_LIMIT)
    differences = sorted(name for name in current["sources"] if current["sources"][name] != inverse["sources"][name])
    require(differences == value["files"], "Repeated image plan has another actual file delta")
    metadata = {**old["metadata"], **(request["metadata"] or {})}
    require(metadata == value["new"]["metadata"], "Repeated image plan has another metadata effect")
    for kind, notice_name in (("reveal", reveal.identity(entry)["notice"]), ("background", bg.notice_path(identifier))):
        previous, following = old[kind], value["new"][kind]
        if previous == following: continue
        part = request[kind]
        require(part is not None, "Repeated image plan changes an unrequested source")
        _manual_transition(kind, entry, previous, following, binding["identity"]["definition"], inverse["sources"][notice_name])
        require(following["current"]["authority"] == {"kind": "manual", "decision": request["decision"], "provenance": part["provenance"]},
                "Repeated image plan has another manual decision")
        actual_notice = snapshot["texts"][notice_name]
        if following["current"]["asset"] is None:
            require(actual_notice is None, "Image-free preference retains a notice")
            continue
        if kind == "reveal":
            prefix = (reveal_notice or following["origin"]["notice"])["text"].encode()
        elif background_notice is not None:
            prefix = actual_notice[:background_notice["bytes"]]
        else:
            notice = following["origin"]["notice"]
            prefix = notice["text"].encode() if notice is not None else b""
        if inverse["sources"][notice_name] is not None:
            require(io.checksum(prefix) == inverse["sources"][notice_name], "Repeated image plan changes its old notice prefix")
        require(actual_notice == source.manual_notice(prefix, part["provenance"], request["decision"]),
                "Repeated image plan changes the exact notice append")

    replacements = {}
    for name in set(differences) & tx.image_candidates({"entries": [entry]}):
        pair = {}
        for side, hashes in (("old", inverse["sources"]), ("new", current["sources"])):
            checksum = hashes[name]
            raw = None if checksum is None else (io.read(bundle, "previous/" + checksum + ".bin", reveal.IMAGE_LIMIT)
                                                 if side == "old" else io.read(root, name, reveal.IMAGE_LIMIT))
            require(io.checksum(raw) == checksum, "Repeated image binary differs from its binding")
            if side == "old":
                ref = next((asset for asset in (reveal_asset, background_asset) if asset is not None and asset["file"] == name), None)
                require(ref is None or "bytes" not in ref or len(raw) == ref["bytes"], "Old image preview has another byte count")
            pair[side] = publication.binary(raw) if raw is not None else None
        replacements[name] = pair
    publication.validate_replacements({"format": tx.IMAGE_FORMATS["editor-images"], "operation": "editor-images", "replacements": replacements}, reverted)
    return True


def apply(root, plan_path, *, seconds=300, fail_step=None):
    with io.budget(seconds):
        root = io.external(root)
        plan_path = _outside(plan_path, root)
        if plan_path.is_dir(): plan_path = io.safe(plan_path, "plan.json")
        value = _validate_plan(io.json_bytes(io.read(plan_path.parent, plan_path.name, PLAN_LIMIT), PLAN_LIMIT))
        if value["format"] == MIGRATION: return apply_migration(root, value, seconds=seconds, fail_step=fail_step)
        require(plan_path.name == "plan.json", "Image plan must be the closed bundle's plan.json")
        request, raw = _bundle(plan_path, value)
        snapshot = tx.capture(root)
        if tx.image_snapshot(snapshot) != value["snapshot"]:
            require(_already_applied(root, snapshot, value, request, plan_path.parent), "Image plan is stale")
            repeated, _, _ = _construct(root, snapshot, request, raw, plan_path.parent / "input")
            require(not repeated["files"], "Bound request no longer describes the reached state")
            return {"status": "noop", "id": request["id"], "files": [], "plan_hash": value["plan_hash"]}
        rebuilt, journal, _ = _construct(root, snapshot, request, raw, plan_path.parent / "input")
        require(rebuilt == value, "Image plan preview/request differs from fresh reconstruction")
        if value["files"]: tx.execute(root, journal, fail_step=fail_step)
        return {"status": "updated" if value["files"] else "noop", "id": request["id"],
                "files": value["files"], "plan_hash": value["plan_hash"]}


def apply_migration(root, value, *, seconds=300, fail_step=None):
    with io.budget(seconds):
        root = io.external(root)
        value = _validate_plan(deepcopy(value))
        require(value["format"] == MIGRATION, "Expected image migration plan")
        snapshot = tx.capture(root)
        if value["old"]["format"] == registry.METADATA_RUNTIME_FORMAT:
            require(all(not source.is_editor(_source(snapshot["texts"], name)) for entry in snapshot["registry"]["entries"]
                        for name in (reveal.path(entry["id"]), bg.path(entry["id"]))),
                    "Runtime v7 cannot be the old image migration state of editor sources")
        actual = tx.image_snapshot(snapshot)
        if actual != value["snapshot"]:
            inverse = deepcopy(actual)
            inverse["sources"][tx.RUNTIME] = io.checksum(encoded(value["old"]))
            require(io.json_bytes(snapshot["texts"][tx.RUNTIME], 8 * 1024 * 1024) == value["new"] and
                    inverse == value["snapshot"], "Image migration plan is stale")
            return {"status": "noop", "files": [], "plan_hash": value["plan_hash"]}
        journal = tx.prepare(root, snapshot, {}, operation="editor-image-migration", generation="images")
        require(io.json_bytes(journal["old"][tx.RUNTIME].encode(), 8 * 1024 * 1024) == value["old"] and
                io.json_bytes(journal["new"][tx.RUNTIME].encode(), 8 * 1024 * 1024) == value["new"] and
                value["files"] == ([tx.RUNTIME] if journal["old"][tx.RUNTIME] != journal["new"][tx.RUNTIME] else []),
                "Migration preview differs from fresh reconstruction")
        if value["files"]: tx.execute(root, journal, fail_step=fail_step)
        return {"status": "migrated" if value["files"] else "noop", "files": value["files"], "plan_hash": value["plan_hash"]}


def validate_delta(journal, before, after, root):
    """Independently derive the only legal one-ID delta from complete sources."""
    require(tx.images(journal) and before["format"] == after["format"] == registry.METADATA_FORMAT,
            "Image operation requires registry v4")
    require(not journal["additions"] and journal["report_run"] is None and before["entries"] == after["entries"],
            "Image operation changes production entries or adds reports/packages")
    changed = {name for name in journal["old"] if journal["old"][name] != journal["new"][name]}
    if journal["operation"] == "editor-image-migration":
        require(before == after and changed <= {tx.RUNTIME} and not journal["replacements"], "Migration changes more than runtime")
        old = io.json_bytes(journal["old"][tx.RUNTIME].encode(), 8 * 1024 * 1024)
        new = io.json_bytes(journal["new"][tx.RUNTIME].encode(), 8 * 1024 * 1024)
        require(old["format"] in (registry.METADATA_RUNTIME_FORMAT, registry.IMAGE_RUNTIME_FORMAT) and
                {**old, "format": registry.IMAGE_RUNTIME_FORMAT} == new, "Image migration is not lossless")
        return None
    require(journal["operation"] == "editor-images", "Wrong image delta operation")
    identifiers = {row["id"] for row, target in zip(before["metadata"], after["metadata"]) if row != target}
    mutable = {tx.REGISTRY, tx.RUNTIME}
    for entry in before["entries"]:
        identifier = entry["id"]
        for kind, name in (("reveal", reveal.path(identifier)), ("background", bg.path(identifier))):
            if name not in changed: continue
            identifiers.add(identifier)
            old, new = _source(journal["old"], name), _source(journal["new"], name)
            notice_name = reveal.identity(entry)["notice"] if kind == "reveal" else bg.notice_path(identifier)
            notice_raw = journal["old"][notice_name]
            definition_raw = journal["old"]["game/" + entry["definition"]].encode()
            _manual_transition(kind, entry, old, new, bg.ref("game/" + entry["definition"], definition_raw),
                               io.checksum(notice_raw.encode() if notice_raw is not None else None))
            mutable.add(name)
            mutable.add(notice_name)
            authority = new["current"]["authority"]
            prefix = journal["old"][notice_name]
            if prefix is None and new["origin"]["notice"] is not None: prefix = new["origin"]["notice"]["text"]
            notice_raw = source.manual_notice(prefix or b"", authority["provenance"], authority["decision"]) if new["current"]["asset"] is not None else None
            require(journal["new"][notice_name] == (notice_raw.decode() if notice_raw is not None else None), "Manual notice differs from its bound decision")
    require(len(identifiers) <= 1, "Image operation changes more than one puzzle")
    require(changed <= mutable, "Unexpected image text mutation")
    expected_index = []
    expected_pairs = {}
    for entry in before["entries"]:
        identifier = entry["id"]
        old_bg, new_bg = _source(journal["old"], bg.path(identifier)), _source(journal["new"], bg.path(identifier))
        if new_bg is not None: expected_index.append({"id": identifier, "source": bg.ref(bg.path(identifier), journal["new"][bg.path(identifier)].encode())})
        if identifier not in identifiers: continue
        for side in ("old", "new"):
            texts = journal[side]
            name = tx.active_reveal(entry, texts)
            record = _source(texts, reveal.path(identifier))
            if source.is_editor(record): asset = record["current"]["asset"]
            else:
                pair = journal["replacements"].get(name)
                raw = publication.decode_binary(pair[side]) if pair is not None and pair[side] is not None else io.read(root, name, reveal.IMAGE_LIMIT)
                asset = bg.ref(name, raw)
            refs = [asset]
            background_record = old_bg if side == "old" else new_bg
            if background_record is not None and bg.current(background_record)["asset"] is not None:
                refs.append(bg.current(background_record)["asset"])
            for ref in refs: expected_pairs.setdefault(ref["file"], {"old": None, "new": None})[side] = ref
    require(after["backgrounds"] == expected_index, "Image operation changes unrelated background index")
    expected_pairs = {name: pair for name, pair in expected_pairs.items() if pair["old"] != pair["new"]}
    require(set(journal["replacements"]) == set(expected_pairs), "Image replacement targets differ from active sources")
    for name, expected in expected_pairs.items():
        for side, ref in expected.items():
            actual = journal["replacements"][name][side]
            require(actual is None if ref is None else actual is not None and
                    {key: actual[key] for key in ("sha256", "bytes")} == {key: ref[key] for key in ("sha256", "bytes")},
                    "Image replacement bytes differ from source")
    require(not (changed or journal["replacements"]) or identifiers, "Image mutation has no selected ID")
    return None


def view(root, identifier):
    with io.budget():
        root = io.external(root)
        snapshot = tx.capture(root)
        return view_from_snapshot(snapshot, identifier)


def view_from_snapshot(snapshot, identifier):
    """Pure projection of the caller's freshly validated complete snapshot."""
    require(any(e["id"] == identifier for e in snapshot["registry"]["entries"]), "Unknown puzzle ID")
    registry.require_current(snapshot["registry"])
    return {"format": "picross-editor-images-view-v1", "id": identifier,
            "migration_required": not tx.image_generation(snapshot), **_summary(snapshot["texts"], identifier)}


def recover(root):
    return registry.recover(io.external(root))
