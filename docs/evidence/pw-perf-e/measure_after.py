import sys, json, time, platform, shutil
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parent
repo=root/'repo'
sys.path[:0]=[str(repo),str(repo/'tests/puzzle_production')]
from test_integrated_content import IntegratedContentTests
from tools.puzzle_production import catalog_io as io, integrated_content
IntegratedContentTests.setUpClass()
try:
 for warm in (False,True):
  t=IntegratedContentTests(); t.setUp()
  try:
   _,commit=t.prepare()
   counts={'read_calls':0,'read_bytes':0,'hash_calls':0,'hash_bytes':0,'paths':{}}
   read,checksum=io._read,io._checksum
   def measured(r,n,l,**kw):
    data=read(r,n,l,**kw); name=str((Path(r)/n).relative_to(t.checkout))
    counts['read_calls']+=1; counts['read_bytes']+=len(data or b'')
    counts['paths'][name]=counts['paths'].get(name,0)+len(data or b'')
    return data
   def hashed(raw):
    counts['hash_calls']+=1; counts['hash_bytes']+=len(raw or b''); return checksum(raw)
   start=time.perf_counter()
   with patch.object(io,'_read',measured),patch.object(io,'_checksum',hashed):
    result=integrated_content.retire(t.checkout,['pz-test-direct-mono'],commit)
   counts.update(seconds=time.perf_counter()-start,warm=warm,os=platform.platform(),python=sys.version,result=result)
   (root/('after-warm.json' if warm else 'after-first.json')).write_text(json.dumps(counts,indent=2),encoding='utf-8')
   print({k:v for k,v in counts.items() if k!='paths'},flush=True)
  finally: t.doCleanups()
finally: IntegratedContentTests.doClassCleanups()
