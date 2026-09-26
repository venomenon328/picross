extends Control
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
const ClueLayout = preload("res://ui/clue_layout.gd")
const ClueCompletion = preload("res://model/clue_completion.gd")
signal edited
signal committed
signal view_changed
signal pointed(cell: Vector2i)
var session: Session
var view: GridView = GridView.new()
var eraser: bool = false
var hand: bool = false
var active_color: int = 1
var ui_scale: float = 1.0
# Optional Z1 frame styling; the regular renderer keeps its original default.
var frame_style: StyleBox = null
var overview: bool = false
var held_button: MouseButton = MOUSE_BUTTON_NONE
var pan_button: MouseButton = MOUSE_BUTTON_NONE
var pan_target: String = ""
var pan_line_index: int = -1
var pan_last: Vector2
var pan_origin: Vector2
var pan_drag_distance: float = 0.0
var row_clue_steps: Array[int] = []
var column_clue_steps: Array[int] = []
var row_clue_reads: Array[Dictionary] = []
var column_clue_reads: Array[Dictionary] = []
var hover: Vector2i = Vector2i(-1, -1)
var clue_hover_axis: String = ""
var clue_hover_index: int = -1
var row_slot_extent_cache: Dictionary = {}
var mark_completed_clues: bool = true
var completion_searches: int = 0
var completion_cache: Dictionary = {}
var completion_session: Session
var completion_cells: Array[int] = []
const INK: Color = Color("343f42")
const PAPER: Color = Color("faf6ec")
const ACCENT: Color = Color("be7446")
const PREVIEW_LINE: Color = Color("fffaf0")
const WORK_STEPS: Array[float] = [12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 40.0, 44.0, 48.0, 54.0, 60.0, 66.0, 72.0]

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	clip_contents = true
	resized.connect(_layout)
	mouse_exited.connect(clear_pointer_hover)
	_layout()

func _layout() -> void:
	if session == null:
		return
	var inset: Vector2 = Vector2(156, 126) * ui_scale
	view.configure(Rect2(inset, (size - inset - Vector2(12, 12)).max(Vector2.ONE)), Vector2i(session.player.width, session.player.height))
	if overview:
		view.zoom_to(minf(view.viewport.size.x / view.dimensions.x, view.viewport.size.y / view.dimensions.y), view.viewport.get_center())
	ensure_clue_steps()
	normalize_clue_steps()
	cancel_gesture()

func cancel_gesture() -> void:
	if session != null:
		session.gesture.cancel()
	held_button = MOUSE_BUTTON_NONE
	pan_button = MOUSE_BUTTON_NONE
	pan_target = ""
	pan_line_index = -1
	pan_drag_distance = 0.0
	queue_redraw()
	edited.emit()

func navigate_to(normalized: Vector2) -> void:
	if session.gesture.active:
		return
	view.center = normalized.clamp(Vector2.ZERO, Vector2.ONE) * Vector2(view.dimensions)
	view.reframe()
	view_changed.emit()
	edited.emit()
	queue_redraw()

func reset_clue_pan() -> void:
	if session.gesture.active:
		return
	ensure_clue_steps()
	row_clue_steps.fill(0)
	column_clue_steps.fill(0)
	for index: int in range(row_clue_reads.size()):
		row_clue_reads[index] = ClueLayout.grid_end_position()
	for index: int in range(column_clue_reads.size()):
		column_clue_reads[index] = ClueLayout.grid_end_position()
	clear_clue_hover()
	view_changed.emit()
	edited.emit()
	queue_redraw()

func ensure_clue_steps() -> void:
	if session == null:
		return
	if row_clue_steps.size() != session.player.height or row_clue_reads.size() != session.player.height:
		row_clue_steps.clear()
		row_clue_steps.resize(session.player.height)
		row_clue_steps.fill(0)
		row_clue_reads.clear()
		for index: int in range(session.player.height):
			row_clue_reads.append(ClueLayout.grid_end_position())
	if column_clue_steps.size() != session.player.width or column_clue_reads.size() != session.player.width:
		column_clue_steps.clear()
		column_clue_steps.resize(session.player.width)
		column_clue_steps.fill(0)
		column_clue_reads.clear()
		for index: int in range(session.player.width):
			column_clue_reads.append(ClueLayout.grid_end_position())

