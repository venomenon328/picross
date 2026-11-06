from pathlib import Path
import sys, subprocess, shutil, os, json, tempfile
w = Path(__file__).parent
r = w.parent/'527-anz-a/repo'
sys.path[:0] = [str(r/'tools'), str(r)]
import p1_preflight as tc
from product_fixtures import copy_regression_game
for asset in (tc.EDITORS['Windows'], tc.TEMPLATES):
    tc.verify_sha256(w.parent/'527-anz-a/cache'/asset.name, asset.sha256)
engine = w.parent/'527-anz-n02/engine/Godot_v4.7.2-stable_win64_console.exe'
assert engine.exists()
project = w/'probe/game'
if not project.exists(): copy_regression_game(r, project)
for folder in ['model','ui','book','tests']:
    for src in (r/'game'/folder).glob('*.gd'):
        shutil.copyfile(src, project/folder/src.name)
for name in ['project.godot','main.tscn','export_presets.cfg']:
    shutil.copyfile(r/'game'/name, project/name)
(w/'probe/output').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='information-', dir=w/'temp') as scratch:
    scratch=Path(scratch)
    env=tc.isolated_environment(scratch/'profile','Windows')
    env.update(TEMP=str(scratch),TMP=str(scratch),P1_TEST_SAVE_ROOT=str(scratch/'saves'),KAT2_OUTPUT=str(w/'probe/output'),KAT2_MODE='information')
    Path(env['P1_TEST_SAVE_ROOT']).mkdir()
    for label, extra in [('import',['--import']),('information',['--script','res://tests/kat2_probe.gd','--','--p1-capture'])]:
        result=subprocess.run([str(engine),'--headless','--path',str(project)]+extra,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        (w/'logs'/(label+'.log')).write_bytes(result.stdout)
        print(label,result.returncode,result.stdout.decode(errors='replace')[-1200:],flush=True)
        assert result.returncode==0 and b'SCRIPT ERROR' not in result.stdout and b'ERROR:' not in result.stdout
    report=json.loads((w/'probe/output/information.json').read_text())
    print(json.dumps(report),flush=True)
    assert not report['failures']
