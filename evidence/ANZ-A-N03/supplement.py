from pathlib import Path
import json,time,os
import win
w=Path(__file__).parent;out=w/'gui-supplement'
report={'source_head':json.loads((w/'export.json').read_text())['source_head'],'assertions':[],'captures':{}}
def check(ok,name):
 report['assertions'].append({'name':name,'passed':bool(ok)});assert ok,name
def capture(name):
 win.capture(name)
 for _ in range(100):
  if (out/(name+'.png')).exists():break
  time.sleep(.05)
 assert (out/(name+'.png')).exists()
 report['captures'][name]=win.state()
def choose(control,popup,index,count):
 win.click_rect(win.state()[control]);s=win.wait(lambda s:s[popup]['visible'])
 p=s[popup];x,y=p['position'];width,height=p['size'];row=(height-18)/count
 win.click_rect([x+9,y+9+index*row,width-18,row]);time.sleep(.3)
def accept():
 win.click_rect(win.state()['accept']);win.wait(lambda s:not s['preview'] and not s['applying'])
try:
 s=win.wait(lambda s:s['album_visible'] and not s['applying'])
 win.click_rect(s['catalog_info'][0]);win.wait(lambda s:s['info'] and s['book_state']==4)
 choose('size_control','size_popup',3,8);win.wait(lambda s:s['preview']);accept()
 choose('scale','scale_popup',1,2);s=win.wait(lambda s:s['ui_scale']==1.25)
 check(s['client']==[1920,1080] and s['heading']['resource']=='res://art/drawing/BaksoDaging-Regular.ttf','supplement actual 1080p/UI125 with Bakso')
 win.click_rect(s['view_control']);win.key(27);time.sleep(.15);win.key(9)
 s=win.wait(lambda s:next(f for f in s['fields'] if f['name']=='Rätselansicht')['focus_tip'])
 capture('settings-1080p-ui125-view-help')
 check(True,'actual 1080p/UI125 view-help scene for prior large-original gate')
 win.key(27);choose('mode_control','mode_popup',1,3);s=win.wait(lambda s:s['preview'] and not s['applying'])
 check(s['mode']==3 and s['card_visible'] and s['client']==[2560,1440],'actual borderless preview with reachable modal at UI125')
 capture('preview-borderless-ui125')
 win.click_rect(s['cancel']);s=win.wait(lambda s:not s['preview'] and not s['applying'])
 check(s['mode']==0 and s['client']==[1920,1080],'supplement cancellation restores prior window')
 win.u.PostMessageW(win.hwnd,0x10,0,0);time.sleep(.7)
 check(not win.u.IsWindow(win.hwnd),'supplement player closes through real WM close')
finally:
 (out/'supplement-report.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print('supplement',len(report['assertions']),'assertions',len(report['captures']),'originals')