func normalize_clue_steps() -> void:
	ensure_clue_steps()
	var row_capacity: int = clue_capacity("row")
	for index: int in range(row_clue_steps.size()):
		row_clue_steps[index] = ClueLayout.offset_for_read_position(clue_entry_count("row", index), row_capacity, row_clue_reads[index])
	var column_capacity: int = clue_capacity("column")
	for index: int in range(column_clue_steps.size()):
		column_clue_steps[index] = ClueLayout.offset_for_read_position(clue_entry_count("column", index), column_capacity, column_clue_reads[index])

func clue_step(axis: String, index: int) -> int:
	ensure_clue_steps()
	return row_clue_steps[index] if axis == "row" else column_clue_steps[index]

func set_clue_step(axis: String, index: int, value: int) -> void:
	ensure_clue_steps()
	var count: int = clue_entry_count(axis, index)
	var capacity: int = clue_capacity(axis)
	var window: Dictionary = ClueLayout.select_window(count, capacity, value)
	var position: Dictionary = ClueLayout.read_position(count, capacity, int(window.offset))
	if axis == "row":
		row_clue_steps[index] = int(window.offset)
		row_clue_reads[index] = position
	else:
		column_clue_steps[index] = int(window.offset)
		column_clue_reads[index] = position

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
	normalize_clue_steps()
	view_changed.emit()
	edited.emit()
	queue_redraw()

func working_size() -> void:
	if session.gesture.active:
		return
	overview = false
	view.zoom_to(24.0, view.viewport.get_center())
	normalize_clue_steps()
	view_changed.emit()
	edited.emit()
	queue_redraw()

func fit_all() -> void:
	if session.gesture.active:
		return
	overview = true
	_layout()
	view_changed.emit()

func capture_view() -> Dictionary:
	ensure_clue_steps()
	return {"center": [view.center.x, view.center.y], "zoom": 24 if overview else roundi(view.cell_size),
		"overview": overview, "active_color": active_color,
		"tool": "hand" if hand else ("erase" if eraser else "fill"),
		"row_clue_reads": row_clue_reads.duplicate(true), "column_clue_reads": column_clue_reads.duplicate(true)}

func restore_view(state: Dictionary) -> void:
	cancel_gesture()
	view.center = Vector2(float(state.center[0]), float(state.center[1]))
	overview = state.overview
	view.cell_size = float(state.zoom)
	active_color = int(state.active_color)
	eraser = state.tool == "erase"
	hand = state.tool == "hand"
	row_clue_reads.clear()
	column_clue_reads.clear()
	for read: Dictionary in state.row_clue_reads:
		row_clue_reads.append(read.duplicate(true))
	for read: Dictionary in state.column_clue_reads:
		column_clue_reads.append(read.duplicate(true))
	row_clue_steps.resize(session.player.height)
	column_clue_steps.resize(session.player.width)
	_layout()
	view.reframe()
	clear_clue_hover()
	queue_redraw()

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
				hover = view.hit(local.position)
				if hover.x >= 0:
					pointed.emit(hover)
			elif pan_target in ["row", "column"] and pan_line_index >= 0:
				var total_delta: Vector2 = local.position - pan_origin
				pan_drag_distance = total_delta.x if pan_target == "row" else total_delta.y
				hover = Vector2i(-1, -1)
			pan_last = local.position
			if pan_target == "grid":
				view_changed.emit()
			edited.emit()
			queue_redraw()
		elif local is InputEventMouseButton and not local.pressed and local.button_index == pan_button:
			if pan_target in ["row", "column"] and pan_line_index >= 0:
				var old_step: int = clue_step(pan_target, pan_line_index)
				set_clue_step(pan_target, pan_line_index, closest_clue_snap(pan_target, pan_line_index))
				if old_step != clue_step(pan_target, pan_line_index):
					view_changed.emit()
			pan_button = MOUSE_BUTTON_NONE
			pan_target = ""
			pan_line_index = -1
			pan_drag_distance = 0.0
			queue_redraw()
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
		hover = cell
		if cell.x >= 0:
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
				pan_line_index = navigation_line(event.position, pan_target)
				if pan_target == "grid" or (pan_line_index >= 0 and int(clue_layout(pan_target, pan_line_index).max_offset) > 0):
					pan_button = event.button_index
					if pan_target != "grid":
						hover = Vector2i(-1, -1)
					pan_last = event.position
					pan_origin = event.position
					pan_drag_distance = 0.0
				else:
					pan_target = ""
					pan_line_index = -1
		else:
			pointer_press(event.position, event.button_index)
		accept_event()

