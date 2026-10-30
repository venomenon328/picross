extends Node3D
## B-A only. No product entry point, registry mutation, save or recovery integration.
const Content = preload("res://study/book/content.gd")
const PAGE = preload("res://study/book/page.gdshader")
const MATERIAL = preload("res://study/book/material.gdshader")
const DURATION: float = 3.0
enum State { CATALOG, PREPARING, OPENING, WORK }
var state: State = State.CATALOG
var generation: int = 0
var selected_id: String = ""
var elapsed: float = 0.0
var release_barrier: bool = false
var held_buttons: int = 0
var app: Content
var camera: Camera3D
var leaf: MeshInstance3D
var paper: MeshInstance3D
var leaf_material: ShaderMaterial
var paper_material: ShaderMaterial
var capture: SubViewport
var catalog_texture: ImageTexture
var frames_ms: Array[float] = []
var wall_started: int = 0
var last_frame_usec: int = 0
var motion_wall_seconds: float = 0.0
var interrupted: String = ""

func _ready() -> void:
	_build_book()
	app = Content.new()
	app.name = "StudyUI"
	app.size = Vector2(get_viewport().size)
	add_child(app)
	app.opening_requested.connect(request_open)
	app.catalog_shown.connect(_catalog)
	app.scale_changing.connect(func() -> void: interrupt("ui-scale"))
	app.exit_requested.connect(func() -> void: interrupt("leave"); get_tree().quit())
	get_viewport().size_changed.connect(_resize)
	_resize()
	if OS.get_cmdline_user_args().has("--book-study-proof"): call_deferred("_native_proof")

func _native_proof() -> void:
	# Export templates do not run the editor's --script entry point. Exercise the
	# actual delivered main scene instead, only under this explicit study flag.
	for i: int in range(6): await get_tree().process_frame
	var accepted: bool = request_open("T-06")
	var deadline: int = Time.get_ticks_usec()+10000000
	while state in [State.PREPARING, State.OPENING] and Time.get_ticks_usec() < deadline:
		await get_tree().process_frame
	var ok: bool = accepted and state == State.WORK and elapsed == DURATION and app.session.definition.id == "T-06"
	await RenderingServer.frame_post_draw
	var destination: String = OS.get_environment("BOOK_STUDY_OUTPUT").path_join("windows-exported-work.png")
	ok = ok and get_viewport().get_texture().get_image().save_png(destination) == OK
	print("BOOK_PACK_MOTION_OK" if ok else "BOOK_PACK_MOTION_FAIL", " elapsed=", elapsed, " id=", selected_id)
	get_tree().quit(0 if ok else 4)

func _material(color: Color, kind: float) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = MATERIAL
	result.set_shader_parameter("base_color", color)
	result.set_shader_parameter("kind", kind)
	return result

func _box(extent: Vector3, at: Vector3, material: Material) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = extent
	instance.mesh = mesh
	instance.material_override = material
	instance.position = at
	add_child(instance)
	return instance

func _page(material: ShaderMaterial) -> MeshInstance3D:
	var mesh := ArrayMesh.new()
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	for y: int in range(9):
		for x: int in range(65):
			var uv := Vector2(x/64.0, y/8.0)
			vertices.append(Vector3((uv.x-0.5)*19.2, (0.5-uv.y)*10.8, 0.0))
			normals.append(Vector3.FORWARD * -1.0)
			uvs.append(uv)
			if x < 64 and y < 8:
				var i: int = y*65+x
				indices.append_array([i, i+1, i+65, i+1, i+66, i+65])
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	add_child(instance)
	return instance

func _build_book() -> void:
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("302b25")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color("f7f3eb")
	environment.environment.ambient_light_energy = 0.4
	add_child(environment)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-25, -32, 0)
	light.light_color = Color("ffeed7")
	light.light_energy = 0.55
	light.shadow_enabled = false
	add_child(light)
	_box(Vector3(80, 50, 0.15), Vector3(0, 0, -0.75), _material(Color("514333"), 2))
	var leather: ShaderMaterial = _material(Color("292c2b"), 0)
	_box(Vector3(18.75, 10.55, 0.16), Vector3(0.03, -0.025, -0.46), leather)
	_box(Vector3(18.53, 10.36, 0.27), Vector3(-0.01, 0.01, -0.245), _material(Color("c9b993"), 1))
	# Individual thin signatures and slightly irregular fore-edges catch material light.
	for i: int in range(18):
		_box(Vector3(18.49+sin(i*4.7)*0.018, 10.32+sin(i*3.1)*0.017, 0.008), Vector3(-0.02, 0.01, -0.37+i*0.015), _material(Color("dfd2b3").darkened((i%3)*0.015), 1))
	_box(Vector3(0.18, 10.43, 0.42), Vector3(9.27, 0.01, -0.2), leather)
	_box(Vector3(0.025, 10.26, 0.015), Vector3(9.16, 0.01, 0.01), _material(Color("756345"), 0))
	paper_material = ShaderMaterial.new()
	paper_material.shader = PAGE
	paper = _page(paper_material)
	leaf_material = ShaderMaterial.new()
	leaf_material.shader = PAGE
	leaf = _page(leaf_material)
	leaf.position.z = 0.014
	leaf.hide()
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.near = 0.05
	camera.far = 100
	camera.current = true
	add_child(camera)
	_pose(0)

