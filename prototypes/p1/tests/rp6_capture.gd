extends "res://tests/rp6_probe.gd"
const Measurements = preload("res://tests/vs2_measurements.gd")
## Native images; completion loads the preceding real mouse/process probe saves.
var surface: SubViewport
var output: String
var captures: Array = []
var failure_captures: Array = []
var pending_failures: Array[String] = []

func check(condition: bool, description: String) -> void:
	super.check(condition, description)
	if not condition:
		pending_failures.append(description)

func write_report() -> void:
	var report: FileAccess = FileAccess.open(output.path_join("rp6-f%02d-renders.json" % [pilot_index+1]),FileAccess.WRITE)
	if report == null:
		check(false, "RP6 render report could not be written")
		quit(4)
		return
	report.store_string(JSON.stringify({"checks":checks,"failures":failures,"captures":captures,"failure_captures":failure_captures,"pending_failures":pending_failures},"\t") + "\n")

func shot(name: String) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	var filename: String = "rp6-f%02d-%s.png" % [pilot_index + 1, name]
	check(image.save_png(output.path_join(filename)) == OK, "native render " + filename)
	captures.append({"file":filename,"size":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,
		"completed":app.session.completed,"reveal":app.session.reveal(),
		"palette":app.session.definition.palette,"own_miniature":app.mini.cells.duplicate(),
		"font":app.board.clue_font().get_font_name(),"c1_color_ids":[2,4],
		"layout_valid":app.board.layout_valid,"grid_fit":Measurements.capture(app.board).grid_fit,
		"geometry_status":"fit_owner_open" if app.board.layout_valid else "too_little_space"})
	if name.begins_with("work-"):
		# Interior own wrong cells remain measurable even in a 100-cell miniature.
		var step: float = app.mini.image_rect().size.x / app.session.player.width
		var point: Vector2i = Vector2i(app.mini.global_position + Vector2(3.5,3.5)*step)
		check(image.get_pixelv(point).is_equal_approx(Color(app.session.definition.palette[0].color)), "native own wrong miniature pixel")
		check(app.board.clue_font().get_font_name() == "Chalkboard", "bound regular clue font")
		check(not app.minimum_message.visible and app.work.visible, "work and critical controls accessible")
		if not app.board.layout_valid:
			check(app.zoom_label.text.contains("Zu wenig Platz") and not app.board.marks.visible,"invalid geometry is explicit and has no marks")
		for control: Control in [app.undo_button,app.redo_button,app.palette_row,app.mini]:
			check(Rect2(Vector2.ZERO,Vector2(surface.size)).encloses(control.get_global_rect()), "controls on surface")
	if not pending_failures.is_empty():
		failure_captures.append({"file":filename,"reasons":pending_failures.duplicate(),"crop":false})
		pending_failures.clear()
		write_report()

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	pilot_index = int(OS.get_environment("RP6_INDEX"))
	SaveStore.test_root_override = "user://rp6-capture-%d-%d" % [pilot_index,Time.get_ticks_usec()]
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	await setup(surface)
	partial()
	for spec: Array in [[1920,1080,1.0],[1280,720,1.25]]:
		surface.size = Vector2i(spec[0],spec[1])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[2])
		await select_pilot()
		var invalid_geometry: bool = not app.board.layout_valid
		if invalid_geometry:
			# Prepare the same own wrong 3x3 block at a valid regular surface.
			# The small surface must display it passively and reject input.
			surface.size = Vector2i(1920,1080)
			app.size = Vector2(surface.size)
			app.set_ui_scale(1.0)
			await select_pilot()
			for y: int in range(2,5):
				for x: int in range(2,5): click(cell_point(Vector2i(x,y)))
			surface.size = Vector2i(spec[0],spec[1])
			app.size = Vector2(surface.size)
			app.set_ui_scale(spec[2])
			await select_pilot()
		var before_cells: Array = app.session.player.cells.duplicate()
		var before_history: Array = app.session.player.history.duplicate(true)
		var before_cursor: int = app.session.player.cursor
		# Same own mistakes in each view, set via normal input and undo after capture.
		for y: int in range(2,5):
			for x: int in range(2,5):
				click(cell_point(Vector2i(x,y)))
		if invalid_geometry:
			check(app.session.player.cells == before_cells and app.session.player.history == before_history and app.session.player.cursor == before_cursor,"invalid small surface rejects real cell input without history loss")
		await shot("work-%d-ui%d" % [spec[0],spec[2]*100])
		if invalid_geometry:
			surface.size = Vector2i(1920,1080)
			app.size = Vector2(surface.size)
			app.set_ui_scale(1.0)
			await select_pilot()
		for i: int in range(9):
			click(app.undo_button.get_global_rect().get_center())
		if invalid_geometry:
			surface.size = Vector2i(spec[0],spec[1])
			app.size = Vector2(surface.size)
			app.set_ui_scale(spec[2])
			await select_pilot()
		click(app.actions["work"].get_global_rect().get_center())
		await shot("detail-%d-ui%d" % [spec[0],spec[2]*100])
		app.show_album()
		await process_frame
		# Every slot can be brought into view, including the bottom row at 125%.
		for choice: Button in app.choices:
			app.album.ensure_control_visible(choice)
			await process_frame
			check(app.album.get_global_rect().encloses(choice.get_global_rect()), "all nine choices reachable")
		check(app.album_reveals[pilot_index].payload.is_empty(), "album no hidden reveal payload")
		await shot("album-partial-%d-ui%d" % [spec[0],spec[2]*100])
	surface.size = Vector2i(1920,1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	check(app._flush_current(), "capture partial flush")
	app.queue_free()
	await process_frame
	var completed_root: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if completed_root.is_empty():
		check(false, "capture requires preceding real completion saves")
		write_report()
		quit(4)
		return
	SaveStore.test_root_override = completed_root
	await setup(surface)
	check(app.session.completed and app.session.is_solution(), "native capture restores real mouse completion")
	for spec: Array in [[1920,1080,1.0],[1280,720,1.25]]:
		surface.size = Vector2i(spec[0],spec[1])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[2])
		app.open_puzzle()
		await shot("completion-%d-ui%d" % [spec[0],spec[2]*100])
		app.show_album()
		app.album.ensure_control_visible(app.choices[pilot_index])
		await shot("album-completed-%d-ui%d" % [spec[0],spec[2]*100])
	write_report()
	if failures == 0:
		print("RP6_CAPTURE_OK")
	quit(0 if failures == 0 else 4)
