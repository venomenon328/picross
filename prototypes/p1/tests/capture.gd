extends SceneTree
## Real GPU/software-rendered offscreen surfaces; not a physical DPI claim.
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
const PencilMarks = preload("res://ui/pencil_marks.gd")
# Same subpixel motion oracle, scaled for the selected 1.35x clue ink area.
# Whole-slot jumps remain far above this bound; untouched neighbour stays exact.
const CLUE_MOTION_PIXEL_BUDGET: int = 550
const COMPACT_WORK_STEPS: Array[float] = [12.0, 16.0, 18.0, 22.0, 24.0, 72.0]
# Review images are independent of assertion coverage. Failure frames are
# always retained uncropped, including the preceding comparison images.
const COMPACT_PICTURES: Array[String] = [
	"1280x720-ui125-f2-independent-slots", "1920x1080-ui100-f1",
	"separation-f1-24-confirmed", "separation-f2-24-confirmed", "f2-reveal",
]
var surface: SubViewport
var output: String
var captures: Array = []
var frames: Array = []
var recent_frames: Array = []
var failure_captures: Array = []
var compact: bool = false
var failed: bool = false
var failure_message: String = ""
var pixel_checks: int = 0
var x_test_cell: Vector2i = Vector2i(-1, -1)

func _initialize() -> void:
	compact = OS.get_cmdline_user_args().has("--ci-compact")
	var temporary: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if temporary.is_empty():
		temporary = OS.get_environment("TEMP") if OS.has_feature("windows") else OS.get_environment("TMPDIR")
	if temporary.is_empty():
		temporary = "/tmp"
	SaveStore.test_root_override = temporary.path_join("picross-p1-capture-%d" % Time.get_ticks_usec())
	call_deferred("run")

func write_report() -> void:
	if output.is_empty():
		return
	var stage: String = OS.get_environment("P1_RENDER_STAGE")
	var report: FileAccess = FileAccess.open(output.path_join("render-report" + ("-"+stage if not stage.is_empty() else "") + ".json"), FileAccess.WRITE)
	if report == null:
		failed = true
		failure_message = "Cannot write native capture report"
		push_error("Cannot write native capture report")
		quit(4)
		return
	report.store_string(JSON.stringify({"renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(),
		"compact": compact, "failed": failed, "failure": failure_message, "pixel_checks": pixel_checks,
		"rendered_count": frames.size(), "retained_count": captures.size() + failure_captures.size(),
		"clue_contract": "single-line colored numbers; shared fixed slots; exact prefix/suffix markers; snapped per-line panning; complete hover tooltip",
		"physical_dpi_acceptance": "OPEN: owner", "captures": captures, "frames": frames, "failure_captures": failure_captures}, "  ") + "\n")

func fail_capture(message: String, code: int = 5) -> void:
	if failed:
		return
	failed = true
	failure_message = message
	push_error(message)
	for frame: Dictionary in recent_frames:
		for kind: String in ["picture", "material"]:
			var picture: Image = frame.get(kind)
			if picture == null:
				continue
			var name: String = "failure-" + str(frame.name) + ("-underlay" if kind == "material" else "") + ".png"
			if picture.save_png(output.path_join(name)) == OK:
				failure_captures.append({"file": name, "frame": frame.name, "kind": kind, "crop": false})
	write_report()
	quit(code)

func fill_patch_region(box: Rect2) -> Rect2i:
	# Independent clear interior, away from the outline and paper moat.
	var margin: float = maxf(minf(4.0,box.size.x*0.3),box.size.x*0.18)
	var a: Vector2i = Vector2i(ceilf(box.position.x+margin),ceilf(box.position.y+margin))
	var b: Vector2i = Vector2i(floorf(box.end.x-margin),floorf(box.end.y-margin))
	return Rect2i(a,b-a)

func fill_patch(picture: Image, material: Image, box: Rect2, palette: Color, alpha: float, band: bool = false) -> Dictionary:
	# V3 moves the light traces. Do not require one formerly blank coordinate
	# to stay blank: retain real palette pixels across at least 1/4 of the core,
	# and bound EVERY other core pixel by the existing 12%-white texture budget.
	var region: Rect2i = fill_patch_region(box)
	var pure: int = 0
	var total: int = 0
	var bounded: bool = true
	var first_bad: Dictionary = {}
	for y: int in range(region.position.y,region.end.y):
		for x: int in range(region.position.x,region.end.x):
			var base: Color = Color("e8e9d9") if band else material.get_pixel(x,y)
			base = base.blend(Color(palette,alpha))
			var actual: Color = picture.get_pixel(x,y)
			var delta: Vector3 = Vector3(actual.r-base.r,actual.g-base.g,actual.b-base.b)
			var within: bool = minf(delta.x,minf(delta.y,delta.z)) >= -0.005 and delta.length() <= alpha*0.13*sqrt(3.0)
			if not within and first_bad.is_empty(): first_bad={"pixel":[x,y],"actual":str(actual),"base":str(base)}
			bounded = bounded and within
			pure += int(actual.is_equal_approx(base) if alpha==1.0 else close_color(actual,base))
			total += 1
	return {"valid":bounded and total>0 and pure>=total*0.25,"bounded":bounded,"pure":pure,"total":total,"first_bad":first_bad}

