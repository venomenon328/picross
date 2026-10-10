extends RefCounted
## Independent corridor oracle, using actual renderer output, not its constants.
static func strokes(b: Control) -> Array:
	var result: Array = []
	var box: Rect2 = b.view.bounds()
	for axis: String in ["row","column"]:
		var horizontal: bool = axis == "row"
		var count: int = b.session.player.height if horizontal else b.session.player.width
		for index: int in range(count+1):
			var start: Vector2 = box.position + (Vector2(0,index*b.view.cell_size) if horizontal else Vector2(index*b.view.cell_size,0))
			var end: Vector2 = start + (Vector2(box.size.x,0) if horizontal else Vector2(0,box.size.y))
			var line: Dictionary = b.grid_stroke(start,end,axis,index)
			line.axis = axis
			line.index = index
			result.append(line)
	return result

static func within_budget(lines: Array, grid: Rect2) -> bool:
	for line: Dictionary in lines:
		if line.width < 0.7 or line.width > 1.64001: return false
		for point: Vector2 in line.points:
			# One physical pixel for antialiasing beyond half the actual stroke.
			var extent: Rect2 = Rect2(point,Vector2.ZERO).grow(line.width/2.0+1.0)
			if not grid.grow(1.001).encloses(extent): return false
	return true

static func layout(app: Control, check: Callable) -> Dictionary:
	var b = app.board
	for spec: Array in [[app.surface.card,"miniature-mount"],[app.surface.palette,"palette-mount"]]:
		var mount: Array = app.surface.mount_strokes(spec[0],spec[1])
		check.call(mount == app.surface.mount_strokes(spec[0],spec[1]),"V2 stable mount geometry")
		check.call(element_fits(mount,spec[0].grow(2)),"V2 actual mount stroke/AA within V1 group envelope")
	check.call(element_fits(app.mini.frame_strokes(),app.mini.image_rect().grow(1)),"V2 miniature frame stroke/AA bounded")
	for item: Control in app.palette_row.get_children():
		check.call(element_fits(item.swatch_strokes(),Rect2(Vector2.ZERO,item.size).grow(1)),"V2 palette stroke/AA within group envelope")
	if not b.layout_valid: return {"valid":false}
	var lines: Array = strokes(b)
	check.call(within_budget(lines,b.view.bounds()),"V2 actual stroke/AA fits unchanged frame budget")
	check.call(lines == strokes(b),"V2 pure stable line geometry")
	var bent: int = 0
	for line: Dictionary in lines:
		var points: PackedVector2Array = line.points
		for i: int in range(1,points.size()-1):
			var straight: Vector2 = points[0].lerp(points[-1],float(i)/(points.size()-1))
			check.call(points[i].distance_to(straight) <= 0.2801,"V3 bounded deviation supersedes V2 amplitude")
			if points[i].distance_to(straight) > 0.01: bent += 1
	check.call(b.view.cell_size < 6.0 or bent > 0,"V2 varied grid at readable size; tiny cells deliberately fade")
	return {"valid":true,"lines":lines.size(),"bent_points":bent,"geometry_sha256":JSON.stringify(lines).sha256_text(),"outer_budget":1.0}

static func element_fits(lines: Array, envelope: Rect2) -> bool:
	for line: Dictionary in lines:
		for p: Vector2 in line.points:
			if not envelope.grow(0.001).encloses(Rect2(p,Vector2.ZERO).grow(line.width/2+1.0)): return false
	return true
