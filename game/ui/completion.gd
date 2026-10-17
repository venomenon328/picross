extends "res://ui/reveal.gd"
## Transient presentation only. No session, persistence, input or deferred navigation.
signal progressed(work_alpha: float, caption_alpha: float)
signal finished
const DURATION := 2.15
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

func _ready() -> void:
	paired = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for kind: String in ["ink", "raster", "art"]:
		var layer := Layer.new()
		layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		add_child(layer)
		set(kind, layer)
	set_process(false)

func contained(extent: Vector2) -> Rect2:
	if extent.x <= 0 or extent.y <= 0: return Rect2()
	var fitted := extent * minf(area.size.x / extent.x, area.size.y / extent.y)
	return Rect2(area.get_center() - fitted / 2, fitted)

func raster_rect() -> Rect2:
	return Rect2() if solved.is_empty() else contained(Vector2(solved[0].size(), solved.size()))

func artwork_rect() -> Rect2:
	return Rect2() if artwork == null else contained(artwork.get_size())

func configure(next_payload: Dictionary, matrix: Array, colors: Array, bounds: Rect2) -> void:
	payload = next_payload
	solved = matrix
	palette = colors
	area = bounds
	art.commands.clear()
	if artwork != null:
		var display: Texture2D = display_texture(artwork_rect())
		art.commands.append([display, artwork_rect(), Rect2(Vector2.ZERO, display.get_size()), Color.WHITE])
	art.queue_redraw()

func begin(origin: Rect2, commands: Array, ink_material: Material) -> void:
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
	progressed.emit(0.0, 1.0)
	if was_active: finished.emit()

func clear() -> void:
	if active: finish()
	payload = {}
	solved = []
	palette = []
	art.commands.clear()
	art.queue_redraw()

func _draw() -> void:
	pass # Each layer caches commands; frames change only transforms and opacity.
