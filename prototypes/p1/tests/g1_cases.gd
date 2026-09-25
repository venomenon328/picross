extends RefCounted
const Player = preload("res://model/player.gd")
const Gesture = preload("res://model/gesture.gd")
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")

static func preview(player: Player, gesture: Gesture) -> Array[int]:
	var visible: Array[int] = player.cells.duplicate()
	for change: Dictionary in gesture.changes():
		visible[change.index] = change.after
	return visible

static func model_cases(t: SceneTree) -> void:
	var start: Vector2i = Vector2i(4, 4)
	for first: Vector2i in [Vector2i(7, 4), Vector2i(1, 4), Vector2i(4, 7), Vector2i(4, 1)]:
		var second: Vector2i = Vector2i(4, 1) if first.y == 4 else Vector2i(1, 4)
		var p: Player = Player.new(9, 9)
		var g: Gesture = Gesture.new()
		g.begin(p, start, 1)
		g.move(first)
		var old_arm: Array[int] = preview(p, g)
		g.move(start)
		t.check(g.axis == Gesture.Axis.UNLOCKED and g.endpoint == start and g.changes().size() == 1, "G-03 actual origin unlocks and shrinks preview")
		g.move(start + Vector2i(2, 2))
		t.check(g.axis == Gesture.Axis.UNLOCKED and g.endpoint == start, "G-03 diagonal tie waits after return")
		g.move(second)
		var new_arm: Array[int] = preview(p, g)
		t.check(g.endpoint == second and g.axis == (Gesture.Axis.VERTICAL if first.y == 4 else Gesture.Axis.HORIZONTAL), "G-01 opposite axis chosen after return")
		for index: int in range(p.cells.size()):
			if old_arm[index] == 1 and new_arm[index] == -1:
				t.check(p.cells[index] == -1, "G-02 abandoned arm remains confirmed unknown")
		g.move(start)
		g.move(first)
		g.move(start)
		g.move(second)
		t.check(g.endpoint == second, "G-01 repeated changes in one gesture")
		var expected: Array[int] = preview(p, g)
		t.check(p.cells.count(1) == 0 and p.history.is_empty(), "G-04 preview has no commit")
		t.check(g.finish(p) and p.cells == expected and p.history.size() == 1, "G-04 one atomic final arm")
		t.check(p.undo() and p.cells.count(-1) == 81, "G-04 undo exact source")
		t.check(p.redo() and p.cells == expected, "G-04 redo exact final arm")
	# A projected endpoint at the origin is not an actual origin hit.
	var p: Player = Player.new(9, 9)
	var g: Gesture = Gesture.new()
	g.begin(p, start, 1)
	g.move(Vector2i(7, 4))
	g.move(Vector2i(4, 7))
	t.check(g.axis == Gesture.Axis.HORIZONTAL and g.endpoint == start, "G-03 projected origin keeps axis")
	g.move(Vector2i(4, 1))
	t.check(g.axis == Gesture.Axis.HORIZONTAL and g.endpoint == start, "G-03 one effective cell does not unlock")
	g.move(Vector2i(1, 4))
	t.check(g.axis == Gesture.Axis.HORIZONTAL and g.endpoint == Vector2i(1, 4), "G-03 jump across origin retains axis")
	g.move(start)
	g.move(Vector2i(4, 7))
	t.check(g.axis == Gesture.Axis.VERTICAL and g.endpoint == Vector2i(4, 7), "G-03 actual hit after jump unlocks")
	g.cancel()
	# All frozen modes operate on the source snapshot after changing direction.
	for target: int in [-1, 0, 1, 3]:
		for initial: int in [-1, 0, 2]:
			var q: Player = Player.new(9, 9)
			q.cells[4 * 9 + 4] = initial
			q.cells[4 * 9 + 5] = 0
			q.cells[4 * 9 + 6] = 2
			q.cells[5 * 9 + 4] = 0
			q.cells[6 * 9 + 4] = 2
			var source: Array[int] = q.cells.duplicate()
			var stroke: Gesture = Gesture.new()
			stroke.begin(q, start, target)
			var mode: Gesture.Mode = stroke.mode
			var frozen: int = stroke.target
			stroke.move(Vector2i(6, 4))
			stroke.move(start)
			stroke.move(Vector2i(4, 6))
			t.check(stroke.mode == mode and stroke.target == frozen and stroke.source == source, "G-02 frozen mode/color/source %d/%d" % [target, initial])
			var final_view: Array[int] = preview(q, stroke)
			t.check(final_view[4 * 9 + 5] == source[4 * 9 + 5] and final_view[4 * 9 + 6] == source[4 * 9 + 6], "G-02 mixed abandoned arm restored %d/%d" % [target, initial])
			var effective: bool = stroke.finish(q)
			t.check(q.cells == final_view and q.history.size() == int(effective), "G-02 final arm only %d/%d" % [target, initial])
			if effective:
				q.undo()
				t.check(q.cells == source, "G-04 mixed undo exact %d/%d" % [target, initial])
				q.redo()
				t.check(q.cells == final_view, "G-04 mixed redo exact %d/%d" % [target, initial])
	var branch: Player = Player.new(9, 9)
	var stroke: Gesture = Gesture.new()
	stroke.begin(branch, start, 1)
	stroke.move(Vector2i(7, 4))
	stroke.move(start)
	t.check(stroke.finish(branch) and branch.history.size() == 1, "G-04 release at origin commits one cell")
	branch.undo()
	stroke.begin(branch, start, -1)
	stroke.move(Vector2i(7, 4))
	stroke.move(start)
	t.check(not stroke.finish(branch) and branch.cursor == 0 and branch.history.size() == 1, "G-04 no-op preserves redo")
	stroke.begin(branch, Vector2i(3, 4), 0)
	stroke.finish(branch)
	t.check(branch.history.size() == 1 and not branch.redo(), "G-04 effective branch replaces redo")

