from pathlib import Path
import sys, json, time, traceback, hashlib, platform
base=Path(__file__).resolve().parent
sys.path.insert(0,str(base/'baseline'))
from tools.puzzle_editor import worker
from tools.puzzle_production import catalog_io as io, catalog_transaction as tx, catalog_images as images, catalog_metadata as metadata, content_registry as cr, reveal_source as reveal, operation_diagnostics as d
for module,names in [(tx,['prepare','validate_journal','namespaces']), (cr,['check_checkout']), (reveal,['package'])]:
    for name in names: setattr(module,name,d.measured(name)(getattr(module,name)))
root=base/'baseline'
work=base/'baseline-work'; work.mkdir(exist_ok=True)
reg=json.loads((root/'content/registry.json').read_bytes())
entries=sorted(reg['entries'],key=lambda e:e['production']['width']*e['production']['height'])
ids=[entries[0]['id'],entries[-1]['id']]
report={'source':'4e5bfe489851fe4a4b771fcdf125fd89ce440a98','environment':{'os':platform.platform(),'python':sys.version},'ids':[{k:e[k] for k in ('id','production')} for e in (entries[0],entries[-1])], 'runs':[]}

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
    result=obs.result(); result.pop('environment'); result.pop('missing_measurements')
    row={'action':name,'wall_seconds':wall,'cpu_seconds':used,'error':error,'profile':result,'changed':{n:{'before':before.get(n),'after':after.get(n)} for n in set(before)|set(after) if before.get(n)!=after.get(n)},'journal':(root/tx.LOCK).exists()}
    report['runs'].append(row)
    (base/'baseline-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('END',name,round(wall,3),error['message'] if error else 'ok', 'changed',list(row['changed']),flush=True)
    return value
for i,identifier in enumerate(ids):
    measure('detail-'+str(i)+'-first',lambda:worker.run(root,work,'detail',{'id':identifier}))
    measure('detail-'+str(i)+'-warm',lambda:worker.run(root,work,'detail',{'id':identifier}))
for condition in ('first','warm'):
    plan=measure('migration-plan-'+condition,lambda:worker.run(root,work,'migration',{}))
if (work/'plan.json').exists():
    measure('migration-apply',lambda:worker.run(root,work,'apply',{'kind':'migration'}))
for condition in ('first','warm'):
    p=measure('metadata-plan-'+condition,lambda:metadata.plan(root,[{'op':'set_metadata','id':ids[0],'name':'PE-PERF1 isolated measurement'}]))
if p is not None: measure('metadata-apply',lambda:metadata.apply(root,p))
