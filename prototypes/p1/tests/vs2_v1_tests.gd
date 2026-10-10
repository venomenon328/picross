extends "res://tests/vs2_tests.gd"
const V1 = preload("res://tests/vs2_v1_cases.gd")
const Drag = preload("res://tests/vs1_e1_cases.gd")
const Definition = preload("res://model/definition.gd")
var focused: Array = []
var glyphs: Array = []

class GlyphBoard extends "res://ui/full_view_board.gd":
	var probe_status: int = 0
	func clue_status(_axis: String, _index: int, _token: int) -> int:
		return probe_status

func stable_input() -> void:
	var b = app.board
	var before: Rect2 = b.view.bounds()
	var rows: Rect2 = b.row_clue_area()
	var columns: Rect2 = b.column_clue_area()
	var saved: Array = app.session.player.cells.duplicate()
	for cell: Vector2i in [Vector2i.ZERO,Vector2i(b.session.player.width-1,b.session.player.height-1)]:
		var p: Vector2 = point(cell)
		mouse(p,MOUSE_BUTTON_LEFT,true)
		mouse(p,MOUSE_BUTTON_LEFT,false)
		check(app.session.player.cells[cell.y*b.session.player.width+cell.x] == 1,"V1 shifted corner actual input")
		app._undo()
		app._redo()
		app._undo()
		check(app.session.player.cells == saved,"V1 shifted input exact undo/redo")
		check(b.view.bounds() == before and b.row_clue_area() == rows and b.column_clue_area() == columns,"V1 progress/undo does not move layout")
	for status: bool in [false,true]:
		app.set_clue_completion(status)
		check(b.view.bounds() == before,"V1 H1 toggle does not move layout")
	for i: int in range(app.palette_row.get_child_count()):
		var p: Vector2 = app.palette_row.get_child(i).get_global_rect().get_center()
		mouse(p,MOUSE_BUTTON_LEFT,true)
		mouse(p,MOUSE_BUTTON_LEFT,false)
		check(b.active_color == i+1 and not b.eraser,"V1 moved palette actual hit")
	app.board.active_color = 1
	app.session.player.history.clear()
	app.session.player.cursor = 0
	app.coordinate.text = "Zeile – · Spalte –"
	app._update_actions()