func clear_clue_hover() -> void:
	clue_hover_axis = ""
	clue_hover_index = -1
	queue_redraw()

func clear_pointer_hover() -> void:
	clear_clue_hover()
	if not session.gesture.active:
		hover = Vector2i(-1, -1)
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

func navigation_line(point: Vector2, target: String) -> int:
	if target == "row":
		var row: int = floori((point.y - view.origin.y) / view.cell_size)
		return row if row >= 0 and row < view.dimensions.y else -1
	if target == "column":
		var column: int = floori((point.x - view.origin.x) / view.cell_size)
		return column if column >= 0 and column < view.dimensions.x else -1
	return -1

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
		hover = session.gesture.endpoint
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
	var changed: bool = session.finish()
	held_button = MOUSE_BUTTON_NONE
	if changed:
		committed.emit()
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

static func clipped_segment(a: Vector2, b: Vector2, bounds: Rect2) -> PackedVector2Array:
	var delta: Vector2 = b - a
	var start: float = 0.0
	var finish: float = 1.0
	for edge: Vector2 in [Vector2(-delta.x, a.x - bounds.position.x), Vector2(delta.x, bounds.end.x - a.x), Vector2(-delta.y, a.y - bounds.position.y), Vector2(delta.y, bounds.end.y - a.y)]:
		if is_zero_approx(edge.x):
			if edge.y < 0.0:
				return PackedVector2Array()
		elif edge.x < 0.0:
			start = maxf(start, edge.y / edge.x)
		else:
			finish = minf(finish, edge.y / edge.x)
		if start > finish:
			return PackedVector2Array()
	return PackedVector2Array([a + delta * start, a + delta * finish])

func draw_clipped_x(box: Rect2) -> void:
	var bounds: Rect2 = view.viewport.grow(-0.65)
	for endpoints: Array in [[box.position + box.size * 0.3, box.position + box.size * 0.7], [box.position + box.size * Vector2(0.7, 0.3), box.position + box.size * Vector2(0.3, 0.7)]]:
		var segment: PackedVector2Array = clipped_segment(endpoints[0], endpoints[1], bounds)
		if segment.size() == 2 and segment[0].distance_to(segment[1]) > 0.01:
			draw_line(segment[0], segment[1], INK, 1.2, true)

func draw_clipped_preview_outline(box: Rect2) -> void:
	var bounds: Rect2 = view.viewport.grow(-0.8)
	for endpoints: Array in [[box.position, Vector2(box.end.x, box.position.y)], [Vector2(box.end.x, box.position.y), box.end], [box.end, Vector2(box.position.x, box.end.y)], [Vector2(box.position.x, box.end.y), box.position]]:
		var segment: PackedVector2Array = clipped_segment(endpoints[0], endpoints[1], bounds)
		if segment.size() == 2 and segment[0].distance_to(segment[1]) > 0.01:
			draw_line(segment[0], segment[1], PREVIEW_LINE, 1.5, true)

