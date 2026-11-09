extends Control
## RZ-EVAL-P1 experiment. No registry/schema change or permanent art selection.
const INK_SHADER = preload("res://book/rz_eval.gdshader")
const CANVAS := Vector2(3072, 768)
const PILOTS = {
	"pz-e2e5092925ce4821a9219be7816b5931": "tomate",
	"pz-20ecf7747bbf40828238ec26d1207172": "qualle",
	"pz-5f5a379b5abb4c979ee23f807aec9418": "hills",
	"pz-9d08697a30c749258b742ac979de9def": "petronas",
	"pz-c71563f1b8c940de998afdd62f09": "basilisk"
}
enum Overlap { A, B1, B2, C }
var mode: Overlap = Overlap.A
var candidate: int = 1
var profile: String = "2304"
var extension: String = "png"
var enabled: bool = true
var transparent_control: bool = false
var active_id: String = ""
var active_texture: Texture2D
var state: String = "idle"
var canvas: Rect2
var grid: Rect2
var protected_areas: Array[Rect2] = []
var generation: int = 0
var pending_path: String = ""
var pending_generation: int = -1
var desired_path: String = ""
var requested_at: int = 0
var last_load_ms: float = 0.0
var load_count: int = 0
var stale_count: int = 0
var publish_allowed: Callable
var ink: ShaderMaterial

func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE
	process_mode = Node.PROCESS_MODE_ALWAYS
	texture_filter = TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	ink = ShaderMaterial.new()
	ink.shader = INK_SHADER
	# CLI switches belong only to the experiment, never to a player preference.
	for argument: String in OS.get_cmdline_user_args():
		if argument == "--rz-without": enabled = false
		elif argument == "--rz-transparent": transparent_control = true
		elif argument.begins_with("--rz-mode="):
			var value: String = argument.trim_prefix("--rz-mode=")
			mode = {"A":Overlap.A,"B1":Overlap.B1,"B2":Overlap.B2,"C":Overlap.C}.get(value,Overlap.A)
		elif argument.begins_with("--rz-candidate="):
			candidate = clampi(argument.trim_prefix("--rz-candidate=").to_int(),1,3)
		elif argument.begins_with("--rz-profile="):
			var value: String = argument.trim_prefix("--rz-profile=")
			if value in ["1536","2304","3072"]: profile = value
		elif argument.begins_with("--rz-format="):
			var value: String = argument.trim_prefix("--rz-format=")
			if value in ["png","webp"]: extension = value

static func placement(paper: Rect2, viewport: Vector2, u: float) -> Rect2:
	# Resting paper projection, shared fold/rim envelope, client bottom. The
	# canvas is never fitted to board zoom, clues, controls or an individual ID.
	var safe := paper.intersection(Rect2(Vector2.ZERO,viewport))
	var left: float = maxf(safe.position.x,paper.position.x+paper.size.x*0.075)+24*u
	var right: float = minf(safe.end.x,paper.end.x)-24*u
	var top: float = maxf(safe.position.y,paper.position.y)+24*u
	var bottom: float = safe.end.y-24*u
	var width: float = minf(right-left,(bottom-top)*4.0)
	if width <= 0: return Rect2()
	return Rect2(Vector2((left+right-width)/2,bottom-width/4),Vector2(width,width/4))

func path_for(id: String) -> String:
	if not PILOTS.has(id): return ""
	return "res://art/drawing/rz_eval/%s-%d-%s.%s" % [PILOTS[id],candidate,profile,extension]

func visit(id: String, path: String) -> void:
	if active_id == id and desired_path == path: return
	generation += 1
	active_id = id
	desired_path = path
	active_texture = null
	canvas = Rect2()
	queue_redraw()
	if id.is_empty(): state = "idle"
	elif transparent_control: state = "intentional-empty"
	elif path.is_empty(): state = "missing"
	else: state = "queued"
	_start_latest()

