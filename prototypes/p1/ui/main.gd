extends Control
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
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

func _ready() -> void:
	get_window().min_size = Vector2i(1280, 720)
	var data: Dictionary = Definition.load_f01()
	var error: String = Definition.validate(data)
	if not error.is_empty():
		push_error(error)
		get_tree().quit(2)
		return
	session = Session.new(data)
	_build()
	show_album()
	if OS.get_cmdline_user_args().has("--p1-smoke"):
		call_deferred("_smoke")

func _build() -> void:
	var theme_resource: Theme = Theme.new()
	theme_resource.default_font_size = 18
	theme_resource.set_color("font_color", "Label", Color("343f42"))
	for state: String in ["normal", "hover", "pressed", "disabled"]:
		var style: StyleBoxFlat = StyleBoxFlat.new()
		style.bg_color = Color("e3e7d6") if state == "normal" else Color("d1d9be")
		if state == "disabled":
			style.bg_color = Color("e5e1d8")
		style.content_margin_left = 18
		style.content_margin_right = 18
		style.content_margin_top = 12
		style.content_margin_bottom = 12
		style.corner_radius_top_left = 6
		style.corner_radius_bottom_right = 6
		theme_resource.set_stylebox(state, "Button", style)
		var color_key: String = "font_color" if state == "normal" else "font_" + state + "_color"
		theme_resource.set_color(color_key, "Button", Color("777a70") if state == "disabled" else Color("343f42"))
	theme = theme_resource
	var margin: MarginContainer = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 24)
	add_child(margin)
	var page: VBoxContainer = VBoxContainer.new()
	page.add_theme_constant_override("separation", 14)
	margin.add_child(page)
	var header: HBoxContainer = HBoxContainer.new()
	page.add_child(header)
	title = label("picross  /  Mein Probealbum", 28)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	album_button = button("Zum Album", show_album)
	header.add_child(album_button)
	header.add_child(button("Beenden", func() -> void: get_tree().quit()))
	album = VBoxContainer.new()
	album.size_flags_vertical = Control.SIZE_EXPAND_FILL
	album.add_theme_constant_override("separation", 22)
	page.add_child(album)
	album.add_child(label("Ein leeres Blatt. Ein Bild zum Entdecken.", 32))
	album.add_child(label("Blatt 01 · Monochrom · 20 × 20", 20))
	album_mini = Miniature.new()
	album_mini.custom_minimum_size = Vector2(260, 260)
	album.add_child(album_mini)
	album_picture = Reveal.new()
	album_picture.paired = false
	album_picture.custom_minimum_size = Vector2(260, 260)
	album.add_child(album_picture)
	open_button = button("Blatt öffnen", open_puzzle)
	open_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	album.add_child(open_button)
	album.add_child(label("Dein Arbeitsstand bleibt beim Wechsel ins Album erhalten.\nBeim Beenden endet diese Sitzung; es gibt noch keine Speicherung.", 18))
	work = HBoxContainer.new()
	work.size_flags_vertical = Control.SIZE_EXPAND_FILL
	work.add_theme_constant_override("separation", 24)
	page.add_child(work)
	board = Board.new()
	board.session = session
	board.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	board.custom_minimum_size = Vector2(810, 570)
	board.edited.connect(refresh)
	board.pointed.connect(func(cell: Vector2i) -> void:
		coordinate.text = "Zeile %02d · Spalte %02d" % [cell.y + 1, cell.x + 1] if cell.x >= 0 else "Zeile – · Spalte –")
	work.add_child(board)
	var sidebar: VBoxContainer = VBoxContainer.new()
	sidebar.custom_minimum_size.x = 280
	sidebar.add_theme_constant_override("separation", 8)
	work.add_child(sidebar)
	sidebar.add_child(label("Dein Arbeitsstand", 22))
	mini = Miniature.new()
	mini.custom_minimum_size = Vector2(160, 160)
	sidebar.add_child(mini)
	coordinate = label("Zeile – · Spalte –", 18)
	sidebar.add_child(coordinate)
	tool_label = label("Werkzeug: Füllen · A", 18)
	sidebar.add_child(tool_label)
	var tools_row: HBoxContainer = HBoxContainer.new()
	sidebar.add_child(tools_row)
	tools_row.add_child(button("■ Füllen", func() -> void:
		board.eraser = false
		tool_label.text = "Werkzeug: Füllen · A"))
	tools_row.add_child(button("Radierer", func() -> void:
		board.eraser = true
		tool_label.text = "Werkzeug: Radierer"))
	var history_row: HBoxContainer = HBoxContainer.new()
	sidebar.add_child(history_row)
	undo_button = button("Rückgängig", func() -> void:
		session.undo()
		refresh())
	redo_button = button("Wiederholen", func() -> void:
		session.redo()
		refresh())
	history_row.add_child(undo_button)
	history_row.add_child(redo_button)
	sidebar.add_child(label("Links: Werkzeug · Rechts: leer\nZiehen: gerader Strich\nZurückziehen: Strich verkürzen\nEsc/Fokusverlust: Vorschau verwerfen\nEinträge geschützt – erst radieren.", 14))
	ending = VBoxContainer.new()
	ending.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ending.add_theme_constant_override("separation", 12)
	page.add_child(ending)
	completion_title = label("", 32)
	ending.add_child(completion_title)
	ending.add_child(label("Prototyp ohne Wertung · Dein Bild ist im Album.", 20))
	reveal_view = Reveal.new()
	reveal_view.custom_minimum_size = Vector2(900, 300)
	reveal_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ending.add_child(reveal_view)
	ending.add_child(button("Zurück ins Album", show_album))
	page.add_child(label("P1.1 · Mausprobe  /  Nur diese Sitzung  /  Ohne Wertung und Fehlerhilfe", 16))

func show_album() -> void:
	board.cancel_gesture()
	album.show()
	work.hide()
	ending.hide()
	album_button.hide()
	title.text = "picross  /  Mein Probealbum"
	open_button.text = session.album_title() + (" · ansehen" if session.completed else " · öffnen")
	album_mini.cells = session.player.cells.duplicate()
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
	title.text = session.album_title()
	refresh()

func refresh() -> void:
	if mini == null:
		return
	mini.cells = session.visible_cells()
	mini.queue_redraw()
	board.queue_redraw()
	undo_button.disabled = session.gesture.active or session.player.cursor == 0
	redo_button.disabled = session.gesture.active or session.player.cursor == session.player.history.size()
	if session.completed and work.visible:
		work.hide()
		ending.show()
		title.text = session.album_title()
	completion_title.text = session.album_title() if session.completed else ""
	reveal_view.payload = session.reveal()
	reveal_view.queue_redraw()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and board != null:
		board.cancel_gesture()

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
	# No saves or external data. Exercise real scene transitions and one input.
	open_puzzle()
	await get_tree().process_frame
	var point: Vector2 = board.view.cell_rect(Vector2i(0, 0)).get_center()
	board.pointer_press(point, MOUSE_BUTTON_LEFT)
	board.pointer_release(point, true)
	if session.player.cells[0] != 1 or session.completed or not session.reveal().is_empty():
		get_tree().quit(3)
		return
	session.undo()
	show_album()
	print("P1_START_OK: album -> board -> mouse -> undo -> album; no persistence")
	get_tree().quit(0)