func snapshot(app: Main, name: String, crop: bool = false) -> Image:
	var material: Image
	if name.begins_with("x-clip-") or name.contains("preview-color"):
		# Complete pending board redraws before hiding its separate ink layer.
		app.refresh()
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		app.board.marks.hide()
		await process_frame
		await RenderingServer.frame_post_draw
		material = surface.get_texture().get_image()
		app.board.marks.show()
	if (name.begins_with("separation-") and name.ends_with("-confirmed")) or name == "f03-grid-focus" or name.begins_with("hint-marker-"):
		app.board.hide()
		await process_frame
		await RenderingServer.frame_post_draw
		material = surface.get_texture().get_image()
		app.board.show()
	app.refresh()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var picture: Image = surface.get_texture().get_image()
	var record: Dictionary = {"name": name, "logical_surface": [surface.size.x, surface.size.y], "ui_scale": app.ui_scale,
		"cell_pitch": app.board.view.cell_size, "fixture": app.session.definition.id, "retained": false, "crop": false}
	frames.append(record)
	recent_frames.append({"name": name, "picture": picture, "material": material})
	if recent_frames.size() > 3:
		recent_frames.pop_front()
	if name.begins_with("separation-") and name.ends_with("-confirmed"):
		for i: int in range(app.session.definition.palette.size()):
			var cell: Rect2 = app.board.view.cell_rect(Vector2i(2 + i * 2, 4))
			var moat: Vector2i = Vector2i(app.board.global_position + cell.position + Vector2(1, cell.size.y / 2))
			var original: Color = Color(app.session.definition.palette[i].color)
			cell.position+=app.board.global_position
			var patch: Dictionary = fill_patch(picture,material,cell,original,1.0)
			if not patch.valid or not picture.get_pixelv(moat).is_equal_approx(material.get_pixelv(moat)):
				fail_capture("Rendered fill/moat regression: %s patch=%s moat=%s paper=%s expected=%s" % [name,patch,picture.get_pixelv(moat),material.get_pixelv(moat),original], 5)
				return picture
			pixel_checks += 3
			if name=="separation-f1-24-confirmed":
				for color: Color in [original.lightened(0.08),Color.WHITE]:
					var wrong: Image = picture.duplicate()
					wrong.fill_rect(fill_patch_region(cell),color)
					if fill_patch(wrong,material,cell,original,1.0).valid:
						fail_capture("V3 fill oracle accepted uniform whitening/missing palette",5)
						return picture
					pixel_checks += 1
	if name.contains("preview-color"):
		var color_index: int = int(name.get_slice("preview-color", 1))
		var preview_cell: Rect2 = app.board.view.cell_rect(Vector2i(2, 3))
		var preview_center: Vector2i = Vector2i(app.board.global_position + preview_cell.position + preview_cell.size * Vector2(0.5, 0.38))
		var preview_moat: Vector2i = Vector2i(app.board.global_position + preview_cell.position + Vector2(1, preview_cell.size.y / 2))
		var gap: Color = picture.get_pixelv(preview_moat)
		# Paper varies spatially, so measure it at this exact pixel with marks
		# hidden. The active band, when present, is the flat moat color.
		var underlay: Color = gap if gap.is_equal_approx(Color("e8e9d9")) else material.get_pixelv(preview_center)
		var expected_fill: Color = underlay.blend(Color(Color(app.session.definition.palette[color_index - 1].color), 0.56))
		preview_cell.position+=app.board.global_position
		var patch: Dictionary = fill_patch(picture,material,preview_cell,Color(app.session.definition.palette[color_index - 1].color),0.56,gap.is_equal_approx(Color("e8e9d9")))
		if not patch.valid or absf(gap.r - expected_fill.r) + absf(gap.g - expected_fill.g) + absf(gap.b - expected_fill.b) < 0.1:
			fail_capture("Rendered preview fill/moat regression: %s patch=%s expected=%s gap=%s" % [name,patch,expected_fill,gap], 5)
			return picture
		pixel_checks += 2
	if name == "f03-grid-focus":
		var focus: Vector2i = app.board.hover
		var row_point: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus + Vector2i(2, 0)).get_center())
		var column_point: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus + Vector2i(0, 2)).get_center())
		var intersection: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus).get_center())
		var outside: Vector2i = Vector2i(app.board.global_position + app.board.view.cell_rect(focus + Vector2i(2, 2)).get_center())
		var band: Color = Color("e8e9d9")
		if not picture.get_pixelv(row_point).is_equal_approx(band) or not picture.get_pixelv(column_point).is_equal_approx(band) or not picture.get_pixelv(intersection).is_equal_approx(band) or not picture.get_pixelv(outside).is_equal_approx(material.get_pixelv(outside)):
			fail_capture("Rendered grid focus regression", 5)
			return picture
		pixel_checks += 4
	if name.begins_with("x-clip-"):
		var cell_box: Rect2 = app.board.view.cell_rect(x_test_cell)
		cell_box.position += app.board.global_position
		var viewport: Rect2 = app.board.view.viewport
		viewport.position += app.board.global_position
		var pixels: int = 0
		# Independent image oracle: visible curved ink, and no ink outside the
		# viewport. It does not reuse the renderer's Bezier/path calculation.
		var region: Rect2i = Rect2i(cell_box.grow(2)).intersection(Rect2i(Vector2i.ZERO, picture.get_size()))
		for y: int in range(region.position.y, region.end.y):
			for x: int in range(region.position.x, region.end.x):
				var delta: float = material.get_pixel(x, y).r - picture.get_pixel(x, y).r
				if delta > 2.0/255 and not viewport.has_point(Vector2(x, y) + Vector2(0.5, 0.5)):
					fail_capture("Rendered X escaped viewport: %s point=%s clip=%s delta=%s" % [name,Vector2i(x,y),viewport,delta], 5)
					return picture
				# Preview active bands are lighter than this threshold; only ink
				# counts as a visible clipped X.
				if delta > 0.12:
					pixels += 1
		if pixels < 3:
			fail_capture("Rendered clipped X absent: " + name, 5)
			return picture
		pixel_checks += 1
	if name == "gesture-counter-8" or name.begins_with("g1-counter-"):
		var font: Font = Board.BODY_FONT
		var fs: int = roundi(15 * app.board.ui_scale)
		var caption: String = "8" if name == "gesture-counter-8" else name.get_slice("-", 2)
		var box_size: Vector2 = font.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(14, 10)
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
			fail_capture("Rendered live counter absent", 5)
			return picture
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
					var paper: Color = material.get_pixel(x,y)
					var delta: Vector3 = Vector3(pixel.r-paper.r,pixel.g-paper.g,pixel.b-paper.b)
					var tint: Vector3 = Vector3(app.board.ACCENT.r-paper.r,app.board.ACCENT.g-paper.g,app.board.ACCENT.b-paper.b)
					var coverage: float = delta.dot(tint)/tint.length_squared()
					# Alpha coverage of this exact accent, not a tolerance that mistakes
					# adjacent original red clue digits for ellipsis pixels.
					if coverage > 0.15 and coverage <= 1.01 and (delta-tint*coverage).length() < 0.01:
						accent_pixels += 1
			if (accent_pixels > 0) != bool(visual[side + "_hidden"]):
				fail_capture("Rendered hint marker mismatch: %s %s (%d pixels)" % [name, side, accent_pixels], 5)
				return picture
			pixel_checks += 1
	if name.ends_with("reveal"):
		var texture_image: Image = app.reveal_view.artwork.get_image()
		if texture_image == null or texture_image.is_empty():
			fail_capture("Missing rendered reveal", 6)
			return picture
	var row_index: int = longest_line(app.session.definition.rows)
	var column_index: int = longest_line(app.session.definition.columns)
	var row_window: Dictionary = app.board.clue_layout("row", row_index)
	var column_window: Dictionary = app.board.clue_layout("column", column_index)
	record.merge({"row_clue_steps": nonzero_steps(app.board.row_clue_steps), "column_clue_steps": nonzero_steps(app.board.column_clue_steps),
		"longest_row_window": [row_window.start, row_window.end, row_window.prefix_hidden, row_window.suffix_hidden],
		"longest_column_window": [column_window.start, column_window.end, column_window.prefix_hidden, column_window.suffix_hidden]})
	if not compact or name in COMPACT_PICTURES:
		var saved: Image = picture
		if crop:
			var box: Rect2 = app.board.view.cell_rect(Vector2i(2, 2)).merge(app.board.view.cell_rect(Vector2i(18, 8)))
			box.position += app.board.global_position
			saved = picture.get_region(Rect2i(box.grow(8)).intersection(Rect2i(Vector2i.ZERO, picture.get_size())))
		if saved.save_png(output.path_join(name + ".png")) != OK:
			fail_capture("Cannot retain capture: " + name, 4)
			return picture
		record.merge({"file": name + ".png", "retained": true, "crop": crop}, true)
		captures.append(record)
	return picture

