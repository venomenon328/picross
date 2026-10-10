extends "res://tests/rp3_probe.gd"
## All six pilots through the regular scene and mouse route; separate real processes.
var pilot_index: int = 3

func setup(viewport: Viewport) -> void:
	target = viewport
	app = load("res://main.tscn").instantiate()
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	target.add_child(app)
	await process_frame
	await process_frame
	check(app.sessions.size() == 9, "all nine fixed registrations load")
	# Retain RP3's registration/path guards when its duplicate F04 playthrough
	# is omitted. RP6 still uses the same real scene, single clicks and strokes.
	check(app.sessions[3].definition.id == "F-04", "regular neutral F-04 registration")
	check(Definition.load_fixture("../art/f04").is_empty() and Definition.load_fixture("unknown").is_empty(), "fixed definition paths reject unregistered IDs")
	check(app.store.path_for("../f04").is_empty(), "save paths reject traversal")
	for i: int in range(9):
		check(Definition.validate(app.sessions[i].definition).is_empty(), "valid definition %d" % i)
		var wrong: Dictionary = app.sessions[i].definition.duplicate(true)
		if i >= 3:
			wrong.reveal.image = "res://art/f01.svg"
			check(not Definition.validate(wrong).is_empty(), "wrong pilot asset rejected")
	if pilot_index == 3 and OS.get_environment("RP6_STAGE") == "partial":
		# Seed a valid unchanged F01 save so the later real restart exercises
		# loaded cell semantics as well as the permitted initial fresh state.
		check(app._save_current(), "isolated F04 seeds unchanged F01 save")
	await select_pilot()

func select_pilot() -> void:
	app.show_album()
	await process_frame
	app.album.ensure_control_visible(app.choices[pilot_index])
	await process_frame
	await process_frame
	var box: Rect2 = app.choices[pilot_index].get_global_rect()
	check(app.album.get_global_rect().encloses(box), "pilot album choice reachable")
	check(box.size.y >= 44 * app.ui_scale, "choice respects minimum hit height")
	click(box.get_center())
	await process_frame
	check(app.session == app.sessions[pilot_index] and (app.ending.visible if app.session.completed else app.work.visible), "regular album click selects pilot and saved completion scene")
	app.board.fit_all()

func partial() -> void:
	check(not app.session.completed and app.session.reveal().is_empty(), "fresh pilot hides reveal")
	check(not app.title.text.contains(app.session.definition.reveal.name), "fresh pilot title hides motif name")
	check(app.session.definition.solution[0][0] == 0, "deliberate wrong corner is background")
	click(cell_point(Vector2i.ZERO))
	check(app.mini.cells[0] == 1 and not app.session.completed, "own incorrect miniature retained")
	click(app.undo_button.get_global_rect().get_center())
	check(app.mini.cells[0] == -1, "mouse undo")
	click(app.redo_button.get_global_rect().get_center())
	check(app.mini.cells[0] == 1 and app.session.player.undo_used, "mouse redo")
	check(app._flush_current(), "partial flush")
	app.show_album()
	check(app.album_previews[pilot_index].cells[0] == 1 and app.album_reveals[pilot_index].payload.is_empty() and not app.choices[pilot_index].text.contains(app.session.definition.reveal.name), "album own wrong miniature and no spoiler/name")

func choose_color(color: int) -> void:
	click(app.palette_row.get_child(color - 1).get_global_rect().get_center())
	check(app.board.active_color == color and not app.board.eraser and not app.board.hand, "real palette selects fill color")

