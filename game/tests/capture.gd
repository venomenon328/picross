extends SceneTree
## Real GPU/software-rendered offscreen surfaces; not a physical DPI claim.
const Main = preload("res://ui/main.gd")
const SaveStore = preload("res://model/save_store.gd")
const Session = preload("res://model/session.gd")
const Board = preload("res://ui/board.gd")
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
var zr_samples: Array = []

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
		"physical_dpi_acceptance": "OPEN: owner", "zr_samples": zr_samples, "captures": captures, "frames": frames, "failure_captures": failure_captures}, "  ") + "\n")

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
	if name.contains("preview-color"):
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
	if (name.begins_with("separation-") and name.ends_with("-confirmed")) or name == "t06-grid-focus":
		var focus_before_hide: Vector2i = app.board.hover
		app.board.hide()
		await process_frame
		await RenderingServer.frame_post_draw
		material = surface.get_texture().get_image()
		app.board.show()
		if name == "t06-grid-focus":
			# Material capture hides the board and therefore clears its transient
			# pointer. Restore the measured sample through the shared resolver;
			# HN separately verifies real main-scene event routing.
			app.board.update_pointer_hover(app.board.view.cell_rect(focus_before_hide).get_center())
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
	if name == "t06-grid-focus":
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
	if name == "gesture-counter-8" or name.begins_with("g1-counter-"):
		var caption: String = "8" if name == "gesture-counter-8" else name.get_slice("-", 2)
		var dark_pixels: int = 0
		var area: Rect2i = Rect2i(app.board.gesture_counter.placement().rect)
		for y: int in range(area.position.y, area.end.y):
			for x: int in range(area.position.x, area.end.x):
				if picture.get_pixel(x, y).r < 0.5:
					dark_pixels += 1
		if app.board.gesture_counter.visible != (caption != "1") or (caption != "1" and dark_pixels < 3):
			fail_capture("Rendered live counter absent", 5)
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
	var label: String = "g1-t%02d" % (fixture_index + 1)
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

func region_difference(before: Image, after: Image, region: Rect2i) -> int:
	var differences: int = 0
	for y: int in range(region.position.y, region.end.y):
		for x: int in range(region.position.x, region.end.x):
			if not before.get_pixel(x, y).is_equal_approx(after.get_pixel(x, y)):
				differences += 1
	return differences

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
	var stages: Array[String] = ["layout","cells-f1","cells-f2","axis","h1"]
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
		app.select_puzzle(3)
		set_pitch(app,24.0)
		app.board.reset_clue_pan()
		await process_frame
		await process_frame
		match current:
			"layout": await capture_layout(app)
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
			for fixture: int in [0,1,3]:
				app.select_puzzle(fixture)
				if scale > 1:
					app.board.zoom(1, app.board.view.viewport.get_center())
				var values: Array[int] = app.session.player.cells.duplicate()
				for i: int in range(4):
					values[(4 + i) * app.session.player.width + 4] = mini(i + 1, app.session.definition.palette.size())
				replace_render_cells(app, values)
				app.board.hover = Vector2i(4, 4)
				await snapshot(app, "%dx%d-ui%d-f%d" % [dims.x, dims.y, roundi(scale * 100), int(app.session.definition.id.trim_prefix("T-"))])
			app.select_puzzle(1)
			set_fractional_step(app, "row", 35, 0.5)
			set_fractional_step(app, "row", 36, 1.0)
			set_fractional_step(app, "column", 21, 0.5)
			set_fractional_step(app, "column", 22, 1.0)
			await snapshot(app, "%dx%d-ui%d-f2-independent-slots" % [dims.x, dims.y, roundi(scale * 100)])
			app.select_puzzle(3)
			set_fractional_step(app, "row", 41, 0.35)
			set_fractional_step(app, "row", 33, 0.7)
			set_fractional_step(app, "column", 17, 0.35)
			set_fractional_step(app, "column", 32, 0.7)
			await snapshot(app, "%dx%d-ui%d-f6-independent-slots" % [dims.x, dims.y, roundi(scale * 100)])

