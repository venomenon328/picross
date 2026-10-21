extends VBoxContainer
## Session-local presentation of the validated KAT-1 registry. Never writes saves.
const Registry = preload("res://model/content_registry.gd")
const Session = preload("res://model/session.gd")
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
const BookButton = preload("res://ui/book_button.gd")
const BookChoice = preload("res://ui/book_choice.gd")
const PaperStyle = preload("res://ui/book_style.gd")
const Card = preload("res://ui/catalog_card.gd")
const Preference = preload("res://model/catalog_preference.gd")
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
var sort_label: Label
var category_tooltip_layout := Vector2.ZERO
var preference: Preference = Preference.new()
var sort_choice: OptionButton
var direction_button: BookButton
var preference_feedback: Label
var summary: Label
var feedback: Label
var empty_message: Label
var all_button: Button
var scroll: ScrollContainer
var grid: GridContainer
var previous_button: BookButton
var next_button: BookButton
var page_label: Label
var choices: Array[Button] = []
var previews: Array[Miniature] = []
var reveals: Array[Reveal] = []
var notes: Array[Label] = []
var reset_buttons: Dictionary = {}
var repair_buttons: Dictionary = {}
var visible_ids: Array[String] = []
var filtered_ids: Array[String] = []
var items: Dictionary = {}
var metadata: Dictionary = {}
var ordinals: Dictionary = {}
var categories: Array[Dictionary] = []
var statuses: Dictionary = {}
var errors: Dictionary = {}
var load_error: String = ""
var generation: int = 0
var scroll_vertical: int:
	get: return scroll.scroll_vertical
	set(value): scroll.scroll_vertical = value

func _ready() -> void:
	preference.load_selection()
	add_theme_constant_override("separation", 10)
	var top: HBoxContainer = HBoxContainer.new()
	add_child(top)
	var label: Label = _label("Kategorie", 16)
	top.add_child(label)
	category_choice = BookChoice.new()
	category_choice.name = "catalog-category"
	category_choice.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	category_choice.fit_to_longest_item = false
	category_choice.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	category_choice.item_selected.connect(func(index: int) -> void: choose_category(str(category_choice.get_item_metadata(index))))
	top.add_child(category_choice)
	sort_label = _label("Sortieren nach", 16)
	sort_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	top.add_child(sort_label)
	sort_choice = BookChoice.new()
	sort_choice.name = "catalog-sort"
	for title: String in ["Kategorie", "Größe", "Schwierigkeit", "Hinzugefügt"]: sort_choice.add_item(title)
	sort_choice.item_selected.connect(func(index: int) -> void: choose_sort(Preference.CRITERIA[index]))
	top.add_child(sort_choice)
	direction_button = _button("", reverse_sort)
	direction_button.name = "catalog-direction"
	direction_button.action_id = "catalog-direction"
	top.add_child(direction_button)
	top.add_child(_button("Einstellungen / Info", func() -> void: information_requested.emit()))
	top.add_child(_button("Beenden", func() -> void: quit_requested.emit()))
	var preference_row: HBoxContainer = HBoxContainer.new()
	add_child(preference_row)
	preference_feedback = _label("", 15)
	preference_row.add_child(preference_feedback)
	preference_row.add_child(_button("Erneut versuchen", _save_preference))
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
	previous_button = _button("Zurück", turn_page.bind(-1))
	previous_button.image = preload("res://art/book/arrow-left.svg")
	pager.add_child(previous_button)
	page_label = _label("", 16)
	pager.add_child(page_label)
	next_button = _button("Weiter", turn_page.bind(1))
	next_button.image = preload("res://art/book/arrow-right.svg")
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
	ordinals.clear()
	categories.clear()
	if error.is_empty(): categories = Registry.categories()
	for entry: Dictionary in Registry.entries() if error.is_empty() else []:
		ordinals[entry.id] = ordinals.size()
		metadata[entry.id] = entry
	for index: int in range(sessions.size()):
		var id: String = str(sessions[index].definition.id)
		items[id] = sessions[index]
		statuses[id] = slot_status[index]
		errors[id] = slot_errors[index]
	category_choice.clear()
	category_tooltip_layout = Vector2.ZERO
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
	if category_id == id: return
	category_id = id
	page_index = 0
	_render(0)

