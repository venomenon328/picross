extends "res://ui/catalog.gd"
## Shared spread: global filter/order/page, independent half-page scroll.
signal page_requested(target: int)
signal help_requested
var locked: bool = false
var right_scroll: ScrollContainer
var right_grid: CatalogGrid
var spread: HBoxContainer
var left_page: VBoxContainer
var right_page: VBoxContainer
var arranging: bool = false
var next_right_position: int = 0
var fold_gap: float = 76.0
var right_pager: BoxContainer

func _ready() -> void:
	super._ready()
	var top: HBoxContainer = category_choice.get_parent()
	var pager: HBoxContainer = previous_button.get_parent()
	var old_children: Array[Node] = get_children()
	spread = HBoxContainer.new()
	spread.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(spread)
	left_page = VBoxContainer.new()
	right_page = VBoxContainer.new()
	for half: VBoxContainer in [left_page, right_page]:
		half.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		spread.add_child(half)
	var category_row := HBoxContainer.new()
	left_page.add_child(category_row)
	for item: Node in [top.get_child(0), category_choice]: item.reparent(category_row)
	var sorting := HBoxContainer.new()
	right_page.add_child(sorting)
	for item: Node in [sort_label, sort_choice, direction_button, filter_button]: item.reparent(sorting)
	var actions := HBoxContainer.new()
	for item: Node in top.get_children(): item.reparent(actions)
	var help := BookButton.new()
	help.text = "Hilfe"
	help.action_id = "catalog-help"
	help.pressed.connect(func() -> void: help_requested.emit())
	actions.add_child(help)
	actions.move_child(help,1)
	actions.move_child(help,1)
	summary.reparent(right_page)
	_detach_summary.call_deferred()
	preference_feedback.get_parent().reparent(left_page)
	for item: Node in [feedback, empty_message, all_button, scroll]: item.reparent(left_page)
	right_scroll = ScrollContainer.new()
	right_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	right_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_page.add_child(right_scroll)
	right_grid = CatalogGrid.new()
	right_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_scroll.add_child(right_grid)
	right_scroll.resized.connect(_layout_cards)
	for half: ScrollContainer in [scroll,right_scroll]:
		half.mouse_force_pass_scroll_events = false
	var left_pager := HBoxContainer.new()
	left_page.add_child(left_pager)
	previous_button.reparent(left_pager)
	page_label.reparent(left_pager)
	right_pager = BoxContainer.new()
	right_pager.alignment = BoxContainer.ALIGNMENT_END
	right_page.add_child(right_pager)
	right_pager.add_child(actions)
	next_button.reparent(right_pager)
	next_button.size_flags_horizontal = Control.SIZE_SHRINK_END
	for node: Node in old_children:
		if node.get_parent() == self and node != filter_panel:
			remove_child(node)
			node.free()
	_layout_cards()

func _detach_summary() -> void:
	# Parent is still in _ready while this catalog is constructed.
	summary.reparent(get_parent())
	get_parent().get_parent()._layout_book()

func positions() -> Vector2i:
	return Vector2i(scroll.scroll_vertical,right_scroll.scroll_vertical)

func present(sessions: Array[Session], slot_status: Array[String], slot_errors: Array[String], error: String, selection: String) -> void:
	# Base present passes only its legacy left property to _render. Preserve the
	# right half explicitly on redisplay; a real filter/sort still resets both.
	next_right_position = right_scroll.scroll_vertical
	super.present(sessions,slot_status,slot_errors,error,selection)

func restore_positions(pair: Vector2i, expected_generation: int) -> void:
	# A partial -> full spread changes Grid minima in a deferred container pass.
	# Wait for that pass before clamping; the preceding ranges can still be zero.
	await get_tree().process_frame
	if generation != expected_generation: return
	# Each ScrollContainer clamps against its own current content and viewport.
	scroll.scroll_vertical = pair.x
	right_scroll.scroll_vertical = pair.y

func open_filters() -> void:
	if not locked: super.open_filters()

func apply_filters(status: String, mode: String, lower: int, upper: int, cells: String) -> void:
	if not locked: super.apply_filters(status,mode,lower,upper,cells)

func reset_filters() -> void:
	if not locked: super.reset_filters()

func choose_category(id: String) -> void:
	if not locked: super.choose_category(id)

func choose_sort(criterion: String) -> void:
	if not locked: super.choose_sort(criterion)

func reverse_sort() -> void:
	if not locked: super.reverse_sort()

func turn_page(delta: int) -> void:
	if locked: return
	var target: int = clampi(page_index + delta, 0, maxi(0, ceili(filtered_ids.size()/float(PAGE_SIZE))-1))
	if target != page_index: page_requested.emit(target)

func commit_page(target: int, position: int = 0, right_position: int = 0) -> void:
	page_index = target
	next_right_position = right_position
	_render(position)

func _render(position: int) -> void:
	var pair := Vector2i(position,next_right_position)
	var old_page: int = page_index
	next_right_position = 0
	# The base owns card lifecycle, metadata, stable IDs and spoiler gates.
	if right_grid != null:
		for child: Node in right_grid.get_children(): child.reparent(grid)
	super._render(position)
	if page_index != old_page: pair = Vector2i.ZERO
	for item: Node in find_children("*","Button",true,false):
		if item is BookButton: item.paper_transparent = true
	if right_scroll != null:
		# Settings and quit share this row but are not pagination controls.
		next_button.visible = previous_button.get_parent().visible
		restore_positions.call_deferred(pair,generation)

func _shared_card_width() -> float:
	var width: float = super._shared_card_width()
	return minf(width, _available_card_width(right_scroll)) if right_scroll != null else width

func _layout_cards() -> void:
	if arranging: return
	arranging = true
	if right_grid != null:
		var split: int = mini(12,choices.size())
		for i: int in range(choices.size()):
			var column: Node = choices[i].get_parent()
			var target: Node = grid if i < split else right_grid
			if column.get_parent() != target: column.reparent(target)
		spread.add_theme_constant_override("separation", roundi(fold_gap))
		for half: VBoxContainer in [left_page, right_page]: half.add_theme_constant_override("separation", roundi(8*ui_scale))
	super._layout_cards()
	if right_grid != null:
		right_grid.add_theme_constant_override("h_separation", roundi(12*ui_scale))
		right_grid.add_theme_constant_override("v_separation", roundi(12*ui_scale))
		right_grid.arrange(grid.columns, _available_card_width(right_scroll))
	arranging = false

func ensure_control_visible(control: Control) -> void:
	if right_grid.is_ancestor_of(control): right_scroll.ensure_control_visible(control)
	else: super.ensure_control_visible(control)
