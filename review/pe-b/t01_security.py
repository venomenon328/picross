import os,sys,json,subprocess,shutil,time
from pathlib import Path
from unittest.mock import patch
H=Path(__file__).parent;sys.path.insert(0,str(H/'repo'))
from t01 import Client,inventory,authority
from tools.puzzle_editor.server import Service
from tests.puzzle_production.test_catalog_images import SVG,PROVENANCE,png

def main():
    root=H/'t01-security-delivery'
    if not root.exists():shutil.copytree(H/'synthetic-seed',root)
    s=Service(root,temporary=H/'temp');s.bind();c=Client(s)
    report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=H/'repo',text=True).strip(),'steps':[]}
    def record(text):report['steps'].append(text);print('PASS',text,flush=True)
    identifier='pz-test-direct-mono'
    try:
        p=c.job('migration',{'snapshot':c.catalog()['snapshot']});c.apply(p);c.discard()
        before=inventory(root,True)
        d=c.detail(identifier);up=c.job('upload/reveal/svg',SVG,'image/svg+xml')
        try:c.plan(d,reveal={'upload':up['upload'],'provenance':{**PROVENANCE,'usage_basis':''}},authority=authority())
        except AssertionError as e:assert 'declaration' in str(e).lower(),e
        else:raise AssertionError('missing rights accepted')
        assert inventory(root,True)==before;c.discard();record('missing actual usage basis blocks plan with all checkout bytes and mtimes unchanged')
        d=c.detail(identifier);up=c.job('upload/reveal/svg',SVG,'image/svg+xml')
        p=c.plan(d,reveal={'upload':up['upload'],'provenance':PROVENANCE},authority=authority())
        upload=s.uploads[up['upload']];file=s.work/upload['file'];file.write_bytes(file.read_bytes()+b'\n')
        c.call('apply',{'plan':p['plan'],'id':identifier},expected=409);assert inventory(root,True)==before;c.discard();record('changed uploaded bytes block apply before mutation')
        d=c.detail(identifier);p=c.plan(d,metadata={'name':'bundle stale'})
        file=Path(s.plans[p['plan']]['work'])/'plan.json';file.write_bytes(file.read_bytes()+b'\n')
        c.call('apply',{'plan':p['plan'],'id':identifier},expected=409);assert inventory(root,True)==before;c.discard();record('changed bound plan bundle blocks apply before mutation')
        d=c.detail(identifier);p=c.plan(d,metadata={'name':'expired'})
        s.plans[p['plan']]['expires']=time.monotonic()-1
        c.call('apply',{'plan':p['plan'],'id':identifier},expected=409);assert inventory(root,True)==before;c.discard();record('expired plan rejected and own plan bytes removed')
        d=c.detail(identifier);p=c.plan(d,metadata={'name':'upload superseded'})
        c.job('upload/reveal/svg',SVG,'image/svg+xml')
        c.call('apply',{'plan':p['plan'],'id':identifier},expected=409);assert inventory(root,True)==before;c.discard();record('later upload invalidates earlier plan')
        # Stage is produced by the actual writer; interruption precedes journal rename.
        p=c.plan(c.detail(identifier),metadata={'name':'staged interruption'})
        original=subprocess.Popen
        def injected(command,**kwargs):
            command=list(command)
            if '-c' in command and 'puzzle_editor.worker' in command[command.index('-c')+1]:
                command[command.index('-c')+1]="import sys;sys.path.insert(0,sys.argv[1]);from tools.puzzle_production import catalog_publication as pub;original=pub.rename;pub.rename=lambda a,b,**k: (_ for _ in ()).throw(InterruptedError('Injected before journal publication')) if str(b).endswith('.registration-pending.json') else original(a,b,**k);from tools.puzzle_editor.worker import main;main(sys.argv[2])"
            return original(command,**kwargs)
        with patch('tools.puzzle_editor.server.subprocess.Popen',side_effect=injected):c.apply(p,error='before journal')
        assert c.call('status')['recovery_required']
        c.job('recover',{'confirmed':True});c.job('recover',{'confirmed':True});assert inventory(root)=={k:v[0] for k,v in before.items()};c.discard()
        record('actual pre-publication staging interruption and common recovery, including repeated no-op')
        junction=H/'t01-junction'
        import _winapi
        _winapi.CreateJunction(str(root),str(junction))
        try:
            try:Service(junction,temporary=H/'temp')
            except ValueError:pass
            else:raise AssertionError('junction root accepted')
        finally:
            assert junction.parent==H and junction.is_junction();junction.rmdir()
        record('actual Windows junction checkout rejected without following target')
        from PIL import Image
        from io import BytesIO
        stream=BytesIO();Image.new('RGBA',(2304,576),(20,30,40,255)).save(stream,format='PNG')
        c.job('upload/background/png',stream.getvalue(),'image/png',error='transparent');assert inventory(root)=={k:v[0] for k,v in before.items()}
        record('opaque prepared background rejected without content writes')
        p=c.plan(c.detail(identifier),text='1 1\n1 1\n',profile='paired',authority=authority());assert p['quality'] is not None;c.apply(p);c.discard()
        record('explicit paired profile runs actual proof/rating and applies a checked raster')
        report['passed']=True
        (H/'t01-security-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    finally:s.close()

if __name__=='__main__':main()
