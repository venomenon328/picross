extends "res://ui/reveal.gd"
## Transient presentation only. No session, persistence, input or deferred navigation.
signal progressed(work_alpha: float, caption_alpha: float)
signal finished
const DURATION := 2.15
const Atlas = preload("res://ui/cell_atlas.gd")
const Scribble = preload("res://ui/scribble.gd")
var grid_selected := false
var identity: String
var revision: int
var stable_ink: Layer
var stable_lines: Control
var stable_key: Array = []
var strokes: Array = []
var active := false
var elapsed := 0.0
var started_usec: int = 0
var source: Rect2
var area: Rect2
var ink: Layer
var raster: Layer
var art: Layer

class Layer extends Control:
	var commands: Array = []
	func _draw() -> void:
		for command: Array in commands:
			if command.size() == 2:
				draw_rect(command[0], command[1])
			else:
				draw_texture_rect_region(command[0], command[1], command[2], command[3], false, true)

class Lines extends Control:
	var presentation: Control
	func _draw() -> void:
		for line: Dictionary in presentation.strokes:
			Scribble.paint(self, line, line.color)

func _ready() -> void:
	paired = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for kind: String in ["ink", "raster", "art"]:
		var layer := Layer.new()
		layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		add_child(layer)
		set(kind, layer)
	stable_ink = Layer.new()
	stable_ink.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stable_ink.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	stable_ink.texture_repeat = CanvasItem.TEXTURE_REPEAT_DISABLED
	add_child(stable_ink)
	stable_lines = Lines.new()
	stable_lines.presentation = self
	stable_lines.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(stable_lines)
	_update_selection()
	set_process(false)

func contained(extent: Vector2) -> Rect2:
	if extent.x <= 0 or extent.y <= 0: return Rect2()
	var fitted := extent * minf(area.size.x / extent.x, area.size.y / extent.y)
	return Rect2(area.get_center() - fitted / 2, fitted)

func raster_rect() -> Rect2:
	return Rect2() if solved.is_empty() else contained(Vector2(solved[0].size(), solved.size()))

func artwork_rect() -> Rect2:
	return Rect2() if artwork == null else contained(artwork.get_size())

func configure(next_payload: Dictionary, matrix: Array, colors: Array, bounds: Rect2, puzzle_id: String, puzzle_revision: int) -> void:
	if payload != next_payload: payload = next_payload
	solved = matrix.duplicate(true)
	palette = colors.duplicate(true)
	area = bounds
	identity = puzzle_id
	revision = puzzle_revision
	art.commands.clear()
	if artwork != null:
		var display: Texture2D = display_texture(artwork_rect())
		art.commands.append([display, artwork_rect(), Rect2(Vector2.ZERO, display.get_size()), Color.WHITE])
	art.queue_redraw()
	_configure_grid()
	_update_selection()

func _configure_grid() -> void:
	var key: Array = [solved, palette, area, identity, revision]
	if key == stable_key: return
	stable_key = key.duplicate(true)
	stable_ink.commands.clear()
	strokes.clear()
	if not solved.is_empty():
		var resources: Dictionary = get_tree().get_meta("cell_atlas_resources")
		stable_ink.material = resources.material
		var rect := raster_rect()
		var step: float = rect.size.x / solved[0].size()
		var lod := Atlas.level(step)
		# Below the work-board minimum keep the whole miniature readable, with
		# proportionally reduced gaps rather than dropping confirmed fills.
		var reference := maxf(8.0, step)
		for y: int in range(solved.size()):
			for x: int in range(solved[y].size()):
				var value: int = int(solved[y][x])
				if value <= 0: continue
				for entry: Dictionary in palette:
					if int(entry.id) != value: continue
					var box := Atlas.mapped_box(Rect2(Vector2.ZERO, Vector2.ONE * reference), lod)
					box = Rect2(rect.position + Vector2(x,y)*step + box.position*step/reference, box.size*step/reference)
					stable_ink.commands.append([resources.textures["fill-"+lod], box,
						Atlas.region(lod, Atlas.variant(identity, revision, Vector2i(x,y)), Atlas.FRAMES-1), Color(entry.color)])
		for axis: String in ["row", "column"]:
			var limit: int = solved.size() if axis == "row" else solved[0].size()
			for index: int in range(limit+1):
				var start := rect.position + (Vector2(0,index*step) if axis == "row" else Vector2(index*step,0))
				var end := start + (Vector2(rect.size.x,0) if axis == "row" else Vector2(0,rect.size.y))
				strokes.append(Scribble.grid_stroke(start,end,axis,index,limit,step,identity,revision))
	stable_ink.queue_redraw()
	stable_lines.queue_redraw()

func select_grid(value: bool) -> void:
	if active or payload.is_empty(): return
	grid_selected = value
	_update_selection()

func _update_selection() -> void:
	if stable_ink == null: return
	stable_ink.visible = grid_selected and not active and not payload.is_empty()
	stable_lines.visible = stable_ink.visible
	art.visible = not stable_ink.visible

func begin(origin: Rect2, commands: Array, ink_material: Material) -> void:
	grid_selected = false
	source = origin
	ink.commands = commands
	ink.material = ink_material
	ink.queue_redraw()
	raster.commands.clear()
	var step: float = source.size.x / solved[0].size()
	for y: int in range(solved.size()):
		for x: int in range(solved[y].size()):
			for entry: Dictionary in palette:
				if int(entry.id) == int(solved[y][x]):
					raster.commands.append([Rect2(Vector2(x, y) * step, Vector2.ONE * step), Color(entry.color)])
	raster.queue_redraw()
	elapsed = 0
	started_usec = Time.get_ticks_usec()
	active = true
	_update_selection()
	set_process(true)
	apply_time()

func _process(_delta: float) -> void:
	elapsed = (Time.get_ticks_usec() - started_usec) / 1000000.0
	if elapsed >= DURATION:
		finish()
	else:
		apply_time()

func apply_time() -> void:
	var move := smoothstep(0.0, 1.0, clampf((elapsed - 0.25) / 0.65, 0, 1))
	var destination := raster_rect()
	for layer: Layer in [ink, raster]:
		layer.position = source.position.lerp(destination.position, move)
		layer.scale = Vector2.ONE * lerpf(1.0, destination.size.x / source.size.x, move)
	var art_alpha := clampf((elapsed - 1.30) / 0.65, 0, 1)
	ink.modulate.a = 1.0 - move
	raster.modulate.a = move * (1.0 - art_alpha)
	art.modulate.a = art_alpha
	progressed.emit(1.0 - clampf(elapsed / 0.25, 0, 1), clampf((elapsed - 1.95) / 0.20, 0, 1))

func finish() -> void:
	var was_active := active
	active = false
	set_process(false)
	elapsed = DURATION
	for layer: Layer in [ink, raster]:
		layer.commands.clear()
		layer.material = null
		layer.queue_redraw()
	art.modulate.a = 1
	_update_selection()
	progressed.emit(0.0, 1.0)
	if was_active: finished.emit()

func clear() -> void:
	if active: finish()
	payload = {}
	solved = []
	palette = []
	grid_selected = false
	stable_key.clear()
	stable_ink.commands.clear()
	stable_ink.material = null
	strokes.clear()
	stable_ink.queue_redraw()
	stable_lines.queue_redraw()
	art.commands.clear()
	art.queue_redraw()
	_update_selection()

func _draw() -> void:
	pass # Each layer caches commands; frames change only transforms and opacity.
