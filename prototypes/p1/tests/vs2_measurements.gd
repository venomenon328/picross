extends RefCounted
## Developer-only matrix diagnosis; never part of the regular PCK.
static func rect_values(rect: Rect2) -> Array:
	return [rect.position.x, rect.position.y, rect.size.x, rect.size.y]

static func capture(board) -> Dictionary:
	var session = board.session
	var view = board.view
	var ui_scale = board.ui_scale
	var size = board.size
	var mode = board.mode
	var raw_fit = board.raw_fit
	var fit_ceiling = board.fit_ceiling
	var reserve_slots = board.reserve_slots
	var minimum_slots = board.minimum_slots
	var horizontal_budget = board.horizontal_budget
	var horizontal_used = board.horizontal_used
	var layout_valid = board.layout_valid
	var glyph_risk = board.glyph_risk
	var fs: int = board.clue_font_size()
	var clipped: int = 0
	var collisions: int = 0
	var hidden: int = 0
	var glyph_count: int = 0
	var largest: Vector2 = Vector2.ZERO
	var extents: Dictionary = {}
	var axis_counts: Dictionary = {}
	for axis: String in ["row", "column"]:
		var area: Rect2 = board.row_clue_area() if axis == "row" else board.column_clue_area()
		var lines: Array = session.definition.rows if axis == "row" else session.definition.columns
		var boxes: Array[Rect2] = []
		var buckets: Dictionary = {}
		var visible_numbers: int = 0
		var total_numbers: int = 0
		var visible_by_line: Array[int] = []
		for index: int in range(lines.size()):
			var layout: Dictionary = board.clue_layout(axis, index)
			var visible_line: int = 0
			total_numbers += lines[index].size()
			hidden += int(layout.start) + int(layout.entries.size()) - int(layout.end)
			for unit: Dictionary in board.visual_hint_units(axis, index).units:
				if unit.kind == "token" and not lines[index].is_empty():
					visible_line += 1
				var text: String = "…" if unit.kind != "token" else str(layout.entries[int(unit.index)].text)
				var width: float = board.clue_text_font(board.clue_font(), text).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
				var cross: float = (view.origin.y if axis == "row" else view.origin.x) + (index + 0.5) * view.cell_size
				var baseline: Vector2 = Vector2(float(unit.center) - width / 2.0, cross + board.clue_baseline_offset(fs)) if axis == "row" else Vector2(cross - width / 2.0, float(unit.center) + board.clue_baseline_offset(fs))
				var box: Rect2 = board.glyph_box(text, baseline, fs)
				largest = largest.max(box.size)
				glyph_count += 1
				if not area.grow(0.01).encloses(box):
					clipped += 1
				var tested: Dictionary = {}
				for bx: int in range(floori(box.position.x/16),floori(box.end.x/16)+1):
					for by: int in range(floori(box.position.y/16),floori(box.end.y/16)+1):
						var bucket: Vector2i = Vector2i(bx,by)
						for prior: int in buckets.get(bucket,[]):
							if not tested.has(prior) and boxes[prior].intersects(box): collisions += 1
							tested[prior] = true
						if not buckets.has(bucket): buckets[bucket] = []
						buckets[bucket].append(boxes.size())
				boxes.append(box)
			visible_numbers += visible_line
			visible_by_line.append(visible_line)
		axis_counts[axis] = {"visible_numbers": visible_numbers, "hidden_numbers": total_numbers - visible_numbers, "total_numbers": total_numbers, "visible_by_line": visible_by_line}
		if not boxes.is_empty():
			var union: Rect2 = boxes[0]
			for box: Rect2 in boxes:
				union = union.merge(box)
			extents[axis] = rect_values(union)
	var grid_frame: Rect2 = view.bounds().grow(1.0)
	var grid_fit: bool = view.viewport.grow(0.01).encloses(grid_frame) and layout_valid
	var complete: bool = grid_fit and hidden == 0 and clipped == 0 and collisions == 0
	var original_grid: Rect2 = view.bounds()
	original_grid.position.x -= horizontal_used
	var original_rows: Rect2 = board.row_clue_area()
	original_rows.size.x -= horizontal_used
	var original_columns: Rect2 = board.column_clue_area()
	original_columns.position.x -= horizontal_used
	var fit_dimensions: Vector2 = (size - Vector2(minimum_slots) * Vector2(26,18) * ui_scale - Vector2(14,14)) / Vector2(view.dimensions)
	return {"mode": mode, "cell_pitch": view.cell_size, "raw_fit_ceiling": raw_fit, "zoom_ceiling": fit_ceiling, "reserve_slots": [reserve_slots.x,reserve_slots.y],
		"minimum_reserve_slots": [minimum_slots.x,minimum_slots.y], "axis_counts": axis_counts,
		"horizontal_budget_px": horizontal_budget, "horizontal_used_px": horizontal_used, "horizontal_remaining_px": horizontal_budget-horizontal_used,
		"minimum_grid": rect_values(original_grid), "minimum_row_clues": rect_values(original_rows), "minimum_column_clues": rect_values(original_columns),
		"fit_axis_cells": [fit_dimensions.x,fit_dimensions.y], "limiting_axis": "width" if fit_dimensions.x < fit_dimensions.y else "height", "frame_area_px": grid_frame.get_area(),
		"grid": rect_values(view.bounds()), "grid_frame": rect_values(grid_frame), "viewport": rect_values(view.viewport), "row_clues": rect_values(board.row_clue_area()), "column_clues": rect_values(board.column_clue_area()),
		"font_px": fs, "glyph_max": [largest.x, largest.y], "glyph_extents": extents, "glyph_count": glyph_count,
		"clipped_glyphs": clipped, "glyph_collisions": collisions, "hidden_tokens": hidden, "grid_fit": grid_fit, "full_sheet_fit": complete,
		"grid_navigation_needed": not grid_fit, "hint_navigation_needed": hidden > 0, "layout_valid": layout_valid,
		"geometry_rendered": layout_valid, "glyph_risk": glyph_risk,
		"max_row_hints": session.definition.rows.map(func(x: Array) -> int: return x.size()).max(),
		"max_column_hints": session.definition.columns.map(func(x: Array) -> int: return x.size()).max(),
		"status": "geometric_fit_owner_open" if (complete if mode == "V" else grid_fit) and view.cell_size >= 16 and collisions == 0 and clipped == 0 else "restricted_or_failed_owner_open"}
