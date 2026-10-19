extends Node
## TEST ONLY packed input driver of two actual Windows EXEs and PCKs.
const Main = preload("res://ui/main.gd")
const Store = preload("res://model/save_store.gd")
var app: Main
var checks := 0
var failures: Array[String] = []
var output: String
var root: Window

func _ready() -> void:
	root=get_tree().root
	call_deferred("run")

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message); print("AT_PACK_FAIL ",message)

func frames() -> void:
	for i: int in range(4): await get_tree().process_frame

func click(point: Vector2) -> void:
	for pressed: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position=point;event.button_index=MOUSE_BUTTON_LEFT;event.pressed=pressed
		root.push_input(event,true)

func cell(x: int, y: int) -> void:
	click(app.board.global_position+app.board.view.cell_rect(Vector2i(x,y)).get_center())

func capture(name: String) -> void:
	await RenderingServer.frame_post_draw
	check(root.get_texture().get_image().save_png(output.path_join(name+".png"))==OK,"original actual EXE framebuffer")

func slots() -> Array:
	var result: Array = []
	for item in app.sessions: result.append(Store.snapshot(item,item.view_state))
	return result

func run() -> void:
	output=OS.get_environment("AT_PACK_OUTPUT")
	var mode := OS.get_environment("AT_PACK_MODE")
	if output.is_empty() or not mode in ["before","after","restart"]: get_tree().quit(4);return
	root.size=Vector2i(1280,720);root.gui_embed_subwindows=true;root.notify_mouse_entered()
	app=Main.new();root.add_child(app);app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await frames()
	check(app.sessions.size()==6 and app.album.visible,"actual packed fixture catalog starts")
	app.album.choose_sort("added")
	await frames()
	check(app.choices[0].picture.artwork==null and app.choices[1].picture.artwork==null,"fresh/begun reveal not loaded")
	if mode=="before":
		check(app.choices[2].picture.artwork==null,"new solved candidate remains unrevealed")
		app.select_puzzle(0);await frames()
		cell(2,2);cell(3,2)
		click(app.undo_button.get_global_rect().get_center());await frames()
		check(app.session.player.cursor==1 and app.session.player.history.size()==2 and not app.session.completed,"actual input leaves begun history and redo")
		app.show_album();app.select_puzzle(2);await frames()
		for x: int in range(5): cell(x,2)
		check(app.session.completed,"actual pointer input earned completion")
		while app.reveal_view.active: await get_tree().process_frame
	else:
		check(app.sessions[0].player.cursor==1 and app.sessions[0].player.history.size()==2 and not app.sessions[0].completed,"begun history and redo survive actual process/export restart")
		app.select_puzzle(2);await frames()
		check(app.session.completed and app.ending.visible and not app.reveal_view.active,"solved save opens stable end without replay/migration")
	var preserved := slots()
	var image: Image = app.reveal_view.artwork.get_image()
	if image.is_compressed(): image.decompress()
	var expected := Color8(56,132,90) if mode=="before" else Color8(174,85,52)
	check(image.get_pixel(128,64).is_equal_approx(expected),"actual PCK contains the expected image revision")
	check(image.get_pixel(76,76).is_equal_approx(Color.WHITE) and image.get_pixel(154,154).a==0 and absf(image.get_pixel(16,128).a-80.0/255)<.001,"actual imported white/hole/soft alpha")
	await capture(mode+"-end")
	click(app.completion_reset.get_global_rect().get_center());await frames()
	check(app.reset_dialog.visible,"reset still requires explicit confirmation")
	var cancel: Control = app.reset_dialog.get_cancel_button()
	click(cancel.get_global_rect().get_center()+Vector2(cancel.get_window().position));await frames()
	check(slots()==preserved,"cancel preserves begun and solved saves")
	app.show_album();await frames()
	check(app.choices[0].picture.artwork==null and app.choices[1].picture.artwork==null and app.choices[2].picture.artwork!=null,"no premature reveal alongside revised solved card")
	await capture(mode+"-catalog")
	var slot_root := ProjectSettings.globalize_path("user://p1/saves")
	var hashes: Dictionary = {}
	for name: String in ["t01.json","t04.json"]: hashes[name]=FileAccess.get_sha256(slot_root.path_join(name))
	var definitions: Dictionary = {}
	for name: String in ["t01","t04"]: definitions[name]=FileAccess.get_sha256("res://data/fixtures/"+name+".json")
	var report := {"format":"picross-at-windows-process-v1","test_only":true,"mode":mode,"checks":checks,"failures":failures,
		"pid":OS.get_process_id(),"executable":OS.get_executable_path(),"profile":slot_root,"slots":slots(),"slot_hashes":hashes,
		"definitions":definitions,"registry_sha256":FileAccess.get_sha256("res://data/registry.json"),
		"image_pixel":[expected.r,expected.g,expected.b],"display":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name()}
	var file := FileAccess.open(output.path_join(mode+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")+"\n");file.close()
	app.free();print("AT_WINDOWS_PROCESS_OK ",mode," ",checks);get_tree().quit(0 if failures.is_empty() else 4)