func _pose(progress: float) -> void:
	var retreat: float = sin(PI * clampf(progress/0.84, 0, 1))
	var viewport_size := Vector2(get_viewport().size)
	var fit: float = maxf(10.8, 19.2*viewport_size.y/maxf(1, viewport_size.x))
	camera.size = fit*(1.0+0.17*retreat)
	camera.position = Vector3(-3.5*retreat, 3.2*retreat, 30)
	camera.look_at(Vector3.ZERO)
	var t: float = smoothstep(0.12, 0.88, progress)
	leaf_material.set_shader_parameter("turn", t)
	paper_material.set_shader_parameter("shadow", sin(t*PI))

func _catalog() -> void:
	if state in [State.PREPARING, State.OPENING]: interrupt("leave")
	state = State.CATALOG
	selected_id = ""
	leaf.hide()
	_pose(0)

func _resize() -> void:
	if app == null: return
	if state in [State.PREPARING, State.OPENING]: interrupt("resize")
	app.size = Vector2(get_viewport().size)
	_pose(1.0 if state == State.WORK else 0.0)
	app._layout_book()

func request_open(id: String) -> bool:
	if state != State.CATALOG or release_barrier or not app.session_indices.has(id): return false
	selected_id = id # Bind identity before any await or catalog rebuild.
	generation += 1
	state = State.PREPARING
	interrupted = ""
	app._cancel_interaction()
	app.process_mode = Node.PROCESS_MODE_DISABLED
	release_barrier = true
	_prepare(generation)
	return true

func _prepare(token: int) -> void:
	capture = SubViewport.new()
	capture.size = get_viewport().size
	capture.disable_3d = true
	capture.transparent_bg = true
	capture.gui_disable_input = true
	capture.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(capture)
	app.reparent(capture, false)
	app.position = Vector2.ZERO
	app.size = Vector2(capture.size)
	leaf_material.set_shader_parameter("content", capture.get_texture())
	leaf_material.set_shader_parameter("has_content", true)
	leaf.show()
	await RenderingServer.frame_post_draw
	if token != generation: return
	catalog_texture = ImageTexture.create_from_image(capture.get_texture().get_image())
	leaf_material.set_shader_parameter("content", catalog_texture)
	app.activate(selected_id)
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	if token != generation: return
	paper_material.set_shader_parameter("content", capture.get_texture())
	paper_material.set_shader_parameter("has_content", true)
	elapsed = 0
	frames_ms.clear()
	wall_started = Time.get_ticks_usec()
	last_frame_usec = wall_started
	state = State.OPENING

func _process(delta: float) -> void:
	if state == State.OPENING:
		var now: int = Time.get_ticks_usec()
		frames_ms.append((now-last_frame_usec)/1000.0)
		last_frame_usec = now
		elapsed = minf(DURATION, elapsed+delta if OS.has_feature("movie") else (now-wall_started)/1000000.0)
		_pose(elapsed/DURATION)
		if elapsed >= DURATION:
			motion_wall_seconds = (Time.get_ticks_usec()-wall_started)/1000000.0
			_settle(true)
	elif state != State.PREPARING and release_barrier and held_buttons == 0 and Input.get_mouse_button_mask() == 0:
		# The release itself was consumed. Only a subsequent event can reach UI.
		release_barrier = false
		if app != null: app.process_mode = Node.PROCESS_MODE_INHERIT

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MIDDLE, MOUSE_BUTTON_XBUTTON1, MOUSE_BUTTON_XBUTTON2]:
		var mask: int = 1 << (event.button_index-1)
		held_buttons = (held_buttons | mask) if event.pressed else (held_buttons & ~mask)
	if state in [State.PREPARING, State.OPENING] or release_barrier:
		get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		interrupt("leave")
		app.show_album()

func interrupt(reason: String) -> void:
	if state not in [State.PREPARING, State.OPENING]: return
	interrupted = reason
	generation += 1
	_settle(reason != "leave")

func _settle(to_work: bool) -> void:
	generation += 1
	state = State.WORK if to_work else State.CATALOG
	if app.get_parent() != self: app.reparent(self, false)
	app.position = Vector2.ZERO
	app.size = Vector2(get_viewport().size)
	if to_work: app.activate(selected_id)
	else: app.show_album()
	leaf.visible = to_work
	_pose(1.0 if to_work else 0.0)
	leaf_material.set_shader_parameter("has_content", false)
	leaf_material.set_shader_parameter("content", null)
	paper_material.set_shader_parameter("has_content", false)
	paper_material.set_shader_parameter("content", null)
	catalog_texture = null
	if capture != null:
		capture.queue_free()
		capture = null
	# Stay disabled until the transition-triggering and all blocked buttons are up.
	release_barrier = true
	app._cancel_interaction()

func set_ui_scale(value: float) -> void:
	interrupt("ui-scale")
	app.set_ui_scale(value)

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		held_buttons = 0
		interrupt("focus")
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		interrupt("leave")
		get_tree().quit()

func resource_report() -> Dictionary:
	var pixels: int = get_viewport().size.x * get_viewport().size.y
	return {"viewport": get_viewport().size, "page_vertices": 585, "page_triangles": 1024,
		"animation_seconds": DURATION, "motion_wall_seconds": motion_wall_seconds,
		"ui_capture_targets": 1 if capture != null else 0, "catalog_rgba_textures": 1 if catalog_texture != null else 0,
		"peak_color_target_and_snapshot_bytes": pixels*8, "peak_capture_depth_upper_bound_bytes": pixels*4,
		"shared_resources_excluded_from_estimate": "font atlases, six cell atlases, SL frames, main framebuffer, driver overhead"}
