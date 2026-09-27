extends SceneTree
## Runs unchanged against the bound pre-Z2 regular P1 source, in its own profile.
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
var surface: SubViewport

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	SaveStore.test_root_override = "user://z2-before-%d" % Time.get_ticks_usec()
	var output: String = OS.get_environment("P1_CAPTURE_DIR")
	surface = SubViewport.new()
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	var app: Main = Main.new()
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
	var records: Array = []
	for spec: Array in [[1,1920,1080,1.0,18,"f02-1920"],[1,2560,1440,1.0,18,"f02-2560"],[0,2560,1440,1.0,24,"f01-2560"],[2,1920,1080,1.0,24,"f03-1920"],[1,1280,720,1.25,22,"f02-1280"]]:
		surface.size = Vector2i(spec[1],spec[2])
		app.size = Vector2(surface.size)
		app.set_ui_scale(spec[3])
		app.select_puzzle(spec[0])
		await process_frame
		await process_frame
		app.board.view.zoom_to(spec[4],app.board.view.viewport.get_center())
		app.board.overview = false
		app.board.normalize_clue_steps()
		app.board.view.center = Vector2(53.5,49) if spec[0] == 2 else app.board.view.viewport.size/(2*float(spec[4]))
		app.board.view.reframe()
		app.refresh()
		await process_frame
		await RenderingServer.frame_post_draw
		surface.get_texture().get_image().save_png(output.path_join("z2-before-"+spec[5]+".png"))
		records.append({"file":"z2-before-"+spec[5]+".png","size":[spec[1],spec[2]],"ui_scale":spec[3],"cell":spec[4],"demo":"z1-demo-1"})
	var report: FileAccess = FileAccess.open(output.path_join("z2-before.json"),FileAccess.WRITE)
	report.store_string(JSON.stringify(records,"\t"))
	print("Z2_BEFORE_OK")
	quit()
