"""PE-A3 planning and explicit apply through the shared catalog transaction."""
from copy import deepcopy
from pathlib import Path
import tempfile

from .authoring_package import require
from .contract import canonical_bytes, digest, exact_keys, Budget, load_json
from . import catalog_io as io, catalog_transaction as tx, catalog_images as images
from . import editor_raster as raster, editor_image_source as source, editor_image_input as inputs
from . import catalog_background as bg, reveal_source as reveal, categories, content_registry as registry
from . import catalog_rating as rating, catalog_method, catalog_analysis as analysis

PLAN = "picross-editor-raster-plan-v1"
LIMIT = 32*1024*1024
encoded = raster.encoded


def _definition(snapshot, identifier):
    entry = next((e for e in snapshot["registry"]["entries"] if e["id"] == identifier), None)
    require(entry is not None, "Unknown puzzle ID")
    raw = snapshot["texts"]["game/"+entry["definition"]]
    return entry, raw, rating.definition(raw)[0]


def _summary(texts, identifier):
    result = images._summary(texts, identifier)
    raw = texts["game/"+result["entry"]["definition"]]
    if isinstance(raw,str): raw = raw.encode()
    return {**result,"definition":rating.definition(raw)[0]}


def _hash(value):
    value["plan_hash"] = digest(value)
    require(len(encoded(value)) <= LIMIT, "Raster plan exceeds 32 MiB")
    return value


def _require_target(snapshot):
    registry.require_current(snapshot["registry"])
    require(tx.image_generation(snapshot), "Explicit migration required: run images_cli plan-migration/apply-migration for v7 first")


def _make_package(root, snapshot, request, request_raw, value, directory):
    from .solver import solve
    from .verifier import verify
    entry, previous_raw, previous = _definition(snapshot,request["id"])
    directory.mkdir()
    raw = encoded(value)
    (directory/"definition.json").write_bytes(raw)
    (directory/"previous-definition.json").write_bytes(previous_raw)
    (directory/"request.json").write_bytes(request_raw)
    puzzle = rating.definition(raw)[1]
    baseline = None
    if request["profile"] == "paired":
        baseline = solve(puzzle,Budget())
        (directory/"baseline.json").write_bytes(encoded(baseline))
        verify(puzzle,load_json(directory/"baseline.json",puzzle.proof_byte_limit),Budget())
    proof = solve(puzzle,Budget(),profile="paired-lines-color" if baseline is not None else None)
    (directory/"proof.json").write_bytes(encoded(proof))
    checked = verify(puzzle,load_json(directory/"proof.json",puzzle.proof_byte_limit),Budget())
    require(checked["certified"] and proof["status"] == "solved", "Raster deduction blocked: "+proof["status"])
    raster.check_end(value,proof)
    method = catalog_method.current(catalog_method.from_bytes(snapshot["texts"][catalog_method.PATH]))["method"]
    checked_rating = analysis.analyze_single(directory/"definition.json",directory/"analysis",
        production_mode=entry["production"]["mode"],method=method,
        proof=directory/"proof.json" if baseline is not None else None,
        baseline=directory/"baseline.json" if baseline is not None else None)
    q = {"method":method,"checked":checked_rating,"proof":bg.ref("proof.json",encoded(proof)),
         "baseline":bg.ref("baseline.json",encoded(baseline)) if baseline is not None else None}
    raster.quality(q,raw)
    _, historical_notice, _, _ = reveal.package(root,entry)
    previous_manifest = io.json_bytes(io.read(root,entry["production"]["package"]+"/manifest.json",8*1024*1024),8*1024*1024)
    anchor = {"entry":deepcopy(entry),"identity":raster.identity(entry,previous_raw)}
    active_reveal = reveal.load(root,entry,io.json_bytes(snapshot["texts"][categories.PATH],categories.MAX_BYTES))
    image_hash = (active_reveal["revisions"][-1]["reveal_sha256"] if active_reveal and not source.is_editor(active_reveal)
                  else entry["production"]["reveal_sha256"])
    manifest = {"format":raster.PACKAGE,"id":entry["id"],"revision":"editor-"+str(value["revision"]),
        "previous":anchor,"origin":previous_manifest["origin"] if previous_manifest.get("format") == raster.PACKAGE else anchor,
        "definition":bg.ref("definition.json",raw),"reveal_sha256":image_hash,"notice_sha256":historical_notice,"quality":q,
        "decision":request["decision"],"provenance":request["provenance"],
        "files":{name:io.file_hash(directory,name,64*1024*1024) for name in raster.inventory(directory)}}
    manifest["package_hash"] = digest(manifest)
    (directory/"manifest.json").write_bytes(encoded(manifest))
    raster.verify(directory,replay=True)
    return manifest


