from pathlib import Path
import sys,time,json,ctypes,hashlib,os
import win
w=Path(__file__).parent;out=w/os.environ.get('ANZ_GUI','gui')
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
  win.u.mouse_event(0x0800,0,0,ctypes.c_ulong(direction*120).value,0);time.sleep(.06)
 win.record('wheel',direction=direction,count=count);time.sleep(.2)
def top():
 wheel(1,12);win.wait(lambda s:s['scroll_value']==0)
def choose(control,popup_key,index,count):
 win.key(27);time.sleep(.15)
 for attempt in range(2):
  win.click_rect(win.state()[control])
  try:s=win.wait(lambda s:s[popup_key]['visible'],seconds=2);break
  except RuntimeError:
   win.record('popup-retry',control=control,attempt=attempt);win.key(27);time.sleep(.2)
 else:raise AssertionError('popup failed '+control)
 p=s[popup_key];x,y=p['position'];width,height=p['size'];row=(height-18)/count
 win.click_rect([x+9,y+9+index*row,width-18,row]);time.sleep(.4)
def scale(value):
 top()
 if win.state()['ui_scale']!=value:
  choose('scale','scale_popup',1 if value==1.25 else 0,2)
  win.wait(lambda s:s['ui_scale']==value)
 time.sleep(.3)
def preset(index):
 top();choose('size_control','size_popup',index,8);win.wait(lambda s:s['preview'])
def mode(index):
 top();choose('mode_control','mode_popup',index,3);win.wait(lambda s:s['preview'])
def accept():
 win.click_rect(win.state()['accept']);win.wait(lambda s:not s['preview'] and not s['applying']);time.sleep(.3)
def cancel():
 win.click_rect(win.state()['cancel']);win.wait(lambda s:not s['preview'] and not s['applying']);time.sleep(.3)
