extends Control
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
signal edited
signal pointed(cell: Vector2i)
signal clue_requested(axis: String, index: int)
var session: Session
var view: GridView = GridView.new()
var eraser: bool = false
var hand: bool = false
var active_color: int = 1
var ui_scale: float = 1.0
var overview: bool = false
var held_button: MouseButton = MOUSE_BUTTON_NONE
var pan_button: MouseButton = MOUSE_BUTTON_NONE
var pan_last: Vector2
var hover: Vector2i = Vector2i(-1, -1)
const INK: Color = Color("343f42")
const PAPER: Color = Color("faf6ec")
const ACCENT: Color = Color("be7446")
const WORK_STEPS: Array[float] = [18.0, 24.0, 36.0, 48.0]

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	clip_contents = true
	resized.connect(_layout)
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
	queue_redraw()
	edited.emit()

func navigate_to(normalized: Vector2) -> void:
	if session.gesture.active:
		return
	view.center = normalized.clamp(Vector2.ZERO, Vector2.ONE) * Vector2(view.dimensions)
	view.reframe()
	edited.emit()
	queue_redraw()

func zoom(direction: int, anchor: Vector2) -> void:
	if session.gesture.active:
		return
	var step: float = WORK_STEPS[-1] if direction > 0 else WORK_STEPS[0]
	for candidate: float in (WORK_STEPS if direction > 0 else [48.0, 36.0, 24.0, 18.0]):
		if (direction > 0 and candidate > view.cell_size + 0.01) or (direction < 0 and candidate < view.cell_size - 0.01):
			step = candidate
			break
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
			view.pan(local.position - pan_last)
			pan_last = local.position
			edited.emit()
			queue_redraw()
		elif local is InputEventMouseButton and not local.pressed and local.button_index == pan_button:
			pan_button = MOUSE_BUTTON_NONE
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
		queue_redraw()
	if event is InputEventMouseButton and event.pressed:
		if session.gesture.active or pan_button != MOUSE_BUTTON_NONE:
			return
		if event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			zoom(1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else -1, event.position)
		elif event.button_index == MOUSE_BUTTON_MIDDLE or (event.button_index == MOUSE_BUTTON_LEFT and hand):
			if view.viewport.has_point(event.position):
				pan_button = event.button_index
				pan_last = event.position
		elif event.button_index == MOUSE_BUTTON_LEFT and view.hit(event.position).x < 0:
			request_clue(event.position)
		else:
			pointer_press(event.position, event.button_index)
		accept_event()

func request_clue(point: Vector2) -> void:
	var cell: Vector2i = Vector2i(((point - view.origin) / view.cell_size).floor())
	if point.x < view.visible_bounds().position.x and point.y >= view.viewport.position.y and cell.y >= 0 and cell.y < view.dimensions.y:
		clue_requested.emit("row", cell.y)
	elif point.y < view.visible_bounds().position.y and point.x >= view.viewport.position.x and cell.x >= 0 and cell.x < view.dimensions.x:
		clue_requested.emit("column", cell.x)

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

func _draw_clues(first: Vector2i, last: Vector2i) -> void:
	var font: Font = ThemeDB.fallback_font
	var fs: int = roundi(14 * ui_scale)
	var line_height: float = 19 * ui_scale
	var sparse: int = maxi(1, ceili(line_height / view.cell_size))
	var near_grid: Vector2 = view.visible_bounds().position
	for y: int in range(first.y, last.y):
		var py: float = view.cell_rect(Vector2i(0, y)).get_center().y
		if py < view.viewport.position.y + line_height / 2 or py > view.viewport.end.y - line_height / 2 or (y % sparse != 0 and y != hover.y):
			continue
		var text: String = "%d: %s" % [y + 1, hint_text(session.definition.rows[y])]
		var max_width: float = view.viewport.position.x - 16
		if font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > max_width or sparse > 1:
			text = "%d: … ↗" % (y + 1)
		if y == hover.y:
			draw_rect(Rect2(near_grid.x - max_width - 8, py - line_height / 2, max_width + 6, line_height), Color("d8ddcc"))
		var tw: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, Vector2(near_grid.x - 10 - tw, py + fs * 0.35), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, INK)
	for x: int in range(first.x, last.x):
		var px: float = view.cell_rect(Vector2i(x, 0)).get_center().x
		var stride: int = maxi(sparse, ceili(22 * ui_scale / view.cell_size))
		if px < view.viewport.position.x + 10 or px > view.viewport.end.x - 10 or (x % stride != 0 and x != hover.x):
			continue
		var clues: Array = session.definition.columns[x]
		var room: int = floori((view.viewport.position.y - 35 * ui_scale) / line_height)
		var texts: PackedStringArray = []
		var too_wide: bool = false
		for clue: Dictionary in clues:
			too_wide = too_wide or font.get_string_size(token(clue), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > view.cell_size - 2
		if clues.size() > room or stride > 1 or too_wide:
			texts.append("…↗")
		else:
			for clue: Dictionary in clues:
				texts.append(token(clue))
			if texts.is_empty():
				texts.append("–")
		if x == hover.x:
			draw_rect(Rect2(px - view.cell_size / 2, near_grid.y - (texts.size() + 1) * line_height - 8, view.cell_size, (texts.size() + 1) * line_height + 4), Color("d8ddcc"))
		var number: String = str(x + 1)
		var nw: float = font.get_string_size(number, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, Vector2(px - nw / 2, near_grid.y - view.viewport.position.y + 22 * ui_scale), number, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, INK)
		for i: int in range(texts.size()):
			var tw: float = font.get_string_size(texts[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			draw_string(font, Vector2(px - tw / 2, near_grid.y - 10 - (texts.size() - 1 - i) * line_height), texts[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, INK)

func token(clue: Dictionary) -> String:
	var symbol: String = ""
	if session.definition.palette.size() > 1:
		for entry: Dictionary in session.definition.palette:
			if int(entry.id) == int(clue.color):
				symbol = entry.symbol
	return str(int(clue.length)) + symbol

func hint_text(clues: Array) -> String:
	var texts: PackedStringArray = []
	for clue: Dictionary in clues:
		texts.append(token(clue))
	return "  ".join(texts) if not texts.is_empty() else "–"

static func _paper_style() -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color("f4efdf")
	style.corner_radius_top_left = 12
	style.corner_radius_bottom_right = 12
	return style
