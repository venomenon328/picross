extends RefCounted
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
const P12 = preload("res://tests/p12_cases.gd")

static func click(t: SceneTree, item: Control) -> void:
	var point: Vector2 = item.get_global_rect().get_center()
	t.mouse_motion(point,false)
	t.mouse_button(point,true)
	t.mouse_button(point,false)

static func state(app: Main) -> Dictionary:
	return SaveStore.snapshot(app.session,app.board.capture_view()).duplicate(true)

static func run(t: SceneTree) -> void:
	SaveStore.test_root_override = SaveStore.test_root_override.path_join("z2")
	t.root.size = Vector2i(1920,1080)
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	await t.process_frame
	click(t,app.choices[1])
	await t.process_frame
	t.check(app.work.visible and app.session == app.sessions[1],"Z2-A01 album opens regular F-02")
	t.check(app.theme.default_font.get_font_name() == "IBM Plex Sans" and app.TITLE_FONT.get_font_name() == "Fraunces","Z2-A01 bundled font families")
	for tool: String in ["hand","erase"]:
		click(t,app.actions[tool])
		click(t,app.actions["color-2"])
		t.check(not app.board.hand and not app.board.eraser and app.board.active_color == 2 and app.actions.fill.selected and app.actions["color-2"].selected,"Z2-A02 colour after " + tool + " selects fill")
		var cell: Vector2i = app.board.view.hit(app.board.view.viewport.get_center())
		var point: Vector2 = app.board.global_position + app.board.view.cell_rect(cell).get_center()
		t.mouse_button(point,true)
		t.mouse_button(point,false)
		t.check(app.session.player.cells[cell.y*40+cell.x] == 2,"Z2-A02 next real board click fills")
		click(t,app.undo_button)
		t.check(app.redo_button.disabled == false and app.undo_button.disabled,"Z2-A02 actual undo/redo availability")
		click(t,app.redo_button)
		click(t,app.undo_button)
	# Keep real history, a redo branch, tool, colour and non-default views.
	var zoom_before: float = app.board.view.cell_size
	click(t,app.actions.plus)
	t.check(app.board.view.cell_size > zoom_before,"Z2-A02 plus changes working zoom")
	click(t,app.actions.minus)
	t.check(app.board.view.cell_size == zoom_before,"Z2-A02 minus restores previous step")
	click(t,app.actions.fit)
	t.check(app.board.overview,"Z2-A02 fit via viewport")
	click(t,app.actions.work)
	t.check(not app.board.overview,"Z2-A02 work size via viewport")
	app.board.set_clue_step("row",35,2)
	app.board.set_clue_step("row",36,1)
	app.board.set_clue_step("column",21,2)
	app.board.set_clue_step("column",22,1)
	click(t,app.actions.hand)
	app._save_current()
	for route: String in ["nav-information","help","menu"]:
		if route == "nav-information":
			click(t,app.actions.fit)
		else:
			click(t,app.actions.work)
		var before: Dictionary = state(app)
		t.check(app.board.clue_step("row",35) > 0 and app.board.clue_step("row",36) > 0 and app.board.clue_step("column",21) > 0 and app.board.clue_step("column",22) > 0,"Z2-A03 navigation starts with four nontrivial line reads")
		click(t,app.actions[route])
		await t.process_frame
		t.check(app.information.visible and not app.work.visible and app.information_section == ("help" if route == "help" else "settings"),"Z2-A03 shared N1 route " + route)
		t.check(app.get_viewport().gui_get_focus_owner() == (app.information.get_node("help-access") if route == "help" else app.ui_scale_button),"Z2-A03 deterministic focus " + route)
		var point: Vector2 = app.board.global_position+app.board.view.viewport.get_center()
		t.mouse_button(point,true,MOUSE_BUTTON_RIGHT)
		t.mouse_button(point,false,MOUSE_BUTTON_RIGHT)
		t.mouse_button(point,true,MOUSE_BUTTON_WHEEL_UP)
		t.mouse_button(point,false,MOUSE_BUTTON_WHEEL_UP)
		t.check(state(app) == before,"Z2-A03 hidden board ignores clicks/wheel")
		click(t,app.actions["nav-work"])
		await t.process_frame
		t.check(app.work.visible and state(app) == before,"Z2-A03 full state survives return " + route)
	click(t,app.actions.work)
	# Native six-slot version supplements the historical exact owner regression.
	var original_viewport: Rect2 = app.board.view.viewport
	app.board.view.configure(Rect2(Vector2(180,original_viewport.position.y),Vector2(original_viewport.end.x-180,original_viewport.size.y)),app.board.view.dimensions)
	app.board.normalize_clue_steps()
	app.board.navigate_to(Vector2(0.5,11.0/40.0))
	t.check(app.board.clue_capacity("row") == 6,"Z2-A06 native six 30px slots")
	P12.snap_geometry_case(t,app.board,"row",11,0,1.8,"Z2 native row12 +1.8 slots")
	P12.monotone_clue_route(t,app.board,"row",11)
	app._layout_book()
	# Every transient interaction is cancelled, never committed by navigation.
	for gesture: String in ["cells","raster","row","column","mini"]:
		app.set_tool("fill")
		var point: Vector2 = app.board.global_position+app.board.view.viewport.get_center()
		var button: MouseButton = MOUSE_BUTTON_LEFT
		if gesture == "raster":
			button = MOUSE_BUTTON_MIDDLE
		elif gesture == "row" or gesture == "column":
			app.board.navigate_to(Vector2(0.8,0.8))
			point = P12.clue_point(app.board,gesture,35 if gesture == "row" else 21)
			button = MOUSE_BUTTON_MIDDLE
		elif gesture == "mini":
			point = app.mini.get_global_rect().get_center()
		var history: Array = app.session.player.history.duplicate(true)
		t.mouse_button(point,true,button)
		t.mouse_motion(point+Vector2(8,8),true,button)
		t.check(app.session.gesture.active if gesture == "cells" else (app.mini.dragging if gesture == "mini" else app.board.pan_button != MOUSE_BUTTON_NONE),"Z2-A03 actual transient started: " + gesture)
		app.show_information("settings")
		t.mouse_button(point+Vector2(8,8),false,button)
		t.check(app.information.visible and not app.session.gesture.active and app.board.pan_button == MOUSE_BUTTON_NONE and app.board.pan_drag_distance == 0 and not app.mini.dragging and app.session.player.history == history,"Z2-A03 cancels " + gesture + " without history")
		app.return_to_work()
	app.show_information("settings")
	await t.process_frame
	click(t,app.information.get_node("help-access"))
	t.check(app.help_panel.visible and not app.settings_panel.visible,"Z2-A02 N1 help section event")
	click(t,app.information.get_node("settings-access"))
	t.check(app.settings_panel.visible and not app.help_panel.visible,"Z2-A02 N1 settings section event")
	click(t,app.ui_scale_button)
	t.check(app.ui_scale == 1.25,"Z2-A03 UI scale in N1")
	click(t,app.clue_completion_toggle)
	t.check(not app.mark_completed_clues,"Z2-A03 H1 in N1")
	click(t,app.clue_reset_button)
	t.check(app.board.row_clue_steps.count(0) == 40 and app.board.column_clue_steps.count(0) == 40,"Z2-A03 reset reads in N1")
	t.root.size = Vector2i(1280,720)
	await t.process_frame
	app.return_to_work()
	t.check(app.board.size.x > 0 and app.work.visible and app.ui_scale == 1.25 and not app.mark_completed_clues,"Z2-A03 resize hidden board preserves valid view and settings")
	for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080),Vector2i(2560,1440)]:
		for scale: float in [1.0,1.25]:
			t.root.size = dimensions
			app.set_ui_scale(scale)
			await t.process_frame
			var grid: Rect2 = app.board.view.visible_bounds()
			grid.position += app.board.global_position
			t.check(Rect2(Vector2.ZERO,Vector2(dimensions)).encloses(grid) and grid.end.y <= app.actions.fill.global_position.y-4,"Z2-A05 raster stays above tools at intermediate sizes")
			for key: String in app.actions:
				var item: Control = app.actions[key]
				if item.is_visible_in_tree():
					t.check(Rect2(Vector2.ZERO,Vector2(dimensions)).encloses(item.get_global_rect()) and item.size.x >= 44*scale and item.size.y >= 44*scale,"Z2-A05 visible hit area " + key + str(dimensions) + str(scale))
	# Missing primary after rotation must not trap recovery behind N1.
	app.set_ui_scale(1.0)
	app._save_current()
	var other: Array = [app.sessions[0].player.cells.duplicate(),app.sessions[2].player.cells.duplicate()]
	app.board.zoom(1,app.board.view.viewport.get_center())
	var pending: Dictionary = state(app)
	app.store.fail_step = "after_rotation"
	click(t,app.actions.menu)
	t.check(app.work.visible and not app.information.visible and state(app) == pending and app.status_label.visible and app.work_repair_button.is_visible_in_tree(),"Z2-A04 failed flush keeps view, error and recovery reachable")
	t.check(not FileAccess.file_exists(app.store.path_for("f02")) and app.slot_status[1] == "recovered","Z2-A04 primary missing, backup retained")
	var backup: String = FileAccess.get_file_as_string(app.store.path_for("f02",".bak"))
	app.store.fail_step = ""
	click(t,app.work_repair_button)
	t.check(app.repair_dialog.visible and not FileAccess.file_exists(app.store.path_for("f02")),"Z2-A04 repair requires explicit confirmation")
	var modal_history: Array = app.session.player.history.duplicate(true)
	var behind: Vector2 = app.board.global_position+app.board.view.viewport.get_center()
	t.mouse_button(behind,true)
	t.mouse_button(behind,false)
	t.check(app.session.player.history == modal_history and not app.session.gesture.active,"Z2-A04 modal does not click through")
	app.repair_dialog.hide()
	click(t,app.actions.menu)
	t.check(app.work.visible and FileAccess.get_file_as_string(app.store.path_for("f02",".bak")) == backup,"Z2-A04 cancelled repair and retry preserve backup")
	click(t,app.work_repair_button)
	app.repair_dialog.hide()
	app.repair_dialog.confirmed.emit()
	app.open_puzzle()
	click(t,app.actions.menu)
	t.check(app.information.visible and app.store.load_slot(app.session.definition).status == "loaded" and app.sessions[0].player.cells == other[0] and app.sessions[2].player.cells == other[1],"Z2-A04 confirmed repair allows retry and preserves other slots")
	app.return_to_work()
	click(t,app.actions["nav-album"])
	t.check(app.album.visible,"Z2-A02 album register via viewport")
	app.queue_free()
	await t.process_frame
