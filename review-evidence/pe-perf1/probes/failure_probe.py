"""One-time actual worker protocol at shared publication checkpoints."""
from pathlib import Path
import sys,os,json,subprocess,tempfile,shutil,hashlib,time
b=Path(__file__).resolve().parent;sys.path.insert(0,str(b/'work'))
t=b/'temp-failure';t.mkdir(exist_ok=True)
os.environ.update(TEMP=str(t),TMP=str(t),TMPDIR=str(t));tempfile.tempdir=str(t)
from tools.puzzle_production import catalog_transaction as tx, catalog_publication as pub
from tools.puzzle_editor.progress import state
report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=b/'work',text=True).strip(),'hook':'existing catalog_publication.checkpoint; InterruptedError; no budget/guard patch','cases':[],'passed':False}
def inventory(root):return {p.relative_to(root).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtime_ns':p.stat().st_mtime_ns} for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
def hashes(value):return {k:v['sha256'] for k,v in value.items()}
def run(root,workspace,action,body,boundary=None):
    job=workspace.parent/(action+'-'+(boundary or 'plain')+'.json')
    job.write_text(json.dumps({'root':str(root),'work':str(workspace),'action':action,'body':body}),encoding='utf-8')
    code='import sys;sys.path.insert(0,sys.argv[1]);'
    if boundary:
        code+='from tools.puzzle_production import catalog_publication as pub;exec("def fault(phase, name=None):\\n    if phase == '+repr(boundary)+': raise InterruptedError(\\\"controlled '+boundary+' interruption\\\")");pub.checkpoint=fault;'
    code+='from tools.puzzle_editor.worker import main;main(sys.argv[2])'
    started=time.perf_counter()
    p=subprocess.run([sys.executable,'-I','-c',code,str(b/'work'),str(job)],cwd=b/'work',capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    result=json.loads((job.parent/'result.json').read_bytes())
    return result,{'action':action,'boundary':boundary,'exit_code':p.returncode,'wall_seconds':time.perf_counter()-started,'error':result['error'],'diagnostics':result['diagnostics'],'observed_state':state(root),'journal_exists':(root/tx.LOCK).exists(),'staging_count':len(pub.staging(root)),'runtime_format':json.loads((root/tx.RUNTIME).read_bytes())['format']}
for boundary in ('P0','journal-complete','P1','P5'):
    root=b/('failure-'+boundary);assert not root.exists();shutil.copytree(b/'synthetic-seed-636',root)
    work=b/('failure-work-'+boundary);work.mkdir();workspace=work/'work';workspace.mkdir()
    initial=inventory(root);before=hashes(initial)
    plan,_=run(root,workspace,'migration',{});assert not plan['error']
    failed,row=run(root,workspace,'apply',{'kind':'migration'},boundary)
    assert failed['error'] and row['exit_code']==0,row
    assert 'Phase:' in failed['error'] and str(b) not in failed['error']
    after=inventory(root);row['changed_at_failure']={n:{'before':initial.get(n),'after':after.get(n)} for n in set(initial)|set(after) if initial.get(n)!=after.get(n)}
    if boundary=='P0':
        assert after==initial and row['runtime_format'].endswith('-v7') and not row['journal_exists'] and row['staging_count']==0
    else:
        assert 'recovery_required' in row['observed_state']
        if boundary=='P5':assert row['runtime_format'].endswith('-v8')
    recovered,r1=run(root,workspace,'recover',{});assert not recovered['error'];assert hashes(inventory(root))==before
    stable=inventory(root)
    repeated,r2=run(root,workspace,'recover',{});assert not repeated['error'] and repeated['result']['status']=='noop';assert inventory(root)==stable
    fresh,_=run(root,workspace,'migration',{});assert not fresh['error']
    success,applied=run(root,workspace,'apply',{'kind':'migration'});assert not success['error'] and applied['runtime_format'].endswith('-v8')
    final=inventory(root)
    again,noop=run(root,workspace,'apply',{'kind':'migration'});assert not again['error'] and again['result']['status']=='noop';assert inventory(root)==final
    row['recovery']=[r1,r2];row['fresh_apply']=applied;row['repeat_noop']=noop;row['hash_restoration']=True;row['noop_mtimes_unchanged']=True
    report['cases'].append(row)
    (b/'failure-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
report['passed']=True
(b/'failure-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
