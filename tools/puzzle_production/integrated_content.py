"""Retire explicitly associated work after comparing the current main result."""
from pathlib import Path
import re
import subprocess
from . import catalog_io as io, current_content as content, current_delivery as delivery
from . import current_registration as transaction, content_registry
from .authoring_package import require, relative
from .reveal_retirement import index_rows, selection, blob_id
from .contract import exact_keys
INDEX = "content/authoring/index.json"
LIMIT = 8*1024*1024


def _within(name,directory):
    return name==directory or name.startswith(directory+"/")


def _completed_selection(ids,revisions,work):
    result={identifier:{"revisions":set(),"work":set()} for identifier in ids}
    for values,kind in ((revisions or [],"revisions"),(work or [],"work")):
        require(isinstance(values,(list,tuple)),"Expected completed work pairs")
        for pair in values:
            require(isinstance(pair,(list,tuple)) and len(pair)==2,"Expected ID/path pair")
            identifier,value=pair
            require(identifier in result,"Unselected completed work")
            relative(value)
            name=selection(identifier,value) if kind=="revisions" else "content/authoring/"+identifier+"/"+value
            require(not any(_within(name,n) or _within(n,name) for n in result[identifier][kind]),"Overlapping work selection")
            result[identifier][kind].add(name)
    return result


