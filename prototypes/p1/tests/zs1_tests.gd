extends SceneTree
const Study = preload("res://study/main.gd")
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")
const Marks = preload("res://study/marks.gd")
var app: Control
var surface: SubViewport
var checks: int = 0
var failures: int = 0
var buttons: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("ZS1 FAIL: ", message)

func run() -> void:
	# A poisoned default/override must not be opened by the study constructor.
	Store.test_root_override = "user://zs1-forbidden-normal"
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	var sentinel: FileAccess = FileAccess.open(Store.test_root_override.path_join("f01.json"), FileAccess.WRITE)
	sentinel.store_string("normal-save-sentinel")
	sentinel.close()
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	root.add_child(surface)
	app = load("res://study/main.tscn").instantiate()
	surface.add_child(app)
	await process_frame
	check(app.store.root == app.study_root and not app.store.root.contains("forbidden"), "isolation before slot load")
	check(FileAccess.get_file_as_string(Store.test_root_override.path_join("f01.json")) == "normal-save-sentinel", "normal sentinel untouched")
	check(app.board.style == 2, "selected pencil is startup default")
	check(app.board.font_choice == 2, "owner-selected Chalkboard is startup default")
	font_probe()
	slot_probe()
	for index: int in range(30):
		for which: int in range(2):
			var path: PackedVector2Array = Marks.x_path(index, which)
			check(path == Marks.x_path(index, which), "X geometry deterministic")
			check(path != Marks.x_path(index + 1, which), "X varies across cells")
			for p: Vector2 in path:
				check(Rect2(0.15, 0.15, 0.7, 0.7).has_point(p), "bounded X geometry")
	for choice: int in [1, 2]:
		app.board.set_font_choice(choice)
		app.board.set_style(2)
		gesture_probe()
		fresh()
		# Geometry and semantic reads stay fixed while switching only style.
		var rect: Rect2 = app.board.view.viewport
		var view: Dictionary = app.board.capture_view()
		var before_cells: Array[int] = app.session.player.cells.duplicate()
		for variant: int in [0, 2]:
			app.board.set_style(variant)
			check(app.board.view.viewport == rect and app.board.capture_view() == view and app.session.player.cells == before_cells, "variant same geometry/state")
	check(FileAccess.get_file_as_string(Store.test_root_override.path_join("f01.json")) == "normal-save-sentinel", "normal sentinel still untouched")
	print("ZS1_TESTS checks=", checks, " failures=", failures)
	if failures == 0:
		print("ZS1_TESTS_OK")
	quit(0 if failures == 0 else 1)

