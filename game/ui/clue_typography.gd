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

static func cross_width(fs: int, stroke: int = 0) -> float:
	return maxf(1.0, fs / 18.0) * (1.08 if stroke == 0 else 0.96)

static func cross_inset(box: Rect2, fs: int, ui: float) -> float:
	return minf(cross_width(fs) / 2.0 + ui / 4.0 + 0.5, maxf(0, minf(box.size.x, box.size.y) / 2.0 - 0.05))

static func cross_strokes(text: String, fs: int, identity: String, face: Font = null, ui: float = 1.0) -> Array[PackedVector2Array]:
	var strokes: Array[PackedVector2Array] = []
	if not text.is_valid_int(): return strokes
	var box: Rect2 = ink(text, fs, face)
	# Centerlines inset by the largest stroke/C1 radius: the visible X reaches
	# the whole token's edges without avoidable new slot/font reserves.
	box = box.grow(-cross_inset(box, fs, ui))
	# FNV-1a over the original puzzle/axis/line/token identity. No screen, status,
	# clock or font-size input: zoom, tooltip wrapping and restore retain the form.
	var seed: int = 2166136261
	for byte: int in identity.to_utf8_buffer():
		seed = ((seed ^ byte) * 16777619) & 0xffffffff
	var bend: float = [-0.035, 0.025, -0.02, 0.04][seed % 4]
	var end: float = [0.0, 0.025, 0.04, 0.015][(seed >> 2) % 4]
	# All vertices lie within the native whole-token ink rectangle. Both strokes
	# span its full width/height; bounded kinks suggest a single pencil movement.
	for points: Array in [
		[Vector2(0, end), Vector2(0.32, 0.32 + bend), Vector2(0.68, 0.68 - bend), Vector2(1, 1 - end)],
		[Vector2(1 - end, 0), Vector2(0.67 + bend, 0.34), Vector2(0.31 - bend, 0.70), Vector2(end, 1)]]:
		var path: PackedVector2Array = []
		for point: Vector2 in points: path.append(box.position + point * box.size)
		strokes.append(path)
	return strokes

static func number_envelope(text: String, fs: int, ui: float) -> Rect2:
	# Baseline-relative, status/identity-independent maximum for glyph, C1, both
	# pencil widths and AA. Convex rectangle contains every segment/variant.
	var box: Rect2 = ink(text, fs)
	var margin: float = maxf(0.5, ui / 4.0)
	# Native polyline AA extends up to one pixel; glyph AA reserves 0.5 px.
	if text.is_valid_int(): margin = maxf(margin, cross_width(fs) / 2.0 + ui / 4.0 + 1.0 - cross_inset(box, fs, ui))
	return box.grow(margin)

static func ink(text: String, fs: int, face: Font = null) -> Rect2:
	var f: Font = text_font(text) if face == null else face
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
	var box: Rect2 = number_envelope(text, fs, ui)
	box.position += origin
	return box
