extends SceneTree
## Regular main scene, synthetic viewport input, three real process stages.
const Main = preload("res://ui/main.gd")
const Definition = preload("res://model/definition.gd")
const SaveStore = preload("res://model/save_store.gd")
var app: Main
var target: Viewport
var checks: int = 0
var failures: int = 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, description: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		push_error("RP3_FAIL: " + description)

func event(point: Vector2, pressed: bool, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	target.push_input(motion,true)
	var mouse: InputEventMouseButton = InputEventMouseButton.new()
	mouse.position = point
	mouse.global_position = point
	mouse.button_index = button
	mouse.pressed = pressed
	mouse.button_mask = (MOUSE_BUTTON_MASK_RIGHT if button == MOUSE_BUTTON_RIGHT else MOUSE_BUTTON_MASK_LEFT) if pressed else 0
	target.push_input(mouse,true)

func click(point: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	event(point,true,button)
	event(point,false,button)

func cell_point(cell: Vector2i) -> Vector2:
	return app.board.global_position + app.board.view.cell_rect(cell).get_center()

func setup(viewport: Viewport) -> void:
	target = viewport
	app = load("res://main.tscn").instantiate()
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	target.add_child(app)
	await process_frame
	await process_frame
	check(app.sessions.size() == 9 and app.sessions[3].definition.id == "F-04", "regular registration of neutral F-04")
	check(Definition.load_fixture("../art/f04").is_empty() and Definition.load_fixture("unknown").is_empty(), "fixed definition paths reject unregistered IDs")
	check(app.store.path_for("../f04").is_empty(), "save paths reject traversal")
	check(Definition.validate(app.sessions[3].definition).is_empty(), "schema/hints/reveal validate")
	click(app.choices[3].get_global_rect().get_center())
	await process_frame
	check((app.ending.visible if app.session.completed else app.work.visible) and app.session == app.sessions[3], "real album choice opens F-04 according to saved completion")
	app.board.restore_view(app.board.capture_view().merged({"zoom":72,"overview":false},true))

func partial() -> void:
	check(not app.session.completed and app.session.reveal().is_empty() and not app.title.text.contains("Fliegenpilz"), "unknown state has no motif name or reveal")
	check(app.session.definition.solution[0][0] == 0, "wrong input is deliberately outside motif")
	click(cell_point(Vector2i(0,0)))
	check(app.session.player.cells[0] == 1 and app.mini.cells[0] == 1 and not app.session.completed, "wrong own input remains in miniature")
	click(app.undo_button.get_global_rect().get_center())
	check(app.mini.cells[0] == -1, "real Undo removes own wrong input")
	click(app.redo_button.get_global_rect().get_center())
	check(app.mini.cells[0] == 1 and app.session.player.undo_used, "real Redo restores own wrong input")
	app.show_album()
	check(app.album_previews[3].cells[0] == 1 and app.album_reveals[3].payload.is_empty() and not app.choices[3].text.contains("Fliegenpilz"), "album partial thumbnail has same wrong input without reveal")

func finish() -> void:
	check(app.session.player.cells[0] == 1 and app.session.player.undo_used and not app.session.completed, "real new process restored partial/history/undo")
	click(cell_point(Vector2i(0,0)),MOUSE_BUTTON_RIGHT)
	check(app.session.player.cells[0] == 0, "wrong fill removed by normal right-click conversion")
	var last: Vector2i = Vector2i(-1,-1)
	for y: int in range(app.session.player.height):
		for x: int in range(app.session.player.width):
			if app.session.definition.solution[y][x] > 0:
				last = Vector2i(x,y)
	for y: int in range(app.session.player.height):
		for x: int in range(app.session.player.width):
			var cell: Vector2i = Vector2i(x,y)
			if app.session.definition.solution[y][x] > 0 and cell != last:
				click(cell_point(cell))
	check(not app.session.completed and app.session.reveal().is_empty(), "missing final fill keeps spoiler boundary")
	event(cell_point(last),true)
	check(not app.session.completed and app.session.reveal().is_empty() and app.mini.cells[last.y*20+last.x] == 1, "last-cell preview visible only as own input")
	event(cell_point(last),false)
	check(app.session.completed and app.ending.visible and not app.work.visible, "real committed last event opens completion")
	check(app.completion_title.text == "Fliegenpilz" and app.reveal_view.payload.image == "res://art/f04.svg", "new name and matching refined asset only after completion")
	check(app.session.player.cells.count(-1) > 0, "completion without mandatory background crosses")
	app.show_album()
	check(app.album_reveals[3].visible and app.album_reveals[3].payload.definition_id == "F-04", "earned album artwork bound to F-04")
	check(app.sessions[0].player.cells.count(-1) == 400 and app.sessions[1].player.cells.count(-1) == 1600 and app.sessions[2].player.cells.count(-1) == 10000, "old slots remain untouched")

func restored() -> void:
	check(app.session.completed and app.session.is_solution() and app.session.player.undo_used, "second real restart restores full completion/history")
	app.show_album()
	check(app.album_reveals[3].visible and app.choices[3].text.contains("Fliegenpilz"), "new process earned album state")
	var first: Dictionary = app.store.load_slot(app.sessions[0].definition)
	check(first.status == "fresh" or first.status == "loaded" and first.data.cells.count(-1) == 400, "isolated new slot has not changed old fixture cells")

func run() -> void:
	var isolated: String = OS.get_environment("P1_TEST_SAVE_ROOT")
	if isolated.is_empty():
		push_error("RP3 requires explicit isolated save root")
		quit(4)
		return
	SaveStore.test_root_override = isolated
	root.size = Vector2i(1920,1080)
	await setup(root)
	var stage: String = OS.get_environment("RP3_STAGE")
	if stage == "partial":
		partial()
	elif stage == "finish":
		finish()
	elif stage == "read":
		restored()
	else:
		check(false,"unknown probe stage")
	check(app._flush_current(), "real mandatory flush succeeds")
	print("RP3_RESULT stage=%s checks=%d failures=%d" % [stage,checks,failures])
	if failures == 0:
		print("RP3_" + stage.to_upper() + "_OK")
	quit(0 if failures == 0 else 4)
