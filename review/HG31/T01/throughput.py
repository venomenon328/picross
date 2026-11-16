import sys, json, hashlib, subprocess, shutil, os, struct, time
from pathlib import Path
from PIL import Image, ImageDraw
R=Path.cwd(); W=R.parent; sys.path[:0]=[str(R),str(R/'tools')]
from tools.puzzle_production import background_assets as hp, background_contract as bc, editor_image_input as prepared, catalog_integration as ri, editor_change as editor
from tests.puzzle_production.background_fixtures import BackgroundFixture
from tests.puzzle_production.current_fixtures import checkout,make,approve,put,json_file,fingerprints
import background_import as imp
from product_fixtures import copy_regression_game
import p1_preflight as tc
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();base='ffa02800cc88ddee566d33e94826c187f347442d'
report={'source_head':head,'base':base,'environment':{'os':sys.platform,'python':sys.version,'pillow':__import__('PIL').__version__},'T01':{},'T02':{}}
def save(): (W/'technical.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
# T02 live source protection; only compact files and bytes, never puzzle replay.
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'--','content','game/data','game/art/backgrounds','game/art/content'],text=True).splitlines()
paths=[p for p in paths if p!='game/data/background-capability.json']
changed=[]
for p in paths:
 expected=subprocess.check_output(['git','show',f'{base}:{p}']); actual=(R/p).read_bytes()
 if expected!=actual:changed.append(p)
assert not changed, changed
report['T02']={'protected_files':len(paths),'changed':changed,'method':'git-object byte comparison of all content, runtime data, background and reveal assets; capability separately permitted; no real solver/analysis'};save()
cap=json.loads((R/'game/data/background-capability.json').read_bytes())
source=Image.new('RGBA',(600,200),(0,0,0,0));d=ImageDraw.Draw(source)
# Clearly synthetic full-canvas corner and contour markers, no production asset.
for box in [(1,1,130,80),(470,1,598,80),(1,120,130,198),(470,120,598,198)]:d.rounded_rectangle(box,radius=15,outline=(65,65,65,190),width=5)
d.line([(2,198),(150,135),(300,185),(450,135),(598,198)],fill=(85,85,85,140),width=5)
f=BackgroundFixture(W/'hp-throughput',hp.describe(profile_id=bc.PROFILE_3['id']),image=source)
a=hp.derive(f.request,f.source,f.output);assert a['status']=='derived',a
raw=(f.target/'background.png').read_bytes();assert prepared.validate_background(raw)['profile']=='picross-prepared-background-png2304x768-v1'
assert hp.verify(f.request,f.source,f.target)['status']=='verified'
stamp=(f.target/'background.png').stat().st_mtime_ns;assert hp.derive(f.request,f.source,f.output)['status']=='reused';assert (f.target/'background.png').stat().st_mtime_ns==stamp
root=checkout(W/'ri-throughput');json_file(root,'game/data/background-capability.json',cap)
for key,status in [('new','selected'),('legacy','selected'),('standard','standard'),('none','none')]:
 s=make(W/('input-'+key),identifier='pz-hg31-'+key,background=status)
 if key=='new':
  v=json.loads((s/'manifest.json').read_bytes());v['background']['image']['asset']=put(s,'background.png',raw);approve(s,v)
 assert ri.integrate(s,root)['status']=='planned'
 assert ri.integrate(s,root,apply=True)['status']=='registered'
 before=fingerprints(root);assert ri.integrate(s,root,apply=True)['status']=='no-op';assert fingerprints(root)==before
# Separate current editor input follows an already registered standard entry.
eroot=checkout(W/'editor-throughput');json_file(eroot,'game/data/background-capability.json',cap)
s=make(W/'editor-initial',identifier='pz-hg31-editor');ri.integrate(s,eroot,apply=True)
req={'id':'pz-hg31-editor','metadata':None,'text':None,'profile':None,'reveal':None,'background':{'status':'selected','upload':'background'}}
uploads={'background':{'raw':raw,'suffix':'png','checked':prepared.validate_background(raw)}}
plan=editor.plan(eroot,req,uploads=uploads);editor.apply(eroot,plan)
assert (eroot/'game/art/backgrounds/pz-hg31-editor.png').read_bytes()==raw
before=fingerprints(eroot);assert editor.apply(eroot,editor.plan(eroot,req,uploads=uploads))['status']=='noop';assert before==fingerprints(eroot)
report['T01']['consumer_paths']={'hp_derive_verify_reuse':True,'prepared':True,'current_editor_plan_apply_readback_noop':True,'separate_RI_plan_apply_readback_noop':True,'cases':['selected 2304x768','selected 2304x576','standard','none'],'new_source_png_sha256':sha((f.source/f.request['source']['file']).read_bytes()),'new_prepared_png_sha256':sha(raw)};save()
project=W/'throughput-game';copy_regression_game(R,project)
# Replace only synthetic runtime namespaces with synthetic current RI output.
for n in ['data','art/content','art/backgrounds']:
 p=project/n
 if p.exists():shutil.rmtree(p)
 if (root/'game'/n).exists():shutil.copytree(root/'game'/n,p)
inventory=imp.source_inventory(root);imp.prepare_import(project,inventory)
profile=W/'throughput-profile';env=tc.isolated_environment(profile,'Windows');env['TEMP']=str(W/'temp');env['TMP']=env['TEMP'];env['ZA1_PACK_COUNT']='4'
templates=tc.template_directory(profile,'Windows');templates.mkdir(parents=True)
old=Path('E:/Zeuch/Coding/picross_codex/558-rz-eval-p1/measurements-verified/profile/roaming/Godot/export_templates/4.7.2.stable')
report['environment']['templates']={}
for name in ['version.txt','windows_debug_x86_64.exe','windows_debug_x86_64_console.exe','web_nothreads_debug.zip']:
 shutil.copyfile(old/name,templates/name);report['environment']['templates'][name]=sha((templates/name).read_bytes())
engine=Path('D:/AppData/Local/Temp/picross-rp6-cache/engine/Godot_v4.7.2-stable_win64_console.exe')
(W/'exports/windows').mkdir(parents=True);(W/'exports/web').mkdir(parents=True)
(W/'background-inventory.json').write_text(json.dumps(inventory),encoding='utf8');env['HP_BACKGROUND_EXPECTED']=str(W/'background-inventory.json')
logs=W/'throughput-logs';logs.mkdir()
def run(label,args):
 t=time.monotonic();p=subprocess.run([str(engine),*args],env=env,capture_output=True,text=True,timeout=240);out=p.stdout+p.stderr;(logs/(label+'.log')).write_text(out,encoding='utf8');print(label,p.returncode,out[-1200:],flush=True)
 report['T01'][label]={'exit':p.returncode,'seconds':round(time.monotonic()-t,3)};save();assert p.returncode==0 and 'SCRIPT ERROR' not in out and 'ERROR:' not in out,out
run('engine-import',['--headless','--editor','--path',str(project),'--import'])
report['T01']['actual_import']=imp.verify_import(project,inventory);save()
for kind,preset,target in [('windows','P1 Windows x86_64',W/'exports/windows/picross-p1.exe'),('web','P1 Web',W/'exports/web/index.html')]:
 run(kind+'-export',['--headless','--path',str(project),'--export-debug',preset,str(target)])
 run(kind+'-PCK',['--headless','--main-pack',str(target.with_suffix('.pck')),'--script',str(R/'game/tests/content_pack_probe.gd')])
report['T01']['files']={p.relative_to(W).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in (W/'exports').rglob('*') if p.is_file()};save()
print('HG31_T01_T02_OK',flush=True)
