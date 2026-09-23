extends Control
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
const ClueLayout = preload("res://ui/clue_layout.gd")
signal edited
signal pointed(cell: Vector2i)
var session: Session
var view: GridView = GridView.new()
var eraser: bool = false
var hand: bool = false
var active_color: int = 1
var ui_scale: float = 1.0
var accessibility_labels: bool = false
var overview: bool = false
var held_button: MouseButton = MOUSE_BUTTON_NONE
var pan_button: MouseButton = MOUSE_BUTTON_NONE
var pan_target: String = ""
var pan_last: Vector2
var row_clue_position: float = 0.0
var column_clue_position: float = 0.0
var hover: Vector2i = Vector2i(-1, -1)
var clue_hover_axis: String = ""
var clue_hover_index: int = -1
const INK: Color = Color("343f42")
const PAPER: Color = Color("faf6ec")
const ACCENT: Color = Color("be7446")
const WORK_STEPS: Array[float] = [12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 40.0, 44.0, 48.0, 54.0, 60.0, 66.0, 72.0]

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	clip_contents = true
	resized.connect(_layout)
	mouse_exited.connect(clear_clue_hover)
	_layout()

func _layout() -> void:
	if session == null:
		return
	var inset: Vector2 = Vector2(156, 126) * ui_scale
	view.configure(Rect2(inset, (size - inset - Vector2(12, 12)).max(Vector2.ONE)), Vector2i(session.player.width, session.player.height))
	if overview:
		view.zoom_to(minf(view.viewport.size.x / view.dimensions.x, view.viewport.size.y / view.dimensions.y), view.viewport.get_center())
	cancel_gesture()

func cancel_gesture() -> void:
	if session != null:
		session.gesture.cancel()
	held_button = MOUSE_BUTTON_NONE
	pan_button = MOUSE_BUTTON_NONE
	pan_target = ""
	queue_redraw()
	edited.emit()

func navigate_to(normalized: Vector2) -> void:
	if session.gesture.active:
		return
	view.center = normalized.clamp(Vector2.ZERO, Vector2.ONE) * Vector2(view.dimensions)
	view.reframe()
	edited.emit()
	queue_redraw()

func reset_clue_pan() -> void:
	if session.gesture.active:
		return
	row_clue_position = 0.0
	column_clue_position = 0.0
	clear_clue_hover()
	edited.emit()
	queue_redraw()

static func next_zoom_step(current: float, direction: int) -> float:
	if direction > 0:
		for candidate: float in WORK_STEPS:
			if candidate > current + 0.01:
				return candidate
	elif direction < 0:
		for i: int in range(WORK_STEPS.size() - 1, -1, -1):
			if WORK_STEPS[i] < current - 0.01:
				return WORK_STEPS[i]
	return current

func zoom(direction: int, anchor: Vector2) -> void:
	if session.gesture.active:
		return
	var step: float = next_zoom_step(view.cell_size, direction)
	if is_equal_approx(step, view.cell_size):
		return
	overview = false
	view.zoom_to(step, anchor if view.viewport.has_point(anchor) else view.viewport.get_center())
	edited.emit()
	queue_redraw()

func working_size() -> void:
	if session.gesture.active:
		return
	overview = false
	view.zoom_to(24.0, view.viewport.get_center())
	edited.emit()
	queue_redraw()

func fit_all() -> void:
	if session.gesture.active:
		return
	overview = true
	_layout()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		cancel_gesture()

func _input(event: InputEvent) -> void:
	if not is_visible_in_tree() or session == null:
		return
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		cancel_gesture()
		get_viewport().set_input_as_handled()
	var local: InputEvent = make_input_local(event)
	if pan_button != MOUSE_BUTTON_NONE:
		if local is InputEventMouseMotion:
			var delta: Vector2 = local.position - pan_last
			if pan_target == "grid":
				view.pan(delta)
			elif pan_target == "row":
				row_clue_position = clampf(row_clue_position + delta.x / maxf(row_clue_area().size.x, 1.0), 0.0, 1.0)
			elif pan_target == "column":
				column_clue_position = clampf(column_clue_position + delta.y / maxf(column_clue_area().size.y, 1.0), 0.0, 1.0)
			pan_last = local.position
			edited.emit()
			queue_redraw()
		elif local is InputEventMouseButton and not local.pressed and local.button_index == pan_button:
			pan_button = MOUSE_BUTTON_NONE
			pan_target = ""
			get_viewport().set_input_as_handled()
		return
	if not session.gesture.active:
		return
	if local is InputEventMouseMotion:
		pointer_move(local.position, get_viewport().gui_get_hovered_control() == self)
	elif local is InputEventMouseButton and not local.pressed and local.button_index == held_button:
		pointer_release(local.position, get_viewport().gui_get_hovered_control() == self)
		get_viewport().set_input_as_handled()

