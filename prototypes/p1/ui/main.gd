extends Control
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
const SaveStore = preload("res://model/save_store.gd")
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
var session: Session
var board: Board
var mini: Miniature
var album_mini: Miniature
var album_picture: Reveal
var reveal_view: Reveal
var album: VBoxContainer
var work: HBoxContainer
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
var palette_row: HBoxContainer
var sidebar: VBoxContainer
var page: VBoxContainer
var minimum_message: Label
var clue_reset_button: Button
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

func _ready() -> void:
	get_tree().auto_accept_quit = false
	store = SaveStore.new(SaveStore.test_root_override if not SaveStore.test_root_override.is_empty() else "user://p1/saves")
	if DisplayServer.get_name() != "headless" and not OS.get_cmdline_user_args().has("--p1-capture"):
		var usable: Rect2i = DisplayServer.screen_get_usable_rect()
		var decorations: Vector2i = (DisplayServer.window_get_size_with_decorations() - DisplayServer.window_get_size()).max(Vector2i(16, 48))
		var client_offset: Vector2i = DisplayServer.window_get_position() - DisplayServer.window_get_position_with_decorations()
		get_window().size = bounded_start(usable, decorations)
		get_window().position = bounded_position(usable, get_window().size, decorations, client_offset)
	for id: String in ["f01", "f02", "f03"]:
		var data: Dictionary = Definition.load_fixture(id)
		var error: String = Definition.validate(data)
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
	theme.default_font_size = 16
	theme.set_color("font_color", "Label", Board.INK)
	for state: String in ["normal", "hover", "pressed", "disabled"]:
		var style: StyleBoxFlat = StyleBoxFlat.new()
		style.bg_color = Color("e3e7d6") if state == "normal" else Color("d1d9be")
		style.content_margin_left = 10
		style.content_margin_right = 10
		style.content_margin_top = 5
		style.content_margin_bottom = 5
		style.corner_radius_top_left = 5
		style.corner_radius_bottom_right = 5
		theme.set_stylebox(state, "Button", style)
		theme.set_color("font_color" if state == "normal" else "font_" + state + "_color", "Button", Board.INK)
	var margin: MarginContainer = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 16)
	add_child(margin)
	page = VBoxContainer.new()
	page.add_theme_constant_override("separation", 10)
	margin.add_child(page)
	var header: HBoxContainer = HBoxContainer.new()
	page.add_child(header)
	title = label("picross / Mein Probealbum", 24)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	header.add_child(button("UI 100 / 125 %", func() -> void: set_ui_scale(1.25 if ui_scale == 1.0 else 1.0)))
	album_button = button("Zum Album", show_album)
	header.add_child(album_button)
	header.add_child(button("Beenden", leave_app))
	status_label = label("", 16)
	page.add_child(status_label)
	stress_label = label("UI-Testdatensatz – Rätselqualität nicht abgenommen", 16)
	page.add_child(stress_label)
	album = VBoxContainer.new()
	album.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(album)
	album.add_child(label("Drei Blätter zum Entdecken", 28))
	var choice_row: HBoxContainer = HBoxContainer.new()
	album.add_child(choice_row)
	for i: int in range(sessions.size()):
		var slot_column: VBoxContainer = VBoxContainer.new()
		choice_row.add_child(slot_column)
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
	album.add_child(album_mini)
	album_picture = Reveal.new()
	album_picture.paired = false
	album_picture.custom_minimum_size = Vector2(240, 240)
	album.add_child(album_picture)
	open_button = button("Blatt öffnen", open_puzzle)
	open_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album.add_child(open_button)
	album.add_child(label("Jedes Blatt speichert den eigenen Arbeitsstand lokal.", 16))
	var reset_button: Button = button("Arbeitsstand zurücksetzen", _ask_reset)
	reset_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album.add_child(reset_button)
	repair_button = button("Backup zum Speichern übernehmen", _ask_repair)
	repair_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album.add_child(repair_button)
	reset_dialog = ConfirmationDialog.new()
	reset_dialog.title = "Arbeitsstand zurücksetzen?"
	reset_dialog.dialog_text = "Nur das ausgewählte Blatt wird vollständig zurückgesetzt."
	reset_dialog.confirmed.connect(_reset_selected)
	add_child(reset_dialog)
	repair_dialog = ConfirmationDialog.new()
	repair_dialog.title = "Backup übernehmen?"
	repair_dialog.dialog_text = "Der beschädigte Primärstand dieses Blatts wird durch das gültige Backup ersetzt."
	repair_dialog.confirmed.connect(_repair_selected)
	add_child(repair_dialog)
	work = HBoxContainer.new()
	work.size_flags_vertical = Control.SIZE_EXPAND_FILL
	work.add_theme_constant_override("separation", 16)
	page.add_child(work)
	board = Board.new()
	board.session = session
	board.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	board.edited.connect(refresh)
	board.committed.connect(_on_commit)
	board.view_changed.connect(_schedule_view_save)
	board.pointed.connect(func(cell: Vector2i) -> void: coordinate.text = "Zeile %d · Spalte %d" % [cell.y + 1, cell.x + 1])
	work.add_child(board)
	sidebar = VBoxContainer.new()
	sidebar.custom_minimum_size.x = 300
	work.add_child(sidebar)
	sidebar.add_child(label("Dein Arbeitsstand · ziehen zum Navigieren", 14))
	mini = Miniature.new()
	mini.custom_minimum_size = Vector2(156, 156)
	mini.interactive = true
	mini.navigated.connect(board.navigate_to)
	sidebar.add_child(mini)
	coordinate = label("Zeile – · Spalte –", 16)
	sidebar.add_child(coordinate)
	clue_reset_button = button("Hinweise rasterseitig ausrichten", board.reset_clue_pan)
	sidebar.add_child(clue_reset_button)
	var scroll: ScrollContainer = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sidebar.add_child(scroll)
	var controls: VBoxContainer = VBoxContainer.new()
	controls.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(controls)
	tool_label = label("Werkzeug: Füllen · A", 16)
	controls.add_child(tool_label)
	palette_row = HBoxContainer.new()
	controls.add_child(palette_row)
	var tool_row: HBoxContainer = HBoxContainer.new()
	controls.add_child(tool_row)
	tool_row.add_child(button("Füllen", set_tool.bind("fill")))
	tool_row.add_child(button("Radierer", set_tool.bind("erase")))
	tool_row.add_child(button("Hand", set_tool.bind("hand")))
	var history_row: HBoxContainer = HBoxContainer.new()
	controls.add_child(history_row)
	undo_button = button("Rückgängig", _undo)
	redo_button = button("Wiederholen", _redo)
	history_row.add_child(undo_button)
	history_row.add_child(redo_button)
	zoom_label = label("Arbeitszoom 100 %", 16)
	controls.add_child(zoom_label)
	var zoom_row: HBoxContainer = HBoxContainer.new()
	controls.add_child(zoom_row)
	zoom_row.add_child(button("−", func() -> void: board.zoom(-1, board.view.viewport.get_center())))
	zoom_row.add_child(button("+", func() -> void: board.zoom(1, board.view.viewport.get_center())))
	zoom_row.add_child(button("Gesamtansicht", board.fit_all))
	controls.add_child(button("Arbeitsgröße (100 %)", board.working_size))
	controls.add_child(label("Links: Farbe setzen / Füllung zurücknehmen\nRechts: Kreuz setzen / Kreuz zurücknehmen\nX ↔ Farbe wird direkt umgewandelt\nRad: Zoom · Mitte/Hand im Raster: verschieben\nMitte/Hand: angefasste Zeile ↔ / Spalte ↕\nEsc/Fokusverlust: Geste verwerfen\n…: verborgener Anfang/verborgenes Ende · Hover: vollständig", 14))
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
	page.add_child(label("P1.3 · Lokaler Arbeitsstand / Ohne Wertung und Fehlerhilfe", 14))
	minimum_message = label("Mindestens 1280 × 720 logische Fensterfläche benötigt.\nBitte das Fenster vergrößern oder die Anzeigeskalierung prüfen.", 20)
	minimum_message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	minimum_message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	minimum_message.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(minimum_message)
	_update_palette()

