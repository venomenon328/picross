from pathlib import Path
import sys,shutil,subprocess,json,uuid
w=Path(__file__).parent;project=w/'scratch'/'game'
sys.path.insert(0,str(w/'repo'));sys.path.insert(0,str(w/'repo'/'tools'))
import p1_preflight as tc,product_fixtures as f,kat2_product as k
for path in (w/'repo'/'game').rglob('*.gd'):
    shutil.copyfile(path,project/path.relative_to(w/'repo'/'game'))
tag=uuid.uuid4().hex; saves=w/'scratch'/('verify-saves-'+tag);saves.mkdir()
f.install_runtime_fixtures(w/'repo',project);k.fixture(project,saves,'pages')
env=tc.isolated_environment(w/'scratch'/('verify-profile-'+tag),'Windows')
env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'),P1_TEST_SAVE_ROOT=str(saves),KAT2_OUTPUT=str(w/'scratch'),KAT2_MODE='pages')
engine=w/'engine'/'Godot_v4.7.2-stable_win64_console.exe'
with (w/'compact-pages.log').open('wb') as log:
    r=subprocess.run([str(engine),'--path',str(project),'--rendering-driver','opengl3','--audio-driver','Dummy','--script','res://tests/kat2_probe.gd','--','--p1-capture'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
data=(w/'compact-pages.log').read_text(encoding='utf-8',errors='replace')
print(r.returncode,data[-4000:])
assert r.returncode==0 and 'ERROR:' not in data
from native_results import validate_catalog_cases
report=json.loads((w/'scratch'/'pages.json').read_text(encoding='utf-8'));validate_catalog_cases(report)
print('Independent pages checkpoint reader accepted',report['checks'])
