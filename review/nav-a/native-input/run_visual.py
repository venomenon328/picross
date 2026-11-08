from pathlib import Path
import os, sys, subprocess, shutil, hashlib, json
root=Path.cwd();base=root.parent
sys.path[:0]=[str(root),str(root/'tools')]
import p1_preflight as tc
from product_fixtures import copy_regression_game
from kat2_product import fixture
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
tc.verify_sha256(base/'cache'/tc.EDITORS['Windows'].name,tc.EDITORS['Windows'].sha256)
engine=tc.extract_editor(base/'cache'/tc.EDITORS['Windows'].name,base/'engine','Windows')
work=base/'visual-final2';project=work/'game'
fresh=not project.exists()
if fresh: copy_regression_game(root,project)
saves=work/'saves';saves.mkdir(exist_ok=True)
if fresh: fixture(project,saves,'pages')
shutil.copyfile(base/'nav_visual.gd',project/'tests/nav_visual.gd')
originals=base/'originals-final2';originals.mkdir(exist_ok=True)
env=tc.isolated_environment(work,'Windows')
env.update(P1_TEST_SAVE_ROOT=str(saves),NAV_VISUAL_OUTPUT=str(originals),NAV_PRODUCT_HEAD=head)
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
for name,args in [('import',['--headless','--import']),('visual',['--rendering-driver','opengl3','--script','res://tests/nav_visual.gd'])]:
 if name=='import' and not fresh:continue
 with (base/(name+'-final2-bound.log')).open('w',encoding='utf-8') as out:
  result=subprocess.run([str(engine),'--path',str(project),'--audio-driver','Dummy',*args],env=env,stdout=out,stderr=subprocess.STDOUT,startupinfo=startup,timeout=300)
 print(name,result.returncode,flush=True)
 if result.returncode:sys.exit(result.returncode)
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
print("Native window probe complete at "+head,flush=True)
