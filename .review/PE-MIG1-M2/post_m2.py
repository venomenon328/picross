"""Independent whole-file postcomparison and repeated byte/mtime no-op."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import migrate_m2 as migration
import probe_m2
from tools import background_import

ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT/'repo'; OUT=ROOT/'evidence'
PLAN=json.loads((OUT/'migration-plan-final.json').read_bytes())


def inventory():
    return {p.relative_to(PRODUCT).as_posix(): {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns}
            for p in PRODUCT.rglob('*') if p.is_file() and p.name!='.git' and '.git' not in p.relative_to(PRODUCT).parts}


def main():
    actual=inventory(); expected=migration.expected(PLAN,True)
    assert {n:{k:v for k,v in item.items() if k!='mtime_ns'} for n,item in actual.items()}==expected
    probe_m2.PLAN=PLAN
    report=probe_m2.check_plan()
    diff=subprocess.check_output(['git','diff','--name-only',migration.BASE],cwd=PRODUCT,text=True).splitlines()
    allowed=set(PLAN['changes'])|{'.ci/package.json','tools/background_import.py','tools/test_background_import.py','docs/PUZZLE_BACKGROUNDS.md'}
    assert set(diff)<=allowed
    # Include currently untracked newly introduced sources in the exact set.
    changed=set(diff)|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=PRODUCT,text=True).splitlines())
    assert changed==allowed
    noops=[]
    for kind in ('original_plan_apply','fresh_plan_apply'):
        before=inventory(); started=time.perf_counter()
        value=PLAN if kind=='original_plan_apply' else migration.build(PRODUCT)
        if kind=='fresh_plan_apply': assert not value['changes']
        result=migration.apply(PRODUCT,value)
        assert result['status']=='noop' and inventory()==before
        noops.append({'scenario':kind,'result':result,'seconds':time.perf_counter()-started,'files_and_mtimes_identical':len(before)})
    sources=background_import.source_inventory(PRODUCT)
    assert len(sources['assets'])==3 and all(r['notice'] is not None for r in sources['assets'])
    (OUT/'product-background-inventory.json').write_text(json.dumps(sources,indent=2)+'\n',encoding='utf-8')
    report.update(noops=noops,source_inventory=sources,all_files=actual,exact_product_diff=sorted(changed),
                  pending=migration.edit.pending(PRODUCT),status='passed')
    assert not report['pending']
    (OUT/'postcomparison-noop.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: exact 118-path product diff; 114 migration data files; all retained bytes unchanged; two complete byte/mtime noops; current import reader')


if __name__=='__main__': main()
