extends Control
const Scribble = preload("res://ui/scribble.gd")
## Only own cells, palette and view rectangle; no solution reference.
var cells: Array[int] = []
var width: int = 20
var height: int = 20
var palette: Array = []
var view_rect: Rect2 = Rect2(0, 0, 1, 1)
var interactive: bool = false
var dragging: bool = false
var style_identity: String = "miniature"

func image_rect() -> Rect2:
	var step: float = minf(size.x / width, size.y / height)
	return Rect2(Vector2.ZERO, Vector2(width, height) * step)

func frame_strokes() -> Array:
	return Scribble.outline_strokes(image_rect().grow(-1.0),style_identity,1.2)

func _gui_input(event: InputEvent) -> void:
	# Passive even if an obsolete caller tries to enable interactivity.
	pass

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
	# X and unknown intentionally project to the same neutral paper. The input
	# matrix is kept intact for the main grid, history, H1 and persistence.
	for line: Dictionary in frame_strokes():
		Scribble.paint(self,line,Color("a4a99f"))
