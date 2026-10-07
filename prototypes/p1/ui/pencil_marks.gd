extends Control
const Board = preload("res://ui/board.gd")
var board: Control
var mark_clip: Rect2

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
	mark_clip = board.view.viewport
	var alpha: float = board.PREVIEW_ALPHA if board.preview.has(index) else 1.0
	var progress: float = 1.0
	if board.effects.has(index) and not board.preview.has(index):
		var effect: Dictionary = board.effects[index]
		progress = clampf(float(int(board.animation_clock.call()) - int(effect.start)) / (1000000.0 * float(effect.seconds)), 0.0, 1.0)
	if value < 0:
		if board.preview.has(index) or board.effects.has(index):
			outline(box.grow(-2), Color(board.INK, 0.32 * (1.0 if board.preview.has(index) else 1.0 - progress)), 0.8)
		return
	if value == 0:
		for which: int in range(2):
			var path: PackedVector2Array = x_path(index, which)
			var head: float = clampf(progress * 2.0 - which, 0.0, 1.0)
			var weight: float = minf(1.7, box.size.x * 0.09) * (0.9 + variation(index, which + 7) * 0.18)
			for k: int in range(path.size() - 1):
				var a: Vector2 = box.position + box.size * path[k]
				var b: Vector2 = box.position + box.size * path[k + 1]
				var part: float = clampf(head * (path.size() - 1) - k, 0.0, 1.0)
				var middle: Vector2 = a.lerp(b, part)
				stroke(a, middle, Color(board.INK, 0.60 * alpha), weight)
				stroke(middle, b, Color(board.INK, 0.60 * board.PREVIEW_ALPHA), weight)
		return
	if progress < 1.0:
		# Complete static target remains underneath. Opaque paint replaces it only
		# along successive alternating pen passes, never through a global fade.
		draw_fill(box, value, index, board.PREVIEW_ALPHA)
		var inside: Rect2 = box.grow(-0.4 if board.overview else -2.0)
		for k: int in range(6):
			var part: float = clampf(progress * 6.0 - k, 0.0, 1.0)
			if part <= 0.0:
				break
			var width: float = inside.size.x * part
			var left: float = inside.position.x if k % 2 == 0 else inside.end.x - width
			mark_clip = board.view.viewport.intersection(Rect2(left, inside.position.y + inside.size.y * k / 6.0, width, inside.size.y / 6.0))
			draw_fill(box, value, index, 1.0)
		mark_clip = board.view.viewport
	else:
		draw_fill(box, value, index, alpha)

static func variation(index: int, salt: int) -> float:
	# Integer-only cell identity: independent of frames, viewport, zoom and saves.
	var seed: int = (index * 1103515245 + salt * 12345 + 1013904223) & 0x7fffffff
	seed = ((seed ^ (seed >> 13)) * 1274126177) & 0x7fffffff
	return float(seed % 1001) / 1000.0

static func x_path(index: int, which: int) -> PackedVector2Array:
	var a: Vector2 = Vector2(0.27, 0.29) if which == 0 else Vector2(0.72, 0.27)
	var b: Vector2 = Vector2(0.71, 0.72) if which == 0 else Vector2(0.29, 0.70)
	a += Vector2(variation(index, which * 5) - 0.5, variation(index, which * 5 + 1) - 0.5) * 0.11
	b += Vector2(variation(index, which * 5 + 2) - 0.5, variation(index, which * 5 + 3) - 0.5) * 0.11
	var bend: Vector2 = (a + b) * 0.5 + Vector2(variation(index, which * 5 + 4) - 0.5, variation(index, which * 5 + 6) - 0.5) * 0.22
	var result: PackedVector2Array = PackedVector2Array()
	for step: int in range(9):
		var t: float = step / 8.0
		result.append(a.lerp(bend, t).lerp(bend.lerp(b, t), t))
	return result

func draw_fill(box: Rect2, value: int, index: int, alpha: float) -> void:
	if not mark_clip.has_area():
		return
	var fill: Color = Color(board.cell_color(value), alpha)
	var inside: Rect2 = box.grow(-0.4 if board.overview else -2.0)
	if box.size.x < 18 or board.overview:
		draw_rect(inside.intersection(mark_clip), fill)
		return
	var wobble: float = 0.025 + float((index * 17 + 3) % 7) * 0.003
	var points: PackedVector2Array = PackedVector2Array()
	for p: Vector2 in [Vector2(wobble, 0), Vector2(0.96, wobble), Vector2(1, 0.51), Vector2(0.98, 0.98), Vector2(0.48, 1), Vector2(0, 0.97), Vector2(wobble, 0.45)]:
		points.append(inside.position + inside.size * p)
	if mark_clip.encloses(inside):
		draw_colored_polygon(points, fill)
	else:
		var bounds: PackedVector2Array = PackedVector2Array([mark_clip.position, Vector2(mark_clip.end.x, mark_clip.position.y), mark_clip.end, Vector2(mark_clip.position.x, mark_clip.end.y)])
		for polygon: PackedVector2Array in Geometry2D.intersect_polygons(points, bounds):
			# At a moving pass boundary the clipper can return a degenerate
			# subpixel sliver. Do not submit an untriangulatable polygon to Canvas.
			if not Geometry2D.triangulate_polygon(polygon).is_empty():
				draw_colored_polygon(polygon, fill)
	for k: int in range(points.size()):
		stroke(points[k], points[(k + 1) % points.size()], Color(board.cell_color(value).darkened(0.22), 0.55 * alpha), 0.8)
	for k: int in range(3):
		var y: float = 0.26 + k * 0.23
		stroke(inside.position + inside.size * Vector2(0.12, y), inside.position + inside.size * Vector2(0.88, y - wobble), Color(Color.WHITE, 0.12 * alpha), 1.2)

func stroke(a: Vector2, b: Vector2, color: Color, width: float) -> void:
	# Reserve the antialias fringe as well as half the stroke width. The old
	# 0.2px allowance leaked faint X pixels beyond a clipped viewport edge.
	var segment: PackedVector2Array = Board.clipped_segment(a, b, board.view.viewport.grow(-width / 2.0 - 1.0).intersection(mark_clip))
	if segment.size() == 2 and segment[0].distance_to(segment[1]) > 0.01:
		draw_line(segment[0], segment[1], color, width, true)

func outline(box: Rect2, color: Color, width: float) -> void:
	var corners: Array[Vector2] = [box.position, Vector2(box.end.x, box.position.y), box.end, Vector2(box.position.x, box.end.y)]
	for i: int in range(4):
		stroke(corners[i], corners[(i + 1) % 4], color, width)
