extends RefCounted
const Definition = preload("res://model/definition.gd")
const Player = preload("res://model/player.gd")
const Gesture = preload("res://model/gesture.gd")
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
const Main = preload("res://ui/main.gd")
const Board = preload("res://ui/board.gd")
const ClueLayout = preload("res://ui/clue_layout.gd")

static func run(t: SceneTree) -> void:
	for id: String in ["f01", "f02", "f03"]:
		var data: Dictionary = Definition.load_fixture(id)
		t.check(Definition.validate(data).is_empty(), id + " valid independent artwork")
		for key: String in ["version", "definition_id", "image"]:
			var bad: Dictionary = data.duplicate(true)
			bad.reveal.erase(key)
			t.check(not Definition.validate(bad).is_empty(), id + " missing reveal " + key)
		for path: String in ["res://art/../data/f01.json", "res://art/missing.svg", "user://private.svg"]:
			var bad: Dictionary = data.duplicate(true)
			bad.reveal.image = path
			t.check(not Definition.validate(bad).is_empty(), "invalid resource path")
		var s: Session = Session.new(data)
		if id == "f02":
			var artwork: Texture2D = load(data.reveal.image) as Texture2D
			t.check(data.revision == 2 and artwork != null and artwork.get_width() == 800 and artwork.get_height() == 800, "J-05 F-02 revision binds independent 800px lighthouse artwork")
		for y: int in range(s.player.height):
			for x: int in range(s.player.width):
				if data.solution[y][x] > 0:
					s.player.cells[y * s.player.width + x] = int(data.solution[y][x])
		t.check(s.is_solution() and s.reveal().is_empty(), "no preview reveal; unknown background accepted " + id)
		var index: int = s.player.width + (10 if id == "f01" else 1)
		var actual: int = s.player.cells[index]
		for wrong: int in [-1, 0, (actual % 4) + 1]:
			s.player.cells[index] = wrong
			t.check(not s.is_solution(), "missing/empty/wrong color rejects " + id)
			t.check(s.visible_cells()[index] == wrong, "miniature preserves wrong values " + id)
		s.player.cells[index] = -1
		s.gesture.begin(s.player, Vector2i(index % s.player.width, index / s.player.width), actual)
		t.check(not s.completed and s.reveal().is_empty(), "last-cell preview hidden " + id)
		s.finish()
		t.check(s.completed and not s.reveal().is_empty(), "actual committed completion " + id)
		s.player.cells[0] = 1
		t.check(not s.is_solution(), "extra fill rejects " + id)
	# D-15 full table, including mixed colors, direct conversion and typed removal.
	for start_value: int in [-1, 0, 1, 2, 3, 4]:
		for target: int in [-1, 0, 1, 2, 3, 4]:
			var p: Player = Player.new(8, 1)
			p.cells = [start_value, -1, 0, 1, 2, 3, 4, -1]
			var before: Array[int] = p.cells.duplicate()
			var g: Gesture = Gesture.new()
			g.begin(p, Vector2i.ZERO, target)
			g.move(Vector2i(7, 0))
			g.move(Vector2i(5, 0))
			g.move(Vector2i(7, 0))
			var expected: Array[int] = before.duplicate()
			for i: int in range(8):
				if target == -1 or (target > 0 and start_value > 0 and before[i] > 0) or (target == 0 and start_value == 0 and before[i] == 0):
					expected[i] = -1
				elif target > 0 and start_value <= 0 and before[i] in [-1, 0]:
					expected[i] = target
				elif target == 0 and start_value != 0 and (before[i] == -1 or before[i] > 0):
					expected[i] = target
			t.check(p.cells == before, "preview does not mutate source")
			var changed: bool = g.finish(p)
			t.check(p.cells == expected, "frozen gesture table %d/%d" % [start_value, target])
			if changed:
				t.check(p.cursor == 1 and not p.undo_used, "neutralize is normal atomic action")
				p.undo()
				t.check(p.cells == before and p.undo_used, "exact mixed undo")
				p.redo()
				t.check(p.cells == expected and p.undo_used, "exact mixed redo")
	# All transforms share coordinates; resizing does not change work pitch.
	for n: int in [20, 40, 100]:
		for step: float in [18.0, 24.0, 36.0, 48.0]:
			var v: GridView = GridView.new()
			v.cell_size = step
			v.center = Vector2(n, n) / 2
			v.configure(Rect2(180, 150, 700, 400), Vector2i(n, n))
			var center: Vector2 = v.center
			for point: Vector2 in [Vector2.ZERO, Vector2.ONE, Vector2(0.35, 0.67)]:
				v.center = point * n
				v.reframe()
				var visible: Rect2 = v.visible_bounds()
				var hit: Vector2i = v.hit(visible.get_center())
				t.check(hit.x >= 0 and hit.y >= 0 and v.hit(v.cell_rect(hit).get_center()) == hit, "transformed hit round trip")
				t.check(Rect2(0, 0, 1, 1).encloses(v.normalized_view()), "mini frame bounded")
				t.check(v.hit(v.viewport.position - Vector2.ONE).x == -1, "no hit below gutters")
			v.center = center
			v.configure(Rect2(180, 150, 800, 450), Vector2i(n, n))
			t.check(v.cell_size == step and v.center.is_equal_approx(center), "resize stable cells and focus")
	var v: GridView = GridView.new()
	v.center = Vector2(50, 50)
	v.configure(Rect2(100, 100, 600, 400), Vector2i(100, 100))
	var anchor: Vector2 = Vector2(310, 270)
	var coordinate: Vector2 = (anchor - v.origin) / v.cell_size
	v.zoom_to(48, anchor)
	t.check(((anchor - v.origin) / v.cell_size).is_equal_approx(coordinate), "pointer anchored zoom")
	t.check(Board.WORK_STEPS.size() >= 16, "D-13 offers substantially finer work zoom steps")
	for i: int in range(1, Board.WORK_STEPS.size()):
		t.check(Board.WORK_STEPS[i] > Board.WORK_STEPS[i - 1], "work zoom steps strictly increase")
	t.check(Board.next_zoom_step(5.0, -1) == 5.0 and Board.next_zoom_step(5.0, 1) == Board.WORK_STEPS[0], "overview below work range keeps zoom direction")
	t.check(Board.next_zoom_step(96.0, 1) == 96.0 and Board.next_zoom_step(96.0, -1) == Board.WORK_STEPS[-1], "overview above work range keeps zoom direction")
	for current: float in [5.0, 12.0, 23.0, 24.0, 73.0, 96.0]:
		t.check(Board.next_zoom_step(current, -1) <= current and Board.next_zoom_step(current, 1) >= current, "zoom direction monotone at " + str(current))
	t.check(Main.bounded_start(Rect2i(0, 0, 1366, 768), Vector2i(16, 48)) == Vector2i(1350, 720), "small work area bounded")
	t.check(Main.bounded_start(Rect2i(0, 0, 2560, 1400), Vector2i(16, 48)) == Vector2i(1920, 1080), "large work area reaches 1080p client target")
	t.check(Main.bounded_start(Rect2i(0, 0, 1920, 1040), Vector2i(16, 48)) == Vector2i(1904, 992), "1080p work area bounds complete decorated window")
	for usable: Rect2i in [Rect2i(0, 0, 1366, 768), Rect2i(-1920, 32, 1920, 1000), Rect2i(0, 0, 1100, 680)]:
		var decoration: Vector2i = Vector2i(16, 48)
		var offset: Vector2i = Vector2i(8, 40)
		var client: Vector2i = Main.bounded_start(usable, decoration)
		var position: Vector2i = Main.bounded_position(usable, client, decoration, offset)
		t.check(usable.encloses(Rect2i(position - offset, client + decoration)), "whole decorated window fits asymmetric frame")
	test_atomic_clue_windows(t)
	await ui_cases(t)

