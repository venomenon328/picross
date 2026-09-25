extends RefCounted
const Completion = preload("res://model/clue_completion.gd")
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")

static func cells(text: String) -> Array[int]:
	var result: Array[int] = []
	for c: String in text:
		result.append({"?": -1, "X": 0, "#": 1, "A": 1, "B": 2}[c])
	return result

static func clues(lengths: Array, colors: Array = []) -> Array:
	var result: Array = []
	for i: int in range(lengths.size()):
		result.append({"length": lengths[i], "color": 1 if colors.is_empty() else colors[i]})
	return result

## Independent test oracle: enumerate cell assignments, scan maximal colored
## runs, then compare their intervals. No production DP/Definition.hints calls.
static func oracle(input: Array[int], hints: Array, colors: int) -> Array[bool]:
	var starts: Array = []
	var matches: int = 0
	for code: int in range(int(pow(colors + 1, input.size()))):
		var value: int = code
		var candidate: Array[int] = []
		var compatible: bool = true
		for p: int in range(input.size()):
			var color: int = value % (colors + 1)
			value = value / (colors + 1)
			candidate.append(color)
			if input[p] != -1 and input[p] != color:
				compatible = false
		if not compatible:
			continue
		var runs: Array = []
		var positions: Array = []
		for p: int in range(candidate.size()):
			if candidate[p] == 0:
				continue
			if p > 0 and candidate[p - 1] == candidate[p]:
				runs[-1].length += 1
			else:
				runs.append({"length": 1, "color": candidate[p]})
				positions.append(p)
		if runs != hints:
			continue
		if matches == 0:
			starts = positions.duplicate()
		else:
			for i: int in range(starts.size()):
				if starts[i] != positions[i]:
					starts[i] = -1
		matches += 1
	var flags: Array[bool] = []
	for i: int in range(hints.size()):
		var done: bool = matches > 0 and starts[i] >= 0
		if done:
			for p: int in range(starts[i], starts[i] + int(hints[i].length)):
				done = done and input[p] == int(hints[i].color)
		flags.append(done)
	return flags

static func run(t: SceneTree) -> void:
	var vectors: Array = [
		[[10], "??##########???", [true]],
		[[3, 3], "???????###???????", [false, false]],
		[[3, 5], "???????###???????", [false, false]],
		[[3, 5], "??????X###X??????", [true, false]],
		[[3, 5], "??????X###X????", [false, false]],
		[[3, 3], "???????", [false, false]],
		[[3, 3], "###?###", [true, true]],
		[[3, 3], "###???????", [true, false]],
		[[3, 3], "???????###", [false, true]],
		[[3, 3], "AAABBB", [true, true], [1, 2]],
		[[3, 3], "AAAAAA", [false, false]],
		[[3, 3], "??????X###X??????", [false, false]],
		[[3], "##???", [false]], [[3], "####?", [false]],
		[[3], "BBB??", [false]], [[3], "###?#", [false]],
		[[3], "#?#??", [false]], [[3], "###??", [true]],
		[[], "?XX??", []], [[], "#????", []]]
	for v: Array in vectors:
		var input: Array[int] = cells(v[1])
		var hints: Array = clues(v[0], v[3] if v.size() == 4 else [])
		var before: Array = [input.duplicate(), hints.duplicate(true)]
		t.check(Completion.analyze(input, hints) == v[2], "H1 vector " + str(v))
		t.check(input == before[0] and hints == before[1], "H1 pure inputs")
		input.reverse()
		hints.reverse()
		var expected: Array = v[2].duplicate()
		expected.reverse()
		t.check(Completion.analyze(input, hints) == expected, "H1 mirrored vector")
	# Fixed seed, small exhaustive candidate spaces; also contradictory inputs.
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = 1901
	for trial: int in range(400):
		var n: int = 1 + trial % 6
		var colors: int = 1 + trial % 2
		var input: Array[int] = []
		for p: int in range(n):
			input.append(rng.randi_range(-1, colors))
		var hints: Array = []
		for i: int in range(rng.randi_range(0, 3)):
			hints.append({"length": rng.randi_range(1, 3), "color": rng.randi_range(1, colors)})
		var expected: Array[bool] = oracle(input, hints, colors)
		t.check(Completion.analyze(input, hints) == expected, "H1 independent cell oracle trial %d" % trial)
		input.reverse()
		hints.reverse()
		expected.reverse()
		t.check(Completion.analyze(input, hints) == expected, "H1 oracle mirrored trial %d" % trial)
	var timings: Array[int] = []
	for kind: int in range(4):
		var input: Array[int] = []
		input.resize(100)
		input.fill(-1)
		var hints: Array = []
		for i: int in range(30 if kind != 2 else 100):
			hints.append({"length": 1, "color": 1 + i % 2 if kind == 2 else 1})
		if kind == 0:
			hints.clear()
		if kind == 2:
			for p: int in range(100):
				input[p] = 1 + p % 2
		if kind == 3:
			input.fill(2)
		var start: int = Time.get_ticks_usec()
		for repeat: int in range(20):
			var flags: Array[bool] = Completion.analyze(input, hints)
			t.check(flags.size() == hints.size() and (not flags.has(false) if kind == 2 else not flags.has(true)), "H1 bounded 100-cell case %d" % kind)
		timings.append(Time.get_ticks_usec() - start)
	print("H1_LINE_TIMING_US twenty analyses each [empty, ambiguous, 100 colored, contradiction]=", timings)
	await scene_cases(t)

