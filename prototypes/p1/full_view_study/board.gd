extends "res://study/board.gd"
## Same ZS-1 drawing layer in R/G/V; only bounded layout/navigation differs.
var mode: String = "G"
var requested_cell: float = 0.0 # zero means the current fit ceiling
var fit_ceiling: float = 24.0
var raw_fit: float = 24.0
var max_hints: Vector2i = Vector2i.ONE
var reference_views: Dictionary = {}
var layout_valid: bool = true
var glyph_risk: bool = false

func _layout() -> void:
	if mode == "R":
		if marks != null:
			marks.show()
		super._layout()
		raw_fit = minf(view.viewport.size.x/session.player.width,view.viewport.size.y/session.player.height)
		fit_ceiling = 72.0
		return
	if session == null or size.x <= 1 or size.y <= 1:
		return
	max_hints = Vector2i.ONE
	for line: Array in session.definition.rows:
		max_hints.x = maxi(max_hints.x, line.size())
	for line: Array in session.definition.columns:
		max_hints.y = maxi(max_hints.y, line.size())
	var slots: Vector2i = max_hints if mode == "V" else Vector2i(mini(max_hints.x, 6), mini(max_hints.y, 5))
	# At least three slots in navigable G, matching the existing marker contract.
	if mode == "G":
		slots = slots.max(Vector2i(3, 3))
	book_inset = Vector2(slots) * Vector2(26, 18) * ui_scale + Vector2(6, 6)
	var available: Vector2 = size - book_inset - Vector2(6, 6)
	raw_fit = minf(available.x / session.player.width, available.y / session.player.height)
	# The bound pen uses a two-pixel inset. Below four pixels even its interior
	# disappears: report failure rather than feeding negative rectangles to it.
	layout_valid = raw_fit > 4.0
	fit_ceiling = maxf(1.0, floorf(raw_fit * 100.0) / 100.0)
	view.cell_size = minf(requested_cell, fit_ceiling) if requested_cell > 0 else fit_ceiling
	book_grid_size = Vector2(session.player.width, session.player.height) * view.cell_size
	view.configure(Rect2(book_inset, book_grid_size), Vector2i(session.player.width, session.player.height))
	view.center = Vector2(view.dimensions) / 2.0
	view.reframe()
	if marks != null:
		marks.visible = layout_valid
	# Conservative real ink/status extents, including multi-digit columns. This
	# fast warning complements the exhaustive measured overlap test in delivery.
	glyph_risk = false
	var fs: int = clue_font_size()
	for axis: String in ["row", "column"]:
		for line: Array in (session.definition.rows if axis == "row" else session.definition.columns):
			for clue: Dictionary in line:
				var box: Rect2 = glyph_box(str(clue.length), Vector2.ZERO, fs)
				if (box.size.y if axis == "row" else box.size.x) > view.cell_size:
					glyph_risk = true
	ensure_clue_steps()
	normalize_clue_steps()
	cancel_gesture()

func set_mode(value: String) -> void:
	if not value in ["R", "G", "V"] or value == mode:
		return
	cancel_gesture()
	if mode == "R":
		reference_views[session.definition.id] = super.capture_view()
	mode = value
	var color_before: int = active_color
	var eraser_before: bool = eraser
	var hand_before: bool = hand
	if mode == "R" and reference_views.has(session.definition.id):
		super.restore_view(reference_views[session.definition.id])
	else:
		overview = false
		if mode == "R":
			view.cell_size = 24.0
	active_color = color_before
	eraser = eraser_before
	hand = hand_before
	viewport_layout_requested.emit()
	_layout()
	view_changed.emit()

func navigation_target(point: Vector2) -> String:
	if mode == "R":
		return super.navigation_target(point)
	if mode == "G" and layout_valid:
		var target: String = super.navigation_target(point)
		return target if target in ["row", "column"] else ""
	return ""

func navigate_to(normalized: Vector2) -> void:
	if mode == "R":
		super.navigate_to(normalized)

func zoom(direction: int, anchor: Vector2) -> void:
	if mode == "R":
		super.zoom(direction, anchor)
		return
	if session.gesture.active or not layout_valid:
		return
	var step: float = next_zoom_step(view.cell_size, direction)
	if direction < 0 and step >= view.cell_size:
		return
	if direction > 0:
		step = minf(step, fit_ceiling)
	if is_equal_approx(step, view.cell_size):
		return
	requested_cell = step
	_layout()
	view_changed.emit()

func working_size() -> void:
	if mode == "R":
		super.working_size()
	elif not session.gesture.active:
		requested_cell = 20.0
		_layout()
		view_changed.emit()

func fit_all() -> void:
	if mode == "R":
		super.fit_all()
	elif not session.gesture.active:
		requested_cell = 0.0
		_layout()
		view_changed.emit()