static func test_atomic_clue_windows(t: SceneTree) -> void:
	var full: Dictionary = ClueLayout.select_window(3, 5, 0)
	t.check(full.start == 0 and full.end == 3 and full.token_slot == 2 and not full.prefix_hidden and not full.suffix_hidden, "J-02 fitting clue sequence snaps to grid-near slots")
	var just_overflowing: Dictionary = ClueLayout.select_window(6, 5, 0)
	t.check(just_overflowing.start == 2 and just_overflowing.end == 6 and just_overflowing.prefix_hidden and not just_overflowing.suffix_hidden, "J-02 overflow keeps maximum grid-near complete tokens")
	var middle: Dictionary = ClueLayout.select_window(8, 5, 2)
	t.check(middle.start < middle.end and middle.prefix_hidden and middle.suffix_hidden and middle.units[0].slot == 0 and middle.units[-1].slot == 4, "J-02 middle clue window reserves fixed marker slots")
	var outer: Dictionary = ClueLayout.select_window(8, 5, 5)
	t.check(outer.start == 0 and outer.end == 4 and not outer.prefix_hidden and outer.suffix_hidden, "J-02 outer beginning and suffix marker are reachable")
	var outer_read: Dictionary = ClueLayout.read_position(90, 7, 85)
	var outer_reflow: Dictionary = ClueLayout.select_window(90, 5, ClueLayout.offset_for_read_position(90, 5, outer_read))
	t.check(outer_read.anchor == ClueLayout.OUTER_START and outer_reflow.start == 0 and not outer_reflow.prefix_hidden and outer_reflow.suffix_hidden, "B-03 outer-start anchor survives reduced slot capacity")
	var grid_read: Dictionary = ClueLayout.read_position(90, 5, 0)
	var grid_reflow: Dictionary = ClueLayout.select_window(90, 7, ClueLayout.offset_for_read_position(90, 7, grid_read))
	t.check(grid_read.anchor == ClueLayout.GRID_END and grid_reflow.end == 90 and grid_reflow.prefix_hidden and not grid_reflow.suffix_hidden, "B-03 grid-end anchor survives increased slot capacity")
	var middle_before: Dictionary = ClueLayout.select_window(90, 7, 42)
	var middle_read: Dictionary = ClueLayout.read_position(90, 7, 42)
	var middle_after: Dictionary = ClueLayout.select_window(90, 5, ClueLayout.offset_for_read_position(90, 5, middle_read))
	var middle_overlap: int = mini(int(middle_before.end), int(middle_after.end)) - maxi(int(middle_before.start), int(middle_after.start))
	t.check(middle_read.anchor == ClueLayout.MIDDLE and middle_overlap == mini(int(middle_before.end) - int(middle_before.start), int(middle_after.end) - int(middle_after.start)), "B-03 middle reflow retains the maximum readable token interval")
	var empty: Dictionary = ClueLayout.select_window(0, 5, 0)
	t.check(empty.start == 0 and empty.end == 0 and not empty.prefix_hidden and not empty.suffix_hidden, "J-02 empty layout is stable")
	var reached: Dictionary = {}
	var maximum: int = int(ClueLayout.select_window(24, 6, 0).max_offset)
	for sample: int in range(maximum + 1):
		var window: Dictionary = ClueLayout.select_window(24, 6, sample)
		t.check(window.start < window.end and window.offset == sample, "J-02 very long sequence uses exact snapped offset")
		var occupied: Dictionary = {}
		for unit: Dictionary in window.units:
			t.check(int(unit.slot) >= 0 and int(unit.slot) < 6 and not occupied.has(unit.slot), "J-02 each visible unit owns one regular slot")
			occupied[unit.slot] = true
		for index: int in range(int(window.start), int(window.end)):
			reached[index] = true
	t.check(reached.size() == 24, "J-02 panning reaches every token in a very long sequence")

