extends Node3D
## Shared book presentation; the regular content owns persistence and lifecycle.
const Content = preload("res://book/content.gd")
const PAGE = preload("res://book/page.gdshader")
const Binding = preload("res://book/binding.gd")
const InformationRoutes = preload("res://book/information_routes.gd")
const PAPER_SOURCE = preload("res://book/paper.png")
const DURATION: float = 3.0
const PAGE_DURATION: float = 0.85
const RETURN_DURATION: float = 1.8
const OPENING_LEAVES: int = 3
enum State { CATALOG, PREPARING, OPENING, WORK, INFORMATION }
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
var transition_id: String = ""
var target_page: int = 0
var preparation_started: int = 0
var settling: bool = false
var return_context: Dictionary = {}
var material_catalog_page: int = -1
var binding := Binding.new()
var information_routes: RefCounted

func _ready() -> void:
	_build_book()
	information_routes = InformationRoutes.new(self)
	app = create_content()
	app.book = self
	app.name = "PlayerUI"
	app.size = Vector2(get_viewport().size)
	add_child(app)
	if app.album == null:
		# A refused Web storage attachment owns its visible startup error.
		set_process(false)
		return
	app.opening_requested.connect(request_open)
	app.return_requested.connect(request_return)
	app.album.page_requested.connect(request_page)
	app.catalog_shown.connect(_catalog)
	app.scale_changing.connect(func() -> void: interrupt("ui-scale"))
	app.exit_requested.connect(request_quit)
	get_viewport().size_changed.connect(_resize)
	_resize()


func create_content() -> Content:
	return Content.new()

func _page_material(side: float) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = PAGE
	result.set_shader_parameter("side", side)
	result.set_shader_parameter("paper_source", PAPER_SOURCE)
	return result

func _page(material: ShaderMaterial) -> MeshInstance3D:
	var mesh := ArrayMesh.new()
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	for y: int in range(17):
		for x: int in range(65):
			var uv := Vector2(Binding.column(x)/10.0, y/16.0)
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
	binding.build(self)
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
	# Expose the top rim and page block without changing any UI pixel scale.
	var center_y: float = 6.48-height/2 if work else 0.0
	return Vector4((5.0 if work else 0.0)-width/2,center_y-height/2,width,height)

func page_identity(material: ShaderMaterial, identity: String, back: bool = false) -> void:
	var seed: int = absi(identity.hash())
	material.set_shader_parameter("back_paper_offset" if back else "paper_offset",Vector2((seed%997)/997.0,((seed/997)%991)/991.0)*0.26)

func projected_paper(work: bool, side: int = 1) -> Rect2:
	var view: Vector4 = view_rect(work)
	var scale: Vector2 = Vector2(get_viewport().size)/Vector2(view.z,view.w)
	return Rect2(Vector2(((-10.0 if side < 0 else 0.0)-view.x)*scale.x,(view.y+view.w-6.2)*scale.y),Vector2(10.0,12.4)*scale)

func projected_information(side: int) -> Rect2:
	var rect: Rect2 = projected_paper(true)
	# Both near poses have identical scale; mirror the camera, never the text.
	if side < 0:
		rect.position.x = get_viewport().size.x-rect.end.x
	return rect

func catalog_materials(page_index: int) -> void:
	page_identity(left_material,"catalog/%d/left" % page_index)
	page_identity(paper_material,"catalog/%d/right" % page_index)
	material_catalog_page = page_index

