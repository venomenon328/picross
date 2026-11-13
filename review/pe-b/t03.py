import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)
import os,sys,json,time,shutil,subprocess,socket,hashlib
from pathlib import Path
from pywinauto import Desktop
from pywinauto.controls.hwndwrapper import HwndWrapper
H=Path(__file__).parent;R=H/'repo';sys.path.insert(0,str(R))
sys.stdout.reconfigure(encoding='utf-8')
from t01 import inventory
from tools.puzzle_editor.bundle import verify

def wait(fn,seconds=40):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        try:
            value=fn()
            if value:return value
        except (RuntimeError,LookupError):pass
        time.sleep(.15)
    raise AssertionError('Native expected state timeout')

def windows():return Desktop(backend='uia').windows()
def mains():return [w for w in windows() if w.window_text()=='Picross · Bestandseditor 0.1.0']
def pane(w,width,height):return next(c for c in w.descendants() if c.element_info.control_type=='Pane' and c.rectangle().width()==width and c.rectangle().height()==height)
def click(w,width,height=25):
    w.set_focus();time.sleep(.4);target=pane(w,width,height);target.click_input();time.sleep(.5)
    # A newly activated Tk window may consume the first injected mouse event.
    # Retry only Start, whose successful command disables itself immediately.
    if width==80 and not any(c.element_info.control_type=='Window' for c in w.descendants()):
        target.click_input();time.sleep(.5)
def dialog(w,title):return next((c for c in w.descendants() if c.element_info.control_type=='Window' and c.window_text()==title),None)
def button(w,text):return next((c for c in w.descendants() if c.element_info.control_type=='Button' and c.window_text()==text),None)
def browser(root,port):
    for w in windows():
        if 'Picross' in w.window_text() and 'Bestandseditor' in w.window_text() and w.window_text()!='Picross · Bestandseditor 0.1.0':
            try:
                texts=[c.window_text() for c in w.descendants(control_type='Text')]
                if any(str(root) in text for text in texts) and any('http://127.0.0.1:'+str(port) in text for text in texts):return w
            except RuntimeError:pass
def close_browser(w):
    if w:
        w.set_focus();w.type_keys('^w');time.sleep(.3)
def stop(w):
    pid=w.process_id();click(w,108)
    d=wait(lambda:dialog(w,'Editor beenden'))
    wait(lambda:button(d,'OK')).invoke()
    def finished():
        failure=dialog(w,'Beenden unvollständig')
        if failure:raise AssertionError('Native drain: '+repr([c.window_text() for c in failure.descendants(control_type='Text')]))
        return not any(x.process_id()==pid for x in mains())
    wait(finished,60)
def port_free(port):
    with socket.socket() as s:return s.connect_ex(('127.0.0.1',port))!=0

