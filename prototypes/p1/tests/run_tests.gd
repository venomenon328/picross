extends SceneTree
const Definition = preload("res://model/definition.gd")
const Player = preload("res://model/player.gd")
const Gesture = preload("res://model/gesture.gd")
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
var checked: int = 0
var failures: int = 0
var fixture: Dictionary

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, description: String) -> void:
	checked += 1
	if not condition:
		failures += 1
		print("FAIL: ", description)

func run() -> void:
	var temporary: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if temporary.is_empty():
		temporary = OS.get_environment("TEMP") if OS.has_feature("windows") else OS.get_environment("TMPDIR")
	if temporary.is_empty():
		temporary = "/tmp"
	SaveStore.test_root_override = temporary.path_join("picross-p1-tests-%d" % Time.get_ticks_usec())
	root.size = Vector2i(1280, 720)
	fixture = Definition.load_f01()
	test_definition()
	test_gesture()
	test_history()
	test_completion()
	test_geometry()
	await test_scene()
	await test_event_routing()
	await preload("res://tests/p12_cases.gd").run(self)
	await preload("res://tests/p13_cases.gd").run(self)
	if OS.get_cmdline_user_args().has("--force-failure"):
		check(false, "P1_EXPECTED_FAILURE")
	print("P1_TEST_RESULT checks=%d failures=%d" % [checked, failures])
	if failures == 0:
		print("P1_TESTS_OK")
	quit(0 if failures == 0 else 23)

func test_definition() -> void:
	check(Definition.validate(fixture).is_empty(), "F-01 validates")
	check(Definition.hints([0, 0, 0]).is_empty(), "empty line")
	check(Definition.hints([1, 1, 1]) == [{"length": 3, "color": 1}], "full line")
	check(Definition.hints([1, 0, 1]) == [{"length": 1, "color": 1}, {"length": 1, "color": 1}], "same colors separated")
	check(Definition.hints([1, 2, 2, 1]) == [{"length": 1, "color": 1}, {"length": 2, "color": 2}, {"length": 1, "color": 1}], "different colors directly adjacent")
	var long_line: Array = []
	for i: int in range(100):
		long_line.append(1 if i % 2 == 0 else 2)
	check(Definition.hints(long_line).size() == 100, "long clues not truncated")
	for key: String in ["schema", "id", "revision", "width", "height", "palette", "solution", "rows", "columns", "reveal"]:
		var bad: Dictionary = fixture.duplicate(true)
		bad.erase(key)
		check(not Definition.validate(bad).is_empty(), "missing " + key)
	for bad_value: Variant in [-1, 2, 0.5, "1", null, true]:
		var bad: Dictionary = fixture.duplicate(true)
		bad.solution[0][0] = bad_value
		check(not Definition.validate(bad).is_empty(), "invalid solution value " + str(bad_value))
	for bad_value: Variant in [0, 101, 20.5, "20"]:
		var bad: Dictionary = fixture.duplicate(true)
		bad.width = bad_value
		check(not Definition.validate(bad).is_empty(), "invalid width " + str(bad_value))
	var broken: Dictionary = fixture.duplicate(true)
	broken.rows[1][0].length += 1
	check(not Definition.validate(broken).is_empty(), "stored clue mismatch")
	broken = fixture.duplicate(true)
	broken.solution[0].pop_back()
	check(not Definition.validate(broken).is_empty(), "ragged matrix")
	broken = fixture.duplicate(true)
	broken.reveal.image = "res://art/missing.svg"
	check(not Definition.validate(broken).is_empty(), "missing reveal resource")
	broken = fixture.duplicate(true)
	broken.palette.append(broken.palette[0].duplicate())
	check(not Definition.validate(broken).is_empty(), "duplicate color IDs")
	# A fully valid tiny colored definition exercises the validator, not F-02 UX.
	var colored: Dictionary = {"schema": 2, "id": "test", "revision": 1, "width": 4, "height": 1,
		"palette": [{"id": 1, "color": "#123456", "symbol": "A"}, {"id": 2, "color": "#abcdef", "symbol": "B"}],
		"solution": [[1, 2, 0, 2]], "rows": [[{"length": 1, "color": 1}, {"length": 1, "color": 2}, {"length": 1, "color": 2}]],
		"columns": [[{"length": 1, "color": 1}], [{"length": 1, "color": 2}], [], [{"length": 1, "color": 2}]],
		"reveal": {"version": 1, "definition_id": "test", "name": "test", "image": "res://art/f01.svg"}}
	check(Definition.validate(colored).is_empty(), "valid color boundary definition")
	colored.rows[0] = [{"length": 1, "color": 1}, {"length": 2, "color": 2}]
	check(not Definition.validate(colored).is_empty(), "same-color separated clues cannot merge")

