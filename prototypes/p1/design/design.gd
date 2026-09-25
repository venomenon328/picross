extends Control
## Z1-only shell: no Main, SaveStore, timer, persistence or reveal path.
const Demo = preload("res://design/demo.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const Miniature = preload("res://ui/miniature.gd")
const Backdrop = preload("res://design/backdrop.gd")
var session: Session
var board: Board
var mini: Miniature
var backdrop: Backdrop
var variant: int = 0
var fixture: int = 1
var ui_scale: float = 1.0
var mark_completed: bool = true
var panel: Panel
var heading: Label
var subtitle: Label
var mini_title: Label
var coordinate: Label
var tool_title: Label
var zoom_label: Label
var note: Label
var help_button: Button
var menu_button: Button
var undo_button: Button
var redo_button: Button
var zoom_out: Button
var zoom_in: Button
var fit_button: Button
var work_button: Button
var palette_buttons: Array[Button] = []
var tool_buttons: Array[Button] = []
var variant_choice: OptionButton
var fixture_choice: OptionButton
var reset_button: Button
var test_bar: Panel
var test_label: Label
var overlay: ColorRect
var drawer: Panel
var drawer_title: Label
var drawer_close: Button
var help_text: Label
var ui_button: Button
var clue_button: Button
var completion_button: Button
var exit_button: Button
var minimum: Label
var overlay_kind: String = ""

func _ready() -> void:
	get_window().title = "picross · Z1 Entwurfsvergleich"
	session = Demo.create(fixture)
	backdrop = Backdrop.new()
	add_child(backdrop)
	panel = Panel.new()
	add_child(panel)
	board = Board.new()
	board.session = session
	board.edited.connect(refresh)
	board.view_changed.connect(refresh)
	board.pointed.connect(func(cell: Vector2i) -> void: coordinate.text = "Zeile %02d   ·   Spalte %02d" % [cell.y + 1, cell.x + 1])
	add_child(board)
	heading = label("", 30)
	subtitle = label("", 14)
	mini_title = label("DEIN ARBEITSSTAND", 12)
	mini = Miniature.new()
	mini.interactive = true
	mini.navigated.connect(board.navigate_to)
	mini.tooltip_text = "Klicken oder ziehen: Ausschnitt im eigenen Arbeitsstand wählen."
	add_child(mini)
	coordinate = label("Zeile –   ·   Spalte –", 14)
	tool_title = label("", 14)
	for tool: String in ["Füllen", "Radierer", "Hand"]:
		var button: Button = action(tool, set_tool.bind(tool))
		button.toggle_mode = true
		button.tooltip_text = {"Füllen": "Links: Farbe / Füllung entfernen. Rechts: X / X entfernen.", "Radierer": "Links: Markierungen neutralisieren. Rechts: X bearbeiten.", "Hand": "Links ziehen: Raster oder die angefasste Hinweisfolge verschieben."}[tool]
		tool_buttons.append(button)
	undo_button = action("↶", undo)
	undo_button.tooltip_text = "Rückgängig: letzten ganzen Strich zurücknehmen."
	redo_button = action("↷", redo)
	redo_button.tooltip_text = "Wiederholen: zurückgenommenen Strich wiederherstellen."
	zoom_label = label("", 14)
	zoom_out = action("−", func() -> void: board.zoom(-1, board.view.viewport.get_center()))
	zoom_in = action("+", func() -> void: board.zoom(1, board.view.viewport.get_center()))
	zoom_out.tooltip_text = "Raster verkleinern"
	zoom_in.tooltip_text = "Raster vergrößern"
	fit_button = action("Gesamt", board.fit_all)
	fit_button.tooltip_text = "Ganzes Raster einpassen"
	work_button = action("100 %", board.working_size)
	work_button.tooltip_text = "Arbeitsgröße wiederherstellen"
	help_button = action("?  Hilfe", show_overlay.bind("help"))
	menu_button = action("Menü", show_overlay.bind("menu"))
	note = label("", 13)
	test_bar = Panel.new()
	add_child(test_bar)
	test_label = label("Z1 · PRÜFBEREICH", 13)
	variant_choice = OptionButton.new()
	variant_choice.add_item("V1 · Hell / redaktionell")
	variant_choice.add_item("V2 · Ruhig / atmosphärisch")
	variant_choice.item_selected.connect(set_variant)
	add_child(variant_choice)
	fixture_choice = OptionButton.new()
	for caption: String in ["F-01 · 20 × 20", "F-02 · 40 × 40", "F-03 · 100 × 100 / UI-Test"]:
		fixture_choice.add_item(caption)
	fixture_choice.select(fixture)
	fixture_choice.item_selected.connect(select_fixture)
	add_child(fixture_choice)
	reset_button = action("Beispiel zurücksetzen", reset_demo)
	reset_button.tooltip_text = "Denselben Demo-Teilstand und dieselbe Ansicht wiederherstellen. Nur im Speicher."
	_build_overlay()
	minimum = label("Mindestens 1280 × 720 logische Fensterfläche benötigt.", 20)
	minimum.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	minimum.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	minimum.mouse_filter = Control.MOUSE_FILTER_STOP
	minimum.add_theme_stylebox_override("normal", style(Color("fcfcf7"), Color("293e3d")))
	_palette()
	_apply_theme()
	resized.connect(_layout)
	_layout()
	board.restore_view(session.view_state)
	refresh()
	if not OS.get_cmdline_user_args().has("--z1-capture") and DisplayServer.get_name() != "headless":
		var usable: Rect2i = DisplayServer.screen_get_usable_rect()
		get_window().size = Vector2i(1920, 1080).min(usable.size - Vector2i(32, 64))
		get_window().position = usable.position + (usable.size - get_window().size) / 2
	if OS.get_cmdline_user_args().has("--z1-smoke"):
		call_deferred("_smoke")

func label(caption: String, font_size: int) -> Label:
	var result: Label = Label.new()
	result.text = caption
	result.set_meta("font_size", font_size)
	result.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(result)
	return result

func action(caption: String, callback: Callable) -> Button:
	var result: Button = Button.new()
	result.text = caption
	result.pressed.connect(callback)
	result.focus_mode = Control.FOCUS_NONE
	add_child(result)
	return result

static func style(fill: Color, border: Color, radius: int = 6, width: int = 1) -> StyleBoxFlat:
	var result: StyleBoxFlat = StyleBoxFlat.new()
	result.bg_color = fill
	result.border_color = border
	result.set_border_width_all(width)
	result.set_corner_radius_all(radius)
	result.content_margin_left = 10
	result.content_margin_right = 10
	return result

func _apply_theme() -> void:
	theme = Theme.new()
	theme.default_font_size = roundi(15 * ui_scale)
	var ink: Color = Color("293e3d")
	var accent: Color = Color("a8452e") if variant == 0 else Color("38594c")
	var paper: Color = Color("fcfcf7") if variant == 0 else Color("f4efdf")
	var radius: int = 3 if variant == 0 else 10
	for type: String in ["Button", "OptionButton"]:
		for state: String in ["normal", "hover", "pressed", "hover_pressed", "disabled", "focus"]:
			var fill: Color = paper
			if state in ["hover", "focus"]:
				fill = Color("e0e9dd")
			if state in ["pressed", "hover_pressed"]:
				fill = accent
			theme.set_stylebox(state, type, style(fill, Color("a5afa3"), radius))
			var color: Color = Color("788277") if state == "disabled" else (Color("ffffff") if state in ["pressed", "hover_pressed"] else ink)
			theme.set_color("font_color" if state == "normal" else "font_" + state + "_color", type, color)
	theme.set_color("font_color", "Label", ink)
	panel.add_theme_stylebox_override("panel", style(paper, Color("adb5a8"), radius))
	var frame: StyleBoxFlat = style(paper, Color("adb5a8"), radius)
	frame.shadow_color = Color(0.12, 0.2, 0.16, 0.16 if variant == 1 else 0.04)
	frame.shadow_size = 6 if variant == 1 else 1
	board.frame_style = frame
	drawer.add_theme_stylebox_override("panel", style(paper, ink, radius))
	test_bar.add_theme_stylebox_override("panel", style(Color("273b36"), Color("273b36"), 0))
	test_label.add_theme_color_override("font_color", Color("ffffff"))
	for item: Label in [heading, subtitle, note]:
		item.add_theme_color_override("font_color", ink if variant == 0 else Color("ffffff"))
	var title_font: FontVariation = FontVariation.new()
	title_font.base_font = ThemeDB.fallback_font
	title_font.variation_embolden = 0.7 if variant == 0 else 0.2
	title_font.spacing_glyph = 1 if variant == 0 else 0
	if variant == 1:
		title_font.variation_transform = Transform2D(Vector2(1, 0), Vector2(0.14, 1), Vector2.ZERO)
	heading.add_theme_font_override("font", title_font)
	heading.text = "BILD FÜR BILD" if variant == 0 else "Zeit für ein Bild"
	mini_title.text = "DEIN ARBEITSSTAND" if variant == 0 else "Dein Arbeitsstand"
	backdrop.variant = variant
	backdrop.queue_redraw()
	for item: Node in get_children():
		if item is Label:
			item.add_theme_font_size_override("font_size", roundi(int(item.get_meta("font_size", 14)) * ui_scale))
	_style_palette()

func place(control: Control, x: float, y: float, w: float, h: float) -> void:
	control.position = Vector2(x, y)
	control.size = Vector2(w, h)

func _layout() -> void:
	if board == null:
		return
	var s: float = ui_scale
	var edge: float = 32 * s
	var top: float = 110 * s
	var bottom: float = 82 * s
	var side: float = 252 * s
	var gap: float = 20 * s
	var sx: float = size.x - edge - side
	var height: float = size.y - top - bottom
	var compact: bool = height < 540 * s
	place(backdrop, 0, 0, size.x, size.y)
	place(heading, edge + 22, 20 * s, 550 * s, 42 * s)
	place(subtitle, edge + 22, 64 * s, size.x - 410 * s, 24 * s)
	place(help_button, size.x - edge - 212 * s, 34 * s, 110 * s, 36 * s)
	place(menu_button, size.x - edge - 92 * s, 34 * s, 92 * s, 36 * s)
	place(panel, sx, top, side, height)
	place(board, edge, top, sx - gap - edge, height)
	board.ui_scale = s
	board._layout()
	var inner: float = sx + 16 * s
	var width: float = side - 32 * s
	var y: float = top + 16 * s
	place(mini_title, inner, y, width, 20 * s)
	y += (23 if compact else 29) * s
	var mini_size: float = (72 if compact else 184) * s
	place(mini, inner + (width - mini_size) / 2, y, mini_size, mini_size)
	y += mini_size + (4 if compact else 12) * s
	place(coordinate, inner, y, width, 24 * s)
	y += (25 if compact else 34) * s
	place(tool_title, inner, y, width, 24 * s)
	y += (25 if compact else 30) * s
	for i: int in range(palette_buttons.size()):
		place(palette_buttons[i], inner + i * 54 * s, y, 46 * s, 38 * s)
	y += (44 if compact else 49) * s
	for i: int in range(3):
		place(tool_buttons[i], inner + [0, 74, 162][i] * s, y, [66, 80, 58][i] * s, 32 * s)
	y += (36 if compact else 42) * s
	# History actions share the flat header, leaving the navigation column compact.
	place(undo_button, size.x - edge - 310 * s, 34 * s, 40 * s, 36 * s)
	place(redo_button, size.x - edge - 264 * s, 34 * s, 40 * s, 36 * s)
	place(zoom_label, inner, y, width, 24 * s)
	y += 30 * s
	place(zoom_out, inner, y, 34 * s, 32 * s)
	place(zoom_in, inner + 38 * s, y, 34 * s, 32 * s)
	place(fit_button, inner + 76 * s, y, 76 * s, 32 * s)
	place(work_button, inner + 156 * s, y, 64 * s, 32 * s)
	place(note, edge, size.y - 75 * s, size.x - edge * 2, 24 * s)
	place(test_bar, 0, size.y - 44 * s, size.x, 44 * s)
	place(test_label, 20 * s, size.y - 38 * s, 164 * s, 30 * s)
	place(variant_choice, 186 * s, size.y - 38 * s, 238 * s, 30 * s)
	place(fixture_choice, 436 * s, size.y - 38 * s, 235 * s, 30 * s)
	place(reset_button, 683 * s, size.y - 38 * s, 215 * s, 30 * s)
	_layout_overlay()
	var small: bool = size.x < 1280 or size.y < 720
	minimum.visible = small
	place(minimum, 0, 0, size.x, size.y)
	board.mouse_filter = Control.MOUSE_FILTER_IGNORE if small else Control.MOUSE_FILTER_STOP
	if small:
		move_child(minimum, -1)
		board.cancel_gesture()
	refresh()

func _palette() -> void:
	for item: Button in palette_buttons:
		remove_child(item)
		item.queue_free()
	palette_buttons.clear()
	for entry: Dictionary in session.definition.palette:
		var button: Button = action("", set_color.bind(int(entry.id)))
		button.tooltip_text = "Rätselfarbe %d wählen" % int(entry.id)
		palette_buttons.append(button)

func _style_palette() -> void:
	for i: int in range(palette_buttons.size()):
		var entry: Dictionary = session.definition.palette[i]
		var active: bool = board.active_color == int(entry.id)
		var button: Button = palette_buttons[i]
		for state: String in ["normal", "hover", "pressed"]:
			var box: StyleBoxFlat = style(Color(entry.color), Color("ffffff") if state == "hover" else Color("273b36"), 5, 3 if active or state == "hover" else 1)
			if active:
				box.shadow_color = Color("273b36")
				box.shadow_size = 3
			button.add_theme_stylebox_override(state, box)
		button.text = "●" if active else ""
		# Two-tone marker remains legible on every unchanged puzzle color.
		button.add_theme_color_override("font_color", Color.WHITE)
		button.add_theme_color_override("font_hover_color", Color.WHITE)
		button.add_theme_color_override("font_outline_color", Color("273b36"))
		button.add_theme_constant_override("outline_size", 4)

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
	undo_button.disabled = session.gesture.active or session.player.cursor == 0
	redo_button.disabled = session.gesture.active or session.player.cursor == session.player.history.size()
	zoom_label.text = ("Gesamtansicht" if board.overview else "Raster") + "   %d %%" % roundi(board.view.cell_size / 24.0 * 100)
	var tool: String = "Hand" if board.hand else ("Radierer" if board.eraser else "Füllen")
	tool_title.text = tool + (" · Monochrom" if palette_buttons.size() == 1 else " · Farbe %d" % board.active_color)
	for button: Button in tool_buttons:
		button.set_pressed_no_signal(button.text == tool)
	_style_palette()
	subtitle.text = "BLATT %02d   /   %d × %d   /   %s" % [fixture + 1, session.player.width, session.player.height, "Monochrom" if fixture == 0 else "Vier Farben"]
	note.text = "Beispiel · nur im Speicher" if fixture != 2 else "UI-Testdatensatz – Rätselqualität nicht abgenommen · Beispiel nur im Speicher"
	if session.completed:
		note.text += " · Beispiel abgeschlossen; Enthüllung im regulären P1"

func set_variant(value: int) -> void:
	board.cancel_gesture()
	mini.dragging = false
	variant = value
	variant_choice.select(value)
	_apply_theme()
	refresh()

func select_fixture(value: int) -> void:
	fixture = value
	fixture_choice.select(value)
	reset_demo()

func reset_demo() -> void:
	board.cancel_gesture()
	mini.dragging = false
	session = Demo.create(fixture)
	board.session = session
	board.mark_completed_clues = mark_completed
	_palette()
	board.restore_view(session.view_state)
	board.clear_pointer_hover()
	coordinate.text = "Zeile –   ·   Spalte –"
	_layout()
	refresh()

func set_tool(value: String) -> void:
	board.hand = value == "Hand"
	board.eraser = value == "Radierer"
	refresh()

func set_color(value: int) -> void:
	board.active_color = value
	refresh()

func undo() -> void:
	board.cancel_gesture()
	session.undo()
	refresh()

func redo() -> void:
	board.cancel_gesture()
	session.redo()
	refresh()

func set_ui_scale(value: float) -> void:
	ui_scale = value
	_apply_theme()
	_layout()
	ui_button.text = "Oberfläche: %d %%" % roundi(value * 100)

func _build_overlay() -> void:
	overlay = ColorRect.new()
	overlay.color = Color(0.1, 0.16, 0.14, 0.42)
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(overlay)
	drawer = Panel.new()
	add_child(drawer)
	drawer_title = label("", 24)
	drawer_close = action("Schließen", hide_overlay)
	help_text = label("Links: Farbe setzen / Füllung entfernen.\nRechts: X setzen / X entfernen. X ↔ Farbe direkt.\n\nZiehen: gerade Linie; zurückziehen verkürzt sie.\nZur Startzelle zurück: neue Achse wählen.\nEsc oder Fokusverlust: Vorschau verwerfen.\n\nRad: Zoom. Mitte / Hand: Raster verschieben.\nMiniatur: Ausschnitt wählen.\nMitte / Hand auf Hinweisen: nur diese Folge ziehen.\n… zeigt weitere Zahlen; Hover zeigt die ganze Folge.\n\nRückgängig / Wiederholen gilt für ganze Striche.\nMarkierte Hinweise sind keine Fehlerprüfung.", 16)
	help_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ui_button = action("Oberfläche: 100 %", func() -> void: set_ui_scale(1.25 if ui_scale == 1.0 else 1.0))
	clue_button = action("Hinweise rasterseitig ausrichten", board.reset_clue_pan)
	completion_button = action("Erfüllte Hinweise markieren: an", func() -> void:
		mark_completed = not mark_completed
		board.mark_completed_clues = mark_completed
		completion_button.text = "Erfüllte Hinweise markieren: " + ("an" if mark_completed else "aus")
		board.queue_redraw())
	exit_button = action("Vorschau beenden", leave_app)
	hide_overlay()

func _layout_overlay() -> void:
	var s: float = ui_scale
	var w: float = 560 * s
	var h: float = minf(530 * s, size.y - 100)
	var x: float = (size.x - w) / 2
	var y: float = (size.y - h) / 2
	place(overlay, 0, 0, size.x, size.y)
	place(drawer, x, y, w, h)
	place(drawer_title, x + 24 * s, y + 20 * s, w - 160 * s, 38 * s)
	place(drawer_close, x + w - 136 * s, y + 20 * s, 112 * s, 36 * s)
	place(help_text, x + 24 * s, y + 78 * s, w - 48 * s, h - 94 * s)
	var items: Array[Button] = [ui_button, clue_button, completion_button, exit_button]
	for i: int in range(items.size()):
		place(items[i], x + 24 * s, y + (90 + i * 60) * s, w - 48 * s, 40 * s)

func show_overlay(kind: String) -> void:
	board.cancel_gesture()
	board.clear_pointer_hover()
	mini.dragging = false
	overlay_kind = kind
	for item: Control in [overlay, drawer, drawer_title, drawer_close]:
		item.show()
	help_text.visible = kind == "help"
	drawer_title.text = "Hilfe zur Rätselarbeit" if kind == "help" else "Ansicht & Optionen"
	for item: Control in [ui_button, clue_button, completion_button, exit_button]:
		item.visible = kind == "menu"
	# Palette recreated by reset must never sit above the input shield.
	for item: Control in [overlay, drawer, drawer_title, drawer_close, help_text, ui_button, clue_button, completion_button, exit_button]:
		move_child(item, -1)

func hide_overlay() -> void:
	overlay_kind = ""
	for item: Control in [overlay, drawer, drawer_title, drawer_close, help_text, ui_button, clue_button, completion_button, exit_button]:
		item.hide()

func leave_app() -> void:
	board.cancel_gesture()
	get_tree().quit()

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST and board != null:
		leave_app()

func _smoke() -> void:
	await get_tree().process_frame
	set_variant(1)
	select_fixture(2)
	reset_demo()
	show_overlay("help")
	hide_overlay()
	print("Z1_START_OK ", DisplayServer.get_name(), " ", size)
	leave_app()
