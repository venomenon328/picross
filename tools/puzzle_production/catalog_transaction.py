"""Current metadata/rating/date transactions, separate from first registration."""
from copy import deepcopy
from pathlib import Path
import os
from . import catalog_io as io, current_content as content, current_registration as registration
from . import puzzle_record, puzzle_catalog
from . import categories, catalog_rating as rating, catalog_added as added, catalog_method
from . import catalog_background as background_source, reveal_source as reveal
from . import catalog_publication as publication
from .authoring_package import require, relative, sha
from .contract import exact_keys

RUNTIME, LOCK = content.RUNTIME, registration.LOCK
LIMIT = 24*1024*1024
REVEAL_LIMIT = 128*1024*1024
FORMAT = "picross-puzzle-catalog-journal-v1"
OPERATIONS = ("adoption", "added-adoption", "method-activation", "metadata", "sync")
IMAGE_FORMATS = PE_FORMATS = FORMATS = dict.fromkeys(OPERATIONS, FORMAT)
STAGE = "content/.registration-journal-catalog.tmp"
safe = io.safe


def read(root, name, journal=None):
    return io.read(root,name,content.LIMIT,missing=True)


def file_hash(root,name):
    return io.checksum(read(root,name))


def file_limit(root,name,journal=None):
    return content.LIMIT


def capture(root, identifiers=(), *, allow_stale=False):
    root = io.external(root)
    require(not registration.pending(root),"Pending publication requires recovery")
    ids = puzzle_record.inventory(root)
    texts = {}
    def bound(name,limit,*,missing=False):
        if name not in texts:
            texts[name] = io.read(root,name,limit,missing=missing)
        return texts[name]
    cats = categories.validate(io.json_bytes(bound(categories.PATH,categories.MAX_BYTES),categories.MAX_BYTES))
    raw = bound(RUNTIME,content.RUNTIME_LIMIT)
    runtime = None if allow_stale else puzzle_catalog.validate_runtime(io.json_bytes(raw,content.RUNTIME_LIMIT),cats,ids)
    if allow_stale:
        old = io.json_bytes(raw,content.RUNTIME_LIMIT)
        exact_keys(old, {"format","entries","categories"})
        require(old["format"] == content.RUNTIME_FORMAT and
                [row["id"] for row in old["entries"]] == sorted(ids), "Cannot sync a different record inventory")
    rows = {} if runtime is None else {r["id"]:r for r in runtime["entries"]}
    bound(catalog_method.PATH,catalog_method.LIMIT,missing=True)
    records = {}
    selected = sorted(ids) if identifiers is None else list(identifiers)
    require(len(selected) == len(set(selected)) and set(selected) <= ids,"Unknown or duplicate puzzle selection")
    for identifier in selected:
        record = puzzle_record.load(root,identifier,category_catalog=cats,read=bound)
        require(allow_stale or puzzle_record.runtime_row(record) == rows[identifier],"Stale selected projection")
        records[identifier] = record
    require(not registration.pending(root) and all(read(root,n)==v for n,v in texts.items())
            and ids == puzzle_record.inventory(root),"Catalog changed during capture")
    return {"texts":texts,"records":records,"runtime":runtime,"categories":cats}


def image_snapshot(snapshot):
    return {"sources":{n:io.checksum(raw) for n,raw in snapshot["texts"].items()}}


def report_names(run, operation="adoption"):
    from .catalog_analysis import run_id
    if run is None: return set()
    if operation == "added-adoption": return {added.report_path(run)}
    prefix = "content/difficulty/reports/"+run_id(run)+"/report."
    return {prefix+"json",prefix+"md"}


def sync_runtime(root):
    snapshot = capture(root,None,allow_stale=True)
    rows = [puzzle_record.runtime_row(r) for r in snapshot["records"].values()]
    expected = content.encoded({"format":content.RUNTIME_FORMAT,"categories":categories.ordered(snapshot["categories"]),"entries":rows})
    if expected != snapshot["texts"][RUNTIME]:
        execute(root,record_journal(snapshot["texts"],{RUNTIME:expected},operation="sync"))
    return {"status":"projected","entries":len(rows),"categories":len(snapshot["categories"]["categories"])}


