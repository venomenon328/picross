extends "res://tests/kat2_probe.gd"
var captures: Array = []
func capture(label: String, scenario: String) -> void:
 await frames()
 await RenderingServer.frame_post_draw
 var image: Image = surface.get_texture().get_image()
 image.save_png(output.path_join(label+".png"))
 var regions: Array = []
 for bar: ScrollBar in preload("res://tests/scrollbar_cases.gd").bars(app):
  if bar.is_visible_in_tree(): regions.append({"path":str(bar.get_path()),"value":bar.value,"maximum":bar.max_value,"page":bar.page})
 captures.append({"file":label+".png","scenario":scenario,"width":surface.size.x,"height":surface.size.y,"ui_scale":app.ui_scale,"catalog_positions":str(app.album.positions()),"information_positions":str(app.info.positions()),"visible_scrollbars":regions})
 print("CAPTURE ",label)
func run() -> void:
 output = OS.get_environment("KAT2_OUTPUT")
 mode = "pages"
 Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
 surface = SubViewport.new()
 surface.gui_embed_subwindows = true
 surface.size = Vector2i(1920,1080)
 surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
 root.add_child(surface)
 surface.notify_mouse_entered()
 await new_app()
 for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1200,1.25]]:
  surface.size = Vector2i(spec[0],spec[1])
  app.set_ui_scale(spec[2])
  await frames()
  app.album.scroll.scroll_vertical = 0
  app.album.right_scroll.scroll_vertical = int((app.album.right_scroll.get_v_scroll_bar().max_value-app.album.right_scroll.get_v_scroll_bar().page)*0.5)
  await capture("catalog-%d-ui%d" % [spec[0],roundi(spec[2]*100)],"Synthetic native catalog pair: left at start, right at middle; actual projected book")
  if spec[0] == 1920 and spec[1] == 1080:
   # Original 1:1 viewport region, no resize or re-encoding after publication.
   await RenderingServer.frame_post_draw
   var bar: VScrollBar = app.album.scroll.get_v_scroll_bar()
   surface.get_texture().get_image().get_region(Rect2i(bar.get_global_rect().grow(2))).save_png(output.path_join("scrollbar-1to1.png"))
   captures.append({"file":"scrollbar-1to1.png","scenario":"Native viewport region at actual UI100 scale; same catalog scene","ui_scale":1.0})
   app.show_information("help")
   await frames()
   app.info.help_scroll.scroll_vertical = int(app.info.help_scroll.get_v_scroll_bar().max_value)
   await capture("help-1920-ui100-end","Help at native lower bound, fixed navigation")
   app.return_to_work()
   await frames()
  if spec[0] == 1280:
   app.show_information("settings")
   await frames()
   app.info_scroll.scroll_vertical = int(app.info_scroll.get_v_scroll_bar().max_value)
   await capture("settings-1280-ui125-end","Settings at native lower bound, fixed navigation")
   app.return_to_work()
   await frames()
   var choice: OptionButton = app.album.category_choice
   var count: int = choice.item_count
   for index: int in range(60): choice.add_item("TEST ONLY Scrolloption %d" % index)
   click(choice)
   surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
   await frames()
   choice.get_popup().scroll_to_item(30)
   await frames()
   for bar: ScrollBar in preload("res://tests/scrollbar_cases.gd").bars(choice.get_popup()):
    if bar.is_visible_in_tree(): bar.value = (bar.max_value-bar.page)*0.5
   await capture("popup-1280-ui125-middle","Real long embedded category PopupMenu with synthetic extra options; middle")
   choice.get_popup().hide()
   while choice.item_count > count: choice.remove_item(choice.item_count-1)
   await frames()
   app.album.open_filters()
   await frames()
   var panel = app.album.filter_panel
   panel.error.text = "TEST ONLY langer Entwurfsfehler. ".repeat(100)
   panel.error.show()
   panel._fit_content()
   await frames()
   panel.scroller.scroll_vertical = int(panel.scroller.get_v_scroll_bar().max_value)
   await capture("filter-1280-ui125-end","Real narrow filter panel with overflowing synthetic draft error; end, fixed actions")
   panel.hide()
   await frames()
 var f := FileAccess.open(output.path_join("scenarios.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify(captures,"  ")+"\n")
 f.close()
 print("SBR_CAPTURE_OK")
 quit(0)
