extends SceneTree
## Real main-scene event routes and original pixels; also runs externally on PCK.
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
const Store = preload("res://model/save_store.gd")
var app: Control
var output: String
var checks: int = 0
var failures: int = 0
var records: Array = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("HN192_FAIL: ", label)

func settle() -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw

func motion(p: Vector2, mask: int = 0) -> void:
	var e := InputEventMouseMotion.new()
	e.position = p
	e.button_mask = mask
	root.push_input(e, true)

func mouse(p: Vector2, down: bool, button: MouseButton = MOUSE_BUTTON_LEFT, mask: int = -1) -> void:
	var e := InputEventMouseButton.new()
	e.position = p
	e.button_index = button
	e.pressed = down
	e.button_mask = (MOUSE_BUTTON_MASK_LEFT if button == MOUSE_BUTTON_LEFT else MOUSE_BUTTON_MASK_RIGHT) if down else 0
	if mask >= 0: e.button_mask = mask
	root.push_input(e, true)

func source(axis: String, index: int) -> Vector2:
	var b: Control = app.board
	var area: Rect2 = b.row_clue_area() if axis == "row" else b.column_clue_area()
	var c: Vector2 = b.view.cell_rect(Vector2i(index,index)).get_center()
	return b.global_position + (Vector2(area.get_center().x,c.y) if axis == "row" else Vector2(c.x,area.get_center().y))

func fixture(mono: bool) -> Dictionary:
	var data: Dictionary = app.session.definition.duplicate(true)
	data.width = 50
	data.height = 50
	data.palette = [{"id":1,"color":"#343f42"}] if mono else [{"id":1,"color":"#343f42"},{"id":2,"color":"#f7dc74"}]
	data.solution = []
	data.rows = []
	data.columns = []
	for y: int in range(50):
		var row: Array = []
		for x: int in range(50): row.append((x+y)%2 if mono else 1+(x+y)%2)
		if y == 48: row.fill(0)
		if y == 49: row.fill(1)
		data.solution.append(row)
		data.rows.append(Definition.hints(row))
	for x: int in range(50): data.columns.append(Definition.hints(Definition.column(data.solution,x)))
	return data

func install(mono: bool = false) -> void:
	app.save_timer.stop()
	app.board.cancel_gesture()
	app.board.clear_pointer_hover()
	app.board.cell_buttons_blocked = false
	app.sessions[0] = Session.new(fixture(mono))
	app.session = app.sessions[0]
	app.board.session = app.session
	app.board.row_clue_reads.clear()
	app.board.column_clue_reads.clear()
	app.slot_status[0] = "fresh"
	app.board.mode = "G"
	app.board.requested_cell = 72
	app.open_puzzle()
	app.board.restore_view(app.session.view_state)
	app.board.requested_cell = 72
	app._layout_book()

func invariant(before: Dictionary, label: String) -> void:
	var now: Dictionary = Store.snapshot(app.session,app.board.capture_view())
	# Only confirmed clue reads may differ. All model/history/view fields remain.
	now.view.row_clue_reads = before.view.row_clue_reads
	now.view.column_clue_reads = before.view.column_clue_reads
	check(now == before, label)
	check(not app.session.gesture.active and app.board.preview.is_empty() and app.board.gesture_length() == 0, label+" no cell preview/counter")

