import sys, json, time, subprocess, platform
from pathlib import Path
ROOT=Path(r'E:\Zeuch\Coding\picross_codex\ri-one-20261116\repo')
sys.path.insert(0,str(ROOT))
from tools.puzzle_production.za1_fixtures import make,approve,isolated_checkout,difficulty_for_export
from tools.puzzle_production.target_adapter import export
from tools.puzzle_production.content_registry import registration
from tools.puzzle_production.integrated_content import retire
from tools.puzzle_production.contract import write_json
from PIL import __version__ as pillow
BASE=ROOT.parent/'baseline-v8'
BASE.mkdir(exist_ok=False)
events=[]
phase=None
def audit(event,args):
    if phase and event in ('open','os.listdir','os.scandir'):
        events.append({'phase':phase,'event':event,'path':str(args[0]),'mode':str(args[1]) if event=='open' else None})
sys.addaudithook(audit)
def git(root,*args):
    p=subprocess.run(['git',*args],cwd=root,capture_output=True,check=True)
    return p.stdout.decode().strip()
report={'base':git(ROOT,'rev-parse','HEAD'),'python':platform.python_version(),'pillow':pillow,'cases':[]}
for label,mode,colors in [('mono','mono',1),('one-color','color',1)]:
    home=BASE/label
    package=make(home/'package','pz-ri-one-'+label,3,3,mode,colors=colors)
    approval=home/'approval.json';approve(package,approval)
    checkout=isolated_checkout(home/'checkout')
    runtime=json.loads((checkout/'game/data/registry.json').read_bytes());runtime['format']='picross-runtime-registry-v8';write_json(checkout/'game/data/registry.json',runtime)
    write_json(checkout/'content/authoring/index.json',{'format':'picross-authoring-index-v1','entries':[]})
    dest=home/'export'
    times={}
    def run(name,fn):
        global phase
        phase=label+'/'+name
        start=time.perf_counter()
        try:return fn()
        finally:times[name]=time.perf_counter()-start;phase=None
    run('export',lambda:export(package,dest,name='TEST ONLY '+label,revision=1,stem='pz-ri-one-'+label,save_slot='slot_'+label,approval_path=approval,category_id='gemuese-pilze-kraeuter',categories_path=checkout/'content/categories.json'))
    difficulty=difficulty_for_export(dest)
    write_json(home/'difficulty.json',difficulty)
    run('plan',lambda:registration(dest,checkout,difficulty=difficulty))
    run('write',lambda:registration(dest,checkout,difficulty=difficulty,apply=True))
    git(checkout,'init','--initial-branch=main')
    git(checkout,'config','user.name','RI-ONE synthetic fixture')
    git(checkout,'config','user.email','ri-one@example.invalid')
    git(checkout,'add','.')
    git(checkout,'commit','-m','Synthetic integration baseline')
    head=git(checkout,'rev-parse','HEAD')
    git(checkout,'update-ref','refs/remotes/origin/main',head)
    result=run('completion',lambda:retire(checkout,['pz-ri-one-'+label],head))
    report['cases'].append({'case':label,'times_seconds':times,'total_seconds':sum(times.values()),'completion':result})
report['file_accesses']=events
(BASE/'before.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({**report,'file_accesses':len(events)},indent=2))


