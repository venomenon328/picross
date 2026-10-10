extends RefCounted
const Main = preload("res://ui/main.gd")

static func require(c: SceneTree, condition: bool, message: String) -> void:
	if not condition:
		c.fail_capture("H1_RENDER: " + message)
		return
	c.pixel_checks += 1

static func changed_pixels(a: Image, b: Image, rect: Rect2) -> int:
	var count: int = 0
	var box: Rect2i = Rect2i(rect).intersection(Rect2i(Vector2i.ZERO, a.get_size()))
	for y: int in range(box.position.y, box.end.y):
		for x: int in range(box.position.x, box.end.x):
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				count += 1
	return count

static func same_region(a: Image, b: Image, rect: Rect2) -> bool:
	var box: Rect2i = Rect2i(rect).intersection(Rect2i(Vector2i.ZERO, a.get_size()))
	return a.get_region(box).get_data() == b.get_region(box).get_data()

static func token_ink_rect(font: Font, text: String, fs: int, baseline: Vector2) -> Rect2:
	# A full-em rectangle includes blank marker bearings where an adjacent
	# completed token's antialiased strike can legitimately end during a drag.
	# Check the actual glyph bounds, including their native texture bearings.
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var rect: Rect2 = Rect2()
	for i: int in range(text.length()):
		var glyph: int = ts.font_get_glyph_index(rid, fs, text.unicode_at(i), 0)
		var offset: Vector2 = ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph)
		var extent: Vector2 = ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph)
		var advance: float = font.get_string_size(text.left(i), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var box: Rect2 = Rect2(baseline + Vector2(advance, 0) + offset, extent)
		rect = rect.merge(box) if rect.has_area() else box
	return rect

static func pair(c: SceneTree, app: Main, name: String) -> void:
	var view_before: Dictionary = app.board.capture_view()
	app.set_clue_completion(false)
	var off: Image = await c.snapshot(app, name + "-off")
	var searches: int = app.board.completion_searches
	app.set_clue_completion(true)
	var on: Image = await c.snapshot(app, name + "-on")
	require(c, app.board.capture_view() == view_before and app.board.completion_searches == searches, name + " toggle keeps reads and cache")
	# Bind pixel regions to the selected clue face, punctuation and baseline.
	# The independent off/on pixel oracle and unchanged-grid checks stay intact.
	var font: Font = app.board.clue_font()
	var fs: int = app.board.clue_font_size()
	var marked: Dictionary = {"row": 0, "column": 0}
	var colors: Dictionary = {}
	var tooltip_box: Rect2 = Rect2()
	if not app.board.clue_hover_axis.is_empty():
		var tooltip_width: float = minf(520 * app.ui_scale, app.board.size.x - app.board.view.viewport.position.x - 32)
		var cursor: Vector2 = Vector2(14, 44 * app.ui_scale)
		for entry: Dictionary in app.board.tooltip_entries(app.board.clue_hover_axis, app.board.clue_hover_index):
			var width: float = app.board.clue_text_font(font, entry.text).get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, app.board.clue_tooltip_font_size()).x
			if cursor.x + width > tooltip_width - 14:
				cursor.x = 14
				cursor.y += 22 * app.ui_scale
			cursor.x += width + 9 * app.ui_scale
		tooltip_box = Rect2(app.board.global_position + app.board.view.viewport.position + Vector2(12, 12), Vector2(tooltip_width, cursor.y + 12 * app.ui_scale))
	for axis: String in ["row", "column"]:
		var count: int = app.session.player.height if axis == "row" else app.session.player.width
		for index: int in range(count):
			var center: Vector2 = app.board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
			var cross: float = center.y if axis == "row" else center.x
			var low: float = app.board.view.viewport.position.y if axis == "row" else app.board.view.viewport.position.x
			var high: float = app.board.view.viewport.end.y if axis == "row" else app.board.view.viewport.end.x
			if cross < low or cross > high:
				continue
			var entries: Array = app.board.tooltip_entries(axis, index)
			for unit: Dictionary in app.board.visual_hint_units(axis, index).units:
				var entry: Dictionary = entries[int(unit.index)] if unit.kind == "token" else {"text": "…", "marked": false}
				var width: float = app.board.clue_text_font(font, entry.text).get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
				var baseline: Vector2 = Vector2(float(unit.center) - width / 2, cross + app.board.clue_baseline_offset(fs)) if axis == "row" else Vector2(cross - width / 2, float(unit.center) + app.board.clue_baseline_offset(fs))
				var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
				if axis == "row" and (float(unit.center) - width / 2 < area.position.x or float(unit.center) + width / 2 > area.end.x):
					continue
				if axis == "column" and (float(unit.center) - app.board.clue_vertical_extents(fs).x < area.position.y or float(unit.center) + app.board.clue_vertical_extents(fs).y > area.end.y):
					continue
				var rect: Rect2 = token_ink_rect(app.board.clue_text_font(font, entry.text), entry.text, fs, app.board.global_position + baseline)
				if tooltip_box.has_area() and tooltip_box.intersects(rect):
					continue # Covered tokens are checked in the full tooltip below.
				var changed: int = changed_pixels(off, on, rect)
				var done: bool = int(entry.get("status", 0)) > 0
				require(c, (changed > 0) == done, name + " original token %s/%d/%d changed=%d rect=%s" % [axis, index, int(unit.index), changed, rect])
				if done:
					marked[axis] += 1
					colors[str(entry.color)] = true
	# The board's raster and separate miniature must be pixel-identical.
	if app.board.clue_hover_axis.is_empty():
		var grid: Rect2 = app.board.view.visible_bounds()
		require(c, same_region(off, on, Rect2(app.board.global_position + grid.position, grid.size)), name + " grid unchanged")
	else:
		var entries: Array = app.board.tooltip_entries(app.board.clue_hover_axis, app.board.clue_hover_index)
		var tooltip_fs: int = app.board.clue_tooltip_font_size()
		var box_width: float = minf(520 * app.ui_scale, app.board.size.x - app.board.view.viewport.position.x - 32)
		var cursor: Vector2 = Vector2(14, 44 * app.ui_scale)
		for entry: Dictionary in entries:
			var width: float = app.board.clue_text_font(font, entry.text).get_string_size(entry.text, HORIZONTAL_ALIGNMENT_LEFT, -1, tooltip_fs).x
			if cursor.x + width > box_width - 14:
				cursor.x = 14
				cursor.y += 22 * app.ui_scale
			var baseline: Vector2 = app.board.global_position + app.board.view.viewport.position + Vector2(12, 12) + cursor
			require(c, (changed_pixels(off, on, token_ink_rect(app.board.clue_text_font(font, entry.text), entry.text, tooltip_fs, baseline)) > 0) == (int(entry.get("status", 0)) > 0), name + " tooltip original token")
			cursor.x += width + 9 * app.ui_scale
	require(c, same_region(off, on, app.mini.get_global_rect()), name + " miniature unchanged")
	require(c, marked.row > 0 and marked.column > 0, name + " both axes drawn with marks")
	c.frames[-1]["h1_pair"] = {"off_frame": name + "-off", "marked_tokens": marked, "colors": colors.keys(), "searches_on_toggle": app.board.completion_searches - searches}

