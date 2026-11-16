import json, pathlib, sys, shutil, time, platform, subprocess
from PIL import __version__ as pillow
ROOT = pathlib.Path(sys.argv[2]).resolve()
REPO = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0,str(REPO))
from tools.puzzle_production import current_content as c, integration_input as inp, catalog_rating, catalog_integration as integration, current_registration as tx
from tools.puzzle_production.contract import canonical_bytes, Budget
from tools.puzzle_production.solver import solve
from tools.puzzle_production.current_rating import from_checked

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(c.encoded(value))

events=[]
phase=None
report={"source_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO).decode().strip(),"python":platform.python_version(),"pillow":pillow,"cases":[]}
def audit(event,args):
    if phase and event in ('open','os.listdir','os.scandir'):
        events.append({'phase':phase,'event':event,'path':str(args[0]),'mode':str(args[1]) if event=='open' else None})
sys.addaudithook(audit)
def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.DEVNULL).decode().strip()
for label,mode in (("mono","mono"),("one-color","color")):
    old = ROOT/"baseline-v8"/label
    source = ROOT/"t03-final-inputs"/label
    source.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((old/"export/manifest.json").read_bytes())
    definition=(old/"export"/manifest["definition"]).read_bytes()
    data=json.loads(definition)
    entry={"id":data["id"],"key":data["id"],"save_slot":"slot_"+label,
           "definition":"data/content/"+data["id"]+".json","reveal":data["reveal"]["image"].removeprefix("res://"),
           "visible":True,"mode":mode,"category_id":manifest["category_id"]}
    files = {"definition.json":definition,
             "reveal.png":(old/"export"/manifest["reveal"]).read_bytes(),
             "notice.txt": (old/"export/runtime"/pathlib.Path(entry["reveal"]).with_suffix(".txt")).read_bytes(),
             "difficulty.json":c.encoded(from_checked(json.loads((old/"difficulty.json").read_bytes()))),
             "proof.json":c.encoded(solve(catalog_rating.definition(definition)[1],Budget())),
             "review.json":c.encoded({"actor":"TEST ONLY","timestamp_utc":"2026-11-16T00:00:00Z","statement":"Synthetic final visual review.","criteria":{k:{"result":"fulfilled","accepted":False,"reason":"Synthetic fixture inspected."} for k in ("Q-R04","Q-H01","Q-H02")}}),
             "approval.txt":b"TEST ONLY fixture approval for this final definition, reveal and standard background.\n"}
    for name,raw in files.items(): (source/name).write_bytes(raw)
    refs={name:c.ref(name,raw) for name,raw in files.items()}
    value={"format":inp.FORMAT,"entry":entry,"metadata":{"id":entry["id"],"name":data["reveal"]["name"],"category_id":entry["category_id"]},
           "definition":refs["definition.json"],"reveal":{"asset":refs["reveal.png"],"notice":refs["notice.txt"],
               "rights":{"author":"Test fixture code","usage_basis":"Repository-owned synthetic test pixels; not a catalog asset","source":"Test fixture code","changes":"Test fixture code"}},
           "background":{"status":"standard","image":None},"difficulty":refs["difficulty.json"],"proof":refs["proof.json"],
           "quality":{"review":refs["review.json"],"exceptions":[]},"test_only":True}
    value["approval"]={"actor":"TEST ONLY","timestamp_utc":"2026-11-16T00:00:00Z","statement":"Approve this synthetic fixture only.",
                       "selection_sha256":inp.selection(value),"evidence":refs["approval.txt"],"checks":dict.fromkeys(inp.CHECKS,True)}
    write(source/"manifest.json",value)
    checkout=ROOT/"t03-final-checkouts"/label
    checkout.mkdir(parents=True,exist_ok=True)
    for name in ("content/categories.json","content/difficulty-method.json","game/data/background-capability.json"):
        source_path=ROOT/"baseline-v8"/label/"checkout"/name
        if not source_path.exists() and name == "content/difficulty-method.json": continue
        if not source_path.exists(): source_path=REPO/name
        target=checkout/name
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source_path,target)
    from tools.puzzle_production import categories
    catalog=json.loads((checkout/"content/categories.json").read_bytes())
    write(checkout/c.REGISTRY,{"format":c.FORMAT,"entries":[],"metadata":[],"backgrounds":[]})
    write(checkout/c.RUNTIME,{"format":c.RUNTIME_FORMAT,"entries":[],"categories":categories.ordered(catalog)})
    write(checkout/"content/authoring/index.json",{"format":"picross-authoring-index-v1","entries":[]})
    # Preparation, analysis and normalized independent proof are outside timing,
    # exactly as the old fixture producer/checked analysis were outside timing.
    inp.Input(source)
    times={}
    def run(name,fn):
        global phase
        phase=label+'/'+name;start=time.perf_counter()
        try:return fn()
        finally:times[name]=time.perf_counter()-start;phase=None
    exported=ROOT/"t03-final-export"/label
    run('export',lambda:inp.export(source,exported))
    run('plan',lambda:integration.integrate(exported,checkout))
    run('write',lambda:integration.integrate(exported,checkout,apply=True))
    git(checkout,'init','--initial-branch=main');git(checkout,'config','user.name','RI-ONE synthetic fixture');git(checkout,'config','user.email','ri-one@example.invalid')
    git(checkout,'add','.');git(checkout,'commit','-m','Synthetic current integration')
    head=git(checkout,'rev-parse','HEAD');git(checkout,'update-ref','refs/remotes/origin/main',head)
    from tools.puzzle_production.integrated_content import retire
    result=run('completion',lambda:retire(checkout,[entry['id']],head))
    old_runtime=json.loads((old/'checkout/game/data/registry.json').read_bytes())['entries'][0]
    new_runtime=json.loads((checkout/c.RUNTIME).read_bytes())['entries'][0]
    comparison={k:old_runtime[k]==new_runtime[k] for k in old_runtime if k not in ('background','added_at')}
    assert all(comparison.values()),comparison
    report['cases'].append({'case':label,'mode':mode,'times_seconds':times,'total_seconds':sum(times.values()),'completion':result,'unchanged_runtime_fields':comparison,'background_note':'Old fixture had legacy standard background; new fixture declares standard explicitly.','definition_sha256':c.io.checksum(definition),'reveal_sha256':c.io.checksum(files['reveal.png']),'notice_sha256':c.io.checksum(files['notice.txt'])})
report['file_accesses']=events
(ROOT/'t03-final.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({**report,'file_accesses':len(events)},indent=2))
