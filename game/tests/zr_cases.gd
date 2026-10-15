extends RefCounted
const Player = preload("res://model/player.gd")
const Gesture = preload("res://model/gesture.gd")
const Session = preload("res://model/session.gd")
const Definition = preload("res://model/definition.gd")
const Main = preload("res://ui/main.gd")
const Store = preload("res://model/save_store.gd")

static func model_cases(t: SceneTree) -> void:
	for dims: Vector2i in [Vector2i(30,30), Vector2i(30,12), Vector2i(12,30)]:
		for direction: Vector2i in [Vector2i.RIGHT,Vector2i.LEFT,Vector2i.DOWN,Vector2i.UP]:
			for target: int in [0,1,8]:
				var p: Player = Player.new(dims.x,dims.y)
				var g: Gesture = Gesture.new()
				var start: Vector2i = Vector2i(4,4)
				var end: Vector2i = start + direction * 100
				var expected: Vector2i = end.clamp(Vector2i.ZERO,dims-Vector2i.ONE)
				g.begin(p,start,target)
				g.move(end)
				var length: int = absi(expected.x-start.x)+absi(expected.y-start.y)+1
				t.check(g.endpoint == expected and g.changes().size() == length,"ZR unbounded jump reaches complete rectangular edge %s/%s/%d" % [dims,direction,target])
				if dims.x == 30 and direction == Vector2i.RIGHT:
					t.check(length == 26,"ZR 30 columns, 5 to outside = 26")
				g.move(start+direction*2)
				t.check(g.changes().size()==3,"ZR outside retreat remains elastic")
				g.move(end)
				t.check(g.finish(p) and p.history.size()==1 and p.cells.count(target)==length,"ZR full edge is one action")
				t.check(p.undo() and p.cells.count(-1)==dims.x*dims.y,"ZR full edge undo exact")
				t.check(p.redo() and p.cells.count(target)==length,"ZR full edge redo exact")
	var p: Player = Player.new(30,12)
	var g: Gesture = Gesture.new()
	g.begin(p,Vector2i(29,4),1)
	g.move(Vector2i(100,20))
	t.check(g.axis==Gesture.Axis.HORIZONTAL and g.endpoint==Vector2i(29,4),"ZR axis chosen before asymmetric clamping")
	g.move(Vector2i(29,100))
	t.check(g.axis==Gesture.Axis.HORIZONTAL,"ZR projection at edge start does not unlock")
	g.move(Vector2i(29,4),false)
	t.check(g.axis==Gesture.Axis.HORIZONTAL,"ZR clipped start-coordinate is not an actual hit")
	g.move(Vector2i(29,4))
	g.move(Vector2i(29,100))
	t.check(g.axis==Gesture.Axis.VERTICAL and g.endpoint==Vector2i(29,11),"ZR true origin permits new outside axis")
	g.cancel()
	g.begin(p,Vector2i(4,4),0)
	g.move(Vector2i(100,100))
	t.check(g.axis==Gesture.Axis.UNLOCKED and g.endpoint==Vector2i(4,4),"ZR outside diagonal tie waits")
	g.cancel()
	t.check(not g.begin(p,Vector2i(-1,4),1),"ZR clamping cannot start outside")
	# Protection, target and start category remain frozen over exterior motion.
	p.cells[4*30+8]=0
	p.cells[4*30+9]=8
	g.begin(p,Vector2i(4,4),1)
	g.move(Vector2i(100,4))
	t.check(g.changes().size()==24 and g.target==1 and g.initial==-1,"ZR geometric 26 includes two protected cells")
	g.finish(p)
	t.check(p.cells[4*30+8]==0 and p.cells[4*30+9]==8,"ZR exterior stroke preserves GP48 prefill")

static func pattern() -> Dictionary:
	var data: Dictionary = Definition.load_fixture("t01").duplicate(true)
	data.width=30
	data.height=12
	data.solution=[]
	data.rows=[]
	data.columns=[]
	for y: int in range(12):
		var row: Array = []
		for x: int in range(30): row.append(1 if x==y else 0)
		data.solution.append(row)
		data.rows.append(Definition.hints(row))
	for x: int in range(30): data.columns.append(Definition.hints(Definition.column(data.solution,x)))
	return data

static func point(b: Control, cell: Vector2i) -> Vector2:
	return b.get_global_transform_with_canvas()*b.view.cell_rect(cell).get_center()

