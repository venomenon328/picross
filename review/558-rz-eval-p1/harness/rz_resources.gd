extends "E:/Zeuch/Coding/picross_codex/558-rz-eval-p1/temp/rz_probe.gd"
var memory_frames: Array = []
func observe(label: String) -> void:
	memory_frames.append({"phase":label,"book_state":book.state,"capture":book.capture != null,"active_illustration":app.rz_eval.active_texture != null,"pending":not app.rz_eval.pending_path.is_empty(),"texture_memory":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),"video_memory":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),"static_cpu_memory":OS.get_static_memory_usage()})
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
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames()
	observe("catalog-before")
	check(book.request_open("pz-20ecf7747bbf40828238ec26d1207172"),"open")
	while book.state in [book.State.PREPARING,book.State.OPENING]:
		observe("opening")
		await process_frame
	await frames()
	observe("work-settled")
	check(app.rz_eval.state == "ready","correct illustration ready")
	check(book.request_return(),"return")
	while book.state in [book.State.PREPARING,book.State.OPENING]:
		observe("returning")
		await process_frame
	await frames(15)
	observe("catalog-after")
	check(book.capture == null and app.rz_eval.active_texture == null and app.rz_eval.pending_path.is_empty(),"capture, illustration and request released")
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"frames":memory_frames,"failures":failures},"\t"))
	file.close()
	print("RZ_RESOURCES_DONE frames ",memory_frames.size()," failures ",failures.size())
	quit(0 if failures.is_empty() else 1)
