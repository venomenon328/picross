extends RefCounted
## K-A: one session selection; no persistence or derived difficulty ratings.
const DEFAULTS: Dictionary = {"category":"", "status":"all", "mode":"all", "lower":0, "upper":0, "width":0, "height":0}
const STATUSES: Array[String] = ["all", "open", "new", "started", "solved"]
const MODES: Array[String] = ["all", "mono", "color"]

static func _dimension(value: String, label: String) -> Dictionary:
	if value.is_empty(): return {"value":0}
	var message: String = label + ": eine ganze Zahl von 1 bis 50 eingeben oder leer lassen."
	if value.length() > 8: return {"error":message}
	for character: String in value:
		if character < "0" or character > "9": return {"error":message}
	var limit: int = value.to_int()
	if limit < 1 or limit > 50: return {"error":message}
	return {"value":limit}

static func validate(category: String, status: String, mode: String, lower: int, upper: int, width: String, height: String) -> Dictionary:
	if not status in STATUSES or not mode in MODES or lower < 0 or lower > 5 or upper < 0 or upper > 5:
		return {"error":"Bitte gültige Filterwerte wählen."}
	if lower > 0 and upper > 0 and lower > upper:
		return {"error":"Schwierigkeit: Die Untergrenze darf nicht über der Obergrenze liegen."}
	var horizontal: Dictionary = _dimension(width,"Maximale Breite")
	var vertical: Dictionary = _dimension(height,"Maximale Höhe")
	if horizontal.has("error"): return horizontal
	if vertical.has("error"): return vertical
	return {"selection":{"category":category, "status":status, "mode":mode, "lower":lower, "upper":upper, "width":horizontal.value, "height":vertical.value}}

static func matches(selection: Dictionary, category: String, status: String, color: bool, width: int, height: int, difficulty: Variant) -> bool:
	if not str(selection.category).is_empty() and selection.category != category: return false
	match selection.status:
		"open":
			if not status in ["new", "started"]: return false
		"new", "started", "solved":
			if selection.status != status: return false
	if selection.mode == "mono" and color or selection.mode == "color" and not color: return false
	if selection.width > 0 and width > selection.width: return false
	if selection.height > 0 and height > selection.height: return false
	if selection.lower > 0 or selection.upper > 0:
		if not difficulty is Dictionary: return false
		var level: int = str(difficulty.level).trim_prefix("L").to_int()
		if selection.lower > 0 and level < selection.lower: return false
		if selection.upper > 0 and level > selection.upper: return false
	return true
