extends SceneTree
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
var surface: SubViewport
var app: Main
var output: String
var records: Array = []
var contrast_records: Array = []
var failed: bool = false

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	SaveStore.test_root_override = "user://z2-capture-saves-%d" % Time.get_ticks_usec()
	output = OS.get_environment("P1_CAPTURE_DIR")
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	app = Main.new()
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	surface.add_child(app)
	await process_frame
	var demos: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/z2-demo.json"))
	for i: int in range(3):
		var changes: Array = []
		var cells: Array = demos[["f01","f02","f03"][i]]
		for index: int in range(cells.size()):
			if int(cells[index]) != -1:
				changes.append({"index":index,"before":-1,"after":int(cells[index])})
		app.sessions[i].player.commit(changes)
	for spec: Array in [[1,1920,1080,1.0,18,"f02-1920"],[1,2560,1440,1.0,18,"f02-2560"],[0,2560,1440,1.0,24,"f01-2560"],[2,1920,1080,1.0,24,"f03-1920"],[1,1280,720,1.25,22,"f02-1280"]]:
		surface.size = Vector2i(spec[1],spec[2])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[3])
		app.select_puzzle(spec[0])
		app.board.view.zoom_to(spec[4],app.board.view.viewport.get_center())
		app.board.overview = false
		app.board.normalize_clue_steps()
		if spec[0] == 2:
			app.board.view.center = Vector2(53.5,49)
		else:
			app.board.view.center = app.board.view.viewport.size/(2*float(spec[4]))
		app.board.view.reframe()
		app._save_current()
		await shot(spec[5])
		if spec[5] == "f02-1920":
			await detail_shots()
		if spec[5] == "f02-1920" or spec[5] == "f02-1280":
			app.show_information("settings")
			await shot(spec[5]+"-information")
			app.show_information("help")
			await shot(spec[5]+"-help")
			app.return_to_work()
	# Native contextual recovery and existing completion/album, no new content.
	surface.size = Vector2i(1920,1080)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	app.select_puzzle(1)
	app._save_current()
	app.board.zoom(1,app.board.view.viewport.get_center())
	app.store.fail_step = "after_rotation"
	app.show_information("settings")
	await shot("recovery-blocked")
	app._ask_repair()
	await shot("recovery-confirmation")
	app.repair_dialog.hide()
	app.store.fail_step = ""
	app._repair_selected()
	app.select_puzzle(0)
	# Real gestures commit the remaining correct cells, triggering normal completion.
	app.board.fit_all()
	for y: int in range(20):
		for x: int in range(20):
			var desired: int = int(app.session.definition.solution[y][x])
			var current: int = app.session.player.cells[y*20+x]
			if desired > 0 and current != desired or desired == 0 and current > 0:
				var point: Vector2 = app.board.view.cell_rect(Vector2i(x,y)).get_center()
				app.board.pointer_press(point,MOUSE_BUTTON_LEFT if desired > 0 else MOUSE_BUTTON_RIGHT)
				app.board.pointer_release(point,true)
	if not app.session.completed:
		push_error("Z2 actual completion failed")
		failed = true
	await shot("completion")
	app.show_album()
	await shot("album-completed")
	var report: FileAccess = FileAccess.open(output.path_join("z2-renders.json"),FileAccess.WRITE)
	report.store_string(JSON.stringify({"captures":records,"normal_text_contrasts":contrast_records,"body_font":app.BODY_FONT.get_font_name(),"title_font":app.TITLE_FONT.get_font_name(),"c1_outer_radius_px":0.25,"reference_outer_radius_px":0.275},"\t"))
	if not failed:
		print("Z2_CAPTURE_OK")
	quit(5 if failed else 0)

func shot(name: String) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	picture.save_png(output.path_join("z2-"+name+".png"))
	if name == "f02-1280":
		picture.get_region(Rect2i(90,102,850,180)).save_png(output.path_join("z2-detail-clues-ui125-1to1.png"))
		picture.get_region(Rect2i(245,608,590,65)).save_png(output.path_join("z2-detail-tools-ui125-1to1.png"))
	var grid: Rect2 = app.board.view.visible_bounds()
	var reference: Dictionary = {"f02-1920":Rect2(510,252,720,720),"f02-2560":Rect2(830,432,720,720),"f01-2560":Rect2(970,470,480,480),"f03-1920":Rect2(310,270,1368,672),"f02-1280":Rect2(300,222,638,374)}
	if reference.has(name):
		var actual: Rect2 = Rect2(grid.position+app.board.position,grid.size)
		if not actual.is_equal_approx(reference[name]):
			push_error("Z2 reference geometry: %s actual=%s expected=%s" % [name,actual,reference[name]])
			failed = true
	records.append({"file":"z2-"+name+".png","size":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,"grid":[grid.position.x+app.board.position.x,grid.position.y+app.board.position.y,grid.size.x,grid.size.y],"cell":app.board.view.cell_size,"visible_cells":[grid.size.x/app.board.view.cell_size,grid.size.y/app.board.view.cell_size],"information":app.information.visible})
	await contrast_check(name,picture)

