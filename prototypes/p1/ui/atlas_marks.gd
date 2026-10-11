extends Control
## Bounded Canvas command caches. No raster bitmap, cell nodes or cell timers.
const Atlas = preload("res://ui/cell_atlas.gd")
const CHUNK_SIZE = 64
var board: Control
var chunks: Array[Control] = []
var transitions: Control
var cursor_layer: Control
var values: Array[int] = []
var variants: PackedInt32Array = PackedInt32Array()
var suppressed: Dictionary = {}
var geometry: Array = []
var identity: String = ""
var cursor_state: Array = []
var stats: Dictionary = {"rest_draws": 0, "rest_cells": 0, "transition_draws": 0, "transition_cells": 0, "cursor_draws": 0, "syncs": 0}
var textures: Dictionary = {}
var ink_material: ShaderMaterial

class Chunk extends Control:
	var owner_marks: Control
	var start: int
	func _draw() -> void:
		var began: int = Time.get_ticks_usec()
		owner_marks.stats.rest_draws += 1
		for index: int in range(start, mini(start + CHUNK_SIZE, owner_marks.values.size())):
			owner_marks.stats.rest_cells += 1
			if not owner_marks.suppressed.has(index):
				owner_marks.paint(self, index, owner_marks.values[index], 23, 1.0)
		owner_marks.record_time(began)

class Transitions extends Control:
	var owner_marks: Control
	func _draw() -> void:
		var began: int = Time.get_ticks_usec()
		owner_marks.stats.transition_draws += 1
		for index: int in owner_marks.suppressed:
			owner_marks.stats.transition_cells += 1
			var state: Dictionary = owner_marks.presentation(index)
			owner_marks.paint(self, index, int(state.value), int(state.frame), float(state.alpha))
		owner_marks.record_time(began)

class Cursor extends Control:
	var owner_marks: Control
	func _draw() -> void:
		var began: int = Time.get_ticks_usec()
		owner_marks.stats.cursor_draws += 1
		var b: Control = owner_marks.board
		var active: Vector2i = b.session.gesture.endpoint if b.session.gesture.active else b.hover
		var grid: Rect2 = b.view.visible_bounds()
		if not b.book_layout:
			draw_style_box(b._paper_style(),Rect2(Vector2.ZERO,b.size))
			draw_rect(grid,b.PAPER)
		if active.x >= 0 and active.y >= 0 and active.x < b.view.dimensions.x and active.y < b.view.dimensions.y:
			var box: Rect2 = b.view.cell_rect(active)
			var near_grid: Vector2 = grid.position
			# Same clue bands as Board; below the cached clue glyphs.
			if b.hover.y >= 0:
				draw_rect(Rect2(4, box.position.y, near_grid.x-8, box.size.y), Color("d8ddcc"))
			if b.hover.x >= 0:
				draw_rect(Rect2(box.position.x, 4, box.size.x, near_grid.y-8), Color("d8ddcc"))
			var row: Rect2 = Rect2(grid.position.x, box.position.y, grid.size.x, box.size.y).intersection(grid)
			var column: Rect2 = Rect2(box.position.x, grid.position.y, box.size.x, grid.size.y).intersection(grid)
			draw_rect(row, Color("e8e9d9"))
			draw_rect(Rect2(column.position, Vector2(column.size.x, maxf(0, row.position.y-column.position.y))), Color("e8e9d9"))
			draw_rect(Rect2(Vector2(column.position.x, row.end.y), Vector2(column.size.x, maxf(0, column.end.y-row.end.y))), Color("e8e9d9"))
		owner_marks.record_time(began)

func _ready() -> void:
	# Shared for the lifetime of this SceneTree; at most six textures/one material.
	var tree: SceneTree = get_tree()
	if not tree.has_meta("cell_atlas_resources"):
		var loaded: Dictionary = {}
		for kind: String in ["fill", "x"]:
			for lod: String in ["small", "medium", "large"]:
				loaded[kind + "-" + lod] = load("res://art/cells/" + kind + "-" + lod + ".png")
		var shared := ShaderMaterial.new()
		shared.shader = preload("res://ui/atlas_mask.gdshader")
		tree.set_meta("cell_atlas_resources", {"textures": loaded, "material": shared})
	var resources: Dictionary = tree.get_meta("cell_atlas_resources")
	textures = resources.textures
	ink_material = resources.material
	cursor_layer = Cursor.new()
	cursor_layer.owner_marks = self
	cursor_layer.show_behind_parent = true
	cursor_layer.mouse_filter = MOUSE_FILTER_IGNORE
	add_child(cursor_layer)
	transitions = Transitions.new()
	transitions.owner_marks = self
	transitions.material = ink_material
	transitions.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	transitions.texture_repeat = CanvasItem.TEXTURE_REPEAT_DISABLED
	transitions.mouse_filter = MOUSE_FILTER_IGNORE
	add_child(transitions)

func record_time(began: int) -> void:
	if board.measure_draws:
		board.draw_times_us.append(Time.get_ticks_usec() - began)

