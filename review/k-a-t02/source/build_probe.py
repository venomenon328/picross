from pathlib import Path
import sys, subprocess, shutil, json
w=Path(__file__).parent
sys.path.insert(0,str(w/'repo'/'tools'))
import p1_preflight as tc
out=w/'build-compact-row';out.mkdir()
project=w/'gui'/'game'
for name in subprocess.check_output(['git','ls-files','game'],cwd=w/'repo',text=True).splitlines():
    if name.endswith(('.gd','.tscn','.godot','.gdshader','.gdshaderinc')):
        shutil.copyfile(w/'repo'/name,project/Path(name).relative_to('game'))
engine=w/'engine'/'Godot_v4.7.2-stable_win64_console.exe'
env=tc.isolated_environment(w/'build-profile','Windows')
env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'))
(out/'windows').mkdir()
for label,args in [('import',['--import']),('export',['--export-debug','P1 Windows x86_64',str(out/'windows'/'picross-p1.exe')])]:
    with (out/(label+'.log')).open('wb') as log:
        r=subprocess.run([str(engine),'--headless','--path',str(project),*args],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    data=(out/(label+'.log')).read_text(encoding='utf-8',errors='replace')
    print(label,r.returncode,flush=True)
    assert r.returncode==0 and 'ERROR:' not in data,(label,data[-3000:])
source={}
for name in subprocess.check_output(['git','ls-files','game'],cwd=w/'repo',text=True).splitlines():
    if name.endswith(('.gd','.tscn','.godot','.gdshader','.gdshaderinc')) and not any('/'+p+'/' in name for p in ['tests','study','full_view_study']):
        p=w/'repo'/name;q=project/Path(name).relative_to('game')
        assert p.read_bytes()==q.read_bytes(),name
        source[name]=tc.sha256_file(p)
manifest=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w/'repo',text=True).strip(),base='ec2188b5da7b3f24a070592b6fbe7b8003c73cc1',purpose='K-A-T02: 54 isolated synthetic puzzles; exact product code; not the regular player catalog',sources=source,files={p.name:{'bytes':p.stat().st_size,'sha256':tc.sha256_file(p)} for p in (out/'windows').iterdir() if p.is_file()},archives={a.name:a.sha256 for a in [tc.EDITORS['Windows'],tc.TEMPLATES]})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(manifest['head'],manifest['files'],flush=True)