func gesture_length() -> int:
	if not session.gesture.active:
		return 0
	return maxi(absi(session.gesture.endpoint.x - session.gesture.start.x), absi(session.gesture.endpoint.y - session.gesture.start.y)) + 1

func _draw() -> void:
	if session == null:
		return
	draw_style_box(frame_style if frame_style != null else _paper_style(), Rect2(Vector2.ZERO, size))
	var grid: Rect2 = view.visible_bounds()
	draw_rect(grid, PAPER)
	var values: Array[int] = session.visible_cells()
	sync_clue_completion(values)
	var first: Vector2i = Vector2i(((grid.position - view.origin) / view.cell_size).floor()).max(Vector2i.ZERO)
	var last: Vector2i = Vector2i(((grid.end - view.origin) / view.cell_size).ceil()).min(view.dimensions)
	var active: Vector2i = session.gesture.endpoint if session.gesture.active else hover
	if active.x >= 0 and active.y >= 0 and active.x < view.dimensions.x and active.y < view.dimensions.y:
		var active_box: Rect2 = view.cell_rect(active)
		var row: Rect2 = Rect2(Vector2(grid.position.x, active_box.position.y), Vector2(grid.size.x, active_box.size.y)).intersection(grid)
		var column: Rect2 = Rect2(Vector2(active_box.position.x, grid.position.y), Vector2(active_box.size.x, grid.size.y)).intersection(grid)
		var band: Color = Color("e8e9d9")
		if row.has_area() and column.has_area():
			draw_rect(row, band)
			draw_rect(Rect2(column.position, Vector2(column.size.x, maxf(0.0, row.position.y - column.position.y))), band)
			draw_rect(Rect2(Vector2(column.position.x, row.end.y), Vector2(column.size.x, maxf(0.0, column.end.y - row.end.y))), band)
	for y: int in range(first.y, last.y):
		for x: int in range(first.x, last.x):
			var box: Rect2 = view.cell_rect(Vector2i(x, y))
			var value: int = values[y * view.dimensions.x + x]
			if value > 0:
				clipped_box(box.grow(-2.0 if not overview else -0.4), cell_color(value))
			elif value == 0:
				draw_clipped_x(box)
	for change: Dictionary in session.gesture.changes():
		var box: Rect2 = view.cell_rect(Vector2i(change.index % view.dimensions.x, change.index / view.dimensions.x)).grow(-2)
		if box.intersects(view.viewport):
			draw_clipped_preview_outline(box)
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
	_draw_gesture_counter()

func _draw_gesture_counter() -> void:
	if not session.gesture.active:
		return
	var font: Font = ThemeDB.fallback_font
	var fs: int = roundi(15 * ui_scale)
	var caption: String = str(gesture_length())
	var box_size: Vector2 = font.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(14, 10)
	var end_point: Vector2 = view.cell_rect(session.gesture.endpoint).get_center()
	var place: Vector2 = (end_point + Vector2(12, -box_size.y - 8)).clamp(view.viewport.position + Vector2(2, 2), view.viewport.end - box_size - Vector2(2, 2))
	var box: Rect2 = Rect2(place, box_size)
	_draw_counter_box(box, caption, font, fs)

func _draw_counter_box(box: Rect2, caption: String, font: Font, fs: int) -> void:
	draw_rect(box, Color("fffaf0"))
	draw_rect(box, ACCENT, false, 1.0)
	draw_string(font, box.position + Vector2(7, box.size.y - 5), caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, INK)

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

## One entry per complete row/column, never a growing cache of past previews.
## Definitions are immutable within a Session. Full snapshots also detect old
## preview arms, in-place restore and undo without changing gameplay signals.
func sync_clue_completion(values: Array[int]) -> void:
	if completion_session != session:
		completion_session = session
		completion_cache.clear()
		completion_cells.clear()
	if values == completion_cells:
		return
	completion_cells = values.duplicate()
	for axis: String in ["row", "column"]:
		var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
		for index: int in range(lines.size()):
			var cells: Array[int] = []
			var length: int = session.player.width if axis == "row" else session.player.height
			for p: int in range(length):
				cells.append(values[index * session.player.width + p] if axis == "row" else values[p * session.player.width + index])
			var key: String = "%s/%d" % [axis, index]
			if completion_cache.has(key) and completion_cache[key].cells == cells:
				continue
			completion_cache[key] = {"cells": cells, "flags": ClueCompletion.analyze(cells, lines[index])}
			completion_searches += 1

