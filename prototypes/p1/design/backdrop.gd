extends Control
## Original procedural contour/flat-color illustration, independent of fixtures.
var variant: int = 0

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func leaf(origin: Vector2, direction: Vector2, length: float, color: Color) -> void:
	var side: Vector2 = direction.orthogonal() * length * 0.24
	var tip: Vector2 = origin + direction * length
	var points: PackedVector2Array = PackedVector2Array()
	for i: int in range(17):
		var t: float = float(i) / 16
		points.append(origin.lerp(tip, t) + side * sin(t * PI))
	for i: int in range(16, -1, -1):
		var t: float = float(i) / 16
		points.append(origin.lerp(tip, t) - side * sin(t * PI) * 0.7)
	draw_colored_polygon(points, color)
	points.append(origin)
	draw_polyline(points, Color("364c48"), 1.8, true)
	draw_line(origin, tip, Color("415951"), 1.0, true)

func _draw() -> void:
	if variant == 0:
		draw_rect(Rect2(Vector2.ZERO, size), Color("e9ece7"))
		# Fine editorial ruling and a small album registration motif.
		for y: int in range(18, int(size.y), 7):
			draw_line(Vector2(0, y), Vector2(size.x, y), Color(0.2, 0.3, 0.25, 0.015))
		draw_rect(Rect2(36, 30, 5, 45), Color("b45336"))
		return
	draw_rect(Rect2(Vector2.ZERO, size), Color("526d60"))
	# Layered paper-cut curves; abstract garden foliage has no puzzle motif.
	var sweep: PackedVector2Array = PackedVector2Array([Vector2(0, size.y * 0.55)])
	for x: int in range(0, int(size.x) + 41, 40):
		sweep.append(Vector2(x, size.y * 0.78 + sin(float(x) / 310.0) * 80))
	sweep.append(Vector2(size.x, size.y))
	sweep.append(Vector2(0, size.y))
	draw_colored_polygon(sweep, Color("506a60"))
	for i: int in range(6):
		var base: Vector2 = Vector2(size.x * (0.12 + i * 0.17), size.y + 35)
		var tip: Vector2 = base + Vector2(-105 + i * 19, -160 - (i % 3) * 34)
		draw_line(base, tip, Color("354f46"), 3, true)
		for j: int in range(1, 5):
			var node: Vector2 = base.lerp(tip, float(j) / 5)
			leaf(node, Vector2(-0.86, -0.5), 42 + j * 6, Color("91a08a"))
			leaf(node, Vector2(0.8, -0.6), 36 + j * 5, Color("bdba96"))
	# A quiet contour frieze at the top; deliberately no sun, sea or buildings.
	for i: int in range(8):
		var base: Vector2 = Vector2(size.x - 45 - i * 54, -15)
		leaf(base, Vector2(-0.3, 0.95), 105 + (i % 3) * 22, Color("829382"))
	draw_line(Vector2(32, 94), Vector2(size.x - 32, 94), Color("b6bda5"), 1, true)
