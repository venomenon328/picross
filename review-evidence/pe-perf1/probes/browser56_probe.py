"""One-time real Edge DOM/service/worker test. Headless: never takes mouse/focus."""
from pathlib import Path
import sys, os, json, time, hashlib, zipfile, subprocess, ctypes, tempfile
base=Path(__file__).resolve().parent
mode=sys.argv[1]; assert mode in ('old','new','retry')
suffix=sys.argv[2] if len(sys.argv)>2 else ''
trace=mode=='old' and suffix=='-traced'
program=base/('old-program' if mode=='old' else 'work')
sys.path.insert(0,str(program))
temp=base/('temp-browser56-'+mode);temp.mkdir(exist_ok=True)
os.environ.update(TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp));tempfile.tempdir=str(temp)
from tools.puzzle_editor import server
from playwright.sync_api import sync_playwright
root=base/(('browser56-old' if mode=='retry' else 'browser56-'+mode)+suffix)
if mode=='retry':
    assert json.loads((base/('browser56-old'+suffix+'-report.json')).read_bytes())['passed']
else:
    if root.exists():raise RuntimeError('Fresh isolated copy required')
    root.mkdir()
    with zipfile.ZipFile(base/'baseline-source.zip') as z:z.extractall(root)
    (root/'.git').mkdir()
