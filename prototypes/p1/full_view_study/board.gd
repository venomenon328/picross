extends "res://study/board.gd"
## VS-GF1: fit from minimum reserves, then spend spare width on row clues.
const FRAME_MARGIN: float = 1.0 # half the widest (two-pixel) grid stroke
var mode: String = "G"
var requested_cell: float = 0.0 # zero means the current fit ceiling
var fit_ceiling: float = 24.0
var raw_fit: float = 24.0
var max_hints: Vector2i = Vector2i.ONE
var reserve_slots: Vector2i = Vector2i.ONE
var minimum_slots: Vector2i = Vector2i.ONE
var horizontal_budget: float = 0.0
var horizontal_used: float = 0.0
var reserve_cache: Dictionary = {}
var ink_cache: Dictionary = {}
var layout_valid: bool = true
var glyph_risk: bool = false

func _layout() -> void:
	if session == null or size.x <= 1 or size.y <= 1:
		return
	mode = "V" if mode == "V" else "G"
	hand = false
	max_hints = Vector2i.ONE
	for line: Array in session.definition.rows:
		max_hints.x = maxi(max_hints.x, line.size())
	for line: Array in session.definition.columns:
		max_hints.y = maxi(max_hints.y, line.size())
	minimum_slots = max_hints if mode == "V" else Vector2i(required_slots("row"), required_slots("column"))
	reserve_slots = minimum_slots
	book_inset = Vector2(minimum_slots) * Vector2(26, 18) * ui_scale + Vector2(6, 6)
	var frame_space: Vector2 = Vector2.ONE * 2.0 * FRAME_MARGIN
	var available: Vector2 = size - book_inset - Vector2(6, 6) - frame_space
	raw_fit = minf(available.x / session.player.width, available.y / session.player.height)
	# The bound pen uses a two-pixel inset. Below four pixels even its interior
	# disappears: report failure rather than feeding negative rectangles to it.
	layout_valid = raw_fit > 4.0
	fit_ceiling = maxf(1.0, floorf(raw_fit * 100.0) / 100.0)
	view.cell_size = minf(requested_cell, fit_ceiling) if requested_cell > 0 else fit_ceiling
	layout_valid = layout_valid and view.cell_size > 4.0
	book_grid_size = Vector2(session.player.width, session.player.height) * view.cell_size
	# One-way allocation: the displayed capacity never feeds back into fit.
	horizontal_budget = maxf(0.0, available.x - book_grid_size.x)
	horizontal_used = 0.0
	if mode == "G" and layout_valid:
		var pitch: float = 26.0 * ui_scale
		var offered: int = mini(max_hints.x, minimum_slots.x + floori((horizontal_budget + 0.000001) / pitch))
		for capacity: int in range(offered, minimum_slots.x, -1):
			if suitable_slots("row", capacity):
				reserve_slots.x = capacity
				break
		horizontal_used = (reserve_slots.x - minimum_slots.x) * pitch
		book_inset.x += horizontal_used
	view.configure(Rect2(book_inset, book_grid_size + frame_space), Vector2i(session.player.width, session.player.height))
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
				var box: Rect2 = glyph_box(clue_token(clue), Vector2.ZERO, fs)
				if (box.size.y if axis == "row" else box.size.x) > view.cell_size:
					glyph_risk = true
	ensure_clue_steps()
	normalize_clue_steps()
	cancel_gesture()

func set_mode(value: String) -> void:
	value = "G" if value == "R" else value
	if not value in ["G", "V"]:
		return
	cancel_gesture()
	mode = value
	overview = false
	hand = false
	viewport_layout_requested.emit()
	_layout()
	view_changed.emit()

func navigation_target(point: Vector2) -> String:
	if mode == "G" and layout_valid:
		var target: String = super.navigation_target(point)
		if target in ["row", "column"]:
			var index: int = navigation_line(point, target)
			if index >= 0 and int(clue_layout(target, index).max_offset) > 0:
				return target
	return ""

func navigate_to(_normalized: Vector2) -> void:
	pass

func zoom(direction: int, anchor: Vector2) -> void:
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
	if not session.gesture.active:
		requested_cell = 20.0
		_layout()
		view_changed.emit()

