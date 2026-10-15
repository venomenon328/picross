extends SceneTree
## Same external probe runs against source and the delivered separate PCK.
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
const Store = preload("res://model/save_store.gd")
const Board = preload("res://ui/full_view_board.gd")
var checks: int = 0
var failures: int = 0
var records: Array = []
var app: Control
var output: String
var stage: String

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("HF149_FAIL: ", label)

func fixture(width: int, height: int) -> Dictionary:
	var data: Dictionary = app.sessions[0].definition.duplicate(true)
	data.width = width
	data.height = height
	data.palette = []
	for i: int in range(8):
		data.palette.append({"id": i+1, "color": ["#343f42", "#f7dc74", "#638a65", "#e9ddc3", "#9d5553", "#567f9c", "#ad7752", "#886b9d"][i]})
	data.solution = []
	data.rows = []
	data.columns = []
	for y: int in range(height):
		var row: Array = []
		for x: int in range(width):
			row.append(1+(x+y)%8)
		# Valid multi-digit row and short overlay case, alongside long axes.
		if y == 3:
			for x: int in range(width): row[x] = 1+(x/4)%8
		if y == 4:
			for x: int in range(11): row[x] = 1
		data.solution.append(row)
		data.rows.append(Definition.hints(row))
	for y: int in range(height): data.solution[y][3] = 1+(y/6)%8
	data.rows.clear()
	for row: Array in data.solution: data.rows.append(Definition.hints(row))
	for x: int in range(width): data.columns.append(Definition.hints(Definition.column(data.solution, x)))
	return data

func install(data: Dictionary) -> void:
	app.save_timer.stop()
	app.board.cancel_gesture()
	app.board.clear_pointer_hover()
	app.sessions[0] = Session.new(data)
	app.session = app.sessions[0]
	app.board.session = app.session
	app.board.row_clue_reads.clear()
	app.board.column_clue_reads.clear()
	app.slot_status[0] = "fresh"
	app.board.requested_cell = 24
	app.board.mode = "G"
	app.open_puzzle()
	app.board.restore_view(app.session.view_state)
	app._update_palette()

func anchors() -> void:
	var b: Control = app.board
	b.mode = "G"
	b.requested_cell = 12
	b.size = Vector2(500, 520)
	b._layout()
	if stage == "write":
		app.session.player.commit([{"index": 0, "before": -1, "after": 1}])
		app.session.player.commit([{"index": 1, "before": -1, "after": 0}])
		app.session.player.undo()
		for axis: String in ["row", "column"]:
			for i: int in range(3):
				var maximum: int = b.clue_layout(axis, i).max_offset
				check(maximum > 2, "narrow genuinely overflows on both axes")
				b.set_clue_step(axis, i, [0, maximum/2, maximum][i])
		var narrow: Dictionary = b.capture_view()
		for mode: String in ["G", "V", "G"]:
			b.mode = mode
			b.size = Vector2(2000, 1600)
			b._layout()
			check(b.reserve_slots == b.max_hints, "temporary full visibility")
			# A harmless no-op must not erase a latent middle/outer anchor.
			for axis: String in ["row", "column"]: b.set_clue_step(axis, 2, 0)
			check(b.capture_view().row_clue_reads == narrow.row_clue_reads and b.capture_view().column_clue_reads == narrow.column_clue_reads, "full display retains intent")
		var snapshot: Dictionary = Store.snapshot(app.session, b.capture_view())
		check(Store.validate(snapshot, app.session.definition).is_empty(), "full snapshot validates schema/history/redo")
		var store: Store = Store.new(output.path_join("roundtrip-saves"))
		check(store.write_slot(app.session,b.capture_view()).is_empty(), "normal writer saves during full visibility")
		FileAccess.open(output.path_join("hf-narrow.json"), FileAccess.WRITE).store_string(JSON.stringify(narrow))
	else:
		var store: Store = Store.new(output.path_join("roundtrip-saves"))
		var loaded: Dictionary = store.load_slot(app.session.definition)
		check(loaded.status == "loaded", "fresh process uses normal slot reader")
		var snapshot: Dictionary = loaded.data
		check(Store.validate(snapshot, app.session.definition).is_empty(), "fresh process validates entire save")
		Store.apply(snapshot,app.session)
		b.restore_view(snapshot.view)
		b.size = Vector2(500, 520)
		b._layout()
		var narrow: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(output.path_join("hf-narrow.json")))
		check(JSON.stringify(b.capture_view().row_clue_reads) == JSON.stringify(narrow.row_clue_reads) and JSON.stringify(b.capture_view().column_clue_reads) == JSON.stringify(narrow.column_clue_reads), "fresh process restores semantic windows")
		for axis: String in ["row", "column"]:
			for i: int in range(3):
				var layout: Dictionary = b.clue_layout(axis, i)
				check(layout.offset == [0, layout.max_offset/2, layout.max_offset][i], "fresh process same narrowed offset")
		check(app.session.player.redo() and app.session.player.cells[1] == 0, "fresh process real redo")
	check(b.requested_cell == 12, "valid zoom wish preserved")