func finish() -> void:
	check(app.session.player.cells[0] == 1 and app.session.player.undo_used and not app.session.completed, "new process restores partial and history")
	click(cell_point(Vector2i.ZERO), MOUSE_BUTTON_RIGHT)
	check(app.session.player.cells[0] == 0, "real conversion removes incorrect fill")
	var matrix: Array = app.session.definition.solution
	var width: int = app.session.player.width
	var last: Vector2i = Vector2i(-1, -1)
	for y: int in range(matrix.size()):
		for x: int in range(width):
			if matrix[y][x] > 0:
				last = Vector2i(x,y)
	# Whole same-color horizontal runs are ordinary atomic mouse strokes. This
	# avoids a save per cell while preserving the actual product/save path.
	for selected_color: int in range(1,app.session.definition.palette.size()+1):
		choose_color(selected_color)
		for y: int in range(matrix.size()):
			var x: int = 0
			while x < width:
				var color: int = int(matrix[y][x])
				if color != selected_color or Vector2i(x,y) == last:
					x += 1
					continue
				var end: int = x
				while end + 1 < width and int(matrix[y][end+1]) == color and Vector2i(end+1,y) != last:
					end += 1
				event(cell_point(Vector2i(x,y)),true)
				var move: InputEventMouseMotion = InputEventMouseMotion.new()
				move.position = cell_point(Vector2i(end,y))
				move.global_position = move.position
				move.button_mask = MOUSE_BUTTON_MASK_LEFT
				target.push_input(move,true)
				event(cell_point(Vector2i(end,y)),false)
				x = end + 1
	check(not app.session.completed and app.session.reveal().is_empty(), "last missing cell still hides motif")
	choose_color(int(matrix[last.y][last.x]))
	event(cell_point(last),true)
	check(not app.session.completed and app.session.reveal().is_empty() and app.mini.cells[last.y * width + last.x] == matrix[last.y][last.x], "last-cell preview is own miniature input and never completes")
	event(cell_point(last),false)
	check(app.session.completed and app.session.is_solution() and app.ending.visible, "committed regular mouse path completes pilot")
	check(app.reveal_view.payload == app.session.definition.reveal and app.completion_title.text == app.session.definition.reveal.name, "exact completion asset and name")
	if pilot_index == 3:
		check(app.completion_title.text == "Fliegenpilz" and app.reveal_view.payload.image == "res://art/f04.svg", "retained F-04 name and SVG binding")
	check(app.session.player.cells.count(-1) > 0, "unknown background allowed")
	app.show_album()
	check(app.album_reveals[pilot_index].visible and app.album_reveals[pilot_index].payload.definition_id == app.session.definition.id, "earned pilot artwork bound to its album slot")
	if pilot_index == 3:
		check(app.sessions[0].player.cells.count(-1) == 400 and app.sessions[1].player.cells.count(-1) == 1600 and app.sessions[2].player.cells.count(-1) == 10000, "isolated F04 leaves old F01-F03 cells unknown")

func restored() -> void:
	check(app.session.completed and app.session.is_solution() and app.session.player.undo_used, "second restart restores completed pilot")
	check(app.store.load_slot(app.session.definition).status == "loaded", "separate fixed slot loaded")
	app.show_album()
	check(app.album_reveals[pilot_index].payload == app.session.definition.reveal and app.choices[pilot_index].text.contains(app.session.definition.reveal.name), "restored correct earned album asset and name")
	if pilot_index == 3:
		var first: Dictionary = app.store.load_slot(app.sessions[0].definition)
		var unknown: int = saved_unknown_count(first)
		print("RP6_F01_SAVE status=%s unknown=%d" % [first.status, unknown])
		check(first.status == "fresh" or first.status == "loaded" and unknown == 400, "isolated F04 preserves F01 cells after restart")

func saved_unknown_count(slot: Dictionary) -> int:
	if slot.status != "loaded":
		return -1
	# JSON numbers are floats; Array.count(-1) would compare their Variant types.
	# load_slot has already validated integer values and the complete save contract.
	var count: int = 0
	for value: Variant in slot.data.cells:
		if int(value) == -1:
			count += 1
	return count

func write_foreign_slot_control() -> void:
	# Only the harness's disposable profile copy uses this short control stage.
	check(pilot_index == 3 and app.sessions[0].player.cells.count(-1) == 400, "foreign control starts from unchanged F01")
	app.select_puzzle(0)
	app.board.fit_all()
	check(app._save_current(), "foreign control can create an unchanged F01 save")
	var first: Dictionary = app.store.load_slot(app.sessions[0].definition)
	check(saved_unknown_count(first) == 400, "valid unchanged persisted F01 cells are accepted")
	click(cell_point(Vector2i.ZERO))
	check(app.session == app.sessions[0] and app.session.player.cells.count(-1) == 399, "real F01 cell action seeds foreign-slot control")
	check(app._flush_current(), "foreign-slot control write succeeds")
	first = app.store.load_slot(app.sessions[0].definition)
	check(saved_unknown_count(first) == 399, "foreign-slot control is a valid persisted save")

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if isolated.is_empty():
		quit(4)
		return
	SaveStore.test_root_override = isolated
	pilot_index = int(OS.get_environment("RP6_INDEX"))
	root.size = Vector2i(1920,1080)
	await setup(root)
	var others: Array = []
	for i: int in range(9):
		others.append(app.sessions[i].player.cells.duplicate())
	var stage: String = OS.get_environment("RP6_STAGE")
	if stage == "partial":
		partial()
	elif stage == "finish":
		finish()
	elif stage == "read":
		restored()
	elif stage == "foreign_write":
		write_foreign_slot_control()
	else:
		check(false,"unknown stage")
	for i: int in range(9):
		if i != pilot_index and not (stage == "foreign_write" and i == 0):
			check(app.sessions[i].player.cells == others[i], "other slot unchanged %d" % i)
	check(app._flush_current(), "final mandatory flush")
	print("RP6_RESULT index=%d stage=%s checks=%d failures=%d" % [pilot_index,stage,checks,failures])
	if failures == 0:
		print("RP6_" + stage.to_upper() + "_OK")
	quit(0 if failures == 0 else 4)