func _gui_input(event: InputEvent) -> void:
	if session.completed:
		return
	if event is InputEventMouseMotion and not session.gesture.active and pan_button == MOUSE_BUTTON_NONE:
		var cell: Vector2i = view.hit(event.position)
		if cell.x >= 0:
			hover = cell
			pointed.emit(hover)
		update_clue_hover(event.position)
		queue_redraw()
	if event is InputEventMouseButton and event.pressed:
		if session.gesture.active or pan_button != MOUSE_BUTTON_NONE:
			return
		if event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			zoom(1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else -1, event.position)
		elif event.button_index == MOUSE_BUTTON_MIDDLE or (event.button_index == MOUSE_BUTTON_LEFT and hand):
			pan_target = navigation_target(event.position)
			if not pan_target.is_empty():
				pan_button = event.button_index
				pan_last = event.position
		else:
			pointer_press(event.position, event.button_index)
		accept_event()

func clear_clue_hover() -> void:
	clue_hover_axis = ""
	clue_hover_index = -1
	queue_redraw()

func set_clue_hover(axis: String, index: int) -> void:
	clue_hover_axis = axis
	clue_hover_index = index
	queue_redraw()

func update_clue_hover(point: Vector2) -> void:
	var cell: Vector2i = Vector2i(((point - view.origin) / view.cell_size).floor())
	if row_clue_area().has_point(point) and cell.y >= 0 and cell.y < view.dimensions.y and row_hint_overflows(cell.y):
		set_clue_hover("row", cell.y)
	elif column_clue_area().has_point(point) and cell.x >= 0 and cell.x < view.dimensions.x and column_hint_overflows(cell.x):
		set_clue_hover("column", cell.x)
	else:
		clear_clue_hover()

func navigation_target(point: Vector2) -> String:
	if row_clue_area().has_point(point):
		return "row"
	if column_clue_area().has_point(point):
		return "column"
	if view.viewport.has_point(point):
		return "grid"
	return ""

func row_clue_area() -> Rect2:
	var grid: Rect2 = view.visible_bounds()
	return Rect2(Vector2(4.0 * ui_scale, grid.position.y), Vector2(maxf(1.0, grid.position.x - 14.0 * ui_scale), grid.size.y))

func column_clue_area() -> Rect2:
	var grid: Rect2 = view.visible_bounds()
	return Rect2(Vector2(grid.position.x, 4.0 * ui_scale), Vector2(grid.size.x, maxf(1.0, grid.position.y - 14.0 * ui_scale)))

func pointer_press(point: Vector2, button: MouseButton) -> void:
	if session.completed or hand or (button != MOUSE_BUTTON_LEFT and button != MOUSE_BUTTON_RIGHT):
		return
	var target: int = 0 if button == MOUSE_BUTTON_RIGHT else (-1 if eraser else active_color)
	if session.gesture.begin(session.player, view.hit(point), target):
		held_button = button
		queue_redraw()
		edited.emit()

func pointer_move(point: Vector2, over_board: bool) -> void:
	if over_board:
		session.gesture.move(view.hit(point))
	if session.gesture.active:
		hover = session.gesture.endpoint
		pointed.emit(hover)
	queue_redraw()
	edited.emit()

func pointer_release(point: Vector2, over_board: bool) -> void:
	if over_board:
		session.gesture.move(view.hit(point))
	session.finish()
	held_button = MOUSE_BUTTON_NONE
	queue_redraw()
	edited.emit()

func cell_color(value: int) -> Color:
	for entry: Dictionary in session.definition.palette:
		if int(entry.id) == value:
			return Color(entry.color)
	return INK

func clipped_box(box: Rect2, color: Color) -> void:
	var clipped: Rect2 = box.intersection(view.viewport)
	if clipped.has_area():
		draw_rect(clipped, color)