func detail_shots() -> void:
	var image: Image = surface.get_texture().get_image()
	for entry: Array in [["clues",Rect2i(300,125,935,190)],["tools",Rect2i(295,970,480,60)],["palette",Rect2i(1395,452,125,125)],["fold",Rect2i(1770,0,150,1080)]]:
		image.get_region(entry[1]).save_png(output.path_join("z2-detail-"+entry[0]+"-1to1.png"))
	app.board.set_clue_hover("row",11)
	await shot("c1-tooltip")
	var tooltip_state: Dictionary = SaveStore.snapshot(app.session,app.board.capture_view())
	var tooltip_click: InputEventMouseButton = InputEventMouseButton.new()
	tooltip_click.position = app.board.global_position+app.board.clue_tooltip_rect.get_center()
	tooltip_click.button_index = MOUSE_BUTTON_LEFT
	tooltip_click.pressed = true
	surface.push_input(tooltip_click,true)
	tooltip_click = tooltip_click.duplicate()
	tooltip_click.pressed = false
	surface.push_input(tooltip_click,true)
	if SaveStore.snapshot(app.session,app.board.capture_view()) != tooltip_state or app.session.gesture.active:
		push_error("Z2 rendered tooltip allowed a board action")
		failed = true
	app.board.clear_clue_hover()
	var area: Rect2 = app.board.row_clue_area()
	var point: Vector2 = Vector2(area.end.x-10,app.board.view.cell_rect(Vector2i(0,11)).get_center().y)
	var press: InputEventMouseButton = InputEventMouseButton.new()
	press.position = app.board.global_position+point
	press.button_index = MOUSE_BUTTON_MIDDLE
	press.pressed = true
	surface.push_input(press,true)
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = press.position+Vector2(14.7,0)
	motion.relative = Vector2(14.7,0)
	motion.button_mask = MOUSE_BUTTON_MASK_MIDDLE
	surface.push_input(motion,true)
	await shot("c1-drag")
	app.board.cancel_gesture()
	app.board.clear_pointer_hover()
	var hover: InputEventMouseMotion = InputEventMouseMotion.new()
	hover.position = app.actions.fill.get_global_rect().get_center()
	surface.push_input(hover,true)
	await create_timer(0.8).timeout
	await shot("tool-hover")
	hover.position = Vector2(5,5)
	surface.push_input(hover,true)

func text_controls(node: Node, result: Array) -> void:
	if (node is Label or node is BaseButton) and node.is_visible_in_tree() and not node.text.is_empty():
		result.append(node)
	for child: Node in node.get_children(true):
		text_controls(child,result)

static func luminance(color: Color) -> float:
	var linear: Color = color.srgb_to_linear()
	return linear.r*0.2126+linear.g*0.7152+linear.b*0.0722

func contrast_check(name: String, rendered: Image) -> void:
	var controls: Array = []
	text_controls(app.page,controls)
	if app.repair_dialog.visible:
		text_controls(app.repair_dialog,controls)
	var colors: Array = []
	for item: Control in controls:
		colors.append(item.get_theme_color("font_color"))
		for key: String in ["font_color","font_focus_color","font_hover_color","font_pressed_color","font_hover_pressed_color","font_disabled_color"]:
			item.add_theme_color_override(key,Color.TRANSPARENT)
	await process_frame
	await RenderingServer.frame_post_draw
	var background: Image = surface.get_texture().get_image()
	for i: int in range(controls.size()):
		var item: Control = controls[i]
		var ink: Color = colors[i]
		for key: String in ["font_color","font_focus_color","font_hover_color","font_pressed_color","font_hover_pressed_color","font_disabled_color"]:
			item.remove_theme_color_override(key)
		item.add_theme_color_override("font_color",ink)
		var global_box: Rect2 = item.get_global_rect()
		if app.repair_dialog.is_ancestor_of(item):
			global_box.position += Vector2(app.repair_dialog.position)
		var rect: Rect2i = Rect2i(global_box).intersection(Rect2i(Vector2i.ZERO,rendered.get_size()))
		var minimum: float = 100.0
		var count: int = 0
		for y: int in range(rect.position.y,rect.end.y):
			for x: int in range(rect.position.x,rect.end.x):
				var pixel: Color = rendered.get_pixel(x,y)
				var paper: Color = background.get_pixel(x,y)
				if absf(pixel.r-ink.r)+absf(pixel.g-ink.g)+absf(pixel.b-ink.b) < 0.03 and pixel != paper:
					var light: float = luminance(paper)
					var dark: float = luminance(ink)
					minimum = minf(minimum,(maxf(light,dark)+0.05)/(minf(light,dark)+0.05))
					count += 1
		if count > 0:
			contrast_records.append({"capture":name,"text":item.text,"opaque_glyph_pixels":count,"minimum":minimum})
			if minimum < 4.5:
				push_error("Z2 normal text contrast %.2f: %s / %s" % [minimum,name,item.text])
				failed = true
