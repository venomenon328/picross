extends SceneTree
## Finite B-A native proof. Actual renderer and pointer dispatch, synthetic inputs.
const Study = preload("res://study/book/main.gd")
const Main = preload("res://ui/main.gd")
const Current = preload("res://tests/current_visual_cases.gd")
var study: Study
var checks: int = 0
var failures: Array[String] = []
var output: String
var layouts: Array = []
var handoffs: Array = []

class Baseline extends Main:
	func create_store() -> SaveStore: return Study.Content.MemoryStore.new()
	func puzzle_definitions() -> Array[Dictionary]:
		var result: Array[Dictionary] = []
		var input: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://study/book/fixtures.json"))
		Registry.cached = input.registry
		for data: Dictionary in input.definitions: result.append(data)
		return result
	func validate_definition(data: Dictionary) -> String:
		return Definition.validate(data, {data.id: data.reveal.image})

func _initialize() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures.append(label)
		print("BOOK_STUDY_FAIL ", label)

func frames(count: int = 3) -> void:
	for i: int in range(count): await process_frame
	await RenderingServer.frame_post_draw

func screenshot(name: String) -> Image:
	await frames()
	var image: Image = root.get_texture().get_image()
	check(image.save_png(output.path_join(name+".png")) == OK, "native framebuffer " + name)
	return image

func fingerprint() -> Array:
	var result: Array = []
	for s: RefCounted in study.app.sessions:
		result.append([s.player.cells.duplicate(), s.player.history.duplicate(true), s.player.cursor, s.player.undo_used, s.completed])
	return result

func geometry(app: Control) -> Array:
	return [app.board.get_rect(), app.board.view.bounds(), app.board.view.cell_size,
		app.board.fit_ceiling, app.board.type_size, app.board.slot_pitch,
		app.board.reserve_slots, app.board.composition_envelope(), app.mini.get_rect(),
		app.palette_row.get_rect(), app.tools_scroll.get_rect(), app.title.get_rect()]

