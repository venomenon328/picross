extends Control
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const ChalkboardBoard = preload("res://ui/chalkboard_board.gd")
const FullViewBoard = preload("res://ui/full_view_board.gd")
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
const SaveStore = preload("res://model/save_store.gd")
const BookButton = preload("res://ui/book_button.gd")
const BookSurface = preload("res://ui/book_surface.gd")
const BODY_FONT = preload("res://art/book/PlexSans.ttf")
const TITLE_FONT = preload("res://art/book/Fraunces.ttf")
var surface: BookSurface
var information: Control
var information_section: String = "settings"
var settings_panel: VBoxContainer
var help_panel: VBoxContainer
var info_scroll: ScrollContainer
var information_origin: String = "album"
var view_choice: OptionButton
var ui_scale_button: Button
var actions: Dictionary = {}
var mini_title: Label
var laying_out: bool = false
var sessions: Array[Session] = []
var store: SaveStore
var slot_status: Array[String] = []
var slot_errors: Array[String] = []
var save_error: String = ""
var save_timer: Timer
var status_label: Label
var reset_dialog: ConfirmationDialog
var repair_dialog: ConfirmationDialog
var repair_button: Button
var work_repair_button: Button
var session: Session
var board: Board
var mini: Miniature
var album_mini: Miniature
var album_picture: Reveal
var reveal_view: Reveal
var album: ScrollContainer
var album_content: VBoxContainer
var album_grid: GridContainer
var work: Control
var ending: VBoxContainer
var title: Label
var album_button: Button
var open_button: Button
var undo_button: Button
var redo_button: Button
var coordinate: Label
var tool_label: Label
var completion_title: Label
var zoom_label: Label
var stress_label: Label
var palette_row: Control
var sidebar: Control
var page: Control
var minimum_message: Label
var clue_reset_button: Button
var animation_toggle: CheckBox
var clue_completion_toggle: CheckBox
var mark_completed_clues: bool = true
var ui_scale: float = 1.0
var choices: Array[Button] = []
var album_previews: Array[Miniature] = []
var album_reveals: Array[Reveal] = []
var album_slot_status: Array[Label] = []

static func bounded_start(usable: Rect2i, decorations: Vector2i) -> Vector2i:
	return Vector2i(1920, 1080).min((usable.size - decorations).max(Vector2i.ONE))

static func bounded_position(usable: Rect2i, client: Vector2i, decorations: Vector2i, client_offset: Vector2i) -> Vector2i:
	# Window.position is the client origin. Center the entire decorated window.
	return usable.position + (usable.size - client - decorations) / 2 + client_offset

func create_store() -> SaveStore:
	return SaveStore.new(SaveStore.test_root_override if not SaveStore.test_root_override.is_empty() else "user://p1/saves")

func puzzle_definitions() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for id: String in SaveStore.IDS:
		result.append(Definition.load_fixture(id))
	return result

func validate_definition(data: Dictionary) -> String:
	return Definition.validate(data)

func _ready() -> void:
	get_tree().auto_accept_quit = false
	store = create_store()
	if DisplayServer.get_name() != "headless" and not OS.get_cmdline_user_args().has("--p1-capture"):
		var usable: Rect2i = DisplayServer.screen_get_usable_rect()
		var decorations: Vector2i = (DisplayServer.window_get_size_with_decorations() - DisplayServer.window_get_size()).max(Vector2i(16, 48))
		var client_offset: Vector2i = DisplayServer.window_get_position() - DisplayServer.window_get_position_with_decorations()
		get_window().size = bounded_start(usable, decorations)
		get_window().position = bounded_position(usable, get_window().size, decorations, client_offset)
	for data: Dictionary in puzzle_definitions():
		var error: String = validate_definition(data)
		if not error.is_empty():
			push_error(error)
			get_tree().quit(2)
			return
		var item: Session = Session.new(data)
		var result: Dictionary = store.load_slot(data)
		if result.status in ["loaded", "recovered", "backup_invalid"]:
			SaveStore.apply(result.data, item)
		sessions.append(item)
		slot_status.append(str(result.status))
		slot_errors.append("")
	session = sessions[0]
	_build()
	save_timer = Timer.new()
	save_timer.one_shot = true
	save_timer.wait_time = 0.35
	save_timer.timeout.connect(_save_current)
	add_child(save_timer)
	resized.connect(_check_minimum)
	_check_minimum()
	board.restore_view(session.view_state)
	session.view_state = board.capture_view()
	show_album()
	if OS.get_cmdline_user_args().has("--p1-smoke"):
		call_deferred("_smoke")

