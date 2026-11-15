"""Observe native publication failure without replacing any production function."""
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import runpy
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parent / 'repo'
RUN = Path(os.environ.get('PICROSS_RENAME_DIAGNOSTIC_ROOT', str(HERE))).resolve()
assert RUN.is_relative_to(REPO.parents[1].resolve())
sys.path.insert(0, str(REPO))
K = ctypes.WinDLL('kernel32', use_last_error=True)
K.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p,
                         w.DWORD, w.DWORD, w.HANDLE]
K.CreateFileW.restype = w.HANDLE
K.CloseHandle.argtypes = [w.HANDLE]
K.CloseHandle.restype = w.BOOL
K.GetFileAttributesW.argtypes = [w.LPCWSTR]
K.GetFileAttributesW.restype = w.DWORD
INVALID = ctypes.c_void_p(-1).value
events = []


class HandleEntry(ctypes.Structure):
    _fields_ = [('handle', w.HANDLE), ('handle_count', ctypes.c_size_t),
                ('pointer_count', ctypes.c_size_t), ('access', w.ULONG),
                ('type_index', w.ULONG), ('attributes', w.ULONG), ('reserved', w.ULONG)]


def disk_handles(pid, selected_root):
    """Read handle names only; retain only this diagnostic subtree's paths."""
    K.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    K.OpenProcess.restype = w.HANDLE
    K.GetCurrentProcess.restype = w.HANDLE
    K.DuplicateHandle.argtypes = [w.HANDLE, w.HANDLE, w.HANDLE, ctypes.POINTER(w.HANDLE),
                                 w.DWORD, w.BOOL, w.DWORD]
    K.GetFileType.argtypes = [w.HANDLE]
    K.GetFinalPathNameByHandleW.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD]
    process = K.OpenProcess(0x440, False, pid)
    if not process:
        return {'pid': pid, 'open_error': ctypes.get_last_error()}
    try:
        nt = ctypes.WinDLL('ntdll')
        query = nt.NtQueryInformationProcess
        query.argtypes = [w.HANDLE, w.ULONG, ctypes.c_void_p, w.ULONG, ctypes.POINTER(w.ULONG)]
        query.restype = ctypes.c_long
        buffer = ctypes.create_string_buffer(4 * 1024 * 1024)
        used = w.ULONG()
        status = query(process, 51, buffer, len(buffer), ctypes.byref(used))
        if status < 0:
            return {'pid': pid, 'status': hex(status & 0xffffffff)}
        count = ctypes.c_size_t.from_buffer(buffer).value
        offset = 2 * ctypes.sizeof(ctypes.c_size_t)
        assert offset + count * ctypes.sizeof(HandleEntry) <= len(buffer)
        matches = []
        for index in range(count):
            entry = HandleEntry.from_buffer(buffer, offset + index * ctypes.sizeof(HandleEntry))
            duplicate = w.HANDLE()
            if not K.DuplicateHandle(process, entry.handle, K.GetCurrentProcess(),
                                     ctypes.byref(duplicate), 0, False, 2):
                continue
            try:
                if K.GetFileType(duplicate) != 1:
                    continue
                path = ctypes.create_unicode_buffer(32768)
                length = K.GetFinalPathNameByHandleW(duplicate, path, len(path), 0)
                if not 0 < length < len(path):
                    continue
                name = path.value.removeprefix('\\\\?\\')
                if name.casefold().startswith(str(selected_root).casefold() + '\\'):
                    matches.append({'handle': int(entry.handle), 'path': name,
                                    'access': hex(entry.access)})
            finally:
                K.CloseHandle(duplicate)
        return {'pid': pid, 'total_handles': count, 'selected_handles': matches}
    finally:
        K.CloseHandle(process)


def access_probe(path):
    row = {'path': str(path), 'attributes': K.GetFileAttributesW(str(path))}
    # Requesting DELETE access does not delete anything. Rename needs this access.
    for name, desired in [('metadata', 0), ('rename_access', 0x10000)]:
        ctypes.set_last_error(0)
        handle = K.CreateFileW(str(path), desired, 7, None, 3, 0x02000000, None)
        row[name] = 0 if handle != INVALID else ctypes.get_last_error()
        if handle != INVALID:
            K.CloseHandle(handle)
    return row


