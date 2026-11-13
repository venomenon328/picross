"""OS owned checkout lock. No PID based takeover and no checkout writes."""
import hashlib
import os


class Instance:
    def __init__(self, root):
        self.handle = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            self.kernel.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
            self.kernel.CreateMutexW.restype = wintypes.HANDLE
            self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            name = hashlib.sha256(str(root).casefold().encode()).hexdigest()
            self.handle = self.kernel.CreateMutexW(None, False, "Local\\PicrossPE-"+name)
            if not self.handle: raise OSError("Editorinstanz konnte nicht gesichert werden.")
            if ctypes.get_last_error() == 183:
                self.close()
                raise ValueError("Für dieses Checkout läuft bereits ein Editor. Vorhandenes Starterfenster öffnen.")
        else:
            # Abstract Unix sockets leave no permanent lock file or data in the checkout.
            import socket
            self.handle = socket.socket(socket.AF_UNIX)
            try: self.handle.bind("\0picross-pe-"+hashlib.sha256(str(root).encode()).hexdigest())
            except OSError:
                self.close()
                raise ValueError("Für dieses Checkout läuft bereits ein Editor.")

    def close(self):
        if self.handle is not None:
            if os.name == "nt": self.kernel.CloseHandle(self.handle)
            else: self.handle.close()
            self.handle = None
