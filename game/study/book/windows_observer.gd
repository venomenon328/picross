extends Node
## External, read-only observer of the actual exported PCK. Never injects input.
var study: Node
var directory: String
var trace: FileAccess
var elapsed: float = 0.0
var sequence: int = 0
var root: Window

func _ready() -> void: call_deferred("start")

func start() -> void:
	root = get_tree().root
	directory = OS.get_environment("BOOK_WINDOWS_OBSERVATION")
	if directory.is_empty(): get_tree().quit(4); return
	trace = FileAccess.open(directory.path_join("engine.jsonl"),FileAccess.WRITE)
	root.window_input.connect(func(event: InputEvent):
		if event is InputEventMouse:
			record("window-input",{"position":[event.position.x,event.position.y],"mask":event.button_mask,
				"button":event.button_index if event is InputEventMouseButton else 0,
				"pressed":event.pressed if event is InputEventMouseButton else false}))
	root.focus_entered.connect(func(): record("window-focus-in"))
	root.focus_exited.connect(func(): record("window-focus-out"))
	get_tree().node_added.connect(func(node: Node):
		if node is PopupPanel:
			var id: int = node.get_instance_id()
			node.visibility_changed.connect(func(): record("popup-visible",{"id":id,"visible":node.visible}))
			node.tree_exiting.connect(func(): record("popup-exit",{"id":id})))
	study = get_tree().current_scene
	for control: Node in get_tree().get_nodes_in_group("book-buttons"):
		for event: String in ["mouse_entered","mouse_exited","focus_entered","focus_exited"]:
			control.connect(event,func(): record(event,{"control":str(control.name)}))
	record("started",{"engine":Engine.get_version_info(),"adapter":RenderingServer.get_video_adapter_name(),"os":OS.get_version()})

func identity(node: Object) -> String:
	return str(node.name) if is_instance_valid(node) else ""

func rect(control: Control) -> Array:
	var r: Rect2 = control.get_global_rect()
	return [r.position.x,r.position.y,r.size.x,r.size.y]

func snapshot(full: bool = false) -> Dictionary:
	if not is_instance_valid(study) or not is_instance_valid(study.get("app")): return {}
	var app = study.app
	var board = app.board
	if not is_instance_valid(board): return {}
	var session = app.session
	var tips: Dictionary = {}
	for key: String in app.actions:
		var b: Control = app.actions[key]
		if not b is Button or not "tooltip_ref" in b: continue
		var tip: Control = b.tooltip_ref.get_ref() if b.tooltip_ref != null else null
		tips[key] = {"visible":tip != null and tip.is_inside_tree() and tip.get_window().visible,"rect":rect(b),"caption":b.tooltip_text.strip_edges()}
		if tip != null and tip.is_inside_tree():
			tips[key]["text"] = tip.get_child(0).text
			var popup: Window = tip.get_window()
			tips[key]["popup"] = [popup.position.x,popup.position.y,popup.size.x,popup.size.y]
	var row: Dictionary = {"us":Time.get_ticks_usec(),"state":study.state,"barrier":study.release_barrier,
		"size":[root.size.x,root.size.y],"mode":root.mode,"pointer":str(root.get_mouse_position()),
		"buttons":Input.get_mouse_button_mask(),"gui_hover":identity(root.gui_get_hovered_control()),
		"focus":identity(root.gui_get_focus_owner()),"board_hover":[board.hover.x,board.hover.y],
		"gesture":session.gesture.active,"held":board.held_button,"blocked":board.cell_buttons_blocked,
		"clue":board.clue_press_owned,"cursor":session.player.cursor,"history_size":session.player.history.size(),
		"tool":[board.eraser,board.active_color],"tips":tips,"selected":study.selected_id}
	if full:
		row["presentation"] = study.get_script().resource_path
		row["renderer"] = RenderingServer.get_video_adapter_name()
		row["framebuffer"] = [root.get_texture().get_width(),root.get_texture().get_height()]
		row["screen_dpi"] = DisplayServer.screen_get_dpi()
		row["screen_scale"] = DisplayServer.screen_get_scale()
		row["ui_scale"] = app.ui_scale
		row["section"] = app.info.section
		row["scale_control"] = rect(app.ui_scale_button)
		row["info_switch"] = rect(app.information.get_node("help-access" if app.info.section == "settings" else "settings-access"))
		row["info_return"] = rect(app.actions["nav-work"] if app.info.section == "settings" else app.info.right_return)
		row["cells"] = session.player.cells
		row["history"] = session.player.history
		if "snapshots" in app.store:
			row["memory"] = app.store.snapshots.get(session.definition.id,{})
			row["writes"] = app.store.writes
		else:
			var path: String = app.store.path_for(app.store.key_for_definition(session.definition.id))
			row["slot_path"] = ProjectSettings.globalize_path(path)
			row["memory"] = JSON.parse_string(FileAccess.get_file_as_string(path)) if FileAccess.file_exists(path) else {}
			row["save_error"] = app.save_error
			row["retry"] = rect(app.save_retry)
			row["retry_visible"] = app.save_retry.is_visible_in_tree()
		row["board_rect"] = rect(board)
		var grid: Rect2 = board.view.bounds()
		row["grid"] = [grid.position.x+board.global_position.x,grid.position.y+board.global_position.y,grid.size.x,grid.size.y]
		row["cell_size"] = board.view.cell_size
		var index: int = app.album.visible_ids.find("T-06")
		row["card"] = rect(app.album.choices[index]) if index >= 0 else []
		row["card_clip"] = rect(app.album.right_scroll if index >= 12 else app.album.scroll)
	return row

func record(event: String, detail: Dictionary = {}) -> void:
	if trace == null or sequence >= 4096: return
	sequence += 1
	trace.store_line(JSON.stringify({"seq":sequence,"event":event,"detail":detail,"state":snapshot()}))
	trace.flush()

func _process(delta: float) -> void:
	elapsed += delta
	if elapsed >= 0.08 and is_instance_valid(study) and study.get("app") != null:
		elapsed = 0
		var file := FileAccess.open(directory.path_join("state.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify(snapshot(true)))
		file.close()
