extends SceneTree
## Runs from source AND as an external script against the downloaded PCK.
const Store = preload("res://model/save_store.gd")
const Miniature = preload("res://ui/miniature.gd")
var geometry: Script
var app: Control
var canvas: SubViewport
var output: String
var checks: int = 0
var failures: int = 0
var pictures: Array = []
var scenarios: Array = []

class Lines extends Control:
	var lines: Array = []
	var straight: bool = false
	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO,size),Color("faf6ec"))
		for line: Dictionary in lines:
			var p: PackedVector2Array = line.points
			if straight: p = PackedVector2Array([p[0],p[-1]])
			draw_polyline(p,line.color,line.width,true)

func _initialize() -> void:
	geometry = load(get_script().resource_path.get_base_dir().path_join("vs2_v2_cases.gd"))
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("VS2_V2_FAIL: ",label)

func frame() -> Image:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	return canvas.get_texture().get_image()

func mini_image() -> Image:
	var image: Image = await frame()
	return image.get_region(Rect2i(app.mini.get_global_rect()))

func mouse(cell: Vector2i, button: MouseButton, down: bool) -> void:
	var p: Vector2 = app.board.global_position+app.board.view.cell_rect(cell).get_center()
	motion(cell)
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	canvas.push_input(event,true)

func motion(cell: Vector2i) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = app.board.global_position+app.board.view.cell_rect(cell).get_center()
	canvas.push_input(event,true)

func click(cell: Vector2i, button: MouseButton) -> void:
	mouse(cell,button,true)
	mouse(cell,button,false)

func projection(label: String, cell: Vector2i, expected: int) -> void:
	check(app.mini.cells == app.session.visible_cells(),label+" full unfiltered input")
	check(app.mini.cells[cell.y*app.mini.width+cell.x] == expected,label+" exact visible state")
	var image: Image = await mini_image()
	var step: float = app.mini.image_rect().size.x/app.mini.width
	var p: Vector2i = Vector2i((Vector2(cell)+Vector2(0.5,0.5))*step)
	var color: Color = Color("faf6ec") if expected <= 0 else Color(app.session.definition.palette[expected-1].color)
	check(image.get_pixelv(p).is_equal_approx(color),label+" immediate original-color/neutral pixels")
	scenarios.append(label)

func save_image(name: String, image: Image) -> void:
	var path: String = output.path_join(name+".png")
	check(image.save_png(path)==OK,"V2 image saved")
	pictures.append({"file":name+".png","sha256":FileAccess.get_sha256(path)})

func equal_projection() -> void:
	app.hide()
	var mini = Miniature.new()
	mini.size = Vector2(240,120)
	mini.width = 8
	mini.height = 4
	mini.palette = app.session.definition.palette
	mini.style_identity = "fixed-projection-fixture"
	mini.cells.resize(32)
	mini.cells.fill(-1)
	for i: int in range(mini.palette.size()): mini.cells[9+i] = i+1
	canvas.add_child(mini)
	var original: Array = mini.cells.duplicate()
	var first: Image = (await frame()).get_region(Rect2i(0,0,240,120))
	for i: int in range(32):
		if mini.cells[i] == -1 and i%2==0: mini.cells[i] = 0
	var with_x: Array = mini.cells.duplicate()
	mini.queue_redraw()
	var second: Image = (await frame()).get_region(Rect2i(0,0,240,120))
	check(first.get_data()==second.get_data(),"NA05 equal fill pixels despite distinct X/unknown")
	check(mini.cells==with_x and with_x!=original,"NA05 renderer preserves X input")
	for i: int in range(mini.palette.size()):
		check(first.get_pixel(45+i*30,45).is_equal_approx(Color(mini.palette[i].color)),"NA05 positive original color prevents empty-image false pass")
	var bad: Image = second.duplicate()
	bad.set_pixel(15,15,Color("827765"))
	check(first.get_data()!=bad.get_data(),"negative reintroduced X/dot rejected")
	bad = second.duplicate()
	bad.set_pixel(45,45,Color("faf6ec"))
	check(first.get_data()!=bad.get_data(),"negative corrected/hidden own fill rejected")
	save_image("v2-projection-"+str(mini.palette.size()),first)
	mini.queue_free()
	await process_frame
	app.show()

