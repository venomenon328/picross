extends SceneTree
## Actual OS Window/client geometry, also against the delivered embedded PCK.
var app: Control
var failures: int = 0
var checks: int = 0
var records: Array = []

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("VS1 WINDOW FAIL: ",message)

func motion(point: Vector2) -> void:
	var event: InputEventMouseMotion = InputEventMouseMotion.new()
	event.position = point
	root.push_input(event,true)

func mouse(point: Vector2, button: MouseButton, down: bool) -> void:
	motion(point)
	app.board.clear_clue_hover()
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position=point; event.button_index=button; event.pressed=down
	root.push_input(event,true)

func run() -> void:
	check(DisplayServer.get_name() != "headless", "native OS window required")
	app=load("res://full_view_study/main.tscn").instantiate()
	root.add_child(app)
	await process_frame
	for client: Vector2i in [Vector2i(1920,1080),Vector2i(1280,720)]:
		root.mode=Window.MODE_WINDOWED
		root.size=client
		await process_frame
		await process_frame
		check(root.size==client,"actual requested client reached")
		for ui: float in [1.0,1.25]:
			app.set_ui_scale(ui)
			for index: int in [0,3,5,7,9]:
				app.select_puzzle(index)
				app._reset_selected()
				app.open_puzzle()
				for mode: String in ["G","V"]:
					app.choose_mode(mode)
					app.board.fit_all()
					await process_frame
					var record: Dictionary=app.board.measurements()
					record.merge({"id":app.session.definition.id,"client":[root.size.x,root.size.y],"ui_scale":ui,"actual_window":true})
					records.append(record)
					if not app.board.layout_valid: continue
					var center: Vector2=app.board.view.center
					var w: int=app.session.player.width
					var h: int=app.session.player.height
					for cell: Vector2i in [Vector2i.ZERO,Vector2i(w-1,0),Vector2i(0,h-1),Vector2i(w-1,h-1)]:
						var point: Vector2=app.board.global_position+app.board.view.cell_rect(cell).get_center()
						check(app.board.view.hit(point-app.board.global_position)==cell,"actual window corner hit matches drawn cell")
						var cursor: int=app.session.player.cursor
						mouse(point,MOUSE_BUTTON_LEFT,true); mouse(point,MOUSE_BUTTON_LEFT,false)
						check(app.session.player.cursor==cursor+1,"corner input commits one action")
						app._undo()
						check(app.session.player.cells[cell.y*w+cell.x]==-1,"corner undo")
					var point: Vector2=app.board.global_position+app.board.view.viewport.get_center()
					mouse(point,MOUSE_BUTTON_MIDDLE,true); motion(point-Vector2(90,60)); mouse(point-Vector2(90,60),MOUSE_BUTTON_MIDDLE,false)
					app.board.navigate_to(Vector2.ZERO)
					check(app.board.view.center==center,"MMB/miniature cannot move grid")
					for direction: MouseButton in [MOUSE_BUTTON_WHEEL_DOWN,MOUSE_BUTTON_WHEEL_UP]:
						for step: int in range(20):
							mouse(point,direction,true)
							check(app.board.view.cell_size<=app.board.fit_ceiling and app.board.view.viewport.grow(0.01).encloses(app.board.view.bounds()),"actual wheel retains grid and ceiling")
					for tool: String in ["work","minus","plus","fit"]:
						var control_point: Vector2=app.actions[tool].get_global_rect().get_center()
						mouse(control_point,MOUSE_BUTTON_LEFT,true); mouse(control_point,MOUSE_BUTTON_LEFT,false)
						check(app.board.view.cell_size<=app.board.fit_ceiling,"actual toolbar zoom capped")
					check(is_equal_approx(app.board.view.cell_size,app.board.fit_ceiling),"actual Fit button reaches ceiling")
					if mode=="G":
						for axis: String in ["row","column"]:
							var lines: Array=app.session.definition.rows if axis=="row" else app.session.definition.columns
							var line: int=0
							for i: int in range(lines.size()):
								if lines[i].size()>lines[line].size(): line=i
							var layout: Dictionary=app.board.clue_layout(axis,line)
							if int(layout.max_offset)==0: continue
							var area: Rect2=app.board.row_clue_area() if axis=="row" else app.board.column_clue_area()
							var local: Vector2=Vector2(area.get_center().x,app.board.view.origin.y+(line+0.5)*app.board.view.cell_size) if axis=="row" else Vector2(app.board.view.origin.x+(line+0.5)*app.board.view.cell_size,area.get_center().y)
							var old_reads: Array=app.board.column_clue_reads.duplicate(true) if axis=="row" else app.board.row_clue_reads.duplicate(true)
							var start: Vector2=app.board.global_position+local
							mouse(start,MOUSE_BUTTON_MIDDLE,true)
							for distance: float in [0.0,13.25,44.5,120.75,2000.0,38.25,-2000.0]:
								motion(start+(Vector2(distance,0) if axis=="row" else Vector2(0,distance)))
								var tokens: Array=app.board.visual_hint_units(axis,line).units.filter(func(u: Dictionary)->bool:return u.kind=="token")
								check(tokens.size()>=mini(5,lines[line].size()),"actual continuous MMB draws min(5,n)")
								check(app.board.view.center==center,"hint drag keeps grid still")
							var nearest: int=app.board.closest_clue_snap(axis,line)
							mouse(start+(Vector2(-2000,0) if axis=="row" else Vector2(0,-2000)),MOUSE_BUTTON_MIDDLE,false)
							check(app.board.clue_step(axis,line)==nearest,"actual release uses geometric nearest snap")
							check((app.board.column_clue_reads if axis=="row" else app.board.row_clue_reads)==old_reads,"hint axes remain independent")
					# Escape, resize and case/mode changes discard uncommitted ink.
					point=app.board.global_position+app.board.view.cell_rect(Vector2i(2,2)).get_center()
					mouse(point,MOUSE_BUTTON_LEFT,true)
					var key: InputEventKey=InputEventKey.new()
					key.keycode=KEY_ESCAPE; key.pressed=true; root.push_input(key,true)
					check(not app.session.gesture.active,"actual Escape cancels")
					mouse(point,MOUSE_BUTTON_LEFT,false)
					mouse(point,MOUSE_BUTTON_LEFT,true)
					root.size=client+Vector2i(20,10)
					await process_frame
					check(not app.session.gesture.active,"actual resize cancels gesture")
					root.size=client
					await process_frame
					mouse(point,MOUSE_BUTTON_LEFT,false)
					check(app.board.view.cell_size<=app.board.fit_ceiling,"resize re-clamps ceiling")
	var output: String=OS.get_environment("VS1_PROBE_OUTPUT")
	if not output.is_empty():
		FileAccess.open(output.path_join("vs1-window.json"),FileAccess.WRITE).store_string(JSON.stringify({"records":records,"checks":checks,"failures":failures,"screen":str(DisplayServer.screen_get_size()),"dpi":DisplayServer.screen_get_dpi(),"scale":DisplayServer.screen_get_scale()},"\t"))
	print("VS1_WINDOW_", "OK" if failures==0 else "FAILED", " checks=",checks," rows=",records.size()," failures=",failures)
	quit(0 if failures==0 else 1)
