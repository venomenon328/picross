extends SceneTree
## Real GPU/software-rendered offscreen surfaces; not a physical DPI claim.
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
var surface: SubViewport
var output: String
var captures: Array = []
var pixel_checks: int = 0
var x_test_cell: Vector2i = Vector2i(-1, -1)

func _initialize() -> void:
	var temporary: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if temporary.is_empty():
		temporary = OS.get_environment("TEMP") if OS.has_feature("windows") else OS.get_environment("TMPDIR")
	if temporary.is_empty():
		temporary = "/tmp"
	SaveStore.test_root_override = temporary.path_join("picross-p1-capture-%d" % Time.get_ticks_usec())
	call_deferred("run")

func snapshot(app: Main, name: String, crop: bool = false) -> void:
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	if name.begins_with("separation-") and name.ends_with("-confirmed"):
		for i: int in range(app.session.definition.palette.size()):
			var cell: Rect2 = app.board.view.cell_rect(Vector2i(2 + i * 2, 4))
			var center: Vector2i = Vector2i(app.board.global_position + cell.get_center())
			var expanded: Vector2i = Vector2i(app.board.global_position + cell.position + Vector2(2, cell.size.y / 2))
			var moat: Vector2i = Vector2i(app.board.global_position + cell.position + Vector2(1, cell.size.y / 2))
			if not picture.get_pixelv(center).is_equal_approx(Color(app.session.definition.palette[i].color)) or not picture.get_pixelv(expanded).is_equal_approx(Color(app.session.definition.palette[i].color)) or not picture.get_pixelv(moat).is_equal_approx(app.board.PAPER):
				push_error("Rendered fill/moat regression: " + name)
				quit(5)
				return
			pixel_checks += 3
	if name.contains("preview-color"):
		var color_index: int = int(name.get_slice("preview-color", 1))
		var preview_cell: Rect2 = app.board.view.cell_rect(Vector2i(2, 3))
		var preview_center: Vector2i = Vector2i(app.board.global_position + preview_cell.get_center())
		var preview_moat: Vector2i = Vector2i(app.board.global_position + preview_cell.position + Vector2(1, preview_cell.size.y / 2))
		var expected_fill: Color = Color(app.session.definition.palette[color_index - 1].color)
		var gap: Color = picture.get_pixelv(preview_moat)
		if not picture.get_pixelv(preview_center).is_equal_approx(expected_fill) or absf(gap.r - expected_fill.r) + absf(gap.g - expected_fill.g) + absf(gap.b - expected_fill.b) < 0.2:
			push_error("Rendered preview fill/moat regression: " + name)
			quit(5)
			return
		pixel_checks += 2
	if name == "f03-grid-focus":
		var focus: Vector2i = app.board.hover
		var row_point: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus + Vector2i(2, 0)).get_center())
		var column_point: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus + Vector2i(0, 2)).get_center())
		var intersection: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus).get_center())
		var outside: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus + Vector2i(2, 2)).get_center())
		var band: Color = Color("e8e9d9")
		if not picture.get_pixelv(row_point).is_equal_approx(band) or not picture.get_pixelv(column_point).is_equal_approx(band) or not picture.get_pixelv(intersection).is_equal_approx(band) or not picture.get_pixelv(outside).is_equal_approx(app.board.PAPER):
			push_error("Rendered grid focus regression")
			quit(5)
			return
		pixel_checks += 4
	if name.begins_with("x-clip-"):
		var cell_box: Rect2 = app.board.view.cell_rect(x_test_cell)
		var found: bool = false
		for endpoints: Array in [[cell_box.position + cell_box.size * 0.3, cell_box.position + cell_box.size * 0.7], [cell_box.position + cell_box.size * Vector2(0.7, 0.3), cell_box.position + cell_box.size * Vector2(0.3, 0.7)]]:
			var segment: PackedVector2Array = Board.clipped_segment(endpoints[0], endpoints[1], app.board.view.viewport.grow(-0.65))
			if segment.size() == 2 and segment[0].distance_to(segment[1]) >= 3.0:
				var sample: Vector2i = Vector2i(app.board.global_position + (segment[0] + segment[1]) * 0.5)
				var pixel: Color = picture.get_pixelv(sample)
				if pixel.r < 0.82 and pixel.g < 0.82 and pixel.b < 0.82:
					found = true
					break
		if not found:
			push_error("Rendered clipped X absent: " + name)
			quit(5)
			return
		pixel_checks += 1
	if name == "gesture-counter-8":
		var font: Font = ThemeDB.fallback_font
		var fs: int = roundi(15 * app.board.ui_scale)
		var box_size: Vector2 = font.get_string_size("8", HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(14, 10)
		var end_point: Vector2 = app.board.view.cell_rect(app.session.gesture.endpoint).get_center()
		var place: Vector2 = (end_point + Vector2(12, -box_size.y - 8)).clamp(app.board.view.viewport.position + Vector2(2, 2), app.board.view.viewport.end - box_size - Vector2(2, 2))
		var sample: Vector2i = Vector2i(app.board.global_position + place + Vector2(3, 3))
		var dark_pixels: int = 0
		var area: Rect2i = Rect2i(Rect2(app.board.global_position + place, box_size))
		for y: int in range(area.position.y + 3, area.end.y - 3):
			for x: int in range(area.position.x + 3, area.end.x - 3):
				if picture.get_pixel(x, y).r < 0.5:
					dark_pixels += 1
		if not picture.get_pixelv(sample).is_equal_approx(Color("fffaf0")) or dark_pixels < 3:
			push_error("Rendered live counter absent")
			quit(5)
			return
		pixel_checks += 2
	if name.begins_with("hint-marker-"):
		var parts: PackedStringArray = name.split("-")
		var axis: String = parts[2]
		var index: int = int(parts[3])
		var visual: Dictionary = app.board.visual_hint_units(axis, index)
		var layout: Dictionary = app.board.visible_clue_layout(axis, index)
		var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
		var line_center: Vector2 = app.board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
		for side: String in ["prefix", "suffix"]:
			var slot: int = 0 if side == "prefix" else int(layout.slot_count) - 1
			var center: float = app.board.clue_slot_center(axis, area, layout, slot)
			var marker_center: Vector2 = app.board.global_position + (Vector2(center, line_center.y) if axis == "row" else Vector2(line_center.x, center))
			var region: Rect2i = Rect2i(Rect2(marker_center - Vector2(8, 9), Vector2(16, 18))).intersection(Rect2i(Vector2i.ZERO, picture.get_size()))
			var accent_pixels: int = 0
			for y: int in range(region.position.y, region.end.y):
				for x: int in range(region.position.x, region.end.x):
					var pixel: Color = picture.get_pixel(x, y)
					if absf(pixel.r - app.board.ACCENT.r) + absf(pixel.g - app.board.ACCENT.g) + absf(pixel.b - app.board.ACCENT.b) < 0.03:
						accent_pixels += 1
			if (accent_pixels > 0) != bool(visual[side + "_hidden"]):
				push_error("Rendered hint marker mismatch: %s %s (%d pixels)" % [name, side, accent_pixels])
				quit(5)
				return
			pixel_checks += 1
	if name.ends_with("reveal"):
		var texture_image: Image = app.reveal_view.artwork.get_image()
		if texture_image == null or texture_image.is_empty():
			push_error("Missing rendered reveal")
			quit(6)
			return
	if crop:
		var box: Rect2 = app.board.view.cell_rect(Vector2i(2, 2)).merge(app.board.view.cell_rect(Vector2i(18, 8)))
		box.position += app.board.global_position
		picture = picture.get_region(Rect2i(box.grow(8)))
	if picture.save_png(output.path_join(name + ".png")) != OK:
		quit(4)
		return
	var row_index: int = longest_line(app.session.definition.rows)
	var column_index: int = longest_line(app.session.definition.columns)
	var row_window: Dictionary = app.board.clue_layout("row", row_index)
	var column_window: Dictionary = app.board.clue_layout("column", column_index)
	captures.append({"file": name + ".png", "logical_surface": [surface.size.x, surface.size.y], "ui_scale": app.ui_scale, "cell_pitch": app.board.view.cell_size, "fixture": app.session.definition.id, "crop": crop,
		"row_clue_steps": nonzero_steps(app.board.row_clue_steps), "column_clue_steps": nonzero_steps(app.board.column_clue_steps),
		"longest_row_window": [row_window.start, row_window.end, row_window.prefix_hidden, row_window.suffix_hidden],
		"longest_column_window": [column_window.start, column_window.end, column_window.prefix_hidden, column_window.suffix_hidden]})

func nonzero_steps(steps: Array[int]) -> Dictionary:
	var result: Dictionary = {}
	for index: int in range(steps.size()):
		if steps[index] != 0:
			result[str(index + 1)] = steps[index]
	return result

func longest_line(lines: Array) -> int:
	var result: int = 0
	for i: int in range(1, lines.size()):
		if lines[i].size() > lines[result].size():
			result = i
	return result

func set_fractional_step(app: Main, axis: String, index: int, fraction: float) -> void:
	var maximum: int = int(app.board.clue_layout(axis, index).max_offset)
	app.board.set_clue_step(axis, index, roundi(float(maximum) * fraction))

func replace_render_cells(app: Main, values: Array[int]) -> void:
	var view_state: Dictionary = app.board.capture_view()
	var fresh: Session = Session.new(app.session.definition)
	var changes: Array[Dictionary] = []
	for index: int in range(values.size()):
		if values[index] != -1:
			changes.append({"index": index, "before": -1, "after": values[index]})
	if not changes.is_empty():
		fresh.player.commit(changes)
	fresh.completed = fresh.is_solution()
	fresh.view_state = view_state
	var slot: int = app.sessions.find(app.session)
	app.sessions[slot] = fresh
	app.session = fresh
	app.board.session = fresh
	app.board.restore_view(view_state)

func edge_cell(app: Main, edge: String) -> Vector2i:
	var grid: Rect2 = app.board.view.visible_bounds()
	var first: Vector2i = Vector2i(((grid.position - app.board.view.origin) / app.board.view.cell_size).floor()).max(Vector2i.ZERO)
	var last: Vector2i = Vector2i(((grid.end - app.board.view.origin) / app.board.view.cell_size).ceil()).min(app.board.view.dimensions) - Vector2i.ONE
	var middle: Vector2i = (first + last) / 2
	match edge:
		"left": return Vector2i(first.x, middle.y)
		"right": return Vector2i(last.x, middle.y)
		"top": return Vector2i(middle.x, first.y)
		"bottom": return Vector2i(middle.x, last.y)
	return first

func x_crosses_view(app: Main, cell: Vector2i) -> bool:
	var box: Rect2 = app.board.view.cell_rect(cell)
	if not box.intersects(app.board.view.viewport) or app.board.view.viewport.encloses(box):
		return false
	for endpoints: Array in [[box.position + box.size * 0.3, box.position + box.size * 0.7], [box.position + box.size * Vector2(0.7, 0.3), box.position + box.size * Vector2(0.3, 0.7)]]:
		var segment: PackedVector2Array = Board.clipped_segment(endpoints[0], endpoints[1], app.board.view.viewport.grow(-0.65))
		if segment.size() == 2 and segment[0].distance_to(segment[1]) >= 3.0:
			return true
	return false

func capture_x_edges(app: Main) -> void:
	for pitch: float in [24.0, 36.0]:
		app.board.view.zoom_to(pitch, app.board.view.viewport.get_center())
		for edge: String in ["top", "bottom", "left", "right", "corner"]:
			var found: bool = false
			for xi: int in range(10):
				for yi: int in range(10):
					app.board.view.center = Vector2(49.1 + xi * 0.1, 49.1 + yi * 0.1)
					app.board.view.reframe()
					x_test_cell = edge_cell(app, edge)
					var corner_box: Rect2 = app.board.view.cell_rect(x_test_cell)
					var corner_cut: bool = edge != "corner" or (corner_box.position.x < app.board.view.viewport.position.x and corner_box.position.y < app.board.view.viewport.position.y)
					if corner_cut and x_crosses_view(app, x_test_cell):
						found = true
						break
				if found:
					break
			if not found:
				push_error("Cannot position partial X at " + edge)
				quit(5)
				return
			var values: Array[int] = app.session.player.cells.duplicate()
			values.fill(-1)
			values[x_test_cell.y * app.session.player.width + x_test_cell.x] = 0
			replace_render_cells(app, values)
			app.board.hover = Vector2i(-1, -1)
			await snapshot(app, "x-clip-%d-%s-confirmed" % [roundi(pitch), edge])
			values[x_test_cell.y * app.session.player.width + x_test_cell.x] = -1
			replace_render_cells(app, values)
			app.session.gesture.begin(app.session.player, x_test_cell, 0)
			await snapshot(app, "x-clip-%d-%s-preview" % [roundi(pitch), edge])
			app.session.gesture.cancel()

func region_difference(before: Image, after: Image, region: Rect2i) -> int:
	var differences: int = 0
	for y: int in range(region.position.y, region.end.y):
		for x: int in range(region.position.x, region.end.x):
			if not before.get_pixel(x, y).is_equal_approx(after.get_pixel(x, y)):
				differences += 1
	return differences

func capture_hint_markers(app: Main, row: int, column: int) -> void:
	app.board.clear_clue_hover()
	app.board.hover = Vector2i(-1, -1)
	app.board.navigate_to(Vector2(float(column) / 100.0, float(row) / 100.0))
	for axis: String in ["row", "column"]:
		var index: int = row if axis == "row" else column
		var maximum: int = int(app.board.clue_layout(axis, index).max_offset)
		var pitch: float = float(app.board.clue_layout(axis, index).slot_extent)
		for anchor: int in [0, int(float(maximum) / 2.0), maximum]:
			app.board.set_clue_step(axis, index, anchor)
			app.board.pan_button = MOUSE_BUTTON_MIDDLE
			app.board.pan_target = axis
			app.board.pan_line_index = index
			var direction: float = -1.0 if anchor == maximum else 1.0
			var previous: Image
			for fraction: float in [0.0, 0.49, 0.51, 1.49, 1.51]:
				app.board.pan_drag_distance = direction * pitch * fraction
				var name: String = "hint-marker-%s-%d-%d-%d" % [axis, index, anchor, roundi(fraction * 100)]
				await snapshot(app, name)
				if not FileAccess.file_exists(output.path_join(name + ".png")):
					return
				var current: Image = Image.load_from_file(output.path_join(name + ".png"))
				if previous != null and roundi(fraction * 100) in [51, 151]:
					var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
					var line: Vector2 = app.board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
					var region: Rect2i = Rect2i(Rect2(app.board.global_position + (Vector2(area.position.x, line.y - 9) if axis == "row" else Vector2(line.x - 9, area.position.y)),
						Vector2(area.size.x, 18) if axis == "row" else Vector2(18, area.size.y))).intersection(Rect2i(Vector2i.ZERO, surface.size))
					if region_difference(previous, current, region) > 300:
						push_error("Rendered hint numbers snapped before drop: " + name)
						quit(5)
						return
					pixel_checks += 1
				previous = current
			app.board.cancel_gesture()
	app.board.reset_clue_pan()

func visible_token_centers(app: Main, axis: String, index: int) -> Dictionary:
	var result: Dictionary = {}
	for unit: Dictionary in app.board.visual_hint_units(axis, index).units:
		if unit.kind == "token":
			result[int(unit.index)] = float(unit.center)
	return result

func token_pixels(image_file: String, app: Main, axis: String, index: int, centers: Dictionary) -> bool:
	var picture: Image = Image.load_from_file(output.path_join(image_file + ".png"))
	var layout: Dictionary = app.board.clue_layout(axis, index)
	var line: Vector2 = app.board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
	for token: int in centers:
		var position: Vector2 = app.board.global_position + (Vector2(float(centers[token]), line.y) if axis == "row" else Vector2(line.x, float(centers[token])))
		var region: Rect2i = Rect2i(Rect2(position - Vector2(12, 10), Vector2(24, 20))).intersection(Rect2i(Vector2i.ZERO, picture.get_size()))
		var ink: Color = Color(layout.entries[token].color)
		var found: bool = false
		for y: int in range(region.position.y, region.end.y):
			for x: int in range(region.position.x, region.end.x):
				var pixel: Color = picture.get_pixel(x, y)
				if absf(pixel.r - ink.r) + absf(pixel.g - ink.g) + absf(pixel.b - ink.b) < 0.06:
					found = true
					break
			if found:
				break
		if not found:
			return false
		pixel_checks += 1
	return true

func capture_drop_snap(app: Main, axis: String, index: int, anchor: int, fraction: float, name: String) -> void:
	app.board.set_clue_step(axis, index, anchor)
	var pitch: float = float(app.board.clue_layout(axis, index).slot_extent)
	var point: Vector2 = preload("res://tests/p12_cases.gd").clue_point(app.board, axis, index)
	var delta: Vector2 = Vector2(fraction * pitch, 0) if axis == "row" else Vector2(0, fraction * pitch)
	var press: InputEventMouseButton = InputEventMouseButton.new()
	press.button_index = MOUSE_BUTTON_MIDDLE
	press.button_mask = MOUSE_BUTTON_MASK_MIDDLE
	press.pressed = true
	press.position = point
	press.global_position = point
	surface.push_input(press, true)
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.button_mask = MOUSE_BUTTON_MASK_MIDDLE
	motion.position = point + delta
	motion.global_position = motion.position
	surface.push_input(motion, true)
	var before: Dictionary = visible_token_centers(app, axis, index)
	var before_units: Dictionary = app.board.visual_hint_units(axis, index)
	await snapshot(app, name + "-before-mouse-up")
	var release: InputEventMouseButton = InputEventMouseButton.new()
	release.button_index = MOUSE_BUTTON_MIDDLE
	release.pressed = false
	release.position = point + delta
	release.global_position = release.position
	surface.push_input(release, true)
	var after: Dictionary = visible_token_centers(app, axis, index)
	await snapshot(app, name + "-after-mouse-up")
	if not token_pixels(name + "-before-mouse-up", app, axis, index, before) or not token_pixels(name + "-after-mouse-up", app, axis, index, after):
		push_error("Rendered snap token absent: " + name)
		quit(5)
		return
	var before_capture: Dictionary = captures[-2]
	before_capture.token_centers = before
	before_capture.pointer_delta = [delta.x, delta.y]
	before_capture.hint_units = before_units
	var after_capture: Dictionary = captures[-1]
	after_capture.token_centers = after
	after_capture.hint_units = app.board.visual_hint_units(axis, index)
	var distance: Dictionary = preload("res://tests/p12_cases.gd").coordinate_distance(before, after)
	if distance.count == 0 or distance.largest > pitch * 0.5 + 0.001:
		push_error("Rendered snap moved shared tokens more than half a slot: " + name)
		quit(5)
		return
	if name == "snap-f02-row12-owner":
		var layout: Dictionary = app.board.clue_layout(axis, index)
		var owner_snapped: bool = false
		if before.has(0) and after.has(0):
			var nearest: int = roundi((float(before[0]) - app.board.clue_slot_origin(axis, app.board.row_clue_area(), layout)) / pitch - 0.5)
			owner_snapped = is_equal_approx(float(after[0]), app.board.clue_slot_center(axis, app.board.row_clue_area(), layout, nearest))
		if not owner_snapped or absf(float(before.get(0, -1)) - 51.2) > 0.001 or absf(float(after.get(0, -1)) - 56.0) > 0.001:
			push_error("Rendered F-02 row 12 token 4 missed its nearest slot")
			quit(5)
			return
		pixel_checks += 1

func capture_drop_matrix(app: Main, row: int, column: int) -> void:
	app.board.navigate_to(Vector2(float(column) / 100.0, float(row) / 100.0))
	for axis: String in ["row", "column"]:
		var index: int = row if axis == "row" else column
		var maximum: int = int(app.board.clue_layout(axis, index).max_offset)
		for anchor: int in [0, maximum / 2, maximum]:
			var direction: float = -1.0 if anchor == maximum else 1.0
			for fraction: float in [0.49, 0.51, 1.8]:
				await capture_drop_snap(app, axis, index, anchor, direction * fraction,
					"snap-%s-%d-%d-%d" % [axis, index, anchor, roundi(direction * fraction * 100)])
		await capture_drop_snap(app, axis, index, maximum / 2, -1.8, "snap-%s-%d-middle-reverse" % [axis, index])
	app.board.reset_clue_pan()

func capture_owner_drop(app: Main) -> void:
	surface.size = Vector2i(1280, 720)
	app.size = Vector2(surface.size)
	app.set_ui_scale(1.0)
	await process_frame
	await process_frame
	app.select_puzzle(1)
	await process_frame
	await process_frame
	app.board._layout()
	app.board.view.zoom_to(36.0, app.board.view.viewport.get_center())
	var original_viewport: Rect2 = app.board.view.viewport
	app.board.view.configure(Rect2(Vector2(174, original_viewport.position.y), Vector2(original_viewport.end.x - 174, original_viewport.size.y)), app.board.view.dimensions)
	app.board.normalize_clue_steps()
	app.board.navigate_to(Vector2(0.5, 11.0 / 40.0))
	if app.board.clue_capacity("row") != 6:
		push_error("F-02 owner render requires six actual row slots")
		quit(5)
		return
	await capture_drop_snap(app, "row", 11, 0, 1.8, "snap-f02-row12-owner")
	var row_maximum: int = int(app.board.clue_layout("row", 11).max_offset)
	if app.board.clue_step("row", 11) != row_maximum or app.board.row_clue_reads[11].anchor != "outer_start":
		push_error("V-01 owner render did not reach the direct outer stop")
		quit(5)
		return
	await capture_drop_snap(app, "row", 11, row_maximum, 1.0, "variant-a-owner-outer-clamp")
	await capture_monotone_route(app, "row", 11)
	var old_viewport: Rect2 = app.board.view.viewport
	app.board.view.configure(Rect2(Vector2(old_viewport.position.x, 105), Vector2(old_viewport.size.x, old_viewport.end.y - 105)), app.board.view.dimensions)
	app.board.normalize_clue_steps()
	var column_index: int = 11
	app.board.navigate_to(Vector2(float(column_index) / 40.0, 11.0 / 40.0))
	if app.board.clue_capacity("column") != 4 or app.session.definition.columns[column_index].size() != 5:
		push_error("V-02 column render requires four actual slots and five tokens")
		quit(5)
		return
	await capture_monotone_route(app, "column", column_index)
	app.board.view.configure(old_viewport, app.board.view.dimensions)
	app.board.normalize_clue_steps()
	var long_column: int = 20
	app.board.navigate_to(Vector2(float(long_column) / 40.0, 11.0 / 40.0))
	if app.board.clue_capacity("column") != 5 or app.session.definition.columns[long_column].size() != 11:
		push_error("V-03 long column render requires five actual slots and eleven tokens")
		quit(5)
		return
	await capture_monotone_route(app, "column", long_column)

func capture_monotone_route(app: Main, axis: String, index: int) -> void:
	app.board.set_clue_step(axis, index, 0)
	var maximum: int = int(app.board.clue_layout(axis, index).max_offset)
	for direction: int in [1, -1]:
		var seen: Dictionary = visible_token_centers(app, axis, index)
		var target: int = maximum if direction == 1 else 0
		for step: int in range(maximum + 1):
			var origin: int = app.board.clue_step(axis, index)
			if origin == target:
				break
			await capture_drop_snap(app, axis, index, origin, float(direction), "variant-a-%s-%d-dir%d-step%d" % [axis, index, direction, step])
			seen.merge(visible_token_centers(app, axis, index))
			if (app.board.clue_step(axis, index) - origin) * direction <= 0:
				push_error("V-02 rendered same-sign route did not progress")
				quit(5)
				return
		if app.board.clue_step(axis, index) != target or seen.size() != app.board.clue_entry_count(axis, index):
			push_error("V-03 rendered route did not reach every token")
			quit(5)
			return
		var stop: Dictionary = visible_token_centers(app, axis, index)
		await capture_drop_snap(app, axis, index, target, float(direction), "variant-a-%s-%d-dir%d-clamp" % [axis, index, direction])
		if stop != visible_token_centers(app, axis, index) or stop != captures[-2].token_centers:
			push_error("V-02 rendered outer/grid clamp moved tokens")
			quit(5)
			return

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	var app: Main = load("res://main.tscn").instantiate()
	surface.add_child(app)
	await snapshot(app, "album")
	for dims: Vector2i in [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]:
		surface.size = dims
		for scale: float in [1.0, 1.25]:
			app.set_ui_scale(scale)
			for fixture: int in range(3):
				app.select_puzzle(fixture)
				if scale > 1:
					app.board.zoom(1, app.board.view.viewport.get_center())
				var values: Array[int] = app.session.player.cells.duplicate()
				for i: int in range(4):
					values[(4 + i) * app.session.player.width + 4] = mini(i + 1, app.session.definition.palette.size())
				replace_render_cells(app, values)
				app.board.hover = Vector2i(4, 4)
				await snapshot(app, "%dx%d-ui%d-f%d" % [dims.x, dims.y, roundi(scale * 100), fixture + 1])
			app.select_puzzle(1)
			set_fractional_step(app, "row", 35, 0.5)
			set_fractional_step(app, "row", 36, 1.0)
			set_fractional_step(app, "column", 21, 0.5)
			set_fractional_step(app, "column", 22, 1.0)
			await snapshot(app, "%dx%d-ui%d-f2-independent-slots" % [dims.x, dims.y, roundi(scale * 100)])
			app.select_puzzle(2)
			set_fractional_step(app, "row", 50, 0.35)
			set_fractional_step(app, "row", 51, 0.7)
			set_fractional_step(app, "column", 50, 0.35)
			set_fractional_step(app, "column", 51, 0.7)
			await snapshot(app, "%dx%d-ui%d-f3-independent-slots" % [dims.x, dims.y, roundi(scale * 100)])
	# D-18/D-19: unnumbered colored numbers remain single-line in shared slots.
	# D-20 adds independent snapped positions for every concrete row and column.
	surface.size = Vector2i(1920, 1080)
	app.set_ui_scale(1)
	app.select_puzzle(1)
	app.board.hover = Vector2i(10, 10)
	await snapshot(app, "f02-colored-hints-default")
	for step: float in [22.0, 24.0]:
		app.board.view.zoom_to(step, app.board.view.viewport.get_center())
		for position: float in [0.0, 0.5, 1.0]:
			set_fractional_step(app, "row", 35, position)
			set_fractional_step(app, "column", 21, position)
			await snapshot(app, "f02-hints-%d-%s" % [roundi(step), ["end", "middle", "start"][roundi(position * 2.0)]])
	app.board.view.zoom_to(12.0, app.board.view.viewport.get_center())
	set_fractional_step(app, "row", 35, 0.5)
	set_fractional_step(app, "row", 36, 1.0)
	set_fractional_step(app, "column", 21, 0.5)
	set_fractional_step(app, "column", 22, 1.0)
	await snapshot(app, "f02-hints-50-independent-middle")
	app.board.view.zoom_to(24.0, app.board.view.viewport.get_center())
	app.board.reset_clue_pan()
	set_fractional_step(app, "row", 35, 1.0)
	await snapshot(app, "f02-row-start-column-end")
	app.board.reset_clue_pan()
	set_fractional_step(app, "column", 21, 1.0)
	await snapshot(app, "f02-row-end-column-start")
	app.select_puzzle(2)
	var f03_row: int = longest_line(app.session.definition.rows)
	var f03_column: int = longest_line(app.session.definition.columns)
	app.board.hover = Vector2i(f03_column, f03_row)
	app.board.set_clue_hover("row", f03_row)
	await snapshot(app, "f03-overflow-hover-tooltip")
	app.board.clear_clue_hover()
	for step: float in [12.0, 18.0, 22.0, 24.0]:
		app.board.view.zoom_to(step, app.board.view.viewport.get_center())
		app.board.reset_clue_pan()
		await snapshot(app, "f03-hints-work-%d-end" % roundi(step / 24.0 * 100.0))
	for step: float in [12.0, 24.0]:
		app.board.view.zoom_to(step, app.board.view.viewport.get_center())
		for position: float in [0.5, 1.0]:
			set_fractional_step(app, "row", f03_row, position)
			set_fractional_step(app, "column", f03_column, position)
			await snapshot(app, "f03-hints-work-%d-%s" % [roundi(step / 24.0 * 100.0), "middle" if position == 0.5 else "start"])
	app.board.view.zoom_to(24.0, app.board.view.viewport.get_center())
	set_fractional_step(app, "row", f03_row, 0.45)
	set_fractional_step(app, "column", f03_column, 0.65)
	app.board.view.pan(Vector2(120, 80))
	app.board.navigate_to(Vector2(0.78, 0.22))
	await snapshot(app, "f03-hints-after-raster-pan")
	# Same L/block at normal and five-cell boundaries, every color/work step.
	for fixture: int in [0, 1]:
		app.select_puzzle(fixture)
		var values: Array[int] = app.session.player.cells.duplicate()
		values.fill(-1)
		for i: int in range(app.session.definition.palette.size()):
			var x: int = 2 + i * 2
			for cell: Vector2i in [Vector2i(x, 4), Vector2i(x+1, 4), Vector2i(x, 5), Vector2i(x, 7), Vector2i(x+1, 7), Vector2i(x+1, 8)]:
				values[cell.y * app.session.player.width + cell.x] = i + 1
		replace_render_cells(app, values)
		app.board.hover = Vector2i(-1, -1)
		for step: float in app.board.WORK_STEPS:
			app.board.view.zoom_to(step, app.board.view.viewport.get_center())
			app.board.navigate_to(Vector2.ZERO)
			await snapshot(app, "separation-f%d-%d-confirmed" % [fixture + 1, roundi(step)], true)
			# Preview whole mixed-color removal: original values outside endpoint survive.
			app.session.gesture.begin(app.session.player, Vector2i(2, 4), 1)
			app.session.gesture.move(Vector2i(10, 4))
			await snapshot(app, "separation-f%d-%d-removal" % [fixture + 1, roundi(step)], true)
			app.session.gesture.cancel()
			for color: int in range(1, app.session.definition.palette.size() + 1):
				app.session.gesture.begin(app.session.player, Vector2i(2, 3), color)
				app.session.gesture.move(Vector2i(10, 3))
				await snapshot(app, "separation-f%d-%d-preview-color%d" % [fixture + 1, roundi(step), color], true)
				app.session.gesture.cancel()
	app.select_puzzle(2)
	app.board.view.zoom_to(24.0, app.board.view.viewport.get_center())
	app.board.view.center = Vector2(50, 50)
	app.board.view.reframe()
	app.board.hover = app.board.view.hit(app.board.view.viewport.get_center())
	await snapshot(app, "f03-grid-focus")
	app.board.hover = Vector2i(-1, -1)
	await capture_x_edges(app)
	app.board.view.zoom_to(24.0, app.board.view.viewport.get_center())
	app.board.navigate_to(Vector2(0.5, float(f03_row) / 100.0))
	app.board.reset_clue_pan()
	await snapshot(app, "hint-drag-before")
	var before_drag: Image = Image.load_from_file(output.path_join("hint-drag-before.png"))
	app.board.pan_button = MOUSE_BUTTON_MIDDLE
	app.board.pan_target = "row"
	app.board.pan_line_index = f03_row
	app.board.pan_drag_distance = float(app.board.clue_layout("row", f03_row).slot_extent) * 0.42
	await snapshot(app, "hint-drag-subslot")
	var after_drag: Image = Image.load_from_file(output.path_join("hint-drag-subslot.png"))
	var row_rect: Rect2 = app.board.row_clue_area()
	var row_y: float = app.board.view.cell_rect(Vector2i(0, f03_row)).get_center().y
	var target_region: Rect2i = Rect2i(Rect2(app.board.global_position + Vector2(row_rect.position.x, row_y - 9), Vector2(row_rect.size.x, 18)))
	var neighbour_y: float = row_y + app.board.view.cell_size
	var neighbour_region: Rect2i = Rect2i(Rect2(app.board.global_position + Vector2(row_rect.position.x, neighbour_y - 9), Vector2(row_rect.size.x, 18)))
	if region_difference(before_drag, after_drag, target_region) < 5 or region_difference(before_drag, after_drag, neighbour_region) != 0 or app.board.clue_step("row", f03_row) != 0:
		push_error("Rendered subslot hint drag did not move continuously")
		quit(5)
		return
	pixel_checks += 1
	var pitch: float = float(app.board.clue_layout("row", f03_row).slot_extent)
	app.board.pan_drag_distance = pitch * 0.49
	await snapshot(app, "hint-drag-before-slot-boundary")
	var before_boundary: Image = Image.load_from_file(output.path_join("hint-drag-before-slot-boundary.png"))
	app.board.pan_drag_distance = pitch * 0.51
	await snapshot(app, "hint-drag-after-slot-boundary")
	var after_boundary: Image = Image.load_from_file(output.path_join("hint-drag-after-slot-boundary.png"))
	if region_difference(before_boundary, after_boundary, target_region) > 300 or region_difference(before_boundary, after_boundary, neighbour_region) != 0:
		push_error("Rendered row hint jumped at a slot boundary")
		quit(5)
		return
	pixel_checks += 2
	app.board.cancel_gesture()
	app.board.navigate_to(Vector2(float(f03_column) / 100.0, float(f03_row) / 100.0))
	app.board.pan_button = MOUSE_BUTTON_MIDDLE
	app.board.pan_target = "column"
	app.board.pan_line_index = f03_column
	var column_pitch: float = float(app.board.clue_layout("column", f03_column).slot_extent)
	app.board.pan_drag_distance = column_pitch * 0.49
	await snapshot(app, "hint-drag-column-before-slot-boundary")
	var column_before_boundary: Image = Image.load_from_file(output.path_join("hint-drag-column-before-slot-boundary.png"))
	app.board.pan_drag_distance = column_pitch * 0.51
	await snapshot(app, "hint-drag-column-after-slot-boundary")
	var column_after_boundary: Image = Image.load_from_file(output.path_join("hint-drag-column-after-slot-boundary.png"))
	var column_area: Rect2 = app.board.column_clue_area()
	var column_x: float = app.board.view.cell_rect(Vector2i(f03_column, 0)).get_center().x
	var column_region: Rect2i = Rect2i(Rect2(app.board.global_position + Vector2(column_x - 9, column_area.position.y), Vector2(18, column_area.size.y))).intersection(Rect2i(Vector2i.ZERO, surface.size))
	if region_difference(column_before_boundary, column_after_boundary, column_region) > 300 or app.board.clue_step("column", f03_column) != 0:
		push_error("Rendered column hint jumped at a slot boundary")
		quit(5)
		return
	pixel_checks += 1
	app.board.cancel_gesture()
	await capture_hint_markers(app, f03_row, f03_column)
	await capture_drop_matrix(app, f03_row, f03_column)
	var gesture_start: Vector2i = app.board.view.hit(app.board.view.viewport.get_center())
	app.board.pointer_press(app.board.view.cell_rect(gesture_start).get_center(), MOUSE_BUTTON_RIGHT)
	app.board.pointer_move(app.board.view.cell_rect(gesture_start + Vector2i(7, 0)).get_center(), true)
	if app.board.gesture_length() != 8:
		push_error("Rendered gesture counter has wrong value")
		quit(5)
		return
	await snapshot(app, "gesture-counter-8")
	app.board.cancel_gesture()
	app.board.hover = Vector2i(f03_column, f03_row)
	app.board.set_clue_hover("row", f03_row)
	await snapshot(app, "f03-full-clues-in-work-tooltip")
	app.board.clear_clue_hover()
	app.board.fit_all()
	await snapshot(app, "f03-overview")
	await capture_owner_drop(app)
	for index: int in [0, 1, 2]:
		app.select_puzzle(index)
		var values: Array[int] = app.session.player.cells.duplicate()
		values.fill(-1)
		for y: int in range(app.session.player.height):
			for x: int in range(app.session.player.width):
				var value: int = int(app.session.definition.solution[y][x])
				if value > 0:
					values[y * app.session.player.width + x] = value
		replace_render_cells(app, values)
		await snapshot(app, "f%d-reveal" % (index + 1))
		app.show_album()
		await snapshot(app, "f%d-earned-album" % (index + 1))
	var report: FileAccess = FileAccess.open(output.path_join("render-report.json"), FileAccess.WRITE)
	report.store_string(JSON.stringify({"renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(), "pixel_checks": pixel_checks, "clue_contract": "single-line colored numbers; shared fixed slots; exact prefix/suffix markers; snapped per-line panning; complete hover tooltip", "physical_dpi_acceptance": "OPEN: owner", "captures": captures}, "  ") + "\n")
	print("P1_CAPTURE_OK: %d actual rendered images" % captures.size())
	quit(0)
