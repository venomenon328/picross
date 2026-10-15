extends RefCounted
## HC: immutable original font; all measures are native, in logical pixels.
const SOURCE = preload("res://art/drawing/DelightCoffee-Regular.ttf")
const REFERENCE = preload("res://ui/clue_font.tres")
const SHA256: String = "4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23"
static var font: FontFile
static var vertical_cache: Dictionary = {}
static var web_sizes: Dictionary = {}

static func retain_web_size(f: Font, fs: int) -> void:
	if not OS.has_feature("web"):
		return
	# Exact measurements survive in the numeric caches. Retain only a small
	# working set of rasterized sizes while the exhaustive fit search runs;
	# otherwise a tiny grid can exhaust the WebAssembly heap with glyph atlases.
	var ts: TextServer = TextServerManager.get_primary_interface()
	for rid: RID in f.get_rids():
		var sizes: Array = web_sizes.get(rid, [])
		sizes.erase(fs)
		sizes.append(fs)
		while sizes.size() > 8:
			ts.font_remove_size_cache(rid, Vector2i(int(sizes.pop_front()), 0))
		web_sizes[rid] = sizes

static func selected() -> Font:
	if font == null:
		font = SOURCE.duplicate()
		font.allow_system_fallback = false
		# Only navigation punctuation uses the explicit bundled Plex resource.
		font.fallbacks = []
	return font

static func text_font(text: String) -> Font:
	return selected() if text.is_valid_int() else REFERENCE

static func strike_width(text: String, fs: int, ui: float) -> float:
	var f: Font = text_font(text)
	retain_web_size(f, fs)
	# envelope() always includes this centered numeric status strike plus C1/AA.
	return f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 2.0 * maxf(0.5, ui / 4.0)

static func ink(text: String, fs: int) -> Rect2:
	var f: Font = text_font(text)
	retain_web_size(f, fs)
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = f.get_rids()[0]
	var result: Rect2
	var advance: float = 0.0
	for i: int in range(text.length()):
		var glyph: int = ts.font_get_glyph_index(rid, fs, text.unicode_at(i), 0)
		var box: Rect2 = Rect2(Vector2(advance, 0) + ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph), ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph))
		result = box if i == 0 else result.merge(box)
		advance += f.get_string_size(text[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	return result

static func vertical(fs: int) -> Vector2:
	if not vertical_cache.has(fs):
		if vertical_cache.size() >= 512: vertical_cache.clear()
		var bounds: Vector2 = Vector2(INF, -INF)
		for symbol: String in "0123456789…–":
			var box: Rect2 = ink(symbol, fs)
			bounds.x = minf(bounds.x, box.position.y)
			bounds.y = maxf(bounds.y, box.end.y)
		vertical_cache[fs] = bounds
	return vertical_cache[fs]

static func baseline(fs: int) -> float:
	var bounds: Vector2 = vertical(fs)
	return -(bounds.x + bounds.y) / 2.0

static func envelope(text: String, fs: int, ui: float) -> Rect2:
	var f: Font = text_font(text)
	retain_web_size(f, fs)
	var width: float = f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var origin: Vector2 = Vector2(-width / 2.0, baseline(fs))
	var box: Rect2 = ink(text, fs)
	box.position += origin
	# Include the actual strike thickness and C1/AA, even while status is open.
	if text.is_valid_int():
		var thickness: float = maxf(1.0, fs / 14.0)
		box = box.merge(Rect2(origin - Vector2(0, fs * 0.32 + thickness / 2.0), Vector2(width, thickness)))
	return box.grow(maxf(0.5, ui / 4.0))