func close_color(actual: Color, expected: Color) -> bool:
	return absf(actual.r - expected.r) <= 2.0/255 and absf(actual.g - expected.g) <= 2.0/255 and absf(actual.b - expected.b) <= 2.0/255

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

func capture_axis_reset(app: Main, fixture_index: int, pitch: float, color: int) -> void:
	app.select_puzzle(fixture_index)
	var values: Array[int] = app.session.player.cells.duplicate()
	values.fill(-1)
	replace_render_cells(app, values)
	set_pitch(app,pitch)
	app.board.view.center = Vector2(app.session.player.width, app.session.player.height) / 2.0
	app.board.view.reframe()
	await process_frame
	await process_frame
	var start: Vector2i = app.board.view.hit(app.board.view.viewport.get_center())
	var old: Vector2i = start + Vector2i(3, 0)
	var next: Vector2i = start + Vector2i(0, 3)
	app.board.active_color = color
	app.board.pointer_press(app.board.view.cell_rect(start).get_center(), MOUSE_BUTTON_LEFT)
	app.board.pointer_move(app.board.view.cell_rect(old).get_center(), true)
	var label: String = "g1-f%02d" % (fixture_index + 1)
	var old_image: Image = await snapshot(app, label + "-old-arm")
	app.board.pointer_move(app.board.view.cell_rect(start).get_center(), true)
	if app.board.gesture_length() != 1:
		fail_capture("Origin counter did not reset to one: " + label, 5)
		return
	var origin_image: Image = await snapshot(app, "g1-counter-1-" + label)
	app.board.pointer_move(app.board.view.cell_rect(next).get_center(), true)
	if app.board.gesture_length() != 4:
		fail_capture("New axis counter has wrong length: " + label, 5)
		return
	var new_image: Image = await snapshot(app, "g1-counter-4-" + label)
	var old_box: Rect2 = app.board.view.cell_rect(old)
	var new_box: Rect2 = app.board.view.cell_rect(next)
	old_box.position+=app.board.global_position
	new_box.position+=app.board.global_position
	var palette: Color = Color(app.session.definition.palette[color - 1].color)
	var patches: Array[Dictionary] = [fill_patch(old_image,old_image,old_box,palette,0.56,true),
		fill_patch(origin_image,origin_image,old_box,palette,0.56,true),
		fill_patch(new_image,new_image,old_box,palette,0.56,true),
		fill_patch(new_image,new_image,new_box,palette,0.56,true)]
	if not patches[0].valid or patches[1].valid or patches[2].valid or not patches[3].valid:
		fail_capture("Rendered old/new arm pixel mismatch: %s %s" % [label,patches], 5)
		return
	pixel_checks += 4
	app.board.cancel_gesture()

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
	var visible_length: float = 0.0
	var crosses: bool = false
	for which: int in range(2):
		var path: PackedVector2Array = PencilMarks.x_path(cell.y * app.session.player.width + cell.x, which)
		for i: int in range(path.size() - 1):
			var a: Vector2 = box.position + box.size * path[i]
			var b: Vector2 = box.position + box.size * path[i+1]
			crosses = crosses or (app.board.view.viewport.has_point(a) != app.board.view.viewport.has_point(b))
			var segment: PackedVector2Array = Board.clipped_segment(a, b, app.board.view.viewport.grow(-0.65))
			if segment.size() == 2:
				visible_length += segment[0].distance_to(segment[1])
	return crosses and visible_length >= 6.0

