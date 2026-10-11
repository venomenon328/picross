extends RefCounted
## Bundled, generated data only. No save input or runtime directory discovery.
const PATH: String = "res://data/registry.json"
static var cached: Array[Dictionary] = []

static func entries() -> Array[Dictionary]:
	if not cached.is_empty():
		return cached
	var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	if not raw is Dictionary or raw.get("format") != "picross-runtime-registry-v1" or not raw.get("entries") is Array:
		return []
	var seen: Dictionary = {}
	var loaded: Array[Dictionary] = []
	for item: Variant in raw.entries:
		if not item is Dictionary or item.size() != 6 or not item.get("visible") is bool:
			return []
		for field: String in ["id", "key", "save_slot", "definition", "reveal"]:
			if not item.get(field) is String or item[field].is_empty():
				return []
			var unique: String = field + ":" + str(item[field]).to_lower()
			if seen.has(unique):
				return []
			seen[unique] = true
		for field: String in ["key", "save_slot"]:
			for letter: String in str(item[field]):
				if not letter in "abcdefghijklmnopqrstuvwxyz0123456789_-":
					return []
		for field: String in ["definition", "reveal"]:
			if ".." in item[field] or "\\" in item[field] or ":" in item[field] or str(item[field]).begins_with("/"):
				return []
		if not str(item.definition).begins_with("data/") or not str(item.definition).ends_with(".json") or not str(item.reveal).begins_with("art/"):
			return []
		loaded.append(item)
	cached = loaded
	return cached

static func by_key(key: String) -> Dictionary:
	for entry: Dictionary in entries():
		if entry.key == key:
			return entry
	return {}

static func by_id(id: String) -> Dictionary:
	for entry: Dictionary in entries():
		if entry.id == id:
			return entry
	return {}

static func key_for_id(id: String) -> String:
	return str(by_id(id).get("key", ""))

static func catalog_ids() -> Array[String]:
	var result: Array[String] = []
	for entry: Dictionary in entries():
		if entry.visible:
			result.append(entry.key)
	return result