func test_gesture() -> void:
	var p: Player = Player.new(20, 20)
	var g: Gesture = Gesture.new()
	check(g.begin(p, Vector2i(4, 3), 1), "start column 5")
	g.move(Vector2i(11, 3))
	check(g.changes().size() == 8, "jump has all intermediate cells")
	g.move(Vector2i(8, 7))
	check(g.endpoint == Vector2i(8, 3), "axis remains horizontal")
	check(g.changes().size() == 5, "5 to 12 to 9 elastic preview")
	check(p.cells.count(1) == 0 and p.history.is_empty(), "preview never writes state/history")
	check(g.finish(p) and p.cells.count(1) == 5, "elastic atomic commit")
	check(p.cells[3 * 20 + 9] == -1 and p.history.size() == 1, "no trailing cells")
	g.begin(p, Vector2i(2, 2), 0)
	g.move(Vector2i(5, 5))
	check(g.axis == Gesture.Axis.UNLOCKED and g.changes().size() == 1, "diagonal tie stays start only")
	g.move(Vector2i(4, 7))
	check(g.axis == Gesture.Axis.VERTICAL and g.endpoint == Vector2i(2, 7), "vertical dominant move locks")
	g.move(Vector2i(19, 0))
	check(g.endpoint == Vector2i(2, 0) and g.changes().size() == 3, "cross start stays same axis")
	g.move(Vector2i(20, 0))
	check(g.endpoint == Vector2i(2, 0), "outside freezes last valid endpoint")
	g.cancel()
	check(g.changes().is_empty() and p.cells.count(0) == 0, "cancel removes preview")
	check(not g.begin(p, Vector2i(-1, 0), 1), "cannot start outside")
	p.cells[0] = 0
	p.cells[1] = 1
	p.cells[2] = 2
	g.begin(p, Vector2i(0, 0), 1)
	g.move(Vector2i(4, 0))
	g.finish(p)
	check(p.cells.slice(0, 5) == [1, 1, 2, 1, 1], "left set converts X and protects existing fills")
	g.begin(p, Vector2i(1, 0), 0)
	g.move(Vector2i(5, 0))
	g.finish(p)
	check(p.cells.slice(0, 6) == [1, 0, 0, 0, 0, 0], "right set converts fills directly to X")
	g.begin(p, Vector2i(0, 0), -1)
	g.move(Vector2i(5, 0))
	check(g.changes().size() == 6, "eraser targets all existing types")
	g.finish(p)
	check(p.cells.slice(0, 6) == [-1, -1, -1, -1, -1, -1], "eraser resets to unknown")
	p.undo()
	check(p.cells.slice(0, 6) == [1, 0, 0, 0, 0, 0], "eraser undo restores mixed exact values")
	var before: Array[int] = p.cells.duplicate()
	g.begin(p, Vector2i(19, 19), 1)
	g.move(Vector2i(0, 19))
	check(g.changes().size() == 20, "both edges included")
	g.cancel()
	check(p.cells == before, "focus/escape cancellation data invariant")

func test_history() -> void:
	var p: Player = Player.new(20, 20)
	var g: Gesture = Gesture.new()
	check(not p.undo() and not p.undo_used, "empty undo is not used")
	g.begin(p, Vector2i(0, 0), 1)
	g.move(Vector2i(19, 0))
	g.finish(p)
	var filled: Array[int] = p.cells.duplicate()
	check(p.history.size() == 1, "whole stroke one history step")
	check(p.undo() and p.cells.count(-1) == 400 and p.undo_used, "undo entire stroke")
	check(p.redo() and p.cells == filled and p.undo_used, "redo exact state; metadata sticky")
	g.begin(p, Vector2i(0, 1), -1)
	g.move(Vector2i(19, 1))
	check(not g.finish(p) and p.history.size() == 1, "protected no-op no history")
	p.undo()
	g.begin(p, Vector2i(0, 1), -1)
	check(not g.finish(p) and p.history.size() == 1 and p.cursor == 0, "no-op preserves redo branch")
	g.begin(p, Vector2i(2, 1), 0)
	g.finish(p)
	check(p.history.size() == 1 and not p.redo() and p.undo_used, "effective branch drops redo")
	var before: Array[int] = p.cells.duplicate()
	check(not p.commit([{"index": 0, "before": -1, "after": 1}, {"index": 22, "before": -1, "after": 1}]) and p.cells == before, "stale action cannot partly commit")