func capture_x_edges(app: Main) -> void:
	var regular: Board = use_renderer_component(app)
	for pitch: float in [24.0, 36.0]:
		set_pitch(app,pitch)
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
				fail_capture("Cannot position partial X at " + edge, 5)
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

	restore_regular_board(app,regular)

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
	component_navigate(app,Vector2(float(column) / 100.0, float(row) / 100.0))
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
				var current: Image = await snapshot(app, name)
				if previous != null and roundi(fraction * 100) in [51, 151]:
					var area: Rect2 = app.board.row_clue_area() if axis == "row" else app.board.column_clue_area()
					var line: Vector2 = app.board.view.cell_rect(Vector2i(0, index) if axis == "row" else Vector2i(index, 0)).get_center()
					var region: Rect2i = Rect2i(Rect2(app.board.global_position + (Vector2(area.position.x, line.y - 9) if axis == "row" else Vector2(line.x - 9, area.position.y)),
						Vector2(area.size.x, 18) if axis == "row" else Vector2(18, area.size.y))).intersection(Rect2i(Vector2i.ZERO, surface.size))
					if region_difference(previous, current, region) > CLUE_MOTION_PIXEL_BUDGET:
						fail_capture("Rendered hint numbers snapped before drop: " + name, 5)
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

func token_pixels(picture: Image, app: Main, axis: String, index: int, centers: Dictionary) -> bool:
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
	var before_image: Image = await snapshot(app, name + "-before-mouse-up")
	var release: InputEventMouseButton = InputEventMouseButton.new()
	release.button_index = MOUSE_BUTTON_MIDDLE
	release.pressed = false
	release.position = point + delta
	release.global_position = release.position
	surface.push_input(release, true)
	var after: Dictionary = visible_token_centers(app, axis, index)
	var after_image: Image = await snapshot(app, name + "-after-mouse-up")
	if not token_pixels(before_image, app, axis, index, before) or not token_pixels(after_image, app, axis, index, after):
		fail_capture("Rendered snap token absent: " + name, 5)
		return
	var before_capture: Dictionary = frames[-2]
	before_capture.token_centers = before
	before_capture.pointer_delta = [delta.x, delta.y]
	before_capture.hint_units = before_units
	var after_capture: Dictionary = frames[-1]
	after_capture.token_centers = after
	after_capture.hint_units = app.board.visual_hint_units(axis, index)
	var distance: Dictionary = preload("res://tests/p12_cases.gd").coordinate_distance(before, after)
	if distance.count == 0 or distance.largest > pitch * 0.5 + 0.001:
		fail_capture("Rendered snap moved shared tokens more than half a slot: " + name, 5)
		return
	if name == "snap-f02-row12-owner":
		var layout: Dictionary = app.board.clue_layout(axis, index)
		var owner_snapped: bool = false
		if before.has(0) and after.has(0):
			var nearest: int = roundi((float(before[0]) - app.board.clue_slot_origin(axis, app.board.row_clue_area(), layout)) / pitch - 0.5)
			owner_snapped = is_equal_approx(float(after[0]), app.board.clue_slot_center(axis, app.board.row_clue_area(), layout, nearest))
		if not owner_snapped or absf(float(before.get(0, -1)) - 51.2) > 0.001 or absf(float(after.get(0, -1)) - 56.0) > 0.001:
			fail_capture("Rendered F-02 row 12 token 4 missed its nearest slot", 5)
			return
		pixel_checks += 1

