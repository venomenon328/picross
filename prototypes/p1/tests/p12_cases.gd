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
	t.check(Main.bounded_start(Rect2i(0, 0, 2560, 1400), Vector2i(16, 48)) == Vector2i(1600, 900), "large start remains 1600x900")
	for usable: Rect2i in [Rect2i(0, 0, 1366, 768), Rect2i(-1920, 32, 1920, 1000), Rect2i(0, 0, 1100, 680)]:
		var decoration: Vector2i = Vector2i(16, 48)
		var offset: Vector2i = Vector2i(8, 40)
		var client: Vector2i = Main.bounded_start(usable, decoration)
		var position: Vector2i = Main.bounded_position(usable, client, decoration, offset)
		t.check(usable.encloses(Rect2i(position - offset, client + decoration)), "whole decorated window fits asymmetric frame")
	test_atomic_clue_windows(t)
	await ui_cases(t)

static func test_atomic_clue_windows(t: SceneTree) -> void:
	var full: Dictionary = ClueLayout.select_window([10.0, 10.0, 10.0], 40.0, 0.0, 6.0, 2.0)
	t.check(full.start == 0 and full.end == 3 and not full.prefix_hidden and not full.suffix_hidden, "H-01 fitting clue sequence has no marker")
	var just_overflowing: Dictionary = ClueLayout.select_window([10.0, 10.0, 10.0], 30.0, 0.0, 6.0, 2.0)
	t.check(just_overflowing.start == 1 and just_overflowing.end == 3 and just_overflowing.prefix_hidden and not just_overflowing.suffix_hidden, "H-01 overflow drops one outer token, not the fitting suffix")
	var middle: Dictionary = ClueLayout.select_window([10.0, 18.0, 10.0, 10.0, 22.0, 10.0], 48.0, 0.5, 6.0, 2.0)
	t.check(middle.start < middle.end and middle.prefix_hidden and middle.suffix_hidden, "H-01 middle clue window reserves both markers")
	var empty: Dictionary = ClueLayout.select_window([], 10.0, 0.0, 6.0, 2.0)
	t.check(empty.start == 0 and empty.end == 0 and not empty.prefix_hidden and not empty.suffix_hidden, "H-01 empty layout is stable")
	var reached: Dictionary = {}
	var extents: Array[float] = []
	for i: int in range(24):
		extents.append(8.0 if i % 3 else 16.0)
	for sample: int in range(49):
		var window: Dictionary = ClueLayout.select_window(extents, 52.0, float(sample) / 48.0, 6.0, 2.0)
		t.check(window.start < window.end, "H-01 very long sequence always keeps complete clues")
		for index: int in range(int(window.start), int(window.end)):
			reached[index] = true
	t.check(reached.size() == extents.size(), "H-01 panning reaches every token in a very long sequence")

