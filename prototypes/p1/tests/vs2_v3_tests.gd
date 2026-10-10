extends SceneTree
## Current source and external downloaded-PCK probe; no developer code exported.
const Store = preload("res://model/save_store.gd")
const Marks = preload("res://ui/pencil_marks.gd")
var app: Control
var canvas: SubViewport
var output: String
var checks: int = 0
var failures: int = 0
var records: Array = []
var pictures: Array = []
var geometry: Script

func _initialize() -> void:
	geometry = load(get_script().resource_path.get_base_dir().path_join("vs2_v2_cases.gd"))
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		if failures < 150: printerr("V3 FAIL: ",message)

func settle() -> void:
	await process_frame
	await process_frame
	await process_frame

func mouse(p: Vector2, button: MouseButton, down: bool) -> void:
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = p
	canvas.push_input(motion,true)
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	canvas.push_input(event,true)

func click(item: Control) -> void:
	var p: Vector2 = item.get_global_rect().get_center()
	mouse(p,MOUSE_BUTTON_LEFT,true)
	mouse(p,MOUSE_BUTTON_LEFT,false)

func reveal_tool(id: String) -> void:
	app.tools_scroll.ensure_control_visible(app.actions[id])
	await settle()
	check(app.tools_scroll.get_global_rect().encloses(app.actions[id].get_global_rect()),"scroll reveals full hitbox "+id)

func shot(name: String, region: Rect2 = Rect2()) -> void:
	app.board.clear_pointer_hover()
	await settle()
	await RenderingServer.frame_post_draw
	var image: Image = canvas.get_texture().get_image()
	if region.has_area(): image = image.get_region(Rect2i(region))
	var path: String = output.path_join(name+".png")
	check(image.save_png(path)==OK,"native picture saved")
	pictures.append({"file":name+".png","sha256":FileAccess.get_sha256(path)})

func title_ok() -> bool:
	return app.title.get_theme_font("font").get_font_name() == "Bakso Daging"

func layout_ok() -> bool:
	var rail: Rect2 = app.tools_scroll.get_global_rect()
	var previous: Rect2
	for id: String in app.TOOL_IDS:
		var box: Rect2 = app.actions[id].get_global_rect()
		if box.size.x < 44*app.ui_scale or box.size.y < 44*app.ui_scale: return false
		if previous.has_area() and (absf(previous.position.x-box.position.x)>0.01 or box.position.y < previous.end.y): return false
		previous = box
	if rail.intersects(app.board.get_global_rect()) or rail.position.y < app.surface.palette.end.y: return false
	return app.surface.wells.size()==1 and app.surface.wells[0].encloses(app.tools_scroll.get_rect())

func text_ok() -> bool:
	for item: Node in app.work.find_children("*","Label",true,false):
		if item.text.contains("Zoom ") or item.text.contains("Werkzeug:") or item.text.contains("Füllen · Farbe"): return false
	return not app.layout_warning.text.contains("%")

