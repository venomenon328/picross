from pathlib import Path
import sys,os,time,subprocess,importlib,json,ctypes,hashlib
w=Path(__file__).parent;os.environ['ANZ_GUI']='gui-w05';out=w/'gui-w05'
results=[]; snapshots={};win=None

def launch():
 global win
 subprocess.run([sys.executable,str(w/'launch.py')],check=True,stdout=subprocess.DEVNULL)
 time.sleep(2)
 if win is None:import win as module;win=module
 else:win=importlib.reload(win)
 win.wait(lambda s:s.get('pid')==int((out/'pid.txt').read_text()) and not s['applying'],seconds=30)

def check(ok,name):
 results.append(dict(name=name,passed=bool(ok)));print(name,ok,flush=True)
 if not ok:raise AssertionError(name)

def snapshot(name,png=False):
 snapshots[name]=win.state()
 rect=win.wt.RECT();win.u.GetClientRect(win.hwnd,ctypes.byref(rect));snapshots[name]['win32_client']=[rect.right,rect.bottom]
 if png:win.capture(name)

def open_settings():
 win.click_rect(win.state()['catalog_info'][0]);win.wait(lambda s:s['info'] and s['book_state']==4)

def mode(index):
 win.choose('mode_control',index);return win.wait(lambda s:s['preview'])

def accept():
 win.click_rect(win.state()['accept']);return win.wait(lambda s:not s['preview'] and not s['applying'])

def cancel():
 win.click_rect(win.state()['cancel']);return win.wait(lambda s:not s['preview'] and not s['applying'])

def close(force=False):
 pid=int((out/'pid.txt').read_text())
 if force:
  subprocess.run(['taskkill','/PID',str(pid),'/T','/F'],check=True,stdout=subprocess.DEVNULL)
 else:win.u.PostMessageW(win.hwnd,0x10,0,0)
 handle=ctypes.windll.kernel32.OpenProcess(0x100000,False,pid)
 if handle:
  ctypes.windll.kernel32.WaitForSingleObject(handle,5000)
  ctypes.windll.kernel32.CloseHandle(handle)
 time.sleep(.3)
 trace=out/'engine.jsonl'
 if trace.exists():trace.rename(out/('engine-'+str(pid)+'.jsonl'))
 log=out/'stdout.log'
 if log.exists():log.rename(out/('stdout-'+str(pid)+'.log'))

def prefbytes():
 paths=list((out/'profile').rglob('display-preference.json'))
 return paths[0].read_bytes() if paths else None

try:
 launch();snapshot('start')
 s=win.state();check(s['mode']==0 and s['client']==[1920,1080] and s['resize_disabled'],'native fixed 1080p window')
 check(not win.u.GetWindowLongW(win.hwnd,-16)&0x50000,'Win32 no thickframe or maximize box')
 open_settings();snapshot('settings-1080p',True)
 s=mode(1);check(s['mode']==3 and s['client']==s['desktop'] and s['size_disabled'],'actual borderless fullscreen and disabled size')
 snapshot('borderless-preview')
 saved=prefbytes()
 # Real Alt-Tab focus roundtrip; no product callback or injected viewport input.
 win.activate();win.u.keybd_event(0x12,0,0,0);win.key(9);win.u.keybd_event(0x12,0,2,0);time.sleep(.3)
 s=win.state();check(s['preview'] and prefbytes()==saved,'Alt-Tab preserves preview and persisted state')
 win.activate();win.wait(lambda s:s['focused'],seconds=5);s=accept();check(s['active']['mode']=='borderless' and prefbytes() is not None,'explicit borderless acceptance after Alt-Tab on disk')
 saved=prefbytes()
 s=mode(2);check(s['mode']==4 and s['client']==s['desktop'],'actual exclusive fullscreen')
 snapshot('exclusive-preview',True)
 s=cancel();check(s['mode']==3 and prefbytes()==saved,'cancel exclusive restores confirmed borderless')
 mode(0);s=accept();check(s['mode']==0 and s['client']==[1920,1080],'return to remembered 1080p window')
 snapshot('return-window')
 check(snapshots['return-window']['win32_client']==[1920,1080],'independent Win32 client confirms exact returned preset')
 win.u.ShowWindow(win.hwnd,3);time.sleep(.8);s=win.state();check(s['mode']==0 and s['client']==[1920,1080],'external maximize cannot create a free lasting size')
 win.u.SetWindowPos(win.hwnd,0,0,0,1300,800,0x16);time.sleep(.9);s=win.state();check(s['client']==[1920,1080],'external resize restored to selected preset')
 s=mode(1);start=time.monotonic();win.wait(lambda s:not s['preview'] and not s['applying'],seconds=18)
 check(14<=time.monotonic()-start<=17 and win.state()['mode']==0,'real 15 second preview timeout')
 saved=prefbytes();mode(2);close(force=True)
 launch();s=win.state();check(s['mode']==0 and s['client']==[1920,1080] and prefbytes()==saved,'process death before acceptance restarts prior preference')
 open_settings()
 # Switch to a small real preset using the embedded native menu by OS pointer.
 win.click_rect(win.state()['size_control']);time.sleep(.1)
 # Eight rows: menu panel 9px plus row34px; first row is always 1280x720.
 s=win.state();rect=s['size_control'];win.click_rect([rect[0]+10,rect[1]+rect[3]+9,rect[2]-20,34]);win.wait(lambda s:s['preview']);s=accept()
 check(s['client']==[1280,720],'real 720p client preset')
 win.click_rect(win.state()['scale']);win.wait(lambda s:s['ui_scale']==1.25);snapshot('settings-720p-ui125',True)
 s=mode(2);snapshot('exclusive-ui125');s=accept();check(s['mode']==4 and s['active']['preset']=='1280x720','exclusive accepted with separate remembered small window')
 close();launch();s=win.state();check(s['mode']==4 and s['active']['preset']=='1280x720','fresh process restores accepted exclusive and last window preset')
 open_settings();mode(0);s=accept();check(s['client']==[1280,720],'return from persisted exclusive uses remembered 720p')
 # Two physical monitors, unchanged desktop modes/DPI; move only our window.
 old_screen=win.state()['screen'];win.u.SetWindowPos(win.hwnd,0,-2200,200,0,0,0x15);time.sleep(1)
 s=win.state();snapshot('second-monitor');check(s['screen']!=old_screen and s['mode']==0 and s['client']==[1280,720],'real monitor migration stays visible at fixed preset')
 close()
finally:
 binding=json.loads((w/'export.json').read_text())
 binding.update(results=results,snapshots=snapshots,stimulus='Win32 OS pointer, focus, close, resize and Alt-Tab. External read-only observer; no product state writes.',limits='Physical 2560x1440 monitors at 96 DPI only. 4K/16:10/720p desktop and changed DPI geometry are synthetic, not physical hardware evidence.',expires='2026-11-13',reviewer='ANZ-A-R01 independent reviewer',before_release='ANZ-A-M01 owner comfort trial remains open')
 (out/'report.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