func _draw() -> void:
	if session == null:
		return
	draw_style_box(_paper_style(), Rect2(Vector2.ZERO, size))
	var grid: Rect2 = view.visible_bounds()
	draw_rect(grid, PAPER)
	var values: Array[int] = session.visible_cells()
	var first: Vector2i = Vector2i(((grid.position - view.origin) / view.cell_size).floor()).max(Vector2i.ZERO)
	var last: Vector2i = Vector2i(((grid.end - view.origin) / view.cell_size).ceil()).min(view.dimensions)
	for y: int in range(first.y, last.y):
		for x: int in range(first.x, last.x):
			var box: Rect2 = view.cell_rect(Vector2i(x, y))
			var value: int = values[y * view.dimensions.x + x]
			if value > 0:
				clipped_box(box.grow(-3.0 if not overview else -0.4), cell_color(value))
			elif value == 0 and view.viewport.encloses(box):
				draw_line(box.position + box.size * 0.3, box.position + box.size * 0.7, INK, 1.2, true)
				draw_line(box.position + box.size * Vector2(0.7, 0.3), box.position + box.size * Vector2(0.3, 0.7), INK, 1.2, true)
	for change: Dictionary in session.gesture.changes():
		var box: Rect2 = view.cell_rect(Vector2i(change.index % view.dimensions.x, change.index / view.dimensions.x)).grow(-3)
		if view.viewport.encloses(box):
			draw_rect(box, ACCENT, false, 1.5)
	for x: int in range(first.x, last.x + 1):
		var px: float = view.origin.x + x * view.cell_size
		if px >= grid.position.x and px <= grid.end.x:
			draw_line(Vector2(px, grid.position.y), Vector2(px, grid.end.y), INK if x % 5 == 0 else Color("b5b6ab"), 2.0 if x % 5 == 0 else 1.0)
	for y: int in range(first.y, last.y + 1):
		var py: float = view.origin.y + y * view.cell_size
		if py >= grid.position.y and py <= grid.end.y:
			draw_line(Vector2(grid.position.x, py), Vector2(grid.end.x, py), INK if y % 5 == 0 else Color("b5b6ab"), 2.0 if y % 5 == 0 else 1.0)
	_draw_clues(first, last)
	_draw_clue_tooltip()

func _draw_clues(first: Vector2i, last: Vector2i) -> void:
	var font: Font = ThemeDB.fallback_font
	var fs: int = clue_font_size()
	var near_grid: Vector2 = view.visible_bounds().position
	for y: int in range(first.y, last.y):
		var py: float = view.cell_rect(Vector2i(0, y)).get_center().y
		if py < view.viewport.position.y or py > view.viewport.end.y:
			continue
		if y == hover.y:
			draw_rect(Rect2(4, py - view.cell_size / 2, near_grid.x - 8, view.cell_size), Color("d8ddcc"))
		_draw_row_hint(y, py, font, fs)
	for x: int in range(first.x, last.x):
		var px: float = view.cell_rect(Vector2i(x, 0)).get_center().x
		if px < view.viewport.position.x or px > view.viewport.end.x:
			continue
		if x == hover.x:
			draw_rect(Rect2(px - view.cell_size / 2, 4, view.cell_size, near_grid.y - 8), Color("d8ddcc"))
		_draw_column_hint(x, px, font, fs)

func clue_font_size() -> int:
	return mini(roundi(14 * ui_scale), maxi(8, floori(view.cell_size - 2.0)))

func clue_token(clue: Dictionary) -> String:
	return str(int(clue.length)) + clue_symbol(clue)

func clue_symbol(clue: Dictionary) -> String:
	if accessibility_labels and session.definition.palette.size() > 1:
		for entry: Dictionary in session.definition.palette:
			if int(entry.id) == int(clue.color):
				return str(entry.symbol)
	return ""

func hint_text(clues: Array) -> String:
	var texts: PackedStringArray = []
	for clue: Dictionary in clues:
		texts.append(clue_token(clue))
	return "  ".join(texts) if not texts.is_empty() else "–"

func clue_color(clue: Dictionary) -> Color:
	if session.definition.palette.size() > 1:
		return cell_color(int(clue.color))
	return INK

func row_hint_overflows(index: int) -> bool:
	var layout: Dictionary = clue_layout("row", index)
	return layout.prefix_hidden or layout.suffix_hidden

func column_hint_overflows(index: int) -> bool:
	var layout: Dictionary = clue_layout("column", index)
	return layout.prefix_hidden or layout.suffix_hidden

