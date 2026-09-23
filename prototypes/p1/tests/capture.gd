extends SceneTree
## Real GPU/software-rendered offscreen surfaces; not a physical DPI claim.
const Main = preload("res://ui/main.gd")
var surface: SubViewport
var output: String
var captures: Array = []
var pixel_checks: int = 0

func _initialize() -> void:
	call_deferred("run")

func snapshot(app: Main, name: String, crop: bool = false) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	if name.contains("confirmed"):
		for i: int in range(app.session.definition.palette.size()):
			var cell: Rect2 = app.board.view.cell_rect(Vector2i(2 + i * 2, 4))
			var center: Vector2i = Vector2i(app.board.global_position + cell.get_center())
			var moat: Vector2i = Vector2i(app.board.global_position + cell.position + Vector2(2, cell.size.y / 2))
			if not picture.get_pixelv(center).is_equal_approx(Color(app.session.definition.palette[i].color)) or not picture.get_pixelv(moat).is_equal_approx(app.board.PAPER):
				push_error("Rendered fill/moat regression: " + name)
				quit(5)
				return
			pixel_checks += 2
	if name.ends_with("reveal"):
		var texture_image: Image = app.reveal_view.artwork.get_image()
		if texture_image == null or texture_image.is_empty():
			push_error("Missing rendered reveal")
			quit(6)
			return
	if crop:
		var box: Rect2 = app.board.view.cell_rect(Vector2i(2, 2)).merge(app.board.view.cell_rect(Vector2i(18, 8)))
		box.position += app.board.global_position
		picture = picture.get_region(Rect2i(box.grow(8)))
	if picture.save_png(output.path_join(name + ".png")) != OK:
		quit(4)
		return
	var row_index: int = longest_line(app.session.definition.rows)
	var column_index: int = longest_line(app.session.definition.columns)
	var row_window: Dictionary = app.board.clue_layout("row", row_index)
	var column_window: Dictionary = app.board.clue_layout("column", column_index)
	captures.append({"file": name + ".png", "logical_surface": [surface.size.x, surface.size.y], "ui_scale": app.ui_scale, "cell_pitch": app.board.view.cell_size, "fixture": app.session.definition.id, "crop": crop,
		"row_clue_position": app.board.row_clue_position, "column_clue_position": app.board.column_clue_position,
		"longest_row_window": [row_window.start, row_window.end, row_window.prefix_hidden, row_window.suffix_hidden],
		"longest_column_window": [column_window.start, column_window.end, column_window.prefix_hidden, column_window.suffix_hidden]})

