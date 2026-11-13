"""Run only after the user's explicit two-minute input-control permission."""
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)
import os,sys,json,time,threading,subprocess,socket,hashlib
from pathlib import Path
from pywinauto import Desktop
from pywinauto.controls.hwndwrapper import HwndWrapper
from t03 import mains,wait,click,dialog,button,browser,stop
from t01 import inventory
H=Path(__file__).parent;R=H/'repo'

def main():
    # This is a hard stop of the input driver, independent of model/tool polling.
    started=time.monotonic()
    watchdog=threading.Timer(120,lambda:os._exit(124));watchdog.daemon=True;watchdog.start()
    app=H/'delivery/dist/Picross-Bestandseditor';root=H/'t03-target'
    state=H/'t03-delivery-current-state';config=json.loads((state/'config.json').read_bytes())
    report=json.loads((H/'review/review/pe-b/t03-partial.json').read_bytes())
    report.update(status='running',permission='Explicit user permission before input; hard limit 120 seconds',remaining=[])
    before=inventory(root,True);b=None;w=None
    def record(text):
        report.setdefault('completed_remaining_scenarios',[]).append(text)
        print('PASS',text,round(time.monotonic()-started,2),flush=True)
    def launch(args,developer=False):
        previous={x.process_id() for x in mains()}
        env={**os.environ,'TEMP':str(H/'temp'),'TMP':str(H/'temp')}
        cmd=([sys.executable,'-m','tools.puzzle_editor'] if developer else [str(app/'Picross-Bestandseditor.exe')])+list(map(str,args))
        proc=subprocess.Popen(cmd,cwd=R,env=env,creationflags=subprocess.CREATE_NO_WINDOW,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        value=wait(lambda:next((x for x in mains() if x.process_id() not in previous),None),15)
        time.sleep(1.3);return value
    try:
        with socket.socket() as foreign:
            foreign.bind(('127.0.0.1',config['port']));foreign.listen()
            w=launch(['--state',state]);click(w,80)
            d=wait(lambda:dialog(w,'Port belegt'),10);button(d,'Yes').invoke()
            changed=wait(lambda:json.loads((state/'config.json').read_bytes()) if json.loads((state/'config.json').read_bytes())['port']!=config['port'] else None,15)
            b=wait(lambda:browser(root,changed['port']),15)
            entry=wait(lambda:next((c for c in b.descendants(control_type='Button') if 'pz-test-direct-mono' in c.window_text()),None),10)
            entry.invoke()
            wait(lambda:any('Fachoperation' in c.window_text() and ('läuft' in c.window_text() or 'gestartet' in c.window_text()) for c in b.descendants(control_type='Text')),10)
            stop(w);w=None
            with socket.socket() as probe:assert probe.connect_ex(('127.0.0.1',changed['port']))!=0
            assert foreign.getsockname()[1]==config['port']
            b.set_focus();b.type_keys('^w');b=None
        assert inventory(root,True)==before
        record('Remembered checkout; explicit port-conflict fallback; foreign listener preserved; active frozen detail drains before native stop')
        if time.monotonic()-started>85:raise TimeoutError('Not starting another input scenario near the permission deadline')
        w=launch(['--state',H/'t03-permitted-invalid','--root',H/'not-a-checkout']);click(w,80)
        d=wait(lambda:dialog(w,'Editorstart nicht möglich'),10)
        texts=[c.window_text() for c in d.descendants(control_type='Text')]
        assert texts
        button(d,'OK').invoke();HwndWrapper(w.element_info.handle).close();w=None
        record('Invalid checkout rejected by the actual native start dialog')
        if time.monotonic()-started>90:raise TimeoutError('Not starting fallback near the permission deadline')
        devstate=H/'t03-permitted-developer'
        w=launch(['--root',root,'--state',devstate],developer=True);click(w,80)
        dc=wait(lambda:json.loads((devstate/'config.json').read_bytes()) if (devstate/'config.json').exists() else None,10)
        b=wait(lambda:browser(root,dc['port']),15)
        wait(lambda:any('pz-test-direct-mono' in c.window_text() for c in b.descendants(control_type='Button')),10)
        stop(w);w=None
        with socket.socket() as probe:assert probe.connect_ex(('127.0.0.1',dc['port']))!=0
        b.set_focus();b.type_keys('^w');b=None
        assert inventory(root,True)==before
        record('Exact python -m tools.puzzle_editor developer fallback opens its real window/browser and stops cleanly')
        report.update(status='passed',passed=True,automation_seconds=round(time.monotonic()-started,3),checkout_inventory=before)
    except Exception as exc:
        report.update(status='partial',passed=False,error=type(exc).__name__+': '+str(exc),automation_seconds=round(time.monotonic()-started,3))
        raise
    finally:
        # No focus operations here: the driver always relinquishes input now.
        watchdog.cancel()
        (H/'t03-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print('INPUT CONTROL STOPPED',round(time.monotonic()-started,2),flush=True)

if __name__=='__main__':main()
