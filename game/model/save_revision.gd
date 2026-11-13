extends RefCounted
## PE-A3: bound, repeatable deletion of one positively identified older slot.
const Recent = preload("res://model/recent_puzzle.gd")
const Registry = preload("res://model/content_registry.gd")
const FORMAT: String = "picross-save-revision-reset-v1"
const SUFFIXES: Array[String] = [".json", ".bak", ".tmp"]

static func exact_keys(value: Dictionary, expected: Array) -> bool:
	return value.size() == expected.size() and expected.all(func(key: String) -> bool: return value.has(key))

static func recent_path(store: RefCounted) -> String:
	return Recent.PATH if store.test_root_override.is_empty() else store.root.path_join("recent-metadata/recent-puzzle.json")

static func marker_path(store: RefCounted, id: String, temporary: bool = false) -> String:
	return store.root.path_join(store.slot_for_key(id) + (".revision-reset.tmp" if temporary else ".revision-reset.json"))

static func pending(store: RefCounted, id: String) -> bool:
	for temporary: bool in [false,true]:
		var path: String = marker_path(store,id,temporary)
		if not Recent.safe_file(path) or FileAccess.file_exists(path): return true
	return false

static func hash_file(path: String) -> Variant:
	if not Recent.safe_file(path): return "unsafe"
	if not FileAccess.file_exists(path): return null
	var file := FileAccess.open(path,FileAccess.READ)
	if file == null: return "unreadable"
	var length: int = file.get_length()
	var remaining: int = length
	var hashing := HashingContext.new()
	hashing.start(HashingContext.HASH_SHA256)
	while remaining > 0:
		var raw: PackedByteArray = file.get_buffer(mini(remaining,1024*1024))
		if raw.is_empty() or not file.get_error() in [OK,ERR_FILE_EOF]:
			file.close()
			return "unreadable"
		hashing.update(raw)
		remaining -= raw.size()
	var ok: bool = file.get_length() == length
	file.close()
	return hashing.finish().hex_encode() if ok else "unreadable"

static func old_envelope(data: Variant, definition: Dictionary, store: RefCounted) -> bool:
	if not data is Dictionary or not exact_keys(data,["schema","definition_id","definition_revision","width","height","cells","history","cursor","undo_used","completed","view"]): return false
	if not store.integer(data.schema) or int(data.schema) != 1 or data.definition_id != definition.id: return false
	if not store.integer(data.definition_revision) or data.definition_revision <= 0 or data.definition_revision >= definition.revision: return false
	if not store.integer(data.width) or not store.integer(data.height) or data.width < 1 or data.width > 50 or data.height < 1 or data.height > 50: return false
	var count: int = int(data.width)*int(data.height)
	if not data.cells is Array or data.cells.size() != count or not data.history is Array: return false
	if not store.integer(data.cursor) or data.cursor < 0 or data.cursor > data.history.size() or not data.undo_used is bool or not data.completed is bool: return false
	if data.cursor < data.history.size() and not data.undo_used: return false
	var colors: Array[int] = [1,2,3,4,5,6,7,8]
	for cell: Variant in data.cells:
		if not store.valid_cell(cell,colors): return false
	var replay: Array = []
	replay.resize(count)
	replay.fill(-1)
	var at_cursor: Array = replay.duplicate()
	for index: int in data.history.size():
		var action: Variant = data.history[index]
		if not action is Array or action.is_empty() or action.size() > count: return false
		var seen: Dictionary = {}
		for change: Variant in action:
			if not change is Dictionary or not exact_keys(change,["index","before","after"]): return false
			if not store.integer(change.index) or change.index < 0 or change.index >= count or seen.has(int(change.index)): return false
			if not store.valid_cell(change.before,colors) or not store.valid_cell(change.after,colors) or change.before == change.after: return false
			if replay[int(change.index)] != change.before: return false
			seen[int(change.index)] = true
		for change: Dictionary in action: replay[int(change.index)] = int(change.after)
		if index+1 == int(data.cursor): at_cursor = replay.duplicate()
	for index: int in count:
		if int(at_cursor[index]) != int(data.cells[index]): return false
	var view: Variant = data.view
	if not view is Dictionary or not exact_keys(view,["center","zoom","overview","active_color","tool","row_clue_reads","column_clue_reads"]): return false
	if not view.center is Array or view.center.size() != 2: return false
	if not store.number(view.center[0]) or not store.number(view.center[1]) or view.center[0] < 0 or view.center[0] > data.width or view.center[1] < 0 or view.center[1] > data.height: return false
	if not view.overview is bool or not store.integer(view.zoom) or not int(view.zoom) in store.ZOOMS: return false
	if not store.integer(view.active_color) or not int(view.active_color) in colors or not view.tool is String or not view.tool in ["fill","erase","hand"]: return false
	for axis: String in ["row","column"]:
		var reads: Variant = view[axis+"_clue_reads"]
		if not reads is Array or reads.size() != int(data.height if axis == "row" else data.width): return false
		for read: Variant in reads:
			if not read is Dictionary or not read.get("anchor") is String: return false
			if read.anchor in ["grid_end","outer_start"]:
				if not exact_keys(read,["anchor"]): return false
			elif read.anchor == "middle":
				if not exact_keys(read,["anchor","start","end"]) or not store.integer(read.start) or not store.integer(read.end) or read.start <= 0 or read.end <= read.start or read.end > 50: return false
			else: return false
	return true

