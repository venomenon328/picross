extends SceneTree
const Store = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
const Cases = preload("res://tests/vs2_scene.gd")
var app: Control
var canvas: SubViewport
var checks: int = 0
var failures: int = 0
var records: Array = []
var pictures: Array = []
var output: String

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		if failures < 30: printerr("VS2 FAIL: ", message)

func point(cell: Vector2i) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(cell).get_center()

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

func shot(name: String) -> void:
	if output.is_empty() or DisplayServer.get_name() == "headless": return
	app.board.clear_pointer_hover()
	app.board.clear_effects()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var image: Image = canvas.get_texture().get_image()
	var path: String = output.path_join(name + ".png")
	check(image.save_png(path) == OK, "native PNG write")
	pictures.append({"file":name+".png", "sha256":FileAccess.get_sha256(path), "client":[canvas.size.x,canvas.size.y]})

func run() -> void:
	output = OS.get_environment("VS2_CAPTURE_DIR")
	Store.test_root_override = OS.get_user_data_dir().path_join("vs2-regular-%d" % Time.get_ticks_usec())
	var sentinel: String = OS.get_user_data_dir().path_join("vs1/revision-1/study-view.json")
	DirAccess.make_dir_recursive_absolute(sentinel.get_base_dir())
	FileAccess.open(sentinel,FileAccess.WRITE).store_string("untouched VS2 sentinel")
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920,1080)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	app = load("res://main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	check(app.album.visible and not app.work.visible and not app.ending.visible, "fresh regular startup is collection")
	check(app.board.mode == "G" and app.view_choice.item_count == 2 and not app.actions.has("hand"), "one named option, G default, no hand")
	check(app.sessions.size() == 9 and app.store.root == Store.test_root_override, "unchanged regular catalog/root")
	await shot("album")
	app.show_information("settings")
	check(app.information.visible and app.information_origin == "album" and not app.work.visible, "options from album never open a sheet")
	app.view_choice.item_selected.emit(1)
	check(app.board.mode == "V", "real named option selects V")
	await shot("options")
	app.return_to_work()
	check(app.album.visible and not app.work.visible, "options return to collection")
	for index: int in range(9):
		app.select_puzzle(index)
		app._reset_selected()
		check(app.board.mode == "V", "view choice survives sheet/reset")
	app.set_puzzle_view(0)
	await matrix(false)
	app.select_puzzle(0)
	app.set_ui_scale(1.0)
	canvas.size = Vector2i(1920,1080)
	app.size = Vector2(canvas.size)
	await process_frame
	app._reset_selected()
	app.open_puzzle()
	app.board.working_size()
	var cells: Array = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	var center: Vector2 = app.board.view.center
	var p: Vector2 = point(Vector2i(2,2))
	mouse(p,MOUSE_BUTTON_MIDDLE,true)
	motion(p+Vector2(100,80))
	mouse(p+Vector2(100,80),MOUSE_BUTTON_MIDDLE,false)
	app.board.hand = true # An injected obsolete state must have no input route.
	mouse(p,MOUSE_BUTTON_LEFT,true)
	motion(p+Vector2(100,80))
	mouse(p+Vector2(100,80),MOUSE_BUTTON_LEFT,false)
	app.board.hand = false
	var m: Vector2 = app.mini.global_position+app.mini.image_rect().get_center()
	mouse(m,MOUSE_BUTTON_LEFT,true)
	motion(m+Vector2(20,20))
	mouse(m+Vector2(20,20),MOUSE_BUTTON_LEFT,false)
	check(app.board.view.center == center and app.session.player.cells == cells and app.session.player.history == history, "native grid MMB, legacy hand and miniature cannot pan or paint")
	var legacy: Dictionary = app.board.capture_view()
	legacy.zoom = 72
	legacy.overview = false
	legacy.tool = "hand"
	legacy.center = [18.0,3.0]
	app.board.restore_view(legacy)
	check(not app.board.hand and not app.board.eraser and app.board.capture_view().zoom == 72 and app.board.view.cell_size <= app.board.fit_ceiling and app.board.view.center == Vector2(10,10), "legacy hand/pan/zoom maps after validation, desired step retained")
	check(app.session.player.cells == cells and app.session.player.history == history, "restore changes no gameplay")
	mouse(p,MOUSE_BUTTON_LEFT,true)
	app.show_information()
	check(not app.session.gesture.active and app.board.effects.is_empty() and app.session.player.cells == cells, "options cancel gesture/effects")
	app.return_to_work()
	app.select_puzzle(2)
	app.set_puzzle_view(0)
	app.board.working_size()
	await process_frame
	for axis: String in ["row","column"]:
		var lines: Array = app.session.definition.rows if axis == "row" else app.session.definition.columns
		var index: int = 0
		for i: int in range(lines.size()):
			if lines[i].size() > lines[index].size(): index=i
		var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
		var cross: Vector2 = app.board.view.cell_rect(Vector2i(index,index)).get_center()
		var local: Vector2 = Vector2(area.get_center().x,cross.y) if axis == "row" else Vector2(cross.x,area.get_center().y)
		var start: Vector2 = app.board.global_position+local
		var prior: Array = app.board.row_clue_reads.duplicate(true) if axis == "row" else app.board.column_clue_reads.duplicate(true)
		mouse(start,MOUSE_BUTTON_MIDDLE,true)
		motion(start+(Vector2(100,60) if axis=="row" else Vector2(60,100)))
		check(app.board.pan_target == axis and app.board.pan_line_index == index, "MMB target freezes across lines")
		mouse(start,MOUSE_BUTTON_MIDDLE,false)
		var after: Array = app.board.row_clue_reads if axis == "row" else app.board.column_clue_reads
		check(after[index] != prior[index], "positive independent clue MMB")
		for i: int in range(prior.size()):
			if i != index: check(after[i] == prior[i], "other clue reads unchanged")
	app.queue_free()
	await process_frame
	app = Cases.new()
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	canvas.add_child(app)
	await process_frame
	await matrix(true)
	check(FileAccess.get_file_as_string(sentinel) == "untouched VS2 sentinel", "regular work leaves study root untouched")
	if not output.is_empty():
		FileAccess.open(output.path_join("vs2-matrix.json"),FileAccess.WRITE).store_string(JSON.stringify({"records":records,"pictures":pictures,"checks":checks,"failures":failures},"\t"))
	print("VS2_TESTS_", "OK" if failures == 0 else "FAILED", " checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)

func matrix(corpus: bool) -> void:
	for client: Vector2i in [Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080),Vector2i(2560,1440)]:
		print("VS2_MATRIX corpus=",corpus," client=",client)
		canvas.size = client
		app.size = Vector2(client)
		for ui: float in [1.0,1.25]:
			app.set_ui_scale(ui)
			for index: int in range(app.sessions.size()):
				app.select_puzzle(index)
				for mode: int in range(2):
					app.set_puzzle_view(mode)
					app.board.fit_all()
					await process_frame
					var board = app.board
					var data: Dictionary = board.measurements()
					data.merge({"id":app.session.definition.id,"corpus":corpus,"client":[client.x,client.y],"ui_scale":ui,"board_rect":board.rect_values(board.get_global_rect())})
					check(not data.layout_valid or data.grid_fit, "all four outer frame edges fit")
					check(mode == 0 or data.hidden_tokens == 0, "V retains all hints")
					var old: float = board.view.cell_size
					for i: int in range(22): board.zoom(1,board.view.viewport.get_center())
					check(board.view.cell_size <= board.fit_ceiling and is_equal_approx(board.view.cell_size,old), "all zoom-up routes stop at fit")
					check(board.capture_view().zoom in Store.ZOOMS, "computed fractional fit is never saved as desired zoom")
					if data.layout_valid:
						for cell: Vector2i in [Vector2i.ZERO,Vector2i(board.session.player.width-1,0),Vector2i(0,board.session.player.height-1),Vector2i(board.session.player.width-1,board.session.player.height-1)]:
							check(board.view.hit(board.view.cell_rect(cell).get_center()) == cell, "four rectangular corner hits")
					check(is_equal_approx(app.mini.image_rect().size.x/app.mini.image_rect().size.y,float(app.session.player.width)/app.session.player.height), "proportional passive own miniature")
					check(not app.mini.interactive and app.mini.cells == app.session.visible_cells(), "miniature exclusively own cells")
					records.append(data)
					if client.x == 1920 and mode == 0 and ((corpus and index in [3,7,8]) or (not corpus and index in [0,6])):
						await shot("%s-%s-ui%d" % ["corpus" if corpus else "regular",app.session.definition.id,roundi(ui*100)])
