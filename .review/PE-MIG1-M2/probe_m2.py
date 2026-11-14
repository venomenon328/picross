"""One-off independent pre/post oracle and external runner fault probes."""
import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import migrate_m2 as migration

ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT/'repo'
TEST=ROOT/'testrepo'
EVIDENCE=ROOT/'evidence'
PLAN=json.loads((EVIDENCE/'migration-plan.json').read_bytes())


def digest(raw): return hashlib.sha256(raw).hexdigest()
def unpack(v): return base64.b64decode(v) if v is not None else None


def old(name):
    pair=PLAN['changes'].get(name)
    return unpack(pair['old']) if pair else (PRODUCT/name).read_bytes()


def check_plan():
    changes=PLAN['changes']
    index=json.loads(old('content/registry.json'))
    runtime=json.loads(old('game/data/registry.json'))
    after_index=json.loads(unpack(changes['content/registry.json']['new']))
    after_runtime=json.loads(unpack(changes['game/data/registry.json']['new']))
    assert {k:v for k,v in index.items() if k!='backgrounds'} == {k:v for k,v in after_index.items() if k!='backgrounds'}
    assert runtime['categories']==after_runtime['categories'] and runtime['format']==after_runtime['format']
    ids=[e['id'] for e in index['entries']]
    allowed={'content/registry.json','game/data/registry.json'}|{f'content/{kind}/{i}.json' for i in ids for kind in ('reveals','backgrounds')}
    assert set(changes)==allowed and len(changes)==114
    legacy, selected, old_reveals, sourcefree=0,0,0,0
    rows=[]
    for entry,before,after in zip(index['entries'],runtime['entries'],after_runtime['entries']):
        identifier=entry['id']
        assert {k:v for k,v in before.items() if k!='background'} == {k:v for k,v in after.items() if k!='background'}
        definition=(PRODUCT/('game/'+entry['definition'])).read_bytes()
        assert digest(definition)==entry['production']['definition_sha256']
        raw=(PRODUCT/('game/'+before['reveal'])).read_bytes()
        r=json.loads(unpack(changes[f'content/reveals/{identifier}.json']['new']))
        b=json.loads(unpack(changes[f'content/backgrounds/{identifier}.json']['new']))
        expected_binding={'entry':entry,'identity':{'key':entry['key'],'save_slot':entry['save_slot'],
          'definition':{'file':'game/'+entry['definition'],'sha256':digest(definition),'bytes':len(definition)},'runtime_revision':json.loads(definition)['revision']}}
        for source in (r,b):
            assert set(source)=={'format','id','record_revision','binding','current','record_hash'}
            assert source['id']==identifier and source['binding']==expected_binding
            canonical=json.dumps({k:v for k,v in source.items() if k!='record_hash'},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
            assert source['record_hash']==digest(canonical)
        assert r['format']=='picross-catalog-reveal-v4' and b['format']=='picross-catalog-background-v6'
        assert r['current']['asset']=={'file':'game/'+before['reveal'],'sha256':digest(raw),'bytes':len(raw)}
        previous=unpack(changes[f'content/reveals/{identifier}.json']['old'])
        if previous:
            previous=json.loads(previous); old_reveals+=1
            assert r['current']['image_revision']==previous['revisions'][-1]['image_revision']
            assert r['current']['asset']['sha256']==previous['revisions'][-1]['reveal_sha256']
            assert r['record_revision']==max(previous['record_revision'],previous['current']['image_revision'])+1
        else:
            sourcefree+=1; assert r['record_revision']==r['current']['image_revision']==1
        if before['background']['status']=='legacy':
            legacy+=1
            assert after['background']=={'status':'standard','image_revision':1,'asset':None}
            assert b['record_revision']==1
        else:
            selected+=1; assert before['background']==after['background']
            previous=json.loads(unpack(changes[f'content/backgrounds/{identifier}.json']['old']))
            assert b['current']['asset']==previous['asset'] and b['current']['image_revision']==previous['image_revision']
            assert b['record_revision']==previous['image_revision']+1
        projected=deepcopy(b['current'])
        if projected['asset']: projected['asset']['file']=projected['asset']['file'].removeprefix('game/')
        assert projected==after['background']
        rb=unpack(changes[f'content/backgrounds/{identifier}.json']['new'])
        assert next(i['source'] for i in after_index['backgrounds'] if i['id']==identifier)=={'file':f'content/backgrounds/{identifier}.json','bytes':len(rb),'sha256':digest(rb)}
        rows.append({'id':identifier,'definition_sha256':digest(definition),'reveal_sha256':digest(raw),'old_background':before['background'],'new_background':after['background']})
    assert (old_reveals,sourcefree,legacy,selected)==(26,30,53,3)
    return {'status':'passed','files':114,'inventory_files':len(PLAN['inventory']),'old_reveals':old_reveals,'sourcefree':sourcefree,'legacy_to_standard':legacy,'selected_retained':selected,'rows':rows}


def negative(name, fn):
    before=migration.files(TEST)
    try: fn()
    except (ValueError,OSError,KeyError,TypeError) as exc:
        assert migration.files(TEST)==before
        return {'scenario':name,'status':'rejected_without_mutation','error':str(exc)}
    raise AssertionError('Expected rejection: '+name)


def faults():
    results=[]
    assert migration.build(TEST)==PLAN
    lock=TEST/migration.LOCK
    lock.write_bytes(b'unknown foreign journal\n')
    results.append(negative('foreign_lock',lambda:migration.apply(TEST,PLAN)))
    lock.unlink()
    stage=TEST/'content/.editor-change-journal.tmp'
    stage.write_bytes(b'foreign staging\n')
    results.append(negative('foreign_staging',lambda:migration.apply(TEST,PLAN)))
    stage.unlink()
    file=TEST/'game/data/registry.json'; raw=file.read_bytes(); stamp=file.stat()
    file.write_bytes(raw+b' '); os.utime(file,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
    results.append(negative('same_mtime_stale_bytes',lambda:migration.apply(TEST,PLAN)))
    file.write_bytes(raw); os.utime(file,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
    bad=deepcopy(PLAN); bad['changes']['game/code.gd']=bad['changes'].pop('game/data/registry.json')
    bad=migration.hashed({k:v for k,v in bad.items() if k!='plan_hash'},'plan_hash')
    results.append(negative('forged_write_path',lambda:migration.apply(TEST,bad)))
    target=TEST/'content/reveals'/ (PLAN['bindings'][0]['id']+'.json')
    assert not target.exists()
    os.link(file,target)
    try:
        try: migration.apply(TEST,PLAN)
        except ValueError as exc: results.append({'scenario':'hardlink','status':'rejected_without_mutation','error':str(exc)})
        else: raise AssertionError('Hardlink accepted')
    finally: target.unlink()
    try: os.symlink(file,target)
    except OSError as exc: results.append({'scenario':'symlink','status':'unavailable','error':str(exc)})
    else:
        try:
            try: migration.apply(TEST,PLAN)
            except ValueError as exc: results.append({'scenario':'symlink','status':'rejected_without_mutation','error':str(exc)})
            else: raise AssertionError('Symlink accepted')
        finally: target.unlink()
    for step in (0,1,113,114):
        start=time.perf_counter()
        try: migration.apply(TEST,PLAN,step)
        except RuntimeError as exc: assert str(exc).startswith('Injected stop')
        else: raise AssertionError('Missing injected failure')
        assert lock.is_file()
        if step==1:
            first=migration.order(PLAN)[0]; p=TEST/first; prior=p.read_bytes(); p.write_bytes(prior+b'foreign')
            results.append(negative('foreign_recovery_bytes',lambda:migration.rollback(TEST)))
            p.write_bytes(prior)
        result=migration.rollback(TEST)
        assert result['status']=='rolled_back' and migration.files(TEST)==PLAN['inventory']
        assert migration.rollback(TEST)['status']=='noop'
        results.append({'scenario':'interruption_'+str(step),'status':'rolled_back_exactly','seconds':time.perf_counter()-start})
    return results


if __name__=='__main__':
    result=check_plan()
    (EVIDENCE/'plan-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PRE-APPLY INDEPENDENT PLAN REVIEW PASS',len(result['rows']),flush=True)
    results=faults()
    (EVIDENCE/'guard-rollback.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print('GUARD/ROLLBACK PROBES PASS',len(results),flush=True)
    print(migration.apply(TEST,PLAN),flush=True)
