extends Node3D
## B-A-N01 only: synthetic RAM study, no regular startup or save integration.
const Content = preload("res://study/book/content.gd")
const PAGE = preload("res://study/book/page.gdshader")
const MATERIAL = preload("res://study/book/material.gdshader")
const SOURCE = preload("res://art/book/bp2-a-inventarband.png")
const DURATION: float = 3.0
const PAGE_DURATION: float = 0.85
const OPENING_LEAVES: int = 3
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
var left_material: ShaderMaterial
var leaves: Array[MeshInstance3D] = []
var capture: SubViewport
var catalog_texture: ImageTexture
var frames_ms: Array[float] = []
var wall_started: int = 0
var last_frame_usec: int = 0
var motion_wall_seconds: float = 0.0
var preparation_seconds: float = 0.0
var interrupted: String = ""
var motion_kind: String = ""
var direction: int = 1
var source_context: Dictionary = {}
var target_page: int = 0
var preparation_started: int = 0
var settling: bool = false

func _ready() -> void:
	_build_book()
	app = Content.new()
	app.name = "StudyUI"
	app.size = Vector2(get_viewport().size)
	add_child(app)
	app.opening_requested.connect(request_open)
	app.album.page_requested.connect(request_page)
	app.catalog_shown.connect(_catalog)
	app.scale_changing.connect(func() -> void: interrupt("ui-scale"))
	app.exit_requested.connect(func() -> void: interrupt("leave"); get_tree().quit())
	get_viewport().size_changed.connect(_resize)
	_resize()
	if OS.get_cmdline_user_args().has("--book-study-proof"): call_deferred("_native_proof")

func _native_proof() -> void:
	for i: int in range(6): await get_tree().process_frame
	var accepted: bool = request_open("T-06")
	var deadline: int = Time.get_ticks_usec()+10000000
	while state in [State.PREPARING, State.OPENING] and Time.get_ticks_usec() < deadline:
		await get_tree().process_frame
	var ok: bool = accepted and state == State.WORK and elapsed == DURATION and app.session.definition.id == "T-06"
	await RenderingServer.frame_post_draw
	ok = ok and get_viewport().get_texture().get_image().save_png(OS.get_environment("BOOK_STUDY_OUTPUT").path_join("windows-exported-work.png")) == OK
	print("BOOK_PACK_MOTION_OK" if ok else "BOOK_PACK_MOTION_FAIL", " elapsed=", elapsed, " id=", selected_id)
	get_tree().quit(0 if ok else 4)

func _material(color: Color, kind: float) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = MATERIAL
	result.set_shader_parameter("base_color", color)
	result.set_shader_parameter("kind", kind)
	result.set_shader_parameter("material_source", SOURCE)
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

func _page_material(side: float) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = PAGE
	result.set_shader_parameter("side", side)
	result.set_shader_parameter("material_source", SOURCE)
	return result

func _page(material: ShaderMaterial) -> MeshInstance3D:
	var mesh := ArrayMesh.new()
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	for y: int in range(17):
		for x: int in range(65):
			var uv := Vector2(x/64.0, y/16.0)
			vertices.append(Vector3(uv.x*10.0, (0.5-uv.y)*12.4, 0.0))
			normals.append(Vector3.BACK)
			uvs.append(uv)
			if x < 64 and y < 16:
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
	add_child(environment)
	_box(Vector3(80,50,0.15),Vector3(0,0,-0.75),_material(Color("514333"),2))
	var leather: ShaderMaterial = _material(Color("292522"),0)
	for side: float in [-1.0,1.0]:
		_box(Vector3(10.36,12.86,0.18),Vector3(side*5.13,-0.04,-0.49),leather)
		_box(Vector3(10.12,12.62,0.31),Vector3(side*5.04,0,-0.28),_material(Color("cbb992"),1))
		for i: int in range(16):
			_box(Vector3(10.06+sin(i*4.7)*0.025,12.52+sin(i*3.1)*0.024,0.008),Vector3(side*5.02,0,-0.40+i*0.021),_material(Color("e5d4ae").darkened((i%3)*0.025),1))
		# A worn raised leather lip remains visible in the close work crop.
		_box(Vector3(0.13,12.77,0.06),Vector3(side*10.22,-0.02,-0.32),leather)
	_box(Vector3(0.22,12.75,0.32),Vector3(0,0,-0.20),leather)
	var thread := StandardMaterial3D.new()
	thread.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	thread.albedo_color = Color("947349")
	for y: float in [-5.6,-3.7,-1.8,0.1,2.0,3.9,5.7]:
		_box(Vector3(0.15,0.025,0.02),Vector3(0,y,0.01),thread)
	left_material = _page_material(-1)
	_page(left_material)
	paper_material = _page_material(1)
	paper = _page(paper_material)
	for i: int in range(OPENING_LEAVES):
		var sheet: MeshInstance3D = _page(_page_material(1))
		sheet.position.z = 0.025+(OPENING_LEAVES-i)*0.022
		sheet.hide()
		leaves.append(sheet)
	leaf = leaves[0]
	leaf_material = leaf.material_override
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.near = 0.05
	camera.far = 100
	camera.current = true
	add_child(camera)
	_pose(0)

