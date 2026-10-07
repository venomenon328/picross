extends RefCounted
## Exact owner inputs; navigation punctuation deliberately uses explicit Plex glyphs.
const REFERENCE = preload("res://ui/clue_font.tres")
const BAKSO = preload("res://study/fonts/BaksoDaging-Regular.ttf")
const CHALKBOARD = preload("res://study/fonts/Chalkboard-Regular.ttf")
const LABELS: Array[String] = ["Plex · Referenz", "Bakso Daging", "Chalkboard"]
const HASHES: Array[String] = ["", "56372bf12a6e4fa47a655ff9b2c4cc73172ddd387b3a047093d3e637d081790e", "163d5acb0c4cc2f54a603501836fda2dcdd1d09579a8d1f790ab882d86175c4d"]
static var candidates: Array[Font] = []
static var vertical_cache: Dictionary = {}

static func raw(choice: int) -> FontFile:
	return BAKSO if choice == 1 else CHALKBOARD

static func selected(choice: int) -> Font:
	if choice == 0:
		return REFERENCE
	if candidates.is_empty():
		for source: FontFile in [BAKSO, CHALKBOARD]:
			var font: FontFile = source.duplicate()
			font.allow_system_fallback = false
			font.fallbacks = [REFERENCE]
			candidates.append(font)
	return candidates[choice - 1]

static func evidence(choice: int) -> Dictionary:
	var font: Font = selected(choice)
	var report: Dictionary = {"choice": choice, "label": LABELS[choice], "family": font.get_font_name(), "style": font.get_font_style_name()}
	if choice > 0:
		var bytes: PackedByteArray = raw(choice).data
		var hashing: HashingContext = HashingContext.new()
		hashing.start(HashingContext.HASH_SHA256)
		hashing.update(bytes)
		report.sha256 = hashing.finish().hex_encode()
		report.digits_native = true
		for digit: String in "0123456789":
			report.digits_native = report.digits_native and raw(choice).has_char(digit.unicode_at(0))
		report.plex_punctuation = ["…", "–"]
		report.missing_native_punctuation = []
		for symbol: String in "…–":
			if not raw(choice).has_char(symbol.unicode_at(0)):
				report.missing_native_punctuation.append(symbol)
	return report

static func pixel_size(choice: int, nominal: int) -> int:
	# Chalkboard has substantially smaller ink within its em. Uniform size
	# normalization preserves the original outlines and all advance metrics.
	return roundi(nominal * 1.35) if choice == 2 else nominal

static func ink_vertical(choice: int, fs: int) -> Vector2:
	var key: String = "%d/%d" % [choice, fs]
	if vertical_cache.has(key):
		return vertical_cache[key]
	var ts: TextServer = TextServerManager.get_primary_interface()
	var bounds: Vector2 = Vector2.ZERO
	for symbol: String in "0123456789…–":
		var font: Font = selected(choice)
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
