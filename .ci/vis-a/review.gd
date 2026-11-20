extends SceneTree
## Package-scoped evidence on main.tscn. No book_fixture or modified product scripts.
const Book = preload("res://book/main.gd")
const Store = preload("res://model/save_store.gd")
const BGTests = preload("res://tests/background_tests.gd")
const ID := "pz-vis-a"
var book: Book
var app: Control
var output: String
var failures: Array[String] = []
var replayed := false
var movement_frames: Dictionary = {}

func _initialize() -> void: run.call_deferred()

func check(value: bool, label: String) -> void:
	if not value:
		failures.append(label)
		printerr("VIS_A_FAIL ",label)

func drawn() -> void:
	await process_frame
	await RenderingServer.frame_post_draw

func frame(name: String) -> void:
	await drawn()
	check(root.get_texture().get_image().save_png(output.path_join(name+".png")) == OK,name)

func settle() -> void:
	while book.state in [Book.State.PREPARING,Book.State.OPENING] or book.release_barrier:
		await process_frame
	await drawn()

func opening() -> void:
	while book.state == Book.State.PREPARING: await process_frame
	check(book.state == Book.State.OPENING,"target prepared before motion")

func slot_hashes() -> Dictionary:
	var result := {}
	for file: String in DirAccess.get_files_at(Store.test_root_override):
		result[file] = FileAccess.get_sha256(Store.test_root_override.path_join(file))
	return result

func escape() -> void:
	var key := InputEventKey.new()
	key.keycode = KEY_ESCAPE
	key.pressed = true
	root.push_input(key,true)

func sampled_motion(prefix: String, duration: float) -> void:
	for i: int in range(6):
		while book.state == Book.State.OPENING and book.elapsed < duration*(i+0.3)/7: await process_frame
		await drawn()
		movement_frames["motion-"+prefix+"-"+str(i)] = root.get_texture().get_image()

func shadow_case(label: String) -> void:
	var artwork: Rect2 = app.reveal_view.raster_rect() if label == "grid" else app.reveal_view.artwork_rect()
	var drawing: Rect2 = app.puzzle_background.box
	check(book.request_return(),"return "+label)
	await opening()
	while book.elapsed < 0.34: await process_frame
	book.set_process(false)
	await frame("shadow-"+label)
	var shadowed := root.get_texture().get_image()
	var strength: float = book.paper_material.get_shader_parameter("shadow")
	book.paper_material.set_shader_parameter("shadow",0.0)
	await drawn()
	var neutral := root.get_texture().get_image()
	var source := book.catalog_texture.get_image()
	var view := book.view_rect(true)
	var counts := {"paper":0,"drawing":0,"opaque":0,"alpha":0}
	for y: int in range(80,source.get_height()-60,5):
		for x: int in range(100,source.get_width()-100,5):
			var uv := Vector2(x+0.5,y+0.5)/Vector2(source.get_size())
			var world := Vector3(view.x+uv.x*view.z,view.y+(1.0-uv.y)*view.w,0)
			var p := Vector2i(book.camera.unproject_position(world))
			if not Rect2i(Vector2i.ZERO,neutral.get_size()).has_point(p): continue
			var ink := source.get_pixel(x,y)
			if neutral.get_pixelv(p).get_luminance()-shadowed.get_pixelv(p).get_luminance() < 0.018: continue
			var point := Vector2(x,y)
			if artwork.has_point(point):
				if ink.a > 0.97: counts.opaque += 1
				elif ink.a > 0.1 and ink.a < 0.9: counts.alpha += 1
			elif drawing.has_point(point) and ink.a > 0.06 and ink.a < 0.42:
				counts.drawing += 1
			elif ink.a == 0: counts.paper += 1
	print("VIS_A_SHADOW ",label," ",counts)
	for kind: String in counts: check(counts[kind] > 0,"cast shadow "+label+"/"+kind)
	book.paper_material.set_shader_parameter("shadow",strength)
	book.wall_started = Time.get_ticks_usec()-roundi(book.elapsed*1000000)
	book.set_process(true)
	if label == "image": await sampled_motion("b",book.RETURN_DURATION)
	await settle()
	check(book.state == Book.State.CATALOG and app.puzzle_background.binding.is_empty(),"catalog releases "+label)

