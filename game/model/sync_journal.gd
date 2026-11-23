extends RefCounted
## Compare and publish one complete, checksummed journal image under a native writer lock.
const Recent = preload("res://model/recent_puzzle.gd")
const Registry = preload("res://model/content_registry.gd")
const FORMAT = "picross-local-sync/v1"
var path: String
var digest := ""
var locked := false

func _init(root: String) -> void:
	path = root.path_join("journal.json")

func acquire() -> bool:
	var lock_path := path + ".lock"
	if locked or not Recent.safe_file(path) or not Recent.safe_file(path + ".tmp"):
		return false
	locked = DirAccess.make_dir_absolute(lock_path) == OK
	return locked

func release() -> void:
	if locked:
		DirAccess.remove_absolute(path + ".lock")
		locked = false

func read_image() -> Dictionary:
	if not Recent.safe_file(path) or not FileAccess.file_exists(path):
		return {}
	var bytes := FileAccess.get_file_as_bytes(path)
	if not Recent.valid_utf8(bytes):
		return {}
	var raw := bytes.get_string_from_utf8()
	if not Registry.unique_keys(raw):
		return {}
	var record: Variant = JSON.parse_string(raw)
	if not record is Dictionary or record.size() != 3 or record.get("format") != FORMAT or not record.get("payload") is String:
		return {}
	var payload: String = record.payload
	if payload.sha256_text() != record.get("sha256") or not Registry.unique_keys(payload):
		return {}
	var state: Variant = JSON.parse_string(payload)
	if not state is Dictionary:
		return {}
	digest = raw.sha256_text()
	return state

func publish(state: Dictionary) -> bool:
	if not locked or not Recent.safe_file(path) or not Recent.safe_file(path + ".tmp"):
		return false
	var exists := FileAccess.file_exists(path)
	if exists != (digest != "") or (exists and FileAccess.get_sha256(path) != digest):
		return false
	var payload := JSON.stringify(state, "", true, true)
	var raw := JSON.stringify({"format":FORMAT, "payload":payload, "sha256":payload.sha256_text()}) + "\n"
	var temporary := path + ".tmp"
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		return false
	var bytes := raw.to_utf8_buffer()
	var written := file.store_buffer(bytes)
	file.flush()
	var error := file.get_error()
	file.close()
	if not written or error != OK or FileAccess.get_file_as_bytes(temporary) != bytes:
		return false
	if not Recent.new(path)._replace(temporary, exists) or FileAccess.get_file_as_bytes(path) != bytes:
		return false
	digest = raw.sha256_text()
	return true

## Native completion is issued only after the caller published and verified both files.
func confirm_local(ticket: Dictionary, callback: Callable) -> void:
	callback.call(ticket, true)
