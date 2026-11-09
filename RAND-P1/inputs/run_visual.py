from pathlib import Path
import sys,os,subprocess,shutil,json
base=Path(__file__).resolve().parent;root=base/'repo'
sys.path[:0]=[str(root),str(root/'tools')]
import p1_preflight as tc
from kat2_product import fixture
project=base/'probe/game';work=base/'probe'
# Each exploratory run starts from known synthetic bytes, never previous saves.
save_root=work/'saves'
for path in save_root.glob('*'):
    if path.is_file(): path.unlink()
fixture(project,save_root,'pages')
shutil.copyfile(base/'rand_visual.gd',project/'tests/rand_visual.gd')
shutil.copyfile(base/'rand_extra.gd',project/'tests/rand_extra.gd')
registry=json.loads((project/'data/registry.json').read_text(encoding='utf-8'))
registry['categories']=json.loads((root/'content/categories.json').read_text(encoding='utf-8'))['categories']
registry['entries'][1]['category_id']='wasserwelt'
registry['entries'][3]['category_id']='landschaften-natur'
large=json.loads((project/'data/fixtures/t06.json').read_text(encoding='utf-8'))
entry=registry['entries'][53]
large['id']=entry['id'];large['reveal']['definition_id']=entry['id'];large['reveal']['image']='res://'+entry['reveal']
(project/entry['definition']).write_text(json.dumps(large)+'\n',encoding='utf-8')
entry['category_id']='landschaften-natur'
if os.environ.get('RAND_SCRIPT') == 'rand_extra':
    rectangle=json.loads((project/'data/fixtures/t01.json').read_text(encoding='utf-8'))
    entry=registry['entries'][51]
    rectangle.update(id=entry['id'],width=40,height=30)
    rectangle['reveal'].update(definition_id=entry['id'],image='res://'+entry['reveal'])
    rectangle['solution']=[[int(0<x<39 and 0<y<29) for x in range(40)] for y in range(30)]
    rectangle['rows']=[([dict(length=38,color=1)] if 0<y<29 else []) for y in range(30)]
    rectangle['columns']=[([dict(length=28,color=1)] if 0<x<39 else []) for x in range(40)]
    (project/entry['definition']).write_text(json.dumps(rectangle)+'\n',encoding='utf-8')
    entry['category_id']='wasserwelt'
(project/'data/registry.json').write_text(json.dumps(registry)+'\n',encoding='utf-8')
env=tc.isolated_environment(work,'Windows')
env.update(TEMP=str(base/'temp'),TMP=str(base/'temp'),P1_TEST_SAVE_ROOT=str(work/'saves'),RAND_VISUAL_OUTPUT=str(base/os.environ.get('RAND_OUTPUT','originals-dev')),RAND_PRODUCT_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip())
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
engine=base/'engine/Godot_v4.7.2-stable_win64_console.exe'
log=base/('visual-extra.log' if os.environ.get('RAND_SCRIPT') else 'visual.log')
with log.open('w',encoding='utf-8') as out:
    result=subprocess.run([str(engine),'--path',str(project),'--audio-driver','Dummy','--rendering-driver','opengl3','--script','res://tests/'+os.environ.get('RAND_SCRIPT','rand_visual')+'.gd','--','--p1-capture'],env=env,stdout=out,stderr=subprocess.STDOUT,startupinfo=startup,timeout=300)
print('native visual',result.returncode,flush=True)
print(log.read_text(encoding='utf-8')[-6500:])
sys.exit(result.returncode)
