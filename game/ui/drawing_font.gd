extends RefCounted
## Byte-identical selected ZS-1 input. Punctuation deliberately remains Plex.
const REFERENCE = preload("res://ui/clue_font.tres")
const CHALKBOARD = preload("res://art/drawing/Chalkboard-Regular.ttf")
const SHA256: String = "163d5acb0c4cc2f54a603501836fda2dcdd1d09579a8d1f790ab882d86175c4d"
static var font: FontFile
static var vertical_cache: Dictionary = {}

static func selected() -> Font:
	if font == null:
		font = CHALKBOARD.duplicate()
		font.allow_system_fallback = false
		font.fallbacks = [REFERENCE]
	return font

static func pixel_size(nominal: int) -> int:
	return roundi(nominal * 1.35)

static func ink_vertical(fs: int) -> Vector2:
	var key: String = str(fs)
	if vertical_cache.has(key):
		return vertical_cache[key]
	var ts: TextServer = TextServerManager.get_primary_interface()
	var bounds: Vector2 = Vector2.ZERO
	for symbol: String in "0123456789…–":
		var font: Font = selected()
		if not symbol.is_valid_int():
			font = REFERENCE
		var rid: RID = font.get_rids()[0]
		var glyph: int = ts.font_get_glyph_index(rid, fs, symbol.unicode_at(0), 0)
		var offset: Vector2 = ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph)
		var extent: Vector2 = ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph)
		bounds.x = minf(bounds.x, offset.y)
		bounds.y = maxf(bounds.y, offset.y + extent.y)
	vertical_cache[key] = bounds
	return bounds
