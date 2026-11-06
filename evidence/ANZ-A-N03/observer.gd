extends Node
var elapsed: float = 0.0
var folder: String
var trace: FileAccess
var last_capture: String = ""
func _ready() -> void:
 folder = OS.get_environment("ANZ_OBSERVATION")
 trace = FileAccess.open(folder.path_join("engine.jsonl"),FileAccess.WRITE)
 var previous: String = folder.path_join("capture.txt")
 if FileAccess.file_exists(previous): last_capture = FileAccess.get_file_as_string(previous).strip_edges()
func box(item: Control) -> Array:
 var rect: Rect2 = item.get_global_rect()
 return [rect.position.x,rect.position.y,rect.size.x,rect.size.y]
func vec(value: Vector2i) -> Array: return [value.x,value.y]
func _process(delta: float) -> void:
 elapsed += delta
 if elapsed < 0.1: return
 elapsed = 0.0
 var scene = get_tree().current_scene
 if scene == null or scene.get("app") == null: return
 var app = scene.app
 var control = app.display_controller
 if control == null: return
 var panel = app.display_settings
 var popup: PopupMenu = panel.mode_choice.get_popup()
 var rows: Array = []
 for i: int in range(popup.item_count): rows.append([popup.get_item_text(i),popup.get_item_id(i)])
 var data: Dictionary = {"pid":OS.get_process_id(),"focused":DisplayServer.window_is_focused(),"time":Time.get_ticks_msec(),"mode":DisplayServer.window_get_mode(),"client":vec(control.backend.observed().client),"server_client":vec(DisplayServer.window_get_size()),"window_client":vec(get_tree().root.size),"outer":vec(DisplayServer.window_get_size_with_decorations()),"position":vec(DisplayServer.window_get_position()),"screen":DisplayServer.window_get_current_screen(),"desktop":vec(DisplayServer.screen_get_size(DisplayServer.window_get_current_screen())),"dpi":DisplayServer.screen_get_dpi(),"screen_scale":DisplayServer.screen_get_scale(),"resize_disabled":get_tree().root.unresizable,"borderless":get_tree().root.borderless,"applying":control.applying,"preview":control.preview,"active":control.active,"saved":control.saved,"message":control.message,"seconds":control.seconds_left(),"info":app.information.visible,"section":app.information_section,"book_state":scene.state,"ui_scale":app.ui_scale,"mode_control":box(panel.mode_choice),"size_control":box(panel.size_choice),"size_disabled":panel.size_choice.disabled,"accept":box(panel.accept),"cancel":box(panel.reject),"card":box(panel.card),"card_visible":panel.shield.visible,"settings_visible":panel.is_visible_in_tree(),"scroll":box(app.info_scroll),"size_popup":{"visible":panel.size_choice.get_popup().visible,"position":vec(panel.size_choice.get_popup().position),"size":vec(panel.size_choice.get_popup().size),"disabled":[panel.size_choice.is_item_disabled(0),panel.size_choice.is_item_disabled(7)]},"mode_popup":{"visible":popup.visible,"position":vec(popup.position),"size":vec(popup.size),"items":rows},"scale":box(app.ui_scale_choice),"menu":box(app.actions["menu"]),"help":box(app.actions["help"]),"settings_access":box(app.information.get_node("settings-access")),"info_switch":box(app.information.get_node("help-access")),"info_return":box(app.actions["nav-work"]),"catalog_info":[],"catalog_cards":[],"resolution":panel.size_choice.text,"feedback":panel.feedback.text,"feedback_visible":panel.feedback.visible,"feedback_box":box(panel.feedback),"save_current":box(panel.save_current),"save_visible":panel.save_current.visible,"scroll_value":app.info_scroll.scroll_vertical,"scroll_max":app.info_scroll.get_v_scroll_bar().max_value,"scroll_page":app.info_scroll.get_v_scroll_bar().page,"view_control":box(app.view_choice),"mark":box(app.clue_completion_toggle),"animation":box(app.animation_toggle),"section_boxes":[],"quit_control":[],"adapter":RenderingServer.get_video_adapter_name(),"os":OS.get_version()}
 data["scale_popup"] = {"visible":app.ui_scale_choice.get_popup().visible,"position":vec(app.ui_scale_choice.get_popup().position),"size":vec(app.ui_scale_choice.get_popup().size)}
 data["view_popup"] = {"visible":app.view_choice.get_popup().visible,"position":vec(app.view_choice.get_popup().position),"size":vec(app.view_choice.get_popup().size)}
 data["fields"] = []
 for field: Control in app.settings_fields:
  var help = field.help
  data.fields.append({"name":field.caption.text,"row":box(field),"label":box(field.caption),"choice":box(field.choice),"child_count":field.get_child_count(),"help":box(help) if help != null else [],"help_focused":help.has_focus() if help != null else false,"tooltip_text":help.tooltip_text if help != null else "","focus_tip":box(help.focus_tip) if help != null and is_instance_valid(help.focus_tip) else []})
 data["information_origin"] = app.information_origin
 data["player"] = {"cells":app.session.player.cells,"history":app.session.player.history,"cursor":app.session.player.cursor,"view":app.board.capture_view()} if app.session != null else {}
 data["heading"] = font_info(app.settings_title)
 data["catalog_heading"] = font_info(app.title)
 data["album_visible"] = app.album.visible
 data["work_visible"] = app.work.visible
 data["left_back"] = button_info(app.actions["nav-work"])
 data["right_back"] = button_info(app.info.right_return)
 data["help_return"] = box(app.info.right_return)
 data["board_cell"] = box_cell(app)
 data["settings_box"] = box(app.settings_panel)
 data["focused_control"] = str(app.get_viewport().gui_get_focus_owner().name) if app.get_viewport().gui_get_focus_owner() != null else ""
 data["native_tips"] = []
 for node: Node in get_tree().get_nodes_in_group("book-buttons"):
  if node.tooltip_ref != null and is_instance_valid(node.tooltip_ref.get_ref()): data.native_tips.append({"text":node.tooltip_text,"box":box(node.tooltip_ref.get_ref()),"window_position":vec(node.tooltip_ref.get_ref().get_window().position)})
 for group: Node in app.settings_panel.get_children():
  if group is PanelContainer: data.section_boxes.append({"name":group.name,"box":box(group),"heading":group.heading.text,"font":font_info(group.heading)})
 for child: Node in app.album.find_children("*","Button",true,false):
  if child.text == "Einstellungen / Info": data.catalog_info.append(box(child))
 for child: Node in app.choices:
  if child.is_visible_in_tree(): data.catalog_cards.append(box(child))
 var usable: Rect2i = DisplayServer.screen_get_usable_rect(DisplayServer.window_get_current_screen())
 data.usable = [usable.position.x,usable.position.y,usable.size.x,usable.size.y]
 var text: String = JSON.stringify(data)
 var state := FileAccess.open(folder.path_join("state.json"),FileAccess.WRITE)
 state.store_string(text)
 state.close()
 trace.store_line(text)
 trace.flush()
 var request: String = folder.path_join("capture.txt")
 if FileAccess.file_exists(request):
  var label: String = FileAccess.get_file_as_string(request).strip_edges()
  if label != last_capture and label.is_valid_filename():
   last_capture = label
   call_deferred("capture_image",label)

func capture_image(label: String) -> void:
 await RenderingServer.frame_post_draw
 get_tree().root.get_texture().get_image().save_png(folder.path_join(label+".png"))

func font_info(label: Label) -> Dictionary:
 var font: Font = label.get_theme_font("font")
 return {"text":label.text,"font":font.get_font_name(),"resource":font.resource_path,"instance":font.get_instance_id(),"base":font.base_font.resource_path if font is FontVariation else "","weight":font.variation_opentype if font is FontVariation else {},"size":label.get_theme_font_size("font_size"),"box":box(label),"visible":label.is_visible_in_tree()}

func button_info(button: Button) -> Dictionary:
 return {"text":button.text,"tooltip":button.tooltip_text,"accessibility":button.accessibility_name,"box":box(button),"visible":button.is_visible_in_tree()}

func box_cell(app: Control) -> Array:
 if app.session == null: return []
 var rect: Rect2 = app.board.view.cell_rect(Vector2i(2,0))
 rect.position += app.board.global_position
 return [rect.position.x,rect.position.y,rect.size.x,rect.size.y]