def _construct(root, snapshot, request, request_raw, input_root, package_directory=None):
    _require_target(snapshot)
    raster.request(request)
    identifier = request["id"]
    entry, previous_raw, previous = _definition(snapshot,identifier)
    value = raster.definition(previous,raster.parse(request["text"],previous["palette"]))
    changed_logic = value["revision"] != previous["revision"]
    # A2 is only planned here. Its bytes enter the one final raster journal.
    if any(request[key] is not None for key in ("metadata","reveal","background")):
        image_request = {"format":images.REQUEST,**{key:request[key] for key in ("id","metadata","reveal","background","decision")}}
        _, image_journal, bundle_files = images._construct(root,snapshot,image_request,encoded(image_request),input_root)
        bundle_files.pop("request.json")
    else:
        image_journal = tx.prepare(root,snapshot,{},operation="editor-images",generation="images")
        bundle_files = {}
    changes = {name: raw.encode() if raw is not None else None for name,raw in image_journal["new"].items()
               if raw != image_journal["old"][name] and name != tx.RUNTIME}
    replacements = image_journal["replacements"]
    additions = {}
    manifest = None
    if changed_logic:
        require(package_directory is not None,"Missing checked raster package")
        manifest = raster.verify(package_directory,replay=True)
        require(manifest["previous"] == {"entry":entry,"identity":raster.identity(entry,previous_raw)} and
                io.read(package_directory,"definition.json",2*1024*1024) == encoded(value) and
                io.read(package_directory,"request.json",raster.REQUEST_LIMIT) == request_raw,"Raster package is stale or belongs to another request")
        require(manifest["quality"]["method"] == catalog_method.current(catalog_method.from_bytes(snapshot["texts"][catalog_method.PATH]))["method"],"Raster rating method is stale")
        after = io.json_bytes(changes.get(tx.REGISTRY,snapshot["texts"][tx.REGISTRY]),8*1024*1024)
        fresh = deepcopy(entry)
        prefix = "content/packages/"+identifier+"/"+manifest["revision"]
        require(not io.safe(root,prefix).exists(),"Raster package target already exists")
        fresh["production"].update(package=prefix,package_sha256=io.file_hash(package_directory,"manifest.json"),
            revision=manifest["revision"],definition_sha256=io.checksum(encoded(value)),reveal_sha256=manifest["reveal_sha256"],width=value["width"],height=value["height"])
        after["entries"][after["entries"].index(entry)] = fresh
        name = "game/"+entry["definition"]
        changes[name] = encoded(value)
        prior_raw = snapshot["texts"][rating.path(identifier)]
        prior = rating.validate(io.json_bytes(prior_raw,rating.LIMIT)) if prior_raw is not None else None
        changes[rating.path(identifier)] = rating.encoded(rating.active_record(manifest["quality"]["checked"],prior))
        catalog = io.json_bytes(snapshot["texts"][categories.PATH],categories.MAX_BYTES)
        for kind,path in (("reveal",reveal.path(identifier)),("background",bg.path(identifier))):
            active = images._source({**snapshot["texts"],**changes},path)
            if active is None: continue
            if source.is_editor(active):
                rebound = source.rebind(active,fresh,bg.ref(name,encoded(value)),value["revision"],catalog)
            elif kind == "reveal":
                rebound = reveal.rebind(active,fresh,value["revision"],active["bindings"][-1]["notice"]["text"].encode(),catalog,historical_categories=True)
            else:
                rebound = source.promote_background(root,snapshot["registry"],entry,fresh,bg.ref(name,encoded(value)),value["revision"],manual_raster=True)
            changes[path] = encoded(rebound)
            if kind == "background":
                for row in after["backgrounds"]:
                    if row["id"] == identifier: row["source"] = bg.ref(path,changes[path])
        changes[tx.REGISTRY] = encoded(after)
        additions = {prefix+"/"+name:path for name,path in raster.inventory(package_directory).items()}
    # Check the actual final reveal against the new dimensions, even without import.
    active_name = tx.active_reveal(entry,{**snapshot["texts"],**changes})
    if active_name in replacements:
        from .catalog_publication import decode_binary
        active_raw = decode_binary(replacements[active_name]["new"])
    else: active_raw = io.read(root,active_name,reveal.IMAGE_LIMIT)
    from .target_adapter import validate_reveal
    with tempfile.TemporaryDirectory(prefix="pe-raster-reveal-") as directory:
        path = Path(directory)/("image"+Path(active_name).suffix)
        path.write_bytes(active_raw)
        validate_reveal(path,value["width"],value["height"])
    journal = tx.prepare(root,snapshot,changes,operation="editor-raster",additions=additions,replacements=replacements,generation="images")
    before_bytes = 0
    for name, text in journal["old"].items():
        if text is not None and text != journal["new"][name]:
            raw = text.encode()
            before_bytes += len(raw)
            bundle_files["before/"+io.checksum(raw)+".txt"] = raw
    require(before_bytes <= tx.LIMIT,"Raster before-text bundle exceeds 24 MiB")
    files = sorted({name for name in journal["old"] if journal["old"][name] != journal["new"][name]} | set(replacements) | set(additions))
    plan = _hash({"format":PLAN,"request":bg.ref("request.json",request_raw),"snapshot":tx.image_snapshot(snapshot),
        "old":_summary(journal["old"],identifier),"new":_summary(journal["new"],identifier),
        "quality":manifest["quality"] if manifest else None,"files":files})
    return plan,journal,bundle_files,additions


