from gui_steps import *
def scale(index):
    click_control('Einstellungen / Info');menu('scale',index);stable()
    win.click_rect(win.state()['back']);stable()
def resize(width,height):
    r=wt.RECT();c=wt.RECT();win.u.GetWindowRect(win.hwnd,ctypes.byref(r));win.u.GetClientRect(win.hwnd,ctypes.byref(c))
    win.u.SetWindowPos(win.hwnd,wt.HWND(0),20,20,width+(r.right-r.left-c.right),height+(r.bottom-r.top-c.bottom),0x14)
    time.sleep(.6);stable();assert win.state()['client']==[width,height]
def check_layout(label):
    s=win.state();r=s['recent'];p=r['box'];c=r['caption'];d=r['detail'];preview=r['preview']
    assert r['visible'] and abs((c[1]+d[1]+d[3])/2-(p[1]+p[3]/2))<1
    assert abs(c[0]-p[0]-12*s['ui'])<1
    assert preview[2]<=56*s['ui']+.1 and p[1]+p[3]<=s['sort']['box'][1]
    record(label);win.capture(label)
if __name__=='__main__':
    check_layout('final-1920-ui100')
    scale(1);check_layout('final-1920-ui125')
    resize(1280,720);check_layout('final-1280-ui125')
    scale(0);check_layout('final-1280-ui100')
    resize(1920,1080)
