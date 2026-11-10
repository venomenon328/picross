extends Control
## HP-I2: one passive paper-bound drawing, frozen at the visit's publication.
const Registry = preload("res://model/content_registry.gd")
const NativeLoader = preload("res://book/puzzle_background_loader.gd")
const WebLoader = preload("res://book/puzzle_background_web.gd")
const IMAGE_SIZE := Vector2i(2304, 576)
const OPACITY: float = 0.48

var backend: RefCounted = NativeLoader.new()
var binding: Dictionary = {}
var request: Dictionary = {}
var desired: Dictionary = {}
var texture: Texture2D
var ready_texture: Texture2D
var state: String = "idle"
var diagnostic: String = ""
var frozen: bool = false
var box := Rect2()
var request_count: int = 0
var completed_count: int = 0
var discarded_count: int = 0
var peak_requests: int = 0
var last_load_usec: int = 0
var _request_started: int = 0

func _init() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	focus_mode = FOCUS_NONE
	process_mode = PROCESS_MODE_ALWAYS
	texture_filter = TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	if OS.has_feature("web"): backend = WebLoader.new()

func begin_visit(entry: Dictionary, token: int) -> void:
	var background: Dictionary = Registry.background(entry)
	var next: Dictionary = {
		"id":entry.get("id", ""), "image_revision":background.get("image_revision"),
		"token":token, "status":background.get("status", "invalid"),
		"asset":background.get("asset")
	}
	if binding == next: return
	_clear_view()
	binding = next.duplicate(true)
	frozen = false
	diagnostic = ""
	state = str(binding.status)
	_retire_request()
	if state == "selected":
		if not Registry.valid_background(entry):
			state = "failed"
			diagnostic = "invalid_background_declaration"
		else:
			state = "loading"
			desired = binding.duplicate(true)
			_poll()
			_start_desired()
	queue_redraw()

func publish(token: int) -> void:
	if binding.is_empty() or int(binding.token) != token or frozen: return
	_poll()
	frozen = true
	desired.clear()
	if binding.status == "selected":
		if ready_texture != null:
			texture = ready_texture
			ready_texture = null
			state = "visible"
		else:
			state = "omitted"
			if diagnostic.is_empty(): diagnostic = "not_ready_at_publication"
			_retire_request()
	queue_redraw()

func leave() -> void:
	_clear_view()
	binding.clear()
	frozen = false
	state = "idle"
	diagnostic = ""
	_retire_request()
	queue_redraw()

func _clear_view() -> void:
	texture = null
	ready_texture = null
	desired.clear()

func _retire_request() -> void:
	if not request.is_empty() and backend.cancel():
		request.clear()

func _process(_delta: float) -> void:
	_poll()
	_start_desired()

func _start_desired() -> void:
	if not request.is_empty() or desired.is_empty() or frozen or desired != binding: return
	var wanted: Dictionary = desired.duplicate(true)
	desired.clear()
	var error: String = backend.start("res://" + str(wanted.asset.file))
	request_count += 1
	if not error.is_empty():
		state = "failed"
		diagnostic = error
		return
	request = wanted
	_request_started = Time.get_ticks_usec()
	peak_requests = maxi(peak_requests, 1)

func _poll() -> void:
	if request.is_empty(): return
	var result: Dictionary = backend.poll()
	if result.get("status") == "pending": return
	var finished: Dictionary = request
	request = {}
	completed_count += 1
	last_load_usec = Time.get_ticks_usec() - _request_started
	if finished != binding or frozen:
		discarded_count += 1
		return
	if result.get("status") != "loaded" or not result.get("texture") is Texture2D:
		state = "failed"
		diagnostic = str(result.get("error", "texture_load_failed"))
		return
	var loaded: Texture2D = result.texture
	if Vector2i(loaded.get_width(), loaded.get_height()) != IMAGE_SIZE:
		state = "failed"
		diagnostic = "invalid_texture_dimensions"
		return
	# The Web decoder already owns the verified CPU image. Reuse it for this
	# check instead of forcing an immediate synchronous GPU readback.
	var image: Image = result.get("image", null)
	if image == null: image = loaded.get_image()
	if image == null or image.is_empty() or image.get_mipmap_count() != 11:
		state = "failed"
		diagnostic = "invalid_texture_mipmaps"
		return
	ready_texture = loaded
	state = "ready"

static func placement(paper: Rect2, viewport: Vector2, u: float) -> Rect2:
	# Same fold/rim safety envelope for every image. No functional rectangles
	# or zoom inputs: variant A stays behind both cells and clues.
	var safe := Rect2(Vector2(paper.position.x + paper.size.x * 0.075 + 24 * u, maxf(24 * u, paper.position.y + 20 * u)), Vector2.ZERO)
	safe.size = Vector2(paper.end.x - 24 * u, minf(viewport.y - 24 * u, paper.end.y - 24 * u)) - safe.position
	if safe.size.x <= 0 or safe.size.y <= 0: return Rect2()
	var width: float = minf(safe.size.x, safe.size.y * 4.0)
	var extent := Vector2(width, width / 4.0)
	return Rect2(Vector2(safe.get_center().x - width / 2.0, safe.end.y - extent.y), extent)

func arrange(paper: Rect2, viewport: Vector2, u: float) -> void:
	var next: Rect2 = placement(paper, viewport, u)
	if box == next: return
	box = next
	queue_redraw()

func snapshot() -> Dictionary:
	return {
		"binding":binding.duplicate(true), "state":state, "frozen":frozen,
		"diagnostic":diagnostic, "visible_id":binding.get("id", "") if texture != null else "",
		"visible_revision":binding.get("image_revision") if texture != null else null,
		"visible_token":binding.get("token") if texture != null else null,
		"has_texture":texture != null, "has_ready":ready_texture != null,
		"active_requests":0 if request.is_empty() else 1,
		"stale_requests":0 if request.is_empty() or (request == binding and not frozen) else 1,
		"queued":not desired.is_empty(), "request_count":request_count,
		"completed_count":completed_count, "discarded_count":discarded_count,
		"peak_requests":peak_requests, "last_load_usec":last_load_usec, "rect":box
	}

func _draw() -> void:
	if texture != null and box.has_area():
		draw_texture_rect(texture, box, false, Color(1, 1, 1, OPACITY))

func _notification(what: int) -> void:
	# Reparenting the real page into a transition SubViewport leaves/re-enters
	# the tree. That is still the same visit, not an exit from the puzzle.
	if what == NOTIFICATION_PREDELETE:
		texture = null
		ready_texture = null
		backend.cancel()
