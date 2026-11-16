"""PE-APP-A T02/T03: source-side data preparation, actual frozen worker/MSI bytes.

Excluded from PYZ and method data. No real content, installation or publication.
"""
import argparse
import base64
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from unittest.mock import patch

from PIL import Image
from tools.app_products import PE, PW
from tools.production_workspace import release_channel as channel, update_verifier as verifier
from tools.production_workspace.payload import canonical
from tools.production_workspace.update_diagnostic import test_identity
from tools.production_workspace.install_interlock import InstallInterlock


def require(value,message):
    if not value: raise ValueError(message)


def frozen(build, output):
    from tests.puzzle_production.catalog_fixtures import registered
    from tools.puzzle_production import editor_change as edit, catalog_background as bg
    exe=build/'dist'/PE.executable/(PE.executable+'.exe')
    with tempfile.TemporaryDirectory(prefix='frozen-',dir=output) as folder:
        home=Path(folder);registered(home/'fixture',stem='peapp',save_slot='peapp')
        root=home/'fixture/base'; work=home/'requests';work.mkdir()
        # Data fixture contains no executable code or historical archives.
        require(not list(root.rglob('*.py')),'Fixture includes code')
        environment={**os.environ,'PYTHONPATH':'','PYTHONHOME':'','PATH':os.environ['SystemRoot']+'\\System32',
                     'TEMP':str(home),'TMP':str(home)}
        process=subprocess.Popen([str(exe),'--session',str(work)],stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=home,env=environment,
            creationflags=subprocess.CREATE_NO_WINDOW)
        calls=[]
        def call(action,body,expected_error=False):
            result=work/'result.json';result.unlink(missing_ok=True)
            job={'root':str(root),'work':str(work),'action':action,'body':body}
            (work/'job.json').write_bytes(canonical(job))
            process.stdin.write((str(work/'job.json')+'\n').encode());process.stdin.flush()
            deadline=time.monotonic()+330
            while not result.exists():
                require(process.poll() is None,'Actual frozen worker exited: '+str(process.returncode))
                require(time.monotonic()<deadline,'Frozen worker timeout');time.sleep(.05)
            value=json.loads(result.read_bytes());calls.append({'action':action,'error':value['error']})
            require(bool(value['error'])==expected_error,'Unexpected frozen result: '+str(value['error']))
            return value['result']
        identifier=json.loads((root/'content/registry.json').read_bytes())['entries'][0]['id']
        def snapshot():
            return edit.token({name:(root/name).read_bytes() for name in edit.INDEXES})
        def detail(): return call('detail',{'id':identifier,'snapshot':snapshot()})
        def plan(**changes):
            request={'id':identifier,'metadata':None,'text':None,'profile':None,'reveal':None,'background':None,**changes}
            return call('plan',{'request':request,'uploads':uploads,'catalog_snapshot':snapshot()})
        def apply(value): return call('apply',{'plan_hash':value['plan_hash']})
        uploads={}
        try:
            original=detail();require(original['raster']['revision']==1,'Unexpected initial revision')
            apply(plan(metadata={'name':'Frozen PE','category_id':'voegel'}))
            before={p.relative_to(root).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
            require(apply(plan(metadata={'name':'Frozen PE','category_id':'voegel'}))['status']=='noop','Metadata noop failed')
            require(before=={p.relative_to(root).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()},'Noop changed bytes/mtime')
            for height in (576,768):
                image=Image.new('RGBA',(2304,height),(0,0,0,0));image.putpixel((30,height-30),(60,60,60,128))
                stream=BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
                (work/'background.png').write_bytes(raw)
                checked=call('validate_upload',{'file':'background.png','kind':'background'})
                require(checked['height']==height,'Wrong profile geometry')
                uploads={'background':{'file':'background.png','sha256':checked['sha256']}}
                request={'id':identifier,'metadata':None,'text':None,'profile':None,'reveal':None,
                         'background':{'status':'selected','upload':'background'}}
                if height==768:
                    call('plan',{'request':request,'uploads':uploads,'catalog_snapshot':snapshot()},expected_error=True)
                    (root/bg.CAPABILITY).write_bytes(canonical({'format':'picross-runtime-background-capability-v2',
                        'runtime_format':'picross-runtime-registry-v8','profile_ids':['picross-background-png2304-v1','picross-background-png2304x768-v1'],'enabled':True}))
                apply(plan(background=request['background']))
                require((root/bg.asset_path(identifier)).read_bytes()==raw,'Background import changed original bytes')
                require(not (root/bg.asset_path(identifier)).with_suffix('.txt').exists(),'Unexpected optional background TXT')
                detail()
                uploads={}
                for status in ('none','standard'): apply(plan(background={'status':status,'upload':None}));detail()
            uploads={}
            same=detail()['raster']['text']
            require(not plan(text=same,profile='line')['files'],'Same raster not noop')
            apply(plan(text='1 1 1\n0 0 0',profile='line'))
            require(detail()['raster']['revision']==2,'Raster revision did not increase exactly once')
        finally:
            if process.poll() is None:
                process.stdin.write(b'stop\n');process.stdin.flush();process.stdin.close()
                process.wait(timeout=30)
        require(process.returncode==0,'Frozen worker did not stop cleanly')
        return {'calls':calls,'reader_metadata_noop':True,'both_profiles_byte_equal':True,
                'capability_boundary':True,'optional_txt_absent':True,'raster_revision':2,
                'limits':'Actual frozen worker; browser rendering and personal Windows installation remain R01/U01.'}


def signatures(build, output):
    from tools.test_production_installer import MemoryGitHub
    provenance=json.loads((build/'manifest.json').read_bytes())
    files={n:(build/n).read_bytes() for n in provenance['assets']}
    trust,secret=test_identity(app=PE)
    raw,sig=verifier._sign(provenance,files,secret,trust,app=PE)
    candidate=verifier._verify(raw,sig,files,trust,app=PE)
    msi=next(n for n in files if n.endswith('.msi'))
    for action in (lambda:verifier._verify(raw,sig,{**files,msi:files[msi]+b'bad'},trust,app=PE),
                   lambda:verifier._verify(raw,sig,files,trust,app=PW),
                   lambda:verifier.verify_candidate(raw,sig,files,app=PE)):
        try: action()
        except ValueError: pass
        else: raise ValueError('Negative signature case accepted')
    api=MemoryGitHub(app=PE);api.source=provenance['source_commit'];api.run['head_sha']=api.source
    plan={'source_commit':api.source,'run_id':9,'run_attempt':1,'version':provenance['version'],
          'payload_fingerprint':provenance['payload_fingerprint'],'authority':None,'diagnostic':False,
          'trust_sha256':channel.digest(canonical(trust))}
    with patch.object(verifier,'production_trust',return_value=trust):
        api.fail_upload='START.txt'
        try: channel.publish(api,build,plan,enabled=True,signing_enabled=True,secret=secret,app=PE)
        except RuntimeError: pass
        else: raise ValueError('Expected lost synthetic upload response')
        channel.publish(api,build,plan,enabled=True,signing_enabled=True,secret=secret,app=PE)
        previous=channel.authority(api,app=PE)
        require(channel.next_version({'sha256':plan['payload_fingerprint']},previous,app=PE) is None,'Identical payload not noop')
        require(channel.next_version({'sha256':'changed'},previous,app=PE)=='0.2.2','Next patch incorrect')
    del secret
    for name,value in [('test-manifest.json',raw),('test-signature.json',sig),('public-test-trust.json',canonical(trust))]:
        (output/name).write_bytes(value)
    return {'msi_sha256':candidate.msi_sha256,'manifest_sha256':candidate.binding,
            'actual_bytes_signed':True,'partial_upload_resume':True,'unchanged_noop':True,
            'tampered_foreign_and_production_testroot_rejected':True,'publication':'Synthetic memory API only'}


def guards(build):
    target=Path(os.environ['LOCALAPPDATA'])/'Programs'/PE.install_directory
    require(not target.exists(),'Existing user PE installation is protected; use an isolated Windows profile')
    guard=build/'work/Guard.exe'
    def invoke(): return subprocess.run([str(guard),str(target)],creationflags=subprocess.CREATE_NO_WINDOW).returncode
    require(invoke()==0,'Unoccupied PE guard failed')
    a,b=InstallInterlock(app=PE),InstallInterlock(app=PW)
    try:
        b.acquire();require(invoke()==0,'PE guard incorrectly blocks on PW')
        a.acquire();require(invoke()==2,'PE guard accepted a running PE')
        a.close();require(invoke()==0,'PE guard did not release')
    finally: a.close();b.close()
    return {'actual_guard_running_pe_refused':True,'parallel_pw_allowed':True,'no_installation':True}


def run(build,output):
    require(not output.exists(),'Use a new diagnosis directory');output.mkdir(parents=True)
    delivery=json.loads((build/'delivery.json').read_bytes())
    result={'format':'picross-pe-diagnostic-v1','source_commit':delivery['commit'],
            'payload_fingerprint':delivery['payload_fingerprint'],'version':delivery['version'],
            'frozen':frozen(build,output),'signatures':signatures(build,output),'guards':guards(build)}
    (output/'result.json').write_bytes(canonical(result));print(canonical(result).decode())
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.build,a.output)
