extends SceneTree
const Session = preload("res://model/session.gd")
var app: Control
var canvas: SubViewport
var records: Array = []
var pictures: Array = []
var failures: int = 0
var output: String
var diagnostics: Array = []

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		printerr("VS1 CAPTURE FAIL: ", message)

func shot(name: String) -> void:
	app.board.clear_pointer_hover()
	app.board.clear_effects()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var path: String = name + ".png"
	check(canvas.get_texture().get_image().save_png(output.path_join(path)) == OK, "PNG write")
	pictures.append({"file": path, "sha256": FileAccess.get_sha256(output.path_join(path)), "id": app.session.definition.id, "mode": app.board.mode, "ui_scale": app.ui_scale, "client": [canvas.size.x, canvas.size.y], "own_cells_sha256": JSON.stringify(app.session.player.cells).sha256_text()})

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	OS.set_environment("VS1_TEST_ROOT", OS.get_user_data_dir().path_join("vs1-capture-%d" % Time.get_ticks_usec()))
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920, 1080)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	app = load("res://full_view_study/main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	for extent: Vector2i in [Vector2i(1920,1080), Vector2i(1280,720), Vector2i(2560,1440)]:
		canvas.size = extent
		app.size = Vector2(extent)
		for ui: float in ([1.0] if extent.x == 2560 else [1.0,1.25]):
			app.set_ui_scale(ui)
			for index: int in range(10):
				app.select_puzzle(index)
				app.replace_with_sample()
				var cells: Array = app.session.player.cells.duplicate()
				var history: Array = app.session.player.history.duplicate(true)
				for mode: String in ["R", "G", "V"]:
					app.choose_mode(mode)
					if mode == "R":
						app.board.working_size()
					else:
						app.board.fit_all()
					await process_frame
					var record: Dictionary = app.board.measurements()
					record.merge({"id": app.session.definition.id, "revision": app.session.definition.revision, "definition_sha256": FileAccess.get_sha256("res://full_view_study/cases/vs%02d/definition.json" % (index+1)), "format": [app.session.player.width,app.session.player.height], "color": app.session.definition.palette.size() > 1, "client": [extent.x,extent.y], "ui_scale": ui, "surface_kind": "native-rendered logical SubViewport, not physical display proof", "board_rect": app.board.rect_values(app.board.get_global_rect()), "miniature_rect": app.board.rect_values(app.mini.get_global_rect()), "controls": {}, "controls_clipped": [], "control_overlaps": [], "spoiler_free": not app.session.completed and not app.ending.visible})
					var controls: Dictionary = {"mini": app.mini, "palette": app.palette_row, "modes": app.mode_controls, "status": app.study_status, "coordinate": app.coordinate, "zoom_label": app.zoom_label, "tool_label": app.tool_label, "mini_title": app.mini_title}
					for key: String in app.actions:
						if app.actions[key].is_visible_in_tree():
							controls[key] = app.actions[key]
					for key: String in controls:
						var rect: Rect2 = controls[key].get_global_rect()
						record.controls[key] = app.board.rect_values(rect)
						if not Rect2(Vector2.ZERO,Vector2(extent)).encloses(rect):
							record.controls_clipped.append(key)
						if app.board.get_global_rect().intersects(rect):
							record.control_overlaps.append(key)
					record.limiting_element = "reference navigation" if mode == "R" else ("glyph collision/clipping" if record.glyph_collisions > 0 or record.clipped_glyphs > 0 else ("control space" if not record.controls_clipped.is_empty() or not record.control_overlaps.is_empty() else ("height / upper clues" if (app.board.size.y-app.board.book_inset.y-6)/app.session.player.height <= (app.board.size.x-app.board.book_inset.x-6)/app.session.player.width else "width / left clues")))
					check(app.session.player.cells == cells and app.session.player.history == history, "comparison preserves model")
					if mode != "R":
						check(record.grid_fit or not record.layout_valid, "full grid or explicit invalid layout")
						check(record.hidden_tokens == 0 if mode == "V" else true, "V hides no clue")
						for direction: int in [-1,1]:
							for step: int in range(24):
								app.board.zoom(direction,app.board.view.viewport.get_center())
								check(app.board.view.cell_size <= app.board.fit_ceiling + 0.01, "zoom bounded")
								check(app.board.view.viewport.grow(0.01).encloses(app.board.view.bounds()), "all offered zoom steps fit")
						app.board.fit_all()
						record.checkpoints = []
						for pitch: float in [16.0,18.0,20.0]:
							app.board.requested_cell = pitch
							app.board._layout()
							record.checkpoints.append({"requested":pitch,"actual":app.board.view.cell_size,"font_px":app.board.clue_font_size(),"capped":app.board.view.cell_size < pitch,"glyph_risk":app.board.glyph_risk})
						app.board.fit_all()
					records.append(record)
					if (extent.x == 1920 and ui == 1.0 and index in [0,6,7,8,9]) or (extent.x == 1280 and ui == 1.25 and index in [0,5,7,9] and mode != "R"):
						await shot("vs1-%s-%d-u%d-%s" % [app.session.definition.id,extent.x,roundi(ui*100),mode])
	canvas.size = Vector2i(1920,1080)
	app.size = Vector2(canvas.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(7)
	app._reset_selected()
	app.open_puzzle()
	app.choose_mode("V")
	app.board.fit_all()
	await shot("vs1-VS08-empty")
	await diagnostic_probe()
	var report: Dictionary = {"schema": 1, "records": records, "pictures": pictures, "diagnostics": diagnostics, "failures": failures, "drawing_basis": "985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f / study / Chalkboard 1.35 / pencil", "renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(), "physical_environment": {"screen": str(DisplayServer.screen_get_size()), "usable": str(DisplayServer.screen_get_usable_rect()), "dpi": DisplayServer.screen_get_dpi(), "scale": DisplayServer.screen_get_scale(), "root_client": str(root.size), "physical_720p_1080p_dpi_comfort": "not tested"}}
	FileAccess.open(output.path_join("vs1-matrix.json"), FileAccess.WRITE).store_string(JSON.stringify(report,"\t")+"\n")
	if failures == 0:
		print("VS1_CAPTURE_OK rows=", records.size(), " pictures=", pictures.size())
	quit(0 if failures == 0 else 1)

func diagnostic_probe() -> void:
	# Review-only synthetic matrices; never registered, saved or certified.
	const Definition = preload("res://model/definition.gd")
	app.hide()
	var background: ColorRect = ColorRect.new()
	background.color = Color("faf6ec")
	background.size = Vector2(canvas.size)
	canvas.add_child(background)
	var title: Label = Label.new()
	title.position = Vector2(60,30)
	title.add_theme_color_override("font_color",Color("343f42"))
	title.add_theme_font_size_override("font_size",24)
	canvas.add_child(title)
	for id: String in ["VS-D11","VS-D12"]:
		var board: Control = load("res://full_view_study/board.gd").new()
		var data: Dictionary = app.sessions[7].definition.duplicate(true)
		data.id = id
		data.width = 50 if id == "VS-D11" else 40
		data.height = 30 if id == "VS-D11" else 40
		data.solution = []
		data.rows = []
		data.columns = []
		for y: int in range(data.height):
			var row: Array = []
			for x: int in range(data.width):
				row.append(1+(x+y)%2 if id == "VS-D11" else (1 if y<20 and x>=2 and x<22 else 0))
			data.solution.append(row)
			data.rows.append(Definition.hints(row))
		for x: int in range(data.width):
			data.columns.append(Definition.hints(Definition.column(data.solution,x)))
		board.session = Session.new(data)
		board.book_layout = true
		board.mode = "G" if id == "VS-D11" else "V"
		board.position = Vector2(60,110)
		board.size = Vector2(1740,890)
		canvas.add_child(board)
		board._layout()
		for state: int in ([0] if id == "VS-D11" else [0,1,2]):
			title.text = "%s · DIAGNOSE, nicht zertifiziert · Hinweiszustand %d" % [id,state]
			if id == "VS-D11":
				for index: int in range(board.session.player.cells.size()):
					board.session.player.cells[index] = 0 if index%3==0 else 1+index%2
			elif state > 0:
				for x: int in range(40):
					board.session.player.cells[x] = 1 if x>=2 and x<22 else (0 if state==2 else -1)
			board.sync_clue_completion(board.session.visible_cells())
			if id == "VS-D12":
				check(board.clue_status("row",0,0)==state,"three real diagnostic clue states")
			board.queue_redraw()
			await process_frame
			await RenderingServer.frame_post_draw
			var name: String = "vs1-%s-state%d.png" % [id,state]
			canvas.get_texture().get_image().save_png(output.path_join(name))
			diagnostics.append({"id":id,"certified":false,"kind":"diagnostic","state":state,"file":name,"sha256":FileAccess.get_sha256(output.path_join(name)),"matrix_sha256":JSON.stringify(data.solution).sha256_text(),"measurements":board.measurements()})
		board.queue_free()
		await process_frame
