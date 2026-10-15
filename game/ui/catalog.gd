extends VBoxContainer
## Session-local presentation of the validated KAT-1 registry. Never writes saves.
const Registry = preload("res://model/content_registry.gd")
const Session = preload("res://model/session.gd")
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
const BookButton = preload("res://ui/book_button.gd")
const PAGE_SIZE: int = 24
signal opened(id: String)
signal reset_requested(id: String)
signal repair_requested(id: String)
signal information_requested
signal quit_requested
var category_id: String = ""
var page_index: int = 0
var selected_id: String = ""
var ui_scale: float = 1.0
var category_choice: OptionButton
var summary: Label
var feedback: Label
var empty_message: Label
var all_button: Button
var scroll: ScrollContainer
var grid: GridContainer
var previous_button: Button
var next_button: Button
var page_label: Label
var choices: Array[Button] = []
var previews: Array[Miniature] = []
var reveals: Array[Reveal] = []
var notes: Array[Label] = []
var reset_buttons: Dictionary = {}
var play_buttons: Dictionary = {}
var repair_buttons: Dictionary = {}
var visible_ids: Array[String] = []
var filtered_ids: Array[String] = []
var items: Dictionary = {}
var metadata: Dictionary = {}
var categories: Array[Dictionary] = []
var statuses: Dictionary = {}
var errors: Dictionary = {}
var load_error: String = ""
var generation: int = 0
var scroll_vertical: int:
	get: return scroll.scroll_vertical
	set(value): scroll.scroll_vertical = value

func _ready() -> void:
	add_theme_constant_override("separation", 10)
	var top: HBoxContainer = HBoxContainer.new()
	add_child(top)
	var label: Label = _label("Kategorie", 16)
	top.add_child(label)
	category_choice = OptionButton.new()
	category_choice.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	category_choice.fit_to_longest_item = false
	category_choice.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	category_choice.item_selected.connect(func(index: int) -> void: choose_category(str(category_choice.get_item_metadata(index))))
	top.add_child(category_choice)
	top.add_child(_button("Einstellungen / Info", func() -> void: information_requested.emit()))
	top.add_child(_button("Beenden", func() -> void: quit_requested.emit()))
	summary = _label("", 18)
	add_child(summary)
	feedback = _label("", 15)
	feedback.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	feedback.hide()
	add_child(feedback)
	empty_message = _label("", 22)
	empty_message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(empty_message)
	all_button = _button("Alle Rätsel", choose_category.bind(""))
	all_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	add_child(all_button)
	scroll = ScrollContainer.new()
	# Child widths are recomputed on resize; old grid minima must not force the
	# entire page beyond the client before that container sort can run.
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(scroll)
	grid = GridContainer.new()
	grid.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 14)
	scroll.add_child(grid)
	var pager: HBoxContainer = HBoxContainer.new()
	pager.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(pager)
	previous_button = _button("← Zurück", turn_page.bind(-1))
	pager.add_child(previous_button)
	page_label = _label("", 16)
	pager.add_child(page_label)
	next_button = _button("Weiter →", turn_page.bind(1))
	pager.add_child(next_button)
	resized.connect(_layout_cards)
	scroll.resized.connect(_layout_cards)

func present(sessions: Array[Session], slot_status: Array[String], slot_errors: Array[String], error: String, selection: String) -> void:
	feedback.hide()
	load_error = error
	selected_id = selection
	items.clear()
	statuses.clear()
	errors.clear()
	metadata.clear()
	categories.clear()
	if error.is_empty(): categories = Registry.categories()
	for entry: Dictionary in Registry.entries() if error.is_empty() else []:
		metadata[entry.id] = entry
	for index: int in range(sessions.size()):
		var id: String = str(sessions[index].definition.id)
		items[id] = sessions[index]
		statuses[id] = slot_status[index]
		errors[id] = slot_errors[index]
	category_choice.clear()
	category_choice.add_item("Alle Rätsel (%d)" % items.size())
	category_choice.set_item_metadata(0, "")
	for category: Dictionary in categories:
		category_choice.add_item("%s (%d)" % [category.name, _ids(str(category.id)).size()])
		category_choice.set_item_metadata(category_choice.item_count - 1, category.id)
	category_choice.disabled = not error.is_empty()
	_render(scroll_vertical)