static func ui_cases(t: SceneTree) -> void:
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	app.select_puzzle(1)
	await t.process_frame
	await t.process_frame
	var b: Control = app.board
	var sample_clue: Dictionary = app.session.definition.rows[10][0]
	t.check(b.clue_token(sample_clue) == str(int(sample_clue.length)), "J-01 colored clue is the complete number without suffix")
	t.check(b.clue_color(sample_clue).is_equal_approx(Color(app.session.definition.palette[int(sample_clue.color) - 1].color)), "clue number uses puzzle color")
	t.check(not has_button_text(app, "Farbkennungen in Hinweisen: aus") and not has_button_text(app, "Farbkennungen in Hinweisen: an"), "J-01 obsolete clue-label option removed")
	var empty_row: int = first_empty_line(app.session.definition.rows)
	var empty_layout: Dictionary = b.clue_layout("row", empty_row)
	t.check(empty_layout.entries.size() == 1 and empty_layout.entries[0].text == "–" and empty_layout.units[-1].slot == empty_layout.slot_count - 1, "J-01/J-02 empty line remains a grid-near dash")
	t.check(b.clue_token({"length": 12, "color": 1}) == "12", "J-01 multi-digit clue remains one horizontal token")
	# J-02: actual F-02 geometry uses common slots and exposes start/middle/end.
	var column_22: Array = app.session.definition.columns[21]
	t.check(column_22.size() == 12 and int(column_22[0].length) == 6 and int(column_22[0].color) == 4 and int(column_22[1].length) == 3 and int(column_22[1].color) == 3 and int(column_22[2].length) == 3 and int(column_22[2].color) == 2, "J-02 F-02 column 22 starts blue 6, red 3, yellow 3")
	for step: float in [22.0, 24.0]:
		b.view.zoom_to(step, b.view.viewport.get_center())
		var base_layout: Dictionary = b.clue_layout("column", 21)
		var neighbor_layout: Dictionary = b.clue_layout("column", 22)
		t.check(base_layout.slot_count == neighbor_layout.slot_count and is_equal_approx(base_layout.slot_extent, neighbor_layout.slot_extent), "J-02 adjacent columns share slot rows at pitch " + str(step))
		var reached: Dictionary = {}
		for offset: int in range(int(base_layout.max_offset) + 1):
			b.set_clue_step("column", 21, offset)
			var window: Dictionary = b.clue_layout("column", 21)
			t.check(window.offset == offset and window.start < window.end, "J-02 column 22 snaps at offset %d / pitch %s" % [offset, step])
			for index: int in range(int(window.start), int(window.end)):
				reached[index] = true
		t.check(reached.size() == column_22.size(), "J-02 column 22 exposes every token at pitch " + str(step))
		b.set_clue_step("column", 21, 0)
		var grid_end: Dictionary = b.clue_layout("column", 21)
		b.set_clue_step("column", 21, maxi(1, int(float(grid_end.max_offset) / 2.0)))
		var middle: Dictionary = b.clue_layout("column", 21)
		b.set_clue_step("column", 21, int(grid_end.max_offset))
		var outer: Dictionary = b.clue_layout("column", 21)
		t.check(grid_end.end == column_22.size() and grid_end.prefix_hidden and not grid_end.suffix_hidden, "J-02 grid-near F-02 suffix retained at pitch " + str(step))
		t.check(middle.prefix_hidden and middle.suffix_hidden and outer.start == 0 and outer.suffix_hidden, "J-02 F-02 middle and outer marker states at pitch " + str(step))
	b.view.zoom_to(24.0, b.view.viewport.get_center())
	var short_row_layout: Dictionary = b.clue_layout("row", 34)
	var long_row_layout: Dictionary = b.clue_layout("row", 35)
	var row_area: Rect2 = b.row_clue_area()
	t.check(short_row_layout.max_offset == 0 and long_row_layout.max_offset > 0 and short_row_layout.slot_count == long_row_layout.slot_count, "J-02 adjacent short and overflowing rows share one slot grid")
	t.check(is_equal_approx(b.clue_slot_center("row", row_area, short_row_layout, short_row_layout.slot_count - 1), b.clue_slot_center("row", row_area, long_row_layout, long_row_layout.slot_count - 1)), "J-02 adjacent row slots have identical coordinates")
	t.check(is_equal_approx(b.clue_slot_center("row", row_area, long_row_layout, 1) - b.clue_slot_center("row", row_area, long_row_layout, 0), long_row_layout.slot_extent), "J-02 row slot spacing is regular")
	for position: int in [0, 1, 2]:
		var column_base: Dictionary = b.clue_layout("column", 21)
		var row_base: Dictionary = b.clue_layout("row", 35)
		b.set_clue_step("column", 21, [0, int(float(column_base.max_offset) / 2.0), int(column_base.max_offset)][position])
		var column_window: Dictionary = b.clue_layout("column", 21)
		b.set_clue_step("row", 35, [0, int(float(row_base.max_offset) / 2.0), int(row_base.max_offset)][position])
		var row_window: Dictionary = b.clue_layout("row", 35)
		t.check(column_window.start < column_window.end and row_window.start < row_window.end, "J-02 both axes keep real clues at snapped state " + str(position))
		if position == 0:
			t.check(column_window.end == column_22.size() and row_window.end == app.session.definition.rows[35].size(), "J-02 default windows retain grid-near ends")
		elif position == 2:
			t.check(column_window.start == 0 and row_window.start == 0, "J-02 outer beginnings reachable on both axes")
	b.reset_clue_pan()
	b.navigate_to(Vector2(0.5, 0.5))
	var start: Vector2i = b.view.hit(b.view.viewport.get_center())
	var point: Vector2 = b.get_global_transform() * b.view.cell_rect(start).get_center()
	# Real palette and viewport dispatch, all four colors.
	for i: int in range(4):
		var palette_point: Vector2 = app.palette_row.get_child(i).get_global_rect().get_center()
		t.mouse_motion(palette_point, false)
		t.mouse_button(palette_point, true)
		t.mouse_button(palette_point, false)
		t.mouse_motion(point, false)
		t.mouse_button(point, true)
		t.mouse_button(point, false)
		t.check(app.session.player.cells[start.y * 40 + start.x] == i + 1, "palette/viewport fill color " + str(i))
		t.mouse_button(point, true)
		var prior: Vector2 = b.view.center
		b.zoom(1, b.view.viewport.get_center())
		b.navigate_to(Vector2.ONE)
		t.check(b.view.center == prior and b.view.cell_size == 24, "cell gesture blocks zoom and miniature")
		t.mouse_button(point, false)
		t.check(app.session.player.cells[start.y * 40 + start.x] == -1, "viewport left neutralizes color " + str(i))
		t.mouse_button(point, true, MOUSE_BUTTON_RIGHT)
		t.mouse_button(point, false, MOUSE_BUTTON_RIGHT)
		t.check(app.session.player.cells[start.y * 40 + start.x] == 0, "viewport right marks empty")
		t.mouse_button(point, true)
		t.mouse_button(point, false)
		t.check(app.session.player.cells[start.y * 40 + start.x] == i + 1, "viewport left converts X directly to active color")
		t.mouse_button(point, true, MOUSE_BUTTON_RIGHT)
		t.mouse_button(point, false, MOUSE_BUTTON_RIGHT)
		t.check(app.session.player.cells[start.y * 40 + start.x] == 0, "viewport right converts fill directly to X")
		t.mouse_button(point, true, MOUSE_BUTTON_RIGHT)
		t.mouse_button(point, false, MOUSE_BUTTON_RIGHT)
		t.check(app.session.player.cells[start.y * 40 + start.x] == -1, "viewport right removes empty")
	var history: Array = app.session.player.history.duplicate(true)
	var cells: Array[int] = app.session.player.cells.duplicate()
	var mini_point: Vector2 = app.mini.get_global_position() + app.mini.image_rect().size * 0.85
	t.mouse_motion(mini_point, false)
	t.mouse_button(mini_point, true)
	t.mouse_button(mini_point, false)
	t.check(b.view.center.x > 20 and b.view.center.y > 20, "real miniature click navigates")
	var before_center: Vector2 = b.view.center
	app.set_tool("hand")
	point = b.get_global_transform() * b.view.viewport.get_center()
	t.mouse_motion(point, false)
	t.mouse_button(point, true)
	t.mouse_motion(point + Vector2(80, 60), true)
	t.mouse_button(point + Vector2(80, 60), false)
	t.check(b.view.center != before_center and not app.session.gesture.active, "hand pans without gesture")
	t.check(app.session.player.history == history and app.session.player.cells == cells, "navigation history/matrix invariant")
	app.select_puzzle(0)
	app.select_puzzle(1)
	t.check(app.session.player.history == history, "per-fixture session history retained")
	app.select_puzzle(2)
	await t.process_frame
	await t.process_frame
	t.check(app.stress_label.visible, "F03 stress marking")
	var longest_row: int = longest_line(app.session.definition.rows)
	var longest_column: int = longest_line(app.session.definition.columns)
	b.navigate_to(Vector2(float(longest_column) / 100.0, float(longest_row) / 100.0))
	var clue_point: Vector2 = b.get_global_transform() * Vector2(b.row_clue_area().get_center().x, b.view.cell_rect(Vector2i(0, longest_row)).get_center().y)
	t.mouse_motion(clue_point, false)
	t.check(b.clue_hover_axis == "row" and b.clue_hover_index == longest_row, "H-03 real pointer route opens in-work clue tooltip")
	t.check(b.row_hint_overflows(longest_row), "long F03 row uses token-level overflow")
	var tooltip: Array = b.tooltip_entries("row", longest_row)
	var complete_tooltip: bool = tooltip.size() == app.session.definition.rows[longest_row].size()
	for i: int in range(tooltip.size()):
		var clue: Dictionary = app.session.definition.rows[longest_row][i]
		complete_tooltip = complete_tooltip and tooltip[i].text == b.clue_token(clue) and tooltip[i].color.is_equal_approx(b.clue_color(clue))
	t.check(complete_tooltip, "in-work hover tooltip contains every row clue and color")
	t.check(not has_button_text(app, "Ganze Zeile / Spalte ↗") and not has_button_text(app, "Hinweisansicht schließen"), "separate clue view removed")
	# H-03: real numeric sections remain in both gutters at small work zooms.
	for scale: float in [1.0, 1.25]:
		app.set_ui_scale(scale)
		for step: float in [12.0, 18.0, 22.0, 24.0]:
			b.view.zoom_to(step, b.view.viewport.get_center())
			for position: int in [0, 1, 2]:
				var row_base: Dictionary = b.clue_layout("row", longest_row)
				var column_base: Dictionary = b.clue_layout("column", longest_column)
				b.set_clue_step("row", longest_row, [0, int(float(row_base.max_offset) / 2.0), int(row_base.max_offset)][position])
				b.set_clue_step("column", longest_column, [0, int(float(column_base.max_offset) / 2.0), int(column_base.max_offset)][position])
				var row_window: Dictionary = b.clue_layout("row", longest_row)
				var column_window: Dictionary = b.clue_layout("column", longest_column)
				t.check(row_window.end > row_window.start and column_window.end > column_window.start, "J-02 real F-03 clues at UI/pitch/slot %s/%s/%s" % [scale, step, position])
				t.check(row_window.prefix_hidden or row_window.suffix_hidden, "J-02 long row markers reflect hidden entries")
	app.set_ui_scale(1.0)
	b.working_size()
	b.reset_clue_pan()
	await semantic_clue_geometry_routes(t, app)
	await clue_navigation_routes(t, app, longest_row, longest_column)
	await followup_input_geometry(t, app)
	b.fit_all()
	var below_work_range: float = b.view.cell_size
	t.check(below_work_range < Board.WORK_STEPS[0], "F03 overview is below minimum work zoom")
	b.zoom(-1, b.view.viewport.get_center())
	t.check(is_equal_approx(b.view.cell_size, below_work_range) and b.overview, "zoom out from small overview never zooms in")
	b.zoom(1, b.view.viewport.get_center())
	t.check(b.view.cell_size > below_work_range and not b.overview, "zoom in from small overview increases monotonically")
	b.view.zoom_to(96.0, b.view.viewport.get_center())
	b.overview = true
	b.zoom(1, b.view.viewport.get_center())
	t.check(b.view.cell_size == 96.0 and b.overview, "zoom in above maximum never shrinks")
	b.zoom(-1, b.view.viewport.get_center())
	t.check(b.view.cell_size == Board.WORK_STEPS[-1] and not b.overview, "zoom out above maximum decreases monotonically")
	b.working_size()
	for dims: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		t.root.size = dims
		for scale: float in [1.0, 1.25]:
			app.set_ui_scale(scale)
			await t.process_frame
			await t.process_frame
			t.check(app.work.get_global_rect().end.y < dims.y and app.mini.get_global_rect().end.x < dims.x, "logical layout bounds " + str(dims))
			t.check(b.view.cell_size == 24, "UI scale/resize independent from zoom")
			t.check(not app.minimum_message.visible and app.page.visible, "supported layout visible")
	t.root.size = Vector2i(1000, 650)
	await t.process_frame
	await t.process_frame
	t.check(app.minimum_message.visible and not app.page.visible, "undersize clear fallback")
	app.queue_free()
	await t.process_frame
	t.root.size = Vector2i(1280, 720)

