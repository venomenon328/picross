extends Control
## Completion gated artwork, independent of puzzle resolution.
var artwork: Texture2D
var payload: Dictionary = {}:
	set(value):
		payload = value
		artwork = null if value.is_empty() else load(value.image) as Texture2D
var paired: bool = true
var solved: Array = []
var palette: Array = []

func _draw() -> void:
	if payload.is_empty():
		return
	var edge: float = minf((size.x - 32) / 2, size.y - 36) if paired else minf(size.x, size.y)
	var offset: Vector2 = Vector2(0, 32) if paired else Vector2.ZERO
	if paired:
		draw_string(ThemeDB.fallback_font, Vector2(0, 22), "Dein gelöstes Raster", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("343f42"))
		draw_string(ThemeDB.fallback_font, Vector2(edge + 32, 22), "Das erarbeitete Motiv", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("343f42"))
		draw_rect(Rect2(offset, Vector2.ONE * edge), Color("faf6ec"))
		if not solved.is_empty():
			var step: float = edge / solved.size()
			for y: int in range(solved.size()):
				for x: int in range(solved[y].size()):
					for entry: Dictionary in palette:
						if int(entry.id) == int(solved[y][x]):
							draw_rect(Rect2(offset + Vector2(x, y) * step, Vector2.ONE * step), Color(entry.color))
		offset.x += edge + 32
	if artwork != null:
		draw_texture_rect(artwork, Rect2(offset, Vector2.ONE * edge), false)
