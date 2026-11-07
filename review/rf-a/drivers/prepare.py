from pathlib import Path
import sys,subprocess,shutil
w=Path(__file__).parent;r=w/'repo';sys.path.insert(0,str(r/'tools'))
sys.path.insert(0,str(r))
import p1_preflight as tc
from product_fixtures import install_runtime_fixtures
from kat2_product import fixture
cache=w/'cache';cache.mkdir(exist_ok=True)
for a in [tc.EDITORS['Windows'],tc.TEMPLATES]:
    p=cache/a.name
    if not p.exists():shutil.copyfile(w.parent/'485-k-b-b01'/'cache'/a.name,p)
    tc.verify_sha256(p,a.sha256)
if not (w/'engine').exists():tc.extract_editor(cache/tc.EDITORS['Windows'].name,w/'engine','Windows')
profile=w/'profile'
if not tc.template_directory(profile,'Windows').exists():tc.extract_windows_templates(cache/tc.TEMPLATES.name,tc.template_directory(profile,'Windows'))
project=w/'probe'/'game';project.mkdir(parents=True,exist_ok=True)
paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','game'],cwd=r,text=True).splitlines()
for name in paths:
    target=project/Path(name).relative_to('game');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,target)
install_runtime_fixtures(r,project)
saves=w/'probe'/'saves';saves.mkdir(exist_ok=True)
if not (w/'probe'/'prepared').exists():
    fixture(project,saves,'pages');(w/'probe'/'prepared').touch()
else:fixture(project,w/'unused-saves','pages')
env=tc.isolated_environment(profile,'Windows');env.pop('GITHUB_TOKEN',None)
(w/'temp').mkdir(exist_ok=True);env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'))
with (w/'import.log').open('w') as f:
    result=subprocess.run([str(w/'engine'/'Godot_v4.7.2-stable_win64_console.exe'),'--headless','--path',str(project),'--import'],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
print((w/'import.log').read_text(encoding='utf-8')[-7000:]);assert result.returncode==0