func _check_minimum() -> void:
	var small: bool = size.x < 1280 or size.y < 720
	minimum_message.visible = small
	page.visible = not small
	if small:
		board.cancel_gesture()

func set_ui_scale(value: float) -> void:
	ui_scale = value
	theme.default_font_size = roundi(16 * value)
	_scale_labels(self)
	sidebar.custom_minimum_size.x = 300 * value
	board.ui_scale = value
	board._layout()
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
	board.hand = tool == "hand"
	tool_label.text = "Werkzeug: " + ("Radierer" if board.eraser else ("Hand" if board.hand else "Füllen · " + str(session.definition.palette[board.active_color - 1].symbol)))
	if save_timer != null:
		_save_current()

func _update_palette() -> void:
	for child: Node in palette_row.get_children():
		palette_row.remove_child(child)
		child.queue_free()
	for entry: Dictionary in session.definition.palette:
		var item: Button = button(entry.symbol, func() -> void: board.active_color = int(entry.id); set_tool("fill"))
		item.add_theme_color_override("font_color", Color(entry.color).darkened(0.3))
		palette_row.add_child(item)

func select_puzzle(index: int) -> void:
	board.cancel_gesture()
	_flush_current()
	session.view_state = board.capture_view()
	session = sessions[index]
	board.session = session
	board.hover = Vector2i(-1, -1)
	board.restore_view(session.view_state)
	tool_label.text = "Werkzeug: " + ("Radierer" if board.eraser else ("Hand" if board.hand else "Füllen · " + str(session.definition.palette[board.active_color - 1].symbol)))
	_update_palette()
	_update_status()
	open_puzzle()

