"""PE-EDIT2: selected inputs and prepared bytes, never a catalog certification.

This is the shared API/CLI/desktop edit path. Explicit full diagnostics and
current metadata operations retain their own readers. Nothing here traverses a catalog tree.
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
from . import catalog_io as io, categories, content_registry as registry, current_content
from . import puzzle_record, puzzle_catalog
from . import catalog_publication as publication, catalog_metadata as metadata
from . import catalog_background as bg, editor_raster as raster, catalog_rating as rating, catalog_method

PLAN = "picross-puzzle-editor-plan-v1"
JOURNAL = "picross-puzzle-editor-journal-v1"
LOCK = "content/.registration-pending.json"
STAGE = "content/.editor-change-journal.tmp"
INDEXES = (categories.PATH, registry.RUNTIME)
LIMIT = 128 * 1024 * 1024
FILE_LIMIT = 64 * 1024 * 1024


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


def parsed_definition(raw):
    parsed = rating.definition(raw)
    cache = _hashes.get()
    if cache is not None: cache[id(raw)] = (raw, parsed[2]["definition_sha256"])
    return parsed


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
    require(len(raw) <= FILE_LIMIT and pack(raw) == value, "Noncanonical change side")
    return raw


def pending(root):
    return (io.safe(root, LOCK).exists() or io.safe(root, STAGE).exists()
            or bool(publication.staging(root)))


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
        cats,runtime = puzzle_catalog.index(self.read,puzzle_record.inventory(self.root))
        value = metadata._state(runtime)
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
    cats = io.json_bytes(raw[categories.PATH],categories.MAX_BYTES)
    runtime = io.json_bytes(raw[registry.RUNTIME],current_content.RUNTIME_LIMIT)
    value = metadata._state(runtime)
    return {"catalog": {"format": "picross-pe-api-v1", "entries": value["metadata"],
            "categories": categories.ordered(cats), "snapshot": token(raw), "runtime_format": runtime["format"],
            "migration_required": runtime["format"] != registry.IMAGE_RUNTIME_FORMAT},
            "runtime": next((e for e in runtime["entries"] if e["id"] == identifier), None)}


def selected(inputs,cats,runtime,identifier):
    record = puzzle_record.load(inputs.root,identifier,category_catalog=cats,read=inputs.read)
    row = next((r for r in runtime["entries"] if r["id"] == identifier),None)
    require(row == puzzle_record.runtime_row(record), "Selected projection differs")
    return record,row


@operation
def detail(root, identifier, expected=None):
    inputs = Inputs(root)
    value, cats, runtime = inputs.indices()
    require(expected is None or expected == token(inputs.raw), "Catalog changed; reload")
    record,row = selected(inputs,cats,runtime,identifier)
    entry = puzzle_record.entry(record)
    raw = inputs.read(record["definition"]["file"],2*1024*1024)
    definition = io.json_bytes(raw,2*1024*1024)
    result = {"id":identifier,"entry":entry,"metadata":{k:record[k] for k in ("id","name","category_id")},
              "reveal":{"file":row["reveal"]},"background":deepcopy(row["background"]),"runtime":row}
    names = {record["reveal"]["asset"]["file"]:record["reveal"]["asset"]["sha256"]}
    if record["background"]["asset"]:
        asset = record["background"]["asset"]
        names[asset["file"]] = asset["sha256"]
    return {"detail": result, "raster": {"text": "\n".join(" ".join(map(str, r)) for r in definition["solution"]),
            "palette": definition["palette"], "width": definition["width"], "height": definition["height"],
            "revision": definition["revision"]}, "snapshot": token(inputs.raw),
            "definition_sha256": checksum(raw), "_resources": names,
            "source_migration_required": False}


def _summary(record,row):
    if record is None:
        return None
    return {"entry":puzzle_record.entry(record),"metadata":{k:record[k] for k in ("id","name","category_id")},
            "runtime":deepcopy(row),"reveal":row["reveal"],"background":deepcopy(row["background"])}


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
    original,row = selected(inputs,cats,runtime,identifier) if identifier is not None else (None,None)
    proposed = deepcopy(original)
    entry = puzzle_record.entry(original) if original else None
    before = _summary(original,row)
    changes, quality = {}, None
    action = "metadata"
    def put(name, raw):
        old = inputs.read(name, missing=True)
        if old != raw: changes[name] = {"old": pack(old), "new": pack(raw)}
    exact_keys(request, {"id", "metadata", "text", "profile", "reveal", "background"})
    operations = request["metadata"] if identifier is None else (
        [{"op": "set_metadata", "id": identifier, **request["metadata"]}] if request["metadata"] else [])
    if identifier is None:
        require(all(request[k] is None for k in ("text", "profile", "reveal", "background")), "Category action has puzzle inputs")
    target, target_cats = metadata._edit(value, cats, metadata._operations(operations, catalog=cats), validate_registry=metadata._validate_metadata)
    target_runtime["categories"] = categories.ordered(target_cats)
    meta = {e["id"]: e for e in target["metadata"]}
    for item in target_runtime["entries"]:
        key = item["id"]
        if any(item[k] != meta[key][k] for k in ("name","category_id")):
            updated = proposed if key == identifier else selected(inputs,cats,runtime,key)[0]
            updated.update(meta[key])
            item.update(meta[key])
            if key != identifier:
                put(puzzle_record.path(key), puzzle_record.encode(updated))
    if identifier is not None and any(request[k] is not None for k in ("text", "reveal", "background")):
        action = "raster" if request["text"] is not None else "images"
        definition_raw = inputs.read("game/"+entry["definition"], 2*1024*1024)
        definition = io.json_bytes(definition_raw, 2*1024*1024)
        _hashes.get()[id(definition_raw)] = (definition_raw, original["definition"]["sha256"])
        require(expected_definition is None or checksum(definition_raw) == expected_definition, "Selected raster changed; reload")
        target_row = next(r for r in target_runtime["entries"] if r["id"] == identifier)
        if request["text"] is not None:
            matrix = raster.parse(request["text"], definition["palette"])
            new_definition = raster.definition(definition, matrix)
            before["definition"] = definition
            if new_definition != definition:
                require(work is not None, "Raster preparation requires a private workspace")
                work = io.external(work)
                require(not work.is_relative_to(inputs.root), "Raster workspace must be outside checkout")
                quality, package = _prepare_raster(inputs, entry, definition_raw, new_definition, request["profile"], Path(work))
                definition_raw = encoded(new_definition)
                put("game/"+entry["definition"], definition_raw)
                active = rating.active_record(quality["checked"])
                proposed["difficulty"] = puzzle_catalog.difficulty_fields(active)
                proposed["difficulty"]["rating_revision"] = original["difficulty"]["rating_revision"] + 1
                proposed["definition"] = ref("game/"+entry["definition"],definition_raw)
                target_row["difficulty"] = rating.project(active)
            definition = new_definition
        for kind in ("reveal", "background"):
            part = request[kind]
            # Only a real raster change needs both current bindings rebound.
            if part is None and quality is None: continue
            previous = original[kind]
            current = None
            catalog = puzzle_record.catalog(original) if kind == "reveal" else None
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
                        require(ref(old_name, old) == previous["asset"], "Previous reveal bytes differ")
                        catalog, profiles = current_content.catalog_profiles.generate(identifier, ref(name, raw), raw)
                        for profile in previous["catalog"]["profiles"]:
                            asset = profile["asset"]
                            require(ref(asset["file"], inputs.read(asset["file"])) == asset, "Previous catalog bytes differ")
                            put(asset["file"], profiles[asset["file"]])
                        target_row["catalog_reveal"] = current_content.catalog_profiles.project(catalog)
                        if name != old_name:
                            require(inputs.read(name, 32*1024*1024, missing=True) is None, "New original path is occupied")
                            put(old_name, None)
                        put(name, raw)
                        old_revision = (previous["image_revision"] if previous else 0)
                        current = {"image_revision": old_revision+1, "asset": ref(name, raw)}
                        target_row["reveal"] = name.removeprefix("game/")
                if current is None and quality is not None:
                    current = {k:v for k,v in previous.items() if k != "catalog"}
            else:
                old_current = row["background"]
                if part is not None:
                    exact_keys(part, {"status", "upload", "rights"} if "rights" in part else {"status", "upload"})
                    if "rights" in part:
                        from .reveal_source import provenance, make_notice
                        require(part["status"] == "selected" and part["upload"] is not None, "New background rights need selected image")
                        provenance(part["rights"])
                        notice=("\n".join(k+": "+part["rights"][k] for k in sorted(part["rights"]))+"\n").encode("utf8")
                        make_notice(notice)
                        put("game/art/backgrounds/"+identifier+".txt",notice)
                    require(part["status"] in ("standard", "selected", "none"), "Invalid background preference")
                    raw = uploads[part["upload"]]["raw"] if part["upload"] else None
                    if raw is not None:
                        from .editor_image_input import PROFILES
                        checked = uploads[part["upload"]]["checked"]
                        require(checked["profile"] in PROFILES.values() and checked["sha256"] == checksum(raw), "Prepared background binding differs")
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
                            bg.capability(inputs.root, {bg.CAPABILITY: encoded(capability) if capability else None}, required=True,
                                          profile_id=bg.image_profile(raw) if raw is not None else None)
                        if raw is not None: put(bg.asset_path(identifier), raw)
                        elif old_current["status"] == "selected": put(bg.asset_path(identifier), None)
                        current = {"image_revision": (old_current["image_revision"] or 0)+1, "status": part["status"], "asset": asset}
                        target_row["background"] = deepcopy(current)
                        if asset: target_row["background"]["asset"]["file"] = asset["file"].removeprefix("game/")
                if current is None and quality is not None and previous is not None:
                    current = deepcopy(row["background"])
                    if current["asset"]: current["asset"]["file"] = "game/"+current["asset"]["file"]
            if current is not None:
                proposed[kind] = current
                if kind == "reveal":
                    proposed[kind]["catalog"] = {k:v for k,v in catalog.items() if k != "source_sha256"}
    if proposed != original:
        put(puzzle_record.path(identifier),puzzle_record.encode(proposed))
    for name,old,new in ((categories.PATH,cats,target_cats),(registry.RUNTIME,runtime,target_runtime)):
        if old != new: put(name,encoded(new))
    after = _summary(proposed,next((r for r in target_runtime["entries"] if r["id"] == identifier),None))
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
    work.mkdir(parents=True, exist_ok=True)
    directory = work/"raster"; directory.mkdir()
    raw = encoded(definition)
    files = {"definition.json": raw, "previous-definition.json": previous}
    for name, data in files.items(): (directory/name).write_bytes(data)
    puzzle = parsed_definition(raw)[1]
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
        production_mode=entry["mode"], method=method,
        proof=directory/"proof.json" if baseline is not None else None,
        baseline=directory/"baseline.json" if baseline is not None else None)
    quality = {"method": method, "checked": checked, "proof": ref("proof.json", files["proof.json"]),
               "baseline": ref("baseline.json", files["baseline.json"]) if baseline is not None else None}
    # Traversal is confined to this operation's newly generated proof output.
    for path in (directory/"analysis").rglob("*"):
        if path.is_file(): files[path.relative_to(directory).as_posix()] = path.read_bytes()
    quality.update(proof_data=proof, baseline_data=baseline)
    return quality, files


def validate(value, *, journal=False):
    keys = {"format", "action", "id", "entry", "reads", "changes", "quality"}
    exact_keys(value, keys if journal else keys | {"before", "after", "plan_hash"})
    require(value["format"] == (JOURNAL if journal else PLAN), "Unsupported change format")
    require(value["action"] in ("metadata", "images", "raster"), "Invalid editor action")
    if not journal:
        require(value["plan_hash"] == digest({k: v for k, v in value.items() if k != "plan_hash"}), "Plan changed")
    allowed = set(INDEXES)
    entry, identifier = value["entry"], value["id"]
    if identifier is not None:
        current_content.entries([entry])
        require(entry["id"] == identifier, "Selected identity differs")
    else: require(entry is None, "Unselected entry")
    if value["action"] in ("images", "raster"):
        require(entry is not None, "Puzzle action requires ID")
        allowed |= {"game/"+entry["definition"], puzzle_record.path(identifier), bg.asset_path(identifier), "game/art/backgrounds/"+identifier+".txt", bg.CAPABILITY}
        allowed.update(current_content.catalog_profiles.path(identifier, label) for label, _, _ in current_content.catalog_profiles.PROFILES)
        allowed |= {Path("game/"+entry["reveal"]).with_suffix(s).as_posix() for s in (".png", ".svg")}
    if value["action"] == "raster":
        from .catalog_method import PATH
        allowed.add(PATH)
    require(isinstance(value["reads"], dict) and isinstance(value["changes"], dict), "Invalid read/write set")
    require(set(INDEXES) <= set(value["reads"]), "Missing index conflict bindings")
    if identifier is not None:
        require({puzzle_record.path(identifier),"game/"+entry["definition"]} <= value["reads"].keys(),
                "Selected plan entry lacks bound record or definition")
    for name, expected_hash in value["reads"].items():
        relative(name)
        if re.fullmatch(r"content/puzzles/pz-[a-z0-9][a-z0-9-]{0,59}\.json",name):
            require(identifier is None or name == puzzle_record.path(identifier),"Foreign selected record")
            allowed.add(name)
        if re.fullmatch(r"game/data/content/[a-z][a-z0-9_-]{0,63}\.json",name):
            allowed.add(name)
        require(name in allowed, "Unrelated editor input: "+name)
        if expected_hash is not None: sha(expected_hash)
    sides = {}
    for name, pair in value["changes"].items():
        require(name in value["reads"], "Unbound change target")
        exact_keys(pair, {"old", "new"})
        old, new = unpack(pair["old"]), unpack(pair["new"])
        require(old != new and checksum(old) == value["reads"][name], "Invalid old target binding")
        require(name not in (bg.CAPABILITY, "content/difficulty-method.json"), "Read-only input cannot be edited")
        if name.startswith("game/data/content/"):
            require(value["action"] == "raster" and name == "game/"+entry["definition"], "Invalid definition write")
        sides[name] = (old, new)
    require(len(encoded(value)) <= LIMIT, "Oversized editor transaction")
    return sides


@catalog_method.bound_validation
def validate_targets(root, value, sides, actual):
    """Closed technical deltas, using already read bytes; no plan rebuilding."""
    target = {**actual, **{name: pair[1] for name, pair in sides.items()}}
    old_runtime,runtime = (io.json_bytes(data[registry.RUNTIME],current_content.RUNTIME_LIMIT) for data in (actual,target))
    ids = puzzle_record.inventory(root)
    old_cats,cats = (categories.validate(io.json_bytes(data[categories.PATH],categories.MAX_BYTES)) for data in (actual,target))
    puzzle_catalog.validate_runtime(old_runtime,old_cats,ids)
    puzzle_catalog.validate_runtime(runtime,cats,ids)
    identifier,action = value["id"],value["action"]
    if action != "metadata":
        require(identifier in ids and old_cats == cats, "Invalid puzzle edit")
    record_names = {n for n in actual if n.startswith(puzzle_record.DIRECTORY+"/")}
    require(record_names <= {puzzle_record.path(k) for k in ids},"Foreign record read")
    for old_row,row in zip(old_runtime["entries"],runtime["entries"],strict=True):
        key = row["id"]
        name = puzzle_record.path(key)
        if name not in record_names:
            require(row == old_row, "Unbound runtime change")
            continue
        old,record = (puzzle_record.decode(data[name],key) for data in (actual,target))
        definition_path = old["definition"]["file"]
        definition_raw = target[definition_path]
        puzzle_record.validate(old,key,actual[definition_path],category_catalog=old_cats)
        puzzle_record.validate(record,key,definition_raw,category_catalog=cats)
        require(puzzle_record.runtime_row(old) == old_row and puzzle_record.runtime_row(record) == row,
                "Editor projection differs")
        fields = {"name","category_id"}
        if key == identifier:
            require(puzzle_record.entry(old) == value["entry"],"Foreign selected entry")
            if action in ("images","raster"):
                fields |= {"reveal","background"}
            if action == "raster":
                fields |= {"definition","difficulty"}
        require(all(old[k] == record[k] for k in record.keys()-fields), "Unrelated record change")
        if action == "metadata" or key != identifier:
            continue
        require(old["definition"]["file"] == record["definition"]["file"], "Definition path changed")
        require((old["difficulty"] != record["difficulty"]) == (definition_path in sides),"Unbound rating change")
        if definition_path in sides:
            require(record["difficulty"]["rating_revision"] == old["difficulty"]["rating_revision"]+1,"Invalid rating revision")
        bound = {}
        for kind in ("reveal","background"):
            prior,following = old[kind],record[kind]
            changed = any(prior[k] != following[k] for k in prior if k not in ("image_revision","catalog"))
            require(following["image_revision"] == prior["image_revision"] + int(changed),"Invalid image revision")
            a,b = prior["asset"],following["asset"]
            if a != b:
                if a and (not b or a["file"] != b["file"]):
                    require(a["file"] in sides and sides[a["file"]][1] is None,"Previous image not removed")
                    bound[a["file"]] = None
                if b:
                    require(b["file"] in sides and ref(b["file"],sides[b["file"]][1]) == b,"Image bytes differ")
                    require(a and a["file"] == b["file"] or sides[b["file"]][0] is None,"Occupied image destination")
                    bound[b["file"]] = b
            if kind == "reveal":
                require(changed or following["catalog"] == prior["catalog"], "Unexpected catalog profile change")
                if changed:
                    require(Path(a["file"]).with_suffix("") == Path(b["file"]).with_suffix(""),"Reveal stem changed")
                    for previous,current in zip(prior["catalog"]["profiles"],following["catalog"]["profiles"],strict=True):
                        asset = current["asset"]
                        n = asset["file"]
                        require(n in actual and ref(n,actual[n]) == previous["asset"],"Changed old profile")
                        current_content.catalog_profiles.validate_png(current,target[n])
                        bound[n] = asset
        notice = bg.notice_path(key)
        if notice in sides:
            from .reveal_source import make_notice
            require(record["background"]["status"] == "selected" and target[notice] is not None,"Invalid rights change")
            make_notice(target[notice])
            bound[notice] = None
        require(all(n in bound for n in sides if n.startswith("game/art/")), "Unbound asset change")
        if definition_path in sides:
            old_def, new_def = (io.json_bytes(raw, 2*1024*1024) for raw in sides[definition_path])
            require(new_def == raster.definition(old_def, new_def["solution"]) and new_def["revision"] == old_def["revision"]+1, "Invalid raster delta")
            from .verifier import verify
            from .contract import Budget
            evidence = value["quality"]
            require(isinstance(evidence, dict), "Raster proof missing")
            proof = evidence["proof_data"]
            checked = verify(parsed_definition(definition_raw)[1], proof, Budget())
            require(checked["certified"], "Raster proof incomplete")
            raster.check_end(new_def, proof)
            active = rating.active_record(evidence["checked"])
            expected = puzzle_catalog.difficulty_fields(active)
            expected["rating_revision"] = record["difficulty"]["rating_revision"]
            require(expected == record["difficulty"], "New assessment differs from approved raster")
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
        validate_targets(root,value,sides,actual)
        require(not pending(root), "Publication started during no-op readback")
        return {"status": "noop", "files": [], **readback(actual, value["id"])}
    journal = {k: deepcopy(value[k]) for k in ("action", "id", "entry", "reads", "changes", "quality")}
    journal["format"] = JOURNAL
    raw = publication.journal_bytes(journal)
    journal_hash = checksum(raw)
    checkpoint("before-journal")
    def rollback():
        with io.budget():
            recover(root)
    with publication.owned_journal(root,STAGE,LOCK,raw,rollback):
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
            validate_targets(root, value, sides, actual)
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
    validate_targets(root, journal, sides, old_inputs)
    for temporary, temp in temps.items():
        require(io.read(root, temporary, FILE_LIMIT) == temp, "Recovery temporary changed")
        io.safe(root, temporary).unlink(); publication.sync_directory(io.safe(root, temporary).parent)
    for target in sorted(sides, key=lambda n: (n == registry.RUNTIME, n)):
        if actual[target] != sides[target][0]: _write(root, target, actual[target], sides[target][0], journal_hash)
    require(io.read(root, name, LIMIT) == raw, "Recovery journal changed")
    io.safe(root, name).unlink(); publication.sync_directory(root/"content")
    return {"status": "rolled-back", "registered": False}