class UniqueProcess(ctypes.Structure):
    _fields_ = [('pid', w.DWORD), ('start', w.FILETIME)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [('process', UniqueProcess), ('name', w.WCHAR * 256),
                ('service', w.WCHAR * 64), ('kind', ctypes.c_int),
                ('status', w.ULONG), ('session', w.DWORD), ('restartable', w.BOOL)]


def users_of(files):
    rm = ctypes.WinDLL('rstrtmgr', use_last_error=True)
    session = w.DWORD()
    key = ctypes.create_unicode_buffer(33)
    code = rm.RmStartSession(ctypes.byref(session), 0, key)
    result = {'start': code}
    if code:
        return result
    try:
        paths = (w.LPCWSTR * len(files))(*map(str, files))
        code = rm.RmRegisterResources(session, len(files), paths, 0, None, 0, None)
        result['register'] = code
        if code:
            return result
        needed, count, reason = w.UINT(), w.UINT(), w.DWORD()
        code = rm.RmGetList(session, ctypes.byref(needed), ctypes.byref(count),
                            None, ctypes.byref(reason))
        if code == 234:
            count.value = needed.value
            rows = (ProcessInfo * count.value)()
            code = rm.RmGetList(session, ctypes.byref(needed), ctypes.byref(count),
                                rows, ctypes.byref(reason))
            result['processes'] = [{'pid': p.process.pid, 'name': p.name,
                                    'service': p.service, 'status': p.status}
                                   for p in rows[:count.value]] if not code else []
        else:
            result['processes'] = []
        result.update(list_code=code, reboot_reason=reason.value)
        return result
    finally:
        result['end'] = rm.RmEndSession(session)


def capture(stage, target, when, error=None):
    try:
        stage, target = Path(stage), Path(target)
        paths = [stage, *stage.rglob('*')]
        row = {'when': when, 'pid': os.getpid(), 'cwd': os.getcwd(),
               'stage': str(stage), 'target': str(target),
               'target_exists': target.exists(), 'time': time.time(),
               'access': [access_probe(p) for p in paths],
               'target_parent_access': access_probe(target.parent)}
        if error is not None:
            row['error'] = repr(error)
        row['restart_manager'] = users_of([p for p in paths if p.is_file()])
        files = [p for p in paths if p.is_file()]
        groups = {p.relative_to(stage).parts[0] for p in files}
        row['resource_groups'] = {g: users_of([p for p in files if p.relative_to(stage).parts[0] == g])
                                  for g in sorted(groups)}
        pids = {os.getpid(), *[p['pid'] for p in row['restart_manager'].get('processes', [])]}
        row['handles'] = [disk_handles(pid, stage.parent) for pid in sorted(pids)]
        events.append(row)
    except Exception as exc:
        events.append({'when': when, 'observation_error': repr(exc)})
    (RUN / 'native-observations.json').write_text(
        json.dumps(events, indent=2), encoding='utf-8')


def local_trace(frame, event, arg):
    if event == 'exception' and isinstance(arg[1], OSError):
        capture(frame.f_locals['stage'], frame.f_locals['target'],
                'rename_exception', arg[1])
    return local_trace


def trace(frame, event, arg):
    if (event == 'call' and frame.f_code.co_name == 'publish_directory'
            and frame.f_code.co_filename.endswith('background_io.py')):
        capture(frame.f_locals['stage'], frame.f_locals['target'], 'before_rename')
        if os.environ.get('PICROSS_RENAME_WAIT_FOR_RELEASE') == '1':
            package = Path(frame.f_locals['stage']) / 'input/package.zip'
            start = time.monotonic()
            checks = []
            while time.monotonic() - start < 5:
                users = users_of([package])
                checks.append({'seconds': time.monotonic() - start, 'users': users})
                if not users.get('processes'):
                    break
                time.sleep(0.1)
            (RUN / 'release-wait.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
            capture(frame.f_locals['stage'], frame.f_locals['target'], 'after_observation_pause')
        return local_trace
    return None


def main():
    sys.settrace(trace)
    sys.argv = ['tools.puzzle_production.target_adapter', 'export', '--allow-background',
    '--input', str(REPO / 'content/authoring/pz-fliegenpilz/r07/package.zip'),
    '--external-root', str(REPO),
    '--approval', str(REPO / 'content/authoring/pz-fliegenpilz/r07/final-editorial-v2/approval.json'),
    '--name', 'Fliegenpilz', '--runtime-revision', '1', '--stem', 'fliegenpilz_001',
    '--save-slot', 'fliegenpilz_001', '--category-id', 'gemuese-pilze-kraeuter',
    '--categories', str(REPO / 'content/categories.json'),
    '--output-dir', str(RUN / 'export'),
    '--operation-report', str(RUN / 'export-operation.json')]
    try:
        runpy.run_module('tools.puzzle_production.target_adapter', run_name='__main__')
    finally:
        sys.settrace(None)


if __name__ == '__main__':
    main()
