import json,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parent/'repo'
out=root.parent/'t01-final';out.mkdir(exist_ok=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root)
command=[sys.executable,'-m','unittest','-v','tests.puzzle_production.test_registration_publication.CurrentGenerationTests','tests.puzzle_production.test_registration_publication.PublicationTests.test_current_and_legacy_dispatch_is_explicit']
meta={'head':head,'base':'c243d9ce95f7cfe55332840f3bf44b313d3b9128','command':command,'purpose':'PW-PERF-B-T01 final-head synthetic cases','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
(out/'run.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
start=time.monotonic()
with (out/'unittest.log').open('w',encoding='utf-8') as log:
 result=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
meta.update(exit_code=result.returncode,seconds=time.monotonic()-start,finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root)
(out/'run.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
raise SystemExit(result.returncode)
