// Explicit T02 harness only. Never collected into the app; never invokes MSI.
using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Reflection;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Web.Script.Serialization;

class HelperDiagnostic {
    static Type Helper;
    static string Phase="arguments";
    static object Call(string method, params object[] args) {
        return Helper.GetMethod(method,BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,args);
    }
    static void Need(bool b) { if(!b) throw new Exception("Diagnostic assertion failed"); }
    static void Reject(string method, params object[] args) {
        try { Call(method,args); } catch(TargetInvocationException) { return; }
        throw new Exception("Negative accepted: "+method);
    }
    static void Load(string path) { Helper=Assembly.LoadFile(Path.GetFullPath(path)).GetType("UpdateHelper"); }
    static void Native(string[] args) {
        string selection="{\"checkout\":\"C:/synthetic \\u00fc\",\"port\":\"1234\"}";
        foreach(string variant in new[]{"good","bad-key","wrong-commit","wrong-selection"}) {
            string nonce=Guid.NewGuid().ToString("N")+"aaaaaaaaaaaaaaaa", key=new string('a',48);
            using(var pipe=new NamedPipeServerStream("PicrossPEReady-"+nonce,PipeDirection.InOut,1,PipeTransmissionMode.Byte,PipeOptions.Asynchronous)) {
                var info=new ProcessStartInfo(args[9],"-X utf8 -m tools.puzzle_editor.diagnostic --native-ready --state "+(string)Call("Quote",args[5])+" --commit "+args[6]) {
                    UseShellExecute=false,CreateNoWindow=true,WorkingDirectory=args[10],RedirectStandardOutput=true,RedirectStandardError=true };
                info.EnvironmentVariables["PICROSS_PE_READY_NONCE"]=nonce;
                info.EnvironmentVariables["PICROSS_PE_READY_KEY"]=variant=="bad-key"?new string('b',48):key;
                info.EnvironmentVariables["PICROSS_PE_READY_SELECTION"]=selection;
                var connected=pipe.BeginWaitForConnection(null,null);
                using(var child=Process.Start(info)) {
                    var d=new Dictionary<string,object>{{"state",args[5]},{"commit",variant=="wrong-commit"?new string('0',40):args[6]},
                        {"selection",variant=="wrong-selection"?"{\"checkout\":\"other\",\"port\":\"1234\"}":selection},
                        {"state_hashes",new Dictionary<string,object>{{"config.json",Call("HashFile",Path.Combine(args[5],"config.json"))},
                            {".updates/app-updates.json",Call("HashFile",Path.Combine(args[5],".updates/app-updates.json"))}}}};
                    if(variant=="good") Call("EditorReady",pipe,child,d,key,connected);
                    else Reject("EditorReady",pipe,child,d,key,connected);
                    Need(child.WaitForExit(10000));
                    if(child.ExitCode!=0) throw new Exception(child.StandardError.ReadToEnd());
                    Need(child.StandardOutput.ReadToEnd().Contains("native-ready-without-service"));
                }
            }
        }
    }
    static int Main(string[] args) {
        if(args.Length==1 && args[0]=="child") { Console.WriteLine("READY"); Console.Out.Flush(); Console.ReadLine(); return 0; }
        try {
            if(args.Length==3 && args[0]=="handshake") {
                Load(args[1]); bool go=(bool)Call("ReadyGo",args[2]);
                Console.WriteLine(go?"GO-accepted":"cancelled"); return 0;
            }
            Need(args.Length==11); bool editor=args[8]=="pe";
            Load(args[0]);
            Phase="MSI identity";
            Call("MsiIdentity",args[1],args[2],args[3],args[4]);
            Reject("MsiIdentity",args[1],"0.1.65535",args[3],args[4]);
            Reject("MsiIdentity",args[1],args[2],Guid.Empty.ToString().ToUpperInvariant(),args[4]);
            Reject("Installed",Guid.Empty.ToString().ToUpperInvariant(),args[2]);
            Phase="version and product";
            string line=editor?"0.2.":"0.1.";
            foreach(string value in new[]{line+"01",editor?"0.1.1":"0.2.1",line+"65536",line+"1.1"}) Reject("VersionOf",value);
            Need((string)Call("ProductCode",args[2])==args[3]);
            string bad=args[1]+".invalid";
            try { File.WriteAllText(bad,"Not an MSI"); Reject("MsiIdentity",bad,args[2],args[3],args[4]); }
            finally { File.Delete(bad); }
            Reject("Parent",IntPtr.Zero,new Dictionary<string,object>());
            Phase="restart context";
            var restart=(ProcessStartInfo)Call("RestartInfo",@"C:\synthetic state\Übung",true);
            Need(!restart.UseShellExecute && restart.EnvironmentVariables["PYINSTALLER_RESET_ENVIRONMENT"]=="1" &&
                 restart.Arguments=="--state \"C:\\synthetic state\\Übung\""+(editor?"":" --no-browser"));
            Reject("RestartInfo","C:\\bad\" --injected",false);
            Phase="actual parent exit";
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
            Phase="READY/GO/EOF";
            foreach(string command in new[]{"", "GO wrong\n", "GO "+new string('a',48)+"\n"}) {
                var start=new ProcessStartInfo(Assembly.GetExecutingAssembly().Location,"handshake "+(string)Call("Quote",args[0])+" "+new string('a',48)) {
                    UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardOutput=true };
                using(var child=Process.Start(start)) {
                    Need(child.StandardOutput.ReadLine()=="READY "+new string('a',48));
                    child.StandardInput.Write(command); child.StandardInput.Close();
                    Need(child.WaitForExit(5000) && child.ExitCode==0);
                    Need(child.StandardOutput.ReadLine()==(command=="GO "+new string('a',48)+"\n"?"GO-accepted":"cancelled"));
                }
            }
            Phase="unbound input rejection";
            foreach(string input in new[]{"{}\n","{\"format\":\"foreign\"}\n",""}) {
                using(var child=Process.Start(new ProcessStartInfo(args[0]) {UseShellExecute=false,CreateNoWindow=true,
                        RedirectStandardInput=true,RedirectStandardOutput=true})) {
                    try { child.StandardInput.Write(input); child.StandardInput.Close(); }
                    catch(IOException) { } // Immediate refusal may close the pipe before the write.
                    Need(child.WaitForExit(5000)); Need(child.ExitCode==2 && child.StandardOutput.ReadToEnd()=="");
                }
            }
            Phase="authenticated restart";
            if(editor) {
                Call("RunningMarker"); Native(args);
            } else using(var runtime=Process.GetProcessById(Int32.Parse(args[7])))
                Need((bool)Call("Ready",runtime,new Dictionary<string,object> {
                    {"state",args[5]},{"commit",args[6]},{"instance","synthetic-old-instance"}}));
            Console.WriteLine(new JavaScriptSerializer().Serialize(new Dictionary<string,object> {
                {"app",args[8]},{"actual_helper_loaded",true},{"ready_go_and_eof_handshake",true},{"tampered_msi_rejected",true},{"derived_product_code",true},{"actual_msi_identity",true},{"wrong_msi_version_rejected",true},
                {"wrong_product_rejected",true},{"uninstalled_identity_rejected",true},{"invalid_versions_rejected",true},
                {"invalid_parent_handle_rejected",true},{"ready_child_did_not_release_wait",true},
                {"restart_environment_and_state_bound",true},
                {"actual_python_control_protocol_authenticated",!editor},{"native_ready_with_config_selection_pid_and_challenge",editor},{"native_wrong_key_commit_selection_rejected",editor},
                {"actual_process_exit_released_wait",true},{"unbound_helper_inputs_rejected",true},
                {"installer_executed",false},{"limits","Reflection into exact built helper; isolated child process. No installed-app or Windows-11 lifecycle claim."}}));
            return 0;
        } catch(Exception e) { Console.Error.WriteLine(Phase+": "+e.ToString()); return 2; }
    }
}
