extends "res://tests/zs1_capture.gd"
## Identical inputs on the previous regular main, selected study and new regular UI.
var role: String

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	role = OS.get_environment("ZS2_VARIANT")
	baseline = role == "before"
	variant = 2
	if output.is_empty() or DisplayServer.get_name() == "headless" or not role in ["before", "study", "after"]:
		quit(2)
		return
	Store.test_root_override = "user://zs2-capture-%d" % Time.get_ticks_usec()
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	app = load("res://study/main.tscn" if role == "study" else "res://main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	await create_timer(0.3).timeout
	for spec: Array in [
		[0, 1920, 1080, 1.0, 24.0, "f01-work"],
		[1, 1920, 1080, 1.0, 24.0, "f02-color"],
		[2, 1920, 1080, 1.0, 12.0, "f03-small"],
		[1, 1280, 720, 1.25, 24.0, "f02-compact"],
		[0, 1600, 900, 1.0, 36.0, "f01-1600"],
		[0, 1920, 1080, 1.0, 36.0, "f01-z150"],
		[2, 2560, 1440, 1.0, 72.0, "f03-z300"],
		[6, 1920, 1080, 1.0, 24.0, "f07-color100"],
		[6, 1280, 720, 1.25, 12.0, "f07-small"]]:
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
	if role == "after":
		await numeral_probe()
		await movement()
		await load_probe()
		measurements.back().real_mouse_acceptance = "OPEN ZS2-M01"
		await color_load_probe()
		await stroke_probe()
	var report: Dictionary = {"role": role, "renderer": RenderingServer.get_video_adapter_name(),
		"display": DisplayServer.get_name(), "captures": captures, "frames": frames,
		"stroke_frames": stroke_frames, "measurements": measurements, "specimens": specimens, "failures": failures}
	FileAccess.open(output.path_join("zs2-" + role + ".json"), FileAccess.WRITE).store_string(JSON.stringify(report, "\t") + "\n")
	if failures == 0:
		print("ZS2_CAPTURE_OK role=", role, " captures=", captures.size())
	quit(0 if failures == 0 else 1)

func shot(name: String) -> void:
	await super.shot(name)
	var record: Dictionary = captures.back()
	var filename: String = "zs2-%s-%s.png" % [role, name]
	check(DirAccess.rename_absolute(output.path_join(record.file), output.path_join(filename)) == OK, "rename bound comparison")
	record.file = filename
	if role == "after":
		check(app.board.get_script().resource_path == "res://ui/chalkboard_board.gd", "actual regular renderer")
		check(app.board.clue_font().get_font_name() == "Chalkboard", "actual regular Chalkboard")

func empty_sample() -> void:
	app._reset_selected()
	app.open_puzzle()

func numeral_probe() -> void:
	var specimen = load("res://tests/zs2_numerals.gd").new()
	specimen.session = Session.new(app.sessions[1].definition)
	specimen.size = Vector2(720, 445)
	surface.add_child(specimen)
	app.hide()
	await process_frame
	await RenderingServer.frame_post_draw
	var filename: String = "zs2-numerals.png"
	check(surface.get_texture().get_image().get_region(Rect2i(0, 0, 720, 445)).save_png(output.path_join(filename)) == OK, "regular numeral specimen")
	specimens.append({"file": filename, "label": "Artificial specimen through the regular clue renderer; no puzzle changes"})
	specimen.queue_free()
	app.show()
	await process_frame

func color_load_probe() -> void:
	app.select_puzzle(6)
	empty_sample()
	app.board.fit_all()
	await process_frame
	app.board.measure_draws = true
	app.board.draw_times_us.clear()
	var began: int = Time.get_ticks_usec()
	for row: int in range(4):
		app.board.active_color = row + 1
		mouse(point(0, row), MOUSE_BUTTON_LEFT, true)
		motion(point(99, row))
		mouse(point(99, row), MOUSE_BUTTON_LEFT, false)
	check(app.session.player.cursor == 4, "F07 four rapid 100-cell strokes retained")
	check(app.mini.cells == app.session.player.cells, "F07 miniature immediately matches own cells")
	var input_us: int = Time.get_ticks_usec() - began
	await process_frame
	var searches: int = app.board.completion_searches
	var frame_times: Array[int] = []
	var previous: int = Time.get_ticks_usec()
	for i: int in range(18):
		await process_frame
		frame_times.append(Time.get_ticks_usec() - previous)
		previous = Time.get_ticks_usec()
	check(app.board.completion_searches == searches and not app.board.is_processing(), "F07 ticker neither analyzes nor keeps running")
	measurements.append({"fixture": "F-07", "overview": true, "cells": 400, "actions": 4,
		"input_commit_us": input_us, "draw_us": app.board.draw_times_us.duplicate(), "frame_us": frame_times,
		"renderer": RenderingServer.get_video_adapter_name(), "real_mouse_acceptance": "OPEN ZS2-M01"})
	app.board.measure_draws = false
