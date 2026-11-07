from pathlib import Path
import sys,subprocess,shutil,os
w=Path(__file__).parent;sys.path.insert(0,str(w/'repo/tools'))
import p1_preflight as tc
out=w/os.environ.get('KA_GUI','gui');out.mkdir(exist_ok=True)
player=w/'gui-build'
(player/'override.cfg').write_text('[autoload]\nKBObserver="*'+(w/'observer.gd').as_posix()+'"\n',encoding='utf-8')
profile=out/'profile';saves=profile/'appdata/Godot/app_userdata/picross · P1/p1/saves'
if not saves.exists():shutil.copytree(w/'gui-seed',saves)
env=tc.isolated_environment(profile,'Windows');env.pop('GITHUB_TOKEN',None)
env.update(KA_OBSERVATION=str(out),TEMP=str(w/'temp'),TMP=str(w/'temp'))
p=subprocess.Popen([str(player/'picross-p1.exe'),'--audio-driver','Dummy','--resolution','1920x1080','--position','20,20'],cwd=player,env=env,stdout=(out/'stdout.log').open('w'),stderr=(out/'stderr.log').open('w'),creationflags=subprocess.CREATE_NO_WINDOW)
(out/'pid.txt').write_text(str(p.pid));print(p.pid)
