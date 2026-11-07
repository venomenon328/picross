from gui_steps import *
from gui_sizes import check_layout,scale
assert win.state()['album'] and not win.state()['recent']['visible'];record('completed-restart-hidden')
win.click_rect(card('pz-test-kat2-003')['box']);stable()
win.click_rect(win.state()['cell_boxes'][2]);win.wait(lambda s:s['recent']['id']=='pz-test-kat2-003')
win.click_rect(win.state()['catalog_return']);stable()
click_control('Einstellungen / Info');menu('display_size',0)
win.wait(lambda s:s['display_preview']);win.click_rect(win.state()['display_accept']);time.sleep(.3)
assert win.state()['client']==[1280,720],win.state()['client']
menu('scale',1);stable();win.click_rect(win.state()['back']);stable();check_layout('final-1280-ui125')
scale(0);check_layout('final-1280-ui100')
win.u.PostMessageW(win.hwnd,0x10,0,0)
