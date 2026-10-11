extends RefCounted
const Definition = preload("res://model/definition.gd")
const IDS: Array[String] = ["vs01", "vs02", "vs03", "vs04", "vs05", "vs06", "vs07", "vs08", "vs09", "vs10"]

static func definitions() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var catalog: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://full_view_study/catalog.json"))
	if not catalog is Dictionary or catalog.get("revision") != 1 or not catalog.get("cases") is Array or catalog.cases.size() != IDS.size():
		return [{}]
	for i: int in range(IDS.size()):
		var entry: Dictionary = catalog.cases[i]
		var path: String = "res://full_view_study/cases/%s/definition.json" % IDS[i]
		if entry.get("id") != IDS[i] or entry.get("kind") != "playable" or entry.get("certified") != true or FileAccess.get_sha256(path) != entry.get("definition_sha256"):
			return [{}]
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if not data is Dictionary or data.get("id") != IDS[i].to_upper():
			return [{}]
		result.append(data)
	return result

static func validate(data: Dictionary) -> String:
	var id: String = str(data.get("id", "")).to_lower()
	if not id in IDS:
		return "Unbekannte Studienkennung."
	var suffix: String = ".svg" if id == "vs01" else ".png"
	var expected: String = "res://full_view_study/cases/%s/reveal%s" % [id, suffix]
	if data.get("reveal", {}).get("image") != expected:
		return "Falsche Studienressource."
	return Definition.validate(data, {data.id: expected})
