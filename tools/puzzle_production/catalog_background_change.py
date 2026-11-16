"""Separate current image edits through the selected editor transaction.

The current request is picross-editor-request-v2. Prepared image bytes and the
explicit request are private work; no production origin or old journal is read.
"""
from pathlib import Path
from . import catalog_io as io, editor_cli, editor_change as edit
from .authoring_package import require
from .contract import digest


def outside(path,root):
    path=io.external(path);root=io.external(root)
    require(not path.is_relative_to(root) and not root.is_relative_to(path),"Image plan must be outside checkout")
    return path


def store(root,record_path,source_root):
    root=io.external(root);source=outside(source_root,root);path=io.external(record_path)
    require(path.is_relative_to(source),"Current image request must belong to selected work")
    value=editor_cli.read(path,256*1024)
    require(value["format"]==editor_cli.REQUEST and value["text"] is None and value["background"] is not None,
            "Use a separate current background request")
    return {"status":"stored","id":value["id"]}


def plan(root,record_path,output,*,seconds=300):
    output=outside(output,root)
    require(not output.exists(),"Image plan output exists")
    output.mkdir()
    with io.budget(seconds):
        result=editor_cli.plan_file(root,record_path,output/"plan.json")
    return {**result,"status":"planned"}


def load_plan(path):
    path=io.external(path)
    if path.is_dir():path=path/"plan.json"
    raw=io.read(path.parent,path.name,edit.LIMIT)
    value=io.json_bytes(raw,edit.LIMIT);edit.validate(value)
    return value,raw,{"plan.json":raw}


def adopt(root,plan_path,*,seconds=300,fail_step=None,no_op_only=False):
    root=io.external(root)
    with io.budget(seconds):
        value,raw,files=load_plan(plan_path)
        sides=edit.validate(value)
        actual={n:io.read(root,n,edit.FILE_LIMIT,missing=True) for n in value["reads"]}
        unchanged=all(n in sides or io.checksum(data)==value["reads"][n] for n,data in actual.items())
        if unchanged and all(actual[n]==pair[1] for n,pair in sides.items()):
            require(not edit.pending(root),"Recovery required")
            return {"status":"no-op","id":value["id"]}
        old=unchanged and all(actual[n]==pair[0] for n,pair in sides.items())
        if no_op_only:
            require(old,"Current image result differs from both booked sides")
            return {"status":"rollback-confirmed","id":value["id"],"plan_hash":value["plan_hash"]}
        result=edit.apply(root,value)
        return {**result,"status":"no-op" if result["status"]=="noop" else "adopted","id":value["id"]}


from .images_cli import main
if __name__ == "__main__":raise SystemExit(main())
