extends RefCounted
## Fixed synthetic glyph contract, also run against the delivered PCK.
const Text = preload("res://ui/ui_text.gd")
const GLYPHS = "äöüÄÖÜß × · … % ,.;:!?–−/\\()[]{}„“‚‘’\"'&+←→↑↓0123456789"
const TIDY_SHA256 = "9eacc0d857ab9decbc34b0dab150641ba5b5a9560a8d163b6494dd5babbcdfd6"
const PLEX_SHA256 = "3b031aa4216174205bd8471f88a49b91f093169e9e87bd5262242bc5967fe2e3"

static func digest(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()

static func glyph_image(font: FontFile, fs: int, code: int) -> Image:
	var index: int = font.get_glyph_index(fs, code, 0)
	font.render_glyph(0, Vector2i(fs, 0), index)
	var image: Image = font.get_texture_image(0, Vector2i(fs, 0), font.get_glyph_texture_idx(0, Vector2i(fs, 0), index))
	return image.get_region(Rect2i(font.get_glyph_uv_rect(0, Vector2i(fs, 0), index)))

static func dot_columns(image: Image) -> int:
	# Small antialiased dots share low-alpha edge columns. Count three actual
	# coverage maxima separated by valleys, rather than thresholding them into
	# a single connected shape (which wrongly rejects the native 12px raster).
	var groups := 0
	var coverage: Array[float] = []
	for x: int in range(image.get_width()):
		var alpha := 0.0
		for y: int in range(image.get_height()):
			alpha += image.get_pixel(x, y).a
		coverage.append(alpha)
	for x: int in range(1, coverage.size() - 1):
		if coverage[x] > 0.25 and coverage[x] > coverage[x-1] and coverage[x] >= coverage[x+1]: groups += 1
	return groups

static func run(runner: Object) -> void:
	var font: FontFile = Text.font()
	runner.check(font != Text.SOURCE and font.data == Text.SOURCE.data and digest(font.data) == TIDY_SHA256, "HZ original Tidy Hand bytes, private normal UI instance")
	runner.check(digest(Text.FALLBACK.data) == PLEX_SHA256, "HZ original local Plex bytes")
	runner.check(not font.allow_system_fallback and font.fallbacks.size() == 1 and not font.fallbacks[0].allow_system_fallback, "HZ local fallback only")
	var ts: TextServer = TextServerManager.get_primary_interface()
	for fs: int in [12,13,14,15,16,18,19,20,22,23,25,26,28,33,35]:
		var line := TextLine.new()
		line.add_string(GLYPHS, font, fs)
		for glyph: Dictionary in ts.shaped_text_get_glyphs(line.get_rid()):
			runner.check(glyph.index > 0 and glyph.font_rid in font.get_rids(), "HZ complete locally shaped inventory at %d" % fs)
		var ellipsis: Image = glyph_image(font, fs, 0x2026)
		runner.check(dot_columns(ellipsis) == 3 and ellipsis.get_height() <= fs * 0.45, "HZ three distinct native ellipsis dots at %d" % fs)
		runner.check(ellipsis.get_data() == glyph_image(Text.SOURCE, fs, 0x2026).get_data(), "HZ ellipse pixels come from original Tidy Hand")
		var long_line := TextLine.new()
		long_line.add_string("TEST lange Kategorie mit Größen und Äpfeln", font, fs)
		ts.shaped_text_overrun_trim_to_width(long_line.get_rid(), 8 * fs, TextServer.OVERRUN_TRIM | TextServer.OVERRUN_ADD_ELLIPSIS)
		var glyphs: Array[Dictionary] = ts.shaped_text_get_ellipsis_glyphs(long_line.get_rid())
		runner.check(glyphs.size() == 1 and glyphs[0].font_rid == font.get_rids()[0] and glyphs[0].index == font.get_glyph_index(fs, 0x2026, 0), "HZ native automatic trimming uses Tidy Hand ellipse")
		runner.check(Text.ink(font, "Größe · … ←", fs).size.y > 0, "HZ measured fallback ink")
	var bakso: FontFile = preload("res://art/drawing/BaksoDaging-Regular.ttf")
	var wrong_ellipse: Image = glyph_image(bakso, 24, 0x2026)
	runner.check(dot_columns(wrong_ellipse) != 3 or wrong_ellipse.get_height() > 24 * 0.45, "HZ negative control detects Bakso's incorrect ellipse; title workaround retained")
	for character: String in ["×", "„", "‚", "–", "−", "←", "→", "↑", "↓"]:
		var line := TextLine.new()
		line.add_string(character, font, 18)
		var glyphs: Array[Dictionary] = ts.shaped_text_get_glyphs(line.get_rid())
		runner.check(glyphs.size() == 1 and glyphs[0].font_rid == font.fallbacks[0].get_rids()[0], "HZ missing character bound to Plex: " + character)
	for character: String in "äöüÄÖÜß·…%":
		var line := TextLine.new()
		line.add_string(character, font, 18)
		var glyphs: Array[Dictionary] = ts.shaped_text_get_glyphs(line.get_rid())
		runner.check(glyphs.size() == 1 and glyphs[0].font_rid == font.get_rids()[0], "HZ original Tidy Hand character: " + character)
