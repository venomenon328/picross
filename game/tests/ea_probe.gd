extends "res://tests/kat2_probe.gd"
## TEST ONLY. Native renderer and actual viewport mouse routes; isolated saves.
var sequence: Array = []
var measurements: Array = []
var motion_images: Array[Image] = []

func event(point: Vector2, down: bool) -> void:
	var input := InputEventMouseButton.new()
	input.position = point
	input.button_index = MOUSE_BUTTON_LEFT
	input.pressed = down
	surface.push_input(input, true)

func cell(point: Vector2i) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(point).get_center()

func prepare(index: int = 2) -> Vector2i:
	app.select_puzzle(index)
	app._ask_reset_id(str(app.session.definition.id), "ending")
	app.reset_dialog.hide()
	app._reset_selected()
	var last := Vector2i.ZERO
	for y: int in range(app.session.player.height):
		for x: int in range(app.session.player.width):
			if app.session.definition.solution[y][x] > 0: last = Vector2i(x, y)
	for y: int in range(app.session.player.height):
		for x: int in range(app.session.player.width):
			var value: int = app.session.definition.solution[y][x]
			if value > 0 and Vector2i(x, y) != last:
				app.session.gesture.begin(app.session.player, Vector2i(x,y), value)
				app.session.finish()
	app.refresh()
	click_at(cell(Vector2i.ZERO),MOUSE_BUTTON_RIGHT)
	app.board.active_color = app.session.definition.solution[last.y][last.x]
	return last

func finish_stroke(last: Vector2i) -> void:
	var origin := Rect2(app.board.position+app.board.view.origin,Vector2(app.session.player.width,app.session.player.height)*app.board.view.cell_size)
	var history: int = app.session.player.history.size()
	event(cell(last), true)
	check(not app.session.completed and app.reveal_view.artwork == null and app.reveal_view.payload.is_empty(), "EA preview cannot load artwork")
	event(cell(last), false)
	check(app.session.completed and app.reveal_view.active and app.session.player.history.size() == history+1, "EA committed stroke completes immediately; one history action")
	check(app.reveal_view.source == origin and app.reveal_view.ink.position == origin.position and app.reveal_view.ink.scale == Vector2.ONE, "EA exact source geometry without fit/zoom jump")
	check(app.reveal_view.ink.commands.size() == app.session.player.cells.filter(func(v: int) -> bool: return v > 0).size(), "EA every confirmed fill including last stroke captured")
	app._undo()
	check(app.session.completed and app.session.player.history.size() == history+1 and app.undo_button.disabled, "EA completed board cannot be undone during fade")
	check(app.completion_title.modulate.a == 0 and app.completion_reset.disabled, "EA name/reset absent until image and no release clickthrough")
	var saved: Dictionary = app.store.load_slot(app.session.definition)
	var restored := Session.new(app.session.definition)
	if saved.status == "loaded": Store.apply(saved.data,restored)
	check(saved.status == "loaded" and restored.completed and restored.player.cells == app.session.player.cells, "EA completion durable before presentation ends")

func final_checks() -> void:
	check(app.ending.visible and not app.work.visible and not app.reveal_view.active and not app.reveal_view.is_processing(), "EA final stable with stopped loop")
	check(app.reveal_view.ink.commands.is_empty() and app.reveal_view.raster.commands.is_empty() and app.reveal_view.ink.material == null, "EA transient commands/material released")
	check(app.title.text == app.session.neutral_title() and app.title.get_theme_font("font") == app.WORK_TITLE_FONT, "EA neutral unchanged heading font")
	check(app.completion_reset.size == Vector2.ONE*44*app.ui_scale and app.completion_reset.image.resource_path == "res://art/book/reset.svg", "EA original reset art and 44/55 target")
	var art: Rect2 = app.reveal_view.artwork_rect()
	check(art.get_center().is_equal_approx(app.reveal_view.area.get_center()) and app.reveal_view.area.grow(0.01).encloses(art), "EA image centered in reserved usable paper")
	check(is_equal_approx(art.size.aspect(),app.reveal_view.artwork.get_size().aspect()), "EA artwork own aspect, no stretching")
	check(art.end.y < app.completion_title.position.y and app.completion_title.get_rect().end.y < app.completion_reset.position.y, "EA name/reset separate reserved rows")
	check(app.completion_title.modulate.a == 1 and not app.completion_reset.disabled, "EA name/reset fully visible after image")