func test_completion() -> void:
	var s: Session = Session.new(fixture)
	check(not s.is_solution() and s.reveal().is_empty(), "empty state no completion or reveal")
	check(s.album_title() == "Blatt 01 · 20 × 20", "neutral album name")
	for y: int in range(20):
		for x: int in range(20):
			if fixture.solution[y][x] > 0:
				s.player.cells[y * 20 + x] = 1
	check(s.is_solution(), "solution with unknown background completes")
	s.player.cells[0] = 0
	check(s.is_solution(), "marked background also accepted")
	s.player.cells[0] = 1
	check(not s.is_solution(), "extra fill prevents completion")
	check(s.visible_cells()[0] == 1, "wrong extra fill stays in miniature")
	s.player.cells[0] = -1
	var motif: int = 30
	for value: int in [-1, 0, 2]:
		s.player.cells[motif] = value
		check(not s.is_solution(), "missing/empty/wrong color prevents completion: " + str(value))
		check(s.visible_cells()[motif] == value, "wrong miniature value is uncorrected")
	s.player.cells[motif] = -1
	s.gesture.begin(s.player, Vector2i(10, 1), 1)
	check(s.visible_cells()[motif] == 1 and not s.completed and s.reveal().is_empty(), "last-cell preview cannot reveal")
	s.finish()
	check(s.completed and s.album_title() == fixture.reveal.name, "committed last cell reveals name")
	check(s.reveal() == fixture.reveal, "reveal uses completion gated independent resource")
	s.undo()
	check(not s.completed and s.reveal().is_empty(), "undo recomputes completion")
	s.redo()
	check(s.completed, "redo recomputes completion")

func test_geometry() -> void:
	var v: GridView = GridView.new()
	for step: float in [16.0, 22.0, 40.0]:
		v.cell_size = step
		for cell: Vector2i in [Vector2i(0, 0), Vector2i(19, 19), Vector2i(7, 12)]:
			check(v.hit(v.cell_rect(cell).get_center()) == cell, "cell center hit at " + str(step))
		check(v.hit(v.origin - Vector2(0.01, 0)).x == -1, "left edge outside")
		check(v.hit(v.bounds().end).x == -1, "bottom right exclusive")
		check(v.hit(v.origin) == Vector2i.ZERO, "top left inclusive")

func test_scene() -> void:
	var app: Main = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	check(app.album.visible and not app.work.visible and app.reveal_view.payload.is_empty(), "scene starts in neutral album")
	app.open_puzzle()
	await process_frame
	var board: Control = app.board
	check(app.work.get_global_rect().end.y <= 697, "1280x720 work area leaves footer visible")
	check(app.board.view.visible_bounds().end.y <= app.board.size.y, "visible grid fits drawing area")
	var start: Vector2 = app.board.view.cell_rect(Vector2i(4, 3)).get_center()
	var far: Vector2 = app.board.view.cell_rect(Vector2i(11, 3)).get_center()
	var back: Vector2 = app.board.view.cell_rect(Vector2i(8, 3)).get_center()
	app.board.pointer_press(start, MOUSE_BUTTON_LEFT)
	app.board.eraser = true
	app.board.active_color = 2
	app.board.pointer_move(far, true)
	app.board.pointer_move(back, true)
	check(app.mini.cells.count(1) == 5 and app.session.player.cells.count(1) == 0, "real scene elastic miniature preview")
	app.board.pointer_move(far, false)
	app.board.pointer_release(Vector2(-10, -10), false)
	check(app.session.player.cells.count(1) == 5, "tool/color frozen; UI/outside release commits last endpoint")
	app.board.pointer_press(start, MOUSE_BUTTON_RIGHT)
	check(app.session.gesture.target == 0, "right button empty even with eraser")
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	board._input(escape)
	check(not app.session.gesture.active, "Escape routed through scene")
	app.board.pointer_press(start, MOUSE_BUTTON_LEFT)
	app.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	check(not app.session.gesture.active, "actual focus-loss notification cancels")
	app.board.pointer_press(start, MOUSE_BUTTON_LEFT)
	app.show_album()
	check(not app.session.gesture.active and app.session.player.cells.count(1) == 5, "album cancels preview, keeps confirmed state")
	app.open_puzzle()
	app.session.undo()
	app.refresh()
	check(app.mini.cells.count(-1) == 400, "UI undo updates miniature")
	# Complete by normal atomic gestures; no direct completed flag or view bypass.
	for y: int in range(20):
		for x: int in range(20):
			if fixture.solution[y][x] > 0:
				app.session.gesture.begin(app.session.player, Vector2i(x, y), 1)
				app.session.finish()
	app.refresh()
	await process_frame
	await process_frame
	check(app.ending.visible and not app.work.visible and app.completion_title.text == fixture.reveal.name, "real completion scene and name")
	check(app.ending.get_global_rect().end.y <= 697, "1280x720 completion leaves footer visible")
	check(not app.reveal_view.payload.is_empty(), "real completion artwork")
	app.show_album()
	check(app.open_button.text.contains(fixture.reveal.name), "completed album entry")
	check(app.album_picture.visible and not app.album_mini.visible and app.album_picture.payload == fixture.reveal, "completed album has colored earned image")
	app.queue_free()
	await process_frame