func view_rect(work: bool) -> Vector4:
	var viewport_size := Vector2(get_viewport().size)
	var height: float = maxf(6.075,10.8*viewport_size.y/maxf(1,viewport_size.x)) if work else maxf(13.4,22.0*viewport_size.y/maxf(1,viewport_size.x))
	var width: float = height*viewport_size.x/maxf(1,viewport_size.y)
	return Vector4((5.0 if work else 0.0)-width/2,-height/2,width,height)

func _pose(progress: float) -> void:
	var work: bool = motion_kind == "open" or state == State.WORK
	var zoom: float = smoothstep(0.45,1.0,progress) if work else 0.0
	var from: Vector4 = view_rect(false)
	var to: Vector4 = view_rect(true)
	camera.size = lerpf(from.w,to.w,zoom)
	var center: float = 5.0*zoom
	var tilt: float = sin(PI*progress)*0.65 if state == State.OPENING else 0.0
	camera.position = Vector3(center,tilt,30)
	camera.look_at(Vector3(center,0,0))
	var strongest: float = 0
	for i: int in range(leaves.size()):
		if progress >= 1.0: leaves[i].hide()
		var turn: float = smoothstep(0.04+i*0.14,0.65+i*0.11,progress) if motion_kind == "open" else smoothstep(0,1,progress)
		leaves[i].material_override.set_shader_parameter("turn",turn)
		strongest = maxf(strongest,sin(turn*PI))
	paper_material.set_shader_parameter("shadow",strongest)
	left_material.set_shader_parameter("shadow",strongest*0.65)

func _catalog() -> void:
	if settling: return
	if state in [State.PREPARING,State.OPENING]: interrupt("leave")
	state = State.CATALOG
	selected_id = ""
	motion_kind = ""
	for sheet: MeshInstance3D in leaves: sheet.hide()
	_pose(0)

func _resize() -> void:
	if app == null: return
	if state in [State.PREPARING,State.OPENING]: interrupt("resize")
	app.size = Vector2(get_viewport().size)
	_pose(1.0 if state == State.WORK else 0.0)
	app._layout_book()

func context() -> Dictionary:
	return {"page":app.album.page_index,"scroll":app.album.scroll_vertical,"category":app.album.category_id,
		"criterion":app.album.preference.criterion,"direction":app.album.preference.direction,
		"selection":app.album.selected_id,"session":str(app.session.definition.id)}

func _begin(kind: String) -> void:
	source_context = context()
	motion_kind = kind
	generation += 1
	state = State.PREPARING
	preparation_started = Time.get_ticks_usec()
	interrupted = ""
	app._cancel_interaction()
	app.album.locked = true
	app.process_mode = Node.PROCESS_MODE_DISABLED
	release_barrier = true
	_prepare(generation)

func request_open(id: String) -> bool:
	if state != State.CATALOG or release_barrier or not app.session_indices.has(id): return false
	selected_id = id
	if app.sessions[int(app.session_indices[id])].completed:
		app.activate(id)
		state = State.WORK
		motion_kind = ""
		_pose(1)
		return true
	direction = 1
	_begin("open")
	return true

func request_page(target: int) -> bool:
	if state != State.CATALOG or release_barrier or target == app.album.page_index: return false
	if target < 0 or target >= ceili(app.album.filtered_ids.size()/24.0): return false
	target_page = target
	direction = 1 if target > app.album.page_index else -1
	_begin("page")
	return true

func _ink(material: ShaderMaterial, texture: Texture2D, rect: Vector4, back: bool = false) -> void:
	material.set_shader_parameter("back_content" if back else "content",texture)
	material.set_shader_parameter("has_back" if back else "has_content",texture != null)
	material.set_shader_parameter("back_rect" if back else "content_rect",rect)

