from pathlib import Path
p=Path(__file__).with_name('windows_rf.py')
exec(p.read_text(encoding='utf-8').split("stable();menu('sort',1)")[0])
observations=[]
def save_record(label):
 observations.append(dict(scenario=label,state=win.state()))
 (win.out/'observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
 print('PASS',label,flush=True)
def safe_click(rect):
 # Choose an actually visible point within our own target. Never remove the
 # ownership guard or click through an occluding application.
 win.activate();win.u.SetWindowPos(win.hwnd,wt.HWND(-1),0,0,0,0,0x13);time.sleep(.15)
 win.u.WindowFromPoint.argtypes=[wt.POINT];win.u.WindowFromPoint.restype=wt.HWND
 for fx,fy in [(0.5,.5),(.15,.3),(.85,.3),(.15,.7),(.85,.7)]:
  x,y=rect[0]+rect[2]*fx,rect[1]+rect[3]*fy
  q=wt.POINT(round(x),round(y));win.u.ClientToScreen(win.hwnd,ctypes.byref(q));owner=wt.DWORD();win.u.GetWindowThreadProcessId(win.u.WindowFromPoint(q),ctypes.byref(owner))
  if owner.value==win.pid:win.click_rect([x,y,0,0]);return
 raise AssertionError(('own target occluded',rect))
def scale_round(index):
 click_control('Einstellungen / Info');menu('scale',index);stable()
 safe_click(win.state()['back']);stable()
stable()
s=win.state();assert s['client']==[1920,1080] and s['recent']['id']=='pz-test-kat2-003',s['client']
# A fresh process starts at UI100; keep the same 1920x1080 client throughout.
assert s['ui']==1
snap('rest-ui100-before',True)
scale_round(1);assert win.state()['client']==[1920,1080];snap('rest-ui125',True)
scale_round(0);assert win.state()['client']==[1920,1080];snap('rest-ui100-after',True)
assert observations[0]['state']['recent']['box']==observations[2]['state']['recent']['box']
save_record('same-window-ui-roundtrip-exact-geometry')
safe_click(card('pz-test-kat2-003')['reset']);win.wait(lambda s:s['reset_dialog'])
safe_click(win.state()['reset_ok']);stable()
assert not win.state()['recent']['visible'] and not win.state()['recent']['id']
save_record('reset-hides-no-fallback')
# Unchanged older progress A must not become recent through view-only entry.
open_card('pz-test-kat2-001');assert win.state()['work']
safe_click(win.state()['catalog_return']);stable()
assert not win.state()['recent']['id'] and not win.state()['recent']['visible']
save_record('view-only-reentry-does-not-mark')
win.capture('rest-reset-reentry-hidden');win.wait(lambda s:(win.out/'rest-reset-reentry-hidden.png').exists())
path=win.out/'rest-reset-reentry-hidden.png'
observations.append(dict(scenario='reset-reentry-original',state=win.state(),file=path.name,crop=json.loads((win.out/'rest-reset-reentry-hidden-crop.json').read_text()),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(win.out/'observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
click_control('Beenden')
print('RF-A-T02 remaining Windows UI proof PASS',flush=True)