static func followup_input_geometry(t: SceneTree, app: Main) -> void:
	var b: Board = app.board
	app.set_tool("fill")
	b.reset_clue_pan()
	var rows: Array[int] = visible_overflowing_lines(b, "row")
	if rows.is_empty():
		return
	var index: int = rows[0]
	var point: Vector2 = clue_point(b, "row", index)
	var pitch: float = float(b.clue_layout("row", index).slot_extent)
	var confirmed: Dictionary = b.capture_view()
	var neighbour: int = rows[1] if rows.size() > 1 else index
	var neighbour_layout: Array = window_signature(b.clue_layout("row", neighbour))
	b.hover = b.view.hit(b.view.viewport.get_center())
	t.mouse_button(point, true, MOUSE_BUTTON_MIDDLE)
	t.check(b.hover == Vector2i(-1, -1), "N-05 hint navigation clears stale grid focus without a cell gesture")
	t.mouse_motion(point + Vector2(pitch * 0.35, 2 * b.view.cell_size), true, MOUSE_BUTTON_MIDDLE)
	t.check(b.clue_step("row", index) == 0 and is_equal_approx(float(b.visible_clue_layout("row", index).visual_shift), pitch * 0.35) and b.capture_view() == confirmed, "N-03 subslot movement stays visual and unsaved")
	t.check(window_signature(b.clue_layout("row", neighbour)) == neighbour_layout, "N-03 adjacent clue remains fixed during drag")
	t.mouse_motion(point + Vector2(pitch * 1.6, 2 * b.view.cell_size), true, MOUSE_BUTTON_MIDDLE)
	t.check(b.clue_step("row", index) == 0 and b.visible_clue_layout("row", index).offset == 2, "N-03 dragged clue crosses slots without committing")
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	t.root.push_input(escape, true)
	t.check(b.capture_view() == confirmed and b.pan_drag_distance == 0.0, "N-03 Escape restores last snapped semantic read")
	t.mouse_button(point, true, MOUSE_BUTTON_MIDDLE)
	t.mouse_motion(point + Vector2(pitch * 1.6, 0), true, MOUSE_BUTTON_MIDDLE)
	t.mouse_button(point, false, MOUSE_BUTTON_MIDDLE)
	t.check(b.clue_step("row", index) == 2 and b.capture_view() != confirmed and b.pan_drag_distance == 0.0, "N-03 drop snaps and commits one semantic read")
	var cells: Array[int] = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	var start: Vector2i = b.view.hit(b.view.viewport.get_center())
	start.x = mini(start.x, app.session.player.width - 12)
	var endpoint: Vector2i = Vector2i(start.x + 7, start.y)
	app.session.gesture.begin(app.session.player, start, 1)
	t.check(b.gesture_length() == 1, "N-07 single cell counts one")
	app.session.gesture.move(endpoint)
	t.check(b.gesture_length() == 8, "N-07 jump counts entire geometric length")
	app.session.gesture.move(Vector2i(start.x + 4, start.y))
	t.check(b.gesture_length() == 5, "N-07 elastic retreat updates immediately")
	app.session.gesture.cancel()
	app.session.player.cells[start.y * app.session.player.width + start.x] = 1
	app.session.gesture.begin(app.session.player, start, 1)
	app.session.gesture.move(endpoint)
	t.check(b.gesture_length() == 8 and app.session.gesture.changes().size() < 8, "N-07 prefilled cells do not shorten counter")
	app.session.gesture.cancel()
	app.session.player.cells = cells
	t.check(app.session.player.history == history and b.gesture_length() == 0, "N-07 canceled count changes no history")
	var clipped: PackedVector2Array = Board.clipped_segment(Vector2.ZERO, Vector2(10, 10), Rect2(2, 2, 6, 6))
	t.check(clipped.size() == 2 and clipped[0].is_equal_approx(Vector2(2, 2)) and clipped[1].is_equal_approx(Vector2(8, 8)), "N-06 diagonal X segment clips at corner")
	for area: Rect2 in [Rect2(2, -1, 8, 12), Rect2(-1, -1, 8, 12), Rect2(-1, 2, 12, 8), Rect2(-1, -1, 12, 8)]:
		clipped = Board.clipped_segment(Vector2.ZERO, Vector2(10, 10), area)
		t.check(clipped.size() == 2 and area.has_point(clipped[0]) and clipped[0].distance_to(clipped[1]) > 0.0, "N-06 X intersection survives a viewport edge")
	t.check(Board.clipped_segment(Vector2.ZERO, Vector2(1, 1), Rect2(5, 5, 2, 2)).is_empty(), "N-06 no artificial X when geometry misses visible remainder")
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = b.view.viewport.get_center()
	b._gui_input(motion)
	t.check(b.hover.x >= 0 and b.hover.y >= 0, "N-05 grid cell activates row and column focus")
	motion.position = b.row_clue_area().get_center()
	b._gui_input(motion)
	t.check(b.hover == Vector2i(-1, -1) and app.session.player.history == history, "N-05 leaving grid clears focus without history")