func choose_sort(criterion: String) -> void:
	if not criterion in Preference.CRITERIA: return
	if preference.criterion != criterion:
		preference.criterion = criterion
		preference.direction = "desc" if criterion == "added" else "asc"
		page_index = 0
		_render(0)
	_save_preference()

func reverse_sort() -> void:
	preference.direction = "desc" if preference.direction == "asc" else "asc"
	page_index = 0
	_render(0)
	_save_preference()

func _save_preference() -> void:
	preference.save_selection()
	_preference_status()

func _process(_delta: float) -> void:
	_preference_status()

func _preference_status() -> void:
	if preference_feedback == null: return
	var message: String = preference.error
	if message.is_empty() and OS.has_feature("web"):
		message = str(JavaScriptBridge.eval("window.picrossStorage.preferenceError || ''", true))
	preference_feedback.text = message
	preference_feedback.get_parent().visible = not message.is_empty()

func _primary(id: String) -> Variant:
	var entry: Dictionary = metadata.get(id, {})
	match preference.criterion:
		"size": return items[id].player.width * items[id].player.height
		"difficulty":
			var difficulty: Variant = entry.get("difficulty")
			return difficulty.get("level") if difficulty is Dictionary else null
		"added": return entry.get("added_at")
		_:
			for category: Dictionary in categories:
				if category.id == entry.get("category_id"): return category.order
	return null

func _before(a: String, b: String) -> bool:
	var av: Variant = _primary(a)
	var bv: Variant = _primary(b)
	if av == null and bv != null: return false
	if bv == null and av != null: return true
	if av == bv: return int(ordinals.get(a, 0)) < int(ordinals.get(b, 0))
	return av < bv if preference.direction == "asc" else av > bv

func _direction_description() -> String:
	var ascending: bool = preference.direction == "asc"
	match preference.criterion:
		"size": return "Kleinste zuerst" if ascending else "Größte zuerst"
		"difficulty": return "Sehr leichte zuerst" if ascending else "Sehr schwere zuerst"
		"added": return "Älteste zuerst" if ascending else "Neueste zuerst"
		_: return "Kategorienfolge" if ascending else "Umgekehrte Kategorienfolge"

func turn_page(delta: int) -> void:
	page_index = clampi(page_index + delta, 0, maxi(0, ceili(filtered_ids.size() / float(PAGE_SIZE)) - 1))
	_render(0)

func suspend() -> void:
	# The completion screen may load its own reveal while the catalog is hidden.
	for picture: Reveal in reveals: picture.payload = {}

func show_error(id: String, message: String) -> void:
	errors[id] = message
	var index: int = visible_ids.find(id)
	if index >= 0: _diagnose(choices[index], id)
	# A blocked quit/switch remains visible even if the active slot is filtered out.
	feedback.text = (items[id].neutral_title() + ": " if items.has(id) else "") + "Speicherfehler: " + message
	feedback.show()

static func progress(item: Session) -> String:
	if item.completed: return "Gelöst"
	if not item.player.history.is_empty() or item.player.cells.count(-1) != item.player.cells.size(): return "Begonnen"
	return "Neu"

func _render(position: int) -> void:
	BookButton.dismiss_all(get_tree())
	BookChoice.dismiss_all(get_tree())
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
	repair_buttons.clear()
	visible_ids.clear()
	filtered_ids = _ids(category_id)
	filtered_ids.sort_custom(_before)
	sort_choice.select(Preference.CRITERIA.find(preference.criterion))
	direction_button.image = load("res://art/book/arrow-up.svg" if preference.direction == "asc" else "res://art/book/arrow-down.svg")
	direction_button.tooltip_text = _direction_description()
	direction_button.accessibility_name = "Sortierrichtung (%s): %s" % [sort_choice.text, direction_button.tooltip_text]
	sort_choice.disabled = not load_error.is_empty()
	direction_button.disabled = not load_error.is_empty()
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

static func reset_allowed(item: Session, state: String, error: String) -> bool:
	return progress(item) != "Neu" or state in ["error", "recovered", "backup_invalid"] or not error.is_empty()