def main():
    assert not ctypes.windll.shell32.IsUserAnAdmin()
    app=H/'delivery/dist/Picross-Bestandseditor'
    head=verify(app);delivery=json.loads((H/'delivery/delivery.json').read_bytes())
    assert delivery['commit']==head
    root=H/'t03-target'
    if not root.exists():shutil.copytree(H/'synthetic-seed',root)
    malicious=root/'tools';malicious.mkdir(exist_ok=True)
    (malicious/'__init__.py').write_text('raise RuntimeError("DATA CHECKOUT CODE MUST NEVER RUN")\n')
    before=inventory(root,True)
    state=H/'t03-delivery-current-state'
    report={'head':head,'platform':'Windows 11 Pro 10.0.26200','standard_user':True,'exe_sha256':delivery['exe_sha256'],'zip_sha256':delivery['zip_sha256'],'steps':[],'native_input':'DPI-aware Windows UI Automation / real Tk folder dialog and standard browser','ports':[]}
    def record(text):report['steps'].append(text);print('PASS',text,flush=True)
    # Close only the explicit preliminary native probe created by this task.
    for w in mains():
        if w.process_id()==39504:
            d=dialog(w,'Bestehendes Picross-Checkout öffnen')
            if d:button(d,'Cancel').invoke();time.sleep(.2)
            HwndWrapper(w.element_info.handle).close();time.sleep(.3)
    def launch(args,developer=False):
        previous={w.process_id() for w in mains()}
        args=' '.join('"'+str(a)+'"' for a in args)
        if developer:
            process=subprocess.Popen([sys.executable,'-m','tools.puzzle_editor','--root',str(root),'--state',str(H/'t03-dev-state')],cwd=R,env={**os.environ,'TEMP':str(H/'temp'),'TMP':str(H/'temp')},creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.startfile(str(app/'Picross-Bestandseditor.exe'),arguments=args)
        value=wait(lambda:next((w for w in mains() if w.process_id() not in previous),None))
        time.sleep(1.5)
        return value
    # First run is an actual ShellExecute (the double-click activation path), no Python/Git in PATH.
    prior_path=os.environ['PATH'];os.environ['PATH']=str(Path(os.environ['SystemRoot'])/'System32')
    os.environ.update(TEMP=str(H/'temp'),TMP=str(H/'temp'))
    w=launch(['--state',state]);click(w,97)
    d=wait(lambda:dialog(w,'Bestehendes Picross-Checkout öffnen'))
    field=next(c for c in d.descendants() if c.element_info.control_type=='Edit' and c.window_text()=='Folder:')
    field.set_edit_text(str(root));button(d,'Select Folder').invoke();time.sleep(.5)
    click(w,80)
    config=wait(lambda:json.loads((state/'config.json').read_bytes()) if (state/'config.json').exists() else None)
    assert config['checkout']==str(root);port=config['port'];report['ports'].append(port)
    b=wait(lambda:browser(root,port));wait(lambda:any('pz-test-direct-mono' in c.window_text() for c in b.descendants(control_type='Button')))
    record('portable EXE via ShellExecute, actual folder chooser, visible checkout/port and automatic standard browser without Python/Git PATH')
    # Same target, separate settings and port cannot create another writer.
    second=launch(['--state',H/'t03-second-state','--root',root])
    click(second,80);d=wait(lambda:dialog(second,'Editorstart nicht möglich'))
    assert any('bereits' in c.window_text() for c in d.descendants())
    button(d,'OK').invoke();HwndWrapper(second.element_info.handle).close()
    assert not port_free(port);record('second instance reports existing checkout and does not stop first instance')
    stop(w);wait(lambda:port_free(port));close_browser(b);assert inventory(root,True)==before
    record('normal native stop releases process and port, preserves every checkout byte/mtime')
    # Reopen settings and exercise an occupied port with explicit affirmative fallback.
    with socket.socket() as foreign:
        foreign.bind(('127.0.0.1',port));foreign.listen()
        w=launch(['--state',state]);click(w,80)
        d=wait(lambda:dialog(w,'Port belegt'));button(d,'Yes').invoke()
        config=wait(lambda:json.loads((state/'config.json').read_bytes()) if json.loads((state/'config.json').read_bytes())['port']!=port else None)
        changed=config['port'];report['ports'].append(changed);assert changed!=port
        b=wait(lambda:browser(root,changed));entry=wait(lambda:next((c for c in b.descendants(control_type='Button') if 'pz-test-direct-mono' in c.window_text()),None));entry.invoke()
        wait(lambda:any('Fachoperation' in c.window_text() and ('läuft' in c.window_text() or 'gestartet' in c.window_text()) for c in b.descendants() if c.element_info.control_type=='Text'))
        stop(w);wait(lambda:port_free(changed));assert foreign.getsockname()[1]==port;close_browser(b)
    assert inventory(root,True)==before
    record('remembered checkout, foreign port preserved, explicit different port, stop drains active frozen detail worker')
    # Invalid path gets an ordinary native message before any service readiness.
    w=launch(['--state',H/'t03-invalid-state','--root',H/'not-a-checkout']);click(w,80)
    d=wait(lambda:dialog(w,'Editorstart nicht möglich'));button(d,'OK').invoke();HwndWrapper(w.element_info.handle).close()
    record('invalid selected checkout rejected visibly without opening service')
    os.environ['PATH']=prior_path
    w=launch([],developer=True);click(w,80)
    config=wait(lambda:json.loads((H/'t03-dev-state/config.json').read_bytes()) if (H/'t03-dev-state/config.json').exists() else None)
    b=wait(lambda:browser(root,config['port']));wait(lambda:any('pz-test-direct-mono' in c.window_text() for c in b.descendants(control_type='Button')))
    stop(w);wait(lambda:port_free(config['port']));close_browser(b)
    assert inventory(root,True)==before
    record('actual developer fallback window, same data-only checkout, browser and orderly stop')
    report['passed']=True;report['checkout_inventory']=before;report['bundle_files']=delivery['files']
    report['settings']=json.loads((state/'config.json').read_bytes())
    (H/'t03-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

if __name__=='__main__':main()
