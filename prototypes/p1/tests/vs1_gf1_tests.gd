extends SceneTree
const Session = preload("res://model/session.gd")
const Cases = preload("res://tests/vs1_e1_cases.gd")
var checks: int = 0
var failures: int = 0
var board: Control

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		if failures < 25: printerr("VS1 GF1 FAIL: ", message)

func probe_row(index: int, all_states: bool = false) -> void:
	if all_states:
		var cells: Array[int] = board.session.player.cells.duplicate()
		var read: Dictionary = board.row_clue_reads[index].duplicate(true)
		var geometry: Rect2 = board.view.bounds()
		for status: int in range(3):
			for x: int in range(board.session.player.width):
				var value: int = board.session.definition.solution[index][x]
				board.session.player.cells[index*board.session.player.width+x] = -1 if status==0 or (status==1 and value==0) else value
			board.sync_clue_completion(board.session.visible_cells())
			check(board.completion_states("row",index).has(status),"each added capacity exercises all three actual clue states")
			board._layout()
			check(board.view.bounds()==geometry,"each status leaves capacity/grid unchanged")
			var maximum: int = board.clue_layout("row",index).max_offset
			for offset: int in [0,maximum/2,maximum]:
				board.set_clue_step("row",index,offset)
				var tokens: Array = board.visual_hint_units("row",index).units.filter(func(u: Dictionary)->bool:return u.kind=="token")
				check(tokens.size()>=mini(5,board.session.definition.rows[index].size()),"all statuses show complete numbers at start middle and outer stop")
			board.set_clue_step("row",index,0)
			probe_row(index)
		board.session.player.cells.assign(cells)
		board.row_clue_reads[index]=read
		board.normalize_clue_steps()
		board.sync_clue_completion(board.session.visible_cells())
		return
	var layout: Dictionary = board.clue_layout("row", index)
	var entries: Array = layout.entries
	var capacity: int = layout.slot_count
	board.pan_target = "row"
	board.pan_line_index = index
	board.pan_button = MOUSE_BUTTON_MIDDLE
	for shift: float in board.sequence_transitions(entries, capacity, "row", board.clue_font_size()) if entries.size() > capacity else [0.0]:
		board.pan_drag_distance = shift
		var visual: Dictionary = board.visual_hint_units("row", index)
		var tokens: Array = visual.units.filter(func(u: Dictionary) -> bool: return u.kind == "token")
		check(tokens.size() >= mini(5, entries.size()), "new capacity retains five whole actual numbers throughout drag")
		check(visual.prefix_hidden == (int(tokens[0].index) > 0) and visual.suffix_hidden == (int(tokens[-1].index) < entries.size()-1), "markers describe hidden indices")
		for i: int in range(tokens.size()):
			var token: Dictionary = tokens[i]
			var original: Dictionary = board.session.definition.rows[index][int(token.index)]
			check(str(entries[int(token.index)].text) == board.clue_token(original) and Color(entries[int(token.index)].color) == board.clue_color(original), "original indices numbers and colors unchanged")
			if i > 0: check(int(token.index) == int(tokens[i-1].index)+1, "complete contiguous numbers")
			var ink: Vector2 = board.token_ink(str(entries[int(token.index)].text), "row", board.clue_font_size())
			check(token.center-ink.x >= 0 and token.center+ink.y <= board.row_clue_area().end.x, "whole ink C1 and strike fit")
			for marker: Dictionary in visual.units:
				if marker.kind == "token": continue
				var mark: Vector2 = board.token_ink("…", "row", board.clue_font_size())
				check(token.center-ink.x >= marker.center+mark.y or token.center+ink.y <= marker.center-mark.x, "marker never consumes counted number")
	board.cancel_gesture()

func run() -> void:
	var definitions: Array = load("res://full_view_study/catalog.gd").definitions()
	board = load("res://full_view_study/board.gd").new()
	board.session = Session.new(definitions[7])
	board.book_layout = true
	board.size = Vector2(1800,900)
	root.add_child(board)
	await process_frame
	# Every width threshold including no spare slot, partial budgets and demand cap.
	for ui: float in [1.0,1.25]:
		board.ui_scale = ui
		for data: Dictionary in [definitions[3],definitions[7],definitions[8],definitions[9], Cases.fixture(definitions[0],25,true)]:
			board.session = Session.new(data)
			board.mode = "G"
			board.requested_cell = 12.0
			board.size = Vector2(1800,900)
			board._layout()
			var minimum: Vector2i = board.minimum_slots
			var index: int = 0
			for i: int in range(data.rows.size()):
				if data.rows[i].size() > data.rows[index].size(): index = i
			for added: int in range(0,board.max_hints.x-minimum.x+2):
				for delta: float in [-0.01,0.0,0.01]:
					board.size.x = minimum.x*26*ui+14+data.width*12+added*26*ui+delta
					board._layout()
					var expected: int = mini(board.max_hints.x,minimum.x+maxi(0,added-(1 if delta < 0 else 0)))
					check(board.reserve_slots.x == expected, "only whole fitting slots; no demand padding")
					check(board.minimum_slots == minimum and board.reserve_slots.y == minimum.y, "minimum and independent upper reserve stable")
					check(board.view.cell_size <= 12 and board.view.cell_size >= 11.99, "new capacity never feeds back into zoom")
					check(board.measurements().grid_fit and board.horizontal_used <= board.horizontal_budget+0.00001, "frame and added budget fit")
					if delta == 0 and expected > minimum.x:
						probe_row(index,true)
				board.fit_all()
				var fit: float = board.fit_ceiling
				var position: Vector2 = board.view.origin
				board._layout()
				check(board.fit_ceiling == fit and board.view.origin == position, "repeated layout never oscillates")
				board.requested_cell = 12.0
	# Preserve all semantic anchors through temporarily complete visibility.
	board.session = Session.new(Cases.fixture(definitions[0],25,true))
	board.ui_scale = 1.0
	board.requested_cell = 12.0
	board.size = Vector2(820,900)
	board._layout()
	for index: int in range(3):
		var max_offset: int = board.clue_layout("row", index).max_offset
		board.set_clue_step("row", index, [0,max_offset/2,max_offset][index])
	var reads: Array = board.row_clue_reads.duplicate(true)
	var steps: Array = board.row_clue_steps.duplicate()
	for mode: String in ["G","V","G"]:
		board.mode = mode
		board.size.x = 2000
		board._layout()
		check(board.reserve_slots.x == 25 and board.row_clue_reads == reads, "full visibility does not erase grid_end middle outer_start")
		check(board.navigation_target(Vector2(board.row_clue_area().get_center().x,board.view.origin.y+0.5*board.view.cell_size)).is_empty(), "complete row offers no useless movement")
	board.size.x = 820
	board._layout()
	check(board.row_clue_reads == reads and board.row_clue_steps == steps, "narrow reconstructs same semantic reads")
	var geometry: Rect2 = board.view.bounds()
	for status: int in range(3):
		for i: int in range(board.session.player.cells.size()):
			var value: int = board.session.definition.solution[i/board.session.player.width][i%board.session.player.width]
			board.session.player.cells[i] = -1 if status == 0 or (status == 1 and value == 0) else value
		board.sync_clue_completion(board.session.visible_cells())
		check(board.clue_status("row",0,0) == status, "three actual statuses")
		board._layout()
		check(board.view.bounds() == geometry, "progress and status never move grid")
		probe_row(0)
	print("VS1_GF1_TESTS_", "OK" if failures == 0 else "FAILED", " checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
