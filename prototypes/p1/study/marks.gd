extends Control
const Board = preload("res://ui/board.gd")
var board: Control

func _draw() -> void:
	if board.session == null or board.style == 0:
		return
	var started: int = Time.get_ticks_usec()
	var grid: Rect2 = board.view.visible_bounds()
	var values: Array[int] = board.session.visible_cells()
	var active: Vector2i = board.session.gesture.endpoint if board.session.gesture.active else board.hover
	draw_active_bands(grid, active)
	var first: Vector2i = Vector2i(((grid.position - board.view.origin) / board.view.cell_size).floor()).max(Vector2i.ZERO)
	var last: Vector2i = Vector2i(((grid.end - board.view.origin) / board.view.cell_size).ceil()).min(board.view.dimensions)
	for y: int in range(first.y, last.y):
		for x: int in range(first.x, last.x):
			var index: int = y * board.view.dimensions.x + x
			if values[index] >= 0 or board.preview.has(index) or board.effects.has(index):
				draw_cell(board.view.cell_rect(Vector2i(x, y)), values[index], index)
	if board.measure_draws:
		board.draw_times_us.append(Time.get_ticks_usec() - started)

func draw_active_bands(grid: Rect2, active: Vector2i) -> void:
	if active.x >= 0 and active.y >= 0 and active.x < board.view.dimensions.x and active.y < board.view.dimensions.y:
		var active_box: Rect2 = board.view.cell_rect(active)
		var row: Rect2 = Rect2(Vector2(grid.position.x, active_box.position.y), Vector2(grid.size.x, active_box.size.y)).intersection(grid)
		var column: Rect2 = Rect2(Vector2(active_box.position.x, grid.position.y), Vector2(active_box.size.x, grid.size.y)).intersection(grid)
		var band: Color = Color("e8e9d9")
		if row.has_area() and column.has_area():
			draw_rect(row, band)
			draw_rect(Rect2(column.position, Vector2(column.size.x, maxf(0.0, row.position.y - column.position.y))), band)
			draw_rect(Rect2(Vector2(column.position.x, row.end.y), Vector2(column.size.x, maxf(0.0, column.end.y - row.end.y))), band)

func draw_cell(box: Rect2, value: int, index: int) -> void:
	var alpha: float = board.PREVIEW_ALPHA if board.preview.has(index) else 1.0
	var progress: float = 1.0
	if board.effects.has(index) and not board.preview.has(index):
		var effect: Dictionary = board.effects[index]
		progress = clampf(float(Time.get_ticks_usec() - int(effect.start)) / (1000000.0 * float(effect.seconds)), 0.0, 1.0)
		alpha = lerpf(board.PREVIEW_ALPHA, 1.0, 1.0 - pow(1.0 - progress, 2))
	if value < 0:
		if board.preview.has(index) or board.effects.has(index):
			outline(box.grow(-2), Color(board.INK, 0.32 * (1.0 if board.preview.has(index) else 1.0 - progress)), 0.8)
		return
	if value == 0:
		var weight: float = minf(2.0 if board.style == 1 else 1.7, box.size.x * 0.09)
		var color: Color = Color(board.INK, alpha * (0.68 if board.style == 1 else 0.60))
		var bend: float = float((index * 13 + 7) % 5 - 2) * 0.009
		stroke(box.position + box.size * Vector2(0.31, 0.30), box.position + box.size * Vector2(0.49, 0.50 + bend), color, weight)
		stroke(box.position + box.size * Vector2(0.49, 0.50 + bend), box.position + box.size * Vector2(0.69, 0.70), color, weight)
		stroke(box.position + box.size * Vector2(0.70, 0.31), box.position + box.size * Vector2(0.50 + bend, 0.49), color, weight)
		stroke(box.position + box.size * Vector2(0.50 + bend, 0.49), box.position + box.size * Vector2(0.30, 0.69), color, weight)
		return
	var fill: Color = Color(board.cell_color(value), alpha)
	var inside: Rect2 = box.grow(-0.4 if board.overview else -2.0)
	if box.size.x < 18 or board.overview:
		draw_rect(inside.intersection(board.view.viewport), fill)
		return
	var wobble: float = 0.025 + float((index * 17 + 3) % 7) * 0.003
	var points: PackedVector2Array = PackedVector2Array()
	for p: Vector2 in [Vector2(wobble, 0), Vector2(0.96, wobble), Vector2(1, 0.51), Vector2(0.98, 0.98), Vector2(0.48, 1), Vector2(0, 0.97), Vector2(wobble, 0.45)]:
		points.append(inside.position + inside.size * p)
	if board.view.viewport.encloses(inside):
		draw_colored_polygon(points, fill)
	else:
		var bounds: PackedVector2Array = PackedVector2Array([board.view.viewport.position, Vector2(board.view.viewport.end.x, board.view.viewport.position.y), board.view.viewport.end, Vector2(board.view.viewport.position.x, board.view.viewport.end.y)])
		for polygon: PackedVector2Array in Geometry2D.intersect_polygons(points, bounds):
			draw_colored_polygon(polygon, fill)
	if board.style == 1:
		for k: int in range(3):
			var offset: float = 0.16 + k * 0.22 + wobble
			stroke(inside.position + inside.size * Vector2(offset, 0.80), inside.position + inside.size * Vector2(offset + 0.16, 0.20), Color(Color.WHITE, 0.15 * alpha), 0.8)
	else:
		for k: int in range(points.size()):
			stroke(points[k], points[(k + 1) % points.size()], Color(board.cell_color(value).darkened(0.22), 0.55 * alpha), 0.8)
		for k: int in range(3):
			var y: float = 0.26 + k * 0.23
			stroke(inside.position + inside.size * Vector2(0.12, y), inside.position + inside.size * Vector2(0.88, y - wobble), Color(Color.WHITE, 0.12 * alpha), 1.2)

func stroke(a: Vector2, b: Vector2, color: Color, width: float) -> void:
	var segment: PackedVector2Array = Board.clipped_segment(a, b, board.view.viewport.grow(-width / 2.0 - 0.2))
	if segment.size() == 2 and segment[0].distance_to(segment[1]) > 0.01:
		draw_line(segment[0], segment[1], color, width, true)

func outline(box: Rect2, color: Color, width: float) -> void:
	var corners: Array[Vector2] = [box.position, Vector2(box.end.x, box.position.y), box.end, Vector2(box.position.x, box.end.y)]
	for i: int in range(4):
		stroke(corners[i], corners[(i + 1) % 4], color, width)
