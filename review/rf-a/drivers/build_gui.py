from pathlib import Path
import sys,subprocess,shutil,json,hashlib
w=Path(__file__).parent;r=w/'repo';sys.path[:0]=[str(r),str(r/'tools')]
import p1_preflight as tc
from product_fixtures import install_runtime_fixtures
from kat2_product import fixture
project=w/'gui-project';out=w/'gui-build';out.mkdir(exist_ok=True)
if not project.exists():shutil.copytree(w/'probe'/'game',project)
paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','game'],cwd=r,text=True).splitlines()
for name in paths:
    if Path(name).suffix in ['.gd','.tscn','.godot','.gdshader','.gdshaderinc']:
        target=project/Path(name).relative_to('game');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,target)
install_runtime_fixtures(r,project)
fixture(project,w/'gui-seed','pages')
def hints(line):
    result=[];prev=0
    for v in line:
        if v:
            if v==prev:result[-1]['length']+=1
            else:result.append(dict(length=1,color=v))
        prev=v
    return result
p=project/'data/kat2_001.json';data=json.loads(p.read_text())
data['solution']=[[int(y==1 and x in (1,2)) for x in range(20)] for y in range(20)]
data['rows']=[hints(row) for row in data['solution']]
data['columns']=[hints([row[x] for row in data['solution']]) for x in range(20)]
p.write_text(json.dumps(data)+'\n',encoding='utf-8')
env=tc.isolated_environment(w/'profile','Windows');env.pop('GITHUB_TOKEN',None)
env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'))
engine=w/'engine/Godot_v4.7.2-stable_win64_console.exe'
for label,args in [('import',['--import']),('export',['--export-debug','P1 Windows x86_64',str(out/'picross-p1.exe')])]:
    with (out/(label+'.log')).open('w') as log:
        result=subprocess.run([str(engine),'--headless','--path',str(project),*args],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    s=(out/(label+'.log')).read_text(encoding='utf-8');print(label,result.returncode,s[-600:],flush=True)
    assert result.returncode==0 and 'ERROR:' not in s
source={}
for name in paths:
    if Path(name).suffix in ['.gd','.tscn','.godot','.gdshader','.gdshaderinc'] and not any('/'+d+'/' in name for d in ['tests','study','full_view_study']):
        assert (r/name).read_bytes()==(project/Path(name).relative_to('game')).read_bytes(),name
        source[name]=tc.sha256_file(r/name)
manifest=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),sources=source,test_only=True,
              description='54 synthetic IDs; kat2_001 has two filled cells for actual pointer completion; all product code byte-identical',
              files={p.name:dict(bytes=p.stat().st_size,sha256=tc.sha256_file(p)) for p in out.iterdir() if p.suffix in ['.exe','.pck']})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