func routes() -> void:
	var b: Control = app.board
	# Explicit component boundary for both mono and colour; actual shared layout.
	b.size = Vector2(500,520)
	b._layout()
	var before: Dictionary = Store.snapshot(app.session,b.capture_view())
	for axis: String in ["row","column"]:
		var p: Vector2 = source(axis,2)
		var middle_before: Dictionary = b.capture_view()
		motion(p)
		mouse(p,true,MOUSE_BUTTON_MIDDLE, MOUSE_BUTTON_MASK_MIDDLE)
		motion(p+Vector2(30,30),MOUSE_BUTTON_MASK_MIDDLE)
		mouse(p,false,MOUSE_BUTTON_MIDDLE)
		check(b.pan_button == MOUSE_BUTTON_NONE and b.capture_view() == middle_before, "A01 middle never navigates "+axis)
		var maximum: int = b.clue_layout(axis,2).max_offset
		check(maximum > 2, "A01 genuine overflow "+axis)
		for sign_value: int in [1,-1]:
			b.set_clue_step(axis,2,0 if sign_value == 1 else maximum)
			var anchor: Dictionary = b.capture_view()
			motion(p)
			mouse(p,true)
			var pitch: float = b.clue_layout(axis,2).slot_extent
			var delta: Vector2 = Vector2(pitch*1.51*sign_value,b.view.cell_size*3) if axis == "row" else Vector2(b.view.cell_size*3,pitch*1.51*sign_value)
			motion(p+delta,MOUSE_BUTTON_MASK_LEFT)
			check(b.pan_target == axis and b.pan_line_index == 2 and b.capture_view() == anchor, "A01 frozen continuous unsaved "+axis)
			check(b.cursor_context() == (Vector2i(-1,2) if axis == "row" else Vector2i(2,-1)), "A05 frozen source band")
			mouse(p+delta,false,MOUSE_BUTTON_RIGHT,MOUSE_BUTTON_MASK_LEFT)
			check(b.pan_button == MOUSE_BUTTON_LEFT, "A02 wrong Up cannot finish")
			var expected: int = b.closest_clue_snap(axis,2)
			var button: Control = app.actions.erase
			var tool_before: bool = b.eraser
			mouse(button.get_global_rect().get_center(),false)
			check(b.clue_step(axis,2) == expected and b.pan_button == MOUSE_BUTTON_NONE and b.eraser == tool_before, "A02 sidebar Up snaps only clue; no button")
			invariant(before,"A02 navigation leaves all other state")
	# No movement, fitting and empty starts cannot become painting on entry.
	for index: int in [2,48,49]:
		var p: Vector2 = source("row",index)
		motion(p)
		mouse(p,true)
		if index != 2: check(b.pan_button == MOUSE_BUTTON_NONE, "A01 fitting/empty no navigation")
		var grid: Vector2 = b.global_position+b.view.cell_rect(Vector2i(10,10)).get_center()
		if index != 2:
			motion(grid,MOUSE_BUTTON_MASK_LEFT)
			check(b.cursor_context() == Vector2i(10,10) and not app.session.gesture.active, "A04 fitting clue press updates orientation without painting")
		mouse(grid,false)
		invariant(before,"A02 clue click/entry cannot paint")
	for reason: String in ["escape","focus","missing","chord","repeated","releasechord","resize","ui","mode","page","session"]:
		var p: Vector2 = source("column",2)
		var confirmed: Dictionary = b.capture_view()
		motion(p)
		mouse(p,true)
		motion(p+Vector2(0,30),MOUSE_BUTTON_MASK_LEFT)
		match reason:
			"escape":
				var e := InputEventKey.new()
				e.keycode = KEY_ESCAPE
				e.pressed = true
				root.push_input(e,true)
			"focus": b.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
			"missing": motion(p+Vector2(0,50))
			"chord": mouse(p,true,MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MASK_LEFT|MOUSE_BUTTON_MASK_RIGHT)
			"repeated": mouse(p,true)
			"releasechord": mouse(p,false,MOUSE_BUTTON_LEFT,MOUSE_BUTTON_MASK_RIGHT)
			"resize":
				b.size.x -= 1
				b._layout()
			"ui": app.set_ui_scale(1.25 if b.ui_scale == 1 else 1)
			"mode": b.set_mode("V")
			"page":
				app.show_information("help")
				app.return_to_work()
			"session": b.restore_view(confirmed)
		check(b.pan_button == MOUSE_BUTTON_NONE and not b.clue_press_owned, "A03 abort ends ownership "+reason)
		check(b.capture_view().column_clue_reads == confirmed.column_clue_reads, "A03 abort keeps confirmed reads "+reason)
		mouse(p,false)
		mouse(p,false,MOUSE_BUTTON_RIGHT)
		b.set_mode("G")
		app.set_ui_scale(1)
		app._layout_book()
		b.size = Vector2(500,520)
		b._layout()
		p = source("row",2)
		motion(p)
		mouse(p,true)
		check(b.pan_button == MOUSE_BUTTON_LEFT, "A03 fresh Down usable "+reason)
		mouse(p,false)
	# A cell owns crossing into hints; normal L/R cells still commit once.
	for button: MouseButton in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT]:
		var p: Vector2 = b.global_position+b.view.cell_rect(Vector2i(10,10)).get_center()
		motion(p)
		mouse(p,true,button)
		motion(source("row",10),MOUSE_BUTTON_MASK_LEFT if button == MOUSE_BUTTON_LEFT else MOUSE_BUTTON_MASK_RIGHT)
		check(app.session.gesture.active and b.pan_button == MOUSE_BUTTON_NONE, "A02 cell owns hint crossing")
		mouse(source("row",10),false,button)
		check(app.session.player.history.size() == 1, "A02 normal cell route single commit")
		app._undo()
		app.session.player.history.clear()
		app.session.player.cursor = 0
	b.clear_effects()

