extends SceneTree
const Store = preload("res://model/save_store.gd")
var book: Node3D
var assertions: Array = []
var output: String
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	assertions.append({"label":label,"passed":ok})
	if not ok: print("HIL_REVIEW_FAIL ",label)
func frames(n: int = 6) -> void:
	for i in range(n): await process_frame
func settled() -> void:
	var deadline: int = Time.get_ticks_msec()+10000
	while (book.state in [book.State.PREPARING,book.State.OPENING] or book.release_barrier) and Time.get_ticks_msec() < deadline: await process_frame
	check(book.state not in [book.State.PREPARING,book.State.OPENING],"real movement settles")
	await frames()
func click(control: Control) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = control.get_global_rect().get_center()
	motion.global_position = motion.position
	root.push_input(motion,true)
	for down: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = motion.position
		event.global_position = motion.position
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		root.push_input(event,true)
func shot(name: String) -> void:
	await frames()
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	check(image.save_png(output.path_join(name+".png")) == OK,"native PNG "+name)
func run() -> void:
	output = OS.get_environment("HIL_REVIEW_OUTPUT")
	if output.is_empty(): quit(4); return
	Store.test_root_override = output.path_join("saves")
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	root.size = Vector2i(1920,1080)
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames()
	var app = book.app
	await frames(90)
	app.display_controller.set_process(false)
	root.mode = Window.MODE_WINDOWED
	book.information_routes.request("help")
	await settled()
	for config in [[1920,1080,1.0],[2560,1440,1.0],[1280,720,1.25]]:
		root.mode = Window.MODE_WINDOWED
		root.borderless = true
		root.size = Vector2i(config[0],config[1])
		DisplayServer.window_set_size(Vector2i(config[0],config[1]))
		book.set_ui_scale(config[2])
		await frames(10)
		var panel = app.help_panel
		click(panel.buttons[2])
		await frames()
		check(panel.chapter == 2 and panel.scroll.scroll_vertical == 0,"native chapter pointer begins operation")
		check(panel.compact == (config[0] == 1280),"actual native compact/wide mode")
		check(root.size == Vector2i(config[0],config[1]),"actual Windows client size "+str(config))
		print("LAYOUT ",root.size,config," size=",panel.size," scroll=",panel.scroll.size," compact=",panel.compact," prose=",panel.paragraph_width," bar=",panel.scroll.get_v_scroll_bar().get_combined_minimum_size()," actual=",panel.scroll.get_v_scroll_bar().size)
		var line_lengths: Array = []
		for column in panel.copy_columns:
			if not column.is_visible_in_tree(): continue
			var label: Label = column.get_child(0)
			var text := TextParagraph.new()
			text.width = label.size.x-label.get_theme_stylebox("normal").get_minimum_size().x
			text.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
			text.add_string(label.text,label.get_theme_font("font"),label.get_theme_font_size("font_size"))
			for j in range(text.get_line_count()-1):
				var span: Vector2i = text.get_line_range(j)
				line_lengths.append(span.y-span.x)
		line_lengths.sort()
		print("PROSE_FULL_LINES ",config," count=",line_lengths.size()," median=",line_lengths[line_lengths.size()/2]," range=",line_lengths[0],"-",line_lengths[-1])
		await shot(str(config[0])+"-operation")
		if config[0] == 1920:
			panel.buttons[3].grab_focus()
			var motion := InputEventMouseMotion.new()
			motion.position = panel.buttons[0].get_global_rect().get_center()
			motion.global_position = motion.position
			root.push_input(motion,true)
			await shot("1920-hover-focus")
		# Native wheel events, bounded to the longest chapter.
		for n in range(110):
			var event := InputEventMouseButton.new()
			event.position = panel.scroll.get_global_rect().get_center()
			event.global_position = event.position
			event.button_index = MOUSE_BUTTON_WHEEL_DOWN
			event.pressed = true
			root.push_input(event,true)
			event = event.duplicate()
			event.pressed = false
			root.push_input(event,true)
		await frames()
		var bar: VScrollBar = panel.scroll.get_v_scroll_bar()
		check(panel.scroll.scroll_vertical == int(bar.max_value-bar.page),"native wheel reaches long article end")
		await shot(str(config[0])+"-end")
		var offset: int = panel.scroll.scroll_vertical
		click(app.information.get_node("settings-access"))
		var deadline: int = Time.get_ticks_msec()+8000
		while book.state == book.State.PREPARING and Time.get_ticks_msec() < deadline: await process_frame
		while book.state == book.State.OPENING and book.elapsed < 0.3 and Time.get_ticks_msec() < deadline: await process_frame
		check(book.capture != null,"real help/register capture in page movement")
		if config[0] == 1920: await shot("1920-settings-pan")
		await settled()
		click(app.information.get_node("help-access"))
		await settled()
		check(panel.chapter == 2 and panel.scroll.scroll_vertical == offset,"native settings return restores chapter and exact offset")
		await shot(str(config[0])+"-return")
		click(panel.buttons[1])
		await frames()
		check(panel.chapter == 1 and panel.scroll.scroll_vertical == 0,"chapter pointer from article end starts new chapter")
		await shot(str(config[0])+"-diagram")
	# Current paper protection with a real pending save failure and retry.
	book.information_routes.request_return()
	await settled()
	check(book.state == book.State.CATALOG,"real return reaches original catalog")
	book.request_open(str(app.sessions[0].definition.id))
	await settled()
	book.information_routes.request("help")
	await settled()
	check(app.help_panel.chapter == 0 and app.info.help_scroll.scroll_vertical == 0,"new work visit resets principle")
	app.store.fail_step = "after_temp"
	app.session.player.commit([{"index":0,"before":-1,"after":1}])
	app._save_current()
	app._layout_book()
	await frames()
	await shot("1280-status-retry")
	check(app.save_retry.visible,"save retry stays reachable")
	app.store.fail_step = ""
	click(app.save_retry)
	await frames()
	book.information_routes.request_return()
	await settled()
	check(book.state == book.State.WORK,"real work visit returns to original puzzle")
	var report = {"host":OS.get_name(),"engine":Engine.get_version_info().string,"renderer":RenderingServer.get_video_adapter_name(),"assertions":assertions}
	var file := FileAccess.open(output.path_join("observations.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	var passed: bool = assertions.all(func(row: Dictionary) -> bool: return row.passed)
	print("HIL_REVIEW_OK" if passed else "HIL_REVIEW_FAILED")
	quit(0 if passed else 4)
