extends RefCounted
## HZ-A: Tidy Hand for normal text; heading and HC resources stay separate.
const SOURCE = preload("res://art/drawing/TidyHand.ttf")
const FALLBACK = preload("res://art/book/PlexSans.ttf")
static var normal: FontFile
static var dimension_widths: Dictionary = {}
const SMALL_SIZE = 15
# The upright body, without accents/descenders, defines the optical centre.
# Actual strings (including fallback ink) still determine clipping and fit.
const BODY_SAMPLE = "Hhx"
static var small_fonts: Dictionary = {}

static func small_size(u: float) -> int:
	return roundi(SMALL_SIZE * u)

static func line_baseline(typeface: Font, fs: int, height: float) -> float:
	var line := TextLine.new()
	line.add_string(BODY_SAMPLE, typeface, fs)
	return floorf((height - line.get_size().y) / 2.0) + line.get_line_ascent()

static func small_font(fs: int) -> FontVariation:
	if not small_fonts.has(fs):
		# Resource.duplicate() also copies already populated glyph-atlas caches.
		# Their shared textures can be overwritten by subsequent glyph uploads
		# in another size variant (visible in the Web comparison). Start with
		# the original bytes and fresh caches instead.
		var base := FontFile.new()
		base.data = SOURCE.data
		base.allow_system_fallback = false
		base.fallbacks = font().fallbacks
		# A fallback character previously increased native ascent by 2–3 px.
		# Reserve that same safe envelope for every value in this role. Mutate
		# only this private in-memory size cache, never original font bytes or
		# normal/help/heading resources.
		var envelope := TextLine.new()
		envelope.add_string("Hhx Ägß × „‚–−←→↑↓", font(), fs)
		base.set_cache_ascent(0, fs, envelope.get_line_ascent())
		base.set_cache_descent(0, fs, envelope.get_line_descent())
		var body: Rect2 = ink(base, BODY_SAMPLE, fs)
		var native_center: float = line_baseline(base, fs, 44.0) + body.get_center().y
		var variation := FontVariation.new()
		variation.base_font = base
		# FontVariation offsets glyph ink, including local fallback, without
		# altering advances or line metrics. One correction per size, never word.
		variation.baseline_offset = roundf(22.0 - native_center) / base.get_height(fs)
		small_fonts[fs] = variation
	return small_fonts[fs]

static func small_label(label: Label, fs: int, u: float = 1.0) -> void:
	label.add_theme_font_override("font", small_font(fs))
	label.add_theme_font_size_override("font_size", fs)
	var line := TextLine.new()
	line.add_string(BODY_SAMPLE, small_font(fs), fs)
	var envelope: Rect2 = ink(small_font(fs), "Ägß × „‚–−←→↑↓", fs)
	var padding: float = ceilf(maxf(0, maxf(-envelope.position.y-line.get_line_ascent(), envelope.end.y-line.get_line_descent()))) + 1
	var style: StyleBox = label_style(u)
	# Symmetric safety padding preserves the optical centre. Category is top
	# aligned within a fixed two-line reservation; status remains centred.
	style.content_margin_top = padding
	style.content_margin_bottom = padding
	label.add_theme_stylebox_override("normal", style)

static func font() -> FontFile:
	if normal == null:
		normal = SOURCE.duplicate()
		var punctuation: FontFile = FALLBACK.duplicate()
		normal.allow_system_fallback = false
		punctuation.allow_system_fallback = false
		normal.fallbacks = [punctuation]
	return normal

static func ink(typeface: Font, text: String, fs: int) -> Rect2:
	# Measure the shaped glyphs' actual RIDs: a primary-RID character lookup
	# misses fallback arrows/punctuation, kerning and shaped glyph offsets.
	var line := TextLine.new()
	line.add_string(text, typeface, fs)
	var ts: TextServer = TextServerManager.get_primary_interface()
	var result: Rect2
	var has_ink := false
	var pen := Vector2.ZERO
	for glyph: Dictionary in ts.shaped_text_get_glyphs(line.get_rid()):
		for repeat_index: int in range(glyph.repeat):
			var extent: Vector2 = ts.font_get_glyph_size(glyph.font_rid, Vector2i(glyph.font_size, 0), glyph.index)
			if extent.x > 0 and extent.y > 0:
				var origin: Vector2 = pen + glyph.offset + ts.font_get_glyph_offset(glyph.font_rid, Vector2i(glyph.font_size, 0), glyph.index)
				var box := Rect2(origin, extent)
				result = result.merge(box) if has_ink else box
				has_ink = true
			pen.x += glyph.advance
	return result

static func width(typeface: Font, text: String, fs: int) -> float:
	var bounds: Rect2 = ink(typeface, text, fs)
	return ceilf(maxf(typeface.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, bounds.end.x) - minf(0, bounds.position.x))

static func dimensions_width(fs: int) -> float:
	if not dimension_widths.has(fs):
		var widest := 0.0
		# Proportional digits: 50 is not necessarily wider than 40 or 44.
		# Equal operands cover the widest independent width/height combination.
		for number: int in range(1, 51):
			widest = maxf(widest, width(font(), "%d × %d" % [number, number], fs))
		dimension_widths[fs] = widest
	return dimension_widths[fs]

static func label_width(label: Label, text: String, fs: int) -> float:
	var style: StyleBox = label.get_theme_stylebox("normal")
	return width(label.get_theme_font("font"), text, fs) + style.get_minimum_size().x

static func label_height(label: Label, fs: int, lines: int = 1) -> float:
	var typeface: Font = label.get_theme_font("font")
	var line := TextLine.new()
	line.add_string("Ägß · … ←", typeface, fs)
	var height: float = maxf(typeface.get_height(fs), line.get_size().y)
	return ceilf(height * lines + label.get_theme_constant("line_spacing") * (lines - 1) + label.get_theme_stylebox("normal").get_minimum_size().y)

static func label_style(u: float = 1.0) -> StyleBoxEmpty:
	var style := StyleBoxEmpty.new()
	# Measured UI-font overhang plus an antialiasing pixel, also at UI125.
	style.content_margin_left = 2 * u
	style.content_margin_right = 2 * u
	return style

static func wrapped(text: String, fs: int, maximum_width: float) -> String:
	var paragraph := TextParagraph.new()
	paragraph.width = maximum_width
	paragraph.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	paragraph.add_string(text, font(), fs)
	var lines: PackedStringArray = []
	for index: int in range(paragraph.get_line_count()):
		var span: Vector2i = paragraph.get_line_range(index)
		lines.append(text.substr(span.x, span.y - span.x))
	return "\n".join(lines)