func check_layout() -> void:
	check(layout_ok(),"vertical rail, original hit sizes, no board overlap or old wells")
	if app.tools_column.size.y>app.tools_scroll.size.y:
		check(app.tools_scroll.get_v_scroll_bar().visible,"tight rail exposes scrollbar")
	else:
		check(not app.tools_scroll.get_v_scroll_bar().visible,"generous rail needs no scrollbar")
		for id: String in app.TOOL_IDS:
			check(app.tools_scroll.get_global_rect().encloses(app.actions[id].get_global_rect()),"generous rail shows every complete tool")
	check(text_ok(),"no persistent tool/zoom text")
	check(title_ok(),"work-only Bakso title")
	var title_box: Rect2 = app.title.get_global_rect()
	var font: Font = app.title.get_theme_font("font")
	var fs: int = app.title.get_theme_font_size("font_size")
	check(font.get_string_size(app.title.text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x <= title_box.size.x,"real title fits horizontally")
	check(font.get_height(fs) <= title_box.size.y,"real title fits vertically")
	for c: String in app.title.text:
		check(font.has_char(c.unicode_at(0)),"title glyph including explicit Plex middle dot "+c)
		var native_glyph: int = TextServerManager.get_primary_interface().font_get_glyph_index(font.get_rids()[0],fs,c.unicode_at(0),0)
		check(native_glyph!=0 or c=="·","only middle dot needs bundled fallback")
	var paper: Rect2 = app.surface.material_rect()
	var inner: Rect2 = Rect2(paper.position+paper.size*Vector2(0.03125,0.034),paper.size*Vector2(0.93125,0.933))
	check(inner.encloses(app.tools_scroll.get_global_rect().grow(3*app.ui_scale)),"rail contours inside paper")
	for i: int in range(3):
		var item: Control = app.actions[["help","menu","nav-information"][i]]
		var box: Rect2 = item.get_global_rect()
		var old: Vector2 = paper.position+Vector2(paper.size.x-(187.5 if paper.size.x<1700 else 150)-(2-i)*58*app.ui_scale,paper.size.y/30)
		check((box.position-old).distance_to(Vector2(-20,12)*app.ui_scale)<0.01,"navigation moves left/down against bound reference")
		check(inner.encloses(box.grow(1)) and not box.intersects(title_box) and not box.intersects(app.surface.card),"nav clear of title/mini/paper")
	for item: Control in [app.layout_warning,app.stress_label]:
		if item.is_visible_in_tree() and not item.text.is_empty():
			check(inner.encloses(item.get_global_rect()) and not item.get_global_rect().intersects(app.board.get_global_rect()),"notice outside grid and within paper")
	records.append({"id":app.session.definition.id,"client":[canvas.size.x,canvas.size.y],"ui":app.ui_scale,"mode":app.board.mode,"fit":app.board.overview,"rail":[app.tools_scroll.position.x,app.tools_scroll.position.y,app.tools_scroll.size.x,app.tools_scroll.size.y],"scroll_needed":app.tools_column.size.y>app.tools_scroll.size.y,"title":app.title.text,"font":font.get_font_name()})

func fingerprint() -> Dictionary:
	var traces: Array = []
	for i: int in range(12):
		for k: int in range(3): traces.append(Marks.fill_trace(i,k))
	return {"traces":JSON.stringify(traces).sha256_text(),"grid":JSON.stringify(geometry.strokes(app.board)).sha256_text()}

func diverse(traces: Array) -> bool:
	var unique: Dictionary = {}
	for trace: PackedVector2Array in traces: unique[str(trace)]=true
	return unique.size()>=10

func max_deviation(lines: Array) -> float:
	var result: float = 0
	for line: Dictionary in lines:
		for i: int in range(1,line.points.size()-1):
			result=maxf(result,line.points[i].distance_to(line.points[0].lerp(line.points[-1],float(i)/(line.points.size()-1))))
	return result

func run() -> void:
	output = OS.get_environment("VS2_V3_CAPTURE_DIR")
	if output.is_empty(): quit(2); return
	Store.test_root_override = output.path_join("v3-saves")
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920,1080)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	app = load("res://main.tscn").instantiate()
	canvas.add_child(app)
	await settle()
	check(not title_ok(),"collection retains Fraunces")
	var font = app.WORK_TITLE_FONT
	check(font.data.size()==128924,"embedded font byte count")
	var hash: HashingContext = HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(font.data)
	check(hash.finish().hex_encode()=="56372bf12a6e4fa47a655ff9b2c4cc73172ddd387b3a047093d3e637d081790e","exact original embedded font")
	check(not font.allow_system_fallback,"no system font dependency")
	for index: int in range(9):
		app.select_puzzle(index)
		for c: String in app.title.text:
			check(font.has_char(c.unicode_at(0)),"all nine actual title glyphs "+c)
	for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080),Vector2i(2560,1440)]:
		canvas.size = dimensions
		app.size = Vector2(dimensions)
		for u: float in [1.0,1.25]:
			app.set_ui_scale(u)
			for index: int in [0,1,7]:
				app.select_puzzle(index)
				for mode: int in [0,1]:
					app.set_puzzle_view(mode)
					for fit: bool in [false,true]:
						if fit: app.board.fit_all()
						else: app.board.working_size()
						await settle()
						check_layout()
	# Tight actual wheel route: scrolling never changes board/model, all buttons reachable.
	canvas.size = Vector2i(1280,720)
	app.size = Vector2(canvas.size)
	app.set_ui_scale(1.25)
	app.select_puzzle(1)
	app.set_puzzle_view(0)
	await settle()
	app.tools_scroll.scroll_vertical=0
	await settle()
	var hidden_clicks: Array[int] = [0]
	var track: Callable = func() -> void: hidden_clicks[0]+=1
	app.actions.work.pressed.connect(track)
	check(not app.tools_scroll.get_global_rect().intersects(app.actions.work.get_global_rect()),"last tool initially clipped")
	click(app.actions.work)
	check(hidden_clicks[0]==0,"clipped tool cannot receive click outside scroll viewport")
	app.actions.work.pressed.disconnect(track)
	var state: String = JSON.stringify(Store.snapshot(app.session,app.board.capture_view()))
	var p: Vector2 = app.tools_scroll.get_global_rect().get_center()
	for i: int in range(20):
		mouse(p,MOUSE_BUTTON_WHEEL_DOWN,true)
		mouse(p,MOUSE_BUTTON_WHEEL_DOWN,false)
	await settle()
	check(app.tools_scroll.scroll_vertical>0 and state==JSON.stringify(Store.snapshot(app.session,app.board.capture_view())),"wheel scroll isolated from board/save/cells")
	for id: String in app.TOOL_IDS:
		await reveal_tool(id)
		check(not app.actions[id].tooltip_text.is_empty(),"tooltip retained "+id)
		click(app.actions[id])
		await settle()
		check(app.board.mode=="G" and app.board.view.cell_size<=app.board.fit_ceiling,"tool preserves mode/fit "+id)
		if id in ["fill","erase"]: check(app.actions[id].selected,"real tool click "+id)
	await shot("v3-tight-rail",app.tools_scroll.get_global_rect().grow(5))
	await reveal_tool("fill")
	click(app.actions.fill)
	var cell: Vector2 = app.board.global_position+app.board.view.cell_rect(Vector2i(2,2)).get_center()
	var cursor: int = app.session.player.cursor
	mouse(cell,MOUSE_BUTTON_LEFT,true)
	mouse(cell,MOUSE_BUTTON_LEFT,false)
	check(app.session.player.cursor==cursor+1,"normal cell route outside rail")
	await reveal_tool("undo")
	click(app.actions.undo)
	check(app.session.player.cursor==cursor,"real scrolled undo")
	await reveal_tool("redo")
	click(app.actions.redo)
	check(app.session.player.cursor==cursor+1,"real scrolled redo")
	app.select_puzzle(0)
	await settle()
	cell=app.board.global_position+app.board.view.cell_rect(Vector2i(2,2)).get_center()
	var pitch: float = app.board.view.cell_size
	var scroll_before: int = app.tools_scroll.scroll_vertical
	mouse(cell,MOUSE_BUTTON_WHEEL_DOWN,true)
	mouse(cell,MOUSE_BUTTON_WHEEL_DOWN,false)
	check(app.board.view.cell_size!=pitch and app.tools_scroll.scroll_vertical==scroll_before,"wheel outside rail still zooms board")
	app.board.working_size()
	for id: String in ["help","menu","nav-information"]:
		click(app.actions[id])
		await settle()
		check(app.information.visible and not title_ok(),"navigation and information font "+id)
		click(app.actions["nav-work"])
		await settle()
		check(app.work.visible and title_ok(),"return restores work font")
	# Deliberate mutations prove new oracles reject the old/wrong arrangements.
	var original: Vector2 = app.actions.erase.position
	app.actions.erase.position.x+=44
	check(not layout_ok(),"negative: horizontal toolbar rejected")
	app.actions.erase.position=original
	var min_size: Vector2 = app.actions.fill.custom_minimum_size
	var actual_size: Vector2 = app.actions.fill.size
	app.actions.fill.custom_minimum_size=Vector2.ONE*20
	app.actions.fill.size=Vector2.ONE*20
	check(not layout_ok(),"negative: undersized tool rejected")
	app.actions.fill.custom_minimum_size=min_size
	app.actions.fill.size=actual_size
	var caption: String = app.layout_warning.text
	app.layout_warning.text="Zoom 100 %"
	check(not text_ok(),"negative: numeric zoom rejected")
	app.layout_warning.text=caption
	app.title.add_theme_font_override("font",app.TITLE_FONT)
	check(not title_ok(),"negative: wrong title font rejected")
	app._layout_book()
	canvas.size=Vector2i(1920,1080)
	app.size=Vector2(canvas.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(0)
	app.board.working_size()
	await settle()
	var before: Dictionary = fingerprint()
	app.board.queue_redraw()
	await settle()
	check(before==fingerprint(),"stable redraw")
	app.board.zoom(-1,Vector2.ZERO)
	app.board.working_size()
	check(before==fingerprint(),"stable zoom return")
	app.select_puzzle(1)
	app.select_puzzle(0)
	app.board.working_size()
	check(before==fingerprint(),"stable page return")
	var traces: Array = []
	var common: Array = []
	for i: int in range(12):
		traces.append(Marks.fill_trace(i,0))
		common.append(Marks.fill_trace(0,0))
	check(diverse(traces),"different stable neighbor textures")
	check(not diverse(common),"negative: common pattern rejected by same diversity oracle")
	var shifted: Array = []
	for i: int in range(12):
		for k: int in range(3): shifted.append(Marks.fill_trace(i+1,k))
	check(JSON.stringify(shifted).sha256_text()!=before.traces,"negative: changed seed rejected by stability fingerprint")
	var lines: Array = geometry.strokes(app.board)
	var max_delta: float = max_deviation(lines)
	check(max_delta>0.20 and max_delta<=0.2801,"V3 visible variation exceeds old maximum, still bounded")
	var old_lines: Array = lines.duplicate(true)
	for line: Dictionary in old_lines:
		for i: int in range(1,line.points.size()-1):
			var straight: Vector2 = line.points[0].lerp(line.points[-1],float(i)/(line.points.size()-1))
			line.points[i]=straight+(line.points[i]-straight)*(0.18/0.28)
	check(max_deviation(old_lines)<=0.20,"negative: old amplitude rejected by same deviation oracle")
	var wide_lines: Array = lines.duplicate(true)
	wide_lines[0].width=4.0
	check(not geometry.within_budget(wide_lines,app.board.view.bounds()),"negative: oversized stroke/AA rejected")
	geometry.layout(app,check)
	for index: int in [0,1,7]:
		app.select_puzzle(index)
		app.board.working_size()
		app.board.set_animations(false)
		# Own confirmed cells; not solution data.
		for x: int in range(3,9):
			var q: Vector2 = app.board.global_position+app.board.view.cell_rect(Vector2i(x,4)).get_center()
			if app.session.player.cells[4*app.session.player.width+x]<0:
				mouse(q,MOUSE_BUTTON_LEFT,true)
				mouse(q,MOUSE_BUTTON_LEFT,false)
		await shot("v3-F%02d-work" % (index+1))
		if index==0:
			var region: Rect2 = app.board.view.cell_rect(Vector2i(3,4))
			region.position+=app.board.global_position
			region.size=Vector2(6,2)*app.board.view.cell_size
			await shot("v3-fills-five",region.grow(3))
		if index==7: await shot("v3-title",app.title.get_global_rect())
	# Bound cross-process fingerprint: the second invocation compares the same geometry.
	app.select_puzzle(0)
	app.board.working_size()
	check(before==fingerprint(),"progress leaves same grid/texture identity")
	var path: String = output.path_join("v3-fingerprint.json")
	var compared: bool = FileAccess.file_exists(path)
	if compared:
		check(JSON.parse_string(FileAccess.get_file_as_string(path))==fingerprint(),"fresh-process geometry/texture stable")
	else: FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(fingerprint()))
	var report: Dictionary = {"checks":checks,"failures":failures,"records":records,"pictures":pictures,"fingerprint":fingerprint(),"fresh_process_compared":compared,"max_grid_deviation":max_delta}
	FileAccess.open(output.path_join("v3-report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("VS2_V3_", "OK" if failures==0 else "FAILED", " checks=",checks," failures=",failures)
	app.queue_free()
	await process_frame
	quit(0 if failures==0 else 1)
