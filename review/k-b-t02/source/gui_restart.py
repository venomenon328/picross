from gui_steps import *
assert win.state()['recent']['id']=='pz-test-kat2-003' and win.state()['album']
record('true-restart-restores-marker-starts-catalog')
win.u.SetWindowPos(win.hwnd,wt.HWND(0),20,20,0,0,0x15)
win.capture('centered-1920-ui100')
win.click_rect(win.state()['filter_button']);time.sleep(.3)
menu('status_filter',4)
win.click_rect(win.state()['buttons']['Übernehmen']);time.sleep(.4)
assert win.state()['album'],win.state()['book_state']
wheel(0,-3);wheel(1,-5)
before=win.state();assert all(x>0 for x in before['positions']),before['positions'];record('excluded-both-scrolls')
win.click_rect(before['recent']['box']);stable()
assert win.state()['session']=='pz-test-kat2-003' and win.state()['work'];record('excluded-direct-open')
win.click_rect(win.state()['catalog_return']);stable()
after=win.state();assert after['filters']==before['filters'] and after['positions']==before['positions'];record('both-scrolls-return')
win.capture('excluded-return')
