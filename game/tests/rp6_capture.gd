extends "res://tests/rp6_probe.gd"
const Measurements = preload("res://tests/vs2_measurements.gd")
## Native images; completion loads the preceding real mouse/process probe saves.
var surface: SubViewport
var output: String
var captures: Array = []
var failure_captures: Array = []
var pending_failures: Array[String] = []
var assertions: Array = []

func check(condition: bool, description: String) -> void:
	super.check(condition, description)
	assertions.append({"label":description,"passed":condition})
	if not condition:
		pending_failures.append(description)

func write_report() -> void:
	var report: FileAccess = FileAccess.open(output.path_join("rp6-t%02d-renders.json" % [int(app.session.definition.id.trim_prefix("T-"))]),FileAccess.WRITE)
	if report == null:
		check(false, "RP6 render report could not be written")
		quit(4)
		return
	report.store_string(JSON.stringify({"checks":checks,"failures":failures,"captures":captures,"failure_captures":failure_captures,"pending_failures":pending_failures,"pending_assertions":assertions},"\t") + "\n")

func pixel(image: Image, point: Vector2, expected: Color, role: String, samples: Dictionary) -> void:
	var actual: Color = image.get_pixelv(Vector2i(point))
	samples[role] = actual.to_html(false)
	check(actual.is_equal_approx(expected), "native pixel " + role)