func clue_layout(axis: String, index: int, available_override: float = -1.0) -> Dictionary:
	var clues: Array = session.definition.rows[index] if axis == "row" else session.definition.columns[index]
	var entries: Array = clue_entries(clues)
	var font: Font = ThemeDB.fallback_font
	var fs: int = clue_font_size()
	var extents: Array[float] = clue_extents(axis, entries, font, fs)
	var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
	var available: float = available_override if available_override >= 0.0 else (area.size.x if axis == "row" else area.size.y)
	var marker_extent: float = clue_marker_extent(axis, font, fs)
	var gap: float = 6.0 * ui_scale if axis == "row" else 3.0 * ui_scale
	var progress: float = row_clue_position if axis == "row" else column_clue_position
	var result: Dictionary = ClueLayout.select_window(extents, available, progress, marker_extent, gap)
	result.entries = entries
	result.extents = extents
	result.marker_extent = marker_extent
	result.gap = gap
	return result

func clue_entries(clues: Array) -> Array:
	var entries: Array = []
	if clues.is_empty():
		entries.append({"text": "–", "number": "–", "symbol": "", "color": INK})
	for clue: Dictionary in clues:
		entries.append({"text": clue_token(clue), "number": str(int(clue.length)), "symbol": clue_symbol(clue), "color": clue_color(clue)})
	return entries

