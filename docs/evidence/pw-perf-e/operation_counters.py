import sys,json
from pathlib import Path
from unittest.mock import patch
import zipfile
home=Path(__file__).resolve().parent;repo=home/'repo'
sys.path[:0]=[str(repo),str(repo/'tests/puzzle_production')]
from test_retirement_current import CurrentRetirementTests
from tools.puzzle_production import integrated_content as retirement, target_adapter, verifier
from PIL import Image
original=retirement.retire;open_zip=zipfile.ZipFile;rows=[]
def observed(*args,**kwargs):
 row={'zip_metadata_opens':0,'production_replays':0,'solver_replays':0,'image_decodes':0}
 def zip_open(*a,**kw):row['zip_metadata_opens']+=1;return open_zip(*a,**kw)
 def forbidden(kind):
  def called(*a,**kw):row[kind]+=1;raise AssertionError('Forbidden retirement work: '+kind)
  return called
 try:
  with patch.object(zipfile,'ZipFile',zip_open),patch.object(target_adapter,'verify_export',forbidden('production_replays')),patch.object(verifier,'verify',forbidden('solver_replays')),patch.object(Image,'open',forbidden('image_decodes')):
   result=original(*args,**kwargs)
  row['result']=result['status'];return result
 except Exception as exc:row['error']=str(exc);raise
 finally:rows.append(row)
CurrentRetirementTests.setUpClass()
try:
 case=CurrentRetirementTests();case.setUp()
 try:
  with patch.object(retirement,'retire',observed):case.test_v6_original_rights_and_distinct_import_source()
 finally:case.doCleanups()
finally:CurrentRetirementTests.doClassCleanups()
assert rows[-1]['result']=='production_retired' and rows[-1]['zip_metadata_opens']==1
assert all(row[k]==0 for row in rows for k in ('production_replays','solver_replays','image_decodes'))
(home/'operation-counters.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
