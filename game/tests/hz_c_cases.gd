extends RefCounted
const Text = preload("res://ui/ui_text.gd")
const Glyphs = preload("res://tests/hz_cases.gd")
const WORDS = ["Neu", "Begonnen", "Gelöst", "Ungültig", "Nicht eingestuft", "Sehr leicht", "Sehr schwer", "Größe × Äpfel – Straße ← …"]

static func run(runner: Object) -> void:
	for fs: int in [14,15,18,19]:
		var font: Font = Text.small_font(fs)
		var private_font: FontFile = font.base_font
		runner.check(private_font.get_rids()[0] != Text.font().get_rids()[0],"HZ-C private font cache RID is separate from normal text")
		for character: String in "HÄgöß…":
			runner.check(Glyphs.glyph_image(private_font,fs,character.unicode_at(0)).get_data() == Glyphs.glyph_image(Text.SOURCE,fs,character.unicode_at(0)).get_data(),"HZ-C private glyph bitmap equals original font: "+character)
		runner.check(Text.font().get_cache_ascent(0,fs) == Text.SOURCE.get_cache_ascent(0,fs) and Text.font().get_cache_descent(0,fs) == Text.SOURCE.get_cache_descent(0,fs),"HZ-C normal/help metrics remain original")
		var reference := TextLine.new()
		reference.add_string(Text.BODY_SAMPLE, font, fs)
		var center: float = Text.line_baseline(font,fs,44) + Text.ink(font,Text.BODY_SAMPLE,fs).get_center().y
		runner.check(absf(center-22) <= 0.5, "HZ-C measured upright body centred at %d" % fs)
		runner.check(font.base_font != Text.font() and font.base_font.data == Text.SOURCE.data and font.variation_transform == Transform2D.IDENTITY and font.variation_embolden == 0, "HZ-C private metrics-only font variant with original bytes")
		for word: String in WORDS:
			var line := TextLine.new()
			line.add_string(word,font,fs)
			runner.check(line.get_line_ascent() == reference.get_line_ascent() and line.get_line_descent() == reference.get_line_descent(), "HZ-C stable native baseline including local fallback: "+word)
			runner.check(font.get_string_size(word,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x == Text.font().get_string_size(word,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x, "HZ-C glyph advances unchanged: "+word)
			var bounds: Rect2 = Text.ink(font,word,fs)
			bounds.position.y += Text.line_baseline(font,fs,44)
			runner.check(bounds.position.y >= 0 and bounds.end.y <= 44, "HZ-C full accent/descender/fallback ink fits hit row")
	# The original direct-word centring produces different baselines. This
	# counterexample must stay different; the new role baseline is shared.
	runner.check(Text.ink(Text.font(),"Neu",15).get_center().y != Text.ink(Text.font(),"Begonnen",15).get_center().y, "HZ-C negative control catches old word-dependent centring")
