extends SceneTree
const InkButton = preload("res://ui/book_button.gd")
const Store = preload("res://model/save_store.gd")
var surface: Viewport
var book: Node3D
var app: Control
var output: String
var rows: Array = []
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func frames(n: int = 5) -> void:
	for i: int in range(n): await process_frame
func check(value: bool, label: String) -> void:
	rows.append({"assertion":label,"passed":value})
	if not value: failures.append(label); print("NAV_VISUAL_FAIL ",label)
func click_at(point: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = point
	surface.push_input(motion,true)
	for down: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.global_position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		surface.push_input(event,true)
func click(control: Control) -> void: click_at(control.get_global_rect().get_center())
func settled() -> void:
	var end: int = Time.get_ticks_msec()+10000
	while (book.state in [book.State.PREPARING,book.State.OPENING] or book.release_barrier) and Time.get_ticks_msec()<end: await process_frame
	check(book.state not in [book.State.PREPARING,book.State.OPENING] and not book.release_barrier,"real motion and release barrier settled")
	await frames(8)
func shot(name: String) -> void:
	await frames(8)
	if app.album.visible:
		preload("res://tests/navigation_cases.gd").geometry(self)
	elif app.information.visible:
		var heading: Control = app.info.settings_heading if app.info.section == "settings" else app.info.help_heading
		check(is_equal_approx(app.actions["nav-work"].global_position.y,heading.global_position.y),"native information title at original top edge beside navigation")
		var image_box := Rect2(heading.global_position+heading.image_rect().position,heading.image_rect().size)
		for button: Control in [app.actions["nav-work"],app.information.get_node("settings-access"),app.information.get_node("help-access")]:
			check(not image_box.intersects(button.get_global_rect()),"native whole title original clears symbol target")
	await RenderingServer.frame_post_draw
	var file: String = name+".png"
	check(surface.get_texture().get_image().save_png(output.path_join(file)) == OK,"original capture "+file)
	rows.append({"file":file,"viewport":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,"book_state":book.state,"section":app.info.section,"page":app.album.page_index,"origin":app.information_origin})
func hover(control: Control) -> void:
	var event := InputEventMouseMotion.new()
	event.position = control.get_global_rect().get_center()
	surface.push_input(event,true)
	await create_timer(0.9).timeout
	await frames()
func resize_viewport(extent: Vector2i, u: float) -> void:
	surface.size = extent
	app.set_ui_scale(u)
	await frames(12)
func run() -> void:
	output = OS.get_environment("NAV_VISUAL_OUTPUT")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	DirAccess.make_dir_recursive_absolute(output)
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	surface = root
	root.gui_embed_subwindows = true
	root.size = Vector2i(1920,1080)
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames(12)
	check(app.display_settings != null,"actual native Windows display settings present")
	if app.display_controller != null: app.display_controller.set_process(false)
	check(book.get_script().resource_path == "res://book/main.gd","unmodified regular product root")
	app.album.choose_category("gebaeude-bauwerke")
	app.album.choose_sort("size")
	await frames()
	check(app.album.previous_button.disabled and not app.album.next_button.disabled,"first filtered spread boundary")
	preload("res://tests/navigation_cases.gd").inventory(self)
	app.album.quit_button.grab_focus()
	await hover(app.album.quit_button)
	var quit_tip: Control = app.album.quit_button.tooltip_ref.get_ref() if app.album.quit_button.tooltip_ref != null else null
	check(quit_tip != null and quit_tip.is_visible_in_tree() and app.album.quit_button.tooltip_text == "Beenden" and app.album.quit_button.accessibility_name == "Beenden" and app.album.quit_button.text.is_empty(),"hand-drawn quit X exact tooltip/name and native hover/focus")
	await shot("01-catalog-first-1920-ui100")
	app.album.ensure_control_visible(app.choices[1])
	await frames()
	var origin_selection: String = app.album.selected_id
	click(app.choices[1])
	await settled()
	check(book.state == book.State.WORK,"pointer opens actual working leaf")
	click_at(app.board.global_position+app.board.view.cell_rect(Vector2i.ZERO).get_center())
	await frames()
	check(app.session.player.cursor == 1,"viewport cell click commits work")
	var id: String = str(app.session.definition.id)
	var cells: Array = app.session.player.cells.duplicate()
	var history: Array = app.session.player.history.duplicate(true)
	await hover(app.actions["menu"])
	var tip: Control = app.actions["menu"].tooltip_ref.get_ref() if app.actions["menu"].tooltip_ref != null else null
	check(tip != null and tip.is_visible_in_tree(),"actual delayed gear tooltip hover")
	await shot("02-work-gear-tooltip-1920-ui100")
	click(app.actions["help"])
	await settled()
	check(app.info.section == "help" and app.information_origin == "work","work to help by pointer")
	click(app.help_panel.buttons[2])
	await frames(12)
	app.info.help_scroll.scroll_vertical = 260
	await frames(12)
	var position: int = app.info.help_scroll.scroll_vertical
	var serial: int = book.generation
	click(app.information.get_node("help-access"))
	await frames()
	check(app.help_panel.chapter == 2 and app.info.help_scroll.scroll_vertical == position and book.generation == serial,"active help click keeps article and animation generation")
	await shot("03-help-active-1920-ui100")
	click(app.information.get_node("settings-access"))
	await settled()
	preload("res://tests/navigation_cases.gd").inventory(self)
	var symbols: Array = []
	for node: Node in app.find_children("*","Button",true,false):
		if node is InkButton and ((node.text.is_empty() and (node.image != null or node.swatch.a > 0)) or node.text == "?"):
			symbols.append({"action":node.action_id,"tooltip":node.tooltip_text,"accessible_name":node.accessibility_name,"disabled":node.disabled})
	rows.append({"actual_native_windows_symbol_inventory":symbols})
	app.information.get_node("settings-access").grab_focus()
	await shot("04-settings-focus-1920-ui100")
	click(app.information.get_node("help-access"))
	await settled()
	check(app.help_panel.chapter == 2 and app.info.help_scroll.scroll_vertical == position,"real pan preserves help chapter and reading")
	click(app.information.get_node("settings-access"))
	await settled()
	click(app.actions["nav-work"])
	await settled()
	check(app.work.visible and str(app.session.definition.id) == id and app.session.player.cells == cells and app.session.player.history == history,"real work-help-settings-back keeps work")
	click(app.album_button)
	await settled()
	check(app.recent_panel.visible and app.album.selected_id == origin_selection,"own work arrow restores bound catalog and recent panel")
	await shot("05-catalog-recent-1920-ui100")
	await resize_viewport(Vector2i(2560,1440),1.0)
	await shot("06-catalog-half-recent-2560-ui100")
	click(app.album.next_button)
	await settled()
	check(app.album.page_index == 1 and app.album.next_button.disabled and not app.album.previous_button.disabled,"last filtered spread by pointer")
	app.album.scroll.scroll_vertical = 90
	app.album.right_scroll.scroll_vertical = 140
	await frames()
	var pair: Vector2i = app.album.positions()
	click(app.album.help_button)
	await settled()
	click(app.information.get_node("settings-access"))
	await settled()
	click(app.actions["nav-work"])
	await settled()
	check(app.album.page_index == 1 and app.album.positions() == pair and app.album.category_id == "gebaeude-bauwerke" and app.album.preference.criterion == "size","real filtered later catalog-help-settings-back restores both offsets")
	await shot("07-catalog-last-2560-ui100")
	await resize_viewport(Vector2i(1280,720),1.25)
	app.session.gesture.begin(app.session.player,Vector2i(1,0),1)
	app.session.finish()
	app.store.fail_step = "after_temp"
	app._on_commit()
	await frames()
	var serial_before: int = book.generation
	click(app.album.help_button)
	await frames()
	check(book.state == book.State.CATALOG and book.generation == serial_before and app.save_retry.visible,"pending save blocks header help with visible retry")
	click(app.album.quit_button)
	await frames()
	check(book.state == book.State.CATALOG and app.save_retry.visible,"pending save blocks actual quit X and keeps retry")
	app.album.notice_area.ensure_control_visible(app.save_retry)
	await frames()
	await shot("08-catalog-error-full-recent-1280-ui125")
	app.store.fail_step = ""
	click(app.save_retry)
	await frames()
	check(not app.save_retry.visible and app.slot_errors[app.sessions.find(app.session)].is_empty(),"real retry clears pending error")
	click(app.album.settings_button)
	await settled()
	await shot("09-settings-1280-ui125")
	click(app.information.get_node("help-access"))
	await settled()
	await shot("10-help-1280-ui125")
	click(app.actions["nav-work"])
	await settled()
	app.album.choose_category("voegel")
	await frames()
	check(app.album.previous_button.disabled and app.album.next_button.disabled,"single filtered spread both inactive")
	await shot("11-catalog-single-1280-ui125")
	var file := FileAccess.open(output.path_join("observations.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"product_head":OS.get_environment("NAV_PRODUCT_HEAD"),"engine":Engine.get_version_info(),"display_server":DisplayServer.get_name(),"adapter":RenderingServer.get_video_adapter_name(),"input":"native Windows root Window viewport events; isolated synthetic registry/profiles; unaccelerated regular book root; display watchdog paused only for measured viewport sizes; no OS desktop input","screen_pixels":DisplayServer.screen_get_size(),"dpi":DisplayServer.screen_get_dpi(),"screen_scale":DisplayServer.screen_get_scale(),"rows":rows,"failures":failures},"\t")+"\n")
	file.close()
	print("NAV_VISUAL_DONE failures=",failures)
	quit(0 if failures.is_empty() else 4)