func _prepare(token: int) -> void:
	capture = SubViewport.new()
	capture.size = get_viewport().size
	capture.disable_3d = true
	capture.transparent_bg = true
	capture.gui_disable_input = true
	capture.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(capture)
	app.reparent(capture,false)
	app.position = Vector2.ZERO
	app.size = Vector2(capture.size)
	for i: int in range(leaves.size()):
		leaves[i].visible = i == 0 or motion_kind == "open"
		leaves[i].material_override.set_shader_parameter("side",float(direction))
		leaves[i].material_override.set_shader_parameter("turn",0.0)
	_ink(leaf_material,capture.get_texture(),view_rect(false))
	_ink(left_material,capture.get_texture(),view_rect(false))
	_ink(paper_material,capture.get_texture(),view_rect(false))
	await RenderingServer.frame_post_draw
	if token != generation: return
	catalog_texture = ImageTexture.create_from_image(capture.get_texture().get_image())
	_ink(leaf_material,catalog_texture,view_rect(false))
	_ink(left_material,catalog_texture,view_rect(false))
	_ink(paper_material,catalog_texture,view_rect(false))
	if motion_kind == "open": app.activate(selected_id)
	else: app.album.commit_page(target_page)
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	if token != generation: return
	if motion_kind == "open":
		_ink(paper_material,capture.get_texture(),view_rect(true))
	else:
		_ink(paper_material if direction == 1 else left_material,capture.get_texture(),view_rect(false))
		_ink(leaf_material,capture.get_texture(),view_rect(false),true)
	elapsed = 0
	frames_ms.clear()
	wall_started = Time.get_ticks_usec()
	preparation_seconds = (wall_started-preparation_started)/1000000.0
	last_frame_usec = wall_started
	state = State.OPENING

func _process(delta: float) -> void:
	if state == State.OPENING:
		var now: int = Time.get_ticks_usec()
		frames_ms.append((now-last_frame_usec)/1000.0)
		last_frame_usec = now
		var duration: float = DURATION if motion_kind == "open" else PAGE_DURATION
		elapsed = minf(duration,elapsed+delta if OS.has_feature("movie") else (now-wall_started)/1000000.0)
		_pose(elapsed/duration)
		if elapsed >= duration:
			motion_wall_seconds = (Time.get_ticks_usec()-wall_started)/1000000.0
			_settle(true)
	elif state != State.PREPARING and release_barrier and held_buttons == 0 and Input.get_mouse_button_mask() == 0:
		release_barrier = false
		app.album.locked = false
		app.process_mode = Node.PROCESS_MODE_INHERIT

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT,MOUSE_BUTTON_MIDDLE,MOUSE_BUTTON_XBUTTON1,MOUSE_BUTTON_XBUTTON2]:
		var mask: int = 1 << (event.button_index-1)
		held_buttons = (held_buttons | mask) if event.pressed else (held_buttons & ~mask)
	if state in [State.PREPARING,State.OPENING] or release_barrier: get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		interrupt("leave")
		app.show_album()

func interrupt(reason: String) -> void:
	if state not in [State.PREPARING,State.OPENING]: return
	interrupted = reason
	generation += 1
	_settle(reason != "leave")

func _settle(target: bool) -> void:
	generation += 1
	settling = true
	var work: bool = target and motion_kind == "open"
	state = State.WORK if work else State.CATALOG
	if app.get_parent() != self: app.reparent(self,false)
	app.position = Vector2.ZERO
	app.size = Vector2(get_viewport().size)
	if work: app.activate(selected_id)
	else:
		if not target:
			app.session = app.sessions[int(app.session_indices[source_context.session])]
			app.board.session = app.session
		app.show_album()
		app.album.selected_id = source_context.selection
		app.album.commit_page(target_page if target else int(source_context.page),0 if target else int(source_context.scroll))
	for sheet: MeshInstance3D in leaves:
		sheet.hide()
		_ink(sheet.material_override,null,Vector4.ZERO)
		_ink(sheet.material_override,null,Vector4.ZERO,true)
	_pose(1.0 if work else 0.0)
	_ink(paper_material,null,Vector4.ZERO)
	_ink(left_material,null,Vector4.ZERO)
	catalog_texture = null
	if capture != null:
		capture.queue_free()
		capture = null
	release_barrier = true
	app._cancel_interaction()
	settling = false

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
	var pixels: int = get_viewport().size.x*get_viewport().size.y
	return {"viewport":get_viewport().size,"page_vertices":1105,"page_triangles":2048,"moving_leaves":OPENING_LEAVES,
		"visible_leaves":leaves.filter(func(sheet: MeshInstance3D) -> bool: return sheet.visible).size(),
		"animation_seconds":DURATION,"page_seconds":PAGE_DURATION,"motion_wall_seconds":motion_wall_seconds,"preparation_seconds":preparation_seconds,
		"ui_capture_targets":1 if capture != null else 0,"catalog_rgba_textures":1 if catalog_texture != null else 0,
		"peak_color_target_and_snapshot_bytes":pixels*8,"peak_capture_depth_upper_bound_bytes":pixels*4,
		"material_source_rgba_bytes":2560*1440*4,
		"shared_resources_excluded_from_estimate":"font atlases, six cell atlases, SL frames, main framebuffer, driver overhead"}
