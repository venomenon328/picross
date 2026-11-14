extends SceneTree
## One-off real migrated-catalog reader/render probe, isolated saves only.
const Registry = preload("res://model/content_registry.gd")
const Definition = preload("res://model/definition.gd")
const Store = preload("res://model/save_store.gd")
var book: Node3D
var failures: Array[String] = []
var cases: Array = []
var output: String

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	if not ok:
		failures.append(label)
		print("M2_FAIL ", label)

func frames(count: int = 3) -> void:
	for index: int in range(count): await process_frame

func capture(name: String) -> Image:
	await frames()
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	check(image != null and not image.is_empty(), "viewport has pixels "+name)
	if image != null: check(image.save_png(output.path_join(name+".png")) == OK, "capture "+name)
	return image

func run() -> void:
	output = OS.get_environment("M2_OUTPUT")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	var entries: Array[Dictionary] = Registry.entries()
	check(Registry.load_error.is_empty() and entries.size() == 56, "real registry 56 entries")
	var standard_drawing: String = ""
	var standard_plain: String = ""
	var revised_reveal: String = ""
	var old: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://m2_before_runtime.json"))
	check(Registry.validate(old).is_empty(), "old runtime remains valid reader input")
	for entry: Dictionary in entries:
		var definition: Dictionary = Definition.load_fixture(entry.key)
		check(not definition.is_empty() and Definition.validate(definition).is_empty(), "definition/reveal decode "+entry.id)
		check(definition.get("id") == entry.id and definition.reveal.name == entry.name, "identity and current name "+entry.id)
		if entry.background.status == "standard":
			if entry.category_id in ["wasserwelt", "landschaften-natur"] and standard_drawing.is_empty(): standard_drawing = entry.id
			if not entry.category_id in ["wasserwelt", "landschaften-natur"] and standard_plain.is_empty(): standard_plain = entry.id
		if entry.id == "pz-023b50b44d1c4698a6e17e65b6ea4337": revised_reveal = entry.id
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames(8)
	check(book.app.sessions.size() == 56, "real player constructed 56 sessions")
	var selected: Array[String] = [standard_drawing, standard_plain, "pz-birne", revised_reveal]
	for index: int in range(selected.size()):
		await frames(5) # Settlement releases its input barrier on a later frame.
		var identifier: String = selected[index]
		check(not identifier.is_empty(), "selected render case exists")
		check(book.request_open(identifier), "open request accepted "+identifier)
		var deadline: int = Time.get_ticks_msec()+20000
		while book.state != book.State.WORK and Time.get_ticks_msec() < deadline: await process_frame
		check(book.state == book.State.WORK and book.app.session.definition.id == identifier, "opened "+identifier)
		await frames(5)
		var entry: Dictionary = Registry.by_id(identifier)
		var snapshot: Dictionary = book.app.puzzle_background.snapshot()
		if entry.background.status == "selected":
			check(snapshot.has_texture and snapshot.state == "visible", "selected real texture visible "+identifier)
			check(snapshot.visible_revision == entry.background.image_revision, "selected image revision retained")
		var name: String = "case-"+str(index)+"-"+str(entry.background.status)
		var image: Image = await capture(name)
		var same: Variant = null
		if entry.background.status == "standard":
			# Compare the actual content/marginalia renderer under old/new status;
			# only the in-memory reader cache changes. No source file is rewritten.
			var position: int = Registry.ordinal(identifier)-1
			var saved: Dictionary = Registry.cached.entries[position].background.duplicate(true)
			Registry.cached.entries[position].background = {"status":"legacy", "image_revision":null, "asset":null}
			book.app._layout_marginalia()
			var legacy: Image = await capture("case-"+str(index)+"-legacy")
			same = image.get_data() == legacy.get_data()
			check(same, "legacy/standard identical rendered bytes "+identifier)
			Registry.cached.entries[position].background = saved
			book.app._layout_marginalia()
		cases.append({"id":identifier,"status":entry.background.status,"category_id":entry.category_id,
			"legacy_standard_pixels_identical":same,"snapshot":snapshot,"image":name+".png",
			"revision":book.app.session.definition.revision,"reveal":entry.reveal})
		await frames(5)
		check(book.request_return(), "return request accepted")
		deadline = Time.get_ticks_msec()+20000
		while book.state != book.State.CATALOG and Time.get_ticks_msec() < deadline: await process_frame
		check(book.state == book.State.CATALOG, "returned to catalog")
		await frames(5)
	var report: Dictionary = {"status":"passed" if failures.is_empty() else "failed", "entries":entries.size(),
		"engine":Engine.get_version_info(),"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),
		"cases":cases,"failures":failures,"user_saves":false}
	var stream: FileAccess = FileAccess.open(output.path_join("player-probe.json"),FileAccess.WRITE)
	stream.store_string(JSON.stringify(report,"\t")+"\n")
	print("M2_PLAYER ",JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
