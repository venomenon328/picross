extends "E:/Zeuch/Coding/picross_codex/558-rz-eval-p1/temp/rz_probe.gd"
func run() -> void:
	output = OS.get_environment("RZ_OUTPUT")
	DirAccess.make_dir_recursive_absolute(output)
	root.size = Vector2i(1280,720)
	surface = SubViewport.new()
	surface.size = Vector2i(2560,1440)
	surface.own_world_3d = true
	surface.gui_embed_subwindows = true
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames()
	var id: String = "pz-20ecf7747bbf40828238ec26d1207172"
	await open_id(id,0)
	resource_record("mono-first-open")
	await close_id()
	await open_id(id,0)
	resource_record("mono-same-image-reopened")
	check(app.rz_eval.load_count == 2,"same illustration is reloaded without an unbounded cache")
	for cell: Vector2i in [Vector2i(10,28),Vector2i(11,28),Vector2i(12,28)]:
		pointer(app.board.global_position+app.board.view.cell_rect(cell).get_center())
		await frames()
	pointer(app.board.global_position+app.board.view.cell_rect(Vector2i(13,28)).get_center(),MOUSE_BUTTON_RIGHT)
	await frames()
	check(app.session.player.cursor == 4,"mono pointer fills and X pass through drawing")
	for i: int in range(20):
		pointer(app.actions.plus.get_global_rect().get_center())
		await frames()
	var bounds: Array = geometry()
	var cells: Array = app.session.player.cells.duplicate()
	var color: Color
	for mode: int in range(4):
		app.rz_eval.mode = mode
		app.rz_eval.queue_redraw()
		await snapshot("mono-overlap-%d" % mode)
		resource_record("mono-overlap-%d" % mode)
		var point: Vector2 = app.board.global_position+app.board.view.cell_rect(Vector2i(10,28)).get_center()
		var actual: Color = surface.get_texture().get_image().get_pixelv(Vector2i(point))
		if mode == 0: color = actual
		else: check(actual == color,"functional black fill pixel unchanged for mode %d" % mode)
		check(bounds == geometry() and cells == app.session.player.cells,"mono mode changes preserve geometry and all cells")
	await close_id()
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"records":records,"black_pixel":str(color),"failures":failures},"\t"))
	file.close()
	print("RZ_MONO_DONE failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
