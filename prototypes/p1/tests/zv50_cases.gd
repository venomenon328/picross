extends RefCounted
const Main = preload("res://ui/main.gd")
const Board = preload("res://ui/board.gd")

static func close(a: float, b: float, epsilon: float = 0.05) -> bool:
	return absf(a - b) <= epsilon

static func full_grid(board: Board) -> bool:
	var expected: Vector2 = Vector2(board.view.dimensions) * board.view.cell_size
	return board.view.visible_bounds().size.is_equal_approx(expected)

static func run(t: SceneTree) -> void:
	t.root.size = Vector2i(1920, 1080)
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	await t.process_frame
	app.select_puzzle(3)
	await t.process_frame
	app.board.working_size()
	await t.process_frame
	t.check(close(app.board.view.cell_size, 24.0) and app.board.view.viewport.size.is_equal_approx(Vector2(480, 480)) and full_grid(app.board), "ZV50-A01 20x20 standard remains 480 at 100 percent")
	for expected: float in [26.0, 28.0, 30.0, 32.0, 34.0, 36.0]:
		app.board.zoom(1, app.board.view.viewport.get_center())
		await t.process_frame
		var extent: Vector2 = Vector2(20, 20) * expected
		t.check(close(app.board.view.cell_size, expected) and app.board.view.viewport.size.x + 0.05 >= extent.x and app.board.view.viewport.size.y + 0.05 >= extent.y and full_grid(app.board), "ZV50-A01 full 20x20 grid at pitch " + str(expected))
		var corner: Vector2 = app.board.view.cell_rect(Vector2i(19, 19)).get_center()
		t.check(app.board.view.hit(corner) == Vector2i(19, 19), "ZV50-A01 hit test reaches last cell at pitch " + str(expected))

	var local_anchor: Vector2 = app.board.view.viewport.position + app.board.view.viewport.size * Vector2(0.68, 0.61)
	var global_anchor: Vector2 = app.board.to_global(local_anchor)
	var coordinate_before: Vector2 = (local_anchor - app.board.view.origin) / app.board.view.cell_size
	app.board.zoom(1, local_anchor)
	await t.process_frame
	var adjusted_anchor: Vector2 = app.board.to_local(global_anchor)
	var coordinate_after: Vector2 = (adjusted_anchor - app.board.view.origin) / app.board.view.cell_size
	t.check(close(app.board.view.cell_size, 40.0) and coordinate_before.distance_to(coordinate_after) < 0.08, "ZV50-A04 pointer anchor survives viewport growth")
	t.check(app.board.view.visible_bounds().size.x >= 799.9 and app.board.view.visible_bounds().size.y < 800.0 and not full_grid(app.board), "ZV50-A02 first tested overflow is actual vertical paper limit at 167 percent")
	app.board.zoom(-1, app.board.view.viewport.get_center())
	await t.process_frame
	t.check(close(app.board.view.cell_size, 36.0) and full_grid(app.board), "ZV50-A04 zooming back restores complete 150 percent view")

	app.select_puzzle(1)
	await t.process_frame
	app.board.working_size()
	await t.process_frame
	t.check(app.board.view.viewport.size.is_equal_approx(Vector2(720, 720)), "ZV50-A04 F02 historical 100 percent viewport stays stable")
	app.board.zoom(1, app.board.view.viewport.get_center())
	await t.process_frame
	t.check(close(app.board.view.cell_size, 26.0) and (app.board.view.viewport.size.x > 720.0 or app.board.view.viewport.size.y > 720.0), "ZV50-A04 F02 zoom uses additional page area")

	app.select_puzzle(2)
	await t.process_frame
	app.board.working_size()
	await t.process_frame
	t.check(app.board.view.viewport.size.x >= 1368.0 and app.board.view.viewport.size.y >= 672.0, "ZV50-A04 F03 minimum large-grid viewport remains")

	for dimensions: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		for scale: float in [1.0, 1.25]:
			t.root.size = dimensions
			app.set_ui_scale(scale)
			app.select_puzzle(3)
			app.board.working_size()
			while app.board.view.cell_size < 36.0:
				app.board.zoom(1, app.board.view.viewport.get_center())
			await t.process_frame
			var viewport_global: Rect2 = Rect2(app.board.global_position + app.board.view.viewport.position, app.board.view.viewport.size)
			var screen: Rect2 = Rect2(Vector2.ZERO, Vector2(dimensions))
			t.check(screen.encloses(viewport_global) and viewport_global.end.y <= app.actions.fill.global_position.y - 4.0, "ZV50-A03 zoom viewport respects UI at " + str(dimensions) + " scale " + str(scale))
			t.check(close(app.board.view.cell_size, 36.0), "ZV50-A03 resize/UI scale never changes chosen cell size")
	app.queue_free()
	await t.process_frame