func _pose(progress: float) -> void:
	if information_routes != null and (information_routes.moving() or state == State.INFORMATION):
		information_routes.pose(progress)
		return
	var work: bool = motion_kind == "open" or state == State.WORK
	var zoom: float = smoothstep(0.45,1.0,progress) if work else 0.0
	if motion_kind == "return" and state in [State.PREPARING,State.OPENING]: zoom = 1.0-smoothstep(0.0,0.85,progress)
	var from: Vector4 = view_rect(false)
	var to: Vector4 = view_rect(true)
	camera.size = lerpf(from.w,to.w,zoom)
	var center: float = 5.0*zoom
	var center_y: float = (to.y+to.w/2)*zoom
	var tilt: float = sin(PI*progress)*0.65 if state == State.OPENING and work else 0.0
	camera.position = Vector3(center,center_y+tilt,30)
	camera.look_at(Vector3(center,center_y,0))
	var strongest: float = 0
	for i: int in range(leaves.size()):
		if progress >= 1.0: leaves[i].hide()
		var turn: float = smoothstep(0.04+i*0.14,0.65+i*0.11,progress) if motion_kind in ["open","return"] else smoothstep(0,1,progress)
		leaves[i].material_override.set_shader_parameter("turn",turn)
		strongest = maxf(strongest,sin(turn*PI))
	paper_material.set_shader_parameter("shadow",strongest)
	left_material.set_shader_parameter("shadow",strongest*0.65)
	if motion_kind == "return" and progress >= 1.0 and capture != null:
		_ink(paper_material,capture.get_texture(),view_rect(false))
		catalog_materials(target_page)
	if motion_kind == "page" and progress >= 1.0: catalog_materials(target_page)

func _catalog() -> void:
	if settling: return
	if state in [State.PREPARING,State.OPENING]: interrupt("leave")
	state = State.CATALOG
	selected_id = ""
	motion_kind = ""
	catalog_materials(app.album.page_index)
	for sheet: MeshInstance3D in leaves: sheet.hide()
	_pose(0)

func _resize() -> void:
	if app == null: return
	if state in [State.PREPARING,State.OPENING]: interrupt("resize")
	app.size = Vector2(get_viewport().size)
	_pose(1.0 if state == State.WORK else 0.0)
	app._layout_book()

func context() -> Dictionary:
	return {"page":app.album.page_index,"scroll":app.album.scroll_vertical,"right_scroll":app.album.right_scroll.scroll_vertical,"category":app.album.category_id,
		"criterion":app.album.preference.criterion,"direction":app.album.preference.direction,
		"selection":app.album.selected_id,"session":str(app.session.definition.id) if app.session != null else ""}

func _begin(kind: String, prior: Dictionary = {}) -> void:
	source_context = context() if prior.is_empty() else prior.duplicate(true)
	motion_kind = kind
	generation += 1
	state = State.PREPARING
	preparation_started = Time.get_ticks_usec()
	interrupted = ""
	app._cancel_interaction()
	app.presentation_locked = true
	transition_id = str(app.session.definition.id) if app.session != null else ""
	app.album.locked = true
	app.process_mode = Node.PROCESS_MODE_DISABLED
	held_buttons = Input.get_mouse_button_mask()
	release_barrier = true
	_prepare(generation)

func request_open(id: String) -> bool:
	if state != State.CATALOG or release_barrier or not app.session_indices.has(id): return false
	var prior: Dictionary = context()
	# Resolve and flush once, before any target animation. A rejected slot or
	# failed source write leaves the catalog and its retry/repair actions intact.
	if not app.activate(id): return false
	selected_id = id
	return_context = prior.duplicate(true)
	if app.sessions[int(app.session_indices[id])].completed:
		app.open_puzzle()
		state = State.WORK
		motion_kind = ""
		page_identity(paper_material,"work/"+id)
		_pose(1)
		return true
	direction = 1
	_begin("open",prior)
	return true

func request_return() -> bool:
	if state != State.WORK or release_barrier or app.information.visible or app.reveal_view.active: return false
	if not (app.work.visible or app.ending.visible): return false
	# Secure edits before hiding the work page. Later capture/settlement only
	# redisplays the already accepted destination and cannot write another save.
	app._cancel_interaction()
	if not app._flush_current(): return false
	target_page = int(return_context.get("page",app.album.page_index))
	direction = -1
	_begin("return")
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