func focused_scene(corpus: bool) -> void:
	if app != null:
		app.queue_free()
		await process_frame
	app = Cases.new() if corpus else load("res://main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	canvas.size = Vector2i(1920,1080)
	app.size = Vector2(canvas.size)
	for index: int in ([3,7,8] if corpus else [0]):
		app.select_puzzle(index)
		app._reset_selected()
		app.open_puzzle()
		for u: float in [1.0,1.25]:
			app.set_ui_scale(u)
			for mode: int in range(2):
				app.set_puzzle_view(mode)
				for fit: bool in [false,true]:
					if fit: app.board.fit_all()
					else: app.board.working_size()
					await process_frame
					var record: Dictionary = V1.layout(app,check)
					var measured: Dictionary = Measurements.capture(app.board)
					check(measured.clipped_glyphs == 0 and measured.glyph_collisions == 0,"V1 focused real glyphs and C1/status bounds fit")
					var ink: Rect2 = app.board.view.bounds().grow(1)
					for axis: String in measured.glyph_extents:
						var box: Array = measured.glyph_extents[axis]
						ink = ink.merge(Rect2(box[0],box[1],box[2],box[3]))
					check(app.board.composition_envelope().grow(0.02).encloses(ink),"V1 stable envelope encloses independent actual glyph bounds")
					record.actual_ink = Measurements.rect_values(ink)
					record.clipped = measured.clipped_glyphs
					record.collisions = measured.glyph_collisions
					focused.append(record)
					if (not corpus or index == 8) and not fit: stable_input()
					if u == 1.0 and mode == 0 and (not corpus or index in [3,7,8]):
						await shot("v1-%s-%s" % [app.session.definition.id,"fit" if fit else "work"])

func recovery_matrix() -> void:
	app.queue_free()
	await process_frame
	app = load("res://main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	for dims: Vector2i in [Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080),Vector2i(2560,1440)]:
		canvas.size = dims
		app.size = Vector2(dims)
		for u: float in [1.0,1.25]:
			app.set_ui_scale(u)
			for index: int in [0,1,2]:
				app.select_puzzle(index)
				app._reset_selected()
				app.open_puzzle()
				check(app._save_current(),"V1 recovery initial valid save")
				app.board.eraser = not app.board.eraser
				app.store.fail_step = "after_rotation"
				check(not app._save_current() and app.work_repair_button.visible,"V1 actual interrupted write shows recovery")
				app.store.fail_step = ""
				for mode: int in range(2):
					app.set_puzzle_view(mode)
					await process_frame
					focused.append(V1.layout(app,check))
					if dims.x == 1280 and u == 1.25 and index == 1 and mode == 0:
						await shot("v1-recovery-1280-ui125")
				var p: Vector2 = app.work_repair_button.get_global_rect().get_center()
				mouse(p,MOUSE_BUTTON_LEFT,true)
				mouse(p,MOUSE_BUTTON_LEFT,false)
				check(app.repair_dialog.visible,"V1 moved recovery action real hit")
				app.repair_dialog.confirmed.emit()
				app.repair_dialog.hide()
				check(not app.work_repair_button.visible and app.store.load_slot(app.session.definition).status == "loaded","V1 confirmed recovery restores valid saving")

func glyph_probe() -> void:
	app.queue_free()
	await process_frame
	var data: Dictionary = Definition.load_fixture("f02").duplicate(true)
	data.width = 40
	data.height = 5
	data.solution = []
	for lengths: Array in [[1],[11],[17],[40],[1,11,17]]:
		var row: Array = []
		for length: int in lengths:
			for i: int in range(length): row.append(2)
			if row.size() < 40: row.append(0)
		while row.size() < 40: row.append(0)
		data.solution.append(row)
	data.rows = []
	data.columns = []
	for row: Array in data.solution: data.rows.append(Definition.hints(row))
	for x: int in range(40): data.columns.append(Definition.hints(Definition.column(data.solution,x)))
	var b = GlyphBoard.new()
	b.session = Session.new(data)
	b.book_layout = true
	b.size = Vector2(1200,500)
	canvas.size = Vector2i(1200,500)
	canvas.add_child(b)
	for u: float in [1.0,1.25]:
		b.ui_scale = u
		b.working_size()
		for status: int in range(3):
			b.probe_status = status
			b.queue_redraw()
			await process_frame
			await RenderingServer.frame_post_draw
			var measurement: Dictionary = Measurements.capture(b)
			check(measurement.clipped_glyphs == 0 and measurement.glyph_collisions == 0,"V1 real 1/11/17/40 C1/AA and three drawn status bounds")
			check(b.clue_font_size() == (19 if u == 1.0 else 20),"V1 glyph proof cannot shrink font")
			var crop: Rect2i = Rect2i(b.row_clue_area().grow(3))
			var name: String = "v1-glyphs-u%d-status%d.png" % [roundi(u*100),status]
			check(canvas.get_texture().get_image().get_region(crop).save_png(output.path_join(name)) == OK,"V1 native 1:1 glyph strip")
			glyphs.append({"file":name,"sha256":FileAccess.get_sha256(output.path_join(name)),"ui_scale":u,"font_px":b.clue_font_size(),"status":status,"row_pitch":24*u,"clipped":measurement.clipped_glyphs,"collisions":measurement.glyph_collisions})
	b.queue_free()
	await process_frame
	# Continuous boundaries/intervals on BOTH axes of the current renderer.
	for transpose: bool in [false,true]:
		var board = load("res://ui/full_view_board.gd").new()
		board.session = Session.new(Drag.fixture(Definition.load_fixture("f01"),25,true,transpose))
		board.book_layout = true
		board.size = Vector2(780,620)
		canvas.add_child(board)
		for u: float in [1.0,1.25]:
			board.ui_scale = u
			board.working_size()
			var before: Rect2 = board.view.bounds()
			Drag.drag_probe(board,check)
			check(board.view.bounds() == before,"V1 continuous hint reading cannot move grid")
		board.queue_free()
		await process_frame

func run() -> void:
	output = OS.get_environment("VS2_V1_CAPTURE_DIR")
	if output.is_empty() or DisplayServer.get_name() == "headless": quit(2); return
	Store.test_root_override = OS.get_user_data_dir().path_join("v1-focused")
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920,1080)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	await focused_scene(false)
	await focused_scene(true)
	await recovery_matrix()
	await glyph_probe()
	FileAccess.open(output.path_join("v1-focused.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"failures":failures,"records":focused,"pictures":pictures,"glyphs":glyphs},"\t")+"\n")
	print("VS2_V1_","OK" if failures == 0 else "FAILED"," checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
