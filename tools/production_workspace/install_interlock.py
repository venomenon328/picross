"""Windows product-wide liveness, independent of state paths, PIDs and ports.

Publish before checking MSI's execution mutex. The execute-sequence CA checks
our marker after MSI acquired its mutex. Thus a racing start either makes MSI
abort, or refuses to enter application code until the installer has finished.
The marker lives through setup, preflight, requests and the entire P2 drain.
"""
import os


class InstallInterlock:
    def __init__(self):
        self.handle = None

    def acquire(self):
        if os.name != 'nt':
            return
        import ctypes
        from ctypes import wintypes as w
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        adv = ctypes.WinDLL('advapi32', use_last_error=True)
        kernel.GetCurrentProcess.restype = w.HANDLE
        kernel.CloseHandle.argtypes = [w.HANDLE]
        adv.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE)]
        adv.GetTokenInformation.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD)]
        adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(w.LPWSTR)]
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        token, size, sid = w.HANDLE(), w.DWORD(), w.LPWSTR()
        if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
            raise ValueError('Windowsbenutzer für Installationsschutz nicht prüfbar.')
        try:
            adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
            buffer = ctypes.create_string_buffer(size.value)
            if not adv.GetTokenInformation(token, 1, buffer, size, ctypes.byref(size)):
                raise ValueError('Windowsbenutzer für Installationsschutz nicht lesbar.')
            pointer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
            if not adv.ConvertSidToStringSidW(pointer, ctypes.byref(sid)):
                raise ValueError('Windowsbenutzer für Installationsschutz unbekannt.')
            name = 'Global\\PicrossProductionWorkspace.Running.' + sid.value
        finally:
            if sid:
                kernel.LocalFree(ctypes.cast(sid, ctypes.c_void_p))
            kernel.CloseHandle(token)
        kernel.CreateEventW.argtypes = [ctypes.c_void_p, w.BOOL, w.BOOL, w.LPCWSTR]
        kernel.CreateEventW.restype = w.HANDLE
        self.handle = kernel.CreateEventW(None, True, False, name)
        if not self.handle:
            raise ValueError('Installationsschutz unklar. Laufende App/Installation regulär beenden und erneut versuchen.')
        kernel.OpenMutexW.argtypes = [w.DWORD, w.BOOL, w.LPCWSTR]
        kernel.OpenMutexW.restype = w.HANDLE
        kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        kernel.WaitForSingleObject.restype = w.DWORD
        kernel.ReleaseMutex.argtypes = [w.HANDLE]
        gate = kernel.OpenMutexW(0x100001, False, 'Global\\_MSIExecute')
        error = ctypes.get_last_error()
        busy = False
        if gate:
            result = kernel.WaitForSingleObject(gate, 0)
            if result in (0, 0x80):
                kernel.ReleaseMutex(gate)
            # An idle MSI server may keep an unowned mutex alive. Only an
            # actually held/abandoned/unqueryable mutex prevents a new start.
            busy = result != 0
            kernel.CloseHandle(gate)
        if busy or (not gate and error != 2):
            self.close()
            raise ValueError('Eine Windowsinstallation läuft oder ist nicht prüfbar. Nach deren Ende erneut starten.')

    def close(self):
        if self.handle:
            import ctypes
            from ctypes import wintypes
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel.CloseHandle(self.handle)
            self.handle = None
