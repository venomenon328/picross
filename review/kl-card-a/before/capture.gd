extends SceneTree
const Store = preload("res://model/save_store.gd")
var surface: SubViewport
var book: Node
var app: Control
var output: String
var measurements: Array = []
func _initialize() -> void: call_deferred("run")
func frames(n: int = 12) -> void:
	for i: int in range(n): await process_frame
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
		halves.append({"clip":clip,"grid":grid.get_global_rect(),"card":card.size,"image":card.image_area,"minimum":card.minimum_card_width(app.ui_scale),"columns":grid.columns,"fully_visible_cards":full,"fully_visible_rows":y_rows.size(),"row_positions":y_rows,"gap":grid.get_theme_constant("v_separation"),"scroll_range":grid.get_parent().get_v_scroll_bar().max_value-grid.get_parent().get_v_scroll_bar().page})
	var file: String = label+".png"
	surface.get_texture().get_image().save_png(output.path_join(file))
	measurements.append({"file":file,"scene":"res://main.tscn / res://book/main.gd (unmodified)","viewport":[surface.size.x,surface.size.y],"ui_scale":app.ui_scale,"page":app.album.page_index,"category":app.album.category_id,"sort":app.album.preference.criterion,"direction":app.album.preference.direction,"scroll":[app.album.positions().x,app.album.positions().y],"halves":halves})
	print(label," ",halves)
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
	var report := {"tag":OS.get_environment("CARD_TAG"),"renderer":RenderingServer.get_video_adapter_name(),"display_server":DisplayServer.get_name(),"measurements":measurements}
	var f := FileAccess.open(output.path_join("measurements.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"\t")+"\n")
	f.close()
	quit()
