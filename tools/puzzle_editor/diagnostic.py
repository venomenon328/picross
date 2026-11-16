"""PE-APP-B T02/T03: source-side data preparation, actual frozen worker/MSI bytes.

Excluded from PYZ and method data. No real content, installation or publication.
"""
import argparse
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import threading
import sys
from types import SimpleNamespace
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
        unrelated=root/'game/data/content/unrelated.json'; unrelated.write_bytes(b'not a selected definition')
        identifier=json.loads((root/'content/registry.json').read_bytes())['entries'][0]['id']
        def snapshot():
            return edit.token({name:(root/name).read_bytes() for name in edit.INDEXES})
        def detail(): return call('detail',{'id':identifier,'snapshot':snapshot()})
        def plan(**changes):
            request={'id':identifier,'metadata':None,'text':None,'profile':None,'reveal':None,'background':None,**changes}
            return call('plan',{'request':request,'uploads':uploads,'catalog_snapshot':snapshot()})
        def apply(value):
            before={p.relative_to(root).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
            result=call('apply',{'plan_hash':value['plan_hash']})
            for name,previous in before.items():
                if name not in value['files']:
                    p=root/name
                    require(p.exists() and (p.read_bytes(),p.stat().st_mtime_ns)==previous,'Unrelated bytes/mtime changed: '+name)
            return result
        uploads={}
        try:
            original=detail();require(original['raster']['revision']==1,'Unexpected initial revision')
            apply(plan(metadata={'name':'Frozen PE','category_id':'voegel'}))
            before={p.relative_to(root).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
            require(apply(plan(metadata={'name':'Frozen PE','category_id':'voegel'}))['status']=='noop','Metadata noop failed')
            require(before=={p.relative_to(root).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()},'Noop changed bytes/mtime')
            stream=BytesIO();Image.new('RGBA',(128,128),(20,60,90,128)).save(stream,format='PNG');reveal=stream.getvalue()
            (work/'reveal.png').write_bytes(reveal)
            checked=call('validate_upload',{'file':'reveal.png','kind':'reveal'})
            uploads={'reveal':{'file':'reveal.png','sha256':checked['sha256']}}
            apply(plan(reveal={'upload':'reveal'}))
            current=detail()
            require((root/'game'/current['detail']['reveal']['file']).read_bytes()==reveal,'Reveal import changed bytes')
            uploads={}
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
        return {'calls':calls,'reader_metadata_noop':True,'reveal_byte_equal':True,'unrelated_bytes_mtimes_preserved':True,'both_profiles_byte_equal':True,
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
    with patch.object(verifier,'production_trust',return_value=trust):
        plan=channel.plan(api,Path(__file__).resolve().parents[2],api.source,9,app=PE)
        require(plan['payload_fingerprint']==provenance['payload_fingerprint'],'Plan differs from real build')
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
    a,b,c=InstallInterlock(app=PE),InstallInterlock(app=PW),InstallInterlock(app=PE)
    try:
        b.acquire();require(invoke()==0,'PE guard incorrectly blocks on PW')
        a.acquire();require(invoke()==2,'PE guard accepted a running PE')
        c.acquire();a.close();require(invoke()==2,'Other PE instance lost protection')
        c.close();require(invoke()==0,'PE guard did not release')
    finally: a.close();b.close();c.close()
    return {'actual_guard_running_pe_refused':True,'parallel_pw_allowed':True,'no_installation':True}


def preview_resources(build):
    image=build/'dist'/PE.executable/'_internal'
    paper=image/'game/book/paper.png'
    with Image.open(paper) as raster:
        raster.load();require(raster.width>0 and raster.height>0,'Missing paper pixels')
    config=json.loads((image/'game/book/paper.json').read_bytes())
    margins=list((image/'game/art/drawing/margins').glob('*'))
    require(config and margins,'Missing preview configuration/margins')
    decoded=[]
    for path in margins:
        if path.suffix=='.png':
            with Image.open(path) as raster: raster.load()
            decoded.append(path.name)
    for name in ('index.html','app.js','style.css'):
        require((image/'tools/puzzle_editor/ui'/name).stat().st_size>0,'Missing preview UI')
    return {'paper_decoded':True,'margin_pngs_decoded':decoded,'ui_present':True,
            'limits':'Technical resource checks only; actual browser appearance remains R01/U01.'}


def native_ready(state, commit):
    """Source-only installed-identity adapter; actual Tk and production IPC code."""
    from . import desktop
    from tools.production_workspace import update_windows as windows, app_updates
    identity=SimpleNamespace(commit=commit,executable=state.parent/"program/editor.exe",version="0.2.1")
    original=desktop.Window.__init__
    windows_seen=[]
    def opened(window,*a,**kw):
        original(window,*a,**kw); windows_seen.append(window)
        window.window.after(1800,lambda:window.close(confirmed=True))
    with (patch.object(windows,"installation",return_value=identity),
          patch.object(app_updates,"production_trust",return_value={"accepted":{}}),
          patch.object(desktop.Window,"__init__",opened),
          patch.object(desktop.webbrowser,"open") as browser,
          patch.object(sys,"argv",["diagnostic","--state",str(state)])):
        desktop.main()
        require(len(windows_seen)==1 and windows_seen[0].service is None and not windows_seen[0].ready_error,"Native window/ready failed")
        browser.assert_not_called()
    print("native-ready-without-service")


def native_cases(output):
    from tests.puzzle_production.catalog_fixtures import registered
    from . import desktop
    desktop.load_ui()
    from tools.production_workspace import update_windows as windows, app_updates, update_client as client
    from tools.production_workspace.update_storage import Preferences
    with tempfile.TemporaryDirectory(prefix="native-",dir=output) as folder:
        home=Path(folder); registered(home/"fixture",stem="native",save_slot="native")
        root=home/"fixture/base"; (root/".git").mkdir(exist_ok=True)
        identity=SimpleNamespace(commit="a"*40,version="0.2.0",executable=home/"program/editor.exe")
        for mode in ("consent","offline","skip"):
            state=home/mode
            if mode!="consent": Preferences(state/".updates").write(True)
            entered,release=threading.Event(),threading.Event()
            def discover(*a,**kw):
                entered.set()
                if mode=="skip": require(release.wait(10),"Native skip hung")
                raise client.Cancelled() if mode=="skip" else OSError("synthetic offline")
            with (patch.object(windows,"installation",return_value=identity),
                  patch.object(app_updates,"production_trust",return_value={"accepted":{"synthetic":{}}}),
                  patch.object(client,"discover",side_effect=discover) as network,
                  patch.object(windows,"prepare") as prepare,
                  patch.object(desktop.messagebox,"showerror",side_effect=lambda title,message,**kw: (_ for _ in ()).throw(ValueError(title+": "+message))),
                  patch.object(desktop.webbrowser,"open") as browser):
                window=desktop.Window(state,str(root),0)
                try:
                    window.window.update()
                    window.start(); window.open()
                    require(window.service is None,"Start gate failed")
                    browser.assert_not_called()
                    if mode=="consent":
                        network.assert_not_called(); window.choose_updates(False)
                    elif mode=="skip":
                        require(entered.wait(5),"No controlled check"); window.skip_update()
                        require(Preferences(state/".updates").read() is True,"Skip lost consent")
                        release.set()
                    if window.updates.updates.thread: window.updates.updates.thread.join(10)
                    deadline=time.monotonic()+5
                    while window.updates.waiting and time.monotonic()<deadline:
                        window.window.update(); time.sleep(.02)
                    window.start()
                    require(window.service is not None,"Explicit native start failed")
                    first=window.service; window.start()
                    require(window.service is first,"Double native start")
                    browser.assert_called_once(); prepare.assert_not_called()
                    require(network.call_count==(0 if mode=="consent" else 1),"Network attempt count changed")
                finally:
                    release.set(); window.close(confirmed=True)
                    window.window.mainloop()
                    window.drain_thread.join()
                    if window.ready_thread: window.ready_thread.join()
                    window.updates.finish(window.stop_error)
                require(not window.stop_error and not first.work.exists(),"Native service did not drain/clean")
    return {"actual_tk_windows":3,"explicit_consent_before_network":True,"offline_released":True,
            "skip_preserved_optin":True,"manual_service_started_exactly_once":True,"browser_stubbed":True,
            "actual_service_http_drain":True,"limits":"Source identity adapter outside product; real native controls/service, no installed-app claim."}


def run(build,output):
    require(not output.exists(),'Use a new diagnosis directory');output.mkdir(parents=True)
    delivery=json.loads((build/'delivery.json').read_bytes())
    result={'format':'picross-pe-diagnostic-v1','source_commit':delivery['commit'],
            'payload_fingerprint':delivery['payload_fingerprint'],'version':delivery['version']}
    for name, operation in (("frozen",lambda:frozen(build,output)),("signatures",lambda:signatures(build,output)),
                            ("guards",lambda:guards(build)),("preview_resources",lambda:preview_resources(build)),
                            ("native",lambda:native_cases(output))):
        print("PE-APP-B diagnosis: "+name,flush=True)
        result[name]=operation()
    (output/'result.json').write_bytes(canonical(result));print(canonical(result).decode())
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--native-ready',action='store_true');p.add_argument('--state',type=Path);p.add_argument('--commit')
    a=p.parse_args()
    if a.native_ready: native_ready(a.state,a.commit)
    else: run(a.build,a.output)
