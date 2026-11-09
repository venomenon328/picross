from pathlib import Path
from PIL import Image
import os,re,shutil,subprocess,time,json
r=Path(__file__).parent;p=r/'render-owner-comparison/game';a=p/'art/drawing/rz_eval'
shutil.copyfile(r/'repo/game/book/rz_eval.gd',p/'book/rz_eval.gd')
image=Image.open(a/'petronas-3-2304.png').convert('RGBA')
image.save(a/'petronas-3-2304.q85.webp',quality=85,method=6)
image.convert('LA').save(a/'petronas-3-2304.la.png',optimize=True)
image.save(a/'petronas-3-2304.nomips.png',optimize=True)
template=(r/'repo/game/art/drawing/rz_eval/qualle-1-2304.png.import').read_text()
for f in a.glob('petronas-3-2304.*.*'):
 if f.suffix not in ['.png','.webp']:continue
 text=template.replace('qualle-1-2304.png',f.name)
 text=re.sub(r'^(path|dest_files|uid)=.*\n','',text,flags=re.M)
 if '.nomips.' in f.name:text=text.replace('mipmaps/generate=true','mipmaps/generate=false')
 (a/(f.name+'.import')).write_text(text,newline='\n')
probe=r/'temp/rz_profiles.gd';text=probe.read_text().replace('\t\tfor entry: Array in','\t\tif not OS.get_environment("RZ_ONLY").is_empty() and Drawing.PILOTS[id] != OS.get_environment("RZ_ONLY"): continue\n\t\tfor entry: Array in')
target=r/'temp/rz_selected_profiles.gd';target.write_text(text,newline='\n')
env=os.environ.copy()
for key in ['APPDATA','LOCALAPPDATA','TEMP','TMP']:
 d=r/'temp/selected-profiles'/key;d.mkdir(parents=True,exist_ok=True);env[key]=str(d)
out=r/'owner-selected-profiles';out.mkdir()
env.update(RZ_OUTPUT=str(out),RZ_ONLY='petronas')
engine=r'E:\Zeuch\Coding\Parkey-Tools\Godot-4.7.2\Godot_v4.7.2-stable_win64_console.exe'
for label,args in [('import',['--headless','--path',str(p),'--import']),('native',['--path',str(p),'--rendering-driver','opengl3','--audio-driver','Dummy','--script',str(target)])]:
 with (out/(label+'.log')).open('wb') as log:
  start=time.monotonic();c=subprocess.run([engine]+args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
  assert c.returncode==0 and 'ERROR:' not in (out/(label+'.log')).read_text(errors='replace')
  print(label,round(time.monotonic()-start,3),flush=True)
assert not json.loads((out/'report.json').read_text())['failures']
