extends RefCounted
## Small native GUI regression. OS delivery is checked separately in the export.
const ButtonType = preload("res://ui/book_button.gd")
const BoardType = preload("res://ui/drawing_board.gd")
const Session = preload("res://model/session.gd")
var proof: SceneTree
var viewport: SubViewport
var board: Control
var button: Control
var clicks: int = 0
var rows: Array = []

class ConsumedRelease extends Node:
	var board: Control
	func _input(event: InputEvent) -> void:
		if event is InputEventMouseButton and not event.pressed:
			board._input(event)
			get_viewport().set_input_as_handled()

class SynchronousHide extends ButtonType:
	func dismiss_tooltip() -> void:
		if tooltip_ref == null: return
		var tip: Control = tooltip_ref.get_ref()
		if tip != null and tip.is_inside_tree(): tip.get_window().hide()
		tooltip_ref = null

func motion(point: Vector2, mask: int = 0) -> void:
	var event := InputEventMouseMotion.new()
	event.position = point
	event.button_mask = mask
	viewport.push_input(event,true)

func press(point: Vector2, down: bool, index: MouseButton = MOUSE_BUTTON_LEFT, mask: int = 0) -> void:
	var event := InputEventMouseButton.new()
	event.position = point
	event.button_index = index
	event.pressed = down
	event.button_mask = mask
	viewport.push_input(event,true)

func visible_tip(control: Control) -> Control:
	if control.tooltip_ref == null: return null
	var tip: Control = control.tooltip_ref.get_ref()
	return tip if tip != null and tip.is_inside_tree() and tip.get_window().visible else null

func tip_after(label: String, expected: bool = true) -> void:
	motion(button.get_rect().get_center())
	await proof.create_timer(0.65).timeout
	await proof.frames(1)
	var shown: bool = visible_tip(button) != null
	var ok: bool = shown == expected and viewport.gui_get_hovered_control() == button
	proof.check(ok,"F01 tooltip "+label)
	rows.append({"case":label,"visible":shown,"expected":expected,"passed":ok})

func run(context: SceneTree) -> Array:
	proof = context
	viewport = SubViewport.new()
	viewport.size = Vector2i(700,500)
	viewport.gui_embed_subwindows = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	proof.root.add_child(viewport)
	viewport.notify_mouse_entered()
	board = BoardType.new()
	board.session = Session.new(proof.Study.StudyContent.Inputs.read().definitions[0])
	board.size = Vector2(440,450)
	viewport.add_child(board)
	board.fit_all()
	button = ButtonType.new()
	button.theme = proof.study.app.theme
	button.text = "F01"
	button.tooltip_text = "Erklärung"
	button.position = Vector2(500,40)
	button.size = Vector2(160,50)
	button.pressed.connect(func(): clicks += 1)
	viewport.add_child(button)
	await proof.frames(1)
	proof.check(not button.paper_transparent and button.get_theme_color("font_color").a > 0,"F01 regular BookButton default")
	await tip_after("default-idle")
	# Native cancellation must leave popup traversal intact during this callback.
	var tip: Control = visible_tip(button)
	if tip != null:
		var popup: Window = tip.get_window()
		button.dismiss_tooltip()
		proof.check(popup.visible and popup.is_queued_for_deletion(),"F01 deferred popup teardown")
		await proof.frames(1)
		proof.check(not is_instance_valid(popup),"F01 popup released after dispatch")
	var cell: Vector2 = board.view.cell_rect(Vector2i(2,2)).get_center()
	proof.check(board.view.hit(cell) == Vector2i(2,2),"F01 fixture has a visible start cell")
	var outside: Vector2 = button.get_rect().get_center()
	for kind: String in ["left","right","outside","clue","chord","escape","lost-release","resize"]:
		var before: int = board.session.player.cursor
		var index: MouseButton = MOUSE_BUTTON_RIGHT if kind == "right" else MOUSE_BUTTON_LEFT
		var mask: int = MOUSE_BUTTON_MASK_RIGHT if index == MOUSE_BUTTON_RIGHT else MOUSE_BUTTON_MASK_LEFT
		var start: Vector2 = Vector2(board.row_clue_area().get_center().x,cell.y) if kind == "clue" else cell
		motion(start)
		press(start,true,index,mask)
		proof.check(board.clue_press_owned if kind == "clue" else board.session.gesture.active,"F01 starts "+kind)
		if kind == "chord": press(start,true,MOUSE_BUTTON_RIGHT,3)
		elif kind == "escape":
			var escape := InputEventKey.new()
			escape.keycode = KEY_ESCAPE
			escape.pressed = true
			viewport.push_input(escape,true)
		elif kind == "lost-release":
			motion(start,0)
			proof.check(not board.session.gesture.active and board.session.player.cursor == before,"F01 lost release cancels without commit")
		elif kind == "resize": board.size.x += 1
		if kind == "outside": motion(outside,mask)
		press(outside if kind == "outside" else start,false,index,2 if kind == "chord" else 0)
		if kind == "chord": press(start,false,MOUSE_BUTTON_RIGHT,0)
		var expected_cursor: int = before+1 if kind in ["left","right","outside"] else before
		proof.check(board.session.player.cursor == expected_cursor and not board.session.gesture.active and not board.cell_buttons_blocked,"F01 gesture "+kind)
		await tip_after(kind)
		motion(cell)
		proof.check(board.hover == Vector2i(2,2),"F01 crosshair returns "+kind)
	proof.check(clicks == 0,"F01 outside releases never click another control")
	var cells: Array = board.session.player.cells.duplicate()
	var cursor: int = board.session.player.cursor
	board.session.undo()
	var undone: bool = board.session.player.cursor == cursor-1 and board.session.player.cells != cells
	board.session.redo()
	proof.check(undone and board.session.player.cursor == cursor and board.session.player.cells == cells,"F01 exact undo redo")
	# Restore only the defective release consumption in a test-only interceptor.
	var old := ConsumedRelease.new()
	old.board = board
	viewport.add_child(old)
	motion(cell)
	press(cell,true,MOUSE_BUTTON_LEFT,1)
	press(cell,false)
	await tip_after("negative-consumed-release",false)
	old.free()
	# Deliver the matching Up through GUI to end the counterexample's capture.
	press(cell,false)
	await tip_after("release-recovered")
	# A real native popup exercises the lifetime oracle against the old method.
	var legacy := SynchronousHide.new()
	legacy.theme = button.theme
	legacy.tooltip_text = "Alte Lebensdauer"
	legacy.position = Vector2(500,150)
	legacy.size = Vector2(160,50)
	viewport.add_child(legacy)
	motion(legacy.get_rect().get_center())
	await proof.create_timer(0.65).timeout
	await proof.frames(1)
	var old_tip: Control = visible_tip(legacy)
	var rejected: bool = false
	if old_tip != null:
		var popup: Window = old_tip.get_window()
		legacy.dismiss_tooltip()
		rejected = not popup.visible and not popup.is_queued_for_deletion()
		popup.queue_free()
	proof.check(rejected,"F01 negative synchronous popup hide rejected")
	rows.append({"case":"negative-synchronous-hide","passed":rejected})
	await proof.frames(1)
	viewport.queue_free()
	await proof.frames(1)
	return rows
