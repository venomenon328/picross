extends RefCounted
## The study has its own resource root, not a second permissive data contract.
const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")
const ROOT = "res://study/book/"

static func read() -> Dictionary:
	var registry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ROOT+"fixtures.json"))
	var definitions: Array[Dictionary] = []
	var error: String = Registry.validate(registry)
	if not error.is_empty(): return {"error":error}
	for entry: Dictionary in registry.entries:
		var path: String = ROOT+str(entry.definition)
		if not FileAccess.file_exists(path): return {"error":"Missing study definition: "+path}
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
		definitions.append(data)

	error = validate(registry, definitions)
	return {"registry":registry,"definitions":definitions,"error":error}

static func validate(registry: Dictionary, definitions: Array) -> String:
	var error: String = Registry.validate(registry)
	if not error.is_empty(): return error
	if registry.entries.size() != 27 or definitions.size() != 27: return "Expected 27 study instances."
	for i: int in range(27):
		var entry: Dictionary = registry.entries[i]
		var data: Dictionary = definitions[i]
		# A fixed prefix relocates the regular relative data/art namespace. There
		# is no arbitrary resolver, cached-registry bypass or shared identity.
		if entry.definition != "data/"+entry.key+".json" or entry.reveal != "art/"+entry.key+".svg": return "Wrong study resource binding."
		if data.get("id") != entry.id: return "Foreign study definition."
		var asset: String = ROOT+str(entry.reveal)
		if data.get("reveal",{}).get("image") != asset: return "Foreign study reveal."
		error = Definition.validate(data,{str(entry.id):asset})
		if not error.is_empty(): return error
	return ""
