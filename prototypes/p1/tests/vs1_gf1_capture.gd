extends "res://tests/vs1_capture.gd"
## Four comparisons fixed in gf1-plan.json; same script also runs on main baseline.

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	var variant: String = OS.get_environment("VS1_GF1_VARIANT")
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("VS1_GF1_PLAN")))
	if output.is_empty() or DisplayServer.get_name() == "headless" or not variant in ["before","after"]:
		quit(2)
		return
	OS.set_environment("VS1_TEST_ROOT", OS.get_user_data_dir().path_join("gf1-capture-"+variant))
	canvas = SubViewport.new()
	canvas.size = Vector2i(1920,1080)
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(canvas)
	app = load("res://full_view_study/main.tscn").instantiate()
	canvas.add_child(app)
	await process_frame
	for comparison: Dictionary in plan.comparisons:
		canvas.size = Vector2i(comparison.client[0],comparison.client[1])
		app.size = Vector2(canvas.size)
		app.set_ui_scale(comparison.ui_scale)
		app.select_puzzle(int(str(comparison.id).substr(2))-1)
		app.replace_with_sample()
		app.choose_mode(comparison.mode)
		app.board.fit_all()
		await process_frame
		var record: Dictionary = app.board.measurements()
		# Also measure the unchanged baseline with actual per-axis drawn numbers.
		var counts: Dictionary = {}
		for axis: String in ["row","column"]:
			var visible: int = 0
			var total: int = 0
			var lines: Array = app.session.definition.rows if axis == "row" else app.session.definition.columns
			for index: int in range(lines.size()):
				total += lines[index].size()
				if not lines[index].is_empty():
					visible += app.board.visual_hint_units(axis,index).units.filter(func(u: Dictionary) -> bool: return u.kind == "token").size()
			counts[axis] = {"visible_numbers":visible,"hidden_numbers":total-visible,"total_numbers":total}
		record.axis_counts = counts
		record.merge(comparison)
		record.own_cells_sha256 = JSON.stringify(app.session.player.cells).sha256_text()
		record.history_sha256 = JSON.stringify(app.session.player.history).sha256_text()
		records.append(record)
		await shot("gf1-%s-%s-u%d" % [variant,comparison.id,roundi(comparison.ui_scale*100)])
	FileAccess.open(output.path_join("gf1-%s.json" % variant),FileAccess.WRITE).store_string(JSON.stringify({"variant":variant,"records":records,"pictures":pictures,"failures":failures},"\t")+"\n")
	print("VS1_GF1_CAPTURE_", "OK" if failures == 0 else "FAILED", " variant=",variant," pairs=",records.size()," failures=",failures)
	quit(0 if failures == 0 else 1)