func _build() -> void:
	theme = Theme.new()
	theme.default_font = BODY_FONT
	theme.default_font_size = 14
	theme.set_color("font_color", "Label", Board.INK)
	for type_name: String in ["Button", "CheckBox"]:
		for color_name: String in ["font_color", "font_focus_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color"]:
			theme.set_color(color_name, type_name, BookButton.INK)
	for state: String in ["normal", "hover", "pressed", "disabled"]:
		var style: StyleBoxFlat = StyleBoxFlat.new()
		style.bg_color = Color("e3e7d6") if state == "normal" else Color("d1d9be")
		style.content_margin_left = 10
		style.content_margin_right = 10
		style.content_margin_top = 5
		style.content_margin_bottom = 5
		style.corner_radius_top_left = 0
		style.corner_radius_bottom_right = 0
		theme.set_stylebox(state, "Button", style)
		theme.set_color("font_color" if state == "normal" else "font_" + state + "_color", "Button", Board.INK)
	var dialog_paper: StyleBoxFlat = StyleBoxFlat.new()
	dialog_paper.bg_color = Color("fffaf0")
	dialog_paper.set_content_margin_all(16)
	theme.set_stylebox("panel","AcceptDialog",dialog_paper)
	theme.set_stylebox("panel","TooltipPanel",dialog_paper)
	theme.set_color("font_color","TooltipLabel",Board.INK)
	surface = BookSurface.new()
	surface.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(surface)
	page = Control.new()
	page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(page)
	title = label("Sammlung", 28)
	var heading: FontVariation = FontVariation.new()
	heading.base_font = TITLE_FONT
	heading.variation_opentype = {"wght": 600.0}
	title.add_theme_font_override("font", heading)
	page.add_child(title)
	status_label = label("", 14)
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	page.add_child(status_label)
	stress_label = label("UI-Testdatensatz – Rätselqualität nicht abgenommen", 14)
	page.add_child(stress_label)
	album = ScrollContainer.new()
	album.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	album_content = VBoxContainer.new()
	album_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	album.add_child(album_content)
	album.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(album)
	album_content.add_child(label("Neun Blätter zum Entdecken", 28))
	album_grid = GridContainer.new()
	album_grid.columns = 3
	album_grid.add_theme_constant_override("h_separation", 16)
	album_grid.add_theme_constant_override("v_separation", 12)
	album_content.add_child(album_grid)
	for i: int in range(sessions.size()):
		var slot_column: VBoxContainer = VBoxContainer.new()
		album_grid.add_child(slot_column)
		slot_column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var choice: Button = button(sessions[i].album_title() + (" · UI-Test" if i == 2 else ""), select_puzzle.bind(i))
		choices.append(choice)
		slot_column.add_child(choice)
		var preview: Miniature = Miniature.new()
		preview.custom_minimum_size = Vector2(96, 96)
		slot_column.add_child(preview)
		album_previews.append(preview)
		var picture: Reveal = Reveal.new()
		picture.paired = false
		picture.custom_minimum_size = Vector2(96, 96)
		slot_column.add_child(picture)
		album_reveals.append(picture)
		var slot_note: Label = label("", 14)
		slot_column.add_child(slot_note)
		album_slot_status.append(slot_note)
	album_mini = Miniature.new()
	album_mini.custom_minimum_size = Vector2(240, 240)
	album_content.add_child(album_mini)
	album_picture = Reveal.new()
	album_picture.paired = false
	album_picture.custom_minimum_size = Vector2(240, 240)
	album_content.add_child(album_picture)
	open_button = button("Blatt öffnen", open_puzzle)
	open_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album_content.add_child(open_button)
	album_content.add_child(label("Jedes Blatt speichert den eigenen Arbeitsstand lokal.", 16))
	album_content.add_child(button("Einstellungen und Hilfe",show_information.bind("settings")))
	var reset_button: Button = button("Arbeitsstand zurücksetzen", _ask_reset)
	reset_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album_content.add_child(reset_button)
	repair_button = button("Backup zum Speichern übernehmen", _ask_repair)
	repair_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album_content.add_child(repair_button)
	reset_dialog = ConfirmationDialog.new()
	reset_dialog.title = "Arbeitsstand zurücksetzen?"
	reset_dialog.dialog_text = "Nur das ausgewählte Blatt wird vollständig zurückgesetzt."
	reset_dialog.confirmed.connect(_reset_selected)
	add_child(reset_dialog)
	reset_dialog.get_ok_button().text = "Zurücksetzen"
	reset_dialog.get_cancel_button().text = "Abbrechen"
	repair_dialog = ConfirmationDialog.new()
	repair_dialog.title = "Backup übernehmen?"
	repair_dialog.dialog_text = "Der beschädigte Primärstand dieses Blatts wird durch das gültige Backup ersetzt."
	repair_dialog.confirmed.connect(_repair_selected)
	add_child(repair_dialog)
	repair_dialog.get_cancel_button().text = "Abbrechen"
	_build_work()
	_build_information()
	ending = VBoxContainer.new()
	ending.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(ending)
	completion_title = label("", 28)
	ending.add_child(completion_title)
	ending.add_child(label("Prototyp ohne Wertung · Dein Bild ist im Album.", 18))
	reveal_view = Reveal.new()
	reveal_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ending.add_child(reveal_view)
	ending.add_child(button("Zurück ins Album", show_album))

	minimum_message = label("Mindestens 1280 × 720 logische Fensterfläche benötigt.\nBitte das Fenster vergrößern oder die Anzeigeskalierung prüfen.", 20)
	minimum_message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	minimum_message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	minimum_message.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(minimum_message)
	# Recovery must remain above either page, including a failed N1 return flush.
	page.move_child(status_label,page.get_child_count()-1)
	page.move_child(work_repair_button,page.get_child_count()-1)
	_update_palette()
	resized.connect(_layout_book)
	_layout_book()