static func point(board: Control, cell: Vector2i) -> Vector2:
	return board.get_global_transform() * board.view.cell_rect(cell).get_center()

static func gui_cases(t: SceneTree) -> void:
	SaveStore.test_root_override += "-g1-routes"
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	app.open_puzzle()
	await t.process_frame
	await t.process_frame
	var b: Control = app.board
	var start: Vector2i = Vector2i(4, 4)
	var old: Vector2i = Vector2i(7, 4)
	var finish: Vector2i = Vector2i(4, 7)
	t.mouse_motion(point(b, start), false)
	t.mouse_button(point(b, start), true)
	t.mouse_motion(point(b, old), true)
	t.mouse_motion(point(b, start), true)
	t.check(b.gesture_length() == 1 and app.mini.cells[4 * 20 + 7] == -1, "G-05 real route origin counter and miniature restore")
	t.mouse_motion(point(b, finish), true)
	t.check(b.gesture_length() == 4 and app.mini.cells[7 * 20 + 4] == 1 and app.mini.cells[4 * 20 + 7] == -1, "G-05 real route new axis counter and miniature")
	t.mouse_button(point(b, finish), false, MOUSE_BUTTON_RIGHT)
	t.check(app.session.gesture.active, "G-04 wrong button release ignored after switch")
	t.mouse_button(point(b, finish), false)
	t.check(app.session.player.history.size() == 1 and app.session.player.cells[7 * 20 + 4] == 1 and app.session.player.cells[4 * 20 + 7] == -1, "G-05 real route final arm committed")
	app.session.undo()
	t.check(app.session.player.cells.count(1) == 0, "G-04 real route undo")
	app.session.redo()
	t.check(app.session.player.cells[7 * 20 + 4] == 1, "G-04 real route redo")
	# Reverse direction through the same viewport route, then erase the first arm.
	t.mouse_motion(point(b, start), false)
	t.mouse_button(point(b, start), true, MOUSE_BUTTON_RIGHT)
	t.mouse_motion(point(b, finish), true, MOUSE_BUTTON_RIGHT)
	t.mouse_motion(point(b, start), true, MOUSE_BUTTON_RIGHT)
	t.mouse_motion(point(b, old), true, MOUSE_BUTTON_RIGHT)
	t.mouse_button(point(b, old), false, MOUSE_BUTTON_RIGHT)
	t.check(app.session.player.cells[4 * 20 + 7] == 0 and app.session.player.cells[7 * 20 + 4] == 1, "G-05 vertical to horizontal right stroke")
	app.set_tool("erase")
	t.mouse_motion(point(b, start), false)
	t.mouse_button(point(b, start), true)
	t.mouse_motion(point(b, old), true)
	t.mouse_motion(point(b, start), true)
	t.mouse_motion(point(b, finish), true)
	t.mouse_button(point(b, finish), false)
	t.check(app.session.player.cells[4 * 20 + 7] == 0 and app.session.player.cells[7 * 20 + 4] == -1, "G-05 eraser switches without old arm remnants")
	for button: MouseButton in [MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_LEFT]:
		if button == MOUSE_BUTTON_LEFT:
			app.set_tool("erase")
		t.mouse_motion(point(b, start), false)
		t.mouse_button(point(b, start), true, button)
		t.mouse_motion(point(b, old), true, button)
		t.mouse_motion(point(b, start), true, button)
		t.mouse_motion(point(b, finish), true, button)
		t.check(app.session.gesture.endpoint == finish, "G-05 right/eraser switches axis")
		var before: int = app.session.player.history.size()
		var escape: InputEventKey = InputEventKey.new()
		escape.keycode = KEY_ESCAPE
		escape.pressed = true
		t.root.push_input(escape, true)
		t.check(not app.session.gesture.active and app.session.player.history.size() == before, "G-04 Escape discards switched preview")
	app.set_tool("fill")
	app.select_puzzle(1)
	await t.process_frame
	b = app.board
	start = b.view.hit(b.view.viewport.get_center())
	old = start + Vector2i(2, 0)
	finish = start + Vector2i(0, 2)
	b.active_color = 3
	t.mouse_motion(point(b, start), false)
	t.mouse_button(point(b, start), true)
	t.mouse_motion(point(b, old), true)
	t.mouse_motion(point(b, start), true)
	t.mouse_motion(point(b, finish), true)
	t.check(app.session.gesture.target == 3 and app.mini.cells[finish.y * 40 + finish.x] == 3, "G-05 F-02 frozen color in miniature")
	app.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	t.check(not app.session.gesture.active, "G-04 focus loss discards changed axis")
	app.select_puzzle(2)
	await t.process_frame
	b = app.board
	b.view.zoom_to(12.0, b.view.viewport.get_center())
	start = b.view.hit(b.view.viewport.get_center())
	old = start + Vector2i(2, 0)
	finish = start + Vector2i(0, 2)
	t.mouse_motion(point(b, start), false)
	t.mouse_button(point(b, start), true)
	t.mouse_motion(point(b, old), true)
	t.mouse_motion(point(b, start), true)
	t.mouse_motion(point(b, finish), true)
	t.check(b.gesture_length() == 3 and app.mini.cells[finish.y * 100 + finish.x] == 1, "G-05 F-03 small zoom route")
	var held: Vector2i = app.session.gesture.endpoint
	t.mouse_motion(b.get_global_rect().position - Vector2(10, 10), true)
	t.check(app.session.gesture.endpoint == held, "G-05 outside board holds last endpoint")
	t.mouse_button(b.get_global_rect().position - Vector2(10, 10), false)
	t.check(app.session.player.cells[finish.y * 100 + finish.x] == 1, "G-05 outside release commits held endpoint")
	app.queue_free()
	await t.process_frame

static func run(t: SceneTree) -> void:
	model_cases(t)
	await gui_cases(t)
