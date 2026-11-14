extends SceneTree
## One visible category drawing, old/new status on the actual book renderer.
const Registry = preload("res://model/content_registry.gd")
const Store = preload("res://model/save_store.gd")
func _initialize() -> void: call_deferred("run")
func frames() -> void:
	for index: int in range(8): await process_frame
func run() -> void:
	var output: String = OS.get_environment("M2_OUTPUT")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	var book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames()
	var identifier: String = "pz-7635c2e042e349fc90ad9ae55681de0f"
	var accepted: bool = book.request_open(identifier)
	var deadline: int = Time.get_ticks_msec()+20000
	while book.state != book.State.WORK and Time.get_ticks_msec()<deadline: await process_frame
	await frames()
	var boxes: Array = book.app.marginalia.boxes.duplicate()
	var visible_parts: int = 0
	for box: Rect2 in boxes:
		if box.has_area(): visible_parts += 1
	await RenderingServer.frame_post_draw
	var standard: Image = root.get_texture().get_image()
	standard.save_png(output.path_join("category-visible-standard.png"))
	var position: int = Registry.ordinal(identifier)-1
	var original: Dictionary = Registry.cached.entries[position].background.duplicate(true)
	Registry.cached.entries[position].background = {"status":"legacy","image_revision":null,"asset":null}
	book.app._layout_marginalia()
	await frames()
	await RenderingServer.frame_post_draw
	var legacy: Image = root.get_texture().get_image()
	legacy.save_png(output.path_join("category-visible-legacy.png"))
	var same: bool = standard.get_data() == legacy.get_data()
	Registry.cached.entries[position].background = original
	var ok: bool = accepted and book.app.session.definition.id == identifier and visible_parts > 0 and same
	var report: Dictionary = {"status":"passed" if ok else "failed","id":identifier,"resolution":str(root.size),
		"category":book.app.marginalia.family,"visible_parts":visible_parts,"boxes":str(boxes),
		"legacy_standard_pixels_identical":same,"in_memory_status_only":true,"user_saves":false}
	var stream: FileAccess = FileAccess.open(output.path_join("category-probe.json"),FileAccess.WRITE)
	stream.store_string(JSON.stringify(report,"\t")+"\n")
	print("M2_CATEGORY ",JSON.stringify(report))
	quit(0 if ok else 1)
