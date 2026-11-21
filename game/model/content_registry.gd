extends RefCounted
## Bundled, generated data only. No save input or runtime directory discovery.
const PATH: String = "res://data/registry.json"
const CATALOG_FORMAT := "picross-runtime-registry-v9"
const CAPABILITY_PATH: String = "res://data/background-capability.json"
const Difficulty = preload("res://model/catalog_difficulty.gd")
static var cached: Dictionary = {}
static var load_error: String = ""
const BACKGROUND_PROFILES: Array = ["picross-background-png2304-v1", "picross-background-png2304x768-v1"]
static var background_profiles: Array = ["picross-background-png2304-v1"]
static var indexed_cache: Dictionary = {}
static var indexed_count: int = -1
static var id_positions: Dictionary = {}
static var key_positions: Dictionary = {}
const LEGACY_BACKGROUND: Dictionary = {"status":"legacy", "image_revision":null, "asset":null}

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
	if not raw is Dictionary or raw.size() != 3 or not raw.get("format") in ["picross-runtime-registry-v2", "picross-runtime-registry-v3", "picross-runtime-registry-v4", "picross-runtime-registry-v5", "picross-runtime-registry-v6", "picross-runtime-registry-v7", "picross-runtime-registry-v8", CATALOG_FORMAT] or not raw.get("entries") is Array or not raw.get("categories") is Array:
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
	var current: bool = raw.format != "picross-runtime-registry-v2"
	var catalog_images: bool = raw.format == CATALOG_FORMAT
	var image_preferences: bool = catalog_images or raw.format == "picross-runtime-registry-v8"
	var named: bool = image_preferences or raw.format == "picross-runtime-registry-v7"
	var backgrounds: bool = named or raw.format == "picross-runtime-registry-v6"
	var dated: bool = backgrounds or raw.format in ["picross-runtime-registry-v4", "picross-runtime-registry-v5"]
	# V8 retains the v7 fields and v5 difficulty; only v8 adds standard.
	var version: int = 5 if backgrounds or raw.format == "picross-runtime-registry-v5" else 4
	for item: Variant in raw.entries:
		if not item is Dictionary or item.size() != (12 if catalog_images else 11 if named else 10 if backgrounds else 9 if dated else 8 if current else 7) or not item.get("visible") is bool or not item.has("category_id"):
			return "Invalid registry entry fields"
		if named and not valid_name(item.get("name")):
			return "Invalid current puzzle name"
		if backgrounds and not valid_background(item, image_preferences):
			return "Invalid catalog background"
		if dated and (not item.has("added_at") or not valid_added(item.added_at)):
			return "Invalid catalog added timestamp"
		if current and (not item.has("difficulty") or not Difficulty.valid(item.difficulty, version)):
			return "Invalid catalog difficulty"
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
		if image_preferences and not (str(item.reveal).ends_with(".png") or str(item.reveal).ends_with(".svg")):
			return "Invalid current reveal type"
		if catalog_images and not valid_catalog_reveal(item):
			return "Invalid catalog reveal profile or resource"
		if not valid_category_id(item.category_id) or not category_ids.has(item.category_id):
			return "Missing or unknown category for " + str(item.id)
	return ""

static func valid_name(value: Variant) -> bool:
	if not value is String or value.length() < 1 or value.length() > 128:
		return false
	# Match Python's string.strip() boundary, including non-ASCII whitespace.
	for index: int in range(value.length()):
		var point: int = value.unicode_at(index)
		if not ((point >= 9 and point <= 13) or (point >= 28 and point <= 32) or point in [133, 160, 5760, 8232, 8233, 8239, 8287, 12288] or (point >= 8192 and point <= 8202)):
			return true
	return false

static func validate_capability(registry: Dictionary, value: Variant, present: bool) -> String:
	# V7/v8 always have a background field, even for a category-only target.
	# The capability continues to certify the unchanged v6 background contract.
	var enabled: bool = false
	if present:
		if capability_profiles(value).is_empty():
			return "Invalid background capability"
		enabled = value.enabled
	for entry: Dictionary in registry.entries:
		if entry.background.status in ["selected", "none"] and not enabled:
			return "Background catalog requires enabled compatible capability"
	return ""

static func capability_profiles(value: Variant) -> Array:
	if not value is Dictionary or value.size() != 4 or not value.get("enabled") is bool: return []
	if value.get("format") == "picross-runtime-background-capability-v1":
		if value.get("runtime_format") == "picross-runtime-registry-v6" and value.get("profile_id") == BACKGROUND_PROFILES[0]:
			return [BACKGROUND_PROFILES[0]]
	elif value.get("format") == "picross-runtime-background-capability-v2":
		if value.get("runtime_format") == "picross-runtime-registry-v8" and value.get("profile_ids") == BACKGROUND_PROFILES:
			return BACKGROUND_PROFILES.duplicate()
	return []