func _check_minimum() -> void:
	var small: bool = size.x < 1280 or size.y < 720
	minimum_message.visible = small
	page.visible = not small
	surface.work_visible = work.visible and not small
	surface.queue_redraw()
	if small:
		_cancel_interaction()

func set_clue_completion(enabled: bool) -> void:
	mark_completed_clues = enabled
	clue_completion_toggle.set_pressed_no_signal(enabled)
	board.mark_completed_clues = enabled
	board.queue_redraw()

func set_ui_scale(value: float) -> void:
	_cancel_interaction()
	ui_scale = value
	theme.default_font_size = roundi(14 * value)
	_scale_labels(self)
	board.ui_scale = value
	ui_scale_button.text = "UI %d %%" % roundi(ui_scale * 100)
	_layout_book()
	board.queue_redraw()

func _scale_labels(node: Node) -> void:
	if node is Label:
		if not node.has_meta("base_font"):
			node.set_meta("base_font", node.get_theme_font_size("font_size"))
		node.add_theme_font_size_override("font_size", roundi(float(node.get_meta("base_font")) * ui_scale))
	for child: Node in node.get_children():
		_scale_labels(child)

func set_tool(tool: String) -> void:
	board.eraser = tool == "erase"
	board.hand = false
	tool_label.text = "Werkzeug: " + ("Radierer" if board.eraser else ("Füllen · " + str(session.definition.palette[board.active_color - 1].symbol)))
	_update_actions()
	if save_timer != null:
		_save_current()

func _update_palette() -> void:
	for key: String in actions.keys():
		if key.begins_with("color-"):
			actions.erase(key)
	for child: Node in palette_row.get_children():
		palette_row.remove_child(child)
		child.queue_free()
	for entry: Dictionary in session.definition.palette:
		var item: BookButton = _icon_button("color-%d" % int(entry.id), func() -> void: board.active_color = int(entry.id); set_tool("fill"), palette_row)
		item.swatch = Color(entry.color)
		item.tooltip_text = "Farbe %d wählen · aktiviert Füllen" % int(entry.id)
	_update_actions()
	_layout_book()

func select_puzzle(index: int) -> void:
	_cancel_interaction()
	if not _flush_current():
		return
	session.view_state = board.capture_view()
	session = sessions[index]
	board.session = session
	_layout_book()
	board.hover = Vector2i(-1, -1)
	board.restore_view(session.view_state)
	tool_label.text = "Werkzeug: " + ("Radierer" if board.eraser else ("Füllen · " + str(session.definition.palette[board.active_color - 1].symbol)))
	_update_palette()
	_update_status()
	open_puzzle()

func show_album() -> void:
	_cancel_interaction()
	if not _flush_current():
		return
	board.clear_clue_hover()
	information.hide()
	album.show()
	work.hide()
	ending.hide()
	album_button.hide()
	stress_label.visible = session.definition.get("stress", false)
	title.text = "Sammlung"
	open_button.text = session.album_title() + (" · ansehen" if session.completed else " · öffnen")
	repair_button.visible = slot_status[sessions.find(session)] in ["recovered", "backup_invalid"]
	repair_button.text = "Backup erneuern" if slot_status[sessions.find(session)] == "backup_invalid" else "Backup zum Speichern übernehmen"
	_update_status()
	for i: int in range(sessions.size()):
		choices[i].text = sessions[i].album_title() + (" · UI-Test" if i == 2 else "")
		album_previews[i].cells = sessions[i].player.cells.duplicate()
		album_previews[i].width = sessions[i].player.width
		album_previews[i].height = sessions[i].player.height
		album_previews[i].palette = sessions[i].definition.palette
		album_previews[i].visible = not sessions[i].completed
		album_previews[i].queue_redraw()
		album_reveals[i].payload = sessions[i].reveal()
		album_reveals[i].visible = sessions[i].completed
		album_reveals[i].queue_redraw()
		album_slot_status[i].text = "Backup geladen" if slot_status[i] == "recovered" else ("Backup beschädigt" if slot_status[i] == "backup_invalid" else ("Speicherfehler" if slot_status[i] == "error" or not slot_errors[i].is_empty() else ""))
		album_slot_status[i].visible = not album_slot_status[i].text.is_empty()
	album_mini.cells = session.player.cells.duplicate()
	album_mini.width = session.player.width
	album_mini.height = session.player.height
	album_mini.palette = session.definition.palette
	album_mini.visible = not session.completed
	album_picture.visible = session.completed
	album_picture.payload = session.reveal()
	album_picture.queue_redraw()
	album_mini.queue_redraw()
	_layout_book()

