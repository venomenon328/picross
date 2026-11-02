extends "res://book/main.gd"
## Isolated synthetic study and native evidence only.
const StudyContent = preload("res://study/book/content.gd")

func create_content() -> Content:
	return StudyContent.new()

func _ready() -> void:
	super._ready()
	if OS.get_cmdline_user_args().has("--book-study-proof"): call_deferred("_native_proof")

func _native_proof() -> void:
	for i: int in range(6): await get_tree().process_frame
	var windows: Array = []
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	get_tree().root.size = Vector2i(1600,900)
	get_tree().root.move_to_center()
	windows.append(await _window_proof_frame("standard"))
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MAXIMIZED)
	windows.append(await _window_proof_frame("maximized"))
	var accepted: bool = request_open("T-06")
	var deadline: int = Time.get_ticks_usec()+10000000
	while state in [State.PREPARING, State.OPENING] and Time.get_ticks_usec() < deadline:
		await get_tree().process_frame
	var ok: bool = accepted and state == State.WORK and elapsed == DURATION and app.session.definition.id == "T-06"
	await RenderingServer.frame_post_draw
	ok = ok and get_viewport().get_texture().get_image().save_png(OS.get_environment("BOOK_STUDY_OUTPUT").path_join("windows-exported-work.png")) == OK
	_proof_click(app.board.global_position+app.board.view.origin+Vector2(5.5,5.5)*app.board.view.cell_size)
	for i: int in range(4): await get_tree().process_frame
	ok = ok and app.session.player.cursor == 2
	var info_routes: Array = []
	for section: String in ["settings","help"]:
		var entry: Control = app.actions["menu" if section == "settings" else "help"]
		_proof_click(entry.get_global_rect().get_center())
		await _proof_settled()
		ok = ok and state == State.INFORMATION and app.info.section == section and information_routes.origin.kind == "work"
		await _window_proof_frame("information-"+section)
		var other: String = "help" if section == "settings" else "settings"
		_proof_click(app.information.get_node(other+"-access").get_global_rect().get_center())
		await _proof_settled()
		ok = ok and state == State.INFORMATION and app.info.section == other
		var back: Control = app.actions["nav-work"] if other == "settings" else app.info.right_return
		_proof_click(back.get_global_rect().get_center())
		await _proof_settled()
		ok = ok and state == State.WORK and app.session.player.cursor == 2
		info_routes.append({"entry":section,"pan":other,"return":"work","cursor":app.session.player.cursor})
	_proof_click(app.album_button.get_global_rect().get_center())
	deadline = Time.get_ticks_usec()+10000000
	while state in [State.PREPARING,State.OPENING] and Time.get_ticks_usec() < deadline: await get_tree().process_frame
	ok = ok and state == State.CATALOG and elapsed == RETURN_DURATION and app.session.player.cursor == 2
	await RenderingServer.frame_post_draw
	ok = ok and get_viewport().get_texture().get_image().save_png(OS.get_environment("BOOK_STUDY_OUTPUT").path_join("windows-exported-catalog.png")) == OK
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	windows.append(await _window_proof_frame("restored"))
	ok = ok and windows[0].mode == DisplayServer.WINDOW_MODE_WINDOWED and windows[1].mode == DisplayServer.WINDOW_MODE_MAXIMIZED and windows[2].mode == DisplayServer.WINDOW_MODE_WINDOWED
	ok = ok and windows[0].client == windows[2].client and windows[0].framebuffer == windows[2].framebuffer
	var file := FileAccess.open(OS.get_environment("BOOK_STUDY_OUTPUT").path_join("windows-native.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":ok,"windows":windows,"information_routes":info_routes,"id":selected_id,"cursor":app.session.player.cursor,"engine":Engine.get_version_info(),"os":OS.get_version(),"adapter":RenderingServer.get_video_adapter_name()},"\t")+"\n")
	file.close()
	print("BOOK_PACK_MOTION_OK" if ok else "BOOK_PACK_MOTION_FAIL", " return=", elapsed, " cursor=",app.session.player.cursor," id=", selected_id)
	get_tree().quit(0 if ok else 4)

func _proof_settled() -> void:
	var deadline: int = Time.get_ticks_usec()+10000000
	while (state in [State.PREPARING,State.OPENING] or release_barrier) and Time.get_ticks_usec() < deadline: await get_tree().process_frame
	for i: int in range(3): await get_tree().process_frame

func _window_proof_frame(label: String) -> Dictionary:
	for i: int in range(8): await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image: Image = get_viewport().get_texture().get_image()
	image.save_png(OS.get_environment("BOOK_STUDY_OUTPUT").path_join("windows-"+label+".png"))
	var desktop: Vector2i = DisplayServer.screen_get_size()
	var client: Vector2i = DisplayServer.window_get_size()
	var outer: Vector2i = DisplayServer.window_get_size_with_decorations()
	return {"stage":label,"mode":DisplayServer.window_get_mode(),"desktop":[desktop.x,desktop.y],"client":[client.x,client.y],"outer":[outer.x,outer.y],"framebuffer":[image.get_width(),image.get_height()],
		"position":DisplayServer.window_get_position(),"usable":DisplayServer.screen_get_usable_rect(),"os_scale":DisplayServer.screen_get_scale(),"dpi":DisplayServer.screen_get_dpi(),"ui_scale":app.ui_scale,
		"paper":projected_paper(false,-1),"left_footer":app.album.previous_button.get_global_rect(),"right_footer":app.album.next_button.get_global_rect()}

func _proof_click(point: Vector2) -> void:
	for pressed: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		get_viewport().push_input(event,true)

func resource_report() -> Dictionary:
	var pixels: int = get_viewport().size.x*get_viewport().size.y
	return {"viewport":get_viewport().size,"page_vertices":1105,"page_triangles":2048,"moving_leaves":OPENING_LEAVES,
		"visible_leaves":leaves.filter(func(sheet: MeshInstance3D) -> bool: return sheet.visible).size(),
		"animation_seconds":DURATION,"page_seconds":PAGE_DURATION,"motion_wall_seconds":motion_wall_seconds,"preparation_seconds":preparation_seconds,
		"return_seconds":RETURN_DURATION,"organic_paper_rgba_bytes":1254*1254*4,"organic_paper_with_mipmaps_upper_bytes":1254*1254*4*4/3,
		"ui_capture_targets":1 if capture != null else 0,"catalog_rgba_textures":1 if catalog_texture != null else 0,
		"information_snapshots":information_routes.textures.size(),"information_visit":not information_routes.origin.is_empty(),
		"peak_color_target_and_snapshot_bytes":pixels*16,"peak_capture_depth_upper_bound_bytes":pixels*4,
		"binding":binding.report(),
		"shared_original_a_rgba_bytes":2560*1440*4,
		"shared_resources_excluded_from_estimate":"font atlases, six cell atlases, SL frames, main framebuffer, driver overhead"}
