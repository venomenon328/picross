extends RefCounted
## Cheap PE-A1 boundary/save cases within the existing native.core process.
const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")
const BackgroundCases = preload("res://tests/background_tests.gd")

static func registry(status: String = "legacy") -> Dictionary:
	var entry: Dictionary = BackgroundCases.entry("pz-metadata-native", status)
	entry["name"] = "Current name"
	return BackgroundCases.registry(entry, 7)

static func capability(enabled: bool) -> Dictionary:
	return {"format":"picross-runtime-background-capability-v1", "runtime_format":"picross-runtime-registry-v6", "profile_id":"picross-background-png2304-v1", "enabled":enabled}

static func reader_cases(runner: SceneTree) -> void:
	var valid: Dictionary = registry()
	runner.check(Registry.validate(valid).is_empty(), "PE-A1 exact v7 shape")
	for field: String in valid:
		var bad: Dictionary = valid.duplicate(true)
		bad.erase(field)
		runner.check(not Registry.validate(bad).is_empty(), "PE-A1 rejects missing v7 root field " + field)
	var future_registry: Dictionary = valid.duplicate(true)
	future_registry.format = "picross-runtime-registry-v8"
	runner.check(not Registry.validate(future_registry).is_empty(), "PE-A1 rejects unknown future registry")
	var extra_root: Dictionary = valid.duplicate(true)
	extra_root["metadata"] = []
	runner.check(not Registry.validate(extra_root).is_empty(), "PE-A1 rejects alternate metadata root")
	for value: Variant in [null, 7, true, [], {}, "", " \t\n", "\u00a0\u2003", "x".repeat(129)]:
		var bad: Dictionary = valid.duplicate(true)
		bad.entries[0].name = value
		runner.check(not Registry.validate(bad).is_empty(), "PE-A1 rejects invalid current name " + str(value))
	for value: String in ["x", "x".repeat(128), " Current name ", "\u00a0x\u00a0"]:
		var good: Dictionary = valid.duplicate(true)
		good.entries[0].name = value
		runner.check(Registry.validate(good).is_empty(), "PE-A1 keeps existing name boundary " + value)
	for field: String in valid.entries[0]:
		var bad: Dictionary = valid.duplicate(true)
		bad.entries[0].erase(field)
		runner.check(not Registry.validate(bad).is_empty(), "PE-A1 rejects missing v7 field " + field)
	var extra: Dictionary = valid.duplicate(true)
	extra.entries[0]["label"] = "alias"
	runner.check(not Registry.validate(extra).is_empty(), "PE-A1 rejects extra v7 field")
	for version: int in range(2, 7):
		var old: Dictionary = BackgroundCases.registry(BackgroundCases.entry(), version)
		if version < 6: old.entries[0].erase("background")
		if version < 4: old.entries[0].erase("added_at")
		if version < 3: old.entries[0].erase("difficulty")
		runner.check(Registry.validate(old).is_empty(), "PE-A1 retains exact old reader v%d" % version)
		old.entries[0]["name"] = "not in old version"
		runner.check(not Registry.validate(old).is_empty(), "PE-A1 old reader rejects added name v%d" % version)
	for status: String in ["legacy", "none", "selected"]:
		var data: Dictionary = registry(status)
		runner.check(Registry.validate(data).is_empty(), "PE-A1 v7 retains background shape " + status)
		runner.check(Registry.validate_capability(data, capability(true), true).is_empty(), "PE-A1 unchanged v6 capability enables " + status)
		runner.check(Registry.validate_capability(data, null, false).is_empty() == (status == "legacy"), "PE-A1 missing capability boundary " + status)
		runner.check(Registry.validate_capability(data, capability(false), true).is_empty() == (status == "legacy"), "PE-A1 disabled capability boundary " + status)
	for value: Variant in [null, {}, [], {"format":"picross-runtime-background-capability-v1"}]:
		runner.check(not Registry.validate_capability(valid, value, true).is_empty(), "PE-A1 malformed existing capability never ignored")
	for field: String in capability(true):
		var bad: Dictionary = capability(true)
		bad[field] = "wrong"
		runner.check(not Registry.validate_capability(valid, bad, true).is_empty(), "PE-A1 rejects capability mismatch " + field)
	var future: Dictionary = capability(true)
	future.runtime_format = "picross-runtime-registry-v7"
	runner.check(not Registry.validate_capability(valid, future, true).is_empty(), "PE-A1 does not invent a new capability generation")

static func definition(identifier: String, name: String) -> Dictionary:
	return {"schema":2, "id":identifier, "revision":1, "width":2, "height":2,
		"palette":[{"id":1,"color":"224466","symbol":"A"}], "solution":[[1,0],[0,1]],
		"rows":[[{"length":1,"color":1}],[{"length":1,"color":1}]],
		"columns":[[{"length":1,"color":1}],[{"length":1,"color":1}]],
		"reveal":{"version":1,"definition_id":identifier,"name":name,"image":"res://art/fixtures/t01.svg"}}