func gestures() -> void:
	app.select_puzzle(1)
	app._reset_selected()
	app.open_puzzle()
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	var cell: Vector2i = Vector2i(2,2)
	click(cell,MOUSE_BUTTON_RIGHT)
	await projection("committed X remains neutral",cell,0)
	var snapshot: Array = app.session.player.cells.duplicate()
	mouse(cell,MOUSE_BUTTON_LEFT,true)
	await projection("X to fill preview",cell,1)
	check(app.session.player.cells==snapshot,"preview leaves confirmed X unchanged")
	motion(Vector2i(5,2))
	await projection("extended fill preview",Vector2i(5,2),1)
	motion(cell)
	await projection("elastic retraction",Vector2i(5,2),-1)
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	canvas.push_input(escape,true)
	mouse(cell,MOUSE_BUTTON_LEFT,false)
	await projection("Escape restores X",cell,0)
	for reason: String in ["focus","opposite"]:
		mouse(cell,MOUSE_BUTTON_LEFT,true)
		if reason == "focus": app.board.notification(Control.NOTIFICATION_APPLICATION_FOCUS_OUT)
		else: mouse(cell,MOUSE_BUTTON_RIGHT,true)
		mouse(cell,MOUSE_BUTTON_LEFT,false)
		mouse(cell,MOUSE_BUTTON_RIGHT,false)
		await projection(reason+" restores X",cell,0)
	click(cell,MOUSE_BUTTON_LEFT)
	await projection("fill commit immediate during animation",cell,1)
	mouse(cell,MOUSE_BUTTON_RIGHT,true)
	await projection("fill to X preview removes fill",cell,0)
	app._cancel_interaction()
	mouse(cell,MOUSE_BUTTON_RIGHT,false)
	await projection("abort restores fill",cell,1)
	mouse(cell,MOUSE_BUTTON_LEFT,true)
	await projection("neutral preview removes fill",cell,-1)
	mouse(cell,MOUSE_BUTTON_LEFT,false)
	await projection("neutral commit",cell,-1)
	app._undo()
	await projection("undo restores fill",cell,1)
	app._redo()
	await projection("redo restores neutral",cell,-1)
	for i: int in range(4):
		app.board.active_color = i+1
		click(Vector2i(i+2,4),MOUSE_BUTTON_LEFT)
		await projection("own color "+str(i+1),Vector2i(i+2,4),i+1)
	var own: Array = app.session.player.cells.duplicate()
	var wrong: bool = false
	for i: int in range(4):
		if int(app.session.definition.solution[4][i+2]) != own[4*app.session.player.width+i+2]: wrong = true
	check(wrong,"positive own wrong fill/color retained, not solution-corrected")
	check(not app.session.completed,"own wrong colors do not reveal solution")
	app.show_album()
	check(app.album_previews[1].cells==own and app.album_mini.cells==own,"both existing album paths keep own unfiltered cells")
	check(app.album_previews[1].get_script()==Miniature and app.album_mini.get_script()==Miniature,"album uses verified fill-only renderer")
	app.select_puzzle(0)
	app.select_puzzle(1)
	check(app.session.player.cells==own,"sheet change retains cells")
	app._reset_selected()
	app.open_puzzle()
	await projection("reset",cell,-1)

