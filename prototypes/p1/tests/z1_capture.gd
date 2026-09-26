extends SceneTree
## Executes the real isolated Z1 scene, GUI routes and actual rendered surfaces.
const DesignScene = preload("res://design/main.tscn")
const Design = preload("res://design/design.gd")
const Demo = preload("res://design/demo.gd")
var surface: SubViewport
var app: Design
var checks: int = 0
var failures: int = 0
var captures: Array[Dictionary] = []
var output: String
var tests_only: bool
var pointer_position: Vector2 = Vector2.ZERO
var pointer_buttons: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, caption: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		push_error("Z1: " + caption)

func frames() -> void:
	await process_frame
	await process_frame

func pointer(point: Vector2, down: bool, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	pointer_position = point
	var mask: int = 1 << (int(button) - 1)
	pointer_buttons = (pointer_buttons | mask) if down else (pointer_buttons & ~mask)
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.button_mask = pointer_buttons
	event.position = point
	event.global_position = point
	event.button_index = button
	event.pressed = down
	surface.push_input(event, true)
	await frames()

func motion(point: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.relative = point - pointer_position
	event.button_mask = pointer_buttons
	pointer_position = point
	event.position = point
	event.global_position = point
	surface.push_input(event, true)
	await frames()

func click(control: Control) -> void:
	var point: Vector2 = control.get_global_rect().get_center()
	await motion(point)
	await pointer(point, true)
	await pointer(point, false)

func state() -> Dictionary:
	return {"cells": app.session.player.cells.duplicate(), "history": app.session.player.history.duplicate(true), "cursor": app.session.player.cursor,
		"rows": app.session.definition.rows, "columns": app.session.definition.columns,
		"palette": app.session.definition.palette, "view": app.board.capture_view(),
		"viewport": var_to_str(app.board.view.viewport), "board": var_to_str(app.board.get_rect()),
		"miniature": app.mini.cells.duplicate(), "scale": app.ui_scale}

func contrast(a: Color, b: Color) -> float:
	var first: float = a.srgb_to_linear().get_luminance()
	var second: float = b.srgb_to_linear().get_luminance()
	return snappedf((maxf(first, second) + 0.05) / (minf(first, second) + 0.05), 0.01)

func contrasts() -> Dictionary:
	var frame: Color = app.board.frame_style.bg_color
	var entries: Array[Dictionary] = []
	for entry: Dictionary in app.session.definition.palette:
		entries.append({"color": entry.color, "on_hint_surface": contrast(Color(entry.color), frame), "on_grid": contrast(Color(entry.color), app.board.PAPER)})
	return {"method": "sRGB linear relative luminance ratio; no physical DPI or accessibility certification",
		"hint_surface": frame.to_html(), "grid_surface": app.board.PAPER.to_html(),
		"ui_text": contrast(app.coordinate.get_theme_color("font_color"), frame), "puzzle_colors": entries}

func snapshot(name: String) -> void:
	if tests_only:
		return
	app.refresh()
	await frames()
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	check(picture.save_png(output.path_join(name + ".png")) == OK, name + " PNG")
	var s: Dictionary = state()
	captures.append({"file": name + ".png", "source_commit": OS.get_environment("Z1_SOURCE_COMMIT"),
		"demo_revision": Demo.REVISION, "fixture": app.session.definition.id,
		"variant": app.variant + 1, "logical_size": [surface.size.x, surface.size.y],
		"ui_scale": app.ui_scale, "cell_size": app.board.view.cell_size,
		"state_sha256": JSON.stringify(s.cells).sha256_text(), "history_sha256": JSON.stringify(s.history).sha256_text(),
		"clues_sha256": JSON.stringify([s.rows, s.columns]).sha256_text(),
		"palette": s.palette, "view": s.view, "board_rect": s.board, "grid_viewport": s.viewport,
		"miniature_matches_visible_cells": app.mini.cells == app.session.visible_cells(),
		"gesture_length": app.board.gesture_length(), "overlay": app.overlay_kind, "contrast": contrasts()})
	if app.overlay_kind.is_empty():
		# Actual swatch center samples; marker and selection borders stay outside.
		for i: int in range(app.palette_buttons.size()):
			var point: Vector2i = Vector2i(app.palette_buttons[i].global_position + Vector2(10, 10))
			check(picture.get_pixelv(point).is_equal_approx(Color(app.session.definition.palette[i].color)), name + " unchanged swatch " + str(i))
		# Own miniature and board sample the same confirmed or preview fill.
		for i: int in range(app.mini.cells.size()):
			if not app.board.clue_hover_axis.is_empty():
				break # Full-hint popup covers the grid; covered fills are not visible.
			if app.mini.cells[i] <= 0:
				continue
			var cell: Vector2i = Vector2i(i % app.mini.width, i / app.mini.width)
			var box: Rect2 = app.board.view.cell_rect(cell)
			if not app.board.view.viewport.encloses(box):
				continue
			var color: Color = app.board.cell_color(app.mini.cells[i])
			var mini_point: Vector2 = (Vector2(cell) + Vector2.ONE * 0.5) * app.mini.image_rect().size / Vector2(app.mini.width, app.mini.height)
			# Avoid the miniature's viewport outline.
			var frame: Rect2 = Rect2(app.mini.view_rect.position * app.mini.image_rect().size, app.mini.view_rect.size * app.mini.image_rect().size).grow(-5)
			if not frame.has_point(mini_point):
				continue
			check(picture.get_pixelv(Vector2i(app.board.global_position + box.get_center())).is_equal_approx(color), name + " board fill")
			check(picture.get_pixelv(Vector2i(app.mini.global_position + mini_point)).is_equal_approx(color), name + " own miniature fill")
			break

func run() -> void:
	# Refuse a direct invocation against the owner's normal Godot profile.
	# The harness must bind user:// beneath its freshly isolated temporary root.
	var profile: String = OS.get_environment("Z1_PROFILE_ROOT").replace("\\", "/").simplify_path().to_lower()
	var user_path: String = ProjectSettings.globalize_path("user://").replace("\\", "/").simplify_path().to_lower()
	if profile.is_empty() or not user_path.begins_with(profile.trim_suffix("/") + "/"):
		print("Z1_ISOLATION_REQUIRED")
		quit(2)
		return
	output = OS.get_environment("Z1_CAPTURE_DIR")
	tests_only = OS.get_cmdline_user_args().has("--z1-tests-only")
	if output.is_empty():
		push_error("Z1_CAPTURE_DIR required; run the isolated harness")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(output)
	# A deliberately invalid sentinel cannot be loaded by the independent entry.
	DirAccess.make_dir_recursive_absolute("user://p1/saves")
	var sentinel: FileAccess = FileAccess.open("user://p1/saves/f01.json", FileAccess.WRITE)
	sentinel.store_string("Z1 sentinel: never load or overwrite")
	sentinel.close()
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	# A standalone offscreen viewport has no SubViewportContainer to deliver entry.
	# Without this notification Godot tracks hover but skips unpressed GUI motion.
	surface.notify_mouse_entered()
	app = DesignScene.instantiate()
	surface.add_child(app)
	await frames()
	check(app.session.definition.id == "F-02", "separate scene starts F-02")
	check(app.session.player.cursor < app.session.player.history.size(), "consistent redo exists")
	app.variant_choice.item_selected.emit(1)
	check(app.variant == 1, "variant selector connected")
	app.fixture_choice.item_selected.emit(0)
	check(app.fixture == 0 and app.palette_buttons.size() == 1, "fixture selector and mono simplification")
	for fixture: int in range(3):
		app.select_fixture(fixture)
		for dims: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
			surface.size = dims
			for scale: float in [1.0, 1.25]:
				app.set_ui_scale(scale)
				await frames()
				app.set_variant(0)
				var before: Dictionary = state()
				app.set_variant(1)
				check(state() == before, "same state, hints and geometry V1/V2")
				check(app.board.view.cell_size == (18 if fixture == 1 else 24), "resize/scale never inflates cells")
				check(app.mini.cells == app.session.visible_cells(), "own miniature")
				for control: Control in [app.mini, app.coordinate, app.work_button, app.palette_buttons[-1], app.tool_buttons[-1]]:
					check(app.panel.get_global_rect().encloses(control.get_global_rect()), "sidebar encloses " + str(control) + " at " + str(dims) + "/" + str(scale))
				for cell: Vector2i in [Vector2i(5, 5), Vector2i(10, 10)]:
					var point: Vector2 = app.board.view.cell_rect(cell).get_center()
					if app.board.view.viewport.has_point(point):
						check(app.board.view.hit(point) == cell, "cell transform")
				check(app.board.row_clue_area().end.x <= app.board.view.visible_bounds().position.x, "clues outside grid")
	# All interaction checks go through the actual UI or Board viewport route.
	surface.size = Vector2i(1920, 1080)
	app.set_ui_scale(1.0)
	app.select_fixture(1)
	app.board.working_size()
	await frames()
	var initial: Array[int] = app.session.player.cells.duplicate()
	await click(app.palette_buttons[2])
	check(app.board.active_color == 3, "swatch GUI selection")
	await click(app.tool_buttons[1])
	check(app.board.eraser, "eraser GUI selection")
	await click(app.tool_buttons[0])
	var point: Vector2 = app.board.global_position + app.board.view.cell_rect(Vector2i(15, 12)).get_center()
	await motion(point)
	await pointer(point, true)
	await motion(point + Vector2(4 * 24, 0))
	check(app.session.gesture.active and app.board.gesture_length() == 5, "actual stroke preview")
	check(app.mini.cells == app.session.visible_cells() and app.mini.cells != initial, "preview in miniature")
	app.set_variant(1 - app.variant)
	check(not app.session.gesture.active and app.session.player.cells == initial, "variant aborts before switch")
	await pointer(point, false)
	await motion(point)
	await pointer(point, true)
	await motion(point + Vector2(4 * 24, 0))
	await pointer(point + Vector2(4 * 24, 0), false)
	check(app.session.player.cells != initial, "actual cell edit")
	await click(app.undo_button)
	check(app.session.player.cells == initial, "GUI undo atomic")
	await click(app.redo_button)
	check(app.session.player.cells != initial, "GUI redo")
	for kind: String in ["help", "menu"]:
		await click(app.help_button if kind == "help" else app.menu_button)
		check(app.overlay_kind == kind and app.overlay.visible, "opens " + kind)
		if kind == "menu":
			await click(app.completion_button)
			check(not app.mark_completed and not app.board.mark_completed_clues, "H1 menu switch")
			await click(app.ui_button)
			check(app.ui_scale == 1.25 and app.overlay.visible, "UI menu switch keeps modal open")
			await click(app.ui_button)
			await click(app.completion_button)
		var blocked: Array[int] = app.session.player.cells.duplicate()
		await motion(point)
		await pointer(point, true)
		await pointer(point, false)
		check(app.session.player.cells == blocked and not app.session.gesture.active, "overlay blocks cells " + kind)
		await click(app.drawer_close)
		check(not app.overlay.visible, "closes " + kind)
	app.select_fixture(2)
	await frames()
	var nav_cells: Array[int] = app.session.player.cells.duplicate()
	var old_center: Vector2 = app.board.view.center
	await pointer(app.mini.global_position + app.mini.size * 0.8, true)
	await pointer(app.mini.global_position + app.mini.size * 0.8, false)
	check(app.board.view.center != old_center and app.session.player.cells == nav_cells, "miniature navigation")
	await click(app.zoom_in)
	check(app.board.view.cell_size == 26, "zoom GUI")
	await click(app.work_button)
	var grid: Vector2 = app.board.global_position + app.board.view.viewport.get_center()
	old_center = app.board.view.center
	await pointer(grid, true, MOUSE_BUTTON_MIDDLE)
	await motion(grid + Vector2(60, 0))
	await pointer(grid + Vector2(60, 0), false, MOUSE_BUTTON_MIDDLE)
	check(app.board.view.center != old_center and app.session.player.cells == nav_cells, "board pan")
	for axis: String in ["row", "column"]:
		var index: int = roundi(app.board.view.center.y if axis == "row" else app.board.view.center.x)
		var cross: Vector2 = app.board.view.cell_rect(Vector2i(index, index)).get_center()
		var local: Vector2 = Vector2(app.board.row_clue_area().get_center().x, cross.y) if axis == "row" else Vector2(cross.x, app.board.column_clue_area().get_center().y)
		var start: Vector2 = app.board.global_position + local
		var reads: Array = (app.board.row_clue_reads if axis == "row" else app.board.column_clue_reads).duplicate(true)
		await pointer(start, true, MOUSE_BUTTON_MIDDLE)
		check(app.board.pan_target == axis and app.board.pan_line_index == index, "hint target frozen")
		var end: Vector2 = start + (Vector2(60, 0) if axis == "row" else Vector2(0, 60))
		await motion(end)
		await pointer(end, false, MOUSE_BUTTON_MIDDLE)
		var updated: Array = app.board.row_clue_reads if axis == "row" else app.board.column_clue_reads
		check(updated[index] != reads[index], "individual hint changed")
		for neighbor: int in range(reads.size()):
			if neighbor != index:
				check(updated[neighbor] == reads[neighbor], "neighbor hint unchanged")
	check(app.session.player.cells == nav_cells, "navigation keeps cells")
	app.show_overlay("menu")
	await click(app.clue_button)
	check(app.board.row_clue_steps.count(0) == 100 and app.board.column_clue_steps.count(0) == 100, "hint reset via menu")
	app.hide_overlay()
	# Eight mandatory main views, reset from the identical explicit gesture script.
	for variant: int in range(2):
		app.set_variant(variant)
		for item: Array in [[1, Vector2i(1920, 1080)], [1, Vector2i(2560, 1440)], [0, Vector2i(1920, 1080)], [2, Vector2i(1920, 1080)]]:
			surface.size = item[1]
			app.select_fixture(int(item[0]))
			await frames()
			await snapshot("v%d-f%02d-%dx%d" % [variant + 1, int(item[0]) + 1, surface.size.x, surface.size.y])
		# Same original H1 token, color and slot before/after the session toggle.
		app.select_fixture(1)
		await frames()
		check(app.board.clue_is_marked("row", 1, 0), "demo has an actually fulfilled original clue")
		await snapshot("v%d-h1-on" % (variant + 1))
		var marked: Image = null if tests_only else surface.get_texture().get_image()
		app.board.mark_completed_clues = false
		await snapshot("v%d-h1-off" % (variant + 1))
		if not tests_only:
			var unmarked: Image = surface.get_texture().get_image()
			var grid_box: Rect2i = Rect2i(Rect2(app.board.global_position + app.board.view.visible_bounds().position, app.board.view.visible_bounds().size))
			check(marked.get_region(grid_box).get_data() == unmarked.get_region(grid_box).get_data(), "H1 keeps rendered grid")
			check(marked.get_data() != unmarked.get_data(), "H1 real rendered strike changes")
		app.board.mark_completed_clues = true
		surface.size = Vector2i(1280, 720)
		app.set_ui_scale(1.25)
		app.select_fixture(1)
		await snapshot("v%d-tight-ui125" % (variant + 1))
		app.show_overlay("help")
		await snapshot("v%d-help-ui125" % (variant + 1))
		app.hide_overlay()
		surface.size = Vector2i(1920, 1080)
		app.set_ui_scale(1.0)
		app.select_fixture(1)
		app.show_overlay("menu")
		await snapshot("v%d-menu" % (variant + 1))
		app.hide_overlay()
		await motion(app.palette_buttons[2].get_global_rect().get_center())
		await snapshot("v%d-hover" % (variant + 1))
		await motion(Vector2(5, 5))
		for _i: int in range(app.session.player.cursor):
			app.undo()
		await snapshot("v%d-undo-disabled" % (variant + 1))
		for _i: int in range(app.session.player.history.size()):
			app.redo()
		await snapshot("v%d-redo-disabled" % (variant + 1))
		app.select_fixture(2)
		await frames()
		var hint_point: Vector2 = app.board.global_position + Vector2(app.board.row_clue_area().get_center().x, app.board.view.cell_rect(Vector2i(0, 50)).get_center().y)
		await motion(hint_point)
		check(app.board.row_hint_overflows(50) and app.board.clue_hover_axis == "row" and app.board.clue_hover_index == 50, "real overflow hover for full hint capture")
		await snapshot("v%d-full-hint" % (variant + 1))
		app.select_fixture(1)
		app.board.working_size()
		point = app.board.global_position + app.board.view.cell_rect(Vector2i(15, 12)).get_center()
		await motion(point)
		await pointer(point, true)
		await motion(point + Vector2(7 * 24, 0))
		check(app.board.gesture_length() == 8, "capture counter 8")
		await snapshot("v%d-stroke-8" % (variant + 1))
		app.board.cancel_gesture()
		await pointer(point, false)
	check(FileAccess.get_file_as_string("user://p1/saves/f01.json") == "Z1 sentinel: never load or overwrite", "normal save sentinel unchanged")
	check(DirAccess.get_files_at("user://p1/saves") == PackedStringArray(["f01.json"]), "no saves created by Z1")
	app.queue_free()
	await frames()
	var report: FileAccess = FileAccess.open(output.path_join("z1-render-report.json"), FileAccess.WRITE)
	report.store_string(JSON.stringify({"checks": checks, "failures": failures, "captures": captures, "renderer": RenderingServer.get_video_adapter_name(), "physical_dpi": "not measured"}, "\t") + "\n")
	report.close()
	print("Z1_CHECKS ", checks, " failures=", failures)
	if failures == 0:
		print("Z1_TESTS_OK" if tests_only else "Z1_CAPTURE_OK")
	quit(0 if failures == 0 else 5)