def plan(root, request_path, output, *, seconds=300):
    with io.budget(seconds):
        root = io.external(root)
        request_path, output = images._outside(request_path,root),images._outside(output,root)
        require(not output.exists(),"Raster plan output must be new")
        require(not output.is_relative_to(request_path.parent) and not request_path.parent.is_relative_to(output),"Raster input and bundle overlap")
        raw = io.read(request_path.parent,request_path.name,raster.REQUEST_LIMIT)
        request = raster.request(io.json_bytes(raw,raster.REQUEST_LIMIT))
        snapshot = tx.capture(root)
        _require_target(snapshot)
        _, _, old = _definition(snapshot,request["id"])
        value = raster.definition(old,raster.parse(request["text"],old["palette"]))
        with tempfile.TemporaryDirectory(prefix="pe-raster-plan-") as temporary:
            package = Path(temporary)/"package"
            if value["revision"] != old["revision"]: _make_package(root,snapshot,request,raw,value,package)
            result,journal,files,additions = _construct(root,snapshot,request,raw,request_path.parent,package if package.exists() else None)
            require(tx.image_snapshot(tx.capture(root)) == result["snapshot"],"Checkout changed during raster planning")
            require(io.read(request_path.parent,request_path.name,raster.REQUEST_LIMIT) == raw,"Raster request changed during planning")
            files.update({"package/"+path.relative_to(package).as_posix():io.read(path.parent,path.name,64*1024*1024) for path in additions.values()})
            files.update({"request.json":raw,"plan.json":encoded(result)})
            images._write_bundle(output,files)
        return result


def apply(root, bundle, *, fail_step=None, seconds=300):
    with io.budget(seconds):
        root, bundle = io.external(root),io.external(bundle)
        images._outside(bundle,root)
        value = io.json_bytes(io.read(bundle,"plan.json",LIMIT),LIMIT)
        exact_keys(value,{"format","request","snapshot","old","new","quality","files","plan_hash"})
        require(value["format"] == PLAN and value["plan_hash"] == digest({k:v for k,v in value.items() if k != "plan_hash"}),"Invalid raster plan/hash")
        raw = io.read(bundle,"request.json",raster.REQUEST_LIMIT)
        require(bg.ref("request.json",raw) == value["request"],"Raster request changed")
        request = raster.request(io.json_bytes(raw,raster.REQUEST_LIMIT))
        snapshot = tx.capture(root)
        if tx.image_snapshot(snapshot) != value["snapshot"]:
            return _repeat(root,snapshot,value,request,raw,bundle)
        fresh,journal,files,additions = _construct(root,snapshot,request,raw,bundle/"input",bundle/"package" if value["quality"] is not None else None)
        require(fresh == value,"Raster plan preview differs from fresh reconstruction")
        expected = {"plan.json","request.json"} | set(files)
        expected |= {"package/"+path.relative_to(bundle/"package").as_posix() for path in additions.values()}
        actual = {path.relative_to(bundle).as_posix() for path in bundle.rglob("*") if io.safe(bundle,path.relative_to(bundle).as_posix()).is_file()}
        require(actual == expected,"Raster bundle has foreign/missing files")
        bound = {name:io.checksum(raw) for name,raw in files.items()}
        bound.update({"request.json":io.checksum(raw),"plan.json":io.checksum(encoded(value))})
        bound.update({"package/"+path.relative_to(bundle/"package").as_posix():journal["additions"][name] for name,path in additions.items()})
        _bundle_guard(bundle,bound)
        if value["files"]:
            tx.execute(root,journal,additions,fail_step=fail_step,source_check=lambda:_bundle_guard(bundle,bound))
        else:
            require(tx.image_snapshot(tx.capture(root)) == value["snapshot"],"Checkout changed during raster no-op verification")
        return {"status":"applied" if value["files"] else "noop","files":value["files"],"plan_hash":value["plan_hash"]}


