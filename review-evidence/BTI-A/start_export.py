from pathlib import Path
import ctypes as c
from ctypes import wintypes as t
import subprocess,time,sys,json,hashlib
from PIL import Image
w=Path(__file__).parent;r=w/'repo';sys.path.insert(0,str(r/'tools'));import p1_preflight as tc
env=tc.isolated_environment(w/'startup-profile','Windows');env.update(TEMP=str(w/'temp'),TMP=str(w/'temp'))
u=c.windll.user32;g=c.windll.gdi32
u.GetDC.argtypes=[t.HWND];u.GetDC.restype=t.HDC
g.CreateCompatibleDC.argtypes=[t.HDC];g.CreateCompatibleDC.restype=t.HDC
g.CreateCompatibleBitmap.argtypes=[t.HDC,c.c_int,c.c_int];g.CreateCompatibleBitmap.restype=t.HBITMAP
g.SelectObject.argtypes=[t.HDC,t.HANDLE];g.SelectObject.restype=t.HANDLE
g.GetDIBits.argtypes=[t.HDC,t.HBITMAP,t.UINT,t.UINT,c.c_void_p,c.c_void_p,t.UINT]
u.PrintWindow.argtypes=[t.HWND,t.HDC,t.UINT]
g.DeleteObject.argtypes=[t.HANDLE];g.DeleteDC.argtypes=[t.HDC];u.ReleaseDC.argtypes=[t.HWND,t.HDC]
class BI(c.Structure):
    _fields_=[('size',t.DWORD),('width',t.LONG),('height',t.LONG),('planes',t.WORD),('bits',t.WORD),('compression',t.DWORD),('bytes',t.DWORD),('x',t.LONG),('y',t.LONG),('used',t.DWORD),('important',t.DWORD)]
def capture(hwnd,name):
    rect=t.RECT();u.GetClientRect(hwnd,c.byref(rect));width,height=rect.right,rect.bottom
    dc=u.GetDC(hwnd);mem=g.CreateCompatibleDC(dc);bmp=g.CreateCompatibleBitmap(dc,width,height);old=g.SelectObject(mem,bmp)
    try:
        assert u.PrintWindow(hwnd,mem,3)
        info=BI(c.sizeof(BI),width,-height,1,32,0,0,0,0,0,0)
        pixels=c.create_string_buffer(width*height*4)
        assert g.GetDIBits(mem,bmp,0,height,pixels,c.byref(info),0)==height
        Image.frombuffer('RGB',(width,height),pixels,'raw','BGRX',0,1).save(w/'native'/name)
        return [width,height]
    finally:
        g.SelectObject(mem,old);g.DeleteObject(bmp);g.DeleteDC(mem);u.ReleaseDC(hwnd,dc)
exe=w/'player-final/picross-p1.exe'
with (w/'logs/player-start.log').open('wb') as log:
    p=subprocess.Popen([str(exe),'--rendering-driver','opengl3','--audio-driver','Dummy'],env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    hwnd=None
    try:
        for attempt in range(40):
            found=[]
            @c.WINFUNCTYPE(t.BOOL,t.HWND,t.LPARAM)
            def enum(h,arg):
                pid=t.DWORD();u.GetWindowThreadProcessId(h,c.byref(pid))
                if pid.value==p.pid and u.IsWindowVisible(h):found.append(h)
                return True
            u.EnumWindows(enum,0)
            if found:hwnd=found[0];break
            time.sleep(.25)
        assert hwnd and p.poll() is None
        time.sleep(4)
        dimensions=capture(hwnd,'shipped-windows-catalog.png')
        u.PostMessageW(hwnd,0x10,0,0)
        assert p.wait(timeout=15)==0
    finally:
        if p.poll() is None:p.kill();p.wait()
packs={'windows':w/'player-final/picross-p1.pck','web':next((w/'web-final').rglob('index.pck'))}
rows=[dict(platform=k,bytes=v.stat().st_size,sha256=hashlib.sha256(v.read_bytes()).hexdigest()) for k,v in packs.items()]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
(w/'native/exports.json').write_text(json.dumps(dict(source_head=head,packs=rows,exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),startup='Unmodified Windows exe/PCK, isolated profile, actual native client PrintWindow capture; normal WM_CLOSE exit 0; no gameplay.',client=dimensions),indent=2),encoding='utf-8')
print('WINDOWS_START_OK',dimensions)
