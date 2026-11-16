from pathlib import Path
import unittest,sys,json,time,subprocess,platform,os
repo=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=False)
sys.path[:0]=[str(repo),str(repo/'tests/puzzle_production')];os.chdir(repo)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
class Result(unittest.TextTestResult):
 def startTest(self,test):self.began=time.perf_counter();super().startTest(test)
 def addSuccess(self,test):super().addSuccess(test);rows.append({'test':test.id(),'status':'passed','seconds':time.perf_counter()-self.began})
 def addError(self,test,error):super().addError(test,error);rows.append({'test':test.id(),'status':'error','seconds':time.perf_counter()-self.began})
 def addFailure(self,test,error):super().addFailure(test,error);rows.append({'test':test.id(),'status':'failed','seconds':time.perf_counter()-self.began})
rows=[];started=time.perf_counter()
names=['test_current_integration','test_current_consumers','test_current_completion']
with (out/'tests.log').open('w',encoding='utf-8',newline='\n') as log:
 result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromNames(names))
unchanged=head==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip() and not subprocess.check_output(['git','status','--porcelain'],text=True)
from PIL import __version__ as pillow
report={'format':'ri-one-t01/v1','source_head':head,'base':'62401382f58adc2e3d303b19c1ecb1f1dc8a5040','source_unchanged':bool(unchanged),'passed':result.wasSuccessful() and bool(unchanged),'tests':rows,'seconds':time.perf_counter()-started,'python':platform.python_version(),'pillow':pillow}
(out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='tests'}));sys.exit(not report['passed'])