func completion_flags(axis: String, index: int) -> Array[bool]:
	sync_clue_completion(session.visible_cells())
	return completion_cache["%s/%d" % [axis, index]].flags.duplicate()

func clue_is_marked(axis: String, index: int, token: int) -> bool:
	if not mark_completed_clues or token < 0:
		return false
	var flags: Array[bool] = completion_cache["%s/%d" % [axis, index]].flags
	return token < flags.size() and flags[token]

func draw_clue_number(font: Font, baseline: Vector2, text: String, fs: int, color: Color, marked: bool) -> void:
	draw_string(font, baseline, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, color)
	if marked:
		var width: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var start: Vector2 = baseline - Vector2(0, float(fs) * 0.32)
		draw_line(start, start + Vector2(width, 0), Color(color, 0.72), maxf(1.0, float(fs) / 14.0), true)

func clue_font_size() -> int:
	return mini(roundi(14 * ui_scale), maxi(8, floori(view.cell_size - 4.0)))

func clue_token(clue: Dictionary) -> String:
	return str(int(clue.length))

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
	var capacity: int = clue_capacity(axis, available_override)
	var result: Dictionary = ClueLayout.select_window(entries.size(), capacity, clue_step(axis, index))
	result.entries = entries
	result.slot_extent = shared_clue_slot_extent(axis, ThemeDB.fallback_font, clue_font_size())
	return result

func visible_clue_layout(axis: String, index: int) -> Dictionary:
	var result: Dictionary = clue_layout(axis, index)
	result.visual_shift = 0.0
	if pan_button != MOUSE_BUTTON_NONE and pan_target == axis and pan_line_index == index:
		var pitch: float = maxf(float(result.slot_extent), 1.0)
		# Marker reservations make read offsets non-linear in screen space.
		# Clamp in the same token coordinates used by drawing and drop scoring.
		var grid: Dictionary = ClueLayout.select_window(result.entries.size(), int(result.slot_count), 0)
		var outer: Dictionary = ClueLayout.select_window(result.entries.size(), int(result.slot_count), int(result.max_offset))
		var origin_slot: int = int(result.token_slot) - int(result.start)
		var low: float = float(int(grid.token_slot) - int(grid.start) - origin_slot) * pitch
		var high: float = float(int(outer.token_slot) - int(outer.start) - origin_slot) * pitch
		result.visual_shift = clampf(pan_drag_distance, low, high)
	return result

func clue_entry_count(axis: String, index: int) -> int:
	var clues: Array = session.definition.rows[index] if axis == "row" else session.definition.columns[index]
	return maxi(1, clues.size())

func clue_capacity(axis: String, available_override: float = -1.0) -> int:
	var font: Font = ThemeDB.fallback_font
	var fs: int = clue_font_size()
	var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
	var available: float = available_override if available_override >= 0.0 else (area.size.x if axis == "row" else area.size.y)
	var slot_extent: float = shared_clue_slot_extent(axis, font, fs)
	return maxi(3, floori(available / slot_extent))

func clue_entries(clues: Array) -> Array:
	var entries: Array = []
	if clues.is_empty():
		entries.append({"text": "–", "color": INK})
	for clue: Dictionary in clues:
		entries.append({"text": clue_token(clue), "color": clue_color(clue)})
	return entries

