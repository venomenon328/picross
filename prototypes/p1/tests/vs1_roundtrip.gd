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
	var legacy: bool = stage.begins_with("legacy-")
	var vertical: bool = stage.begins_with("v-")
	var color: int = 2 if legacy or vertical else 1
	if stage.ends_with("write"):
		app.select_puzzle(9 if legacy or vertical else 8)
		app._reset_selected()
		app.choose_mode("V" if vertical else "G")
		app.board.active_color = color
		app.open_puzzle()
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
		check(app.session.player.cells[0] == color and app.session.player.cells[1499] == color and app.session.player.cursor == 2, "real mouse edits in rectangular export")
		if legacy or vertical:
			app.board.row_clue_reads[0] = {"anchor":"middle","start":2,"end":6}
			app.board.column_clue_reads[0] = {"anchor":"outer_start"}
			app.board.normalize_clue_steps()
		check(app._save_current(), "export writes")
	else:
		check(stage in ["read","legacy-read","v-read"], "known stage")
		check(app.session.definition.id == ("VS10" if legacy or vertical else "VS09") and app.board.mode == ("V" if vertical else "G"), "restart selection and mode")
		check(app.session.player.cells[0] == color and app.session.player.cells[1499] == color and app.session.player.cursor == 2, "restart exact cells/history")
		check(app.board.active_color == color and not app.board.hand and app.board.view.center == Vector2(25,15), "restart normalizes hand/pan and preserves color")
		if legacy or vertical:
			var read: Dictionary = app.board.row_clue_reads[0]
			check(read.get("anchor") == "middle" and int(read.get("start",-1)) == 2 and int(read.get("end",-1)) == 6 and app.board.column_clue_reads[0].get("anchor") == "outer_start", "restart preserves semantic reads including JSON numeric roundtrip")
		check(app.board.view.cell_size <= app.board.fit_ceiling and app.board.view.viewport.grow(0.01).encloses(app.board.view.bounds()), "restart full grid within hard fit ceiling")
	var info: Dictionary = {"stage":stage,"os":OS.get_name(),"version":OS.get_version(),"screen":str(DisplayServer.screen_get_size()),"usable":str(DisplayServer.screen_get_usable_rect()),"normal_client":str(root.size),"dpi":DisplayServer.screen_get_dpi(),"windows_scale":DisplayServer.screen_get_scale(),"ui_scale":app.ui_scale,"root":app.store.root,"failures":errors,"cells_sha256":JSON.stringify(app.session.player.cells).sha256_text(),"history_sha256":JSON.stringify(app.session.player.history).sha256_text(),"cursor":app.session.player.cursor,"active_color":app.board.active_color}
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
	# Inject only after native resize/capture waits; their normal deferred saves
	# must not overwrite the legacy fixture before the separate reader starts.
	if stage == "legacy-write":
		var path: String = app.store.path_for("vs10")
		var old: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
		old.view.tool = "hand"
		old.view.center = [0,0]
		old.view.zoom = 72
		old.view.overview = false
		FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(old))
		var metadata: Dictionary = {"revision":1,"selected":9,"mode":"R","requested_cell":72,"ui_scale":1.25}
		FileAccess.open(app.study_root.path_join("study-view.json"),FileAccess.WRITE).store_string(JSON.stringify(metadata))
	print("VS1_ROUNDTRIP_",stage.to_upper().replace("-","_"),"_", "OK" if errors == 0 else "FAILED", " ",JSON.stringify(info))
	quit(0 if errors == 0 else 1)