static func semantic_clue_geometry_routes(t: SceneTree, app: Main) -> void:
	var b: Control = app.board
	var original_size: Vector2i = t.root.size
	var original_scale: float = app.ui_scale
	var original_zoom: float = b.view.cell_size
	var original_center: Vector2 = b.view.center
	t.root.size = Vector2i(1920, 1080)
	app.set_ui_scale(1.0)
	await t.process_frame
	await t.process_frame
	b.reset_clue_pan()
	set_work_zoom(b, 12.0)
	var rows: Array[int] = overflowing_lines(b, "row")
	var columns: Array[int] = overflowing_lines(b, "column")
	t.check(rows.size() >= 3 and columns.size() >= 3, "B-03 three long F-03 rows and columns available for semantic reflow")
	if rows.size() < 3 or columns.size() < 3:
		return
	var cases: Array[Dictionary] = [
		{"axis": "row", "index": rows[0], "anchor": ClueLayout.OUTER_START},
		{"axis": "row", "index": rows[1], "anchor": ClueLayout.GRID_END},
		{"axis": "row", "index": rows[2], "anchor": ClueLayout.MIDDLE},
		{"axis": "column", "index": columns[0], "anchor": ClueLayout.OUTER_START},
		{"axis": "column", "index": columns[1], "anchor": ClueLayout.GRID_END},
		{"axis": "column", "index": columns[2], "anchor": ClueLayout.MIDDLE},
	]
	for entry: Dictionary in cases:
		var layout: Dictionary = b.clue_layout(entry.axis, entry.index)
		var offset: int = 0
		if entry.anchor == ClueLayout.OUTER_START:
			offset = int(layout.max_offset)
		elif entry.anchor == ClueLayout.MIDDLE:
			offset = maxi(1, int(layout.max_offset) / 2)
		b.set_clue_step(entry.axis, entry.index, offset)
	var initial: Array[Dictionary] = semantic_windows(b, cases)
	set_work_zoom(b, 24.0)
	var current: Array[Dictionary] = check_semantic_transition(t, b, cases, initial, "50 to 100 percent")
	set_work_zoom(b, 12.0)
	current = check_semantic_transition(t, b, cases, current, "100 to 50 percent")
	check_restored_windows(t, current, initial, "50 to 100 to 50 percent")
	app.set_ui_scale(1.25)
	current = check_semantic_transition(t, b, cases, current, "UI 100 to 125 percent")
	app.set_ui_scale(1.0)
	current = check_semantic_transition(t, b, cases, current, "UI 125 to 100 percent")
	check_restored_windows(t, current, initial, "UI round trip")
	t.root.size = Vector2i(1280, 720)
	await t.process_frame
	await t.process_frame
	current = check_semantic_transition(t, b, cases, current, "resize smaller")
	t.root.size = Vector2i(1920, 1080)
	await t.process_frame
	await t.process_frame
	current = check_semantic_transition(t, b, cases, current, "resize larger")
	check_restored_windows(t, current, initial, "resize round trip")
	b.reset_clue_pan()
	app.set_ui_scale(original_scale)
	t.root.size = original_size
	await t.process_frame
	await t.process_frame
	set_work_zoom(b, original_zoom)
	b.view.center = original_center
	b.view.reframe()