static func ui_cases(t: SceneTree) -> void:
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	app.select_puzzle(1)
	await t.process_frame
	await t.process_frame
	var b: Control = app.board
	var sample_clue: Dictionary = app.session.definition.rows[10][0]
	t.check(b.clue_token(sample_clue) == str(int(sample_clue.length)), "colored clue defaults to number without suffix")
	t.check(b.clue_color(sample_clue).is_equal_approx(Color(app.session.definition.palette[int(sample_clue.color) - 1].color)), "clue number uses puzzle color")
	app.toggle_accessibility_labels()
	t.check(b.clue_token(sample_clue).ends_with(app.session.definition.palette[int(sample_clue.color) - 1].symbol), "optional accessibility suffix enabled")
	app.toggle_accessibility_labels()
	var empty_row: int = first_empty_line(app.session.definition.rows)
	var empty_layout: Dictionary = b.clue_layout("row", empty_row)
	t.check(empty_layout.entries.size() == 1 and empty_layout.entries[0].text == "–" and not empty_layout.prefix_hidden and not empty_layout.suffix_hidden, "H-01 empty fixture line remains a visible dash")
	t.check(b.clue_token({"length": 12, "color": 1}) == "12", "H-01 multi-digit clue remains one token")
	# H-01/H-02: actual F-02 geometry keeps atomic suffixes and exposes start/middle/end.
	var column_22: Array = app.session.definition.columns[21]
	t.check(column_22.size() == 12 and int(column_22[0].length) == 6 and int(column_22[0].color) == 4 and int(column_22[1].length) == 3 and int(column_22[1].color) == 3 and int(column_22[2].length) == 3 and int(column_22[2].color) == 2, "H-02 F-02 column 22 starts blue 6, red 3, yellow 3")
	for step: float in [22.0, 24.0]:
		b.view.zoom_to(step, b.view.viewport.get_center())
		b.column_clue_position = 0.0
		var base_layout: Dictionary = b.clue_layout("column", 21)
		var extents: Array[float] = base_layout.extents
		var n: int = extents.size()
		var one_removed_space: float = float(base_layout.marker_extent) + float(base_layout.gap) * float(n - 1)
		for i: int in range(1, n):
			one_removed_space += extents[i]
		var after_blue: Dictionary = b.clue_layout("column", 21, one_removed_space)
		t.check(after_blue.start == 1 and after_blue.end == n and after_blue.prefix_hidden and not after_blue.suffix_hidden, "H-02 removing blue 6 keeps suffix at pitch " + str(step))
		var two_removed_space: float = float(base_layout.marker_extent) + float(base_layout.gap) * float(n - 2)
		for i: int in range(2, n):
			two_removed_space += extents[i]
		var after_red: Dictionary = b.clue_layout("column", 21, two_removed_space)
		t.check(after_red.start == 2 and after_red.end == n and after_red.prefix_hidden and not after_red.suffix_hidden, "H-02 removing red 3 keeps suffix from yellow 3 at pitch " + str(step))
	b.view.zoom_to(24.0, b.view.viewport.get_center())
	for position: float in [0.0, 0.5, 1.0]:
		b.column_clue_position = position
		var column_window: Dictionary = b.clue_layout("column", 21)
		b.row_clue_position = position
		var row_window: Dictionary = b.clue_layout("row", 35)
		t.check(column_window.start < column_window.end and row_window.start < row_window.end, "H-02 both axes keep real clues at pan " + str(position))
		if position == 0.0:
			t.check(column_window.end == column_22.size() and row_window.end == app.session.definition.rows[35].size(), "H-02 default windows retain grid-near ends")
		elif position == 1.0:
			t.check(column_window.start == 0 and row_window.start == 0, "H-02 outer beginnings reachable on both axes")
	b.column_clue_position = 0.5
	var labels_off: Dictionary = b.clue_layout("column", 21)
	app.toggle_accessibility_labels()
	var labels_on: Dictionary = b.clue_layout("column", 21)
	t.check(labels_on.start < labels_on.end and labels_on.entries[labels_on.start].text.length() > labels_off.entries[labels_off.start].number.length(), "H-01 A-D labels participate in atomic layout")
	app.toggle_accessibility_labels()
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
			for position: float in [0.0, 0.5, 1.0]:
				b.row_clue_position = position
				b.column_clue_position = position
				var row_window: Dictionary = b.clue_layout("row", longest_row)
				var column_window: Dictionary = b.clue_layout("column", longest_column)
				t.check(row_window.end > row_window.start and column_window.end > column_window.start, "H-03 real F-03 clues at UI/pitch/pan %s/%s/%s" % [scale, step, position])
				t.check(row_window.prefix_hidden or row_window.suffix_hidden, "H-03 long row markers reflect hidden entries")
	app.set_ui_scale(1.0)
	b.working_size()
	b.reset_clue_pan()
	await clue_navigation_routes(t, app, longest_row, longest_column)
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

