extends RefCounted
## Measurement oracle uses the native font RID, independently of board envelopes.
static func measure(board: Control, text: String, fs: int) -> Dictionary:
	var font: Font = board.clue_text_font(board.clue_font(), text)
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var bounds: Rect2
	var advance: float = 0
	var glyphs: Array = []
	for i: int in range(text.length()):
		var glyph: int = ts.font_get_glyph_index(rid, fs, text.unicode_at(i), 0)
		var offset: Vector2 = ts.font_get_glyph_offset(rid, Vector2i(fs,0), glyph)
		var extent: Vector2 = ts.font_get_glyph_size(rid, Vector2i(fs,0), glyph)
		var part: Rect2 = Rect2(offset+Vector2(advance,0),extent)
		bounds = part if i == 0 else bounds.merge(part)
		glyphs.append({"codepoint":text.unicode_at(i),"index":glyph,"offset":[offset.x,offset.y],"size":[extent.x,extent.y]})
		advance += font.get_string_size(text[i],HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x
	return {"text":text,"font":font.get_font_name(),"advance":font.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x,
		"ink":[bounds.position.x,bounds.position.y,bounds.size.x,bounds.size.y],"glyphs":glyphs}

static func at_size(board: Control, fs: int) -> Dictionary:
	var top: float = INF
	var bottom: float = -INF
	var reference: Array = []
	for symbol: String in "0123456789…–":
		var data: Dictionary = measure(board,symbol,fs)
		reference.append(data)
		top = minf(top,data.ink[1])
		bottom = maxf(bottom,data.ink[1]+data.ink[3])
	var result: Dictionary = {"fs":fs,"baseline":-(top+bottom)/2,"reference":reference,"row":[],"column":[]}
	for axis: String in ["row","column"]:
		for text: String in board.type_tokens[axis]:
			result[axis].append(measure(board,text,fs))
	return result

static func capture(board: Control) -> Dictionary:
	var digest: HashingContext = HashingContext.new()
	digest.start(HashingContext.HASH_SHA256)
	digest.update(board.clue_font().data)
	return {"sha256":digest.finish().hex_encode(),"selected":at_size(board,board.clue_font_size()),
		"next":at_size(board,board.clue_font_size()+1)}