func grid_probe() -> void:
	app.select_puzzle(0)
	app._reset_selected()
	app.open_puzzle()
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	var original: Array = geometry.strokes(app.board)
	geometry.layout(app,check)
	click(Vector2i(4,4),MOUSE_BUTTON_LEFT)
	click(Vector2i(5,4),MOUSE_BUTTON_LEFT)
	click(Vector2i(4,5),MOUSE_BUTTON_LEFT)
	app.set_clue_completion(false)
	check(original==geometry.strokes(app.board),"progress/H1 cannot reroll ink")
	app.set_clue_completion(true)
	app.select_puzzle(1)
	app.select_puzzle(0)
	check(original==geometry.strokes(app.board),"sheet return stable ink")
	var bad: Array = original.duplicate(true)
	bad[0].width = 5.0
	check(not geometry.within_budget(bad,app.board.view.bounds()),"negative stroke/AA overshoot rejected")
	bad = original.duplicate(true)
	bad[0].points[1] += Vector2(0,0.1)
	check(bad != original,"negative rerolled geometry rejected")
	for cell: Vector2i in [Vector2i(0,0),Vector2i(4,4),Vector2i(19,19)]:
		var rect: Rect2 = app.board.view.cell_rect(cell)
		check(app.board.view.hit(rect.position+Vector2(0.01,0.01))==cell and app.board.view.hit(rect.end-Vector2(0.01,0.01))==cell,"precise regular logical cell boundaries")
	app.board.clear_pointer_hover()
	app.board.clear_effects()
	save_image("v2-mono-work",await frame())
	var box: Rect2 = app.board.view.cell_rect(Vector2i(3,3))
	box.position += app.board.global_position
	box.size = Vector2.ONE*app.board.view.cell_size*4
	save_image("v2-five-crossing",(await frame()).get_region(Rect2i(box)))
	app.hide()
	var painter = Lines.new()
	painter.size = Vector2(canvas.size)
	painter.lines = original
	canvas.add_child(painter)
	var ink: Image = await frame()
	painter.queue_redraw()
	check(ink.get_data()==(await frame()).get_data(),"native redraw pixel stability")
	painter.straight = true
	painter.queue_redraw()
	check(ink.get_data()!=(await frame()).get_data(),"native ink differs from straight reference")
	painter.queue_free()
	await process_frame
	app.show()
	app.select_puzzle(1)
	app._reset_selected()
	app.open_puzzle()
	for i: int in range(4):
		app.board.active_color = i+1
		click(Vector2i(i+3,4),MOUSE_BUTTON_LEFT)
	app.board.clear_pointer_hover()
	app.board.clear_effects()
	save_image("v2-color-work",await frame())
	save_image("v2-mini-palette",(await frame()).get_region(Rect2i(app.surface.card.merge(app.surface.palette).grow(3))))
	for u: float in [1.0,1.25]:
		app.set_ui_scale(u)
		app.board.requested_cell = 12
		app.board.overview = false
		app.board._layout()
		geometry.layout(app,check)
		app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
		geometry.layout(app,check)
	app.set_ui_scale(1.0)

func run() -> void:
	output = OS.get_environment("VS2_V2_CAPTURE_DIR")
	var stage: String = OS.get_environment("VS2_V2_STAGE")
	if output.is_empty() or DisplayServer.get_name()=="headless": quit(2); return
	Store.test_root_override = OS.get_user_data_dir().path_join("v2-projection")
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920,1080)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	app = load("res://main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	app.size = Vector2(canvas.size)
	var expected_path: String = output.path_join("v2-expected.json")
	if stage != "read":
		app.select_puzzle(0)
		await equal_projection()
		app.select_puzzle(1)
		await equal_projection()
		await gestures()
		await grid_probe()
		app.select_puzzle(0)
		app._reset_selected()
		app.open_puzzle()
		app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
		click(Vector2i(2,3),MOUSE_BUTTON_RIGHT)
		click(Vector2i(3,3),MOUSE_BUTTON_LEFT)
		click(Vector2i(4,3),MOUSE_BUTTON_RIGHT)
		app._undo()
		app.board.clear_pointer_hover()
		app.board.clear_effects()
		check(app._save_current(),"V2 real partial save with X and redo")
		var image: Image = await mini_image()
		var expected: Dictionary = {"geometry":JSON.stringify(geometry.strokes(app.board)),"mini":image.get_data().hex_encode().sha256_text(),"cells":app.session.player.cells,"history":app.session.player.history,"cursor":app.session.player.cursor}
		FileAccess.open(expected_path,FileAccess.WRITE).store_string(JSON.stringify(expected))
	else:
		check(app.album.visible,"fresh process collection start")
		app.select_puzzle(0)
		app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
		var expected: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(expected_path))
		check(JSON.stringify(geometry.strokes(app.board))==expected.geometry,"fresh process same stable stroke geometry")
		check((await mini_image()).get_data().hex_encode().sha256_text()==expected.mini,"fresh process same miniature pixels")
		check(JSON.parse_string(JSON.stringify(app.session.player.cells))==expected.cells and JSON.parse_string(JSON.stringify(app.session.player.history))==expected.history and app.session.player.cursor==expected.cursor,"saved X cells/history/redo unmodified")
		check(app.session.player.cells[3*app.session.player.width+2] == 0 and app.session.player.cursor < app.session.player.history.size(),"fresh process retains real X and pending redo")
		app._redo()
		await projection("fresh process redo restores X",Vector2i(4,3),0)
	FileAccess.open(output.path_join("v2-"+stage+".json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"failures":failures,"pictures":pictures,"scenarios":scenarios},"\t")+"\n")
	print("VS2_V2_",stage.to_upper(),"_", "OK" if failures==0 else "FAILED"," checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