func geometry() -> void:
	var b: Control = app.board
	for dimensions: Vector2i in [Vector2i(30,35), Vector2i(50,50)]:
		install(fixture(dimensions.x, dimensions.y))
		for u: float in [1.0, 1.25]:
			b.ui_scale = u
			b.requested_cell = 12
			b.size = Vector2(1800, 1500)
			b._layout()
			var pitch: Vector2 = b.slot_pitch
			var minimum: Vector2i = b.minimum_slots
			for axis: int in range(2):
				for added: int in [0,1,2,b.max_hints[axis]-minimum[axis]-1,b.max_hints[axis]-minimum[axis],b.max_hints[axis]-minimum[axis]+1]:
					for delta: float in [-0.01, 0.0, 0.01]:
						b.size = Vector2(1800, 1500)
						b.size[axis] = dimensions[axis]*12 + minimum[axis]*pitch[axis] + 14 + added*pitch[axis] + delta
						b._layout()
						var budgets: Vector2 = b.size - Vector2(dimensions)*b.view.cell_size - Vector2(b.minimum_slots)*b.slot_pitch - Vector2.ONE*14
						for k: int in range(2):
							var expected: int = mini(b.max_hints[k],b.minimum_slots[k]+maxi(0,floori((budgets[k]+0.000001)/b.slot_pitch[k])))
							check(b.reserve_slots[k] == expected, "maximal independent slot capacity")
						check(b.view.cell_size >= 11.99 and b.view.cell_size <= 12, "capacity never reduces chosen cell")
						check(Rect2(Vector2.ZERO,b.size).grow(0.02).encloses(b.composition_envelope()), "real composed envelope stays inside budget")
						for cell: Vector2i in [Vector2i.ZERO, Vector2i(dimensions.x-1,0), Vector2i(0,dimensions.y-1), dimensions-Vector2i.ONE]:
							check(b.view.hit(b.view.cell_rect(cell).get_center()) == cell, "all four corners hit")
						records.append({"kind":"slots", "axis":axis, "delta":delta, "size":[b.size.x,b.size.y], "dimensions":[dimensions.x,dimensions.y], "cell":b.view.cell_size, "ui":u, "pitch":[b.slot_pitch.x,b.slot_pitch.y], "minimum":[b.minimum_slots.x,b.minimum_slots.y], "reserve":[b.reserve_slots.x,b.reserve_slots.y], "demand":[b.max_hints.x,b.max_hints.y]})

