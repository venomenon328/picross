extends Control
## Receives only the completion-gated payload. No name/image before a match.
var payload: Dictionary = {}
var paired: bool = true

func _draw() -> void:
	if payload.is_empty():
		return
	var step: float = minf((size.x - 60) / 40, (size.y - 45) / 20) if paired else minf(size.x, size.y) / 20
	var font: Font = ThemeDB.fallback_font
	for side: int in range(2 if paired else 1):
		var origin: Vector2 = Vector2(side * (20 * step + 60), 35) if paired else Vector2.ZERO
		if paired:
			draw_string(font, origin - Vector2(0, 12), "Dein gelöstes Raster" if side == 0 else "Das erarbeitete Motiv", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("343f42"))
		draw_rect(Rect2(origin, Vector2.ONE * step * 20), Color("faf6ec"))
		for y: int in range(20):
			for x: int in range(20):
				var color: String = payload.pixels[y][x]
				if not color.is_empty():
					draw_rect(Rect2(origin + Vector2(x, y) * step, Vector2.ONE * step), Color("343f42") if paired and side == 0 else Color(color))
