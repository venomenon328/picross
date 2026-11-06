from pathlib import Path
import sys,os,json,time,subprocess,ctypes
w=Path(__file__).parent;os.environ['ANZ_GUI']='gui-w05';out=w/'gui-w05'
subprocess.run([sys.executable,str(w/'launch.py')],check=True)
time.sleep(3)
import win
win.wait(lambda s:s['pid']==int((out/'pid.txt').read_text()) and not s['applying'],seconds=30)
win.click_rect(win.state()['catalog_info'][0]);win.wait(lambda s:s['info'] and s['book_state']==4)
win.click_rect(win.state()['scale']);win.wait(lambda s:s['ui_scale']==1.25)
def capture(label):
 win.capture(label);time.sleep(.4)
 report['captures'][label]=win.state()
def size(index):
 win.click_rect(win.state()['size_control']);s=win.wait(lambda s:s['size_popup']['visible']);p=s['size_popup'];x,y=p['position'];width,height=p['size'];row=(height-18)/8
 win.click_rect([x+9,y+9+row*index,width-18,row]);win.wait(lambda s:s['preview'])
def accept():
 win.click_rect(win.state()['accept']);win.wait(lambda s:not s['preview'] and not s['applying'])
def cancel():
 win.click_rect(win.state()['cancel']);win.wait(lambda s:not s['preview'] and not s['applying'])
report={'head':json.loads((w/'export.json').read_text())['source_head'],'captures':{}}
assert win.state()['client']==[1280,720]
capture('settings-720p-ui125')
win.click_rect(win.state()['mode_control']);win.wait(lambda s:s['mode_popup']['visible']);capture('mode-options-720p-ui125');win.key(27);time.sleep(.2)
size(1);accept();size(0);capture('confirmation-720p-ui125');cancel()
win.choose('mode_control',2);win.wait(lambda s:s['preview']);capture('exclusive-preview');cancel()
win.u.PostMessageW(win.hwnd,0x10,0,0);time.sleep(1)
(out/'visual.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('visual captures completed')