func captures() -> void:
	var b: Control = app.board
	for config: Vector3 in [Vector3(1280,720,1.25),Vector3(1920,1080,1),Vector3(2560,1440,1.25)]:
		root.size = Vector2i(config.x, config.y)
		app.set_ui_scale(config.z)
		install(fixture(50,50))
		for zoom: int in [20,72]:
			b.requested_cell = zoom
			app._layout_book()
			await process_frame
			await process_frame
			for axis: String in ["row", "column"]:
				var index: int = 0
				if b.clue_layout(axis,index).max_offset == 0:
					var point: Vector2 = Vector2(b.row_clue_area().get_center().x,b.view.origin.y+b.view.cell_size/2) if axis == "row" else Vector2(b.view.origin.x+b.view.cell_size/2,b.column_clue_area().get_center().y)
					b.update_clue_hover(point)
					check(b.clue_hover_axis.is_empty(), "complete native line has no overlay or marker")
					records.append({"kind":"complete", "client":[root.size.x,root.size.y], "ui":config.z, "zoom":zoom, "axis":axis})
					continue
				for i: int in range(6):
					var cell: Vector2i = Vector2i(i,0) if axis == "row" else Vector2i(0,i)
					app.session.player.cells[cell.y*50+cell.x] = app.session.definition.solution[cell.y][cell.x]
				b.sync_clue_completion(app.session.visible_cells())
				var statuses: Array = b.completion_states(axis,index)
				check(statuses.has(0) and statuses.has(1) and statuses.has(2), "all three actual states in overlay")
				var source: Vector2 = Vector2(b.row_clue_area().get_center().x,b.view.origin.y+b.view.cell_size/2) if axis == "row" else Vector2(b.view.origin.x+b.view.cell_size/2,b.column_clue_area().get_center().y)
				root.warp_mouse(b.global_position+source)
				b.update_clue_hover(source)
				b.queue_redraw()
				await process_frame
				await process_frame
				await RenderingServer.frame_post_draw
				var g: Dictionary = b.tooltip_geometry()
				check(Rect2(Vector2.ZERO,b.size).encloses(g.rect), "overlay remains inside actual protected board")
				check(g.title_size < g.font_size, "heading visibly smaller")
				for box: Rect2 in g.boxes:
					check(not box.intersects(g.title_box) and box.position.y >= g.title_box.end.y+9*config.z, "measured heading/number gap")
					check(Rect2(Vector2.ONE*g.padding,g.rect.size-Vector2.ONE*2*g.padding).grow(0.01).encloses(box), "all ink/contour/status inside safe padding")
				var image: Image = root.get_texture().get_image()
				var name: String = "hf-%d-%d-%s-z%d" % [config.x,roundi(config.z*100),axis,zoom]
				var global_box: Rect2 = Rect2(b.global_position+g.rect.position,g.rect.size).grow(3)
				image.get_region(Rect2i(global_box)).save_png(output.path_join(name+".png"))
				if zoom == 72: image.save_png(output.path_join(name+"-scene.png"))
				var entries: Array = b.tooltip_entries(axis,index)
				var token_boxes: Array = []
				for box: Rect2 in g.boxes: token_boxes.append([box.position.x,box.position.y,box.size.x,box.size.y])
				records.append({"kind":"overlay", "file":name+".png", "client":[root.size.x,root.size.y], "ui":config.z, "zoom":zoom, "axis":axis, "rows":g.rows, "font":b.clue_font().get_font_name(), "heading":b.ClueOverlay.title_font().get_font_name(), "fs":g.font_size, "title_fs":g.title_size, "rect":[g.rect.position.x,g.rect.position.y,g.rect.size.x,g.rect.size.y], "title_box":[g.title_box.position.x,g.title_box.position.y,g.title_box.size.x,g.title_box.size.y], "boxes":token_boxes, "tokens":entries.map(func(e:Dictionary)->String:return e.text), "statuses":statuses})
				var before: int = app.session.player.cursor
				var click: InputEventMouseButton = InputEventMouseButton.new()
				click.position = g.rect.get_center()
				click.button_index = MOUSE_BUTTON_LEFT
				click.pressed = true
				b._gui_input(click)
				check(app.session.player.cursor == before and not app.session.gesture.active and b.clue_tooltip_rect == Rect2(), "visible overlay click consumes action and clears hit box")
		# One-line overlay uses a short, actually overflowing row at the fit ceiling.
		check(b.column_hint_overflows(3), "single-line native source genuinely overflows")
		var single_source: Vector2 = Vector2(b.view.origin.x+3.5*b.view.cell_size,b.column_clue_area().get_center().y)
		root.warp_mouse(b.global_position+single_source)
		b.update_clue_hover(single_source)
		check(b.tooltip_geometry().rows == 1, "short overlay uses one content-sized line")
		b.queue_redraw()
		await process_frame
		await RenderingServer.frame_post_draw
		var g: Dictionary = b.tooltip_geometry()
		root.get_texture().get_image().get_region(Rect2i(Rect2(b.global_position+g.rect.position,g.rect.size).grow(3))).save_png(output.path_join("hf-%d-single.png" % config.x))
		# Stationary pointer no longer targets overflow after G -> V.
		var point: Vector2 = Vector2(b.row_clue_area().get_center().x,b.view.origin.y+b.view.cell_size/2)
		b.update_clue_hover(point)
		b.set_mode("V")
		check(b.clue_hover_axis.is_empty() and b.clue_tooltip_rect == Rect2(), "stationary stale hover and hit box invalidated")
		b.set_mode("G")
		var geometry_before: Rect2 = b.view.bounds()
		for value: int in [-1,0,1]:
			app.session.player.cells.fill(value)
			b._layout()
			check(b.view.bounds() == geometry_before, "progress never moves composition")

func run() -> void:
	output = OS.get_environment("HF149_OUTPUT")
	stage = OS.get_environment("HF149_STAGE")
	if output.is_empty(): quit(2); return
	Store.test_root_override = output.path_join("isolated-saves")
	root.size = Vector2i(1920,1080)
	app = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	install(fixture(30,35))
	if stage in ["write","read"]: anchors()
	else:
		if stage != "capture": geometry()
		await captures()
	var report: Dictionary = {"stage":stage, "checks":checks, "failures":failures, "records":records, "display":DisplayServer.get_name(), "os":OS.get_name(), "dpi":DisplayServer.screen_get_dpi(), "screen_scale":DisplayServer.screen_get_scale(), "screen":[DisplayServer.screen_get_size().x,DisplayServer.screen_get_size().y], "renderer":RenderingServer.get_video_adapter_name()}
	FileAccess.open(output.path_join("hf-"+(stage if not stage.is_empty() else "native")+".json"),FileAccess.WRITE).store_string(JSON.stringify(report))
	print("HF149_",stage.to_upper() if not stage.is_empty() else "NATIVE", "_", "OK" if failures == 0 else "FAILED", " checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
