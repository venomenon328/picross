extends SceneTree
## Current native cell animation: temporary original crops for Python oracles.
const Store = preload("res://model/save_store.gd")
var app: Control
var surface: SubViewport
var output: String
var failures: int = 0
var probe_time: int = 1000000

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	if not condition:
		failures += 1
		printerr("CURRENT MOTION FAIL: ", message)

func point(x: int, y: int) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(Vector2i(x, y)).get_center()

func motion(p: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = p
	event.button_mask = MOUSE_BUTTON_MASK_LEFT if app.board.pan_button == MOUSE_BUTTON_LEFT else MOUSE_BUTTON_MASK_LEFT if app.board.held_button == MOUSE_BUTTON_LEFT else (MOUSE_BUTTON_MASK_RIGHT if app.board.held_button == MOUSE_BUTTON_RIGHT else 0)
	surface.push_input(event, true)

func mouse(p: Vector2, button: MouseButton, down: bool) -> void:
	motion(p)
	app.board.clear_clue_hover()
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	surface.push_input(event, true)

var role: String
var rework_sequences: Array = []
var fill_sequences: Array = []
var wave_sequence: Dictionary = {}

func rework_wave() -> void:
	app.select_puzzle(0)
	empty_sample()
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
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
	for pitch: int in [24]:
		app.select_puzzle(0)
		empty_sample()
		app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
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
		var times: Array = [0, 105, 210] if marker == "x" else [0, 75, 105, 150, 210]
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
		# Keep draw, presentation-clock and readback times distinct. In particular,
		# the production clock stops being called once the effect has expired.
		# Buffer only timestamps here; serialize after the real animation window.
		var trace: Array = []
		var on_draw: Callable = func() -> void:
			trace.append(["draw", Time.get_ticks_usec(), rendered[0], app.board.effects.has(21)])
		var on_post: Callable = func() -> void:
			trace.append(["post", Time.get_ticks_usec(), rendered[0], app.board.effects.has(21)])
		app.board.marks.transitions.draw.connect(on_draw)
		RenderingServer.frame_post_draw.connect(on_post)
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
		for i: int in range(3):
			# Three actual rendered instants; no dense readback/PNG sequence.
			if i == 0:
				# Observe a completed early production draw. The first nonzero
				# atlas frame may still have no visible hatch pixels (observed at
				# 9ms on llvmpipe). Wait on post-draw timestamps, not an extra
				# pre-draw delay/readback; the independent oracle still requires
				# visible ink before 105ms and the unchanged second-stroke window.
				await RenderingServer.frame_post_draw
				while rendered[0] - began < 30000:
					await RenderingServer.frame_post_draw
			else:
				var target_ms: int = [105,230][i-1]
				while Time.get_ticks_usec()-began < target_ms*1000:
					await process_frame
				app.board.marks.queue_redraw()
				# Capture this frame without adding another process-frame wait.
				await RenderingServer.frame_post_draw
			trace.append(["read-before", Time.get_ticks_usec(), rendered[0], app.board.effects.has(21)])
			pictures.append(surface.get_texture().get_image())
			trace.append(["read-after", Time.get_ticks_usec(), rendered[0], app.board.effects.has(21)])
			live.append({"file": prefix + "-live-%02d.png" % i, "elapsed_ms": float(rendered[0] - began) / 1000.0})
		app.board.marks.transitions.draw.disconnect(on_draw)
		RenderingServer.frame_post_draw.disconnect(on_post)
		check(not app.board.is_processing(), "real-time X ends without callback")
		for i: int in range(pictures.size()):
			pictures[i].get_region(crop).save_png(output.path_join(live[i].file))
		var sequences: Array = rework_sequences if marker == "x" else fill_sequences
		sequences.append({"cell_size": pitch, "blank": blank,
			"crop": [crop.position.x, crop.position.y, crop.size.x, crop.size.y], "controlled": controlled,
			"timing_trace": {"began_usec": began, "columns": ["event", "wall_usec", "last_animation_clock_usec", "effect_active"], "events": trace},
			"live": live, "clock": "Time.get_ticks_usec sampled by production draw", "native_scale": "1:1"})
	app.board.animation_clock = Time.get_ticks_usec

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	role = OS.get_environment("ZS2_VARIANT")
	if output.is_empty() or DisplayServer.get_name() == "headless" or role != "after":
		quit(2)
		return
	Store.test_root_override = "user://zs2-capture-%d" % Time.get_ticks_usec()
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	app = preload("res://tests/book_fixture.gd").attach(surface)
	await process_frame
	await create_timer(0.3).timeout
	await rework_motion()
	await rework_motion("fill")
	await rework_wave()
	var report: Dictionary = {"role": role, "renderer": RenderingServer.get_video_adapter_name(),
		"display": DisplayServer.get_name(), "rework_sequences": rework_sequences, "wave_sequence": wave_sequence, "fill_sequences": fill_sequences, "failures": failures}
	FileAccess.open(output.path_join("zs2-" + role + ".json"), FileAccess.WRITE).store_string(JSON.stringify(report, "\t") + "\n")
	if failures == 0:
		print("ZS2_CAPTURE_OK role=", role)
	quit(0 if failures == 0 else 1)

func empty_sample() -> void:
	app._reset_selected()
	app.open_puzzle()
