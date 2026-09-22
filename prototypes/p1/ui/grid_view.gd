extends RefCounted
## View coordinates are local to the drawing Control, never OS pixels.
var origin: Vector2 = Vector2(114, 112)
var cell_size: float = 24.0
var dimensions: Vector2i = Vector2i(20, 20)

func bounds() -> Rect2:
	return Rect2(origin, Vector2(dimensions) * cell_size)

func hit(point: Vector2) -> Vector2i:
	if not bounds().has_point(point):
		return Vector2i(-1, -1)
	return Vector2i(floori((point.x - origin.x) / cell_size), floori((point.y - origin.y) / cell_size))

func cell_rect(cell: Vector2i) -> Rect2:
	return Rect2(origin + Vector2(cell) * cell_size, Vector2.ONE * cell_size)
