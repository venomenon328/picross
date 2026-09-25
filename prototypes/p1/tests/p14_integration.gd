extends SceneTree
## Synthetic viewport input, normal Main/Board/SaveStore, and a real second process.
const SaveStore = preload("res://model/save_store.gd")
const Main = preload("res://ui/main.gd")

var app: Main
var output: FileAccess
var dispatch_usec: int = 0
var frames_usec: int = 0

func _initialize() -> void:
	call_deferred("run")

func fail(message: String) -> void:
	print("P1_INTEGRATION_FAIL: ", message)
	quit(4)

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	var trace_path: String = OS.get_environment("P1_INTEGRATION_TRACE")
	var plan_path: String = OS.get_environment("P1_INTEGRATION_PLAN")
	var expected_path: String = OS.get_environment("P1_INTEGRATION_EXPECTED")
	var start_number: int = int(OS.get_environment("P1_INTEGRATION_START"))
	var count: int = int(OS.get_environment("P1_INTEGRATION_COUNT"))
	if isolated.is_empty() or trace_path.is_empty() or plan_path.is_empty() or expected_path.is_empty():
		fail("isolated root, plan, trace and expected file required")
		return
	SaveStore.test_root_override = isolated
	root.size = Vector2i(1600, 900)
	app = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	app.select_puzzle(2)
	await process_frame
	await process_frame
	if OS.get_cmdline_user_args().has("--read"):
		verify_restart(expected_path)
		return
	var plan: Variant = JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	if not plan is Array or plan.size() != 500:
		fail("plan must contain exactly 500 actions")
		return
	if count <= 0 or start_number < 0 or start_number + count > 500:
		fail("invalid action segment")
		return
	output = FileAccess.open(trace_path, FileAccess.WRITE if start_number == 0 else FileAccess.READ_WRITE)
	if output == null:
		fail("trace cannot be opened")
		return
	if start_number > 0:
		output.seek_end()
	var begun: int = Time.get_ticks_usec()
	for index: int in range(start_number, start_number + count):
		var action: Dictionary = plan[index]
		var before: Array[int] = app.session.player.cells.duplicate()
		var before_cursor: int = app.session.player.cursor
		await perform(action)
		if app.session == null:
			fail("missing F-03 session at action %d" % int(action.number))
			return
		var changes: Array[Dictionary] = []
		for i: int in range(before.size()):
			if before[i] != app.session.player.cells[i]:
				changes.append({"index": i, "before": before[i], "after": app.session.player.cells[i]})
		var player = app.session.player
		var record: Dictionary = {"number": int(action.number), "kind": str(action.kind), "changes": changes,
			"cursor": player.cursor, "history_size": player.history.size(), "undo_used": player.undo_used,
			"history_tail": player.history[-1] if not player.history.is_empty() else [],
			"redo_next": player.history[player.cursor] if player.cursor < player.history.size() else [],
			"view": view_record(), "row_reads": app.board.row_clue_reads.duplicate(true),
			"column_reads": app.board.column_clue_reads.duplicate(true),
			"dispatch_us": dispatch_usec, "frame_wait_us": frames_usec,
			"save_in_dispatch": action.kind in ["cell", "undo", "redo"]}
		if action.kind == "cell" and player.cursor == before_cursor:
			fail("ineffective cell gesture at action %d" % int(action.number))
			return
		output.store_line(JSON.stringify(record))
		output.flush()
	output.close()
	var final_state: Dictionary = {"cells": app.session.player.cells, "history": app.session.player.history,
		"cursor": app.session.player.cursor, "undo_used": app.session.player.undo_used,
		"view": view_record(), "row_reads": app.board.row_clue_reads,
		"column_reads": app.board.column_clue_reads,
		"elapsed_us": Time.get_ticks_usec() - begun,
		"engine": Engine.get_version_info(), "renderer": {"display": DisplayServer.get_name(), "configured_method": str(ProjectSettings.get_setting("rendering/renderer/rendering_method", "unknown"))}}
	var final_file: FileAccess = FileAccess.open(trace_path + ".final.json", FileAccess.WRITE)
	final_file.store_string(JSON.stringify(final_state) + "\n")
	final_file.close()
	print("P1_INTEGRATION_WRITE_OK start=", start_number, " count=", count, " cursor=", app.session.player.cursor,
		" history=", app.session.player.history.size())
	app.leave_app()

func verify_restart(path: String) -> void:
	var expected: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not expected is Dictionary:
		fail("invalid expected restart state")
		return
	var player = app.session.player
	if not cells_match(player.cells, expected.cells) or not history_match(player.history, expected.history) or player.cursor != int(expected.cursor) or player.undo_used != bool(expected.undo_used):
		fail("cells/history/cursor/undo_used differ after real process restart")
		return
	if not view_match(view_record(), expected.view) or not reads_match(app.board.row_clue_reads, expected.row_reads) or not reads_match(app.board.column_clue_reads, expected.column_reads):
		fail("view or individual semantic clue reads differ after real process restart")
		return
	if player.cursor >= player.history.size():
		fail("restart expected a nontrivial redo branch")
		return
	# Redo through the same UI button signal used by a completed button command.
	var redo: Array = player.history[player.cursor]
	ui_command(app.redo_button)
	await tick()
	if player.cursor != int(expected.cursor) + 1:
		fail("redo command did not advance after restart")
		return
	for change: Dictionary in redo:
		if player.cells[int(change.index)] != int(change.after):
			fail("redo changed wrong cell after restart")
			return
	print("P1_INTEGRATION_READ_OK cells/history/view/clues/redo")
	quit(0)

