"""One isolated RI-V9 acceptance run; observers only, no validation replacements."""
import contextlib, hashlib, json, os, platform, subprocess, sys, time, zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent / 'repo'))
from tools.puzzle_production import target_adapter as adapter, catalog_rating as rating
from tools.puzzle_production import content_registry as cr, registration_publication as phased
from tools.puzzle_production import catalog_transaction as tx, catalog_publication as pub
from tools.production_workspace import projector, current_view
from tools.production_workspace.sources import LocalSource
from PIL import __version__ as pillow
HERE = Path(__file__).resolve().parent
ROOT = HERE / 'through'
EVIDENCE = HERE / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
EXPORT = HERE / 'fliegenpilz-export'
RECORD = 'content/authoring/pz-fliegenpilz/r07/record.json'
MAIN = '6b0057100d5bdacd68878d80d5bd29e5ca4ee9a5'
SOURCE = 'e3b177673011c5477dd605c24420fef589e8f878'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(name, value): (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def git(*args):
    return subprocess.run(['git', '-c', 'user.name=RI-V9 isolated test',
        '-c', 'user.email=ri-v9@example.invalid', '-c', 'commit.gpgsign=false', *args],
        cwd=ROOT, check=True, capture_output=True).stdout.decode().strip()
def inventory():
    return {p.relative_to(ROOT).as_posix(): {'sha256':sha(p.read_bytes()), 'bytes':p.stat().st_size}
            for base in ('content','game') for p in (ROOT/base).rglob('*') if p.is_file()}
def native(command, args):
    with (EVIDENCE/(command+'-result.json')).open('w',encoding='utf8') as output,          (EVIDENCE/(command+'-stderr.log')).open('w',encoding='utf8') as errors,          contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        code=adapter.main([command,*map(str,args),'--operation-report',str(EVIDENCE/(command+'-operation.json'))])
    print(command, code, flush=True)
    if code: raise RuntimeError(command+' failed; native result retained')
    return json.loads((EVIDENCE/(command+'-result.json')).read_text(encoding='utf8'))

before=inventory()
record=json.loads((ROOT/RECORD).read_bytes())
assert record['state']=='editorially_approved' and record['integration'] is None
registry_before=json.loads((ROOT/cr.REGISTRY).read_bytes())
runtime_before=json.loads((ROOT/cr.RUNTIME).read_bytes())
assert registry_before['format']=='picross-content-registry-v4'
assert runtime_before['format']=='picross-runtime-registry-v8'
assert not (ROOT/tx.LOCK).exists()
assert sha((ROOT/record['package']['file']).read_bytes())==record['package']['sha256']
tool_root=Path(adapter.__file__).resolve().parents[2]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=tool_root).decode().strip()
save('inputs.json',{'main':MAIN,'source':SOURCE,'tool_head':head,
    'tool_diff_sha256':sha(subprocess.check_output(['git','diff','HEAD'],cwd=tool_root)),
    'python':sys.version,'pillow':pillow,'platform':platform.platform(),
    'registry':registry_before['format'],'runtime':runtime_before['format'],
    'entries':len(registry_before['entries']),
    'original_zip':record['package'],'approval':record['final_editorial_approval']})
native('export',['--input',ROOT/record['package']['file'],'--output-dir',EXPORT,
    '--approval',ROOT/record['final_editorial_approval']['file'],'--allow-background',
    '--external-root',ROOT,'--history-repo',ROOT,'--name','Fliegenpilz',
    '--runtime-revision','1','--stem','fliegenpilz','--save-slot','fliegenpilz',
    '--category-id',record['category_id'],'--categories',ROOT/'content/categories.json'])
manifest=json.loads((EXPORT/'manifest.json').read_bytes())
with zipfile.ZipFile(ROOT/record['package']['file']) as archive:
    checked_raw=archive.read('analysis/r05-visible/checked.json')
checked=rating.rebind_checked(json.loads(checked_raw), (EXPORT/manifest['definition']).read_bytes(), production_mode='color')
(HERE/'checked.json').write_text(json.dumps(checked,sort_keys=True)+'\n',encoding='utf8')
save('rating-binding.json',{'original_checked_sha256':sha(checked_raw),'rebound_checked_sha256':sha((HERE/'checked.json').read_bytes()),
                          'method':checked['rating']['method'],'checked':checked})
args=['--export',EXPORT,'--checkout',ROOT,'--difficulty',HERE/'checked.json']
native('plan',args)
assert inventory()==before, 'Plan changed checkout'
calls={'old':0,'new':0}
old_packages={(ROOT/e['production']['package']).resolve() for e in registry_before['entries']}
verify=adapter.verify_export
def observed_verify(path):
    calls['old' if Path(path).resolve() in old_packages else 'new']+=1
    return verify(path)
route=[]
execute=phased.execute
def observed_execute(root,journal,additions,**kwargs):
    route.append({'format':journal['format'],'operation':journal['operation'],
        'writer':'registration_publication.execute','journal_sha256':sha(pub.journal_bytes(journal)),
        'additions':sorted(journal['additions']),
        'targets':sorted(set(journal['additions']) | {n for n in journal['new'] if journal['new'][n]!=journal['old'][n]})})
    return execute(root,journal,additions,**kwargs)
guards=[]
full=phased.Guards.full
def observed_full(self, boundary, **kwargs):
    result=full(self,boundary,**kwargs)
    guards.append(boundary)
    return result

