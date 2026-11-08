extends SceneTree
const Store = preload("res://model/save_store.gd")
var surface: SubViewport
var book: Node
var app: Control
var output: String
var measurements: Array = []
var checks: Array = []
func _initialize() -> void: call_deferred("run")
func frames(n: int = 12) -> void:
	for i: int in range(n): await process_frame
func check(value: bool, label: String) -> void:
	checks.append({"assertion":label,"passed":value})
	if not value: push_error("CARD_VISUAL_FAIL "+label)
func click(control: Control) -> void:
	var point: Vector2 = control.get_global_rect().get_center()
	if control.get_window() != root: point += Vector2(control.get_window().position)
	var motion := InputEventMouseMotion.new()
	motion.position = point
	surface.push_input(motion,true)
	for down: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		surface.push_input(event,true)
func slot_hashes(excluded: String = "") -> Dictionary:
	var hashes: Dictionary = {}
	for file: String in DirAccess.get_files_at(Store.test_root_override):
		if not file.begins_with(excluded+"."):
			hashes[file] = FileAccess.get_sha256(Store.test_root_override.path_join(file))
	return hashes
func write_file(name: String, value: String) -> void:
	var f := FileAccess.open(Store.test_root_override.path_join(name),FileAccess.WRITE)
	f.store_string(value)
	f.close()
func capture(label: String) -> void:
	await frames()
	await RenderingServer.frame_post_draw
	var halves: Array = []
	for grid: Control in [app.album.grid,app.album.right_grid]:
		var clip: Rect2 = grid.get_parent().get_global_rect()
		var full: int = 0
		var y_rows: Array = []
		for column: Control in grid.get_children():
			var box: Rect2 = column.get_child(0).get_global_rect()
			if clip.encloses(box):
				full += 1
				if not box.position.y in y_rows: y_rows.append(box.position.y)
		var card: Control = grid.get_child(0).get_child(0)
		halves.append({"clip":clip,"grid":grid.get_global_rect(),"card":card.size,"image":card.image_area,"minimum":card.minimum_card_width(app.ui_scale),"columns":grid.columns,"fully_visible_cards":full,"fully_visible_rows":y_rows.size(),"row_positions":y_rows,"gap":grid.get_theme_constant("v_separation"),"scroll_range":grid.get_parent().get_v_scroll_bar().max_value-grid.get_parent().get_v_scroll_bar().page,"side_by_side":card.side_by_side,"side_minimum":card.side_width_budget,"text_minimum":card.text_width_budget})
	var file: String = label+".png"
	surface.get_texture().get_image().save_png(output.path_join(file))
	measurements.append({"file":file,"scene":"res://main.tscn / res://book/main.gd (unmodified)","viewport":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,"page":app.album.page_index,"category":app.album.category_id,"sort":app.album.preference.criterion,"direction":app.album.preference.direction,"scroll":[app.album.positions().x,app.album.positions().y],"halves":halves})
	print(label," ",halves)
