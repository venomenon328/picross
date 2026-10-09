extends SceneTree
## The same script runs against the pinned main and the delivery project.
## Fixtures, player inputs, geometry and pointer events are identical.
const Main = preload("res://ui/main.gd")
const Session = preload("res://model/session.gd")
const SaveStore = preload("res://model/save_store.gd")
var surface: SubViewport
var app: Main
var output: String
var variant: String
var captures: Array = []

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	SaveStore.test_root_override = "user://gp48-capture-%d" % Time.get_ticks_usec()
	output = OS.get_environment("P1_CAPTURE_DIR")
	variant = OS.get_environment("GP48_VARIANT")
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	app = load("res://main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	await create_timer(0.5).timeout
	for spec: Array in [[1920, 1080, 1.0], [1280, 720, 1.25]]:
		surface.size = Vector2i(spec[0], spec[1])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[2])
		await process_frame
		for fixture: int in range(3):
			app.select_puzzle(fixture)
			install_cells(fixture)
			app.open_puzzle()
			app.board.clear_pointer_hover()
			if app.board.has_method("set_mode"):
				app.board.requested_cell = 24.0 if fixture == 0 else 22.0
				app.board.overview = false
				app.board._layout()
			else:
				app.board.view.zoom_to(24.0 if fixture == 0 else 22.0, app.board.view.viewport.get_center())
			app.board.view.center = Vector2(10, 10) if fixture == 0 else (Vector2(22, 28) if fixture == 1 else Vector2(18, 12))
			app.board.view.reframe()
			app.board.reset_clue_pan()
			await process_frame
			var prefix: String = "f%d-%d-ui%d" % [fixture + 1, spec[0], roundi(spec[2] * 100)]
			await shot(prefix + "-work")
			var line: int = 3 if fixture == 0 else (35 if fixture == 1 else 11)
			app.board.set_clue_hover("row", line)
			await shot(prefix + "-row-tooltip")
			var column: int = 10 if fixture == 0 else (24 if fixture == 1 else 17)
			app.board.set_clue_hover("column", column)
			await shot(prefix + "-column-tooltip")
			app.board.clear_pointer_hover()
			if fixture > 0:
				for axis: String in ["row", "column"]:
					var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
					var cell: Vector2 = app.board.view.cell_rect(Vector2i(column, line)).get_center()
					var point: Vector2 = app.board.global_position + (Vector2(area.get_center().x, cell.y) if axis == "row" else Vector2(cell.x, area.get_center().y))
					var press: InputEventMouseButton = InputEventMouseButton.new()
					press.position = point
					press.button_index = MOUSE_BUTTON_MIDDLE
					press.pressed = true
					var hover: InputEventMouseMotion = InputEventMouseMotion.new()
					hover.position = point
					surface.push_input(hover, true)
					app.board.clear_clue_hover()
					surface.push_input(press, true)
					var motion: InputEventMouseMotion = InputEventMouseMotion.new()
					motion.position = point + (Vector2(44.7 * spec[2], 0) if axis == "row" else Vector2(0, 26.82 * spec[2]))
					surface.push_input(motion, true)
					var expected: String = axis
					if app.board.has_method("set_mode"):
						expected = app.board.navigation_target(point-app.board.global_position)
					if app.board.pan_target != expected:
						push_error("GP48 capture did not start the intended overflow drag")
						quit(6)
						return
					await shot(prefix + "-" + axis + "-drag")
					var release: InputEventMouseButton = press.duplicate()
					release.position = motion.position
					release.pressed = false
					surface.push_input(release, true)
					app.board.clear_pointer_hover()
					await shot(prefix + "-" + axis + "-drop")
		app.select_puzzle(0)
		install_cells(0)
		app.open_puzzle()
		app.board.view.center = Vector2(10, 10)
		app.board.view.reframe()
		app.board.clear_pointer_hover()
		# Normal -> filled -> closed, same glyph positions and font size.
		for step: int in range(3):
			var changes: Array = []
			for x: int in range(8, 11):
				add_change(changes, 3 * 20 + x, -1 if step == 0 else 1)
			add_change(changes, 3 * 20 + 7, 0 if step == 2 else -1)
			add_change(changes, 3 * 20 + 11, 0 if step == 2 else -1)
			app.session.player.commit(changes)
			app.board.queue_redraw()
			await shot("f1-%d-ui%d-status%d" % [spec[0], roundi(spec[2] * 100), step])
	var report: FileAccess = FileAccess.open(output.path_join("gp48-" + variant + ".json"), FileAccess.WRITE)
	report.store_string(JSON.stringify({"variant": variant, "renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(), "captures": captures}, "\t") + "\n")
	print("GP48_CAPTURE_OK images=", captures.size())
	quit(0)

func install_cells(fixture: int) -> void:
	var fresh: Session = Session.new(app.sessions[fixture].definition)
	var n: int = fresh.player.width
	var changes: Array = []
	for y: int in range(n):
		for x: int in range(n):
			var v: int = int(fresh.definition.solution[y][x])
			# Explicit technical player stand; never installed in a user profile.
			if (fixture == 0 and y < 14) or (fixture == 1 and y < 30) or (fixture == 2 and y < 20):
				var value: int = v if v > 0 else (0 if y % 3 == 1 else -1)
				if value != -1:
					changes.append({"index": y * n + x, "before": -1, "after": value})
	fresh.player.commit(changes)
	app.sessions[fixture] = fresh
	app.session = fresh
	app.board.session = fresh
	app.board.ensure_clue_steps()

func add_change(changes: Array, index: int, value: int) -> void:
	var before: int = app.session.player.cells[index]
	if before != value:
		changes.append({"index": index, "before": before, "after": value})

func shot(name: String) -> void:
	# Native window mouse-exit notifications may arrive during layout. Pin the
	# explicitly selected technical hover after layout, before the final draw.
	var hover_axis: String = app.board.clue_hover_axis
	var hover_index: int = app.board.clue_hover_index
	app.board.queue_redraw()
	app.mini.queue_redraw()
	app.refresh()
	await process_frame
	await process_frame
	if not hover_axis.is_empty():
		app.board.set_clue_hover(hover_axis, hover_index)
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	var file: String = "gp48-" + variant + "-" + name + ".png"
	if image.save_png(output.path_join(file)) != OK:
		push_error("GP48 image write failed")
		quit(5)
	var states: Dictionary = {}
	var focus_states: Array = []
	if app.board.has_method("completion_states"):
		focus_states = app.board.call("completion_states", "row", 3)
		for axis: String in ["row", "column"]:
			var counts: Array[int] = [0, 0, 0]
			for i: int in range(app.session.player.width):
				for state: int in app.board.call("completion_states", axis, i):
					counts[state] += 1
			states[axis] = counts
	captures.append({"file": file, "case": name, "fixture": app.session.definition.id, "size": [surface.size.x, surface.size.y], "ui_scale": app.ui_scale, "cells_sha256": JSON.stringify(app.session.player.cells).sha256_text(), "view": app.board.capture_view(), "font_size": app.board.clue_font_size(), "states": states, "focus_states": focus_states, "row3_units": app.board.visual_hint_units("row", 3), "pan_target": app.board.pan_target, "tooltip": [app.board.clue_hover_axis, app.board.clue_hover_index]})
	if app.board.has_method("measurements"): captures.back().full_view = app.board.measurements()
