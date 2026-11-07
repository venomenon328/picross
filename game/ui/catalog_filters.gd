extends PopupPanel
## Draft controls are separate from the catalog's last valid applied selection.
const Filter = preload("res://model/catalog_filter.gd")
const Choice = preload("res://ui/book_choice.gd")
const BookButton = preload("res://ui/book_button.gd")
const Paper = preload("res://ui/book_style.gd")
const Text = preload("res://ui/ui_text.gd")
signal submitted(status: String, mode: String, lower: int, upper: int, width: String, height: String)
signal reset_requested
var status: Choice
var mode_choice: Choice
var lower: Choice
var upper: Choice
var width_input: LineEdit
var height_input: LineEdit
var error: Label
var body: VBoxContainer
var form: GridContainer
var scroller: ScrollContainer
var actions: HBoxContainer
var ui_scale: float = 1.0

func _ready() -> void:
	name = "catalog-filter-panel"
	wrap_controls = true
	var outer := VBoxContainer.new()
	add_child(outer)
	scroller = ScrollContainer.new()
	scroller.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroller.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(scroller)
	body = VBoxContainer.new()
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroller.add_child(body)
	form = GridContainer.new()
	form.columns = 2
	form.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(form)
	status = _choice("Status", ["Alle", "Noch offen", "Neu", "Begonnen", "Gelöst"])
	mode_choice = _choice("Modus", ["Alle", "Monochrom", "Farbe"])
	var difficulty := HBoxContainer.new()
	_label("Schwierigkeit", form)
	form.add_child(difficulty)
	var levels: Array = ["Ohne Grenze", "Sehr leicht", "Leicht", "Mittel", "Schwer", "Sehr schwer"]
	lower = _choice("Von", levels, difficulty)
	upper = _choice("Bis", levels, difficulty)
	lower.accessibility_name = "Schwierigkeit von"
	upper.accessibility_name = "Schwierigkeit bis"
	lower.item_selected.connect(func(_index: int) -> void: _bounds_changed(true))
	upper.item_selected.connect(func(_index: int) -> void: _bounds_changed(false))
	var dimensions := HBoxContainer.new()
	_label("Maximale Größe", form)
	form.add_child(dimensions)
	width_input = _dimension("Breite", dimensions)
	height_input = _dimension("Höhe", dimensions)
	error = Label.new()
	error.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	error.add_theme_color_override("font_color", Color("863c32"))
	error.hide()
	body.add_child(error)
	body.move_child(error,0)
	actions = HBoxContainer.new()
	outer.add_child(actions)
	for spec: Array in [["Übernehmen", submit], ["Schließen", hide]]:
		var button := BookButton.new()
		button.text = spec[0]
		button.action_id = "catalog-filter-" + spec[0]
		button.pressed.connect(spec[1])
		actions.add_child(button)
	var reset := BookButton.new()
	reset.text = "Filter zurücksetzen"
	reset.action_id = "catalog-filter-reset"
	reset.tooltip_text = "Kategorie und alle Filter zurücksetzen; Sortierung behalten"
	reset.pressed.connect(func() -> void: reset_requested.emit())
	outer.add_child(reset)
	get_parent().get_viewport().size_changed.connect(hide)

func _label(title: String, parent: Container) -> void:
	var label := Label.new()
	label.text = title
	label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	parent.add_child(label)

func _choice(title: String, entries: Array, parent: Container = null) -> Choice:
	if parent == null: parent = form
	_label(title, parent)
	var choice := Choice.new()
	choice.name = "catalog-filter-" + title
	choice.accessibility_name = title
	choice.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	choice.fit_to_longest_item = false
	for title_text: String in entries: choice.add_item(title_text)
	parent.add_child(choice)
	return choice

func _dimension(title: String, parent: HBoxContainer) -> LineEdit:
	_label(title, parent)
	var field := LineEdit.new()
	field.name = "catalog-filter-" + title
	field.accessibility_name = "Maximale " + title + " (1 bis 99, leer ohne Grenze)"
	field.placeholder_text = "Alle"
	field.max_length = 2
	field.add_theme_constant_override("minimum_character_width", 2)
	field.add_theme_color_override("font_color", Color("293e3d"))
	field.add_theme_color_override("font_placeholder_color", Color("64685f"))
	field.add_theme_color_override("caret_color", Color("293e3d"))
	field.add_theme_color_override("selection_color", Color("b4c6b5"))
	field.add_theme_color_override("font_selected_color", Color("293e3d"))
	field.text_submitted.connect(func(_value: String) -> void: submit())
	parent.add_child(field)
	return field