func open_puzzle() -> void:
	information.hide()
	album.hide()
	album_button.show()
	work.visible = not session.completed
	ending.visible = session.completed
	stress_label.visible = session.definition.get("stress", false)
	title.text = session.album_title()
	_layout_book()
	refresh()

func refresh() -> void:
	if mini == null or undo_button == null:
		return
	_update_actions()
	mini.cells = session.visible_cells()
	mini.width = session.player.width
	mini.height = session.player.height
	mini.palette = session.definition.palette
	mini.view_rect = board.view.normalized_view()
	mini.queue_redraw()
	board.queue_redraw()
	zoom_label.text = "Zoom %d %%" % roundi(board.view.cell_size / 24 * 100)
	if board is FullViewBoard and (not board.layout_valid or board.glyph_risk or board.view.cell_size < 16):
		zoom_label.text += " · " + ("Zu wenig Platz" if not board.layout_valid else "Kleine / eng stehende Hinweise")
	undo_button.disabled = session.gesture.active or session.player.cursor == 0
	redo_button.disabled = session.gesture.active or session.player.cursor == session.player.history.size()
	if session.completed and work.visible:
		work.hide()
		ending.show()
		title.text = session.album_title()
		_layout_book()
	completion_title.text = session.album_title() if session.completed else ""
	reveal_view.payload = session.reveal()
	reveal_view.solved = session.definition.solution if session.completed else []
	reveal_view.palette = session.definition.palette
	reveal_view.queue_redraw()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and board != null:
		_cancel_interaction()
	if what == NOTIFICATION_WM_CLOSE_REQUEST and board != null:
		leave_app()

func _on_commit() -> void:
	_save_current()

func _schedule_view_save() -> void:
	if save_timer != null:
		save_timer.start()

func _undo() -> void:
	board.clear_effects()
	var old: int = session.player.cursor
	session.undo()
	if session.player.cursor != old:
		_save_current()
	refresh()

func _redo() -> void:
	board.clear_effects()
	var old: int = session.player.cursor
	session.redo()
	if session.player.cursor != old:
		_save_current()
	refresh()

func _save_current() -> bool:
	if store == null or board == null or session == null:
		return true
	if save_timer != null:
		save_timer.stop()
	session.view_state = board.capture_view()
	save_error = "Backup vor weiterem Speichern bewusst übernehmen." if slot_status[sessions.find(session)] == "recovered" else store.write_slot(session, session.view_state)
	slot_errors[sessions.find(session)] = save_error
	if save_error.is_empty():
		slot_status[sessions.find(session)] = "loaded"
	else:
		var disk_state: String = str(store.load_slot(session.definition).status)
		if disk_state in ["recovered", "backup_invalid"]:
			slot_status[sessions.find(session)] = disk_state
	_update_status()
	return save_error.is_empty()

func _flush_current() -> bool:
	if (save_timer != null and not save_timer.is_stopped()) or (board != null and session != null and (board.capture_view() != session.view_state or not slot_errors[sessions.find(session)].is_empty())):
		return _save_current()
	return true

func _update_status() -> void:
	if status_label == null or session == null:
		return
	var previous_visibility: bool = status_label.visible
	var previous_repair: bool = work_repair_button.visible if work_repair_button != null else false
	var state: String = slot_status[sessions.find(session)]
	var error: String = slot_errors[sessions.find(session)]
	status_label.text = "Speicherfehler: " + error if not error.is_empty() else ("Backup geladen; Primärstand beschädigt. Vor weiterem Speichern Backup bewusst übernehmen." if state == "recovered" else ("Backup beschädigt; gültiger Primärstand geladen. Backup vor weiterem Speichern bewusst erneuern." if state == "backup_invalid" else ("Speicherdaten ungültig. Nur bestätigter Reset dieses Blatts ist möglich." if state == "error" else "")))
	status_label.visible = not status_label.text.is_empty()
	status_label.add_theme_color_override("font_color", Color("682e24"))
	if work_repair_button != null:
		work_repair_button.visible = state in ["recovered", "backup_invalid"] and not album.visible
		work_repair_button.text = "Backup erneuern" if state == "backup_invalid" else "Backup zum Speichern übernehmen"
	if work != null and work.visible and (previous_visibility != status_label.visible or previous_repair != work_repair_button.visible):
		_layout_book()

func _ask_reset() -> void:
	_cancel_interaction()
	reset_dialog.popup_centered()

func _reset_selected() -> void:
	var index: int = sessions.find(session)
	var id: String = str(session.definition.id).to_lower().replace("-", "")
	if save_timer != null:
		save_timer.stop()
	var error: String = store.reset_slot(id)
	if not error.is_empty():
		save_error = error
		slot_errors[index] = error
		_update_status()
		return
	sessions[index] = Session.new(session.definition)
	session = sessions[index]
	slot_status[index] = "fresh"
	slot_errors[index] = ""
	board.session = session
	board.restore_view(session.view_state)
	save_error = ""
	show_album()

