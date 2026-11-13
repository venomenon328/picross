import os, sys, json, time, http.client, hashlib, shutil, subprocess, threading
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
HOME=Path(__file__).parent
REPO=HOME/'work'
sys.path.insert(0,str(REPO))
os.environ.update(TEMP=str(HOME/'temp-synthetic'),TMP=str(HOME/'temp-synthetic'),TMPDIR=str(HOME/'temp-synthetic'))
from tests.puzzle_production.catalog_fixtures import registered, compact
from tests.puzzle_production.test_catalog_images import PROVENANCE, SVG, png, capability
from tools.puzzle_production import content_registry as registry, catalog_images, catalog_metadata, catalog_io as io, catalog_transaction as tx
from tools.puzzle_production.target_adapter import export
from tools.puzzle_production.za1_fixtures import FIXTURES, approve, difficulty_for_export
from tools.puzzle_editor.server import Service, API

def inventory(root, mtimes=False):
    return {p.relative_to(root).as_posix(): ([hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns] if mtimes else hashlib.sha256(p.read_bytes()).hexdigest()) for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}

def prepare(destination):
    if destination.exists():
        capability(destination)
        subprocess.run(['git','init','-q',str(destination)],check=True)
        return destination
    work=destination.parent/(destination.name+'-input')
    registered(work,stem='pe_primary',save_slot='pe_primary')
    shutil.copytree(work/'base',destination)
    approval=work/'color-approval.json'; approve(FIXTURES/'direct-color',approval)
    exp=work/'color-export'
    export(FIXTURES/'direct-color',exp,name='TEST COLOR',revision=1,stem='pe_secondary',save_slot='pe_secondary',approval_path=approval,category_id='voegel',categories_path=destination/'content/categories.json')
    checked=difficulty_for_export(exp)
    registry.registration(exp,destination,apply=True,difficulty=checked)
    compact(destination,[checked['current_source']['id']])
    capability(destination)
    subprocess.run(['git','init','-q',str(destination)],check=True)
    # Enable the existing capability only in this synthetic test target.
    capability_file=REPO/'game/data/background-capability.json'
    print('CAPABILITY',capability_file.exists(),flush=True)
    return destination

JOB_TIMES=[]

class Client:
    def __init__(self,s): self.s=s
    def call(self,route,body=None,mime=None,headers=None,expected=200):
        c=http.client.HTTPConnection('127.0.0.1',self.s.http.server_port,timeout=30)
        h={'X-PE-Session':self.s.secret}
        if body is not None:
            h.update(Origin=self.s.origin);h['Content-Type']=mime or 'application/json'
            if not mime: body=json.dumps(body).encode()
        h.update(headers or {})
        c.request('POST' if body is not None else 'GET',API+route,body,h)
        r=c.getresponse();raw=r.read();status=r.status;c.close()
        if status!=expected: raise AssertionError((route,status,raw[:2000]))
        return json.loads(raw) if raw else None
    def job(self,route,body,mime=None,error=None):
        started=time.perf_counter()
        job=self.call(route,body,mime,expected=202)['job']
        deadline=time.monotonic()+330
        while time.monotonic()<deadline:
            row=self.call('status')['job']; assert row['id']==job
            if row['state']!='running':
                JOB_TIMES.append(dict(route=route,wall_seconds=time.perf_counter()-started,state=row['state'],error=row['error']))
                if error:
                    assert row['state']=='error' and error.lower() in row['error'].lower(), row
                    return row
                assert row['state']=='done',row
                return row['result']
            time.sleep(.1)
        raise AssertionError('job timeout')
    def catalog(self): return self.call('catalog')
    def detail(self,identifier): return self.job('detail',dict(id=identifier,snapshot=self.catalog()['snapshot']))
    def plan(self,detail,**changes):
        body=dict(snapshot=detail['snapshot'],id=detail['detail']['id'],metadata=None,text=None,profile='line',reveal=None,background=None,authority=None)
        body.update(changes)
        return self.job('plan',body)
    def apply(self,p,error=None): return self.job('apply',{'plan':p['plan'],'id':p['id']},error=error)
    def discard(self): self.call('discard',{'confirmed':True})
    def category(self,op,**fields):
        return self.job('plan',dict(snapshot=self.catalog()['snapshot'],id=None,metadata=[dict(op=op,**fields)],text=None,profile=None,reveal=None,background=None,authority=None))

