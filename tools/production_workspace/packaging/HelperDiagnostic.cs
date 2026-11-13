// Explicit T02 harness only. Never collected into the app; never invokes MSI.
using System;
using System.IO;
using System.Reflection;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Web.Script.Serialization;

class HelperDiagnostic {
    static Type Helper;
    static object Call(string method, params object[] args) {
        return Helper.GetMethod(method,BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,args);
    }
    static void Need(bool b) { if(!b) throw new Exception("Diagnostic assertion failed"); }
    static void Reject(string method, params object[] args) {
        try { Call(method,args); } catch(TargetInvocationException) { return; }
        throw new Exception("Negative accepted: "+method);
    }
    static int Main(string[] args) {
        if(args.Length==1 && args[0]=="child") { Console.WriteLine("READY"); Console.Out.Flush(); Console.ReadLine(); return 0; }
        try {
            Need(args.Length==8);
            Helper=Assembly.LoadFile(Path.GetFullPath(args[0])).GetType("UpdateHelper");
            Call("MsiIdentity",args[1],args[2],args[3],args[4]);
            Reject("MsiIdentity",args[1],"0.1.65535",args[3],args[4]);
            Reject("MsiIdentity",args[1],args[2],Guid.Empty.ToString().ToUpperInvariant(),args[4]);
            Reject("Installed",Guid.Empty.ToString().ToUpperInvariant(),args[2]);
            foreach(string value in new[]{"0.1.01","0.2.1","0.1.65536","0.1.1.1"}) Reject("VersionOf",value);
            Reject("Parent",IntPtr.Zero,new Dictionary<string,object>());
            var restart=(ProcessStartInfo)Call("RestartInfo",@"C:\synthetic state\Übung",true);
            Need(!restart.UseShellExecute && restart.EnvironmentVariables["PYINSTALLER_RESET_ENVIRONMENT"]=="1" &&
                 restart.Arguments=="--state \"C:\\synthetic state\\Übung\" --no-browser");
            Reject("RestartInfo","C:\\bad\" --injected",false);
            var info=new ProcessStartInfo(Assembly.GetExecutingAssembly().Location,"child") {
                UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardOutput=true };
            using(var child=Process.Start(info)) {
                try {
                    Need(child.StandardOutput.ReadLine()=="READY");
                    IntPtr handle=child.Handle;
                    var waiting=Task.Factory.StartNew(()=>Call("WaitParent",handle));
                    Need(!waiting.Wait(300)); // Readiness is deliberately not process termination.
                    child.StandardInput.WriteLine("END"); child.StandardInput.Close();
                    Need(waiting.Wait(5000)); child.WaitForExit(); Need(child.ExitCode==0);
                } finally { child.StandardInput.Close(); child.WaitForExit(5000); }
            }
            foreach(string input in new[]{"{}\n","{\"format\":\"foreign\"}\n",""}) {
                using(var child=Process.Start(new ProcessStartInfo(args[0]) {UseShellExecute=false,CreateNoWindow=true,
                        RedirectStandardInput=true,RedirectStandardOutput=true})) {
                    child.StandardInput.Write(input); child.StandardInput.Close();
                    Need(child.WaitForExit(5000)); Need(child.ExitCode==2 && child.StandardOutput.ReadToEnd()=="");
                }
            }
            using(var runtime=Process.GetProcessById(Int32.Parse(args[7])))
                Need((bool)Call("Ready",runtime,new Dictionary<string,object> {
                    {"state",args[5]},{"commit",args[6]},{"instance","synthetic-old-instance"}}));
            Console.WriteLine(new JavaScriptSerializer().Serialize(new Dictionary<string,object> {
                {"actual_helper_loaded",true},{"actual_msi_identity",true},{"wrong_msi_version_rejected",true},
                {"wrong_product_rejected",true},{"uninstalled_identity_rejected",true},{"invalid_versions_rejected",true},
                {"invalid_parent_handle_rejected",true},{"ready_child_did_not_release_wait",true},
                {"restart_environment_and_state_bound",true},
                {"actual_python_control_protocol_authenticated",true},
                {"actual_process_exit_released_wait",true},{"unbound_helper_inputs_rejected",true},
                {"installer_executed",false},{"limits","Reflection into exact built helper; isolated child process. No installed-app or Windows-11 lifecycle claim."}}));
            return 0;
        } catch(Exception e) { Console.Error.WriteLine(e.GetType().Name+": helper diagnostic failed"); return 2; }
    }
}
