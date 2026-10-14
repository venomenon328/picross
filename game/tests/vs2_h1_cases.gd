extends RefCounted
const VisualCases = preload("res://tests/current_visual_cases.gd")
const Measurements = preload("res://tests/vs2_measurements.gd")
## Current regular H1 off/on pixels; no historical clipped-board replay.
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
	for configuration: Array in VisualCases.CONFIGURATIONS:
		var dims: Vector2i = configuration[0]
		var ui: float = configuration[1]
		c.surface.size = dims
		app.size = Vector2(dims)
		app.set_ui_scale(ui)
		for mode: int in range(2):
			app.set_puzzle_view(mode)
			app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
			await c.process_frame
			H1.require(c,app.board.layout_valid and Measurements.capture(app.board).glyph_collisions==0,"current regular H1 drawable non-overlapping geometry")
			await H1.pair(c,app,"h1-vs2-%dx%d-ui%d-%s" % [dims.x,dims.y,roundi(ui*100),app.board.mode])
	app.set_clue_completion(true)