func details() -> void:
	surface.size = Vector2i(2560,1440)
	app.set_ui_scale(1.25)
	var category: Dictionary
	for value: Dictionary in app.album.categories:
		if value.id == "gebaeude-bauwerke": category = value
	var old_name: String = category.name
	category.name = "Eine lange technische Kategorie mit Äpfeln und Kräutern"
	app.album._render(0)
	await frames()
	var card: Control = app.choices[0]
	var image := Image.create(480,48,false,Image.FORMAT_RGBA8)
	image.fill(Color("376a60"))
	image.fill_rect(Rect2i(0,0,24,48),Color("dca751"))
	image.fill_rect(Rect2i(456,0,24,48),Color("b4584a"))
	card.picture.artwork = ImageTexture.create_from_image(image)
	card.picture.filtered_artwork = null
	card.picture.queue_redraw()
	await frames()
	check(card.reset.visible and card.detail.get_line_count() == 2 and card.difficulty.text == "Nicht eingestuft","UI125 actual long category, missing rating and reset")
	check(is_equal_approx(card.picture.artwork_rect().size.aspect(),10),"full 10:1 earned reveal with distinct end markers")
	await capture("long-wide-2560-ui125")
	click(card.reset)
	await frames()
	check(app.reset_dialog.visible and app.reset_id == card.action_id,"long UI125 reset pointer opens correct confirmation")
	click(app.reset_dialog.get_cancel_button())
	await frames()
	check(not app.reset_dialog.visible and app.album.visible,"long UI125 reset cancellation keeps card and catalog")
	surface.size = Vector2i(1280,720)
	app.album._render(0)
	await frames()
	check(not app.choices[0].side_by_side and app.choices[0].detail.get_line_count() <= 2,"narrow UI125 common stacked fallback with full long category")
	check(app.choices[0].size.x <= app.album._shared_card_width(),"narrow full card width clears native scrollbar reserve")
	await capture("narrow-long-1280-ui125")
	card = app.choices[0]
	app.album.ensure_control_visible(card.mode_tip)
	app.album.scroll.scroll_vertical += 2 # expose whole AA envelope after integer scroll rounding
	await frames()
	check(app.album.scroll.get_global_rect().encloses(card.mode_tip.get_global_rect()) and app.album.scroll.get_global_rect().encloses(card.difficulty.get_global_rect()),"narrow fallback full metadata reached by native scroll")
	await capture("narrow-metadata-1280-ui125")
	app.album.scroll.scroll_vertical = 0
	category.name = old_name
	app.album._render(0)
	var samples: Array = []
	for extent: Vector2i in [Vector2i(1920,1080),Vector2i(2560,1440)]:
		surface.size = extent
		await frames()
		samples.append({"width":extent.x,"available":app.album._shared_card_width()})
	var crossing: float = samples[0].width+(2*app.choices[0].side_width_budget+15-samples[0].available)/((samples[1].available-samples[0].available)/640)
	for width: int in [floori(crossing)-8,ceili(crossing)+8]:
		surface.size = Vector2i(width,roundi(width*9.0/16.0))
		await capture("fit-%d-ui125" % width)
	surface.size = Vector2i(1920,1080)
	app.set_ui_scale(1.0)
	await frames()
	app.album.selected_id = app.album.visible_ids[13]
	app.album.scroll.scroll_vertical = 70
	app.album.right_scroll.scroll_vertical = 140
	await frames()
	var pair: Vector2i = app.album.positions()
	var selected: String = app.album.selected_id
	var saved: Dictionary = slot_hashes()
	for u: float in [1.25,1.0]:
		app.set_ui_scale(u)
		await frames()
		check(app.album.positions() == pair and app.album.selected_id == selected and slot_hashes() == saved,"UI scale roundtrip preserves both scrolls, ID and save bytes")
	# Real invalid/backup-only/damaged-backup slots; reload into a fresh regular
	# book root. Every mutation stays in this synthetic test profile.
	book.free()
	await frames()
	var value: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Store.test_root_override.path_join("kat2_002.json")))
	value.cells.fill(-1)
	value.cells[0] = 1
	value.history = [[{"index":0,"before":-1,"after":1}]]
	value.cursor = 1
	value.completed = false
	value.undo_used = false
	DirAccess.remove_absolute(Store.test_root_override.path_join("kat2_002.json"))
	write_file("kat2_002.bak",JSON.stringify(value))
	write_file("kat2_000.json","TEST ONLY invalid primary")
	write_file("kat2_004.bak","TEST ONLY invalid backup")
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames()
	app.set_ui_scale(1.25)
	await frames()
	check(app.slot_status[0] == "error" and app.slot_status[2] == "recovered" and app.slot_status[4] == "backup_invalid","actual loader distinguishes invalid, backup-only and damaged backup")
	card = app.choices[0]
	check(card.disabled and card.note.text == "Ungültig" and not card.unknown.visible and card.picture.payload.is_empty(),"invalid save cannot become new or reveal")
	app.album.ensure_control_visible(card.reset)
	await frames()
	await capture("invalid-1920-ui125")
	saved = slot_hashes("kat2_000")
	click(card.reset)
	await frames()
	check(app.reset_dialog.visible and app.reset_id == "pz-test-kat2-000","invalid reset pointer opens bound confirmation")
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.slot_status[0] == "fresh" and slot_hashes("kat2_000") == saved,"confirmed invalid reset owns only its slot")
	for index: int in [2,4]:
		var stem: String = "kat2_%03d" % index
		card = app.choices[index]
		app.album.ensure_control_visible(card.recovery)
		card.recovery.ensure_control_visible(card.repair)
		await frames()
		check(card.recovery.get_global_rect().grow(0.01).encloses(card.repair.get_global_rect()),"entire recovery pointer target in inner clip")
		await capture("recovery-%d-1920-ui125" % index)
		saved = slot_hashes(stem)
		click(card.repair)
		await frames()
		check(app.repair_dialog.visible and app.repair_id == "pz-test-kat2-%03d" % index,"recovery pointer opens separate bound confirmation")
		click(app.repair_dialog.get_ok_button())
		await frames()
		check(app.slot_status[index] == "loaded" and slot_hashes(stem) == saved,"confirmed recovery repairs target and preserves every foreign slot")
func run() -> void:
	output = OS.get_environment("CARD_OUTPUT")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	surface = SubViewport.new()
	surface.size = Vector2i(1920,1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	surface.gui_embed_subwindows = true
	root.add_child(surface)
	surface.notify_mouse_entered()
	book = load("res://main.tscn").instantiate()
	surface.add_child(book)
	app = book.app
	await frames()
	app.album.choose_category("gebaeude-bauwerke")
	app.album.choose_sort("size")
	await frames()
	for extent: Vector2i in [Vector2i(1920,1080),Vector2i(2560,1440)]:
		surface.size = extent
		app.set_ui_scale(1.0)
		await frames()
		app.album.scroll.scroll_vertical = 0
		app.album.right_scroll.scroll_vertical = 0
		await capture("catalog-%d-ui100" % extent.x)
	await details()
	var report := {"tag":OS.get_environment("CARD_TAG"),"product_head":OS.get_environment("CARD_PRODUCT_HEAD"),"renderer":RenderingServer.get_video_adapter_name(),"display_server":DisplayServer.get_name(),"measurements":measurements,"checks":checks}
	var f := FileAccess.open(output.path_join("measurements.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"\t")+"\n")
	f.close()
	quit(4 if checks.any(func(value: Dictionary) -> bool: return not value.passed) else 0)