func gesture_probe() -> void:
	fresh()
	var a: Vector2 = point(0, 0)
	var b: Vector2 = point(19, 0)
	mouse(a, MOUSE_BUTTON_LEFT, true)
	motion(b)
	check(app.session.gesture.active and app.board.preview.size() == 20, "native route long static preview")
	check(app.board.effects.is_empty() and app.session.player.cursor == 0, "preview no effect/history")
	mouse(b, MOUSE_BUTTON_LEFT, false)
	check(app.session.player.cursor == 1 and app.board.effects.size() == 20, "one atomic commit, 20 directed effects")
	var start: int = int(app.board.effects[0].start)
	for index: int in range(20):
		check(int(app.board.effects[index].start) == start + roundi(index * 120000.0 / 19), "directed bounded timestamp")
	# Same tick: the first effect has not ended. A new real GUI gesture wins.
	mouse(a, MOUSE_BUTTON_RIGHT, true)
	motion(point(4, 0))
	check(app.session.gesture.active and app.board.effects.size() == 15, "second gesture before first finishes")
	check(app.session.visible_cells()[0] == 0 and not app.board.effects.has(0), "conversion preview replaces old fill")
	motion(a)
	check(not app.board.effects.has(4) and app.session.visible_cells()[4] == 1, "retraction never resurrects effect")
	mouse(a, MOUSE_BUTTON_RIGHT, false)
	check(app.session.player.cells[0] == 0 and app.session.player.cursor == 2, "immediate conversion commit")
	check(int(app.board.effects[0].after) == 0, "only youngest target")
	var snapshot: Array[int] = app.session.player.cells.duplicate()
	app._undo()
	check(app.board.effects.is_empty() and app.session.player.cells[0] == 1, "undo immediate, no effect")
	app._redo()
	check(app.board.effects.is_empty() and app.session.player.cells == snapshot, "redo exact, no effect")
	mouse(a, MOUSE_BUTTON_RIGHT, true)
	check(app.session.visible_cells()[0] == -1 and app.board.preview.has(0), "erase preview unknown with contour")
	mouse(a, MOUSE_BUTTON_RIGHT, false)
	check(int(app.board.effects[0].after) == -1 and float(app.board.effects[0].seconds) == 0.08, "erase effect only neutral target")
	var cursor: int = app.session.player.cursor
	var bytes: String = FileAccess.get_file_as_string(app.store.path_for("f01"))
	app.board.set_animations(false)
	check(app.board.effects.is_empty() and not app.board.is_processing(), "disable clears and stops ticking")
	app.board.set_animations(true)
	check(app.board.effects.is_empty() and app.session.player.cursor == cursor, "enable no replay/history")
	check(FileAccess.get_file_as_string(app.store.path_for("f01")) == bytes, "toggle does not save")
	# Unknown start protects the existing fills in the middle of a long stroke.
	mouse(a, MOUSE_BUTTON_RIGHT, true)
	motion(b)
	check(app.board.preview.size() == 1, "protected cells absent from preview")
	mouse(b, MOUSE_BUTTON_RIGHT, false)
	check(app.board.effects.size() == 1, "protected cells do not animate")
	app.board.cancel_gesture()
	app.board.eraser = true
	mouse(point(0, 1), MOUSE_BUTTON_LEFT, true)
	mouse(point(0, 1), MOUSE_BUTTON_LEFT, false)
	check(app.board.effects.is_empty(), "noop does not animate")
	app.board.eraser = false
	mouse(point(0, 1), MOUSE_BUTTON_LEFT, true)
	motion(point(8, 1))
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	surface.push_input(escape, true)
	check(app.board.effects.is_empty() and app.session.player.cells[20] == -1 and not app.session.gesture.active, "escape without action/effect")
	mouse(point(0, 1), MOUSE_BUTTON_LEFT, false)
	mouse(point(0, 1), MOUSE_BUTTON_LEFT, true)
	app._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	check(app.board.preview.is_empty() and not app.session.gesture.active, "focus loss clears preview")
	mouse(point(0, 1), MOUSE_BUTTON_LEFT, false)
	for event: String in ["zoom", "resize", "information", "album", "reset", "switch"]:
		fresh()
		mouse(point(0, 0), MOUSE_BUTTON_LEFT, true)
		mouse(point(0, 0), MOUSE_BUTTON_LEFT, false)
		check(not app.board.effects.is_empty(), "lifecycle starts effect")
		match event:
			"zoom": app.board.zoom(1, app.board.view.viewport.get_center())
			"resize": app.size = Vector2(1600, 900); app._layout_book()
			"information": app.show_information()
			"album": app.show_album()
			"reset": fresh()
			"switch": app.select_puzzle(1)
		check(app.board.effects.is_empty(), "lifecycle clears " + event)
		app.size = Vector2(1920, 1080)
	# Finish is immediate even while the display would still be animating.
	fresh()
	var changes: Array = []
	var final_cell: Vector2i = Vector2i(-1, -1)
	for y: int in range(20):
		for x: int in range(20):
			if int(app.session.definition.solution[y][x]) > 0:
				if final_cell.x < 0:
					final_cell = Vector2i(x, y)
				else:
					changes.append({"index": y * 20 + x, "before": -1, "after": 1})
	app.session.player.commit(changes)
	mouse(point(final_cell.x, final_cell.y), MOUSE_BUTTON_LEFT, true)
	mouse(point(final_cell.x, final_cell.y), MOUSE_BUTTON_LEFT, false)
	check(app.session.completed and app.ending.visible and app.board.effects.is_empty(), "finish has no animation delay")
	check(app.store.load_slot(app.session.definition).data.completed, "completion saved immediately")