func fit_all() -> void:
	if not session.gesture.active:
		requested_cell = 0.0
		_layout()
		view_changed.emit()

func capture_view() -> Dictionary:
	var state: Dictionary = super.capture_view()
	# Fit values belong only to VS. Never put fractional/nonstandard zooms in Schema 1.
	state.zoom = 24
	state.overview = true
	state.tool = "erase" if eraser else "fill"
	state.center = [session.player.width / 2.0, session.player.height / 2.0]
	return state

func restore_view(state: Dictionary) -> void:
	var normalized: Dictionary = state.duplicate(true)
	normalized.tool = "fill" if normalized.get("tool") == "hand" else normalized.get("tool", "fill")
	normalized.center = [session.player.width / 2.0, session.player.height / 2.0]
	normalized.zoom = 24
	normalized.overview = true
	super.restore_view(normalized)
	_layout()

func pointer_press(point: Vector2, button: MouseButton) -> void:
	if layout_valid:
		super.pointer_press(point, button)

func _draw() -> void:
	if not layout_valid:
		if marks != null:
			marks.hide()
		draw_string(BODY_FONT, Vector2(12, 36), "PASST NICHT · Fenster vergrößern oder UI verkleinern.", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, INK)
		return
	super._draw()
	if marks != null:
		marks.visible = layout_valid

func clue_capacity(axis: String, _available_override: float = -1.0) -> int:
	return reserve_slots.x if axis == "row" else reserve_slots.y

