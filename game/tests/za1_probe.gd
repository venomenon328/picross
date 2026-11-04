extends "res://tests/rp6_probe.gd"
## Artificial registrations, actual main scene/input, isolated profile, real restarts.
var output: String
var captures: Array = []
var surface: SubViewport

func setup(viewport: Viewport) -> void:
	target = viewport
	app = preload("res://tests/book_fixture.gd").attach(target)
	await process_frame
	await process_frame
	check(app.sessions.size() == Definition.catalog_ids().size() and app.sessions.size() >= 10, "old plus four artificial registrations")
	var id: String = OS.get_environment("ZA1_ID")
	pilot_index = -1
	for i: int in range(app.sessions.size()):
		if app.sessions[i].definition.id == id: pilot_index = i
	check(pilot_index >= 6, "new exact neutral ID registered")
	check(Definition.load_fixture("unknown").is_empty() and Definition.load_fixture(id.to_upper()).is_empty(), "unknown and alias IDs rejected")
	check(app.store.path_for("unknown").is_empty() and app.store.path_for(id,"../json").is_empty(), "unknown and suffix traversal save access rejected")
	check(app.store.key_for_definition(id) == id and app.store.path_for(id).get_file() == "slot_"+id+".json", "explicit lossless slot")
	for session: RefCounted in app.sessions:
		check(Definition.validate(session.definition).is_empty(), "registered definition validated")
	await select_pilot()

func shot(stage: String) -> void:
	# Contrast/pixel oracle describes the final view; EA covers the moving phases.
	while app.reveal_view.active: await process_frame
	app.refresh()
	await process_frame
	await process_frame
	if app.album.visible:
		var index: int = app.album.visible_ids.find(str(app.session.definition.id))
		var observed: Control = app.album_reveals[index] if app.session.completed else app.album_previews[index]
		# The compact book half scrolls independently. Observe the actual visible
		# miniature/reveal rather than pixels of a clipped card below its viewport.
		app.album.ensure_control_visible(observed)
		await process_frame
		await process_frame
		var scroller: ScrollContainer = app.album.right_scroll if app.album.right_grid.is_ancestor_of(observed) else app.album.scroll
		check(scroller.get_global_rect().encloses(observed.get_global_rect()),"native observed album image entirely visible")
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	var ratio: float = float(app.session.player.width)/app.session.player.height
	var mini: Rect2 = app.mini.image_rect()
	check(is_equal_approx(mini.size.x/mini.size.y,ratio), "rectangular miniature has square cells")
	var cell: Rect2 = app.board.view.cell_rect(Vector2i.ZERO)
	check(is_equal_approx(cell.size.x,cell.size.y), "regular rectangular board has square cells")
	var earned: bool = app.session.completed
	if not earned:
		check(app.session.reveal().is_empty() and app.album_reveals[app.album.visible_ids.find(str(app.sessions[pilot_index].definition.id))].payload.is_empty() and app.reveal_view.payload.is_empty(), "all unsolved reveal payloads absent")
		var artwork_pixels: int = 0
		for y: int in range(image.get_height()):
			for x: int in range(image.get_width()):
				if image.get_pixel(x,y).is_equal_approx(Color8(76,145,93)): artwork_pixels += 1
		check(artwork_pixels == 0, "native unsolved/partial pixels contain no artificial artwork")
		if stage == "partial":
			var preview: Control = app.album_previews[app.album.visible_ids.find(str(app.sessions[pilot_index].definition.id))]
			var step: float = preview.image_rect().size.x/app.session.player.width
			var point: Vector2i = Vector2i(preview.global_position + Vector2.ONE*step*0.5)
			check(image.get_pixelv(point).is_equal_approx(Color(app.session.definition.palette[0].color)), "native own wrong album cell pixel retained")
	else:
		var reveal: Control = app.album_reveals[app.album.visible_ids.find(str(app.sessions[pilot_index].definition.id))] if app.album.visible else app.reveal_view
		var art: Rect2 = reveal.artwork_rect()
		check(is_equal_approx(art.size.x/art.size.y,ratio), "native reveal preserves rectangle aspect")
		check(image.get_pixelv(Vector2i(reveal.global_position+art.get_center())).is_equal_approx(Color8(76,145,93)), "native earned artwork interior pixel")
		if reveal.paired:
			var grid: Rect2 = reveal.raster_rect()
			check(is_equal_approx(grid.size.x/grid.size.y,ratio), "native solved raster preserves square cells")
			var step: float = grid.size.x/app.session.player.width
			for y: int in range(app.session.player.height):
				for x: int in range(app.session.player.width):
					var expected: Color = Color("faf6ec")
					for entry: Dictionary in app.session.definition.palette:
						if int(entry.id) == int(app.session.definition.solution[y][x]): expected = Color(entry.color)
					check(image.get_pixelv(Vector2i(reveal.global_position+grid.position+Vector2(x+0.5,y+0.5)*step)).is_equal_approx(expected), "native solved raster cell/color")

func seed_old() -> void:
	for index: int in [0,1,3]:
		app.select_puzzle(index)
		app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
		await process_frame
		click(cell_point(Vector2i.ZERO))
		check(app.session.player.cells[0] == 1 and app._flush_current(), "real old slot partial seed")

func reset_selected() -> void:
	app.show_album()
	app._ask_reset()
	await process_frame
	app.reset_dialog.confirmed.emit()
	app.reset_dialog.hide()
	await process_frame
	check(not app.session.completed and app.session.player.cells.count(-1) == app.session.player.width*app.session.player.height, "confirmed selected reset clears only current new slot")

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	output = OS.get_environment("ZA1_OUTPUT")
	if isolated.is_empty() or output.is_empty(): quit(4); return
	SaveStore.test_root_override = isolated
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	await setup(surface)
	var others: Array = []
	for session: RefCounted in app.sessions: others.append(session.player.cells.duplicate())
	var stage: String = OS.get_environment("ZA1_STAGE")
	if stage == "seed":
		await seed_old()
	elif stage == "partial":
		await shot("unstarted")
		partial()
		await process_frame
		await shot("partial")
	elif stage == "finish":
		finish()
		app.open_puzzle()
		await shot("completion")
	elif stage == "read":
		restored()
		app.album.ensure_control_visible(app.choices[app.album.visible_ids.find(str(app.sessions[pilot_index].definition.id))])
		await shot("album")
	elif stage == "reset":
		await reset_selected()
	elif stage == "oldreset":
		app.select_puzzle(0)
		await reset_selected()
	else: check(false,"unknown ZA1 stage")
	if stage != "seed":
		for i: int in range(app.sessions.size()):
			if i != (0 if stage == "oldreset" else pilot_index): check(others[i] == app.sessions[i].player.cells,"foreign slot cells unchanged")
	check(app._flush_current(), "mandatory final write")
	var report: FileAccess = FileAccess.open(output.path_join(OS.get_environment("ZA1_ID")+"-"+stage+".json"),FileAccess.WRITE)
	report.store_string(JSON.stringify({"checks":checks,"failures":failures,"stage":stage,"captures":captures})+"\n")
	if failures == 0: print("ZA1_PROBE_OK")
	quit(0 if failures == 0 else 4)
