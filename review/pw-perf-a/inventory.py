import collections,json,re,subprocess,time
from pathlib import Path
ROOT=Path(__file__).parent/'repo'
def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT)
rows={}
for row in git('ls-tree','-rlz','HEAD').split(b'\0'):
    if row:
        meta,name=row.split(b'\t'); mode,typ,oid,size=meta.decode().split()
        rows[name.decode()]={'mode':mode,'oid':oid,'bytes':int(size)}
def data(name): return json.loads((ROOT/name).read_bytes())
registry=data('content/registry.json')
packages=[]
for name in rows:
    if name.startswith('content/packages/') and name.endswith('/manifest.json'):
        m=data(name); prefix=name.rsplit('/',1)[0]+'/'
        members={n:v for n,v in rows.items() if n.startswith(prefix)}
        packages.append({'path':name,'format':m['format'],'files':len(members),'bytes':sum(v['bytes'] for v in members.values()),'active':any(e['production']['package']+'/'==prefix for e in registry['entries']),'zip_bytes':sum(v['bytes'] for n,v in members.items() if n.endswith('.zip'))})
result={'head':git('rev-parse','HEAD').decode().strip(),'registry':registry['format'],'runtime':data('game/data/registry.json')['format'],'entries':len(registry['entries']),'package_forms':dict(collections.Counter(p['format'] for p in packages)),'packages':packages,'sources':{},'authoring':data('content/authoring/index.json')}
for directory in ['content/reveals/','content/backgrounds/']:
    result['sources'][directory]=dict(collections.Counter(data(n)['format'] for n in rows if n.startswith(directory) and n.endswith('.json')))
result['zip_tree']=[{'path':n,**v} for n,v in rows.items() if n.startswith('content/') and n.endswith('.zip')]
result['doc_sizes']={n:rows[n]['bytes'] for n in ['AGENTS.md','README.md','docs/PROJECT_PROFILE.md','docs/PRODUCTION_WORKSPACE.md','docs/ai-workflows/PUZZLE_AUTHORING.md','docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md','docs/PUZZLE_QUALITY.md','docs/PUZZLE_BACKGROUNDS.md','docs/ZA1_ADAPTER.md','tools/puzzle_production/README.md','docs/workflow/Puzzle_Authoring_Cheat-Sheet.html'] if n in rows}
print(json.dumps(result,ensure_ascii=False,indent=2))
(Path(__file__).parent/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
