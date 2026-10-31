extends "res://ui/catalog.gd"
## Study-only two-page presentation; one canonical filter/order/page and scroll.
signal page_requested(target: int)
var locked: bool = false
var right_scroll: ScrollContainer
var right_grid: GridContainer
var spread: HBoxContainer
var left_page: VBoxContainer
var right_page: VBoxContainer
var arranging: bool = false
var syncing_scroll: bool = false
var fold_gap: float = 76.0

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
	for item: Node in [sort_label, sort_choice, direction_button]: item.reparent(sorting)
	var actions := HBoxContainer.new()
	for item: Node in top.get_children(): item.reparent(actions)
	summary.reparent(right_page)
	_detach_summary.call_deferred()
	preference_feedback.get_parent().reparent(left_page)
	for item: Node in [feedback, empty_message, all_button, scroll]: item.reparent(left_page)
	right_scroll = ScrollContainer.new()
	right_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	right_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_page.add_child(right_scroll)
	right_grid = GridContainer.new()
	right_scroll.add_child(right_grid)
	scroll.get_v_scroll_bar().value_changed.connect(_sync_scroll.bind(false))
	right_scroll.get_v_scroll_bar().value_changed.connect(_sync_scroll.bind(true))
	var left_pager := HBoxContainer.new()
	left_page.add_child(left_pager)
	previous_button.reparent(left_pager)
	page_label.reparent(left_pager)
	var right_pager := HBoxContainer.new()
	right_pager.alignment = BoxContainer.ALIGNMENT_END
	right_page.add_child(right_pager)
	right_pager.add_child(actions)
	next_button.reparent(right_pager)
	for node: Node in old_children:
		if node.get_parent() == self:
			remove_child(node)
			node.free()
	_layout_cards()

func _detach_summary() -> void:
	# Parent is still in _ready while this catalog is constructed.
	summary.reparent(get_parent())
	get_parent().get_parent()._layout_book()

func _sync_scroll(value: float, from_right: bool) -> void:
	# A partial spread can have unequal ranges. The shorter side must not
	# clamp a new position back into the originating, longer side.
	if syncing_scroll: return
	syncing_scroll = true
	if from_right: scroll.scroll_vertical = int(value)
	else: right_scroll.scroll_vertical = int(value)
	syncing_scroll = false

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

func commit_page(target: int, position: int = 0) -> void:
	page_index = target
	_render(position)

func _render(position: int) -> void:
	# The base owns card lifecycle, metadata, stable IDs and spoiler gates.
	if right_grid != null:
		for child: Node in right_grid.get_children(): child.reparent(grid)
	super._render(position)
	for item: Node in find_children("*","Button",true,false):
		if item is BookButton: item.paper_transparent = true
	if right_scroll != null:
		# Settings and quit share this row but are not pagination controls.
		next_button.visible = previous_button.get_parent().visible

func _layout_cards() -> void:
	if arranging: return
	arranging = true
	if right_grid != null:
		var split: int = ceili(choices.size()/2.0)
		for i: int in range(choices.size()):
			var column: Node = choices[i].get_parent()
			var target: Node = grid if i < split else right_grid
			if column.get_parent() != target: column.reparent(target)
		spread.add_theme_constant_override("separation", roundi(fold_gap))
		for half: VBoxContainer in [left_page, right_page]: half.add_theme_constant_override("separation", roundi(8*ui_scale))
	super._layout_cards()
	if right_grid != null:
		right_grid.columns = grid.columns
		right_grid.add_theme_constant_override("h_separation", roundi(12*ui_scale))
		right_grid.add_theme_constant_override("v_separation", roundi(12*ui_scale))
	arranging = false

func ensure_control_visible(control: Control) -> void:
	if right_grid.is_ancestor_of(control): right_scroll.ensure_control_visible(control)
	else: super.ensure_control_visible(control)