func _diagnose(card: Card, id: String) -> void:
	var state: String = str(statuses[id])
	card.note.text = "Ungültig" if state == "error" else progress(items[id])
	var message: String = ""
	if state == "error": message = "Speicherdaten ungültig. Öffnen gesperrt; bitte zurücksetzen."
	elif state == "recovered": message = "Backup geladen. Zum Speichern bitte bewusst übernehmen."
	elif state == "backup_invalid": message = "Backup beschädigt. Zum Speichern bitte erneuern."
	if not str(errors[id]).is_empty():
		message += ("\n" if not message.is_empty() else "") + "Speicherfehler: " + str(errors[id])
	card.set_diagnosis(message, reset_allowed(items[id],state,str(errors[id])))
	var action: String = "Öffnen gesperrt" if state == "error" else "Ansehen" if items[id].completed else "Fortsetzen" if progress(items[id]) == "Begonnen" else "Spielen"
	card.accessibility_name = "%s · %s · %s · %s · %s · %s · %s · %s" % [card.caption.text,card.leaf.text,card.detail.text,card.dimensions.text,card.mode_tip.tooltip_text,card.difficulty.text,card.note.text,action]
	card.reset.accessibility_name = "Rätsel zurücksetzen · " + card.leaf.text + " · " + card.note.text
	if card.repair != null: card.repair.accessibility_name = card.repair.text + " · " + card.leaf.text + " · " + card.note.text

func _add_card(id: String) -> void:
	var item: Session = items[id]
	visible_ids.append(id)
	var column: VBoxContainer = VBoxContainer.new()
	grid.add_child(column)
	var card: Card = Card.new()
	card.action_id = id
	card.content_surface = true
	card.focus_mode = Control.FOCUS_ALL
	card.pressed.connect(func() -> void: opened.emit(id))
	card.recovery_activated.connect(func() -> void: opened.emit(id))
	for state: String in ["normal", "hover", "pressed", "focus", "disabled"]:
		var paper = PaperStyle.make("card/"+id,ui_scale,Color("fff8e8") if state == "normal" else Color("c5d6cd") if state == "pressed" else Color("e0e9d9"))
		if state == "disabled": paper.paper = Color("eadbd1")
		paper.selected = id == selected_id
		if state == "focus":
			paper.focus = true
			paper.paper = Color.TRANSPARENT
			paper.ink = BookButton.INK
		card.add_theme_stylebox_override(state, paper)
	card.disabled = statuses[id] == "error"
	column.add_child(card)
	choices.append(card)
	var leaf: String = item.neutral_title().split(" · ")[0]
	var meta: String = ""
	if category_id.is_empty():
		for category: Dictionary in categories:
			if category.id == metadata.get(id, {}).get("category_id"): meta = str(category.name)
	card.configure(item.album_title() if item.completed and statuses[id] != "error" else "???",meta,leaf)
	card.set_metadata(item.player.width,item.player.height,item.definition.palette.size() > 1,metadata.get(id,{}).get("difficulty"))
	var reset: BookButton = _button("",func() -> void: reset_requested.emit(id))
	reset.action_id = "reset"
	reset.name = "reset-" + id
	reset.image = preload("res://art/book/reset.svg")
	reset.tooltip_text = "Rätsel zurücksetzen"
	reset.accessibility_name = "Rätsel zurücksetzen · " + leaf
	card.add_child(reset)
	card.reset = reset
	reset_buttons[id] = reset
	card.preview.cells = item.player.cells.duplicate()
	card.preview.width = item.player.width
	card.preview.height = item.player.height
	card.preview.palette = item.definition.palette
	card.preview.style_identity = id + "/miniature"
	previews.append(card.preview)
	# Session.reveal remains the only gate; unearned resources are never loaded.
	card.picture.payload = item.reveal() if statuses[id] != "error" else {}
	reveals.append(card.picture)
	notes.append(card.note)
	if statuses[id] in ["recovered", "backup_invalid"]:
		var repair: BookButton = _button("Backup erneuern" if statuses[id] == "backup_invalid" else "Backup übernehmen",func() -> void: repair_requested.emit(id))
		repair.accessibility_name = repair.text + " · " + leaf
		card.recovery_content.add_child(repair)
		card.repair = repair
		repair_buttons[id] = repair
	_diagnose(card,id)

