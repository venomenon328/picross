"""PE-EDIT2: selected inputs and prepared bytes, never a catalog certification.

This is the shared API/CLI/desktop edit path. Historical full diagnostics and
their journals retain their own readers. Nothing here traverses a catalog tree.
"""
import base64
from copy import deepcopy
from pathlib import Path
import os
import re
from contextvars import ContextVar
from functools import wraps

from .authoring_package import require, relative, sha
from .contract import canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io, categories, content_registry as registry
from . import catalog_publication as publication, catalog_metadata as metadata
from . import catalog_background as bg, editor_raster as raster, catalog_rating as rating, catalog_method

PLAN = "picross-editor-change-plan-v1"
JOURNAL = "picross-editor-change-journal-v1"
LOCK = "content/.registration-pending.json"
STAGE = "content/.editor-change-journal.tmp"
INDEXES = (registry.REGISTRY, categories.PATH, registry.RUNTIME)
LIMIT = 128 * 1024 * 1024
FILE_LIMIT = 64 * 1024 * 1024
REVEAL = "picross-catalog-reveal-v4"
BACKGROUND = "picross-catalog-background-v6"
RASTER = "picross-editor-raster-package-v2"


_hashes = ContextVar("editor_operation_hashes", default=None)


def operation(function):
    """Reuse digests of immutable byte objects within one call, never paths."""
    @wraps(function)
    def run(*args, **kwargs):
        token = _hashes.set({})
        try: return function(*args, **kwargs)
        finally: _hashes.reset(token)
    return run


def checksum(raw):
    cache = _hashes.get()
    if raw is None or cache is None: return io.checksum(raw)
    key = id(raw)
    if key not in cache: cache[key] = (raw, io.checksum(raw))
    return cache[key][1]


def ref(name, raw):
    return {"file": name, "sha256": checksum(raw), "bytes": len(raw)}


def identity(entry, raw):
    return {"key": entry["key"], "save_slot": entry["save_slot"],
            "definition": ref("game/"+entry["definition"], raw),
            "runtime_revision": io.json_bytes(raw, 2*1024*1024)["revision"]}


def encoded(value): return canonical_bytes(value) + b"\n"
def pack(raw): return base64.b64encode(raw).decode("ascii") if raw is not None else None