func _ids(category: String) -> Array[String]:
	var result: Array[String] = []
	# Sessions arrive in canonical registry order; no sorting by label or page index.
	for id: String in items:
		if category.is_empty() or metadata.get(id, {}).get("category_id") == category:
			result.append(id)
	return result

func choose_category(id: String) -> void:
	category_id = id
	page_index = 0
	_render(0)

func turn_page(delta: int) -> void:
	page_index = clampi(page_index + delta, 0, maxi(0, ceili(filtered_ids.size() / float(PAGE_SIZE)) - 1))
	_render(0)

func suspend() -> void:
	# The completion screen may load its own reveal while the catalog is hidden.
	for picture: Reveal in reveals: picture.payload = {}

func show_error(id: String, message: String) -> void:
	var index: int = visible_ids.find(id)
	if index >= 0: notes[index].text = "Speicherfehler"
	# A blocked quit/switch remains visible even if the active slot is filtered out.
	feedback.text = (items[id].neutral_title() + ": " if items.has(id) else "") + "Speicherfehler: " + message
	feedback.show()

static func progress(item: Session) -> String:
	if item.completed: return "Gelöst"
	if not item.player.history.is_empty() or item.player.cells.count(-1) != item.player.cells.size(): return "Begonnen"
	return "Neu"

func _render(position: int) -> void:
	BookButton.dismiss_all(get_tree())
	generation += 1
	for child: Node in grid.get_children():
		# Synchronous release bounds live cards AND reveal textures during page turns.
		grid.remove_child(child)
		child.free()
	choices.clear()
	previews.clear()
	reveals.clear()
	notes.clear()
	reset_buttons.clear()
	play_buttons.clear()
	repair_buttons.clear()
	visible_ids.clear()
	filtered_ids = _ids(category_id)
	var page_count: int = maxi(1, ceili(filtered_ids.size() / float(PAGE_SIZE)))
	page_index = clampi(page_index, 0, page_count - 1)
	var solved: int = 0
	for id: String in filtered_ids:
		if items[id].completed and statuses[id] != "error": solved += 1
	summary.text = "%d von %d gelöst" % [solved, filtered_ids.size()]
	summary.visible = load_error.is_empty()
	for index: int in range(category_choice.item_count):
		if str(category_choice.get_item_metadata(index)) == category_id: category_choice.select(index)
	category_choice.tooltip_text = category_choice.text
	empty_message.text = "Katalog konnte nicht geladen werden.\n" + load_error if not load_error.is_empty() else "Hier gibt es noch keine Rätsel"
	empty_message.visible = not load_error.is_empty() or filtered_ids.is_empty()
	all_button.visible = load_error.is_empty() and filtered_ids.is_empty() and not category_id.is_empty()
	for id: String in filtered_ids.slice(page_index * PAGE_SIZE, (page_index + 1) * PAGE_SIZE):
		_add_card(id)
	page_label.text = "Seite %d von %d" % [page_index + 1, page_count]
	previous_button.disabled = page_index == 0
	next_button.disabled = page_index + 1 >= page_count
	previous_button.get_parent().visible = page_count > 1
	_layout_cards()
	_restore_scroll.call_deferred(position, generation)

func _restore_scroll(position: int, expected_generation: int) -> void:
	# Container sorting precedes deferred calls; a stale rebuild cannot move a newer page.
	if generation == expected_generation: scroll_vertical = position