func frame(name: String) -> void:
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	check(image.save_png(output.path_join(name+".png")) == OK, "EA native frame "+name)

func run() -> void:
	output = OS.get_environment("EA_OUTPUT")
	mode = OS.get_environment("EA_MODE")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	surface.notify_mouse_entered()
	await new_app()
	if mode == "restart":
		app.select_puzzle(2)
		await frames()
		check(app.session.completed, "EA actual second process loads completed slot")
		final_checks()
	else:
		for context: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
			surface.size = Vector2i(context[0],context[1])
			app.set_ui_scale(context[2])
			var last := prepare()
			await frames()
			finish_stroke(last)
			var bytes := save_bytes()
			var started := Time.get_ticks_msec()
			var next_frame := 0.0
			var target_rect: Rect2 = app.reveal_view.artwork_rect()
			while app.reveal_view.active:
				await process_frame
				if app.reveal_view.elapsed >= next_frame:
					if context[0] == 1280:
						var name := "motion-%03d" % sequence.size()
						await RenderingServer.frame_post_draw
						motion_images.append(surface.get_texture().get_image())
						sequence.append({"file":name+".png","seconds":app.reveal_view.elapsed})
					next_frame += 0.10
			final_checks()
			check(app.reveal_view.artwork_rect() == target_rect, "EA caption arrival never changes image geometry")
			check(save_bytes() == bytes, "EA presentation never rewrites save/history")
			measurements.append({"window":context,"duration_ms":Time.get_ticks_msec()-started,"source":str(app.reveal_view.source),"area":str(app.reveal_view.area),"art":str(app.reveal_view.artwork_rect())})
			await frame("final-%d" % context[0])
			click(app.completion_reset)
			await frames()
			check(app.reset_dialog.visible and app.reset_origin == "ending", "EA actual reset pointer opens bound dialog")
			click(app.reset_dialog.get_cancel_button())
			await frames()
			check(save_bytes() == bytes and app.ending.visible and app.session.completed, "EA cancel unchanged")
			app.show_album()
			app.select_puzzle(2)
			final_checks()
			check(save_bytes() == bytes, "EA reopen does not persist presentation")
		for i: int in range(motion_images.size()):
			check(motion_images[i].save_png(output.path_join(sequence[i].file)) == OK, "EA buffered actual motion frame")
		motion_images.clear()
		# Rectangular eight-colour raster, long title, independent image aspect.
		var rectangle_last := prepare(5)
		app.session.definition.reveal.name = "TEST ONLY Ein besonders langer deutscher Motivname mit mehreren Wörtern für einen Zeilenumbruch auf der schmalen Papierseite"
		surface.size = Vector2i(1280,720)
		app.set_ui_scale(1.25)
		await frames()
		finish_stroke(rectangle_last)
		app.reveal_view.set_process(false)
		app.reveal_view.elapsed = 1.1
		app.reveal_view.apply_time()
		check(app.reveal_view.raster.modulate.a == 1 and app.reveal_view.art.modulate.a == 0, "EA gapless raster holds before artwork")
		check(is_equal_approx(app.reveal_view.raster_rect().size.aspect(),50.0/30.0), "EA rectangular raster keeps square cells")
		var before_raster: Image
		await RenderingServer.frame_post_draw
		before_raster = surface.get_texture().get_image()
		app.reveal_view.raster.hide()
		await RenderingServer.frame_post_draw
		var paper_only: Image = surface.get_texture().get_image()
		app.reveal_view.raster.show()
		var rect: Rect2 = app.reveal_view.raster_rect()
		var step: float = rect.size.x / app.session.player.width
		for y: int in range(app.session.player.height):
			for x: int in range(app.session.player.width):
				var value: int = app.session.player.cells[y*app.session.player.width+x]
				var sample := Vector2i(rect.position+Vector2(x+0.5,y+0.5)*step)
				var color: Color = app.board.cell_color(value) if value > 0 else paper_only.get_pixelv(sample)
				check(before_raster.get_pixelv(sample).is_equal_approx(color), "EA native raster cell retains exact palette color")
		# Every pixel across the filled row, including all cell boundaries.
		var row_y := int(rect.position.y+2.5*step)
		for pixel_x: int in range(ceili(rect.position.x),floori(rect.end.x)):
			# Native rasterization chooses either adjacent cell at a fractional edge.
			# Require an opaque original neighbor color; paper/blending is a seam.
			var low := clampi(floori((pixel_x-0.5-rect.position.x)/step),0,49)
			var high := clampi(floori((pixel_x+0.5-rect.position.x)/step),0,49)
			var actual := before_raster.get_pixel(pixel_x,row_y)
			var matches := false
			for column: int in range(low,high+1):
				matches = matches or actual.is_equal_approx(app.board.cell_color(app.session.player.cells[2*app.session.player.width+column]))
			check(matches, "EA native filled row has no residual seams")
		app.reveal_view.finish()
		await frames()
		final_checks()
		await frame("rectangle-long-title")
		var landscape := app.reveal_view.artwork
		var portrait_image := Image.create(30,80,false,Image.FORMAT_RGB8)
		portrait_image.fill(Color("6d9dad"))
		app.reveal_view.artwork = ImageTexture.create_from_image(portrait_image)
		var portrait: Rect2 = app.reveal_view.artwork_rect()
		check(is_equal_approx(portrait.size.aspect(),30.0/80.0) and portrait.get_center().is_equal_approx(rect.get_center()), "EA portrait artwork independent of landscape raster, same center")
		app.reveal_view.artwork = landscape
		# Failed final save and mandatory leave flush preserve the visible end/error.
		var failed_last := prepare()
		await frames()
		app._save_current()
		app.store.fail_step = "after_temp"
		event(cell(failed_last), true)
		event(cell(failed_last), false)
		check(app.session.completed and app.status_label.visible and not app.save_error.is_empty(), "EA final-save failure remains explicit")
		app.show_album()
		check(not app.album.visible and app.ending.visible and app.status_label.visible, "EA failed mandatory flush blocks catalog without hiding error")
		app.store.fail_step = ""
		app._save_current()
		app.show_album()
		check(app.album.visible, "EA retry permits normal navigation")
		# Interruption paths and origin-bound reset, including changed selection.
		for interruption: String in ["focus","scale","resize","catalog","switch","web"]:
			var last := prepare()
			await frames()
			finish_stroke(last)
			if interruption in ["catalog","switch"]:
				await create_timer(0.6 if interruption == "catalog" else 1.8).timeout
			match interruption:
				"focus": app._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
				"scale": app.set_ui_scale(1.0)
				"resize": surface.size = Vector2i(1920,1080); await frames()
				"catalog": app.show_album()
				"switch": app.select_puzzle(0)
				"web": app._web_lifecycle([])
			check(not app.reveal_view.active and not app.reveal_view.is_processing(), "EA stop on "+interruption)
			if interruption == "catalog": check(app.album.visible and app.reveal_view.artwork == null, "EA leaving releases image")
			elif interruption == "switch": check(app.work.visible and not app.session.completed and app.reveal_view.artwork == null, "EA switch cannot resurrect old view")
			else: final_checks()
		app.select_puzzle(2)
		var before_failure := save_bytes()
		app.store.fail_step = "reset"
		click(app.completion_reset)
		await frames()
		click(app.reset_dialog.get_ok_button())
		await frames()
		check(app.ending.visible and app.session.completed and app.status_label.visible and save_bytes() == before_failure, "EA failed reset stays visible with recoverable bytes")
		app.store.fail_step = ""
		app._save_current()
		click(app.completion_reset)
		await frames()
		app.select_puzzle(0)
		var other := app.session.player.cells.duplicate()
		click(app.reset_dialog.get_ok_button())
		await frames()
		check(app.session == app.sessions[2] and app.work.visible and not app.session.completed and app.session.player.history.is_empty(), "EA confirmation retains ending origin and selected ID, opens blank same sheet")
		check(app.sessions[0].player.cells == other and app.store.load_slot(app.session.definition).status == "fresh" and app.save_timer.is_stopped(), "EA reset affects only bound slot; no delayed save")
		# Leave completed on disk for a real independent process restart.
		var last := prepare()
		await frames()
		finish_stroke(last)
		app.reveal_view.finish()
		app.show_album()
	var report := {"checks":checks,"failures":failures,"sequence":sequence,"measurements":measurements,"test_only":true,"mode":mode}
	var file := FileAccess.open(output.path_join(mode+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")+"\n")
	file.close()
	if failures.is_empty(): print("EA_PROBE_OK ",checks)
	app.free()
	quit(0 if failures.is_empty() else 23)
