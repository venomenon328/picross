"""Current metadata/rating/date transactions, separate from first registration."""
from copy import deepcopy
from pathlib import Path
import os
from . import catalog_io as io, current_content as content, current_registration as registration
from . import categories, catalog_rating as rating, catalog_added as added, catalog_method
from . import catalog_background as background_source, reveal_source as reveal
from . import catalog_publication as publication
from .authoring_package import require, relative, sha
from .contract import exact_keys

REGISTRY, RUNTIME, LOCK = content.REGISTRY, content.RUNTIME, registration.LOCK
LIMIT = 24*1024*1024
REVEAL_LIMIT = 128*1024*1024
FORMAT = "picross-current-catalog-journal-v1"
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


def image_generation(snapshot):
    raw = snapshot["texts"][RUNTIME]
    if isinstance(raw,str): raw=raw.encode()
    return io.json_bytes(raw,8*1024*1024)["format"] == content.RUNTIME_FORMAT


def active_reveal(entry,texts):
    raw=texts[reveal.path(entry["id"])]
    if isinstance(raw,str): raw=raw.encode()
    return content.validate_source(io.json_bytes(raw,reveal.LIMIT),entry)["current"]["asset"]["file"]


def text_names(registry, **unused):
    names={REGISTRY,RUNTIME,categories.PATH,catalog_method.PATH,background_source.CAPABILITY}
    for entry in registry["entries"]:
        identifier=entry["id"]
        names.update(("game/"+entry["definition"],content.notice_path(entry),rating.path(identifier),added.path(identifier),
                      reveal.path(identifier),background_source.path(identifier),background_source.notice_path(identifier)))
    return names


def report_names(run, operation="adoption"):
    if run is None: return set()
    if operation == "added-adoption": return {added.report_path(run)}
    from .catalog_analysis import run_id
    prefix="content/difficulty/reports/"+run_id(run)
    return {prefix+"/report.json",prefix+"/report.md"}


def image_candidates(registry):
    return {name for entry in registry["entries"] for name in
            (*(Path("game/"+entry["reveal"]).with_suffix(s).as_posix() for s in (".png",".svg")),
             background_source.asset_path(entry["id"]))}


def retained_names(root,registry,**options):
    texts=options.get("texts") or {n:read(root,n) for n in text_names(registry)}
    names={active_reveal(e,texts) for e in registry["entries"]}
    names |= background_source.retained_names(root,registry,texts)
    return names-set(options.get("exclude",()))


def namespaces(root,registry,**unused):
    # Names of current resources only; no archive enumeration.
    return {"current":sorted(text_names(registry)|retained_names(root,registry))}


def image_snapshot(snapshot):
    return {"sources":{**snapshot["retained"],**{n:io.checksum(raw.encode() if isinstance(raw,str) else raw)
                                               for n,raw in snapshot["texts"].items()}},
            "namespaces":deepcopy(snapshot["namespaces"])}


def capture(root, *, allow_stale=False):
    root=io.external(root)
    require(not registration.pending(root),"Pending publication requires recovery")
    value=content.validate(io.json_bytes(read(root,REGISTRY),8*1024*1024),
                           io.json_bytes(read(root,categories.PATH),categories.MAX_BYTES))
    texts={n:read(root,n) for n in text_names(value)}
    retained={n:file_hash(root,n) for n in retained_names(root,value,texts=texts)}
    expected=projection(texts,value)
    require(allow_stale or texts[RUNTIME] == expected,"Stale runtime")
    snapshot={"registry":value,"texts":texts,"retained":retained,"namespaces":{"current":sorted(set(texts)|set(retained))}}
    recheck(root,snapshot)
    return snapshot


def capture_detail(root,identifier):
    s=registration.Snapshot(root,identifier)
    require(s.delivery is not None,"Unknown current ID")
    return {"registry":s.registry,"texts":s.raw,"retained":{},"namespaces":{"current":sorted(s.raw)}}


