from pathlib import Path
import json,time,ctypes
import win
w=Path(__file__).parent;out=w/'gui';report=json.loads((out/'n01-report.json').read_text(encoding='utf-8'))
def check(ok,name):
 report['assertions'].append({'name':name,'passed':bool(ok)});assert ok,name
def capture(name):
 win.capture(name);time.sleep(.4);assert (out/(name+'.png')).exists();report['captures'][name]=win.state()
def top():
 win.activate();b=win.state()['scroll'];p=win.wt.POINT(round(b[0]+b[2]-40),round(b[1]+b[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y)
 for _ in range(20):win.u.mouse_event(0x0800,0,0,120,0);time.sleep(.025)
 time.sleep(.2)
try:
 top();s=win.state();assert s['client']==[1280,720] and s['ui_scale']==1.25
 if win.state()['preview']:
  win.click_rect(win.state()['cancel']);win.wait(lambda s:not s['preview'] and not s['applying'])
 if win.state()['mode']==0:
  win.choose('mode_control',1);win.wait(lambda s:s['preview']);win.click_rect(win.state()['accept']);win.wait(lambda s:not s['preview'] and not s['applying'])
 win.choose('mode_control',0);win.wait(lambda s:s['preview'] and s['card'][3]<720)
 s=win.state();check(s['client']==[1280,720] and s['card'][1]>=0 and s['card'][1]+s['card'][3]<=720,'720p/UI125 actual preview fits and has reachable actions')
 capture('preview-720p-ui125');win.click_rect(win.state()['accept']);win.wait(lambda s:not s['preview'] and not s['applying'])
 top();win.click_rect(win.state()['view_control']);time.sleep(.4);capture('puzzle-options-720p-ui125');win.key(27);time.sleep(.3)
 win.click_rect(win.state()['info_return']);win.wait(lambda s:not s['info'] and s['book_state']==0)
 win.click_rect(win.state()['catalog_cards'][0]);win.wait(lambda s:s['book_state']==3,seconds=10)
 win.click_rect(win.state()['menu']);win.wait(lambda s:s['info'] and s['book_state']==4)
 win.click_rect(win.state()['info_switch']);win.wait(lambda s:s['section']=='help' and s['book_state']==4)
 win.click_rect(win.state()['settings_access']);win.wait(lambda s:s['section']=='settings' and s['book_state']==4)
 win.click_rect(win.state()['info_return']);win.wait(lambda s:not s['info'] and s['book_state']==3)
 check(True,'actual work-origin settings/help/return stays bound to puzzle')
 win.u.PostMessageW(win.hwnd,0x10,0,0);time.sleep(1)
finally:
 (out/'n01-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('N01 complete:',len(report['assertions']),'assertions')
