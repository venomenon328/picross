extends SceneTree
const Main = preload("res://book/main.gd")
const Drawing = preload("res://book/rz_eval.gd")
var surface: SubViewport
var book: Node3D
var app: Control
var output: String
var records: Array = []
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")

func frames(count: int = 3) -> void:
	for i: int in range(count): await process_frame
	await RenderingServer.frame_post_draw

func check(value: bool, message: String) -> void:
	if not value:
		failures.append(message)
		print("RZ_FAIL ",message)

func snapshot(label: String) -> void:
	await frames()
	var file: String = output.path_join(label+".png")
	check(surface.get_texture().get_image().save_png(file) == OK,"save "+label)
	print("RZ_SHOT ",label)

func wait_motion() -> void:
	var deadline: int = Time.get_ticks_msec()+12000
	while book.state in [book.State.PREPARING,book.State.OPENING] and Time.get_ticks_msec() < deadline:
		await process_frame
	await frames()
	check(book.state not in [book.State.PREPARING,book.State.OPENING],"motion completes")

func geometry() -> Array:
	return [app.board.get_rect(),app.board.view.bounds(),app.board.row_clue_area(),app.board.column_clue_area(),app.tools_scroll.get_rect(),app.title.get_rect()]

func resource_record(label: String) -> void:
	var drawing: Control = app.rz_eval
	var texture: Texture2D = drawing.active_texture
	var image: Image = texture.get_image() if texture != null else null
	records.append({"label":label,"id":drawing.active_id,"state":drawing.state,"paper":str(book.projected_paper(true)),"canvas":str(drawing.canvas),"grid":str(drawing.grid),"clues":str(drawing.clue_areas),"protected":str(drawing.protected_areas),"load_ms":drawing.last_load_ms,"loads":drawing.load_count,"stale":drawing.stale_count,"dimensions":str(texture.get_size()) if texture != null else "none","decoded_bytes":image.get_data_size() if image != null else 0,"mipmaps":image.has_mipmaps() if image != null else false,"texture_memory_monitor":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),"video_memory_monitor":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),"static_cpu_memory":OS.get_static_memory_usage(),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)})

func pointer(point: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = point
	surface.push_input(motion,true)
	for down: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = button
		event.pressed = down
		surface.push_input(event,true)

func open_id(id: String, candidate: int) -> void:
	app.rz_eval.candidate = candidate
	check(book.request_open(id),"open "+id)
	await wait_motion()
	check(app.rz_eval.active_id == id and app.rz_eval.state == "ready","loaded correct illustration for "+id)

func close_id() -> void:
	check(book.request_return(),"return")
	await wait_motion()
	check(app.rz_eval.active_texture == null,"released after return")

func run() -> void:
	output = OS.get_environment("RZ_OUTPUT")
	DirAccess.make_dir_recursive_absolute(output)
	root.size = Vector2i(1280,720)
	surface = SubViewport.new()
	surface.size = Vector2i(2560,1440)
	surface.own_world_3d = true
	surface.gui_embed_subwindows = true
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	if app.display_controller != null: app.display_controller.set_process(false)
	await frames()
	print("RZ_RENDERER ",RenderingServer.get_video_adapter_name()," / ",RenderingServer.get_video_adapter_api_version())
	var full: bool = OS.get_environment("RZ_FULL") == "1"
	var ids: Array = Drawing.PILOTS.keys()
	for id: String in ids:
		if not OS.get_environment("RZ_ONLY").is_empty() and Drawing.PILOTS[id] != OS.get_environment("RZ_ONLY"): continue
		for candidate: int in range(1,4 if full else 2):
			await open_id(id,candidate)
			var label: String = str(Drawing.PILOTS[id])+"-c%d-1440-A" % candidate
			resource_record(label)
			await snapshot(label)
			var before: Array = geometry()
			app.rz_eval.active_texture = null
			app.rz_eval.queue_redraw()
			await snapshot(label+"-without")
			check(before == geometry(),"unchanged functional geometry with/without")
			await close_id()
			if not full: break
		if not full: break
	var report := {"engine":Engine.get_version_info(),"renderer":RenderingServer.get_video_adapter_name(),"api":RenderingServer.get_video_adapter_api_version(),"native_windows":OS.get_name(),"window_pixels":str(root.size),"records":records,"failures":failures}
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	file.close()
	print("RZ_DONE ",records.size()," failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