func capture_compact_layout(app: Main) -> void:
	app.show_album()
	await snapshot(app, "album")
	# Minimum client at the larger UI scale; regular 1080p at both scales.
	# Each visits mono, color and the 50x50 case; independent reads remain
	# visible on both axes at UI125 rather than repeating a 4x2 cross product.
	for configuration: Dictionary in [
		{"size": Vector2i(1280, 720), "scale": 1.25},
		{"size": Vector2i(1920, 1080), "scale": 1.0},
		{"size": Vector2i(1920, 1080), "scale": 1.25},
	]:
		surface.size = configuration.size
		app.set_ui_scale(configuration.scale)
		for fixture: int in [0,1,3]:
			app.select_puzzle(fixture)
			if app.ui_scale > 1.0:
				app.board.zoom(1, app.board.view.viewport.get_center())
			var values: Array[int] = app.session.player.cells.duplicate()
			for i: int in range(4):
				values[(4 + i) * app.session.player.width + 4] = mini(i + 1, app.session.definition.palette.size())
			replace_render_cells(app, values)
			app.board.hover = Vector2i(4, 4)
			var name: String = "%dx%d-ui%d-f%d" % [surface.size.x, surface.size.y, roundi(app.ui_scale * 100), int(app.session.definition.id.trim_prefix("T-"))]
			if fixture > 0 and app.ui_scale > 1.0:
				var row: int = 35 if fixture == 1 else 41
				var column: int = 21 if fixture == 1 else 17
				for axis: String in ["row", "column"]:
					var index: int = row if axis == "row" else column
					set_fractional_step(app, axis, index, 0.5)
					set_fractional_step(app, axis, index + 1 if fixture == 1 else (33 if axis == "row" else 32), 1.0)
				name += "-independent-slots"
			await snapshot(app, name)

func capture_cells(app: Main, fixtures: Array) -> void:
	# Same L/block at normal and five-cell boundaries, every color/work step.
	# This spatial renderer oracle covers the current cell-size boundaries;
	# regular fit-bounded geometry is checked by VS2's native matrix.
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

func capture_axis(app: Main) -> void:
	app.board.hover = app.board.view.hit(app.board.view.viewport.get_center())
	await snapshot(app, "t06-grid-focus")
	app.board.hover = Vector2i(-1, -1)
	var t06_row: int = longest_line(app.sessions[3].definition.rows)
	var t06_column: int = longest_line(app.sessions[3].definition.columns)
	var gesture_start: Vector2i = app.board.view.hit(app.board.view.viewport.get_center())
	app.board.pointer_press(app.board.view.cell_rect(gesture_start).get_center(), MOUSE_BUTTON_RIGHT)
	app.board.pointer_move(app.board.view.cell_rect(gesture_start + Vector2i(7, 0)).get_center(), true)
	if app.board.gesture_length() != 8:
		fail_capture("Rendered gesture counter has wrong value", 5)
		return
	await snapshot(app, "gesture-counter-8")
	app.board.cancel_gesture()
	await capture_axis_reset(app, 1, 24.0, 3)
	await capture_axis_reset(app, 3, 12.0, 1)
	app.board.hover = Vector2i(t06_column, t06_row)
	app.board.set_clue_hover("row", t06_row)
	await snapshot(app, "t06-full-clues-in-work-tooltip")
	app.board.clear_clue_hover()
	app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))
	await snapshot(app, "t06-overview")
	await capture_zr_counter(app)

