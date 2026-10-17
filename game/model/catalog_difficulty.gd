extends RefCounted
## Typed display metadata only; no production prose, inference or solver.
const LEVELS: Array[String] = ["L1", "L2", "L3", "L4", "L5"]
const LABELS: Array[String] = ["Sehr leicht", "Leicht", "Mittel", "Schwer", "Sehr schwer"]
const COLORS: Array[Color] = [Color("52734e"), Color("74713e"), Color("997337"), Color("a36342"), Color("9b514b")]

static func valid(value: Variant) -> bool:
	if value == null: return true
	if not value is Dictionary or value.size() != 6: return false
	if not value.get("method") in ["picross-difficulty-0.1", "picross-difficulty-0.2", "picross-difficulty-0.3"] or not value.get("level") in LEVELS: return false
	if not value.get("assessment_type") in ["editorial_estimate", "instrumented"] or not value.get("confidence") in ["low", "medium", "high"]: return false
	var span: Variant = value.get("plausible_range")
	if not span is Array or span.size() != 2 or not span[0] in LEVELS or not span[1] in LEVELS: return false
	if span[0] > value.level or span[1] < value.level or not value.get("r4_required") is bool: return false
	if value.method == "picross-difficulty-0.3":
		return value.assessment_type == "instrumented" and value.confidence == "medium" and span == [value.level, value.level] and (not value.r4_required or value.level == "L5")
	if value.r4_required:
		return value.method == "picross-difficulty-0.2" and value.level == "L5" and span == ["L5", "L5"] and value.assessment_type == "instrumented" and value.confidence == "medium"
	return true

static func label(value: Variant) -> String:
	if value == null: return "Nicht eingestuft"
	return level_label(value.level)

static func level_label(level: String) -> String:
	var index: int = LEVELS.find(level)
	return str(index+1) + " " + LABELS[index]

static func accent(value: Variant) -> Color:
	return Color("343f42") if value == null else COLORS[LEVELS.find(value.level)]

static func explanation(value: Variant) -> String:
	if value == null: return "Für dieses Rätsel liegt keine Schwierigkeitseinstufung vor."
	if value.method == "picross-difficulty-0.3":
		var model_text: String = label(value) + ". Modellbasierte Einstufung nach picross-difficulty-0.3.\nAussagekraft: mittel; noch nicht menschlich kalibriert. Die angezeigte Stufe ist das Ergebnis des Modells, keine menschlich gemessene Genauigkeit oder Unsicherheitsspanne."
		if value.r4_required: model_text += "\nNotwendige Paarlinienlogik (R4): linienübergreifend, besonders hoher logischer Anspruch."
		return model_text
	var method: String = "Redaktionelle Schätzung nach " + value.method + "." if value.assessment_type == "editorial_estimate" else "Instrumentierte Einstufung nach " + value.method + "."
	var confidence: String = {"low":"gering", "medium":"mittel", "high":"hoch"}[value.confidence]
	var span: Array = value.plausible_range
	var result: String = label(value) + ". " + method + "\nSicherheit: " + confidence + ". Plausible Spannweite: " + level_label(span[0]) + " bis " + level_label(span[1]) + "."
	if value.r4_required: result += "\nNotwendige Paarlinienlogik (R4): linienübergreifend, besonders hoher logischer Anspruch."
	return result
