from pathlib import Path
import subprocess,os,time,json,hashlib
t=Path(__file__).parent
p=t/'player-final'; o=t/'windows-start-final';o.mkdir(exist_ok=True)
env=os.environ.copy()
for key in ['APPDATA','LOCALAPPDATA','TEMP','TMP']:
 d=t/'temp/windows-start'/key;d.mkdir(parents=True,exist_ok=True);env[key]=str(d)
begin=time.monotonic()
with (o/'console.log').open('wb') as log:
 result=subprocess.run([str(p/'picross-p1.console.exe'),'--','--p1-smoke'],cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
text=(o/'console.log').read_text(errors='replace')
good=result.returncode==0 and 'P1_START_OK' in text and 'OpenGL' in text and 'ERROR:' not in text
data=dict(source_head='535403d8ac89c2da4800719f0d4a0fe0ba041950',artifact_id=13678883964,run_id=42627286101,command=['picross-p1.console.exe','--','--p1-smoke'],headless=False,exit_code=result.returncode,seconds=time.monotonic()-begin,passed=good,scope='Actual exported Windows native startup and regular catalog resource checks; no puzzle replay or OS pointer/DPI claim',files=[])
for name in ['picross-p1.exe','picross-p1.console.exe','picross-p1.pck','README.txt']:
 b=(p/name).read_bytes();data['files'].append(dict(path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(o/'report.json').write_text(json.dumps(data,indent=2)+'\n')
print(text);print(json.dumps(data))
raise SystemExit(0 if good else 1)
