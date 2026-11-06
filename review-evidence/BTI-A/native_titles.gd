extends SceneTree
## One-time BTI evidence: ordinary main scene, real rendered Windows viewport.
var book: Node
var app: Control
var folder: String
var checks := 0
var failures: Array[String] = []
var samples: Array = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		print("BTI_FAIL ",message)
func settle(seconds: float = 0.1) -> void:
	await create_timer(seconds).timeout
	var deadline: int = Time.get_ticks_msec()+10000
	while app.presentation_locked and Time.get_ticks_msec()<deadline: await process_frame
	check(not app.presentation_locked,"natural book transition completes")
	await process_frame
	await process_frame
func click(control: Control) -> void:
	check(control.is_visible_in_tree(),"pointer target visible: "+str(control.name))
	var point: Vector2 = control.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = point
	root.push_input(motion,true)
	for down: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		root.push_input(event,true)
func button(caption: String) -> Control:
	for node: Node in app.album.find_children("*","Button",true,false):
		if node.text == caption: return node
	return null
func shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	check(root.get_texture().get_image().save_png(folder.path_join(name+".png")) == OK,"native capture "+name)
func layout(section: String) -> void:
	var h: Control = app.info.settings_heading if section == "settings" else app.info.help_heading
	var scroll: ScrollContainer = app.info_scroll if section == "settings" else app.info.help_scroll
	var back: Control = app.actions["nav-work"] if section == "settings" else app.info.right_return
	var switch: Control = app.information.get_node("help-access" if section == "settings" else "settings-access")
	check(h.texture != null and not h.fallback.visible,"one image title "+section)
	check(h.get_global_rect().end.y < scroll.get_global_rect().position.y and scroll.get_global_rect().end.y < back.get_global_rect().position.y,"separate fixed and scrolling areas "+section)
	check(not back.get_global_rect().intersects(switch.get_global_rect()),"navigation targets separate")
	var fixed: Rect2 = h.get_global_rect()
	scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
	await settle()
	var last: Control = app.animation_toggle if section == "settings" else app.help_panel.chapters[app.help_panel.chapter].get_children()[-1]
	check(last.get_global_rect().end.y <= scroll.get_global_rect().end.y+1 and fixed == h.get_global_rect(),"content end reachable with fixed title")
	samples.append({"viewport":root.size,"ui":app.ui_scale,"section":section,"title":h.get_global_rect(),"ink":h.image_rect(),"scroll":scroll.get_global_rect(),"back":back.get_global_rect(),"switch":switch.get_global_rect()})
	scroll.scroll_vertical = 0
	await settle()
func run() -> void:
	folder = OS.get_environment("BTI_OUTPUT")
	root.gui_embed_subwindows = true
	root.notify_mouse_entered()
	load("res://model/save_store.gd").test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	current_scene = book
	app = book.app
	await settle(0.8)
	check(app.display_settings != null,"actual Windows display controls present")
	# One-time size matrix: retain actual controls but freeze monitor polling.
	# Display-mode behavior is outside BTI; no desktop mode switch is requested.
	app.display_controller.set_process(false)
	root.borderless = true
	root.unresizable = false
	root.position = Vector2i(-3500,-2000)
	for config: Vector3 in [Vector3(1280,720,1),Vector3(1280,720,1.25),Vector3(1920,1080,1),Vector3(1920,1080,1.25),Vector3(2560,1440,1),Vector3(2560,1440,1.25),Vector3(1920,1200,1.25)]:
		root.size = Vector2i(config.x,config.y)
		app.set_ui_scale(config.z)
		await settle()
		if root.size != Vector2i(config.x,config.y):
			DisplayServer.window_set_size(Vector2i(config.x,config.y))
			await settle(0.2)
		check(root.size == Vector2i(config.x,config.y),"actual native client size")
		var capture: bool = (config.x == 1280 and config.z == 1.25) or (config.y == 1080 and config.z == 1) or (config.x == 2560 and config.z == 1.25)
		var suffix: String = "-%dx%d-ui%d" % [config.x,config.y,roundi(config.z*100)]
		if capture: await shot("catalog"+suffix)
		click(button("Einstellungen / Info"))
		await settle()
		check(app.information.visible and app.information_origin == "album" and app.info.section == "settings","native catalog pointer opens settings")
		await layout("settings")
		if capture: await shot("settings"+suffix)
		click(app.information.get_node("help-access"))
		await settle()
		check(app.info.section == "help" and app.info.right_return.tooltip_text == "Zurück zum Katalog","bottom pointer pan to help retains origin")
		await layout("help")
		if capture: await shot("help"+suffix)
		click(app.help_panel.buttons[2])
		await settle()
		app.info.help_scroll.scroll_vertical = 80
		await settle()
		var offset: int = app.info.help_scroll.scroll_vertical
		click(app.information.get_node("settings-access"))
		await settle()
		click(app.information.get_node("help-access"))
		await settle()
		check(app.help_panel.chapter == 2 and app.info.help_scroll.scroll_vertical == offset,"chapter and scroll survive natural camera pans")
		app.info.right_return.grab_focus()
		check(app.info.right_return.has_focus() and app.info.right_return.accessibility_name == "Zurück zum Katalog","bottom focus and semantic destination")
		click(app.info.right_return)
		await settle()
		check(app.album.visible and not app.catalog_title.fallback.visible,"native bottom return to catalog")
	# Work-origin navigation uses the unchanged real leaf animations too.
	root.size = Vector2i(1920,1080)
	app.set_ui_scale(1.0)
	await settle()
	var original: Rect2 = app.catalog_title.get_global_rect()
	app.set_ui_scale(1.25)
	await settle()
	app.set_ui_scale(1.0)
	await settle()
	check(app.catalog_title.get_global_rect() == original,"UI100 to125 to100 exact geometry roundtrip")
	click(app.choices[0])
	await settle()
	check(app.work.visible,"real book opens synthetic puzzle")
	click(app.actions["help"])
	await settle()
	check(app.information_origin == "work" and app.info.right_return.accessibility_name == "Zurück zum Rätsel","work-origin help destination")
	click(app.information.get_node("settings-access"))
	await settle()
	click(app.actions["nav-work"])
	await settle()
	check(app.work.visible and app.title.visible and not app.catalog_title.visible,"bottom return restores ordinary worksheet title")
	var report = {"source_head":OS.get_environment("BTI_HEAD"),"checks":checks,"failures":failures,"samples":samples,"driver":RenderingServer.get_video_adapter_name(),"method":"Ordinary main.tscn, actual Windows display controls, OpenGL viewport; native engine mouse event injection, no OS mouse automation; synthetic saves; natural leaf/pan durations, no fixture interruption. For the programmatic viewport matrix only, monitor polling frozen after native initialization, window decoration/resize lock removed to avoid Windows work-area clipping of 1440 client pixels. No display-mode validation or desktop mode change. Separate shipped-executable startup retains ordinary window behavior."}
	FileAccess.open(folder.path_join("native.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("BTI_NATIVE ",checks," failures=",failures)
	quit(0 if failures.is_empty() else 4)
