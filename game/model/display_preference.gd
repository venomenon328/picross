extends RefCounted
## Display-only preference. Never opens puzzle slots or catalog preferences.
const PATH: String = "user://p1/display-preference.json"
const FORMAT: String = "picross-display-preference-v1"
const MODES: Array[String] = ["window", "borderless", "exclusive"]
const PRESETS: Array[String] = ["1280x720", "1366x768", "1600x900", "1920x1080", "1920x1200", "2560x1440", "2560x1600", "3840x2160"]
var path: String
var error: String = ""
var fail_write: bool = false
var fail_replace: bool = false

func _init(location: String = PATH) -> void:
	path = location

static func defaults() -> Dictionary:
	return {"mode": "window", "preset": "1920x1080"}

static func pixels(preset: String) -> Vector2i:
	var parts: PackedStringArray = preset.split("x")
	return Vector2i(int(parts[0]), int(parts[1]))

static func valid(value: Variant) -> bool:
	return value is Dictionary and value.size() == 3 and value.get("format") == FORMAT and value.get("mode") is String and value.get("preset") is String and value.mode in MODES and value.preset in PRESETS

static func decode(text: String) -> Dictionary:
	# Exactly three JSON string pairs. Godot additionally accepts trailing
	# commas/control characters; exclude these before its otherwise useful decoder.
	var token: String = r'"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"'
	var shape := RegEx.new()
	shape.compile("\\A\\s*\\{\\s*"+token+"\\s*:\\s*"+token+"(?:\\s*,\\s*"+token+"\\s*:\\s*"+token+"){2}\\s*\\}\\s*\\z")
	if shape.search(text) == null: return {}
	var parser := JSON.new()
	if parser.parse(text) != OK: return {}
	var value: Variant = parser.data
	# Three pairs and exactly three decoded keys also rejects escaped duplicates.
	if not valid(value): return {}
	return {"mode": value.mode, "preset": value.preset}

func load_selection() -> Dictionary:
	error = ""
	var selection: Dictionary = read(path)
	if not selection.is_empty(): return selection
	selection = read(path+".bak")
	if not selection.is_empty():
		error = "Vorherige Anzeige-Präferenz wiederhergestellt."
		return selection
	if not FileAccess.file_exists(path) and not FileAccess.file_exists(path+".bak"): return defaults()
	error = "Anzeige-Präferenz nicht lesbar. Sichere Starteinstellung wird verwendet."
	return defaults()

static func read(location: String) -> Dictionary:
	var file := FileAccess.open(location,FileAccess.READ)
	if file == null or file.get_length() > 1024: return {}
	return decode(file.get_as_text())

func save_selection(selection: Dictionary) -> bool:
	var value: Dictionary = selection.duplicate()
	value["format"] = FORMAT
	if not valid(value): return false
	var temporary: String = path + ".tmp"
	error = "Anzeige konnte nicht gespeichert werden. Die vorherige Einstellung bleibt erhalten."
	if fail_write or DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK: return false
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null: return false
	file.store_string(JSON.stringify(value) + "\n")
	file.flush()
	var result: Error = file.get_error()
	file.close()
	# Windows DirAccess.rename removes an existing destination before moving.
	# Never use that destructive overwrite: journal the valid primary first,
	# then publish to an absent path. A crash in the gap loads the valid backup.
	if result != OK or read(temporary) != selection:
		DirAccess.remove_absolute(temporary)
		return false
	var backup: String = path+".bak"
	var rotated: bool = false
	if not read(path).is_empty():
		if FileAccess.file_exists(backup) and DirAccess.remove_absolute(backup) != OK:
			DirAccess.remove_absolute(temporary)
			return false
		if DirAccess.rename_absolute(path,backup) != OK:
			DirAccess.remove_absolute(temporary)
			return false
		rotated = true
	elif FileAccess.file_exists(path):
		if DirAccess.remove_absolute(path) != OK:
			DirAccess.remove_absolute(temporary)
			return false
	if fail_replace or DirAccess.rename_absolute(temporary,path) != OK:
		if rotated: DirAccess.rename_absolute(backup,path)
		DirAccess.remove_absolute(temporary)
		return false
	error = ""
	return true
