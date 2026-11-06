from pathlib import Path
import json,time,ctypes
import win
w=Path(__file__).parent;out=w/'gui-restart';report={'assertions':[]}
def check(ok,name):
 report['assertions'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 s=win.wait(lambda s:not s['applying'])
 report['initial']=s
 check(s['mode']==0 and s['client']==[1280,720] and s['saved']=={'mode':'window','preset':'1280x720'},'fresh exported process restores confirmed display')
 check(s['ui_scale']==1.0,'fresh process resets session UI scale to 100 percent')
 win.click_rect(s['catalog_cards'][0]);s=win.wait(lambda s:s['book_state']==3 and not s['info'],seconds=8)
 before=s['player'];report['work_before']=s
 win.click_rect(s['menu']);s=win.wait(lambda s:s['info'] and s['book_state']==4)
 check(s['information_origin']=='work','actual work-origin settings retains visit origin')
 win.click_rect(s['scale']);s=win.wait(lambda s:s['scale_popup']['visible']);p=s['scale_popup'];x,y=p['position'];width,height=p['size'];row=(height-18)/2
 win.click_rect([x+9,y+9+row,width-18,row]);win.wait(lambda s:s['ui_scale']==1.25)
 win.click_rect(win.state()['info_return']);s=win.wait(lambda s:not s['info'] and s['book_state']==3)
 report['work_after']=s
 check(s['player']==before,'settings and UI change preserve actual work cells history and semantic clue view')
 win.u.PostMessageW(win.hwnd,0x10,0,0);time.sleep(.5)
 check(not win.u.IsWindow(win.hwnd),'regular WM close ends exported player after flush')
finally:
 (out/'restart-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('restart/work/close',len(report['assertions']))