func show_album() -> void:
	board.cancel_gesture()
	_flush_current()
	board.clear_clue_hover()
	album.show()
	work.hide()
	ending.hide()
	album_button.hide()
	stress_label.visible = session.definition.get("stress", false)
	title.text = "picross / Mein Probealbum"
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

func open_puzzle() -> void:
	album.hide()
	album_button.show()
	work.visible = not session.completed
	ending.visible = session.completed
	stress_label.visible = session.definition.get("stress", false)
	title.text = session.album_title()
	refresh()

func refresh() -> void:
	if mini == null or undo_button == null:
		return
	mini.cells = session.visible_cells()
	mini.width = session.player.width
	mini.height = session.player.height
	mini.palette = session.definition.palette
	mini.view_rect = board.view.normalized_view()
	mini.queue_redraw()
	board.queue_redraw()
	zoom_label.text = ("Gesamtansicht " if board.overview else "Arbeitszoom ") + "%d %%" % roundi(board.view.cell_size / 24 * 100)
	undo_button.disabled = session.gesture.active or session.player.cursor == 0
	redo_button.disabled = session.gesture.active or session.player.cursor == session.player.history.size()
	if session.completed and work.visible:
		work.hide()
		ending.show()
		title.text = session.album_title()
	completion_title.text = session.album_title() if session.completed else ""
	reveal_view.payload = session.reveal()
	reveal_view.solved = session.definition.solution if session.completed else []
	reveal_view.palette = session.definition.palette
	reveal_view.queue_redraw()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and board != null:
		board.cancel_gesture()
	if what == NOTIFICATION_WM_CLOSE_REQUEST and board != null:
		leave_app()

func _on_commit() -> void:
	_save_current()

func _schedule_view_save() -> void:
	if save_timer != null:
		save_timer.start()

func _undo() -> void:
	var old: int = session.player.cursor
	session.undo()
	if session.player.cursor != old:
		_save_current()
	refresh()

func _redo() -> void:
	var old: int = session.player.cursor
	session.redo()
	if session.player.cursor != old:
		_save_current()
	refresh()

func _save_current() -> void:
	if store == null or board == null or session == null:
		return
	if save_timer != null:
		save_timer.stop()
	session.view_state = board.capture_view()
	save_error = store.write_slot(session, session.view_state)
	slot_errors[sessions.find(session)] = save_error
	if save_error.is_empty():
		slot_status[sessions.find(session)] = "loaded"
	_update_status()

func _flush_current() -> void:
	if (save_timer != null and not save_timer.is_stopped()) or (board != null and session != null and (board.capture_view() != session.view_state or not slot_errors[sessions.find(session)].is_empty())):
		_save_current()

func _update_status() -> void:
	if status_label == null or session == null:
		return
	var state: String = slot_status[sessions.find(session)]
	var error: String = slot_errors[sessions.find(session)]
	status_label.text = "Speicherfehler: " + error if not error.is_empty() else ("Backup geladen; Primärstand beschädigt. Vor weiterem Speichern Backup bewusst übernehmen." if state == "recovered" else ("Backup beschädigt; gültiger Primärstand geladen. Backup vor weiterem Speichern bewusst erneuern." if state == "backup_invalid" else ("Speicherdaten ungültig. Nur bestätigter Reset dieses Blatts ist möglich." if state == "error" else "")))
	status_label.visible = not status_label.text.is_empty()
	status_label.add_theme_color_override("font_color", Color("9d2e24"))

func _ask_reset() -> void:
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
	repair_dialog.title = "Backup erneuern?" if slot_status[sessions.find(session)] == "backup_invalid" else "Backup übernehmen?"
	repair_dialog.dialog_text = "Das beschädigte Backup wird entfernt und aus dem gültigen Primärstand neu erstellt." if slot_status[sessions.find(session)] == "backup_invalid" else "Der beschädigte Primärstand dieses Blatts wird durch das gültige Backup ersetzt."
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
	board.cancel_gesture()
	_flush_current()
	get_tree().quit()

static func label(text: String, font_size: int) -> Label:
	var item: Label = Label.new()
	item.text = text
	item.add_theme_font_size_override("font_size", font_size)
	return item

static func button(text: String, action: Callable) -> Button:
	var item: Button = Button.new()
	item.text = text
	item.focus_mode = Control.FOCUS_NONE
	item.pressed.connect(action)
	return item

func _smoke() -> void:
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
	for i: int in range(3):
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
	show_album()
	print("P1_START_OK: three fixtures -> mouse -> undo -> album; isolated persistence")
	get_tree().quit(0)
