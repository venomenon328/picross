extends Node
## External K-A read-only observer; no product or save mutation.
var folder: String
var elapsed: float = 0
var last_capture: String = ""
func _ready() -> void: folder = OS.get_environment("KA_OBSERVATION")
func box(item: Control) -> Array:
 var r: Rect2 = item.get_global_rect()
 return [r.position.x,r.position.y,r.size.x,r.size.y]
func window_box(item: Control) -> Array:
 var r: Array = box(item)
 if item.get_window()!=get_tree().root:r[0]+=item.get_window().position.x;r[1]+=item.get_window().position.y
 return r
func menu(choice: OptionButton) -> Dictionary:
 var popup: PopupMenu = choice.get_popup()
 var offset: Vector2 = Vector2(choice.get_window().position) if choice.get_window() != get_tree().root else Vector2.ZERO
 var r: Array = box(choice);r[0]+=offset.x;r[1]+=offset.y
 var entries: Array=[]
 for i: int in range(choice.item_count):entries.append({"text":choice.get_item_text(i),"disabled":choice.is_item_disabled(i)})
 return {"box":r,"visible":popup.visible,"position":[popup.position.x,popup.position.y],"size":[popup.size.x,popup.size.y],"items":entries,"selected":choice.selected}
func _process(delta: float) -> void:
 elapsed += delta
 if elapsed < 0.08:return
 elapsed=0
 var book = get_tree().current_scene
 if book == null or book.get("app") == null:return
 var app = book.app
 var a=app.album
 var panel=a.filter_panel
 var state: Dictionary={"pid":OS.get_process_id(),"ms":Time.get_ticks_msec(),"book_state":book.state,"capture":book.capture!=null,"barrier":book.release_barrier,"client":[get_tree().root.size.x,get_tree().root.size.y],"screen":[DisplayServer.screen_get_size().x,DisplayServer.screen_get_size().y],"dpi":DisplayServer.screen_get_dpi(),"renderer":RenderingServer.get_video_adapter_name(),"ui":app.ui_scale,"album":a.visible,"work":app.work.visible,"info":app.information.visible,"section":app.info.section,"origin":app.information_origin,"filters":a.filters,"ids":a.visible_ids,"filtered_ids":a.filtered_ids,"selected_id":a.selected_id,"page":a.page_index,"positions":[a.scroll.scroll_vertical,a.right_scroll.scroll_vertical],"scrollers":[box(a.scroll),box(a.right_scroll)],"filter_button":box(a.filter_button),"panel":{"visible":panel.visible,"position":[panel.position.x,panel.position.y],"size":[panel.size.x,panel.size.y],"error":panel.error.text,"error_visible":panel.error.is_visible_in_tree(),"scroll":panel.scroller.scroll_vertical},"category":menu(a.category_choice),"sort":menu(a.sort_choice),"status_filter":menu(panel.status),"mode_filter":menu(panel.mode_choice),"lower_filter":menu(panel.lower),"upper_filter":menu(panel.upper),"summary":a.summary.text,"empty":a.empty_message.text,"empty_visible":a.empty_message.is_visible_in_tree(),"feedback":a.feedback.text,"feedback_visible":a.feedback.is_visible_in_tree(),"buttons":{},"cards":[],"scale":menu(app.ui_scale_choice),"back":box(app.actions["nav-work"] if app.info.section=="settings" else app.info.right_return),"display_mode":menu(app.display_settings.mode_choice),"display_size":menu(app.display_settings.size_choice),"display_preview":app.display_controller.preview,"display_accept":box(app.display_settings.accept),"catalog_return":box(app.album_button),"focus":str(app.get_viewport().gui_get_focus_owner().name) if app.get_viewport().gui_get_focus_owner()!=null else "","reset_dialog":app.reset_dialog.visible,"reset_ok":window_box(app.reset_dialog.get_ok_button()),"reset_cancel":window_box(app.reset_dialog.get_cancel_button()),"repair_dialog":app.repair_dialog.visible,"repair_cancel":window_box(app.repair_dialog.get_cancel_button())}
 state.notice_area=box(a.notice_area);state.feedback_box=box(a.feedback);state.empty_box=box(a.empty_message)
 state.width_input=window_box(panel.width_input);state.height_input=window_box(panel.height_input);state.width_text=panel.width_input.text;state.height_text=panel.height_input.text
 for child: Node in a.find_children("*","Button",true,false):
  if child.is_visible_in_tree():
   var r: Array=box(child)
   if child.get_window()!=get_tree().root:r[0]+=child.get_window().position.x;r[1]+=child.get_window().position.y
   state.buttons[child.text if not child.text.is_empty() else str(child.name)]=r
 for card in a.choices:
  state.cards.append({"id":card.action_id,"box":box(card),"reset":box(card.reset),"reset_visible":card.reset.visible,"status":card.note.text,"diagnosis":card.diagnosis.text if card.get("diagnosis")!=null else "","repair":box(card.repair) if card.repair!=null else []})
 if app.session!=null:state.session=str(app.session.definition.id)
 var f:=FileAccess.open(folder.path_join("state.json"),FileAccess.WRITE);f.store_string(JSON.stringify(state));f.close()
 var request: String=folder.path_join("capture.txt")
 if FileAccess.file_exists(request):
  var label: String=FileAccess.get_file_as_string(request).strip_edges()
  if label!=last_capture and label.is_valid_filename():last_capture=label;call_deferred("capture_image",label)
func capture_image(label: String) -> void:
 await RenderingServer.frame_post_draw
 get_tree().root.get_texture().get_image().save_png(folder.path_join(label+".png"))
