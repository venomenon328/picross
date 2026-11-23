import os, sys, json, time, secrets, ctypes, subprocess, shutil, hashlib
from ctypes import wintypes as W
from pathlib import Path
from contextlib import ExitStack
from uuid import uuid4
from e2e_web import Proxy,Project,Client,serve,seed,task,out,root
from windows_service import WindowsProject as Project
U=ctypes.windll.user32; G=ctypes.windll.gdi32
U.SetProcessDPIAware()
class Native:
    def __init__(self,stack,evidence,profile):
        self.obs=profile/'observed.json';self.obs.unlink(missing_ok=True)
        env=dict(os.environ,APPDATA=str(profile/'roaming'),LOCALAPPDATA=str(profile/'local'),TMP=str(profile/'temp'),TEMP=str(profile/'temp'),B2_OBSERVATION=str(self.obs))
        for k in ['APPDATA','LOCALAPPDATA','TEMP']:Path(env[k]).mkdir(parents=True,exist_ok=True)
        self.log=(evidence.parent/(profile.name+'-diag.log')).open('ab')
        self.proc=subprocess.Popen([str(out/'picross.exe'),'--rendering-driver','opengl3','--audio-driver','Dummy'],cwd=out,env=env,stdout=self.log,stderr=self.log)
        stack.callback(self.close)
        self.window=0
        end=time.monotonic()+90
        while time.monotonic()<end and not self.window:
            def each(h,p):
                pid=W.DWORD()
                U.GetWindowThreadProcessId(h,ctypes.byref(pid))
                if pid.value==self.proc.pid:
                    cl=ctypes.create_unicode_buffer(256);U.GetClassNameW(h,cl,255)
                    if cl.value=='Engine':self.window=h
                return True
            cb=ctypes.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM)(each)
            U.EnumWindows(cb,0)
            if self.proc.poll() is not None: raise RuntimeError('native exited '+str(self.proc.returncode))
            time.sleep(.15)
        if not self.window:raise RuntimeError('No owned Godot GUI window')
    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=20)
        self.log.close()
    def wait(self,predicate,stage,timeout=95):
        print('stage',stage,flush=True)
        end=time.monotonic()+timeout;s={}
        while time.monotonic()<end:
            if self.proc.poll() is not None:raise RuntimeError('native exited '+stage)
            try:s=json.loads(self.obs.read_text(encoding='utf8'))
            except (OSError,ValueError):time.sleep(.25);continue
            if predicate(s):return s
            time.sleep(.2)
        raise RuntimeError(stage+' '+str({k:s.get(k) for k in ('state','status','id','busy','confirmed','size','cursor','cells')})+' controls '+str(list(s.get('points',{}))[:12]))
    def resize(self,width,height):
        c=W.RECT();w=W.RECT()
        U.GetClientRect(self.window,ctypes.byref(c));U.GetWindowRect(self.window,ctypes.byref(w))
        U.SetWindowPos(self.window,0,w.left,w.top,width+w.right-w.left-c.right,height+w.bottom-w.top-c.bottom,0x14)
        self.wait(lambda s:s['size']==[width,height],'window size')
    def click(self,key):
        st=self.wait(lambda s:key in s['points'],key)
        x,y=map(round,st['points'][key])
        self.press_at(x,y)
    def press_at(self,x,y):
        U.ShowWindow(self.window,5)
        U.SetForegroundWindow(self.window)
        screen=W.POINT(x,y);U.ClientToScreen(self.window,ctypes.byref(screen))
        # Godot also queries the physical pointer after capturing a board gesture.
        U.SetCursorPos(screen.x,screen.y)
        time.sleep(.15)
        pos=(y<<16)|x
        if U.GetForegroundWindow()!=self.window:
            raise RuntimeError('Windows focus unavailable for the owned product')
        hit=U.WindowFromPoint(screen)
        if hit!=self.window and not U.IsChild(self.window,hit):
            raise RuntimeError('Owned target is obscured at '+str([x,y]))
        U.mouse_event(2,0,0,0,0)
        time.sleep(.18)
        U.mouse_event(4,0,0,0,0)
        time.sleep(.45)
    def type(self,value):
        for c in value:
            vk=ord(c.upper())
            scan=U.MapVirtualKeyW(vk,0)<<16
            U.PostMessageW(self.window,0x100,vk,scan|1)
            time.sleep(.035)
            U.PostMessageW(self.window,0x101,vk,scan|0xc0000001)
            time.sleep(.02)
    def screenshot(self,path):
        req=Path(str(self.obs)+'.png.request')
        source=Path(str(self.obs)+'.png')
        source.unlink(missing_ok=True)
        req.touch()
        end=time.monotonic()+20
        while req.exists() and time.monotonic()<end:time.sleep(.1)
        assert source.exists() and not req.exists()
        source.replace(path)
