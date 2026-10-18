extends RefCounted
## One local UI preference, independent of puzzle slots and their recovery.
const PATH: String = "user://p1/catalog-preference.json"
const FORMAT: String = "picross-catalog-preference-v1"
const CRITERIA: Array[String] = ["category", "size", "difficulty", "added"]
var path: String
var criterion: String = "category"
var direction: String = "asc"
var saved: String = ""
var error: String = ""
var fail_write: bool = false

func _init(location: String = PATH) -> void:
	path = location

static func valid(value: Variant) -> bool:
	return value is Dictionary and value.size() == 3 and value.get("format") == FORMAT and value.get("criterion") in CRITERIA and value.get("direction") in ["asc", "desc"]

func load_selection() -> void:
	criterion = "category"
	direction = "asc"
	saved = ""
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null or file.get_length() > 1024: return
	var text: String = file.get_as_text()
	var value: Variant = JSON.parse_string(text)
	# Exactly three keys, also when duplicate spellings use JSON escapes.
	var keys: RegEx = RegEx.new()
	keys.compile('"(?:[^"\\\\]|\\\\.)*"\\s*:')
	if not valid(value) or keys.search_all(text).size() != 3: return
	criterion = value.criterion
	direction = value.direction
	saved = criterion + "/" + direction

func save_selection() -> bool:
	var pair: String = criterion + "/" + direction
	if pair == saved and error.is_empty():
		if OS.has_feature("web"): JavaScriptBridge.eval("window.picrossStorage.preferenceRetry()", true)
		return true
	var temporary: String = path + ".tmp"
	if fail_write or DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK:
		error = "Sortierung konnte nicht gespeichert werden."
		return false
	var file: FileAccess = FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		error = "Sortierung konnte nicht gespeichert werden."
		return false
	file.store_string(JSON.stringify({"format": FORMAT, "criterion": criterion, "direction": direction}) + "\n")
	file.flush()
	var result: Error = file.get_error()
	file.close()
	if result != OK or DirAccess.rename_absolute(temporary, path) != OK:
		DirAccess.remove_absolute(temporary)
		error = "Sortierung konnte nicht gespeichert werden."
		return false
	error = ""
	saved = pair
	if OS.has_feature("web"): JavaScriptBridge.eval("window.picrossStorage.preferenceChanged()", true)
	return true