# Full glyph + C1/AA + status-strike bounds in the moving direction. Status
# never reduces the geometry; the reserve is stable while solving or zooming.
func token_ink(text: String, axis: String, fs: int) -> Vector2:
	var key: String = "%s/%s/%d/%s" % [text, axis, fs, ui_scale]
	if ink_cache.has(key):
		return ink_cache[key]
	var width: float = clue_text_font(clue_font(), text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box: Rect2 = glyph_box(text, Vector2(-width / 2.0, clue_baseline_offset(fs)), fs)
	var result: Vector2 = Vector2(-box.position.x, box.end.x) if axis == "row" else Vector2(-box.position.y, box.end.y)
	ink_cache[key] = result
	return result

func sequence_units(entries: Array, capacity: int, origin_slot: int, shift: float, axis: String, fs: int, low: float, high: float) -> Dictionary:
	var pitch: float = (26.0 if axis == "row" else 18.0) * ui_scale
	var origin: float = high - capacity * pitch
	var candidates: Array[Dictionary] = []
	for i: int in range(entries.size()):
		var center: float = origin + (origin_slot + i + 0.5) * pitch + shift
		var ink: Vector2 = token_ink(str(entries[i].text), axis, fs)
		if center - ink.x >= low and center + ink.y <= high:
			candidates.append({"kind": "token", "index": i, "center": center, "before": ink.x, "after": ink.y})
	var prefix: bool = candidates.is_empty() or int(candidates[0].index) > 0
	var suffix: bool = candidates.is_empty() or int(candidates[-1].index) < entries.size() - 1
	var marker: Vector2 = token_ink("…", axis, fs)
	var start: float = origin + 0.5 * pitch
	var finish: float = origin + (capacity - 0.5) * pitch
	var units: Array[Dictionary] = []
	if prefix:
		units.append({"kind": "prefix", "index": -1, "center": start})
	for unit: Dictionary in candidates:
		if prefix and unit.center - unit.before < start + marker.y:
			continue
		if suffix and unit.center + unit.after > finish - marker.x:
			continue
		units.append(unit)
	if suffix:
		units.append({"kind": "suffix", "index": -1, "center": finish})
	return {"units": units, "prefix_hidden": prefix, "suffix_hidden": suffix}

# Visibility changes only at these glyph/area/marker boundaries. Testing both
# sides and each open interval proves the entire continuous drag, not samples.
func sequence_transitions(entries: Array, capacity: int, axis: String, fs: int) -> Array[float]:
	var pitch: float = (26.0 if axis == "row" else 18.0) * ui_scale
	var high: float = capacity * pitch + 6.0
	var maximum: float = (entries.size() - capacity + 1) * pitch
	var marker: Vector2 = token_ink("…", axis, fs)
	var boundaries: Dictionary = {0.0: true, maximum: true}
	for i: int in range(entries.size()):
		var center: float = 6.0 + (capacity - entries.size() + i + 0.5) * pitch
		var ink: Vector2 = token_ink(str(entries[i].text), axis, fs)
		for boundary: float in [ink.x - center, high - ink.y - center, 6.0 + pitch * 0.5 + marker.y + ink.x - center, 6.0 + pitch * 0.5 - marker.x - ink.y - center, high - pitch * 0.5 + marker.y + ink.x - center, high - pitch * 0.5 - marker.x - ink.y - center]:
			if boundary > 0.0 and boundary < maximum:
				boundaries[boundary] = true
	var points: Array = boundaries.keys()
	points.sort()
	var result: Array[float] = []
	for i: int in range(points.size()):
		result.append(points[i])
		if i > 0:
			result.append((points[i-1] + points[i]) / 2.0)
	return result

func required_slots(axis: String) -> int:
	var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
	var key: String = "%s/%s/%s" % [JSON.stringify(lines), axis, ui_scale]
	if reserve_cache.has(key):
		return int(reserve_cache[key])
	var maximum: int = max_hints.x if axis == "row" else max_hints.y
	var chosen: int = maximum
	for capacity: int in range(mini(maximum, 5), maximum + 1):
		if suitable_slots(axis, capacity):
			chosen = capacity
			break
	reserve_cache[key] = chosen
	return chosen

func suitable_slots(axis: String, capacity: int) -> bool:
	var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
	var key: String = "safe/%s/%s/%s/%d" % [JSON.stringify(lines), axis, ui_scale, capacity]
	if reserve_cache.has(key):
		return bool(reserve_cache[key])
	var suitable: bool = true
	for line: Array in lines:
		if line.size() <= capacity:
			continue
		var entries: Array = clue_entries(line)
		for fs: int in range(Fonts.pixel_size(font_choice, 8), Fonts.pixel_size(font_choice, roundi(14 * ui_scale)) + 1):
			for shift: float in sequence_transitions(entries, capacity, axis, fs):
				var drawn: Array = sequence_units(entries, capacity, capacity - entries.size(), shift, axis, fs, 0.0, capacity * (26.0 if axis == "row" else 18.0) * ui_scale + 6.0).units
				if drawn.filter(func(unit: Dictionary) -> bool: return unit.kind == "token").size() < mini(5, line.size()):
					suitable = false
					break
			if not suitable: break
		if not suitable: break
	reserve_cache[key] = suitable
	return suitable

func visual_hint_units(axis: String, index: int) -> Dictionary:
	var layout: Dictionary = visible_clue_layout(axis, index)
	if is_zero_approx(float(layout.visual_shift)):
		return super.visual_hint_units(axis, index)
	var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
	return sequence_units(layout.entries, int(layout.slot_count), int(layout.token_slot) - int(layout.start), float(layout.visual_shift), axis, clue_font_size(), area.position.x if axis == "row" else area.position.y, area.end.x if axis == "row" else area.end.y)

func _draw_row_hint(index: int, py: float, font: Font, fs: int) -> void:
	draw_hint_units("row", index, py, font, fs)

func _draw_column_hint(index: int, px: float, font: Font, fs: int) -> void:
	draw_hint_units("column", index, px, font, fs)

func draw_hint_units(axis: String, index: int, cross: float, font: Font, fs: int) -> void:
	var layout: Dictionary = visible_clue_layout(axis, index)
	for unit: Dictionary in visual_hint_units(axis, index).units:
		var text: String = "…" if unit.kind != "token" else str(layout.entries[int(unit.index)].text)
		var color: Color = ACCENT if unit.kind != "token" else Color(layout.entries[int(unit.index)].color)
		var width: float = clue_text_font(font, text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var baseline: Vector2 = Vector2(float(unit.center) - width/2.0, cross + clue_baseline_offset(fs)) if axis == "row" else Vector2(cross - width/2.0, float(unit.center) + clue_baseline_offset(fs))
		draw_clue_number(font, baseline, text, fs, color, clue_status(axis, index, int(unit.index)))

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
	var axis_counts: Dictionary = {}
	for axis: String in ["row", "column"]:
		var area: Rect2 = row_clue_area() if axis == "row" else column_clue_area()
		var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
		var boxes: Array[Rect2] = []
		var visible_numbers: int = 0
		var total_numbers: int = 0
		var visible_by_line: Array[int] = []
		for index: int in range(lines.size()):
			var layout: Dictionary = clue_layout(axis, index)
			var visible_line: int = 0
			total_numbers += lines[index].size()
			hidden += int(layout.start) + int(layout.entries.size()) - int(layout.end)
			for unit: Dictionary in visual_hint_units(axis, index).units:
				if unit.kind == "token" and not lines[index].is_empty():
					visible_line += 1
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
			visible_numbers += visible_line
			visible_by_line.append(visible_line)
		axis_counts[axis] = {"visible_numbers": visible_numbers, "hidden_numbers": total_numbers - visible_numbers, "total_numbers": total_numbers, "visible_by_line": visible_by_line}
		if not boxes.is_empty():
			var union: Rect2 = boxes[0]
			for box: Rect2 in boxes:
				union = union.merge(box)
			extents[axis] = rect_values(union)
	var grid_frame: Rect2 = view.bounds().grow(FRAME_MARGIN)
	var grid_fit: bool = view.viewport.grow(0.01).encloses(grid_frame) and layout_valid
	var complete: bool = grid_fit and hidden == 0 and clipped == 0 and collisions == 0
	var original_grid: Rect2 = view.bounds()
	original_grid.position.x -= horizontal_used
	var original_rows: Rect2 = row_clue_area()
	original_rows.size.x -= horizontal_used
	var original_columns: Rect2 = column_clue_area()
	original_columns.position.x -= horizontal_used
	var fit_dimensions: Vector2 = (size - Vector2(minimum_slots) * Vector2(26,18) * ui_scale - Vector2(14,14)) / Vector2(view.dimensions)
	return {"mode": mode, "cell_pitch": view.cell_size, "raw_fit_ceiling": raw_fit, "zoom_ceiling": fit_ceiling, "reserve_slots": [reserve_slots.x,reserve_slots.y],
		"minimum_reserve_slots": [minimum_slots.x,minimum_slots.y], "axis_counts": axis_counts,
		"horizontal_budget_px": horizontal_budget, "horizontal_used_px": horizontal_used, "horizontal_remaining_px": horizontal_budget-horizontal_used,
		"minimum_grid": rect_values(original_grid), "minimum_row_clues": rect_values(original_rows), "minimum_column_clues": rect_values(original_columns),
		"fit_axis_cells": [fit_dimensions.x,fit_dimensions.y], "limiting_axis": "width" if fit_dimensions.x < fit_dimensions.y else "height", "frame_area_px": grid_frame.get_area(),
		"grid": rect_values(view.bounds()), "grid_frame": rect_values(grid_frame), "viewport": rect_values(view.viewport), "row_clues": rect_values(row_clue_area()), "column_clues": rect_values(column_clue_area()),
		"font_px": fs, "glyph_max": [largest.x, largest.y], "glyph_extents": extents, "glyph_count": glyph_count,
		"clipped_glyphs": clipped, "glyph_collisions": collisions, "hidden_tokens": hidden, "grid_fit": grid_fit, "full_sheet_fit": complete,
		"grid_navigation_needed": not grid_fit, "hint_navigation_needed": hidden > 0, "layout_valid": layout_valid,
		"geometry_rendered": layout_valid, "glyph_risk": glyph_risk,
		"max_row_hints": session.definition.rows.map(func(x: Array) -> int: return x.size()).max(),
		"max_column_hints": session.definition.columns.map(func(x: Array) -> int: return x.size()).max(),
		"status": "geometric_fit_owner_open" if (complete if mode == "V" else grid_fit) and view.cell_size >= 16 and collisions == 0 and clipped == 0 else "restricted_or_failed_owner_open"}
