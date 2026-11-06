from pathlib import Path
import sys,os,subprocess
w=Path('E:/Zeuch/Coding/picross_codex/527-anz-n02');sys.path.insert(0,str(w.parent/'527-anz-a/repo/tools'));import p1_preflight as tc
env=tc.isolated_environment(w/'core-profile','Windows');env.update(P1_TEST_SAVE_ROOT=str(w/'core-saves'),TEMP=str(w/'temp'),TMP=str(w/'temp'))
with (w/'logs/core.log').open('wb') as log:
 p=subprocess.run([str(w/'engine/Godot_v4.7.2-stable_win64_console.exe'),'--headless','--path',str(w/'probe/game'),'--script','res://tests/n02_core.gd','--','--p1-capture'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
print(p.returncode,(w/'logs/core.log').read_text(encoding='utf-8')[-3500:])
