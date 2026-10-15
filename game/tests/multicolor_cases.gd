extends RefCounted
const Definition = preload("res://model/definition.gd")
const Registry = preload("res://model/content_registry.gd")
const Session = preload("res://model/session.gd")
const Store = preload("res://model/save_store.gd")
const Main = preload("res://ui/main.gd")

static func pattern(count: int) -> Dictionary:
	var data: Dictionary = Definition.load_fixture("t02").duplicate(true)
	data.width = 10
	data.height = 8
	data.palette = []
	var colors: Array[String] = ["d52b2b","2858b8","218121","e5aa21","912191","218181","c86521","654321","c82165"]
	for i: int in range(count):
		data.palette.append({"id":i+1,"color":colors[i],"symbol":String.chr(65+i)})
	data.solution = []
	data.rows = []
	data.columns = []
	for y: int in range(data.height):
		var row: Array = []
		for x: int in range(data.width): row.append((x+y)%count+1)
		data.solution.append(row)
		data.rows.append(Definition.hints(row))
	for x: int in range(data.width): data.columns.append(Definition.hints(Definition.column(data.solution,x)))
	return data

static func run(t: SceneTree) -> void:
	t.check(Definition.validate(pattern(9)) == "Zu viele Vordergrundfarben.","nine foreground colors rejected")
	# Exercise the production-ID reveal branch without adding permanent fixtures.
	var cached: Dictionary = Registry.cached.duplicate(true)
	var production: Dictionary = pattern(8)
	production.id = "pz-test-eight-colors"
	production.reveal.definition_id = production.id
	var entry: Dictionary = Registry.by_key("t02")
	entry.id = production.id
	entry.key = production.id
	Registry.cached.entries.append(entry)
	t.check(Definition.validate(production).is_empty(),"production definition accepts eight colors")
	Registry.cached = cached
	var old_root: String = Store.test_root_override
	var configurations: Array = [[Vector2i(1280,720),1.25],[Vector2i(1920,1080),1.0],[Vector2i(2560,1440),1.25]]
	for count: int in [5,8]:
		for configuration: Array in configurations:
			Store.test_root_override = old_root+"-colors-%d-%d" % [count,int(configuration[0].x)]
			t.root.size = configuration[0]
			var app: Main = load("res://main.tscn").instantiate()
			t.root.add_child(app)
			await t.process_frame
			app.sessions[1] = Session.new(pattern(count))
			app.select_puzzle(1)
			app.open_puzzle()
			app.size = Vector2(configuration[0])
			app.set_ui_scale(configuration[1])
			await t.process_frame
			await t.process_frame
			t.check(Definition.validate(app.session.definition).is_empty(),"synthetic multicolor definition valid")
			t.check(app.palette_row.get_child_count()==count,"all palette buttons created")
			t.check(app.palette_row.size.is_equal_approx(Vector2(206,98)*app.ui_scale),"extra colors retain two-row vertical budget")
			t.check(not app.palette_row.get_global_rect().intersects(app.tools_scroll.get_global_rect()),"palette and tools do not overlap")
			t.check(app.tools_scroll.get_global_rect().end.y<=float(configuration[0].y)-28,"tools stay above footer")
			var ink: Rect2 = app.board.composition_envelope()
			ink.position += app.board.global_position
			t.check(not ink.intersects(app.surface.palette),"expanded palette frame clears board composition")
			var point: Vector2 = app.board.get_global_transform()*app.board.view.cell_rect(Vector2i.ZERO).get_center()
			for i: int in range(count):
				var item: Control = app.palette_row.get_child(i)
				t.check(app.palette_row.get_global_rect().encloses(item.get_global_rect()),"palette hit target contained")
				var palette_point: Vector2 = item.get_global_rect().get_center()
				t.mouse_motion(palette_point,false)
				t.mouse_button(palette_point,true)
				t.mouse_button(palette_point,false)
				t.check(app.board.active_color==i+1 and not app.board.eraser,"real pointer selects extra color")
				t.mouse_motion(point,false)
				t.mouse_button(point,true)
				t.mouse_button(point,false)
				t.check(app.session.player.cells[0]==i+1,"real pointer fills every supported color")
				t.check(app.board.cell_color(i+1).is_equal_approx(Color(app.session.definition.palette[i].color)),"cell color lookup includes extra IDs")
				t.check(app.board.clue_color({"length":1,"color":i+1}).is_equal_approx(Color(app.session.definition.palette[i].color)),"clues retain extra colors")
				var snapshot: Dictionary = Store.snapshot(app.session,app.board.capture_view())
				t.check(Store.validate(snapshot,app.session.definition).is_empty(),"save/history supports extra colors")
				var revised: Dictionary = app.session.definition.duplicate(true)
				revised.revision += 1
				t.check(Store.validate(snapshot,revised)=="Definition oder Revision passt nicht.","old revision is rejected rather than misapplied")
				t.mouse_button(point,true)
				t.mouse_button(point,false)
				t.check(app.session.player.cells[0]==-1,"real pointer neutralizes every supported color")
			app.queue_free()
			await t.process_frame
	Store.test_root_override = old_root
	t.root.size = Vector2i(1280,720)
