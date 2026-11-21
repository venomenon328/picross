// Excluded GAME-APP-B adapter. Reflect the built helper, never install an MSI.
using System;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Collections.Generic;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

public static class GameUpdateDiagnostic {
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern bool QueryFullProcessImageName(IntPtr process,uint flags,StringBuilder path,ref uint length);
    static MethodInfo Method(Type helper, string name) {
        return helper.GetMethod(name,BindingFlags.NonPublic|BindingFlags.Static);
    }
    static void Reject(Action action) {
        try { action(); } catch(TargetInvocationException error) {
            if(error.InnerException is InvalidDataException) return;
            throw;
        }
        throw new Exception("Unexpected helper acceptance");
    }

    static string Q(string value) {
        if(value.Contains("\"")) throw new ArgumentException();
        return "\""+value+"\"";
    }
    static void Restart(string[] args) {
        string helperPath=args[1], python=args[2], state=args[3], image=args[4], report=args[5], scenario=args[6];
        Type helper=Assembly.LoadFile(helperPath).GetType("UpdateHelper",true);
        helper.GetField("Install",BindingFlags.NonPublic|BindingFlags.Static).SetValue(null,image);
        string stage=Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        string handoff=Path.GetFileName(stage);
        string name=(string)Method(helper,"RandomHex").Invoke(null,null);
        string key=(string)Method(helper,"RandomHex").Invoke(null,null);
        string preferences=Path.Combine(state,".updates","app-updates.json");
        var request=new Dictionary<string,object>{
            {"state",state},{"commit",args[7]},{"version",args[8]},{"fingerprint",args[9]},
            {"state_hashes",new Dictionary<string,object>{{".updates/app-updates.json",Method(helper,"HashFile").Invoke(null,new object[]{preferences})}}}
        };
        var identity=WindowsIdentity.GetCurrent().User;
        var security=new PipeSecurity();
        security.SetAccessRuleProtection(true,false);
        security.AddAccessRule(new PipeAccessRule(identity,PipeAccessRights.FullControl,AccessControlType.Allow));
        using(var active=new FileStream(Path.Combine(stage,"active"),FileMode.CreateNew,FileAccess.ReadWrite,FileShare.None))
        using(var pipe=new NamedPipeServerStream("PicrossPGReady-"+name,PipeDirection.InOut,1,PipeTransmissionMode.Byte,
                                                 PipeOptions.Asynchronous,4096,4096,security)) {
            var info=new ProcessStartInfo(python,"-B -m tools.game_app.restart_diagnostic "+Q(state)+" "+Q(image)+" "+Q(report)+" "+scenario) {
                UseShellExecute=false, CreateNoWindow=true
            };
            info.EnvironmentVariables["PICROSS_PG_RESTART_PIPE"]=name;
            info.EnvironmentVariables["PICROSS_PG_RESTART_KEY"]=key;
            info.EnvironmentVariables["PICROSS_PG_RESTART_PID"]=Process.GetCurrentProcess().Id.ToString();
            info.EnvironmentVariables["PICROSS_PG_RESTART_STAGE"]=handoff;
            var connected=pipe.BeginWaitForConnection(null,null);
            using(var launcher=Process.Start(info)) {
                // The Store Python launcher can resolve to its registered package image.
                // Observe that exact process image in the diagnostic bootstrap only.
                var path=new StringBuilder(32768); uint length=32768;
                if(!QueryFullProcessImageName(launcher.Handle,0,path,ref length))
                    throw new Exception("Diagnostic launcher image error: "+Marshal.GetLastWin32Error());
                helper.GetField("Exe",BindingFlags.NonPublic|BindingFlags.Static).SetValue(null,path.ToString());
                bool legacy=scenario=="legacy";
                bool confirmed=false;
                try {
                    Method(helper,legacy?"GameReady":"LauncherReady").Invoke(null,new object[]{pipe,launcher,request,key,connected});
                    confirmed=true;
                } catch(TargetInvocationException error) {
                    if(!(error.InnerException is InvalidDataException)) throw;
                }
                bool expected=legacy || scenario=="confirmed" || scenario=="missing";
                if(confirmed!=expected) throw new Exception("Wrong PG readiness: "+scenario);
                if(legacy) {
                    if(!launcher.WaitForExit(35000) || launcher.ExitCode!=0) throw new Exception("Legacy child failed");
                } else if(scenario!="missing") {
                    Method(helper,"Report").Invoke(null,new object[]{state,handoff,confirmed?"installed":"unconfirmed",args[8]});
                }
                Console.WriteLine(scenario+" launcher_pid="+launcher.Id+" authenticated_readiness="+confirmed);
            }
        }
    }

    public static int Main(string[] args) {
        if(args[0]=="--restart") { Restart(args); return 0; }
        if(args.Length==1 && args[0]=="--wait-child") {
            Console.WriteLine("waiting"); Console.ReadLine(); return 0;
        }
        Type helper=Assembly.LoadFile(args[0]).GetType("UpdateHelper",true);
        var identity=Method(helper,"MsiIdentity");
        identity.Invoke(null,new object[]{args[1],args[2],args[3],args[4]});
        Reject(()=>identity.Invoke(null,new object[]{args[1],args[2],args[3],Guid.Empty.ToString()}));
        Reject(()=>identity.Invoke(null,new object[]{args[1],"0.1.0",args[3],args[4]}));
        Reject(()=>identity.Invoke(null,new object[]{args[1],args[2],Guid.Empty.ToString(),args[4]}));
        Console.WriteLine("MSI database: PG accepted; false product, upgrade and version refused");

        var info=new ProcessStartInfo(Assembly.GetExecutingAssembly().Location,"--wait-child") {
            UseShellExecute=false, RedirectStandardInput=true, RedirectStandardOutput=true, CreateNoWindow=true
        };
        using(var child=Process.Start(info)) {
            try {
                if(child.StandardOutput.ReadLine()!="waiting") throw new Exception("Child did not start");
                IntPtr handle=child.Handle;
                var wait=Task.Factory.StartNew(()=> Method(helper,"WaitParent").Invoke(null,new object[]{handle}));
                if(wait.Wait(300)) throw new Exception("Exited before real child exit");
                child.StandardInput.WriteLine("end"); child.StandardInput.Flush();
                if(!wait.Wait(5000) || !child.WaitForExit(5000) || child.ExitCode!=0)
                    throw new Exception("Real child exit not observed");
                Console.WriteLine("Parent wait: live process blocked; real exit released it");
            } finally {
                child.StandardInput.Close();
                child.WaitForExit(5000);
            }
        }
        return 0;
    }
}