func shared_clue_slot_extent(axis: String, font: Font, fs: int) -> float:
	if axis == "column":
		return maxf(16.0 * ui_scale, float(fs) + 6.0 * ui_scale)
	# Every visible row requests the same slot width. Measuring all tokens for
	# each row on every redraw made F-03 take hundreds of milliseconds per frame.
	# Definitions are immutable within a Session; scale and font size form the
	# remaining geometry inputs.
	var key: String = "%d/%d/%s" % [session.get_instance_id(), fs, str(ui_scale)]
	if row_slot_extent_cache.has(key):
		return float(row_slot_extent_cache[key])
	var width: float = font.get_string_size("…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	for line: Array in session.definition.rows:
		if line.is_empty():
			width = maxf(width, font.get_string_size("–", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
		for clue: Dictionary in line:
			width = maxf(width, font.get_string_size(clue_token(clue), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	var extent: float = maxf(24.0 * ui_scale, width + 8.0 * ui_scale)
	row_slot_extent_cache[key] = extent
	return extent

func clue_slot_origin(axis: String, area: Rect2, layout: Dictionary) -> float:
	var finish: float = area.end.x if axis == "row" else area.end.y
	return finish - float(layout.slot_count) * float(layout.slot_extent)

func clue_slot_center(axis: String, area: Rect2, layout: Dictionary, slot: int) -> float:
	return clue_slot_origin(axis, area, layout) + (float(slot) + 0.5) * float(layout.slot_extent)

func tooltip_entries(axis: String, index: int) -> Array:
	sync_clue_completion(session.visible_cells())
	var clues: Array = session.definition.rows[index] if axis == "row" else session.definition.columns[index]
	var result: Array = []
	if clues.is_empty():
		result.append({"text": "–", "color": INK})
	for i: int in range(clues.size()):
		result.append({"text": clue_token(clues[i]), "color": clue_color(clues[i]), "marked": clue_is_marked(axis, index, i)})
	return result

## The snapped read stays unchanged during a drag. Derive both the moving
## tokens and the edge markers from the same temporary screen positions.
func visual_hint_units(axis: String, index: int) -> Dictionary:
	var layout: Dictionary = visible_clue_layout(axis, index)
	var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
	var font: Font = ThemeDB.fallback_font
	var fs: int = clue_font_size()
	var units: Array[Dictionary] = []
	if is_zero_approx(float(layout.visual_shift)):
		for unit: Dictionary in layout.units:
			units.append({"kind": unit.kind, "index": unit.get("index", -1),
				"center": clue_slot_center(axis, area, layout, int(unit.slot))})
		return {"units": units, "prefix_hidden": layout.prefix_hidden, "suffix_hidden": layout.suffix_hidden}
	var low: float = area.position.x if axis == "row" else area.position.y
	var high: float = area.end.x if axis == "row" else area.end.y
	var candidates: Array[Dictionary] = []
	var first_visible: int = layout.entries.size()
	var last_visible: int = -1
	for token_index: int in range(layout.entries.size()):
		var token: Dictionary = layout.entries[token_index]
		var slot: int = int(layout.token_slot) + token_index - int(layout.start)
		var center: float = clue_slot_center(axis, area, layout, slot) + float(layout.visual_shift)
		var before: float = font.get_string_size(str(token.text), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x / 2.0 if axis == "row" else float(fs)
		var after: float = before if axis == "row" else float(fs) * 0.35
		if center - before >= low and center + after <= high:
			candidates.append({"kind": "token", "index": token_index, "center": center, "before": before, "after": after})
			first_visible = mini(first_visible, token_index)
			last_visible = token_index
	var prefix_hidden: bool = first_visible > 0
	var suffix_hidden: bool = last_visible < layout.entries.size() - 1
	var marker_before: float = font.get_string_size("…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x / 2.0 if axis == "row" else float(fs)
	var marker_after: float = marker_before if axis == "row" else float(fs) * 0.35
	var prefix_center: float = clue_slot_center(axis, area, layout, 0)
	var suffix_center: float = clue_slot_center(axis, area, layout, int(layout.slot_count) - 1)
	if prefix_hidden:
		units.append({"kind": "prefix", "index": -1, "center": prefix_center})
	for candidate: Dictionary in candidates:
		var center: float = float(candidate.center)
		if prefix_hidden and center - float(candidate.before) < prefix_center + marker_after and center + float(candidate.after) > prefix_center - marker_before:
			continue
		if suffix_hidden and center - float(candidate.before) < suffix_center + marker_after and center + float(candidate.after) > suffix_center - marker_before:
			continue
		units.append(candidate)
	if suffix_hidden:
		units.append({"kind": "suffix", "index": -1, "center": suffix_center})
	return {"units": units, "prefix_hidden": prefix_hidden, "suffix_hidden": suffix_hidden}

## Compare the same rendered tokens before mouse-up with every valid resting
## window. Marker slots make clue offsets non-linear in screen coordinates.
func closest_clue_snap(axis: String, index: int) -> int:
	var visible: Dictionary = visual_hint_units(axis, index)
	var layout: Dictionary = visible_clue_layout(axis, index)
	var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
	var best_offset: int = clue_step(axis, index)
	var best_distance: float = INF
	var best_count: int = -1
	var best_total: float = INF
	for offset: int in range(int(layout.max_offset) + 1):
		var candidate: Dictionary = ClueLayout.select_window(layout.entries.size(), int(layout.slot_count), offset)
		var total: float = 0.0
		var shared: int = 0
		for unit: Dictionary in visible.units:
			if unit.kind != "token" or int(unit.index) < int(candidate.start) or int(unit.index) >= int(candidate.end):
				continue
			var slot: int = int(candidate.token_slot) + int(unit.index) - int(candidate.start)
			var delta: float = clue_slot_center(axis, area, layout, slot) - float(unit.center)
			total += delta * delta
			shared += 1
		if shared == 0:
			continue
		var distance: float = total / float(shared)
		if distance < best_distance - 0.001 or (absf(distance - best_distance) <= 0.001 and (shared > best_count or (shared == best_count and (total < best_total - 0.001 or (absf(total - best_total) <= 0.001 and offset < best_offset))))):
			best_offset = offset
			best_distance = distance
			best_count = shared
			best_total = total
	return best_offset

func _draw_row_hint(index: int, py: float, font: Font, fs: int) -> void:
	var layout: Dictionary = visible_clue_layout("row", index)
	var area: Rect2 = row_clue_area()
	for unit: Dictionary in visual_hint_units("row", index).units:
		var text: String = "…" if unit.kind != "token" else str(layout.entries[int(unit.index)].text)
		var color: Color = ACCENT if unit.kind != "token" else Color(layout.entries[int(unit.index)].color)
		var center: float = float(unit.center)
		var width: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if center - width / 2.0 >= area.position.x and center + width / 2.0 <= area.end.x:
			draw_clue_number(font, Vector2(center - width / 2.0, py + fs * 0.35), text, fs, color, unit.kind == "token" and clue_is_marked("row", index, int(unit.index)))

func _draw_column_hint(index: int, px: float, font: Font, fs: int) -> void:
	var layout: Dictionary = visible_clue_layout("column", index)
	var area: Rect2 = column_clue_area()
	for unit: Dictionary in visual_hint_units("column", index).units:
		var text: String = "…" if unit.kind != "token" else str(layout.entries[int(unit.index)].text)
		var color: Color = ACCENT if unit.kind != "token" else Color(layout.entries[int(unit.index)].color)
		var center: float = float(unit.center)
		var width: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		if center - fs >= area.position.y and center + fs * 0.35 <= area.end.y:
			draw_clue_number(font, Vector2(px - width / 2.0, center + fs * 0.35), text, fs, color, unit.kind == "token" and clue_is_marked("column", index, int(unit.index)))

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
		draw_clue_number(font, box.position + positions[i], entries[i].text, fs, entries[i].color, entries[i].get("marked", false))

static func _paper_style() -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color("f4efdf")
	style.corner_radius_top_left = 12
	style.corner_radius_bottom_right = 12
	return style
