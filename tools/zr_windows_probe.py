"""Native export EXE mouse delivery, observed through isolated saves/own HWND.

Win32 OS-injected stimuli are explicit; never a physical owner acceptance claim.
The editor reads layout from the PCK only. All tested gestures run in the EXE.
"""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes as w
import json
from pathlib import Path
import platform
import struct
import subprocess
import time
import p1_preflight as toolchain

ROOT = Path(__file__).resolve().parents[1]

class CursorInfo(ctypes.Structure):
    _fields_=[('size',w.DWORD),('flags',w.DWORD),('cursor',w.HANDLE),('point',w.POINT)]

class GuiInfo(ctypes.Structure):
    _fields_=[('size',w.DWORD),('flags',w.DWORD),('active',w.HWND),('focus',w.HWND),
              ('capture',w.HWND),('menu',w.HWND),('move',w.HWND),('caret',w.HWND),('rect',w.RECT)]

class MonitorInfo(ctypes.Structure):
    _fields_=[('size',w.DWORD),('monitor',w.RECT),('work',w.RECT),('flags',w.DWORD)]


def capture(user, hwnd, size, path):
    from PIL import Image
    gdi = ctypes.windll.gdi32
    user.GetDC.restype = w.HDC
    user.GetDC.argtypes = [w.HWND]
    user.PrintWindow.argtypes = [w.HWND,w.HDC,w.UINT]
    user.ReleaseDC.argtypes = [w.HWND,w.HDC]
    gdi.CreateCompatibleDC.restype = w.HDC
    gdi.CreateCompatibleDC.argtypes = [w.HDC]
    gdi.CreateCompatibleBitmap.restype = w.HBITMAP
    gdi.CreateCompatibleBitmap.argtypes = [w.HDC,ctypes.c_int,ctypes.c_int]
    gdi.SelectObject.restype = w.HANDLE
    gdi.SelectObject.argtypes = [w.HDC,w.HANDLE]
    gdi.DeleteObject.argtypes = [w.HANDLE]
    gdi.DeleteDC.argtypes = [w.HDC]
    gdi.GetDIBits.argtypes = [w.HDC,w.HBITMAP,w.UINT,w.UINT,ctypes.c_void_p,ctypes.c_void_p,w.UINT]
    width,height = size
    dc = user.GetDC(hwnd)
    memory = gdi.CreateCompatibleDC(dc)
    bitmap = gdi.CreateCompatibleBitmap(dc,width,height)
    previous = gdi.SelectObject(memory,bitmap)
    try:
        if not user.PrintWindow(hwnd,memory,3):
            raise RuntimeError("Owned HWND capture failed")
        gdi.SelectObject(memory,previous)
        header = struct.pack('<IiiHHIIiiII',40,width,-height,1,32,0,width*height*4,0,0,0,0)
        pixels = ctypes.create_string_buffer(width*height*4)
        if gdi.GetDIBits(memory,bitmap,0,height,pixels,header,0)!=height:
            raise RuntimeError("Owned HWND bitmap read failed")
        image = Image.frombytes('RGB',(width,height),pixels.raw,'raw','BGRX')
        if len(image.getcolors(width*height))<16:
            raise RuntimeError("Owned HWND image stayed blank")
        image.save(path)
    finally:
        gdi.SelectObject(memory,previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(memory)
        user.ReleaseDC(hwnd,dc)


def probe(player: Path, engine: Path, output: Path, expected_head: str) -> None:
    if platform.system() != "Windows":
        raise RuntimeError("Native Windows required")
    report = json.loads((player.parent / "product-report.json").read_text(encoding="utf-8"))
    if report["source_commit"]!=expected_head or report["source_tree_dirty"]:
        raise RuntimeError("Expected clean commit-bound Product export")
    for name,digest in report["export_files"].items():
        toolchain.verify_sha256(player.parent/name,digest)
    version = subprocess.check_output([str(engine),'--version'],text=True).strip()
    if version!=toolchain.EXPECTED_VERSION:
        raise RuntimeError("Wrong bound editor")
    output.mkdir(parents=True,exist_ok=False)
    layout_env = toolchain.isolated_environment(output/'layout-profile','Windows')
    layout_env['ZR_WINDOWS_PLAN']=str(output/'layout.json')
    script=ROOT/'game/tests/zr_windows_probe.gd'
    layout=subprocess.run([str(engine),'--headless','--main-pack',str(player.with_suffix('.pck')),
                           '--script',str(script),'--','--p1-capture'],cwd=player.parent,
                          env=layout_env,capture_output=True,text=True,timeout=60,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    (output/'layout.log').write_text(layout.stdout+layout.stderr,encoding='utf-8',newline='\n')
    if layout.returncode or 'ZR_WINDOWS_LAYOUT_OK' not in layout.stdout or 'ERROR:' in layout.stdout+layout.stderr:
        raise RuntimeError('PCK layout planning failed')
    plan=json.loads((output/'layout.json').read_text())
    if not plan['layout_valid'] or plan['ui']!=1.0:
        raise RuntimeError('Unsupported native probe layout')
    env=toolchain.isolated_environment(output/'profile','Windows')
    log=(output/'native.log').open('w',encoding='utf-8')
    process=subprocess.Popen([str(player)],cwd=player.parent,env=env,stdout=log,
                             stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    user=ctypes.windll.user32
    user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    user.GetForegroundWindow.restype=w.HWND
    user.SetForegroundWindow.argtypes=[w.HWND]
    user.WindowFromPoint.restype=w.HWND
    user.WindowFromPoint.argtypes=[w.POINT]
    user.ClientToScreen.argtypes=[w.HWND,ctypes.POINTER(w.POINT)]
    user.GetDpiForWindow.argtypes=[w.HWND]
    user.SetWindowPos.argtypes=[w.HWND,w.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,w.UINT]
    user.GetWindowRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
    user.GetClientRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
    user.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
    original=w.POINT()
    user.GetCursorPos(ctypes.byref(original))
    results=[]
    held=set()
    hwnd=None
    binding=dict(source_commit=expected_head,base_commit=report['base_commit'],
                 tested_checkout_commit=report['tested_checkout_commit'],github_run_id=report.get('github_run_id'),
                 export_files=report['export_files'],platform=platform.platform(),
                 stimulus='Win32 OS-injected mouse to unmodified exported EXE; no Viewport injection',
                 observation='isolated schema-1 saves and PrintWindow of owned HWND',
                 layout_only_editor=version,script_sha256=toolchain.sha256_file(script),
                 editor_sha256=toolchain.sha256_file(engine),
                 driver_sha256=toolchain.sha256_file(Path(__file__)),owner_ZR_M01='OPEN',
                 physical_mouse_acceptance='OPEN: owner',results=results)

    def wait(action,timeout=10):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            try:
                value=action()
                if value: return value
            except (OSError,ValueError): pass
            time.sleep(.05)
        raise RuntimeError('Native condition timed out')

    def save():
        paths=list((output/'profile').rglob(plan['save_file']))
        return json.loads(paths[0].read_text(encoding='utf-8')) if len(paths)==1 else None

    def move(local):
        if not user.SetCursorPos(origin.x+round(local[0]),origin.y+round(local[1])):
            raise RuntimeError('Native cursor move failed')
        time.sleep(.12)

    def button(right,down):
        user.mouse_event((8 if down else 16) if right else (2 if down else 4),0,0,0,0)
        held.add(right) if down else held.discard(right)
        time.sleep(.12)

    def click(point):
        move(point)
        button(False,True)
        button(False,False)

    def require(condition,label,state=None):
        results.append(dict(label=label,passed=bool(condition),state=state))
        if not condition: raise RuntimeError(label)

    try:
        if any(user.GetAsyncKeyState(key)&0x8000 for key in (1,2)):
            raise RuntimeError('Mouse already held; native probe did not take input')
        callback_type=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
        owned=[]
        @callback_type
        def visit(handle,_):
            pid=w.DWORD()
            user.GetWindowThreadProcessId(handle,ctypes.byref(pid))
            if pid.value==process.pid and user.IsWindowVisible(handle): owned.append(handle)
            return True
        def find():
            owned.clear()
            user.EnumWindows(visit,0)
            return owned[0] if len(owned)==1 else None
        hwnd=wait(find)
        time.sleep(1)
        outer=w.RECT()
        client=w.RECT()
        user.GetWindowRect(hwnd,ctypes.byref(outer))
        user.GetClientRect(hwnd,ctypes.byref(client))
        width,height=plan['client']
        user.SetWindowPos(hwnd,None,outer.left,outer.top,width+outer.right-outer.left-client.right,
                          height+outer.bottom-outer.top-client.bottom,0x14)
        time.sleep(.5)
        origin=w.POINT(0,0)
        user.ClientToScreen(hwnd,ctypes.byref(origin))
        user.GetClientRect(hwnd,ctypes.byref(client))
        require([client.right,client.bottom]==plan['client'],'actual-client-size')
        binding.update(client=plan['client'],ui=1.0,windows_dpi=user.GetDpiForWindow(hwnd),
                       native_client_origin=[origin.x,origin.y],plan=plan)
        user.MonitorFromWindow.restype=w.HANDLE
        user.MonitorFromWindow.argtypes=[w.HWND,w.DWORD]
        user.GetMonitorInfoW.argtypes=[w.HANDLE,ctypes.POINTER(MonitorInfo)]
        monitor=MonitorInfo()
        monitor.size=ctypes.sizeof(monitor)
        if not user.GetMonitorInfoW(user.MonitorFromWindow(hwnd,2),ctypes.byref(monitor)):
            raise RuntimeError('Native monitor metadata unavailable')
        binding['screen']=[monitor.monitor.right-monitor.monitor.left,monitor.monitor.bottom-monitor.monitor.top]
        game_thread=user.GetWindowThreadProcessId(hwnd,None)
        # Keep only this disposable owned window above desktop applications.
        # Activate through its empty paper; never click a covered foreign HWND.
        user.SetWindowPos(hwnd,w.HWND(-1),0,0,0,0,0x13)
        time.sleep(.1)
        blank=[width-12,height-12]
        q=w.POINT(origin.x+round(blank[0]),origin.y+round(blank[1]))
        require(user.WindowFromPoint(q)==hwnd,'owned-window-uncovered')
        click(blank)
        wait(lambda: user.GetForegroundWindow()==hwnd)
        user.SetForegroundWindow(hwnd)
        binding['foreground_before_card']=user.GetForegroundWindow()
        q=w.POINT(origin.x+round(plan['card'][0]),origin.y+round(plan['card'][1]))
        binding['card_point_window']=user.WindowFromPoint(q)
        binding['owned_hwnd']=hwnd
        click(plan['card'])
        time.sleep(.3)
        capture(user,hwnd,plan['client'],output/'native-board.png')
        # Opening a fresh board need not create a save; only confirmed edits do.
        baseline=dict(cells=[-1]*(plan['dimensions'][0]*plan['dimensions'][1]),cursor=0)
        require(save() is None or set(save()['cells'])=={-1},'fresh-isolated-board')
        count=plan['dimensions'][0]-4
        for right in (False,True):
            for direction in (-1,1):
                start=plan['starts'][0 if direction>0 else 1]
                outside=[-80 if direction<0 else width+80,start[1]]
                move(start)
                button(right,True)
                move(outside)
                require(user.GetForegroundWindow()==hwnd,'outside-focus-retained')
                cursor=CursorInfo()
                cursor.size=ctypes.sizeof(cursor)
                if not user.GetCursorInfo(ctypes.byref(cursor)):
                    raise RuntimeError('Native cursor metadata unavailable')
                require(bool(cursor.flags&1) and cursor.point.x==origin.x+round(outside[0])
                        and cursor.point.y==origin.y+round(outside[1]),'free-visible-outside-cursor',
                        dict(flags=cursor.flags,screen_position=[cursor.point.x,cursor.point.y]))
                capture(user,hwnd,plan['client'],output/f'outside-{int(right)}-{direction}.png')
                require((save() or baseline)['cells']==baseline['cells'],'outside-preview-has-no-commit')
                button(right,False)
                final=wait(lambda: (s if (s:=save()) and s['cursor']==1 else None))
                require(len(final['history'])==1 and final['cells'].count(0 if right else 1)==count,
                        f'outside-release right={right} dir={direction}',final)
                gui=GuiInfo()
                gui.size=ctypes.sizeof(gui)
                if not user.GetGUIThreadInfo(game_thread,ctypes.byref(gui)):
                    raise RuntimeError('Native capture metadata unavailable')
                require(not gui.capture,'outside-release-frees-native-capture')
                move(start)
                time.sleep(.15)
                require(save()==final,'return-after-release-no-phantom')
                click(plan['actions'][0])
                undone=wait(lambda: (s if (s:=save()) and s['cursor']==0 else None))
                require(set(undone['cells'])=={-1},'native-undo-exact')
                click(plan['actions'][1])
                redone=wait(lambda: (s if (s:=save()) and s['cursor']==1 else None))
                require(redone['cells']==final['cells'],'native-redo-exact')
                click(plan['actions'][0])
                baseline=wait(lambda: (s if (s:=save()) and s['cursor']==0 else None))
            start=plan['starts'][0]
            move(start)
            button(right,True)
            move([width+80,start[1]])
            move(start)
            move(plan['starts'][2])
            button(right,False)
            final=wait(lambda: (s if (s:=save()) and s['cursor']==1 else None))
            require(final['cells'].count(0 if right else 1)==5,'return-held-reorients',final)
            click(plan['actions'][0])
            baseline=wait(lambda: (s if (s:=save()) and s['cursor']==0 else None))
        user.CreateWindowExW.restype=w.HWND
        target=user.CreateWindowExW(0,'STATIC','ZR focus target',0x10CF0000,
                                    origin.x+40,origin.y+40,200,100,None,None,None,None)
        if not target: raise RuntimeError('Cannot create owned focus target')
        try:
            for right in (False,True):
                user.SetForegroundWindow(hwnd)
                click(blank)
                move(plan['starts'][0])
                button(right,True)
                move([width+80,plan['starts'][0][1]])
                user.SetForegroundWindow(target)
                wait(lambda: user.GetForegroundWindow()==target)
                time.sleep(.2)
                button(right,False)
                require(save()['cells']==baseline['cells'] and save()['cursor']==0,'focus-loss-no-commit')
                user.SetForegroundWindow(hwnd)
                click(blank)
                move(plan['starts'][0])
                time.sleep(.2)
                require(save()['cells']==baseline['cells'],'focus-return-no-phantom')
                capture(user,hwnd,plan['client'],output/f'focus-return-{int(right)}.png')
                button(right,True)
                button(right,False)
                fresh=wait(lambda: (s if (s:=save()) and s['cursor']==1 else None))
                require(fresh['cells'].count(0 if right else 1)==1,'fresh-down-after-focus',fresh)
                click(plan['actions'][0])
                baseline=wait(lambda: (s if (s:=save()) and s['cursor']==0 else None))
        finally:
            user.DestroyWindow(target)
        binding['status']='success'
        user.PostMessageW(hwnd,0x10,0,0)
        process.wait(timeout=10)
        require(process.returncode==0,'native-player-exit')
    except Exception as exc:
        binding.update(status='failure',error=str(exc))
        raise
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        for right in held: user.mouse_event(16 if right else 4,0,0,0,0)
        user.SetCursorPos(original.x,original.y)
        log.close()
        binding['images']={p.name:toolchain.sha256_file(p) for p in output.glob('*.png')}
        (output/'zr-windows-report.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('player','engine','output-dir'): parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--head',required=True)
    args=parser.parse_args()
    probe(args.player.resolve(),args.engine.resolve(),args.output_dir.resolve(),args.head)
