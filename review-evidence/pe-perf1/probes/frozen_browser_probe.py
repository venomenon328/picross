"""Continue the already-started genuine portable EXE through headless Edge.

No desktop focus, mouse, visible browser launch or native UI Automation.
"""
from pathlib import Path
import sys,os,json,time,hashlib,http.client,threading,socket,tempfile
from urllib.parse import urlsplit
b=Path(__file__).resolve().parent;sys.path.insert(0,str(b/'work'))
private=b/'temp-frozen-browser';private.mkdir(exist_ok=True)
os.environ.update(TEMP=str(private),TMP=str(private),TMPDIR=str(private));tempfile.tempdir=str(private)
from playwright.sync_api import sync_playwright
from tools.puzzle_editor.bundle import verify
root=b/'native-final-data';session=(b/'native-session-private.txt').read_text(encoding='utf-8');url=urlsplit(session)
head=verify(b/'portable-delivery/dist/Picross-Bestandseditor')
report={'head':head,'standard_user':True,'browser_mode':'headless Edge on Windows; existing genuine portable EXE service and frozen worker processes','native_precondition':'Native Start, OS default browser, two physical ID selections and migration plan observed in native-final-report; no claim that physical Apply clicked successfully.','jobs':[],'passed':False}
out=b/'frozen-browser-report.json';sys.stdout.reconfigure(line_buffering=True,encoding='utf-8')
def save():out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def api(route,body=None):
    c=http.client.HTTPConnection(url.hostname,url.port,timeout=15)
    headers={'X-PE-Session':url.fragment,'Origin':'http://127.0.0.1:'+str(url.port),'Content-Type':'application/json'}
    c.request('GET' if body is None else 'POST','/api/pe/v1/'+route,None if body is None else json.dumps(body),headers)
    r=c.getresponse();raw=r.read();c.close();assert r.status<300,(route,r.status,raw[:200]);return json.loads(raw)
