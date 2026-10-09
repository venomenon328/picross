extends RefCounted
## N02/N03: actual viewport input, real save bytes, independently computed order.
var t: SceneTree
var app: Control
var clock: Array[int] = [1000000]

func run(test: SceneTree) -> void:
	t = test
	app = t.app
	app.board.animation_clock = func() -> int: return clock[0]
	for length: int in [1, 4, 16, 17, 100]:
		for axis: Vector2i in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
			for button: MouseButton in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
				reset(2)
				var first: Vector2i = Vector2i(2, 2)
				if axis.x != 0:
					first.x = 0 if axis.x > 0 else length - 1
				else:
					first.y = 0 if axis.y > 0 else length - 1
				var indices: Array[int] = []
				for i: int in range(length):
					var cell: Vector2i = first + axis * i
					indices.append(cell.y * 100 + cell.x)
				stroke(first, first + axis * (length - 1), button)
				wave(indices, 1 if button == MOUSE_BUTTON_LEFT else 0)
	protection_and_g1()
	lifecycle()
	chords()
	app.board.animation_clock = Time.get_ticks_usec
	t.fresh()

func reset(sheet: int = 0) -> void:
	clock[0] = 1000000
	t.buttons = 0
	app.board.cell_buttons_blocked = false
	app.select_puzzle(sheet)
	app._reset_selected()
	app.open_puzzle()
	app.board.hand = false
	app.board.eraser = false
	app.animation_toggle.button_pressed = true
	app.board.set_animations(true)
	app.board.fit_all()

func stroke(first: Vector2i, last: Vector2i, button: MouseButton) -> void:
	t.mouse(t.point(first.x, first.y), button, true)
	t.motion(t.point(last.x, last.y))
	t.mouse(t.point(last.x, last.y), button, false)

func saved() -> String:
	return FileAccess.get_file_as_string(app.store.path_for(str(app.session.definition.id).to_lower().replace("-", "")))

func logical() -> Array:
	return [app.session.player.cells.duplicate(), app.session.player.history.duplicate(true),
		app.session.player.cursor, app.session.completed, app.mini.cells.duplicate(), saved()]

func wave(indices: Array[int], target: int) -> void:
	var effects: Dictionary = app.board.effects
	t.check(effects.size() == indices.size(), "only effective cells animate")
	# Independent oracle: start at gesture origin, 12ms steps up to length 16;
	# longer lines place their final start exactly at 180ms.
	for i: int in range(indices.size()):
		var expected: int = i * 12000 if indices.size() <= 16 else roundi(180000.0 * i / (indices.size() - 1))
		t.check(effects.has(indices[i]), "effective cell has effect")
		if not effects.has(indices[i]):
			continue
		t.check(int(effects[indices[i]].start) == 1000000 + expected, "start follows gesture direction and effective ordinal")
		t.check(effects[indices[i]].after == target and is_equal_approx(effects[indices[i]].seconds, 0.21), "210ms target only")
		t.check(app.session.player.cells[indices[i]] == target and app.mini.cells[indices[i]] == target, "model and miniature already committed")
	var restored: Array[int] = []
	for value: Variant in app.store.load_slot(app.session.definition).data.cells:
		restored.append(int(value))
	t.check(restored == app.session.player.cells, "all cells saved before visual starts")
	t.check(not saved().is_empty(), "save-byte oracle reads a real slot")
	t.check(app.session.player.history.back().size() == indices.size(), "one atomic history entry contains every effective cell")
	var state: Array = logical()
	var last_start: int = int(effects[indices.back()].start)
	t.check(last_start <= 1180000, "maximum 180ms spread")
	clock[0] = last_start + 209000
	app.board._process(0)
	t.check(app.board.effects.has(indices.back()), "last cell still active at 209ms")
	clock[0] += 1000
	app.board._process(0)
	t.check(app.board.effects.is_empty() and not app.board.is_processing(), "last ends by 390ms and ticker stops")
	t.check(logical() == state, "elapsed effects never write model/history/mini/save/completion")

