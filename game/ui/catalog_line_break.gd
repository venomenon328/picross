extends RefCounted
## Display-only wrapping for catalog titles and the two recovery actions.
const UiText = preload("res://ui/ui_text.gd")
const LEXICON = "res://data/hyphenation/de-1996.deflate"
const ELLIPSIS = "..."
static var lexicon: PackedByteArray

static func _points(word: String) -> PackedStringArray:
	if lexicon.is_empty():
		lexicon = FileAccess.get_file_as_bytes(LEXICON).decompress_dynamic(12 * 1024 * 1024, FileAccess.COMPRESSION_DEFLATE)
	var low := 0
	var high := lexicon.size()
	while low < high:
		@warning_ignore("integer_division")
		var row: int = (low + high) / 2
		while row > low and lexicon[row - 1] != 10:
			row -= 1
		var separator: int = lexicon.find(9, row)
		var end: int = lexicon.find(10, separator)
		var key: String = lexicon.slice(row, separator).get_string_from_utf8()
		if key == word:
			return lexicon.slice(separator + 1, end).get_string_from_ascii().split(",")
		if key < word:
			low = end + 1
		else:
			high = row
	return []

var typeface: Font
var pixels: int
var width: float

func _init(label: Label, available_width: float) -> void:
	typeface = label.get_theme_font("font")
	pixels = label.get_theme_font_size("font_size")
	width = available_width - label.get_theme_stylebox("normal").get_minimum_size().x

func _fits(value: String) -> bool:
	return UiText.width(typeface, value, pixels) <= width

func _ellipsis(value: String) -> String:
	if not _fits(ELLIPSIS):
		return ""
	var text_server: TextServer = TextServerManager.get_primary_interface()
	var breaks: PackedInt32Array = text_server.string_get_character_breaks(value, "")
	var retained := ""
	for index: int in breaks:
		var prefix: String = value.left(index).strip_edges(false, true)
		if not _fits(prefix + ELLIPSIS):
			break
		retained = prefix
	return retained + ELLIPSIS

func _split_word(words: PackedStringArray, final_pair: bool) -> int:
	var word: String = words[0]
	var later: String = " ".join(words.slice(1))
	for point: String in _points(word):
		var offset: int = point.to_int()
		if not _fits(word.left(offset) + "-"):
			continue
		var rest: String = word.substr(offset)
		if final_pair and not later.is_empty():
			rest += " " + later
		if _fits(rest):
			return offset
	return 0

func lines(original: String, limit: int = 0) -> PackedStringArray:
	var words: PackedStringArray = original.split(" ", false)
	var result: PackedStringArray = []
	while not words.is_empty():
		if limit > 0 and result.size() == limit - 1:
			var rest: String = " ".join(words)
			result.append(rest if _fits(rest) else _ellipsis(rest))
			break

		# Use a whole-word boundary whenever a complete word fits on this line.
		var line := ""
		var count := 0
		for word: String in words:
			var candidate: String = word if line.is_empty() else line + " " + word
			if not _fits(candidate):
				break
			line = candidate
			count += 1
		if count > 0:
			result.append(line)
			words = words.slice(count)
			continue

		var word: String = words[0]
		var offset: int = _split_word(words, limit > 0 and result.size() == limit - 2)
		if offset > 0:
			result.append(word.left(offset) + "-")
			words[0] = word.substr(offset)
		elif limit > 0:
			result.append(_ellipsis(" ".join(words)))
			break
		else:
			# Recovery has no ellipsis. Keep a whole unknown word if measured
			# before the container has its usable width.
			result.append(word)
			words = words.slice(1)
	return result