func _ask_repair() -> void:
	_cancel_interaction()
	repair_dialog.title = "Backup erneuern?" if slot_status[sessions.find(session)] == "backup_invalid" else "Backup übernehmen?"
	repair_dialog.dialog_text = "Das beschädigte Backup wird entfernt und aus dem gültigen Primärstand neu erstellt." if slot_status[sessions.find(session)] == "backup_invalid" else "Der beschädigte Primärstand dieses Blatts wird durch das gültige Backup ersetzt."
	repair_dialog.get_ok_button().text = "Erneuern" if slot_status[sessions.find(session)] == "backup_invalid" else "Übernehmen"
	repair_dialog.popup_centered()

func _repair_selected() -> void:
	var error: String = store.discard_invalid_backup(session.definition) if slot_status[sessions.find(session)] == "backup_invalid" else store.repair_from_backup(session.definition)
	if error.is_empty():
		slot_status[sessions.find(session)] = "loaded"
		save_error = ""
		slot_errors[sessions.find(session)] = ""
		_save_current()
	else:
		save_error = error
		slot_errors[sessions.find(session)] = error
	show_album()

func leave_app() -> void:
	_cancel_interaction()
	if _flush_current():
		get_tree().quit()

static func label(text: String, font_size: int) -> Label:
	var item: Label = Label.new()
	item.text = text
	item.add_theme_font_size_override("font_size", font_size)
	if font_size >= 26:
		var heading: FontVariation = FontVariation.new()
		heading.base_font = TITLE_FONT
		heading.variation_opentype = {"wght":600.0}
		item.add_theme_font_override("font",heading)
	return item

static func button(text: String, action: Callable) -> Button:
	var item: Button = Button.new()
	item.text = text
	item.focus_mode = Control.FOCUS_NONE
	item.pressed.connect(action)
	return item

func _smoke() -> void:
	if board is ChalkboardBoard:
		var digest: HashingContext = HashingContext.new()
		digest.start(HashingContext.HASH_SHA256)
		digest.update(ChalkboardBoard.Fonts.CHALKBOARD.data)
		if digest.finish().hex_encode() != ChalkboardBoard.Fonts.SHA256:
			push_error("ZS2 selected embedded font bytes differ")
			get_tree().quit(10)
			return
		if not OS.has_feature("editor") and (ResourceLoader.exists("res://study/main.tscn") or ResourceLoader.exists("res://study/fonts/BaksoDaging-Regular.ttf")):
			push_error("ZS2 regular export contains the isolated study")
			get_tree().quit(11)
			return
		print("ZS2_REGULAR_RESOURCES_OK Chalkboard=", ChalkboardBoard.Fonts.SHA256)
	if BODY_FONT.get_font_name() != "IBM Plex Sans" or TITLE_FONT.get_font_name() != "Fraunces" or surface.ART.get_width() != 2560:
		push_error("Z2 bundled offline resource mismatch")
		get_tree().quit(8)
		return
	print("Z2_OFFLINE_RESOURCES body=",BODY_FONT.get_font_name()," title=",TITLE_FONT.get_font_name()," A_dimensions=",surface.ART.get_size())
	if DisplayServer.get_name() == "headless":
		get_window().size = Vector2i(1920, 1080)
	else:
		var outer: Rect2i = Rect2i(DisplayServer.window_get_position_with_decorations(), DisplayServer.window_get_size_with_decorations())
		var usable: Rect2i = DisplayServer.screen_get_usable_rect()
		print("P1_WINDOW_INFO client=", get_window().size, " outer=", outer, " usable=", usable, " screen=", DisplayServer.screen_get_size())
		if not usable.encloses(outer):
			push_error("Decorated start window exceeds usable monitor area")
			get_tree().quit(7)
			return
	for i: int in range(sessions.size()):
		select_puzzle(i)
		await get_tree().process_frame
		await get_tree().process_frame
		var cell: Vector2i = board.view.hit(board.view.viewport.get_center())
		var point: Vector2 = board.view.cell_rect(cell).get_center()
		board.pointer_press(point, MOUSE_BUTTON_LEFT)
		board.pointer_release(point, true)
		if session.player.cells.count(1) != 1 or session.completed or not session.reveal().is_empty():
			get_tree().quit(3)
			return
		_undo()
		show_information("settings")
		if not information.visible or work.visible:
			get_tree().quit(9)
			return
		return_to_work()
	show_album()
	print("P1_START_OK: nine fixtures -> mouse -> undo -> album; isolated persistence")
	get_tree().quit(0)

func _icon_button(id: String, action: Callable, parent: Control) -> BookButton:
	var item: BookButton = BookButton.new()
	item.action_id = id
	item.name = id
	if not id.begins_with("color-"):
		item.image = load("res://art/book/" + id + ".svg")
		var icons: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/book/icons.json"))
		item.tooltip_text = icons[id][1]
	item.pressed.connect(action)
	parent.add_child(item)
	actions[id] = item
	return item

