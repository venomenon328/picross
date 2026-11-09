extends "E:/Zeuch/Coding/picross_codex/558-rz-eval-p1/temp/rz_probe.gd"
var zoom_trace: Array = []
var performance_rows: Array = []

func disk_bytes() -> Dictionary:
	var result: Dictionary = {}
	for name: String in DirAccess.get_files_at(app.store.root):
		result[name] = FileAccess.get_file_as_bytes(app.store.root.path_join(name)).hex_encode()
	return result

func change_zoom(direction: int) -> void:
	pointer(app.actions["plus" if direction > 0 else "minus"].get_global_rect().get_center())
	await frames()
	zoom_trace.append({"mode":app.rz_eval.mode,"cell":app.board.view.cell_size,"canvas":str(app.rz_eval.canvas),"grid":str(app.rz_eval.grid),"texture_rid":str(app.rz_eval.active_texture.get_rid()) if app.rz_eval.active_texture != null else "none","load_count":app.rz_eval.load_count,"state":app.rz_eval.state})

func timed_mode(mode: int) -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	app.rz_eval.mode = mode
	app.rz_eval.queue_redraw()
	await frames(12)
	var cpu: Array[float] = []
	var gpu_monitor: Array[float] = []
	var prior: int = Time.get_ticks_usec()
	for i: int in range(90):
		await process_frame
		var now: int = Time.get_ticks_usec()
		cpu.append((now-prior)/1000.0)
		gpu_monitor.append(Performance.get_monitor(Performance.TIME_PROCESS)*1000.0)
		prior = now
	cpu.sort()
	performance_rows.append({"mode":mode,"frame_interval_ms_median":cpu[45],"frame_interval_ms_p95":cpu[85],"process_time_monitor_ms":gpu_monitor.back(),"texture_memory_monitor":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),"video_memory_monitor":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),"static_cpu_memory":OS.get_static_memory_usage(),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)})
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)

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
	await frames()
	var id: String = "pz-c71563f1b8c940de998afdd62f09"
	await open_id(id,0)
	# Real viewport events create a small arbitrary player stand, never a solution.
	var width: int = app.session.player.width
	for cell: Vector2i in [Vector2i(2,18),Vector2i(3,18),Vector2i(4,18),Vector2i(2,19)]:
		pointer(app.board.global_position+app.board.view.cell_rect(cell).get_center())
		await frames()
	pointer(app.board.global_position+app.board.view.cell_rect(Vector2i(5,18)).get_center(),MOUSE_BUTTON_RIGHT)
	await frames()
	check(app.session.player.cursor == 5,"five real pointer commits through decoration")
	var own_cells: Array = app.session.player.cells.duplicate()
	for mode: int in range(4):
		app.rz_eval.mode = mode
		app.rz_eval.queue_redraw()
		for i: int in range(20): await change_zoom(-1)
		var fixed_canvas: Rect2 = app.rz_eval.canvas
		var texture: Texture2D = app.rz_eval.active_texture
		var loads: int = app.rz_eval.load_count
		await snapshot("overlap-%d-low" % mode)
		for i: int in range(8): await change_zoom(1)
		await snapshot("overlap-%d-mid" % mode)
		for i: int in range(20): await change_zoom(1)
		await snapshot("overlap-%d-high" % mode)
		resource_record("overlap-%d-high" % mode)
		var geo: Array = geometry()
		check(app._save_current(),"flush before art-only change")
		var saved: Dictionary = disk_bytes()
		await timed_mode(mode)
		check(geo == geometry() and saved == disk_bytes(),"mode changes leave geometry and save bytes unchanged")
		for i: int in range(24): await change_zoom(-1)
		await snapshot("overlap-%d-return" % mode)
		check(app.rz_eval.canvas == fixed_canvas and app.rz_eval.active_texture == texture and app.rz_eval.load_count == loads,"actual zoom in/back preserves canvas and loaded resource")
		check(app.session.player.cells == own_cells,"zoom leaves all player cells unchanged")
	# Transparent semantic control, all modes: no texture and pixel-identical book.
	var texture: Texture2D = app.rz_eval.active_texture
	app.rz_eval.active_texture = null
	app.rz_eval.queue_redraw()
	await frames()
	var clear_bytes: PackedByteArray = surface.get_texture().get_image().get_data()
	for mode: int in range(4):
		app.rz_eval.mode = mode
		app.rz_eval.queue_redraw()
		await frames()
		check(clear_bytes == surface.get_texture().get_image().get_data(),"empty canvas mode %d visually inert" % mode)
	await snapshot("transparent-control")
	app.rz_eval.active_texture = texture
	app.rz_eval.mode = 0
	app.rz_eval.queue_redraw()
	# Representative physical render sizes, same paper logic; no OS/DPI claim.
	for entry: Array in [[Vector2i(1920,1080),1.0,"1080"],[Vector2i(1280,720),1.25,"720-ui125"],[Vector2i(3840,2160),1.0,"4k"],[Vector2i(2560,1600),1.0,"16x10"]]:
		surface.size = entry[0]
		app.set_ui_scale(entry[1])
		await frames()
		app._layout_book()
		await snapshot("reference-"+entry[2])
		resource_record("reference-"+entry[2])
	surface.size = Vector2i(2560,1440)
	app.set_ui_scale(1.0)
	await frames()
	# Current decoration participates in a real moving leaf and releases on exit.
	check(book.request_return(),"real return motion")
	while book.state == book.State.PREPARING: await process_frame
	while book.state == book.State.OPENING and book.elapsed < 0.6: await process_frame
	await snapshot("moving-return-leaf")
	await wait_motion()
	check(book.capture == null and app.rz_eval.active_texture == null,"transition releases capture and illustration")
	# Fast open/abort/next visit, no stale result, source leakage or stuck overlay.
	check(book.request_open("pz-20ecf7747bbf40828238ec26d1207172"),"rapid first request")
	book.interrupt("leave")
	await frames()
	check(book.state == book.State.CATALOG and app.rz_eval.active_texture == null,"abort returns blank catalog")
	await open_id("pz-9d08697a30c749258b742ac979de9def",1)
	await snapshot("after-rapid-abort")
	resource_record("after-rapid-abort")
	await close_id()
	var report := {"engine":Engine.get_version_info(),"renderer":RenderingServer.get_video_adapter_name(),"api":RenderingServer.get_video_adapter_api_version(),"records":records,"zoom_trace":zoom_trace,"performance":performance_rows,"failures":failures,"input_scope":"actual SubViewport pointer events in native Windows Godot on product scene; no OS mouse/DPI or exported-player claim"}
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	file.close()
	print("RZ_DIAG_DONE failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
