extends RefCounted
## Shared logical transform; center is measured in cells, not OS pixels.
var origin: Vector2 = Vector2(114, 112)
var cell_size: float = 24.0
var dimensions: Vector2i = Vector2i(20, 20)
var viewport: Rect2 = Rect2(0, 0, 10000, 10000)
var center: Vector2 = Vector2(10, 10)

func configure(area: Rect2, dims: Vector2i) -> void:
	viewport = area
	dimensions = dims
	reframe()

func reframe() -> void:
	var half: Vector2 = viewport.size / (2.0 * cell_size)
	for axis: int in range(2):
		center[axis] = float(dimensions[axis]) / 2.0 if half[axis] >= float(dimensions[axis]) / 2.0 else clampf(center[axis], half[axis], float(dimensions[axis]) - half[axis])
	origin = viewport.get_center() - center * cell_size

func zoom_to(step: float, anchor: Vector2) -> void:
	var coordinate: Vector2 = (anchor - origin) / cell_size
	cell_size = step
	center = coordinate - (anchor - viewport.get_center()) / cell_size
	reframe()

func pan(delta: Vector2) -> void:
	center -= delta / cell_size
	reframe()

func bounds() -> Rect2:
	return Rect2(origin, Vector2(dimensions) * cell_size)

func visible_bounds() -> Rect2:
	return bounds().intersection(viewport)

func normalized_view() -> Rect2:
	var visible: Rect2 = visible_bounds()
	return Rect2((visible.position - origin) / bounds().size, visible.size / bounds().size)

func hit(point: Vector2) -> Vector2i:
	if not viewport.has_point(point) or not bounds().has_point(point):
		return Vector2i(-1, -1)
	return Vector2i(floori((point.x - origin.x) / cell_size), floori((point.y - origin.y) / cell_size))

func cell_rect(cell: Vector2i) -> Rect2:
	return Rect2(origin + Vector2(cell) * cell_size, Vector2.ONE * cell_size)