func capture_view() -> Dictionary:
	var state: Dictionary = super.capture_view()
	if mode != "R":
		# Fit values belong only to VS. Never put fractional/nonstandard zooms in Schema 1.
		state.zoom = 24
		state.overview = true
	return state

func restore_view(state: Dictionary) -> void:
	super.restore_view(state)
	if mode != "R":
		_layout()

func pointer_press(point: Vector2, button: MouseButton) -> void:
	if mode == "R" or layout_valid:
		super.pointer_press(point, button)

func _draw() -> void:
	if mode != "R" and not layout_valid:
		draw_string(BODY_FONT, Vector2(12, 36), "Kein Platz für alle Hinweise. Referenz R verwenden.", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, INK)
		return
	super._draw()

static func rect_values(rect: Rect2) -> Array:
	return [rect.position.x, rect.position.y, rect.size.x, rect.size.y]

func glyph_box(text: String, baseline: Vector2, fs: int) -> Rect2:
	var font: Font = clue_text_font(clue_font(), text)
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var result: Rect2
	var advance: float = 0.0
	var first: bool = true
	for c: String in text:
		var glyph: int = ts.font_get_glyph_index(rid, fs, c.unicode_at(0), 0)
		var box: Rect2 = Rect2(baseline + Vector2(advance, 0) + ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph), ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph))
		result = box if first else result.merge(box)
		first = false
		advance += font.get_string_size(c, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	# Bound C1/AA and all three statuses, independent of current completion state.
	var width: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	result = result.merge(Rect2(baseline - Vector2(0, fs * 0.32 + 1), Vector2(width, 2)))
	return result.grow(maxf(0.5, ui_scale / 4.0))

func measurements() -> Dictionary:
	var fs: int = clue_font_size()
	var clipped: int = 0
	var collisions: int = 0
	var hidden: int = 0
	var glyph_count: int = 0
	var largest: Vector2 = Vector2.ZERO
	var extents: Dictionary = {}
	for axis: String in ["row", "column"]:
		var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
		var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
		var boxes: Array[Rect2] = []
		for index: int in range(lines.size()):
			var layout: Dictionary = clue_layout(axis, index)
			hidden += int(layout.start) + int(layout.entries.size()) - int(layout.end)
			for unit: Dictionary in visual_hint_units(axis, index).units:
				var text: String = "…" if unit.kind != "token" else str(layout.entries[int(unit.index)].text)
				var width: float = clue_text_font(clue_font(), text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
				var cross: float = (view.origin.y if axis == "row" else view.origin.x) + (index + 0.5) * view.cell_size
				var baseline: Vector2 = Vector2(float(unit.center) - width / 2.0, cross + clue_baseline_offset(fs)) if axis == "row" else Vector2(cross - width / 2.0, float(unit.center) + clue_baseline_offset(fs))
				var box: Rect2 = glyph_box(text, baseline, fs)
				largest = largest.max(box.size)
				glyph_count += 1
				if not area.grow(0.01).encloses(box):
					clipped += 1
				for other: Rect2 in boxes:
					if other.intersects(box):
						collisions += 1
				boxes.append(box)
		if not boxes.is_empty():
			var union: Rect2 = boxes[0]
			for box: Rect2 in boxes:
				union = union.merge(box)
			extents[axis] = rect_values(union)
	var grid_fit: bool = view.viewport.grow(0.01).encloses(view.bounds()) and (mode == "R" or layout_valid)
	var complete: bool = grid_fit and hidden == 0 and clipped == 0 and collisions == 0
	return {"mode": mode, "cell_pitch": view.cell_size, "raw_fit_ceiling": raw_fit, "zoom_ceiling": fit_ceiling if mode != "R" else 72.0,
		"grid": rect_values(view.bounds()), "viewport": rect_values(view.viewport), "row_clues": rect_values(row_clue_area()), "column_clues": rect_values(column_clue_area()),
		"font_px": fs, "glyph_max": [largest.x, largest.y], "glyph_extents": extents, "glyph_count": glyph_count,
		"clipped_glyphs": clipped, "glyph_collisions": collisions, "hidden_tokens": hidden, "grid_fit": grid_fit, "full_sheet_fit": complete,
		"grid_navigation_needed": not grid_fit, "hint_navigation_needed": hidden > 0, "layout_valid": mode == "R" or layout_valid,
		"geometry_rendered": mode == "R" or layout_valid, "glyph_risk": glyph_risk,
		"max_row_hints": session.definition.rows.map(func(x: Array) -> int: return x.size()).max(),
		"max_column_hints": session.definition.columns.map(func(x: Array) -> int: return x.size()).max(),
		"status": "geometric_fit_owner_open" if (complete if mode == "V" else grid_fit) and view.cell_size >= 16 and collisions == 0 and clipped == 0 else "restricted_or_failed_owner_open"}
