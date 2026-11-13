"""One-time T03 on the final B01 build; only task-owned windows and synthetic data."""
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)
import hashlib, http.client, json, os, shutil, socket, subprocess, sys, time
from pathlib import Path
from pywinauto import Desktop
from pywinauto.controls.hwndwrapper import HwndWrapper
H=Path(__file__).resolve().parent; R=H/'repo'
sys.path.insert(0,str(R))
from socket_probe import contender, inventory
from tools.puzzle_editor.bundle import verify
sys.stdout.reconfigure(encoding='utf-8')
DEADLINE=time.monotonic()+240

def allowed():
    if time.monotonic()>DEADLINE: raise TimeoutError('Task window input deadline reached')
def wait(fn,seconds=60):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        try:
            v=fn()
            if v:return v
        except (RuntimeError,LookupError): pass
        time.sleep(.15)
    raise TimeoutError('Native expected state timeout')
def mains():return [w for w in Desktop(backend='uia').windows() if w.window_text()=='Picross · Bestandseditor 0.1.0']
def pane(w,width):return next(c for c in w.descendants() if c.element_info.control_type=='Pane' and c.rectangle().width()==width and c.rectangle().height()==25)
def click(w,width):
    allowed(); w.set_focus(); time.sleep(.15); pane(w,width).click_input(); time.sleep(.3)
    if width==80 and not any(c.element_info.control_type=='Window' for c in w.descendants()):
        pane(w,width).click_input();time.sleep(.3)
def dialog(w,title):return next((c for c in w.descendants() if c.element_info.control_type=='Window' and c.window_text()==title),None)
def button(w,text):return next(c for c in w.descendants(control_type='Button') if c.window_text()==text)
def browser(root,port):
    for w in Desktop(backend='uia').windows():
        if 'Bestandseditor' not in w.window_text() or w.window_text()=='Picross · Bestandseditor 0.1.0':continue
        texts=[c.window_text() for c in w.descendants(control_type='Text')]
        if str(root) in texts and 'http://127.0.0.1:'+str(port) in texts:return w
def close_browser(w):
    allowed();w.set_focus();w.type_keys('^w');time.sleep(.2)
def stop(w):
    pid=w.process_id();click(w,108)
    d=wait(lambda:dialog(w,'Editor beenden'),5);button(d,'OK').invoke()
    wait(lambda:not any(x.process_id()==pid for x in mains()),60)
def port_free(port):
    with socket.socket() as s:return s.connect_ex(('127.0.0.1',port))!=0
def config(path):return json.loads((path/'config.json').read_bytes()) if (path/'config.json').exists() else None

