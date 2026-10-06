extends RefCounted
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const H1 = preload("res://tests/h1_cases.gd")
const SaveStore = preload("res://model/save_store.gd")

static func run(t: SceneTree) -> void:
	# Explicit six-row owner contract, exercised through actual viewport events.
	var cases: Array = [
		[-1, MOUSE_BUTTON_LEFT, [4, 0, 2, 4, 3, 0, -1]],
		[-1, MOUSE_BUTTON_RIGHT, [0, 0, 2, 0, 3, 0, -1]],
		[0, MOUSE_BUTTON_LEFT, [4, 4, 2, 4, 3, 0, -1]],
		[0, MOUSE_BUTTON_RIGHT, [-1, -1, 2, -1, 3, 0, -1]],
		[2, MOUSE_BUTTON_LEFT, [-1, 0, -1, -1, 3, 0, -1]],
		[2, MOUSE_BUTTON_RIGHT, [0, 0, 0, 0, 3, 0, -1]]]
	for horizontal: bool in [true, false]:
		for spec: Array in cases:
			var b: Board = Board.new()
			b.size = Vector2(1100, 700)
			b.session = Session.new(Definition.load_fixture("f02"))
			t.root.add_child(b)
			await t.process_frame
			b.view.center = Vector2(8, 8)
			b.view.reframe()
			var origin: Vector2i = Vector2i(3, 3)
			var direction: Vector2i = Vector2i(1, 0) if horizontal else Vector2i(0, 1)
			var source: Array[int] = [int(spec[0]), 0, 2, -1, 3, 0, -1]
			for i: int in range(source.size()):
				var cell: Vector2i = origin + direction * i
				b.session.player.cells[cell.y * 40 + cell.x] = source[i]
			var before: Array[int] = b.session.player.cells.duplicate()
			b.active_color = 4
			H1.send(t, b, origin, spec[1], true)
			H1.move(t, b, origin + direction * 6) # jump includes protected cells
			t.check(b.gesture_length() == 7, "GP48 geometric count includes protections")
			b.active_color = 1
			b.eraser = true # UI changes cannot alter the already frozen gesture
			H1.move(t, b, origin + direction * 3)
			var visible: Array[int] = b.session.visible_cells()
			for i: int in range(source.size()):
				var cell: Vector2i = origin + direction * i
				t.check(visible[cell.y * 40 + cell.x] == spec[2][i], "GP48 six cases retract with original category and color")
			t.check(b.session.player.cells == before and b.session.player.history.is_empty(), "GP48 preview stays atomic")
			var other: Vector2i = Vector2i(0, 1) if horizontal else Vector2i(1, 0)
			H1.move(t, b, origin + other * 2)
			t.check(b.session.gesture.axis != 0, "GP48 projected origin keeps original axis")
			H1.move(t, b, origin)
			t.check(b.session.gesture.axis == 0 and b.gesture_length() == 1, "GP48 true origin releases axis only")
			H1.move(t, b, origin + other * 2)
			t.check(b.session.gesture.initial == spec[0] and b.session.gesture.source == before, "GP48 axis change keeps start snapshot")
			H1.move(t, b, origin)
			H1.move(t, b, origin + direction * 3)
			H1.send(t, b, origin + direction * 3, spec[1], false)
			var after: Array[int] = b.session.player.cells.duplicate()
			t.check(after == visible and b.session.player.history.size() == 1, "GP48 commit equals retracted preview")
			b.session.undo()
			t.check(b.session.player.cells == before, "GP48 atomic undo restores all protected colors")
			b.session.redo()
			t.check(b.session.player.cells == after, "GP48 atomic redo restores six-case result")
			b.queue_free()
			await t.process_frame
	await status_events(t)
	legacy_replay(t)

