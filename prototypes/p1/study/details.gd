extends Control
## Original static pen accents. Never within the board, hit areas, or text.
var app: Control

func _draw() -> void:
	if app == null or not app.work.visible or app.board.style == 0 or app.size.x < 1700 or app.board.view.cell_size > 24:
		return
	var color: Color = Color("635c4b")
	color.a = 0.42 if app.board.style == 1 else 0.30
	var card: Rect2 = app.surface.card
	for offset: float in [0.0, 4.0, 8.0]:
		draw_line(card.end + Vector2(-30 + offset, 6), card.end + Vector2(-25 + offset, 11), color, 1.1, true)
	for well: Rect2 in app.surface.wells:
		var p: Vector2 = well.position + Vector2(8, -5)
		draw_polyline(PackedVector2Array([p, p + Vector2(12, -0.5), p + Vector2(24, 0.8)]), color, 0.9, true)