def record_journal(texts, changes, *, operation):
    require(changes.keys() <= texts.keys(), "Unbound catalog change")
    sides = {name:raw.decode() if raw is not None else None for name,raw in texts.items()
             if name in changes or name in (categories.PATH,RUNTIME)}
    new = {**sides, **{n:raw.decode() for n,raw in changes.items()}}
    return {"format":FORMAT,"operation":operation,"old":sides,"new":new,
            "retained":{n:io.checksum(raw) for n,raw in texts.items() if n not in sides}}


def validate_metadata_journal(root,journal,*,journal_temps=()):
    exact_keys(journal,{"format","operation","old","new","retained"})
    require(journal["format"] == FORMAT and journal["operation"] == "metadata" and
            len(content.encoded(journal)) <= LIMIT, "Invalid metadata journal")
    require(set(journal["old"]) == set(journal["new"]), "Different metadata sides")
    ids = puzzle_record.inventory(root,journal_temps=journal_temps)
    selected = {Path(n).stem for n in journal["old"] if n.startswith(puzzle_record.DIRECTORY+"/")}
    require(selected <= ids and set(journal["old"]) == {RUNTIME,categories.PATH,*map(puzzle_record.path,selected)},
            "Foreign metadata targets")
    sides = {s:{n:raw.encode() for n,raw in journal[s].items()} for s in ("old","new")}
    states = {}
    for side, files in sides.items():
        cats, runtime = puzzle_catalog.index(lambda n,limit:files[n],ids)
        rows = {r["id"]:r for r in runtime["entries"]}
        definitions = {}
        records = {}
        for identifier in selected:
            record = puzzle_record.decode(files[puzzle_record.path(identifier)],identifier)
            row = rows[identifier]
            name = "game/"+row["definition"]
            raw = io.read(root,name,2*1024*1024)
            definitions[name] = io.checksum(raw)
            puzzle_record.validate(record,identifier,raw,category_catalog=cats)
            require(row == puzzle_record.runtime_row(record), "Metadata projection mismatch")
            records[identifier] = record
        require(definitions == journal["retained"], "Metadata definition binding differs")
        states[side] = rows,records
    old_rows, old_records = states["old"]
    new_rows, new_records = states["new"]
    require(all(old_rows[k] == new_rows[k] for k in ids-selected), "Foreign metadata row change")
    for key in selected:
        require(all(old_records[key][k] == v for k,v in new_records[key].items() if k not in ("name","category_id")),
                "Metadata changed another field")
    return sides