def _repeat(root, snapshot, value, request, request_raw, bundle):
    """Reconstruct and validate the full original view; accept only this exact delta."""
    identifier = request["id"]
    require(_summary(snapshot["texts"],identifier) == value["new"],"Raster plan is stale; create a new plan")
    current = tx.image_snapshot(snapshot)
    exact_keys(value["snapshot"],{"sources","namespaces"})
    require(isinstance(value["snapshot"]["sources"],dict) and set(value["snapshot"]["sources"]) <= set(current["sources"]),"Repeated raster source set differs")
    with tempfile.TemporaryDirectory(prefix="pe-raster-repeat-") as directory:
        old_root = Path(directory)
        for name, checksum in value["snapshot"]["sources"].items():
            if checksum is None: continue
            if current["sources"].get(name) == checksum:
                raw = tx.read(root,name)
            else:
                require(name in value["files"],"Unrelated source changed since raster apply")
                backup = "before/"+checksum+".txt" if name in snapshot["texts"] else "previous/"+checksum+".bin"
                raw = io.read(bundle,backup,tx.LIMIT if name in snapshot["texts"] else reveal.IMAGE_LIMIT)
            require(io.checksum(raw) == checksum,"Repeated raster original bytes differ")
            path = io.safe(old_root,name)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)
        original = tx.capture(old_root)
        require(tx.image_snapshot(original) == value["snapshot"],"Repeated raster original namespace differs")
        fresh,journal,files,additions = _construct(old_root,original,request,request_raw,bundle/"input",bundle/"package" if value["quality"] else None)
        require(fresh == value,"Repeated raster plan differs from original reconstruction")
        expected = {name:io.checksum(text.encode() if text is not None else None) for name,text in journal["new"].items()}
        expected.update(journal["retained"])
        expected.update(journal["additions"])
        from .catalog_publication import binary_hash
        expected.update({name:binary_hash(pair["new"]) for name,pair in journal["replacements"].items()})
        for name in tx.image_candidates(snapshot["registry"]): expected.setdefault(name,None)
        require(current["sources"] == expected,"Repeated raster current sources differ from exact applied result")
        expected_files = {"request.json","plan.json"} | set(files) | {"package/"+path.relative_to(bundle/"package").as_posix() for path in additions.values()}
        bound = {name:io.checksum(content) for name,content in files.items()}
        bound.update({"request.json":io.checksum(request_raw),"plan.json":io.checksum(encoded(value))})
        bound.update({"package/"+path.relative_to(bundle/"package").as_posix():journal["additions"][name] for name,path in additions.items()})
        require(set(bound) == expected_files,"Repeated raster bundle file set differs")
        _bundle_guard(bundle,bound)
        require(tx.image_snapshot(tx.capture(root)) == current,"Checkout changed during repeated raster verification")
    return {"status":"noop","files":[],"plan_hash":value["plan_hash"]}


def _bundle_guard(bundle, expected):
    actual = raster.inventory(bundle)
    require(set(actual) == set(expected),"Raster bundle changed: foreign/missing files")
    for name,checksum in expected.items():
        require(io.file_hash(bundle,name,64*1024*1024) == checksum,"Raster bundle changed: "+name)


def view(root, identifier):
    with io.budget():
        snapshot = tx.capture(io.external(root))
        _, _, value = _definition(snapshot,identifier)
        return {"format":"picross-editor-raster-view-v1","id":identifier,"revision":value["revision"],
                "palette":value["palette"],"text":"\n".join(" ".join(map(str,row)) for row in value["solution"])+"\n",
                "migration_required":not tx.image_generation(snapshot)}