func slot_probe() -> void:
	app.board.set_font_choice(2)
	app.set_ui_scale(1.0)
	var fs: int = app.board.clue_font_size()
	check(is_equal_approx(app.board.shared_clue_slot_extent("row", app.board.clue_font(), fs), 26.0), "Chalkboard row clues use compact 26px slots")
	check(is_equal_approx(app.board.shared_clue_slot_extent("column", app.board.clue_font(), fs), 18.0), "column clue spacing remains 18px")
	app.set_ui_scale(1.25)
	fs = app.board.clue_font_size()
	check(is_equal_approx(app.board.shared_clue_slot_extent("row", app.board.clue_font(), fs), 32.5), "compact row slots scale with UI")
	check(is_equal_approx(app.board.shared_clue_slot_extent("column", app.board.clue_font(), fs), 22.5), "column slots scale unchanged")
	app.set_ui_scale(1.0)

func font_probe() -> void:
	var fonts = app.board.Fonts
	for choice: int in [1, 2]:
		var evidence: Dictionary = fonts.evidence(choice)
		check(evidence.digits_native and evidence.sha256 == fonts.HASHES[choice], "exact original TTF with native digits")
		check(not fonts.selected(choice).allow_system_fallback, "no implicit system font")
		app.board.set_font_choice(choice)
		for symbol: String in "…–":
			check(app.board.clue_text_font(fonts.selected(choice), symbol) == fonts.REFERENCE, "explicit shared navigation punctuation")
		print("ZS1_FONT ", JSON.stringify(evidence))
	for index: int in range(3):
		app.select_puzzle(index)
		app.open_puzzle()
		app.board.set_clue_step("row", 12, 2)
		app.board.set_clue_step("column", 22 if index > 0 else 2, 3)
		app.session.player.commit([{"index": 0, "before": app.session.player.cells[0], "after": 1 if app.session.player.cells[0] != 1 else 0}])
		app._save_current()
		var save_path: String = app.store.path_for("f%02d" % (index + 1))
		check(FileAccess.file_exists(save_path), "font switch has a real saved nonempty history")
		var before: Dictionary = app.board.capture_view()
		var cells: Array[int] = app.session.player.cells.duplicate()
		var cursor: int = app.session.player.cursor
		var saved: String = FileAccess.get_file_as_string(save_path)
		for style: int in [0, 2]:
			app.board.set_style(style)
			for choice: int in [0, 1, 2]:
				app.board.set_font_choice(choice)
				check(app.board.style == style and app.board.capture_view() == before, "font independent of style and semantic reads")
				check(app.session.player.cells == cells and app.session.player.cursor == cursor, "font preserves cells and history")
				check(FileAccess.get_file_as_string(save_path) == saved, "font does not write saves")
				for symbol: String in "0123456789…–":
					check(app.board.clue_font().has_char(symbol.unicode_at(0)), "digit or explicit punctuation available")
	app.board.set_style(2)
	app.board.set_font_choice(2)

func fresh() -> void:
	app.select_puzzle(0)
	app.empty_sample()
	app.board.working_size()
	app.board.hand = false
	app.board.eraser = false

func point(x: int, y: int) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(Vector2i(x, y)).get_center()

func motion(p: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = p
	event.button_mask = buttons
	surface.push_input(event, true)

func mouse(p: Vector2, button: MouseButton, down: bool) -> void:
	motion(p)
	app.board.clear_clue_hover()
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	var flag: int = 1 << (int(button) - 1)
	buttons = (buttons | flag) if down else (buttons & ~flag)
	event.button_mask = buttons
	surface.push_input(event, true)
