"""CLI/shared editor source readers on all 56 real migrated entries.

Only TEST is edited. Product bytes are checked before and after this probe.
No browser automation, user profile or save store is used.
"""
import base64
from copy import deepcopy
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import migrate_m2 as migration
from tools.puzzle_production import editor_change as edit, editor_cli
from tools.puzzle_production import catalog_background as bg, reveal_source as reveal, categories
from tools.puzzle_editor.server import Service
from tools.puzzle_editor import server

ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT/'repo'; TEST=ROOT/'testrepo'; OUT=ROOT/'evidence'


def call_cli(args):
    result=subprocess.run([sys.executable,'-m','tools.puzzle_production.editor_cli',*args,'--target-root',str(TEST)],
      cwd=PRODUCT,env=os.environ.copy(),capture_output=True,timeout=300)
    assert result.returncode==0, result.stdout.decode()+result.stderr.decode()
    return json.loads(result.stdout)


def wait(service):
    end=time.monotonic()+300
    while time.monotonic()<end:
        status=service.status()
        if status['job']['state']!='running':
            assert status['job']['state']=='done',status['job']
            return status['job']['result']
        time.sleep(.02)
    raise AssertionError('Editor job did not finish')


def main():
    product_before=migration.files(PRODUCT)
    catalog=call_cli(['list'])
    index=json.loads((TEST/'content/registry.json').read_bytes())
    runtime=json.loads((TEST/'game/data/registry.json').read_bytes())
    cats=categories.load(TEST/categories.PATH)
    assert len(catalog['entries'])==56 and not catalog['migration_required']
    details=[]
    for entry in index['entries']:
        detail=call_cli(['detail','--id',entry['id']])
        assert not detail['source_migration_required']
        r=reveal.load(TEST,entry,cats); b=bg.load(TEST,index,entry)
        resolved=reveal.resolve(TEST,entry,cats)
        assert resolved['effective_reveal_sha256']==r['current']['asset']['sha256']
        assert resolved['runtime_revision']==detail['raster']['revision']
        details.append({'id':entry['id'],'cli_detail':detail,'reveal_record_hash':r['record_hash'],'background_record_hash':b['record_hash'], 'resolved':resolved})
    texts={n:(TEST/n).read_bytes() for n in bg.text_names(index) if (TEST/n).exists()}
    assert bg.projection(index,texts)=={r['id']:r['background'] for r in runtime['entries']}
    (OUT/'reader-all56.json').write_bytes(edit.encoded({'status':'passed','count':56,'details':details}))
    # Exercise the actual editor worker/detail and preview byte path for every ID.
    previews=[]
    # -I workers ignore bytecode environment variables; use a byteidentical
    # private trusted program copy so they cannot create caches in PRODUCT.
    program=ROOT/'trusted-program'
    shutil.copytree(PRODUCT/'tools',program/'tools',dirs_exist_ok=True)
    shutil.copytree(PRODUCT/'game/art/drawing',program/'game/art/drawing',dirs_exist_ok=True)
    (program/'game/book').mkdir(parents=True,exist_ok=True)
    shutil.copyfile(PRODUCT/'game/book/paper.png',program/'game/book/paper.png')
    server.CODE=program
    service=Service(TEST,temporary=ROOT/'temp',state=ROOT/'temp/editor-settings')
    try:
        for entry in index['entries']:
            service.detail({'id':entry['id'],'snapshot':catalog['snapshot']})
            result=wait(service)
            pictures=[]
            for kind,keys in result['pictures'].items():
                if isinstance(keys,str): keys=[keys]
                for key in keys:
                    raw,mime=service.picture(key)
                    pictures.append({'kind':kind,'mime':mime,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            previews.append({'id':entry['id'],'pictures':pictures,'raster_width':result['raster']['width'],'raster_height':result['raster']['height']})
    finally: service.close()
    (OUT/'editor-preview-all56.json').write_bytes(edit.encoded({'status':'passed','count':56,'previews':previews}))
    # Every actual plan/apply is restricted to the second disposable checkout.
    operations=[]
    identifier='pz-birne'
    def execute(kind,**kwargs):
        request={'format':editor_cli.REQUEST,'id':identifier,'metadata':None,'text':None,'profile':'line','reveal':None,'background':None,'imports':{}}
        request.update(kwargs)
        req=OUT/(kind+'-request.json'); req.write_bytes(edit.encoded(request))
        plan_path=OUT/(kind+'-plan.json')
        start=time.perf_counter(); summary=editor_cli.plan_file(TEST,req,plan_path)
        value=json.loads(plan_path.read_bytes()); applied=edit.apply(TEST,value)
        operations.append({'operation':kind,'plan':plan_path.name,'summary':summary,'apply':applied,'seconds':time.perf_counter()-start})
        return value
    execute('metadata',metadata={'name':'Birne Test M2'})
    # Copy another existing PNG unchanged, only into the disposable test target.
    row=next(r for r in runtime['entries'] if r['id']==identifier)
    image_input=next(r for r in runtime['entries'] if r['id']!=identifier and r['reveal'].endswith('.png'))
    import_name='test-import.png'
    (OUT/import_name).write_bytes((TEST/('game/'+image_input['reveal'])).read_bytes())
    try:
        execute('image',reveal={'upload':'r'},imports={'r':import_name},background={'status':'selected','upload':None})
    finally: (OUT/import_name).unlink()
    # An actual preference mutation also tests compact v6/source-index/runtime writes.
    execute('preference',background={'status':'standard','upload':None})
    execute('raster',text='1 1\n1 1')
    detail=edit.detail(TEST,identifier)
    assert detail['raster']['text']=='1 1\n1 1' and detail['raster']['revision']==next(r for r in details if r['id']==identifier)['cli_detail']['raster']['revision']+1
    assert not edit.pending(TEST)
    assert migration.files(PRODUCT)==product_before, 'Product checkout changed during test copy edits'
    (OUT/'editor-plan-apply.json').write_bytes(edit.encoded({'status':'passed','test_checkout_only':True,'operations':operations,'final_detail':{k:v for k,v in detail.items() if k!='_resources'}}))
    print('ALL56 CLI/RESOLVER/EDITOR PREVIEW PASS; METADATA/IMAGE/PREFERENCE/RASTER PLAN/APPLY PASS')


if __name__=='__main__': main()
