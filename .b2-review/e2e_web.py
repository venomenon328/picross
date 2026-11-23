from pathlib import Path
import sys, json, secrets, os, time, hashlib, threading, subprocess, socket, shutil, io, http.client
from http.server import SimpleHTTPRequestHandler,BaseHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from contextlib import ExitStack
from uuid import uuid4
task=Path(__file__).resolve().parent.parent
root=task/'repo'
out=task/os.getenv('B2_BUILD','integration-build')/'export'
sys.path[:0]=[str(task/'probe/python'),str(root/'server/save_sync')]
from test_integration import Project,Client
from playwright.sync_api import sync_playwright
class Static(SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
class Proxy(BaseHTTPRequestHandler):
    offline=False
    drop=False
    trace=[]
    port=0
    signed_in_device=None
    def log_message(self,*a): pass
    def forward(self):
        payload=self.rfile.read(int(self.headers.get('Content-Length','0')))
        if self.offline: self.send_error(503);return
        db=http.client.HTTPConnection('127.0.0.1',self.port,timeout=30)
        try:
            db.request(self.command,self.path,payload,dict(self.headers))
            resp=db.getresponse()
            data=resp.read()
            row={'method':self.command,'path':self.path.split('?')[0],'status':resp.status,'generation':resp.getheader('X-Picross-Generation')}
            if self.path.endswith('/mutations') and self.command=='POST':
                row.update(body=payload.decode(),receipt=data.decode())
            if self.command=='POST' and self.path.endswith('/auth/login'):
                if resp.status==200: type(self).signed_in_device=json.loads(data)['device_id']
                auth=json.loads(payload)
                row['username_length']=len(auth.get('username',''))
                row['password_present']=bool(auth.get('password'))
            self.trace.append(row)
            if self.command=='POST' and self.path.endswith('/auth/login'):print('login',row['status'],row['username_length'],row['password_present'],flush=True)
            if self.drop and 'receipt' in row:
                type(self).drop=False
                row['lost']=True
                self.connection.shutdown(socket.SHUT_RDWR)
                return
            self.send_response(resp.status)
            for k,v in resp.getheaders():
                if k.lower() not in ['connection','transfer-encoding','date','server','content-length']: self.send_header(k,v)
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        finally:db.close()
    do_GET=do_POST=do_OPTIONS=forward

def serve(stack,port,handler):
    server=ThreadingHTTPServer(('127.0.0.1',port),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    stack.callback(server.server_close)
    stack.callback(server.shutdown)
def seed(client,name):
    registry=json.loads((root/'game/data/registry.json').read_text(encoding='utf8'))
    r=next(x for x in registry['entries'] if x['id']==name)
    d=json.loads((root/'game'/r['definition']).read_text(encoding='utf8'))
    cells=[-1]*(d['width']*d['height'])
    cells[0]=0
    value=dict(format='picross-progress/v1',definition_id=name,definition_revision=d['revision'],width=d['width'],height=d['height'],cells=cells,undo_used=False,completed=False)
    client.put(name,1,0,'snapshot',save=value)
def observe(page): return page.evaluate('window.b2Observation || {}')
def wait(page,fn,name,timeout=75):
    print('stage',name,flush=True)
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        state=observe(page)
        if state and fn(state): return state
        page.wait_for_timeout(140)
    raise RuntimeError(name+' '+str({k:state.get(k) for k in ('state','status','profile','ready','cursor','cells','size','confirmed','busy')})+' controls '+str(list(state.get('points',{}))[:12]))
def click(page,key):
    st=wait(page,lambda s: key in s['points'],key)
    x,y=st['points'][key]
    canvas=page.locator('canvas').bounding_box()
    page.mouse.click(canvas['x']+x,canvas['y']+y)
    page.wait_for_timeout(260)
def locate_manage(page):
    click(page,'settings')
    st=wait(page,lambda s: 'manage' in s['points'] and s['state']==4,'settings')
    canvas=page.locator('canvas').bounding_box()
    x,y=st['points']['manage']
    if y>canvas['height']*.85:
        page.mouse.move(canvas['x']+x,canvas['y']+canvas['height']*.72)
        for _ in range(8):
            page.mouse.wheel(0,520)
            page.wait_for_timeout(160)
    click(page,'manage')
def login(page,client):
    locate_manage(page)
    click(page,'username')
    page.keyboard.type(client.name,delay=10)
    click(page,'password')
    page.keyboard.type(client.password,delay=10)
    click(page,'Anmelden')
    return wait(page,lambda s:s['profile'] and s['ready'] and s['confirmed'],'normal login',140)
def execute(kind):
    run=uuid4().hex[:10]; name='picross-sync-b2-'+run
    evidence=task/('proof-'+kind+'-'+run); evidence.mkdir()
    with ExitStack() as stack:
        proj=Project(name,name+':local',secrets.token_urlsafe(32))
        proj.env['SYNC_ORIGINS']='http://127.0.0.1:18212'
        stack.callback(lambda:subprocess.run(['docker','image','rm',name+':local'],capture_output=True))
        stack.callback(proj.down)
        proj.up('--build')
        client=Client(proj,'konto'+run+'x'*17)
        client.register()
        Proxy.port=proj.port
        serve(stack,18211,Proxy)
        serve(stack,18212,partial(Static,directory=str(out)))
        play=stack.enter_context(sync_playwright())
        launcher=getattr(play,kind)
        folder=evidence.parent/('profile-'+run)
        def launch():
            opt=dict(headless=True,viewport=dict(width=1920,height=1118))
            if kind=='chromium':opt['args']=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']
            if kind=='firefox':opt['firefox_user_prefs']={'webgl.force-enabled':True,'webgl.disabled':False}
            ctx=launcher.launch_persistent_context(str(folder),**opt)
            stack.callback(ctx.close)
            p=ctx.pages[0]
            p.set_default_timeout(60000)
            p.on('pageerror',lambda e: print('pageerror',str(e)[:180],flush=True))
            p.goto('http://127.0.0.1:18212')
            return ctx,p
        ctx,page=launch()
        try:
            st=wait(page,lambda s:s.get('ids') and s['status']=='Gast','guest',180)
            assert len(Proxy.trace)==0
            # The header is outside the game canvas. Match the actual game surface.
            delta=1080-st['size'][1]
            page.set_viewport_size({'width':1920,'height':int(1118+delta)})
            wait(page,lambda s:s['size']==[1920,1080],'surface')
            target=st['ids'][0]
            seed(client,target)
            st=login(page,client)
            assert st['font_size']==18
            page.locator('canvas').screenshot(path=str(evidence/'status-ui100.png'))
            if kind=='chromium':
                other=ctx.new_page();other.goto('http://127.0.0.1:18212');other.wait_for_function("document.querySelector('#message').textContent.includes('anderen Tab')");other.close()
            click(page,'puzzle/'+target)
            wait(page,lambda s:s['id']==target and s['baseline'][:1]==[0] and 'cell1' in s['points'] and s['state']==3,'baseline')
            if kind=='chromium':
                page.evaluate(Path(__file__).with_name('barriers.js').read_text())
                page.evaluate("['dirty','request','receipt'].forEach(x=>b2Gates.arm(x))")
            click(page,'cell1')
            if kind=='chromium':
                page.wait_for_function("b2Gates.pending.has('dirty')")
                assert not any('receipt' in x for x in Proxy.trace)
                assert not observe(page)['confirmed']
                page.evaluate("b2Gates.release('dirty')")
            wait(page,lambda s:s['cursor']==1 and s['confirmed'],'edit')
            assert all(x['method']!='POST' or not x['path'].endswith('/mutations') for x in Proxy.trace)
            click(page,'back')
            if kind=='chromium':
                page.wait_for_function("b2Gates.pending.has('request')")
                assert not any('receipt' in x for x in Proxy.trace)
                page.evaluate("b2Gates.release('request')")
                page.wait_for_function("b2Gates.pending.has('receipt')")
                assert sum('receipt' in x for x in Proxy.trace)==1
                assert not observe(page)['confirmed']
                page.evaluate("b2Gates.release('receipt')")
                (evidence/'barriers.json').write_text(json.dumps(page.evaluate('b2Gates.events'),indent=2))
            wait(page,lambda s:s['state']==0 and 'Synchronisiert' in s['status'] and any('receipt' in x for x in Proxy.trace),'uploaded',130)
            assert client.get('puzzles/'+target)['server_revision']==2
            ctx.close()
            ctx,page=launch()
            st=wait(page,lambda s:s.get('profile') and s['ready'] and s['confirmed'],'restart',180)
            click(page,'puzzle/'+target)
            st=wait(page,lambda s:s['state']==3 and s['id']==target,'reload work')
            assert st['baseline'][0]==0 and st['cursor']==1 and st['cells'][1]>0,st['cursor']
            click(page,'undo')
            wait(page,lambda s:s['cursor']==0 and s['cells'][0]==0 and s['cells'][1]==-1,'undo to basis')
            click(page,'redo')
            wait(page,lambda s:s['cursor']==1,'redo')
            originals=page.evaluate("""async () => {
                const db=await new Promise((ok,no)=>{const r=indexedDB.open('/userfs');r.onsuccess=()=>ok(r.result);r.onerror=()=>no(r.error)});
                const files={};await new Promise((ok,no)=>{const t=db.transaction('FILE_DATA','readonly'),r=t.objectStore('FILE_DATA').openCursor();
                  r.onsuccess=()=>{const c=r.result;if(!c)return;const k=String(c.key);
                    if(k.includes('/accounts/')&&(k.endsWith('/journal.json')||/\/saves\/[^/]+\.json$/.test(k))){
                      files[k.endsWith('/journal.json')?'journal.json':'account-save.json']=Array.from(c.value.contents);
                    }c.continue()};t.oncomplete=ok;t.onerror=()=>no(t.error)});db.close();return files;
            }""")
            assert set(originals)=={'journal.json','account-save.json'},list(originals)
            for file,data in originals.items():(evidence/file).write_bytes(bytes(data))
            (evidence/'http.json').write_text(json.dumps(Proxy.trace,indent=2))
            (evidence/'platform.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'browser':kind,'version':ctx.browser.version,'engine':'4.7.2.stable.official.ed1daf0bf','size':st['size'],'ui':st['scale'],'observed':['ordinary login','postgres push','process restart','undo to received baseline','redo']}))
            if kind=='chromium':
                click(page,'back')
                wait(page,lambda s:s['state']==0,'catalog before scale')
                canvas=page.locator('canvas').bounding_box()
                vp=page.viewport_size
                page.set_viewport_size({'width':1280,'height':720+round(vp['height']-canvas['height'])})
                st=wait(page,lambda s:s['size'][0]==1280,'narrow surface')
                if st['size'][1]!=720:
                    page.set_viewport_size({'width':1280,'height':page.viewport_size['height']+720-round(st['size'][1])})
                wait(page,lambda s:s['size']==[1280,720],'1280x720')
                click(page,'settings')
                click(page,'scale')
                click(page,'scale125')
                wait(page,lambda s:s['scale']==1.25,'UI125')
                click(page,'info-back')
                wait(page,lambda s:s['state']==0,'catalog UI125')
                click(page,'puzzle/'+target)
                wait(page,lambda s:'cell2' in s['points'] and not s['locked'],'ready for fault')
                page.evaluate(Path(__file__).with_name('barriers.js').read_text())
                page.evaluate("b2Gates.arm('dirty')")
                click(page,'cell2')
                page.wait_for_function("b2Gates.pending.has('dirty')")
                page.evaluate("b2Gates.release('dirty',true)")
                click(page,'back')
                st=wait(page,lambda s:'retry' in s['points'] and s['state']==0,'visible error with retry')
                assert st['font_size']==23 and st['size']==[1280,720]
                page.locator('canvas').screenshot(path=str(evidence/'status-ui125.png'))
                click(page,'retry')
                wait(page,lambda s:s['confirmed'],'retried local flush')
                wait(page,lambda s:'Synchronisiert' in s['status'],'confirmed after retry',120)
                # Rotate the synthetic test device with a real second login; the original browser token is now rejected.
                assert Proxy.signed_in_device
                client.http('POST','/v1/auth/login',dict(username=client.name,password=client.password,device_id=Proxy.signed_in_device,device_name='isolated rotation'))
                locate_manage(page);click(page,'open-local')
                wait(page,lambda s:'Erneut anmelden' in s['status'],'server confirmed 401',140)
                assert any(r['status']==401 for r in Proxy.trace)
                if observe(page)['state']==4:click(page,'info-back')
                st=login(page,client)
                assert st['profile'] and st['ready']
                locate_manage(page);click(page,'Abmelden')
                wait(page,lambda s:not s['profile'] and s['status'].startswith('Gast'),'local logout')
                page.evaluate("b2Gates.replay('dirty')")
                page.wait_for_timeout(400)
                assert not observe(page)['profile'] and observe(page)['status'].startswith('Gast')
                first=json.loads((evidence/'barriers.json').read_text())
                (evidence/'barriers.json').write_text(json.dumps(first+page.evaluate('b2Gates.events'),indent=2))
                (evidence/'http.json').write_text(json.dumps(Proxy.trace,indent=2))
            print('PASS',kind,evidence.name,flush=True)
        except Exception:
            (evidence/'http.json').write_text(json.dumps(Proxy.trace,indent=2))
            page.screenshot(path=str(evidence/'debug.png'))
            (evidence/'state.json').write_text(json.dumps(observe(page),ensure_ascii=False))
            raise
if __name__=='__main__':execute(sys.argv[1])
