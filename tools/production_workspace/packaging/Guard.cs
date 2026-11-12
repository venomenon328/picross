// Runs in the per-user MSI execute sequence, before InstallInitialize.
// No shutdown, process termination, state writes or network operations.
using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;
using Microsoft.Deployment.WindowsInstaller;
using FileAttributes = System.IO.FileAttributes;

public static class Guard {
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern IntPtr OpenEvent(uint access, bool inherit, string name);
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
    [DllImport("rstrtmgr.dll", CharSet=CharSet.Unicode)]
    static extern int RmStartSession(out uint session, int flags, StringBuilder key);
    [DllImport("rstrtmgr.dll", CharSet=CharSet.Unicode)]
    static extern int RmRegisterResources(uint session, uint files, string[] paths, uint apps, IntPtr processes, uint services, IntPtr names);
    [DllImport("rstrtmgr.dll")] static extern int RmGetList(uint session, out uint needed, ref uint count, IntPtr data, ref uint reasons);
    [DllImport("rstrtmgr.dll")] static extern int RmEndSession(uint session);

    static void NoLinks(string path) {
        for (var dir = new DirectoryInfo(path); dir != null; dir = dir.Parent) {
            if (dir.Exists && (dir.Attributes & FileAttributes.ReparsePoint) != 0)
                throw new IOException("Installationspfad enthält einen Link.");
        }
    }

    [CustomAction]
    public static ActionResult Check(Session session) {
        try {
            // Reject property-based path redirection, also during upgrade/uninstall.
            var local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            var expected = Path.Combine(local, "Programs", "Picross-Produktionsassistent");
            var target = Path.GetFullPath(session["INSTALLFOLDER"]).TrimEnd('\\');
            if (!String.Equals(target, expected, StringComparison.OrdinalIgnoreCase))
                throw new IOException("Installationsziel muss im eigenen Programmverzeichnis liegen.");
            NoLinks(target);
            var marker = OpenEvent(0x100000, false, @"Global\PicrossProductionWorkspace.Running." + WindowsIdentity.GetCurrent().User.Value);
            var error = Marshal.GetLastWin32Error();
            if (marker != IntPtr.Zero) CloseHandle(marker);
            if (marker != IntPtr.Zero || error != 2)
                throw new IOException("Eine App-Instanz läuft oder ihr Zustand ist unklar.");
            // Older portable P3 has no product marker. Never trust its PID/port.
            var state = Path.Combine(local, "PicrossProductionWorkspace", ".launcher");
            NoLinks(state);
            var stateLock = Path.Combine(state, "lock");
            if (File.Exists(stateLock)) {
                if ((File.GetAttributes(stateLock) & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Instanzlock enthält einen Link.");
                using (var stream = new FileStream(stateLock, FileMode.Open, FileAccess.ReadWrite, FileShare.None)) { }
            }
            // Also detect unrelated processes holding ANY installed payload file.
            // No RmShutdown/RmRestart. An inconclusive query is a hard refusal.
            uint rm;
            if (RmStartSession(out rm, 0, new StringBuilder(33)) != 0)
                throw new IOException("Windows-Dateibelegung nicht prüfbar.");
            try {
                using (var view = session.Database.OpenView("SELECT `FileName`, `Directory_` FROM `File`, `Component` WHERE `File`.`Component_` = `Component`.`Component`")) {
                    view.Execute();
                    Record row;
                    while ((row = view.Fetch()) != null) using (row) {
                        var name = row.GetString(1).Split('|').Last();
                        var file = Path.Combine(session.GetTargetPath(row.GetString(2)), name);
                        if (File.Exists(file) && RmRegisterResources(rm, 1, new string[] { file }, 0, IntPtr.Zero, 0, IntPtr.Zero) != 0)
                            throw new IOException("Dateibelegung nicht vollständig prüfbar.");
                    }
                }
                uint needed, count = 0, reasons = 0;
                var result = RmGetList(rm, out needed, ref count, IntPtr.Zero, ref reasons);
                if (result != 0 || needed != 0)
                    throw new IOException("Programmdateien sind durch eine laufende oder fremde Anwendung belegt.");
            } finally { RmEndSession(rm); }
            session.Log("P4: Programm-/Instanzschutz erfolgreich; keine Prozesse beendet.");
            return ActionResult.Success;
        } catch (Exception ex) {
            // No personal paths, credentials or instance metadata in the report.
            session.Log("P4: Installation vor Dateimanipulation abgebrochen (" + ex.GetType().Name + ").");
            using (var record = new Record(1)) {
                record.SetString(0, "Picross kann gerade nicht installiert/entfernt werden. " +
                    "Assistent und andere Anwendungen mit offenen Programmdateien regulär beenden; " +
                    "eine laufende Produktionsentfernung vollständig abwarten. Bei unklarem Zustand Pfade/Rechte prüfen. Danach den Installer erneut starten. Es wurde kein Prozess beendet.");
                session.Message(InstallMessage.Error, record);
            }
            return ActionResult.Failure;
        }
    }
}
