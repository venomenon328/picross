extends "res://tests/rp3_probe.gd"
var surface: SubViewport
var output: String
var captures: Array = []

func shot(name: String) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	check(image.save_png(output.path_join("rp3-" + name + ".png")) == OK, "render file " + name)
	captures.append({"file":"rp3-" + name + ".png", "size":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,"completed":app.session.completed,"own_miniature":app.mini.cells.duplicate(),"reveal":app.session.reveal()})
	if name.begins_with("work-"):
		# Sample the deliberate wrong own pixel away from miniature frame/border.
		var inset: float = app.mini.image_rect().size.x / 20.0 * 0.7
		var point: Vector2i = Vector2i(app.mini.global_position + Vector2(inset,inset))
		check(image.get_pixelv(point).is_equal_approx(Color(app.session.definition.palette[0].color)), "actual miniature renders wrong own fill")

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	SaveStore.test_root_override = "user://rp3-capture-%d" % Time.get_ticks_usec()
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	await setup(surface)
	partial()
	await shot("album-partial")
	for spec: Array in [[1920,1080,1.0],[1280,720,1.25]]:
		surface.size = Vector2i(spec[0],spec[1])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[2])
		app.select_puzzle(3)
		app.board.fit_all()
		await shot("work-%d-ui%d" % [spec[0],spec[2]*100])
	surface.size = Vector2i(1920,1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(3)
	app.board.fit_all()
	finish()
	app.open_puzzle()
	await shot("completion")
	app.show_album()
	await shot("album-completed")
	var report: FileAccess = FileAccess.open(output.path_join("rp3-renders.json"),FileAccess.WRITE)
	report.store_string(JSON.stringify({"checks":checks,"failures":failures,"captures":captures},"\t") + "\n")
	if failures == 0:
		print("RP3_CAPTURE_OK")
	quit(0 if failures == 0 else 4)