static func legacy_replay(t: SceneTree) -> void:
	var s: Session = Session.new(Definition.load_fixture("f02"))
	s.player.commit([{"index": 1, "before": -1, "after": 0}])
	# Pre-GP gesture: started on unknown and converted the adjacent X as well.
	s.player.commit([{"index": 0, "before": -1, "after": 4}, {"index": 1, "before": 0, "after": 4}])
	var saved: Dictionary = SaveStore.snapshot(s, s.view_state)
	t.check(SaveStore.validate(saved, s.definition).is_empty(), "GP48 legacy conversion action remains schema-valid")
	var restored: Session = Session.new(s.definition)
	SaveStore.apply(saved, restored)
	t.check(restored.player.cells == s.player.cells and restored.player.history == s.player.history, "GP48 legacy action restore preserves exact history")
	restored.undo()
	t.check(restored.player.cells[0] == -1 and restored.player.cells[1] == 0, "GP48 legacy action undo restores protected original X")
	restored.redo()
	t.check(restored.player.cells == s.player.cells, "GP48 legacy action redo replays original conversion, not new gesture rules")

static func status_events(t: SceneTree) -> void:
	var data: Dictionary = Definition.load_f01()
	data.rows[3] = H1.clues([3])
	data.columns[3] = H1.clues([3])
	var b: Board = Board.new()
	b.size = Vector2(1100, 700)
	b.session = Session.new(data)
	t.root.add_child(b)
	await t.process_frame
	b.view.center = Vector2(10, 10)
	b.view.reframe()
	H1.send(t, b, Vector2i(3, 3), MOUSE_BUTTON_LEFT, true)
	H1.move(t, b, Vector2i(5, 3))
	t.check(b.completion_states("row", 3) == [1], "GP48 filled preview is weakened, no strike")
	H1.move(t, b, Vector2i(4, 3))
	t.check(b.completion_states("row", 3) == [0], "GP48 retract clears filled state")
	H1.move(t, b, Vector2i(3, 3))
	H1.move(t, b, Vector2i(3, 5))
	t.check(b.completion_states("row", 3) == [0] and b.completion_states("column", 3) == [1], "GP48 axis switch invalidates both states")
	b.cancel_gesture()
	t.check(b.completion_states("column", 3) == [0], "GP48 abort clears preview state")
	H1.stroke(t, b, Vector2i(3, 3), Vector2i(5, 3))
	var view_before: Dictionary = b.capture_view()
	H1.stroke(t, b, Vector2i(2, 3), Vector2i(2, 3), MOUSE_BUTTON_RIGHT)
	t.check(b.completion_states("row", 3) == [1], "GP48 one adjacent X stays weakened")
	H1.send(t, b, Vector2i(6, 3), MOUSE_BUTTON_RIGHT, true)
	t.check(b.completion_states("row", 3) == [2], "GP48 second X preview closes block")
	b.cancel_gesture()
	t.check(b.completion_states("row", 3) == [1], "GP48 X abort restores weakened state")
	H1.stroke(t, b, Vector2i(6, 3), Vector2i(6, 3), MOUSE_BUTTON_RIGHT)
	t.check(b.completion_states("row", 3) == [2], "GP48 second X commit closes block")
	b.session.undo()
	t.check(b.completion_states("row", 3) == [1], "GP48 undo closed to filled")
	b.session.redo()
	t.check(b.completion_states("row", 3) == [2], "GP48 redo filled to closed")
	b.mark_completed_clues = false
	t.check(b.tooltip_entries("row", 3)[0].status == 0, "GP48 switch hides entire status display")
	b.mark_completed_clues = true
	t.check(b.tooltip_entries("row", 3)[0].status == 2 and b.capture_view() == view_before, "GP48 tooltip preserves original index and geometry")
	# A viewport edge next to a filled block is not the actual line boundary.
	b.session.player.cells[3 * 20 + 2] = -1
	b.session.player.cells[3 * 20 + 6] = -1
	b.view.viewport = Rect2(b.view.cell_rect(Vector2i(3, 3)).position, Vector2(72, 96))
	t.check(b.completion_states("row", 3) == [1], "GP48 artificial viewport edges cannot close full line")
	b.queue_free()
	await t.process_frame
