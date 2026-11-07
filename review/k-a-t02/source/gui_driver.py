from pathlib import Path
import sys,time,json,ctypes,os
sys.path.insert(0,str(Path(__file__).parent));import win
out=win.out
checks=json.loads((out/'checks.json').read_text(encoding='utf-8')) if (out/'checks.json').exists() else []
def check(ok,label):
 checks.append(dict(check=label,passed=bool(ok)))
 (out/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 if not ok:raise AssertionError(label)
def idle():return win.wait(lambda s:s['book_state'] in [0,3,4] and not s['capture'] and not s['barrier'],seconds=15)
def press(text):
 win.click_rect(win.state()['buttons'][text]);time.sleep(.5)
 if text=='Einstellungen / Info':
  # Verify that the real navigation click was consumed after a page release.
  if not win.state()['info']:
   time.sleep(.7);win.click_rect(win.state()['buttons'][text])
  win.wait(lambda s:s['info'],seconds=10)
 return idle()
def option(key,index):
 win.click_rect(win.state()[key]['box']);p=win.wait(lambda s:s[key]['visible'])[key]
 # Popup opens with no hovered row; Down traverses real native menu focus.
 for _ in range(sum(not item["disabled"] for item in p["items"][:index+1])):win.key(0x28)
 win.key(0x0d)
 win.wait(lambda s:not s[key]['visible']);time.sleep(.2)
 win.record('choice',key=key,index=index)
def open_panel():
 win.click_rect(win.state()['filter_button']);win.wait(lambda s:s['panel']['visible'])
def text(value,key="width_input"):
 win.click_rect(win.state()[key]);win.u.keybd_event(0x11,0,0,0);win.key(0x41);win.u.keybd_event(0x11,0,2,0)
 win.key(0x08)
 for char in value:win.key(ord(char))
 time.sleep(.15)
def capture(name):
 win.capture(name);win.wait(lambda s:(out/(name+'.png')).exists())
 (out/(name+'.json')).write_text(json.dumps(win.state(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def scale(index):
 option('scale',index);win.wait(lambda s:s['ui']==(1.25 if index else 1));idle()
def display(width,height):
 if width==2560:
  option('display_mode',1)
 else:
  if win.state()['client']==[2560,1440]:
   option('display_mode',0);win.wait(lambda s:s['display_preview']);win.click_rect(win.state()['display_accept']);win.wait(lambda s:not s['display_preview'])
  i=next(i for i,v in enumerate(win.state()['display_size']['items']) if v['text']==f'{width} × {height}')
  option('display_size',i)
 win.wait(lambda s:s['display_preview']);win.click_rect(win.state()['display_accept']);win.wait(lambda s:not s['display_preview'] and s['client']==[width,height]);time.sleep(.5)
def back():win.click_rect(win.state()['back']);return idle()
def wheel(rect,amount):
 win.activate();p=win.wt.POINT(round(rect[0]+rect[2]/2),round(rect[1]+rect[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y);win.u.mouse_event(0x0800,0,0,amount,0);time.sleep(.25);win.record('wheel',amount=amount,rect=rect)
if __name__=='__main__':
 win.wait(lambda s:s['pid']==win.pid);idle();capture('study-1920-wide-button')
 press('Einstellungen / Info');scale(1);display(1280,720);back()
 check(win.state()['client']==[1280,720] and win.state()['ui']==1.25,'tight native 1280/ui125')
 capture('study-1280-catalog')
 open_panel();option('lower_filter',5);option('upper_filter',1);press('Übernehmen')
 check(win.state()['panel']['error_visible'] and win.state()['filters']['lower']==0,'invalid range shown without application')
 capture('study-1280-invalid')
 option('upper_filter',5);text('400');option('status_filter',1);option('mode_filter',1);press('Übernehmen')
 check(not win.state()['panel']['visible'],'valid panel applies and closes')
 capture('study-1280-filtered')
 open_panel();press('Filter zurücksetzen');press('Einstellungen / Info');scale(0);display(1920,1080);back()
 capture('study-1920-restored');win.u.PostMessageW(win.hwnd,0x10,0,0)
