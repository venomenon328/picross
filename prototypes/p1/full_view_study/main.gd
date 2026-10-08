extends "res://ui/main.gd"
const VSBoard = preload("res://full_view_study/board.gd")
const VSStore = preload("res://full_view_study/save_store.gd")
const Catalog = preload("res://full_view_study/catalog.gd")
var study_root: String
var mode_controls: HBoxContainer
var study_status: Label
var animation_toggle: CheckBox
var study_ready: bool = false
var state: Dictionary = {"revision": 1, "selected": 0, "mode": "G", "requested_cell": 0.0}

func create_board() -> Board:
	var item: VSBoard = VSBoard.new()
	item.mode = state.mode
	item.requested_cell = float(state.requested_cell)
	return item

func create_store() -> SaveStore:
	# Revision-bound and stable across launches. Set before ANY slot load, direct EXE included.
	study_root = OS.get_user_data_dir().path_join("vs1/revision-1")
	if not OS.get_environment("VS1_TEST_ROOT").is_empty():
		study_root = OS.get_environment("VS1_TEST_ROOT")
	_read_state()
	return VSStore.new(study_root)

func puzzle_definitions() -> Array[Dictionary]:
	return Catalog.definitions()

func validate_definition(data: Dictionary) -> String:
	return Catalog.validate(data)

func _ready() -> void:
	super._ready()
	if board == null or sessions.size() != 10:
		return
	get_window().title = "picross · VS-1 · Vollsicht-Studie"
	for item: Node in album_content.get_children():
		if item is Label and item.text == "Neun Blätter zum Entdecken":
			item.text = "Zehn Studienblätter · Spalten × Zeilen"
	mode_controls = HBoxContainer.new()
	mode_controls.add_theme_constant_override("separation", 8)
	work.add_child(mode_controls)
	for mode: String in ["R", "G", "V"]:
		var caption: String = {"R": "R · Referenz", "G": "G · Raster", "V": "V · Ganzes Blatt"}[mode]
		mode_controls.add_child(_text_button(caption, choose_mode.bind(mode)))
	study_status = label("", 14)
	study_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	study_status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	work.add_child(study_status)
	animation_toggle = CheckBox.new()
	animation_toggle.text = "Zellanimationen"
	animation_toggle.button_pressed = true
	animation_toggle.toggled.connect(board.set_animations)
	settings_panel.add_child(animation_toggle)
	for mode: String in ["R","G","V"]:
		settings_panel.add_child(_text_button("Ansicht %s öffnen" % mode, func() -> void: choose_mode(mode); open_puzzle()))
	settings_panel.add_child(_text_button("Künstlichen Vergleichsstand laden", _ask_sample))
	settings_panel.add_child(_text_button("Studienblatt leeren", _ask_reset))
	var info: Label = label("VS-1: R behält die Referenznavigation. G hält das Raster sichtbar; lange Hinweise bleiben verschiebbar. V reserviert alle Hinweise. Kleine oder kollidierende Zahlen sind kein Komfortnachweis.\nVergleichsstand: künstliche eigene Eingaben, keine Lösungshilfe. Zurücksetzen betrifft nur dieses Studienblatt. Normale P1-Spielstände bleiben getrennt.", 16)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	settings_panel.add_child(info)
	var restored: Dictionary = state.duplicate(true)
	select_puzzle(clampi(int(restored.selected), 0, sessions.size() - 1))
	set_ui_scale(float(restored.get("ui_scale", 1.0)))
	study_ready = true
	_schedule_view_save()
	if OS.get_cmdline_user_args().has("--vs1-smoke"):
		call_deferred("study_smoke")

func show_album() -> void:
	super.show_album()
	for i: int in range(choices.size()):
		choices[i].text = sessions[i].album_title()

func select_puzzle(index: int) -> void:
	super.select_puzzle(index)
	if study_ready:
		_schedule_view_save()