func capture_drop_matrix(app: Main, row: int, column: int) -> void:
	component_navigate(app,Vector2(float(column) / 100.0, float(row) / 100.0))
	for axis: String in ["row", "column"]:
		var index: int = row if axis == "row" else column
		var maximum: int = int(app.board.clue_layout(axis, index).max_offset)
		if compact:
			# Both sides of the half-slot boundary, both directions, a longer
			# middle drag, and the real current layout's two outward clamps.
			for anchor: int in [0, maximum]:
				var direction: float = -1.0 if anchor == maximum else 1.0
				for fraction: float in [0.49, 0.51]:
					await capture_drop_snap(app, axis, index, anchor, direction * fraction,
						"snap-%s-%d-%d-%d" % [axis, index, anchor, roundi(direction * fraction * 100)])
			for direction: float in [-1.0, 1.0]:
				await capture_drop_snap(app, axis, index, maximum / 2, direction * 1.8,
					"snap-%s-%d-middle-%d" % [axis, index, roundi(direction)])
			for anchor: int in [0, maximum]:
				app.board.set_clue_step(axis, index, anchor)
				var stop: Dictionary = visible_token_centers(app, axis, index)
				await capture_drop_snap(app, axis, index, anchor, -1.0 if anchor == 0 else 1.0,
					"snap-%s-%d-clamp-%d" % [axis, index, anchor])
				if stop != visible_token_centers(app, axis, index) or stop != frames[-2].token_centers:
					fail_capture("Current rendered outward clamp moved tokens: " + axis)
					return
				pixel_checks += 1
			continue
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
	var regular: Board = use_renderer_component(app)
	app.board._layout()
	set_pitch(app,36.0)
	# Retain the historical six-slot/24px repro alongside native Z2 captures.
	app.board.book_layout = false
	app.board.row_slot_extent_cache["%d/%d/%s" % [app.session.get_instance_id(),app.board.clue_font_size(),str(app.ui_scale)]] = 24.0
	var original_viewport: Rect2 = app.board.view.viewport
	app.board.view.configure(Rect2(Vector2(174, 126), Vector2(original_viewport.end.x - 174, original_viewport.size.y)), app.board.view.dimensions)
	app.board.normalize_clue_steps()
	component_navigate(app,Vector2(0.5, 11.0 / 40.0))
	if app.board.clue_capacity("row") != 6:
		fail_capture("F-02 owner render requires six actual row slots", 5)
		return
	await capture_drop_snap(app, "row", 11, 0, 1.8, "snap-f02-row12-owner")
	var row_maximum: int = int(app.board.clue_layout("row", 11).max_offset)
	if app.board.clue_step("row", 11) != row_maximum or app.board.row_clue_reads[11].anchor != "outer_start":
		fail_capture("V-01 owner render did not reach the direct outer stop", 5)
		return
	await capture_drop_snap(app, "row", 11, row_maximum, 1.0, "variant-a-owner-outer-clamp")
	await capture_monotone_route(app, "row", 11)
	var old_viewport: Rect2 = app.board.view.viewport
	var column_top: float = 4.0 * app.board.shared_clue_slot_extent("column", app.board.clue_font(), app.board.clue_font_size()) + 15.0
	app.board.view.configure(Rect2(Vector2(old_viewport.position.x, column_top), Vector2(old_viewport.size.x, old_viewport.end.y - column_top)), app.board.view.dimensions)
	app.board.normalize_clue_steps()
	var column_index: int = 11
	component_navigate(app,Vector2(float(column_index) / 40.0, 11.0 / 40.0))
	if app.board.clue_capacity("column") != 4 or app.session.definition.columns[column_index].size() != 5:
		fail_capture("V-02 column render requires four actual slots and five tokens", 5)
		return
	await capture_monotone_route(app, "column", column_index)
	column_top = 5.0 * app.board.shared_clue_slot_extent("column", app.board.clue_font(), app.board.clue_font_size()) + 15.0
	app.board.view.configure(Rect2(Vector2(old_viewport.position.x, column_top), Vector2(old_viewport.size.x, old_viewport.end.y - column_top)), app.board.view.dimensions)
	app.board.normalize_clue_steps()
	var long_column: int = 20
	component_navigate(app,Vector2(float(long_column) / 40.0, 11.0 / 40.0))
	if app.board.clue_capacity("column") != 5 or app.session.definition.columns[long_column].size() != 11:
		fail_capture("V-03 long column render requires five actual slots and eleven tokens", 5)
		return
	await capture_monotone_route(app, "column", long_column)
	restore_regular_board(app,regular)
	app._layout_book()

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
				fail_capture("V-02 rendered same-sign route did not progress", 5)
				return
		if app.board.clue_step(axis, index) != target or seen.size() != app.board.clue_entry_count(axis, index):
			fail_capture("V-03 rendered route did not reach every token", 5)
			return
		var stop: Dictionary = visible_token_centers(app, axis, index)
		await capture_drop_snap(app, axis, index, target, float(direction), "variant-a-%s-%d-dir%d-clamp" % [axis, index, direction])
		if stop != visible_token_centers(app, axis, index) or stop != frames[-2].token_centers:
			fail_capture("V-02 rendered outer/grid clamp moved tokens", 5)
			return

