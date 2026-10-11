extends SceneTree
## Developer-only native experiment. Runtime renderer and puzzle bytes unchanged.
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")
var app: Control
var output: String
var plan: Dictionary
var draws: Array[int] = [0, 0, 0]
var failures: int = 0
var fixture: int = 1
var width: int = 40
var height: int = 40

func _initialize() -> void:
	call_deferred("run")

func require(ok: bool, message: String) -> void:
	if not ok:
		failures += 1
		printerr("PERF_B_FAIL: ", message)

func sample(density: String) -> Dictionary:
	var fresh: Session = Session.new(app.sessions[fixture].definition)
	var changes: Array = []
	for i: int in range(width*(height-2)):
		if density == "dense" or i % 31 == 0:
			changes.append({"index": i, "before": -1, "after": 0 if i % 5 == 0 else 1 + i % fresh.definition.palette.size()})
	require(fresh.player.commit(changes), "synthetic history transaction")
	fresh.completed = fresh.is_solution()
	app.sessions[fixture] = fresh
	app.session = fresh
	app.board.session = fresh
	app.board.clear_effects()
	app.board.preview.clear()
	var view: Dictionary = app.board.capture_view()
	var snapshot: Dictionary = Store.snapshot(fresh, view)
	require(Store.validate(snapshot, fresh.definition).is_empty(), "full schema-1 validation")
	var invalid: Dictionary = snapshot.duplicate(true)
	invalid.cells[0] = 4 if int(invalid.cells[0]) != 4 else 3
	require(not Store.validate(invalid, fresh.definition).is_empty(), "mismatched history negative control")
	return snapshot

func motion(cell: Vector2i, mask: int = 0) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = app.board.global_position + app.board.view.cell_rect(cell).get_center()
	event.button_mask = mask
	root.push_input(event, true)

func stroke(row: int, button: MouseButton) -> void:
	for pressed: bool in [true, false]:
		var event: InputEventMouseButton = InputEventMouseButton.new()
		var cell: Vector2i = Vector2i(0 if pressed else width-1, row)
		event.position = app.board.global_position + app.board.view.cell_rect(cell).get_center()
		event.button_index = button
		event.pressed = pressed
		event.button_mask = (MOUSE_BUTTON_MASK_LEFT if button == MOUSE_BUTTON_LEFT else MOUSE_BUTTON_MASK_RIGHT) if pressed else 0
		root.push_input(event, true)
		if pressed: motion(Vector2i(width-1, row), event.button_mask)

func frame() -> void:
	await process_frame
	await RenderingServer.frame_post_draw