func create_board() -> Board:
	return FullViewBoard.new()

func _build_work() -> void:
	work = Control.new()
	work.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_child(work)
	board = create_board()
	board.book_layout = true
	board.session = session
	board.edited.connect(refresh)
	board.committed.connect(_on_commit)
	board.view_changed.connect(_schedule_view_save)
	board.viewport_layout_requested.connect(_layout_book)
	board.pointed.connect(func(cell: Vector2i) -> void: coordinate.text = "Zeile %d · Spalte %d" % [cell.y+1,cell.x+1])
	work.add_child(board)
	sidebar = Control.new()
	sidebar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	work.add_child(sidebar)
	mini_title = label("Dein Stand",12)
	sidebar.add_child(mini_title)
	mini = Miniature.new()
	mini.interactive = false
	sidebar.add_child(mini)
	coordinate = label("Zeile – · Spalte –",13)
	coordinate.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sidebar.add_child(coordinate)
	tool_label = label("",12)
	sidebar.add_child(tool_label)
	zoom_label = label("",12)
	sidebar.add_child(zoom_label)
	palette_row = Control.new()
	palette_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sidebar.add_child(palette_row)
	for id: String in ["fill","erase"]:
		_icon_button(id,set_tool.bind(id),work)
	undo_button = _icon_button("undo",_undo,work)
	redo_button = _icon_button("redo",_redo,work)
	_icon_button("minus",func() -> void: board.zoom(-1,board.view.viewport.get_center()),work)
	_icon_button("plus",func() -> void: board.zoom(1,board.view.viewport.get_center()),work)
	_icon_button("fit",board.fit_all,work)
	actions["fit"].tooltip_text = "Einpassen"
	_icon_button("work",board.working_size,work)
	_icon_button("help",show_information.bind("help"),work)
	_icon_button("menu",show_information.bind("settings"),work)
	_icon_button("nav-information",show_information.bind("settings"),work)
	album_button = _icon_button("nav-album",show_album,page)
	# Kept on the visible page even when a failed flush blocks access to N1.
	work_repair_button = button("Backup zum Speichern übernehmen",_ask_repair)
	page.add_child(work_repair_button)

func _build_information() -> void:
	information = Control.new()
	information.mouse_filter = Control.MOUSE_FILTER_STOP
	page.add_child(information)
	_icon_button("nav-work",return_to_work,information)
	var settings_access: Button = _text_button("Einstellungen",_information_section.bind("settings"))
	settings_access.name = "settings-access"
	information.add_child(settings_access)
	var help_access: Button = _text_button("Hilfe",_information_section.bind("help"))
	help_access.name = "help-access"
	information.add_child(help_access)
	info_scroll = ScrollContainer.new()
	info_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	information.add_child(info_scroll)
	var content: VBoxContainer = VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info_scroll.add_child(content)
	settings_panel = VBoxContainer.new()
	settings_panel.add_theme_constant_override("separation",16)
	content.add_child(settings_panel)
	settings_panel.add_child(label("Einstellungen",26))
	ui_scale_button = _text_button("UI 100 %",func() -> void: set_ui_scale(1.25 if ui_scale == 1 else 1.0))
	settings_panel.add_child(ui_scale_button)
	settings_panel.add_child(label("Rätselansicht",20))
	view_choice = OptionButton.new()
	view_choice.name = "puzzle-view"
	view_choice.add_item("Rasteransicht")
	view_choice.add_item("Gesamtansicht mit allen Hinweisen")
	view_choice.item_selected.connect(set_puzzle_view)
	settings_panel.add_child(view_choice)
	var explanation: Label = label("Rasteransicht hält das ganze Raster sichtbar; lange Hinweise lassen sich einzeln verschieben. Die Gesamtansicht zeigt alle Hinweise und kann kleinere Zellen benötigen.",16)
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	settings_panel.add_child(explanation)
	clue_reset_button = _text_button("Hinweise rasterseitig ausrichten",board.reset_clue_pan)
	settings_panel.add_child(clue_reset_button)
	clue_completion_toggle = CheckBox.new()
	clue_completion_toggle.text = "Erfüllte Hinweise markieren"
	clue_completion_toggle.button_pressed = mark_completed_clues
	clue_completion_toggle.add_theme_color_override("font_color",BookButton.INK)
	clue_completion_toggle.toggled.connect(set_clue_completion)
	settings_panel.add_child(clue_completion_toggle)
	animation_toggle = CheckBox.new()
	animation_toggle.text = "Zellanimationen"
	animation_toggle.button_pressed = true
	animation_toggle.add_theme_color_override("font_color", BookButton.INK)
	animation_toggle.toggled.connect(func(enabled: bool) -> void: board.set_animations(enabled))
	settings_panel.add_child(animation_toggle)
	settings_panel.add_child(_text_button("Beenden",leave_app))
	help_panel = VBoxContainer.new()
	help_panel.add_theme_constant_override("separation",16)
	content.add_child(help_panel)
	help_panel.add_child(label("Maus und Hinweise",26))
	var help_text: Label = label("Links: Farbe setzen, Füllung zurücknehmen, X in Farbe umwandeln.\nRechts: X setzen, X zurücknehmen, Füllung in X umwandeln.\n\nStart auf unbekannt schützt X und Füllungen. Bewusste Umwandlung startet auf X (links) oder Füllung (rechts). Rücknahmestriche löschen nur ihren Starttyp.\n\nModus und Farbe bleiben im Strich fest. Zurückziehen verkürzt die Vorschau. Bei Rückkehr zur Startzelle lässt sich die Achse neu wählen. Loslassen übernimmt einen Schritt; Undo/Redo nimmt ganze Striche zurück.\n\nRad und +/−: Zoom bis zur Vollsichtgrenze. Einpassen passt innerhalb der gewählten Rätselansicht ein; Arbeitsgröße stellt die gewünschte Standardgröße wieder her. Raster und eigene Miniatur bleiben fest. Die Rätselansicht wird nur unter Einstellungen gewählt.\n\nMittlere Taste auf überlaufenden Hinweisen: nur die angefasste Zeile waagerecht oder Spalte senkrecht ziehen. Loslassen rastet ein. … markiert verborgene Zahlen; darüberfahren zeigt die vollständige Folge.\n\nDie Vorschau bleibt statisch und heller. Beim Loslassen wird alles sofort übernommen; die Striche zeichnen sich vom Start zum Ende in höchstens 390 ms. Entfernen dauert 120 ms. Zellanimationen lassen sich für diese Sitzung abschalten.\n\nEsc, Fokusverlust oder Drücken der anderen Maustaste verwirft die laufende Zellgeste. Nach Gegentasten-Abbruch beide Tasten loslassen, dann neu beginnen.\nHinweise: normal = offen; abgeschwächt = eindeutig vollständig gesetzt; durchgestrichen = zusätzlich an beiden Enden abgegrenzt. X, echter Rasterrand oder direkt andere Füllfarbe zählen; unbekannte Nachbarn und Ausschnittränder nicht. Nur die eigene vollständige Linie zählt – keine Fehlerprüfung der Lösung. Der Schalter gilt für diese Sitzung.\n\nDer Arbeitsstand wird lokal gespeichert. Speicherfehler bleiben sichtbar; eine Backupübernahme braucht deine Bestätigung.",16)
	help_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	help_panel.add_child(help_text)
	information.hide()
	_information_section("settings")