func _start_latest() -> void:
	# ResourceLoader has no cancellation API: drain at most ONE in-flight
	# request, then consider only the latest visit. Never accumulate a queue.
	if not pending_path.is_empty() or state != "queued": return
	if not ResourceLoader.exists(desired_path,"Texture2D"):
		state = "missing"
		return
	requested_at = Time.get_ticks_usec()
	var error: Error = ResourceLoader.load_threaded_request(desired_path,"Texture2D",false,ResourceLoader.CACHE_MODE_IGNORE)
	if error != OK:
		state = "broken"
		return
	pending_path = desired_path
	pending_generation = generation
	state = "loading"
	load_count += 1

func accept_result(token: int, texture: Texture2D) -> void:
	if token != generation or active_id.is_empty():
		stale_count += 1
		return
	if texture == null:
		state = "broken"
		return
	# No late decoration popping onto an already visible page. A slow result
	# is omitted for this visit; the next visit retries without a history cache.
	if publish_allowed.is_valid() and not publish_allowed.call():
		state = "late-omitted"
		return
	active_texture = texture
	state = "ready"
	queue_redraw()

func _process(_delta: float) -> void:
	if pending_path.is_empty(): return
	var status: int = ResourceLoader.load_threaded_get_status(pending_path)
	if status == ResourceLoader.THREAD_LOAD_IN_PROGRESS: return
	var texture: Texture2D
	if status == ResourceLoader.THREAD_LOAD_LOADED:
		texture = ResourceLoader.load_threaded_get(pending_path) as Texture2D
	var token: int = pending_generation
	pending_path = ""
	last_load_ms = (Time.get_ticks_usec()-requested_at)/1000.0
	accept_result(token,texture)
	_start_latest()

func arrange(paper: Rect2, viewport: Vector2, u: float, board_area: Rect2, protections: Array[Rect2]) -> void:
	canvas = placement(paper,viewport,u)
	grid = board_area
	protected_areas = protections.duplicate()
	queue_redraw()

func _draw() -> void:
	if active_texture == null or not canvas.has_area(): return
	ink.set_shader_parameter("overlap_mode",mode)
	ink.set_shader_parameter("grid",Vector4(grid.position.x,grid.position.y,grid.size.x,grid.size.y))
	ink.set_shader_parameter("canvas_pixels",canvas.size)
	var rectangles: Array[Vector4] = []
	for i: int in range(24):
		var area: Rect2 = protected_areas[i] if i < protected_areas.size() else Rect2()
		rectangles.append(Vector4(area.position.x,area.position.y,area.size.x,area.size.y))
	ink.set_shader_parameter("protected_count",mini(24,protected_areas.size()))
	ink.set_shader_parameter("protected_areas",rectangles)
	draw_set_transform(Vector2.ZERO)
	# Use a child CanvasItem for decoration material so C's opaque paper has
	# no decoration shader/alpha. Entire grid including unknown/X/gaps is covered.
	if mode == Overlap.C and grid.has_area(): draw_rect(grid,Color("faf6ec"))
	RenderingServer.canvas_item_clear(ink_item())
	RenderingServer.canvas_item_add_texture_rect(_ink_item,canvas,active_texture.get_rid(),false)
	RenderingServer.canvas_item_set_visible(_ink_item,true)

var _ink_item: RID
func ink_item() -> RID:
	if not _ink_item.is_valid():
		_ink_item = RenderingServer.canvas_item_create()
		RenderingServer.canvas_item_set_parent(_ink_item,get_canvas_item())
		RenderingServer.canvas_item_set_material(_ink_item,ink.get_rid())
	return _ink_item

func _notification(what: int) -> void:
	if what == NOTIFICATION_DRAW and active_texture == null and _ink_item.is_valid():
		RenderingServer.canvas_item_clear(_ink_item)
	if what == NOTIFICATION_PREDELETE and _ink_item.is_valid():
		RenderingServer.free_rid(_ink_item)