func _add_card(id: String) -> void:
	var item: Session = items[id]
	visible_ids.append(id)
	var column: VBoxContainer = VBoxContainer.new()
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_child(column)
	var card: BookButton = BookButton.new()
	card.content_surface = true
	# Retain the existing semantic button text; only the wrapping labels draw it.
	card.text = item.album_title()
	card.focus_mode = Control.FOCUS_ALL
	card.pressed.connect(func() -> void: opened.emit(id))
	card.clip_text = true
	card.alignment = HORIZONTAL_ALIGNMENT_LEFT
	# Dimensions belong only to metadata, never to this neutral catalog heading.
	# Registry order is the canonical numbering used by Session.neutral_title().
	var leaf: String = item.neutral_title().split(" · ")[0]
	var caption_text: String = (item.album_title() + "\n" + leaf) if item.completed and statuses[id] != "error" else leaf
	card.tooltip_text = caption_text
	card.accessibility_name = caption_text
	# Native button supplies the whole-card hit/focus surface. Its caption is laid
	# out by a wrapping label so long names cannot force the grid wider than paper.
	for state: String in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		card.add_theme_color_override(state, Color.TRANSPARENT)
	for state: String in ["normal", "hover", "pressed", "focus", "disabled"]:
		var paper: StyleBoxFlat = StyleBoxFlat.new()
		paper.bg_color = Color("fff8e8") if state == "normal" else Color("e0e9d9")
		if state == "disabled": paper.bg_color = Color("eadbd1")
		paper.border_color = Color("376a60") if id == selected_id or state == "focus" else Color("ac9369")
		paper.set_border_width_all(3 if id == selected_id or state == "focus" else 1)
		card.add_theme_stylebox_override(state, paper)
	card.disabled = statuses[id] == "error"
	column.add_child(card)
	choices.append(card)
	var margin: MarginContainer = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]: margin.add_theme_constant_override("margin_" + side, 12)
	card.add_child(margin)
	margin.minimum_size_changed.connect(func() -> void: card.custom_minimum_size.y = margin.get_combined_minimum_size().y)
	var content: VBoxContainer = VBoxContainer.new()
	margin.add_child(content)
	var caption: Label = _label(caption_text, 18)
	caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	content.add_child(caption)
	var meta: String = "%d × %d · %s" % [item.player.width, item.player.height, "Mono" if item.definition.palette.size() == 1 else "Farbe"]
	if category_id.is_empty():
		for category: Dictionary in categories:
			if category.id == metadata.get(id, {}).get("category_id"): meta += "\n" + str(category.name)
	var detail: Label = _label(meta, 14)
	detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var row: HBoxContainer = HBoxContainer.new()
	row.name = "metadata-actions"
	content.add_child(row)
	row.add_child(detail)
	var actions: VBoxContainer = VBoxContainer.new()
	row.add_child(actions)
	var play: BookButton = _button("", func() -> void: opened.emit(id))
	play.action_id = "play"
	play.name = "play-" + id
	play.image = preload("res://art/book/play.svg")
	play.tooltip_text = "Ansehen" if item.completed else "Fortsetzen" if progress(item) == "Begonnen" else "Spielen"
	play.disabled = statuses[id] == "error"
	if play.disabled: play.tooltip_text = "Speicherdaten ungültig · Reset erforderlich"
	play.accessibility_name = play.tooltip_text + " · " + leaf
	actions.add_child(play)
	play_buttons[id] = play
	var reset: BookButton = _button("", func() -> void: reset_requested.emit(id))
	reset.action_id = "reset"
	reset.name = "reset-" + id
	reset.image = preload("res://art/book/reset.svg")
	reset.tooltip_text = "Rätsel zurücksetzen"
	reset.accessibility_name = "Rätsel zurücksetzen · " + leaf
	actions.add_child(reset)
	reset_buttons[id] = reset
	var preview: Miniature = Miniature.new()
	preview.cells = item.player.cells.duplicate()
	preview.width = item.player.width
	preview.height = item.player.height
	preview.palette = item.definition.palette
	preview.style_identity = id + "/miniature"
	preview.interactive = false
	preview.draw_frame = false
	preview.size_flags_vertical = Control.SIZE_EXPAND_FILL
	preview.custom_minimum_size = Vector2(96, 96)
	preview.visible = not item.completed and statuses[id] != "error"
	content.add_child(preview)
	previews.append(preview)
	var picture: Reveal = Reveal.new()
	picture.paired = false
	picture.size_flags_vertical = Control.SIZE_EXPAND_FILL
	picture.custom_minimum_size = Vector2(96, 96)
	# reveal() is the only source; no unearned image is loaded speculatively.
	picture.payload = item.reveal() if statuses[id] != "error" else {}
	picture.visible = not picture.payload.is_empty()
	content.add_child(picture)
	reveals.append(picture)
	var status: String = progress(item)
	if statuses[id] == "error": status = "Speicherdaten ungültig · Reset erforderlich"
	elif statuses[id] == "recovered": status += " · Backup geladen"
	elif statuses[id] == "backup_invalid": status += " · Backup beschädigt"
	elif not str(errors[id]).is_empty(): status += " · Speicherfehler"
	var note: Label = _label(status, 15)
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	content.add_child(note)
	notes.append(note)
	_ignore_pointer(margin)
	if statuses[id] in ["recovered", "backup_invalid"]:
		var repair: Button = _button("Backup erneuern" if statuses[id] == "backup_invalid" else "Backup übernehmen", func() -> void: repair_requested.emit(id))
		column.add_child(repair)
		repair_buttons[id] = repair

