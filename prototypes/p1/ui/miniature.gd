extends Control
## This component has no solution/definition reference.
var cells: Array[int] = []
var width: int = 20
var ink: Color = Color("343f42")

func _draw() -> void:
	var edge: float = minf(size.x, size.y)
	var step: float = edge / width
	draw_rect(Rect2(Vector2.ZERO, Vector2.ONE * edge), Color("faf6ec"))
	for i: int in range(cells.size()):
		var box: Rect2 = Rect2(Vector2(i % width, i / width) * step, Vector2.ONE * step)
		if cells[i] > 0:
			draw_rect(box, ink)
		elif cells[i] == 0:
			draw_circle(box.get_center(), maxf(1, step * 0.12), Color("9c8874"))
	draw_rect(Rect2(Vector2.ZERO, Vector2.ONE * edge), Color("a4a99f"), false, 1)
