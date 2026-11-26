"""One-shot measurements on a newly generated synthetic two-puzzle catalog."""
import collections
import hashlib
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()))
from tests.puzzle_production import current_fixtures as fx
from tools.puzzle_production import catalog_integration as reg, catalog_io as io, catalog_metadata as meta, current_registration as transaction

def inventory(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}

def sample(results, label, root, operation):
    before = inventory(root)
    real_read = io.read
    reads = collections.Counter()
    def traced(root,name,*args,**kwargs):
        reads[name] += 1
        return real_read(root,name,*args,**kwargs)
    start = perf_counter()
    with patch.object(io,'read',traced):
        result = operation()
    elapsed = perf_counter()-start
    after = inventory(root)
    written = {p:len(after.get(p,b'')) for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
    results[label] = {'seconds':elapsed,'catalog_read_calls':dict(sorted(reads.items())),'net_changed_files_bytes':written}
    return result

def main(stage):
    results = {}
    with TemporaryDirectory(dir=Path.cwd().parent) as temp:
        work=Path(temp)
        root=fx.checkout(work/'catalog')
        a=fx.make(work/'a',identifier='pz-sample-a')
        b=fx.make(work/'b',identifier='pz-sample-b')
        reg.integrate(b,root,apply=True)
        sample(results,'registration',root,lambda:reg.integrate(a,root,apply=True))
        sample(results,'list',root,lambda:meta.view(root))
        sample(results,'detail',root,lambda:transaction.Snapshot(root,'pz-sample-a').delivery)
        assert sample(results,'no-op',root,lambda:reg.integrate(a,root,apply=True))['status']=='no-op'
        assert sample(results,'completion',root,lambda:reg.reached(a,root))
        operation = [{'op':'set_metadata','id':'pz-sample-a','name':'Measured'}]
        plan=sample(results,'edit-plan',root,lambda:meta.plan(root,operation))
        sample(results,'edit-apply',root,lambda:meta.apply(root,plan))
        assert meta.MetadataView(root).lookup('pz-sample-a')['name']=='Measured'
    out=Path.cwd().parent / ('measurement-'+stage+'.json')
    out.write_bytes((json.dumps(results,sort_keys=True,indent=2)+'\n').encode())
    for k,v in results.items(): print(k,round(v['seconds'],3),sum(v['catalog_read_calls'].values()),len(v['net_changed_files_bytes']))
if __name__=='__main__': main(sys.argv[1])