def validate_journal(root,journal,*,journal_temps=()):
    if journal.get("operation") == "metadata":
        return validate_metadata_journal(root,journal,journal_temps=journal_temps)
    exact_keys(journal,{"format","operation","old","new","retained"})
    require(journal["format"] == FORMAT and len(content.encoded(journal)) <= LIMIT, "Invalid catalog journal")
    op = journal["operation"]
    require(op in ("sync","method-activation","adoption","added-adoption"),"Unknown catalog operation")
    require(journal["old"].keys() == journal["new"].keys(), "Different catalog sides")
    sides = {s:{n:raw.encode() if raw is not None else None for n,raw in journal[s].items()} for s in ("old","new")}
    old,new = sides["old"],sides["new"]
    cats = categories.validate(io.json_bytes(old[categories.PATH],categories.MAX_BYTES))
    require(new[categories.PATH] == old[categories.PATH],"Foreign category change")
    ids = puzzle_record.inventory(root,journal_temps=journal_temps)
    if op == "added-adoption":
        from . import catalog_added_history
        return catalog_added_history.validate_journal(root,journal,sides,ids,cats)
    if op == "method-activation":
        require(old.keys() == {RUNTIME,categories.PATH,catalog_method.PATH} and not journal["retained"]
                and old[RUNTIME] == new[RUNTIME],"Foreign activation targets")
        puzzle_catalog.validate_runtime(io.json_bytes(old[RUNTIME],content.RUNTIME_LIMIT),cats,ids)
        previous = catalog_method.from_bytes(old[catalog_method.PATH])
        following = catalog_method.from_bytes(new[catalog_method.PATH])
        require(following and following["revision"] == (previous["revision"]+1 if previous else 1) and
                following["previous_record_hash"] == (previous["record_hash"] if previous else None) and
                following["method"] != catalog_method.current(previous)["method"], "Invalid method transition")
        return sides
    if op == "sync":
        prior = io.json_bytes(old[RUNTIME],content.RUNTIME_LIMIT)
        require(prior["format"] == content.RUNTIME_FORMAT and [row["id"] for row in prior["entries"]] == sorted(ids),
                "Cannot recover a different record inventory")
        require(old.keys() == {RUNTIME,categories.PATH}, "Foreign sync target")
        retained = {}
        def bound(n,limit):
            raw = io.read(root,n,limit)
            retained[n] = io.checksum(raw)
            return raw
        rows = [puzzle_record.runtime_row(puzzle_record.load(root,key,category_catalog=cats,read=bound)) for key in sorted(ids)]
        retained[catalog_method.PATH] = io.checksum(read(root,catalog_method.PATH))
        require(retained == journal["retained"] and new[RUNTIME] == content.encoded(
            {"format":content.RUNTIME_FORMAT,"categories":categories.ordered(cats),"entries":rows}),"Sync projection differs")
        puzzle_catalog.validate_runtime(io.json_bytes(new[RUNTIME],content.RUNTIME_LIMIT),cats,ids)
        return sides
    from . import catalog_analysis as analysis
    report_paths = [n for n in new if n.startswith("content/difficulty/reports/") and n.endswith("/report.json")]
    require(len(report_paths) == 1,"Missing rating report")
    report_name = report_paths[0]
    report = analysis.validate_report(io.json_bytes(new[report_name],analysis.REPORT_LIMIT))
    run = report["run_id"]
    reports = report_names(run)
    require(report_name in reports and report["format"] == analysis.IMAGE_FORMAT and report["operation"]["phase"] == "adopted"
            and all(old[n] is None for n in reports) and
            new[report_name[:-4]+"md"] == analysis.markdown(report).encode(),"Invalid adoption report")
    result = report["result"]
    selected = {r["id"]:r for r in result["entries"]}
    old_runtime = puzzle_catalog.validate_runtime(io.json_bytes(old[RUNTIME],content.RUNTIME_LIMIT),cats,ids)
    projected = deepcopy(old_runtime)
    sources = dict(journal["retained"])
    sources.update({n:io.checksum(raw) for n,raw in old.items() if n not in reports})
    require(sources == result["sources"] and set(old)-reports-{categories.PATH,RUNTIME} <= {puzzle_record.path(k) for k in selected},
            "Foreign adoption sources or targets")
    expected_sources = {categories.PATH,RUNTIME,catalog_method.PATH}
    for row in projected["entries"]:
        key = row["id"]
        if key not in selected: continue
        request = selected[key]
        name = puzzle_record.path(key)
        definition_name = "game/"+row["definition"]
        expected_sources.update((name,definition_name))
        if name not in old: continue
        raw = io.read(root,definition_name,2*1024*1024)
        prior, record = (puzzle_record.validate(puzzle_record.decode(side[name],key),key,raw,category_catalog=cats) for side in (old,new))
        require(request["status"] == "rated" and io.checksum(old[name]) == request["previous_record_hash"] and
                all(prior[k] == record[k] for k in prior if k != "difficulty") and
                prior["difficulty"]["rating_revision"]+1 == record["difficulty"]["rating_revision"] and
                record["difficulty"]["rating"]["rating_hash"] == request["rating_hash"] and
                puzzle_record.runtime_row(prior) == row,"Invalid adopted rating change")
        row.update(puzzle_record.runtime_row(record))
        require(row["difficulty"] == request["proposed"],"Wrong adoption projection")
    require(set(sources) == expected_sources and content.encoded(projected) == new[RUNTIME],"Foreign adoption result")
    return sides