static func clue_navigation_routes(t: SceneTree, app: Main, longest_row: int, longest_column: int) -> void:
	var b: Control = app.board
	var cells: Array[int] = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	var raster_center: Vector2 = b.view.center
	var raster_size: float = b.view.cell_size
	var mini_frame: Rect2 = b.view.normalized_view()
	var row_local: Vector2 = b.row_clue_area().get_center()
	var column_local: Vector2 = b.column_clue_area().get_center()
	var row_point: Vector2 = b.get_global_transform() * row_local
	var column_point: Vector2 = b.get_global_transform() * column_local
	# Middle-button row drag crosses into the grid and releases outside; target stays row.
	t.mouse_motion(row_point, false)
	t.mouse_button(row_point, true, MOUSE_BUTTON_MIDDLE)
	t.mouse_motion(row_point + Vector2(b.row_clue_area().size.x * 0.8, 0), true, MOUSE_BUTTON_MIDDLE)
	t.check(b.pan_target == "row" and b.row_clue_position > 0.0 and b.column_clue_position == 0.0, "H-04 row hint drag is independently horizontal")
	var outside: Vector2 = b.get_global_rect().end + Vector2(40, 40)
	t.mouse_button(outside, false, MOUSE_BUTTON_MIDDLE)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.pan_target.is_empty(), "H-04 row drag releases outside")
	# Wrong release cannot finish a middle-button hint drag.
	t.mouse_motion(column_point, false)
	t.mouse_button(column_point, true, MOUSE_BUTTON_MIDDLE)
	t.mouse_button(column_point, false, MOUSE_BUTTON_LEFT)
	t.check(b.pan_button == MOUSE_BUTTON_MIDDLE and b.pan_target == "column", "H-04 wrong button release ignored for clue drag")
	t.mouse_motion(column_point + Vector2(0, b.column_clue_area().size.y * 0.8), true, MOUSE_BUTTON_MIDDLE)
	t.mouse_button(outside, false, MOUSE_BUTTON_MIDDLE)
	t.check(b.column_clue_position > 0.0 and b.row_clue_position > 0.0, "H-04 column hint drag is independent and vertical")
	# Hand/left follows the same route and clamps rather than panning forever.
	app.set_tool("hand")
	b.column_clue_position = 0.95
	t.mouse_motion(column_point, false)
	t.mouse_button(column_point, true)
	t.mouse_motion(column_point + Vector2(0, b.column_clue_area().size.y), true)
	t.mouse_button(column_point + Vector2(0, b.column_clue_area().size.y), false)
	t.check(b.column_clue_position == 1.0, "H-04 hand drag clamps at clue boundary")
	# Escape and focus loss terminate clue navigation without state changes.
	t.mouse_motion(row_point, false)
	t.mouse_button(row_point, true)
	var escape: InputEventKey = InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	t.root.push_input(escape, true)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.pan_target.is_empty(), "H-04 Escape ends clue drag")
	t.mouse_motion(row_point, false)
	t.mouse_button(row_point, true)
	app.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	t.check(b.pan_button == MOUSE_BUTTON_NONE and b.pan_target.is_empty(), "H-04 focus loss ends clue drag")
	# A normal clue click cannot paint, and an active cell gesture blocks clue panning.
	app.set_tool("fill")
	var prior_row: float = b.row_clue_position
	t.mouse_button(row_point, true)
	t.mouse_button(row_point, false)
	t.check(app.session.player.cells == cells and app.session.player.history == history and b.row_clue_position == prior_row, "H-04 normal clue click changes nothing")
	t.check(b.view.center == raster_center and b.view.cell_size == raster_size and b.view.normalized_view() == mini_frame, "H-04 pure clue navigation leaves raster and miniature frame unchanged")
	var visible_cell: Vector2i = b.view.hit(b.view.viewport.get_center())
	var cell_point: Vector2 = b.get_global_transform() * b.view.cell_rect(visible_cell).get_center()
	t.mouse_motion(cell_point, false)
	t.mouse_button(cell_point, true)
	t.mouse_button(row_point, true, MOUSE_BUTTON_MIDDLE)
	t.check(app.session.gesture.active and b.pan_button == MOUSE_BUTTON_NONE, "H-04 cell gesture blocks clue navigation")
	t.root.push_input(escape, true)
	# Pure raster pan, zoom, UI resize and labels preserve the two read positions.
	b.row_clue_position = 0.4
	b.column_clue_position = 0.6
	app.set_tool("hand")
	var grid_point: Vector2 = b.get_global_transform() * b.view.viewport.get_center()
	t.mouse_motion(grid_point, false)
	t.mouse_button(grid_point, true)
	t.mouse_motion(grid_point + Vector2(60, 40), true)
	t.mouse_button(grid_point + Vector2(60, 40), false)
	t.check(b.view.center != raster_center and is_equal_approx(b.row_clue_position, 0.4) and is_equal_approx(b.column_clue_position, 0.6), "H-04 raster pan preserves clue read positions")
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
	t.check(b.view.center != before_miniature and is_equal_approx(b.row_clue_position, 0.4) and is_equal_approx(b.column_clue_position, 0.6), "H-04 miniature input route preserves clue read positions")
	b.zoom(1, b.view.viewport.get_center())
	app.set_ui_scale(1.25)
	app.toggle_accessibility_labels()
	t.check(is_equal_approx(b.row_clue_position, 0.4) and is_equal_approx(b.column_clue_position, 0.6), "H-04 zoom/UI/A-D preserve bounded clue positions")
	t.check(app.session.player.cells == cells and app.session.player.history == history and b.view.cell_size > raster_size and b.view.normalized_view() != mini_frame, "H-04 clue navigation keeps cells/history; raster navigation remains independent")
	# Visible reset control returns both areas to their grid-side defaults.
	app.set_ui_scale(1.0)
	app.toggle_accessibility_labels()
	await t.process_frame
	t.check(app.clue_reset_button.is_visible_in_tree(), "H-04 clue reset control stays visible")
	app.clue_reset_button.pressed.emit()
	t.check(b.row_clue_position == 0.0 and b.column_clue_position == 0.0, "H-04 reset control restores grid-side clue windows")
	app.select_puzzle(1)
	app.select_puzzle(2)
	t.check(b.row_clue_position == 0.0 and b.column_clue_position == 0.0, "H-04 deliberate fixture switch resets clue views")
	t.check(b.clue_layout("row", longest_row).end > b.clue_layout("row", longest_row).start and b.clue_layout("column", longest_column).end > b.clue_layout("column", longest_column).start, "H-04 mapping remains valid after route sequence")

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
