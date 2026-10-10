extends SceneTree
## External developer probe also runs against the downloaded regular PCK.
const Store = preload("res://model/save_store.gd")
var app: Control
var stage: String
var output: String
var failures: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		printerr("VS2_ROUNDTRIP_FAIL: ",label)

func run() -> void:
	stage = OS.get_environment("VS2_STAGE")
	output = OS.get_environment("VS2_PROBE_OUTPUT")
	if output.is_empty() or not stage in ["legacy-write","legacy-read","write","read"]:
		quit(2)
		return
	# CI uses a dedicated slot root; downloaded-player probes deliberately
	# leave this unset to exercise the actual isolated user profile.
	if not OS.get_environment("P1_TEST_SAVE_ROOT").is_empty():
		Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	root.size = Vector2i(1920,1080)
	app = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	if not OS.get_environment("P1_TEST_SAVE_ROOT").is_empty():
		check(app.store.root == OS.get_environment("P1_TEST_SAVE_ROOT"), "explicit CI slot isolation")
	check(app.album.visible and not app.work.visible and not app.ending.visible,"restart always collection, including partial/completed")
	var prefix: String = "legacy" if stage.begins_with("legacy") else "new"
	var expected_path: String = output.path_join(prefix+"-expected.json")
	var records: Array = []
	if stage.ends_with("write"):
		for index: int in range(9):
			app.select_puzzle(index)
			app._reset_selected()
			app.open_puzzle()
			var player = app.session.player
			check(player.commit([{"index":0,"before":-1,"after":1}]),"write first action")
			check(player.commit([{"index":1,"before":-1,"after":0}]) and player.undo(),"write real redo branch")
			if index == 3 or (index == 0 and OS.get_environment("VS2_COMPLETE_FIRST") == "1"):
				var changes: Array = []
				for y: int in range(player.height):
					for x: int in range(player.width):
						var i: int = y*player.width+x
						var value: int = app.session.definition.solution[y][x]
						if value != player.cells[i]: changes.append({"index":i,"before":player.cells[i],"after":value})
				player.commit(changes)
				app.session.completed = app.session.is_solution()
			app.board.active_color = app.session.definition.palette.size()
			if stage == "legacy-write":
				app.board.overview = false
				app.board.view.zoom_to(72,app.board.view.viewport.get_center())
				app.board.view.center = Vector2(1,1)
				app.board.view.reframe()
				app.set_tool("hand" if index % 2 == 0 else "erase")
			else:
				app.board.requested_cell = 72
				app.board.overview = false
				app.board._layout()
				app.set_tool("fill" if index % 2 == 0 else "erase")
			for axis: String in ["row","column"]:
				for i: int in range(3):
					var maximum: int = app.board.clue_layout(axis,i).max_offset
					app.board.set_clue_step(axis,i,[0,maximum/2,maximum][i])
			check(app._save_current(),"normal schema-1 writer")
			records.append(app.store.load_slot(app.session.definition).data)
		FileAccess.open(expected_path,FileAccess.WRITE).store_string(JSON.stringify(records))
	else:
		records = JSON.parse_string(FileAccess.get_file_as_string(expected_path))
		check(app.board.mode == "G","mode is session-only default")
		for index: int in range(9):
			app.select_puzzle(index)
			var actual: Dictionary = Store.snapshot(app.session,app.board.capture_view())
			var expected: Dictionary = records[index]
			for key: String in ["cells","history","cursor","undo_used","completed"]:
				# JSON's numeric representation is double while the model stores
				# typed integers. Compare the full JSON values, not 1 versus 1.0 text.
				check(JSON.parse_string(JSON.stringify(actual[key])) == expected[key],"exact restart "+key+" slot "+str(index))
			check(not app.board.hand and actual.view.active_color == expected.view.active_color and actual.view.tool == ("fill" if expected.view.tool == "hand" else expected.view.tool),"legacy presentation normalized, color/eraser retained")
			check(actual.view.zoom == expected.view.zoom and actual.view.overview == expected.view.overview and app.board.view.cell_size <= app.board.fit_ceiling,"desired valid work step retained and fit bounded")
			check(JSON.stringify(actual.view.row_clue_reads)==JSON.stringify(expected.view.row_clue_reads) and JSON.stringify(actual.view.column_clue_reads)==JSON.stringify(expected.view.column_clue_reads),"semantic read intent retained through full visibility")
			if not app.session.completed:
				check(app.session.player.redo() and app.session.player.cells[1] == 0,"real redo retained after restart")
			else:
				check(app.ending.visible and not app.session.reveal().is_empty(),"completed opens proportional reveal only on selection")
	var resources: Array[String] = []
	collect("res://",resources)
	if OS.get_environment("VS2_PACK_AUDIT") == "1":
		check(not app.board.has_method("measurements"),"PCK excludes developer matrix diagnosis")
		for path: String in resources:
			check(not path.contains("/study/") and not path.contains("/full_view_study/") and not path.contains("/tests/") and not path.contains("Shantell") and not path.contains("Virgil"),"PCK excludes developer/study resources: "+path)
	var report: Dictionary = {"stage":stage,"failures":failures,"root":app.store.root,"app_data":OS.get_user_data_dir(),"client":[root.size.x,root.size.y],"display":DisplayServer.get_name(),"resources":resources}
	FileAccess.open(output.path_join("vs2-"+stage+".json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("VS2_ROUNDTRIP_",stage.to_upper().replace("-","_"),"_", "OK" if failures==0 else "FAILED")
	quit(0 if failures==0 else 1)

func collect(path: String, result: Array[String]) -> void:
	for file: String in DirAccess.get_files_at(path): result.append(path.path_join(file))
	for folder: String in DirAccess.get_directories_at(path):
		collect(path.path_join(folder),result)
