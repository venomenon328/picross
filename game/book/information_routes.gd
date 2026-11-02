extends RefCounted
## A single immutable visit origin; separate from work -> catalog return_context.
const LEAF_SECONDS: float = 0.85
const PAN_SECONDS: float = 0.65
var book: Node3D
var origin: Dictionary = {}
var source: String = ""
var target: String = ""
var textures: Dictionary = {}

func _init(owner: Node3D) -> void: book = owner

func moving() -> bool:
	return book.motion_kind.begins_with("info-") and book.state in [book.State.PREPARING,book.State.OPENING]

func duration() -> float:
	return PAN_SECONDS if book.motion_kind == "info-pan" else LEAF_SECONDS

func request(section: String) -> bool:
	if section not in ["settings","help"] or book.release_barrier: return false
	if book.state not in [book.State.CATALOG,book.State.WORK,book.State.INFORMATION]: return false
	var app = book.app
	if book.state == book.State.INFORMATION:
		if app.info.section == section: return false
		source = app.info.section
		target = section
		book.direction = 0
		book._begin("info-pan")
		return true
	if app.reveal_view.active: return false
	app._cancel_interaction()
	var kind: String = "catalog" if book.state == book.State.CATALOG else "ending" if app.ending.visible else "work"
	# A passive catalog's placeholder session creates no save obligation.
	if kind != "catalog" and not app._flush_current(): return false
	origin = {"kind":kind,"id":str(app.session.definition.id) if app.session != null else "","catalog":book.context().duplicate(true)}
	app.information_origin = "album" if kind == "catalog" else kind
	source = kind
	target = section
	book.direction = 1
	app.info_scroll.scroll_vertical = 0
	app.info.help_scroll.scroll_vertical = 0
	book._begin("info-enter")
	return true

func request_return() -> bool:
	if book.state != book.State.INFORMATION or book.release_barrier or origin.is_empty(): return false
	book.app._cancel_interaction()
	if origin.kind != "catalog" and not book.app._flush_current(): return false
	source = book.app.info.section
	target = origin.kind
	book.direction = -1
	book._begin("info-return")
	return true

func rect(endpoint: String) -> Vector4:
	var result: Vector4 = book.view_rect(endpoint != "catalog")
	if endpoint == "settings": result.x -= 10.0
	return result

func present(endpoint: String) -> void:
	var app = book.app
	if endpoint in ["settings","help"]:
		app.info.present(endpoint)
	elif endpoint == "catalog":
		book.settling = true
		app.present_album()
		var c: Dictionary = origin.catalog
		app.album.selected_id = c.selection
		app.album.commit_page(c.page,c.scroll,c.right_scroll)
		book.catalog_materials(c.page)
		book.settling = false
	else:
		# No session reload/snapshot restore: explicit settings changes survive.
		app.open_puzzle()
		book.page_identity(book.paper_material,"work/"+origin.id)