func clue_extents(axis: String, entries: Array, font: Font, fs: int) -> Array[float]:
	var extents: Array[float] = []
	for entry: Dictionary in entries:
		if axis == "row":
			extents.append(font.get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
		else:
			extents.append(float(column_token_metrics(entry, font, fs).extent))
	return extents

func clue_marker_extent(axis: String, font: Font, fs: int) -> float:
	return font.get_string_size("…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x if axis == "row" else maxf(float(fs + 2), 10.0 * ui_scale)

func column_token_metrics(entry: Dictionary, font: Font, fs: int) -> Dictionary:
	var lane: float = maxf(6.0, view.cell_size - 2.0)
	var number: String = str(entry.number)
	var symbol: String = str(entry.symbol)
	var inline_width: float = font.get_string_size(str(entry.text), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	if inline_width <= lane:
		return {"compact": false, "stack_digits": false, "font_size": fs, "suffix_size": 0, "extent": maxf(14.0 * ui_scale, float(fs + 4))}
	var compact_font: int = mini(fs, maxi(8, floori(lane)))
	var number_width: float = font.get_string_size(number, HORIZONTAL_ALIGNMENT_LEFT, -1, compact_font).x
	var stack_digits: bool = number_width > lane
	var number_lines: int = number.length() if stack_digits else 1
	var suffix_size: int = maxi(7, compact_font - 2) if not symbol.is_empty() else 0
	var extent: float = 4.0 + number_lines * float(compact_font + 1) + (float(suffix_size + 1) if suffix_size > 0 else 0.0)
	return {"compact": true, "stack_digits": stack_digits, "font_size": compact_font, "suffix_size": suffix_size, "extent": maxf(extent, 14.0 * ui_scale)}

func tooltip_entries(axis: String, index: int) -> Array:
	var clues: Array = session.definition.rows[index] if axis == "row" else session.definition.columns[index]
	var result: Array = []
	if clues.is_empty():
		result.append({"text": "–", "color": INK})
	for clue: Dictionary in clues:
		result.append({"text": clue_token(clue), "color": clue_color(clue)})
	return result

func _draw_row_hint(index: int, py: float, font: Font, fs: int) -> void:
	var layout: Dictionary = clue_layout("row", index)
	var area: Rect2 = row_clue_area()
	var cursor: float = _aligned_chain_start(area.position.x, area.end.x, layout)
	if layout.prefix_hidden:
		_draw_row_unit("…", ACCENT, cursor, py, font, fs)
		cursor += float(layout.marker_extent) + float(layout.gap)
	for i: int in range(int(layout.start), int(layout.end)):
		var entry: Dictionary = layout.entries[i]
		_draw_row_unit(entry.text, entry.color, cursor, py, font, fs)
		cursor += float(layout.extents[i])
		if i + 1 < int(layout.end) or layout.suffix_hidden:
			cursor += float(layout.gap)
	if layout.suffix_hidden:
		_draw_row_unit("…", ACCENT, cursor, py, font, fs)

func _draw_row_unit(text: String, color: Color, left: float, py: float, font: Font, fs: int) -> void:
	draw_string(font, Vector2(left, py + fs * 0.35), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, color)

func _draw_column_hint(index: int, px: float, font: Font, fs: int) -> void:
	var layout: Dictionary = clue_layout("column", index)
	var area: Rect2 = column_clue_area()
	var cursor: float = _aligned_chain_start(area.position.y, area.end.y, layout)
	if layout.prefix_hidden:
		_draw_column_marker(px, cursor, float(layout.marker_extent), font, fs)
		cursor += float(layout.marker_extent) + float(layout.gap)
	for i: int in range(int(layout.start), int(layout.end)):
		var extent: float = float(layout.extents[i])
		_draw_column_unit(layout.entries[i], px, cursor, extent, font, fs)
		cursor += extent
		if i + 1 < int(layout.end) or layout.suffix_hidden:
			cursor += float(layout.gap)
	if layout.suffix_hidden:
		_draw_column_marker(px, cursor, float(layout.marker_extent), font, fs)

func _aligned_chain_start(start: float, finish: float, layout: Dictionary) -> float:
	var used: float = float(layout.used_extent)
	if not layout.prefix_hidden:
		return start
	if not layout.suffix_hidden:
		return finish - used
	return start + (finish - start - used) / 2.0

func _draw_column_marker(px: float, top: float, extent: float, font: Font, fs: int) -> void:
	var width: float = font.get_string_size("…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(font, Vector2(px - width / 2.0, top + (extent + fs * 0.7) / 2.0), "…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs, ACCENT)

func _draw_column_unit(entry: Dictionary, px: float, top: float, extent: float, font: Font, fs: int) -> void:
	var metrics: Dictionary = column_token_metrics(entry, font, fs)
	if not metrics.compact:
		var width: float = font.get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, Vector2(px - width / 2.0, top + (extent + fs * 0.7) / 2.0), entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, entry.color)
		return
	var lane_width: float = maxf(7.0, view.cell_size - 2.0)
	draw_rect(Rect2(Vector2(px - lane_width / 2.0, top + 1.0), Vector2(lane_width, extent - 2.0)), Color(PAPER, 0.92))
	draw_rect(Rect2(Vector2(px - lane_width / 2.0, top + 1.0), Vector2(lane_width, extent - 2.0)), Color(INK, 0.35), false, 1.0)
	var compact_font: int = int(metrics.font_size)
	var cursor: float = top + 2.0
	var number_parts: Array[String] = []
	if metrics.stack_digits:
		for character: String in str(entry.number):
			number_parts.append(character)
	else:
		number_parts.append(str(entry.number))
	for part: String in number_parts:
		var width: float = font.get_string_size(part, HORIZONTAL_ALIGNMENT_LEFT, -1, compact_font).x
		cursor += compact_font
		draw_string(font, Vector2(px - width / 2.0, cursor), part, HORIZONTAL_ALIGNMENT_LEFT, -1, compact_font, entry.color)
		cursor += 1.0
	if int(metrics.suffix_size) > 0:
		var suffix_size: int = int(metrics.suffix_size)
		var suffix_width: float = font.get_string_size(entry.symbol, HORIZONTAL_ALIGNMENT_LEFT, -1, suffix_size).x
		cursor += suffix_size
		draw_string(font, Vector2(px - suffix_width / 2.0, cursor), entry.symbol, HORIZONTAL_ALIGNMENT_LEFT, -1, suffix_size, entry.color)

func _draw_clue_tooltip() -> void:
	if clue_hover_axis.is_empty() or clue_hover_index < 0:
		return
	var entries: Array = tooltip_entries(clue_hover_axis, clue_hover_index)
	var font: Font = ThemeDB.fallback_font
	var fs: int = roundi(16 * ui_scale)
	var line_height: float = 22 * ui_scale
	var box_width: float = minf(520 * ui_scale, size.x - view.viewport.position.x - 32)
	var positions: Array[Vector2] = []
	var cursor: Vector2 = Vector2(14, 44 * ui_scale)
	for entry: Dictionary in entries:
		var width: float = font.get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if cursor.x + width > box_width - 14:
			cursor.x = 14
			cursor.y += line_height
		positions.append(cursor)
		cursor.x += width + 9 * ui_scale
	var box_height: float = cursor.y + 12 * ui_scale
	var box: Rect2 = Rect2(view.viewport.position + Vector2(12, 12), Vector2(box_width, box_height))
	draw_rect(box, Color("fffaf0"))
	draw_rect(box, ACCENT, false, 2)
	draw_string(font, box.position + Vector2(14, 26 * ui_scale), "Vollständiger Hinweis", HORIZONTAL_ALIGNMENT_LEFT, -1, fs, INK)
	for i: int in range(entries.size()):
		draw_string(font, box.position + positions[i], entries[i].text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, entries[i].color)

static func _paper_style() -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color("f4efdf")
	style.corner_radius_top_left = 12
	style.corner_radius_bottom_right = 12
	return style