func _text_button(caption: String, action: Callable) -> BookButton:
	var item: BookButton = BookButton.new()
	item.text = caption
	item.pressed.connect(action)
	return item

func _cancel_interaction() -> void:
	board.cancel_gesture()
	board.clear_pointer_hover()
	if mini != null:
		mini.dragging = false

func show_information(section: String = "settings") -> void:
	_cancel_interaction()
	if not _flush_current():
		return
	information_origin = "album" if album.visible else ("ending" if ending.visible else "work")
	work.hide()
	album.hide()
	ending.hide()
	information.show()
	album_button.hide()
	_information_section(section)
	title.text = "Information" if information_origin == "album" else "Information / " + str(session.definition.id)
	_layout_book()

func _information_section(section: String) -> void:
	information_section = section
	settings_panel.visible = section == "settings"
	help_panel.visible = section == "help"
	info_scroll.scroll_vertical = 0
	# One shared settings instance; shortcuts change only the visible section.
	if information.visible:
		var target: Control = ui_scale_button if section == "settings" else information.get_node("help-access")
		target.focus_mode = Control.FOCUS_ALL
		target.grab_focus()

func return_to_work() -> void:
	_cancel_interaction()
	if not _flush_current():
		return
	if information_origin == "album":
		show_album()
	else:
		open_puzzle()

func set_puzzle_view(index: int) -> void:
	_cancel_interaction()
	board.set_mode("V" if index == 1 else "G")
	view_choice.select(1 if board.mode == "V" else 0)
	refresh()

func _update_actions() -> void:
	if board == null or tool_label == null:
		return
	var selected_tool: String = "erase" if board.eraser else "fill"
	tool_label.text = ("Radierer" if board.eraser else "Füllen") + " · Farbe %d" % board.active_color
	for key: String in actions:
		if not is_instance_valid(actions[key]):
			continue
		var item: BookButton = actions[key]
		item.selected = key == selected_tool or key == "color-%d" % board.active_color
		item.ui_scale = ui_scale
		item.queue_redraw()

func _place(item: Control, box: Rect2) -> void:
	item.position = box.position
	item.size = box.size

