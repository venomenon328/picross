from pathlib import Path
import sys,time,json,ctypes
import win
w=Path(__file__).parent;out=w/'gui'
report={'source_head':json.loads((w/'export.json').read_text(encoding='utf-8'))['source_head'],'assertions':[],'captures':{}}
def check(ok,name):
 report['assertions'].append({'name':name,'passed':bool(ok)})
 assert ok,name
def capture(name):
 win.capture(name)
 for _ in range(100):
  if (out/(name+'.png')).exists():break
  time.sleep(.05)
 assert (out/(name+'.png')).exists()
 report['captures'][name]=win.state()
def wheel(direction,count=1):
 win.activate();s=win.state();rect=s['scroll'];p=win.wt.POINT(round(rect[0]+rect[2]-50),round(rect[1]+rect[3]/2))
 win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y)
 for _ in range(count):
  win.u.mouse_event(0x0800,0,0,ctypes.c_ulong(direction*120).value,0);time.sleep(.08)
 win.record('wheel',direction=direction,count=count);time.sleep(.2)
def top():
 wheel(1,16);win.wait(lambda s:s['scroll_value']==0)
def scale(value):
 top()
 if win.state()['ui_scale']!=value:
  win.click_rect(win.state()['scale']);win.wait(lambda s:s['ui_scale']==value)
 time.sleep(.3)
def preset(index):
 top();win.click_rect(win.state()['size_control']);s=win.wait(lambda s:s['size_popup']['visible'])
 p=s['size_popup'];x,y=p['position'];width,height=p['size'];row=(height-18)/8
 win.click_rect([x+9,y+9+index*row,width-18,row]);win.wait(lambda s:s['preview'])
def mode(index):
 top();win.choose('mode_control',index);win.wait(lambda s:s['preview'])
def accept():
 win.click_rect(win.state()['accept']);win.wait(lambda s:not s['preview'] and not s['applying']);time.sleep(.3)
def cancel():
 win.click_rect(win.state()['cancel']);win.wait(lambda s:not s['preview'] and not s['applying']);time.sleep(.3)
def rest(name,size,u):
 top();s=win.state()
 check(s['client']==size and s['ui_scale']==u,name+' actual client and UI')
 check(not s['feedback_visible'] and not s['card_visible'],name+' quiet stable state')
 check([g['heading'] for g in s['section_boxes']]==['Anzeige','Rätselansicht','Beenden'],name+' grouped controls')
 check(all(abs(s[key][0]-s['mode_control'][0])<1 and s[key][2]<=640*u+1 and s[key][3]>=44*u for key in ['mode_control','size_control','scale','view_control','clue_reset','mark','animation']),name+' compact aligned hit areas')
 capture(name)
 wheel(-1,16);s=win.state();q=s['quit_control'];b=s['scroll']
 check(q[1]>=b[1]-1 and q[1]+q[3]<=b[1]+b[3]+1,name+' bottom reachable by real wheel')
 if size==[1280,720] and u==1.25:capture('settings-720p-ui125-bottom')
 top()
try:
 win.wait(lambda s:s['info'] and not s['applying'],seconds=10)
 win.key(27);scale(1.0)
 rest('settings-1080p-ui100',[1920,1080],1.0)
 scale(1.25);rest('settings-1080p-ui125',[1920,1080],1.25)
 preset(0);accept();scale(1.0);rest('settings-720p-ui100',[1280,720],1.0)
 scale(1.25);rest('settings-720p-ui125',[1280,720],1.25)
 win.click_rect(win.state()['view_control']);win.wait(lambda s:s['view_control'] and not s['mode_popup']['visible'])
 # Escape exercises the native puzzle-view popup, then open display mode.
 win.key(27);time.sleep(.2)
 win.click_rect(win.state()['mode_control']);s=win.wait(lambda s:s['mode_popup']['visible']);capture('mode-options-720p-ui125')
 check(s['mode_popup']['position'][0]>=0 and s['mode_popup']['position'][1]+s['mode_popup']['size'][1]<=720,'mode popup fits 720p/UI125')
 win.key(27);time.sleep(.2)
 mode(1);win.wait(lambda s:s['card'][3]<s['client'][1],seconds=4);capture('preview-ui125')
 s=win.state();check(s['seconds']>0 and s['card'][1]>=0 and s['card'][1]+s['card'][3]<=s['client'][1],'countdown and confirmation inside viewport')
 accept();s=win.state();check(s['mode']==3 and s['size_disabled'] and s['resolution']=='2560 × 1440 (Desktop)' and s['active']['preset']=='1280x720','fullscreen desktop label preserves window preset')
 check(not s['feedback_visible'],'successful fullscreen acceptance stays quiet');capture('fullscreen-desktop-ui125')
 mode(0);accept();check(win.state()['client']==[1280,720],'return restores remembered 720p window')
 # A real isolated filesystem failure, without a controller test hook.
 candidates=list((out/'profile').rglob('display-preference.json'));assert len(candidates)==1,candidates
 blocked=Path(str(candidates[0])+'.tmp');blocked.mkdir()
 mode(1);accept();s=win.state()
 check(s['mode']==0 and s['feedback_visible'] and 'nicht gespeichert' in s['feedback'],'real storage failure rolls back visibly')
 capture('storage-error-720p-ui125');blocked.rmdir()
 mode(1);cancel();check(win.state()['mode']==0,'explicit cancellation returns window')
 mode(1);win.wait(lambda s:not s['preview'] and not s['applying'],seconds=20)
 check(win.state()['mode']==0 and win.state()['active']['preset']=='1280x720','real timeout restores last confirmed selection')
 top();win.click_rect(win.state()['info_switch']);win.wait(lambda s:s['section']=='help' and s['book_state']==4)
 check(not win.state()['mode_popup']['visible'],'help leaves no stale mode popup')
 # On the right page the same shortcut switches back to settings.
 win.key(9)
 # Explicitly use the observed settings-access control below (observer field).
 win.click_rect(win.state()['settings_access']);win.wait(lambda s:s['section']=='settings' and s['book_state']==4)
 scale(1.0);scale(1.25)
 win.click_rect(win.state()['info_return']);win.wait(lambda s:not s['info'] and s['book_state']==0)
 check(True,'catalog return after help/settings and UI roundtrip')
 win.click_rect(win.state()['catalog_info'][0]);win.wait(lambda s:s['info'] and s['book_state']==4)
 check(win.state()['ui_scale']==1.25 and win.state()['active']['preset']=='1280x720','revisit preserves options')
finally:
 (out/'n01-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('N01 Windows:',len(report['assertions']),'assertions;',len(report['captures']),'original PNGs')
