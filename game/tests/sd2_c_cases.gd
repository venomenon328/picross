extends RefCounted
const Registry = preload("res://model/content_registry.gd")
const Difficulty = preload("res://model/catalog_difficulty.gd")
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")

static func rating(level: String, method: String = "picross-difficulty-0.4") -> Dictionary:
	return {"method":method,"level":level,"assessment_type":"instrumented","confidence":"medium","plausible_range":[level,level],"r4_required":level == "L5"}

static func run(runner: SceneTree) -> void:
	var original: Dictionary = Registry.cached.duplicate(true)
	var mixed: Dictionary = original.duplicate(true)
	mixed.format = "picross-runtime-registry-v5"
	for index: int in range(mixed.entries.size()):
		mixed.entries[index]["added_at"] = null
		mixed.entries[index]["difficulty"] = null if index == 0 else rating("L%d" % index,"picross-difficulty-0.4" if index % 2 else "picross-difficulty-0.3")
	runner.check(Registry.validate(mixed).is_empty(), "SD2-C runtime v5 mixed 0.3/0.4/null validates")
	for level: String in Difficulty.LEVELS:
		var value: Dictionary = rating(level)
		runner.check(Difficulty.valid(value,5), "SD2-C all five levels and necessary R4")
		runner.check(Difficulty.label(value) == Difficulty.level_label(level), "SD2-C unchanged five-level label")
		for version: int in [2,3,4]:
			runner.check(not Difficulty.valid(value,version), "SD2-C old projection rejects new method")
		for field: String in ["confidence","r4_required","method","score","plausible_range"]:
			var bad: Dictionary = value.duplicate(true)
			bad[field] = {"confidence":"high","r4_required":1,"method":"picross-difficulty-0.5","score":1,"plausible_range":["L1","L5"]}[field]
			runner.check(not Difficulty.valid(bad,5), "SD2-C strict projection rejects " + field)
	for version: int in [3,4]:
		var old: Dictionary = mixed.duplicate(true)
		old.format = "picross-runtime-registry-v%d" % version
		if version == 3:
			for entry: Dictionary in old.entries: entry.erase("added_at")
		runner.check(not Registry.validate(old).is_empty(), "SD2-C older registry cannot carry 0.4")
	Registry.cached = mixed
	# The frozen partial/completed saves exercise actual load, undo/redo and reveal.
	for key: String in ["f01","f02"]:
		Registry.cached.entries.append({"id":"F-0"+key.right(1),"key":key,"save_slot":key,"definition":"tests/fixtures/kat1/definitions/"+key+".json","reveal":"","visible":false,"category_id":"voegel","difficulty":rating("L3"),"added_at":null})
	var store: Store = Store.new(Store.test_root_override + "-sd2-c")
	DirAccess.make_dir_recursive_absolute(store.root)
	for key: String in ["f01","f02"]:
		var bytes: PackedByteArray = FileAccess.get_file_as_bytes("res://tests/fixtures/kat1/"+key+".json")
		var destination: String = store.path_for(key)
		var file: FileAccess = FileAccess.open(destination,FileAccess.WRITE)
		file.store_buffer(bytes)
		file.close()
		var definition: Dictionary = Definition.load_fixture(key)
		var loaded: Dictionary = store.load_slot(definition)
		runner.check(loaded.status == "loaded", "SD2-C preexisting synthetic save loads")
		if loaded.status != "loaded": continue
		var session: Session = Session.new(definition)
		Store.apply(loaded.data,session)
		var snapshot: Dictionary = Store.snapshot(session,session.view_state)
		runner.check(JSON.parse_string(JSON.stringify(snapshot)) == loaded.data, "SD2-C save semantics remain exact")
		runner.check(session.completed == (key == "f02") and not session.reveal().is_empty() == (key == "f02"), "SD2-C earned completion and reveal survive")
		Registry.cached.entries[-2 if key == "f01" else -1].difficulty = rating("L5","picross-difficulty-0.3")
		runner.check(store.load_slot(definition) == loaded and FileAccess.get_file_as_bytes(destination) == bytes, "SD2-C rating methods do not change save identity or bytes")
		if key == "f01":
			runner.check(session.player.cursor == 1 and session.player.history.size() == 2 and session.player.undo_used, "SD2-C partial history intact")
			session.redo()
			runner.check(session.player.cells[65] == 0, "SD2-C redo resumes")
	Registry.cached = original
