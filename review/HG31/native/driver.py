from pathlib import Path
import ctypes,json,time,os
from ctypes import wintypes as w
from PIL import ImageGrab
W=Path(__file__).resolve().parent;out=W/'native-visual';user=ctypes.windll.user32;user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
for name,args in [('GetWindowThreadProcessId',[w.HWND,ctypes.POINTER(w.DWORD)]),('GetClientRect',[w.HWND,ctypes.POINTER(w.RECT)]),('ClientToScreen',[w.HWND,ctypes.POINTER(w.POINT)]),('SetForegroundWindow',[w.HWND]),('SetWindowPos',[w.HWND,w.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,w.UINT]),('GetWindowLongW',[w.HWND,ctypes.c_int]),('SetWindowLongW',[w.HWND,ctypes.c_int,ctypes.c_long]),('PostMessageW',[w.HWND,w.UINT,w.WPARAM,w.LPARAM])]:getattr(user,name).argtypes=args
user.GetForegroundWindow.restype=w.HWND
pid=int((out/'pid.txt').read_text());handles=[]
@ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
def visit(h,_):
 p=w.DWORD();user.GetWindowThreadProcessId(h,ctypes.byref(p))
 if p.value==pid and user.IsWindowVisible(h):handles.append(h)
 return True
user.EnumWindows(visit,0);assert handles;
def area(h):
 r=w.RECT();user.GetClientRect(h,ctypes.byref(r));return r.right*r.bottom
hwnd=max(handles,key=area)
original=w.POINT();user.GetCursorPos(ctypes.byref(original));trace=[]
def state():
 for _ in range(50):
  try:return json.loads((out/'state.json').read_bytes())
  except (ValueError,OSError):time.sleep(.02)
 raise RuntimeError('No observer state')
def wait(f,timeout=35):
 stop=time.monotonic()+timeout
 while time.monotonic()<stop:
  s=state()
  if f(s):return s
  time.sleep(.06)
 raise RuntimeError('State timeout '+str({k:s[k] for k in ['state','selected','background','size','ui_scale']}))
def activate():
 tid=user.GetWindowThreadProcessId(user.GetForegroundWindow(),None);own=ctypes.windll.kernel32.GetCurrentThreadId();a=user.AttachThreadInput(own,tid,True)
 try:user.SetForegroundWindow(hwnd)
 finally:
  if a:user.AttachThreadInput(own,tid,False)
 user.ShowWindow(hwnd,9)
 user.SetWindowPos(hwnd,None,0,0,0,0,0x0001|0x0002)
 user.keybd_event(0x12,0,0,0)
 user.SetForegroundWindow(hwnd)
 user.keybd_event(0x12,0,2,0)
 deadline=time.monotonic()+5
 while user.GetForegroundWindow()!=hwnd and time.monotonic()<deadline:time.sleep(.05)
 assert user.GetForegroundWindow()==hwnd, (hwnd,user.GetForegroundWindow())

def center(r):return [r[0]+r[2]/2,r[1]+r[3]/2]
def click(point):
 assert user.GetForegroundWindow()==hwnd
 origin=w.POINT();user.ClientToScreen(hwnd,ctypes.byref(origin));user.SetCursorPos(round(origin.x+point[0]),round(origin.y+point[1]));time.sleep(.08);user.mouse_event(2,0,0,0,0);time.sleep(.08);user.mouse_event(4,0,0,0,0);time.sleep(.2)
def key(k):user.keybd_event(k,0,0,0);time.sleep(.05);user.keybd_event(k,0,2,0);time.sleep(.05)
def capture(name):
 s=state();origin=w.POINT();size=w.RECT();user.ClientToScreen(hwnd,ctypes.byref(origin));user.GetClientRect(hwnd,ctypes.byref(size));ImageGrab.grab((origin.x,origin.y,origin.x+size.right,origin.y+size.bottom)).save(out/(name+'.png'));trace.append({'capture':name+'.png','state':s,'stimulus':'actual Win32 OS input','client':[size.right,size.bottom]})
def tip(k):click(center(state()['tips'][k]['rect']))
def catalog():
 if state()['state']==3:tip('nav-information');wait(lambda s:s['state']==0 and not s['barrier'])
def open_(id):
 catalog();click(center(state()['cards'][id]));wait(lambda s:s['state']==3 and not s['barrier'] and s['selected']==id)
def scale(u):
 if state()['ui_scale']==u:return
 tip('menu');wait(lambda s:s['state']==4 and not s['barrier']);capture('native-settings-before-scale');click(center(state()['scale_control']));popup=wait(lambda s:s['scale_popup']['visible'])['scale_popup'];x,y=popup['position'];width,height=popup['size'];click([x+width/2,y+9+((1 if u==1.25 else 0)+.5)*(height-18)/2]);wait(lambda s:s['ui_scale']==u and not s['barrier']);click(center(state()['info_return']));wait(lambda s:s['state']==3 and not s['barrier'])
try:
 activate();style=user.GetWindowLongW(hwnd,-16);user.SetWindowLongW(hwnd,-16,style & ~0x00C40000)
 for width,height,u in [(1920,1080,1.0),(1920,1080,1.25),(1280,720,1.25),(2560,1440,1.0)]:
  user.SetWindowPos(hwnd,None,0,0,width,height,0x0020|0x0004);wait(lambda s:s['size']==[width,height]);time.sleep(.4)
  open_('pz-hg31-new');scale(u);s=wait(lambda s:s['background']['state']=='visible');assert s['background']['size']==[2304,768];new=s['background']['rect'];capture(f'native-new-{width}x{height}-ui{int(u*100)}')
  open_('pz-hg31-legacy');s=wait(lambda s:s['background']['state']=='visible');assert s['background']['size']==[2304,576];old=s['background']['rect'];assert abs(new[2]-old[2])<.1 and abs(new[3]/old[3]-4/3)<.001;capture(f'native-legacy-{width}x{height}-ui{int(u*100)}')
 # Actual cell, clue, zoom, info/book return, standard/none and repeat visit.
 open_('pz-hg31-new');s=state();g=s['grid'];cell=s['cell_size'];before=s['cursor'];click([g[0]+cell*1.5,g[1]+cell*1.5]);wait(lambda s:s['cursor']>before);trace.append({'interaction':'cell','before_cursor':before,'after_cursor':state()['cursor']})
 click([g[0]-cell*.5,g[1]+cell*1.5]);trace.append({'interaction':'clue','owned_after_release':state()['clue']})
 tip('plus');time.sleep(.2);tip('minus');tip('menu');wait(lambda s:s['state']==4 and not s['barrier']);capture('native-information');click(center(state()['info_return']));wait(lambda s:s['state']==3 and not s['barrier']);capture('native-return-new')
 for id,status in [('pz-hg31-none','none'),('pz-hg31-standard','legacy'),('pz-hg31-new','visible')]:
  open_(id);s=wait(lambda s:s['background']['state']==status);capture('native-'+id.removeprefix('pz-hg31-')+'-return');assert not s['background']['stale_requests']
 print('HG31_NATIVE_T03_OK',len(trace))
finally:
 (out/'protocol.json').write_text(json.dumps({'source_head':'21ae27c3d2ce6e88852a41765d84c76695d0d8f7','environment':'Windows native EXE/PCK; NVIDIA RTX3070 OpenGL; borderless client; external read-only observer','trace':trace},indent=2)+'\n',encoding='utf8');user.SetCursorPos(original.x,original.y);user.PostMessageW(hwnd,0x0010,0,0)
