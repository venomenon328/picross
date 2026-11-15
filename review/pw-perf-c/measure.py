"""Temporary PW-PERF-C T02 driver based on the PW3-B synthetic fixtures; never part of product/test discovery."""
import contextlib
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys
import time
import tracemalloc
import unittest
from unittest.mock import patch
import zipfile

TASK = Path(__file__).parent
REPO = Path(os.environ.get('PW3_MEASURE_REPO', str(TASK / 'repo')))
sys.path.insert(0, str(REPO))
os.environ.update(TEMP=str(TASK/'temp'), TMP=str(TASK/'temp'),
                  GIT_AUTHOR_DATE='2026-11-14T20:00:00Z', GIT_COMMITTER_DATE='2026-11-14T20:00:00Z')
from tools.production_workspace import projector, presentation as p, sources
from tools.puzzle_production import authoring_builder as builder, target_adapter as adapter
from tools.puzzle_production import catalog_io as io, background_assets
from tests.puzzle_production.test_authoring_workflow import WorkflowFixture

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def remove_owned(root):
    root=Path(root).resolve()
    assert root.is_relative_to(TASK.resolve()) and root != TASK.resolve() and not root.is_symlink()
    def readonly(fn,path,error):
        # Git objects in our synthetic copies carry Windows' read-only attribute.
        if not isinstance(error,PermissionError):raise error
        os.chmod(path,stat.S_IWRITE)
        fn(path)
    shutil.rmtree(root,onexc=readonly)

