extends SceneTree
## Also run externally against the downloaded embedded Windows PCK.
var app: Control
var errors: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	if not ok:
		errors += 1
		printerr("VS1 ROUNDTRIP FAIL: ",message)

func run() -> void:
	app = load("res://full_view_study/main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	if DisplayServer.get_name() == "headless":
		root.size = Vector2i(1920,1080)
		app.size = Vector2(1920,1080)
	app._layout_book()
	var stage: String = OS.get_environment("VS1_STAGE")
	check(app.store.root == OS.get_user_data_dir().path_join("vs1/revision-1"), "direct stable isolated root before reads")
	check(app.store.path_for("f01").is_empty(), "no normal slots")
	if stage == "write":
		app.select_puzzle(8)
		app.choose_mode("G")
		app.board.fit_all()
		await process_frame
		for cell: Vector2i in [Vector2i(0,0),Vector2i(49,29)]:
			var p: Vector2 = app.board.global_position+app.board.view.cell_rect(cell).get_center()
			var motion: InputEventMouseMotion = InputEventMouseMotion.new()
			motion.position = p
			root.push_input(motion,true)
			for down: bool in [true,false]:
				var event: InputEventMouseButton = InputEventMouseButton.new()
				event.position = p
				event.button_index = MOUSE_BUTTON_LEFT
				event.pressed = down
				root.push_input(event,true)
		check(app.session.player.cells[0] == 1 and app.session.player.cells[1499] == 1 and app.session.player.cursor == 2, "real mouse edits in rectangular export")
		check(app._save_current(), "export writes")
	else:
		check(stage == "read", "known stage")
		check(app.session.definition.id == "VS09" and app.board.mode == "G", "restart selection and mode")
		check(app.session.player.cells[0] == 1 and app.session.player.cells[1499] == 1 and app.session.player.cursor == 2, "restart exact cells/history")
	var info: Dictionary = {"stage":stage,"os":OS.get_name(),"version":OS.get_version(),"screen":str(DisplayServer.screen_get_size()),"usable":str(DisplayServer.screen_get_usable_rect()),"normal_client":str(root.size),"dpi":DisplayServer.screen_get_dpi(),"windows_scale":DisplayServer.screen_get_scale(),"ui_scale":app.ui_scale,"root":app.store.root,"failures":errors}
	if DisplayServer.get_name() != "headless":
		root.mode = Window.MODE_MAXIMIZED
		await create_timer(0.5).timeout
		info.maximized_client = str(root.size)
		info.geometry = app.board.measurements()
	var output: String = OS.get_environment("VS1_PROBE_OUTPUT")
	if not output.is_empty():
		if DisplayServer.get_name() != "headless":
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(output.path_join("vs1-export-%s.png" % stage))
		FileAccess.open(output.path_join("vs1-export-%s.json" % stage),FileAccess.WRITE).store_string(JSON.stringify(info,"\t"))
	print("VS1_ROUNDTRIP_",stage.to_upper(),"_", "OK" if errors == 0 else "FAILED", " ",JSON.stringify(info))
	quit(0 if errors == 0 else 1)
