extends RefCounted
## Typed display metadata only; no production prose, inference or solver.
const LEVELS: Array[String] = ["L1", "L2", "L3", "L4", "L5"]
const LABELS: Array[String] = ["Sehr leicht", "Leicht", "Mittel", "Schwer", "Sehr schwer"]

static func valid(value: Variant) -> bool:
	if value == null: return true
	if not value is Dictionary or value.size() != 6: return false
	if not value.get("method") in ["picross-difficulty-0.1", "picross-difficulty-0.2"] or not value.get("level") in LEVELS: return false
	if not value.get("assessment_type") in ["editorial_estimate", "instrumented"] or not value.get("confidence") in ["low", "medium", "high"]: return false
	var span: Variant = value.get("plausible_range")
	if not span is Array or span.size() != 2 or not span[0] in LEVELS or not span[1] in LEVELS: return false
	if span[0] > value.level or span[1] < value.level or not value.get("r4_required") is bool: return false
	if value.r4_required:
		return value.method == "picross-difficulty-0.2" and value.level == "L5" and span == ["L5", "L5"] and value.assessment_type == "instrumented" and value.confidence == "medium"
	return true

static func label(value: Variant) -> String:
	if value == null: return "Nicht eingestuft"
	return ("≈ " if value.assessment_type == "editorial_estimate" else "") + LABELS[LEVELS.find(value.level)]

static func explanation(value: Variant) -> String:
	if value == null: return "Für dieses Rätsel liegt keine Schwierigkeitseinstufung vor."
	var method: String = "Redaktionelle Schätzung nach " + value.method + "." if value.assessment_type == "editorial_estimate" else "Instrumentierte Einstufung nach " + value.method + "."
	var confidence: String = {"low":"gering", "medium":"mittel", "high":"hoch"}[value.confidence]
	var span: Array = value.plausible_range
	var result: String = method + "\nSicherheit: " + confidence + ". Plausible Spannweite: " + LABELS[LEVELS.find(span[0])] + " bis " + LABELS[LEVELS.find(span[1])] + "."
	if value.r4_required: result += "\nNotwendige Paarlinienlogik (R4): linienübergreifend, besonders hoher logischer Anspruch."
	return result
