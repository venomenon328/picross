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
var frame_evidence: Array = []

func frame_bindings_ok() -> bool:
	for item: Dictionary in app.surface.frame_metadata.derivatives:
		var kind: String = item.file.trim_prefix("frame-").trim_suffix(".png")
		var image: Image = app.surface.frames[kind].get_image()
		image.convert(Image.FORMAT_RGBA8)
		var hash: HashingContext = HashingContext.new()
		hash.start(HashingContext.HASH_SHA256)
		var bytes: PackedByteArray = image.get_data()
		for i: int in range(0,bytes.size(),4):
			if bytes[i+3]==0:
				bytes[i]=0
				bytes[i+1]=0
				bytes[i+2]=0
		hash.update(bytes)
		var digest: String = hash.finish().hex_encode()
		if digest!=item.rgba_sha256:
			return false
		var safe: Rect2i = Rect2i(ceili(item.safe[0]),ceili(item.safe[1]),floori(item.safe[2])-1,floori(item.safe[3])-1)
		if not image.get_region(safe).is_invisible(): return false
	return true

func frame_geometry_ok() -> bool:
	var boxes: Array[Rect2] = [app.surface.card,app.surface.palette,app.surface.wells[0]]
	var paper: Rect2 = app.surface.material_rect()
	var inner: Rect2 = Rect2(paper.position+paper.size*Vector2(0.03125,0.034),paper.size*Vector2(0.93125,0.933))
	for i: int in range(3):
		if not inner.encloses(boxes[i]) or boxes[i].intersects(app.board.get_global_rect()):
			print("FRAME bounds ",canvas.size," u",app.ui_scale," ",i," ",boxes[i]," inner",inner)
			return false
		if absf(boxes[i].get_center().x-boxes[0].get_center().x)>0.05:
			print("FRAME axis ",canvas.size," u",app.ui_scale," ",boxes)
			return false
		for j: int in range(i+1,3):
			if boxes[i].intersects(boxes[j]):
				return false
		for node: Control in [app.coordinate,app.title,app.work_repair_button,app.layout_warning,app.stress_label]:
			if node.is_visible_in_tree() and boxes[i].intersects(node.get_global_rect()):
				print("FRAME content ",canvas.size," u",app.ui_scale," ",i," ",node.name," ",node.get_global_rect()," box",boxes[i])
				return false
	if app.surface.mouse_filter!=Control.MOUSE_FILTER_IGNORE or app.mini.draw_frame: print("FRAME interaction")
	return app.surface.mouse_filter==Control.MOUSE_FILTER_IGNORE and not app.mini.draw_frame

func frame_pixels() -> void:
	check(frame_bindings_ok(),"SL actual texture RGBA hashes and transparent safe interiors")
	await shot("v3-sidebar-detail",Rect2(app.surface.card.position,Vector2(app.surface.card.size.x,app.surface.wells[0].end.y-app.surface.card.position.y)).grow(2))
	var original: Dictionary = app.surface.frames.duplicate()
	await RenderingServer.frame_post_draw
	var before: Image = canvas.get_texture().get_image()
	var blank: Image = Image.create(4,4,false,Image.FORMAT_RGBA8)
	for kind: String in original: app.surface.frames[kind]=ImageTexture.create_from_image(blank)
	check(not frame_bindings_ok(),"negative: missing/substituted frame rejected")
	app.surface.queue_redraw()
	await settle()
	await RenderingServer.frame_post_draw
	var after: Image = canvas.get_texture().get_image()
	for box: Rect2 in [app.surface.card,app.surface.palette,app.surface.wells[0]]:
		var changed: int = 0
		for y: int in range(ceili(box.position.y),floori(box.end.y)):
			for x: int in range(ceili(box.position.x),floori(box.end.x)):
				if before.get_pixel(x,y)!=after.get_pixel(x,y): changed+=1
		check(changed>100,"SL frame has actual native rendered pixels")
		frame_evidence.append({"rect":[box.position.x,box.position.y,box.size.x,box.size.y],"changed_pixels":changed})
	for kind: String in original: app.surface.frames[kind]=original[kind]
	app.surface.queue_redraw()
	await settle()

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
	if app.TOOL_IDS != ["fill","erase","undo","redo","minus","plus"]: return false
	if app.actions.has("fit") or app.actions.has("work"): return false
	for i: int in range(app.TOOL_IDS.size()):
		var box: Rect2 = app.actions[app.TOOL_IDS[i]].get_global_rect()
		if box.size.x < 44*app.ui_scale or box.size.y < 44*app.ui_scale: return false
		var expected: Vector2 = rail.position+Vector2(i%2,i/2)*48*app.ui_scale
		if box.position.distance_to(expected)>0.05 or not rail.grow(0.01).encloses(box): return false
	if rail.intersects(app.board.get_global_rect()) or rail.position.y < app.surface.palette.end.y: return false
	return app.surface.wells.size()==1 and app.surface.wells[0].encloses(rail)

func text_ok() -> bool:
	for item: Node in app.work.find_children("*","Label",true,false):
		if item.text.contains("Dein Stand") or item.text.contains("Zoom ") or item.text.contains("Werkzeug:") or item.text.contains("Füllen · Farbe"): return false
	return not app.layout_warning.text.contains("%")

