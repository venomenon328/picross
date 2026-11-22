"""Check the normal PG window using an MSI-inspected image on an isolated Windows runner."""
import argparse
from contextlib import ExitStack, contextmanager
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
import time
import unicodedata

from tools.app_products import PG
from tools.game_app.diagnose import close, windows
from tools.game_app.inspect import binding
from tools.production_workspace.payload import canonical
from tools.production_workspace.update_storage import no_links
from tools.production_workspace.update_windows import local_appdata
from tools.production_workspace.verify_installer import require

FORMAT = 'picross-pg-launcher-smoke-v1'
ROOT = Path(__file__).resolve().parents[2]
VERSION_GLYPHS = str.maketrans('oilzsb', '011258')


class EarlyExit(RuntimeError):
    pass


class Accounting(ctypes.Structure):
    _fields_ = [(name, ctypes.c_longlong) for name in ('user', 'kernel', 'period_user', 'period_kernel')] + [
        (name, wintypes.DWORD) for name in ('faults', 'total', 'active', 'terminated')
    ]


@contextmanager
def isolated_process(argv, cwd, env):
    # Assign before the executable runs so even a short-lived descendant is counted.
    import _winapi

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    signatures = [
        ('CreateJobObjectW', [ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
        ('AssignProcessToJobObject', [wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        ('QueryInformationJobObject', [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                       wintypes.DWORD, ctypes.c_void_p], wintypes.BOOL),
        ('TerminateJobObject', [wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        ('ResumeThread', [wintypes.HANDLE], wintypes.DWORD),
    ]
    for name, arguments, result in signatures:
        api = getattr(kernel, name)
        api.argtypes = arguments
        api.restype = result
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())

    def accounting():
        info = Accounting()
        if not kernel.QueryInformationJobObject(job, 1, ctypes.byref(info), ctypes.sizeof(info), None):
            raise ctypes.WinError(ctypes.get_last_error())
        return info

    try:
        proc, thread, pid, _ = _winapi.CreateProcess(
            argv[0], subprocess.list2cmdline(argv), None, None, False, 0x4, env, str(cwd),
            subprocess.STARTUPINFO(),  # CREATE_SUSPENDED
        )
        assigned = False
        try:
            assigned = kernel.AssignProcessToJobObject(job, proc)
            if not assigned or kernel.ResumeThread(thread) == 0xffffffff:
                raise ctypes.WinError(ctypes.get_last_error())

            def exit_code(timeout_ms=0):
                if _winapi.WaitForSingleObject(proc, timeout_ms) == _winapi.WAIT_TIMEOUT:
                    return None
                return _winapi.GetExitCodeProcess(proc)

            yield pid, exit_code, lambda: accounting().total
        finally:
            try:
                # Also clean up descendants on a failing smoke. The job contains only our launch.
                if assigned:
                    if accounting().active and not kernel.TerminateJobObject(job, 1):
                        raise ctypes.WinError(ctypes.get_last_error())
                    until = time.monotonic() + 15
                    while accounting().active:
                        if time.monotonic() >= until:
                            raise RuntimeError('PG diagnostic job did not stop')
                        time.sleep(0.05)
                else:
                    _winapi.TerminateProcess(proc, 1)
                if _winapi.WaitForSingleObject(proc, 15000) == _winapi.WAIT_TIMEOUT:
                    raise RuntimeError('PG diagnostic process did not terminate')
            finally:
                _winapi.CloseHandle(thread)
                _winapi.CloseHandle(proc)
    finally:
        _winapi.CloseHandle(job)


def responsive(handle):
    send = ctypes.WinDLL('user32', use_last_error=True).SendMessageTimeoutW
    send.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
                     wintypes.UINT, wintypes.UINT, ctypes.c_void_p]
    send.restype = wintypes.LPARAM
    return bool(send(handle, 0, 0, 0, 2, 1000, None))  # WM_NULL, SMTO_ABORTIFHUNG


def read_window(handle, snapshot):
    from PIL import ImageGrab

    with ImageGrab.grab(window=handle) as image:
        with image.resize((image.width * 2, image.height * 2)) as enlarged:
            enlarged.save(snapshot)
    powershell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    outcome = subprocess.run(
        [str(powershell), '-NoProfile', '-NonInteractive', '-File',
         str(Path(__file__).with_name('launcher_ocr.ps1')), str(snapshot)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=snapshot.parent,
        encoding='utf-8', errors='replace', timeout=12,
    )
    require(outcome.returncode == 0, f'Launcher OCR failed: {outcome.stdout.strip()[:512]!a}')
    return outcome.stdout.strip()


def launcher_controls(text, version):
    # The English recognizer is available on hosted Windows. Accept its accent
    # simplifications while requiring the actual German control labels.
    folded = unicodedata.normalize('NFKD', text.casefold())
    folded = ''.join(char for char in folded if not unicodedata.combining(char))
    # Restrict digit substitutions to a complete Version value.
    versions = re.findall(
        r'\bversion\s+([0-9oilzsb]+(?:\s*\.\s*[0-9oilzsb]+){2})(?![\w.+-]|\s+\.)',
        text.lower(),
    )
    words = ' ' + ' '.join(re.findall(r'\w+', folded)) + ' '
    return any(re.sub(r'\s+', '', value).translate(VERSION_GLYPHS) == version for value in versions) and all(
        ' ' + label + ' ' in words for label in
        ('automatische update suche', 'nicht verfugbar', 'suche aktivieren', 'spielen')
    )


def observe(pid, exit_code, count, version, snapshot, log):
    until = time.monotonic() + 45
    observations = set()
    ocr_reads = 0
    try:
        while time.monotonic() < until:
            code = exit_code()
            if code is not None:
                raise EarlyExit(f'Process exited before launcher window (exit {code})')
            if count() != 1:
                raise RuntimeError('Launcher spawned a process before game choice')
            for handle, title, kind in windows(pid):
                observed = (title, kind)
                if observed not in observations and len(observations) < 8:
                    log(f'Visible PID window: title={title[:128]!a}, class={kind[:128]!a}')
                    observations.add(observed)
                if title != 'Picross' or kind != 'TkTopLevel' or not responsive(handle):
                    continue
                text = read_window(handle, snapshot)
                ocr_reads += 1
                if ocr_reads <= 8:
                    log(f'PID window OCR: {text[:512]!a}')
                if launcher_controls(text, version):
                    return handle, text
            time.sleep(0.25)
        raise TimeoutError('Timed out waiting for the normal responsive PG launcher controls')
    except Exception:
        if not observations:
            log(f'No visible titled window observed for PID={pid}.')
        else:
            log(f'PID={pid} produced {ocr_reads} OCR reads from responsive launcher windows.')
        raise


def inventory(image, commit):
    raw = (image / 'inventory.json').read_bytes()
    report = json.loads(raw)
    expected = {row['file']: {key: row[key] for key in ('bytes', 'sha256')} for row in report['files']}
    expected['inventory.json'] = binding(image / 'inventory.json')
    actual = {path.relative_to(image).as_posix(): binding(no_links(path))
              for path in image.rglob('*') if path.is_file()}
    require(report['commit'] == commit and len(expected) == len(report['files']) + 1 and actual == expected,
            'Launcher smoke image differs from the MSI-inspected inventory')
    return actual


def verify_result(result, delivery, inspection, commit):
    require(inspection['compared_to_build'] is True and
            result['commit'] == delivery['commit'] == inspection['commit'] == commit and
            result['msi_sha256'] == delivery['msi_sha256'] == inspection['msi_sha256'] and
            result['version'] == delivery['version'] == inspection['version'] and
            result['payload_fingerprint'] == delivery['payload_fingerprint'] == inspection['payload_fingerprint'] and
            result['launcher_sha256'] == delivery['exe_sha256'] and
            result['format'] == FORMAT and result['exit_code'] == 0 and result['processes'] == 1 and
            result['window_class'] == 'TkTopLevel' and launcher_controls(result['window_text'], result['version']) and
            result['inventory_files'] == inspection['inventory_files'] + 1,
            'Missing or unbound successful normal PG launcher start')


def smoke(build, inspection_path, output, commit, *, negative_control=False):
    require(os.name == 'nt' and not output.is_relative_to(ROOT), 'Windows output outside checkout required')
    output.mkdir(parents=True, exist_ok=False)
    # Keep the last PID-window capture available if the smoke fails.
    snapshot = output / 'window.png'

    with (output / 'process.log').open('x', encoding='utf-8') as stream:
        start = time.monotonic()

        def log(message):
            line = f'{time.monotonic() - start:.3f}s {message}'
            print(line, file=stream, flush=True)
            print(line, flush=True)

        log(f'Checking MSI-inspected PG launcher for source {commit}.')
        delivery = json.loads((build / 'delivery.json').read_bytes())
        inspection = json.loads(inspection_path.read_bytes())
        require(inspection['compared_to_build'] is True and
                inspection['commit'] == delivery['commit'] == commit and
                binding(build / delivery['msi_file']) ==
                {'bytes': inspection['msi_bytes'], 'sha256': inspection['msi_sha256']},
                'A matching --compare-build MSI inspection is required')
        source = build / 'dist' / PG.executable
        source_files = inventory(source, commit)
        launcher_name = PG.executable + '.exe'
        require(source_files[launcher_name]['sha256'] == delivery['exe_sha256'] and
                len(source_files) == inspection['inventory_files'] + 1, 'Unbound launcher executable or inventory')
        version = delivery['version']

        with ExitStack() as cleanup:
            work = Path(cleanup.enter_context(TemporaryDirectory(prefix='isolated-', dir=output)))
            local = no_links(local_appdata())
            programs = no_links(local / 'Programs')
            try:
                programs.mkdir()
            except FileExistsError:
                require(programs.is_dir(), 'Windows Programs path is not a directory')
            else:
                cleanup.callback(programs.rmdir)
            image = no_links(programs / PG.install_directory)
            state = no_links(local / PG.state_directory)
            for directory in (image, state):
                directory.mkdir()  # Atomic ownership. Never reuse an existing installation/profile.
                cleanup.callback(lambda path=directory: shutil.rmtree(no_links(path)))

            shutil.copytree(source, image, dirs_exist_ok=True)
            require(inventory(image, commit) == source_files, 'Copied launcher image differs from the original')
            env = {key: value for key, value in os.environ.items()
                   if not key.upper().startswith('PYTHON') and key.upper() not in
                   {'GH_TOKEN', 'GITHUB_TOKEN', 'TCL_LIBRARY', 'TK_LIBRARY', 'TCLLIBPATH'}}
            system = Path(os.environ['SystemRoot'])
            env.update(APPDATA=str(work / 'appdata'), TEMP=str(work), TMP=str(work),
                       PATH=os.pathsep.join((str(system / 'System32'), str(system))))
            with isolated_process([str(image / launcher_name)], work, env) as (pid, exit_code, count):
                log(f'Started installed-path frozen launcher without arguments. PID={pid}.')
                handle, window_text = observe(pid, exit_code, count, version, snapshot, log)
                log('Responsive normal launcher controls recognized.')
                close(handle)
                code = exit_code(15000)
                processes = count()
                log(f'WM_CLOSE: exit={code!r}; total job processes={processes}.')
                require(code == 0 and processes == 1, 'Launcher failed normal close or spawned a process')

            require(inventory(image, commit) == source_files, 'Launcher changed the inspected image')
            if negative_control:
                with isolated_process([str(system / 'System32/cmd.exe'), '/d', '/c', 'exit', '23'],
                                      work, env) as (pid, exit_code, count):
                    try:
                        observe(pid, exit_code, count, version, snapshot, log)
                    except EarlyExit as error:
                        require(exit_code() == 23, 'Negative control returned the wrong process result')
                        log(f'Negative control rejected: {error}')
                        (output / 'negative-control.json').write_bytes(canonical({
                            'commit': commit, 'expected_exit': 23, 'exit_code': 23,
                            'rejected': True, 'reason': str(error),
                        }))
                    else:
                        raise RuntimeError('Early-exit control was accepted')

        result = {
            'format': FORMAT, 'commit': commit, 'version': version, 'msi_sha256': inspection['msi_sha256'],
            'payload_fingerprint': delivery['payload_fingerprint'], 'launcher_sha256': delivery['exe_sha256'],
            'inventory_sha256': source_files['inventory.json']['sha256'], 'inventory_files': len(source_files),
            'window_class': 'TkTopLevel', 'window_text': window_text, 'exit_code': code, 'processes': processes,
            'duration_seconds': round(time.monotonic() - start, 3),
        }
        verify_result(result, delivery, inspection, commit)
        (output / 'result.json').write_bytes(canonical(result))
        snapshot.unlink(missing_ok=True)
        print(json.dumps(result, ensure_ascii=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--inspection', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--negative-control', action='store_true')
    parser.add_argument('--verify-result', action='store_true')
    args = parser.parse_args()
    if args.verify_result:
        result = json.loads((args.output / 'result.json').read_bytes())
        verify_result(result, json.loads((args.build / 'delivery.json').read_bytes()),
                      json.loads(args.inspection.read_bytes()), args.expected_commit)
        inventory_file = args.build / 'dist' / PG.executable / 'inventory.json'
        require(result['inventory_sha256'] == binding(inventory_file)['sha256'],
                'Launcher start result refers to a different image inventory')
    else:
        smoke(args.build.resolve(), args.inspection.resolve(), args.output.resolve(),
              args.expected_commit, negative_control=args.negative_control)


if __name__ == '__main__':
    main()
