extends "res://tests/zs1_tests.gd"
## Run the proven gesture contract through the actual regular scene and save path.
const Regular = preload("res://ui/chalkboard_board.gd")
var saved_root: String

func run() -> void:
	Store.test_root_override = "user://zs2-tests-%d" % Time.get_ticks_usec()
	saved_root = Store.test_root_override
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	root.add_child(surface)
	app = load("res://main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	check(app.board is Regular and app.store.root == saved_root, "regular scene and isolated test save root")
	check(app.sessions.size() == 9, "all nine regular sheets available")
	check(app.animation_toggle.button_pressed and app.board.animations, "new session starts enabled")
	check(not app.has_method("cycle_font") and not app.has_method("empty_sample"), "no study controls in regular app")
	for index: int in range(9):
		app.select_puzzle(index)
		for scale: float in [1.0, 1.25]:
			app.set_ui_scale(scale)
			var board = app.board
			var fs: int = board.clue_font_size()
			check(is_equal_approx(board.shared_clue_slot_extent("row", board.clue_font(), fs), 26.0 * scale), "selected row slots on every sheet")
			check(is_equal_approx(board.shared_clue_slot_extent("column", board.clue_font(), fs), 18.0 * scale), "unchanged column slots on every sheet")
			check(board.clue_font().get_font_name() == "Chalkboard" and not board.clue_font().allow_system_fallback, "selected offline font")
			for symbol: String in "…–":
				check(board.clue_text_font(board.clue_font(), symbol) == Regular.Fonts.REFERENCE, "explicit Plex punctuation")
	app.set_ui_scale(1.0)
	gesture_probe()
	# Real toggle event must not touch any save, history, cells or semantic view.
	fresh()
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, true)
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, false)
	var bytes: String = FileAccess.get_file_as_string(app.store.path_for("f01"))
	var state: Dictionary = app.board.capture_view()
	var history: Array = app.session.player.history.duplicate(true)
	app.animation_toggle.button_pressed = false
	check(app.board.effects.is_empty() and not app.board.animations, "checkbox ends active effects")
	check(app.board.capture_view() == state and app.session.player.history == history, "checkbox preserves view/history")
	check(FileAccess.get_file_as_string(app.store.path_for("f01")) == bytes, "checkbox preserves save bytes")
	for index: int in range(9):
		app.select_puzzle(index)
		app.show_information()
		app.return_to_work()
		app._reset_selected()
		app.open_puzzle()
		check(not app.board.animations and not app.animation_toggle.button_pressed, "session choice survives sheet/page/reset")
	app.animation_toggle.button_pressed = true
	check(app.board.effects.is_empty(), "reenabling never replays")
	app.animation_toggle.button_pressed = false
	app.queue_free()
	await process_frame
	app = load("res://main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	check(app.board.animations and app.animation_toggle.button_pressed, "new app ignores previous session choice")
	# Real G1 reorientation and cancellation supersede old effects permanently.
	fresh()
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, true)
	motion(point(6, 0))
	mouse(point(6, 0), MOUSE_BUTTON_LEFT, false)
	mouse(point(0, 0), MOUSE_BUTTON_RIGHT, true)
	motion(point(6, 0))
	motion(point(0, 0))
	motion(point(0, 5))
	check(app.board.preview.size() == 6 and app.session.visible_cells()[6] == 1, "G1 reorients static target")
	check(not app.board.effects.has(6), "retracted horizontal effect stays superseded")
	app.board.cancel_gesture()
	check(app.board.effects.is_empty() and app.session.player.cursor == 1, "cancel leaves confirmed action only")
	# Removing cannot resurrect the old fill; set/remove clocks are total durations.
	var time: Array[int] = [1000000]
	app.board.animation_clock = func() -> int: return time[0]
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, true)
	mouse(point(0, 0), MOUSE_BUTTON_LEFT, false)
	time[0] += 79000
	app.board._process(0)
	check(app.board.effects.has(0) and app.session.player.cells[0] == -1, "remove remains purely visual at 79ms")
	time[0] += 1000
	app.board._process(0)
	check(app.board.effects.is_empty(), "remove ends at 80ms")
	mouse(point(0, 1), MOUSE_BUTTON_RIGHT, true)
	mouse(point(0, 1), MOUSE_BUTTON_RIGHT, false)
	time[0] += 139000
	app.board._process(0)
	check(app.board.effects.has(20), "set still active at 139ms")
	time[0] += 1000
	app.board._process(0)
	check(app.board.effects.is_empty() and not app.board.is_processing(), "set ends at 140ms and ticker stops")
	app.board.animation_clock = Time.get_ticks_usec
	print("ZS2_TESTS checks=", checks, " failures=", failures)
	if failures == 0:
		print("ZS2_TESTS_OK")
	quit(0 if failures == 0 else 1)

func fresh() -> void:
	app.select_puzzle(0)
	app._reset_selected()
	app.open_puzzle()
	app.board.working_size()
	app.board.hand = false
	app.board.eraser = false
