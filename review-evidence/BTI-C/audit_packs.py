from pathlib import Path
import sys,os,json,subprocess,shutil
w=Path(__file__).parent;r=w/'repo';sys.path.insert(0,str(r/'tools'))
import p1_preflight as tc
from p1_product import run_phase,require_clean_output
env=tc.isolated_environment(w/'audit-profile','Windows');env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'),BTI_SOURCE=str(r))
engine=next((w/'engine').glob('*console.exe'))
for kind in ['windows','web','regular-web']:
 pack=next((w/'regular-web').rglob('*.pck')) if kind=='regular-web' else next((w/'exports'/kind).glob('*.pck'))
 env.update(BTI_PACK=kind,BTI_PCK_REPORT=str(w/'evidence'/f'pck-{kind}.json'))
 result=run_phase('title-pck-'+kind,[str(engine),'--headless','--main-pack',str(pack),'--script',str(w/'pck_probe.gd')],env,120,w/'logs');require_clean_output(result,'BTI_PCK_OK')
print('Actual PCKs: title/NOTICE/manifest/provenance verified. Regular delivery extras checked separately.')
