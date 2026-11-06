from pathlib import Path
import sys,os,time,json,ctypes,hashlib
sys.path.insert(0,str(Path(__file__).parent))
import win
w=Path(__file__).parent;out=w/os.environ.get('BTI_GUI','gui');results=[]
def check(ok,label):
 results.append(dict(check=label,passed=bool(ok)))
 if not ok: raise AssertionError(label)
def save():
 (out/'checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def wait(test):return win.wait(test,seconds=10)
def idle():return wait(lambda s:s['book_state'] in [0,3,4] and not s['capture'] and not s['barrier'])
def press(key):
 before=win.state();win.click_rect(before[key]['box'] if key in ['back','switch'] else before[key])
 if key=='switch':wait(lambda s:s['section']!=before['section'] and s['book_state']==4 and not s['capture'])
 elif key=='back' and not before['status_visible']:wait(lambda s:s['book_state']==(0 if before['origin']=='album' else 3) and not s['capture'])
 elif key in ['menu','help']:wait(lambda s:s['book_state']==4 and s['section']==('settings' if key=='menu' else 'help') and not s['capture'])
 else:time.sleep(.5)
 return idle()
def move(rect):
 win.activate();p=win.wt.POINT(round(rect[0]+rect[2]/2),round(rect[1]+rect[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y);time.sleep(.1)
def wheel(delta):
 move(win.state()['scroll']);win.u.mouse_event(0x0800,0,0,delta,0);win.record('wheel',delta=delta);time.sleep(.25)
def resize(width,height):
 # Use the actual display controls: external WM_SIZE is intentionally corrected.
 if width==2560:
  option('mode',1);confirm_display()
 else:
  if win.state()['client']==[2560,1440]:option('mode',0);confirm_display()
  win.u.SetWindowPos(win.hwnd,None,30,30,0,0,0x15);time.sleep(.6)
  items=win.state()['options']['size']['items']
  index=next(i for i,item in enumerate(items) if item['text']==f'{width} × {height}')
  option('size',index);confirm_display()
 wait(lambda s:s['client']==[width,height]);time.sleep(.7)
 check(win.state()['client']==[width,height],'confirmed client '+str([width,height]))
def option(kind,index):
 key={'mode':'display_mode','size':'display_size','view':'view_choice'}[kind]
 win.click_rect(win.state()[key]);s=wait(lambda s:s['options'][kind]['visible']);p=s['options'][kind];x,y=p['position'];width,height=p['size'];row=(height-18)/len(p['items'])
 win.click_rect([x+9,y+9+index*row,width-18,row]);win.record('option',kind=kind,index=index)
def confirm_display():
 wait(lambda s:s['display_preview'] and not s['display_applying']);win.click_rect(win.state()['display_accept']);wait(lambda s:not s['display_preview'] and not s['display_applying'])
def scale(index):
 win.click_rect(win.state()['scale']);s=wait(lambda s:s['scale_popup']['visible']);p=s['scale_popup'];x,y=p['position'];width,height=p['size'];row=(height-18)/2
 win.click_rect([x+9,y+9+index*row,width-18,row]);wait(lambda s:s['ui']==(1.25 if index else 1));idle()
def snapshot(label,capture=False):
 s=idle();win.record('checkpoint',name=label)
 title=next(t for t in s['titles'] if t['visible']);x,y,width,height=title['box'];ix,iy,iw,ih=title['image'];ox,oy,ow,oh=title['ink']
 check(ix>=-0.001 and iy>=-0.001 and ix+iw<=width+.001 and iy+ih<=height+.001,label+': full image fits')
 check(abs(ox+ow/2-width/2)<.01 and abs(oy+oh/2-height/2)<.01,label+': optical ink centred')
 check(not title['fallback'],label+': only image title')
 if s['info']:
  bx,by,bw,bh=s['back']['box'];sx,sy,sw,sh=s['scroll'];vx,vy,vw,vh=s['switch']['box'];u=s['ui']
  check(bw>=44*u and bh>=44*u and vw>=44*u and vh>=44*u,label+': full hit targets')
  check(y+height<sy and sy+sh<by and by+bh<=s['client'][1],label+': title scroll nav separate')
  check(s['back']['accessibility']==('Zurück zum Katalog' if s['origin']=='album' else 'Zurück zum Rätsel'),label+': real return origin')
 results.append(dict(check=label,passed=True,client=s['client'],ui=s['ui'],title=title,scroll=s['scroll'],section=s['section'],chapter=s['chapter'],positions=s['positions'],origin=s['origin'],snapshots=s['snapshots'],capture=s['capture']))
 if capture:
  win.capture(label);wait(lambda s:(out/(label+'.png')).exists())
def run():
 # Continue the untouched EXE/PCK launched for the first original inspections.
 win.u.SetWindowPos(win.hwnd,None,30,30,0,0,0x15);time.sleep(.5)
 win.click_rect(win.state()['catalog_info'][0]);wait(lambda s:s['book_state']==4 and not s['capture']);snapshot('settings-1920-ui100',True);press('switch')
 snapshot('help-1920-ui100',True)
 win.click_rect(win.state()['chapters'][2]);wait(lambda s:s['chapter']==2)
 wheel(-1200);s=win.state();before=s['positions'][1];check(before>0,'OS wheel scrolls help')
 press('switch');press('switch');check(win.state()['chapter']==2 and win.state()['positions'][1]==before,'chapter and scroll survive natural settings pan')
 snapshot('help-scroll-memory')
 press('switch');scale(1);resize(1280,720)
 snapshot('settings-1280-ui125',True)
 wheel(-2400);s=win.state();check(s['scroll_value']>=s['scroll_max']-s['scroll_page']-1,'tight settings scroll end reachable')
 press('switch');win.click_rect(win.state()['chapters'][0]);wheel(-9600)
 s=win.state();check(s['scroll_value']>=s['scroll_max']-s['scroll_page']-1,'tight help scroll end reachable')
 snapshot('help-1280-ui125',True)
 press('back');check(win.state()['album'],'help returns to catalog')
 continuation()
def continuation():
 check(win.state()['album'],'help returns to catalog after complete natural animation')
 snapshot('catalog-1280-ui125',True)
 # Resize/UI return and large actual framebuffer, no desktop display-mode change.
 win.click_rect(win.state()['catalog_info'][0]);idle();scale(0);scale(1);resize(2560,1440)
 snapshot('settings-2560-ui125',True)
 press('switch');snapshot('help-2560-ui125',True)
 press('back');snapshot('catalog-2560-ui125',True)
 win.click_rect(win.state()['catalog_info'][0]);idle();resize(1920,1200);scale(0);snapshot('settings-1920x1200-ui100')
 press('switch');snapshot('help-1920x1200-ui100');press('switch');scale(1);scale(0)
 check(win.state()['ui']==1,'UI100 to125 to100 real popup round trip')
 resize(1920,1080);press('back')
 work_case()
def work_case():
 # Work-origin interaction plus actual filesystem failure, blocked back and retry.
 if not win.state()['info']:
  win.click_rect(win.state()['cards'][0]);wait(lambda s:s['book_state']==3 and not s['capture'])
  press('menu')
 check(win.state()['origin']=='work','work opens settings with distinct origin')
 # Change view with its actual existing option after a .tmp obstacle is created.
 slot=Path(win.state()['slot']).resolve();check(slot.is_relative_to((out/'profile').resolve()),'save inside own isolated profile')
 slot.parent.mkdir(parents=True,exist_ok=True)
 obstacle=slot.with_suffix('.tmp');obstacle.mkdir()
 before_bytes=slot.read_bytes() if slot.exists() else None
 try:
  option('view',1);wait(lambda s:s['status_visible'])
  check(slot.read_bytes()==before_bytes if before_bytes is not None else not slot.exists(),'failed flush preserves primary bytes')
  press('back');check(win.state()['info'] and win.state()['status_visible'],'settings back blocked by actual save failure')
  snapshot('settings-save-failure')
  press('switch');press('back');check(win.state()['section']=='help' and win.state()['info'],'help back blocked by same save failure')
  snapshot('help-save-failure',True)
 finally:obstacle.rmdir()
 press('back');check(win.state()['work'] and not win.state()['status_visible'],'retry back flushes and returns to actual work origin')
 press('help');check(win.state()['chapter']==0,'new work visit starts first help chapter')
 move(win.state()['back']['box']);time.sleep(.9)
 check(any(t['text']=='Zurück zum Rätsel' for t in win.state()['tooltips']),'actual back tooltip names work origin')
 win.key(0x09);time.sleep(.2);check(bool(win.state()['focus']),'keyboard focus remains reachable on help')
 before=win.state()['player'];press('switch');press('back');check(win.state()['player']['cells']==before['cells'] and win.state()['player']['history']==before['history'],'info navigation leaves cells/history unchanged')
 check(win.state()['snapshots']==0 and not win.state()['capture'],'all capture resources freed after natural movement')
 win.u.PostMessageW(win.hwnd,0x10,0,0);win.record('close');time.sleep(.8)
if __name__=='__main__':
 try:
  if '--workfinish' in sys.argv:
   results=json.loads((out/'checks.json').read_text(encoding='utf-8'));results=[x for x in results if x['passed']];work_case()
  elif '--finish' in sys.argv:
   results=json.loads((out/'checks.json').read_text(encoding='utf-8'));results=[x for x in results if x['passed']]
   snapshot('help-1920x1200-ui100');press('switch');scale(1);scale(0);check(win.state()['ui']==1,'UI100 to125 to100 real popup round trip');resize(1920,1080);press('back');work_case()
  elif '--continue' in sys.argv:
   results=json.loads((out/'checks.json').read_text(encoding='utf-8'));results=[x for x in results if x['passed']];continuation()
  else:run()
 finally:save()