func mouse_motion(point: Vector2, held: bool, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = point
	event.global_position = point
	if held:
		event.button_mask = MOUSE_BUTTON_MASK_MIDDLE if button == MOUSE_BUTTON_MIDDLE else (MOUSE_BUTTON_MASK_RIGHT if button == MOUSE_BUTTON_RIGHT else MOUSE_BUTTON_MASK_LEFT)
	else:
		event.button_mask = 0
	root.push_input(event, true)

func mouse_button(point: Vector2, pressed: bool, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = point
	event.global_position = point
	event.button_index = button
	event.pressed = pressed
	if pressed:
		event.button_mask = MOUSE_BUTTON_MASK_MIDDLE if button == MOUSE_BUTTON_MIDDLE else (MOUSE_BUTTON_MASK_RIGHT if button == MOUSE_BUTTON_RIGHT else MOUSE_BUTTON_MASK_LEFT)
	else:
		event.button_mask = 0
	root.push_input(event, true)

func test_event_routing() -> void:
	var app: Main = load("res://main.tscn").instantiate()
	root.add_child(app)
	app.open_puzzle()
	await process_frame
	await process_frame
	var start: Vector2 = app.board.get_global_transform() * app.board.view.cell_rect(Vector2i(4, 3)).get_center()
	var far: Vector2 = app.board.get_global_transform() * app.board.view.cell_rect(Vector2i(11, 3)).get_center()
	var back: Vector2 = app.board.get_global_transform() * app.board.view.cell_rect(Vector2i(8, 3)).get_center()
	mouse_motion(start, false)
	mouse_button(start, true)
	check(app.session.gesture.active, "viewport dispatch starts gesture via GUI hit test")
	mouse_motion(far, true)
	mouse_motion(back, true)
	check(app.session.gesture.changes().size() == 5, "viewport dispatch elastic motion")
	mouse_button(back, false)
	check(app.session.player.cells.count(1) == 5 and not app.session.gesture.active, "viewport dispatch releases atomically")
	# A wrong-button release must not complete an existing left gesture.
	mouse_motion(start, false)
	mouse_button(start, true)
	mouse_button(start, false, MOUSE_BUTTON_RIGHT)
	check(app.session.gesture.active, "unrelated mouse-button release ignored")
	var key: InputEventKey = InputEventKey.new()
	key.keycode = KEY_ESCAPE
	key.pressed = true
	root.push_input(key, true)
	check(not app.session.gesture.active and app.session.player.history.size() == 1, "viewport Escape cancels without history")
	# A toolbar button click changes history only through the button, never grid hit tests.
	var undo_point: Vector2 = app.undo_button.get_global_rect().get_center()
	mouse_motion(undo_point, false)
	mouse_button(undo_point, true)
	mouse_button(undo_point, false)
	check(app.session.player.cells.count(-1) == 400 and not app.session.gesture.active, "real undo button dispatch without painting beneath UI")
	app.queue_free()
	await process_frame
