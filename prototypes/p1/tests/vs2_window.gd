extends SceneTree
## Native OS window and downloaded PCK input/options proof, no player test route.
var app: Control
var failures: int = 0
var checks: int = 0
var records: Array = []
var output: String
var measurements: Script

func _initialize() -> void:
	measurements = load(get_script().resource_path.get_base_dir().path_join("vs2_measurements.gd"))
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("VS2_WINDOW_FAIL: ",label)

func motion(p: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = p
	root.push_input(event,true)

func mouse(p: Vector2, button: MouseButton, down: bool) -> void:
	motion(p)
	app.board.clear_clue_hover()
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = p
	event.button_index = button
	event.pressed = down
	root.push_input(event,true)

func click(control: Control) -> void:
	var p: Vector2 = control.get_global_rect().get_center()
	mouse(p,MOUSE_BUTTON_LEFT,true)
	mouse(p,MOUSE_BUTTON_LEFT,false)

func run() -> void:
	output = OS.get_environment("VS2_PROBE_OUTPUT")
	check(DisplayServer.get_name() != "headless","actual native OS window")
	app = load("res://main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	await process_frame
	check(app.album.visible and not app.work.visible,"regular PCK starts in collection")
	app.show_information("settings")
	check(app.information.visible and app.information_origin == "album" and not app.work.visible,"PCK options from collection")
	app.view_choice.item_selected.emit(1)
	check(app.board.mode == "V","PCK named option V")
	click(app.actions["nav-work"])
	check(app.album.visible,"PCK actual back button returns to collection")
	for window_mode: int in [Window.MODE_WINDOWED,Window.MODE_MAXIMIZED]:
		root.mode = window_mode
		await create_timer(0.3).timeout
		for ui: float in [1.0,1.25]:
			app.set_ui_scale(ui)
			for index: int in [0,1,2,6,8]:
				app.select_puzzle(index)
				app._reset_selected()
				app.open_puzzle()
				for mode: int in range(2):
					app.set_puzzle_view(mode)
					app.board.fit_all()
					await process_frame
					var board = app.board
					var record: Dictionary = measurements.capture(board)
					record.merge({"id":app.session.definition.id,"window_mode":window_mode,"client":[root.size.x,root.size.y],"ui_scale":ui,"dpi":DisplayServer.screen_get_dpi(),"windows_scale":DisplayServer.screen_get_scale()})
					records.append(record)
					check(not board.layout_valid or record.grid_fit,"native full frame or explicit geometry failure")
					check(mode == 0 or record.hidden_tokens == 0,"native V all clues")
					if not board.layout_valid: continue
					var cell: Vector2i = Vector2i(2,2)
					var p: Vector2 = board.global_position+board.view.cell_rect(cell).get_center()
					var cells: Array = app.session.player.cells.duplicate()
					var history: Array = app.session.player.history.duplicate(true)
					var cursor: int = app.session.player.cursor
					var center: Vector2 = board.view.center
					mouse(p,MOUSE_BUTTON_MIDDLE,true)
					motion(p+Vector2(90,60))
					mouse(p+Vector2(90,60),MOUSE_BUTTON_MIDDLE,false)
					board.hand = true
					mouse(p,MOUSE_BUTTON_LEFT,true)
					motion(p+Vector2(90,60))
					mouse(p+Vector2(90,60),MOUSE_BUTTON_LEFT,false)
					board.hand = false
					var mini: Vector2 = app.mini.get_global_rect().get_center()
					mouse(mini,MOUSE_BUTTON_LEFT,true)
					motion(mini+Vector2(20,20))
					mouse(mini+Vector2(20,20),MOUSE_BUTTON_LEFT,false)
					check(center == board.view.center and app.session.player.cells == cells and app.session.player.history == history,"native PCK negative MMB/hand/mini input")
					mouse(p,MOUSE_BUTTON_LEFT,true)
					mouse(p,MOUSE_BUTTON_LEFT,false)
					check(app.session.player.cursor == cursor+1,"native PCK real paint commits, including existing redo")
					app._undo()
					check(app.session.player.cells == cells,"native PCK undo exact")
					app._redo()
					app._undo()
					for tool: String in ["minus","plus","fit","work"]:
						click(app.actions[tool])
						check(board.view.cell_size <= board.fit_ceiling and board.mode == ("G" if mode==0 else "V"),"native toolbar bounded and preserves mode")
					if mode == 0:
						for axis: String in ["row","column"]:
							var lines: Array = app.session.definition.rows if axis=="row" else app.session.definition.columns
							var line: int = 0
							for i: int in range(lines.size()):
								if lines[i].size() > lines[line].size(): line=i
							if board.clue_layout(axis,line).max_offset == 0: continue
							var area: Rect2 = board.row_clue_area() if axis=="row" else board.column_clue_area()
							var cross: float = (board.view.origin.y if axis=="row" else board.view.origin.x)+(line+.5)*board.view.cell_size
							var start: Vector2 = board.global_position+(Vector2(area.get_center().x,cross) if axis=="row" else Vector2(cross,area.get_center().y))
							mouse(start,MOUSE_BUTTON_MIDDLE,true)
							motion(start+(Vector2(44.5,90) if axis=="row" else Vector2(90,44.5)))
							check(board.pan_target == axis and board.pan_line_index == line,"native positive frozen clue MMB")
							var tokens: Array = board.visual_hint_units(axis,line).units.filter(func(unit: Dictionary)->bool:return unit.kind=="token")
							check(tokens.size() >= mini(5,lines[line].size()),"native complete minimum tokens")
							mouse(start+(Vector2(44.5,90) if axis=="row" else Vector2(90,44.5)),MOUSE_BUTTON_MIDDLE,false)
							check(board.clue_step(axis,line)>0,"native clue snap saved")
					if index==0 and not output.is_empty():
						board.clear_pointer_hover()
						board.clear_effects()
						await process_frame
						await RenderingServer.frame_post_draw
						root.get_texture().get_image().save_png(output.path_join("vs2-window-%d-u%d-m%d.png" % [window_mode,roundi(ui*100),mode]))
	if not output.is_empty():
		FileAccess.open(output.path_join("vs2-window.json"),FileAccess.WRITE).store_string(JSON.stringify({"records":records,"checks":checks,"failures":failures,"screen":str(DisplayServer.screen_get_size()),"dpi":DisplayServer.screen_get_dpi(),"windows_scale":DisplayServer.screen_get_scale()},"\t"))
	print("VS2_WINDOW_","OK" if failures==0 else "FAILED"," checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