func button(down: bool, point: Vector2, index: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var event := InputEventMouseButton.new()
	event.position = point
	event.button_index = index
	event.pressed = down
	root.push_input(event, true)

func no_spoiler(image: Image, label: String) -> void:
	var data: PackedByteArray = image.get_data()
	var found: bool = false
	for i: int in range(0, data.size()-4, 64):
		if data[i] > 175 and data[i+1] < 85 and data[i+2] > 150:
			found = true
			break
	check(not found, "no synthetic magenta reveal in " + label)
	check(not "VERBORGENER" in study.app.title.text, "neutral work title " + label)
	check(study.app.reveal_view.artwork == null and not study.app.ending.visible, "no earned ending " + label)

func prepare_open(id: String) -> void:
	study.app.show_album()
	await frames()
	check(study.request_open(id), "ID-bound opening accepted " + id)
	check(not study.request_open("T-01"), "repeated request is discarded")
	while study.state == Study.State.PREPARING: await process_frame
	check(study.state == Study.State.OPENING, "actual texture preparation completes")

func run() -> void:
	output = OS.get_environment("BOOK_STUDY_OUTPUT")
	if output.is_empty(): quit(4); return
	root.gui_embed_subwindows = true
	root.size = Vector2i(1920, 1080)
	study = Study.new()
	root.add_child(study)
	await frames(6)
	if OS.get_cmdline_user_args().has("--movie"):
		await movie()
		return
	check(study.app.sessions.size() == 3, "only three fixed synthetic specimens")
	var before: Array = fingerprint()
	var writes_before: int = study.app.store.writes
	var start: Image = await screenshot("catalog")
	no_spoiler(start, "catalog")
	# Real pointer activation through the existing catalog card.
	var card: Control = study.app.album.choices[1]
	var point: Vector2 = card.get_global_rect().get_center()
	button(true, point)
	button(false, point)
	await frames(1)
	check(study.selected_id == "T-06", "actual catalog pointer selects correct ID")
	check(not study.request_open("T-08"), "no queued second selection")
	while study.state == Study.State.PREPARING: await process_frame
	var mid_saved: bool = false
	var late_saved: bool = false
	while study.state == Study.State.OPENING:
		if study.elapsed > 1.0 and not mid_saved:
			mid_saved = true
			no_spoiler(await screenshot("opening-middle"), "moving front")
			button(true, Vector2(500, 400))
			button(false, Vector2(500, 400))
		if study.elapsed > 1.9 and not late_saved:
			late_saved = true
			no_spoiler(await screenshot("opening-back"), "blank underside")
		await process_frame
	check(study.elapsed == 3.0 and study.motion_wall_seconds >= 2.8, "natural total three-second movement")
	check(fingerprint() == before, "motion and blocked pointer input preserve cells/history/redo")
	check(study.app.store.writes == writes_before, "presentation creates no save action")
	var motion_ms: Array[float] = study.frames_ms.duplicate()
	var motion_wall: float = study.motion_wall_seconds
	# Quiet measurement excludes screenshot readback/PNG work from frame times.
	await prepare_open("T-06")
	while study.state == Study.State.OPENING: await process_frame
	var quiet_ms: Array[float] = study.frames_ms.duplicate()
	var quiet_wall: float = study.motion_wall_seconds
	var baseline := Baseline.new()
	baseline.size = Vector2(root.size)
	root.add_child(baseline)
	baseline.hide()
	baseline.process_mode = Node.PROCESS_MODE_DISABLED
	await frames()
	for index: int in range(3):
		var configuration: Array = Current.CONFIGURATIONS[index]
		root.size = configuration[0]
		study.set_ui_scale(configuration[1])
		baseline.size = Vector2(configuration[0])
		baseline.set_ui_scale(configuration[1])
		var id: String = ["T-01", "T-06", "T-08"][index]
		baseline.select_puzzle(index)
		await prepare_open(id)
		# Controlled final pose checks the SAME actual viewport/material against
		# direct UI, separately from the unaccelerated motion above.
		study.set_process(false)
		study._pose(1)
		var textured: Image = await screenshot("handoff-texture-%d" % configuration[0].x)
		var expected: Array = geometry(baseline)
		check(geometry(study.app) == expected, "unchanged regular fit/font/slot/control geometry " + id)
		study._settle(true)
		study.set_process(true)
		var direct: Image = await screenshot("work-%d" % configuration[0].x)
		no_spoiler(direct, "stable " + id)
		check(geometry(study.app) == expected, "handoff preserves geometry " + id)
		check(study.app.board.layout_valid, "valid fit " + id)
		check(study.app.board.view.cell_size <= 24.0, "small raster preserves zoom wish " + id)
		study.app.hide()
		study.hide()
		baseline.show()
		await screenshot("baseline-%d" % configuration[0].x)
		baseline.hide()
		study.show()
		study.app.show()
		layouts.append({"configuration": configuration, "id": id, "geometry": expected})
		var bounds := Rect2i(study.app.board.position+study.app.board.view.bounds().position, study.app.board.view.bounds().size)
		# Preserve original full-resolution pairs for independent pixel inspection.
		handoffs.append({"configuration": configuration, "board_pixels": bounds, "texture": "handoff-texture-%d.png" % configuration[0].x, "direct": "work-%d.png" % configuration[0].x})
		var report: Dictionary = study.resource_report()
		check(report.ui_capture_targets == 0 and report.catalog_rgba_textures == 0, "transient textures released " + id)
	baseline.free()
	# Existing popups and gestures are cancelled before a page can move.
	study.app.show_album()
	await frames()
	study.app.album.sort_choice.show_popup()
	await frames()
	check(study.app.album.sort_choice.get_popup().visible, "actual regular popup opened")
	check(study.request_open("T-06"), "open dismisses popup before capture")
	check(not study.app.album.sort_choice.get_popup().visible, "no global popup bypasses input lock")
	button(true, Vector2(400, 300), MOUSE_BUTTON_WHEEL_UP)
	check(study.release_barrier and study.app.process_mode == Node.PROCESS_MODE_DISABLED, "preparing input remains locked")
	study.interrupt("focus")
	await frames()
	check(not study.release_barrier, "wheel event cannot leave a held-button lock")
	var gesture_cells: Array = fingerprint()
	var start_cell: Vector2 = study.app.board.global_position+study.app.board.view.origin+Vector2(5.5, 5.5)*study.app.board.view.cell_size
	button(true, start_cell)
	check(study.app.session.gesture.active, "actual cell gesture exists before leaving")
	study.app.show_album()
	button(false, start_cell)
	await frames()
	check(not study.app.session.gesture.active and fingerprint() == gesture_cells, "leaving cancels gesture without commit")
	# Interrupted preparation and movement: stale awaits cannot restore old pages.
	for reason: String in ["resize", "ui-scale", "focus", "leave"]:
		study.app.show_album()
		await frames()
		var cells: Array = fingerprint()
		check(study.request_open("T-06"), "interruption starts " + reason)
		var token: int = study.generation
		if reason == "resize": root.size = Vector2i(1920, 1080)
		elif reason == "ui-scale": study.set_ui_scale(1.0)
		elif reason == "focus": study._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
		else:
			study.interrupt("leave")
			study.app.show_album()
		await frames(8)
		check(study.generation > token and study.state == (Study.State.CATALOG if reason == "leave" else Study.State.WORK), "stable interrupted end state " + reason)
		check(study.capture == null and (not study.leaf.visible or study.leaf_material.get_shader_parameter("turn") == 1.0), "no half leaf or stale viewport " + reason)
		check(fingerprint() == cells, "interruption has no cell/history effect " + reason)
		check(not study.release_barrier, "input barrier eventually releases " + reason)
	await prepare_open("T-01")
	button(true, Vector2(400, 300))
	study.interrupt("focus")
	await frames()
	check(study.release_barrier and study.app.process_mode == Node.PROCESS_MODE_DISABLED, "held blocked button cannot become a gesture")
	var cell_point: Vector2 = study.app.board.global_position+study.app.board.view.origin+Vector2(5.5, 5.5)*study.app.board.view.cell_size
	button(false, cell_point)
	await frames()
	check(not study.release_barrier and not study.app.session.gesture.active, "consumed release cannot commit")
	var old_cursor: int = study.app.session.player.cursor
	button(true, cell_point)
	button(false, cell_point)
	await frames()
	check(study.app.session.player.cursor == old_cursor+1, "fresh actual pointer gesture works after interruption")
	var report: Dictionary = {"checks": checks, "failures": failures, "layouts": layouts, "handoffs": handoffs,
		"resources": study.resource_report(), "motion_frame_ms_with_captures": motion_ms, "motion_wall_seconds_with_captures": motion_wall,
		"motion_frame_ms_quiet": quiet_ms, "motion_wall_seconds_quiet": quiet_wall,
		"engine": Engine.get_version_info(), "display": DisplayServer.get_name(), "adapter": RenderingServer.get_video_adapter_name(),
		"renderer": RenderingServer.get_current_rendering_method(), "logical_window": root.size,
		"screen_size": DisplayServer.screen_get_size(), "screen_scale": DisplayServer.screen_get_scale(), "screen_dpi": DisplayServer.screen_get_dpi()}
	var file := FileAccess.open(output.path_join("native.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t")+"\n")
	file.close()
	study.free()
	print("BOOK_STUDY_OK checks=", checks, " failures=", failures.size())
	quit(0 if failures.is_empty() else 4)

func movie() -> void:
	await prepare_open("T-06")
	while study.state == Study.State.OPENING: await process_frame
	await frames(8)
	print("BOOK_STUDY_MOVIE_OK total=", study.elapsed, " fixed_fps=30 native_motion_separately_measured=true")
	study.free()
	quit(0 if failures.is_empty() else 4)
