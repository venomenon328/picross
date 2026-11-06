extends Node
func _ready() -> void:
 load("res://model/save_store.gd").test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
 call_deferred("capture")
func capture() -> void:
 await get_tree().create_timer(0.8).timeout
 var book = get_tree().current_scene
 var app = book.app
 get_tree().root.size = Vector2i(1920,1080)
 app.set_ui_scale(1.0)
 await get_tree().create_timer(0.2).timeout
 app.album.scroll.scroll_vertical = int(app.album.scroll.get_v_scroll_bar().max_value)
 await get_tree().create_timer(0.2).timeout
 await RenderingServer.frame_post_draw
 get_tree().root.get_texture().get_image().save_png(OS.get_environment("PANG_OUTPUT").path_join("catalog-status-bottom-1920-ui100.png"))
 print("PANG_STATUS_ORIGINAL_OK")
 get_tree().quit()
