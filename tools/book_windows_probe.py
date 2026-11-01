"""B-A-N05-F01: bounded real Win32 input in the hash-bound exported study.

An external read-only autoload observes the pack's configured main scene and records
state. No Viewport injection, model calls or real save directories. A separate
ordinary-start run can reuse the recorded OS plan without this observer.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

import p1_preflight as tc

ROOT = Path(__file__).resolve().parents[1]
OBSERVER = ROOT / 'game/study/book/windows_observer.gd'


def probe(source: Path, output: Path, expected_head: str) -> dict:
    if platform.system() != 'Windows':
        raise RuntimeError('Real Windows desktop required')
    report = json.loads((source / 'report.json').read_text(encoding='utf-8'))
    if report['source_commit'] != expected_head or report['source_tree_dirty']:
        raise ValueError('Expected clean commit-bound export')
    checkout = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty = subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()
    if checkout != expected_head or dirty:
        raise ValueError('Observer and driver require the same clean checkout as the export')
    player = source / 'windows/book-study.exe'
    for name in ('book-study.exe', 'book-study.pck'):
        tc.verify_sha256(source / 'windows' / name, report['files']['windows/' + name]['sha256'])
    output.mkdir(parents=True, exist_ok=False)
    # Export templates ignore --script. Their documented override.cfg mechanism
    # adds only an observer to a private copy of the unchanged EXE and PCK.
    player_dir = output / 'player'
    player_dir.mkdir()
    for name in ('book-study.exe', 'book-study.pck'):
        shutil.copyfile(source / 'windows' / name, player_dir / name)
        tc.verify_sha256(player_dir / name, report['files']['windows/' + name]['sha256'])
    shutil.copyfile(OBSERVER, player_dir / 'observer.gd')
    override = player_dir / 'override.cfg'
    override.write_text('[autoload]\nF01Observer="*'+(player_dir/'observer.gd').as_posix()+'"\n', encoding='utf-8')
    player = player_dir / 'book-study.exe'
    user = ctypes.windll.user32
    user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    for name, args in (
        ('GetWindowThreadProcessId', [w.HWND, ctypes.POINTER(w.DWORD)]),
        ('GetClientRect', [w.HWND, ctypes.POINTER(w.RECT)]),
        ('ClientToScreen', [w.HWND, ctypes.POINTER(w.POINT)]),
        ('SetForegroundWindow', [w.HWND]), ('ShowWindow', [w.HWND, ctypes.c_int]),
        ('GetWindowRect', [w.HWND, ctypes.POINTER(w.RECT)]),
        ('SetWindowPos', [w.HWND, w.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, w.UINT]),
        ('PostMessageW', [w.HWND, w.UINT, w.WPARAM, w.LPARAM]),
    ):
        getattr(user, name).argtypes = args
    user.GetForegroundWindow.restype = w.HWND
    if any(user.GetAsyncKeyState(k) & 0x8000 for k in (1, 2)):
        raise RuntimeError('Physical mouse button held; no input taken')
    original = w.POINT()
    user.GetCursorPos(ctypes.byref(original))
    env = tc.isolated_environment(output / 'profile', 'Windows')
    env['BOOK_WINDOWS_OBSERVATION'] = str(output)
    stdout = (output / 'stdout.log').open('w', encoding='utf-8')
    stderr = (output / 'stderr.log').open('w', encoding='utf-8')
    trace = (output / 'os.jsonl').open('w', encoding='utf-8')
    started = time.monotonic()
    results = []
    process = subprocess.Popen([str(player), '--audio-driver', 'Dummy'],
                               cwd=player.parent, env=env, stdout=stdout, stderr=stderr,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    hwnd = None
    held = set()
    binding = dict(package='B-A-N05-F01-T01', source_commit=expected_head,
                   base_commit=report['base_commit'], tested_checkout_commit=report['tested_checkout_commit'],
                   export_files={n: report['files']['windows/'+n] for n in ('book-study.exe','book-study.pck')},
                   observer_sha256=tc.sha256_file(OBSERVER), driver_sha256=tc.sha256_file(Path(__file__)),
                   override_sha256=tc.sha256_file(override),
                   platform=platform.platform(), stimulus='Win32 OS mouse; no Viewport injection',
                   observation='External read-only observer in actual exported EXE/PCK, owned client captures',
                   owner_acceptance='OPEN', results=results)

    def record(event, **detail):
        trace.write(json.dumps(dict(seconds=time.monotonic()-started, utc=time.time(), event=event, **detail))+'\n')
        trace.flush()
        os.fsync(trace.fileno())

    def state():
        # The observer can be in the middle of its bounded snapshot write.
        for _ in range(20):
            try:
                return json.loads((output / 'state.json').read_text(encoding='utf-8'))
            except (OSError, ValueError):
                time.sleep(.01)
        raise OSError('No complete observation snapshot within 200 ms')

    def wait(condition, timeout=8):
        deadline = time.monotonic()+timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Player exited: {process.returncode:#x}')
            if time.monotonic()-started > 180:
                raise TimeoutError('Windows probe exceeded 180 seconds')
            try:
                value = condition()
                if value:
                    return value
            except (OSError, ValueError, KeyError):
                pass
            time.sleep(.025)
        raise TimeoutError('Windows observation did not reach expected state')

    def require(ok, label, detail=None):
        results.append(dict(label=label, passed=bool(ok), detail=detail))
        record('assertion', **results[-1])
        if not ok:
            raise AssertionError(label)

    def foreground():
        if user.GetForegroundWindow() != hwnd:
            record('unexpected-focus-loss')
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            raise RuntimeError('Own player lost foreground; stopped sending input')

    def activate():
        thread = user.GetWindowThreadProcessId(user.GetForegroundWindow(), None)
        own = ctypes.windll.kernel32.GetCurrentThreadId()
        attached = user.AttachThreadInput(own, thread, True)
        try:
            user.SetForegroundWindow(hwnd)
        finally:
            if attached:
                user.AttachThreadInput(own, thread, False)
        wait(lambda: user.GetForegroundWindow() == hwnd)

    def geometry():
        r, origin = w.RECT(), w.POINT()
        user.GetClientRect(hwnd, ctypes.byref(r))
        user.ClientToScreen(hwnd, ctypes.byref(origin))
        return origin, (r.right, r.bottom)

    def move(point, seconds=.12):
        foreground()
        origin, _ = geometry()
        record('move', point=point)
        if not user.SetCursorPos(origin.x+round(point[0]), origin.y+round(point[1])):
            raise RuntimeError('OS pointer move failed')
        time.sleep(seconds)

    def button(down, right=False):
        foreground()
        record('button', down=down, right=right)
        user.mouse_event((8 if down else 16) if right else (2 if down else 4), 0, 0, 0, 0)
        held.add(right) if down else held.discard(right)
        time.sleep(.12)

    def center(rect):
        return [rect[0]+rect[2]/2, rect[1]+rect[3]/2]

    def click(point):
        move(point)
        button(True)
        button(False)

    def cell_point(x=5, y=5):
        s = state()
        return [s['grid'][0]+(x+.5)*s['cell_size'], s['grid'][1]+(y+.5)*s['cell_size']]

    def tooltip(label, key='help'):
        move(center(state()['tips'][key]['rect']), .72)
        s = wait(lambda: state() if state()['tips'][key]['visible'] else None)
        require(not s['gesture'] and not s['blocked'] and not s['clue'] and not s['barrier']
                and s['held'] == 0 and s['buttons'] == 0, label, dict(cursor=s['cursor'], tip=key))
        tip = s['tips'][key]
        require(bool(tip['caption'].strip()) and tip['text'] == tip['caption'], label+' correct text')
        return s

    def capture(name):
        from PIL import ImageGrab
        foreground()
        origin, size = geometry()
        ImageGrab.grab((origin.x, origin.y, origin.x+size[0], origin.y+size[1])).save(output/(name+'.png'))
        record('capture', file=name+'.png', client=size, origin=[origin.x, origin.y])

    try:
        owned = []
        @ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
        def visit(handle, _):
            pid = w.DWORD()
            user.GetWindowThreadProcessId(handle, ctypes.byref(pid))
            if pid.value == process.pid and user.IsWindowVisible(handle):
                owned.append(handle)
            return True
        def find():
            owned.clear()
            user.EnumWindows(visit, 0)
            return owned[0] if owned else None
        hwnd = wait(find)
        wait(lambda: state().get('card'))
        hwnd = wait(find)
        record('window-ready', pid=process.pid, hwnd=hwnd)
        user.ShowWindow(hwnd, 3)
        activate()
        time.sleep(.5)
        click(center(state()['card']))
        wait(lambda: state()['state'] == 3 and not state()['barrier'])
        initial = state()
        require(initial['selected'] == 'T-06', 'real catalog click opens T-06')
        baseline_cursor = initial['cursor']
        for i in range(32):
            move(cell_point())
            wait(lambda: state()['board_hover'] == [5,5])
            if i in (8,16,24):
                before = state()
                button(True)
                wait(lambda: state()['gesture'])
                button(False)
                after = wait(lambda: state() if state()['cursor'] == before['cursor']+1 else None)
                changed = [j for j,(a,b) in enumerate(zip(before['cells'],after['cells'])) if a != b]
                require(changed == [255], f'commit {i} changes one intended cell', changed)
            key = ('help','menu','nav-information')[i % 3]
            if i % 4 == 0:
                move(center(state()['tips'][key]['rect']), .08)
                require(not state()['tips'][key]['visible'], f'fast transition {i} respects delay')
                move(cell_point())
            s = tooltip(f'transition {i} tooltip after idle/commit', key)
            if i in (0,8,31):
                capture('tooltip-'+str(i))
            # Cross the visible popup: this reproduces the baseline's crash path.
            if i % 2 == 0:
                move(center(s['tips'][key]['popup']), .03)
            move(cell_point())
            wait(lambda: state()['board_hover'] == [5,5])
            require(not state()['tips'][key]['visible'], f'transition {i} crosshair returns')
        require(state()['cursor'] == baseline_cursor+3, '32 round trips add only three intended transactions')
        capture('crosshair')
        committed = state()
        click(center(committed['tips']['undo']['rect']))
        wait(lambda: state()['cursor'] == committed['cursor']-1)
        click(center(state()['tips']['redo']['rect']))
        wait(lambda: state()['cursor'] == committed['cursor'])
        require(state()['cells'] == committed['cells'] and state()['history'] == committed['history'], 'OS Undo/Redo exact state')
        for key, eraser in (('erase',True),('fill',False)):
            click(center(state()['tips'][key]['rect']))
            wait(lambda: state()['tool'][0] == eraser)
        click(center(state()['tips']['color-2']['rect']))
        wait(lambda: state()['tool'] == [False,2])
        require(state()['cells'] == committed['cells'], 'tool/color selection preserves cells')
        # Real focus loss while held, then the matching Up after focus return.
        move(cell_point(7,7))
        button(True)
        wait(lambda: state()['gesture'])
        user.ShowWindow(hwnd, 6)
        time.sleep(.2)
        wait(lambda: not state()['gesture'])
        user.ShowWindow(hwnd, 9)
        activate()
        button(False)
        wait(lambda: state()['buttons'] == 0)
        require(state()['cells'] == committed['cells'], 'OS focus loss cancels held gesture')
        tooltip('tooltip after focus loss')
        # Restore a bounded window for a real release outside its client area.
        user.ShowWindow(hwnd, 9)
        wait(lambda: state()['mode'] == 0)
        outer = w.RECT()
        user.GetWindowRect(hwnd, ctypes.byref(outer))
        _, size = geometry()
        user.SetWindowPos(hwnd, None, 100, 100, 1600+outer.right-outer.left-size[0],
                          900+outer.bottom-outer.top-size[1], 0x14)
        wait(lambda: state()['size'] == [1600,900])
        move(cell_point(7,7))
        button(True)
        wait(lambda: state()['gesture'])
        user.SetWindowPos(hwnd, None, 100, 100, 1610+outer.right-outer.left-size[0],
                          850+outer.bottom-outer.top-size[1], 0x14)
        wait(lambda: state()['size'] == [1610,850])
        wait(lambda: not state()['gesture'])
        button(False)
        require(state()['cells'] == committed['cells'], 'OS resize cancels held gesture')
        tooltip('tooltip after resize')
        move(cell_point(7,7))
        button(True)
        wait(lambda: state()['gesture'])
        move([state()['size'][0]+20,cell_point(7,7)[1]])
        button(False)
        wait(lambda: state()['cursor'] == committed['cursor']+1)
        require(state()['state'] == 3 and not state()['gesture'], 'real outside-client release commits without navigation')
        tooltip('tooltip after outside-client release')
        capture('outside-release-tooltip')
        binding['round_trips'] = 32
        saved = wait(lambda: state() if state()['memory'].get('cursor') == state()['cursor'] else None)
        require(all(saved['memory'][k] == saved[k] for k in ('cells','history','cursor')), 'RAM snapshot preserves exact player state')
        profile_files = [p.relative_to(output/'profile') for p in (output/'profile').rglob('*') if p.is_file()]
        require(all('logs' in p.parts or 'shader_cache' in p.parts for p in profile_files), 'no save or preference files in isolated profile')
        binding['final_state'] = saved
        binding['passed'] = True
    except Exception as exc:
        binding['passed'] = False
        binding['failure'] = str(exc)
        raise
    finally:
        for right in held:
            user.mouse_event(16 if right else 4,0,0,0,0)
        if process.poll() is None and hwnd:
            user.PostMessageW(hwnd,0x10,0,0)
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            binding['forced_cleanup'] = True
            binding['passed'] = False
        binding['exit_code'] = process.returncode
        binding['seconds'] = time.monotonic()-started
        record('exit', code=process.returncode)
        user.SetCursorPos(original.x,original.y)
        stdout.close()
        stderr.close()
        trace.close()
        output_text = (output/'stdout.log').read_text(encoding='utf-8')+(output/'stderr.log').read_text(encoding='utf-8')
        binding['passed'] = bool(binding.get('passed')) and process.returncode == 0 and 'ERROR:' not in output_text
        binding['profile_files'] = [p.relative_to(output/'profile').as_posix() for p in (output/'profile').rglob('*') if p.is_file()]
        binding['files'] = {p.relative_to(output).as_posix():dict(bytes=p.stat().st_size,sha256=tc.sha256_file(p))
                            for p in output.rglob('*') if p.is_file() and 'profile' not in p.relative_to(output).parts}
        (output/'binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not binding['passed']:
        raise RuntimeError('Non-clean native player output')
    return binding


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--head', required=True)
    args = parser.parse_args()
    result = probe(args.source.resolve(), args.output.resolve(), args.head)
    print(json.dumps({k:result[k] for k in ('passed','exit_code','seconds','round_trips')}))