func set_ui_scale(value: float) -> void:
	super.set_ui_scale(value)
	if study_ready:
		_schedule_view_save()

func choose_mode(value: String) -> void:
	board.set_mode(value)
	state.mode = value
	_schedule_view_save()
	_layout_book()
	refresh()

func _ask_sample() -> void:
	var dialog: ConfirmationDialog = ConfirmationDialog.new()
	dialog.dialog_text = "Eigenen Studienstand dieses Blatts durch künstliche Vergleichseingaben ersetzen?"
	dialog.confirmed.connect(func() -> void: replace_with_sample(); dialog.queue_free())
	dialog.canceled.connect(dialog.queue_free)
	add_child(dialog)
	dialog.popup_centered()

func replace_with_sample() -> void:
	_cancel_interaction()
	var index: int = sessions.find(session)
	# Use the same explicit reset/recovery contract as the regular empty action.
	var error: String = store.reset_slot(str(session.definition.id).to_lower())
	if not error.is_empty():
		slot_errors[index] = error
		_update_status()
		return
	slot_status[index] = "fresh"
	slot_errors[index] = ""
	# A deliberate replacement, no injected solution cells: arithmetic pattern only.
	var replacement: Session = Session.new(session.definition)
	var changes: Array = []
	for y: int in range(replacement.player.height):
		for x: int in range(replacement.player.width):
			if (x + y * 3) % 7 < 2 or y < 3:
				changes.append({"index": y * replacement.player.width + x, "before": -1, "after": 0 if (x+y)%3 == 0 else 1 + (x/5+y/4) % replacement.definition.palette.size()})
	replacement.player.commit(changes)
	sessions[index] = replacement
	session = replacement
	board.session = session
	board.restore_view(session.view_state)
	_save_current()
	open_puzzle()

func _undo() -> void:
	board.clear_effects()
	super._undo()

func _redo() -> void:
	board.clear_effects()
	super._redo()

func _read_state() -> void:
	var path: String = study_root.path_join("study-view.json")
	if not FileAccess.file_exists(path):
		return
	var value: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if value is Dictionary and value.get("revision") == 1 and value.get("mode") in ["R", "G", "V"] and SaveStore.integer(value.get("selected")) and int(value.selected) >= 0 and int(value.selected) < 10 and SaveStore.number(value.get("requested_cell")) and float(value.requested_cell) >= 0 and float(value.requested_cell) <= 72 and value.get("ui_scale", 1.0) in [1.0, 1.25]:
		state = value
	# Invalid view metadata never changes cell recovery or creates a new puzzle stand.

func _save_current() -> bool:
	if not super._save_current():
		return false
	if board == null or store == null or not study_ready:
		return true
	state = {"revision": 1, "selected": sessions.find(session), "mode": board.mode, "requested_cell": board.requested_cell, "ui_scale": ui_scale}
	var temporary: String = study_root.path_join("study-view.tmp")
	var file: FileAccess = FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		save_error = "Studienansicht konnte nicht gespeichert werden."
	else:
		file.store_string(JSON.stringify(state))
		file.flush()
		file.close()
		if DirAccess.rename_absolute(temporary, study_root.path_join("study-view.json")) != OK:
			save_error = "Studienansicht konnte nicht ersetzt werden."
	if not save_error.is_empty():
		slot_errors[sessions.find(session)] = save_error
		_update_status()
	return save_error.is_empty()

