"""Final-head genuine Windows executable smoke; worker mode has no windows."""
from pathlib import Path
import sys,os,json,time,shutil,subprocess,tempfile,hashlib
b=Path(__file__).resolve().parent;sys.path.insert(0,str(b/'work'))
t=b/'temp-final-binary';t.mkdir(exist_ok=True);os.environ.update(TEMP=str(t),TMP=str(t),TMPDIR=str(t));tempfile.tempdir=str(t)
from tools.puzzle_editor.bundle import verify
app=b/'portable-final-head/dist/Picross-Bestandseditor';head=verify(app)
old=b/'portable-delivery/dist/Picross-Bestandseditor'
def files(directory):return {p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file()}
prior,current=files(old),files(app);differences=sorted(n for n in set(prior)|set(current) if prior.get(n)!=current.get(n))
root=b/'final-binary-data';assert not root.exists();shutil.copytree(b/'synthetic-seed-636',root)
jobdir=b/'final-binary-job';jobdir.mkdir();workspace=jobdir/'work';workspace.mkdir()
report={'head':head,'previous_native_and_frozen_ui_head':verify(old),'bundle_different_files':differences,'source_diff_since_native_and_full_profiles':subprocess.check_output(['git','diff','--name-only',verify(old),head],cwd=b/'work',text=True).splitlines(),'runs':[],'passed':False}
def inventory():return {p.relative_to(root).as_posix():(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
identifier=json.loads((root/'content/registry.json').read_bytes())['entries'][0]['id']
for label,action,body in [('detail','detail',{'id':identifier}),('migration-plan','migration',{}),('migration-apply','apply',{'kind':'migration'}),('migration-noop','apply',{'kind':'migration'})]:
    before=inventory();job=jobdir/'job.json';job.write_text(json.dumps({'root':str(root),'work':str(workspace),'action':action,'body':body}),encoding='utf-8')
    start=time.perf_counter()
    with (jobdir/'process.log').open('wb') as log:
        p=subprocess.run([str(app/'Picross-Bestandseditor.exe'),'--worker',str(job)],stdout=log,stderr=log,cwd=app,creationflags=subprocess.CREATE_NO_WINDOW)
    wall=time.perf_counter()-start;response=json.loads((jobdir/'result.json').read_bytes());assert p.returncode==0 and response['error'] is None,response
    after=inventory();changed=sorted(n for n in set(before)|set(after) if before.get(n)!=after.get(n))
    assert changed==(['game/data/registry.json'] if label=='migration-apply' else []),changed
    if label=='migration-noop':assert response['result']['status']=='noop'
    report['runs'].append({'action':label,'actual_exe_exit_code':p.returncode,'wall_seconds':wall,'changed':changed,'diagnostics':response['diagnostics']})
assert json.loads((root/'game/data/registry.json').read_bytes())['format']=='picross-runtime-registry-v8'
assert not (root/'content/.registration-pending.json').exists()
assert report['source_diff_since_native_and_full_profiles']==['.ci/package.json','tests/puzzle_production/test_catalog_images.py']
report['passed']=True
(b/'final-binary-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'head':head,'passed':True,'different_bundle_files':differences}))
