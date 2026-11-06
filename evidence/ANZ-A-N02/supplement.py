from pathlib import Path
import sys,time,json,ctypes,os
import win
w=Path(__file__).parent;out=w/'gui-final'
report=json.loads((out/'n02-report.json').read_text(encoding='utf-8'))
def check(ok,name):
 report['assertions'].append({'name':name,'passed':bool(ok)});assert ok,name
def capture(name):
 win.capture(name);time.sleep(.3);assert (out/(name+'.png')).exists();report['captures'][name]=win.state()
def field(name):return next(x for x in win.state()['fields'] if x['name']==name)
def wheel(d,n):
 win.activate();s=win.state();b=s['scroll'];p=win.wt.POINT(round(b[0]+b[2]-50),round(b[1]+b[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y)
 for _ in range(n):win.u.mouse_event(0x0800,0,0,ctypes.c_ulong(d*120).value,0);time.sleep(.06)
 time.sleep(.2)
try:
 wheel(-1,12);win.click_rect(win.state()['view_control']);s=win.wait(lambda s:s['view_popup']['visible']);p=s['view_popup'];size=s['client']
 check(p['position'][0]>=0 and p['position'][1]+p['size'][1]<=size[1] and p['position'][0]+p['size'][0]<=size[0],'full puzzle-view values and popup stay within 720p/UI125')
 capture('puzzle-options-720p-ui125');win.key(27);time.sleep(.2)
 wheel(1,12);win.click_rect(field('Fenstergröße')['help']);win.wait(lambda s:next(x for x in s['fields'] if x['name']=='Fenstergröße')['focus_tip'])
 win.click_rect(win.state()['mode_control']);win.wait(lambda s:s['mode_popup']['visible'])
 check(not any(x['focus_tip'] for x in win.state()['fields']),'opening dropdown dismisses focused help')
 # Click blank paper within the same native client, away from rows/navigation.
 before=win.state()['active'];win.click_rect([80,400,40,40]);win.wait(lambda s:not s['mode_popup']['visible'])
 check(win.state()['active']==before and win.state()['section']=='settings','outside click dismisses menu without activating a setting or navigation')
 win.click_rect(field('Fenstergröße')['help']);win.wait(lambda s:next(x for x in s['fields'] if x['name']=='Fenstergröße')['focus_tip'])
 win.click_rect(win.state()['info_switch']);win.wait(lambda s:s['section']=='help' and s['book_state']==4)
 check(not any(x['focus_tip'] for x in win.state()['fields']),'actual page transition dismisses an open focused help')
 win.click_rect(win.state()['settings_access']);win.wait(lambda s:s['section']=='settings' and s['book_state']==4)
finally:
 (out/'n02-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('supplement total',len(report['assertions']),len(report['captures']))