func _layout_cards() -> void:
	if grid == null: return
	var gap: int = roundi(12 * ui_scale)
	grid.add_theme_constant_override("h_separation", gap)
	grid.add_theme_constant_override("v_separation", gap)
	# Reserve the actual scrollbar width even before the first container sort.
	var available: float = maxf(1, scroll.size.x - scroll.get_v_scroll_bar().get_combined_minimum_size().x - 2*ui_scale)
	# KU-A: choose columns from the complete measured single-line metadata.
	var minimum_width: float = choices[0].minimum_card_width(ui_scale) if not choices.is_empty() else 280*ui_scale
	var capacity: int = maxi(1, floori((available + gap) / (minimum_width + gap)))
	grid.columns = maxi(1, mini(capacity, choices.size()))
	var card_width: float = minf(minimum_width+16*ui_scale, floorf((available-(capacity-1)*gap)/capacity))
	for node: Node in find_children("*", "Label", true, false):
		if node.has_meta("base_font"): node.add_theme_font_size_override("font_size", roundi(float(node.get_meta("base_font")) * ui_scale))
	for node: Node in find_children("*", "Button", true, false):
		if node is BookButton:
			node.ui_scale = ui_scale
			if node.content_surface: continue
			node.add_theme_font_override("font", Card.UiText.small_font(Card.UiText.small_size(ui_scale)))
			node.add_theme_font_size_override("font_size", Card.UiText.small_size(ui_scale))
			node.custom_minimum_size = Vector2(44,44)*ui_scale if node.text.is_empty() else Vector2(maxf(44*ui_scale,Card.UiText.width(node.get_theme_font("font"),node.text,Card.UiText.small_size(ui_scale))+(56 if node.image != null else 16)*ui_scale),44*ui_scale)
	for card: Card in choices:
		card.ui_scale = ui_scale
		for state: String in ["normal","hover","pressed","disabled","focus"]:
			card.get_theme_stylebox(state).ui_scale = ui_scale
		card.custom_minimum_size.x = card_width
		card.size.x = card_width
		card.layout_content()
	category_choice.custom_minimum_size.y = 44 * ui_scale
	category_choice.ui_scale = ui_scale
	sort_choice.ui_scale = ui_scale
	# Wrap the two-word label at narrow widths; every action and the usual
	# category names keep their budgets without adding another toolbar row.
	sort_label.custom_minimum_size.x = Card.UiText.label_width(sort_label, "Sortieren" if size.x < 1100 * ui_scale else "Sortieren nach", roundi(16 * ui_scale))
	# Native OptionButton measures every item, style padding and its arrow.
	# Keep that complete budget instead of a second fixed-width reservation.
	sort_choice.custom_minimum_size = Vector2(44, 44) * ui_scale
	sort_choice.add_theme_font_size_override("font_size", Card.UiText.small_size(ui_scale))
	sort_choice.get_popup().prefer_native_menu = false
	category_choice.get_popup().max_size = Vector2i(roundi(size.x), roundi(minf(480 * ui_scale, size.y * 0.8)))
	category_choice.get_popup().prefer_native_menu = false
	# PopupMenu scrolls vertically but clips overlong individual entries.
	# Its existing tooltip route exposes the entire measured, wrapped label.
	var tooltip_layout := Vector2(roundi(14 * ui_scale), minf(420 * ui_scale, size.x - 56 * ui_scale))
	if category_tooltip_layout != tooltip_layout:
		category_tooltip_layout = tooltip_layout
		for index: int in range(category_choice.item_count):
			var text: String = category_choice.get_item_text(index)
			var full: String = Card.UiText.wrapped(text, int(tooltip_layout.x), tooltip_layout.y)
			category_choice.get_popup().set_item_tooltip(index, full)
	category_choice.tooltip_text = category_choice.get_popup().get_item_tooltip(category_choice.selected) if category_choice.selected >= 0 else ""

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
	result.action_id = text
	result.focus_mode = Control.FOCUS_ALL
	result.pressed.connect(action)
	return result
