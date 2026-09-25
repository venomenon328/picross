extends SceneTree
## Two independent Godot processes exercise the actual P1 scene and save path.
const SaveStore = preload("res://model/save_store.gd")
const Main = preload("res://ui/main.gd")

func _initialize() -> void:
	call_deferred("run")

func require(condition: bool, label: String) -> bool:
	if not condition:
		push_error("P1_ROUNDTRIP_FAIL: " + label)
		quit(4)
	return condition

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if not require(not isolated.is_empty(), "isolated save root required"):
		return
	SaveStore.test_root_override = isolated
	root.size = Vector2i(1600, 900)
	var app: Main = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	if not require(app.mark_completed_clues and app.board.mark_completed_clues, "H1 new process defaults to enabled"):
		return
	if OS.get_cmdline_user_args().has("--write"):
		app.set_clue_completion(false)
		app.open_puzzle()
		await process_frame
		await process_frame
		var first_slot: Vector2 = app.board.view.cell_rect(Vector2i(10, 10)).get_center()
		if not require(app.board.view.viewport.has_point(first_slot), "F-01 first cell visible"):
			return
		app.board.pointer_press(first_slot, MOUSE_BUTTON_LEFT)
		app.board.pointer_release(first_slot, true)
		app.board.zoom(1, app.board.view.viewport.get_center())
		app.set_tool("erase")
		app.select_puzzle(1)
		await process_frame
		var second_slot: Vector2 = app.board.view.cell_rect(Vector2i(10, 10)).get_center()
		app.board.active_color = 3
		app.set_tool("fill")
		app.board.pointer_press(second_slot, MOUSE_BUTTON_LEFT)
		app.board.pointer_release(second_slot, true)
		app.board.fit_all()
		app.set_tool("hand")
	else:
		if not require(app.album_previews[0].cells[10 * 20 + 10] == 1 and app.album_previews[1].cells[10 * 40 + 10] == 3 and app.album_reveals[0].payload.is_empty() and app.album_reveals[1].payload.is_empty(), "album previews restored without reveal spoilers"):
			return
	app.select_puzzle(2)
	await process_frame
	await process_frame
	var board: Control = app.board
	var row: int = -1
	var column: int = -1
	for i: int in range(app.session.definition.rows.size()):
		if app.session.definition.rows[i].size() >= 5:
			row = i
			break
	for i: int in range(app.session.definition.columns.size()):
		if app.session.definition.columns[i].size() >= 5:
			column = i
			break
	if not require(row >= 0 and column >= 0, "long F-03 clue lines"):
		return
	if not require(app.session.definition.rows[row + 1].size() >= 5 and app.session.definition.columns[column + 1].size() >= 5, "neighbouring F-03 lines for both read anchors"):
		return
	if OS.get_cmdline_user_args().has("--write"):
		board.navigate_to(Vector2(0.55, 0.45))
		board.zoom(1, board.view.viewport.get_center())
		board.set_clue_step("row", row, 2)
		board.set_clue_step("column", column, int(board.clue_layout("column", column).max_offset))
		board.set_clue_step("row", row + 1, int(board.clue_layout("row", row + 1).max_offset))
		board.set_clue_step("column", column + 1, 2)
		board.active_color = 2
		app.set_tool("fill")
		var first: Vector2 = board.view.cell_rect(Vector2i(55, 45)).get_center()
		var second: Vector2 = board.view.cell_rect(Vector2i(56, 45)).get_center()
		if not require(board.view.viewport.has_point(first) and board.view.viewport.has_point(second), "selected cells visible"):
			return
		board.pointer_press(first, MOUSE_BUTTON_LEFT)
		board.pointer_release(first, true)
		board.pointer_press(second, MOUSE_BUTTON_RIGHT)
		board.pointer_release(second, true)
		app._undo()
		app.set_tool("hand")
		# Pure view movement is debounced and must be flushed by the normal quit path.
		board.navigate_to(Vector2(0.58, 0.43))
		if not require(app.session.gesture.begin(app.session.player, Vector2i(57, 45), 2), "unfinished preview before close"):
			return
		if not require(app.session.player.cursor == 1 and app.session.player.history.size() == 2 and app.session.player.undo_used, "write phase history"):
			return
		print("P1_ROUNDTRIP_WRITE_OK")
		app.leave_app()
	else:
		var session = app.session
		if not require(session.player.cursor == 1 and session.player.history.size() == 2 and session.player.undo_used, "history restored"):
			return
		if not require(session.player.cells[45 * 100 + 55] == 2 and session.player.cells[45 * 100 + 56] == -1 and session.player.cells[45 * 100 + 57] == -1, "cells restored without unfinished preview"):
			return
		if not require(board.hand and board.active_color == 2 and board.view.cell_size == 26.0 and absf(board.view.center.x - 58.0) < 1.0, "tool, color and raster view restored"):
			return
		var row_layout: Dictionary = board.clue_layout("row", row)
		var column_layout: Dictionary = board.clue_layout("column", column)
		if not require(board.row_clue_reads[row].anchor == "middle" and row_layout.offset == 2 and row_layout.start > 0 and row_layout.token_slot == 1 and board.column_clue_reads[column].anchor == "outer_start" and column_layout.offset == column_layout.max_offset and column_layout.start == 0 and column_layout.end == column_layout.slot_count - 2 and column_layout.token_slot == 1, "middle and direct outer semantic reads restored"):
			return
		var outer_row: Dictionary = board.clue_layout("row", row + 1)
		var middle_column: Dictionary = board.clue_layout("column", column + 1)
		if not require(board.row_clue_reads[row + 1].anchor == "outer_start" and outer_row.offset == outer_row.max_offset and outer_row.start == 0 and outer_row.end == outer_row.slot_count - 2 and outer_row.token_slot == 1 and board.column_clue_reads[column + 1].anchor == "middle" and middle_column.offset == 2 and middle_column.start > 0, "both axes restore direct outer and middle reads independently"):
			return
		if not require(session.player.redo() and session.player.undo_used and session.player.cells[45 * 100 + 56] == 0, "redo after real process restart"):
			return
		if not require(app.sessions[0].player.cells[10 * 20 + 10] == 1 and app.sessions[1].player.cells[10 * 40 + 10] == 3, "other two slots restored independently"):
			return
		app.select_puzzle(0)
		if not require(app.board.view.cell_size == 26.0 and app.board.eraser, "F-01 own zoom/tool survives fixture switch"):
			return
		app.select_puzzle(1)
		if not require(app.board.overview and app.board.hand and app.board.active_color == 3, "F-02 own overview/tool/color survives fixture switch"):
			return
		print("P1_ROUNDTRIP_READ_OK")
		quit(0)
