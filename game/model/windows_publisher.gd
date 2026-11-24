extends Node
## One private pipe per Windows player. All calls run on the scene thread.

const START_MS := 10000
const REPLY_MS := 2000
const COMMAND := r"""
$ErrorActionPreference = 'Stop'
$owner = [Diagnostics.Process]::GetProcessById(%d)
$null = $owner.Handle
$gate = [Threading.Mutex]::new($false, 'Global\PicrossPublisher-%s')
function Enter-Gate {
    try { return $gate.WaitOne(2000) }
    catch [Threading.AbandonedMutexException] { return $true }
}
Add-Type -Namespace Picross -Name Publisher -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet=System.Runtime.InteropServices.CharSet.Unicode, ExactSpelling=true)]
public static extern bool MoveFileExW(string source, string target, uint flags);
[System.Runtime.InteropServices.DllImport("kernel32.dll")]
private static extern IntPtr GetStdHandle(int handle);
[System.Runtime.InteropServices.DllImport("kernel32.dll")]
private static extern bool PeekNamedPipe(IntPtr pipe, IntPtr buffer, uint size, IntPtr read, IntPtr available, IntPtr left);
public static bool ClientConnected() {
    return PeekNamedPipe(GetStdHandle(-10), IntPtr.Zero, 0, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
}

[System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]
private struct FileInfo {
    public uint Attributes, CreationLow, CreationHigh, AccessLow, AccessHigh, WriteLow, WriteHigh;
    public uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
}
[System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet=System.Runtime.InteropServices.CharSet.Unicode, ExactSpelling=true)]
private static extern Microsoft.Win32.SafeHandles.SafeFileHandle CreateFileW(
    string name, uint access, uint share, IntPtr security, uint disposition, uint flags, IntPtr template);
[System.Runtime.InteropServices.DllImport("kernel32.dll")]
private static extern bool GetFileInformationByHandle(Microsoft.Win32.SafeHandles.SafeFileHandle handle, out FileInfo info);
public static string Digest(System.IO.FileStream held, string path) {
    // Reopen for attributes only. The data comes from the independently opened
    // handle, which follows the same file across an atomic rename.
    using (var entry = CreateFileW(path, 0, 7, IntPtr.Zero, 3, 0x00200000, IntPtr.Zero)) {
        FileInfo file, name;
        if (entry.IsInvalid || !GetFileInformationByHandle(entry, out name) ||
            !GetFileInformationByHandle(held.SafeFileHandle, out file) ||
            (name.Attributes & 0x410) != 0 || name.Volume != file.Volume ||
            name.IndexHigh != file.IndexHigh || name.IndexLow != file.IndexLow) return "-";
        held.Position = 0;
        using (var hash = System.Security.Cryptography.SHA256.Create()) {
            return BitConverter.ToString(hash.ComputeHash(held)).Replace("-", "").ToLowerInvariant();
        }
    }
}
'@
if (!(Enter-Gate)) { exit 1 }
$gate.ReleaseMutex()
[Console]::WriteLine('ready')
$held = $null
while ($null -ne ($line = [Console]::ReadLine())) {
    $id, $flags, $src, $dst, $expected = $line.Split(' ')
    $source = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($src))
    $target = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($dst))
    if ($flags -eq 'hold') {
        if ($held) { $held.Dispose(); $held = $null }
        try {
            $held = [IO.FileStream]::new($source, [IO.FileMode]::Open, [IO.FileAccess]::Read,
                ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete), 1)
        } catch [IO.IOException] {} catch [UnauthorizedAccessException] {}
        [Console]::WriteLine($id + ' ' + [int]($null -ne $held))
        continue
    }
    if ($flags -eq 'hash' -or $flags -eq 'finish') {
        $digest = '-'
        if ($held) {
            try { $digest = [Picross.Publisher]::Digest($held, $source) }
            catch [IO.IOException] {} catch [UnauthorizedAccessException] {}
            if ($flags -eq 'finish') { $held.Dispose(); $held = $null }
        }
        [Console]::WriteLine($id + ' ' + $digest)
        continue
    }
    if ($flags -eq 'drop') {
        if ($held) { $held.Dispose(); $held = $null }
        [Console]::WriteLine($id + ' 1')
        continue
    }
    $ok = $false
    if (Enter-Gate) {
        try {
            if ($owner.HasExited -or ![Picross.Publisher]::ClientConnected()) { break }
            if ($flags -eq 'fence') { $ok = $true }
            elseif ($flags -eq 'clear') {
                try {
                    if ([IO.File]::Exists($target)) {
                        $current = [IO.File]::ReadAllBytes($target)
                        $hash = [Security.Cryptography.SHA256]::Create()
                        try { $actual = [BitConverter]::ToString($hash.ComputeHash($current)).Replace('-', '').ToLowerInvariant() }
                        finally { $hash.Dispose() }
                        if ($actual -eq $source -and [Picross.Publisher]::ClientConnected()) { [IO.File]::Delete($target); $ok = $true }
                    } else { $ok = $true }
                } catch [IO.IOException] {} catch [UnauthorizedAccessException] {}
            } elseif ($expected) {
                try {
                    if ($held -and [Picross.Publisher]::Digest($held, $source) -eq $expected -and [Picross.Publisher]::ClientConnected()) {
                        $ok = [Picross.Publisher]::MoveFileExW($source, $target, [uint32]$flags) -and
                            [Picross.Publisher]::Digest($held, $target) -eq $expected
                    }
                } catch [IO.IOException] {} catch [UnauthorizedAccessException] {}
                finally { if ($held) { $held.Dispose(); $held = $null } }
            } else { $ok = [Picross.Publisher]::MoveFileExW($source, $target, [uint32]$flags) }
        } finally { $gate.ReleaseMutex() }
    }
    [Console]::WriteLine($id + ' ' + [int]$ok)
}
"""

