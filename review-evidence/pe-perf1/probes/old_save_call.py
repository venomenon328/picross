"""Unmodified old A2/A3 API under its unchanged 300-s budget, with observations."""
from pathlib import Path
import sys,os,json,time,hashlib,traceback,tempfile
b=Path(__file__).resolve().parent;sys.path.insert(0,str(b/'old-program'))
t=b/'temp-old-save-call';t.mkdir(exist_ok=True);os.environ.update(TEMP=str(t),TMP=str(t),TMPDIR=str(t));tempfile.tempdir=str(t)
from tools.puzzle_production import catalog_images as images,catalog_raster as raster,catalog_transaction as tx,content_registry as cr,reveal_source as reveal,operation_diagnostics as d,catalog_io as io
for module,names in [(tx,['prepare','validate_journal','namespaces']),(cr,['check_checkout']),(reveal,['package'])]:
    for name in names:setattr(module,name,d.measured(name)(getattr(module,name)))
kind,action,bundle=sys.argv[1:];bundle=Path(bundle);root=b/'old-saves-v8-data'
def inventory():return {p.relative_to(root).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtime_ns':p.stat().st_mtime_ns,'bytes':p.stat().st_size} for folder in ('content','game/data','game/art/content','game/art/backgrounds') for p in (root/folder).rglob('*') if p.is_file()}
before=inventory();obs=d.Diagnostics(kind+'-'+action,stderr=sys.stdout);started=time.perf_counter();cpu=time.process_time();error=None
with d.observe(obs):
    try:
        with io.budget(300):
            api=images if kind=='images' else raster
            if action=='plan':result=api.plan(root,b/'old-save-input'/('request.json' if kind=='images' else 'raster.json'),bundle)
            else:result=api.apply(root,bundle)
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc).replace(str(b),'<task>'),'traceback':traceback.format_exc().replace(str(b),'<task>')}
wall=time.perf_counter()-started;used=time.process_time()-cpu;after=inventory();profile=obs.result();profile.pop('environment',None)
row={'source':'4e5bfe489851fe4a4b771fcdf125fd89ce440a98','layer':'direct original A2/A3 API; 300 seconds unchanged','action':kind+'-'+action,'wall_seconds':wall,'cpu_seconds':used,'error':error,'profile':profile,'changed':{n:{'before':before.get(n),'after':after.get(n)} for n in set(before)|set(after) if before.get(n)!=after.get(n)},'journal':(root/tx.LOCK).exists(),'runtime_format':json.loads((root/'game/data/registry.json').read_bytes())['format']}
(b/('old-save-'+kind+'-'+action+'.json')).write_text(json.dumps(row,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('RESULT',row['action'],wall,error['message'] if error else 'ok',flush=True)