func longest_line(lines: Array) -> int:
	var result: int = 0
	for i: int in range(1, lines.size()):
		if lines[i].size() > lines[result].size():
			result = i
	return result

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	surface = SubViewport.new()
	surface.size = Vector2i(1600, 900)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	var app: Main = load("res://main.tscn").instantiate()
	surface.add_child(app)
	await snapshot(app, "album")
	for dims: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		surface.size = dims
		for scale: float in [1.0, 1.25]:
			app.set_ui_scale(scale)
			for fixture: int in range(3):
				app.select_puzzle(fixture)
				if scale > 1:
					app.board.zoom(1, app.board.view.viewport.get_center())
				for i: int in range(4):
					app.session.player.cells[(4 + i) * app.session.player.width + 4] = mini(i + 1, app.session.definition.palette.size())
				app.board.hover = Vector2i(4, 4)
				await snapshot(app, "%dx%d-ui%d-f%d" % [dims.x, dims.y, roundi(scale * 100), fixture + 1])
			app.select_puzzle(1)
			app.toggle_accessibility_labels()
			app.board.row_clue_position = 0.5
			app.board.column_clue_position = 0.5
			await snapshot(app, "%dx%d-ui%d-f2-accessibility-middle" % [dims.x, dims.y, roundi(scale * 100)])
			app.toggle_accessibility_labels()
	# D-11/D-12/D-14: unnumbered colored hints stay in the work view; optional
	# accessibility suffixes and the complete overflow tooltip get real renders.
	# D-16/D-17 add atomic clue windows and independent row/column reading positions.
	surface.size = Vector2i(1600, 900)
	app.set_ui_scale(1)
	app.select_puzzle(1)
	app.board.hover = Vector2i(10, 10)
	await snapshot(app, "f02-colored-hints-default")
	app.toggle_accessibility_labels()
	await snapshot(app, "f02-colored-hints-accessibility")
	app.toggle_accessibility_labels()
	for step: float in [22.0, 24.0]:
		app.board.view.zoom_to(step, app.board.view.viewport.get_center())
		for position: float in [0.0, 0.5, 1.0]:
			app.board.row_clue_position = position
			app.board.column_clue_position = position
			await snapshot(app, "f02-hints-%d-%s" % [roundi(step), ["end", "middle", "start"][roundi(position * 2.0)]])
	app.board.view.zoom_to(12.0, app.board.view.viewport.get_center())
	app.board.row_clue_position = 0.5
	app.board.column_clue_position = 0.5
	app.toggle_accessibility_labels()
	await snapshot(app, "f02-hints-50-accessibility-middle")
	app.toggle_accessibility_labels()
	app.board.view.zoom_to(24.0, app.board.view.viewport.get_center())
	app.board.row_clue_position = 1.0
	app.board.column_clue_position = 0.0
	await snapshot(app, "f02-row-start-column-end")
	app.board.row_clue_position = 0.0
	app.board.column_clue_position = 1.0
	await snapshot(app, "f02-row-end-column-start")
	app.select_puzzle(2)
	var f03_row: int = longest_line(app.session.definition.rows)
	var f03_column: int = longest_line(app.session.definition.columns)
	app.board.hover = Vector2i(f03_column, f03_row)
	app.board.set_clue_hover("row", f03_row)
	await snapshot(app, "f03-overflow-hover-tooltip")
	app.board.clear_clue_hover()
	for step: float in [12.0, 18.0, 22.0, 24.0]:
		app.board.view.zoom_to(step, app.board.view.viewport.get_center())
		app.board.row_clue_position = 0.0
		app.board.column_clue_position = 0.0
		await snapshot(app, "f03-hints-work-%d-end" % roundi(step / 24.0 * 100.0))
	for step: float in [12.0, 24.0]:
		app.board.view.zoom_to(step, app.board.view.viewport.get_center())
		for position: float in [0.5, 1.0]:
			app.board.row_clue_position = position
			app.board.column_clue_position = position
			await snapshot(app, "f03-hints-work-%d-%s" % [roundi(step / 24.0 * 100.0), "middle" if position == 0.5 else "start"])
	app.board.view.zoom_to(24.0, app.board.view.viewport.get_center())
	app.board.row_clue_position = 0.45
	app.board.column_clue_position = 0.65
	app.board.view.pan(Vector2(120, 80))
	app.board.navigate_to(Vector2(0.78, 0.22))
	await snapshot(app, "f03-hints-after-raster-pan")
	# Same L/block at normal and five-cell boundaries, every color/work step.
	for fixture: int in [0, 1]:
		app.select_puzzle(fixture)
		app.session.player.cells.fill(-1)
		for i: int in range(app.session.definition.palette.size()):
			var x: int = 2 + i * 2
			for cell: Vector2i in [Vector2i(x, 4), Vector2i(x+1, 4), Vector2i(x, 5), Vector2i(x, 7), Vector2i(x+1, 7), Vector2i(x+1, 8)]:
				app.session.player.cells[cell.y * app.session.player.width + cell.x] = i + 1
		for step: float in app.board.WORK_STEPS:
			app.board.view.zoom_to(step, app.board.view.viewport.get_center())
			app.board.navigate_to(Vector2.ZERO)
			await snapshot(app, "separation-f%d-%d-confirmed" % [fixture + 1, roundi(step)], true)
			# Preview whole mixed-color removal: original values outside endpoint survive.
			app.session.gesture.begin(app.session.player, Vector2i(2, 4), 1)
			app.session.gesture.move(Vector2i(10, 4))
			await snapshot(app, "separation-f%d-%d-removal" % [fixture + 1, roundi(step)], true)
			app.session.gesture.cancel()
			for color: int in range(1, app.session.definition.palette.size() + 1):
				app.session.gesture.begin(app.session.player, Vector2i(2, 3), color)
				app.session.gesture.move(Vector2i(10, 3))
				await snapshot(app, "separation-f%d-%d-preview-color%d" % [fixture + 1, roundi(step), color], true)
				app.session.gesture.cancel()
	app.select_puzzle(2)
	app.board.hover = Vector2i(f03_column, f03_row)
	app.board.set_clue_hover("row", f03_row)
	await snapshot(app, "f03-full-clues-in-work-tooltip")
	app.board.clear_clue_hover()
	app.board.fit_all()
	await snapshot(app, "f03-overview")
	for index: int in [0, 1, 2]:
		app.select_puzzle(index)
		app.session.player.cells.fill(-1)
		for y: int in range(app.session.player.height):
			for x: int in range(app.session.player.width):
				var value: int = int(app.session.definition.solution[y][x])
				if value > 0:
					app.session.gesture.begin(app.session.player, Vector2i(x, y), value)
					app.session.finish()
		await snapshot(app, "f%d-reveal" % (index + 1))
		app.show_album()
		await snapshot(app, "f%d-earned-album" % (index + 1))
	var report: FileAccess = FileAccess.open(output.path_join("render-report.json"), FileAccess.WRITE)
	report.store_string(JSON.stringify({"renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(), "pixel_checks": pixel_checks, "clue_contract": "atomic contiguous in-work clue windows; exact prefix/suffix markers; independent row/column panning; optional suffixes; complete hover tooltip", "physical_dpi_acceptance": "OPEN: owner", "captures": captures}, "  ") + "\n")
	print("P1_CAPTURE_OK: %d actual rendered images" % captures.size())
	quit(0)
