extends RefCounted
## HF: measured text on existing book paper and tiled SL-65 frame strokes.
const TITLE: String = "Vollständiger Hinweis"
const TITLE_SOURCE = preload("res://art/book/Fraunces.ttf")
const PAPER = preload("res://art/book/bp2-a-inventarband.png")
const FRAME = preload("res://art/book/frame-preview.png")
static var heading: FontVariation
static var frame: StyleBoxTexture
static var paper: AtlasTexture

static func title_font() -> Font:
	if heading == null:
		heading = FontVariation.new()
		heading.base_font = TITLE_SOURCE
		heading.variation_opentype = {"wght": 600.0}
	return heading

static func ink(font: Font, text: String, fs: int) -> Rect2:
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var result: Rect2
	for i: int in range(text.length()):
		var glyph: int = ts.font_get_glyph_index(rid, fs, text.unicode_at(i), 0)
		var advance: float = font.get_string_size(text.left(i), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var box: Rect2 = Rect2(Vector2(advance, 0) + ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph), ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph))
		result = box if i == 0 else result.merge(box)
	return result

static func measure(board: Control, entries: Array) -> Dictionary:
	var u: float = board.ui_scale
	var fs: int = board.clue_tooltip_font_size()
	var title_fs: int = roundi(13 * u)
	var padding: float = 28 * u # outside the frame's safe inset (22 * UI)
	var gap: float = 10 * u
	var title_ink: Rect2 = ink(title_font(), TITLE, title_fs).grow(0.5)
	var max_width: float = minf(520 * u, board.size.x - board.view.viewport.position.x - 24 * u)
	max_width = maxf(title_ink.size.x + 2 * padding, max_width)
	var wrap_width: float = max_width - 2 * padding
	var bounds: Array[Rect2] = []
	for entry: Dictionary in entries:
		var font: Font = board.clue_text_font(board.clue_font(), entry.text)
		var box: Rect2 = ink(font, entry.text, fs)
		var width: float = font.get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var thickness: float = maxf(1, fs / 14.0)
		box = box.merge(Rect2(Vector2(0, -fs * 0.32 - thickness / 2), Vector2(width, thickness)))
		bounds.append(box.grow(maxf(0.5, u / 4)))
	# Wrap complete tokens. Each row uses its actual maximum ink/status height.
	var rows: Array[Dictionary] = []
	var row: Dictionary = {"start": 0, "end": 0, "width": 0.0, "top": INF, "bottom": -INF}
	for i: int in range(bounds.size()):
		var width: float = bounds[i].size.x
		if row.end > row.start and float(row.width) + gap + width > wrap_width:
			rows.append(row)
			row = {"start": i, "end": i, "width": 0.0, "top": INF, "bottom": -INF}
		row.width += (gap if row.end > row.start else 0.0) + width
		row.end = i + 1
		row.top = minf(row.top, bounds[i].position.y)
		row.bottom = maxf(row.bottom, bounds[i].end.y)
	rows.append(row)
	var used_width: float = title_ink.size.x
	var y: float = padding + title_ink.size.y + gap
	var positions: Array[Vector2] = []
	var boxes: Array[Rect2] = []
	for line: Dictionary in rows:
		used_width = maxf(used_width, line.width)
		var x: float = padding
		for i: int in range(line.start, line.end):
			var baseline: Vector2 = Vector2(x - bounds[i].position.x, y - float(line.top))
			positions.append(baseline)
			boxes.append(Rect2(bounds[i].position + baseline, bounds[i].size))
			x += bounds[i].size.x + gap
		y += float(line.bottom) - float(line.top) + gap
	var extent: Vector2 = Vector2(used_width + 2 * padding, y - gap + padding).ceil()
	var origin: Vector2 = board.view.viewport.position + Vector2.ONE * 12 * u
	# The board already excludes title, sidebar, warnings and protected paper.
	origin = origin.min(board.size - Vector2.ONE * 8 * u - extent).max(Vector2.ONE * 8 * u)
	return {"rect": Rect2(origin, extent), "positions": positions, "boxes": boxes,
		"title_baseline": Vector2(padding, padding) - title_ink.position,
		"title_box": Rect2(Vector2(padding, padding), title_ink.size),
		"font_size": fs, "title_size": title_fs, "rows": rows.size(), "padding": padding}

static func paint(canvas: CanvasItem, box: Rect2, u: float) -> void:
	if paper == null:
		paper = AtlasTexture.new()
		paper.atlas = PAPER
		paper.region = Rect2(700, 400, 128, 128) # quiet interior of the bound A paper
	if frame == null:
		frame = StyleBoxTexture.new()
		frame.texture = FRAME
		frame.draw_center = false
		frame.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
		frame.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
		for side: int in range(4): frame.set_texture_margin(side, 64)
	# Fixed-size corners and tiled edges preserve the original pencil stroke.
	for side: int in range(4): frame.set_expand_margin(side, 0)
	canvas.draw_texture_rect(paper, box.grow(-10 * u), false)
	canvas.draw_set_transform(box.position, 0, Vector2.ONE * 0.5 * u)
	canvas.draw_style_box(frame, Rect2(Vector2.ZERO, box.size / (0.5 * u)))
	canvas.draw_set_transform(Vector2.ZERO)