func check_layout() -> void:
	check(layout_ok(),"SL 2x3 order, original hits, no obsolete actions/overlap")
	check(frame_geometry_ok(),"SL visible alpha envelopes centered, paper/content/recovery clear")
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
		check(inner.encloses(box.grow(1)) and not box.intersects(title_box) and not box.intersects(app.surface.card),"nav clear of title/mini/paper %s u%s box%s mini%s" % [canvas.size,app.ui_scale,box,app.surface.card])
	for item: Control in [app.layout_warning,app.stress_label]:
		if item.is_visible_in_tree() and not item.text.is_empty():
			check(inner.encloses(item.get_global_rect()) and not item.get_global_rect().intersects(app.board.get_global_rect()),"notice outside grid and within paper")
	records.append({"id":app.session.definition.id,"client":[canvas.size.x,canvas.size.y],"ui":app.ui_scale,"mode":app.board.mode,"fit":app.board.requested_cell==72,"rail":[app.tools_scroll.position.x,app.tools_scroll.position.y,app.tools_scroll.size.x,app.tools_scroll.size.y],"scroll_needed":app.tools_column.size.y>app.tools_scroll.size.y,"title":app.title.text,"font":font.get_font_name()})

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
						if fit: app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
						else: app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
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
	check(app.tools_scroll.get_global_rect().encloses(app.actions.plus.get_global_rect()),"SL sixth tool visible without scrolling")
	var state: String = JSON.stringify(Store.snapshot(app.session,app.board.capture_view()))
	var p: Vector2 = app.tools_scroll.get_global_rect().get_center()
	for i: int in range(20):
		mouse(p,MOUSE_BUTTON_WHEEL_DOWN,true)
		mouse(p,MOUSE_BUTTON_WHEEL_DOWN,false)
	await settle()
	check(app.tools_scroll.scroll_vertical==0 and state==JSON.stringify(Store.snapshot(app.session,app.board.capture_view())),"UI wheel isolated from board/save/cells")
	for id: String in app.TOOL_IDS:
		await reveal_tool(id)
		check(not app.actions[id].tooltip_text.is_empty(),"tooltip retained "+id)
		click(app.actions[id])
		await settle()
		check(app.board.mode=="G" and app.board.view.cell_size<=app.board.fit_ceiling,"tool preserves mode/fit "+id)
		if id in ["fill","erase"]: check(app.actions[id].selected,"real tool click "+id)
	await shot("v3-tight-rail",app.tools_scroll.get_global_rect().grow(5))
	await shot("v3-sl-720-125-color-G")
	await frame_pixels()
	var saved_palette: Rect2 = app.surface.palette
	app.surface.palette=app.surface.card
	check(not frame_geometry_ok(),"negative: overlaid frame rejected")
	app.surface.palette=saved_palette
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
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
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
	check(not layout_ok(),"negative: misplaced tool rejected")
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
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	await settle()
	var before: Dictionary = fingerprint()
	app.board.queue_redraw()
	await settle()
	check(before==fingerprint(),"stable redraw")
	app.board.zoom(-1,Vector2.ZERO)
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	check(before==fingerprint(),"stable zoom return")
	app.select_puzzle(1)
	app.select_puzzle(0)
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
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
		app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
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
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	check(before==fingerprint(),"progress leaves same grid/texture identity")
	# Five selected SL views supplement the three bound 1080p originals: nine
	# full views including tight normal + actual recovery, not a screenshot matrix.
	for scenario: Array in [[1280,720,1.0,0,1,"720-100-mono-V"],[1600,900,1.0,1,1,"900-100-color-V"],[1600,900,1.25,0,0,"900-125-mono-G"],[2560,1440,1.25,1,1,"1440-125-color-V"]]:
		canvas.size=Vector2i(scenario[0],scenario[1])
		app.size=Vector2(canvas.size)
		app.set_ui_scale(scenario[2])
		app.select_puzzle(scenario[3])
		app.set_puzzle_view(scenario[4])
		await settle()
		await shot("v3-sl-"+scenario[5])
	canvas.size=Vector2i(1280,720)
	app.size=Vector2(canvas.size)
	app.set_ui_scale(1.25)
	app.select_puzzle(1)
	app.set_puzzle_view(0)
	check(app._save_current(),"SL recovery initial write")
	app.store.fail_step="after_rotation"
	check(not app._save_current() and app.work_repair_button.visible,"SL actual recovery visible")
	app.store.fail_step=""
	await settle()
	check(frame_geometry_ok(),"SL recovery frame clearance")
	await shot("v3-sl-720-125-recovery")
	app.repair_dialog.confirmed.emit()
	canvas.size=Vector2i(1920,1080)
	app.size=Vector2(canvas.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(0)
	app.set_puzzle_view(0)
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	await settle()
	var path: String = output.path_join("v3-fingerprint.json")
	var compared: bool = FileAccess.file_exists(path)
	if compared:
		check(JSON.parse_string(FileAccess.get_file_as_string(path))==fingerprint(),"fresh-process geometry/texture stable")
	else: FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(fingerprint()))
	var report: Dictionary = {"checks":checks,"failures":failures,"records":records,"pictures":pictures,"fingerprint":fingerprint(),"fresh_process_compared":compared,"max_grid_deviation":max_delta,"sidebar_assets":app.surface.frame_metadata,"frame_pixels":frame_evidence}
	FileAccess.open(output.path_join("v3-report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("VS2_V3_", "OK" if failures==0 else "FAILED", " checks=",checks," failures=",failures)
	app.queue_free()
	await process_frame
	quit(0 if failures==0 else 1)