def field(name):return next(x for x in win.state()['fields'] if x['name']==name)
def move(rect):
 p=win.wt.POINT(round(rect[0]+rect[2]/2),round(rect[1]+rect[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y)
def rest(name,size,u):
 top();win.key(27);s=win.state()
 check(s['client']==size and s['ui_scale']==u,name+' actual client and UI')
 check(not s['feedback_visible'] and not s['card_visible'],name+' quiet stable state')
 check([g['heading'] for g in s['section_boxes']]==['Anzeige','Rätselansicht'] and not s['quit_control'],name+' exactly two groups and no settings exit')
 check(s['heading']['font']=='Fraunces' and s['heading']['weight']=={'wght':600.0} and s['heading']['size']==round(28*u),name+' specified title role')
 col=s['settings_box'];scroll=s['scroll']
 check(col[2]<=640*u+1 and abs(col[0]+col[2]/2-scroll[0]-scroll[2]/2)<10*u,name+' centred safe left paper block')
 check(all(f['label'][0]<f['choice'][0]<f['help'][0] and abs(f['label'][1]+f['label'][3]/2-f['choice'][1]-f['choice'][3]/2)<1 and f['help'][2]>=44*u and f['help'][3]>=44*u for f in s['fields']),name+' measured inline HZ rows')
 capture(name)
 wheel(-1,14);s=win.state();b=s['scroll'];a=s['animation']
 check(a[1]>=b[1]-1 and a[1]+a[3]<=b[1]+b[3]+1,name+' bottom reachable with actual wheel')
 if size==[1280,720] and u==1.25:capture('settings-720p-ui125-bottom')
 # Keyboard focus from the view selector to its separate question mark.
 win.click_rect(win.state()['view_control']);win.key(27);time.sleep(.15);win.key(9)
 win.wait(lambda s:next(x for x in s['fields'] if x['name']=='Rätselansicht')['focus_tip'])
 f=field('Rätselansicht');t=f['focus_tip']
 check(t[0]>=0 and t[1]>=0 and t[0]+t[2]<=size[0] and t[1]+t[3]<=size[1],name+' keyboard tooltip inside viewport')
 if size==[1280,720] or u==1.25:capture(name+'-view-help')
 win.key(27);win.wait(lambda s:not any(x['focus_tip'] for x in s['fields']))
 check(True,name+' Escape dismisses focus tooltip')
 top();win.click_rect(win.state()['scale']);s=win.wait(lambda s:s['scale_popup']['visible'])
 p=s['scale_popup'];check(p['position'][0]>=0 and p['position'][1]>=0 and p['position'][0]+p['size'][0]<=size[0] and p['position'][1]+p['size'][1]<=size[1],name+' UI dropdown popup fits')
 if size==[1280,720] and u==1.25:capture('scale-options-720p-ui125')
 win.key(27);top()
try:
 win.wait(lambda s:s['info'] and not s['applying'],seconds=10)
 if win.state()['preview']:cancel()
 if win.state()['mode']!=0:mode(0);accept()
 scale(1.0)
 rest('settings-1080p-ui100',[1920,1080],1.0)
 scale(1.25);rest('settings-1080p-ui125',[1920,1080],1.25)
 preset(0);accept();win.wait(lambda s:s['client']==[1280,720]);scale(1.0)
 rest('settings-720p-ui100',[1280,720],1.0)
 scale(1.25);rest('settings-720p-ui125',[1280,720],1.25)
 top();win.click_rect(win.state()['mode_control']);win.wait(lambda s:s['mode_popup']['visible']);capture('mode-options-720p-ui125');win.key(27)
 # Mouse hover uses the original styled native tooltip, without focus.
 top();move(field('Fenstergröße')['help']);win.wait(lambda s:any('Desktopauflösung' in x['text'] for x in s['native_tips']),seconds=3)
 capture('size-hover-720p-ui125');check(True,'window-size tooltip opens by actual hover')
 move(win.state()['info_return']);time.sleep(.2)
 mode(1);capture('preview-borderless-ui125');accept()
 s=win.state();check(s['mode']==3 and s['size_disabled'] and s['resolution']=='2560 × 1440 (Desktop)' and s['active']['preset']=='1280x720','actual borderless uses desktop and retains window preset')
 # Disabled selector does not disable its sibling help control.
 win.click_rect(field('Fenstergröße')['help']);win.wait(lambda s:next(x for x in s['fields'] if x['name']=='Fenstergröße')['focus_tip'])
 capture('fullscreen-size-help-ui125');check(True,'separate fullscreen size help receives focus despite disabled selector')
 win.key(27);mode(2);accept();check(win.state()['mode']==4,'actual exclusive mode remains reachable')
 mode(0);win.wait(lambda s:s['client']==[1280,720]);capture('preview-window-720p-ui125');cancel()
 check(win.state()['mode']==4,'explicit cancellation restores confirmed exclusive')
 mode(0);accept();check(win.state()['client']==[1280,720],'window return restores confirmed preset')
 candidates=list((out/'profile').rglob('display-preference.json'));assert len(candidates)==1
 original=candidates[0].read_bytes();blocked=Path(str(candidates[0])+'.tmp');blocked.mkdir()
 mode(1);accept();s=win.state()
 check(s['mode']==0 and s['feedback_visible'] and 'nicht gespeichert' in s['feedback'] and candidates[0].read_bytes()==original,'real filesystem error rolls back with intact confirmed bytes')
 capture('storage-error-720p-ui125');blocked.rmdir()
 mode(1);win.wait(lambda s:not s['preview'] and not s['applying'],seconds=20)
 check(win.state()['mode']==0,'actual 15-second timeout restores window')
 top();win.click_rect(win.state()['info_switch']);win.wait(lambda s:s['section']=='help' and s['book_state']==4)
 check(not any(f['focus_tip'] for f in win.state()['fields']) and not win.state()['mode_popup']['visible'],'help transition dismisses settings popups and focus tooltips')
 win.click_rect(win.state()['settings_access']);win.wait(lambda s:s['section']=='settings' and s['book_state']==4)
 scale(1.0);scale(1.25)
 win.click_rect(win.state()['info_return']);win.wait(lambda s:not s['info'] and s['book_state']==0)
 check(True,'catalog return remains usable')
 win.click_rect(win.state()['catalog_info'][0]);win.wait(lambda s:s['info'] and s['book_state']==4)
 check(win.state()['ui_scale']==1.25,'settings revisit preserves session scale')
finally:
 (out/'n02-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('N02 Windows:',len(report['assertions']),'assertions;',len(report['captures']),'original PNGs')