def unpack(value):
    if value is None: return None
    require(isinstance(value, str) and len(value) <= 4*((FILE_LIMIT+2)//3), "Oversized change side")
    raw = base64.b64decode(value, validate=True)
    require(pack(raw) == value, "Noncanonical change side")
    return raw


def pending(root):
    return (io.safe(root, LOCK).exists() or io.safe(root, STAGE).exists()
            or bool(publication.staging(root)))


def validate_index(value, cats):
    """Current index shape and foreign keys; no historical rating acceptance."""
    exact_keys(value, {"format", "entries", "metadata", "backgrounds"})
    registry.require_current(value)
    categories.validate(cats)
    cat_ids = {c["id"] for c in cats["categories"]}
    require(isinstance(value["entries"], list) and len(value["entries"]) <= 10000 and
            isinstance(value["metadata"], list) and len(value["metadata"]) == len(value["entries"]), "Invalid current index size")
    seen = {k: set() for k in ("id", "save_slot", "definition", "reveal")}
    ids = []
    for entry, meta in zip(value["entries"], value["metadata"]):
        exact_keys(entry, {"id", "key", "save_slot", "definition", "reveal", "visible", "production", "category_id"})
        require(isinstance(entry["id"], str) and registry.ID.fullmatch(entry["id"]) and entry["key"] == entry["id"] and
                type(entry["visible"]) is bool and isinstance(entry["production"], dict), "Invalid index identity")
        for key in seen:
            require(isinstance(entry[key], str) and entry[key].casefold() not in seen[key], "Index identity collision")
            seen[key].add(entry[key].casefold())
        relative(entry["definition"]); relative(entry["reveal"])
        require(entry["definition"].startswith("data/content/") and entry["definition"].endswith(".json") and
                entry["reveal"].startswith("art/content/") and entry["reveal"].endswith((".png", ".svg")), "Invalid index resource")
        exact_keys(meta, {"id", "name", "category_id"})
        require(meta["id"] == entry["id"] and meta["category_id"] in cat_ids, "Invalid current metadata binding")
        registry.validate_name(meta["name"])
        ids.append(entry["id"])
    require(ids == sorted(ids), "Unsorted current index")
    bg.index(value)
    return value


class Inputs:
    """One operation's explicit read set, not a cache across operations."""
    def __init__(self, root):
        self.root, self.raw, self.objects = io.external(root), {}, {}

    def read(self, name, limit=FILE_LIMIT, missing=False):
        if name not in self.raw:
            self.raw[name] = io.read(self.root, name, limit, missing=missing)
        return self.raw[name]

    def json(self, name, limit=8*1024*1024, missing=False):
        if name not in self.objects:
            raw = self.read(name, limit, missing)
            self.objects[name] = io.json_bytes(raw, limit) if raw is not None else None
        return self.objects[name]

    def indices(self):
        require(not pending(self.root), "Interrupted publication: recovery required")
        cats = categories.validate(self.json(categories.PATH, categories.MAX_BYTES))
        value = validate_index(self.json(registry.REGISTRY), cats)
        registry.require_current(value)
        runtime = self.json(registry.RUNTIME)
        exact_keys(runtime, {"format", "categories", "entries"})
        require(runtime["format"] in (registry.METADATA_RUNTIME_FORMAT, registry.IMAGE_RUNTIME_FORMAT),
                "Explicit metadata migration required")
        require(isinstance(runtime["entries"], list), "Invalid runtime entries")
        ids = [row["id"] for row in runtime["entries"]]
        require(ids == [row["id"] for row in value["entries"]], "Runtime IDs differ from current index")
        require(runtime["categories"] == categories.ordered(cats), "Runtime categories differ")
        for row, entry, meta in zip(runtime["entries"], value["entries"], value["metadata"]):
            require(all(row[key] == entry[key] for key in ("id", "key", "save_slot", "definition", "visible"))
                    and row["name"] == meta["name"] and row["category_id"] == meta["category_id"],
                    "Current runtime metadata differs")
            relative("game/"+row["reveal"])
        require(not pending(self.root), "Publication started while reading indices")
        return value, cats, runtime


def token(raw): return digest({name: checksum(raw[name]) for name in INDEXES})


@operation
def listing(root, *, inputs=None):
    inputs = inputs or Inputs(root)
    value, cats, runtime = inputs.indices()
    return {"format": "picross-pe-api-v1", "entries": deepcopy(value["metadata"]),
            "categories": categories.ordered(cats), "snapshot": token(inputs.raw),
            "runtime_format": runtime["format"],
            "migration_required": runtime["format"] != registry.IMAGE_RUNTIME_FORMAT}


def readback(raw, identifier):
    """Project the bytes actually read under lock / after the changed writes."""
    value = io.json_bytes(raw[registry.REGISTRY], 8*1024*1024)
    cats = io.json_bytes(raw[categories.PATH], categories.MAX_BYTES)
    runtime = io.json_bytes(raw[registry.RUNTIME], 8*1024*1024)
    return {"catalog": {"format": "picross-pe-api-v1", "entries": value["metadata"],
            "categories": categories.ordered(cats), "snapshot": token(raw), "runtime_format": runtime["format"],
            "migration_required": runtime["format"] != registry.IMAGE_RUNTIME_FORMAT},
            "runtime": next((e for e in runtime["entries"] if e["id"] == identifier), None)}


def selected(value, runtime, identifier):
    entry = next((e for e in value["entries"] if e["id"] == identifier), None)
    require(entry is not None, "Unknown puzzle ID")
    return entry, next(e for e in runtime["entries"] if e["id"] == identifier)


def slim(value): return isinstance(value, dict) and value.get("format") in (REVEAL, BACKGROUND)


def technical_entry(entry):
    exact_keys(entry, {"id", "key", "save_slot", "definition", "reveal", "visible", "production", "category_id"})
    rating.identity(entry["id"])
    require(entry["key"] == entry["id"] and isinstance(entry["save_slot"], str) and registry.STEM.fullmatch(entry["save_slot"]) and
            type(entry["visible"]) is bool, "Invalid selected identity")
    for key, prefix, suffixes in (("definition", "data/content/", (".json",)), ("reveal", "art/content/", (".png", ".svg"))):
        relative(entry[key]); require(entry[key].startswith(prefix) and entry[key].endswith(suffixes), "Invalid selected resource path")
    production = entry["production"]
    require(isinstance(production, dict) and production.get("mode") in ("mono", "color"), "Invalid selected production mode")
    relative(production["package"])
    require(production["package"].startswith("content/packages/"), "Invalid selected package reference")
    for key in ("definition_sha256", "reveal_sha256", "package_sha256"): sha(production[key])
    for key in ("width", "height"): integer(production[key], 1, 50, "selected "+key)
    # Historical editorial estimates/descriptions are opaque retained values.
    return entry


def validate_binding(value, identifier):
    exact_keys(value, {"entry", "identity"})
    entry = technical_entry(value["entry"])
    identity = exact_keys(value["identity"], {"key", "save_slot", "definition", "runtime_revision"})
    require(entry["id"] == identifier and all(identity[k] == entry[k] for k in ("key", "save_slot")), "Current identity differs")
    bg._ref(identity["definition"], name="game/"+entry["definition"], limit=2*1024*1024)
    require(identity["definition"]["sha256"] == entry["production"]["definition_sha256"], "Current definition hash differs")
    integer(identity["runtime_revision"], 1, 1000000, "runtime revision")
    return value


def validate_source(value, entry=None):
    exact_keys(value, {"format", "id", "record_revision", "binding", "current", "record_hash"})
    require(slim(value), "Unsupported current editor source")
    rating.identity(value["id"])
    validate_binding(value["binding"], value["id"])
    if entry is not None:
        expected = deepcopy(entry)
        expected["production"]["package_sha256"] = value["binding"]["entry"]["production"]["package_sha256"]
        require(value["binding"]["entry"] == expected, "Stale editor source binding")
    integer(value["record_revision"], 1, 1000000, "record revision")
    current = value["current"]
    exact_keys(current, {"image_revision", "asset"} | ({"status"} if value["format"] == BACKGROUND else set()))
    integer(current["image_revision"], 1, 1000000, "image revision")
    if value["format"] == BACKGROUND:
        require(current["status"] in ("standard", "selected", "none"), "Invalid background preference")
        if current["status"] != "selected": require(current["asset"] is None, "Image-free preference has asset")
        else: bg._ref(current["asset"], name=bg.asset_path(value["id"]), limit=32*1024*1024)
    else:
        e = value["binding"]["entry"]
        allowed = {Path("game/"+e["reveal"]).with_suffix(s).as_posix() for s in (".png", ".svg")}
        bg._ref(current["asset"], limit=32*1024*1024)
        require(current["asset"]["file"] in allowed, "Foreign reveal path")
    require(value["record_hash"] == digest({k: v for k, v in value.items() if k != "record_hash"}), "Source hash differs")
    return value


def source(inputs, entry, kind):
    name = "content/"+("reveals" if kind == "reveal" else "backgrounds")+"/"+entry["id"]+".json"
    value = inputs.json(name, 1024*1024, missing=True)
    if slim(value): validate_source(value, entry)
    if kind == "background":
        index = inputs.json(registry.REGISTRY)
        declared = next((r["source"] for r in index["backgrounds"] if r["id"] == entry["id"]), None)
        require((value is None) == (declared is None), "Background source/index differ")
        if declared is not None: require(ref(name, inputs.raw[name]) == declared, "Background index binding differs")
    if slim(value):
        runtime = inputs.json(registry.RUNTIME)
        row = next(r for r in runtime["entries"] if r["id"] == entry["id"])
        if kind == "reveal":
            require(value["current"]["asset"]["file"] == "game/"+row["reveal"], "Current reveal projection differs")
        else:
            projected = deepcopy(value["current"])
            if projected["asset"]: projected["asset"]["file"] = projected["asset"]["file"].removeprefix("game/")
            require(projected == row["background"], "Current background projection differs")
    return value


@operation
def detail(root, identifier, expected=None):
    inputs = Inputs(root)
    value, cats, runtime = inputs.indices()
    require(expected is None or expected == token(inputs.raw), "Catalog changed; reload")
    entry, row = selected(value, runtime, identifier)
    raw = inputs.read("game/"+entry["definition"], 2*1024*1024)
    definition = rating.definition(raw)[0]
    require(checksum(raw) == entry["production"]["definition_sha256"], "Selected definition changed")
    reveal, background = source(inputs, entry, "reveal"), source(inputs, entry, "background")
    result = {"id": identifier, "entry": entry, "metadata": next(e for e in value["metadata"] if e["id"] == identifier),
              "reveal": reveal, "background": background, "runtime": row}
    # UI receives only current technical values, never historical descriptions.
    result["reveal"] = {"file": row["reveal"]}
    result["background"] = deepcopy(row["background"])
    names = {"game/"+row["reveal"]: None}
    if slim(reveal): names = {reveal["current"]["asset"]["file"]: reveal["current"]["asset"]["sha256"]}
    if row["background"]["status"] == "selected":
        ref = row["background"]["asset"]
        names["game/"+ref["file"]] = ref["sha256"]
    return {"detail": result, "raster": {"text": "\n".join(" ".join(map(str, r)) for r in definition["solution"]),
            "palette": definition["palette"], "width": definition["width"], "height": definition["height"],
            "revision": definition["revision"]}, "snapshot": token(inputs.raw),
            "definition_sha256": checksum(raw), "_resources": names,
            "source_migration_required": not slim(reveal) or not slim(background)}


def _summary(value, runtime, identifier):
    if identifier is None: return None
    entry, row = selected(value, runtime, identifier)
    return {"entry": deepcopy(entry), "metadata": deepcopy(next(e for e in value["metadata"] if e["id"] == identifier)),
            "runtime": deepcopy(row), "reveal": row["reveal"], "background": deepcopy(row["background"])}


def _record(entry, definition_raw, previous, kind, current):
    revision = previous.get("record_revision", 0) if isinstance(previous, dict) else 0
    value = {"format": REVEAL if kind == "reveal" else BACKGROUND, "id": entry["id"],
             "record_revision": revision+1, "binding": {"entry": deepcopy(entry), "identity": identity(entry, definition_raw)},
             "current": current}
    value["record_hash"] = digest(value)
    return validate_source(value, entry)


@catalog_method.bound_validation
@operation
def plan(root, request, *, uploads=None, work=None, expected=None, expected_definition=None):
    """Prepare once. uploads are already technically checked immutable bytes.

    Public file imports use editor_cli.plan_file; desktop keeps that result in
    its private workspace. Apply never re-runs image or solver preparation.
    """
    inputs = Inputs(root)
    value, cats, runtime = inputs.indices()
    require(expected is None or token(inputs.raw) == expected, "Relevant catalog changed; reload")
    target, target_cats, target_runtime = deepcopy(value), deepcopy(cats), deepcopy(runtime)
    identifier = request.get("id") if request else None
    entry, row = selected(value, runtime, identifier) if identifier is not None else (None, None)
    before = _summary(value, runtime, identifier)
    changes, quality = {}, None
    action = "metadata"
    def put(name, raw):
        old = inputs.read(name, missing=True)
        if old != raw: changes[name] = {"old": pack(old), "new": pack(raw)}
    require(runtime["format"] == registry.IMAGE_RUNTIME_FORMAT, "This checkout requires external migration: issue #641")
    exact_keys(request, {"id", "metadata", "text", "profile", "reveal", "background"})
    operations = request["metadata"] if identifier is None else (
        [{"op": "set_metadata", "id": identifier, **request["metadata"]}] if request["metadata"] else [])
    if identifier is None:
        require(all(request[k] is None for k in ("text", "profile", "reveal", "background")), "Category action has puzzle inputs")
    target, target_cats = metadata._edit(value, cats, metadata._operations(operations, catalog=cats), validate_registry=validate_index)
    target_runtime["categories"] = categories.ordered(target_cats)
    meta = {e["id"]: e for e in target["metadata"]}
    for item in target_runtime["entries"]:
        item.update(name=meta[item["id"]]["name"], category_id=meta[item["id"]]["category_id"])
    if identifier is not None and any(request[k] is not None for k in ("text", "reveal", "background")):
        require(runtime["format"] == registry.IMAGE_RUNTIME_FORMAT, "Explicit v7→v8 migration required")
        action = "raster" if request["text"] is not None else "images"
        definition_raw = inputs.read("game/"+entry["definition"], 2*1024*1024)
        require(expected_definition is None or checksum(definition_raw) == expected_definition, "Selected raster changed; reload")
        definition = rating.definition(definition_raw)[0]
        require(checksum(definition_raw) == entry["production"]["definition_sha256"], "Selected definition differs from index")
        target_entry, target_row = selected(target, target_runtime, identifier)
        if request["text"] is not None:
            matrix = raster.parse(request["text"], definition["palette"])
            new_definition = raster.definition(definition, matrix)
            before["definition"] = definition
            if new_definition != definition:
                require(work is not None, "Raster preparation requires a private workspace")
                work = io.external(work)
                require(not work.is_relative_to(inputs.root), "Raster workspace must be outside checkout")
                quality, package = _prepare_raster(inputs, entry, definition_raw, new_definition, request["profile"], Path(work))
                prefix = "content/packages/"+identifier+"/editor-"+str(new_definition["revision"])
                for name, raw in package.items():
                    require(inputs.read(prefix+"/"+name, missing=True) is None, "New raster package path occupied")
                    put(prefix+"/"+name, raw)
                definition_raw = encoded(new_definition)
                put("game/"+entry["definition"], definition_raw)
                target_entry["production"].update(package=prefix, package_sha256=checksum(package["manifest.json"]),
                    revision="editor-"+str(new_definition["revision"]), definition_sha256=checksum(definition_raw),
                    width=new_definition["width"], height=new_definition["height"])
                rating_path = rating.path(identifier)
                previous_rating = inputs.json(rating_path, 1024*1024, missing=True)
                active = rating.active_record(quality["checked"], previous_rating)
                put(rating_path, encoded(active))
                target_row["difficulty"] = rating.project(active)
            definition = new_definition
        for kind in ("reveal", "background"):
            part = request[kind]
            # Only a real raster change needs both current bindings rebound.
            if part is None and quality is None: continue
            previous = source(inputs, entry, kind)
            require(slim(previous), "Current image sources require external migration: issue #641 M2")
            current = None
            if kind == "reveal":
                old_name = "game/"+row["reveal"]
                if part is not None:
                    exact_keys(part, {"upload"})
                    upload = uploads[part["upload"]]
                    raw, suffix = upload["raw"], upload["suffix"]
                    require(upload["checked"]["sha256"] == checksum(raw) and
                            upload["checked"]["width"] >= 2*definition["width"] and
                            upload["checked"]["height"] >= 2*definition["height"], "Prepared reveal dimensions/binding differ")
                    name = Path("game/"+entry["reveal"]).with_suffix("."+suffix).as_posix()
                    old = inputs.read(old_name, 32*1024*1024)
                    if raw != old or name != old_name:
                        if name != old_name: put(old_name, None)
                        put(name, raw)
                        old_revision = (previous.get("current", {}).get("image_revision", 0) if previous else 0)
                        current = {"image_revision": old_revision+1, "asset": ref(name, raw)}
                        target_row["reveal"] = name.removeprefix("game/")
                if current is None and quality is not None:
                    current = deepcopy(previous["current"])
            else:
                old_current = row["background"]
                if part is not None:
                    exact_keys(part, {"status", "upload"})
                    require(part["status"] in ("standard", "selected", "none"), "Invalid background preference")
                    raw = uploads[part["upload"]]["raw"] if part["upload"] else None
                    if raw is not None:
                        from .editor_image_input import PROFILE
                        checked = uploads[part["upload"]]["checked"]
                        require(checked["profile"] == PROFILE and checked["sha256"] == checksum(raw), "Prepared background binding differs")
                    require(part["status"] == "selected" or raw is None, "Image-free background has upload")
                    asset = None
                    if part["status"] == "selected":
                        if raw is None:
                            require(old_current["status"] == "selected", "Background image required")
                            asset = deepcopy(old_current["asset"]); asset["file"] = "game/"+asset["file"]
                        else: asset = ref(bg.asset_path(identifier), raw)
                    old_asset = deepcopy(old_current["asset"])
                    if old_asset: old_asset["file"] = "game/"+old_asset["file"]
                    if (part["status"], asset) != (old_current["status"], old_asset):
                        if part["status"] in ("selected", "none"):
                            capability = inputs.json(bg.CAPABILITY, 4096, missing=True)
                            bg.capability(inputs.root, {bg.CAPABILITY: encoded(capability) if capability else None}, required=True)
                        if raw is not None: put(bg.asset_path(identifier), raw)
                        elif old_current["status"] == "selected": put(bg.asset_path(identifier), None)
                        current = {"image_revision": (old_current["image_revision"] or 0)+1, "status": part["status"], "asset": asset}
                        target_row["background"] = deepcopy(current)
                        if asset: target_row["background"]["asset"]["file"] = asset["file"].removeprefix("game/")
                if current is None and quality is not None and previous is not None:
                    current = deepcopy(row["background"])
                    if current["asset"]: current["asset"]["file"] = "game/"+current["asset"]["file"]
            if current is not None:
                record = _record(target_entry, definition_raw, previous, kind, current)
                name = "content/"+("reveals" if kind == "reveal" else "backgrounds")+"/"+identifier+".json"
                put(name, encoded(record))
                if kind == "background":
                    target["backgrounds"] = sorted([e for e in target["backgrounds"] if e["id"] != identifier]+
                        [{"id": identifier, "source": ref(name, encoded(record))}], key=lambda e: e["id"])
    for name, old, new in ((registry.REGISTRY, value, target), (categories.PATH, cats, target_cats), (registry.RUNTIME, runtime, target_runtime)):
        if old != new: put(name, encoded(new))
    after = _summary(target, target_runtime, identifier)
    if action == "raster": after["definition"] = definition
    if action == "metadata":
        before, after = [], []
        for kind, old_rows, new_rows in (("puzzle", value["metadata"], target["metadata"]), ("category", cats["categories"], target_cats["categories"])):
            old, new = {r["id"]: r for r in old_rows}, {r["id"]: r for r in new_rows}
            after.extend({"kind": kind, "id": key, "before": old.get(key), "after": new.get(key)}
                         for key in sorted(set(old)|set(new)) if old.get(key) != new.get(key))
        before = deepcopy(after)
    result = {"format": PLAN, "action": action, "id": identifier, "entry": entry,
              "reads": {name: checksum(raw) for name, raw in inputs.raw.items()}, "changes": changes,
              "before": before, "after": after, "quality": quality}
    result["plan_hash"] = digest(result)
    require(len(encoded(result)) <= LIMIT, "Change plan exceeds 128 MiB")
    return result


def _prepare_raster(inputs, entry, previous, definition, profile, work):
    from . import catalog_method, catalog_analysis
    from .solver import solve
    from .verifier import verify
    from .contract import Budget
    require(profile in ("line", "paired"), "Invalid deduction profile")
    directory = work/"raster"; directory.mkdir()
    raw = encoded(definition)
    files = {"definition.json": raw, "previous-definition.json": previous}
    for name, data in files.items(): (directory/name).write_bytes(data)
    puzzle = rating.definition(raw)[1]
    baseline = solve(puzzle, Budget()) if profile == "paired" else None
    proof = solve(puzzle, Budget(), profile="paired-lines-color" if baseline is not None else None)
    check = verify(puzzle, proof, Budget())
    require(check["certified"], "Raster has no complete deduction proof")
    raster.check_end(definition, proof)
    files["proof.json"] = encoded(proof)
    if baseline is not None:
        verify(puzzle, baseline, Budget())
        files["baseline.json"] = encoded(baseline)
    for name, data in files.items(): (directory/name).write_bytes(data)
    method = catalog_method.current(catalog_method.from_bytes(inputs.read(catalog_method.PATH, 65536, missing=True)))["method"]
    checked = catalog_analysis.analyze_single(directory/"definition.json", directory/"analysis",
        production_mode=entry["production"]["mode"], method=method,
        proof=directory/"proof.json" if baseline is not None else None,
        baseline=directory/"baseline.json" if baseline is not None else None)
    quality = {"method": method, "checked": checked, "proof": ref("proof.json", files["proof.json"]),
               "baseline": ref("baseline.json", files["baseline.json"]) if baseline is not None else None}
    # Traversal is confined to this operation's newly generated proof output.
    for path in (directory/"analysis").rglob("*"):
        if path.is_file(): files[path.relative_to(directory).as_posix()] = path.read_bytes()
    manifest = {"format": RASTER, "id": entry["id"], "revision": "editor-"+str(definition["revision"]),
        "previous": {"entry": entry, "identity": identity(entry, previous)},
        "definition": ref("definition.json", raw), "quality": quality,
        "files": {name: checksum(data) for name, data in files.items()}}
    manifest["package_hash"] = digest(manifest)
    files["manifest.json"] = encoded(manifest)
    return quality, files


def validate(value, *, journal=False):
    keys = {"format", "action", "id", "entry", "reads", "changes"}
    exact_keys(value, keys if journal else keys | {"before", "after", "quality", "plan_hash"})
    require(value["format"] == (JOURNAL if journal else PLAN), "Unsupported change format")
    require(value["action"] in ("metadata", "images", "raster"), "Invalid editor action")
    if not journal:
        require(value["plan_hash"] == digest({k: v for k, v in value.items() if k != "plan_hash"}), "Plan changed")
    allowed = set(INDEXES)
    entry, identifier = value["entry"], value["id"]
    if identifier is not None:
        technical_entry(entry)
        require(entry["id"] == identifier, "Selected identity differs")
    else: require(entry is None, "Unselected entry")
    if value["action"] in ("images", "raster"):
        require(entry is not None, "Puzzle action requires ID")
        allowed |= {"game/"+entry["definition"], "content/reveals/"+identifier+".json", bg.path(identifier), bg.asset_path(identifier), bg.CAPABILITY}
        allowed |= {Path("game/"+entry["reveal"]).with_suffix(s).as_posix() for s in (".png", ".svg")}
    package_prefix = "content/packages/"+identifier+"/editor-" if identifier else ""
    if value["action"] == "raster":
        from .catalog_method import PATH
        allowed |= {rating.path(identifier), PATH}
    require(isinstance(value["reads"], dict) and isinstance(value["changes"], dict), "Invalid read/write set")
    require(set(INDEXES) <= set(value["reads"]), "Missing index conflict bindings")
    for name, expected_hash in value["reads"].items():
        relative(name)
        package = value["action"] == "raster" and bool(re.fullmatch(re.escape(package_prefix)+r"[1-9][0-9]{0,6}/(?:manifest\.json|definition\.json|previous-definition\.json|proof\.json|baseline\.json|analysis/[a-z0-9/.-]+)", name))
        require(name in allowed or package, "Unrelated editor input: "+name)
        if expected_hash is not None: sha(expected_hash)
        if package: require(expected_hash is None and name in value["changes"], "Historical package input forbidden")
    sides = {}
    for name, pair in value["changes"].items():
        require(name in value["reads"], "Unbound change target")
        exact_keys(pair, {"old", "new"})
        old, new = unpack(pair["old"]), unpack(pair["new"])
        require(old != new and checksum(old) == value["reads"][name], "Invalid old target binding")
        require(name not in (bg.CAPABILITY, "content/difficulty-method.json"), "Read-only input cannot be edited")
        if value["action"] != "raster": require(name in allowed and (entry is None or name != "game/"+entry["definition"]), "Invalid action target")
        sides[name] = (old, new)
    require(len(encoded(value)) <= LIMIT, "Oversized editor transaction")
    return sides


@catalog_method.bound_validation
def validate_targets(value, sides, actual):
    """Closed technical deltas, using already read bytes; no plan rebuilding."""
    target = {**actual, **{name: pair[1] for name, pair in sides.items()}}
    before = io.json_bytes(actual[registry.REGISTRY], 8*1024*1024)
    cats = categories.validate(io.json_bytes(target[categories.PATH], categories.MAX_BYTES))
    after = validate_index(io.json_bytes(target[registry.REGISTRY], 8*1024*1024), cats)
    action, identifier = value["action"], value["id"]
    if identifier is not None:
        require(next((e for e in before["entries"] if e["id"] == identifier), None) == value["entry"],
                "Selected plan entry differs from current index")
    if action != "metadata":
        require(actual[categories.PATH] == target[categories.PATH], "Puzzle edit changes category definitions")
    require([e["id"] for e in before["entries"]] == [e["id"] for e in after["entries"]], "Editor cannot create/remove puzzle IDs")
    for old, new in zip(before["entries"], after["entries"]):
        if action != "raster" or old["id"] != identifier:
            require(old == new, "Editor changes unrelated production entry")
        else:
            require(old == value["entry"], "Plan entry differs from current index")
            require(all(old[k] == new[k] for k in old if k != "production"), "Raster changes fixed identity")
            mutable = {"package", "package_sha256", "revision", "definition_sha256", "width", "height"}
            require({k: v for k, v in old["production"].items() if k not in mutable} ==
                    {k: v for k, v in new["production"].items() if k not in mutable}, "Raster changes unrelated production metadata")
    if action == "metadata":
        require(before["backgrounds"] == after["backgrounds"], "Metadata changes image sources")
    else:
        require([e for e in before["backgrounds"] if e["id"] != identifier] ==
                [e for e in after["backgrounds"] if e["id"] != identifier], "Unrelated background index changed")
        require([e for e in before["metadata"] if e["id"] != identifier] ==
                [e for e in after["metadata"] if e["id"] != identifier], "Unrelated metadata changed")
    old_runtime = io.json_bytes(actual[registry.RUNTIME], 8*1024*1024)
    runtime = io.json_bytes(target[registry.RUNTIME], 8*1024*1024)
    exact_keys(runtime, {"format", "categories", "entries"})
    require(runtime["categories"] == categories.ordered(cats), "Runtime category projection differs")
    require(runtime["format"] == registry.IMAGE_RUNTIME_FORMAT, "Invalid runtime generation")
    require(len(runtime["entries"]) == len(old_runtime["entries"]), "Runtime IDs changed")
    for old, new, meta in zip(old_runtime["entries"], runtime["entries"], after["metadata"]):
        expected = {**old, "name": meta["name"], "category_id": meta["category_id"]}
        if identifier == old["id"] and action in ("images", "raster"):
            for key in ("reveal", "background") + (("difficulty",) if action == "raster" else ()):
                expected[key] = new[key]
        require(expected == new, "Unexpected runtime delta")
    for name, (_, raw) in sides.items():
        if name.startswith(("content/reveals/", "content/backgrounds/")):
            require(raw is not None, "Cannot remove active editor source")
            entry = next(e for e in after["entries"] if e["id"] == identifier)
            validate_source(io.json_bytes(raw, 1024*1024), entry)
    if identifier and action in ("images", "raster"):
        entry, row = selected(after, runtime, identifier)
        definition_path = "game/"+entry["definition"]
        for kind, field in (("reveal", "reveal"), ("background", "background")):
            source_path = "content/"+("reveals" if kind == "reveal" else "backgrounds")+"/"+identifier+".json"
            old_row = next(r for r in old_runtime["entries"] if r["id"] == identifier)
            if row[field] != old_row[field] or definition_path in sides:
                require(source_path in sides, "Changed runtime/definition lacks current image source")
            if kind == "background" and before["backgrounds"] != after["backgrounds"]:
                require(source_path in sides, "Background index changed without source")
        for name, (old_raw, new_raw) in sides.items():
            if not name.startswith("game/art/"): continue
            kind = "background" if name == bg.asset_path(identifier) else "reveal"
            source_path = "content/"+("reveals" if kind == "reveal" else "backgrounds")+"/"+identifier+".json"
            require(source_path in sides, "Image bytes changed without current source")
            current = io.json_bytes(target[source_path], 1024*1024)["current"]["asset"]
            previous = io.json_bytes(actual[source_path], 1024*1024)["current"]["asset"]
            if new_raw is None:
                require(previous is not None and previous["file"] == name and
                        (current is None or current["file"] != name), "Unbound image deletion")
            else:
                require(current == ref(name, new_raw), "Image bytes lack exact current binding")
        definition_raw = target[definition_path]
        require(checksum(definition_raw) == entry["production"]["definition_sha256"], "New definition/index binding differs")
        for kind in ("reveal", "background"):
            name = "content/"+("reveals" if kind == "reveal" else "backgrounds")+"/"+identifier+".json"
            if name not in sides: continue
            current = io.json_bytes(target[name], 1024*1024)
            require(current["binding"]["identity"] == identity(entry, definition_raw), "New source definition binding differs")
            old = io.json_bytes(actual[name], 1024*1024)
            validate_source(old, value["entry"])
            require(current["record_revision"] == old["record_revision"]+1, "Invalid source revision")
            previous_image, image = old["current"], current["current"]
            require(image["image_revision"] == previous_image["image_revision"] +
                    int({k: v for k, v in image.items() if k != "image_revision"} !=
                        {k: v for k, v in previous_image.items() if k != "image_revision"}), "Invalid image revision")
            if image["asset"] and image["asset"]["file"] in sides:
                require(ref(image["asset"]["file"], target[image["asset"]["file"]]) == image["asset"], "New image bytes differ")
            if kind == "reveal": require(row["reveal"] == image["asset"]["file"].removeprefix("game/"), "New reveal projection differs")
            else:
                projected = deepcopy(image)
                if projected["asset"]: projected["asset"]["file"] = projected["asset"]["file"].removeprefix("game/")
                require(row["background"] == projected and next(r["source"] for r in after["backgrounds"] if r["id"] == identifier) == ref(name, target[name]), "New background projection differs")
        if definition_path in sides:
            old_def, new_def = (rating.definition(raw)[0] for raw in sides[definition_path])
            require(new_def == raster.definition(old_def, new_def["solution"]) and new_def["revision"] == old_def["revision"]+1, "Invalid raster delta")
            prefix = entry["production"]["package"]
            manifest = raster.validate(io.json_bytes(target[prefix+"/manifest.json"], 1024*1024), definition_raw)
            require(checksum(target[prefix+"/manifest.json"]) == entry["production"]["package_sha256"] and
                    manifest["previous"] == {"entry": value["entry"], "identity": identity(value["entry"], actual[definition_path])}, "New raster predecessor differs")
            require({n.removeprefix(prefix+"/") for n in sides if n.startswith("content/packages/")} == set(manifest["files"])|{"manifest.json"}, "New raster inventory differs")
            for name, expected_hash in manifest["files"].items():
                require(checksum(target[prefix+"/"+name]) == expected_hash, "New raster file differs")
            active = rating.validate(io.json_bytes(target[rating.path(identifier)], 1024*1024), definition_bytes=definition_raw)
            require(row["difficulty"] == rating.project(active), "New difficulty projection differs")
    return target


def _temp(name, checksum):
    return (Path(name).parent/(".editor-"+checksum+"-"+digest(name)[:16]+".tmp")).as_posix()


def checkpoint(phase, name=None):
    """Fault injection seam; production performs no action."""


def _write(root, name, old, new, checksum):
    target = publication.durable_parents(root, name)
    temporary = _temp(name, checksum)
    require(not io.safe(root, temporary).exists(), "Foreign editor temporary: "+temporary)
    if new is not None:
        with io.safe(root, temporary).open("xb") as stream:
            require(stream.write(new) == len(new), "Short target write")
            stream.flush(); os.fsync(stream.fileno())
    checkpoint("before-target", name)
    require(io.read(root, name, FILE_LIMIT, missing=True) == old, "Target changed: "+name)
    if new is None:
        io.safe(root, name).unlink(); publication.sync_directory(target.parent)
    else: publication.rename(io.safe(root, temporary), io.safe(root, name), replace=old is not None)
    actual = io.read(root, name, FILE_LIMIT, missing=True)
    require(actual == new, "Published target differs: "+name)
    checkpoint("after-runtime" if name == registry.RUNTIME else "after-target", name)
    return actual


@operation
def apply(root, value):
    root = io.external(root)
    sides = validate(value)
    require(not pending(root), "Publication pending; recovery required")
    if not sides:
        actual = {}
        for name, expected_hash in value["reads"].items():
            actual[name] = io.read(root, name, FILE_LIMIT, missing=True)
            require(checksum(actual[name]) == expected_hash, "Relevant input changed: "+name)
        require(not pending(root), "Publication started during no-op readback")
        return {"status": "noop", "files": [], **readback(actual, value["id"])}
    journal = {k: deepcopy(value[k]) for k in ("action", "id", "entry", "reads", "changes")}
    journal["format"] = JOURNAL
    raw = publication.journal_bytes(journal)
    journal_hash = checksum(raw)
    checkpoint("before-journal")
    with io.safe(root, STAGE).open("xb") as stream:
        require(stream.write(raw) == len(raw), "Short journal write")
        stream.flush(); os.fsync(stream.fileno())
    publication.rename(io.safe(root, STAGE), io.safe(root, LOCK), replace=False)
    lock_identity = io.signature(io.safe(root, LOCK).stat())
    checkpoint("after-journal")
    # One fresh relevant-input pass under the common lock, byte based even when
    # an external writer preserves mtime. No reconstruction of the preparation.
    actual = {}
    try:
        require(io.signature(io.safe(root, LOCK).stat()) == lock_identity, "Writer lock changed")
        for name, expected in value["reads"].items():
            actual[name] = io.read(root, name, FILE_LIMIT, missing=True)
            require(checksum(actual[name]) == expected, "Relevant input changed: "+name)
        validate_targets(value, sides, actual)
    except Exception:
        # No target write has started. Release only our byte-identical journal;
        # a stale plan must not strand a foreign edit behind an unusable lock.
        if io.read(root, LOCK, LIMIT) == raw:
            io.safe(root, LOCK).unlink(); publication.sync_directory(root/"content")
        raise
    for name in sorted(sides, key=lambda n: (n == registry.RUNTIME, n)):
        require(io.signature(io.safe(root, LOCK).stat()) == lock_identity, "Writer lock changed")
        actual[name] = _write(root, name, *sides[name], journal_hash)
    require(io.read(root, LOCK, LIMIT) == raw, "Writer journal changed")
    io.safe(root, LOCK).unlink(); publication.sync_directory(root/"content")
    checkpoint("complete")
    return {"status": "updated", "files": sorted(sides), **readback(actual, value["id"]),
            "definition_sha256": checksum(actual.get("game/"+value["entry"]["definition"])) if value["entry"] else None}


@operation
def recover(root):
    root = io.external(root)
    name = LOCK if io.safe(root, LOCK).exists() else STAGE
    raw = io.read(root, name, LIMIT, missing=True)
    if raw is None: return {"status": "noop", "registered": False}
    import zlib
    require(raw.startswith(publication.EDITOR_PREFIX), "Unknown editor journal encoding")
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(raw[len(publication.EDITOR_PREFIX):], LIMIT+1)
    require(len(decoded) <= LIMIT and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
            "Incomplete/oversized editor journal")
    journal = io.json_bytes(decoded, LIMIT)
    sides = validate(journal, journal=True)
    require(bool(sides), "Empty editor journal is not an owned publication")
    require(publication.journal_bytes(journal) == raw, "Noncanonical editor journal")
    journal_hash = checksum(raw)
    actual, temps = {}, {}
    # Validate the entire small write set before the first recovery mutation.
    for target, pair in sides.items():
        current = io.read(root, target, FILE_LIMIT, missing=True)
        require(current in pair, "Foreign target blocks recovery: "+target)
        actual[target] = current
        temporary = _temp(target, journal_hash)
        temp = io.read(root, temporary, FILE_LIMIT, missing=True)
        if temp is not None:
            require(any(data is not None and data.startswith(temp) for data in pair), "Foreign temporary: "+temporary)
            temps[temporary] = temp
    old_inputs = {target: pair[0] for target, pair in sides.items()}
    for target, expected in journal["reads"].items():
        if target not in sides:
            old_inputs[target] = io.read(root, target, FILE_LIMIT, missing=True)
            require(checksum(old_inputs[target]) == expected, "Recovery dependency changed: "+target)
    validate_targets(journal, sides, old_inputs)
    for temporary, temp in temps.items():
        require(io.read(root, temporary, FILE_LIMIT) == temp, "Recovery temporary changed")
        io.safe(root, temporary).unlink(); publication.sync_directory(io.safe(root, temporary).parent)
    for target in sorted(sides, key=lambda n: (n == registry.RUNTIME, n)):
        if actual[target] != sides[target][0]: _write(root, target, actual[target], sides[target][0], journal_hash)
    require(io.read(root, name, LIMIT) == raw, "Recovery journal changed")
    io.safe(root, name).unlink(); publication.sync_directory(root/"content")
    return {"status": "rolled-back", "registered": False}