def inventory():return {p.relative_to(root).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtime_ns':p.stat().st_mtime_ns,'bytes':p.stat().st_size} for f in ('content','game/data','game/art/content','game/art/backgrounds') for p in (root/f).rglob('*') if p.is_file()}
assert Path(api('status')['checkout'])==root
assert not api('status')['recovery_required']
initial=inventory();assert json.loads((root/'game/data/registry.json').read_bytes())['format']=='picross-runtime-registry-v7'
report['initial_inventory_sha256']=hashlib.sha256(json.dumps(initial,sort_keys=True).encode()).hexdigest()
reg=json.loads((root/'content/registry.json').read_bytes());entries=sorted(reg['entries'],key=lambda e:e['production']['width']*e['production']['height']);ids=[entries[0]['id'],entries[-1]['id']]
telemetry=[];done=False
def monitor():
    seen=set()
    while not done:
        for directory in (b/'temp-native-final').glob('picross-pe-*'):
            for path in directory.glob('job-*/result.json'):
                try:
                    key=path.parent.name
                    if key in seen:continue
                    value=json.loads(path.read_bytes());job=json.loads((path.parent/'job.json').read_bytes())
                    telemetry.append({'operation':job['action'],'error':value['error'],'diagnostics':value.get('diagnostics'),'result_status':(value['result'] or {}).get('status')});seen.add(key)
                except (OSError,ValueError):pass
        time.sleep(.025)
thread=threading.Thread(target=monitor);thread.start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        report['browser']=browser.version
        context=browser.new_context(viewport={'width':1600,'height':1000},device_scale_factor=1)
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        def idle():
            end=time.monotonic()+660
            while page.locator('body.busy').count():
                assert time.monotonic()<end,'DOM operation timeout';time.sleep(.1)
        page.goto(session);idle();assert page.locator('.entry').count()==56
        def action(name,click):
            print('START',name);before=inventory();position=len(telemetry);started=time.perf_counter();stages=[]
            click();end=time.monotonic()+660
            while page.locator('body.busy').count():
                state=api('status');job=state['job']
                if job and (not stages or (job['operation'],job['stage'])!=(stages[-1]['operation'],stages[-1]['stage'])):stages.append({'operation':job['operation'],'stage':job['stage'],'elapsed_seconds':job['elapsed_seconds']})
                assert time.monotonic()<end,'DOM operation timeout';time.sleep(.15)
            wall=time.perf_counter()-started;state=api('status');assert state['job']['state']=='done',state['job']['error']
            status=page.locator('#status').inner_text();assert 'error' not in (page.locator('#status').get_attribute('class') or ''),status
            after=inventory();report['jobs'].append({'action':name,'wall_seconds':wall,'stages':stages,'ui_status':status,'worker_results':telemetry[position:],'changed':{n:{'before':before.get(n),'after':after.get(n)} for n in set(before)|set(after) if before.get(n)!=after.get(n)},'recovery_required':state['recovery_required']});save();print('END',name,round(wall,3))
            return state['job']['result']
        for i,identifier in enumerate(ids):
            action('detail-'+str(i),lambda:page.locator('.entry[data-id="'+identifier+'"]').click())
            assert page.locator('#puzzle-id').inner_text()==identifier
            assert page.locator('#name').input_value()==next(row['name'] for row in reg['metadata'] if row['id']==identifier)
            assert len(page.locator('#raster').input_value().splitlines())==entries[0 if i==0 else -1]['production']['height']
            assert page.locator('#palette .swatch').count()>=2
            assert page.locator('#reveal-pictures img').count()==1 and page.locator('#background-pictures').inner_html()
            assert inventory()==initial
        plan=action('migration-plan',lambda:page.locator('#migrate').click());assert plan['files']==['game/data/registry.json']
        assert page.locator('#puzzle-id').inner_text()==ids[-1] and inventory()==initial
        action('migration-apply-and-v8-ui-readback',lambda:page.locator('#apply').click())
        after=inventory();assert {n for n in set(initial)|set(after) if initial.get(n)!=after.get(n)}=={'game/data/registry.json'}
        assert json.loads((root/'game/data/registry.json').read_bytes())['format']=='picross-runtime-registry-v8'
        assert not page.locator('#migration').is_visible() and page.locator('#puzzle-id').inner_text()==ids[-1]
        def apijob(route,body):
            start=time.perf_counter();key=api(route,body)['job'];stages=[]
            while time.perf_counter()-start<660:
                job=api('status')['job'];assert job['id']==key
                if not stages or stages[-1]['stage']!=job['stage']:stages.append({'stage':job['stage'],'elapsed_seconds':job['elapsed_seconds']})
                if job['state']!='running':
                    assert job['state']=='done',job['error'];report['jobs'].append({'action':'api-'+route+'-recheck','wall_seconds':time.perf_counter()-start,'stages':stages});save();return job['result']
                time.sleep(.15)
            raise AssertionError('API timeout')
        recheck=apijob('migration',{'snapshot':api('catalog')['snapshot']});assert recheck['files']==[]
        assert apijob('apply',{'plan':recheck['plan'],'id':None})['status']=='noop';assert inventory()==after
        api('discard',{'confirmed':True})
        action('refresh-v8-and-selected-id',lambda:page.locator('#reload').click())
        assert page.locator('#puzzle-id').inner_text()==ids[-1]
        page.locator('#name').fill('PE PERF1 frozen isolated save')
        action('metadata-plan',lambda:page.locator('#check').click())
        action('metadata-apply-and-ui-readback',lambda:page.locator('#apply').click())
        assert next(row['name'] for row in json.loads((root/'content/registry.json').read_bytes())['metadata'] if row['id']==ids[-1])=='PE PERF1 frozen isolated save'
        assert page.locator('#name').input_value()=='PE PERF1 frozen isolated save'
        stable=inventory()
        # Native poll observes real stop; its drain thread awaits this actual
        # frozen reader. No Win32 focus or input is used for termination.
        page.locator('.entry[data-id="'+ids[0]+'"]').click()
        end=time.monotonic()+10
        while time.monotonic()<end and api('status')['job']['state']!='running':time.sleep(.05)
        assert api('status')['job']['state']=='running'
        page.once('dialog',lambda d:d.accept());page.locator('#stop').click();started=time.perf_counter()
        end=time.monotonic()+90
        while time.monotonic()<end:
            with socket.socket() as c:
                if c.connect_ex(('127.0.0.1',url.port))!=0:break
            time.sleep(.15)
        else:raise AssertionError('Frozen native app failed to drain')
        assert inventory()==stable
        report['native_stop_during_frozen_reader_seconds']=time.perf_counter()-started
        report['native_service_port_closed']=True;report['journal_absent']=not (root/'content/.registration-pending.json').exists();report['page_errors']=errors
        report['passed']=True;save();browser.close()
finally:
    done=True;thread.join(3);report['worker_diagnostics']=telemetry;save()
