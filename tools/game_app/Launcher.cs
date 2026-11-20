using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Threading;

public static class Launcher {
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    static extern int MessageBox(IntPtr parent, string message, string title, uint type);

    static void CheckInstaller() {
        Mutex installer;
        try {
            installer = Mutex.OpenExisting(@"Global\_MSIExecute", MutexRights.Synchronize | MutexRights.Modify);
        } catch (WaitHandleCannotBeOpenedException) {
            return;
        }
        using (installer) {
            try {
                if (installer.WaitOne(0)) {
                    installer.ReleaseMutex();
                    return;
                }
            } catch (AbandonedMutexException) {
                installer.ReleaseMutex();
            }
        }
        throw new IOException("Eine Windowsinstallation läuft oder ist nicht prüfbar. Bitte danach erneut starten.");
    }

    static FileStream OpenPayload(string path, string digest) {
        var file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        try {
            using (var sha = SHA256.Create()) {
                var actual = BitConverter.ToString(sha.ComputeHash(file)).Replace("-", "");
                if (!String.Equals(actual, digest, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException();
            }
            return file;
        } catch {
            file.Dispose();
            throw;
        }
    }

    public static int Main() {
        try {
            string sid;
            using (var identity = WindowsIdentity.GetCurrent()) {
                sid = identity.User.Value;
            }
            using (var marker = new EventWaitHandle(false, EventResetMode.ManualReset,
                                                    @"Global\PicrossGame.Running." + sid)) {
                CheckInstaller();
                var directory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                var player = Path.Combine(directory, "picross-p1.exe");
                var pack = Path.Combine(directory, "picross-p1.pck");
                using (OpenPayload(player, BuildIdentity.PlayerHash))
                using (OpenPayload(pack, BuildIdentity.PackHash))
                using (var process = Process.Start(new ProcessStartInfo(player) {
                    WorkingDirectory = directory,
                    UseShellExecute = false,
                })) {
                    process.WaitForExit();
                    if (process.ExitCode != 0)
                        throw new IOException("Picross wurde mit einem Fehler beendet. Bitte erneut starten.");
                }
            }
            return 0;
        } catch (Exception error) {
            var hint = error.GetType() == typeof(IOException) ? error.Message :
                "Picross konnte nicht gestartet werden. Prüfe die Installation und verwende bei Bedarf den Installer erneut.";
            MessageBox(IntPtr.Zero, hint, "Picross", 0x10);
            return 1;
        }
    }
}
