extends RefCounted
const Registry = preload("res://model/content_registry.gd")
const Preference = preload("res://model/catalog_preference.gd")
const Catalog = preload("res://ui/catalog.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")

static func run(runner: SceneTree) -> void:
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Registry.PATH))
	raw.format = "picross-runtime-registry-v4"
	for entry: Dictionary in raw.entries:
		entry.difficulty = null
		entry.added_at = null
	runner.check(Registry.validate(raw).is_empty(), "KU-B v4 explicit unknown values")
	for value: Variant in ["2024-02-29T23:59:59Z", "0001-01-01T00:00:00Z", "9999-12-31T23:59:59Z", null]:
		raw.entries[0].added_at = value
		runner.check(Registry.validate(raw).is_empty(), "KU-B real UTC/null " + str(value))
	for value: Variant in [false, 1, {}, "2023-02-29T12:00:00Z", "0000-01-01T00:00:00Z", "2024-01-01T24:00:00Z", "2024-01-01T00:00:60Z", "2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00.000Z", "2024-01-01T00:00:00Z\n"]:
		raw.entries[0].added_at = value
		runner.check(not Registry.validate(raw).is_empty(), "KU-B rejects invalid added value " + str(value))
	runner.check(not Registry.unique_keys('{"entries":[],"entr\\u0069es":[]}'), "KU-B rejects escaped duplicate JSON keys")
	var path: String = "user://ku-b-preference-test.json"
	DirAccess.remove_absolute(path)
	var preference: Preference = Preference.new(path)
	preference.load_selection()
	runner.check(preference.criterion == "category" and preference.direction == "asc" and not FileAccess.file_exists(path), "KU-B missing preference is read-only default")
	preference.criterion = "added"
	preference.direction = "desc"
	runner.check(preference.save_selection(), "KU-B native atomic preference write")
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
	var stamp: int = FileAccess.get_modified_time(path)
	runner.check(preference.save_selection() and FileAccess.get_modified_time(path) == stamp, "KU-B same saved selection is a no-op")
	preference.fail_write = true
	preference.criterion = "size"
	runner.check(not preference.save_selection() and FileAccess.get_file_as_bytes(path) == bytes, "KU-B failed write preserves valid preference")
	preference.fail_write = false
	DirAccess.make_dir_absolute(path + ".tmp")
	runner.check(not preference.save_selection() and FileAccess.get_file_as_bytes(path) == bytes, "KU-B actual filesystem write failure preserves valid preference")
	DirAccess.remove_absolute(path + ".tmp")
	runner.check(preference.save_selection(), "KU-B same selection retries failure")
	var second: Preference = Preference.new(path)
	second.load_selection()
	runner.check(second.criterion == "size" and second.direction == "desc", "KU-B preference reload restores complete pair")
	for malformed: String in ['{"format":"picross-catalog-preference-v1","criterion":"size","direction":"asc","direction":"desc"}', '{"format":"picross-catalog-preference-v1","criterion":"size","direction":true}', '{}']:
		var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
		file.store_string(malformed)
		file.close()
		second.load_selection()
		runner.check(second.criterion == "category" and second.direction == "asc" and FileAccess.get_file_as_string(path) == malformed, "KU-B invalid preference defaults whole pair without rewrite")
	DirAccess.remove_absolute(path)
	var catalog: Catalog = Catalog.new()
	catalog.preference = Preference.new(path)
	runner.root.add_child(catalog)
	var sessions: Array[Session] = []
	var statuses: Array[String] = []
	var errors: Array[String] = []
	for entry: Dictionary in Registry.entries():
		if entry.visible:
			sessions.append(Session.new(Definition.load_fixture(entry.key)))
			statuses.append("fresh")
			errors.append("")
	catalog.present(sessions, statuses, errors, "", "")
	for i: int in range(1, catalog.filtered_ids.size()):
		runner.check(catalog._primary(catalog.filtered_ids[i-1]) <= catalog._primary(catalog.filtered_ids[i]), "KU-B default editorial category order")
	var canonical: Array[String] = []
	canonical.assign(catalog.items.keys())
	for i: int in range(canonical.size()):
		catalog.metadata[canonical[i]].added_at = null if i == 0 else "2024-01-01T00:00:00Z"
		catalog.metadata[canonical[i]].difficulty = null
	catalog.choose_sort("added")
	runner.check(catalog.preference.direction == "desc" and catalog.filtered_ids[-1] == canonical[0], "KU-B added defaults newest and unknown last")
	var dates: Array[String] = catalog.filtered_ids.duplicate()
	catalog.reverse_sort()
	runner.check(catalog.filtered_ids == dates, "KU-B reverse preserves canonical ties and unknown last")
	catalog.choose_sort("size")
	runner.check(catalog.preference.direction == "asc", "KU-B changed size criterion resets direction")
	for i: int in range(1, catalog.filtered_ids.size()):
		runner.check(catalog._primary(catalog.filtered_ids[i-1]) <= catalog._primary(catalog.filtered_ids[i]), "KU-B ascending area order")
	catalog.choose_sort("difficulty")
	runner.check(catalog.filtered_ids == canonical, "KU-B unknown difficulty preserves canonical order")
	# Mixed levels use existing metadata only; null stays last in either direction.
	for i: int in range(canonical.size()):
		catalog.metadata[canonical[i]].difficulty = null if i == 0 else {"level": "L" + str(1 + i % 5)}
	for direction: String in ["asc", "desc"]:
		catalog.preference.direction = direction
		var ordered: Array[String] = canonical.duplicate()
		ordered.sort_custom(catalog._before)
		runner.check(ordered[-1] == canonical[0], "KU-B unknown difficulty last " + direction)
		for i: int in range(1, ordered.size() - 1):
			var previous: String = catalog._primary(ordered[i-1])
			var current: String = catalog._primary(ordered[i])
			runner.check(previous <= current if direction == "asc" else previous >= current, "KU-B mixed L1-L5 primary direction")
			if previous == current:
				runner.check(canonical.find(ordered[i-1]) < canonical.find(ordered[i]), "KU-B level ties remain canonical")
	# Equal area must not introduce width/height as an undocumented secondary key.
	catalog.preference.criterion = "size"
	var a: Variant = catalog.items[canonical[0]].player
	var b: Variant = catalog.items[canonical[1]].player
	var dimensions: Array[int] = [a.width, a.height, b.width, b.height]
	a.width = 20; a.height = 30; b.width = 30; b.height = 20
	for direction: String in ["asc", "desc"]:
		catalog.preference.direction = direction
		runner.check(catalog._before(canonical[0], canonical[1]) and not catalog._before(canonical[1], canonical[0]), "KU-B 20x30 and 30x20 tie canonically " + direction)
	a.width = dimensions[0]; a.height = dimensions[1]; b.width = dimensions[2]; b.height = dimensions[3]
	catalog.preference.criterion = "difficulty"
	catalog.page_index = 1
	catalog.choose_sort("difficulty")
	runner.check(catalog.page_index == 1, "KU-B same criterion does not reset page")
	catalog.choose_sort("category")
	runner.check(catalog.page_index == 0, "KU-B changed criterion resets page")
	catalog.queue_free()
	DirAccess.remove_absolute(path)
