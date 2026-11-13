from pathlib import Path
import sys, json, time, traceback, hashlib, platform
base=Path(__file__).resolve().parent
import os,tempfile
owned_temp=base/'temp-final3-measure';owned_temp.mkdir(exist_ok=True)
os.environ.update(TEMP=str(owned_temp),TMP=str(owned_temp),TMPDIR=str(owned_temp));tempfile.tempdir=str(owned_temp)
sys.path.insert(0,str(base/'work'))
sys.stdout.reconfigure(line_buffering=True)
from tools.puzzle_editor import worker
from tools.puzzle_production import catalog_io as io, catalog_transaction as tx, catalog_images as images, catalog_metadata as metadata, content_registry as cr, reveal_source as reveal, operation_diagnostics as d
for module,names in [(tx,['prepare','validate_journal','namespaces']), (cr,['check_checkout']), (reveal,['package'])]:
    for name in names: setattr(module,name,d.measured(name)(getattr(module,name)))
root=base/'final3-data'
work=base/'final3-work'; work.mkdir(exist_ok=True)
reg=json.loads((root/'content/registry.json').read_bytes())
entries=sorted(reg['entries'],key=lambda e:e['production']['width']*e['production']['height'])
ids=[entries[0]['id'],entries[-1]['id']]
report={'source':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=base/'work',text=True).strip(),'environment':{'os':platform.platform(),'python':sys.version},'ids':[{k:e[k] for k in ('id','production')} for e in (entries[0],entries[-1])], 'runs':[]}

def inventory():
    names=[p for folder in ('content','game/data','game/art/content','game/art/backgrounds') for p in (root/folder).rglob('*') if p.is_file()]
    return {p.relative_to(root).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtime_ns':p.stat().st_mtime_ns,'bytes':p.stat().st_size} for p in names}

def measure(name,fn):
    print('START',name,flush=True)
    before=inventory(); t=time.perf_counter(); cpu=time.process_time(); obs=d.Diagnostics(name,stderr=sys.stdout)
    value=None; error=None
    with d.observe(obs):
        try: value=fn()
        except Exception as exc: error={'type':type(exc).__name__,'message':str(exc).replace(str(root),'<checkout>'),'traceback':traceback.format_exc().replace(str(base),'<task>')}
    wall=time.perf_counter()-t; used=time.process_time()-cpu; after=inventory()
    result=obs.result(); result.pop('environment'); result['counter_scope']='catalog_io counters; legacy freeze I/O is outside these counters' if False else 'catalog_io counters including new method byte bindings; no total OS I/O claim'
    row={'action':name,'wall_seconds':wall,'cpu_seconds':used,'error':error,'profile':result,'changed':{n:{'before':before.get(n),'after':after.get(n)} for n in set(before)|set(after) if before.get(n)!=after.get(n)},'journal':(root/tx.LOCK).exists()}
    report['runs'].append(row)
    (base/'final3-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('END',name,round(wall,3),error['message'] if error else 'ok', 'changed',list(row['changed']),flush=True)
    return value
for i,identifier in enumerate(ids):
    measure('detail-'+str(i)+'-first',lambda:worker.run(root,work,'detail',{'id':identifier}))
    measure('detail-'+str(i)+'-warm',lambda:worker.run(root,work,'detail',{'id':identifier}))
for condition in ('first','warm'):
    plan=measure('migration-plan-'+condition,lambda:worker.run(root,work,'migration',{}))
if (work/'plan.json').exists():
    measure('migration-apply',lambda:worker.run(root,work,'apply',{'kind':'migration'}))
    measure('migration-apply-noop',lambda:worker.run(root,work,'apply',{'kind':'migration'}))
for condition in ('first','warm'):
    p=measure('metadata-plan-'+condition,lambda:metadata.plan(root,[{'op':'set_metadata','id':ids[0],'name':'PE-PERF1 isolated measurement'}]))
if p is not None: measure('metadata-apply',lambda:metadata.apply(root,p))
p=measure('metadata-noop-plan',lambda:metadata.plan(root,[{'op':'set_metadata','id':ids[0],'name':'PE-PERF1 isolated measurement'}]))
if p is not None: measure('metadata-noop-apply',lambda:metadata.apply(root,p))

from tools.puzzle_production import catalog_raster as raster, catalog_background as bg, editor_raster
PROV={'author':'Synthetic performance operator','usage_basis':'Own generated test geometry; isolated disposable catalog only','source':'PE-PERF1 measurement fixture','changes':'Unchanged generated test input'}
DEC={'actor':'PE-PERF1 isolated test operator','timestamp_utc':'2026-11-13T18:00:00Z','statement':'Test geometry in isolated disposable copy only; no production decision.'}
inputs=base/'final3-input'; inputs.mkdir(exist_ok=True)
svg=b'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><rect x="8" y="8" width="112" height="112" fill="#369"/></svg>\n'
(inputs/'reveal.svg').write_bytes(svg)
request={'format':images.REQUEST,'id':ids[0],'metadata':None,'reveal':{'asset':bg.ref('reveal.svg',svg),'provenance':PROV},'background':{'status':'standard','asset':None,'provenance':None},'decision':DEC}
(inputs/'request.json').write_bytes(images.encoded(request))
for condition in ('first','warm'):
    bundle=base/('final3-images-'+condition)
    p=measure('images-plan-'+condition,lambda:images.plan(root,inputs/'request.json',bundle))
if p is not None:
    measure('images-apply',lambda:images.apply(root,bundle))
    measure('images-apply-noop',lambda:images.apply(root,bundle))
request={'format':editor_raster.REQUEST,'id':ids[0],'text':'1 1 1\n1 1 1\n','metadata':None,'reveal':None,'background':None,'decision':DEC,'provenance':PROV,'profile':'line'}
(inputs/'raster.json').write_bytes(images.encoded(request))
for condition in ('first','warm'):
    bundle=base/('final3-raster-'+condition)
    p=measure('raster-plan-'+condition,lambda:raster.plan(root,inputs/'raster.json',bundle))
if p is not None:
    measure('raster-apply',lambda:raster.apply(root,bundle))
    measure('raster-apply-noop',lambda:raster.apply(root,bundle))

measure('post-raster-detail',lambda:worker.run(root,work,'detail',{'id':ids[0]}))