func run() -> void:
	output = OS.get_environment("P1_CAPTURE_DIR")
	if output.is_empty() or DisplayServer.get_name() == "headless":
		quit(2)
		return
	for argument: String in OS.get_cmdline_user_args():
		if argument not in ["--ci-compact", "--p1-capture"]:
			fail_capture("Unknown capture argument: " + argument)
			return
	surface = SubViewport.new()
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	var app: Main = load("res://main.tscn").instantiate()
	surface.add_child(app)
	var stage: String = OS.get_environment("P1_RENDER_STAGE")
	var stages: Array[String] = ["layout","views","cells-f1","cells-f2","gestures","hints","axis","h1"]
	if not stage.is_empty() and not stage in stages:
		fail_capture("Unknown capture stage: " + stage, 5)
		return
	for current: String in stages:
		if failed:
			return
		if not stage.is_empty() and stage != current:
			continue
		surface.size = Vector2i(1920,1080)
		app.set_ui_scale(1.0)
		app.select_puzzle(2)
		set_pitch(app,24.0)
		app.board.reset_clue_pan()
		await process_frame
		await process_frame
		match current:
			"layout": await capture_layout(app)
			"views": await capture_views(app)
			"gestures": await capture_gestures(app)
			"hints": await capture_hints(app)
			"axis": await capture_axis(app)
			"h1": await capture_h1(app)
			"cells-f1": await capture_cells(app,[0])
			"cells-f2": await capture_cells(app,[1])
	write_report()
	if failed:
		return
	print("P1_CAPTURE_OK: rendered=%d retained=%d compact=%s" % [frames.size(), captures.size(), compact])
	quit(0)

func capture_layout(app: Main) -> void:
	if compact:
		await capture_compact_layout(app)
		return
	app.show_album()
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

func capture_compact_layout(app: Main) -> void:
	app.show_album()
	await snapshot(app, "album")
	# Minimum client at the larger UI scale; regular 1080p at both scales.
	# Each visits mono, color and the 100x100 case; independent reads remain
	# visible on both axes at UI125 rather than repeating a 4x2 cross product.
	for configuration: Dictionary in [
		{"size": Vector2i(1280, 720), "scale": 1.25},
		{"size": Vector2i(1920, 1080), "scale": 1.0},
		{"size": Vector2i(1920, 1080), "scale": 1.25},
	]:
		surface.size = configuration.size
		app.set_ui_scale(configuration.scale)
		for fixture: int in range(3):
			app.select_puzzle(fixture)
			if app.ui_scale > 1.0:
				app.board.zoom(1, app.board.view.viewport.get_center())
			var values: Array[int] = app.session.player.cells.duplicate()
			for i: int in range(4):
				values[(4 + i) * app.session.player.width + 4] = mini(i + 1, app.session.definition.palette.size())
			replace_render_cells(app, values)
			app.board.hover = Vector2i(4, 4)
			var name: String = "%dx%d-ui%d-f%d" % [surface.size.x, surface.size.y, roundi(app.ui_scale * 100), fixture + 1]
			if fixture > 0 and app.ui_scale > 1.0:
				var row: int = 35 if fixture == 1 else 50
				var column: int = 21 if fixture == 1 else 50
				for axis: String in ["row", "column"]:
					var index: int = row if axis == "row" else column
					set_fractional_step(app, axis, index, 0.5)
					set_fractional_step(app, axis, index + 1, 1.0)
				name += "-independent-slots"
			await snapshot(app, name)

func capture_views(app: Main) -> void:
	var f03_row: int = longest_line(app.sessions[2].definition.rows)
	var f03_column: int = longest_line(app.sessions[2].definition.columns)
	# D-18/D-19: unnumbered colored numbers remain single-line in shared slots.
	# D-20 adds independent snapped positions for every concrete row and column.
	surface.size = Vector2i(1920, 1080)
	app.set_ui_scale(1)
	app.select_puzzle(1)
	app.board.hover = Vector2i(10, 10)
	await snapshot(app, "f02-colored-hints-default")
	for step: float in [22.0, 24.0]:
		set_pitch(app,step)
		for position: float in [0.0, 0.5, 1.0]:
			set_fractional_step(app, "row", 35, position)
			set_fractional_step(app, "column", 21, position)
			await snapshot(app, "f02-hints-%d-%s" % [roundi(step), ["end", "middle", "start"][roundi(position * 2.0)]])
	set_pitch(app,12.0)
	set_fractional_step(app, "row", 35, 0.5)
	set_fractional_step(app, "row", 36, 1.0)
	set_fractional_step(app, "column", 21, 0.5)
	set_fractional_step(app, "column", 22, 1.0)
	await snapshot(app, "f02-hints-50-independent-middle")
	set_pitch(app,24.0)
	app.board.reset_clue_pan()
	set_fractional_step(app, "row", 35, 1.0)
	await snapshot(app, "f02-row-start-column-end")
	app.board.reset_clue_pan()
	set_fractional_step(app, "column", 21, 1.0)
	await snapshot(app, "f02-row-end-column-start")
	app.select_puzzle(2)
	app.board.hover = Vector2i(f03_column, f03_row)
	app.board.set_clue_hover("row", f03_row)
	await snapshot(app, "f03-overflow-hover-tooltip")
	app.board.clear_clue_hover()
	for step: float in [12.0, 18.0, 22.0, 24.0]:
		set_pitch(app,step)
		app.board.reset_clue_pan()
		await snapshot(app, "f03-hints-work-%d-end" % roundi(step / 24.0 * 100.0))
	for step: float in [12.0, 24.0]:
		set_pitch(app,step)
		for position: float in [0.5, 1.0]:
			set_fractional_step(app, "row", f03_row, position)
			set_fractional_step(app, "column", f03_column, position)
			await snapshot(app, "f03-hints-work-%d-%s" % [roundi(step / 24.0 * 100.0), "middle" if position == 0.5 else "start"])
	set_pitch(app,24.0)
	set_fractional_step(app, "row", f03_row, 0.45)
	set_fractional_step(app, "column", f03_column, 0.65)
	app.board.view.pan(Vector2(120, 80))
	component_navigate(app,Vector2(0.78, 0.22))
	await snapshot(app, "f03-hints-after-raster-pan")

