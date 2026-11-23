extends RefCounted
## Build configuration, local account selection and per-account session files.
const Profile = preload("res://model/account_profile.gd")
const Recent = preload("res://model/recent_puzzle.gd")
const Protocol = preload("res://model/sync_protocol.gd")
const Registry = preload("res://model/content_registry.gd")
var server: String
var directory: String

func _init() -> void:
	server = str(ProjectSettings.get_setting("picross/sync/api_base","")).trim_suffix("/")
	var https := Protocol.matches(server,"\\Ahttps://[A-Za-z0-9.-]+(:[0-9]+)?(/[A-Za-z0-9_-]+)*\\z")
	var local := Protocol.matches(server,"\\Ahttp://(127\\.0\\.0\\.1|localhost|\\[::1\\])(:[0-9]+)?(/[A-Za-z0-9_-]+)*\\z")
	if not https and not (local and ProjectSettings.get_setting("picross/sync/loopback_test",false)): server = ""
	directory = Profile.ROOT.path_join(server.sha256_text())

func read(path: String) -> Dictionary:
	if not Recent.safe_file(path): return {}
	var bytes := FileAccess.get_file_as_bytes(path) if FileAccess.file_exists(path) else PackedByteArray()
	if bytes.is_empty() or not Recent.valid_utf8(bytes): return {}
	var raw := bytes.get_string_from_utf8()
	if not Registry.unique_keys(raw): return {}
	var data: Variant = JSON.parse_string(raw)
	return data if data is Dictionary else {}

func publish(path: String, data: Dictionary) -> bool:
	if server.is_empty() or not Recent.safe_file(path) or not Recent.safe_file(path+".tmp"): return false
	if DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK: return false
	var bytes := (JSON.stringify(data)+"\n").to_utf8_buffer()
	var file := FileAccess.open(path+".tmp",FileAccess.WRITE)
	if file == null: return false
	var written := file.store_buffer(bytes)
	file.flush()
	var error := file.get_error()
	file.close()
	if not written or error != OK or bytes != FileAccess.get_file_as_bytes(path+".tmp"): return false
	if not Recent.new(path)._replace(path+".tmp",FileAccess.file_exists(path)) or FileAccess.get_file_as_bytes(path) != bytes: return false
	if OS.has_feature("web"):
		var storage: JavaScriptObject = JavaScriptBridge.get_interface("window").picrossStorage
		var ticket := JSON.stringify([path,ResourceUID.id_to_text(ResourceUID.create_id())])
		if not storage.accountSync(ticket): return false
		var tree := Engine.get_main_loop() as SceneTree
		while true:
			await tree.process_frame
			var state: String = str(storage.accountResult(ticket))
			if state != "pending": return state == "saved"
	return true

func active() -> String:
	return str(read(directory.path_join("selected.json")).get("account",""))

func choose(account: String) -> bool:
	if not account.is_empty() and not Protocol.uuid(account): return false
	return await publish(directory.path_join("selected.json"),{"server":server,"account":account})

func session_path(account: String) -> String:
	return directory.path_join(account).path_join("session.json")

func credentials(account: String) -> Dictionary:
	if not Protocol.uuid(account): return {}
	var data := read(session_path(account))
	if data.size() != 7 or not data.has_all(["account_id","device_id","generation","username","token","expires_at","server"]): return {}
	if data.server != server or data.account_id != account or not Protocol.uuid(data.device_id) or not Protocol.uuid(data.generation): return {}
	if not Protocol.matches(data.username,"\\A[a-z0-9][a-z0-9_-]{2,31}\\z") or not data.token is String or not data.expires_at is String: return {}
	if data.token != "" and not Protocol.matches(data.token,"\\A[A-Za-z0-9_-]{43}\\z"): return {}
	return data

func accounts() -> Dictionary:
	var result := {}
	if server.is_empty() or not DirAccess.dir_exists_absolute(directory): return result
	for id: String in DirAccess.get_directories_at(directory):
		var data := credentials(id)
		if not data.is_empty(): result[data.username] = id
	return result
