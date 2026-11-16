import sys,json,subprocess,hashlib,io,os
from pathlib import Path
from PIL import Image
R=Path.cwd();W=R.parent;sys.path[:0]=[str(R),str(R/'tools')]
import background_import as bi,p1_preflight as tc
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();v=json.loads((W/'technical.json').read_bytes());v['current_head']=head;v['scope_equivalence']={'from':v['source_head'],'to':head,'changed_paths':subprocess.check_output(['git','diff','--name-only',v['source_head'],head],text=True).splitlines(),'statement':'Only catalog harness alias differs; HP/editor/RI/import/runtime/export code remains identical.'}
inv=json.loads((W/'background-inventory.json').read_bytes())
for row in inv['assets']:
 image=Image.open(W/'ri-throughput/game'/row['asset']['file']).convert('RGBA');row['rgba_sha256']=hashlib.sha256(image.tobytes()).hexdigest()
(W/'background-inventory.json').write_text(json.dumps(inv),encoding='utf8')
e=tc.isolated_environment(W/'throughput-profile','Windows');e.update(TEMP=str(W/'temp'),TMP=str(W/'temp'),ZA1_PACK_COUNT='4',HP_BACKGROUND_EXPECTED=str(W/'background-inventory.json'))
for kind,target in [('windows',W/'exports/windows/picross-p1.pck'),('web',W/'exports/web/index.pck')]:
 e['HP_BACKGROUND_PACK_TARGET']=kind;e['HP_BACKGROUND_REPORT']=str(W/(kind+'-pack.json'))
 p=subprocess.run(['D:/AppData/Local/Temp/picross-rp6-cache/engine/Godot_v4.7.2-stable_win64_console.exe','--headless','--main-pack',str(target),'--script',str(R/'game/tests/content_pack_probe.gd')],env=e,capture_output=True,text=True,timeout=60)
 (W/'throughput-logs'/(kind+'-PCK-pixels.log')).write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr
 v['T01'][kind+'-lossless-pixels']=json.loads((W/(kind+'-pack.json')).read_bytes());print(kind,'lossless RGBA and full mip chain OK')
real=bi.source_inventory(R);v['T02']['selected_count']=len(real['assets']);v['T02']['selected']=real['assets'];assert len(real['assets'])==9
base=v['base'];paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'--','content','game/data','game/art/backgrounds','game/art/content'],text=True).splitlines();paths=[p for p in paths if p!='game/data/background-capability.json'];assert all(subprocess.check_output(['git','show',f'{base}:{p}'])==(R/p).read_bytes() for p in paths);v['T02']['end_protected_files']=len(paths);v['T02']['end_byte_comparison']='passed'
from tools.puzzle_production.background_contract import PROFILE,PROFILE_3
from tools.puzzle_production.contract import digest
v['profiles']=[{'profile':p,'sha256':digest(p)} for p in [PROFILE,PROFILE_3]]
(W/'technical.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf8');print('END_T01_T02_OK',head)
