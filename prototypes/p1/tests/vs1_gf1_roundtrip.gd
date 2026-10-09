extends SceneTree
## External script also runs against the old and new downloaded embedded PCKs.
var app: Control
var failures: int = 0
var checks: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("VS1 GF1 ROUNDTRIP FAIL: ",message)

func snapshot() -> Dictionary:
	var state: Dictionary = {"id":app.session.definition.id,"mode":app.board.mode,"cells":app.session.player.cells,
		"history":app.session.player.history,"cursor":app.session.player.cursor,"color":app.board.active_color,
		"rows":app.board.row_clue_reads,"columns":app.board.column_clue_reads}
	# Godot parses JSON numbers as floats. Compare both process snapshots through
	# that same representation without changing the production SaveStore contract.
	return JSON.parse_string(JSON.stringify(state))

func run() -> void:
	var stage: String = OS.get_environment("VS1_GF1_STAGE")
	var output: String = OS.get_environment("VS1_PROBE_OUTPUT")
	var prefix: String = OS.get_environment("VS1_GF1_PREFIX")
	check(stage in ["write","read","old-write","old-read"] and not output.is_empty(),"bound stage and output")
	var expected_path: String = output.path_join(prefix+"-gf1-expected.json")
	root.size = Vector2i(1280,720)
	app = load("res://full_view_study/main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	app.size = Vector2(1280,720)
	app._layout_book()
	check(app.store.root == OS.get_user_data_dir().path_join("vs1/revision-1"),"same stable default root before reads")
	if stage.ends_with("write"):
		app.select_puzzle(3) # VS04, long colored row sequences remain partial when narrow.
		app._reset_selected()
		app.set_ui_scale(1.25)
		app.choose_mode("G")
		app.open_puzzle()
		app.board.fit_all()
		app.board.active_color = 2
		await process_frame
		var rows: Array = []
		for index: int in range(app.session.definition.rows.size()): rows.append(index)
		rows.sort_custom(func(a: int,b: int)->bool:return app.session.definition.rows[a].size()>app.session.definition.rows[b].size())
		for index: int in range(3):
			var line: int = rows[index]
			check(app.board.clue_layout("row",line).max_offset>0,"narrow fixture hides part of all three rows")
			app.board.row_clue_reads[line] = [{"anchor":"grid_end"},{"anchor":"middle","start":2,"end":6},{"anchor":"outer_start"}][index]
		app.board.column_clue_reads[0] = {"anchor":"outer_start"}
		app.board.normalize_clue_steps()
		for cell: Vector2i in [Vector2i.ZERO,Vector2i(39,29)]:
			var point: Vector2 = app.board.global_position+app.board.view.cell_rect(cell).get_center()
			for down: bool in [true,false]:
				var event: InputEventMouseButton = InputEventMouseButton.new()
				event.position=point; event.button_index=MOUSE_BUTTON_LEFT; event.pressed=down
				root.push_input(event,true)
		check(app.session.player.cells[0]==2 and app.session.player.cells[1199]==2 and app.session.player.cursor==2,"real colored corner edits/history")
		var expected: Dictionary = snapshot().duplicate(true)
		if stage == "write":
			# Intentional test layout: save while every row is temporarily complete.
			# OS-client input geometry is tested independently by vs1_window.gd.
			app.board.size.x = 3000
			for mode: String in ["G","V","G"]:
				app.choose_mode(mode)
				app.board.size.x = 3000
				app.board._layout()
				check(app.board.reserve_slots.x==app.board.max_hints.x,"broad view has complete row hints")
				check(snapshot().rows==expected.rows and snapshot().columns==expected.columns,"complete G/V preserves semantic reads")
			check(snapshot()==expected,"complete view preserves exact model/color/history")
		check(app._save_current(),"save from writer process")
		FileAccess.open(expected_path,FileAccess.WRITE).store_string(JSON.stringify(expected))
	else:
		var expected: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(expected_path))
		check(snapshot()==expected,"fresh reader preserves all three anchors and exact cells/history/color")
		check(app.board.reserve_slots.x<app.board.max_hints.x,"fresh narrow reader returns to partial row hints")
		var steps: Array = app.board.row_clue_steps.duplicate()
		for mode: String in ["G","V","G"]:
			app.choose_mode(mode)
		check(snapshot()==expected and app.board.row_clue_steps==steps,"narrow G/V/G reconstructs exact semantic offsets")
		check(app.board.measurements().grid_fit,"fresh delivered reader fits entire frame")
	var evidence: Dictionary = {"stage":stage,"checks":checks,"failures":failures,"root":app.store.root,
		"cells_sha256":JSON.stringify(app.session.player.cells).sha256_text(),"history_sha256":JSON.stringify(app.session.player.history).sha256_text(),
		"reads_sha256":JSON.stringify(snapshot().rows).sha256_text(),"cursor":app.session.player.cursor,"color":app.board.active_color,
		"row_capacity":app.board.reserve_slots.x,"row_maximum":app.board.max_hints.x}
	FileAccess.open(output.path_join(prefix+"-gf1-"+stage+".json"),FileAccess.WRITE).store_string(JSON.stringify(evidence,"\t"))
	print("VS1_GF1_ROUNDTRIP_",stage.to_upper().replace("-","_"),"_","OK" if failures==0 else "FAILED"," ",JSON.stringify(evidence))
	quit(0 if failures==0 else 1)
