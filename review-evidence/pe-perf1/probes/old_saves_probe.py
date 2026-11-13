"""Comparable real-56 old A2/A3 times. New migration only prepares valid v8."""
from pathlib import Path
import sys,os,json,zipfile,shutil,subprocess,tempfile,time
b=Path(__file__).resolve().parent;sys.path.insert(0,str(b/'work'))
t=b/'temp-old-save-setup';t.mkdir(exist_ok=True);os.environ.update(TEMP=str(t),TMP=str(t),TMPDIR=str(t));tempfile.tempdir=str(t)
from tools.puzzle_production import catalog_images as images,catalog_metadata as metadata,catalog_raster as raster,content_registry as registry,catalog_publication as pub,catalog_transaction as tx
root=b/'old-saves-v8-data';assert not root.exists();root.mkdir()
with zipfile.ZipFile(b/'baseline-source.zip') as z:z.extractall(root)
(root/'.git').mkdir()
reg=json.loads((root/'content/registry.json').read_bytes());identifier=min(reg['entries'],key=lambda e:e['production']['width']*e['production']['height'])['id']
images.apply_migration(root,images.plan_migration(root))
metadata.apply(root,metadata.plan(root,[{'op':'set_metadata','id':identifier,'name':'PE-PERF1 isolated measurement'}]))
inputs=b/'old-save-input';shutil.copytree(b/'final3-input',inputs)
report={'old_source':'4e5bfe489851fe4a4b771fcdf125fd89ce440a98','setup_source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=b/'work',text=True).strip(),'initial_catalog_entries':56,'preconditions':['same archive and min-area real ID as current direct measurements','current explicit runtime-only migration prepares valid v8 because old migration apply fails','same A1 sample name as current sequence','old Apply receives a canonical unchanged-schema bundle prepared by the current constructor, then fully revalidates it; no guard or budget patch'],'runs':[],'passed':False}
def save():(b/'old-saves-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for kind in ('images','raster'):
    print('START OLD',kind,'plan',flush=True)
    result=subprocess.run([sys.executable,'-u',str(b/'old_save_call.py'),kind,'plan',str(b/('old-save-'+kind+'-planned'))],cwd=b/'work',check=True)
    report['runs'].append(json.loads((b/('old-save-'+kind+'-plan.json')).read_bytes()));save()
    if (root/tx.LOCK).exists() or pub.staging(root):registry.recover(root)
    api=images if kind=='images' else raster
    request=inputs/('request.json' if kind=='images' else 'raster.json')
    prepared=b/('old-save-'+kind+'-prepared')
    api.plan(root,request,prepared)
    print('START OLD',kind,'apply',flush=True)
    subprocess.run([sys.executable,'-u',str(b/'old_save_call.py'),kind,'apply',str(prepared)],cwd=b/'work',check=True)
    report['runs'].append(json.loads((b/('old-save-'+kind+'-apply.json')).read_bytes()));save()
    if (root/tx.LOCK).exists() or pub.staging(root):registry.recover(root)
    if kind=='images':
        # A fresh current plan establishes the exact A2 state for the following
        # A3 comparison, whether the old call failed or completed.
        fresh=b/'old-save-images-fresh';images.plan(root,request,fresh);images.apply(root,fresh)
registry.check_checkout(root)
report['current_category_runs']=[]
original_category=next(e['category_id'] for e in json.loads((root/'content/registry.json').read_bytes())['metadata'] if e['id']==identifier)
def category_action(label,operation):
    from tools.puzzle_production import operation_diagnostics as diagnostic
    import hashlib
    def inventory():return {p.relative_to(root).as_posix():(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for folder in ('content','game/data','game/art/content','game/art/backgrounds') for p in (root/folder).rglob('*') if p.is_file()}
    for action in ('plan','apply'):
        before=inventory()
        observer=diagnostic.Diagnostics(label+'-'+action,stderr=sys.stdout)
        started=time.perf_counter();cpu=time.process_time()
        with diagnostic.observe(observer):
            if action=='plan':value=metadata.plan(root,[operation])
            else:result=metadata.apply(root,value)
        elapsed,used=time.perf_counter()-started,time.process_time()-cpu
        after=inventory();changed=sorted(n for n in set(before)|set(after) if before.get(n)!=after.get(n))
        assert changed==([] if action=='plan' else sorted(value['files'])),changed
        profile=observer.result();profile.pop('environment',None)
        report['current_category_runs'].append({'source':report['setup_source'],'action':label+'-'+action,'wall_seconds':elapsed,'cpu_seconds':used,'files':value['files'],'actual_changed':{n:{'before':before.get(n),'after':after.get(n)} for n in changed},'profile':profile})
        save()
category_action('category-create',{'op':'category_create','name':'PE PERF1 timing'})
category_id=next(e['id'] for e in metadata.view(root)['categories'] if e['name']=='PE PERF1 timing')
category_action('category-assign',{'op':'set_metadata','id':identifier,'category_id':category_id})
category_action('category-delete-reassign',{'op':'category_delete','id':category_id,'reassign_to':original_category})
assert next(e['category_id'] for e in json.loads((root/'content/registry.json').read_bytes())['metadata'] if e['id']==identifier)==original_category
assert not any(e['id']==category_id for e in metadata.view(root)['categories'])
registry.check_checkout(root)
report['passed']=True;save()