static func set_work_zoom(board: Control, target: float) -> void:
	while board.view.cell_size < target - 0.01:
		board.zoom(1, board.view.viewport.get_center())
	while board.view.cell_size > target + 0.01:
		board.zoom(-1, board.view.viewport.get_center())

static func overflowing_lines(board: Control, axis: String) -> Array[int]:
	var result: Array[int] = []
	var count: int = board.view.dimensions.y if axis == "row" else board.view.dimensions.x
	for index: int in range(count):
		if int(board.clue_layout(axis, index).max_offset) > 0:
			result.append(index)
	return result

static func semantic_windows(board: Control, cases: Array[Dictionary]) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for entry: Dictionary in cases:
		result.append(board.clue_layout(entry.axis, entry.index))
	return result

static func check_semantic_transition(t: SceneTree, board: Control, cases: Array[Dictionary], before: Array[Dictionary], label: String) -> Array[Dictionary]:
	var after: Array[Dictionary] = semantic_windows(board, cases)
	for i: int in range(cases.size()):
		var entry: Dictionary = cases[i]
		var previous: Dictionary = before[i]
		var current: Dictionary = after[i]
		if entry.anchor == ClueLayout.OUTER_START:
			t.check(int(current.start) == 0 and not current.prefix_hidden and current.suffix_hidden and int(current.offset) == int(current.max_offset), "B-03 %s outer-start anchor survives %s" % [entry.axis, label])
		elif entry.anchor == ClueLayout.GRID_END:
			var count: int = board.clue_entry_count(entry.axis, entry.index)
			t.check(int(current.end) == count and current.prefix_hidden and not current.suffix_hidden and int(current.offset) == 0, "B-03 %s grid-end anchor survives %s" % [entry.axis, label])
		else:
			var overlap: int = maxi(0, mini(int(previous.end), int(current.end)) - maxi(int(previous.start), int(current.start)))
			var smaller: int = mini(int(previous.end) - int(previous.start), int(current.end) - int(current.start))
			t.check(current.prefix_hidden and current.suffix_hidden and overlap == smaller, "B-03 %s middle tokens retain maximal overlap across %s" % [entry.axis, label])
	return after

static func check_restored_windows(t: SceneTree, actual: Array[Dictionary], expected: Array[Dictionary], label: String) -> void:
	for i: int in range(actual.size()):
		t.check(reading_signature(actual[i]) == reading_signature(expected[i]), "B-03 semantic token window restores after " + label)

static func reading_signature(layout: Dictionary) -> Array:
	return [layout.start, layout.end, layout.prefix_hidden, layout.suffix_hidden]

