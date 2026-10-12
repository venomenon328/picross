from pathlib import Path
import hashlib, json, shutil, subprocess, sys
ROOT = Path(r'E:\Zeuch\Coding\picross-knoblauch-r03')
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT/'tools'))
import p1_preflight as tc
WORK = OUT/'runtime-test-v3'
WORK.mkdir(exist_ok=False)
CACHE = Path(r'D:\AppData\Local\Temp\picross-rp6-cache')
metadata = tc.request_json(tc.RELEASE_API)
tc.official_asset_urls(metadata, (tc.EDITORS['Windows'], tc.TEMPLATES))
for asset in (tc.EDITORS['Windows'], tc.TEMPLATES):
    tc.verify_sha256(CACHE/asset.name, asset.sha256)
engine = tc.extract_editor(CACHE/tc.EDITORS['Windows'].name,WORK/'engine','Windows')
tc.extract_windows_templates(CACHE/tc.TEMPLATES.name,tc.template_directory(WORK,'Windows'))
env = tc.isolated_environment(WORK,'Windows')
project = WORK/'game'
shutil.copytree(ROOT/'game',project,ignore=shutil.ignore_patterns('.godot','build'))
shutil.copyfile(OUT/'garlic_probe.gd',project/'tests/garlic_probe.gd')
saves = WORK/'saves'
env.update(P1_TEST_SAVE_ROOT=str(saves), GARLIC_OUTPUT=str(OUT/'native-v3'))
(OUT/'native-v3').mkdir()
results = []
def phase(name, command, marker=None, required=True):
    print('RUN',name,flush=True)
    r = tc.run_command(name,command,env,300)
    (OUT/('v3-'+name+'.log')).write_text(r['output'],encoding='utf-8')
    results.append({k:v for k,v in r.items() if k!='output'})
    (OUT/'native-phases-v3.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(r['output'][-2500:],flush=True)
    if required: tc.require_success(r,marker)
    return r
phase('import',[str(engine),'--headless','--path',str(project),'--import'])
command=[str(engine),'--path',str(project),'--rendering-driver','opengl3','--audio-driver','Dummy','--script','res://tests/garlic_probe.gd','--','--p1-capture']
for stage in ['seed','partial','finish','read','reset']:
    before={p.name:tc.sha256_file(p) for p in saves.glob('*') if p.is_file() and not p.name.startswith('knoblauch_001.')}
    env['GARLIC_STAGE']=stage
    phase('garlic-'+stage,command,'GARLIC_PROBE_OK')
    assert all((saves/n).is_file() and tc.sha256_file(saves/n)==h for n,h in before.items()), 'foreign save changed'
    (OUT/'native-v3'/('foreign-'+stage+'.json')).write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
build=project/'build/windows'; build.mkdir(parents=True)
phase('windows-export',[str(engine),'--headless','--path',str(project),'--export-debug','P1 Windows x86_64',str(build/'picross-p1.exe')])
env['ZA1_PACK_COUNT']='7'
phase('actual-pck',[str(engine),'--headless','--main-pack',str(build/'picross-p1.exe'),'--script',str(ROOT/'game/tests/content_pack_probe.gd')],'CONTENT_PACK_OK')
phase('exported-windows-start',[str(build/'picross-p1.console.exe'),'--headless','--','--p1-smoke'],'P1_START_OK')
print('NATIVE_GARLIC_SUCCESS',flush=True)