func shot(name: String) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	var filename: String = "rp6-t%02d-%s.png" % [int(app.session.definition.id.trim_prefix("T-")), name]
	var samples: Dictionary = {}
	if name.begins_with("work-"):
		# Interior own wrong cells remain measurable in the largest supported miniature.
		var step: float = app.mini.image_rect().size.x / app.session.player.width
		var point: Vector2i = Vector2i(app.mini.global_position + Vector2(3.5,3.5)*step)
		pixel(image,Vector2(point),Color(app.session.definition.palette[0].color),"wrong-block",samples)
		check(app.board.clue_font().get_font_name() == "Delight Coffee", "bound regular clue font")
		check(not app.minimum_message.visible and app.work.visible, "work and critical controls accessible")
		if not app.board.layout_valid:
			check(app.layout_warning.text.contains("Zu wenig Platz") and not app.board.marks.visible,"invalid geometry is explicit and has no marks")
		for control: Control in [app.palette_row,app.mini,app.tools_scroll]:
			check(Rect2(Vector2.ZERO,Vector2(surface.size)).encloses(control.get_global_rect()), "controls on surface")
		var scroll_before: int = app.tools_scroll.scroll_vertical
		for control: Control in [app.undo_button,app.redo_button]:
			app.tools_scroll.ensure_control_visible(control)
			await process_frame
			await process_frame
			check(app.tools_scroll.get_global_rect().encloses(control.get_global_rect()),"V3 history controls reachable inside clipped rail %s control%s rail%s scroll%s" % [control.name,control.get_global_rect(),app.tools_scroll.get_global_rect(),app.tools_scroll.scroll_vertical])
		app.tools_scroll.scroll_vertical=scroll_before
		await process_frame
	elif name.begins_with("detail-") or name.begins_with("album-partial-"):
		var preview: Control = app.album_previews[app.album.visible_ids.find(str(app.session.definition.id))] if app.album.visible else app.mini
		var rect: Rect2 = preview.image_rect()
		pixel(image,preview.global_position+rect.position+Vector2.ONE*rect.size.x/app.session.player.width*0.5,Color(app.session.definition.palette[0].color),"wrong-corner",samples)
		check(app.session.reveal().is_empty(),"selected partial has no reveal")
	else:
		var reveal: Control = app.album_reveals[app.album.visible_ids.find(str(app.session.definition.id))] if app.album.visible else app.reveal_view
		var rect: Rect2 = reveal.artwork_rect()
		check(reveal.is_visible_in_tree() and rect.has_area() and is_equal_approx(rect.size.x,rect.size.y),"selected earned artwork visible and proportional")
		check(reveal.payload == app.session.definition.reveal,"selected earned artwork bound to slot")
		pixel(image,reveal.global_position+rect.get_center(),Color.WHITE,"reveal-center",samples)
		var background := Color("6c9aab") if pilot_index == 2 else Color("edca78")
		pixel(image,reveal.global_position+rect.position+rect.size*0.1,background,"reveal-background",samples)
	captures.append({"id":name,"definition_id":app.session.definition.id,
		"slot":app.store.path_for(app.store.key_for_definition(app.session.definition.id)).get_file(),
		"size":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,
		"completed":app.session.completed,"reveal":app.session.reveal(),
		"palette":app.session.definition.palette,"own_miniature":app.mini.cells.duplicate(),
		"font":app.board.clue_font().get_font_name(),
		"layout_valid":app.board.layout_valid,"grid_fit":Measurements.capture(app.board).grid_fit,
		"pixels":samples,"assertions":assertions.duplicate(true),"checks":assertions.size()})
	assertions.clear()
	if not pending_failures.is_empty():
		image.save_png(output.path_join(filename))
		failure_captures.append({"file":filename,"reasons":pending_failures.duplicate(),"crop":false})
		pending_failures.clear()
		write_report()

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	pilot_index = int(OS.get_environment("RP6_INDEX"))
	if pilot_index not in [2,3]:
		push_error("RP6 capture only selects T04 and T06")
		quit(4)
		return
	var selected_specs: Array = [[1920,1080,1.0]] if pilot_index == 2 else [[1280,720,1.25]]
	SaveStore.test_root_override = "user://rp6-capture-%d-%d" % [pilot_index,Time.get_ticks_usec()]
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	await setup(surface)
	partial()
	for spec: Array in selected_specs:
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
		app.tools_scroll.ensure_control_visible(app.undo_button)
		await process_frame
		await process_frame
		var undo_cursor: int = app.session.player.cursor
		for i: int in range(9):
			click(app.undo_button.get_global_rect().get_center())
		check(app.session.player.cursor==undo_cursor-9,"nine real visible undo clicks remove the wrong block")
		if invalid_geometry:
			surface.size = Vector2i(spec[0],spec[1])
			app.size = Vector2(surface.size)
			app.set_ui_scale(spec[2])
			await select_pilot()
		app.tools_scroll.ensure_control_visible(app.actions["plus"])
		await process_frame
		await process_frame
		click(app.actions["plus"].get_global_rect().get_center())
		check(not app.board.overview,"real visible plus click retains normal zoom")
		await shot("detail-%d-ui%d" % [spec[0],spec[2]*100])
		app.show_album()
		await process_frame
		await process_frame
		await process_frame
		# Every slot can be brought into view, including the bottom row at 125%.
		for choice: Button in app.choices:
			app.album.ensure_control_visible(choice)
			await process_frame
			await process_frame
			var scroller: ScrollContainer = app.album.right_scroll if app.album.right_grid.is_ancestor_of(choice) else app.album.scroll
			# Measure inside the actual clip's coordinate system. Adding the
			# fractional projected paper origin separately to each global edge
			# can create a one-float-ULP overrun even at identical local edges.
			var bounds := Rect2(Vector2.ZERO,choice.size)
			var item: CanvasItem = choice
			while item != scroller:
				bounds = item.get_transform()*bounds
				item = item.get_parent() as CanvasItem
			check(Rect2(Vector2.ZERO,scroller.size).encloses(bounds), "all six choices reachable inside their scroll viewport: %s card%s viewport%s" % [choice.leaf.text,bounds,scroller.size])
		check(app.album_reveals[app.album.visible_ids.find(str(app.sessions[pilot_index].definition.id))].payload.is_empty(), "album no hidden reveal payload")
		app.album.ensure_control_visible(app.album_previews[app.album.visible_ids.find(str(app.session.definition.id))])
		await shot("album-partial-%d-ui%d" % [spec[0],spec[2]*100])
	surface.size = Vector2i(1920,1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	check(app._flush_current(), "capture partial flush")
	preload("res://tests/book_fixture.gd").dispose(app,true)
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
	check(app.store.load_slot(app.session.definition).status == "loaded","capture completion slot freshly loaded")
	for spec: Array in selected_specs:
		surface.size = Vector2i(spec[0],spec[1])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[2])
		app.open_puzzle()
		await shot("completion-%d-ui%d" % [spec[0],spec[2]*100])
		app.show_album()
		# Album card layout must settle before scrolling to the actual artwork.
		# The containing card can be taller than the tight UI125 viewport.
		await process_frame
		await process_frame
		await process_frame
		app.album.ensure_control_visible(app.album_reveals[app.album.visible_ids.find(str(app.session.definition.id))])
		await shot("album-completed-%d-ui%d" % [spec[0],spec[2]*100])
	write_report()
	if failures == 0:
		print("RP6_CAPTURE_OK")
	quit(0 if failures == 0 else 4)
