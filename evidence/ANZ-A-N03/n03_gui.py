from pathlib import Path
import sys,time,json,ctypes,hashlib,os
import win
w=Path(__file__).parent;out=w/os.environ.get('ANZ_GUI','gui')
report={'source_head':json.loads((w/'export.json').read_text(encoding='utf-8'))['source_head'],'assertions':[],'captures':{},'catalog_references':{}}
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

def stable():
 return win.wait(lambda s:not s['applying'] and s['book_state'] in [0,3,4],seconds=8)

def back_labels(destination):
 s=win.state()
 check(all(s[k]['text']=='Zurück' and s[k]['tooltip']==destination and s[k]['accessibility']==destination for k in ['left_back','right_back']),'both short back labels retain '+destination)

def rest(name,size,u):
 top();win.key(27);s=stable()
 check(s['client']==size and s['ui_scale']==u,name+' actual client/UI')
 check([g['heading'] for g in s['section_boxes']]==['Anzeige','Rätselansicht'],name+' exactly two framed groups')
 check(s['heading']['resource']=='res://art/drawing/BaksoDaging-Regular.ttf' and s['heading']['size']==round(28*u),name+' actual Bakso resource and 28 x UI')
 check(all(g['font']['resource']=='res://art/drawing/BaksoDaging-Regular.ttf' and g['font']['size']==round(20*u) for g in s['section_boxes']),name+' owner E01 smaller Bakso 20 groups')
 check(sum(bool(f['help']) for f in s['fields'])==2,name+' exactly two helps')
 starts=[f['choice'][0] for f in s['fields']];labels=[f['label'][0] for f in s['fields']]
 check(max(starts)-min(starts)<1 and max(labels)-min(labels)<1,name+' aligned label/choice axes')
 for f in s['fields']:
  if f['name'] in ['Anzeigemodus','UI-Skalierung']:
   check(not f['help'] and not f['tooltip_text'] and f['child_count']==2 and abs(f['choice'][0]+f['choice'][2]-f['row'][0]-f['row'][2])<1,name+' full width without help/focus placeholder '+f['name'])
  else:
   check(f['child_count']==3 and f['help'][2]>=44*u and f['help'][3]>=44*u and abs(f['help'][0]+f['help'][2]-f['row'][0]-f['row'][2])<1,name+' help at safe right edge '+f['name'])
 col=s['settings_box'];scroll=s['scroll']
 check(col[2]<=640*u+1 and abs(col[0]+col[2]/2-scroll[0]-scroll[2]/2)<10*u,name+' centred safe left paper')
 back_labels('Zurück zum Katalog')
 capture(name)
 wheel(-1,14);s=win.state();a=s['animation'];b=s['scroll']
 check(a[1]>=b[1]-1 and a[1]+a[3]<=b[1]+b[3]+1,name+' actual wheel reaches bottom')
 if size==[1280,720] and u==1.25:capture('settings-720p-ui125-bottom')
 top()

def catalog_reference(u,capture_name=None):
 win.click_rect(win.state()['info_return']);s=win.wait(lambda s:s['album_visible'] and s['book_state']==0,seconds=8)
 ref=s['catalog_heading'];report['catalog_references'][str(u)]=ref
 check(ref['visible'] and ref['resource']=='res://art/drawing/BaksoDaging-Regular.ttf' and ref['size']==round(28*u),'actual visible catalog Bakso reference UI'+str(u))
 if capture_name:capture(capture_name)
 win.click_rect(s['catalog_info'][0]);s=win.wait(lambda s:s['info'] and s['book_state']==4)
 check(s['heading']['instance']==ref['instance'] and s['heading']['size']==ref['size'],'same actual font object and size catalog/settings UI'+str(u))