static func run(t: SceneTree) -> void:
	model_cases(t)
	var old_root: String = Store.test_root_override
	Store.test_root_override += "-zr"
	var app: Main = load("res://main.tscn").instantiate()
	t.root.add_child(app)
	app.sessions[0]=Session.new(pattern())
	app.select_puzzle(0)
	app.open_puzzle()
	await t.process_frame
	await t.process_frame
	var b: Control = app.board
	var start: Vector2i = Vector2i(4,4)
	var clock: Array[int] = [1000000]
	b.animation_clock=func() -> int: return clock[0]
	for animations: bool in [true,false]:
		b.set_animations(animations)
		for button: MouseButton in [MOUSE_BUTTON_LEFT,MOUSE_BUTTON_RIGHT]:
			for direction: Vector2i in [Vector2i.RIGHT,Vector2i.LEFT,Vector2i.DOWN,Vector2i.UP]:
				b.cancel_gesture()
				app.session.player=Player.new(30,12)
				app.refresh()
				var a: Vector2 = point(b,start)
				var outside: Vector2 = point(b,start+direction*100)
				t.mouse_motion(a,false)
				t.mouse_button(a,true,button)
				t.check(b.gesture_length()==1 and not b.gesture_counter.visible,"ZR single cell has no counter")
				# Release alone supplies the final position; no last Motion.
				t.mouse_button(outside,false,button)
				var expected_end: Vector2i = (start+direction*100).clamp(Vector2i.ZERO,Vector2i(29,11))
				var length: int = absi(expected_end.x-start.x)+absi(expected_end.y-start.y)+1
				var value: int = 1 if button==MOUSE_BUTTON_LEFT else 0
				t.check(app.session.player.cells.count(value)==length and app.session.player.history.size()==1,"ZR own Mouse-Up position completes full edge once")
				t.check(not b.gesture_counter.visible and b.preview.is_empty(),"ZR drop clears transient counter/preview")
				t.check(b.effects.size()==(length if animations else 0),"ZR animations share complete release set")
				if animations:
					var first: int = start.y*30+start.x
					var last: int = expected_end.y*30+expected_end.x
					t.check(b.effects[first].start==clock[0] and b.effects[last].start>clock[0],"ZR release animation ordered from actual start")
				t.check(app.mini.cells==app.session.player.cells,"ZR release miniature immediately matches model")
				var save: Dictionary = Store.snapshot(app.session,b.capture_view())
				t.check(Store.validate(save,app.session.definition).is_empty() and not JSON.stringify(save).contains("gesture_counter"),"ZR save contains only confirmed state/history")
				app.session.undo()
				t.check(app.session.player.cells.count(-1)==360,"ZR release exact undo")
				app.session.redo()
				t.check(app.session.player.cells.count(value)==length,"ZR release exact redo")
	# Cursor movement within a cell and across the sidebar, all edges/corners.
	app.session.player=Player.new(30,12)
	b.pointer_press(b.view.cell_rect(start).get_center(),MOUSE_BUTTON_LEFT)
	b.pointer_move(b.view.cell_rect(Vector2i(8,4)).get_center(),true)
	var initial_cursor: Vector2 = b.gesture_counter.cursor
	b.pointer_move(b.view.cell_rect(Vector2i(8,4)).get_center()+Vector2(1,1),true)
	t.check(b.gesture_counter.cursor!=initial_cursor and b.gesture_length()==5,"ZR cursor follows subcell motion")
	for ui: float in [1.0,1.25]:
		b.ui_scale=ui
		for cursor: Vector2 in [Vector2(-100,-100),Vector2(1400,-100),Vector2(-100,800),Vector2(1400,800),app.undo_button.get_global_rect().get_center()]:
			b.pointer_move(b.get_global_transform_with_canvas().affine_inverse()*cursor,false)
			var placement: Dictionary = b.gesture_counter.placement()
			t.check(b.gesture_counter.visible and b.gesture_counter.cursor==cursor,"ZR exterior/sidebar cursor stays active")
			t.check(Rect2(Vector2.ZERO,Vector2(t.root.size)).encloses(placement.rect),"ZR native glyph/outline envelope inside client")
			t.check(placement.font==b.clue_font() and placement.font.get_font_name()=="Delight Coffee" and b.gesture_counter.mouse_filter==Control.MOUSE_FILTER_IGNORE,"ZR active font and passive overlay")
	b.ui_scale=1.0
	b.pointer_move(b.view.cell_rect(start).get_center(),true)
	t.check(not b.gesture_counter.visible and app.session.gesture.axis==Gesture.Axis.UNLOCKED,"ZR true return hides length one")
	b.cancel_gesture()
	# Release over an action is consumed; it must not undo the new stroke.
	var a: Vector2 = point(b,start)
	var action: Vector2 = app.undo_button.get_global_rect().get_center()
	t.mouse_motion(a,false)
	t.mouse_button(a,true)
	t.mouse_motion(action,true)
	t.mouse_button(action,false)
	t.check(app.session.player.cursor==1 and not b.gesture_counter.visible,"ZR sidebar release commits without button action")
	# Lost button mask cancels instead of catching up on re-entry.
	t.mouse_motion(a,false)
	t.mouse_button(a,true)
	t.mouse_motion(point(b,Vector2i(8,4)),true)
	var cursor_before: int = app.session.player.cursor
	t.mouse_motion(a,false)
	t.check(not app.session.gesture.active and not b.gesture_counter.visible and app.session.player.cursor==cursor_before,"ZR unassignable motion cancels without phantom commit")
	t.mouse_button(a,false)
	t.mouse_button(a,true)
	t.mouse_button(a,false)
	t.check(app.session.player.cursor==cursor_before+1,"ZR fresh Down works after lost input")
	app.queue_free()
	await t.process_frame
	Store.test_root_override=old_root
