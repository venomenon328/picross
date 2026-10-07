extends SceneTree
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")
const Samples = preload("res://study/samples.gd")
var app: Control
var surface: SubViewport
var output: String
var captures: Array = []
var frames: Array = []
var measurements: Array = []
var specimens: Array = []
var baseline: bool
var variant: int
var failures: int = 0
var stroke_frames: Array = []
var probe_time: int = 1000000

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	if not condition:
		failures += 1
		printerr("ZS1 CAPTURE FAIL: ", message)

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	baseline = OS.get_environment("ZS1_BASELINE") == "1"
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	Store.test_root_override = "user://zs1-capture-%d" % Time.get_ticks_usec()
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	app = load("res://main.tscn" if baseline else "res://study/main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	await create_timer(0.3).timeout
	for style: int in ([0] if baseline else [0, 2]):
		variant = style
		if not baseline:
			app.board.set_style(style)
			app.update_variant()
		for spec: Array in [
			[0, 1920, 1080, 1.0, 24.0, "f01-work"],
			[1, 1920, 1080, 1.0, 24.0, "f02-color"],
			[2, 1920, 1080, 1.0, 12.0, "f03-small"],
			[1, 1280, 720, 1.25, 24.0, "f02-compact"],
			[0, 1600, 900, 1.0, 36.0, "f01-1600"],
			[0, 1920, 1080, 1.0, 36.0, "f01-z150"],
			[2, 2560, 1440, 1.0, 72.0, "f03-z300"]]:
			surface.size = Vector2i(spec[1], spec[2])
			app.size = Vector2(surface.size)
			app.set_ui_scale(spec[3])
			app.select_puzzle(spec[0])
			install_sample(spec[0])
			app.open_puzzle()
			app.board.working_size()
			while app.board.view.cell_size < float(spec[4]) - 0.01:
				app.board.zoom(1, app.board.view.viewport.get_center())
			while app.board.view.cell_size > float(spec[4]) + 0.01:
				app.board.zoom(-1, app.board.view.viewport.get_center())
			app.board.view.center = Vector2(10, 10) if spec[0] == 0 else Vector2(18, 12)
			app.board.view.reframe()
			app.board.clear_pointer_hover()
			await shot(spec[5])
			if spec[5] == "f02-compact":
				for axis: String in ["row", "column"]:
					await hint_probe(axis)
		await status_probe()
		if not baseline:
			await numeral_probe()
		if not baseline and style > 0:
			await movement()
			await load_probe()
			await stroke_probe()
	var report: Dictionary = {"baseline": baseline, "renderer": RenderingServer.get_video_adapter_name(),
		"display": DisplayServer.get_name(), "captures": captures, "frames": frames, "stroke_frames": stroke_frames, "measurements": measurements, "specimens": specimens, "failures": failures}
	var path: String = output.path_join("zs1-baseline.json" if baseline else "zs1-study.json")
	FileAccess.open(path, FileAccess.WRITE).store_string(JSON.stringify(report, "\t") + "\n")
	if failures == 0:
		print("ZS1_CAPTURE_OK captures=", captures.size(), " frames=", frames.size())
	quit(0 if failures == 0 else 1)

func install_sample(index: int) -> void:
	var fresh: Session = Samples.create(app.sessions[index].definition)
	app.sessions[index] = fresh
	app.session = fresh
	app.board.session = fresh
	app.board.restore_view(fresh.view_state)

func status_probe() -> void:
	surface.size = Vector2i(1920, 1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(0)
	var fresh: Session = Session.new(app.session.definition)
	app.sessions[0] = fresh
	app.session = fresh
	app.board.session = fresh
	app.board.restore_view(fresh.view_state)
	app.open_puzzle()
	for state: int in range(3):
		var changes: Array = []
		if state == 1:
			for index: int in [1, 21, 41, 68, 69, 70]:
				changes.append({"index": index, "before": -1, "after": 1})
		elif state == 2:
			for index: int in [61, 67, 71]:
				changes.append({"index": index, "before": -1, "after": 0})
		app.session.player.commit(changes)
		app.board.sync_clue_completion(app.session.visible_cells())
		check(app.board.clue_status("row", 3, 0) == state, "real row clue state")
		check(app.board.clue_status("column", 1, 0) == state, "real column clue state")
		await shot("status-%d" % state)

func numeral_probe() -> void:
	var specimen = load("res://study/numerals.gd").new()
	specimen.session = Session.new(app.sessions[1].definition)
	specimen.style = variant
	specimen.size = Vector2(720, 445)
	surface.add_child(specimen)
	app.hide()
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image().get_region(Rect2i(0, 0, 720, 445))
	var filename: String = "zs1-numerals-%d.png" % variant
	picture.save_png(output.path_join(filename))
	specimens.append({"file": filename, "style": variant, "label": "Artificial font specimen, not puzzle data", "font": specimen.clue_font().get_font_name()})
	specimen.queue_free()
	app.show()
	await process_frame

func rect_data(rect: Rect2) -> Array:
	return [rect.position.x, rect.position.y, rect.size.x, rect.size.y]

func shot(name: String) -> void:
	# Do not carry the last movement probe coordinate into another fixture.
	app.coordinate.text = "Zeile – · Spalte –"
	var axis: String = app.board.clue_hover_axis
	var line: int = app.board.clue_hover_index
	app.refresh()
	await process_frame
	await process_frame
	if not axis.is_empty():
		app.board.set_clue_hover(axis, line)
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	var filename: String = "zs1-%s-%s.png" % ["main" if baseline else str(variant), name]
	check(picture.save_png(output.path_join(filename)) == OK, "image write")
	captures.append({"file": filename, "case": name, "style": variant,
		"fixture": app.session.definition.id, "size": [surface.size.x, surface.size.y], "ui_scale": app.ui_scale,
		"cells_sha256": JSON.stringify(app.session.player.cells).sha256_text(), "view": app.board.capture_view(),
		"board": rect_data(app.board.get_global_rect()), "grid": rect_data(Rect2(app.board.global_position + app.board.view.visible_bounds().position, app.board.view.visible_bounds().size)),
		"viewport": rect_data(app.board.view.viewport), "font_size": app.board.clue_font_size(),
		"pan_target": app.board.pan_target, "tooltip": [axis, line], "spoiler_free": not app.session.completed and app.session.reveal().is_empty()})

func hint_probe(axis: String) -> void:
	var line: int = 12 if axis == "row" else 22
	# Center these real long lines in the working viewport.
	app.board.view.center = Vector2(22, 12)
	app.board.view.reframe()
	app.board.clear_pointer_hover()
	app.refresh()
	await process_frame
	var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
	var cell: Vector2 = app.board.view.cell_rect(Vector2i(22, 12)).get_center()
	var p: Vector2 = app.board.global_position + (Vector2(area.get_center().x, cell.y) if axis == "row" else Vector2(cell.x, area.get_center().y))
	mouse(p, MOUSE_BUTTON_MIDDLE, true)
	var end: Vector2 = p + (Vector2(67, 0) if axis == "row" else Vector2(0, 40))
	motion(end)
	check(app.board.pan_target == axis, "long clue drag " + axis)
	var neighbor: Dictionary = app.board.capture_view()
	await shot("hint-" + axis + "-drag")
	mouse(end, MOUSE_BUTTON_MIDDLE, false)
	check(app.board.pan_target.is_empty(), "clue drop")
	var after: Dictionary = app.board.capture_view()
	check(after.column_clue_reads == neighbor.column_clue_reads if axis == "row" else after.row_clue_reads == neighbor.row_clue_reads, "other axis unchanged")
	app.board.set_clue_hover(axis, line)
	await shot("hint-" + axis + "-tooltip")
	app.board.clear_pointer_hover()

func movement() -> void:
	surface.size = Vector2i(1920, 1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(0)
	app.empty_sample()
	await process_frame
	var board = app.board
	var start: Vector2 = point(0, 0)
	var end: Vector2 = point(19, 0)
	mouse(start, MOUSE_BUTTON_LEFT, true)
	motion(end)
	await process_frame
	await RenderingServer.frame_post_draw
	var preview_one: Image = surface.get_texture().get_image()
	await create_timer(0.08).timeout
	await RenderingServer.frame_post_draw
	var preview_two: Image = surface.get_texture().get_image()
	check(preview_one.get_data() == preview_two.get_data(), "preview static across native frames")
	var images: Array[Image] = [preview_one]
	var timeline: Array = [{"label": "static-preview", "after_commit_ms": -1}]
	mouse(end, MOUSE_BUTTON_LEFT, false)
	var committed_at: int = Time.get_ticks_usec()
	check(board.effects.size() == 20, "20 effective changes on commit")
	# Submit another gesture immediately, while all old effects are still active.
	mouse(start, MOUSE_BUTTON_RIGHT, true)
	motion(point(4, 0))
	var second_ms: float = float(Time.get_ticks_usec() - committed_at) / 1000.0
	check(second_ms < 140 and board.effects.size() == 15, "second gesture before first effect ends")
	await process_frame
	await RenderingServer.frame_post_draw
	images.append(surface.get_texture().get_image())
	timeline.append({"label": "second-conversion-preview", "after_commit_ms": float(Time.get_ticks_usec() - committed_at) / 1000.0})
	mouse(point(4, 0), MOUSE_BUTTON_RIGHT, false)
	for i: int in range(6):
		await process_frame
		await RenderingServer.frame_post_draw
		images.append(surface.get_texture().get_image())
		timeline.append({"label": "parallel-commit-%d" % i, "after_commit_ms": float(Time.get_ticks_usec() - committed_at) / 1000.0})
	await create_timer(0.18).timeout
	await RenderingServer.frame_post_draw
	images.append(surface.get_texture().get_image())
	timeline.append({"label": "settled", "after_commit_ms": float(Time.get_ticks_usec() - committed_at) / 1000.0})
	var final_cells: Array[int] = app.session.player.cells.duplicate()
	board.set_animations(false)
	app.empty_sample()
	mouse(start, MOUSE_BUTTON_LEFT, true)
	motion(end)
	mouse(end, MOUSE_BUTTON_LEFT, false)
	mouse(start, MOUSE_BUTTON_RIGHT, true)
	motion(point(4, 0))
	mouse(point(4, 0), MOUSE_BUTTON_RIGHT, false)
	await process_frame
	await RenderingServer.frame_post_draw
	check(final_cells == app.session.player.cells, "animations off same model end state")
	check(images.back().get_data() == surface.get_texture().get_image().get_data(), "animations off pixel-identical final frame")
	board.set_animations(true)
	for i: int in range(images.size()):
		var filename: String = "zs1-motion-%d-%02d.png" % [variant, i]
		# Small crop, native 1:1 pixels; absolute source bounds retained.
		var crop: Rect2i = Rect2i(Rect2(board.global_position + board.view.visible_bounds().position - Vector2(4, 4), Vector2(488, 92)))
		images[i].get_region(crop).save_png(output.path_join(filename))
		timeline[i]["file"] = filename
		timeline[i]["crop"] = [crop.position.x, crop.position.y, crop.size.x, crop.size.y]
	frames.append({"style": variant, "second_gesture_ms": second_ms, "parallel_cells": 20, "preview_static": true, "off_same_end": true, "timeline": timeline})

func load_probe() -> void:
	app.select_puzzle(2)
	app.empty_sample()
	app.board.fit_all()
	await process_frame
	app.board.measure_draws = true
	app.board.draw_times_us.clear()
	var begin: int = Time.get_ticks_usec()
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, true)
	motion(point(99, 0))
	mouse(point(99, 0), MOUSE_BUTTON_LEFT, false)
	var commit_us: int = Time.get_ticks_usec() - begin
	var searches: int = app.board.completion_searches
	await process_frame
	# One normal analysis update for the logical commit is allowed.
	searches = app.board.completion_searches
	var frame_times: Array[int] = []
	var previous: int = Time.get_ticks_usec()
	for i: int in range(18):
		await process_frame
		frame_times.append(Time.get_ticks_usec() - previous)
		previous = Time.get_ticks_usec()
	check(app.board.completion_searches == searches, "animation ticks do not search clues")
	check(not app.board.is_processing(), "animation ticker stops")
	check(app.session.player.cursor == 1, "100-cell stroke remains one action")
	measurements.append({"style": variant, "fixture": "F-03", "overview": true, "cells": 100,
		"input_commit_us": commit_us, "draw_us": app.board.draw_times_us.duplicate(), "frame_us": frame_times,
		"renderer": RenderingServer.get_video_adapter_name(), "real_mouse_acceptance": "OPEN ZS1-M01"})
	app.board.measure_draws = false

func stroke_probe() -> void:
	# Controlled clock, real production draw path: geometry evidence, not FPS.
	app.select_puzzle(0)
	app.empty_sample()
	var board = app.board
	while board.view.cell_size < 72:
		board.zoom(1, board.view.viewport.get_center())
	board.view.center = Vector2(2, 2)
	board.view.reframe()
	board.animation_clock = func() -> int: return probe_time
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, true)
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, false)
	mouse(point(1, 0), MOUSE_BUTTON_RIGHT, true)
	mouse(point(1, 0), MOUSE_BUTTON_RIGHT, false)
	board.clear_pointer_hover()
	var crop: Rect2i = Rect2i(Rect2(board.global_position + board.view.cell_rect(Vector2i(0, 0)).position, Vector2(144, 72)))
	for elapsed: int in [0, 21, 49, 70, 98, 119, 140]:
		probe_time = 1000000 + elapsed * 1000
		board.marks.queue_redraw()
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		var filename: String = "zs1-strokes-%03d.png" % elapsed
		check(surface.get_texture().get_image().get_region(crop).save_png(output.path_join(filename)) == OK, "stroke frame saved")
		stroke_frames.append({"file": filename, "elapsed_ms": elapsed, "clock": "controlled production animation clock", "crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y], "cell_size": 72, "indices": [0, 1]})
	board.animation_clock = Time.get_ticks_usec
	board.clear_effects()

func point(x: int, y: int) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(Vector2i(x, y)).get_center()

func motion(p: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = p
	surface.push_input(event, true)

func mouse(p: Vector2, button: MouseButton, down: bool) -> void:
	motion(p)
	app.board.clear_clue_hover()
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	surface.push_input(event, true)
