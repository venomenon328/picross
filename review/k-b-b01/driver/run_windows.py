from gui_sizes import *
import math
root=next((win.out/'profile/appdata/Godot/app_userdata').glob('*/p1'))
observations=[]
serial=0

def command(kind):
 global serial
 serial+=1;(win.out/'command.txt').write_text(kind+'/'+str(serial),encoding='utf-8');time.sleep(.4)

def wheel_notice(notches):
 win.activate();r=win.state()['notice_area'];p=wt.POINT(round(r[0]+r[2]/2),round(r[1]+r[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y)
 win.u.mouse_event(0x800,0,0,ctypes.c_uint32(notches*120),0);time.sleep(.2)

def visible_target(which):
 for attempt in range(10):
  s=win.state();r=s['recent']['retry'] if which==0 else s['save_retry']['box'];a=s['notice_area']
  if r[1]>=a[1]-.01 and r[1]+r[3]<=a[1]+a[3]+.01:return r
  wheel_notice(50 if r[1]<a[1] else -50)
 raise AssertionError(('cannot scroll target',which,s))

def fixed(s):return [s['sort']['box'],s['filter_button'],s['recent']['box'],s['scrollers']]

def target_check(which,label):
 r=visible_target(which);s=win.state();u=s['ui'];assert r[2]>=44*u and r[3]>=44*u,(label,r)
 a=s['notice_area'];assert r[0]>=a[0]-.01 and r[0]+r[2]<=a[0]+a[2]+.01
 previous=s['retry_hits'][which];layout=fixed(s)
 # Physical OS mouse hits one pixel inside all four edges and the centre.
 for x,y in [(r[0]+1,r[1]+1),(r[0]+r[2]-1,r[1]+1),(r[0]+r[2]-1,r[1]+r[3]-1),(r[0]+1,r[1]+r[3]-1),(r[0]+r[2]/2,r[1]+r[3]/2)]:
  win.click_rect([x,y,0,0])
 win.wait(lambda t:t['retry_hits'][which]==previous+5)
 s=win.state();assert fixed(s)==layout
 observations.append(dict(scenario=label,state=s,expected_hits=5,observed_hits=s['retry_hits'][which]-previous))
 win.capture(label);time.sleep(.25)
 assert (win.out/f'{label}.png').exists(),label
 print('PASS',label,'target',r,'clip',a,flush=True)

def open_card(identifier):
 for attempt in range(80):
  s=win.state();c=card(identifier)['box'];a=s['scrollers'][0]
  top=max(c[1],a[1]);bottom=min(c[1]+c[3],a[1]+a[3])
  if bottom-top>20:
   win.click_rect([max(c[0],a[0])+8,(top+bottom)/2,0,0]);stable();return
  wheel(0,1 if c[1]<a[1] else -1)
 raise AssertionError(('card not visible',identifier))

stable()
menu('sort',1)
for width,height,index in [(1280,720,0),(1280,720,1),(1920,1080,0),(1920,1080,1)]:
 if win.state()['client'] != [width,height]:
  click_control('Einstellungen / Info');menu('display_size',0 if width==1280 else 3)
  win.wait(lambda t:t['display_preview']);win.click_rect(win.state()['display_accept']);stable()
  win.click_rect(win.state()['back']);stable();assert win.state()['client']==[width,height]
 if win.state()['ui'] != (1 if index==0 else 1.25):scale(index)
 label=f'{width}-ui{100 if index==0 else 125}'
 open_card('pz-test-kat2-001')
 win.click_rect(win.state()['cell_boxes'][0]);win.wait(lambda s:s['recent']['id']=='pz-test-kat2-001' and not s['recent']['error'])
 win.click_rect(win.state()['catalog_return']);stable()
 old=(root/'recent-puzzle.json').read_bytes();tmp=root/'recent-puzzle.json.tmp';assert not tmp.exists();tmp.mkdir()
 open_card('pz-test-kat2-003');win.click_rect(win.state()['cell_boxes'][2]);win.wait(lambda s:bool(s['recent']['error']))
 assert (root/'recent-puzzle.json').read_bytes()==old
 win.click_rect(win.state()['catalog_return']);stable();before=fixed(win.state())
 command('long');assert win.state()['notice_max']>win.state()['notice_area'][3];assert fixed(win.state())==before
 target_check(0,'marker-'+label)
 tmp.rmdir();r=visible_target(0);win.click_rect(r);win.wait(lambda s:not s['recent']['error'] and s['recent']['id']=='pz-test-kat2-003')
 # Catalog failure trigger: invoke the existing save boundary once from the
 # external test driver. The failure itself is a real filesystem directory,
 # not a product fail_step. All retry and scrolling inputs are real OS mouse.
 tmp=root/'saves/kat2_003.tmp';assert not tmp.exists();tmp.mkdir();old=(root/'saves/kat2_003.json').read_bytes()
 command('save');win.wait(lambda s:s['save_retry']['visible'] and bool(s['save_error']))
 assert (root/'saves/kat2_003.json').read_bytes()==old
 before=fixed(win.state());command('long');assert fixed(win.state())==before
 target_check(1,'save-'+label)
 tmp.rmdir();r=visible_target(1);win.click_rect(r);win.wait(lambda s:not s['save_error'] and not s['save_retry']['visible'])
 assert fixed(win.state())==before
 observations.append(dict(scenario='successful-retries-'+label,state=win.state()))
(win.out/'observations.json').write_text(json.dumps(observations,indent=2),encoding='utf-8')
click_control('Beenden')
print('WINDOWS B-01 PASS: 8 failure/target cases, 40 OS corner/centre clicks, both retries resolved per configuration',flush=True)
