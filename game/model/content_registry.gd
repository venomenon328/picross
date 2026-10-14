extends RefCounted
## Bundled, generated data only. No save input or runtime directory discovery.
const PATH: String = "res://data/registry.json"
static var cached: Dictionary = {}
static var load_error: String = ""

static func valid_category_id(value: Variant) -> bool:
	if not value is String or value.length() < 1 or value.length() > 64:
		return false
	if not value[0] in "abcdefghijklmnopqrstuvwxyz":
		return false
	for letter: String in value:
		if not letter in "abcdefghijklmnopqrstuvwxyz0123456789-":
			return false
	return true

static func validate(raw: Variant) -> String:
	if not raw is Dictionary or raw.size() != 3 or raw.get("format") != "picross-runtime-registry-v2" or not raw.get("entries") is Array or not raw.get("categories") is Array:
		return "Unsupported runtime registry format"
	if raw.categories.size() > 256 or raw.entries.size() > 10000:
		return "Registry count limit exceeded"
	var category_ids: Dictionary = {}
	var previous_order: int = 0
	for category: Variant in raw.categories:
		if not category is Dictionary or category.size() != 3 or not valid_category_id(category.get("id")):
			return "Invalid category ID/fields"
		if category_ids.has(category.id):
			return "Duplicate category ID"
		category_ids[category.id] = true
		var label: Variant = category.get("name")
		if not label is String or label.length() < 1 or label.length() > 128 or label != label.strip_edges():
			return "Invalid category name"
		for index: int in range(label.length()):
			var code: int = label.unicode_at(index)
			if code < 32 or (code >= 127 and code <= 159):
				return "Invalid category name"
		var order: Variant = category.get("order")
		if not (order is int or order is float) or not is_finite(float(order)) or float(order) != floor(float(order)) or order <= previous_order or order > 10000:
			return "Category order must be unique, ascending and within 1..10000"
		previous_order = int(order)
	var seen: Dictionary = {}
	for item: Variant in raw.entries:
		if not item is Dictionary or item.size() != 7 or not item.get("visible") is bool or not item.has("category_id"):
			return "Invalid registry entry fields"
		for field: String in ["id", "key", "save_slot", "definition", "reveal"]:
			if not item.get(field) is String or item[field].is_empty():
				return "Invalid registry entry " + field
			var unique: String = field + ":" + str(item[field]).to_lower()
			if seen.has(unique):
				return "Duplicate registry " + field
			seen[unique] = true
		for field: String in ["key", "save_slot"]:
			for letter: String in str(item[field]):
				if not letter in "abcdefghijklmnopqrstuvwxyz0123456789_-":
					return "Invalid registry key/slot"
		for field: String in ["definition", "reveal"]:
			if ".." in item[field] or "\\" in item[field] or ":" in item[field] or str(item[field]).begins_with("/"):
				return "Invalid registry resource path"
		if not str(item.definition).begins_with("data/") or not str(item.definition).ends_with(".json") or not str(item.reveal).begins_with("art/"):
			return "Invalid registry resource type"
		if not valid_category_id(item.category_id) or not category_ids.has(item.category_id):
			return "Missing or unknown category for " + str(item.id)
	return ""

static func _load() -> Dictionary:
	if not cached.is_empty():
		return cached
	var file: FileAccess = FileAccess.open(PATH, FileAccess.READ)
	if file == null or file.get_length() > 8388608:
		load_error = "Missing or oversized runtime registry"
		return {}
	var raw: Variant = JSON.parse_string(file.get_as_text())
	load_error = validate(raw)
	if not load_error.is_empty():
		return {}
	cached = raw
	return cached

static func entries() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for item: Dictionary in _load().get("entries", []):
		result.append(item.duplicate(true))
	return result

static func categories() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for item: Dictionary in _load().get("categories", []):
		result.append(item.duplicate(true))
	return result

static func by_key(key: String) -> Dictionary:
	for entry: Dictionary in _load().get("entries", []):
		if entry.key == key:
			return entry.duplicate(true)
	return {}

static func by_id(id: String) -> Dictionary:
	for entry: Dictionary in _load().get("entries", []):
		if entry.id == id:
			return entry.duplicate(true)
	return {}

static func ordinal(id: String) -> int:
	var index: int = 0
	for entry: Dictionary in _load().get("entries", []):
		index += 1
		if entry.id == id: return index
	return 0

static func key_for_id(id: String) -> String:
	return str(by_id(id).get("key", ""))

static func catalog_ids() -> Array[String]:
	var result: Array[String] = []
	for entry: Dictionary in entries():
		if entry.visible:
			result.append(entry.key)
	return result
