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
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	await t.process_frame
	t.check(close(app.board.view.cell_size,24) and full_grid(app.board), "VS2 preserves regular 24px work intent within fit")
	for i: int in range(24):
		var before: float = app.board.view.cell_size
		app.board.zoom(1,app.board.view.viewport.get_center())
		t.check(app.board.view.cell_size >= before and app.board.view.cell_size <= app.board.fit_ceiling and full_grid(app.board), "VS2 replaces ZV50 overflow by monotone full-frame ceiling")
		var corner: Vector2 = app.board.view.cell_rect(Vector2i(19,19)).get_center()
		t.check(app.board.view.hit(corner) == Vector2i(19,19), "VS2 last cell reachable at every zoom")
	app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
	for index: int in [1,2]:
		app.select_puzzle(index)
		app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
		t.check(full_grid(app.board) and app.board.view.cell_size <= app.board.fit_ceiling, "VS2 large sheets fit instead of historical clipped viewport")
	for dimensions: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		for scale: float in [1.0, 1.25]:
			t.root.size = dimensions
			app.set_ui_scale(scale)
			app.select_puzzle(3)
			app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
			for i: int in range(8):
				app.board.zoom(1, app.board.view.viewport.get_center())
			await t.process_frame
			var viewport_global: Rect2 = Rect2(app.board.global_position + app.board.view.viewport.position, app.board.view.viewport.size)
			var screen: Rect2 = Rect2(Vector2.ZERO, Vector2(dimensions))
			t.check(screen.encloses(viewport_global) and not viewport_global.intersects(app.tools_scroll.get_global_rect().grow(4.0)), "ZV50-A03 zoom viewport stays clear of right V3 tools at " + str(dimensions) + " scale " + str(scale))
			t.check(app.board.view.cell_size <= app.board.fit_ceiling and full_grid(app.board), "VS2 resize/UI always clamps full frame")
	app.queue_free()
	await t.process_frame