func open(selection: Dictionary, anchor: Rect2, scale: float) -> void:
	ui_scale = scale
	status.select(Filter.STATUSES.find(selection.status))
	mode_choice.select(Filter.MODES.find(selection.mode))
	lower.select(selection.lower)
	upper.select(selection.upper)
	_bounds_changed(true)
	width_input.text = "" if selection.width == 0 else str(selection.width)
	height_input.text = "" if selection.height == 0 else str(selection.height)
	error.hide()
	scroller.scroll_vertical = 0
	var fs: int = Text.small_size(scale)
	var paper := Paper.make("catalog/filter-panel",scale,Color("fff8e8"))
	paper.set_content_margin_all(14*scale)
	paper.opaque_bounds = true
	add_theme_stylebox_override("panel", paper)
	for node: Node in find_children("*", "Control", true, false):
		if node is Label or node is LineEdit:
			node.add_theme_font_override("font", Text.small_font(fs))
			node.add_theme_font_size_override("font_size", fs)
		if node is Choice:
			node.ui_scale = scale
			node.custom_minimum_size = Vector2(140 if node in [lower,upper] else 170,44)*scale
		if node is BookButton:
			node.ui_scale = scale
			node.custom_minimum_size = Vector2(120,44)*scale
		if node is BoxContainer: node.add_theme_constant_override("separation",roundi(8*scale))
		if node is GridContainer:
			node.add_theme_constant_override("h_separation",roundi(16*scale))
			node.add_theme_constant_override("v_separation",roundi(8*scale))
		if node is LineEdit:
			node.custom_minimum_size = Vector2(60,44)*scale
			for state: String in ["normal","focus","read_only"]:
				var frame := Paper.make("catalog/filter-input/"+state,scale,Color("fff8e8"))
				frame.content_margin_left = 12*scale
				frame.content_margin_right = 12*scale
				frame.content_margin_top = 6*scale
				frame.content_margin_bottom = 6*scale
				if state == "focus":
					frame.focus = true
					frame.paper = Color.TRANSPARENT
					frame.ink = Color("376a60")
				node.add_theme_stylebox_override(state,frame)
	var viewport_size := Vector2i(get_parent().get_viewport().get_visible_rect().size)
	var panel_size := Vector2i(mini(roundi(540*scale),viewport_size.x-32),mini(roundi(440*scale),viewport_size.y-32))
	scroller.custom_minimum_size = Vector2(0,panel_size.y-140*scale)
	min_size = Vector2i.ZERO
	size = panel_size
	position = Vector2i(clampi(roundi(anchor.position.x),16,viewport_size.x-size.x-16),clampi(roundi(anchor.end.y+8*scale),16,viewport_size.y-size.y-16))
	popup()
	status.grab_focus()

func _bounds_changed(changed_lower: bool) -> void:
	# The changed endpoint wins. The opposite endpoint follows if necessary;
	# each menu keeps only compatible levels selectable, including equality.
	if lower.selected > 0 and upper.selected > 0 and lower.selected > upper.selected:
		if changed_lower: upper.select(lower.selected)
		else: lower.select(upper.selected)
	for index: int in range(1,6):
		lower.set_item_disabled(index,upper.selected > 0 and index > upper.selected)
		upper.set_item_disabled(index,lower.selected > 0 and index < lower.selected)

func submit() -> void:
	_bounds_changed(true)
	submitted.emit(Filter.STATUSES[status.selected], Filter.MODES[mode_choice.selected], lower.selected, upper.selected, width_input.text, height_input.text)

func invalid(message: String) -> void:
	error.text = message
	error.show()
	_reveal_error.call_deferred()

func _reveal_error() -> void:
	# The newly wrapped error changes the container range during its next sort.
	await get_tree().process_frame
	if visible and error.visible: scroller.ensure_control_visible(error)
