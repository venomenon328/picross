extends RefCounted
const Measurements = preload("res://tests/vs2_measurements.gd")
## Current regular H1 off/on pixels, complementing the strict frozen stress replay.
const H1 = preload("res://tests/h1_capture.gd")

static func run(c: SceneTree, app: Control) -> void:
	app.select_puzzle(0)
	var values: Array[int] = []
	for row: Array in app.session.definition.solution:
		for value: int in row: values.append(value if value>0 else -1)
	for i: int in range(values.size()-1,-1,-1):
		if values[i]>0:
			values[i] = -1
			break
	c.replace_render_cells(app,values)
	app.open_puzzle()
	app.board.clear_pointer_hover()
	for dims: Vector2i in [Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080),Vector2i(2560,1440)]:
		c.surface.size = dims
		app.size = Vector2(dims)
		for ui: float in [1.0,1.25]:
			app.set_ui_scale(ui)
			for mode: int in range(2):
				app.set_puzzle_view(mode)
				app.board.working_size()
				await c.process_frame
				H1.require(c,app.board.layout_valid and Measurements.capture(app.board).glyph_collisions==0,"current regular H1 drawable non-overlapping geometry")
				await H1.pair(c,app,"h1-vs2-%dx%d-ui%d-%s" % [dims.x,dims.y,roundi(ui*100),app.board.mode])
	app.set_clue_completion(true)