func prepare(token: int) -> void:
	book.capture = SubViewport.new()
	book.capture.size = book.get_viewport().size
	book.capture.disable_3d = true
	book.capture.transparent_bg = true
	book.capture.gui_disable_input = true
	book.capture.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	book.add_child(book.capture)
	book.app.reparent(book.capture,false)
	book.app.position = Vector2.ZERO
	book.app.size = Vector2(book.capture.size)
	var focus: Control = book.capture.gui_get_focus_owner()
	if focus != null: focus.release_focus()
	for sheet: MeshInstance3D in book.leaves: sheet.hide()
	for material: ShaderMaterial in [book.left_material,book.paper_material]:
		book._ink(material,book.capture.get_texture(),rect(source))
	# Render the source, then each needed destination at native pixel scale.
	# All three snapshots share one temporary viewport and the same UI instance.
	await book.get_tree().process_frame
	if not book.valid_motion(token): return
	await RenderingServer.frame_post_draw
	if not book.valid_motion(token): return
	book.catalog_texture = ImageTexture.create_from_image(book.capture.get_texture().get_image())
	for material: ShaderMaterial in [book.left_material,book.paper_material]:
		book._ink(material,book.catalog_texture,rect(source))
	if target in ["settings","help"]:
		for endpoint: String in ["settings","help"]:
			present(endpoint)
			await book.get_tree().process_frame
			if not book.valid_motion(token): return
			await RenderingServer.frame_post_draw
			if not book.valid_motion(token): return
			textures[endpoint] = ImageTexture.create_from_image(book.capture.get_texture().get_image())
		present(target)
	else:
		present(target)
		await book.get_tree().process_frame
		if not book.valid_motion(token): return
		await RenderingServer.frame_post_draw
		if not book.valid_motion(token): return
		textures[target] = ImageTexture.create_from_image(book.capture.get_texture().get_image())
	if book.motion_kind == "info-pan":
		book._ink(book.left_material,textures.settings,rect("settings"))
		book._ink(book.paper_material,textures.help,rect("help"))
	else:
		book.leaf.show()
		book.leaf_material.set_shader_parameter("side",float(book.direction))
		book.leaf_material.set_shader_parameter("turn",0.0)
		book._ink(book.leaf_material,book.catalog_texture,rect(source))
		if book.direction == 1:
			book._ink(book.left_material,book.catalog_texture,rect(source))
			book._ink(book.paper_material,textures.help,rect("help"))
			book._ink(book.leaf_material,textures.settings,rect("settings"),true)
		else:
			book._ink(book.left_material,textures[target],rect(target))
			book._ink(book.paper_material,book.catalog_texture,rect(source))
			book._ink(book.leaf_material,textures[target],rect(target),true)
	if book.motion_kind == "info-pan":
		book.page_identity(book.left_material,"information/settings")
		book.page_identity(book.paper_material,"information/help")
	elif book.direction == 1:
		book.page_identity(book.paper_material,"information/help")
		book.page_identity(book.leaf_material,"catalog/%d/right" % origin.catalog.page if source == "catalog" else "work/"+origin.id)
		book.page_identity(book.leaf_material,"information/settings",true)
	else:
		book.page_identity(book.left_material,"catalog/%d/left" % origin.catalog.page if target == "catalog" else "work/"+origin.id+"/left")
		book.page_identity(book.paper_material,"information/help")
		book.page_identity(book.leaf_material,"information/settings")
		book.page_identity(book.leaf_material,"catalog/%d/right" % origin.catalog.page if target == "catalog" else "work/"+origin.id,true)
	book.elapsed = 0
	book.frames_ms.clear()
	book.wall_started = Time.get_ticks_usec()
	book.preparation_seconds = (book.wall_started-book.preparation_started)/1000000.0
	book.last_frame_usec = book.wall_started
	book.state = book.State.OPENING
	pose(0)

func pose(progress: float) -> void:
	var active: bool = moving()
	var from: Vector4 = rect(source) if active else rect(book.app.info.section)
	var to: Vector4 = rect(target) if active else from
	var view: Vector4 = from.lerp(to,smoothstep(0,1,progress))
	var center := Vector3(view.x+view.z/2,view.y+view.w/2,30)
	book.camera.size = view.w
	book.camera.position = center
	book.camera.look_at(center-Vector3(0,0,30))
	var turn: float = smoothstep(0,1,progress)
	book.leaf_material.set_shader_parameter("turn",1.0 if active and book.motion_kind == "info-pan" else turn)
	book.paper_material.set_shader_parameter("shadow",sin(turn*PI) if active and book.direction != 0 else 0.0)
	book.left_material.set_shader_parameter("shadow",sin(turn*PI)*0.65 if active and book.direction != 0 else 0.0)
	if active and progress >= 1:
		book.leaf.hide()
		if target in ["settings","help"]:
			book.page_identity(book.left_material,"information/settings")
			book.page_identity(book.paper_material,"information/help")
			book._ink(book.left_material,textures.settings,rect("settings"))
			book._ink(book.paper_material,textures.help,rect("help"))
		else:
			book._ink(book.left_material,textures[target],rect(target))
			book._ink(book.paper_material,textures[target],rect(target))
		if target == "catalog": book.catalog_materials(origin.catalog.page)
		elif target in ["work","ending"]: book.page_identity(book.paper_material,"work/"+origin.id)

func settle(use_target: bool) -> void:
	# Escape reverses entry/pan, but a return always reaches its bound origin.
	var endpoint: String = endpoint(source,target,book.motion_kind,use_target)
	if book.app.get_parent() != book: book.app.reparent(book,false)
	book.app.position = Vector2.ZERO
	book.app.size = Vector2(book.get_viewport().size)
	book.state = book.State.INFORMATION if endpoint in ["settings","help"] else book.State.CATALOG if endpoint == "catalog" else book.State.WORK
	present(endpoint)
	if book.state == book.State.INFORMATION:
		book.page_identity(book.left_material,"information/settings")
		book.page_identity(book.paper_material,"information/help")
	else:
		origin = {}
	book.motion_kind = ""

static func endpoint(from: String, to: String, kind: String, use_target: bool) -> String:
	return to if use_target or kind == "info-return" else from
