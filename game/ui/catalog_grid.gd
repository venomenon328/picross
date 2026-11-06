extends Container
## KL: flat card ownership, with every occupied row centred independently.
## Reflow never reparents controls or creates empty interaction placeholders.
var columns: int = 1
var content_width: float = 0.0

func arrange(count: int, width: float) -> void:
	if columns == count and is_equal_approx(content_width, width): return
	columns = maxi(1, count)
	content_width = width
	update_minimum_size()
	queue_sort()

func _cell_size() -> Vector2:
	var cell := Vector2.ZERO
	for child: Node in get_children():
		if child is Control and child.visible:
			cell = cell.max(child.get_combined_minimum_size())
	return cell

func _get_minimum_size() -> Vector2:
	var rows: int = ceili(get_child_count() / float(columns))
	var gap: int = get_theme_constant("v_separation")
	# Width comes from projected paper, never from the preceding column count.
	# Old minima must not push a shrinking ScrollContainer beyond the page.
	return Vector2(0, rows * _cell_size().y + maxi(0, rows - 1) * gap)

func _notification(what: int) -> void:
	if what != NOTIFICATION_SORT_CHILDREN: return
	var children: Array[Control] = []
	for child: Node in get_children():
		if child is Control and child.visible: children.append(child)
	var cell: Vector2 = _cell_size()
	var horizontal: int = get_theme_constant("h_separation")
	var vertical: int = get_theme_constant("v_separation")
	for start: int in range(0, children.size(), columns):
		var count: int = mini(columns, children.size() - start)
		var band: float = count * cell.x + (count - 1) * horizontal
		var origin := Vector2(floorf((minf(size.x, content_width) - band) / 2), (start / columns) * (cell.y + vertical))
		for index: int in range(count):
			fit_child_in_rect(children[start + index], Rect2(origin + Vector2(index * (cell.x + horizontal), 0), cell))
