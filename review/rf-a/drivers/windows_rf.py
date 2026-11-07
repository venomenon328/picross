from gui_sizes import *
from PIL import Image
import hashlib,math
observations=[]
def snap(label,filled=None,index=21):
 s=stable();p=s['recent'];assert s['album'] and not p['hover'],(label,'already hovered')
 client=s['client'];u=s['ui'];box=p['box'];width=p['heading_width']
 assert min(abs(box[2]-width/2),abs(box[2]-width))<.01
 assert abs(p['caption'][0]-box[0]-12*u)<.01
 assert abs((p['caption'][1]+p['detail'][1]+p['detail'][3])/2-(box[1]+box[3]/2))<.01
 assert p['preview'][2:]==[56*u,56*u]
 assert p['caption'][0]+p['caption'][2]<=p['preview'][0]-8*u+.01
 assert abs(s['sort']['box'][1]-box[1]-box[3]-8*u)<.1
 win.capture(label)
 win.wait(lambda t:(win.out/(label+'.png')).exists())
 path=win.out/(label+'.png');crop=json.loads((win.out/(label+'-crop.json')).read_text())
 im=Image.open(path);r=p['preview'];step=r[2]/20
 xy=(int(r[0]+(index%20+.5)*step)-crop['x'],int(r[1]+(index//20+.5)*step)-crop['y'])
 rgb=im.convert('RGB').getpixel(xy)
 if filled is not None:assert (max(rgb)<120) if filled else (min(rgb)>220),(label,rgb,xy)
 observations.append(dict(scenario=label,state=s,crop=crop,pixel=dict(index=index,xy=xy,rgb=rgb,filled=filled),file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 (win.out/'observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
 print('PASS',label,client,u,box[2],width,'pixel',rgb,flush=True)
 return im,crop,s
def hover_compare(label,before):
 s=win.state();r=s['recent']['box'];point=wt.POINT(round(r[0]+24),round(r[1]+24));win.u.ClientToScreen(win.hwnd,ctypes.byref(point));win.u.SetCursorPos(point.x,point.y);time.sleep(.2)
 assert win.state()['recent']['hover']
 win.capture(label);win.wait(lambda t:(win.out/(label+'.png')).exists())
 im=Image.open(win.out/(label+'.png'));crop=json.loads((win.out/(label+'-crop.json')).read_text());p=s['recent']['preview'];b=before[1]
 rect=(math.ceil(p[0])-crop['x']+2,math.ceil(p[1])-crop['y']+2,math.floor(p[0]+p[2])-crop['x']-2,math.floor(p[1]+p[3])-crop['y']-2)
 assert im.crop(rect).tobytes()==before[0].crop(rect).tobytes(),label
 path=win.out/(label+'.png');observations.append(dict(scenario=label,hover=True,unchanged_miniature=True,file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),crop=crop))
 (win.out/'observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
 # Park on the same catalog-return screen position, outside the panel.
 p=wt.POINT(round(s['catalog_return'][0]+20),round(s['catalog_return'][1]+20));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y);time.sleep(.15)
def open_card(identifier):
 for attempt in range(50):
  c=card(identifier)['box'];a=win.state()['scrollers'][0];top=max(c[1],a[1]);bottom=min(c[1]+c[3],a[1]+a[3])
  if bottom-top>20:win.click_rect([max(c[0],a[0])+8,(top+bottom)/2,0,0]);stable();return
  wheel(0,3 if c[1]<a[1] else -3)
 raise AssertionError(identifier)
def change_size(width,height):
 click_control('Einstellungen / Info')
 desired=1 if width==2560 else 0
 if win.state()['display_mode']['selected']!=desired:
  menu('display_mode',desired);win.wait(lambda s:s['display_preview']);win.click_rect(win.state()['display_accept']);stable()
 if desired==0:
  index={(1280,720):0,(1920,1080):3,(1920,1200):4}[(width,height)]
  if win.state()['display_size']['selected']!=index:
   menu('display_size',index);win.wait(lambda s:s['display_preview']);win.click_rect(win.state()['display_accept']);stable()
  # The desktop has a second screen at a negative origin. Keep only our
  # own window in the known visible work area before issuing another click.
  win.u.SetWindowPos(win.hwnd,wt.HWND(0),20,20,0,0,0x15);time.sleep(.3)
 win.click_rect(win.state()['back']);stable()
 assert win.state()['client']==[width,height],win.state()['client']
stable();menu('sort',1)
assert not win.state()['recent']['visible']
open_card('pz-test-kat2-001');assert not win.state()['recent']['id']
win.click_rect(win.state()['cell_boxes'][0]);win.wait(lambda s:s['recent']['id']=='pz-test-kat2-001' and not s['recent']['error'])
win.click_rect(win.state()['catalog_return']);stable()
before=snap('A-1920-ui100-before',True);hover_compare('A-1920-ui100-after',before)
win.click_rect(win.state()['recent']['box']);stable()
win.click_rect(win.state()['actions']['undo']);win.wait(lambda s:s['cursor']==0)
win.click_rect(win.state()['catalog_return']);stable();snap('undo-empty-before',False)
win.click_rect(win.state()['recent']['box']);stable();win.click_rect(win.state()['actions']['redo']);win.wait(lambda s:s['cursor']==1)
win.click_rect(win.state()['catalog_return']);stable();snap('redo-before',True)
open_card('pz-test-kat2-003');win.click_rect(win.state()['cell_boxes'][2]);win.wait(lambda s:s['recent']['id']=='pz-test-kat2-003')
win.click_rect(win.state()['cell_boxes'][0]);win.click_rect(win.state()['catalog_return']);stable();snap('B-before',True)
for width,height,index in [(1920,1080,1),(2560,1440,0),(2560,1440,1),(1920,1200,1),(1280,720,1),(1920,1080,0)]:
 if win.state()['client'] != [width,height]:change_size(width,height)
 if win.state()['ui']!=(1 if index==0 else 1.25):scale(index)
 label=f'layout-{width}x{height}-ui{100 if index==0 else 125}'
 snap(label)
 if (width,height,index)==(2560,1440,0):assert abs(win.state()['recent']['box'][2]*2-win.state()['recent']['heading_width'])<.01
 if (width,height,index)==(1280,720,1):assert abs(win.state()['recent']['box'][2]-win.state()['recent']['heading_width'])<.01
# Reset B via its actual catalog card; the other recent does not return.
win.click_rect(card('pz-test-kat2-003')['reset']);win.wait(lambda s:s['reset_dialog']);win.click_rect(win.state()['reset_ok']);stable()
assert not win.state()['recent']['visible'] and not win.state()['recent']['id']
observations.append(dict(scenario='reset-hides-no-fallback',state=win.state()))
open_card('pz-test-kat2-001');win.click_rect(win.state()['catalog_return']);stable();assert not win.state()['recent']['id']
observations.append(dict(scenario='view-only-reentry-does-not-mark',state=win.state()))
(win.out/'observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
click_control('Beenden')
print('RF-A-T02 Windows mouse and original pixel checks passed',flush=True)