def prepare():
    configs=[]
    for mode,outcome in [('mono','none'),('color','selected')]:
        case=unittest.TestCase()
        f=WorkflowFixture(case,mode=mode)
        f.build(); f.select()
        h=f.helper
        # Populate the exact r02 file list before retaining the pre-build state.
        f.request['files']=[{'path':q.relative_to(h.source).as_posix(), 'source':q.relative_to(h.source).as_posix(),
            'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size}
            for q in sorted(h.source.rglob('*')) if q.is_file()]
        if mode=='color':
            from tests.puzzle_production.background_fixtures import put_json,file_ref
            ref=f.request['handoff']['palette_review']
            review=json.loads((h.source/ref['file']).read_text(encoding='utf-8'));review['revision']='r02'
            r=put_json(h.source,ref['file'],review)
            f.request['handoff']['palette_review']={k:r[k] for k in ('file','sha256')}
            f.request['files']=[{'path':q.relative_to(h.source).as_posix(),'source':q.relative_to(h.source).as_posix(),
                **{k:file_ref(h.source,q.relative_to(h.source).as_posix())[k] for k in ('sha256','bytes')}}
                for q in sorted(h.source.rglob('*')) if q.is_file()]
        snapshots=TASK/'measure-v2'/mode
        if snapshots.exists():
            assert snapshots.resolve().is_relative_to(TASK.resolve()) and not snapshots.is_symlink()
            remove_owned(snapshots)
        snapshots.mkdir(parents=True)
        shutil.copytree(f.root,snapshots/'before-build')
        built=f.build();assert built['status']=='built',built
        request=h.request(outcome=outcome,approval=True)
        request['format']='picross-authoring-finalize-request-v2'
        shutil.copytree(f.root,snapshots/'before-finalize')
        final=builder.finalize_background(request,h.payload,h.output)
        assert final['status']=='updated',final
        shutil.copytree(f.root,snapshots/'before-export')
        config={'mode':mode,'root':str(f.root),'snapshots':str(snapshots),'request':f.request,
                'finalize':request,'source':str(h.source),'staging':str(f.staging),'repo':str(h.output),
                'directory':str(h.directory),'payload':str(h.payload)}
        configs.append(config)
    save(TASK/'config-v2.json',configs)

def restore(c, state):
    root=Path(c['root']).resolve()
    assert root.is_relative_to((TASK/'temp').resolve()) and not root.is_symlink()
    if root.exists():remove_owned(root)
    shutil.copytree(Path(c['snapshots'])/state,root)

def counted(label, fn):
    counts=Counter()
    phases={}
    frames=[]
    def wrap(obj,name,key,byte_result=False,byte_arg=False):
        original=getattr(obj,name)
        def call(*a,**kw):
            counts[key]+=1
            if byte_arg:counts[key+'_bytes']+=len(a[0]) if a[0] is not None else 0
            value=original(*a,**kw)
            if byte_result:counts[key+'_bytes']+=len(value) if value is not None else 0
            return value
        return patch.object(obj,name,call)
    with contextlib.ExitStack() as stack:
        for args in [(io,'read','file_reads',True,False),(io,'checksum','hash',False,True),
                     (zipfile.ZipFile,'__init__','zip_opens',False,False),
                     (sources.Archive,'read','member_reads',True,False),
                     (p.Record,'__init__','records',False,False),
                     (p,'image','view_image_checks',False,False),
                     (adapter,'inspect','adapter_inspections',False,False),
                     (projector,'_automatic','projector_inspections',False,False)]:
            stack.enter_context(wrap(*args))
        from tools.puzzle_production import background_export, authoring_finalization
        def phase(obj, name, label):
            original=getattr(obj,name)
            def call(*a,**kw):
                frame=[time.perf_counter(),0.0];frames.append(frame)
                try:return original(*a,**kw)
                finally:
                    elapsed=time.perf_counter()-frame[0];frames.pop()
                    if frames:frames[-1][1]+=elapsed
                    row=phases.setdefault(label,{'calls':0,'inclusive_seconds':0.0,'exclusive_seconds':0.0})
                    row['calls']+=1;row['inclusive_seconds']+=elapsed;row['exclusive_seconds']+=elapsed-frame[1]
            return patch.object(obj,name,call)
        for obj,name,label in [(adapter,'inspect','content'), (background_export,'verify_background_export','staging/offline'),
                (background_export,'_snapshot','transport-inventory'), (projector,'automatic','projector'),
                (authoring_finalization,'_inspect','finalizer-content'), (background_assets,'_run','background-reproduction')]:
            stack.enter_context(phase(obj,name,label))
        from PIL import Image, PngImagePlugin
        stack.enter_context(wrap(Image,'open','image_opens'))
        png_load=PngImagePlugin.PngImageFile.load
        def decode(im,*args,**kwargs):
            counts['png_load_calls']+=1
            if im.tile:counts['png_decodes']+=1
            return png_load(im,*args,**kwargs)
        stack.enter_context(patch.object(PngImagePlugin.PngImageFile,'load',decode))
        tracemalloc.start();at=time.perf_counter()
        result=fn()
        elapsed=time.perf_counter()-at
        _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return result,{'operation':label,'seconds':elapsed,'peak_python_bytes':peak,'counts':dict(counts),'phases':phases,'unattributed_seconds':elapsed-sum(r['exclusive_seconds'] for r in phases.values())}

def outputs(root):
    return {q.relative_to(root).as_posix():{'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size}
            for q in sorted(root.rglob('*')) if q.is_file() and '.git' not in q.relative_to(root).parts}

def run(tag):
    rows=[]
    for c in json.loads((TASK/'config-v2.json').read_text(encoding='utf-8')):
        root=Path(c['root']);repo=Path(c['repo']);directory=Path(c['directory'])
        def measure(label,fn):
            result,row=counted(label,fn);row['mode']=c['mode']
            row['result']=result;rows.append(row)
            print(c['mode'],label,round(row['seconds'],3),row['counts'],flush=True)
            return result,row
        restore(c,'before-finalize')
        result,row=measure('finalizer',lambda:builder.finalize_background(c['finalize'],c['payload'],repo))
        assert result['status']=='updated',result
        row['bindings']=outputs(directory)
        row['input_bindings']=outputs(Path(c['snapshots'])/'before-finalize')
        restore(c,'before-export')
        record=p.parse((directory/'record.json').read_bytes())
        approval=repo/record['final_editorial_approval']['file']
        output=root/'measured-export'
        options={'name':'TEST ONLY','revision':1,'stem':'pw3_synthetic','save_slot':'pw3_synthetic',
                 'category_id':'voegel','categories_path':REPO/'tests/puzzle_production/fixtures/catalog/categories.json',
                 'approval_path':approval,'allow_background':True,'external_root':repo,'history_repo':repo}
        result,row=measure('export',lambda:adapter.export(directory/'package.zip',output,**options))
        row['bindings']=outputs(output)
        result,row=measure('verify-export',lambda:adapter.verify_export(output))
    report={'tag':tag,'source_head':sources.git(REPO,'rev-parse','HEAD').decode().strip(),
            'source_diff':sources.git(REPO,'diff','--stat').decode(),
            'modules':{str(q.relative_to(REPO)):hashlib.sha256(q.read_bytes()).hexdigest()
                       for folder in ['production_workspace','puzzle_production'] for q in sorted((REPO/'tools'/folder).glob('*.py'))},
            'environment':{'platform':platform.platform(),'python':sys.version,'background_tool':background_assets.describe()},
            'rows':rows}
    save(TASK/(tag+'.json'),report)

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run(sys.argv[1])
