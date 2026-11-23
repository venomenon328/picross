extends SceneTree
## CI2-D: the same isolated profile across exactly two real processes.
const SaveStore = preload("res://model/save_store.gd")
const Main = preload("res://ui/main.gd")
const SyncCases = preload("res://tests/sync_cases.gd")
const Profile = preload("res://model/account_profile.gd")
const Session = preload("res://model/session.gd")
var account := Profile.new()
var restored: Session
var app: Main
var dispatch_usec: int = 0
var frames_usec: int = 0

func _initialize() -> void:
	call_deferred("run")

func fail(message: String) -> void:
	push_error("P1_INTEGRATION_FAIL: " + message)
	quit(4)

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	var trace_path: String = OS.get_environment("P1_INTEGRATION_TRACE")
	var plan_path: String = OS.get_environment("P1_INTEGRATION_PLAN")
	var stage: String = "reader" if OS.get_cmdline_user_args().has("--read") else "writer"
	if isolated.is_empty() or trace_path.is_empty() or plan_path.is_empty():
		fail("isolated root, plan and trace required")
		return
	if not account.open(SyncCases.HOST,SyncCases.ACCOUNT,SyncCases.DEVICE,SyncCases.EPOCH,stage == "writer"):
		fail("account open: " + str(account.reconciliation().reason))
		return
	SaveStore.test_root_override = isolated
	root.size = Vector2i(1920, 1080)
	app = preload("res://tests/book_fixture.gd").attach(root)
	await process_frame
	await process_frame
	var plan: Variant = JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	if not plan is Array or plan.size() != 17:
		fail("complete bounded plan required")
		return
	var output: FileAccess = FileAccess.open(trace_path, FileAccess.WRITE if stage == "writer" else FileAccess.READ_WRITE)
	if output == null:
		fail("trace cannot be opened")
		return
	if stage == "reader": output.seek_end()
	for action: Dictionary in plan:
		if action.process != stage: continue
		var before: Array[int] = app.session.player.cells.duplicate() if app.session != null else []
		if action.kind == "select": before.assign([])
		var began: int = Time.get_ticks_usec()
		if action.kind == "quit":
			app.leave_app()
			if not app.save_error.is_empty():
				fail("normal quit failed to save")
				return
		else:
			await perform(action)
		var checkpoint := account_checkpoint(stage, int(action.number))
		if checkpoint.has("error"):
			fail(checkpoint.error)
			return
		var player = app.session.player
		var changes: Array = []
		for i: int in range(before.size()):
			if before[i] != player.cells[i]:
				changes.append({"index":i,"before":before[i],"after":player.cells[i]})
		output.store_line(JSON.stringify({"action":action,"changes":changes,"cells":player.cells,
			"history":player.history,"cursor":player.cursor,"undo_used":player.undo_used,
			"view":app.board.capture_view(),"actual_cell":app.board.view.cell_size,"fit_ceiling":app.board.fit_ceiling,"elapsed_us":Time.get_ticks_usec()-began,
			"recent":app.RecentPuzzle.read(app.recent.path),"recent_id":app.recent_id(),
			"account":checkpoint,"pid":OS.get_process_id(),"engine":Engine.get_version_info()}))
		output.flush()
	output.close()
	print("CI2_D_HISTORY_", stage.to_upper(), "_OK")

func perform(action: Dictionary) -> void:
	match str(action.kind):
		"select":
			app.select_puzzle(int(action.index))
		"color":
			ui_command(app.actions["color-%d" % int(action.value)])
		"tool":
			ui_command(app.actions[str(action.value)])
		"cell":
			var button: MouseButton = MOUSE_BUTTON_RIGHT if action.button == "right" else MOUSE_BUTTON_LEFT
			var start: Vector2 = cell_point(action.start)
			var end: Vector2 = cell_point(action.end)
			motion(start, MOUSE_BUTTON_NONE)
			press(start, button)
			motion(end, button)
			release(end, button)
		"zoom":
			var point: Vector2 = app.board.get_global_transform() * app.board.view.viewport.get_center()
			press(point, MOUSE_BUTTON_WHEEL_DOWN)
		"undo":
			ui_command(app.undo_button)
		"redo":
			ui_command(app.redo_button)
		_:
			fail("unknown semantic command")
	await tick()
	await tick()