static func send(t: SceneTree, board: Board, cell: Vector2i, button: MouseButton, pressed: bool) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = board.global_position + board.view.cell_rect(cell).get_center()
	event.button_index = button
	event.pressed = pressed
	t.root.push_input(event, true)

static func move(t: SceneTree, board: Board, cell: Vector2i) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = board.global_position + board.view.cell_rect(cell).get_center()
	t.root.push_input(event, true)

static func stroke(t: SceneTree, board: Board, start: Vector2i, end: Vector2i, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	send(t, board, start, button, true)
	move(t, board, end)
	send(t, board, end, button, false)

static func scene_cases(t: SceneTree) -> void:
	# Isolated synthetic definition only for precise 3/5 versus 3/3 ambiguity.
	# It is not registered in the album or SaveStore's three-fixture whitelist.
	var data: Dictionary = Definition.load_f01()
	data.rows[0] = clues([3, 5])
	data.rows[1] = clues([3, 3])
	data.rows[2] = clues([3])
	data.columns[5] = clues([3])
	var board: Board = Board.new()
	board.size = Vector2(1100, 700)
	board.session = Session.new(data)
	t.root.add_child(board)
	await t.process_frame
	board.view.center = Vector2(10, 10)
	board.view.reframe()
	var s: Session = board.session
	stroke(t, board, Vector2i(8, 0), Vector2i(10, 0))
	t.check(board.completion_flags("row", 0) == [false, false], "H1 3 may be part of 5 through viewport")
	stroke(t, board, Vector2i(7, 0), Vector2i(7, 0), MOUSE_BUTTON_RIGHT)
	stroke(t, board, Vector2i(11, 0), Vector2i(11, 0), MOUSE_BUTTON_RIGHT)
	t.check(board.completion_flags("row", 0) == [true, false], "H1 bounding X makes 3 unique")
	var history: Array = s.player.history.duplicate(true)
	var view_before: Dictionary = board.capture_view()
	var cursor: int = s.player.cursor
	var searches: int = board.completion_searches
	for i: int in range(5):
		board.queue_redraw()
		await t.process_frame
		board.completion_flags("row", 0)
	t.check(board.completion_searches == searches and board.completion_cache.size() == 40, "H1 redraw reuses bounded cache")
	board.zoom(-1, board.view.viewport.get_center())
	board.completion_flags("row", 0)
	t.check(board.completion_searches == searches, "H1 zoom no search")
	board.working_size()
	board.navigate_to(Vector2(0.6, 0.6))
	board.ui_scale = 1.25
	board.size = Vector2(1000, 650)
	board._layout()
	board.set_clue_hover("row", 0)
	board.tooltip_entries("row", 0)
	t.check(board.completion_searches == searches, "H1 pan resize UI-scale hover do not search")
	board.ui_scale = 1.0
	board.size = Vector2(1100, 700)
	board.restore_view(view_before)
	stroke(t, board, Vector2i(12, 0), Vector2i(19, 0), MOUSE_BUTTON_RIGHT)
	t.check(board.completion_flags("row", 0) == [false, false], "H1 contradiction removes every flag")
	s.undo()
	t.check(board.completion_flags("row", 0) == [true, false], "H1 undo restores marker")
	s.redo()
	t.check(board.completion_flags("row", 0) == [false, false], "H1 redo removes marker")
	s.undo()
	# Preview removal and retraction restore exactly the previously visible flag.
	send(t, board, Vector2i(8, 0), MOUSE_BUTTON_LEFT, true)
	move(t, board, Vector2i(10, 0))
	t.check(board.completion_flags("row", 0) == [false, false], "H1 removal preview unmarks")
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	t.root.push_input(escape)
	t.check(board.completion_flags("row", 0) == [true, false], "H1 escape restores current visible line")
	t.check(s.player.history.size() == history.size() + 1 and s.player.cursor == cursor and s.player.undo_used, "H1 analysis and preview add no history")
	stroke(t, board, Vector2i(8, 1), Vector2i(10, 1))
	stroke(t, board, Vector2i(7, 1), Vector2i(7, 1), MOUSE_BUTTON_RIGHT)
	stroke(t, board, Vector2i(11, 1), Vector2i(11, 1), MOUSE_BUTTON_RIGHT)
	t.check(board.completion_flags("row", 1) == [false, false], "H1 bounded identical clues remain ambiguous")
	send(t, board, Vector2i(0, 2), MOUSE_BUTTON_LEFT, true)
	move(t, board, Vector2i(2, 2))
	t.check(board.completion_flags("row", 2) == [true], "H1 filled preview marks without confirmation")
	move(t, board, Vector2i(1, 2))
	t.check(board.completion_flags("row", 2) == [false], "H1 shortening removes abandoned preview marker")
	move(t, board, Vector2i(2, 2))
	board._notification(Control.NOTIFICATION_APPLICATION_FOCUS_OUT)
	t.check(board.completion_flags("row", 2) == [false] and s.player.cells[40] == -1, "H1 focus cancellation discards preview")
	stroke(t, board, Vector2i(0, 2), Vector2i(2, 2))
	t.check(board.completion_flags("row", 2) == [true], "H1 commit marks")
	board.eraser = true
	stroke(t, board, Vector2i(1, 2), Vector2i(1, 2))
	t.check(board.completion_flags("row", 2) == [false], "H1 eraser unmarks incomplete interval")
	board.eraser = false
	stroke(t, board, Vector2i(1, 2), Vector2i(1, 2))
	t.check(board.completion_flags("row", 2) == [true], "H1 refill remarks")
	send(t, board, Vector2i(5, 5), MOUSE_BUTTON_LEFT, true)
	move(t, board, Vector2i(5, 7))
	t.check(board.completion_flags("column", 5) == [true], "H1 column preview marks all current cells")
	move(t, board, Vector2i(5, 8))
	t.check(board.completion_flags("column", 5) == [false], "H1 column overextension contradicts")
	move(t, board, Vector2i(5, 7))
	t.check(board.completion_flags("column", 5) == [true], "H1 retracting column restores marker")
	board.cancel_gesture()
	t.check(board.completion_flags("column", 5) == [false] and board.completion_cache["row/8"].cells == s.player.cells.slice(160, 180), "H1 cancelled and abandoned preview rows are invalidated")
	# Same inputs, entirely different hidden content/crossing constraints.
	var alternative: Dictionary = data.duplicate(true)
	alternative.solution = []
	alternative.reveal = {}
	for x: int in range(20):
		alternative.columns[x] = clues([20])
	board.session = Session.new(alternative)
	board.session.player.cells = s.player.cells.duplicate()
	board.session.completed = true
	t.check(board.completion_flags("row", 0) == [true, false] and board.completion_flags("row", 2) == [true], "H1 independent of solution reveal completion and crossing clues")
	t.check(board.completion_cache.size() == 40 and board.capture_view() == view_before, "H1 session switch replaces cache without moving reads")
	board.queue_free()
	await t.process_frame
	await app_cases(t)

static func app_cases(t: SceneTree) -> void:
	SaveStore.test_root_override = SaveStore.test_root_override.path_join("h1")
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	await t.process_frame
	app.open_puzzle()
	await t.process_frame
	t.check(app.mark_completed_clues and app.board.mark_completed_clues and app.clue_completion_toggle.button_pressed, "H1 application default on")
	var before: Dictionary = SaveStore.snapshot(app.session, app.board.capture_view())
	# Actual checkbox through viewport; it must neither commit nor save.
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = app.clue_completion_toggle.get_global_rect().get_center()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = true
	t.root.push_input(event, true)
	event = event.duplicate()
	event.pressed = false
	t.root.push_input(event, true)
	t.check(not app.mark_completed_clues and not app.board.mark_completed_clues, "H1 real checkbox toggles")
	t.check(SaveStore.snapshot(app.session, app.board.capture_view()) == before and app.save_timer.is_stopped(), "H1 toggle does not mutate save or schedule write")
	app.select_puzzle(1)
	t.check(not app.mark_completed_clues, "H1 setting survives sheet change")
	app._reset_selected()
	t.check(not app.mark_completed_clues and not app.clue_completion_toggle.button_pressed, "H1 setting survives reset and album")
	app.set_clue_completion(true)
	t.check(app.board.mark_completed_clues, "H1 re-enable immediately uses current cells")
	app.select_puzzle(0)
	await t.process_frame
	# First F-01 row with a clue: fill its exact intervals through UI events.
	var y: int = 0
	while app.session.definition.rows[y].is_empty():
		y += 1
	app.board.fit_all()
	for x: int in range(20):
		if int(app.session.definition.solution[y][x]) > 0:
			stroke(t, app.board, Vector2i(x, y), Vector2i(x, y))
	var flags: Array[bool] = app.board.completion_flags("row", y)
	t.check(flags.has(true), "H1 actual fixture filled row marks")
	var saved: Dictionary = SaveStore.snapshot(app.session, app.board.capture_view())
	var path: String = app.store.path_for("f01")
	var disk_before: String = FileAccess.get_file_as_string(path)
	app.set_clue_completion(false)
	app.board.completion_flags("row", y)
	app.set_clue_completion(true)
	t.check(FileAccess.get_file_as_string(path) == disk_before and SaveStore.snapshot(app.session, app.board.capture_view()) == saved, "H1 evaluating and toggling preserve disk history undo and save values")
	# Restore into the same Session after different visible content.
	app.session.player.cells.fill(-1)
	t.check(not app.board.completion_flags("row", y).has(true), "H1 blank restore precursor unmarks")
	SaveStore.apply(saved, app.session)
	t.check(app.board.completion_flags("row", y) == flags, "H1 in-place restore derives fresh flags")
	# Preserve marked state as backup, then make a different primary.
	app._save_current()
	app._undo()
	var damaged: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	damaged.store_string("invalid isolated H1 primary")
	damaged.close()
	app.queue_free()
	await t.process_frame
	app = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	await t.process_frame
	app.open_puzzle()
	await t.process_frame
	t.check(app.slot_status[0] == "recovered" and app.board.completion_flags("row", y) == flags, "H1 actual recovery loads fresh derived markers")
	var recovery_before: String = FileAccess.get_file_as_string(path)
	app.set_clue_completion(false)
	app.set_clue_completion(true)
	t.check(app.slot_status[0] == "recovered" and FileAccess.get_file_as_string(path) == recovery_before, "H1 display cannot repair or overwrite recovery")
	app.queue_free()
	await t.process_frame