func capture_cells(app: Main, fixtures: Array) -> void:
	# Same L/block at normal and five-cell boundaries, every color/work step.
	# This spatial renderer oracle deliberately covers every historical work
	# pitch; regular fit-bounded geometry is checked by VS2's native matrix.
	var regular: Board = use_renderer_component(app)
	for fixture: int in fixtures:
		app.select_puzzle(fixture)
		var values: Array[int] = app.session.player.cells.duplicate()
		values.fill(-1)
		for i: int in range(app.session.definition.palette.size()):
			var x: int = 2 + i * 2
			for cell: Vector2i in [Vector2i(x, 4), Vector2i(x+1, 4), Vector2i(x, 5), Vector2i(x, 7), Vector2i(x+1, 7), Vector2i(x+1, 8)]:
				values[cell.y * app.session.player.width + cell.x] = i + 1
		replace_render_cells(app, values)
		app.board.hover = Vector2i(-1, -1)
		for step: float in COMPACT_WORK_STEPS if compact else app.board.WORK_STEPS:
			set_pitch(app,step)
			app.board.view.center = Vector2.ZERO
			app.board.view.reframe()
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
	restore_regular_board(app,regular)

func capture_gestures(app: Main) -> void:
	var f03_row: int = longest_line(app.sessions[2].definition.rows)
	var f03_column: int = longest_line(app.sessions[2].definition.columns)
	app.select_puzzle(2)
	set_pitch(app,24.0)
	app.board.view.center = Vector2(50, 50)
	app.board.view.reframe()
	app.board.hover = app.board.view.hit(app.board.view.viewport.get_center())
	await snapshot(app, "f03-grid-focus")
	app.board.hover = Vector2i(-1, -1)
	await capture_x_edges(app)
	# Continuous pixel motion at the historical 24px stress-sheet geometry.
	var regular: Board = use_renderer_component(app)
	set_pitch(app,24.0)
	app.board.view.center = Vector2(50,f03_row)
	app.board.view.reframe()
	app.board.reset_clue_pan()
	var before_drag: Image = await snapshot(app, "hint-drag-before")
	app.board.pan_button = MOUSE_BUTTON_MIDDLE
	app.board.pan_target = "row"
	app.board.pan_line_index = f03_row
	app.board.pan_drag_distance = float(app.board.clue_layout("row", f03_row).slot_extent) * 0.42
	var after_drag: Image = await snapshot(app, "hint-drag-subslot")
	var row_rect: Rect2 = app.board.row_clue_area()
	var row_y: float = app.board.view.cell_rect(Vector2i(0, f03_row)).get_center().y
	var target_region: Rect2i = Rect2i(Rect2(app.board.global_position + Vector2(row_rect.position.x, row_y - 9), Vector2(row_rect.size.x, 18)))
	var neighbour_y: float = row_y + app.board.view.cell_size
	var neighbour_region: Rect2i = Rect2i(Rect2(app.board.global_position + Vector2(row_rect.position.x, neighbour_y - 9), Vector2(row_rect.size.x, 18)))
	if region_difference(before_drag, after_drag, target_region) < 5 or region_difference(before_drag, after_drag, neighbour_region) != 0 or app.board.clue_step("row", f03_row) != 0:
		fail_capture("Rendered subslot hint drag did not move continuously", 5)
		return
	pixel_checks += 1
	var pitch: float = float(app.board.clue_layout("row", f03_row).slot_extent)
	app.board.pan_drag_distance = pitch * 0.49
	var before_boundary: Image = await snapshot(app, "hint-drag-before-slot-boundary")
	app.board.pan_drag_distance = pitch * 0.51
	var after_boundary: Image = await snapshot(app, "hint-drag-after-slot-boundary")
	if region_difference(before_boundary, after_boundary, target_region) > CLUE_MOTION_PIXEL_BUDGET or region_difference(before_boundary, after_boundary, neighbour_region) != 0:
		fail_capture("Rendered row hint jumped at a slot boundary", 5)
		return
	pixel_checks += 2
	app.board.cancel_gesture()
	app.board.view.center = Vector2(f03_column,f03_row)
	app.board.view.reframe()
	app.board.pan_button = MOUSE_BUTTON_MIDDLE
	app.board.pan_target = "column"
	app.board.pan_line_index = f03_column
	var column_pitch: float = float(app.board.clue_layout("column", f03_column).slot_extent)
	app.board.pan_drag_distance = column_pitch * 0.49
	var column_before_boundary: Image = await snapshot(app, "hint-drag-column-before-slot-boundary")
	app.board.pan_drag_distance = column_pitch * 0.51
	var column_after_boundary: Image = await snapshot(app, "hint-drag-column-after-slot-boundary")
	var column_area: Rect2 = app.board.column_clue_area()
	var column_x: float = app.board.view.cell_rect(Vector2i(f03_column, 0)).get_center().x
	var column_region: Rect2i = Rect2i(Rect2(app.board.global_position + Vector2(column_x - 9, column_area.position.y), Vector2(18, column_area.size.y))).intersection(Rect2i(Vector2i.ZERO, surface.size))
	if region_difference(column_before_boundary, column_after_boundary, column_region) > CLUE_MOTION_PIXEL_BUDGET or app.board.clue_step("column", f03_column) != 0:
		fail_capture("Rendered column hint jumped at a slot boundary", 5)
		return
	pixel_checks += 1
	app.board.cancel_gesture()
	restore_regular_board(app,regular)

