extends Node
## One private pipe per Windows player. All calls run on the scene thread.

const START_MS := 10000
const REPLY_MS := 2000
const COMMAND := r"""
$ErrorActionPreference = 'Stop'
$owner = [Diagnostics.Process]::GetProcessById(%d)
$null = $owner.Handle
$gate = [Threading.Mutex]::new($false, 'Local\PicrossPublisher-%s')
function Enter-Gate {
    try { return $gate.WaitOne(2000) }
    catch [Threading.AbandonedMutexException] { return $true }
}
Add-Type -Namespace Picross -Name Publisher -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet=System.Runtime.InteropServices.CharSet.Unicode, ExactSpelling=true)]
public static extern bool MoveFileExW(string source, string target, uint flags);
'@
if (!(Enter-Gate)) { exit 1 }
$gate.ReleaseMutex()
[Console]::WriteLine('ready')
while ($null -ne ($line = [Console]::ReadLine())) {
    $id, $flags, $src, $dst = $line.Split(' ')
    $source = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($src))
    $target = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($dst))
    $ok = $false
    if (Enter-Gate) {
        try {
            if ($owner.HasExited) { break }
            $ok = [Picross.Publisher]::MoveFileExW($source, $target, [uint32]$flags)
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

func _start() -> void:
	var executable := OS.get_environment("SystemRoot").path_join("System32/WindowsPowerShell/v1.0/powershell.exe")
	var script := COMMAND % [OS.get_process_id(), OS.get_user_data_dir().to_lower().sha256_text()]
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
			if bytes.size() + count > 64: return ""
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

func replace(temporary: String, destination: String, overwrite: bool) -> bool:
	if not available or not OS.is_process_running(child.pid):
		_retire()
		set_process(true)
		return false
	sequence += 1
	# Give the worker a single-use source. Revoking it after an uncertain reply
	# prevents a late move from ever consuming a subsequent save's .tmp bytes.
	var candidate := temporary + "." + Crypto.new().generate_random_bytes(16).hex_encode()
	if FileAccess.file_exists(candidate) or DirAccess.rename_absolute(temporary, candidate) != OK: return false
	var source := Marshalls.utf8_to_base64(ProjectSettings.globalize_path(candidate))
	var target := Marshalls.utf8_to_base64(ProjectSettings.globalize_path(destination))
	var request := "%d %d %s %s\n" % [sequence, 9 if overwrite else 8, source, target]
	var pipe: FileAccess = child.stdio
	var reply := ""
	if pipe.store_buffer(request.to_ascii_buffer()):
		reply = _reply(REPLY_MS)
	if reply == "%d 1" % sequence: return true
	if FileAccess.file_exists(candidate) and not FileAccess.file_exists(temporary):
		DirAccess.rename_absolute(candidate, temporary)
	if reply != "%d 0" % sequence:
		_retire()
		set_process(true)
	return false
