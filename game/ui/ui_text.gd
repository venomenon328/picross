extends RefCounted
## HZ-A: Tidy Hand for normal text; heading and HC resources stay separate.
const SOURCE = preload("res://art/drawing/TidyHand.ttf")
const FALLBACK = preload("res://art/book/PlexSans.ttf")
static var normal: FontFile
static var dimension_widths: Dictionary = {}

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
	# misses ß, middle dots, arrows, kerning and every other local fallback.
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