static func configurations(compact: bool) -> Array:
	if compact:
		# Preserve minimum-window/UI125 and the current 1080p target, both
		# faces of the clue-size boundary, and the smallest readable pitch.
		return [
			{"size": Vector2i(1280, 720), "scale": 1.25, "pitch": 12.0},
			{"size": Vector2i(1920, 1080), "scale": 1.0, "pitch": 18.0},
			{"size": Vector2i(1920, 1080), "scale": 1.25, "pitch": 22.0},
			{"size": Vector2i(1920, 1080), "scale": 1.0, "pitch": 24.0},
		]
	var result: Array = []
	for dims: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		for scale: float in [1.0, 1.25]:
			for pitch: float in [12.0, 18.0, 22.0, 24.0]:
				result.append({"size": dims, "scale": scale, "pitch": pitch})
	return result

static func run(c: SceneTree, app: Main) -> void:
	for fixture: int in [1, 2]:
		app.select_puzzle(fixture)
		var values: Array[int] = []
		for row: Array in app.session.definition.solution:
			for value: int in row:
				values.append(value if value > 0 else -1)
		# Keep work scene open without changing definitions or completion rules.
		for i: int in range(values.size() - 1, -1, -1):
			if values[i] > 0:
				values[i] = -1
				break
		c.replace_render_cells(app, values)
		app.open_puzzle()
		app.board.clear_pointer_hover()
		for configuration: Dictionary in configurations(c.compact):
			var dims: Vector2i = configuration.size
			var scale: float = configuration.scale
			var pitch: float = configuration.pitch
			c.surface.size = dims
			app.set_ui_scale(scale)
			await c.process_frame
			app.board.view.zoom_to(pitch, app.board.view.viewport.get_center())
			app.board.normalize_clue_steps()
			for axis: String in ["row", "column"]:
				var lines: Array = app.session.definition.rows if axis == "row" else app.session.definition.columns
				for i: int in range(lines.size()):
					c.set_fractional_step(app, axis, i, float(i % 3) / 2.0)
			await pair(c, app, "h1-f%d-%dx%d-ui%d-zoom%d" % [fixture + 1, dims.x, dims.y, roundi(scale * 100), roundi(pitch / 24 * 100)])
		c.surface.size = Vector2i(1920, 1080)
		app.set_ui_scale(1.0)
		app.board.restore_view(app.board.capture_view().merged({"zoom":24,"overview":false},true))
		await c.process_frame
		if fixture == 2:
			var partial: Array[int] = values.duplicate()
			for i: int in range(5000, partial.size()):
				partial[i] = -1
			c.replace_render_cells(app, partial)
			c.component_navigate(app, Vector2(0.5, 0.5))
			for x: int in range(100):
				c.set_fractional_step(app, "column", x, 1.0)
			await pair(c, app, "h1-f3-partial-identical-numbers")
			app.board.set_clue_hover("column", 50)
			await pair(c, app, "h1-f3-partial-tooltip")
			app.board.clear_pointer_hover()
			c.replace_render_cells(app, values)
		for axis: String in ["row", "column"]:
			var lines: Array = app.session.definition.rows if axis == "row" else app.session.definition.columns
			var index: int = c.longest_line(lines)
			c.component_navigate(app, Vector2(0.5, (index + 0.5) / app.session.player.height) if axis == "row" else Vector2((index + 0.5) / app.session.player.width, 0.5))
			app.board.set_clue_step(axis, index, 0)
			app.board.set_clue_hover(axis, index)
			await pair(c, app, "h1-f%d-%s-tooltip" % [fixture + 1, axis])
			app.board.clear_pointer_hover()
			# The wider surface may fit the entire row. Force actual overflow.
			c.surface.size = Vector2i(1280, 720)
			await c.process_frame
			await c.process_frame
			c.component_navigate(app, Vector2(0.5, (index + 0.5) / app.session.player.height) if axis == "row" else Vector2((index + 0.5) / app.session.player.width, 0.5))
			var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
			var cell: Vector2 = app.board.view.cell_rect(Vector2i(index, index)).get_center()
			var point: Vector2 = app.board.global_position + (Vector2(area.get_center().x, cell.y) if axis == "row" else Vector2(cell.x, area.get_center().y))
			var press: InputEventMouseButton = InputEventMouseButton.new()
			press.position = point
			press.button_index = MOUSE_BUTTON_MIDDLE
			press.pressed = true
			c.surface.push_input(press, true)
			var motion: InputEventMouseMotion = InputEventMouseMotion.new()
			var delta: float = 1.49 * app.board.shared_clue_slot_extent(axis, app.board.clue_font(), app.board.clue_font_size())
			motion.position = point + (Vector2(delta, 0) if axis == "row" else Vector2(0, delta))
			c.surface.push_input(motion, true)
			require(c, app.board.pan_target == axis, "H1 live hint drag entered")
			await pair(c, app, "h1-f%d-%s-drag" % [fixture + 1, axis])
			var release: InputEventMouseButton = press.duplicate()
			release.position = motion.position
			release.pressed = false
			c.surface.push_input(release, true)
			app.board.clear_pointer_hover()
			await pair(c, app, "h1-f%d-%s-drop" % [fixture + 1, axis])
	app.set_clue_completion(true)
