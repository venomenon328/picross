extends SceneTree
const Store = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
var app: Control
var canvas: SubViewport
var failures: int = 0
var checks: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("VS1 FAIL: ", message)

func point(x: int, y: int) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(Vector2i(x,y)).get_center()

func motion(p: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = p
	canvas.push_input(event, true)

func mouse(p: Vector2, button: MouseButton, down: bool) -> void:
	motion(p)
	app.board.clear_clue_hover()
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	canvas.push_input(event, true)

func click(x: int, y: int, button: MouseButton) -> void:
	mouse(point(x,y),button,true)
	mouse(point(x,y),button,false)

func run() -> void:
	OS.set_environment("VS1_TEST_ROOT", OS.get_user_data_dir().path_join("vs1-test-%d" % Time.get_ticks_usec()))
	Store.test_root_override = "user://vs1-forbidden-p1"
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	var sentinel: String = Store.test_root_override.path_join("f01.json")
	FileAccess.open(sentinel,FileAccess.WRITE).store_string("normal sentinel")
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920,1080)
	root.add_child(canvas)
	app = load("res://full_view_study/main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	check(app.store.root == OS.get_environment("VS1_TEST_ROOT") and app.store.path_for("f01").is_empty(), "isolation before reads")
	check(Store.new().path_for("vs01").is_empty() and Store.IDS.size() == 9, "normal catalog remains nine")
	check(app.sessions.size() == 10 and app.board.style == 2 and app.board.font_choice == 2, "ten cases with bound drawing layer")
	for index: int in range(10):
		app.select_puzzle(index)
		app._reset_selected()
		app.open_puzzle()
		app.choose_mode("G")
		app.board.fit_all()
		await process_frame
		var w: int = app.session.player.width
		var h: int = app.session.player.height
		for cell: Vector2i in [Vector2i.ZERO,Vector2i(w-1,0),Vector2i(0,h-1),Vector2i(w-1,h-1)]:
			check(app.board.view.hit(point(cell.x,cell.y)-app.board.global_position) == cell, "rectangular corner hit")
			click(cell.x,cell.y,MOUSE_BUTTON_LEFT)
			check(app.session.player.cells[cell.y*w+cell.x] == 1, "actual mouse corner write")
		var cursor: int = app.session.player.cursor
		mouse(point(1,1),MOUSE_BUTTON_LEFT,true)
		motion(point(w-2,1))
		motion(point(5,1))
		mouse(point(5,1),MOUSE_BUTTON_LEFT,false)
		check(app.session.player.cursor == cursor+1 and app.session.player.cells[w+5] == 1 and app.session.player.cells[w+6] == -1, "atomic line retract")
		mouse(point(1,1),MOUSE_BUTTON_RIGHT,true)
		motion(point(5,1))
		mouse(point(5,1),MOUSE_BUTTON_RIGHT,false)
		check(app.session.player.cells[w+5] == 0, "line conversion")
		click(5,1,MOUSE_BUTTON_RIGHT)
		check(app.session.player.cells[w+5] == -1, "neutralize X")
		app._undo()
		check(app.session.player.cells[w+5] == 0, "undo")
		app._redo()
		check(app.session.player.cells[w+5] == -1, "redo")
		var cells: Array = app.session.player.cells.duplicate()
		var history: Array = app.session.player.history.duplicate(true)
		app.board.active_color = app.session.definition.palette.size()
		for mode: String in ["R","G","V","R","G"]:
			mouse(point(1,2),MOUSE_BUTTON_LEFT,true)
			app.choose_mode(mode)
			mouse(point(1,2),MOUSE_BUTTON_LEFT,false)
			check(not app.session.gesture.active and app.session.player.cells == cells and app.session.player.history == history, "switch cancels gesture without model change")
			check(app.board.active_color == app.session.definition.palette.size(), "switch preserves active color")
			check(app._save_current(), "every mode saves valid schema including first R entry")
		app.board.fit_all()
		var center: Vector2 = app.board.view.center
		mouse(point(4,4),MOUSE_BUTTON_MIDDLE,true)
		motion(point(8,8))
		mouse(point(8,8),MOUSE_BUTTON_MIDDLE,false)
		check(app.board.view.center == center, "G middle mouse cannot pan grid")
		check(app.mini.width == w and app.mini.height == h and is_equal_approx(app.mini.image_rect().size.x/app.mini.image_rect().size.y,float(w)/h), "rectangular miniature aspect")
		check(not app.ending.visible and not app.session.completed and app.session.album_title().find(app.session.definition.reveal.name) < 0, "neutral title and no reveal")
		check(app._save_current(), "study write")
		var saved: Dictionary = app.store.load_slot(app.session.definition)
		var replay: Session = Session.new(app.session.definition)
		Store.apply(saved.data, replay)
		check(saved.status == "loaded" and replay.player.cells == app.session.player.cells, "rectangular saved cells")
		check(Store.validate(saved.data,app.session.definition).is_empty() and saved.data.view.zoom in Store.ZOOMS, "unchanged schema valid")
		var bad: Dictionary = saved.data.duplicate(true)
		bad.width += 1
		check(not Store.validate(bad,app.session.definition).is_empty(), "wrong dimensions rejected")
	# Long clues remain independently mouse-navigable in G, never in V.
	app.select_puzzle(7)
	app.choose_mode("G")
	app.board.fit_all()
	for axis: String in ["row","column"]:
		var lines: Array = app.session.definition.rows if axis == "row" else app.session.definition.columns
		var index: int = 0
		for i: int in range(lines.size()):
			if lines[i].size()>lines[index].size(): index=i
		var area: Rect2 = app.board.row_clue_area() if axis=="row" else app.board.column_clue_area()
		var p: Vector2 = app.board.global_position + (Vector2(area.get_center().x,app.board.view.origin.y+(index+0.5)*app.board.view.cell_size) if axis=="row" else Vector2(app.board.view.origin.x+(index+0.5)*app.board.view.cell_size,area.get_center().y))
		var old: Dictionary = app.board.capture_view()
		mouse(p,MOUSE_BUTTON_MIDDLE,true)
		check(app.board.pan_target==axis,"MMB selects clue axis")
		var q: Vector2 = p+(Vector2(120,0) if axis=="row" else Vector2(0,90))
		motion(q)
		mouse(q,MOUSE_BUTTON_MIDDLE,false)
		check(app.board.capture_view()!=old,"MMB commits independent clue read")
	app.choose_mode("V")
	check(app.board.navigation_target(app.board.column_clue_area().get_center()).is_empty(),"V has no hint pan")
	app.choose_mode("R")
	app.board.working_size()
	var center_before: Vector2 = app.board.view.center
	var p: Vector2 = app.board.global_position+app.board.view.viewport.get_center()
	mouse(p,MOUSE_BUTTON_MIDDLE,true)
	motion(p-Vector2(90,60))
	mouse(p-Vector2(90,60),MOUSE_BUTTON_MIDDLE,false)
	check(app.board.view.center!=center_before,"R actual MMB grid pan retained")
	app.choose_mode("G")
	var before_cancel: Array = app.session.player.cells.duplicate()
	for action: String in ["escape","resize"]:
		mouse(point(2,3),MOUSE_BUTTON_LEFT,true)
		if action=="escape":
			var key: InputEventKey = InputEventKey.new()
			key.keycode=KEY_ESCAPE; key.pressed=true; canvas.push_input(key,true)
		else:
			app.size=Vector2(1280,720); app._layout_book()
		check(not app.session.gesture.active and app.session.player.cells==before_cancel,"cancel/resize no cell action")
		mouse(point(2,3),MOUSE_BUTTON_LEFT,false)
		app.size=Vector2(1920,1080); app._layout_book()
	app.select_puzzle(9)
	# Stable restart resumes selected case, mode, UI and exact cells/history.
	app.choose_mode("V")
	app.set_ui_scale(1.25)
	check(app._save_current(), "persist view")
	var wanted: Array = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	app.queue_free()
	await process_frame
	app = load("res://full_view_study/main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	check(app.session.definition.id == "VS10" and app.board.mode == "V" and app.ui_scale == 1.25, "restart restores selection mode UI")
	check(app.session.player.cells == wanted and app.session.player.history == history, "restart exact history")
	# Corrupt primary: backup is exposed; no silent overwrite until explicit recovery.
	check(app._save_current(), "backup exists")
	var path: String = app.store.path_for("vs10")
	FileAccess.open(path,FileAccess.WRITE).store_string("broken")
	var recovered: Dictionary = app.store.load_slot(app.session.definition)
	check(recovered.status == "recovered", "backup recovery offered")
	app.slot_status[9] = "recovered"
	check(not app._save_current() and FileAccess.get_file_as_string(path) == "broken", "recovery needs conscious adoption")
	app._repair_selected()
	check(app._save_current(), "explicit backup adoption")
	# Real completion contract on both rectangle orientations; no aspect distortion.
	for index: int in [2,4,9]:
		app.select_puzzle(index)
		app._reset_selected()
		app.open_puzzle()
		var changes: Array = []
		for y: int in range(app.session.player.height):
			for x: int in range(app.session.player.width):
				changes.append({"index":y*app.session.player.width+x,"before":-1,"after":int(app.session.definition.solution[y][x])})
		app.session.player.commit(changes)
		# Leave the last cell to the actual GUI event/Session.finish route.
		app.session.player.undo()
		changes.pop_back()
		app.session.player.commit(changes)
		var last: int = int(app.session.definition.solution[-1][-1])
		app.choose_mode("G")
		app.board.fit_all()
		app.board.active_color = maxi(last,1)
		click(app.session.player.width-1,app.session.player.height-1,MOUSE_BUTTON_RIGHT if last==0 else MOUSE_BUTTON_LEFT)
		app.refresh()
		check(app.session.completed, "rectangular end matrix completes")
		check(app._save_current() and app.store.load_slot(app.session.definition).data.completed, "completion persists")
	check(FileAccess.get_file_as_string(sentinel) == "normal sentinel", "normal save byte identical")
	print("VS1_TESTS_", "OK" if failures == 0 else "FAILED", " checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
