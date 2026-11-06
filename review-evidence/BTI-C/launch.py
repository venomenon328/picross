from pathlib import Path
import subprocess,os,sys,shutil,json
w=Path(__file__).parent;r=w/'repo';sys.path.insert(0,str(r/'tools'))
import p1_preflight as tc
out=w/os.environ.get('BTI_GUI','gui');out.mkdir(exist_ok=True)
player=out/'player';player.mkdir(exist_ok=True)
for name in ['picross-p1.exe','picross-p1.pck']:shutil.copyfile(w/'exports/windows'/name,player/name)
shutil.copyfile(w/'observer.gd',player/'observer.gd')
(player/'override.cfg').write_text('[autoload]\nBTIObserver="*'+(player/'observer.gd').as_posix()+'"\n',encoding='utf-8')
env=tc.isolated_environment(out/'profile','Windows');env.update(BTI_OBSERVATION=str(out),TEMP=str(w/'temp'),TMP=str(w/'temp'))
p=subprocess.Popen([str(player/'picross-p1.exe'),'--audio-driver','Dummy','--resolution','1920x1080','--position','0,0'],cwd=player,env=env,stdout=(out/'stdout.log').open('w'),stderr=(out/'stderr.log').open('w'),creationflags=subprocess.CREATE_NO_WINDOW)
(out/'pid.txt').write_text(str(p.pid));print(p.pid)
