extends SceneTree
## External --script against the actual exported PCK. Never injects Viewport input.
const Session = preload("res://model/session.gd")
const Player = preload("res://model/player.gd")
const Definition = preload("res://model/definition.gd")
var app: Control
var directory: String
var command_id: int = -1
var events: Array = []

class Sensor extends Node:
	var record: Callable
	func _input(event: InputEvent) -> void:
		if event is InputEventMouse:
			record.call(event)

func _initialize() -> void:
	directory=OS.get_environment("ZR_WINDOWS_OUTPUT")
	if directory.is_empty() or DisplayServer.get_name()!="Windows":
		quit(2)
		return
	call_deferred("run")

func run() -> void:
	app=load("res://main.tscn").instantiate()
	root.add_child(app)
	# Fixed technical raster, using only a registered storage/resource binding.
	var data: Dictionary = app.sessions[0].definition.duplicate(true)
	data.width=30
	data.height=30
	data.solution=[]
	data.rows=[]
	data.columns=[]
	for y: int in range(30):
		var row: Array = []
		for x: int in range(30): row.append(1 if x==y else 0)
		data.solution.append(row)
		data.rows.append(Definition.hints(row))
	for x: int in range(30): data.columns.append(Definition.hints(Definition.column(data.solution,x)))
	app.sessions[0]=Session.new(data)
	app.select_puzzle(0)
	app.open_puzzle()
	root.size=Vector2i(1280,720)
	root.position=Vector2i(300,200)
	app.set_ui_scale(1.25)
	var sensor: Sensor = Sensor.new()
	sensor.record=func(event: InputEventMouse) -> void:
		var record: Dictionary = {"motion":event is InputEventMouseMotion,"position":[event.position.x,event.position.y],"mask":int(event.button_mask),"focus":root.has_focus()}
		if event is InputEventMouseButton:
			record["button"]=int(event.button_index)
			record["pressed"]=event.pressed
		events.append(record)
	root.add_child(sensor)
	root.focus_exited.connect(func() -> void: events.append({"focus_out":true}))
	var timer: Timer = Timer.new()
	timer.wait_time=0.05
	timer.timeout.connect(poll)
	root.add_child(timer)
	timer.start()
	create_timer(90).timeout.connect(func() -> void: quit(4))

func poll() -> void:
	var path: String = directory.path_join("command.json")
	if FileAccess.file_exists(path):
		var cmd: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if cmd is Dictionary and int(cmd.id)!=command_id:
			command_id=int(cmd.id)
			if cmd.op=="reset":
				app.board.cancel_gesture()
				app.board.cell_buttons_blocked=false
				app.session.player=Player.new(30,30)
				app.session.completed=false
				app.refresh()
				events.clear()
			elif cmd.op=="capture":
				await RenderingServer.frame_post_draw
				root.get_texture().get_image().save_png(directory.path_join(str(cmd.name)+".png"))
			elif cmd.op=="quit":
				quit()
	var b: Control = app.board
	var starts: Array = []
	for cell: Vector2i in [Vector2i(4,4),Vector2i(25,4),Vector2i(4,8)]:
		var p: Vector2 = b.get_global_transform_with_canvas()*b.view.cell_rect(cell).get_center()
		starts.append([p.x,p.y])
	var counter: Dictionary = b.gesture_counter.placement() if b.gesture_counter.visible else {}
	var result: Dictionary = {"command_id":command_id,"hwnd":DisplayServer.window_get_native_handle(DisplayServer.WINDOW_HANDLE),
		"client":[root.size.x,root.size.y],"ui":app.ui_scale,"renderer":RenderingServer.get_video_adapter_name(),
		"screen":[DisplayServer.screen_get_size().x,DisplayServer.screen_get_size().y],"focus":root.has_focus(),
		"active":app.session.gesture.active,"length":b.gesture_length(),"counter":b.gesture_counter.visible,
		"counter_rect":str(counter.get("rect","")),"cursor":str(b.gesture_counter.cursor),"starts":starts,
		"endpoint":[app.session.gesture.endpoint.x,app.session.gesture.endpoint.y],"mouse_mode":Input.mouse_mode,
		"history":app.session.player.history.size(),"filled":app.session.player.cells.count(1),"empty":app.session.player.cells.count(0),
		"blocked":b.cell_buttons_blocked,"events":events}
	var f: FileAccess = FileAccess.open(directory.path_join("status.tmp"),FileAccess.WRITE)
	f.store_string(JSON.stringify(result)+"\n")
	f.close()
	DirAccess.rename_absolute(directory.path_join("status.tmp"),directory.path_join("status.json"))
