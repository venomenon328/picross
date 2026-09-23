extends Control
## Only own cells, palette and view rectangle; no solution reference.
signal navigated(point: Vector2)
var cells: Array[int] = []
var width: int = 20
var height: int = 20
var palette: Array = []
var view_rect: Rect2 = Rect2(0, 0, 1, 1)
var interactive: bool = false
var dragging: bool = false

func image_rect() -> Rect2:
	var step: float = minf(size.x / width, size.y / height)
	return Rect2(Vector2.ZERO, Vector2(width, height) * step)

func _gui_input(event: InputEvent) -> void:
	if not interactive:
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		dragging = event.pressed and image_rect().has_point(event.position)
		if dragging:
			navigated.emit(event.position / image_rect().size)
		accept_event()
	elif event is InputEventMouseMotion and dragging:
		navigated.emit((event.position / image_rect().size).clamp(Vector2.ZERO, Vector2.ONE))

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and not event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		dragging = false

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		dragging = false

func _draw() -> void:
	var area: Rect2 = image_rect()
	var step: float = area.size.x / width
	draw_rect(area, Color("faf6ec"))
	for i: int in range(cells.size()):
		var box: Rect2 = Rect2(Vector2(i % width, i / width) * step, Vector2.ONE * step)
		if cells[i] > 0:
			for entry: Dictionary in palette:
				if int(entry.id) == cells[i]:
					draw_rect(box, Color(entry.color))
		elif cells[i] == 0:
			draw_circle(box.get_center(), maxf(0.45, step * 0.16), Color("827765"))
	draw_rect(area, Color("a4a99f"), false, 1)
	if interactive:
		var frame: Rect2 = Rect2(view_rect.position * area.size, view_rect.size * area.size)
		draw_rect(frame.grow(-2), Color.WHITE, false, 3)
		draw_rect(frame.grow(-2), Color("343f42"), false, 1)