static func save_cases(runner: SceneTree) -> void:
	var original: Dictionary = Registry.cached
	var data: Dictionary = registry()
	data.categories.append({"id":"renamed-category","name":"Renamed category","order":2})
	data.entries.clear()
	var files: Array[String] = []
	for state: String in ["begun", "solved"]:
		var identifier: String = "pz-metadata-" + state
		var entry: Dictionary = BackgroundCases.entry(identifier, "legacy")
		entry.key = "metadata_" + state
		entry.save_slot = entry.key
		entry.definition = "data/fixtures/" + entry.key + ".json"
		entry.reveal = "art/fixtures/t01.svg" if state == "begun" else "art/fixtures/t02.svg"
		entry["name"] = "Before " + state
		data.entries.append(entry)
		var value: Dictionary = definition(identifier, entry.name)
		value.reveal.image = "res://" + entry.reveal
		var path: String = "res://" + entry.definition
		var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
		runner.check(file != null, "PE-A1 isolated definition can be written " + state)
		if file == null:
			for previous: String in files: DirAccess.remove_absolute(previous)
			return
		file.store_string(JSON.stringify(value) + "\n")
		file.close()
		files.append(path)
	runner.check(Registry.validate(data).is_empty(), "PE-A1 synthetic save catalog validates")
	Registry.cached = data
	var store: Store = Store.new(Store.test_root_override + "-pe-a1")
	for state: String in ["begun", "solved"]:
		var key: String = "metadata_" + state
		var entry: Dictionary = Registry.by_key(key)
		var path: String = "res://" + entry.definition
		var definition_bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
		var old_definition: Dictionary = Definition.load_fixture(key)
		runner.check(Definition.validate(old_definition).is_empty(), "PE-A1 synthetic definition validates " + state)
		var session: Session = Session.new(old_definition)
		if state == "begun":
			session.player.commit([{"index":0,"before":-1,"after":1}])
			session.player.commit([{"index":1,"before":-1,"after":0}])
			session.undo()
		else:
			session.player.commit([{"index":0,"before":-1,"after":1},{"index":3,"before":-1,"after":1}])
			session.completed = session.is_solution()
		session.view_state.zoom = 36
		session.view_state.tool = "erase"
		# Compare through the actual JSON boundary: restored numeric view values
		# are floats, while unchanged in-memory player values remain integers.
		var before: Dictionary = JSON.parse_string(JSON.stringify(Store.snapshot(session, session.view_state)))
		runner.check(store.write_slot(session, session.view_state).is_empty(), "PE-A1 actual initial save " + state)
		var save_bytes: PackedByteArray = FileAccess.get_file_as_bytes(store.path_for(key))
		for row: Dictionary in Registry.cached.entries:
			if row.id == entry.id:
				row.name = "After " + state
				row.category_id = "renamed-category"
		var current_definition: Dictionary = Definition.load_fixture(key)
		var expected: Dictionary = old_definition.duplicate(true)
		expected.reveal.name = "After " + state
		runner.check(current_definition == expected, "PE-A1 shared loader only overlays current name " + state)
		runner.check(Registry.by_id(entry.id).category_id == "renamed-category", "PE-A1 indexed lookup uses current category " + state)
		var loaded: Dictionary = store.load_slot(current_definition)
		runner.check(loaded.status == "loaded", "PE-A1 old save remains compatible " + state)
		if loaded.status == "loaded":
			var restored: Session = Session.new(current_definition)
			Store.apply(loaded.data, restored)
			var restored_data: Dictionary = JSON.parse_string(JSON.stringify(Store.snapshot(restored, restored.view_state)))
			runner.check(restored_data == before, "PE-A1 preserves cells, history, redo, view and completion " + state)
			runner.check(restored.completed == (state == "solved"), "PE-A1 preserves earned completion " + state)
			if state == "begun":
				runner.check(restored.reveal().is_empty() and not "After" in restored.album_title(), "PE-A1 begun title and reveal stay spoiler-free")
				runner.check(restored.player.cursor == 1 and restored.player.history.size() == 2 and restored.player.undo_used, "PE-A1 redo branch and undo flag survive")
				restored.redo()
				runner.check(restored.player.cells[1] == 0, "PE-A1 retained redo still works")
			else:
				runner.check(restored.album_title() == "After solved" and restored.reveal().name == "After solved", "PE-A1 solved title and reveal use current name")
		runner.check(FileAccess.get_file_as_bytes(path) == definition_bytes, "PE-A1 overlay leaves definition bytes unchanged " + state)
		runner.check(FileAccess.get_file_as_bytes(store.path_for(key)) == save_bytes, "PE-A1 load leaves save bytes unchanged " + state)
		store.reset_slot(key)
	Registry.cached = original
	for path: String in files: DirAccess.remove_absolute(path)
	runner.check(Registry.by_id("T-01").key == "t01", "PE-A1 cached lookup follows replaced catalogs")

static func run(runner: SceneTree) -> void:
	reader_cases(runner)
	save_cases(runner)
