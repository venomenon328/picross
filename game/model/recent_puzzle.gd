extends RefCounted
## Independent, bounded navigation metadata. Never a second save-slot format.
const Session = preload("res://model/session.gd")
const Registry = preload("res://model/content_registry.gd")
const PATH: String = "user://p1/recent-puzzle.json"
const FORMAT: String = "picross-recent-puzzle-v1"
static var windows_filesystem: DirAccess
var path: String
var record: Dictionary = {}
var desired: Dictionary = {}
var pending: bool = false
var error: String = ""
var fail_step: String = "" # Synthetic interruption probes only.

func _init(location: String = PATH) -> void:
	path = location.replace("\\","/")

static func decode(raw: PackedByteArray) -> Dictionary:
	if raw.is_empty() or raw.size() > 1024 or not valid_utf8(raw): return {}
	var text: String = raw.get_string_from_utf8()
	if text.to_utf8_buffer() != raw: return {}
	# A complete flat grammar rejects duplicates, nested values, trailing data,
	# fractional/exponent revisions before JSON parsing. Registry's key scanner
	# also rejects duplicate keys expressed through different JSON escapes.
	var string_token: String = '"(?:[^"\\\\\\x00-\\x1f]|\\\\.)*"'
	var pair: String = string_token+'\\s*:\\s*(?:'+string_token+'|[1-9][0-9]*)'
	var grammar := RegEx.new()
	grammar.compile('^\\s*\\{\\s*(?:'+pair+')\\s*,\\s*(?:'+pair+')\\s*,\\s*(?:'+pair+')\\s*\\}\\s*$')
	if grammar.search(text) == null or not Registry.unique_keys(text): return {}
	var value: Variant = JSON.parse_string(text)
	if not value is Dictionary or value.size() != 3 or value.get("format") != FORMAT: return {}
	if not value.get("id") is String or value.id.is_empty() or not value.get("revision") is float: return {}
	if value.revision <= 0 or value.revision > 9007199254740991: return {}
	return {"format":FORMAT,"id":value.id,"revision":int(value.revision)}

static func valid_utf8(raw: PackedByteArray) -> bool:
	# Validate before Godot's decoder so corrupt local bytes remain a quiet
	# absent marker, rather than emitting engine Unicode parsing errors.
	var i: int = 0
	while i < raw.size():
		var lead: int = raw[i]
		if lead < 128:
			i += 1
			continue
		var count: int = 1 if lead >= 194 and lead <= 223 else (2 if lead >= 224 and lead <= 239 else (3 if lead >= 240 and lead <= 244 else 0))
		if count == 0 or i+count >= raw.size(): return false
		for offset: int in range(1,count+1):
			if raw[i+offset] < 128 or raw[i+offset] > 191: return false
		var second: int = raw[i+1]
		if (lead == 224 and second < 160) or (lead == 237 and second >= 160) or (lead == 240 and second < 144) or (lead == 244 and second >= 144): return false
		i += count+1
	return true

static func read(location: String) -> Dictionary:
	if not safe_file(location): return {}
	var file := FileAccess.open(location,FileAccess.READ)
	if file == null or file.get_length() > 1024: return {}
	return decode(file.get_buffer(file.get_length()))

static func safe_file(location: String) -> bool:
	var absolute: String = ProjectSettings.globalize_path(location).replace("\\","/")
	if absolute != absolute.simplify_path(): return false
	var cursor: String = absolute
	if OS.get_name() == "Windows":
		# Absolute paths query fresh Windows attributes. Reuse the accessor,
		# never a link result, including for previously absent leaf files.
		if windows_filesystem == null: windows_filesystem = DirAccess.open(OS.get_user_data_dir())
		if windows_filesystem == null or windows_filesystem.dir_exists(absolute): return false
		while cursor != cursor.get_base_dir():
			if windows_filesystem.is_link(cursor): return false
			cursor = cursor.get_base_dir()
		return true
	if DirAccess.dir_exists_absolute(absolute): return false
	while cursor != cursor.get_base_dir():
		var directory := DirAccess.open(cursor.get_base_dir())
		if directory != null and directory.is_link(cursor.get_file()): return false
		cursor = cursor.get_base_dir()
	return true

