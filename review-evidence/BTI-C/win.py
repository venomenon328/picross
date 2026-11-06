import ctypes,time,json,sys,os
from ctypes import wintypes as wt
from pathlib import Path
w=Path(__file__).parent; out=w/os.environ.get('BTI_GUI','gui');u=ctypes.windll.user32
u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
for n,args in [('GetWindowThreadProcessId',[wt.HWND,ctypes.POINTER(wt.DWORD)]),('GetClientRect',[wt.HWND,ctypes.POINTER(wt.RECT)]),('ClientToScreen',[wt.HWND,ctypes.POINTER(wt.POINT)]),('SetForegroundWindow',[wt.HWND]),('GetWindowRect',[wt.HWND,ctypes.POINTER(wt.RECT)]),('SetWindowPos',[wt.HWND,wt.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wt.UINT]),('PostMessageW',[wt.HWND,wt.UINT,wt.WPARAM,wt.LPARAM])]:getattr(u,n).argtypes=args
u.GetForegroundWindow.restype=wt.HWND
pid=int((out/'pid.txt').read_text()); hwnd=None
@ctypes.WINFUNCTYPE(wt.BOOL,wt.HWND,wt.LPARAM)
def enum(h,unused):
 global hwnd
 p=wt.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(p))
 if p.value==pid and u.IsWindowVisible(h):hwnd=h
 return True
u.EnumWindows(enum,0)
assert hwnd,'own window missing'
def state():
 for _ in range(20):
  try:return json.loads((out/'state.json').read_text(encoding='utf-8'))
  except (ValueError,OSError):time.sleep(.02)
 raise RuntimeError('state incomplete')
def record(action,**data):
 with (out/'os.jsonl').open('a') as f:f.write(json.dumps(dict(at=time.time(),action=action,**data))+'\n')
def activate():
 thread=u.GetWindowThreadProcessId(u.GetForegroundWindow(),None)
 own=ctypes.windll.kernel32.GetCurrentThreadId()
 attached=u.AttachThreadInput(own,thread,True)
 try:
  if u.IsIconic(hwnd):u.ShowWindow(hwnd,9)
  u.SetForegroundWindow(hwnd)
 finally:
  if attached:u.AttachThreadInput(own,thread,False)
 time.sleep(.1)
 if u.GetForegroundWindow()!=hwnd:
  u.SetWindowPos(hwnd,wt.HWND(-1),0,0,0,0,0x13)
  rect=wt.RECT();u.GetWindowRect(hwnd,ctypes.byref(rect))
  point=wt.POINT(rect.left+100,rect.top+14)
  u.WindowFromPoint.argtypes=[wt.POINT];u.WindowFromPoint.restype=wt.HWND
  assert u.WindowFromPoint(point)==hwnd,'own title occluded'
  u.SetCursorPos(point.x,point.y);u.mouse_event(2,0,0,0,0);time.sleep(.04);u.mouse_event(4,0,0,0,0)
  u.SetWindowPos(hwnd,wt.HWND(-2),0,0,0,0,0x13)
  time.sleep(.15)
 assert u.GetForegroundWindow()==hwnd,'not own foreground'
def click_rect(rect):
 activate()
 u.SetWindowPos(hwnd,wt.HWND(-1),0,0,0,0,0x13)
 try:
  p=wt.POINT(round(rect[0]+rect[2]/2),round(rect[1]+rect[3]/2));u.ClientToScreen(hwnd,ctypes.byref(p));u.SetCursorPos(p.x,p.y);time.sleep(.04)
  u.WindowFromPoint.argtypes=[wt.POINT];u.WindowFromPoint.restype=wt.HWND
  target=u.WindowFromPoint(p);owner=wt.DWORD();u.GetWindowThreadProcessId(target,ctypes.byref(owner))
  assert owner.value==pid,'click target is occluded by another process'
  assert u.GetForegroundWindow()==hwnd
  u.mouse_event(2,0,0,0,0);time.sleep(.04);u.mouse_event(4,0,0,0,0);record('click',client_rect=rect,screen=[p.x,p.y],target_pid=owner.value);time.sleep(.15)
 finally:u.SetWindowPos(hwnd,wt.HWND(-2),0,0,0,0,0x13)
def key(vk):
 u.keybd_event(vk,0,0,0);time.sleep(.025);u.keybd_event(vk,0,2,0)
def choose(control,index):
 click_rect(state()[control]);time.sleep(.15)
 popup=wait(lambda s:s['mode_popup'] if s['mode_popup']['visible'] else None)['mode_popup']
 x,y=popup['position'];width,height=popup['size'];row=(height-18)/3
 click_rect([x+9,y+9+index*row,width-18,row]);record('choose',control=control,index=index);time.sleep(.3)
def wait(test,seconds=5):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  try:s=state()
  except RuntimeError:
   time.sleep(.05);continue
  if test(s):return s
  time.sleep(.05)
 raise RuntimeError('wait failed '+str(state()))
def capture(label):
 (out/'capture.txt').write_text(label);time.sleep(.2)
