extends Node
## External read-only observer, excluded from product PCK.
var folder: String
var elapsed: float = 0
var trace: FileAccess
var last_capture: String = ""
func _ready() -> void:
	folder = OS.get_environment("BTI_OBSERVATION")
	trace = FileAccess.open(folder.path_join("engine.jsonl"),FileAccess.WRITE)
func box(item: Control) -> Array:
	var rect: Rect2 = item.get_global_rect()
	return [rect.position.x,rect.position.y,rect.size.x,rect.size.y]
func local_box(rect: Rect2) -> Array: return [rect.position.x,rect.position.y,rect.size.x,rect.size.y]
func button(item: Button) -> Dictionary:
	return {"box":box(item),"text":item.text,"tooltip":item.tooltip_text,"accessibility":item.accessibility_name,"visible":item.is_visible_in_tree(),"focus":item.has_focus()}
func _process(delta: float) -> void:
	elapsed += delta
	if elapsed < 0.08: return
	elapsed = 0
	var book = get_tree().current_scene
	if book == null or book.get("app") == null: return
	var app = book.app
	var heading = app.info.settings_heading if app.info.section == "settings" else app.info.help_heading
	var scroll = app.info_scroll if app.info.section == "settings" else app.info.help_scroll
	var popup: PopupMenu = app.ui_scale_choice.get_popup()
	var display = app.display_settings
	var state: Dictionary = {"pid":OS.get_process_id(),"ms":Time.get_ticks_msec(),"book_state":book.state,"motion":book.motion_kind,"capture":book.capture != null,"snapshots":book.information_routes.textures.size(),"barrier":book.release_barrier,"client":[get_tree().root.size.x,get_tree().root.size.y],"screen":[DisplayServer.screen_get_size().x,DisplayServer.screen_get_size().y],"dpi":DisplayServer.screen_get_dpi(),"renderer":RenderingServer.get_video_adapter_name(),"source":book.get_script().resource_path,"ui":app.ui_scale,"album":app.album.visible,"work":app.work.visible,"info":app.information.visible,"section":app.info.section,"origin":app.information_origin,"chapter":app.help_panel.chapter,"scroll":box(scroll),"scroll_value":scroll.scroll_vertical,"scroll_max":scroll.get_v_scroll_bar().max_value,"scroll_page":scroll.get_v_scroll_bar().page,"positions":[app.info_scroll.scroll_vertical,app.info.help_scroll.scroll_vertical],"scale":box(app.ui_scale_choice),"scale_popup":{"visible":popup.visible,"position":[popup.position.x,popup.position.y],"size":[popup.size.x,popup.size.y]},"back":button(app.actions["nav-work"] if app.info.section == "settings" else app.info.right_return),"switch":button(app.information.get_node("help-access" if app.info.section == "settings" else "settings-access")),"help":box(app.actions["help"]),"menu":box(app.actions["menu"]),"catalog_return":box(app.album_button),"catalog_info":[],"catalog_help":[],"cards":[],"chapters":[],"titles":[],"status":app.status_label.text,"status_visible":app.status_label.is_visible_in_tree(),"retry":box(app.work_repair_button),"retry_visible":app.work_repair_button.is_visible_in_tree(),"focus":str(app.get_viewport().gui_get_focus_owner().name) if app.get_viewport().gui_get_focus_owner() != null else "","tooltips":[],"catalog_scroll":[app.album.scroll.scroll_vertical,app.album.right_scroll.scroll_vertical]}
	for title: Control in [app.catalog_title,app.info.settings_heading,app.info.help_heading]:
		state.titles.append({"role":title.role,"box":box(title),"image":local_box(title.image_rect()),"ink":local_box(title.ink_rect()),"visible":title.is_visible_in_tree(),"fallback":title.fallback.visible,"semantic":title.accessibility_name})
	for child: Control in app.help_panel.navigation.get_children(): state.chapters.append(box(child))
	state.display_preview = app.display_controller.preview
	state.display_applying = app.display_controller.applying
	state.display_accept = box(display.accept)
	state.display_mode = box(display.mode_choice)
	state.display_size = box(display.size_choice)
	state.view_choice = box(app.view_choice)
	state.view_mode = app.board.mode
	state.options = {}
	for key: String in ["mode","size","view"]:
		var choice: OptionButton = display.mode_choice if key == "mode" else display.size_choice if key == "size" else app.view_choice
		var menu: PopupMenu = choice.get_popup()
		var items: Array = []
		for i: int in range(choice.item_count): items.append({"text":choice.get_item_text(i),"disabled":choice.is_item_disabled(i)})
		state.options[key] = {"visible":menu.visible,"position":[menu.position.x,menu.position.y],"size":[menu.size.x,menu.size.y],"items":items}
	for child: Node in app.album.find_children("*","Button",true,false):
		if child.text == "Einstellungen / Info": state.catalog_info.append(box(child))
		if child.text == "Hilfe": state.catalog_help.append(box(child))
	for card: Control in app.choices:
		if card.is_visible_in_tree(): state.cards.append(box(card))
	for node: Node in get_tree().get_nodes_in_group("book-buttons"):
		if node.tooltip_ref != null and is_instance_valid(node.tooltip_ref.get_ref()): state.tooltips.append({"text":node.tooltip_text,"box":box(node.tooltip_ref.get_ref())})
	if app.session != null:
		var cell: Rect2 = app.board.view.cell_rect(Vector2i(2,0))
		cell.position += app.board.global_position
		state.cell = local_box(cell)
		state.player = {"cells":app.session.player.cells,"history":app.session.player.history,"cursor":app.session.player.cursor,"view":app.board.capture_view()}
		state.slot = ProjectSettings.globalize_path(app.store.path_for(app.store.key_for_definition(app.session.definition.id)))
	var file := FileAccess.open(folder.path_join("state.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(state)); file.close()
	trace.store_line(JSON.stringify(state));trace.flush()
	var request: String = folder.path_join("capture.txt")
	if FileAccess.file_exists(request):
		var label: String = FileAccess.get_file_as_string(request).strip_edges()
		if label != last_capture and label.is_valid_filename():
			last_capture = label
			call_deferred("capture_image",label)
func capture_image(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_tree().root.get_texture().get_image().save_png(folder.path_join(label+".png"))