var child := {}
var available := false
var sequence := 0
var retire_deadline := 0

func _ready() -> void:
	set_process(false)
	if OS.get_name() == "Windows":
		_start()

func _start(worker: String = COMMAND) -> void:
	var executable := OS.get_environment("SystemRoot").path_join("System32/WindowsPowerShell/v1.0/powershell.exe")
	var script := worker % [OS.get_process_id(), OS.get_user_data_dir().to_lower().sha256_text()]
	var command := Marshalls.raw_to_base64(script.to_utf16_buffer())
	child = OS.execute_with_pipe(executable, ["-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand", command], false)
	available = not child.is_empty() and _reply(START_MS) == "ready"
	if not available: _retire()

func _reply(timeout_ms: int) -> String:
	var deadline := Time.get_ticks_msec() + timeout_ms
	var pipe: FileAccess = child.stdio
	var bytes := PackedByteArray()
	while Time.get_ticks_msec() < deadline and OS.is_process_running(child.pid):
		var count := pipe.get_length()
		if count > 0:
			if bytes.size() + count > 128: return ""
			var chunk := pipe.get_buffer(count)
			if chunk.size() != count: return ""
			bytes.append_array(chunk)
			if bytes[-1] == 10: return bytes.get_string_from_ascii().strip_edges()
		else:
			OS.delay_usec(250)
	return ""

func _retire() -> void:
	available = false
	if not child.is_empty() and child.stdio != null:
		child.stdio.close()
		child.stderr.close()
		child.stdio = null
		child.stderr = null
		retire_deadline = Time.get_ticks_msec() + REPLY_MS

func _process(_delta: float) -> void:
	# Closing stdin makes the old worker exit after its only outstanding move.
	# Observe that exit before admitting any request on a replacement pipe.
	if not child.is_empty() and OS.is_process_running(child.pid):
		if Time.get_ticks_msec() < retire_deadline: return
		# A suspended worker cannot observe stdin EOF. Terminate our child.
		# Its replacement also crosses the kernel mutex before advertising readiness.
		if OS.kill(child.pid) != OK: return
	set_process(false)
	_start()

func _exit_tree() -> void:
	_retire()
	if not child.is_empty() and OS.is_process_running(child.pid):
		OS.kill(child.pid)

func replace(temporary: String, destination: String, overwrite: bool, expected: String = "") -> bool:
	if not available: return false
	# Give the worker a single-use source. Revoking it after an uncertain reply
	# prevents a late move from ever consuming a subsequent save's .tmp bytes.
	var candidate := temporary + "." + Crypto.new().generate_random_bytes(16).hex_encode()
	if FileAccess.file_exists(candidate) or DirAccess.rename_absolute(temporary, candidate) != OK: return false
	var reply := _request("9" if overwrite else "8", _absolute(candidate), _absolute(destination), expected)
	if reply == "1": return true
	if FileAccess.file_exists(candidate) and not FileAccess.file_exists(temporary):
		DirAccess.rename_absolute(candidate, temporary)
	return false

func fence() -> bool:
	return _request("fence") == "1"

func clear(destination: String, expected: String) -> bool:
	return _request("clear", expected, _absolute(destination)) == "1"

func hold(path: String) -> bool:
	return _request("hold", _absolute(path)) == "1"

func digest(path: String, finish: bool = false) -> String:
	return _request("finish" if finish else "hash", _absolute(path))

func drop() -> void:
	_request("drop")

func _absolute(path: String) -> String:
	return ProjectSettings.globalize_path(path).replace("/", "\\")

func _request(mode: String, source: String = "", target: String = "", expected: String = "") -> String:
	if not available:
		set_process(true)
		return ""
	sequence += 1
	var request := "%d %s %s %s %s\n" % [sequence, mode, Marshalls.utf8_to_base64(source), Marshalls.utf8_to_base64(target), expected]
	var pipe: FileAccess = child.stdio
	var reply := ""
	if pipe.store_buffer(request.to_ascii_buffer()):
		reply = _reply(REPLY_MS)
	var prefix := "%d " % sequence
	if reply.begins_with(prefix): return reply.trim_prefix(prefix)
	# Close the OS pipe before returning. Under the shared mutex the child
	# either observes EOF before mutating, or finishes before another writer.
	_retire()
	set_process(true)
	return ""