def execute():
    run=uuid4().hex[:10];name='picross-sync-b2-native-'+run
    evidence=task/('proof-win-'+run);evidence.mkdir()
    folder=task/('win-profile-'+run);folder.mkdir()
    with ExitStack() as stack:
        proj=Project(name,name+':local',secrets.token_urlsafe(32))
        stack.callback(proj.down);proj.up('--build')
        Proxy.port=proj.port;serve(stack,18221,Proxy)
        client=Client(proj,'konto'+run+'x'*17);client.password=secrets.token_hex(20);client.register()
        game=Native(stack,evidence,folder)
        st=game.wait(lambda s:s['ids'] and s['status']=='Gast','guest')
        game.resize(1920,1080)
        assert not Proxy.trace
        target=st['ids'][0];seed(client,target)
        game.click('settings')
        game.wait(lambda s:s['state']==4,'settings')
        game.click('manage');game.click('username');game.type(client.name)
        game.click('password');game.type(client.password);game.click('Anmelden')
        st=game.wait(lambda s:s['profile'] and s['confirmed'] and s['ready'],'normal login',120)
        assert st['font_size']==18
        game.screenshot(evidence/'status-ui100.png')
        game.click('puzzle/'+target)
        game.wait(lambda s:s['state']==3 and s['baseline'][:1]==[0] and 'cell1' in s['points'],'basis')
        time.sleep(1.6)
        Proxy.offline=True
        game.click('cell1');game.wait(lambda s:s['cursor']==1 and s['confirmed'],'offline edit')
        game.click('back')
        game.wait(lambda s:'Offline' in s['status'],'offline sender')
        Proxy.offline=False;Proxy.drop=True
        game.wait(lambda s:'Synchronisiert' in s['status'],'retry after response loss',160)
        mutations=[r for r in Proxy.trace if 'receipt' in r]
        assert len(mutations)==2 and mutations[0].get('lost') and mutations[0]['body']==mutations[1]['body']
        assert client.get('puzzles/'+target)['server_revision']==2
        game.close();game=Native(stack,evidence,folder)
        game.wait(lambda s:s['profile'] and s['confirmed'] and s['ready'],'persisted account',120)
        game.click('puzzle/'+target)
        game.wait(lambda s:s['state']==3 and s['cursor']==1 and s['cells'][0]==0,'restart')
        game.click('undo');game.wait(lambda s:s['cursor']==0 and s['cells'][0]==0 and s['cells'][1]==-1,'undo to basis')
        game.click('redo');game.wait(lambda s:s['cursor']==1,'redo')
        account=list((folder/'roaming').rglob('journal.json'))
        assert len(account)==1
        shutil.copyfile(account[0],evidence/'journal.json')
        savefiles=list((account[0].parent/'saves').glob('*.json'));assert len(savefiles)==1
        shutil.copyfile(savefiles[0],evidence/'account-save.json')
        (evidence/'http.json').write_text(json.dumps(Proxy.trace,indent=2))
        print('PASS Windows',evidence.name)
if __name__=='__main__':execute()