func valid_motion(token: int) -> bool:
	if token != generation or not is_inside_tree(): return false
	var id: String = str(app.session.definition.id) if app.session != null else ""
	if id != transition_id:
		interrupt("leave")
		return false
	return true

func _exit_tree() -> void:
	generation += 1

func _prepare(token: int) -> void:
	if information_routes.moving():
		information_routes.prepare(token)
		return
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
		leaves[i].visible = i == 0 or motion_kind in ["open","return"]
		leaves[i].material_override.set_shader_parameter("side",float(direction))
		leaves[i].material_override.set_shader_parameter("turn",0.0)
		page_identity(leaves[i].material_override,"leaf/%s/%d/%d" % [motion_kind,source_context.page,i])
	page_identity(leaf_material,"catalog/%d/%s" % [source_context.page,"right" if direction == 1 else "left"])
	var source_rect: Vector4 = view_rect(motion_kind == "return")
	_ink(leaf_material,capture.get_texture(),source_rect)
	_ink(left_material,capture.get_texture(),source_rect)
	_ink(paper_material,capture.get_texture(),source_rect)
	await RenderingServer.frame_post_draw
	if not valid_motion(token): return
	catalog_texture = ImageTexture.create_from_image(capture.get_texture().get_image())
	_ink(leaf_material,catalog_texture,source_rect)
	_ink(left_material,catalog_texture,source_rect)
	_ink(paper_material,catalog_texture,source_rect)
	if motion_kind == "open": app.open_puzzle()
	elif motion_kind == "return":
		settling = true
		app.present_album()
		app.album.selected_id = return_context.get("selection",selected_id)
		app.album.commit_page(target_page,int(return_context.get("scroll",0)),int(return_context.get("right_scroll",0)))
		settling = false
	else: app.album.commit_page(target_page)
	await get_tree().process_frame
	if not valid_motion(token): return
	await RenderingServer.frame_post_draw
	if not valid_motion(token): return
	if motion_kind == "open":
		page_identity(paper_material,"work/"+selected_id)
		_ink(paper_material,capture.get_texture(),view_rect(true))
	elif motion_kind == "return":
		page_identity(left_material,"catalog/%d/left" % target_page)
		_ink(left_material,capture.get_texture(),view_rect(false))
		_ink(leaf_material,capture.get_texture(),view_rect(false))
		# The last returning leaf covers the current work with the catalog.
		for sheet: MeshInstance3D in leaves:
			_ink(sheet.material_override,capture.get_texture(),view_rect(false),true)
			page_identity(sheet.material_override,"catalog/%d/right" % target_page,true)
	else:
		page_identity(paper_material if direction == 1 else left_material,"catalog/%d/%s" % [target_page,"right" if direction == 1 else "left"])
		page_identity(leaf_material,"catalog/%d/%s" % [target_page,"left" if direction == 1 else "right"],true)
		_ink(paper_material if direction == 1 else left_material,capture.get_texture(),view_rect(false))
		_ink(leaf_material,capture.get_texture(),view_rect(false),true)
	elapsed = 0
	frames_ms.clear()
	wall_started = Time.get_ticks_usec()
	preparation_seconds = (wall_started-preparation_started)/1000000.0
	last_frame_usec = wall_started
	state = State.OPENING