func sync() -> void:
	if board.session == null or transitions == null:
		return
	var began: int = Time.get_ticks_usec()
	stats.syncs += 1
	var definition: Dictionary = board.session.definition
	var next_identity: String = "%s/%s/%s" % [definition.id, definition.revision, board.view.dimensions]
	var cells: Array[int] = board.session.player.cells
	var next_geometry: Array = [board.session.get_instance_id(), board.view.origin, board.view.viewport, board.view.cell_size, board.style, definition.palette]
	var all_dirty: bool = next_geometry != geometry or values.size() != cells.size()
	if next_identity != identity:
		identity = next_identity
		variants.resize(cells.size())
		for i: int in range(cells.size()):
			variants[i] = Atlas.variant(str(definition.id), int(definition.revision), Vector2i(i % board.view.dimensions.x, i / board.view.dimensions.x))
		all_dirty = true
	var count: int = ceili(float(cells.size()) / CHUNK_SIZE)
	while chunks.size() > count:
		var old: Control = chunks.pop_back()
		remove_child(old)
		old.queue_free()
	while chunks.size() < count:
		var chunk := Chunk.new()
		chunk.owner_marks = self
		chunk.start = chunks.size() * CHUNK_SIZE
		chunk.material = ink_material
		chunk.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		chunk.texture_repeat = CanvasItem.TEXTURE_REPEAT_DISABLED
		chunk.mouse_filter = MOUSE_FILTER_IGNORE
		add_child(chunk)
		move_child(chunk, get_child_count() - 2)
		chunks.append(chunk)
	var dirty: Dictionary = {}
	if not all_dirty and cells != values:
		for i: int in range(cells.size()):
			if cells[i] != values[i]: dirty[i / CHUNK_SIZE] = true
	if cells != values: values = cells.duplicate()
	geometry = next_geometry
	var next_suppressed: Dictionary = {}
	for i: int in board.effects: next_suppressed[i] = true
	for i: int in board.preview: next_suppressed[i] = true
	for i: int in suppressed:
		if not next_suppressed.has(i): dirty[i / CHUNK_SIZE] = true
	for i: int in next_suppressed:
		if not suppressed.has(i): dirty[i / CHUNK_SIZE] = true
	suppressed = next_suppressed
	if all_dirty:
		for chunk: Control in chunks: chunk.queue_redraw()
	else:
		for c: int in dirty: chunks[c].queue_redraw()
	if all_dirty or not suppressed.is_empty() or not dirty.is_empty():
		transitions.queue_redraw()
		queue_redraw()
	sync_cursor()
	record_time(began)

func sync_cursor() -> void:
	if cursor_layer == null or board.session == null: return
	var state: Array = [board.hover, board.session.gesture.active, board.session.gesture.endpoint, board.view.origin, board.view.viewport, board.view.cell_size, board.size, board.book_layout]
	if state != cursor_state:
		cursor_state = state
		cursor_layer.queue_redraw()

func tick() -> void:
	# Membership changes restore only the affected resting chunks; ongoing frames
	# never invalidate the unchanged resting population.
	sync()
	transitions.queue_redraw()
	queue_redraw()

func presentation(index: int) -> Dictionary:
	var value: int = values[index]
	var frame: int = 23
	var alpha: float = 1.0
	var progress: float = 1.0
	if board.preview.has(index):
		value = int(board.preview[index])
		alpha = board.PREVIEW_ALPHA
	elif board.effects.has(index):
		var effect: Dictionary = board.effects[index]
		value = int(effect.after)
		var elapsed: int = int(board.animation_clock.call()) - int(effect.start)
		if elapsed < 0: alpha = board.PREVIEW_ALPHA
		else:
			frame = Atlas.frame(elapsed)
			progress = clampf(float(elapsed) / (float(effect.seconds) * 1000000.0), 0, 1)
	return {"value": value, "frame": frame, "alpha": alpha, "progress": progress}

func paint(canvas: CanvasItem, index: int, value: int, frame: int, alpha: float) -> void:
	if value < 0 or (value > 0 and board.view.cell_size <= 4.0): return
	var cell: Rect2 = board.view.cell_rect(Vector2i(index % board.view.dimensions.x, index / board.view.dimensions.x))
	var lod: String = Atlas.level(board.view.cell_size)
	var target: Rect2 = Atlas.mapped_box(cell, lod) if value > 0 else cell
	var clipped: Rect2 = target.intersection(board.view.viewport)
	if not clipped.has_area(): return
	var source: Rect2 = Atlas.region(lod, variants[index], frame)
	var ratio: Vector2 = source.size / target.size
	source = Rect2(source.position + (clipped.position-target.position)*ratio, clipped.size*ratio)
	var color: Color = board.cell_color(value) if value > 0 else board.INK
	color.a = alpha
	canvas.draw_texture_rect_region(textures[("fill" if value > 0 else "x") + "-" + lod], clipped, source, color, false, true)

func _draw() -> void:
	# Neutral erasure contours have no coefficient material or previous ink.
	var began: int = Time.get_ticks_usec()
	if board.session != null:
		for i: int in suppressed:
			var state: Dictionary = presentation(i)
			if int(state.value) >= 0: continue
			var box: Rect2 = board.view.cell_rect(Vector2i(i % board.view.dimensions.x, i / board.view.dimensions.x)).grow(-2)
			var alpha: float = 0.32 * (1.0 if board.preview.has(i) else 1.0-float(state.progress))
			var points: Array[Vector2] = [box.position, Vector2(box.end.x,box.position.y),box.end,Vector2(box.position.x,box.end.y)]
			for k: int in range(4):
				var segment: PackedVector2Array = board.clipped_segment(points[k],points[(k+1)%4],board.view.viewport.grow(-1.4))
				if segment.size()==2 and segment[0].distance_to(segment[1])>0.01:
					draw_line(segment[0],segment[1],Color(board.INK,alpha),0.8,true)
	record_time(began)
