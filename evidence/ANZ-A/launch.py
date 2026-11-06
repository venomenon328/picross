from pathlib import Path
import subprocess,sys,shutil,json,time,os
w=Path(__file__).parent;r=w/'repo';sys.path.insert(0,str(r/'tools'));import p1_preflight as tc
out=w/os.environ.get('ANZ_GUI','gui');out.mkdir(exist_ok=True)
player=out/'player';player.mkdir(exist_ok=True)
for name in ['picross-p1.exe','picross-p1.pck']:
 target=player/name;source=w/'windows'/name
 if not target.exists():shutil.copyfile(source,target)
 tc.verify_sha256(target,tc.sha256_file(source))
shutil.copyfile(w/'observer.gd',player/'observer.gd')
(player/'override.cfg').write_text('[autoload]\nANZObserver="*'+(player/'observer.gd').as_posix()+'"\n')
env=tc.isolated_environment(out/'profile','Windows');env.update(ANZ_OBSERVATION=str(out),TEMP=str(w/'temp'),TMP=str(w/'temp'))
f=(out/'stdout.log').open('w');p=subprocess.Popen([str(player/'picross-p1.exe'),'--audio-driver','Dummy'],cwd=player,env=env,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
(out/'pid.txt').write_text(str(p.pid));print(p.pid)