def recheck(root,snapshot):
    require(not registration.pending(root),"Concurrent publication")
    require(all(read(root,n)==raw for n,raw in snapshot["texts"].items()) and
            all(file_hash(root,n)==h for n,h in snapshot["retained"].items()),"Current catalog changed")


def projection(texts,registry,version=None):
    from .content_registry import projection as project
    def raw(name):
        value=texts[name]
        return value.encode() if isinstance(value,str) else value
    cats=io.json_bytes(raw(categories.PATH),categories.MAX_BYTES)
    ratings,dates,reveals={},{},{}
    for entry in registry["entries"]:
        identifier=entry["id"]
        ratings[identifier]=rating.validate(io.json_bytes(raw(rating.path(identifier)),rating.LIMIT),
                                           definition_bytes=raw("game/"+entry["definition"]),production_mode=entry["mode"])
        dates[identifier]=added.validate(io.json_bytes(raw(added.path(identifier)),added.LIMIT),identifier)
        reveals[identifier]=active_reveal(entry,texts).removeprefix("game/")
    return content.encoded(project(registry,cats,ratings=ratings,added=dates,reveals=reveals,
                                   backgrounds=background_source.projection(registry,texts),version=8))


def prepare(root,snapshot,changes,*,operation,additions=None,report_run=None,replacements=None,generation=None):
    require(operation in OPERATIONS,"Operation requires its dedicated current writer")
    require(not additions and not replacements,"Current metadata transaction does not write assets")
    recheck(root,snapshot)
    allowed={RUNTIME}
    if operation=="metadata": allowed|={REGISTRY,categories.PATH}
    elif operation=="method-activation": allowed.add(catalog_method.PATH)
    elif operation=="adoption": allowed|={rating.path(e["id"]) for e in snapshot["registry"]["entries"]}|report_names(report_run)
    elif operation=="added-adoption": allowed|={added.path(e["id"]) for e in snapshot["registry"]["entries"]}|report_names(report_run,operation)
    require(set(changes)<=allowed,"Foreign current mutation")
    old={**snapshot["texts"],**{n:read(root,n) for n in set(changes)-set(snapshot["texts"])}}
    new={**old,**changes}
    value=io.json_bytes(new[REGISTRY],8*1024*1024)
    new[RUNTIME]=projection(new,value)
    journal={"format":FORMAT,"operation":operation,"report_run":report_run,
             "old":{n:raw.decode() if raw is not None else None for n,raw in old.items()},
             "new":{n:raw.decode() if raw is not None else None for n,raw in new.items()},
             "retained":snapshot["retained"],"additions":{},"replacements":{}}
    validate_journal(root,journal,before_write=True)
    return journal


