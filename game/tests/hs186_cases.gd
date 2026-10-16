extends RefCounted
const Typography = preload("res://ui/clue_typography.gd")
const Board = preload("res://ui/full_view_board.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
const Overlay = preload("res://ui/clue_overlay.gd")

static func run(t: SceneTree) -> void:
	var b: Board = Board.new()
	b.session = Session.new(Definition.load_fixture("t08"))
	b.size = Vector2(1100, 700)
	t.root.add_child(b)
	await t.process_frame
	for ui: float in [1, 1.25]:
		b.ui_scale = ui
		b.type_tokens = {"row":{}, "column":{}}
		for text: String in ["1", "11", "17", "23", "40", "50", "…", "–"]:
			b.type_tokens.row[text] = true
			b.type_tokens.column[text] = true
			for fs: int in [8, 16, 22, 40]:
				var ink: Rect2 = Typography.ink(text, fs)
				var envelope: Rect2 = Typography.number_envelope(text, fs, ui)
				for line: int in range(16):
					var identity: String = b.clue_identity("column", line, 2)
					var strokes: Array[PackedVector2Array] = Typography.cross_strokes(text, fs, identity, null, ui)
					t.check(strokes.size() == (2 if text.is_valid_int() else 0), "HS two whole-token diagonals; markers unmarked")
					for i: int in range(strokes.size()):
						var path: PackedVector2Array = strokes[i]
						var diameter: float = 2 * Typography.cross_inset(ink, fs, ui)
						t.check(path.size() == 4 and absf(path[-1].x - path[0].x) + diameter >= ink.size.x * 0.9 and absf(path[-1].y - path[0].y) + diameter >= ink.size.y * 0.9, "HS each stroke crosses the whole number")
						for p: Vector2 in path:
							var radius: float = Typography.cross_width(fs, i) / 2 + ui / 4 + 1.0
							t.check(envelope.grow(0.0001).encloses(Rect2(p - Vector2.ONE * radius, Vector2.ONE * 2 * radius)), "HS all variants include stroke/C1/AA")
		# Positive and negative candidates on both native/web's shared exhaustive
		# search. The next grade must fail; no advance/old strike approximation.
		for cell: float in [12, 16, 23.37, 24, 40, 72]:
			b.configure_typography(cell)
			var fs: int = b.clue_font_size()
			t.check(fits(b, fs, cell), "HS selected grade fits actual glyph/X")
			t.check(not fits(b, fs + 1, cell), "HS next grade is actually too large")
			var form: Array[PackedVector2Array] = Typography.cross_strokes("23", fs, b.clue_identity("row", 3, 4))
			b.configure_typography(20)
			b.configure_typography(cell)
			t.check(form == Typography.cross_strokes("23", b.clue_font_size(), b.clue_identity("row", 3, 4)), "HS zoom roundtrip preserves original identity/form")
		var entries: Array = []
		for text: String in ["1", "11", "17", "23", "40", "50", "…", "–"]:
			entries.append({"text":text, "color":Color.WHITE})
		var geometry: Dictionary = Overlay.measure(b, entries)
		for status: int in range(3):
			for entry: Dictionary in entries: entry.status = status
			t.check(Overlay.measure(b, entries) == geometry, "HS status cannot alter tooltip wrap/baselines/insets")
		b.type_cache.clear()
		var restored: Board = Board.new()
		restored.session = Session.new(b.session.definition)
		t.check(Typography.cross_strokes("50", 22, b.clue_identity("column", 7, 1)) == Typography.cross_strokes("50", 22, restored.clue_identity("column", 7, 1)), "HS fresh session restores same original hint form")
		restored.free()
	b.queue_free()
	await t.process_frame

static func fits(board: Board, fs: int, cell: float) -> bool:
	var limit: float = maxf(1, cell - 2 * board.ui_scale)
	for axis: String in ["row", "column"]:
		for text: String in board.type_tokens[axis]:
			var box: Rect2 = Typography.envelope(text, fs, board.ui_scale)
			if 2 * maxf(-box.position.y, box.end.y) > limit: return false
			if axis == "column" and 2 * maxf(-box.position.x, box.end.x) > limit: return false
	return true
