import sys,json,unittest
from pathlib import Path
from unittest.mock import patch
home=Path(__file__).resolve().parent;repo=home/'repo'
sys.path[:0]=[str(repo),str(repo/'tests/puzzle_production')]
from test_retirement_current import CurrentRetirementTests,snapshot
from tools.puzzle_production import integrated_content as retirement, target_adapter, contract
suite=unittest.defaultTestLoader.loadTestsFromTestCase(CurrentRetirementTests)
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():raise SystemExit(1)
# Explicit initial compaction with both image-free preferences, in addition to
# durable selected/PNG and imported v6/none cases. No actual catalog data.
CurrentRetirementTests.setUpClass()
rows=[]
try:
 for status,extension in [('standard','.svg'),('none','.png')]:
  case=CurrentRetirementTests();case.setUp()
  try:
   case.migrate(status,extension);commit=case.commit();before=snapshot(case.root)
   with patch.object(target_adapter,'verify_export',side_effect=AssertionError('production replay')):
    value=retirement.retire(case.root,[case.identifier],commit)
   after=snapshot(case.root)
   assert value['status']=='production_retired'
   live={n:v for n,v in before.items() if n.startswith(('game/','content/backgrounds/','content/reveals/','content/added/','content/difficulty/'))}
   assert live=={n:after[n] for n in live}
   assert retirement.retire(case.root,[case.identifier],commit)['status']=='no-op'
   assert after==snapshot(case.root)
   rows.append({'status':status,'extension':extension,'result':value,'live_bytes_and_mtimes_identical':True,
                'delta':sorted(n for n in before.keys()|after.keys() if before.get(n)!=after.get(n))})
  finally:case.doCleanups()
finally:CurrentRetirementTests.doClassCleanups()
(home/'current-cases.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('T01 and one-time current-form matrix passed',flush=True)
