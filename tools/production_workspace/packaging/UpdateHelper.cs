// Standalone .NET Framework executable. No Python/app DLLs, network download,
// arbitrary command API, elevation, process kill or root/configuration override.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Diagnostics;
using System.Reflection;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
using System.Threading.Tasks;
using System.Net;

public static class UpdateHelper {
    static readonly JavaScriptSerializer Json = new JavaScriptSerializer { MaxJsonLength = 32768, RecursionLimit = 20 };
    static string User = WindowsIdentity.GetCurrent().User.Value;
    static string Install = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "Picross-Produktionsassistent");
    static string Exe = Path.Combine(Install, "Picross-Start.exe");
    [DllImport("kernel32.dll", SetLastError=true)] static extern uint WaitForSingleObject(IntPtr h, uint ms);
    [DllImport("kernel32.dll")] static extern uint GetProcessId(IntPtr h);
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    struct ProcessEntry {
        public uint size, usage, pid; public IntPtr heap; public uint module, threads, parent; public int priority; public uint flags;
        [MarshalAs(UnmanagedType.ByValTStr,SizeConst=260)] public string name;
    }
    [DllImport("kernel32.dll",SetLastError=true)] static extern IntPtr CreateToolhelp32Snapshot(uint flags,uint pid);
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode)] static extern bool Process32First(IntPtr snapshot,ref ProcessEntry entry);
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode)] static extern bool Process32Next(IntPtr snapshot,ref ProcessEntry entry);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool QueryFullProcessImageName(IntPtr h, uint flags, StringBuilder name, ref uint length);
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool OpenProcessToken(IntPtr process, uint access, out IntPtr token);
    [DllImport("msi.dll", CharSet=CharSet.Unicode)] static extern uint MsiGetProductInfoEx(string product, string sid, uint context, string property, StringBuilder value, ref uint size);
    [DllImport("msi.dll", CharSet=CharSet.Unicode)] static extern uint MsiOpenDatabase(string path, IntPtr persist, out uint database);
    [DllImport("msi.dll", CharSet=CharSet.Unicode)] static extern uint MsiDatabaseOpenView(uint database, string sql, out uint view);
    [DllImport("msi.dll")] static extern uint MsiViewExecute(uint view, uint record);
    [DllImport("msi.dll")] static extern uint MsiViewFetch(uint view, out uint record);
    [DllImport("msi.dll", CharSet=CharSet.Unicode)] static extern uint MsiRecordGetString(uint record, uint field, StringBuilder text, ref uint length);
    [DllImport("msi.dll")] static extern uint MsiCloseHandle(uint handle);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int MessageBox(IntPtr window, string text, string title, uint type);

    static void Need(bool condition) { if (!condition) throw new InvalidDataException("Update binding refused"); }
    static Dictionary<string,object> Map(object o) { var d = o as Dictionary<string,object>; Need(d != null); return d; }
    static string Text(Dictionary<string,object> d, string k) { Need(d.ContainsKey(k) && d[k] is string); return (string)d[k]; }
    static long Number(Dictionary<string,object> d, string k) { Need(d.ContainsKey(k) && (d[k] is int || d[k] is long)); return Convert.ToInt64(d[k]); }
    static void Shape(Dictionary<string,object> d, string fields) { Need(d.Keys.OrderBy(x=>x).SequenceEqual(fields.Split(' ').OrderBy(x=>x))); }
    static bool Hex(string s, int n) { return s.Length == n && s.All(c=>"0123456789abcdef".Contains(c)); }
    static string Hash(Stream stream) { stream.Position=0; using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(stream)).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { NoLinks(path); using(var f=File.OpenRead(path)) return Hash(f); }
    static Dictionary<string,object> Read(string path) { NoLinks(path); Need(new FileInfo(path).Length <= 32768); return Map(Json.DeserializeObject(File.ReadAllText(path, new UTF8Encoding(false, true)))); }
    static string Quote(string s) { Need(!s.Contains('"') && !s.Contains('\r') && !s.Contains('\n')); return "\"" + s.TrimEnd('\\') + "\""; }
    static void NoLinks(string path) {
        for (string p=Path.GetFullPath(path); p!=null; p=Path.GetDirectoryName(p)) {
            try { Need((File.GetAttributes(p) & FileAttributes.ReparsePoint) == 0); }
            catch (FileNotFoundException) { }
            catch (DirectoryNotFoundException) { }
        }
    }
    static void Private(string path) {
        NoLinks(path);
        var acl = Directory.GetAccessControl(path);
        Need(acl.GetOwner(typeof(SecurityIdentifier)).Value == User && acl.AreAccessRulesProtected);
        foreach (FileSystemAccessRule rule in acl.GetAccessRules(true, true, typeof(SecurityIdentifier)))
            Need(rule.AccessControlType != AccessControlType.Allow || rule.IdentityReference.Value == User || rule.IdentityReference.Value == "S-1-5-18");
    }
    static Version VersionOf(string s) {
        var v = new Version(s);
        Need(v.Major == 0 && v.Minor == 1 && v.Build >= 0 && v.Build <= 65535 && v.Revision == -1 && v.ToString(3) == s);
        return v;
    }
    static void Installed(string product, string version) {
        uint size=128; var text=new StringBuilder(128);
        Need(MsiGetProductInfoEx("{"+product+"}", null, 2, "VersionString", text, ref size) == 0 && text.ToString() == version);
    }
    static void MsiIdentity(string path, string version, string product, string upgrade) {
        uint db; Need(MsiOpenDatabase(path, IntPtr.Zero, out db) == 0);
        try {
            foreach(var pair in new Dictionary<string,string>{{"ProductVersion",version},{"ProductCode","{"+product+"}"},{"UpgradeCode","{"+upgrade+"}"}}) {
                uint view=0, row=0;
                try {
                    Need(MsiDatabaseOpenView(db, "SELECT `Value` FROM `Property` WHERE `Property`='"+pair.Key+"'", out view)==0);
                    Need(MsiViewExecute(view,0)==0 && MsiViewFetch(view,out row)==0);
                    uint n=128; var text=new StringBuilder(128);
                    Need(MsiRecordGetString(row,1,text,ref n)==0 && text.ToString()==pair.Value);
                } finally { if(row!=0) MsiCloseHandle(row); if(view!=0) MsiCloseHandle(view); }
            }
        } finally { MsiCloseHandle(db); }
    }
    static string BoundedLine(int limit, int timeout) {
        var task=Task.Factory.StartNew(()=> {
            var text=new StringBuilder();
            while(true) { int c=Console.In.Read(); if(c<0) return null; if(c=='\n') return text.ToString(); Need(text.Length<limit); text.Append((char)c); }
        });
        Need(task.Wait(timeout)); return task.Result;
    }
    static void Parent(IntPtr handle, Dictionary<string,object> d) {
        Need(handle!=IntPtr.Zero && GetProcessId(handle)==Number(d,"pid") && WaitForSingleObject(handle,0)==258);
        var snapshot=CreateToolhelp32Snapshot(2,0); Need(snapshot!=new IntPtr(-1));
        try {
            var entry=new ProcessEntry(); entry.size=(uint)Marshal.SizeOf(entry); bool found=false;
            if(Process32First(snapshot,ref entry)) do {
                if(entry.pid==Process.GetCurrentProcess().Id) { Need(entry.parent==Number(d,"pid")); found=true; break; }
            } while(Process32Next(snapshot,ref entry));
            Need(found);
        } finally { CloseHandle(snapshot); }
        var image=new StringBuilder(32768); uint n=32768;
        Need(QueryFullProcessImageName(handle,0,image,ref n) && String.Equals(image.ToString(),Exe,StringComparison.OrdinalIgnoreCase));
        IntPtr token; Need(OpenProcessToken(handle,8,out token));
        try { using(var id=new WindowsIdentity(token)) Need(id.User.Value==User); } finally { CloseHandle(token); }
        Need(HashFile(Exe)==Text(d,"old_exe_sha256"));
        var pe=FileVersionInfo.GetVersionInfo(Exe); var old=VersionOf(Text(d,"old_version"));
        Need(pe.FileMajorPart==old.Major && pe.FileMinorPart==old.Minor && pe.FileBuildPart==old.Build && pe.FilePrivatePart==0);
        Installed(Text(d,"old_product"),Text(d,"old_version"));
        var components=Read(Path.Combine(Install,"components.json"));
        Need(Text(components,"version")==Text(d,"old_version") && Text(components,"commit")==Text(d,"old_commit") &&
             Text(components,"product_code")==Text(d,"old_product") && Text(components,"upgrade_code")==Text(d,"upgrade"));
    }
    static void WaitParent(IntPtr handle) {
        // Only called after explicit drain acknowledgement. A live handle remains
        // bound to the original process even if its PID is subsequently reused.
        Need(WaitForSingleObject(handle,120000)==0);
    }
    static void State(Dictionary<string,object> d) {
        string state=Text(d,"state"); NoLinks(state);
        var hashes=Map(d["state_hashes"]);
        Shape(hashes,"config.json .launcher/address.json .launcher/app-updates.json");
        foreach(var pair in hashes) Need(pair.Value is string && HashFile(Path.Combine(state,pair.Key))==(string)pair.Value);
        var preference=Read(Path.Combine(state,".launcher","app-updates.json"));
        Shape(preference,"format enabled");
        Need(Text(preference,"format")=="picross-app-update-preference-v1" && preference["enabled"] is bool && (bool)preference["enabled"]);
    }
    static void Report(string state, string nonce, string status, string version) {
        string path=Path.Combine(state,".launcher","update-result.json"); NoLinks(path);
        string temp=path+"."+nonce+".tmp";
        using(var file=new FileStream(temp,FileMode.CreateNew,FileAccess.Write,FileShare.None)) {
            var bytes=Encoding.UTF8.GetBytes(Json.Serialize(new Dictionary<string,object>{{"format","picross-update-result-v1"},{"nonce",nonce},{"status",status},{"version",version}})+"\n");
            file.Write(bytes,0,bytes.Length); file.Flush(true);
        }
        if(File.Exists(path)) File.Replace(temp,path,null); else File.Move(temp,path);
    }
    static string Mac(string key, string prefix, SortedDictionary<string,object> value) {
        using(var h=new HMACSHA256(Encoding.ASCII.GetBytes(key)))
            return BitConverter.ToString(h.ComputeHash(Encoding.ASCII.GetBytes(prefix+Json.Serialize(value)))).Replace("-","").ToLowerInvariant();
    }
    static bool Ready(Process launched, Dictionary<string,object> d) {
        string state=Text(d,"state");
        int port=Convert.ToInt32(Read(Path.Combine(state,".launcher","address.json"))["port"]);
        for(int attempt=0; attempt<100; attempt++) {
            if(launched.HasExited) return false;
            try {
                var m=Read(Path.Combine(state,".launcher","instance.json"));
                Need(Number(m,"pid")==launched.Id && Text(m,"build")==Text(d,"commit") && Number(m,"port")==port &&
                     Text(m,"instance")!=Text(d,"instance") && Text(m,"protocol")=="picross-launcher-v1");
                byte[] nonce=new byte[24]; using(var random=RandomNumberGenerator.Create()) random.GetBytes(nonce);
                string challenge=BitConverter.ToString(nonce).Replace("-","").ToLowerInvariant();
                var body=new SortedDictionary<string,object>(StringComparer.Ordinal){{"action","identify"},{"challenge",challenge}};
                body["proof"]=Mac(Text(m,"key"),"request:",body);
                byte[] bytes=Encoding.ASCII.GetBytes(Json.Serialize(body));
                var request=(HttpWebRequest)WebRequest.Create("http://127.0.0.1:"+port+"/control/v1");
                request.Proxy=null; request.AllowAutoRedirect=false; request.Timeout=1000; request.ReadWriteTimeout=1000;
                request.Method="POST"; request.ContentType="application/json"; request.ContentLength=bytes.Length;
                using(var stream=request.GetRequestStream()) stream.Write(bytes,0,bytes.Length);
                using(var response=request.GetResponse()) using(var stream=response.GetResponseStream()) using(var output=new MemoryStream()) {
                    var buffer=new byte[8193]; int count=stream.Read(buffer,0,buffer.Length); output.Write(buffer,0,count);
                    while(count>0 && output.Length<=8192) { count=stream.Read(buffer,0,buffer.Length); output.Write(buffer,0,count); }
                    Need(output.Length<=8192);
                    var reply=Map(Json.DeserializeObject(Encoding.UTF8.GetString(output.ToArray())));
                    Shape(reply,"protocol build instance challenge state proof"); string proof=Text(reply,"proof"); reply.Remove("proof");
                    string expected=Mac(Text(m,"key"),"response:",new SortedDictionary<string,object>(reply,StringComparer.Ordinal));
                    Need(proof.Length==expected.Length); int difference=0; for(int i=0;i<proof.Length;i++) difference|=proof[i]^expected[i];
                    Need(difference==0 && Text(reply,"challenge")==challenge && Text(reply,"build")==Text(d,"commit") &&
                         Text(reply,"instance")==Text(m,"instance") && Text(reply,"protocol")=="picross-launcher-v1" && Text(reply,"state")=="ready");
                }
                return true;
            } catch(Exception) { System.Threading.Thread.Sleep(200); }
        }
        return false;
    }
    static ProcessStartInfo RestartInfo(string state, bool noBrowser) {
        var info=new ProcessStartInfo(Exe,"--state "+Quote(state)+(noBrowser?" --no-browser":"")) {
            UseShellExecute=false, WorkingDirectory=Install };
        // A fresh top-level bootloader, not a worker inheriting the old frozen runtime.
        info.EnvironmentVariables["PYINSTALLER_RESET_ENVIRONMENT"]="1";
        return info;
    }
    public static int Main(string[] args) {
        string state=null, nonce=null, version=null, outcome="unconfirmed";
        IntPtr parent=IntPtr.Zero; var streams=new List<FileStream>(); FileStream active=null;
        bool bound=false, committed=false;
        try {
            Console.InputEncoding=new UTF8Encoding(false,true);
            Need(args.Length==0 && !new WindowsPrincipal(WindowsIdentity.GetCurrent()).IsInRole(WindowsBuiltInRole.Administrator));
            string line=BoundedLine(32768,20000); Need(line!=null);
            var d=Map(Json.DeserializeObject(line));
            Shape(d,"format nonce state pid instance old_version old_product old_commit old_exe_sha256 version product upgrade commit binding files state_hashes exe_sha256 exe_bytes no_browser parent_handle");
            Need(Text(d,"format")=="picross-update-handoff-v1" && d["no_browser"] is bool);
            nonce=Text(d,"nonce"); state=Text(d,"state"); version=Text(d,"version");
            Need(Hex(nonce,48) && Path.IsPathRooted(state) && Path.GetFullPath(state)==state &&
                 !String.Equals(state,Install,StringComparison.OrdinalIgnoreCase) && !state.StartsWith(Install+"\\",StringComparison.OrdinalIgnoreCase) &&
                 Hex(Text(d,"binding"),64) && Hex(Text(d,"commit"),40) && Hex(Text(d,"exe_sha256"),64) && Number(d,"exe_bytes")>0 &&
                 VersionOf(version)>VersionOf(Text(d,"old_version")));
            string stage=Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            Need(String.Equals(stage,Path.Combine(state,".launcher","update-staging",nonce),StringComparison.OrdinalIgnoreCase));
            Private(stage); Private(Path.Combine(state,".launcher")); NoLinks(Install);
            parent=new IntPtr(Number(d,"parent_handle")); Parent(parent,d); State(d);
            var instance=Read(Path.Combine(state,".launcher","instance.json"));
            Need(Text(instance,"instance")==Text(d,"instance") && Number(instance,"pid")==Number(d,"pid") && Text(instance,"build")==Text(d,"old_commit"));
            active=new FileStream(Path.Combine(stage,"active"),FileMode.CreateNew,FileAccess.ReadWrite,FileShare.None);
            string msi="Picross-Produktionsassistent-"+version+"-windows-x64.msi";
            var files=Map(d["files"]);
            Shape(files,msi+" "+msi+".sha256 START.txt delivery.json inputs.json manifest.json manifest.sig.json");
            long total=0;
            foreach(var pair in files) {
                var binding=Map(pair.Value); Shape(binding,"bytes sha256");
                long size=Number(binding,"bytes"); total+=size; Need(size>0 && total<=513L*1024*1024 && Hex(Text(binding,"sha256"),64));
                string path=Path.Combine(stage,pair.Key); NoLinks(path);
                var file=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.Read); streams.Add(file);
                Need(file.Length==size && Hash(file)==Text(binding,"sha256"));
            }
            Need(HashFile(Path.Combine(stage,"manifest.json"))==Text(d,"binding"));
            MsiIdentity(Path.Combine(stage,msi),version,Text(d,"product"),Text(d,"upgrade"));
            bound=true;
            Console.Out.NewLine="\n"; Console.WriteLine("READY "+nonce); Console.Out.Flush();
            string command=BoundedLine(80,1800000);
            if(command!="GO "+nonce) { outcome="cancelled"; return 2; }
            committed=true;
            WaitParent(parent); CloseHandle(parent); parent=IntPtr.Zero;
            State(d); Installed(Text(d,"old_product"),Text(d,"old_version"));
            // Rehash every locked candidate immediately before invoking system MSI.
            int index=0; foreach(var pair in files) Need(Hash(streams[index++])==Text(Map(pair.Value),"sha256"));
            MsiIdentity(Path.Combine(stage,msi),version,Text(d,"product"),Text(d,"upgrade"));
            bool desktop=false;
            using(var key=Microsoft.Win32.Registry.CurrentUser.OpenSubKey(@"Software\PicrossProductionWorkspace\Installer"))
                desktop=key!=null && Object.Equals(key.GetValue("DesktopShortcut"),1);
            var info=new ProcessStartInfo(Path.Combine(Environment.SystemDirectory,"msiexec.exe"),
                "/i "+Quote(Path.Combine(stage,msi))+" /qn /norestart ALLUSERS=2 MSIINSTALLPERUSER=1 REBOOT=ReallySuppress MSIRESTARTMANAGERCONTROL=Disable"+(desktop?" INSTALLDESKTOP=1":"")) {
                UseShellExecute=false, CreateNoWindow=true, WorkingDirectory=stage };
            int code;
            using(var installer=Process.Start(info)) { installer.WaitForExit(); code=installer.ExitCode; }
            if(code==3010 || code==1641) { outcome="reboot"; return 3; }
            if(code!=0) { outcome="failed"; return 2; }
            Installed(Text(d,"product"),version); State(d);
            var components=Read(Path.Combine(Install,"components.json"));
            Need(Text(components,"version")==version && Text(components,"commit")==Text(d,"commit") && Text(components,"product_code")==Text(d,"product"));
            Need(HashFile(Exe)==Text(d,"exe_sha256") && new FileInfo(Exe).Length==Number(d,"exe_bytes"));
            var pe=FileVersionInfo.GetVersionInfo(Exe);
            Need(pe.FileMajorPart==0 && pe.FileMinorPart==1 && pe.FileBuildPart==VersionOf(version).Build && pe.FilePrivatePart==0);
            using(var launched=Process.Start(RestartInfo(state,(bool)d["no_browser"]))) Need(Ready(launched,d));
            outcome="installed";
            return 0;
        } catch(Exception) { return 2; }
        finally {
            foreach(var stream in streams) stream.Dispose();
            if(parent!=IntPtr.Zero) CloseHandle(parent);
            if(bound) {
                try { Report(state,nonce,outcome,version); } catch(Exception) { outcome="unconfirmed"; }
                if(committed && outcome!="installed") MessageBox(IntPtr.Zero,
                    "App-Update nicht erfolgreich bestätigt ("+outcome+"). Windowsinstallation prüfen. Danach den Assistenten manuell starten oder einen geprüften neueren Installer erneut ausführen. Es wurde kein Prozess beendet und kein automatischer Wiederholungsversuch gestartet.",
                    "Picross · App-Update",0x10);
                // Delete only the seven fixed inputs after the installer has ended.
                // This running EXE and its lock are reclaimed by the next launcher.
                try {
                    string stage=Path.Combine(state,".launcher","update-staging",nonce);
                    string msi="Picross-Produktionsassistent-"+version+"-windows-x64.msi";
                    foreach(string name in new[]{msi,msi+".sha256","START.txt","delivery.json","inputs.json","manifest.json","manifest.sig.json"}) {
                        string path=Path.Combine(stage,name); NoLinks(path); File.Delete(path);
                    }
                } catch(Exception) { }
            }
            if(active!=null) active.Dispose();
        }
    }
}