func pixels(label: String, context: Vector2i, baseline: Image) -> void:
	var b: Control = app.board
	var image: Image = root.get_texture().get_image()
	var box: Rect2 = b.clue_tooltip_rect
	var marked: int = 0
	var unmarked: int = 0
	for y: int in range(50):
		for x: int in range(50):
			var p: Vector2 = b.view.cell_rect(Vector2i(x,y)).position+Vector2.ONE*b.view.cell_size*0.4
			if box.has_area() and box.grow(3).has_point(p): continue
			var pixel: Vector2i = Vector2i(b.global_position.round()+p)
			var expected: bool = x == context.x or y == context.y
			var changed: bool = image.get_pixelv(pixel) != baseline.get_pixelv(pixel)
			if expected:
				marked += 1
				check(changed,"A04 visible band "+label)
			else:
				unmarked += 1
				check(not changed,"A04 no orthogonal/phantom band "+label)
	check(marked > 0 and unmarked > 100, "A04 real exposed pixels sampled "+label)
	image.save_png(output.path_join(label+".png"))
	records.append({"kind":"pixels","file":label+".png","context":[context.x,context.y],"marked":marked,"unmarked":unmarked,"overlay":[box.position.x,box.position.y,box.size.x,box.size.y],"client":[root.size.x,root.size.y],"ui":b.ui_scale,"cell":b.view.cell_size,"board":[b.global_position.x,b.global_position.y,b.size.x,b.size.y]})