try:
 s=stable();check(s['album_visible'],'fresh exported player starts in actual catalog')
 win.click_rect(s['catalog_info'][0]);win.wait(lambda s:s['info'] and s['book_state']==4)
 catalog_reference(1.0,'catalog-title-1080p-ui100')
 rest('settings-1080p-ui100',[1920,1080],1.0)
 scale(1.25);catalog_reference(1.25);rest('settings-1080p-ui125',[1920,1080],1.25)
 preset(0);accept();win.wait(lambda s:s['client']==[1280,720]);scale(1.0)
 rest('settings-720p-ui100',[1280,720],1.0)
 scale(1.25);rest('settings-720p-ui125',[1280,720],1.25)
 # Both help entry methods use the existing tooltip; no help on the other rows.
 move(field('Fenstergröße')['help']);win.wait(lambda s:any('Desktopauflösung' in x['text'] for x in s['native_tips']),seconds=4)
 capture('size-hover-720p-ui125');check(True,'actual hover opens size explanation')
 move(win.state()['info_return']);wheel(-1,14)
 win.click_rect(win.state()['view_control']);win.key(27);time.sleep(.15);win.key(9)
 s=win.wait(lambda s:next(f for f in s['fields'] if f['name']=='Rätselansicht')['focus_tip'])
 capture('view-focus-720p-ui125');check('kleinere Zellen' in field('Rätselansicht')['tooltip_text'],'keyboard view help retains complete explanation')
 win.key(27);win.wait(lambda s:not any(f['focus_tip'] for f in s['fields']));check(True,'Escape dismisses help')
 top();win.click_rect(win.state()['mode_control']);s=win.wait(lambda s:s['mode_popup']['visible'])
 p=s['mode_popup'];check(p['position'][0]>=0 and p['position'][0]+p['size'][0]<=1280,'expanded mode popup stays in client')
 capture('mode-popup-720p-ui125');win.key(27)
 mode(1);accept();s=win.state()
 check(s['mode']==3 and s['size_disabled'] and s['resolution']=='2560 × 1440 (Desktop)','fullscreen size field stays disabled with actual desktop')
 win.click_rect(field('Fenstergröße')['help']);win.wait(lambda s:next(f for f in s['fields'] if f['name']=='Fenstergröße')['focus_tip'])
 capture('fullscreen-size-help-ui125');check(True,'disabled size field retains separate focus help')
 win.key(27);mode(0);win.wait(lambda s:s['client']==[1280,720]);capture('preview-window-720p-ui125');cancel()
 check(win.state()['mode']==3,'actual cancellation restores confirmed fullscreen')
 mode(0);accept()
 preference=list((out/'profile').rglob('display-preference.json'));assert len(preference)==1
 original=preference[0].read_bytes();blocked=Path(str(preference[0])+'.tmp');blocked.mkdir()
 try:
  mode(1);accept();s=win.state()
  check(s['mode']==0 and s['feedback_visible'] and 'nicht gespeichert' in s['feedback'] and preference[0].read_bytes()==original,'real preference write failure rolls back without corrupting confirmed bytes')
  capture('storage-error-720p-ui125')
 finally:blocked.rmdir()
 # Help and settings both return to the true catalog origin.
 win.click_rect(win.state()['info_switch']);win.wait(lambda s:s['section']=='help' and s['book_state']==4)
 back_labels('Zurück zum Katalog');capture('catalog-origin-help-back')
 win.click_rect(win.state()['help_return']);s=win.wait(lambda s:s['album_visible'] and s['book_state']==0,seconds=8)
 check(True,'actual help back returns to catalog')
 win.click_rect(s['catalog_cards'][0]);s=win.wait(lambda s:s['work_visible'] and s['book_state']==3,seconds=8)
 win.click_rect(s['board_cell']);time.sleep(.5);s=win.state()
 before=s['player'];report['work_before']=s
 check(any(c!=-1 for c in before['cells']) and bool(before['history']),'actual work input creates cells/history before return probes')
 win.click_rect(s['menu']);s=win.wait(lambda s:s['info'] and s['book_state']==4)
 check(s['information_origin']=='work','actual settings retains work origin');back_labels('Zurück zum Rätsel');capture('work-origin-settings-back')
 win.click_rect(s['info_return']);s=win.wait(lambda s:s['work_visible'] and s['book_state']==3)
 check(s['player']==before,'settings back preserves real cell/history/clue view')
 win.click_rect(s['help']);s=win.wait(lambda s:s['info'] and s['section']=='help' and s['book_state']==4)
 back_labels('Zurück zum Rätsel');capture('work-origin-help-back')
 win.click_rect(s['help_return']);s=win.wait(lambda s:s['work_visible'] and s['book_state']==3)
 report['work_after']=s;check(s['player']==before,'help back preserves real cell/history/clue view')
 win.u.PostMessageW(win.hwnd,0x10,0,0);time.sleep(.7)
 check(not win.u.IsWindow(win.hwnd),'actual WM close ends player after flush')
finally:
 (out/'n03-report.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print('N03 Windows:',len(report['assertions']),'assertions;',len(report['captures']),'original PNGs')