static func texture_profile(size: Vector2i) -> String:
	if size == Vector2i(2304, 576): return BACKGROUND_PROFILES[0]
	if size == Vector2i(2304, 768): return BACKGROUND_PROFILES[1]
	return ""

static func bounded_integer(value: Variant, minimum: int, maximum: int) -> bool:
	# JSON numbers are floats in Godot. Booleans, fractions and non-finite values
	# must not be accepted as integer revisions or byte counts.
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value)) and value >= minimum and value <= maximum

static func valid_sha256(value: Variant) -> bool:
	if not value is String or value.length() != 64: return false
	for digit: String in value:
		if not digit in "0123456789abcdef": return false
	return true

static func valid_catalog_reveal(item: Dictionary) -> bool:
	var catalog: Variant = item.get("catalog_reveal")
	if not catalog is Dictionary or catalog.size() != 4 or not valid_sha256(catalog.get("source_sha256")):
		return false
	var vector: bool = str(item.reveal).ends_with(".svg")
	if str(item.reveal).get_base_dir() != "art/content": return false
	for key: String in ["source_width", "source_height"]:
		var axis: Variant = catalog.get(key)
		if not (axis is float or axis is int) or not is_finite(axis) or axis <= 0 or axis > 8192:
			return false
		if not vector and not bounded_integer(axis, 1, 8192): return false
	var w: float = catalog.source_width
	var h: float = catalog.source_height
	if w * h > 8000000 or not catalog.get("profiles") is Array or catalog.profiles.size() != 2: return false
	if not ResourceLoader.exists("res://" + str(item.reveal), "Texture2D"): return false
	for index: int in range(2):
		var label := "ui100" if index == 0 else "ui125"
		var pw := 264 if index == 0 else 329
		var ph := 112 if index == 0 else 140
		var row: Variant = catalog.profiles[index]
		if not row is Dictionary or row.size() != 4 or row.get("profile") != "catalog-" + label + "-v1": return false
		var expected_width: int = mini(pw, maxi(1, ceili(ph * w / h)))
		var expected_height: int = mini(ph, maxi(1, ceili(pw * h / w)))
		if not vector:
			expected_width = mini(int(w), expected_width)
			expected_height = mini(int(h), expected_height)
		if not bounded_integer(row.get("width"), expected_width, expected_width) or not bounded_integer(row.get("height"), expected_height, expected_height): return false
		var asset: Variant = row.get("asset")
		if not asset is Dictionary or asset.size() != 3 or not valid_sha256(asset.get("sha256")) or not bounded_integer(asset.get("bytes"), 1, 262144): return false
		var path: String = "art/catalog/" + str(item.id) + "-" + label + ".png"
		if asset.get("file") != path or not ResourceLoader.exists("res://" + path, "Texture2D"): return false
	return true

static func valid_background(item: Dictionary, allow_standard: bool = false) -> bool:
	var identifier: Variant = item.get("id")
	if not identifier is String or identifier.length() < 4 or identifier.length() > 63 or not identifier.begins_with("pz-") or not identifier[3] in "abcdefghijklmnopqrstuvwxyz0123456789":
		return false
	for letter: String in identifier.substr(3):
		if not letter in "abcdefghijklmnopqrstuvwxyz0123456789-": return false
	var value: Variant = item.get("background")
	if not value is Dictionary or value.size() != 3 or not value.get("status") is String or not value.has("image_revision") or not value.has("asset"):
		return false
	if value.status == "legacy":
		return value.image_revision == null and value.asset == null
	if allow_standard and value.status == "standard":
		return bounded_integer(value.image_revision, 1, 1000000) and value.asset == null
	if not value.status in ["none", "selected"] or not bounded_integer(value.image_revision, 1, 1000000):
		return false
	if value.status == "none": return value.asset == null
	var asset: Variant = value.asset
	if not asset is Dictionary or asset.size() != 3 or not asset.get("file") is String or asset.file != "art/backgrounds/" + identifier + ".png" or not bounded_integer(asset.get("bytes"), 0, 67108864):
		return false
	var digest: Variant = asset.get("sha256")
	if not digest is String or digest.length() != 64: return false
	for letter: String in digest:
		if not letter in "0123456789abcdef": return false
	return true

