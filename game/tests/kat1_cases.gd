extends RefCounted
const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")

static func run(runner: SceneTree) -> void:
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Registry.PATH))
	runner.check(Registry.validate(raw).is_empty(), "KAT1 runtime registry validates")
	runner.check(Registry.categories().size() == 20, "KAT1 initial categories load")
	runner.check(Registry.by_id("T-01").category_id == "fahrzeuge-verkehr", "KAT1 existing assignment")
	var detached: Dictionary = Registry.by_id("T-01")
	detached.category_id = "not-a-category"
	runner.check(Registry.by_key("t01").category_id == "fahrzeuge-verkehr", "registry lookup returns a detached validated entry")
	runner.check(Registry.ordinal("T-09") == 6 and Registry.ordinal("missing") == 0, "registry ordinal uses registry order")
	var changed: Dictionary = raw.duplicate(true)
	changed.categories.append({"id": "test-only-extra", "name": "TEST ONLY", "order": 50})
	changed.entries[0].category_id = "test-only-extra"
	runner.check(Registry.validate(changed).is_empty(), "KAT1 category growth requires only data")
	for value: Variant in [null, [], ["voegel", "wasserwelt"], "unknown"]:
		changed = raw.duplicate(true)
		changed.entries[0].category_id = value
		runner.check(not Registry.validate(changed).is_empty(), "KAT1 missing/unknown/multiple category rejected")
	for attack: String in ["format", "missing", "extra", "duplicate-id", "duplicate-order", "name", "deleted", "hidden-null"]:
		changed = raw.duplicate(true)
		match attack:
			"format": changed.format = "picross-runtime-registry-v1"
			"missing": changed.entries[0].erase("category_id")
			"extra": changed.entries[0]["category_ids"] = ["voegel"]
			"duplicate-id": changed.categories[1].id = changed.categories[0].id
			"duplicate-order": changed.categories[1].order = changed.categories[0].order
			"name": changed.categories[0].name = " "
			"deleted": changed.categories.remove_at(11)
			"hidden-null":
				changed.entries[0].visible = false
				changed.entries[0].category_id = null
		runner.check(not Registry.validate(changed).is_empty(), "KAT1 rejects " + attack)
	changed = {"format": "picross-runtime-registry-v2", "categories": [], "entries": []}
	runner.check(Registry.validate(changed).is_empty(), "KAT1 valid empty catalog is distinct from invalid data")
	# Resolve frozen saves only inside this compatibility check, never in the player.
	var fixture_cache: Dictionary = Registry.cached.duplicate(true)
	for key: String in ["f01", "f02"]:
		Registry.cached.entries.append({"id": "F-0" + key.right(1), "key": key, "save_slot": key, "definition": "tests/fixtures/kat1/definitions/" + key + ".json", "reveal": "", "visible": false, "category_id": "voegel"})
	var store: Store = Store.new(Store.test_root_override + "-kat1-legacy")
	DirAccess.make_dir_recursive_absolute(store.root)
	for key: String in ["f01", "f02"]:
		var source: String = "res://tests/fixtures/kat1/" + key + ".json"
		var bytes: PackedByteArray = FileAccess.get_file_as_bytes(source)
		var destination: String = store.path_for(key)
		var file: FileAccess = FileAccess.open(destination, FileAccess.WRITE)
		file.store_buffer(bytes)
		file.close()
		var definition: Dictionary = Definition.load_fixture(key)
		var loaded: Dictionary = store.load_slot(definition)
		runner.check(loaded.status == "loaded", "KAT1 pre-migration save loaded under same slot " + key)
		if loaded.status != "loaded": continue
		var session: Session = Session.new(definition)
		Store.apply(loaded.data, session)
		# JSON numbers reload as floats; internal cells/history are typed integers.
		var snapshot: Dictionary = Store.snapshot(session, session.view_state)
		runner.check(Store.validate(snapshot, definition).is_empty(), "KAT1 restored snapshot remains valid " + key)
		runner.check(JSON.parse_string(JSON.stringify(snapshot)) == loaded.data, "KAT1 old save semantics unchanged " + key)
		runner.check(session.completed == (key == "f02"), "KAT1 partial and earned completion survive")
		runner.check(not session.reveal().is_empty() == (key == "f02"), "KAT1 old save reveal boundary")
		var original_cache: Dictionary = Registry.cached.duplicate(true)
		Registry.cached.categories[0].name = "TEST ONLY renamed"
		Registry.cached.entries[-2 if key == "f01" else -1].category_id = "fahrzeuge-verkehr"
		runner.check(store.load_slot(definition) == loaded, "KAT1 metadata has no save identity")
		runner.check(FileAccess.get_file_as_bytes(destination) == bytes, "KAT1 loading and metadata preserve old save bytes")
		Registry.cached = original_cache
		if key == "f01":
			runner.check(session.player.cursor == 1 and session.player.history.size() == 2 and session.player.undo_used, "KAT1 old partial history/redo")
			session.redo()
			runner.check(session.player.cells[65] == 0, "KAT1 old redo resumes")

	Registry.cached = fixture_cache