def validate_journal(root,journal,*,before_write=False):
    exact_keys(journal,{"format","operation","report_run","old","new","retained","additions","replacements"})
    require(journal["format"]==FORMAT and journal["operation"] in OPERATIONS and not journal["additions"] and
            not journal["replacements"],"Current metadata journal required")
    require(set(journal["old"])==set(journal["new"]) and len(content.encoded(journal))<=LIMIT,"Invalid journal sides")
    sides={side:{n:raw.encode() if raw is not None else None for n,raw in journal[side].items()} for side in ("old","new")}
    indices={}
    for side,values in sides.items():
        indices[side]=content.validate(io.json_bytes(values[REGISTRY],8*1024*1024),
                                      io.json_bytes(values[categories.PATH],categories.MAX_BYTES))
        require(set(values)==text_names(indices[side])|report_names(journal["report_run"],journal["operation"]),"Foreign journal inventory")
        # Stale runtime is only permissible on the old side of explicit sync.
        if side=="new" or journal["operation"]!="sync":
            require(values[RUNTIME]==projection(values,indices[side]),"Current journal projection differs")
    require(indices["old"]["entries"]==indices["new"]["entries"] and
            indices["old"]["backgrounds"]==indices["new"]["backgrounds"],"Metadata writer changes content identity")
    allowed={RUNTIME}
    op=journal["operation"]
    if op=="metadata": allowed|={REGISTRY,categories.PATH}
    elif op=="method-activation": allowed.add(catalog_method.PATH)
    elif op=="adoption": allowed|={rating.path(e["id"]) for e in indices["old"]["entries"]}|report_names(journal["report_run"])
    elif op=="added-adoption": allowed|={added.path(e["id"]) for e in indices["old"]["entries"]}|report_names(journal["report_run"],op)
    require(all(n in allowed or sides["old"][n]==raw for n,raw in sides["new"].items()),"Foreign operation delta")
    if op=="adoption":
        from . import catalog_analysis as analysis
        prefix="content/difficulty/reports/"+analysis.run_id(journal["report_run"])+"/report."
        report=analysis.validate_report(io.json_bytes(sides["new"][prefix+"json"],analysis.REPORT_LIMIT))
        require(report["format"]==analysis.IMAGE_FORMAT and report["run_id"]==journal["report_run"] and
                report["operation"]["phase"]=="adopted","Invalid current adoption report")
        require(all(sides["old"][prefix+ext] is None for ext in ("json","md")) and
                sides["new"][prefix+"md"]==analysis.markdown(report).encode(),"Changed adoption report")
        sources={n:io.checksum(raw) for n,raw in sides["old"].items() if n not in report_names(journal["report_run"])}
        sources.update(journal["retained"])
        require(sources==report["result"]["sources"],"Adoption report source binding differs")
        rows={row["id"]:row for row in report["result"]["entries"]}
        for entry in indices["old"]["entries"]:
            identifier=entry["id"];name=rating.path(identifier)
            old=rating.validate(io.json_bytes(sides["old"][name],rating.LIMIT))
            new=rating.validate(io.json_bytes(sides["new"][name],rating.LIMIT))
            row=rows.get(identifier)
            if row is None or row["status"]!="rated":
                require(old==new,"Unselected/open rating changed")
            else:
                require(row["old"]==rating.project(old) and row["previous_record_hash"]==old["record_hash"] and
                        row["proposed"]==rating.project(new) and row["rating_hash"]==new["rating"]["rating_hash"] and
                        row["current_source"]==new["current_source"] and row["logic_binding"]==new["logic_binding"],
                        "Adoption rating delta differs from report")
                require(old==new or new["rating_revision"]==old["rating_revision"]+1,"Invalid rating revision")
    elif op=="added-adoption":
        from .catalog_added_history import validate_delta
        validate_delta(journal,indices["old"])
    elif op=="method-activation":
        old=catalog_method.from_bytes(sides["old"][catalog_method.PATH])
        new=catalog_method.from_bytes(sides["new"][catalog_method.PATH])
        require(new is not None and new["revision"]==(old["revision"]+1 if old else 1) and
                new["previous_record_hash"]==(old["record_hash"] if old else None),"Invalid method activation chain")
    expected=retained_names(root,indices["old"],texts=sides["old"])
    require(set(journal["retained"])==expected,"Foreign retained inventory")
    for h in journal["retained"].values(): sha(h)
    return sides


def guard(root,journal,*,old_only=False,**unused):
    for n in journal["old"]:
        choices=[journal["old"][n]] if old_only else [journal["old"][n],journal["new"][n]]
        require(read(root,n) in [v.encode() if v is not None else None for v in choices],"Foreign target: "+n)
    require(all(file_hash(root,n)==h for n,h in journal["retained"].items()),"Foreign retained data")


def execute(root,journal,additions=None,*,fail_step=None,**unused):
    root=io.external(root)
    require(not registration.pending(root),"Publication pending")
    sides=validate_journal(root,journal,before_write=True)
    guard(root,journal,old_only=True)
    raw=content.encoded(journal)
    with io.safe(root,STAGE).open("xb") as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    publication.rename(io.safe(root,STAGE),io.safe(root,LOCK),replace=False)
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
    sides=validate_journal(root,journal)
    require(content.encoded(journal)==raw,"Noncanonical journal")
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