from collections import Counter
from tools.puzzle_production import catalog_io as io, reveal_source, registration_verification as verification
access = Counter()
resolve_counts = Counter()
stage_copies = []
stage_active = []
native_read = io.read
native_write = Path.write_bytes
def observed_read(root, name, *a, **kw):
    raw = native_read(root, name, *a, **kw)
    path = (Path(root) / name).as_posix()
    key = ('old-package' if '/content/packages/' in path and '/pz-fliegenpilz/' not in path else
           'new-package' if '/content/packages/pz-fliegenpilz/' in path else
           'live-content' if '/game/' in path else
           'catalog-source' if '/content/' in path else
           'tool-runtime' if '/repo/tools/' in path or '/venv/' in path or 'WindowsApps' in path else 'input-or-temp')
    access[key + ':calls'] += 1
    access[key + ':bytes'] += len(raw) if raw is not None else 0
    return raw
def observed_write(path, data):
    result = native_write(path, data)
    if stage_active:
        stage_active[-1]['files'] += 1
        stage_active[-1]['bytes'] += len(data)
    return result
native_stage = tx._stage_check
def observed_stage(*a, **kw):
    row = {'files':0,'bytes':0}
    stage_active.append(row); start = time.perf_counter()
    try: return native_stage(*a, **kw)
    finally:
        row['seconds'] = time.perf_counter()-start
        stage_copies.append(row); stage_active.pop()
def count_call(fn, label):
    def call(*a, **kw):
        resolve_counts[label] += 1
        return fn(*a, **kw)
    return call

with patch.object(io,'read',observed_read), patch.object(Path,'write_bytes',observed_write), patch.object(tx,'_stage_check',observed_stage), patch.object(reveal_source,'resolve',count_call(reveal_source.resolve,'reveal.resolve')), patch.object(reveal_source,'package',count_call(reveal_source.package,'reveal.package')), patch.object(cr,'projection',count_call(cr.projection,'registry.projection')), patch.object(verification,'inventory',count_call(verification.inventory,'verification.inventory')), patch.object(verification,'_methods',count_call(verification._methods,'verification.methods')), patch.object(adapter,'verify_export',side_effect=observed_verify),      patch.object(phased,'execute',side_effect=observed_execute),      patch.object(phased.Guards,'full',observed_full):
    registered=native('register',args)
save('work-amounts.json',{'io':dict(access),'calls':dict(resolve_counts),'stage_copies':stage_copies})
save('observations.json',{'replay_calls':calls,'route':route,'completed_guards':guards})
assert registered['status']=='registered'
assert calls['old']==0 and calls['new']>=2
assert [r['format'] for r in route]==['picross-registration-journal-v9']
assert guards==['G0','G2','G5a','G5b','G6']
assert not (ROOT/tx.LOCK).exists() and pub.staging(ROOT)==[]
checked_registry=cr.check_checkout(ROOT)
old_ids={e['id'] for e in registry_before['entries']}
assert [e for e in checked_registry['entries'] if e['id'] in old_ids]==registry_before['entries']
for field in ('metadata','backgrounds'):
    assert [e for e in checked_registry[field] if e['id'] in old_ids]==registry_before[field]
after=inventory()
changed=[n for n in before if after.get(n)!=before[n]]
assert set(changed)=={cr.REGISTRY,cr.RUNTIME}
added=sorted(set(after)-set(before))
assert set(added)==set(route[0]['targets'])-set(changed), (added,route[0]['targets'])
save('registration-diff.json',{'existing_files':len(before),'unchanged_files':len(before)-len(changed),
    'changed':{n:{'before':before[n],'after':after[n]} for n in changed},
    'added':{n:after[n] for n in added},'before_inventory_sha256':sha(json.dumps(before,sort_keys=True).encode())})
git('add','content','game');git('commit','-qm','TEST ONLY RI-V9 isolated registration')
commit=git('rev-parse','HEAD')
started=time.monotonic()
with (EVIDENCE/'completion-result.json').open('w',encoding='utf8') as output, contextlib.redirect_stdout(output):
    code=projector.main(['--repository',str(ROOT),'--complete-record',RECORD,'--integration-commit',commit])
assert code==0
completed=inventory()
completion_changed=[n for n in after if completed.get(n)!=after[n]]
expected={RECORD,RECORD.replace('record.json','workspace.json'),'content/authoring/pz-fliegenpilz/current-view.json'}
assert set(completion_changed)==expected
assert set(completed)==set(after)
view=current_view.inspect(LocalSource(ROOT),None,(ROOT/current_view.path('pz-fliegenpilz')).read_bytes(),'pz-fliegenpilz',originals=True)
assert json.loads((ROOT/RECORD).read_bytes())['state']=='registered'
save('summary.json',{'status':'passed','main':MAIN,'source':SOURCE,'tool_head':head,
    'registration_commit':commit,'registered':True,'completion':True,'completion_seconds':time.monotonic()-started,
    'completion_changed':completion_changed,'current_revision':view['revision'],
    'replays':calls,'guards':guards,'existing_entries_preserved':len(old_ids),
    'original_zip_unchanged':before[record['package']['file']]==completed[record['package']['file']],
    'approval_unchanged':before[record['final_editorial_approval']['file']]==completed[record['final_editorial_approval']['file']],
    'retirement':False,'merge':False,'content_pr_changed':False})
print('passed: isolated registration and completion',flush=True)