func _layout_cards() -> void:
	if grid == null: return
	var gap: int = roundi(12 * ui_scale)
	grid.add_theme_constant_override("h_separation", gap)
	grid.add_theme_constant_override("v_separation", gap)
	# Reserve the actual scrollbar width even before the first container sort.
	var available: float = maxf(1, scroll.size.x - scroll.get_v_scroll_bar().get_combined_minimum_size().x - 2*ui_scale)
	var capacity: int = maxi(1, floori((available + gap) / (220*ui_scale + gap)))
	grid.columns = maxi(1, mini(capacity, choices.size()))
	var card_width: float = minf(240*ui_scale, floorf((available-(capacity-1)*gap)/capacity))
	for node: Node in find_children("*", "Label", true, false):
		if node.has_meta("base_font"): node.add_theme_font_size_override("font_size", roundi(float(node.get_meta("base_font")) * ui_scale))
	for node: Node in find_children("*", "Button", true, false):
		if node is BookButton:
			node.ui_scale = ui_scale
			if node.content_surface: continue
			node.add_theme_font_size_override("font_size", roundi(14*ui_scale))
			node.custom_minimum_size = Vector2(44,44)*ui_scale if node.image != null else Vector2(node.get_theme_font("font").get_multiline_string_size(node.text,HORIZONTAL_ALIGNMENT_LEFT,-1,roundi(14*ui_scale)).x+24*ui_scale,44*ui_scale)
	for card: Button in choices:
		card.get_parent().custom_minimum_size.x = card_width
		card.custom_minimum_size.x = card_width
		var margin: MarginContainer = card.get_child(0)
		for side: String in ["left","right","top","bottom"]: margin.add_theme_constant_override("margin_"+side,roundi(10*ui_scale))
		var content: VBoxContainer = margin.get_child(0)
		content.add_theme_constant_override("separation",roundi(8*ui_scale))
		var row: HBoxContainer = content.get_node("metadata-actions")
		row.add_theme_constant_override("separation",roundi(8*ui_scale))
		row.get_child(1).add_theme_constant_override("separation",roundi(8*ui_scale))
		card.custom_minimum_size.y = margin.get_combined_minimum_size().y
	category_choice.custom_minimum_size.y = 44 * ui_scale
	category_choice.get_popup().max_size = Vector2i(roundi(size.x), roundi(minf(480 * ui_scale, size.y * 0.8)))
	category_choice.get_popup().prefer_native_menu = false

func ensure_control_visible(control: Control) -> void:
	scroll.ensure_control_visible(control)

static func _ignore_pointer(control: Control) -> void:
	# Only decoration passes through. Each action consumes its own down/up route.
	if control is BaseButton: return
	control.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for child: Node in control.get_children():
		if child is Control: _ignore_pointer(child)

static func _label(text: String, font_size: int) -> Label:
	var result: Label = Label.new()
	result.text = text
	result.set_meta("base_font", font_size)
	result.add_theme_font_size_override("font_size", font_size)
	return result

static func _button(text: String, action: Callable) -> BookButton:
	var result: BookButton = BookButton.new()
	result.text = text
	result.focus_mode = Control.FOCUS_ALL
	result.pressed.connect(action)
	return result