func interruptions() -> void:
	await shadowless_return()
	var saved := slot_hashes()
	var ink = app.puzzle_background
	var native: RefCounted = ink.backend
	var controlled := BGTests.ControlledLoader.new()
	ink.backend = controlled
	check(book.request_open(ID),"open pending before Escape")
	escape()
	await settle()
	check(book.state == Book.State.CATALOG and ink.binding.is_empty(),"Escape invalidates target")
	controlled.fail()
	await drawn()
	check(book.request_open(ID),"open pending before resize")
	book._resize()
	check(app.ending.visible and ink.frozen and ink.diagnostic == "forced_stabilization","immediate resize without image")
	await settle()
	controlled.fail()
	await drawn()
	check(ink.texture == null,"no late image")
	app.show_information("help")
	await settle()
	check(ink.binding.is_empty(),"information clears target")
	check(book.information_routes.request_return(),"information return")
	escape()
	check(app.ending.visible and ink.frozen and ink.diagnostic == "forced_stabilization","Escape on information return")
	await settle()
	controlled.fail()
	await drawn()
	ink.backend = native
	await shadowless_return()
	check(book.request_open(ID),"focus after readiness")
	while ink.ready_texture == null and not ink.frozen: await process_frame
	book._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	await settle()
	check(ink.texture != null and app.ending.visible,"focus preserves ready or published image")
	await shadowless_return()
	check(book.request_open(ID),"Escape during motion")
	await opening()
	var history_size: int = app.session.player.history.size()
	var down := InputEventMouseButton.new()
	down.position = Vector2(400,300)
	down.button_index = MOUSE_BUTTON_LEFT
	down.pressed = true
	root.push_input(down,true)
	escape()
	check(book.release_barrier and book.state == Book.State.CATALOG,"held press stays captured")
	down.pressed = false
	root.push_input(down,true)
	await settle()
	check(app.session.player.history.size() == history_size and slot_hashes() == saved,"interruptions preserve saves and history")

func shadowless_return() -> void:
	check(book.request_return(),"return to catalog")
	await settle()

func run() -> void:
	output = OS.get_environment("VIS_A_OUTPUT")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(2); return
	root.size = Vector2i(1920,1080)
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	app = book.app
	await drawn()
	var initial := slot_hashes()
	app.reveal_view.progressed.connect(func(_work: float, _caption: float) -> void:
		if app.reveal_view.active: replayed = true)
	check(book.request_open(ID),"cold solved request")
	await opening()
	var ink = app.puzzle_background
	check(ink.is_visible_in_tree() and ink.frozen and ink.texture != null and app.ending.visible,"first target capture has selected ink")
	var captured := book.capture.get_texture().get_image()
	var line: Vector2i = Vector2i(ink.box.position+ink.box.size*Vector2(190.0/2304,520.0/576))
	check(captured.get_pixelv(line).a > 0.20 and captured.get_pixelv(line+Vector2i(0,-8)).a == 0,"native background line in first transparent target")
	check(captured.save_png(output.path_join("first-target.png")) == OK,"first captured content")
	await sampled_motion("a",book.DURATION)
	await settle()
	print("VIS_A_COLD preparation_s=",book.preparation_seconds," motion_s=",book.motion_wall_seconds," load_us=",ink.last_load_usec)
	check(book.DURATION == 3.0 and book.motion_wall_seconds >= 3 and book.elapsed == book.DURATION and not replayed and not app.reveal_view.grid_selected,"complete three-second motion without replay")
	check(slot_hashes() == initial,"cold opening preserves save")
	await frame("title-short")
	await shadow_case("image")
	check(book.request_open(ID),"reopen for reset")
	await settle()
	app._ask_reset_id(ID,"ending")
	app.reset_dialog.hide()
	app._reset_selected()
	check(book.state == Book.State.WORK and app.work.visible and not app.session.completed,"confirmed reset directly to work")
	root.size = Vector2i(1280,720)
	app.set_ui_scale(1.25)
	await drawn()
	var visit: Dictionary = ink.binding.duplicate(true)
	var count: int = ink.request_count
	app.session.definition.reveal.name = "Süße Grüße aus Đà Nẵng – Églantine, đượm und leuchtende Blüten am Fluss"
	var b = app.board
	b.update_pointer_hover(b.view.cell_rect(Vector2i(17,32)).get_center())
	await frame("highlight")
	var changes: Array[Dictionary] = []
	for y: int in range(app.session.player.height):
		for x: int in range(app.session.player.width):
			var value: int = app.session.definition.solution[y][x]
			if value > 0: changes.append({"index":y*app.session.player.width+x,"before":-1,"after":value})
	var last: Dictionary = changes.pop_back()
	app.session.player.commit(changes)
	app.session.gesture.begin(app.session.player,Vector2i(int(last.index)%app.session.player.width,int(last.index)/app.session.player.width),last.after)
	check(app.session.finish() and app.session.completed,"first completion committed")
	app._on_commit()
	while app.reveal_view.active and app.reveal_view.elapsed < 0.55: await process_frame
	check(app.reveal_view.active and ink.visible and ink.texture != null,"background during live reveal")
	await frame("reveal")
	while app.reveal_view.active: await process_frame
	await frame("image")
	app._select_completion(true)
	await frame("grid")
	app._select_completion(false)
	check(ink.binding == visit and ink.request_count == count and ink.is_visible_in_tree(),"one visit across reveal image raster image")
	app._select_completion(true)
	await shadow_case("grid")
	check(book.request_open(ID),"solved opening after catalog")
	await opening()
	# Compare the affected final neutral pose, with identical camera and geometry.
	book.set_process(false)
	book._pose(1)
	await frame("capture")
	book._settle(true)
	book.set_process(true)
	await settle()
	await frame("direct")
	check(not app.reveal_view.grid_selected and app.ending.visible and ink.texture != null,"stable solved image")
	await interruptions()
	for name: String in movement_frames:
		check(movement_frames[name].save_png(output.path_join(name+".png")) == OK,name)
	if failures.is_empty(): print("VIS_A_BOOK_OK")
	quit(0 if failures.is_empty() else 3)
