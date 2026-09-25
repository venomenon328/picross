extends RefCounted
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")

static func run(t: SceneTree) -> void:
	var board: Board = Board.new()
	board.size = Vector2(1100, 800)
	board.session = Session.new(Definition.load_fixture("f03"))
	t.root.add_child(board)
	await t.process_frame
	var first: float = board.shared_clue_slot_extent("row", ThemeDB.fallback_font, board.clue_font_size())
	for i: int in range(40):
		board.clue_layout("row", i)
	t.check(board.row_slot_extent_cache.size() == 1 and first == board.shared_clue_slot_extent("row", ThemeDB.fallback_font, board.clue_font_size()), "P1.4 F-03 row slot measurement shared across lines")
	board.ui_scale = 1.25
	board._layout()
	var scaled: float = board.shared_clue_slot_extent("row", ThemeDB.fallback_font, board.clue_font_size())
	t.check(board.row_slot_extent_cache.size() == 2 and scaled > first, "P1.4 UI scale recalculates shared row slots")
	board.session = Session.new(Definition.load_fixture("f02"))
	board._layout()
	var switched: float = board.shared_clue_slot_extent("row", ThemeDB.fallback_font, board.clue_font_size())
	var widest: float = 0.0
	for line: Array in board.session.definition.rows:
		for clue: Dictionary in line:
			widest = maxf(widest, ThemeDB.fallback_font.get_string_size(str(int(clue.length)), HORIZONTAL_ALIGNMENT_LEFT, -1, board.clue_font_size()).x)
	t.check(board.row_slot_extent_cache.size() == 3 and switched >= widest + 8.0 * board.ui_scale, "P1.4 fixture switch cannot reuse narrower F-03 slot")
	board.queue_free()
