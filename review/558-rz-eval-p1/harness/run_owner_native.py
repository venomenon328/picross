from pathlib import Path
import subprocess,os,json,time
r=Path(__file__).parent
engine=r'E:\Zeuch\Coding\Parkey-Tools\Godot-4.7.2\Godot_v4.7.2-stable_win64_console.exe'
results=[]
for label,script in [('owner-book','rz_probe.gd'),('owner-diagnostics','rz_diagnostics.gd'),('owner-mono','rz_mono.gd'),('owner-resources','rz_resources.gd')]:
 env=os.environ.copy()
 for key in ['APPDATA','LOCALAPPDATA','TEMP','TMP']:
  d=r/'temp'/label/key;d.mkdir(parents=True,exist_ok=True);env[key]=str(d)
 out=r/label;out.mkdir()
 env.update(RZ_OUTPUT=str(out),RZ_FULL='1',RZ_ONLY='')
 start=time.monotonic()
 with (out/'console.log').open('wb') as log:
  c=subprocess.run([engine,'--path',str(r/'repo/game'),'--rendering-driver','opengl3','--audio-driver','Dummy','--script',str(r/'temp'/script)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
 data=json.loads((out/'report.json').read_text());text=(out/'console.log').read_text(errors='replace')
 assert c.returncode==0 and not data['failures'] and 'ERROR:' not in text,(label,text[-2000:])
 results.append(dict(label=label,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r/'repo',text=True).strip(),seconds=time.monotonic()-start,exit_code=c.returncode,failures=data['failures']))
 print(json.dumps(results[-1]),flush=True)
(r/'owner-native-runs.json').write_text(json.dumps(results,indent=2)+'\n')
