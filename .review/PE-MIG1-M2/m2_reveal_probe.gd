extends SceneTree
## Two explicit in-memory completed views; never a user-save migration.
const Store = preload("res://model/save_store.gd")
var output: String
var book: Node3D
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func frames(count: int = 5) -> void:
	for index: int in range(count): await process_frame
func check(ok: bool, label: String) -> void:
	if not ok: failures.append(label)

func run() -> void:
	output = OS.get_environment("M2_OUTPUT")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames(8)
	var cases: Array = []
	for identifier: String in ["pz-00f37200bcee4d548e2c910ce551d077", "pz-023b50b44d1c4698a6e17e65b6ea4337"]:
		check(book.request_open(identifier), "open accepted "+identifier)
		var deadline: int = Time.get_ticks_msec()+20000
		while book.state != book.State.WORK and Time.get_ticks_msec()<deadline: await process_frame
		await frames()
		var session = book.app.session
		var original: Array[int] = session.player.cells.duplicate()
		for y: int in range(session.player.height):
			for x: int in range(session.player.width):
				session.player.cells[y*session.player.width+x] = int(session.definition.solution[y][x])
		check(session.is_solution(), "in-memory solution agrees")
		session.completed = true
		book.app.refresh()
		book.app._layout_book()
		await frames()
		check(book.app.ending.visible and book.app.reveal_view.artwork != null, "real completion artwork visible")
		check(book.app.reveal_view.payload.image == session.definition.reveal.image, "current reveal reference")
		await RenderingServer.frame_post_draw
		var name: String = "reveal-"+identifier+".png"
		var image: Image = root.get_texture().get_image()
		check(image.save_png(output.path_join(name)) == OK, "reveal capture")
		cases.append({"id":identifier,"image":name,"reveal":session.definition.reveal.image,
			"name":session.definition.reveal.name,"revision":session.definition.revision,
			"texture_size":str(book.app.reveal_view.artwork.get_size()),"in_memory_completed_only":true})
		session.completed = false
		session.player.cells = original
		book.app.open_puzzle()
		book.app.refresh()
		await frames()
		check(book.request_return(), "return accepted")
		deadline = Time.get_ticks_msec()+20000
		while book.state != book.State.CATALOG and Time.get_ticks_msec()<deadline: await process_frame
		await frames()
	var report: Dictionary = {"status":"passed" if failures.is_empty() else "failed", "cases":cases,"failures":failures,"user_saves":false}
	var stream: FileAccess = FileAccess.open(output.path_join("reveal-probe.json"),FileAccess.WRITE)
	stream.store_string(JSON.stringify(report,"\t")+"\n")
	print("M2_REVEAL ",JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