func capture_hints(app: Main) -> void:
	var f03_row: int = longest_line(app.sessions[2].definition.rows)
	var f03_column: int = longest_line(app.sessions[2].definition.columns)
	var regular: Board = use_renderer_component(app)
	set_pitch(app,24.0)
	app.board.view.center = Vector2(f03_column,f03_row)
	app.board.view.reframe()
	await capture_hint_markers(app, f03_row, f03_column)
	await capture_drop_matrix(app, f03_row, f03_column)
	restore_regular_board(app,regular)

func capture_axis(app: Main) -> void:
	var f03_row: int = longest_line(app.sessions[2].definition.rows)
	var f03_column: int = longest_line(app.sessions[2].definition.columns)
	var gesture_start: Vector2i = app.board.view.hit(app.board.view.viewport.get_center())
	app.board.pointer_press(app.board.view.cell_rect(gesture_start).get_center(), MOUSE_BUTTON_RIGHT)
	app.board.pointer_move(app.board.view.cell_rect(gesture_start + Vector2i(7, 0)).get_center(), true)
	if app.board.gesture_length() != 8:
		fail_capture("Rendered gesture counter has wrong value", 5)
		return
	await snapshot(app, "gesture-counter-8")
	app.board.cancel_gesture()
	await capture_axis_reset(app, 1, 24.0, 3)
	await capture_axis_reset(app, 2, 12.0, 1)
	app.board.hover = Vector2i(f03_column, f03_row)
	app.board.set_clue_hover("row", f03_row)
	await snapshot(app, "f03-full-clues-in-work-tooltip")
	app.board.clear_clue_hover()
	app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
	await snapshot(app, "f03-overview")
	if not compact:
		await capture_owner_drop(app)

func capture_h1(app: Main) -> void:
	# Preserve the current renderer's strict overflow/status/tooltip pixel
	# contracts, then exercise the regular full-view route independently.
	var regular: Board = use_renderer_component(app)
	await preload("res://tests/h1_capture.gd").run(self, app)
	restore_regular_board(app, regular)
	await preload("res://tests/vs2_h1_cases.gd").run(self, app)
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


func use_renderer_component(app: Main) -> Board:
	# Explicit developer pixel oracle for historical clipped X/snap geometry.
	# The regular route cannot offer this geometry; VS2 tests assert the opposite.
	var regular: Board = app.board
	var component = load("res://ui/chalkboard_board.gd").new()
	component.session = app.session
	component.size = regular.size
	component.position = regular.position
	component.ui_scale = regular.ui_scale
	component.book_layout = true
	component.book_inset = Vector2(210,126) * regular.ui_scale
	component.book_grid_size = component.size - component.book_inset - Vector2(12,12)
	regular.hide()
	app.work.add_child(component)
	app.board = component
	component.edited.connect(app.refresh)
	component.resized.connect(func() -> void:
		component.book_grid_size = (component.size-component.book_inset-Vector2(12,12)).max(Vector2.ONE)
		component._layout())
	return regular

func restore_regular_board(app: Main, regular: Board) -> void:
	var component: Board = app.board
	component.get_parent().remove_child(component)
	component.queue_free()
	app.board = regular
	regular.session = app.session
	regular.layout_key = ""
	regular._layout()
	regular.show()

func set_pitch(app: Main, pitch: float) -> void:
	if app.board.has_method("set_mode"):
		app.board.requested_cell = pitch
		app.board.overview = false
		app.board._layout()
	else:
		app.board.view.zoom_to(pitch,app.board.view.viewport.get_center())

func component_navigate(app: Main, normalized: Vector2) -> void:
	# Only the explicit developer renderer can exercise historical clipped views.
	if not app.board.has_method("set_mode"):
		app.board.view.center = normalized * Vector2(app.board.view.dimensions)
		app.board.view.reframe()