def retire(root,ids,integrated_commit,*,source_commits=None,completed_revisions=None,completed_work=None):
    root=io.external(root)
    from . import current_authoring
    current_index=io.json_bytes(io.read(root,INDEX,LIMIT),LIMIT)
    if all(not any(r['puzzle_id']==identifier and r['revision']!='current' for r in current_index['entries']) for identifier in ids):
        require(not completed_revisions and not completed_work, 'Current jobs need no historical phase selection')
        return current_authoring.retire(root,ids,integrated_commit,source_commits=source_commits)
    def git(*args):
        result=subprocess.run(["git",*args],cwd=root,capture_output=True)
        require(result.returncode==0,"Cannot confirm main/work: "+result.stderr.decode(errors="replace").strip())
        return result.stdout
    require(root==io.external(git("rev-parse","--show-toplevel").decode().strip()),"Use checkout root")
    require(isinstance(integrated_commit,str) and re.fullmatch(r"[0-9a-f]{40}",integrated_commit),"Full main commit required")
    require(git("cat-file","-t",integrated_commit).strip()==b"commit","Main identity is not a commit")
    for ref in ("origin/main","HEAD"):git("merge-base","--is-ancestor",integrated_commit,ref)
    main=git("rev-parse","origin/main").decode().strip()
    require(isinstance(ids,(list,tuple)) and ids and len(ids)==len(set(ids)),"Select unique IDs")
    for identifier in ids:content.rating.identity(identifier)
    completed=_completed_selection(ids,completed_revisions,completed_work)
    source_commits=source_commits or {}
    require(set(source_commits)<=set(ids),"Foreign work source")
    for commit in source_commits.values():
        require(re.fullmatch(r"[0-9a-f]{40}",commit) and git("cat-file","-t",commit).strip()==b"commit","Invalid work source commit")
        git("merge-base","--is-ancestor",commit,integrated_commit)
    def main_read(name,limit,*,missing=False):
        # Distinguish a genuinely absent historical TXT from an unreadable blob.
        if missing and name.encode() not in git("ls-tree","-r","--name-only",main,"--",name).splitlines():
            return None
        raw=git("show",main+":"+name)
        require(len(raw)<=limit,"Selected main file exceeds limit: "+name)
        return raw
    snapshots={}
    protected=set()
    for identifier in ids:
        snapshot=transaction.Snapshot(root,identifier)
        require(snapshot.delivery is not None,"Delivery is not currently registered")
        local=delivery.snapshot(lambda n,limit,missing=False:snapshot.read(n,limit,missing=missing),identifier)
        confirmed=delivery.snapshot(main_read,identifier)
        require(delivery.same(local,confirmed),"Current selected delivery differs from confirmed main")
        snapshots[identifier]=snapshot
        protected.update(snapshot.raw)
    index_raw=io.read(root,INDEX,LIMIT)
    index=io.json_bytes(index_raw,LIMIT);rows=index_rows(index)
    directories=set()
    for identifier in ids:
        selected=completed[identifier]
        # Current registered work can close automatically. Earlier phases are
        # explicit associations supplied by the normal five-step workflow.
        for directory,row in rows.items():
            if row["puzzle_id"]!=identifier:continue
            record_raw=io.read(root,row["record"],1024*1024,missing=True)
            if record_raw is None:
                record_raw=git("show",source_commits.get(identifier,integrated_commit)+":"+row["record"])
            record=io.json_bytes(record_raw,1024*1024)
            if record.get("state")=="registered":
                selected["revisions"].add(directory)
        directories|=selected["revisions"]|selected["work"]
    files={}
    removed_rows=set()
    for identifier in ids:
        commit=source_commits.get(identifier,integrated_commit)
        for directory in sorted(completed[identifier]["revisions"]|completed[identifier]["work"]):
            path=io.safe(root,directory)
            if not path.exists():
                require(directory not in rows,"Indexed work is missing")
                continue
            require(path.is_dir(),"Completed work must be a directory")
            tree={}
            for item in git("ls-tree","-rz",commit,"--",directory).split(b"\0"):
                if not item:continue
                meta,name=item.split(b"\t",1);mode,kind,object_id=meta.decode().split()
                require(mode=="100644" and kind=="blob","Nonregular completed work")
                tree[name.decode()]=object_id
            local={}
            for child in path.rglob("*"):
                name=child.relative_to(root).as_posix()
                checked=io.safe(root,name)
                if checked.is_file():local[name]=io.read(root,name,content.LIMIT)
            require(set(local)<=set(tree) and all(blob_id(raw)==tree[name] for name,raw in local.items()),
                    "New, open or foreign work differs from completed selection: "+directory)
            require(not set(local)&protected,"Work overlaps current content/rights")
            require(not git("diff","--cached","--name-only","--",directory).strip(),"Completed work has a staged edit")
            files.update(local)
            if directory in rows:
                require(rows[directory]["puzzle_id"]==identifier,"Foreign index row")
                removed_rows.add(directory)
    # Remove a completed current-view pointer only when its exact committed
    # bytes refer to a selected retired revision. A new pointer remains work.
    for identifier in ids:
        name="content/authoring/"+identifier+"/current-view.json"
        raw=io.read(root,name,4096,missing=True)
        if raw is None:continue
        pointer=io.json_bytes(raw,4096)
        if selection(identifier,pointer["revision"]) not in removed_rows:continue
        expected=git("show",source_commits.get(identifier,integrated_commit)+":"+name)
        require(raw==expected,"Current view changed after completion")
        require(not git("diff","--cached","--name-only","--",name).strip(),"Current view has staged edits")
        files[name]=raw
    new_index={"format":index["format"],"entries":[row for directory,row in rows.items() if directory not in removed_rows]}
    if not files and new_index==index:
        return {"status":"no-op","main_commit":main,"retired":[],"registered":True}
    # Use the existing cooperative retirement lock and exact-byte guards.
    from .retirement_scope import operation
    with operation(root) as scope:
        for snapshot in snapshots.values():snapshot.recheck()
        require(io.read(root,INDEX,LIMIT)==index_raw,"Authoring index changed")
        for name,raw in files.items():require(io.read(root,name,content.LIMIT)==raw,"Completed work changed")
        scope.acquire(ids,main)
        try:
            for name in sorted(files):
                scope.pending()
                require(io.read(root,name,content.LIMIT)==files[name],"Foreign work appeared during retirement")
                io.safe(root,name).unlink()
                scope.forget(name)
            if new_index!=index:
                require(io.read(root,INDEX,LIMIT)==index_raw,"Authoring index changed")
                content_registry.atomic_bytes(io.safe(root,INDEX),content.encoded(new_index))
                scope.forget(INDEX)
        finally:
            scope.release()
    return {"status":"retired","main_commit":main,"retired":sorted(files),"registered":True}
