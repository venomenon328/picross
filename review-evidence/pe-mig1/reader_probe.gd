extends SceneTree

const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")

func _initialize() -> void:
	var data: Dictionary = Registry._load()
	if not Registry.load_error.is_empty() or data.get("format") != "picross-runtime-registry-v8":
		push_error("Runtime rejected: " + Registry.load_error)
		quit(1)
		return
	if Registry.entries().size() != 56 or Registry.categories().size() != 20:
		push_error("Runtime inventory count differs")
		quit(1)
		return
	var definitions: int = 0
	for entry: Dictionary in Registry.entries():
		if Registry.by_id(entry.id) != entry or Registry.by_key(entry.key) != entry:
			push_error("Runtime index differs: " + str(entry.id))
			quit(1)
			return
		var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://" + str(entry.definition)))
		var loaded: Dictionary = Definition.load_fixture(entry.key)
		if loaded.is_empty() or loaded.id != entry.id or loaded.reveal.name != entry.name or loaded.reveal.image != "res://" + str(entry.reveal):
			push_error("Definition reader rejected: " + str(entry.id))
			quit(1)
			return
		for field: String in ["id", "revision", "width", "height", "solution", "palette", "rows", "columns"]:
			if loaded[field] != raw[field]:
				push_error("Definition semantic change: " + str(entry.id) + "/" + field)
				quit(1)
				return
		definitions += 1
	print("PE_MIG1_READER_OK format=picross-runtime-registry-v8 entries=56 categories=20 definitions=" + str(definitions) + " identities_revisions_logic_unchanged=true")
	quit(0)