func captures() -> void:
	for config: Vector3 in [Vector3(1280,720,1.25),Vector3(1920,1080,1),Vector3(2560,1440,1.25)]:
		root.size = Vector2i(config.x,config.y)
		DisplayServer.window_set_size(root.size)
		app.set_ui_scale(config.z)
		install()
		await settle()
		var b: Control = app.board
		b.clear_pointer_hover()
		b.marks.sync_cursor()
		await settle()
		var baseline: Image = root.get_texture().get_image()
		var prefix: String = "hn-%d-ui%d" % [config.x,roundi(config.z*100)]
		for axis: String in ["row","column"]:
			motion(source(axis,2))
			await settle()
			check(b.hover == Vector2i(-1,-1) and b.clue_tooltip_rect.has_area(), "A04 hint is not editable cell; overlay open")
			pixels(prefix+"-"+axis,Vector2i(-1,2) if axis == "row" else Vector2i(2,-1),baseline)
			# The reused frame has naturally transparent outer corners. Its safe
			# paper/text interior must be fully opaque to the cursor underneath.
			var overlay: Rect2i = Rect2i(Rect2(b.global_position.round()+b.clue_tooltip_rect.position,b.clue_tooltip_rect.size).grow(-22*b.ui_scale))
			var covered: PackedByteArray = root.get_texture().get_image().get_region(overlay).get_data()
			b.marks.cursor_layer.hide()
			await settle()
			check(root.get_texture().get_image().get_region(overlay).get_data() == covered, "A05 opaque overlay paper/text hides underlying band")
			b.marks.cursor_layer.show()
			await settle()
		# Frozen drag source stays visibly marked after crossing into the grid.
		var start: Vector2 = source("row",2)
		motion(start)
		mouse(start,true)
		motion(b.global_position+b.view.cell_rect(Vector2i(12,18)).get_center(),MOUSE_BUTTON_MASK_LEFT)
		await settle()
		pixels(prefix+"-drag-row",Vector2i(-1,2),baseline)
		mouse(start,false)
		motion(source("column",2))
		await settle()
		var overlay_center: Vector2 = b.global_position+b.clue_tooltip_rect.get_center()
		var cells_before: Array = app.session.player.cells.duplicate()
		mouse(overlay_center,true)
		mouse(overlay_center,false)
		check(app.session.player.cells == cells_before and not app.session.gesture.active and b.clue_tooltip_rect == Rect2(), "A05 visible box click consumed; hit box removed")
		motion(b.global_position+b.view.cell_rect(Vector2i(2,2)).get_center())
		await settle()
		pixels(prefix+"-grid",Vector2i(2,2),baseline)
		# Pure source changes use only cursor commands and cached H1 results.
		var rest: int = b.marks.stats.rest_draws
		var searches: int = b.completion_searches
		for i: int in range(8):
			motion(source("row" if i%2 == 0 else "column",i))
			await settle()
		check(b.marks.stats.rest_draws == rest and b.completion_searches == searches, "A06 source hover no resting rebuild/H1")
		# Deliberately couple full chunk invalidation; the same counter detects it.
		for chunk: Control in b.marks.chunks: chunk.queue_redraw()
		await settle()
		check(b.marks.stats.rest_draws > rest, "A06 negative control detects full rebuild")
		records.append({"kind":"cache","client":[root.size.x,root.size.y],"rest_before":rest,"rest_after_negative":b.marks.stats.rest_draws,"searches":searches,"searches_after":b.completion_searches})
		# Complete hint still orients; mode transition refreshes stationary pointer.
		motion(source("row",49))
		check(b.cursor_context() == Vector2i(-1,49) and b.clue_hover_axis.is_empty(), "A04 complete hint single axis without overlay")
		motion(source("row",2))
		b.set_mode("V")
		await settle()
		check(b.clue_tooltip_rect == Rect2(), "A05 stationary full view removes hit box")
		b.set_mode("G")
		b.clear_pointer_hover()
		b.marks.sync_cursor()
		await settle()
		baseline = root.get_texture().get_image()
		motion(source("row",49))
		await settle()
		pixels(prefix+"-complete-row",Vector2i(-1,49),baseline)
		var size_before: Vector2 = b.size
		b.size = Vector2(100,100)
		b._layout()
		check(not b.layout_valid and b.cursor_context() == Vector2i(-1,-1) and b.clue_tooltip_rect == Rect2(), "A05 invalid layout clears bands and hit box")
		b.size = size_before
		b._layout()
		check(b.cursor_context() == Vector2i(-1,49), "A05 valid layout re-resolves stationary pointer")

func run() -> void:
	output = OS.get_environment("HN192_OUTPUT")
	if output.is_empty(): quit(2); return
	Store.test_root_override = output.path_join("isolated-saves")
	root.size = Vector2i(1920,1080)
	app = load("res://main.tscn").instantiate()
	root.add_child(app)
	await settle()
	install()
	await settle()
	routes()
	install(true)
	await settle()
	routes()
	await captures()
	FileAccess.open(output.path_join("hn-native.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"failures":failures,"records":records,"os":OS.get_name(),"display":DisplayServer.get_name(),"dpi":DisplayServer.screen_get_dpi(),"screen_scale":DisplayServer.screen_get_scale(),"screen":[DisplayServer.screen_get_size().x,DisplayServer.screen_get_size().y],"renderer":RenderingServer.get_video_adapter_name()})+"\n")
	print("HN192_NATIVE_", "OK" if failures == 0 else "FAILED", " checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
