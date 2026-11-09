extends SceneTree
const Store = preload("res://model/save_store.gd")
var surface: Viewport
var book: Node3D
var app: Control
var output: String
var records: Array = []
var assertions: Array = []

func _initialize() -> void: call_deferred("run")
func check(value: bool, text: String) -> void:
	assertions.append({"ok":value,"description":text})
	if not value: push_error("RAND_VISUAL_FAIL: "+text)

func frames(count: int = 4) -> void:
	for i: int in range(count): await process_frame
	await RenderingServer.frame_post_draw

func settle() -> void:
	var start: int = Time.get_ticks_msec()
	await frames()
	while book.state in [book.State.PREPARING,book.State.OPENING] or book.settling or book.release_barrier:
		await process_frame
		if Time.get_ticks_msec()-start > 25000:
			check(false,"unaccelerated book transition timed out")
			break
	await frames()

func click_at(point: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	# Native GUI tests move outside first so resize/return cannot leave a
	# stale hover owner at a numerically identical point in a new viewport.
	var outside := InputEventMouseMotion.new()
	outside.position = Vector2(-20,-20)
	outside.global_position = outside.position
	surface.push_input(outside,true)
	var motion := InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	surface.push_input(motion,true)
	for pressed: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.global_position = point
		event.button_index = button
		event.pressed = pressed
		surface.push_input(event,true)

func click(control: Control) -> void: click_at(control.get_global_rect().get_center())

func rect(box: Rect2) -> Array: return [box.position.x,box.position.y,box.size.x,box.size.y]

func geometry() -> Dictionary:
	var result: Dictionary = {"paper":rect(book.projected_information(1) if app.information.visible else book.projected_paper(app.work.visible)),"title":rect(app.title.get_rect()),"board":rect(app.board.get_rect()),"cell_size":app.board.view.cell_size,"requested_cell":app.board.requested_cell,"grid":rect(Rect2(app.board.position+app.board.view.origin,Vector2(app.board.session.player.width,app.board.session.player.height)*app.board.view.cell_size)) if app.board.session != null else [],"help":rect(app.help_panel.get_global_rect()),"register":rect(app.help_panel.navigation.get_global_rect()),"article":rect(app.info.help_scroll.get_global_rect()),"paragraph_width":app.help_panel.paragraph_width,"tools":rect(app.tools_scroll.get_global_rect())}
	return result

func shot(name: String) -> void:
	await frames()
	var image: Image = surface.get_texture().get_image()
	var filename: String = name+".png"
	check(image.save_png(output.path_join(filename)) == OK,"saved native original "+filename)
	var boxes: Array = []
	for box: Rect2 in app.marginalia.boxes: boxes.append(rect(box))
	records.append({"file":filename,"viewport":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,"head":OS.get_environment("RAND_PRODUCT_HEAD"),"family":app.marginalia.family,"drawing_visible":app.marginalia.visible,"boxes":boxes,"chapter":app.help_panel.chapter,"help_scroll":app.info.help_scroll.scroll_vertical,"geometry":geometry(),"source":"unmodified main.tscn/book/main.gd; native Windows OpenGL3 Window framebuffer; synthetic catalog and isolated saves; no postprocessing"})

func comparison(name: String) -> void:
	print("RAND_PAIR ",name," key=",app.marginalia.family," boxes=",app.marginalia.boxes)
	if app.information.visible:
		for control: Control in [app.status_label,app.layout_warning,app.work_repair_button,app.save_retry,app.info.help_heading,app.help_panel.navigation,app.info.help_scroll.get_v_scroll_bar()]:
			print("RAND_HARD ",control.name," ",control.is_visible_in_tree()," ",control.get_global_rect())
	app.marginalia.show()
	await shot(name+"-with")
	var before: Dictionary = geometry()
	var cells: Array = app.session.player.cells.duplicate() if app.session != null else []
	app.marginalia.hide()
	await shot(name+"-without")
	check(geometry() == before and (app.session == null or cells == app.session.player.cells),"identical geometry/state across "+name+" with/without")
	app.marginalia.show()

func resize(width: int, height: int, u: float) -> void:
	if app.display_controller != null: app.display_controller.set_process(false)
	surface.size = Vector2i(width,height)
	app.size = Vector2(width,height)
	app.set_ui_scale(u)
	await frames(8)
	app._layout_book()
	await frames()

func open_id(id: String) -> void:
	check(book.request_open(id),"canonical open "+id)
	await settle()
	check(app.work.visible and book.state == book.State.WORK,"real opening reaches work")
	app.board.requested_cell = 24
	app._layout_book()
	await frames()

func back() -> void:
	print("RAND_BACK ",book.state," barrier=",book.release_barrier," held=",book.held_buttons," focus=",surface.gui_get_focus_owner()," rect=",app.album_button.get_global_rect()," mouse=",Input.get_mouse_button_mask())
	click(app.album_button)
	print("RAND_BACK_AFTER ",book.state," barrier=",book.release_barrier," held=",book.held_buttons)
	await settle()
	check(app.album.visible,"real return reaches catalog")

func run() -> void:
	output = OS.get_environment("RAND_VISUAL_OUTPUT")
	DirAccess.make_dir_recursive_absolute(output)
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	surface = root
	surface.size = Vector2i(2560,1440)
	surface.gui_embed_subwindows = true
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames(12)
	await resize(2560,1440,1)
	await shot("catalog-1440-ui100")
	check(app.choices.size() == 24 and app.marginalia.family.is_empty(),"full 12/12 catalog has no pilot art")
	var specs: Array = [["water","pz-test-kat2-001"],["nature","pz-test-kat2-003"]]
	if OS.get_environment("RAND_QUICK") == "1": specs = []
	for spec: Array in specs:
		await open_id(spec[1])
		for window: Vector2i in [Vector2i(1920,1080),Vector2i(2560,1440)]:
			await resize(window.x,window.y,1)
			await comparison(spec[0]+"-"+str(window.y)+"-ui100")
		var pair: Array = app.marginalia.boxes.duplicate()
		var family: String = app.marginalia.family
		var cells: Array = app.session.player.cells.duplicate()
		var history: int = app.session.player.history.size()
		click_at(app.board.global_position+app.board.view.cell_rect(Vector2i(2,2)).get_center())
		await frames()
		check(app.session.player.history.size() == history+1,"native GUI cell event passes with art active")
		click(app.undo_button)
		await frames()
		check(app.session.player.cells == cells and app.marginalia.boxes == pair and app.marginalia.family == family,"commit/undo preserve drawing and restore cells")
		# Put the board near its fit ceiling: demonstrate actual layout-dependent omission.
		app.board.requested_cell = 72
		app._layout_book()
		await frames()
		await shot(spec[0]+"-1440-high-zoom")
		await back()
		await open_id(spec[1])
		check(app.marginalia.family == family,"reopening same leaf retains category drawing")
		await back()
	await resize(2560,1440,1)
	await open_id("pz-test-kat2-001")
	click(app.actions.help)
	await settle()
	check(app.info.section == "help","real work-to-help transition")
	for window: Vector2i in [Vector2i(1920,1080),Vector2i(2560,1440)]:
		await resize(window.x,window.y,1)
		await comparison("help-"+str(window.y)+"-ui100")
	var family: String = app.marginalia.family
	var boxes: Array = app.marginalia.boxes.duplicate()
	click(app.help_panel.buttons[2])
	await frames()
	for i: int in range(12):
		click_at(app.info.help_scroll.get_global_rect().get_center(),MOUSE_BUTTON_WHEEL_DOWN)
	await frames()
	check(app.help_panel.chapter == 2 and app.info.help_scroll.scroll_vertical > 0,"chapter pointer and article wheel with drawings")
	check(app.marginalia.family == family and app.marginalia.boxes == boxes,"chapter/wheel keep same pair and placement")
	await shot("help-1440-ui100-scrolled")
	var offset: int = app.info.help_scroll.scroll_vertical
	click(app.information.get_node("settings-access"))
	var start: int = Time.get_ticks_msec()
	while book.state != book.State.OPENING and Time.get_ticks_msec()-start < 20000: await process_frame
	# Sample the actual moving frame, no manually assigned pose.
	while book.state == book.State.OPENING and book.elapsed < 0.26: await process_frame
	await shot("help-settings-pan-moving")
	check(app.get_parent() == book.capture and book.capture != null,"drawings reparent with live UI into real book capture")
	await settle()
	check(app.marginalia.family.is_empty(),"settings has no pilot art")
	await shot("settings-1440-ui100")
	click(app.information.get_node("help-access"))
	await settle()
	check(app.info.help_scroll.scroll_vertical == offset and app.help_panel.chapter == 2 and app.marginalia.family == family and app.marginalia.boxes == boxes,"real settings pan return keeps article and drawings")
	await shot("help-1440-return")
	await resize(1280,720,1.25)
	await comparison("help-720-ui125-tight")
	click(app.actions["nav-work"])
	await settle()
	await back()
	await open_id("pz-test-kat2-053")
	app.board.requested_cell = 72
	app._layout_book()
	await frames()
	await comparison("large-720-ui125-high-zoom")
	await resize(2560,1440,1.25)
	await comparison("large-1440-ui125-high-zoom")
	await back()
	await shot("catalog-1440-ui125")
	var passed: bool = true
	for item: Dictionary in assertions:
		if not item.ok: passed = false
	var report: Dictionary = {"package":"RAND-P1","head":OS.get_environment("RAND_PRODUCT_HEAD"),"engine":Engine.get_version_info(),"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"test_only":true,"unmodified_product_root":true,"physical_os_mouse":false,"assertions":assertions,"records":records,"passed":passed}
	var file := FileAccess.open(output.path_join("native.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	file.close()
	print("RAND_NATIVE_OK" if passed else "RAND_NATIVE_FAILED")
	quit(0 if passed else 1)