func _process(delta: float) -> void:
	if state in [State.PREPARING,State.OPENING] and not valid_motion(generation): return
	if state == State.CATALOG and material_catalog_page != app.album.page_index: catalog_materials(app.album.page_index)
	if state == State.OPENING:
		var now: int = Time.get_ticks_usec()
		frames_ms.append((now-last_frame_usec)/1000.0)
		last_frame_usec = now
		var duration: float = information_routes.duration() if information_routes.moving() else DURATION if motion_kind == "open" else RETURN_DURATION if motion_kind == "return" else PAGE_DURATION
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
	# Track only events owned by this input barrier. During normal work Board
	# can consume a release before its parent sees it; retaining that old Down
	# would incorrectly block the next page forever.
	if (state in [State.PREPARING,State.OPENING] or release_barrier) and event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT,MOUSE_BUTTON_MIDDLE,MOUSE_BUTTON_XBUTTON1,MOUSE_BUTTON_XBUTTON2]:
		var mask: int = 1 << (event.button_index-1)
		held_buttons = (held_buttons | mask) if event.pressed else (held_buttons & ~mask)
	if state in [State.PREPARING,State.OPENING] or release_barrier: get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		if state in [State.PREPARING,State.OPENING]: interrupt("leave")

func interrupt(reason: String) -> void:
	if state not in [State.PREPARING,State.OPENING]: return
	interrupted = reason
	generation += 1
	_settle(reason != "leave")

func _settle(target: bool) -> void:
	if settling or state not in [State.PREPARING,State.OPENING]: return
	generation += 1
	settling = true
	if not target:
		# A cancelled or invalidated capture can only restore its bound source.
		# Never display a newly selected session under the previous page identity.
		var source_id: String = source_context.get("session","")
		var current_id: String = str(app.session.definition.id) if app.session != null else ""
		if current_id != source_id:
			if app.session_indices.has(source_id): app._bind_session(int(app.session_indices[source_id]))
			else:
				app.session = null
				app.board.session = null
	if information_routes.moving():
		information_routes.settle(target)
		_finish_settle()
		return
	var work: bool = target and motion_kind == "open"
	state = State.WORK if work else State.CATALOG
	if app.get_parent() != self: app.reparent(self,false)
	app.position = Vector2.ZERO
	app.size = Vector2(get_viewport().size)
	if work: app.open_puzzle()
	else:
		app.present_album()
		var destination: Dictionary = return_context if motion_kind == "return" else source_context
		app.album.selected_id = destination.selection
		var moved_page: bool = target and motion_kind == "page"
		app.album.commit_page(target_page if moved_page else int(destination.page),0 if moved_page else int(destination.scroll),0 if moved_page else int(destination.right_scroll))
		catalog_materials(app.album.page_index)
	if work: page_identity(paper_material,"work/"+selected_id)
	_finish_settle()

func _finish_settle() -> void:
	for sheet: MeshInstance3D in leaves:
		sheet.hide()
		_ink(sheet.material_override,null,Vector4.ZERO)
		_ink(sheet.material_override,null,Vector4.ZERO,true)
	_pose(1.0 if state in [State.WORK,State.INFORMATION] else 0.0)
	_ink(paper_material,null,Vector4.ZERO)
	_ink(left_material,null,Vector4.ZERO)
	catalog_texture = null
	information_routes.textures.clear()
	if capture != null:
		capture.queue_free()
		capture = null
	release_barrier = true
	app._cancel_interaction()
	app.presentation_locked = false
	settling = false
	motion_kind = ""

func request_quit() -> void:
	# Invalidate all pending awaits before asking the existing native/Web
	# lifecycle to flush. A refusal leaves a stable, usable source and retry.
	interrupt("leave")
	app._cancel_interaction()
	app.quit_after_flush()

func set_ui_scale(value: float) -> void:
	interrupt("ui-scale")
	app.set_ui_scale(value)

func _focus_interrupt(token: int) -> void:
	# OS notifications may arrive inside app.reparent(). Do not re-enter that
	# tree mutation, or interrupt a later motion after this one already settled.
	if token == generation: interrupt("focus")

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		_focus_interrupt.call_deferred(generation)
	if what == NOTIFICATION_APPLICATION_FOCUS_IN:
		# Releases outside the unfocused window may not arrive here. Reconcile
		# only on focus return; never turn a still-held transition press into input.
		held_buttons &= Input.get_mouse_button_mask()
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		if app != null: request_quit()