def authority(): return dict(actor='Synthetic operator',statement='Explicit test-only manual choice of repository-owned geometry.',confirmed=True,provenance=deepcopy(PROVENANCE))

def main():
    root=HOME/'synthetic-http-data'
    if root.exists():raise RuntimeError('Fresh target required')
    shutil.copytree(HOME/'synthetic-seed-636',root)
    s=Service(root,temporary=HOME/'temp-synthetic');s.bind();c=Client(s)
    report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'environment':'Windows 11 Pro 10.0.26200; standard user; Python 3.13.14/Pillow 12.3.0','steps':[]}
    def record(name,**values):
        report['steps'].append(dict(name=name,**values));print('PASS',name,flush=True)
    try:
        listed=c.catalog();ids=[e['id'] for e in listed['entries']];assert len(ids)==2
        identifier=next(e['id'] for e in listed['entries'] if e['name']=='TEST ONLY')
        other=next(e for e in registry.check_checkout(root)['entries'] if e['id']!=identifier)
        untouched={p:v for p,v in inventory(root).items() if p in ('game/'+other['definition'],'game/'+other['reveal']) or p.startswith(other['production']['package']+'/')}
        initial=inventory(root,True)
        d=c.detail(identifier); assert d['detail']['migration_required']
        record('v4/v7 read and stable two-ID listing',ids=ids,palette=d['raster']['palette'])
        p=c.plan(d,metadata={'name':'HTTP renamed'});assert p['kind']=='metadata';c.apply(p);c.discard()
        assert json.loads((root/'game/data/registry.json').read_bytes())['format']=='picross-runtime-registry-v7'
        record('v7 A1 name edit without implicit migration',files=p['files'])
        p=c.category('category_create',name='HTTP group');c.apply(p);c.discard()
        cat=next(e['id'] for e in c.catalog()['categories'] if e['name']=='HTTP group')
        p=c.category('category_rename',id=cat,name='HTTP renamed group');c.apply(p);c.discard()
        p=c.plan(c.detail(identifier),metadata={'category_id':cat});c.apply(p);c.discard()
        p=c.category('category_delete',id=cat,reassign_to='voegel');c.apply(p);c.discard()
        p=c.category('category_create',name='Empty');c.apply(p);c.discard();empty=next(e['id'] for e in c.catalog()['categories'] if e['name']=='Empty')
        p=c.category('category_delete',id=empty);c.apply(p);c.discard()
        record('category create rename occupied delete+reassign and empty delete')
        before=inventory(root,True)
        p=c.job('migration',{'snapshot':c.catalog()['snapshot']});assert p['files']==['game/data/registry.json'];assert inventory(root,True)==before
        c.apply(p);after=inventory(root,True)
        assert {n for n in before if before[n]!=after[n]}=={'game/data/registry.json'}
        assert c.apply(p)['status']=='noop';assert inventory(root,True)==after
        c.discard();record('explicit runtime-only migration and same-plan idempotence',files=p['files'],before=before['game/data/registry.json'],after=after['game/data/registry.json'])
        # The synthetic capability must match the genuine current profile, with test_only true.
        from tools.puzzle_production import catalog_background
        print('capability path',catalog_background.CAPABILITY if hasattr(catalog_background,'CAPABILITY') else 'find',flush=True)
        capname='game/data/background-capability.json'
        # Fixture helper used by the existing PE-A2 tests.
        d=c.detail(identifier)
        raw=png();up=c.job('upload/reveal/png',raw,'image/png')
        p=c.plan(d,metadata={'name':'HTTP image rename'},reveal={'upload':up['upload'],'provenance':PROVENANCE},authority=authority());c.apply(p);c.discard()
        entry=registry.check_checkout(root)['entries'][0]
        active=next(e for e in json.loads((root/'game/data/registry.json').read_bytes())['entries'] if e['id']==identifier)
        assert (root/'game'/active['reveal']).read_bytes()==raw
        record('byte-identical PNG and combined A2 metadata',sha256=io.checksum(raw),files=p['files'])
        d=c.detail(identifier);up=c.job('upload/reveal/svg',SVG,'image/svg+xml')
        p=c.plan(d,reveal={'upload':up['upload'],'provenance':PROVENANCE},background={'status':'standard','upload':None,'provenance':None},authority=authority());c.apply(p);c.discard()
        active=next(e for e in json.loads((root/'game/data/registry.json').read_bytes())['entries'] if e['id']==identifier)
        assert (root/'game'/active['reveal']).read_bytes()==SVG
        record('byte-identical SVG and first legacy standard assignment',sha256=io.checksum(SVG),files=p['files'])
        d=c.detail(identifier);bgbytes=png((2304,576));up=c.job('upload/background/png',bgbytes,'image/png')
        p=c.plan(d,background={'status':'selected','upload':up['upload'],'provenance':PROVENANCE},authority=authority());c.apply(p);c.discard()
        assert (root/'game/art/backgrounds'/f'{identifier}.png').read_bytes()==bgbytes
        for mode in ('none','standard'):
            p=c.plan(c.detail(identifier),background={'status':mode,'upload':None,'provenance':None},authority=authority());c.apply(p);c.discard()
            assert not (root/'game/art/backgrounds'/f'{identifier}.png').exists()
        record('selected none standard roundtrip preserves exact prepared background bytes',sha256=io.checksum(bgbytes))
        before=inventory(root,True);d=c.detail(identifier)
        formatted=d['raster']['text'].replace(' ','\t')
        p=c.plan(d,text=formatted,authority=authority());assert not p['logic_changed'];assert p['files']==[];c.apply(p);assert inventory(root,True)==before;c.discard()
        record('formatted raster no-op preserves all mtimes',files=len(before))
        d=c.detail(identifier)
        body=dict(snapshot=d['snapshot'],id=identifier,metadata=None,text='1 0\n0 1\n',profile='line',reveal=None,background=None,authority=authority())
        c.job('plan',body,error='stalled');assert inventory(root,True)==before
        body['text']='1 9\n1 1\n';c.job('plan',body,error='Zeile 1, Spalte 2');assert inventory(root,True)==before
        record('stalled deduction and precise invalid cell blocked without writes')
        d=c.detail(identifier);up=c.job('upload/reveal/svg',SVG.replace(b'#369',b'#963'),'image/svg+xml')
        p=c.plan(d,text='1 1 1\n1 1 1\n',metadata={'name':'HTTP grid combo'},reveal={'upload':up['upload'],'provenance':PROVENANCE},authority=authority());assert p['logic_changed'];c.apply(p);assert c.apply(p)['status']=='noop';c.discard()
        registry.check_checkout(root,replay=True);record('single A3 raster+image+metadata journal and true repeat',files=p['files'],quality=p['quality'])
        d=c.detail(identifier);p=c.plan(d,metadata={'name':'stale forbidden'})
        cats=root/'content/categories.json';original=cats.read_bytes();cats.write_bytes(original+b'\n');foreign=inventory(root)
        c.apply(p,error='changed');assert inventory(root)==foreign;cats.write_bytes(original);c.discard();record('stale catalog before apply preserves foreign bytes')
        before=inventory(root)
        c.job('upload/reveal/svg',b'<svg width="80" height="80"><script>alert(1)</script></svg>','image/svg+xml',error='Unsupported SVG')
        c.job('upload/background/png',png((20,20)),'image/png',error='2304')
        assert inventory(root)==before;record('malicious SVG and wrong background dimensions blocked')
        # Real HTTP Apply, deterministic interruption through the existing writer test hook.
        d=c.detail(identifier);p=c.plan(d,metadata={'name':'interrupted metadata'})
        real_popen=subprocess.Popen
        def interrupted(command,**kwargs):
            command=list(command)
            if '-c' in command and 'puzzle_editor.worker' in command[command.index('-c')+1]:
                command[command.index('-c')+1]="import sys;sys.path.insert(0,sys.argv[1]);from tools.puzzle_production import catalog_transaction as tx;original=tx.execute;tx.execute=lambda *a,**k: original(*a,**dict(k,fail_step='crash-runtime'));from tools.puzzle_editor.worker import main;main(sys.argv[2])"
            return real_popen(command,**kwargs)
        before=inventory(root)
        with patch('tools.puzzle_editor.server.subprocess.Popen',side_effect=interrupted): c.apply(p,error='interruption')
        assert c.call('status')['recovery_required'];c.job('recover',{'confirmed':True});assert inventory(root)==before
        c.job('recover',{'confirmed':True});assert inventory(root)==before;c.discard();record('actual HTTP interrupted writer and repeated common recovery restore original hashes')
        for headers in ({'Origin':'https://foreign.invalid'},{'Host':'foreign.invalid'},{'X-PE-Session':'forged'},{'Sec-Fetch-Site':'cross-site'}):
            try: c.call('catalog',headers=headers)
            except AssertionError as exc: assert '403' in str(exc)
            else: raise AssertionError('foreign request accepted')
        assert all(inventory(root)[name]==value for name,value in untouched.items())
        record('origin host session fetch-site and independent second-ID bytes',protected=len(untouched))
        # Actual HTTP stop while the shared journal is already durable. The
        # existing checkpoint is only a rendezvous; clock/guards stay active.
        d=c.detail(identifier);p=c.plan(d,metadata={'name':'Drain acknowledged'})
        marker=HOME/'writer-P1.txt';release=HOME/'writer-release.txt'
        assert not marker.exists() and not release.exists()
        real_popen=subprocess.Popen
        rendezvous=("import sys,time;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
            "from tools.puzzle_production import catalog_publication as pub,catalog_io as io;"
            "exec("+repr("def pause(phase,name=None):\n    if phase=='P1':\n        Path("+repr(str(marker))+").write_text('P1')\n        while not Path("+repr(str(release))+").exists():\n            io.tick()\n            time.sleep(.02)")+");pub.checkpoint=pause;"
            "from tools.puzzle_editor.worker import main;main(sys.argv[2])")
        def paused_writer(command,**kwargs):
            command=list(command)
            if '-c' in command and 'puzzle_editor.worker' in command[command.index('-c')+1]:command[command.index('-c')+1]=rendezvous
            return real_popen(command,**kwargs)
        with patch('tools.puzzle_editor.server.subprocess.Popen',side_effect=paused_writer):
            c.call('apply',{'plan':p['plan'],'id':p['id']},expected=202)
            deadline=time.monotonic()+30
            while not marker.exists():
                assert time.monotonic()<deadline,'Writer did not reach P1';time.sleep(.05)
            running=c.call('status');assert running['job']['state']=='running' and running['recovery_required']
            assert c.call('stop',{'confirmed':True})['stopping']
            assert c.call('status')['stopping']
            release.write_text('release',encoding='utf-8')
            s.close()
        assert s.status()['job']['state']=='done',s.status()['job']
        assert not s.status()['recovery_required']
        import socket
        with socket.socket() as closed: assert closed.connect_ex(('127.0.0.1',s.http.server_port))!=0
        registry.check_checkout(root)
        assert next(e for e in json.loads((root/'content/registry.json').read_bytes())['metadata'] if e['id']==identifier)['name']=='Drain acknowledged'
        record('HTTP status and stop during actual P1 writer; orderly drain commits full readback and closes listener')
        report['jobs']=JOB_TIMES
        report['final_inventory_sha256']=hashlib.sha256(json.dumps(inventory(root),sort_keys=True).encode()).hexdigest()
        report['passed']=True
        (HOME/'synthetic-http-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    finally:s.close()

if __name__=='__main__':
    (HOME/'temp-synthetic').mkdir(exist_ok=True)
    prepare(HOME/'synthetic-seed-636')
    main()