static func decode_marker(raw: PackedByteArray, definition: Dictionary, store: RefCounted) -> Dictionary:
	if raw.is_empty() or raw.size() > 4096 or not Recent.valid_utf8(raw): return {}
	var text: String = raw.get_string_from_utf8()
	if not Registry.unique_keys(text): return {}
	var value: Variant = JSON.parse_string(text)
	if not value is Dictionary or not exact_keys(value,["format","id","revision","files","recent"]): return {}
	if value.format != FORMAT or value.id != definition.id or not store.integer(value.revision) or value.revision != definition.revision: return {}
	if not value.files is Dictionary or not exact_keys(value.files,SUFFIXES): return {}
	if value.files.values().all(func(checksum: Variant) -> bool: return checksum == null): return {}
	for checksum: Variant in value.files.values()+[value.recent]:
		if checksum == null: continue
		if not checksum is String or checksum.length() != 64 or not checksum.is_valid_hex_number(): return {}
	value.revision = int(value.revision)
	return value

static func read_marker(path: String, definition: Dictionary, store: RefCounted) -> Dictionary:
	if not Recent.safe_file(path): return {}
	var file := FileAccess.open(path,FileAccess.READ)
	if file == null or file.get_length() > 4096: return {}
	var raw: PackedByteArray = file.get_buffer(file.get_length())
	file.close()
	return decode_marker(raw,definition,store)

static func guard(store: RefCounted, id: String, value: Dictionary, definition: Dictionary) -> bool:
	for suffix: String in SUFFIXES:
		var actual: Variant = hash_file(store.path_for(id,suffix))
		if actual != null and actual != value.files[suffix]: return false
		if actual != null and store._parse(store.path_for(id,suffix),definition).status != "older": return false
	var recent_hash: Variant = hash_file(recent_path(store))
	# A concurrently replaced foreign merker is preserved, never removed below.
	return recent_hash == null or recent_hash is String and recent_hash.length() == 64

static func reset(store: RefCounted, definition: Dictionary) -> String:
	var id: String = store.key_for_definition(str(definition.id))
	var marker: String = marker_path(store,id)
	var temporary: String = marker_path(store,id,true)
	if not Recent.safe_file(marker) or not Recent.safe_file(temporary): return "Unsicherer Revisionsmarker."
	var value: Dictionary = {}
	if FileAccess.file_exists(marker):
		value = read_marker(marker,definition,store)
		if value.is_empty(): return "Revisionsmarker ungültig; Daten bleiben erhalten."
	else:
		var files: Dictionary = {}
		var found: bool = false
		for suffix: String in SUFFIXES:
			var path: String = store.path_for(id,suffix)
			files[suffix] = hash_file(path)
			if files[suffix] != null:
				if store._parse(path,definition).status != "older": return "Revisionsreset: fremde oder ungültige Slotdaten."
				found = true
		if not found: return "Revisionsreset ohne ältere Slotdaten."
		var recent: Dictionary = Recent.read(recent_path(store))
		value = {"format":FORMAT,"id":str(definition.id),"revision":int(definition.revision),"files":files,
			"recent":hash_file(recent_path(store)) if recent.get("id","") == definition.id else null}
		var raw: PackedByteArray = (JSON.stringify(value)+"\n").to_utf8_buffer()
		if decode_marker(raw,definition,store) != value: return "Revisionsreset: Quellen nicht vollständig lesbar."
		if FileAccess.file_exists(temporary):
			if read_marker(temporary,definition,store) != value: return "Fremder Revisionsmarker-Temp bleibt erhalten."
		else:
			var file := FileAccess.open(temporary,FileAccess.WRITE)
			if file == null: return "Revisionsmarker nicht schreibbar."
			file.store_buffer(raw)
			file.flush()
			var write_error: Error = file.get_error()
			file.close()
			if write_error != OK or read_marker(temporary,definition,store) != value: return "Revisionsmarker nicht vollständig."
		if store.fail_step == "revision_before_marker": return "Testabbruch vor Revisionsmarker."
		if not guard(store,id,value,definition) or FileAccess.file_exists(marker): return "Revisionsreset: Quellenkonflikt."
		if not Recent.new(marker)._replace(temporary,false): return "Revisionsmarker nicht publizierbar."
	if store.fail_step == "revision_after_marker": return "Testabbruch nach Revisionsmarker."
	if FileAccess.file_exists(temporary): return "Revisionsreset: unerwarteter Marker-Temp."
	for suffix: String in SUFFIXES:
		if read_marker(marker,definition,store) != value or not guard(store,id,value,definition): return "Revisionsreset: fremde Bytes bleiben erhalten."
		var path: String = store.path_for(id,suffix)
		if FileAccess.file_exists(path) and DirAccess.remove_absolute(store._absolute(path)) != OK: return "Alter Spielstand nicht entfernbar."
		if store.fail_step == "revision_after"+suffix: return "Testabbruch während Revisionsreset."
	if read_marker(marker,definition,store) != value or not guard(store,id,value,definition): return "Revisionsreset: Abschlusskonflikt."
	var recent_location: String = recent_path(store)
	var recent_value: Dictionary = Recent.read(recent_location)
	if value.recent != null and hash_file(recent_location) == value.recent and recent_value.get("id","") == definition.id and recent_value.get("revision",definition.revision) < definition.revision:
		if DirAccess.remove_absolute(store._absolute(recent_location)) != OK: return "Alter Fortsetzen-Merker nicht entfernbar."
	if store.fail_step == "revision_before_finish": return "Testabbruch vor Revisionsabschluss."
	if read_marker(marker,definition,store) != value or not guard(store,id,value,definition): return "Revisionsreset: Abschlusskonflikt."
	if DirAccess.remove_absolute(store._absolute(marker)) != OK: return "Revisionsmarker nicht abschließbar."
	return ""