def validate_delta(journal, before, after, root):
    """Derive fixed one-ID boundaries; independently validated target supplies proof bindings."""
    require(journal["format"] == tx.RASTER_FORMAT and before["format"] == after["format"] == registry.METADATA_FORMAT and
            journal["report_run"] is None,"Invalid raster journal generation")
    pairs = [(a,b) for a,b in zip(before["entries"],after["entries"]) if a != b]
    require(len(before["entries"]) == len(after["entries"]) and len(pairs) <= 1,"Raster journal changes multiple IDs")
    if not pairs:
        delegated = {**journal,"format":tx.IMAGE_FORMATS["editor-images"],"operation":"editor-images"}
        return images.validate_delta(delegated,before,after,root)
    old,new = pairs[0]
    identifier = old["id"]
    require(all(old[k] == new[k] for k in ("id","key","save_slot","definition","reveal","category_id","visible")),"Raster journal changes fixed identity")
    name = "game/"+old["definition"]
    a,b = (rating.definition(journal[side][name].encode())[0] for side in ("old","new"))
    require(b["revision"] == a["revision"]+1 and b["palette"] == a["palette"] and b["reveal"] == a["reveal"] and
            (a["width"],a["height"],a["solution"]) != (b["width"],b["height"],b["solution"]),"Invalid raster logic/revision/palette delta")
    prefix = "content/packages/"+identifier+"/editor-"+str(b["revision"])
    require(new["production"]["package"] == prefix and journal["additions"].get(prefix+"/manifest.json") == new["production"]["package_sha256"] and
            all(path.startswith(prefix+"/") for path in journal["additions"]),"Raster journal package additions differ")
    mutable = {tx.REGISTRY,tx.RUNTIME,name,rating.path(identifier),reveal.path(identifier),reveal.identity(old)["notice"],bg.path(identifier),bg.notice_path(identifier)}
    changed = {path for path in journal["old"] if journal["old"][path] != journal["new"][path]}
    require(changed <= mutable and set(journal["replacements"]) <= tx.image_candidates({"entries":[old]}),"Raster journal mutates unrelated sources")
    _source_delta(journal,before,after,old,new,a,b,root)
    require([row for row in before["metadata"] if row["id"] != identifier] == [row for row in after["metadata"] if row["id"] != identifier] and
            [row for row in before["backgrounds"] if row["id"] != identifier] == [row for row in after["backgrounds"] if row["id"] != identifier],"Raster journal changes another ID")
    prior_raw,current_raw = (journal[side][rating.path(identifier)] for side in ("old","new"))
    require(current_raw is not None,"New raster lacks current rating")
    current = rating.validate(io.json_bytes(current_raw.encode(),rating.LIMIT),definition_bytes=encoded(b),production_mode=new["production"]["mode"])
    prior = rating.validate(io.json_bytes(prior_raw.encode(),rating.LIMIT)) if prior_raw is not None else None
    require(current["rating_revision"] == (prior["rating_revision"]+1 if prior else 1) and
            current["adoption"]["previous_record_hash"] == (prior["record_hash"] if prior else None) and
            rating.method(current) == catalog_method.current(catalog_method.from_bytes(journal["old"][catalog_method.PATH].encode() if journal["old"][catalog_method.PATH] is not None else None))["method"],"Raster rating revision/method differs")
    return prefix


