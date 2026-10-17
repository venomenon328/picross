extends Control
## Completion gated artwork, independent of puzzle resolution.
var artwork: Texture2D
var filtered_artwork: Texture2D
var filtered_size: Vector2i = Vector2i.ZERO
var payload: Dictionary = {}:
	set(value):
		payload = value
		artwork = null if value.is_empty() else load(value.image) as Texture2D
		filtered_artwork = null
		filtered_size = Vector2i.ZERO
		texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
var paired: bool = true
var fit_available: bool = false
var solved: Array = []
var palette: Array = []

func display_texture(rect: Rect2) -> Texture2D:
	if artwork == null: return null
	var target := Vector2i(maxi(1,ceili(rect.size.x)),maxi(1,ceili(rect.size.y)))
	if target.x >= artwork.get_width() and target.y >= artwork.get_height(): return artwork
	if filtered_artwork == null or target != filtered_size:
		# One bounded derived texture per earned view, at its actual pixel size.
		# Integrate source detail before linear display; no global filter or blur.
		var image: Image = artwork.get_image()
		image.fix_alpha_edges()
		image.resize(target.x,target.y,Image.INTERPOLATE_LANCZOS)
		filtered_artwork = ImageTexture.create_from_image(image)
		filtered_size = target
	return filtered_artwork

func panel_edge() -> float:
	return minf((size.x - 32) / 2, size.y - 36) if paired else minf(size.x, size.y)

func raster_rect() -> Rect2:
	if solved.is_empty(): return Rect2()
	var step: float = panel_edge() / maxf(solved.size(), solved[0].size())
	return Rect2(Vector2(0,32), Vector2(solved[0].size(),solved.size()) * step)

func artwork_rect() -> Rect2:
	if artwork == null: return Rect2()
	if fit_available:
		var fitted: Vector2 = artwork.get_size()*minf(size.x/artwork.get_width(),size.y/artwork.get_height())
		return Rect2((size-fitted)/2,fitted)
	var offset: Vector2 = Vector2(panel_edge()+32,32) if paired else Vector2.ZERO
	return Rect2(offset, artwork.get_size() * (panel_edge() / maxf(artwork.get_width(),artwork.get_height())))

func _draw() -> void:
	if payload.is_empty():
		return
	var edge: float = panel_edge()
	var offset: Vector2 = Vector2(0, 32) if paired else Vector2.ZERO
	if paired:
		draw_string(ThemeDB.fallback_font, Vector2(0, 22), "Dein gelöstes Raster", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("343f42"))
		draw_string(ThemeDB.fallback_font, Vector2(edge + 32, 22), "Das erarbeitete Motiv", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("343f42"))
		draw_rect(Rect2(offset, Vector2.ONE * edge), Color("faf6ec"))
		if not solved.is_empty():
			var step: float = edge / maxf(solved.size(), solved[0].size())
			for y: int in range(solved.size()):
				for x: int in range(solved[y].size()):
					for entry: Dictionary in palette:
						if int(entry.id) == int(solved[y][x]):
							draw_rect(Rect2(offset + Vector2(x, y) * step, Vector2.ONE * step), Color(entry.color))
		offset.x += edge + 32
	if artwork != null:
		draw_texture_rect(display_texture(artwork_rect()), artwork_rect(), false)