func protection_and_g1() -> void:
	reset()
	stroke(Vector2i.ZERO, Vector2i(16, 0), MOUSE_BUTTON_LEFT)
	clock[0] += 300000
	app.board._process(0)
	t.check(app.board.effects.has(16), "longer wave still active after the old 260ms bound")
	stroke(Vector2i(16, 0), Vector2i(16, 0), MOUSE_BUTTON_RIGHT)
	t.check(app.session.player.cursor == 2 and app.session.player.cells[16] == 0, "fresh input commits inside extended animation window")
	t.check(app.store.load_slot(app.session.definition).data.cells[16] == 0, "extended-window input is saved immediately")
	reset()
	app.session.player.commit([{"index": 2, "before": -1, "after": 1}, {"index": 5, "before": -1, "after": 0}])
	stroke(Vector2i(7, 0), Vector2i(0, 0), MOUSE_BUTTON_LEFT)
	wave([7, 6, 4, 3, 1, 0], 1)
	reset()
	# Final segment is vertical after a horizontal extension, retraction and G1.
	t.mouse(t.point(5, 5), MOUSE_BUTTON_RIGHT, true)
	t.motion(t.point(12, 5))
	t.motion(t.point(5, 5))
	t.motion(t.point(5, 0))
	t.motion(t.point(5, 2))
	t.mouse(t.point(5, 2), MOUSE_BUTTON_RIGHT, false)
	wave([105, 85, 65, 45], 0)
	reset()
	stroke(Vector2i(0, 0), Vector2i(16, 0), MOUSE_BUTTON_LEFT)
	# Convert pending targets and retract: their older schedules must stay dead.
	t.mouse(t.point(16, 0), MOUSE_BUTTON_RIGHT, true)
	t.motion(t.point(10, 0))
	t.check(app.board.effects.size() == 10 and app.session.visible_cells()[10] == 0, "preview supersedes pending fills")
	t.motion(t.point(16, 0))
	t.check(not app.board.effects.has(10) and app.session.visible_cells()[10] == 1, "retracted waiting fill never returns")
	t.mouse(t.point(16, 0), MOUSE_BUTTON_RIGHT, false)
	t.check(app.board.effects[16].after == 0 and app.session.player.cursor == 2, "new commit wins without input lock")
	app.board.clear_effects()
	stroke(Vector2i(15, 0), Vector2i(0, 0), MOUSE_BUTTON_LEFT)
	for effect: Dictionary in app.board.effects.values():
		t.check(int(effect.start) == clock[0] and is_equal_approx(effect.seconds, 0.12) and effect.after == -1, "removal has no staggering or old mark")
	clock[0] += 120000
	app.board._process(0)
	t.check(app.board.effects.is_empty(), "whole removal ends at 120ms")
	reset()
	stroke(Vector2i(0, 0), Vector2i(16, 0), MOUSE_BUTTON_LEFT)
	app.board.clear_effects()
	stroke(Vector2i(16, 0), Vector2i(0, 0), MOUSE_BUTTON_RIGHT)
	wave([16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], 0)

func lifecycle() -> void:
	for event: String in ["undo", "redo", "escape", "focus", "zoom", "pan", "resize", "information", "album", "reset", "restore", "switch", "off"]:
		reset()
		if event == "redo":
			stroke(Vector2i.ZERO, Vector2i(16, 0), MOUSE_BUTTON_LEFT)
			app._undo()
			app._redo()
			t.check(app.board.effects.is_empty(), "redo never schedules effects")
			continue
		stroke(Vector2i.ZERO, Vector2i(16, 0), MOUSE_BUTTON_LEFT)
		t.check(int(app.board.effects[16].start) > clock[0], "lifecycle has genuinely waiting effects: " + event)
		match event:
			"undo": app._undo()
			"escape": escape()
			"focus": app.propagate_notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
			"zoom": app.board.zoom(1, app.board.view.viewport.get_center())
			"pan": app.board.navigate_to(Vector2(0.4, 0.4))
			"resize": app.size = Vector2(1600, 900); app._layout_book()
			"information": app.show_information()
			"album": app.show_album()
			"reset": app._reset_selected()
			"restore": app.board.restore_view(app.board.capture_view())
			"switch": app.select_puzzle(1)
			"off": app.animation_toggle.button_pressed = false
		t.check(app.board.effects.is_empty(), "lifecycle clears waiting and active: " + event)
		var state: Array = logical()
		clock[0] += 1000000
		app.board._process(0)
		t.check(logical() == state and app.board.effects.is_empty(), "no deferred resurrection after " + event)
		app.size = Vector2(1920, 1080)

func escape() -> void:
	var event: InputEventKey = InputEventKey.new()
	event.keycode = KEY_ESCAPE
	event.pressed = true
	t.surface.push_input(event, true)

