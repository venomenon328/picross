extends SceneTree
## External runner against the delivered PCK. Tiny synthetic input; original UI/art.
const Main = preload("res://ui/main.gd")
const Definition = preload("res://model/definition.gd")
var app: Main
var output: String
var checks := 0
var failures: Array[String] = []
var geometry: Array = []

class TechnicalMain extends Main:
	func puzzle_definitions() -> Array[Dictionary]:
		# Retain one registered identity/reveal so export paths and slot validation
		# remain real. Only this temporary process replaces its logical input.
		var data: Dictionary = super.puzzle_definitions()[0].duplicate(true)
		data.test_only = true
		data.width = 5
		data.height = 3
		data.palette = [{"id":1,"color":"#343f42","symbol":"A"}]
		data.solution = [[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0]]
		data.rows = [[],[{"length":5,"color":1}],[]]
		data.columns = []
		for x: int in range(5): data.columns.append([{"length":1,"color":1}])
		return [data]

func _initialize() -> void: call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures.append(message); print("EA_PACK_FAIL ",message)

func frames() -> void:
	await process_frame
	await process_frame
	await process_frame

func click(item: Control) -> void:
	var point: Vector2 = item.get_global_rect().get_center()
	if item.get_window() != root: point += Vector2(item.get_window().position)
	for pressed: bool in [true,false]: pointer(point,pressed)

func pointer(point: Vector2, pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.position = point
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	root.push_input(event,true)

func run() -> void:
	output = OS.get_environment("EA_PACK_OUTPUT")
	if output.is_empty(): quit(4); return
	root.size = Vector2i(1280,720)
	root.gui_embed_subwindows = true
	root.notify_mouse_entered()
	app = TechnicalMain.new()
	root.add_child(app)
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await frames()
	check(app.album.visible and app.sessions.size() == 1,"actual exported main/UI loads synthetic registered input")
	app.select_puzzle(0)
	if OS.get_environment("EA_PACK_MODE") == "restart":
		check(app.session.completed and app.ending.visible and not app.reveal_view.active,"actual PCK new process restores stable end")
	else:
		for u: float in [1.0,1.25]:
			app.set_ui_scale(u)
			await frames()
			for x: int in range(5):
				var point: Vector2 = app.board.global_position+app.board.view.cell_rect(Vector2i(x,1)).get_center()
				pointer(point,true)
				pointer(point,false)
			check(app.session.completed and app.reveal_view.active,"actual PCK committed completion starts animation")
			var started := Time.get_ticks_msec()
			while app.reveal_view.active: await process_frame
			check(Time.get_ticks_msec()-started >= 1900 and Time.get_ticks_msec()-started < 2800,"actual Windows PCK animation wall time")
			check(not app.reveal_view.is_processing() and app.reveal_view.ink.commands.is_empty(),"actual PCK stops animation and releases transient commands")
			check(app.title.text == app.session.neutral_title() and app.title.get_theme_font("font") == app.WORK_TITLE_FONT,"actual PCK neutral Bakso title used")
			check(app.completion_reset.image.resource_path == "res://art/book/reset.svg" and app.completion_reset.size == Vector2.ONE*44*u,"actual PCK original reset resource and scaled target used")
			check(app.reveal_view.artwork != null and app.reveal_view.payload.image == app.session.definition.reveal.image,"actual PCK registered artwork used")
			geometry.append({"ui_scale":u,"area":str(app.reveal_view.area),"image":str(app.reveal_view.artwork_rect()),"reset":str(app.completion_reset.get_rect())})
			await RenderingServer.frame_post_draw
			check(root.get_texture().get_image().save_png(output.path_join("export-ui%d.png" % roundi(u*100))) == OK,"actual PCK framebuffer")
			click(app.completion_reset)
			await frames()
			check(app.reset_dialog.visible and app.reset_origin == "ending","actual PCK reset pointer opens confirmation")
			click(app.reset_dialog.get_cancel_button())
			await frames()
			check(app.session.completed and app.ending.visible,"actual PCK cancel retains ending")
			if u == 1.0:
				click(app.completion_reset)
				await frames()
				click(app.reset_dialog.get_ok_button())
				await frames()
				check(app.work.visible and not app.session.completed and app.session.player.history.is_empty(),"actual PCK confirmed reset opens blank same sheet")
	var report := {"test_only":true,"mode":OS.get_environment("EA_PACK_MODE"),"checks":checks,"failures":failures,"geometry":geometry,"client":str(root.size),"screen":str(DisplayServer.screen_get_size()),"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name()}
	var file := FileAccess.open(output.path_join("pack-"+OS.get_environment("EA_PACK_MODE")+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")+"\n")
	file.close()
	app.free()
	print("EA_PACK_OK ",checks)
	quit(0 if failures.is_empty() else 4)