func _layout_book() -> void:
	if laying_out or board == null or information == null or ui_scale_button == null:
		return
	if size.x < 1280 or size.y < 720:
		return
	laying_out = true
	var u: float = ui_scale
	var material: Rect2 = surface.material_rect()
	var o: Vector2 = material.position
	var w: float = material.size.x
	var h: float = material.size.y
	var compact: bool = w < 1700
	var hit: float = 44*u
	work.position = Vector2.ZERO
	work.size = Vector2(size.x,size.y-28)
	sidebar.position = Vector2.ZERO
	sidebar.size = work.size
	var left: float = 68*u
	var rail: float = w-260*u
	var top: float = maxf(h*0.039+45*u+6*u,82*u)
	var bottom: float = h-68*u
	var rail_top: float = top
	if work.visible and status_label.visible:
		top += 106*u
		if work_repair_button.visible:
			top += 50*u
	_place(board,Rect2(o+Vector2(left,top),Vector2(rail-left-24*u,bottom-top-10*u)))
	board._layout()
	var mini_extent: float = (100.0 if (bottom-rail_top)/u < 600 else 132.0)*u
	var mini_position: Vector2 = o+Vector2(rail+12*u,rail_top+30*u)
	_place(mini,Rect2(mini_position,Vector2.ONE*mini_extent))
	_place(mini_title,Rect2(mini_position-Vector2(0,26*u),Vector2(180,24)*u))
	_place(coordinate,Rect2(mini_position+Vector2(0,mini_extent+14*u),Vector2(190,44)*u))
	var palette_pos: Vector2 = mini_position+Vector2(0,mini_extent+66*u)
	_place(palette_row,Rect2(palette_pos,Vector2(110,110)*u))
	for i: int in range(palette_row.get_child_count()):
		_place(palette_row.get_child(i),Rect2(Vector2(i%2,i/2)*54*u,Vector2.ONE*hit))
	_place(zoom_label,Rect2(mini_position+Vector2(0,mini_extent+188*u),Vector2(180,52)*u))
	zoom_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_place(tool_label,Rect2(mini_position+Vector2(0,mini_extent+244*u),Vector2(200,24)*u))
	var tools_origin: Vector2 = o+Vector2(left,bottom)
	surface.wells.clear()
	var ids: Array[String] = ["fill","erase","undo","redo","minus","plus","fit","work"]
	for i: int in range(ids.size()):
		_place(actions[ids[i]],Rect2(tools_origin+Vector2(i*52*u,0),Vector2.ONE*hit))
	for group: Vector2i in [Vector2i(0,2),Vector2i(2,2),Vector2i(4,4)]:
		surface.wells.append(Rect2(tools_origin+Vector2(group.x*52*u-3*u,-3*u),Vector2((group.y-1)*52*u+hit+6*u,hit+6*u)))
	var nav_x: float = w-(187.5 if compact else 150)
	for i: int in range(3):
		_place(actions[["help","menu","nav-information"][i]],Rect2(o+Vector2(nav_x-(2-i)*58*u,h/30),Vector2.ONE*hit))
	_place(album_button,Rect2(o+Vector2(w/320,h*7/72),Vector2.ONE*hit))
	_place(title,Rect2(o+Vector2(w*0.043,h*0.039),Vector2(w*0.6,45*u)))
	stress_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_place(stress_label,Rect2(mini_position+Vector2(0,mini_extent+270*u),Vector2(180,64)*u))
	_place(album,Rect2(o+Vector2(90,130),Vector2(w-180,h-200)))
	for choice: Button in choices:
		choice.custom_minimum_size.y = 44 * ui_scale
		choice.add_theme_font_size_override("font_size", int(16 * ui_scale))
	_place(ending,Rect2(o+Vector2(100,120),Vector2(w-200,h-180)))
	_place(information,Rect2(Vector2.ZERO,size))
	_place(actions["nav-work"],Rect2(o+Vector2(100,110),Vector2.ONE*hit))
	_place(information.get_node("settings-access"),Rect2(o+Vector2(180,110),Vector2(210*u,hit)))
	_place(information.get_node("help-access"),Rect2(o+Vector2(410*u,110),Vector2(140*u,hit)))
	_place(info_scroll,Rect2(o+Vector2(180,190),Vector2(w-360,h-300)))
	for item: Control in [ui_scale_button,clue_reset_button,clue_completion_toggle]:
		item.custom_minimum_size.y = hit
	for item: Node in information.find_children("*","Button",true,false):
		item.custom_minimum_size.y = hit
		if item is BookButton:
			item.ui_scale = u
			item.queue_redraw()
	# Local error card stays reachable on a blocked work->information transition.
	_place(status_label,Rect2(o+Vector2(180,h-104 if information.visible else 85),Vector2(w-660 if information.visible else w-550,70*u)))
	_place(work_repair_button,Rect2(o+Vector2(w-430,h-(80 if information.visible else 170)*u),Vector2(340*u,hit)))
	surface.card = Rect2(mini_position-Vector2(10,34),Vector2(mini_extent+20,mini_extent+44))
	surface.miniature = mini.get_rect()
	surface.palette = Rect2(palette_pos-Vector2(6,6),Vector2(56,56)*u if session.definition.palette.size()==1 else Vector2(110,110)*u)
	surface.information = information.visible
	surface.work_visible = work.visible and page.visible
	surface.queue_redraw()
	_update_status()
	_update_actions()
	laying_out = false