static func background(entry: Dictionary) -> Dictionary:
	# Only old entries lacking the field are legacy. A declared invalid value
	# is never silently converted into a deliberate none/legacy state.
	var value: Variant = entry.get("background", LEGACY_BACKGROUND)
	return value.duplicate(true) if value is Dictionary else {}

static func valid_added(value: Variant) -> bool:
	if value == null: return true
	if not value is String or value.length() != 20: return false
	var pattern: RegEx = RegEx.new()
	pattern.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
	if pattern.search(value) == null: return false
	var year: int = int(value.substr(0, 4))
	var month: int = int(value.substr(5, 2))
	var day: int = int(value.substr(8, 2))
	if year < 1 or month < 1 or month > 12: return false
	var days: Array[int] = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	return day >= 1 and day <= days[month - 1] and int(value.substr(11, 2)) < 24 and int(value.substr(14, 2)) < 60 and int(value.substr(17, 2)) < 60

static func _load() -> Dictionary:
	if not cached.is_empty():
		return cached
	var file: FileAccess = FileAccess.open(PATH, FileAccess.READ)
	if file == null or file.get_length() > 16777216:
		load_error = "Missing or oversized runtime registry"
		return {}
	var text: String = file.get_as_text()
	var raw: Variant = JSON.parse_string(text)
	if not unique_keys(text):
		load_error = "Duplicate runtime registry JSON key"
		return {}
	if file.get_length() > 8388608 and (not raw is Dictionary or raw.get("format") != CATALOG_FORMAT):
		load_error = "Oversized legacy registry"
		return {}
	load_error = validate(raw)
	if not load_error.is_empty():
		return {}
	if raw.format in ["picross-runtime-registry-v7", "picross-runtime-registry-v8", CATALOG_FORMAT]:
		var capability: Variant = null
		var present: bool = FileAccess.file_exists(CAPABILITY_PATH) or DirAccess.dir_exists_absolute(CAPABILITY_PATH)
		if present:
			var capability_file: FileAccess = FileAccess.open(CAPABILITY_PATH, FileAccess.READ)
			if capability_file == null or capability_file.get_length() > 4096:
				load_error = "Unreadable or oversized background capability"
				return {}
			var capability_text: String = capability_file.get_as_text()
			if not unique_keys(capability_text):
				load_error = "Duplicate background capability JSON key"
				return {}
			capability = JSON.parse_string(capability_text)
		load_error = validate_capability(raw, capability, present)
		if not load_error.is_empty():
			return {}
		background_profiles = capability_profiles(capability) if present and capability.enabled else []
	cached = raw
	return cached

static func current_reveal_enabled() -> bool:
	return _load().get("format") in ["picross-runtime-registry-v8", CATALOG_FORMAT]

static func unique_keys(text: String) -> bool:
	var objects: Array[Dictionary] = []
	var index: int = 0
	while index < text.length():
		var letter: String = text[index]
		if letter == "{": objects.append({})
		elif letter == "}":
			if objects.is_empty(): return false
			objects.pop_back()
		elif letter == '"':
			var start: int = index
			index += 1
			while index < text.length() and text[index] != '"':
				if text[index] == "\\": index += 1
				index += 1
			if index >= text.length(): return false
			var after: int = index + 1
			while after < text.length() and text[after] in " \r\n\t": after += 1
			if after < text.length() and text[after] == ":":
				var key: Variant = JSON.parse_string(text.substr(start, index - start + 1))
				if not key is String or objects.is_empty() or objects[-1].has(key): return false
				objects[-1][key] = true
		index += 1
	return objects.is_empty()

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

static func _index() -> Array:
	var catalog: Dictionary = _load()
	var items: Array = catalog.get("entries", [])
	if not is_same(indexed_cache, catalog) or indexed_count != items.size():
		id_positions.clear()
		key_positions.clear()
		for index: int in range(items.size()):
			id_positions[items[index].id] = index
			key_positions[items[index].key] = index
		indexed_cache = catalog
		indexed_count = items.size()
	return items

static func by_key(key: String) -> Dictionary:
	var items: Array = _index()
	var index: int = key_positions.get(key, -1)
	return items[index].duplicate(true) if index >= 0 else {}

static func by_id(id: String) -> Dictionary:
	var items: Array = _index()
	var index: int = id_positions.get(id, -1)
	return items[index].duplicate(true) if index >= 0 else {}

static func ordinal(id: String) -> int:
	_index()
	return int(id_positions.get(id, -1)) + 1

static func key_for_id(id: String) -> String:
	return str(by_id(id).get("key", ""))

static func catalog_ids() -> Array[String]:
	var result: Array[String] = []
	for entry: Dictionary in entries():
		if entry.visible:
			result.append(entry.key)
	return result
