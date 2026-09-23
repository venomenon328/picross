extends RefCounted
const Definition = preload("res://model/definition.gd")
const Player = preload("res://model/player.gd")
const Gesture = preload("res://model/gesture.gd")
const Session = preload("res://model/session.gd")
const GridView = preload("res://ui/grid_view.gd")
const Main = preload("res://ui/main.gd")
const Board = preload("res://ui/board.gd")

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
	await ui_cases(t)

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
	b.hover = Vector2i(57, 87)
	t.check(b.row_hint_overflows(87), "long F03 row uses compact overflow marker")
	b.set_clue_hover("row", 87)
	var tooltip: Array = b.tooltip_entries("row", 87)
	var complete_tooltip: bool = tooltip.size() == app.session.definition.rows[87].size()
	for i: int in range(tooltip.size()):
		var clue: Dictionary = app.session.definition.rows[87][i]
		complete_tooltip = complete_tooltip and tooltip[i].text == b.clue_token(clue) and tooltip[i].color.is_equal_approx(b.clue_color(clue))
	t.check(complete_tooltip, "in-work hover tooltip contains every row clue and color")
	t.check(not has_button_text(app, "Ganze Zeile / Spalte ↗") and not has_button_text(app, "Hinweisansicht schließen"), "separate clue view removed")
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

static func has_button_text(node: Node, text: String) -> bool:
	if node is Button and node.text == text:
		return true
	for child: Node in node.get_children():
		if has_button_text(child, text):
			return true
	return false
