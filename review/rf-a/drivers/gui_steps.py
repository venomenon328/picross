import win,time,json,ctypes
from ctypes import wintypes as wt
from pathlib import Path
w=Path(__file__).parent
def menu(name,index):
    win.click_rect(win.state()[name]['box']);time.sleep(.25)
    m=win.state()[name];x,y=m['position'];width,height=m['size'];row=(height-18)/len(m['items'])
    win.click_rect([x+9,y+9+index*row,width-18,row]);time.sleep(.3)
    assert win.state()[name]['selected']==index,(name,index,win.state()[name])
def stable():
    time.sleep(.3)
    return win.wait(lambda s:not s['capture'] and not s['barrier'] and s['book_state'] in [0,3,4],8)
def card(id):return next(c for c in win.state()['cards'] if c['id']==id)
def record(name):
    s=win.state();win.record(name,state=s);print(name,s['session'],s['recent']['id'],s['positions'],flush=True)
def wheel(index,notches):
    win.activate();win.u.SetWindowPos(win.hwnd,wt.HWND(-1),0,0,0,0,0x13)
    r=win.state()['scrollers'][index];p=wt.POINT(round(r[0]+r[2]/2),round(r[1]+r[3]/2));win.u.ClientToScreen(win.hwnd,ctypes.byref(p));win.u.SetCursorPos(p.x,p.y);time.sleep(.1)
    win.u.mouse_event(0x800,0,0,ctypes.c_uint32(notches*120),0);time.sleep(.3)
    win.u.SetWindowPos(win.hwnd,wt.HWND(-2),0,0,0,0,0x13)
    win.record('wheel',index=index,notches=notches)
def click_control(name):win.click_rect(win.state()['buttons'][name]);stable()
if __name__=='__main__':
    assert not win.state()['recent']['visible'];record('no-marker')
    menu('sort',1)
    win.click_rect(card('pz-test-kat2-001')['box']);stable()
    assert win.state()['work'] and not win.state()['recent']['id'];record('open-does-not-mark')
    win.click_rect(win.state()['cell_boxes'][0]);win.wait(lambda s:s['recent']['id']=='pz-test-kat2-001')
    win.click_rect(win.state()['actions']['undo']);win.wait(lambda s:s['cursor']==0);record('undo-redo-only')
    win.click_rect(win.state()['actions']['redo']);win.wait(lambda s:s['cursor']==1);record('redo')
    win.click_rect(win.state()['catalog_return']);stable();win.capture('recent-1920-ui100')
    win.click_rect(card('pz-test-kat2-003')['box']);stable()
    win.click_rect(win.state()['cell_boxes'][2]);win.wait(lambda s:s['recent']['id']=='pz-test-kat2-003');record('second-id')
    win.click_rect(win.state()['catalog_return']);stable()
    win.click_rect(win.state()['filter_button']);time.sleep(.2)
    menu('status_filter',4)
    print(list(win.state()['buttons']),flush=True)