func chords() -> void:
	for first: MouseButton in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		var other: MouseButton = MOUSE_BUTTON_RIGHT if first == MOUSE_BUTTON_LEFT else MOUSE_BUTTON_LEFT
		for outside: bool in [false, true]:
			for release_first: bool in [false, true]:
				reset()
				stroke(Vector2i(0, 2), Vector2i(16, 2), MOUSE_BUTTON_LEFT)
				var state: Array = logical()
				var commits: Array[int] = [0]
				var listener: Callable = func() -> void: commits[0] += 1
				app.board.committed.connect(listener)
				t.mouse(t.point(0, 0), first, true)
				t.motion(t.point(8, 0))
				var p: Vector2 = Vector2(1850, 100) if outside else t.point(8, 0)
				t.mouse(p, other, true)
				t.check(not app.session.gesture.active and app.board.preview.is_empty() and app.board.effects.is_empty(), "opposite Down cancels globally")
				t.check(app.board.cell_buttons_blocked and app.board.held_button == MOUSE_BUTTON_NONE, "both buttons must be released")
				escape()
				var released: MouseButton = first if release_first else other
				var held: MouseButton = other if release_first else first
				t.mouse(p, released, false)
				t.mouse(t.point(1, 0), released, true)
				t.motion(t.point(6, 0))
				t.check(not app.session.gesture.active, "re-Down and movement while either held stay blocked")
				t.mouse(p, held, false)
				t.mouse(p, released, false)
				clock[0] += 1000000
				app.board._process(0)
				t.check(logical() == state and commits[0] == 0, "aborted chord leaves old action/save/mini intact and never commits")
				t.check(not app.board.cell_buttons_blocked, "release barrier recovers")
				stroke(Vector2i.ZERO, Vector2i(3, 0), first)
				t.check(commits[0] == 1, "fresh Down after both Up works")
				app.board.committed.disconnect(listener)
		reset()
		t.mouse(t.point(0, 0), first, true)
		t.mouse(t.point(2, 0), other, true)
		app.propagate_notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
		# OS releases both outside; no phantom commit or stuck stale mask on return.
		t.buttons = 0
		t.motion(t.point(2, 0))
		t.check(not app.session.gesture.active and not app.board.cell_buttons_blocked, "focus loss permits idle recovery")
		stroke(Vector2i.ZERO, Vector2i(2, 0), first)
		t.check(app.session.player.cursor == 1, "fresh focus-return gesture works")
		reset()
		t.mouse(t.point(0, 0), first, true)
		app.propagate_notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
		t.mouse(t.point(2, 0), other, true)
		t.check(not app.session.gesture.active and app.board.cell_buttons_blocked, "focus return with original still held cannot start opposite gesture")
		t.mouse(t.point(2, 0), first, false)
		t.mouse(t.point(2, 0), other, false)
		stroke(Vector2i.ZERO, Vector2i(2, 0), first)
		t.check(app.session.player.cursor == 1, "release after focus-held chord recovers")
		reset()
		t.mouse(t.point(0, 0), first, true)
		# Historic G1 wrong-Up without opposite Down is still ignored.
		t.mouse(t.point(3, 0), other, false)
		t.check(app.session.gesture.active, "wrong Up alone does not cancel")
		t.mouse(t.point(3, 0), first, false)
		t.check(app.session.player.cursor == 1, "original Up still commits")
	reset()
	t.mouse(t.point(4, 4), MOUSE_BUTTON_MIDDLE, true)
	t.mouse(t.point(4, 4), MOUSE_BUTTON_RIGHT, true)
	t.check(app.board.pan_button == MOUSE_BUTTON_MIDDLE and not app.board.cell_buttons_blocked, "MMB navigation is unchanged")
	t.mouse(t.point(5, 4), MOUSE_BUTTON_RIGHT, false)
	t.mouse(t.point(5, 4), MOUSE_BUTTON_MIDDLE, false)
	app.board.hand = true
	t.mouse(t.point(4, 4), MOUSE_BUTTON_LEFT, true)
	t.mouse(t.point(4, 4), MOUSE_BUTTON_RIGHT, true)
	t.check(app.board.pan_button == MOUSE_BUTTON_LEFT and not app.board.cell_buttons_blocked, "hand navigation is unchanged")
	t.mouse(t.point(5, 4), MOUSE_BUTTON_RIGHT, false)
	t.mouse(t.point(5, 4), MOUSE_BUTTON_LEFT, false)
