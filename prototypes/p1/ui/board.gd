extends Control
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
signal edited
signal pointed(cell: Vector2i)
var session: Session
var view: GridView = GridView.new()
var eraser: bool = false
var active_color: int = 1
var held_button: MouseButton = MOUSE_BUTTON_NONE
var hover: Vector2i = Vector2i(-1, -1)
const INK: Color = Color("343f42")
const PAPER: Color = Color("faf6ec")
const ACCENT: Color = Color("be7446")

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(_layout)
	mouse_exited.connect(func() -> void:
		if not session.gesture.active:
			hover = Vector2i(-1, -1)
			pointed.emit(hover)
			queue_redraw())
	_layout()

func _layout() -> void:
	if session == null:
		return
	# #8 fits F-01 completely; scrolling/zoom belong to #9.
	view.cell_size = floorf(minf((size.y - 122.0) / 20.0, (size.x - 170.0) / 20.0))
	view.cell_size = maxf(16.0, view.cell_size)
	view.origin = Vector2(floorf((size.x - view.cell_size * 20.0 + 100.0) / 2.0), 104)
	cancel_gesture()

func cancel_gesture() -> void:
	if session != null:
		session.gesture.cancel()
	held_button = MOUSE_BUTTON_NONE
	queue_redraw()
	edited.emit()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		cancel_gesture()

func _input(event: InputEvent) -> void:
	if not is_visible_in_tree() or session == null:
		return
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		cancel_gesture()
		get_viewport().set_input_as_handled()
	if not session.gesture.active:
		return
	var local: InputEvent = make_input_local(event)
	if local is InputEventMouseMotion:
		var over_board: bool = get_viewport().gui_get_hovered_control() == self
		pointer_move(local.position, over_board)
	elif local is InputEventMouseButton and not local.pressed and local.button_index == held_button:
		# Release can arrive outside the board. Only the last valid endpoint is used.
		pointer_release(local.position, get_viewport().gui_get_hovered_control() == self)
		get_viewport().set_input_as_handled()

func _gui_input(event: InputEvent) -> void:
	if session.completed:
		return
	if event is InputEventMouseMotion and not session.gesture.active:
		hover = view.hit(event.position)
		pointed.emit(hover)
		queue_redraw()
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT or event.button_index == MOUSE_BUTTON_RIGHT:
			pointer_press(event.position, event.button_index)
			accept_event()

func pointer_press(point: Vector2, button: MouseButton) -> void:
	if session.completed or (button != MOUSE_BUTTON_LEFT and button != MOUSE_BUTTON_RIGHT):
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

func _draw() -> void:
	if session == null:
		return
	var font: Font = ThemeDB.fallback_font
	var font_size: int = 16
	var grid: Rect2 = view.bounds()
	draw_style_box(_paper_style(), Rect2(Vector2.ZERO, size))
	draw_rect(grid, PAPER)
	if hover.x >= 0:
		draw_rect(Rect2(Vector2(grid.position.x - 80, grid.position.y + hover.y * view.cell_size), Vector2(80, view.cell_size)), Color("e3e7d6"))
		draw_rect(Rect2(Vector2(grid.position.x + hover.x * view.cell_size, grid.position.y - 62), Vector2(view.cell_size, 62)), Color("e3e7d6"))
	var values: Array[int] = session.visible_cells()
	for y: int in range(20):
		for x: int in range(20):
			var box: Rect2 = view.cell_rect(Vector2i(x, y))
			var value: int = values[y * 20 + x]
			if value > 0:
				draw_rect(box.grow(-1), Color(session.definition.palette[0].color))
			elif value == 0:
				draw_line(box.position + box.size * 0.28, box.position + box.size * 0.72, INK, 1.5, true)
				draw_line(box.position + box.size * Vector2(0.72, 0.28), box.position + box.size * Vector2(0.28, 0.72), INK, 1.5, true)
	if hover.x >= 0:
		draw_rect(Rect2(grid.position + Vector2(0, hover.y * view.cell_size), Vector2(grid.size.x, view.cell_size)), Color(0.74, 0.45, 0.27, 0.12))
		draw_rect(Rect2(grid.position + Vector2(hover.x * view.cell_size, 0), Vector2(view.cell_size, grid.size.y)), Color(0.74, 0.45, 0.27, 0.12))
	for change: Dictionary in session.gesture.changes():
		var cell: Vector2i = Vector2i(change.index % 20, change.index / 20)
		draw_rect(view.cell_rect(cell).grow(-2), ACCENT, false, 2.0)
	for i: int in range(21):
		var thickness: float = 2.0 if i % 5 == 0 else 1.0
		var color: Color = INK if i % 5 == 0 else Color("a4a99f")
		draw_line(grid.position + Vector2(i * view.cell_size, 0), grid.position + Vector2(i * view.cell_size, grid.size.y), color, thickness)
		draw_line(grid.position + Vector2(0, i * view.cell_size), grid.position + Vector2(grid.size.x, i * view.cell_size), color, thickness)
	for y: int in range(20):
		var text: String = hint_text(session.definition.rows[y])
		var baseline: float = grid.position.y + y * view.cell_size + (view.cell_size + font_size) / 2 - 3
		draw_string(font, Vector2(grid.position.x - 12 - font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x, baseline), text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, INK)
	for x: int in range(20):
		var clues: Array = session.definition.columns[x]
		var texts: Array[String] = []
		for clue: Dictionary in clues:
			texts.append(str(int(clue.length)))
		if texts.is_empty():
			texts.append("–")
		for i: int in range(texts.size()):
			var text: String = texts[i]
			var text_width: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
			draw_string(font, Vector2(grid.position.x + (x + 0.5) * view.cell_size - text_width / 2, grid.position.y - 10 - (texts.size() - 1 - i) * 19), text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, INK)

static func hint_text(clues: Array) -> String:
	var texts: PackedStringArray = []
	for clue: Dictionary in clues:
		texts.append(str(int(clue.length)))
	return "  ".join(texts) if not texts.is_empty() else "–"

static func _paper_style() -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color("f4efdf")
	style.corner_radius_top_left = 12
	style.corner_radius_bottom_right = 12
	return style
