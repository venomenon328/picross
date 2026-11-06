from pathlib import Path
import sys,os,json,subprocess,hashlib,time
w=Path(__file__).parent;r=w/'repo';sys.path.insert(0,str(r/'tools'))
import p1_preflight as tc
from p1_product import player_extras,run_phase,require_clean_output
player=w/'ci-player'
for name,source in player_extras(r,w).items():
 if name.startswith('licenses/'):
  assert (player/name).read_bytes()==source.read_bytes(),name
assert '031565d941a60df5643adef561926d5721285322' in (player/'README.txt').read_text(encoding='utf-8')
env=tc.isolated_environment(w/'ci-start-profile','Windows');env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'),BTI_SOURCE=str(r),BTI_PACK='regular-ci-windows',BTI_PCK_REPORT=str(w/'evidence/pck-regular-ci-windows.json'))
engine=next((w/'engine').glob('*console.exe'))
result=run_phase('regular-ci-windows-pck',[str(engine),'--headless','--main-pack',str(player/'picross-p1.pck'),'--script',str(w/'pck_probe.gd')],env,120,w/'logs');require_clean_output(result,'BTI_PCK_OK')
started=time.monotonic()
result=run_phase('actual-ci-windows-start',[str(player/'picross-p1.exe'),'--audio-driver','Dummy','--','--p1-smoke'],env,60,w/'logs');require_clean_output(result,'P1_START_OK')
report=dict(source_head='031565d941a60df5643adef561926d5721285322',artifact_id=13548169497,run_id=42310751535,attempt=1,platform='Windows',native_window=True,external_observer=False,smoke_exit=result['exit_code'],seconds=time.monotonic()-started,files={p.relative_to(player).as_posix():dict(bytes=p.stat().st_size,sha256=tc.sha256_file(p)) for p in player.rglob('*') if p.is_file()},packaged_licenses_equal=True,pck_report='pck-regular-ci-windows.json')
(w/'ci-player-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Actual downloaded CI Windows player started cleanly; source-bound licences and PCK confirmed')
