from pathlib import Path
import sys,os,subprocess,json,shutil
w=Path(__file__).parent;r=w.parent/'527-anz-a/repo';sys.path[:0]=[str(r/'tools'),str(r)]
import p1_preflight as tc
project=w/'probe/game'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=r,text=True).strip()
for folder in ['model','ui','book','tests']:
 for src in (r/'game'/folder).glob('*.gd'):shutil.copyfile(src,project/folder/src.name)
for name in ['project.godot','main.tscn','export_presets.cfg']:shutil.copyfile(r/'game'/name,project/name)
tc.extract_windows_templates(w.parent/'527-anz-a/cache'/tc.TEMPLATES.name,tc.template_directory(w/'export-profile','Windows'))
env=tc.isolated_environment(w/'export-profile','Windows');env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'))
out=w/'windows';out.mkdir(exist_ok=True)
engine=w.parent/'527-anz-n02/engine/Godot_v4.7.2-stable_win64_console.exe'
imported=subprocess.run([str(engine),'--headless','--path',str(project),'--import'],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
assert imported.returncode==0 and b'SCRIPT ERROR' not in imported.stdout
command=[str(engine),'--headless','--path',str(project),'--export-debug','P1 Windows x86_64',str(out/'picross-p1.exe')]
result=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
(w/'logs/export.log').write_bytes(result.stdout)
print(result.returncode,result.stdout.decode(errors='replace')[-1500:])
assert result.returncode==0 and b'SCRIPT ERROR' not in result.stdout and b'ERROR:' not in result.stdout
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
files={p.name:{'bytes':p.stat().st_size,'sha256':tc.sha256_file(p)} for p in out.glob('*') if p.is_file()}
(w/'export.json').write_text(json.dumps(dict(source_head=head,synthetic_catalog=True,source_code={p.relative_to(r/'game').as_posix():tc.sha256_file(p) for p in (r/'game').rglob('*.gd')},engine=tc.EXPECTED_VERSION,files=files),indent=2)+'\n')