func run() -> void:
	output = OS.get_environment("PERF_A_OUTPUT")
	plan = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("PERF_A_PLAN")))
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	Store.test_root_override = output.path_join("isolated-saves")
	app = load("res://main.tscn").instantiate()
	root.add_child(app)
	await frame()
	fixture = int(OS.get_environment("PERF_B_FIXTURE")) if OS.has_environment("PERF_B_FIXTURE") else 1
	app.select_puzzle(fixture)
	width=app.session.player.width
	height=app.session.player.height
	app.board.measure_draws = true
	app.board.draw.connect(func() -> void: draws[0] += 1)
	app.board.marks.draw.connect(func() -> void: draws[1] += 1)
	app.mini.draw.connect(func() -> void: draws[2] += 1)
	var ci: int = int(OS.get_environment("PERF_A_CONTEXT"))
	var context: Array = plan.contexts[ci]
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1920, 1080)
	if context[0] == "maximized": root.mode = Window.MODE_MAXIMIZED
	await create_timer(0.15).timeout
	app.set_ui_scale(float(context[1]))
	app.board.set_mode(str(context[2]))
	var view: Dictionary = app.board.capture_view()
	view.zoom = int(context[3])
	view.overview = OS.get_environment("PERF_A_OVERVIEW") == "1"
	app.board.restore_view(view)
	app.open_puzzle()
	await frame()
	await frame()
	var records: Array = []
	var saves: Dictionary = {}
	for density: String in plan.densities:
		for animations: bool in plan.animations:
			for scenario: String in plan.scenarios:
				for repetition: int in range(int(plan.repetitions)):
					var snapshot: Dictionary = sample(density)
					if not saves.has(density):
						saves[density] = snapshot
						FileAccess.open(output.path_join("synthetic-" + density + ".json"), FileAccess.WRITE).store_string(JSON.stringify(snapshot) + "\n")
					app.board.set_animations(animations)
					app.refresh()
					for f: int in range(int(plan.warmup_frames)):
						motion(Vector2i(f, 1))
						await frame()
					app.board.clear_effects()
					app.board.draw_times_us.clear()
					draws.fill(0)
					var intervals: Array = []
					var layer_cpu: Array = []
					var render_calls: Array = []
					var initial_stats: Dictionary = app.board.marks.get("stats").duplicate() if app.board.marks.get("stats") != null else {}
					var dispatch: Array = []
					var effects: Array = []
					var previous: int = Time.get_ticks_usec()
					for f: int in range(int(plan.sample_frames)):
						var offset: int = app.board.draw_times_us.size()
						var started: int = Time.get_ticks_usec()
						if scenario == "hover": motion(Vector2i((3 * f) % width, (7 * f) % (height-2)))
						elif f == 0: stroke(height-2 if scenario == "fill" else height-1, MOUSE_BUTTON_LEFT if scenario == "fill" else MOUSE_BUTTON_RIGHT)
						dispatch.append(Time.get_ticks_usec() - started)
						effects.append(app.board.effects.size())
						await frame()
						var build: int = 0
						for j: int in range(offset,app.board.draw_times_us.size()): build+=app.board.draw_times_us[j]
						layer_cpu.append(build)
						render_calls.append([Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)])
						var now: int = Time.get_ticks_usec()
						intervals.append(now - previous)
						previous = now
					if scenario != "hover":
						require(app.session.player.cursor == 2, "40-cell native event commit")
						require(app.session.player.cells[(height-2 if scenario == "fill" else height-1) * width] == (1 if scenario == "fill" else 0), "target after stroke")
						require(app.session.player.history[-1].size()==width,"entire native 40-cell transaction")
						for x: int in range(width):
							require(app.session.player.cells[(height-2 if scenario=="fill" else height-1)*width+x]==(1 if scenario=="fill" else 0),"entire native target row")
					records.append({"density": density, "animations": animations, "scenario": scenario, "repetition": repetition,
						"frame_intervals_us": intervals, "dispatch_cpu_us": dispatch, "mark_build_cpu_us": app.board.draw_times_us.duplicate(),
						"all_layer_cpu_per_frame_us":layer_cpu,"render_calls_objects":render_calls,"initial_stats":initial_stats,"final_stats":app.board.marks.get("stats").duplicate() if app.board.marks.get("stats") != null else {},
						"draw_signals": draws.duplicate(), "active_effects": effects, "static_memory_bytes": OS.get_static_memory_usage(),
						"texture_memory_bytes": Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)})
	var report: Dictionary = {"fixture":fixture+1,"context_index": ci, "requested_context": context, "client": [root.size.x, root.size.y],
		"window_mode": root.mode, "screen": DisplayServer.window_get_current_screen(), "screen_size": [DisplayServer.screen_get_size().x, DisplayServer.screen_get_size().y],
		"screen_dpi": DisplayServer.screen_get_dpi(), "screen_scale": DisplayServer.screen_get_scale(),
		"window_vsync_mode":DisplayServer.window_get_vsync_mode(),"screen_refresh_hz":DisplayServer.screen_get_refresh_rate(),
		"renderer": RenderingServer.get_video_adapter_name(), "driver": RenderingServer.get_current_rendering_driver_name(),
		"overview_requested": view.overview, "overview_actual": app.board.overview, "actual_cell": app.board.view.cell_size,
		"fit_ceiling": app.board.fit_ceiling, "records": records, "failures": failures}
	FileAccess.open(output.path_join("measurements.json"), FileAccess.WRITE).store_string(JSON.stringify(report) + "\n")
	print("PERF_B_MEASURE_OK records=", records.size(), " failures=", failures)
	quit(0 if failures == 0 else 1)