static func clue_navigation_routes(t: SceneTree, app: Main, longest_row: int, longest_column: int) -> void:
	var b: Control = app.board
	b.reset_clue_pan()
	var cells: Array[int] = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	var undo_used: bool = app.session.player.undo_used
	var completed: bool = app.session.completed
	var raster_center: Vector2 = b.view.center
	var raster_size: float = b.view.cell_size
	var mini_frame: Rect2 = b.view.normalized_view()
	var rows: Array[int] = visible_overflowing_lines(b, "row")
	var columns: Array[int] = visible_overflowing_lines(b, "column")
	t.check(rows.size() >= 2 and columns.size() >= 2, "J-03 two visible pannable rows and columns available")
	if rows.size() < 2 or columns.size() < 2:
		return
	var row_a: int = rows[0]
	var row_b: int = rows[1]
	var column_a: int = columns[0]
	var column_b: int = columns[1]
	var row_point_a: Vector2 = clue_point(b, "row", row_a)
	var row_point_b: Vector2 = clue_point(b, "row", row_b)
	var column_point_a: Vector2 = clue_point(b, "column", column_a)
	var column_point_b: Vector2 = clue_point(b, "column", column_b)
	var rows_before: Array[int] = b.row_clue_steps.duplicate()
	var columns_before: Array[int] = b.column_clue_steps.duplicate()
	var row_b_window_before: Array = window_signature(b.clue_layout("row", row_b))
	var column_b_window_before: Array = window_signature(b.clue_layout("column", column_b))
	var row_pitch: float = float(b.clue_layout("row", row_a).slot_extent)
	# Middle-button diagonal motion below one slot does not flicker. Crossing one
	# horizontal slot changes only the row selected at gesture start.
	t.mouse_motion(row_point_a, false)
	t.mouse_button(row_point_a, true, MOUSE_BUTTON_MIDDLE)
	t.mouse_motion(row_point_a + Vector2(row_pitch * 0.8, row_pitch * 0.7), true, MOUSE_BUTTON_MIDDLE)
	t.check(b.clue_step("row", row_a) == 0 and b.pan_line_index == row_a, "J-03 sub-slot diagonal motion stays snapped to its start row")
	t.mouse_motion(row_point_a + Vector2(row_pitch * 1.2, row_pitch * 0.7), true, MOUSE_BUTTON_MIDDLE)
	t.check(b.pan_target == "row" and b.pan_line_index == row_a and b.row_clue_steps == rows_before and absf(float(b.visible_clue_layout("row", row_a).visual_shift)) > 0.0, "N-03 middle drag is continuous without confirming slots")
	t.check(window_signature(b.clue_layout("row", row_b)) == row_b_window_before, "J-03 neighbouring row window remains byte-for-byte equivalent")
	var outside: Vector2 = b.get_global_rect().end + Vector2(40, 40)
	t.mouse_button(outside, false, MOUSE_BUTTON_MIDDLE)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.pan_target.is_empty() and only_line_changed(rows_before, b.row_clue_steps, row_a), "N-03 row drag snaps on release outside")
	# Hand/left independently moves a second row by two fixed slots.
	app.set_tool("hand")
	t.mouse_motion(row_point_b, false)
	t.mouse_button(row_point_b, true)
	t.mouse_motion(row_point_b + Vector2(float(b.clue_layout("row", row_b).slot_extent) * 2.2, 0), true)
	t.mouse_button(row_point_b, false)
	t.check(b.clue_step("row", row_b) == 2 and b.clue_step("row", row_a) == 1, "J-03 second row keeps an independent snapped position")
	# Wrong release cannot finish a middle-button drag on one concrete column.
	app.set_tool("fill")
	t.mouse_motion(column_point_a, false)
	t.mouse_button(column_point_a, true, MOUSE_BUTTON_MIDDLE)
	t.mouse_button(column_point_a, false, MOUSE_BUTTON_LEFT)
	t.check(b.pan_button == MOUSE_BUTTON_MIDDLE and b.pan_target == "column" and b.pan_line_index == column_a, "J-03 wrong release keeps frozen column target")
	var column_pitch: float = float(b.clue_layout("column", column_a).slot_extent)
	t.mouse_motion(column_point_a + Vector2(column_pitch * 0.7, column_pitch * 1.2), true, MOUSE_BUTTON_MIDDLE)
	t.mouse_button(outside, false, MOUSE_BUTTON_MIDDLE)
	t.check(only_line_changed(columns_before, b.column_clue_steps, column_a) and b.clue_step("column", column_a) == 1, "J-03 diagonal column drag changes only its vertical slot")
	t.check(window_signature(b.clue_layout("column", column_b)) == column_b_window_before, "J-03 neighbouring column window remains byte-for-byte equivalent")
	# Hand/left follows the same route for a second column and freezes its line
	# even while the pointer crosses neighbouring columns.
	app.set_tool("hand")
	t.mouse_motion(column_point_b, false)
	t.mouse_button(column_point_b, true)
	t.mouse_motion(column_point_b + Vector2(b.view.cell_size * 3.0, float(b.clue_layout("column", column_b).slot_extent) * 2.2), true)
	t.mouse_button(column_point_b, false)
	t.check(b.clue_step("column", column_b) == 2 and b.clue_step("column", column_a) == 1, "J-03 second column ignores crossed neighbours")
	# Escape and focus loss terminate clue navigation without state changes.
	t.mouse_motion(row_point_a, false)
	t.mouse_button(row_point_a, true)
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	t.root.push_input(escape, true)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.pan_target.is_empty(), "J-03 Escape ends clue drag")
	t.mouse_motion(row_point_a, false)
	t.mouse_button(row_point_a, true)
	app.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.pan_target.is_empty(), "J-03 focus loss ends clue drag")
	# Empty/short fitting lines never pan into empty space.
	var short_row: int = first_fitting_line(b, "row")
	var short_point: Vector2 = clue_point(b, "row", short_row)
	t.mouse_motion(short_point, false)
	t.mouse_button(short_point, true, MOUSE_BUTTON_MIDDLE)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.clue_step("row", short_row) == 0, "J-03 empty or short row does not start clue panning")
	t.mouse_button(short_point, false, MOUSE_BUTTON_MIDDLE)
	# A normal clue click cannot paint, and an active cell gesture blocks clue panning.
	app.set_tool("fill")
	var prior_rows: Array[int] = b.row_clue_steps.duplicate()
	t.mouse_button(row_point_a, true)
	t.mouse_button(row_point_a, false)
	t.check(app.session.player.cells == cells and app.session.player.history == history and b.row_clue_steps == prior_rows, "J-03 normal clue click changes nothing")
	t.check(b.view.center == raster_center and b.view.cell_size == raster_size and b.view.normalized_view() == mini_frame, "J-03 pure clue navigation leaves raster and miniature frame unchanged")
	var visible_cell: Vector2i = b.view.hit(b.view.viewport.get_center())
	var cell_point: Vector2 = b.get_global_transform() * b.view.cell_rect(visible_cell).get_center()
	t.mouse_motion(cell_point, false)
	t.mouse_button(cell_point, true)
	t.mouse_button(row_point_a, true, MOUSE_BUTTON_MIDDLE)
	t.check(app.session.gesture.active and b.pan_button == MOUSE_BUTTON_NONE, "J-03 cell gesture blocks clue navigation")
	t.root.push_input(escape, true)
	# Raster pan, miniature, zoom, UI scale and resize preserve all individual
	# read positions where the same offsets remain valid.
	var expected_rows: Array[int] = b.row_clue_steps.duplicate()
	var expected_columns: Array[int] = b.column_clue_steps.duplicate()
	app.set_tool("hand")
	var grid_point: Vector2 = b.get_global_transform() * b.view.viewport.get_center()
	t.mouse_motion(grid_point, false)
	t.mouse_button(grid_point, true)
	t.mouse_motion(grid_point + Vector2(60, 40), true)
	t.mouse_button(grid_point + Vector2(60, 40), false)
	t.check(b.view.center != raster_center and b.row_clue_steps == expected_rows and b.column_clue_steps == expected_columns, "J-03 raster pan preserves every clue read position")
	app.refresh()
	await t.process_frame
	var before_miniature: Vector2 = b.view.center
	var mini_area: Rect2 = app.mini.image_rect()
	var mini_press: InputEventMouseButton = InputEventMouseButton.new()
	mini_press.position = mini_area.position + mini_area.size * Vector2(0.82, 0.82)
	mini_press.button_index = MOUSE_BUTTON_LEFT
	mini_press.pressed = true
	app.mini._gui_input(mini_press)
	var mini_release: InputEventMouseButton = mini_press.duplicate()
	mini_release.pressed = false
	app.mini._gui_input(mini_release)
	t.check(b.view.center != before_miniature and b.row_clue_steps == expected_rows and b.column_clue_steps == expected_columns, "J-03 miniature input preserves every clue read position")
	b.zoom(1, b.view.viewport.get_center())
	app.set_ui_scale(1.25)
	t.root.size = Vector2i(1920, 1080)
	await t.process_frame
	await t.process_frame
	t.check(b.row_clue_steps == expected_rows and b.column_clue_steps == expected_columns, "J-03 zoom/UI/resize preserve snapped per-line positions")
	t.check(app.session.player.cells == cells and app.session.player.history == history and app.session.player.undo_used == undo_used and app.session.completed == completed and app.session.gesture.changes().is_empty(), "J-03 clue navigation preserves matrix/preview/history/undo/completion")
	t.check(b.view.cell_size > raster_size and b.view.normalized_view() != mini_frame, "J-03 raster navigation remains independently functional")
	# Visible reset control returns every line to its grid-side default.
	t.root.size = Vector2i(1280, 720)
	app.set_ui_scale(1.0)
	await t.process_frame
	t.check(app.clue_reset_button.is_visible_in_tree(), "H-04 clue reset control stays visible")
	app.clue_reset_button.pressed.emit()
	t.check(b.row_clue_steps.count(0) == b.row_clue_steps.size() and b.column_clue_steps.count(0) == b.column_clue_steps.size(), "J-03 reset control restores every grid-side clue window")
	b.set_clue_step("row", longest_row, 1)
	b.set_clue_step("column", longest_column, 1)
	app.select_puzzle(1)
	app.select_puzzle(2)
	t.check(b.clue_step("row", longest_row) == 1 and b.clue_step("column", longest_column) == 1, "P1.3 fixture switch retains each clue view")
	t.check(b.clue_layout("row", longest_row).end > b.clue_layout("row", longest_row).start and b.clue_layout("column", longest_column).end > b.clue_layout("column", longest_column).start, "J-03 mapping remains valid after route sequence")