func cells_match(actual: Array, expected: Array) -> bool:
	if actual.size() != expected.size():
		return false
	for i: int in range(actual.size()):
		if int(actual[i]) != int(expected[i]):
			return false
	return true

func history_match(actual: Array, expected: Array) -> bool:
	if actual.size() != expected.size():
		return false
	for i: int in range(actual.size()):
		if actual[i].size() != expected[i].size():
			return false
		for j: int in range(actual[i].size()):
			for key: String in ["index", "before", "after"]:
				if int(actual[i][j][key]) != int(expected[i][j][key]):
					return false
	return true

func reads_match(actual: Array, expected: Array) -> bool:
	if actual.size() != expected.size():
		return false
	for i: int in range(actual.size()):
		if str(actual[i].anchor) != str(expected[i].anchor):
			return false
		for key: String in ["start", "end"]:
			if actual[i].has(key) != expected[i].has(key):
				return false
			if actual[i].has(key) and int(actual[i][key]) != int(expected[i][key]):
				return false
	return true

func view_match(actual: Dictionary, expected: Dictionary) -> bool:
	if actual.overview != expected.overview or actual.tool != expected.tool or int(actual.active_color) != int(expected.active_color) or not is_equal_approx(float(actual.cell_size), float(expected.cell_size)):
		return false
	for key: String in ["center", "viewport"]:
		if actual[key].size() != expected[key].size():
			return false
		for i: int in range(actual[key].size()):
			if absf(float(actual[key][i]) - float(expected[key][i])) > 0.001:
				return false
	return true

func view_record() -> Dictionary:
	var board = app.board
	return {"center": [board.view.center.x, board.view.center.y], "cell_size": board.view.cell_size,
		"overview": board.overview, "active_color": board.active_color,
		"tool": "hand" if board.hand else ("erase" if board.eraser else "fill"),
		"viewport": [board.view.viewport.position.x, board.view.viewport.position.y,
			board.view.viewport.size.x, board.view.viewport.size.y]}

func perform(action: Dictionary) -> void:
	dispatch_usec = 0
	frames_usec = 0
	match str(action.kind):
		"cell":
			app.board.active_color = int(action.color)
			app.set_tool(str(action.tool))
			var button: MouseButton = MOUSE_BUTTON_RIGHT if action.button == "right" else MOUSE_BUTTON_LEFT
			var start: Vector2 = cell_point(action.start)
			var end: Vector2 = cell_point(action.end)
			press(start, button)
			if action.has("via"):
				motion(cell_point(action.via), button)
			motion(end, button)
			release(end, button)
		"mini":
			var desired: Vector2 = Vector2(float(action.point[0]) / 100.0, float(action.point[1]) / 100.0)
			var local: Vector2 = app.mini.image_rect().size * desired
			mini_button(local, true)
			await tick()
			mini_button(local, false)
		"pan":
			var point: Vector2 = app.board.get_global_transform() * app.board.view.viewport.get_center()
			press(point, MOUSE_BUTTON_MIDDLE)
			motion(point + Vector2(action.delta[0], action.delta[1]), MOUSE_BUTTON_MIDDLE)
			release(point + Vector2(action.delta[0], action.delta[1]), MOUSE_BUTTON_MIDDLE)
		"zoom":
			var point: Vector2 = app.board.get_global_transform() * app.board.view.viewport.get_center()
			press(point, MOUSE_BUTTON_WHEEL_UP if int(action.direction) > 0 else MOUSE_BUTTON_WHEEL_DOWN)
		"hint":
			var axis: String = str(action.axis)
			var index: int = int(action.index)
			var board = app.board
			var area: Rect2 = board.row_clue_area() if axis == "row" else board.column_clue_area()
			var cell: Vector2 = board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
			var local: Vector2 = Vector2(area.get_center().x, cell.y) if axis == "row" else Vector2(cell.x, area.get_center().y)
			var point: Vector2 = board.get_global_transform() * local
			var pitch: float = float(board.clue_layout(axis, index).slot_extent)
			var delta: Vector2 = Vector2(pitch * float(action.slots), 0) if axis == "row" else Vector2(0, pitch * float(action.slots))
			press(point, MOUSE_BUTTON_MIDDLE)
			motion(point + delta, MOUSE_BUTTON_MIDDLE)
			release(point + delta, MOUSE_BUTTON_MIDDLE)
		"undo":
			ui_command(app.undo_button)
		"redo":
			ui_command(app.redo_button)
		_:
			fail("unknown action kind")
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

func mini_button(local: Vector2, down: bool) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = local
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = down
	var started: int = Time.get_ticks_usec()
	app.mini._gui_input(event)
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
