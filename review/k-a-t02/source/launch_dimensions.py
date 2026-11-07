from pathlib import Path
import sys,subprocess,shutil,json
w=Path(__file__).parent
sys.path.insert(0,str(w/'repo'/'tools'))
import p1_preflight as tc
out=w/'gui-delivery';out.mkdir()
player=w/'build-delivery'/'windows'
(player/'override.cfg').write_text('[autoload]\nKAObserver="*'+(w/'observer.gd').as_posix()+'"\n',encoding='utf-8')
profile=out/'profile'
saves=profile/'appdata'/'Godot'/'app_userdata'/'picross · P1'/'p1'/'saves'
saves.mkdir(parents=True)
for p in (w/'gui'/'saves').iterdir():
    if p.is_file():shutil.copyfile(p,saves/p.name)
(saves/'kat2_005.json').write_text('{invalid',encoding='utf-8')
shutil.copyfile(saves/'kat2_000.json',saves/'kat2_000.bak')
(saves/'kat2_000.json').write_text('{invalid',encoding='utf-8')
env=tc.isolated_environment(profile,'Windows')
env.update(KA_OBSERVATION=str(out),TEMP=str(w/'temp'),TMP=str(w/'temp'))
env.pop('GITHUB_TOKEN',None)
p=subprocess.Popen([str(player/'picross-p1.exe'),'--audio-driver','Dummy','--resolution','1920x1080','--position','20,20'],cwd=player,env=env,stdout=(out/'stdout.log').open('w'),stderr=(out/'stderr.log').open('w'),creationflags=subprocess.CREATE_NO_WINDOW)
(out/'pid.txt').write_text(str(p.pid))
print(p.pid)
