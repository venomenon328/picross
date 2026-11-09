extends "res://tests/rand_visual.gd"

func run() -> void:
	output = OS.get_environment("RAND_VISUAL_OUTPUT")
	DirAccess.make_dir_recursive_absolute(output)
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	surface = root
	surface.size = Vector2i(1920,1080)
	surface.gui_embed_subwindows = true
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames(12)
	await resize(1920,1080,1.25)
	await open_id("pz-test-kat2-053")
	app.board.requested_cell = 72
	app._layout_book()
	await frames()
	var independent: bool = false
	for config: Vector3 in [Vector3(1920,1080,1),Vector3(1600,900,1),Vector3(2560,1440,1.25)]:
		await resize(int(config.x),int(config.y),config.z)
		var visible_count: int = int(app.marginalia.boxes[0].has_area())+int(app.marginalia.boxes[1].has_area())
		print("RAND_INDEPENDENT_PROBE work ",config," count=",visible_count)
		if visible_count == 1:
			await comparison("independent-work")
			independent = true
			break
	if not independent:
		click(app.actions.help)
		await settle()
		for config: Vector3 in [Vector3(1600,900,1.25),Vector3(1280,720,1),Vector3(1600,900,1),Vector3(1920,1080,1.25)]:
			await resize(int(config.x),int(config.y),config.z)
			var visible_count: int = int(app.marginalia.boxes[0].has_area())+int(app.marginalia.boxes[1].has_area())
			print("RAND_INDEPENDENT_PROBE help ",config," count=",visible_count)
			if visible_count == 1:
				await comparison("independent-help")
				independent = true
				break
		click(app.actions["nav-work"])
		await settle()
	check(independent,"native layout independently omits one drawing")
	await back()
	await resize(2560,1440,1)
	await open_id("pz-test-kat2-051")
	var found: bool = false
	var best_overlap: float = 0
	var best_step: int = 0
	var samples: Array = []
	for step: int in [30,32,34,35,36,37,38,39,40,42,44]:
		app.board.requested_cell = step
		app._layout_book()
		await frames()
		var ink: Rect2 = app.board.composition_envelope()
		ink.position += app.board.position
		var overlap: float = 0
		for box: Rect2 in app.marginalia.boxes:
			if box.has_area(): overlap = maxf(overlap,ink.intersection(box).get_area())
		samples.append({"request":step,"actual":app.board.view.cell_size,"overlap_area":overlap})
		if overlap > best_overlap:
			best_step = step
			best_overlap = overlap
	if best_step > 0:
		found = true
		app.board.requested_cell = best_step
		app._layout_book()
		await frames()
		await comparison("shallow-grid-overlap-1440-ui100")
	check(found,"real valid rectangular puzzle/zoom produces shallow retained overlap for paper/contrast assessment")
	var passed: bool = true
	for item: Dictionary in assertions:
		if not item.ok: passed = false
	var file := FileAccess.open(output.path_join("native-extra.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"package":"RAND-P1","head":OS.get_environment("RAND_PRODUCT_HEAD"),"engine":Engine.get_version_info(),"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"test_only":true,"unmodified_product_root":true,"physical_os_mouse":false,"assertions":assertions,"samples":samples,"records":records,"passed":passed},"  ")+"\n")
	file.close()
	print("RAND_EXTRA_OK" if passed else "RAND_EXTRA_FAILED")
	quit(0 if passed else 1)
