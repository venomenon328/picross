extends RefCounted
static func rect_values(rect: Rect2) -> Array:
	return [rect.position.x,rect.position.y,rect.size.x,rect.size.y]

static func near(a: Vector2, b: Vector2) -> bool:
	return a.distance_to(b) < 0.02

static func label_ink(label: Label) -> Rect2:
	var paragraph: TextParagraph = TextParagraph.new()
	paragraph.width = label.size.x if label.autowrap_mode != TextServer.AUTOWRAP_OFF else -1
	paragraph.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	paragraph.add_string(label.text,label.get_theme_font("font"),label.get_theme_font_size("font_size"))
	var extent: Vector2 = Vector2.ZERO
	for line: int in range(paragraph.get_line_count()):
		var line_size: Vector2 = paragraph.get_line_size(line)
		extent.x = maxf(extent.x,line_size.x)
		extent.y += line_size.y + (label.get_theme_constant("line_spacing") if line > 0 else 0)
	return Rect2(label.global_position,extent).grow(1)

static func layout(app: Control, check: Callable) -> Dictionary:
	var b = app.board
	var u: float = app.ui_scale
	var grid: Rect2 = b.view.bounds()
	var rows: Rect2 = b.row_clue_area()
	var columns: Rect2 = b.column_clue_area()
	var shift: Vector2 = b.composition_shift
	var dimensions: Vector2 = Vector2(b.session.player.width, b.session.player.height)
	var independent_fit: float = minf((b.size.x-b.minimum_slots.x*24*u-14)/dimensions.x, (b.size.y-b.minimum_slots.y*18*u-14)/dimensions.y)
	check.call(is_equal_approx(b.raw_fit, independent_fit), "V1 fit uses unchanged safe budget before translation")
	check.call(b.reserve_slots.x <= b.max_hints.x and b.reserve_slots.y <= b.max_hints.y, "V1 no artificial empty slots")
	check.call(near(grid.position-shift, Vector2(b.reserve_slots.x*24*u+7, b.reserve_slots.y*18*u+7)), "V1 raster and both reserves share translation")
	check.call(near(rows.position, Vector2(shift.x, grid.position.y)) and near(columns.position, Vector2(grid.position.x, shift.y)), "V1 hint hit regions translate with raster")
	check.call(near(grid.size, dimensions*b.view.cell_size), "V1 translation never changes cell scale")
	check.call(b.shared_clue_slot_extent("row",b.clue_font(),b.clue_font_size()) == 24*u and b.shared_clue_slot_extent("column",b.clue_font(),b.clue_font_size()) == 18*u, "V1 fixed independent pitch targets")
	var occupied: Rect2 = b.composition_envelope()
	if b.layout_valid:
		check.call(Rect2(Vector2.ZERO,b.size).grow(0.02).encloses(grid.grow(1)), "V1 full frame within original safe budget")
		if shift.x > 0:
			check.call(absf(occupied.position.x-(b.size.x-occupied.end.x)) <= 1.01, "V1 free horizontal space balanced")
		if shift.y > 0:
			check.call(absf(occupied.position.y-(b.size.y-occupied.end.y)) <= 1.01, "V1 free vertical space balanced")
	var paper: Rect2 = app.surface.material_rect()
	# Inner paper measured from the unchanged A background, excluding wood/fold.
	var inner: Rect2 = Rect2(paper.position+paper.size*Vector2(0.03125,0.034),paper.size*Vector2(0.93125,0.933))
	var boxes: Array[Rect2] = [app.surface.card.grow(2),app.mini.get_global_rect().grow(1),app.surface.palette.grow(2)]
	for label: Label in [app.mini_title,app.coordinate,app.zoom_label,app.tool_label,app.stress_label]:
		if label.is_visible_in_tree() and not label.text.is_empty(): boxes.append(label_ink(label))
	for item: Control in app.palette_row.get_children():
		check.call(item.size.x >= 44*u and item.size.y >= 44*u,"V1 unchanged color minimum hit size")
		boxes.append(item.get_global_rect().grow(1))
	var group: Rect2 = boxes[0]
	for box: Rect2 in boxes:
		group = group.merge(box)
		check.call(inner.grow(0.1).encloses(box),"V1 group inside actual inner paper %s %s u%s box%s inner%s" % [app.session.definition.id,app.size,u,box,inner])
		check.call(not box.intersects(app.board.get_global_rect()),"V1 group clear of whole safe board area")
		for id: String in ["help","menu","nav-information"]:
			check.call(not box.intersects(app.actions[id].get_global_rect()),"V1 group clear of page controls")
		for item: Control in [app.status_label,app.work_repair_button]:
			if item.is_visible_in_tree(): check.call(not box.intersects(item.get_global_rect()),"V1 group clear of recovery card")
	if app.work_repair_button.is_visible_in_tree():
		check.call(not app.work_repair_button.get_global_rect().intersects(app.board.get_global_rect()),"V1 recovery action clear of board")
		check.call(app.work_repair_button.size.y >= 44*u,"V1 recovery minimum hit size")
	var old_mini: Vector2 = paper.position+Vector2(paper.size.x-248*u,maxf(paper.size.y*0.039+51*u,82*u)+30*u)
	var group_delta: Vector2 = app.mini.global_position-old_mini
	check.call(is_equal_approx(group_delta.x,-16*u) and group_delta.y >= 0 and group_delta.y <= 24*u+0.01,"V1 bounded whole-group movement")
	if paper.size.x >= 1920 and paper.size.y >= 1080:
		check.call(is_equal_approx(group_delta.y,24*u),"V1 generous group moves down")
	return {"id":app.session.definition.id,"client":[app.size.x,app.size.y],"ui_scale":u,"mode":b.mode,"overview":b.overview,
		"safe":rect_values(b.get_global_rect()),"occupied":rect_values(occupied),"translation":[shift.x,shift.y],
		"grid":rect_values(grid),"rows":rect_values(rows),"columns":rect_values(columns),
		"requested_cell":b.requested_cell,"actual_cell":b.view.cell_size,"raw_fit":b.raw_fit,"independent_fit":independent_fit,
		"font_px":b.clue_font_size(),"row_pitch":24*u,"column_pitch":18*u,
		"reserve":[b.reserve_slots.x,b.reserve_slots.y],"max_hints":[b.max_hints.x,b.max_hints.y],
		"minimum_reserve":[b.minimum_slots.x,b.minimum_slots.y],"dimensions":[dimensions.x,dimensions.y],
		"untranslated_grid":rect_values(b.untranslated_grid),"untranslated_occupied":rect_values(b.untranslated_occupied),
		"margins":[occupied.position.x,occupied.position.y,b.size.x-occupied.end.x,b.size.y-occupied.end.y],
		"inner_paper":rect_values(inner),"group":rect_values(group),"group_delta":[group_delta.x,group_delta.y],"recovery":app.work_repair_button.is_visible_in_tree()}