def _source_delta(journal, before, after, old, new, old_definition, new_definition, root):
    """Preserved images rebind only; actual image choices retain the full A2 transition."""
    identifier = old["id"]
    definition_name = "game/"+old["definition"]
    definition_ref = bg.ref(definition_name,journal["new"][definition_name].encode())
    catalog = io.json_bytes(journal["old"][categories.PATH].encode(),categories.MAX_BYTES)
    normalized = reveal.package(root,old,historical=True)[0]
    old_binding = {"entry":normalized,"identity":raster.identity(old,journal["old"][definition_name].encode())}
    old_reveal = images._source(journal["old"],reveal.path(identifier))
    expected_hash = old_reveal["revisions"][-1]["reveal_sha256"] if old_reveal and not source.is_editor(old_reveal) else old["production"]["reveal_sha256"]
    require(new["production"]["reveal_sha256"] == expected_hash,"Raster changes historical image without existing authority")
    for kind,path,notice_name in (("reveal",reveal.path(identifier),reveal.identity(old)["notice"]),
                                  ("background",bg.path(identifier),bg.notice_path(identifier))):
        previous,following = (images._source(journal[side],path) for side in ("old","new"))
        require(previous is None or following is not None,"Raster removes active image authority")
        old_notice = journal["old"][notice_name]
        if following is None:
            require(old_notice == journal["new"][notice_name],"Raster changes undeclared notice")
            continue
        if source.is_editor(previous) and following["current"] == previous["current"]:
            expected = source.rebind(previous,new,definition_ref,new_definition["revision"],catalog)
            require(following == expected and old_notice == journal["new"][notice_name],"Raster changes preserved manual image")
        elif not source.is_editor(previous) and kind == "reveal" and not source.is_editor(following):
            require(previous is not None,"Raster invents legacy reveal source")
            expected = reveal.rebind(previous,new,new_definition["revision"],previous["bindings"][-1]["notice"]["text"].encode(),catalog,historical_categories=True)
            require(following == expected and old_notice == journal["new"][notice_name],"Raster changes preserved reveal history")
        elif kind == "background" and previous is not None and not source.is_editor(previous) and source.is_editor(following) and source.preserved_background(following):
            active = bg.current(previous)
            notice = reveal.make_notice(old_notice.encode()) if old_notice is not None else None
            expected = source._new_source(source.BACKGROUND_FORMAT,old,old_binding,previous,notice)
            expected["binding"] = {"entry":deepcopy(new),"identity":raster.identity(new,journal["new"][definition_name].encode())}
            expected["current"] = {key:deepcopy(active[key]) for key in ("image_revision","asset","notice")}
            expected["current"]["status"] = active["decision"]["outcome"]
            expected["current"]["authority"] = {"kind":"production",**{key:deepcopy(active[key]) for key in ("candidate_revision","decision","derivation","provenance","review")},"adoption":deepcopy(active.get("adoption"))}
            require(following == source._hashed(expected,catalog) and old_notice == journal["new"][notice_name],"Raster changes productive background promotion")
        else:
            require(source.is_editor(following),"Raster image change lacks A2 source")
            intermediate = deepcopy(following)
            intermediate["binding"] = deepcopy(old_binding)
            intermediate["record_revision"] -= 1
            intermediate = source._hashed(intermediate,catalog)
            images._manual_transition(kind,old,previous,intermediate,old_binding["identity"]["definition"],io.checksum(old_notice.encode() if old_notice is not None else None))
            expected = source.rebind(intermediate,new,definition_ref,new_definition["revision"],catalog)
            require(following == expected,"Raster manual image rebind differs")
            authority = following["current"]["authority"]
            notice = source.manual_notice(old_notice or b"",authority["provenance"],authority["decision"]) if following["current"]["asset"] is not None else None
            require(journal["new"][notice_name] == (notice.decode() if notice is not None else None),"Raster manual notice differs")
    expected_index = [{"id":entry["id"],"source":bg.ref(bg.path(entry["id"]),journal["new"][bg.path(entry["id"])].encode())}
                      for entry in after["entries"] if journal["new"].get(bg.path(entry["id"])) is not None]
    require(after["backgrounds"] == expected_index,"Raster background index differs")
    # Derive every changed image from the actual active sources on both sides.
    expected_pairs = {}
    for side in ("old","new"):
        texts = journal[side]
        active_name = tx.active_reveal(old,texts)
        record = images._source(texts,reveal.path(identifier))
        if source.is_editor(record): asset = record["current"]["asset"]
        else:
            pair = journal["replacements"].get(active_name)
            from .catalog_publication import decode_binary
            raw = decode_binary(pair[side]) if pair is not None and pair[side] is not None else io.read(root,active_name,reveal.IMAGE_LIMIT)
            asset = bg.ref(active_name,raw)
        refs = [asset]
        background = images._source(texts,bg.path(identifier))
        if background is not None and bg.current(background)["asset"] is not None: refs.append(bg.current(background)["asset"])
        for ref in refs: expected_pairs.setdefault(ref["file"],{"old":None,"new":None})[side] = ref
    expected_pairs = {path:pair for path,pair in expected_pairs.items() if pair["old"] != pair["new"]}
    require(set(expected_pairs) == set(journal["replacements"]),"Raster binary delta differs from source decisions")
    for path,pair in expected_pairs.items():
        for side,ref in pair.items():
            actual = journal["replacements"][path][side]
            require(actual is None if ref is None else actual is not None and all(actual[key] == ref[key] for key in ("sha256","bytes")),"Raster binary bytes differ from source")
