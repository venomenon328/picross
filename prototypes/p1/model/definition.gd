extends RefCounted
## JSON boundary. 0 is background; positive IDs refer to palette entries.

static func load_f01() -> Dictionary:
	return load_fixture("f01")

static func load_fixture(id: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/" + id + ".json"))
	return parsed if parsed is Dictionary else {}

static func integer(value: Variant) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value))

static func hints(line: Array) -> Array:
	var result: Array = []
	var previous: int = 0
	for value: int in line:
		if value > 0:
			if value == previous:
				result[-1]["length"] += 1
			else:
				result.append({"length": 1, "color": value})
		previous = value
	return result

static func column(matrix: Array, x: int) -> Array:
	var result: Array = []
	for row: Array in matrix:
		result.append(row[x])
	return result

static func valid_hints(stored: Variant, expected: Array) -> bool:
	if not stored is Array or stored.size() != expected.size():
		return false
	for i: int in range(expected.size()):
		var item: Variant = stored[i]
		if not item is Dictionary or item.size() != 2:
			return false
		if not integer(item.get("length")) or not integer(item.get("color")):
			return false
		if int(item.length) != expected[i].length or int(item.color) != expected[i].color:
			return false
	return true

static func validate(data: Dictionary) -> String:
	if data.get("schema") != 2 or not integer(data.get("revision")) or data.revision < 1:
		return "Unbekannte Definitionsversion."
	if not data.get("id") is String or data.id.is_empty():
		return "Definitionskennung fehlt."
	for key: String in ["width", "height"]:
		if not integer(data.get(key)) or data[key] < 1 or data[key] > 100:
			return "Ungültige Dimension."
	if not data.get("palette") is Array or data.palette.is_empty():
		return "Palette fehlt."
	var ids: Array[int] = []
	for entry: Variant in data.palette:
		if not entry is Dictionary or not integer(entry.get("id")) or entry.id < 1 or entry.id in ids:
			return "Ungültige Farbkennung."
		if not entry.get("color") is String or not Color.html_is_valid(entry.color):
			return "Ungültige Farbe."
		if not entry.get("symbol") is String or entry.symbol.is_empty():
			return "Farbsymbol fehlt."
		ids.append(int(entry.id))
	if not data.get("solution") is Array or data.solution.size() != int(data.height):
		return "Ungültige Matrixhöhe."
	for row: Variant in data.solution:
		if not row is Array or row.size() != int(data.width):
			return "Ungültige Matrixbreite."
		for value: Variant in row:
			if not integer(value) or (value != 0 and not int(value) in ids):
				return "Ungültiger Zellwert."
	if not data.get("rows") is Array or data.rows.size() != int(data.height):
		return "Zeilenhinweise fehlen."
	if not data.get("columns") is Array or data.columns.size() != int(data.width):
		return "Spaltenhinweise fehlen."
	for y: int in range(int(data.height)):
		if not valid_hints(data.rows[y], hints(data.solution[y])):
			return "Zeilenhinweise widersprechen der Lösung."
	for x: int in range(int(data.width)):
		if not valid_hints(data.columns[x], hints(column(data.solution, x))):
			return "Spaltenhinweise widersprechen der Lösung."
	var reveal: Variant = data.get("reveal")
	if not reveal is Dictionary or not reveal.get("name") is String or reveal.name.is_empty():
		return "Motivname fehlt."
	if reveal.get("version") != 1 or reveal.get("definition_id") != data.id:
		return "Ungültige Abschlusszuordnung."
	var path: Variant = reveal.get("image")
	if not path is String or not path.begins_with("res://art/") or ".." in path or not path.ends_with(".svg"):
		return "Ungültiger lokaler Bildpfad."
	if not ResourceLoader.exists(path, "Texture2D"):
		return "Abschlussbild fehlt."
	var texture: Texture2D = load(path) as Texture2D
	if texture == null or texture.get_width() < 1 or texture.get_height() < 1:
		return "Defektes Abschlussbild."
	return ""