def main():
    assert not ctypes.windll.shell32.IsUserAnAdmin()
    app=H/'build/dist/Picross-Bestandseditor'
    head=verify(app);delivery=json.loads((H/'build/delivery.json').read_bytes());assert delivery['commit']==head
    root=H/'native-target';shutil.copytree(H.parent/'576-pe-b-20261113/synthetic-seed',root)
    (root/'tools').mkdir();(root/'tools/__init__.py').write_text('raise RuntimeError("DATA CHECKOUT CODE MUST NEVER RUN")\n')
    before=inventory(root);state=H/'native-state'
    report={'head':head,'platform':'Windows 11 10.0.26200','standard_user':True,'delivery':delivery,'steps':[],
            'automation':'Real Tk dialog, Windows UI Automation and bounded mouse/keyboard input in own windows; real standard browser',
            'input_limit_seconds':240,'ports':[],'started_pids':[],'later_contenders':[]}
    started=time.monotonic();prior_path=os.environ['PATH']
    def record(text):
        report['steps'].append(text);print('PASS',text,round(time.monotonic()-started,3),flush=True)
        (H/'t03-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    def launch(args,developer=False):
        allowed();previous={x.process_id() for x in mains()}
        if developer:
            subprocess.Popen([sys.executable,'-m','tools.puzzle_editor',*map(str,args)],cwd=R,env=os.environ.copy(),creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.startfile(str(app/'Picross-Bestandseditor.exe'),arguments=subprocess.list2cmdline(list(map(str,args))))
        w=wait(lambda:next((x for x in mains() if x.process_id() not in previous),None),90)
        report['started_pids'].append(w.process_id());time.sleep(.5);return w
    try:
        os.environ.update(TEMP=str(H/'temp'),TMP=str(H/'temp'),PATH=str(Path(os.environ['SystemRoot'])/'System32'))
        w=launch(['--state',state]);click(w,97)
        d=wait(lambda:dialog(w,'Bestehendes Picross-Checkout öffnen'),10)
        field=next(c for c in d.descendants(control_type='Edit') if c.window_text()=='Folder:')
        field.set_edit_text(str(root));button(d,'Select Folder').invoke();time.sleep(.2);click(w,80)
        c=wait(lambda:config(state),10);assert c['checkout']==str(root);port=c['port'];report['ports'].append(port)
        b=wait(lambda:browser(root,port),15)
        wait(lambda:any('pz-test-direct-mono' in x.window_text() for x in b.descendants(control_type='Button')),10)
        record('Portable EXE via ShellExecute; actual folder selection; visible path/port; automatic standard browser without Python/Git in PATH')
        for reuse in (0,1):
            result=contender(port,reuse);assert not result['bound'];report['later_contenders'].append(result)
        # Normal browser keeps serving its authenticated current catalog after the attack.
        reload=next(x for x in b.descendants(control_type='Button') if x.window_text()=='Neu laden');reload.invoke()
        wait(lambda:any('Aktuelle Metadaten geladen' in x.window_text() for x in b.descendants(control_type='Text')),10)
        record('Frozen listener rejects later foreign process with default and SO_REUSEADDR; original authenticated browser reload still succeeds')
        second=launch(['--state',H/'native-second-state','--root',root]);click(second,80)
        d=wait(lambda:dialog(second,'Editorstart nicht möglich'),10)
        assert any('bereits' in x.window_text() for x in d.descendants());button(d,'OK').invoke();HwndWrapper(second.element_info.handle).close()
        assert not port_free(port);record('Second instance rejected while original listener remains alive')
        stop(w);wait(lambda:port_free(port),10);close_browser(b);assert inventory(root)==before
        record('Orderly normal stop; process and port closed; checkout bytes/mtimes preserved')
        # Use a fresh occupied port: an exclusive listener may remain in TCP TIME_WAIT.
        with socket.socket() as foreign:
            foreign.bind(('127.0.0.1',0));foreign.listen();occupied=foreign.getsockname()[1]
            w=launch(['--state',state,'--port',occupied]);click(w,80)
            d=wait(lambda:dialog(w,'Port belegt'),10);button(d,'Yes').invoke()
            c=wait(lambda:config(state) if config(state)['port']!=port else None,10)
            changed=c['port'];assert changed!=occupied;report['ports'].append(changed)
            b=wait(lambda:browser(root,changed),15)
            entry=wait(lambda:next((x for x in b.descendants(control_type='Button') if 'pz-test-direct-mono' in x.window_text()),None),10);entry.invoke()
            wait(lambda:any('Fachoperation' in x.window_text() and ('läuft' in x.window_text() or 'gestartet' in x.window_text()) for x in b.descendants(control_type='Text')),10)
            stop(w);wait(lambda:port_free(changed),10);assert foreign.getsockname()==('127.0.0.1',occupied);close_browser(b)
            report['prior_occupant']={'port':occupied,'preserved':True,'alternative_port':changed,'explicit_Yes':True}
        assert inventory(root)==before
        record('Remembered checkout reopened; actual prior-occupant dialog and explicit Yes; foreign listener preserved; active frozen detail drains before shutdown')
        w=launch(['--state',H/'native-invalid-state','--root',H/'not-a-checkout']);click(w,80)
        d=wait(lambda:dialog(w,'Editorstart nicht möglich'),10);button(d,'OK').invoke();HwndWrapper(w.element_info.handle).close()
        record('Invalid checkout visibly rejected without a ready service')
        os.environ['PATH']=prior_path
        devstate=H/'native-developer-state'
        w=launch(['--state',devstate,'--root',root],developer=True);click(w,80)
        c=wait(lambda:config(devstate),10);b=wait(lambda:browser(root,c['port']),15)
        wait(lambda:any('pz-test-direct-mono' in x.window_text() for x in b.descendants(control_type='Button')),10)
        stop(w);wait(lambda:port_free(c['port']),10);close_browser(b);assert inventory(root)==before
        record('Exact python -m tools.puzzle_editor fallback opens actual window/browser and stops; complete checkout bytes/mtimes unchanged')
        report.update(passed=True,automation_seconds=round(time.monotonic()-started,3),checkout_inventory=before)
    except Exception as exc:
        report.update(passed=False,error=type(exc).__name__+': '+str(exc),automation_seconds=round(time.monotonic()-started,3));raise
    finally:
        os.environ['PATH']=prior_path
        (H/'t03-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print('INPUT CONTROL ENDED',round(time.monotonic()-started,3),flush=True)

if __name__=='__main__':main()
