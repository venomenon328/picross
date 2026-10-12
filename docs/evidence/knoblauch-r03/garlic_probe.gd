extends "res://tests/rp6_probe.gd"
## Disposable verification of the actual registered garlic content.
var surface: SubViewport
var captures: Array = []
var output: String

func setup(viewport: Viewport) -> void:
	pilot_index = Definition.catalog_ids().find("pz-3a744ae1b7cb4d38b0ac29d030ef")
	check(pilot_index == 6, "exact new ID follows unchanged historical prefix")
	await super.setup(viewport)
	check(app.sessions.size() == 7, "seven visible regular sheets")
	check(app.session.definition.id == "pz-3a744ae1b7cb4d38b0ac29d030ef" and app.session.definition.revision == 1, "production ID and runtime revision")
	check(app.session.player.width == 40 and app.session.player.height == 40, "selected dimensions 40x40")
	check(app.store.path_for(app.session.definition.id).get_file() == "knoblauch_001.json", "explicit isolated save slot")
	check(app.session.definition.reveal.image == "res://art/content/knoblauch_001.png", "exact original reveal resource")
	check(Definition.load_fixture("unknown").is_empty() and app.store.path_for("unknown").is_empty(), "unknown IDs rejected")
	if not app.session.completed:
		check(app.choices[pilot_index].text == "Blatt 10 · 40 × 40", "selection has neutral size-labelled title; historical reservations retain their numbering")
		check(app.session.player.cells.count(-1) == 1600 or app.session.player.cells.count(1) == 1, "fresh or saved partial matrix")

func shot(stage: String) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	var mini: Rect2 = app.mini.image_rect()
	check(is_equal_approx(mini.size.x, mini.size.y), "40x40 miniature proportions")
	var cell: Rect2 = app.board.view.cell_rect(Vector2i.ZERO)
	check(is_equal_approx(cell.size.x,cell.size.y), "square runtime cells")
	var areas: Array = []
	if app.session.completed:
		var reveal: Control = app.album_reveals[pilot_index] if app.album.visible else app.reveal_view
		var art: Rect2 = reveal.artwork_rect()
		check(reveal.payload == app.session.definition.reveal and reveal.artwork.get_width() == 1254 and reveal.artwork.get_height() == 1254, "bound original artwork dimensions")
		check(is_equal_approx(art.size.x,art.size.y), "proportional earned artwork")
		areas.append({"kind":"artwork","rect":Rect2(reveal.global_position+art.position,art.size)})
		if reveal.paired:
			var grid: Rect2 = reveal.raster_rect()
			check(is_equal_approx(grid.size.x,grid.size.y), "proportional solved raster")
			var step: float = grid.size.x / 40
			for y: int in range(40):
				for x: int in range(40):
					var expected: Color = Color("faf6ec") if int(app.session.definition.solution[y][x]) == 0 else Color(app.session.definition.palette[0].color)
					var point: Vector2i = Vector2i(reveal.global_position+grid.position+Vector2(x+0.5,y+0.5)*step)
					check(image.get_pixelv(point).is_equal_approx(expected), "exact native solved cell %d,%d" % [x,y])
			areas.append({"kind":"raster","rect":Rect2(reveal.global_position+grid.position,grid.size)})
	else:
		check(app.session.reveal().is_empty() and app.reveal_view.payload.is_empty() and app.album_reveals[pilot_index].payload.is_empty(), "no reveal payload before completion")
		check(app.reveal_view.artwork == null and app.album_reveals[pilot_index].artwork == null, "no artwork texture before completion")
		check(not app.title.text.contains("Knoblauch") and not app.choices[pilot_index].text.contains("Knoblauch"), "no motif name before completion")
		var preview: Control = app.album_mini if app.album.visible else app.mini
		var rect: Rect2 = preview.image_rect()
		areas.append({"kind":"own-miniature","rect":Rect2(preview.global_position+rect.position,rect.size)})
		if stage == "partial":
			var point: Vector2i = Vector2i(preview.global_position+rect.position+Vector2.ONE*(rect.size.x/80))
			check(image.get_pixelv(point).is_equal_approx(Color(app.session.definition.palette[0].color)), "wrong own album pixel remains visible")
	var context: String = stage+"-context.png"
	check(image.save_png(output.path_join(context)) == OK, "native full context saved")
	for item: Dictionary in areas:
		var area: Rect2 = item.rect
		var filename: String = stage+"-"+str(item.kind)+".png"
		check(image.get_region(Rect2i(area)).save_png(output.path_join(filename)) == OK, "native original crop saved")
		captures.append({"file":filename,"context":context,"kind":item.kind,"crop_rect":[area.position.x,area.position.y,area.size.x,area.size.y],"native_size":[1920,1080],"stage":stage})

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	output = OS.get_environment("GARLIC_OUTPUT")
	if isolated.is_empty() or output.is_empty(): quit(4); return
	SaveStore.test_root_override = isolated
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	await setup(surface)
	var stage: String = OS.get_environment("GARLIC_STAGE")
	var others: Array = []
	for session: RefCounted in app.sessions: others.append(session.player.cells.duplicate())
	if stage == "seed":
		for index: int in [0,1,3]:
			app.select_puzzle(index)
			app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
			await process_frame
			click(cell_point(Vector2i.ZERO))
			check(app.session.player.cells[0] == 1 and app._flush_current(), "seed disposable historical slot with real input")
	elif stage == "partial":
		await shot("unstarted")
		partial()
		await shot("partial")
	elif stage == "finish":
		finish()
		app.open_puzzle()
		await shot("completion")
	elif stage == "read":
		restored()
		app.album.ensure_control_visible(app.choices[pilot_index])
		await shot("album")
	elif stage == "reset":
		app.show_album()
		app._ask_reset()
		await process_frame
		app.reset_dialog.confirmed.emit()
		app.reset_dialog.hide()
		await process_frame
		check(not app.session.completed and app.session.player.cells.count(-1) == 1600, "confirmed reset only new slot")
	else: check(false,"unknown stage")
	if stage != "seed":
		for i: int in range(app.sessions.size()):
			if i != pilot_index: check(others[i] == app.sessions[i].player.cells,"other session unchanged")
	check(app._flush_current(),"final mandatory flush")
	var report: FileAccess = FileAccess.open(output.path_join(stage+".json"),FileAccess.WRITE)
	report.store_string(JSON.stringify({"checks":checks,"failures":failures,"stage":stage,"captures":captures})+"\n")
	if failures == 0: print("GARLIC_PROBE_OK stage=",stage," checks=",checks)
	quit(0 if failures == 0 else 4)