func capture_zr_counter(app: Main) -> void:
	# Targeted native glyph pixels; these SubViewport cases do not prove OS input.
	for configuration: Array in [[Vector2i(1280,720),1.25],[Vector2i(1920,1080),1.0],[Vector2i(2560,1440),1.25]]:
		surface.size=configuration[0]
		app.set_ui_scale(configuration[1])
		app.select_puzzle(0)
		var values: Array[int] = app.session.player.cells.duplicate()
		values.fill(-1)
		replace_render_cells(app,values)
		for zoom: float in [12.0,72.0]:
			set_pitch(app,zoom)
			await process_frame
			var b: Control = app.board
			b.pointer_press(b.view.cell_rect(Vector2i(4,4)).get_center(),MOUSE_BUTTON_LEFT)
			if b.gesture_counter.visible:
				fail_capture("ZR length one must be hidden")
				return
			b.pointer_move(b.view.cell_rect(Vector2i(8,4)).get_center(),true)
			var s: Vector2 = Vector2(surface.size)
			var samples: Array[Vector2] = [b.gesture_counter.cursor,b.gesture_counter.cursor+Vector2(1,1),
				app.undo_button.get_global_rect().get_center(),Vector2(-50,s.y/2),Vector2(s.x+50,s.y/2),
				Vector2(s.x/2,-50),Vector2(s.x/2,s.y+50),Vector2(-50,-50),Vector2(s.x+50,-50),
				Vector2(-50,s.y+50),s+Vector2(50,50)]
			for i: int in range(samples.size()):
				b.pointer_move(b.get_global_transform_with_canvas().affine_inverse()*samples[i],false)
				var name: String = "zr-%d-ui%d-z%d-%d" % [surface.size.x,roundi(app.ui_scale*100),roundi(zoom),i]
				var picture: Image = await snapshot(app,name)
				var p: Dictionary = b.gesture_counter.placement()
				var a: Vector2i = Vector2i(p.rect.position.floor())
				var area: Rect2i = Rect2i(a,Vector2i(p.rect.end.ceil())-a)
				if not b.gesture_counter.visible or not Rect2i(Vector2i.ZERO,surface.size).encloses(area) or p.font.get_font_name()!="Delight Coffee" or p.font_size!=roundi(24*app.ui_scale):
					fail_capture("ZR counter visibility/font/client envelope: "+name)
					return
				b.gesture_counter.hide()
				await process_frame
				await RenderingServer.frame_post_draw
				var underlay: Image = surface.get_texture().get_image()
				var masked: Image = picture.duplicate()
				masked.blit_rect(underlay,area,area.position)
				var changed: int = region_difference(picture,underlay,area)
				# Real glyphs leave transparent space. A panel/rectangle, clipped
				# outline, missing text or drawing outside its measured ink fails.
				var corner: Rect2i = Rect2i(area.position,Vector2i(2,2))
				if changed<3 or changed>=area.size.x*area.size.y*0.8 or region_difference(picture,underlay,corner)!=0 or masked.get_data()!=underlay.get_data():
					fail_capture("ZR native glyph/background/outline bounds: "+name)
					return
				pixel_checks+=5
				var record: Dictionary = {"name":name,"cursor":[samples[i].x,samples[i].y],"length":b.gesture_length(),"rect":[area.position.x,area.position.y,area.size.x,area.size.y],"font_size":p.font_size,"ui":app.ui_scale,"requested_zoom":zoom,"actual_cell":b.view.cell_size,"changed_pixels":changed}
				if i==2 and zoom==12.0 or i==10:
					var image: Image = picture if i==2 else picture.get_region(area.grow(4).intersection(Rect2i(Vector2i.ZERO,surface.size)))
					image.save_png(output.path_join(name+".png"))
					record["file"]=name+".png"
					captures.append({"name":name,"file":name+".png","crop":i!=2,"retained":true})
				zr_samples.append(record)
				b.sync_gesture_counter()
			b.cancel_gesture()

func capture_h1(app: Main) -> void:
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
	# Exercise the active shared cell renderer at exact boundary pitches.
	# Full-view fit caps vary with the fixture; VS2 tests cover that composition.
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