report={'mode':mode,'source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=program,text=True).strip(),'baseline_content':'4e5bfe489851fe4a4b771fcdf125fd89ce440a98','headless':True,'native_test':False,'resolution':[1600,1000],'jobs':[],'passed':False}
originals=base/'browser56-originals';originals.mkdir(exist_ok=True)
out=base/('browser56-'+mode+suffix+'-report.json')
sys.stdout.reconfigure(line_buffering=True,encoding='utf-8')
def save():out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def inventory():
    return {p.relative_to(root).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtime_ns':p.stat().st_mtime_ns,'bytes':p.stat().st_size} for f in ('content','game/data','game/art/content','game/art/backgrounds') for p in (root/f).rglob('*') if p.is_file()}
class IO(ctypes.Structure):_fields_=[(k,ctypes.c_ulonglong) for k in ('read_operations','write_operations','other_operations','read_bytes','write_bytes','other_bytes')]
processes=[];real=server.subprocess.Popen
def observe(*args,**kwargs):
    if trace and args and isinstance(args[0],list) and '-c' in args[0]:
        command=list(args[0]);position=command.index('-c')+1
        if 'puzzle_editor.worker' in command[position]:
            command[position]='import sys,runpy;sys.path.insert(0,sys.argv[1]);runpy.run_path('+repr(str(base/'old_light_entry.py'))+',run_name="__main__")'
            args=(command,*args[1:])
    proc=real(*args,**kwargs);row={'process':proc};processes.append(row)
    original=proc.poll
    def poll():
        code=original()
        if code is not None and 'exit_code' not in row:
            row['exit_code']=code
            k=ctypes.windll.kernel32;h=ctypes.c_void_p(int(proc._handle));values=[ctypes.c_ulonglong() for _ in range(4)]
            if k.GetProcessTimes(h,*[ctypes.byref(v) for v in values]):row['launcher_cpu_seconds']=(values[2].value+values[3].value)/1e7
            counts=IO()
            if k.GetProcessIoCounters(h,ctypes.byref(counts)):row['launcher_os_io']={n:getattr(counts,n) for n,_ in counts._fields_}
            path=Path(args[0][-1]).parent/'result.json'
            if path.exists():
                value=json.loads(path.read_bytes());row['worker_error']=value['error'];row['diagnostics']=value.get('diagnostics')
            observation=path.parent/'operation-observation.json'
            if observation.exists():row['worker_observation']=json.loads(observation.read_bytes())
        return code
    proc.poll=poll
    return proc
server.subprocess.Popen=observe
s=server.Service(root,temporary=temp);s.bind();initial=inventory()
report['initial_inventory_sha256']=hashlib.sha256(json.dumps(initial,sort_keys=True).encode()).hexdigest()
report['initial_byte_inventory_sha256']=hashlib.sha256(json.dumps({n:{k:v for k,v in row.items() if k!='mtime_ns'} for n,row in initial.items()},sort_keys=True).encode()).hexdigest()
if mode=='retry':assert report['initial_byte_inventory_sha256']==json.loads((base/('browser56-old'+suffix+'-report.json')).read_bytes())['initial_byte_inventory_sha256']
entries=sorted(json.loads((root/'content/registry.json').read_bytes())['entries'],key=lambda e:e['production']['width']*e['production']['height']);ids=[entries[0]['id'],entries[-1]['id']]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        report['browser']=browser.version
        context=browser.new_context(viewport={'width':1600,'height':1000},device_scale_factor=1)
        page=context.new_page();page_errors=[];page.on('pageerror',lambda e:page_errors.append(str(e)))
        def idle():
            end=time.monotonic()+660
            while page.locator('body.busy').count():
                if time.monotonic()>end:raise AssertionError('DOM job timeout')
                time.sleep(.15)
        page.goto(s.url());idle();assert page.locator('.entry').count()==56
        def action(name,click,error=False):
            print('START',name);before=inventory();start=time.perf_counter();count=len(processes);stages=[]
            click()
            end=time.monotonic()+660
            while page.locator('body.busy').count():
                state=s.status();job=state['job']
                if job and (not stages or (job['operation'],job['stage'])!=(stages[-1]['operation'],stages[-1]['stage'])):stages.append({'operation':job['operation'],'stage':job['stage'],'elapsed_seconds':job.get('elapsed_seconds')})
                if mode!='old' and job and job['operation']=='apply' and 'Guards' in job['stage'] and not (originals/'02-new-apply-phase.png').exists():
                    page.locator('#status').screenshot(path=str(originals/'02-new-apply-phase.png'))
                if time.monotonic()>end:raise AssertionError('DOM operation timeout')
                time.sleep(.15)
            wall=time.perf_counter()-start;state=s.status();job=state['job'];after=inventory()
            assert job and job['state']==('error' if error else 'done'),job
            status=page.locator('#status').inner_text()
            assert ('error' in (page.locator('#status').get_attribute('class') or ''))==error,status
            row={'action':name,'wall_seconds':wall,'ui_status':status,'state':job['state'],'error':job['error'],'recovery_required':state['recovery_required'],'runtime_format':json.loads((root/'game/data/registry.json').read_bytes())['format'],'stages':stages,'changed':{n:{'before':before.get(n),'after':after.get(n)} for n in set(before)|set(after) if before.get(n)!=after.get(n)},'processes':[{k:v for k,v in x.items() if k!='process'} for x in processes[count:]]}
            report['jobs'].append(row);save();print('END',name,round(wall,3),job['error'] or 'ok')
            return job
        def select(identifier,name):
            job=action(name,lambda:page.locator('.entry[data-id="'+identifier+'"]').click())
            assert page.locator('#puzzle-id').inner_text()==identifier
            expected=next(e for e in entries if e['id']==identifier)
            metadata=json.loads((root/'content/registry.json').read_bytes())['metadata']
            meta=next(row for row in metadata if row['id']==identifier)
            assert page.locator('#name').input_value()==meta['name']
            assert page.locator('#category').input_value()==meta['category_id']
            definition=json.loads((root/'game'/expected['definition']).read_bytes())
            assert page.locator('#raster').input_value()=='\n'.join(' '.join(map(str,row)) for row in definition['solution'])+'\n'
            assert page.locator('#palette .swatch').count()==len(definition['palette'])+1
            for index,color in enumerate(definition['palette']):
                rgb=tuple(int(color['color'][i:i+2],16) for i in (0,2,4))
                assert page.locator('#palette .swatch i').nth(index).evaluate('(e)=>e.style.backgroundColor')=='rgb('+', '.join(map(str,rgb))+')'
            assert page.locator('#reveal-pictures img').count()==1
            for kind in ('reveal','background'):
                pictures=page.locator('#'+kind+'-pictures img')
                assert pictures.count()==len(job['result']['pictures'][kind])
                for picture in pictures.all():
                    picture.evaluate('(e)=>e.decode()')
                    assert picture.evaluate('(e)=>e.complete && e.naturalWidth>0')
            assert page.locator('#background').input_value()==job['result']['detail']['runtime']['background']['status']
            assert inventory()==initial
            return job
        if mode!='old':
            for i,identifier in enumerate(ids):
                for condition in ('first','warm'):select(identifier,'detail-'+str(i)+'-'+condition)
            page.locator('#search').fill(ids[-1])
            meta=next(row for row in json.loads((root/'content/registry.json').read_bytes())['metadata'] if row['id']==ids[-1])
            page.locator('#filter').select_option(meta['category_id'])
        plan=action('migration-plan',lambda:page.locator('#migrate').click())
        assert plan['result']['files']==['game/data/registry.json']
        assert inventory()==initial
        if mode=='old':
            failed=action('migration-apply',lambda:page.locator('#apply').click(),True)
            assert 'resource_limit: catalog time budget exhausted' in failed['error']
            after_failure=inventory()
            assert {n:(row['sha256'],row['bytes']) for n,row in after_failure.items()}=={n:(row['sha256'],row['bytes']) for n,row in initial.items()}
            assert not s.status()['recovery_required']
            report['failure_restored_bytes']=True
            report['failure_mtime_changed']=sorted(n for n in initial if initial[n]['mtime_ns']!=after_failure[n]['mtime_ns'])
            assert json.loads((root/'game/data/registry.json').read_bytes())['format']=='picross-runtime-registry-v7'
            page.locator('#status').screenshot(path=str(originals/'01-old-apply-error.png'))
        else:
            assert page.locator('#puzzle-id').inner_text()==ids[-1]
            assert page.locator('#search').input_value()==ids[-1] and page.locator('#filter').input_value()==meta['category_id']
            assert page.locator('#raster').input_value()
            applied=action('migration-apply-and-ui-readback',lambda:page.locator('#apply').click())
            page.locator('#status').screenshot(path=str(originals/'03-new-apply-readback.png'))
            assert json.loads((root/'game/data/registry.json').read_bytes())['format']=='picross-runtime-registry-v8'
            assert not page.locator('#migration').is_visible()
            assert page.locator('#puzzle-id').inner_text()==ids[-1]
            assert page.locator('#search').input_value()==ids[-1] and page.locator('#filter').input_value()==meta['category_id']
            after=inventory();assert {n for n in set(initial)|set(after) if initial.get(n)!=after.get(n)}=={'game/data/registry.json'}
            # The normal UI hides the completed migration. Use the genuine bound
            # API for its fresh recheck/No-op, then refresh the actual DOM.
            def api(route,body=None):
                response=context.request.fetch(s.origin+server.API+route,method='GET' if body is None else 'POST',headers={'X-PE-Session':s.secret,'Origin':s.origin,'Content-Type':'application/json'},data=None if body is None else json.dumps(body))
                assert response.ok,(route,response.status,response.text());return response.json()
            def api_job(route,body):
                started=time.perf_counter();count=len(processes);stages=[]
                key=api(route,body)['job'];end=time.monotonic()+660
                while time.monotonic()<end:
                    job=api('status')['job'];assert job['id']==key
                    if not stages or job['stage']!=stages[-1]['stage']:stages.append({'stage':job['stage'],'elapsed_seconds':job['elapsed_seconds']})
                    if job['state']!='running':
                        assert job['state']=='done',job
                        report['jobs'].append({'action':'api-'+route+'-recheck','wall_seconds':time.perf_counter()-started,'stages':stages,'processes':[{k:v for k,v in x.items() if k!='process'} for x in processes[count:]],'changed':{}})
                        save();return job['result']
                    time.sleep(.15)
                raise AssertionError('API recheck timeout')
            start=time.perf_counter();p2=api_job('migration',{'snapshot':api('catalog')['snapshot']});assert p2['files']==[]
            report['recheck_plan_seconds']=time.perf_counter()-start
            start=time.perf_counter();noop=api_job('apply',{'plan':p2['plan'],'id':None});assert noop['status']=='noop'
            report['noop_apply_seconds']=time.perf_counter()-start;assert inventory()==after
            api('discard',{'confirmed':True})
            action('v8-catalog-refresh-and-selected-detail',lambda:page.locator('#reload').click())
            assert page.locator('#puzzle-id').inner_text()==ids[-1]
            assert inventory()==after
            page.locator('#search').fill('');page.locator('#filter').select_option('')
            action('post-migration-other-ID-selection',lambda:page.locator('.entry[data-id="'+ids[0]+'"]').click())
            assert page.locator('#puzzle-id').inner_text()==ids[0] and inventory()==after
        assert not page_errors,page_errors
        report['page_errors']=page_errors;report['passed']=True;report['journal_absent']=not s.status()['recovery_required'];save()
        report['originals']=[{'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(originals.glob('*.png'))];save()
        browser.close()
finally:
    s.close();save()
