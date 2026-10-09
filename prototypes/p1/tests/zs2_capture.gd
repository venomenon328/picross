extends "res://tests/zs1_capture.gd"
const Measurements = preload("res://tests/vs2_measurements.gd")
## Identical inputs on the previous regular main, selected study and new regular UI.
var role: String
var rework_sequences: Array = []
var fill_sequences: Array = []
var wave_sequence: Dictionary = {}

func rework_wave() -> void:
	app.select_puzzle(0)
	empty_sample()
	app.board.working_size()
	app.board.hover = Vector2i(1, 2)
	await process_frame
	await RenderingServer.frame_post_draw
	var crop: Rect2i = Rect2i(Rect2(app.board.global_position + app.board.view.cell_rect(Vector2i(1, 2)).position, Vector2(17 * 24, 24)))
	var blank: String = "zs2-wave-blank.png"
	surface.get_texture().get_image().get_region(crop).save_png(output.path_join(blank))
	probe_time = 1000000
	app.board.animation_clock = func() -> int: return probe_time
	mouse(point(1, 2), MOUSE_BUTTON_LEFT, true)
	motion(point(17, 2))
	mouse(point(17, 2), MOUSE_BUTTON_LEFT, false)
	app.board.clear_effects()
	mouse(point(17, 2), MOUSE_BUTTON_RIGHT, true)
	motion(point(1, 2))
	await process_frame
	await RenderingServer.frame_post_draw
	var preview: String = "zs2-wave-preview.png"
	surface.get_texture().get_image().get_region(crop).save_png(output.path_join(preview))
	mouse(point(1, 2), MOUSE_BUTTON_RIGHT, false)
	var timeline: Array = []
	for elapsed: int in [0, 12, 105, 180, 210, 390]:
		probe_time = 1000000 + elapsed * 1000
		app.board.marks.queue_redraw()
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		var file: String = "zs2-wave-%03d.png" % elapsed
		surface.get_texture().get_image().get_region(crop).save_png(output.path_join(file))
		timeline.append({"file": file, "elapsed_ms": elapsed})
	wave_sequence = {"blank": blank, "preview": preview, "frames": timeline, "cell_size": 24,
		"crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y], "start": [17, 2], "end": [1, 2],
		"effective_cells": 17, "target": "fill to X", "clock": "controlled production animation clock"}
	app.board.animation_clock = Time.get_ticks_usec