func _layout_book() -> void:
	super._layout_book()
	if board == null or mode_controls == null or size.x < 1280 or size.y < 720:
		return
	var u: float = ui_scale
	# R keeps its original clue surface completely unobscured. Its study-mode
	# controls are reachable in the existing menu; G/V reserve their own header.
	mode_controls.visible = board.mode != "R"
	study_status.visible = board.mode != "R"
	var material: Rect2 = surface.material_rect()
	var origin: Vector2 = material.position
	var extent: Vector2 = material.size
	_place(mode_controls, Rect2(origin + Vector2(100, 98)*u, Vector2(450*u+16, 44*u)))
	for control: Button in mode_controls.get_children():
		control.custom_minimum_size = Vector2(150*u, 44*u)
		control.add_theme_font_size_override("font_size", roundi(15*u))
	if board.mode != "R":
		laying_out = true
		var rail: float = extent.x - 260*u
		var top: float = 158*u
		var bottom: float = extent.y - 76*u
		var left: float = 68*u
		_place(board, Rect2(origin + Vector2(left, top), Vector2(rail-left-24*u, bottom-top-10*u)))
		board._layout()
		_place(mini, Rect2(origin+Vector2(rail+22*u,top+30*u),Vector2(132,132)*u))
		_place(mini_title, Rect2(mini.position-Vector2(0,26*u),Vector2(180,24)*u))
		_place(coordinate,Rect2(mini.position+Vector2(0,150*u),Vector2(190,44)*u))
		_place(palette_row,Rect2(mini.position+Vector2(0,202*u),Vector2(110,110)*u))
		_place(zoom_label,Rect2(mini.position+Vector2(0,316*u),Vector2(200,24)*u))
		_place(tool_label,Rect2(mini.position+Vector2(0,340*u),Vector2(200,24)*u))
		var ids: Array[String] = ["fill","erase","hand","undo","redo","minus","plus","fit","work"]
		surface.wells.clear()
		for i: int in range(ids.size()):
			_place(actions[ids[i]],Rect2(origin+Vector2(left+i*52*u,bottom),Vector2(44,44)*u))
		surface.wells.append(Rect2(origin+Vector2(left-3*u,bottom-3*u),Vector2(466,50)*u))
		surface.card=Rect2(mini.position-Vector2(10,28)*u,mini.size+Vector2(20,38)*u)
		surface.miniature=mini.get_rect()
		surface.palette=palette_row.get_rect().grow(6*u)
		laying_out=false
	_place(study_status,Rect2(origin+Vector2(680*u,90*u),Vector2(maxf(260,extent.x-760*u),62*u)))
	if extent.x < 1500 and u > 1.0:
		_place(study_status,Rect2(origin+Vector2(600*u,70*u),Vector2(extent.x-610*u,82*u)))
	_update_study_status()
	surface.queue_redraw()

func _update_study_status() -> void:
	if study_status == null:
		return
	if work.visible and not session.completed:
		title.text = "%s · %s" % [session.album_title(),board.mode]
	var prefix: String = "R · freie Navigation" if board.mode == "R" else ("G · Raster; Hinweise ggf. verschieben" if board.mode == "G" else "V · Raster und alle Hinweise")
	var warning: String = ""
	if board.mode != "R":
		if not board.layout_valid:
			warning = "PASST NICHT · R verwenden"
		elif board.view.cell_size < 16:
			warning = "Unter 16 px · Diagnose, Komfort offen"
		if board.glyph_risk:
			warning = "Zahlenkollision möglich · R verwenden" if board.layout_valid else warning
	study_status.text = "%s\nZelle %.2f · Fit %.2f · Schrift %d px\n%s" % [prefix,board.view.cell_size,board.fit_ceiling,board.clue_font_size(),warning]

func refresh() -> void:
	super.refresh()
	_update_study_status()

func study_smoke() -> void:
	if store.root != study_root or store.path_for("f01") != "" or sessions.size() != 10:
		get_tree().quit(4)
		return
	print("VS1_START_OK root=", store.root, " cases=", sessions.size(), " mode=", board.mode)
	print("VS1_WINDOW_INFO ", JSON.stringify({"client": [get_window().size.x,get_window().size.y], "screen": str(DisplayServer.screen_get_size()), "scale": DisplayServer.screen_get_scale(), "dpi": DisplayServer.screen_get_dpi()}))
	get_tree().quit(0)
