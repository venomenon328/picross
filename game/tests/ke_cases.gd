extends RefCounted
const Registry = preload("res://model/content_registry.gd")
const Difficulty = preload("res://model/catalog_difficulty.gd")

static func assessment() -> Dictionary:
	return {"method":"picross-difficulty-0.1","level":"L5","assessment_type":"editorial_estimate","confidence":"low","plausible_range":["L2","L5"],"r4_required":false}

static func run(runner: SceneTree) -> void:
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Registry.PATH))
	raw.format = "picross-runtime-registry-v3"
	for entry: Dictionary in raw.entries: entry.difficulty = null
	runner.check(Registry.validate(raw).is_empty(),"KE v3 explicit missing difficulty loads")
	runner.check(Difficulty.label(null) == "Nicht eingestuft","KE missing is not an invented estimate")
	for level: String in Difficulty.LEVELS:
		var value: Dictionary = assessment()
		value.level = level
		value.plausible_range = ["L1","L5"]
		raw.entries[0].difficulty = value
		runner.check(Registry.validate(raw).is_empty() and Difficulty.label(value) == "≈ " + Difficulty.LABELS[Difficulty.LEVELS.find(level)],"KE original level and visible editorial estimate " + level)
	var value: Dictionary = assessment()
	value.merge({"method":"picross-difficulty-0.2","assessment_type":"instrumented","confidence":"medium","plausible_range":["L5","L5"],"r4_required":true},true)
	raw.entries[0].difficulty = value
	runner.check(Registry.validate(raw).is_empty() and Difficulty.label(value) == "Sehr schwer" and Difficulty.explanation(value).contains("Paarlinienlogik (R4)"),"KE instrumented necessary R4 without estimate")
	for attack: Dictionary in [{"method":"unknown"},{"level":"L6"},{"confidence":true},{"plausible_range":["L5","L1"]},{"r4_required":1},{"bottleneck":"SPOILER"},{"assessment_type":"editorial_estimate"}]:
		var changed: Dictionary = value.duplicate(true)
		changed.merge(attack,true)
		raw.entries[0].difficulty = changed
		runner.check(not Registry.validate(raw).is_empty(),"KE malformed metadata rejects complete registry " + str(attack))
	for malformed: Variant in [{},[],false,"L2"]:
		raw.entries[0].difficulty = malformed
		runner.check(not Registry.validate(raw).is_empty(),"KE present malformed metadata cannot become missing")
	raw.entries[0].erase("difficulty")
	runner.check(not Registry.validate(raw).is_empty(),"KE v3 requires eighth field")
	raw.format = "picross-runtime-registry-v2"
	for entry: Dictionary in raw.entries: entry.erase("difficulty")
	runner.check(Registry.validate(raw).is_empty(),"KE legacy exact seven-field v2 stays valid")
	raw.entries[0].difficulty = null
	runner.check(not Registry.validate(raw).is_empty(),"KE v2 never silently reinterpreted as eight fields")