static func visible_overflowing_lines(board: Control, axis: String) -> Array[int]:
	var result: Array[int] = []
	var visible: Rect2 = board.view.visible_bounds()
	var first: int = maxi(0, floori(((visible.position.y if axis == "row" else visible.position.x) - (board.view.origin.y if axis == "row" else board.view.origin.x)) / board.view.cell_size))
	var finish: int = mini(board.view.dimensions.y if axis == "row" else board.view.dimensions.x,
		ceili(((visible.end.y if axis == "row" else visible.end.x) - (board.view.origin.y if axis == "row" else board.view.origin.x)) / board.view.cell_size))
	for index: int in range(first, finish):
		var center: Vector2 = board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
		var in_gutter: bool = board.row_clue_area().has_point(Vector2(board.row_clue_area().get_center().x, center.y)) if axis == "row" else board.column_clue_area().has_point(Vector2(center.x, board.column_clue_area().get_center().y))
		if in_gutter and int(board.clue_layout(axis, index).max_offset) > 0:
			result.append(index)
	return result

static func clue_point(board: Control, axis: String, index: int) -> Vector2:
	var local: Vector2
	if axis == "row":
		local = Vector2(board.row_clue_area().get_center().x, board.view.cell_rect(Vector2i(0, index)).get_center().y)
	else:
		local = Vector2(board.view.cell_rect(Vector2i(index, 0)).get_center().x, board.column_clue_area().get_center().y)
	return board.get_global_transform() * local

static func only_line_changed(before: Array[int], after: Array[int], index: int) -> bool:
	if before.size() != after.size() or before[index] == after[index]:
		return false
	for other: int in range(before.size()):
		if other != index and before[other] != after[other]:
			return false
	return true

static func window_signature(layout: Dictionary) -> Array:
	return [layout.start, layout.end, layout.prefix_hidden, layout.suffix_hidden, layout.offset, layout.units]

static func first_fitting_line(board: Control, axis: String) -> int:
	var count: int = board.view.dimensions.y if axis == "row" else board.view.dimensions.x
	for index: int in range(count):
		if int(board.clue_layout(axis, index).max_offset) == 0:
			return index
	return 0

static func longest_line(lines: Array) -> int:
	var result: int = 0
	for i: int in range(1, lines.size()):
		if lines[i].size() > lines[result].size():
			result = i
	return result

static func first_empty_line(lines: Array) -> int:
	for i: int in range(lines.size()):
		if lines[i].is_empty():
			return i
	return -1

static func has_button_text(node: Node, text: String) -> bool:
	if node is Button and node.text == text:
		return true
	for child: Node in node.get_children():
		if has_button_text(child, text):
			return true
	return false