func cell_point(coords: Array) -> Vector2:
	var cell: Vector2i = Vector2i(int(coords[0]), int(coords[1]))
	var local: Vector2 = app.board.view.cell_rect(cell).get_center()
	if not app.board.view.viewport.has_point(local):
		fail("cell %s is outside viewport" % str(cell))
	return app.board.get_global_transform() * local

func ui_command(control: Button) -> void:
	if not control.is_visible_in_tree() or control.disabled:
		fail("UI history command unavailable: " + control.text)
		return
	var started: int = Time.get_ticks_usec()
	control.pressed.emit()
	dispatch_usec += Time.get_ticks_usec() - started

func press(point: Vector2, button: MouseButton) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = point
	event.global_position = point
	event.button_index = button
	event.button_mask = _mask(button)
	event.pressed = true
	var started: int = Time.get_ticks_usec()
	root.push_input(event, true)
	dispatch_usec += Time.get_ticks_usec() - started

func motion(point: Vector2, button: MouseButton) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = point
	event.global_position = point
	event.button_mask = _mask(button)
	var started: int = Time.get_ticks_usec()
	root.push_input(event, true)
	dispatch_usec += Time.get_ticks_usec() - started

func release(point: Vector2, button: MouseButton) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = point
	event.global_position = point
	event.button_index = button
	event.pressed = false
	var started: int = Time.get_ticks_usec()
	root.push_input(event, true)
	dispatch_usec += Time.get_ticks_usec() - started

func tick() -> void:
	var started: int = Time.get_ticks_usec()
	await process_frame
	frames_usec += Time.get_ticks_usec() - started

func _mask(button: MouseButton) -> int:
	if button == MOUSE_BUTTON_LEFT:
		return MOUSE_BUTTON_MASK_LEFT
	if button == MOUSE_BUTTON_RIGHT:
		return MOUSE_BUTTON_MASK_RIGHT
	if button == MOUSE_BUTTON_MIDDLE:
		return MOUSE_BUTTON_MASK_MIDDLE
	return 0

# The writer captures real action 11 and the later quit. Reader loads a distinct
# account session, repeats the planned redo there and saves that session.
func account_checkpoint(stage: String, number: int) -> Dictionary:
	if number == 10:
		restored = Session.new(app.session.definition)
		var base := Profile.Protocol.progress(SaveStore.snapshot(app.session,app.board.capture_view()))
		var record := {"kind":"snapshot","validation":"progress_structure_checked","save":base,
			"puzzle_id":base.definition_id,"definition_revision":base.definition_revision,"server_revision":7}
		if not account.accept_record(restored,record) or restored.player.undo(): return {"error":"receive basis"}
		return {}
	elif number == 11 or number == 14:
		if number == 11:
			if not restored.player.commit(app.session.player.history.back()): return {"error":"edit above basis"}
		else: restored.undo()
		restored.view_state = app.board.capture_view()
		var version := account.save(restored,restored.view_state)
		if version != (2 if number == 11 else 3): return {"error":"account write " + str(number)}
		if number == 11 and account.prepare(version,7).is_empty(): return {"error":"account prepare"}
	elif number == 15:
		var loaded := account.load_slot(app.session.definition)
		if loaded.status != "loaded": return {"error":"account restart"}
		restored = Session.new(app.session.definition)
		SaveStore.apply(loaded.data,restored)
	elif number == 16:
		var cursor := restored.player.cursor
		restored.redo()
		if restored.player.cursor != cursor + 1 or account.save(restored,restored.view_state) != 4:
			return {"error":"account redo"}
	else:
		return {}
	var request := account.resume_request()
	if request.is_empty(): return {"error":"missing prepared request in "+stage}
	return {"local":account.status().local,"seq":request.seq,"body_sha256":str(request.body).sha256_text(),
		"cursor":restored.player.cursor if restored != null else app.session.player.cursor}