func load_record() -> void:
	record = read(path)
	desired = record.duplicate()
	pending = false
	error = ""

static func started(item: Session) -> bool:
	return not item.completed and (not item.player.history.is_empty() or item.player.cells.any(func(cell: int) -> bool: return cell != -1))

func resolve(items: Dictionary, statuses: Dictionary) -> String:
	var id: String = record.get("id", "")
	if not items.has(id) or statuses.get(id,"error") not in ["loaded","recovered","backup_invalid"]: return ""
	var item: Session = items[id]
	if item.definition.revision != record.revision or not started(item): return ""
	return id

func edited(item: Session) -> bool:
	if item.completed: return clear_matching(str(item.definition.id))
	if not started(item): return true
	desired = {"format":FORMAT,"id":str(item.definition.id),"revision":int(item.definition.revision)}
	pending = true
	return retry()

func clear_matching(id: String) -> bool:
	# Completion/reset of a different puzzle cannot overwrite a failed newer edit.
	if desired.get("id","") == id:
		if record.get("id","") != id:
			# The failed candidate never became the marker. Retain the older one.
			desired = record.duplicate()
			pending = false
			error = ""
			return true
		desired = {}
		pending = true
	elif record.get("id","") != id: return true
	elif pending: return retry()
	else:
		desired = {}
		pending = true
	return retry()

func retry() -> bool:
	if not pending:
		web_retry()
		return true
	if path.get_file() != "recent-puzzle.json" or not safe_file(path) or not safe_file(path+".tmp"):
		return _failed()
	if desired == record and read(path) == record:
		pending = false
		error = ""
		web_retry()
		return true
	if desired.is_empty():
		if fail_step == "delete": return _failed()
		if OS.get_name() == "Windows":
			var expected := ""
			if FileAccess.file_exists(path):
				var bytes := FileAccess.get_file_as_bytes(path)
				if decode(bytes) != record: return _failed()
				var hashing := HashingContext.new()
				hashing.start(HashingContext.HASH_SHA256)
				hashing.update(bytes)
				expected = hashing.finish().hex_encode()
			var publisher := windows_publisher()
			if publisher == null or not publisher.clear(path, expected): return _failed()
		elif FileAccess.file_exists(path) and DirAccess.remove_absolute(path) != OK: return _failed()
	else:
		if fail_step == "open" or DirAccess.make_dir_recursive_absolute(path.get_base_dir()) != OK: return _failed()
		var temporary: String = path+".tmp"
		var file := FileAccess.open(temporary,FileAccess.WRITE)
		if file == null: return _failed()
		file.store_string(JSON.stringify(desired)+"\n")
		file.flush()
		var result: Error = file.get_error()
		file.close()
		if result != OK or fail_step == "after_temp" or read(temporary) != desired: return _failed()
		if fail_step == "replace" or not _replace(temporary): return _failed()
	record = desired.duplicate()
	pending = false
	error = ""
	if OS.has_feature("web"): JavaScriptBridge.eval("window.picrossStorage.recentChanged()",true)
	return true

func _failed() -> bool:
	error = "Fortsetzen-Merker nicht gespeichert. Erneut versuchen"
	return false

func _replace(temporary: String, replace_existing: bool = true) -> bool:
	if OS.get_name() != "Windows":
		if not replace_existing and FileAccess.file_exists(path): return false
		# POSIX rename and Emscripten MEMFS rename replace without a delete gap.
		return DirAccess.rename_absolute(temporary,path) == OK
	var publisher := windows_publisher()
	return publisher != null and publisher.replace(temporary, path, replace_existing)

static func windows_publisher() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null("WindowsPublisher")

static func web_retry() -> void:
	if OS.has_feature("web"): JavaScriptBridge.eval("window.picrossStorage.recentRetry()",true)

func message() -> String:
	if not error.is_empty(): return error
	if OS.has_feature("web"): return str(JavaScriptBridge.eval("window.picrossStorage.recentError || ''",true))
	return ""