func rework_motion(marker: String = "x") -> void:
	surface.size = Vector2i(1920, 1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	for pitch: int in [12, 24, 36]:
		app.select_puzzle(0)
		empty_sample()
		app.board.working_size()
		while not is_equal_approx(app.board.view.cell_size, pitch):
			app.board.zoom(1 if pitch > app.board.view.cell_size else -1, app.board.view.viewport.get_center())
		app.board.view.center = Vector2(10, 10)
		app.board.view.reframe()
		app.board.clear_pointer_hover()
		await process_frame
		await RenderingServer.frame_post_draw
		var crop: Rect2i = Rect2i(Rect2(app.board.global_position + app.board.view.cell_rect(Vector2i(1, 1)).position, Vector2.ONE * pitch))
		var prefix: String = "zs2-%s-%d" % [marker, pitch]
		var button: MouseButton = MOUSE_BUTTON_RIGHT if marker == "x" else MOUSE_BUTTON_LEFT
		var blank: String = prefix + "-blank.png"
		check(surface.get_texture().get_image().get_region(crop).save_png(output.path_join(blank)) == OK, "blank native crop")
		probe_time = 1000000
		app.board.animation_clock = func() -> int: return probe_time
		mouse(point(1, 1), button, true)
		mouse(point(1, 1), button, false)
		app.board.clear_pointer_hover()
		var controlled: Array = []
		var times: Array = [0, 30, 75, 105, 150, 180, 210] if marker == "x" else [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 209, 210]
		for elapsed: int in times:
			probe_time = 1000000 + elapsed * 1000
			app.board.marks.queue_redraw()
			await process_frame
			await process_frame
			await RenderingServer.frame_post_draw
			var file: String = prefix + "-controlled-%03d.png" % elapsed
			check(surface.get_texture().get_image().get_region(crop).save_png(output.path_join(file)) == OK, "controlled native X")
			controlled.append({"file": file, "elapsed_ms": elapsed})
		# Same real input and draw function, wall clock restored for the live run.
		var view_state: Dictionary = app.board.capture_view()
		empty_sample()
		app.board.restore_view(view_state)
		var rendered: Array[int] = [0]
		app.board.animation_clock = func() -> int:
			rendered[0] = Time.get_ticks_usec()
			return rendered[0]
		app.board.clear_pointer_hover()
		await process_frame
		await RenderingServer.frame_post_draw
		mouse(point(1, 1), button, true)
		mouse(point(1, 1), button, false)
		var began: int = int(app.board.effects[21].start)
		app.board.clear_pointer_hover()
		var live: Array = []
		var pictures: Array[Image] = []
		for i: int in range(22):
			app.board.marks.queue_redraw()
			await process_frame
			await RenderingServer.frame_post_draw
			pictures.append(surface.get_texture().get_image())
			live.append({"file": prefix + "-live-%02d.png" % i, "elapsed_ms": float(rendered[0] - began) / 1000.0})
		check(not app.board.is_processing(), "real-time X ends without callback")
		var context: String = prefix + "-context.png"
		pictures.back().save_png(output.path_join(context))
		for i: int in range(pictures.size()):
			pictures[i].get_region(crop).save_png(output.path_join(live[i].file))
		var sequences: Array = rework_sequences if marker == "x" else fill_sequences
		sequences.append({"cell_size": pitch, "blank": blank, "context": context,
			"crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y], "controlled": controlled,
			"live": live, "clock": "Time.get_ticks_usec sampled by production draw", "native_scale": "1:1"})
	app.board.animation_clock = Time.get_ticks_usec

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	role = OS.get_environment("ZS2_VARIANT")
	baseline = role == "before"
	variant = 0 if baseline else 2
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
		for zoom_attempt: int in range(25):
			var before: float = app.board.view.cell_size
			if absf(before-float(spec[4])) < 0.01: break
			app.board.zoom(1 if before < float(spec[4]) else -1,app.board.view.viewport.get_center())
			if is_equal_approx(before,app.board.view.cell_size): break
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
		measurements.back().real_mouse_acceptance = "OPEN VS2-M01; ZS2-M01 passed historically" if app.board.has_method("set_mode") else "Historical developer reference; no new owner acceptance claimed"
		await color_load_probe()
		await stroke_probe()
		await rework_motion()
		await rework_motion("fill")
		await rework_wave()
	var report: Dictionary = {"role": role, "renderer": RenderingServer.get_video_adapter_name(),
		"display": DisplayServer.get_name(), "captures": captures, "frames": frames,
		"stroke_frames": stroke_frames, "rework_sequences": rework_sequences, "wave_sequence": wave_sequence, "fill_sequences": fill_sequences, "measurements": measurements, "specimens": specimens, "failures": failures}
	FileAccess.open(output.path_join("zs2-" + role + ".json"), FileAccess.WRITE).store_string(JSON.stringify(report, "\t") + "\n")
	if failures == 0:
		print("ZS2_CAPTURE_OK role=", role, " captures=", captures.size())
	quit(0 if failures == 0 else 1)

func shot(name: String) -> void:
	await super.shot(name)
	var record: Dictionary = captures.back()
	if role == "after":
		record.full_view = Measurements.capture(app.board)
	var filename: String = "zs2-%s-%s.png" % [role, name]
	check(DirAccess.rename_absolute(output.path_join(record.file), output.path_join(filename)) == OK, "rename bound comparison")
	record.file = filename
	if role == "after":
		check(app.board.get_script().resource_path == "res://ui/full_view_board.gd", "actual regular renderer")
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
	await create_timer(0.40).timeout
	check(app.board.completion_searches == searches and not app.board.is_processing(), "F07 ticker neither analyzes nor keeps running")
	measurements.append({"fixture": "F-07", "overview": true, "cells": 400, "actions": 4,
		"input_commit_us": input_us, "draw_us": app.board.draw_times_us.duplicate(), "frame_us": frame_times,
		"renderer": RenderingServer.get_video_adapter_name(), "real_mouse_acceptance": "OPEN ZS2-M01"})
	app.board.measure_draws = false


func stroke_probe() -> void:
	# The 72px spatial renderer oracle is a developer component probe, not an
	# offered regular zoom. Actual regular 12/24/36px ink is checked separately.
	app.select_puzzle(0)
	empty_sample()
	var regular = app.board
	var component = load("res://ui/chalkboard_board.gd").new()
	component.session = app.session
	component.size = regular.size
	component.position = regular.position
	component.ui_scale = app.ui_scale
	# Pencil marks are drawn behind the board's grid layer. Book rendering
	# supplies the paper externally; the non-book opaque viewport would hide it.
	component.book_layout = true
	component.book_inset = Vector2(210,126)*app.ui_scale
	component.book_grid_size = component.size-component.book_inset-Vector2(12,12)
	regular.hide()
	app.work.add_child(component)
	app.board = component
	component.edited.connect(app.refresh)
	await super.stroke_probe()
	component.get_parent().remove_child(component)
	component.queue_free()
	app.board = regular
	regular.session = app.session
	regular.layout_key = ""
	regular._layout()
	regular.show()