def guard(root,journal,*,old_only=False,**unused):
    for n in journal["old"]:
        choices=[journal["old"][n]] if old_only else [journal["old"][n],journal["new"][n]]
        require(read(root,n) in [v.encode() if v is not None else None for v in choices],"Foreign target: "+n)
    require(all(file_hash(root,n)==h for n,h in journal["retained"].items()),"Foreign retained data")


def execute(root,journal,additions=None,*,fail_step=None,**unused):
    root=io.external(root)
    require(not registration.pending(root),"Publication pending")
    sides=validate_journal(root,journal)
    guard(root,journal,old_only=True)
    raw=content.encoded(journal)
    def rollback():
        with io.budget():
            recover(root)
    with publication.owned_journal(root,STAGE,LOCK,raw,rollback):
        guard(root,journal,old_only=True)
        expected=dict(sides["old"])
        def fresh():
            require(read(root,LOCK)==raw,"Catalog lock changed")
            require(all(read(root,n)==v for n,v in expected.items()),"Current catalog phase changed")
            require(all(file_hash(root,n)==h for n,h in journal["retained"].items()),"Foreign retained data")
        for step,name in enumerate(sorted(sides["old"],key=lambda n:(n==RUNTIME,n)),1):
            fresh()
            if sides["old"][name]!=sides["new"][name]:
                registration.write(root,name,sides["old"][name],sides["new"][name],raw,guard=fresh)
                expected[name]=sides["new"][name]
            if fail_step==step: raise RuntimeError("Injected current catalog interruption")
        fresh()
        require(read(root,LOCK)==raw,"Catalog journal changed")
        io.safe(root,LOCK).unlink();publication.sync_directory(root/"content")
        return {"status":"applied"}


def recover(root):
    root=io.external(root)
    name=LOCK if io.safe(root,LOCK).exists() else STAGE
    raw=read(root,name)
    if raw is None:return {"status":"no-op"}
    journal=io.json_bytes(raw,LIMIT)
    require(content.encoded(journal)==raw,"Noncanonical journal")
    require(isinstance(journal.get("old"),dict),"Missing journal targets")
    journal_hash = io.checksum(raw)
    journal_temps = {registration.temporary(n,journal_hash) for n in journal["old"]}
    sides=validate_journal(root,journal,journal_temps=journal_temps)
    guard(root,journal)
    temps={}
    for target in sides["old"]:
        temp=registration.temporary(target,io.checksum(raw))
        data=read(root,temp)
        if data is not None:
            require(any(v is not None and v.startswith(data) for v in (sides["old"][target],sides["new"][target])),
                    "Foreign temporary")
            temps[temp]=data
    if name==STAGE:
        guard(root,journal,old_only=True)
        publication.rename(io.safe(root,STAGE),io.safe(root,LOCK),replace=False)
    for target,data in temps.items():
        require(read(root,target)==data,"Changed temporary")
        io.safe(root,target).unlink();publication.sync_directory(io.safe(root,target).parent)
    expected={n:read(root,n) for n in sides["old"]}
    def fresh():
        require(read(root,LOCK)==raw,"Recovery lock changed")
        require(all(read(root,n)==v for n,v in expected.items()),"Recovery phase changed")
        require(all(file_hash(root,n)==h for n,h in journal["retained"].items()),"Foreign retained data")
    for target in sorted(sides["old"],key=lambda n:(n!=RUNTIME,n)):
        fresh()
        now=expected[target]
        if now!=sides["old"][target]:
            registration.write(root,target,now,sides["old"][target],raw,guard=fresh)
            expected[target]=sides["old"][target]
    fresh()
    require(read(root,LOCK)==raw,"Changed recovery journal")
    io.safe(root,LOCK).unlink();publication.sync_directory(root/"content")
    return {"status":"rolled-back"}
