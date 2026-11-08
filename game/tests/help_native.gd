extends RefCounted
## Extend the existing regular-book integration, using its isolated real store.
const Store = preload("res://model/save_store.gd")
const Text = preload("res://ui/ui_text.gd")

static func click(t: SceneTree, control: Control) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = control.get_global_rect().get_center()
	motion.global_position = motion.position
	t.root.push_input(motion,true)
	for down: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = control.get_global_rect().get_center()
		event.global_position = event.position
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		t.root.push_input(event,true)


static func layout(t: SceneTree, node: Node, width: float, u: float) -> void:
	for child: Node in node.get_children():
		if child is Control and not child.is_visible_in_tree(): continue
		if child is Label:
			t.check(child.size.x <= width+1 and child.size.y+1 >= child.get_minimum_size().y,"HIL wrapped label fits "+child.text.left(24))
			t.check(child.get_theme_font_size("font_size") == roundi(child.get_meta("base_font")*u),"HIL nested text scales "+child.text.left(24))
			var face: Font = child.get_theme_font("font")
			if child.has_meta("help_heading"):
				t.check(face == t.book.app.WORK_TITLE_FONT,"HIL explicit small information heading role")
			else: t.check(face == Text.font(),"HIL nested normal text role")
		if child is Button:
			t.check(child.size.y >= 44*u and child.size.x >= 44*u and child.paper_transparent,"HIL chapter target and transparent ink")
		layout(t,child,width,u)

static func scroll_to(t: SceneTree, control: Control) -> void:
	# Chapter visibility changes queue nested container layout. Read positions
	# only after that reflow, then let the scroll range clamp the new offset.
	await t.frames(4)
	var scroll: ScrollContainer = t.book.app.info.help_scroll
	scroll.scroll_vertical += roundi(control.get_global_rect().position.y-scroll.get_global_rect().position.y)
	await t.frames(4)

static func run(t: SceneTree) -> void:
	var book = t.book
	var app = book.app
	t.root.size = Vector2i(1920,1080)
	book.set_ui_scale(1.0)
	await t.frames(4)

	t.check(book.information_routes.request("help"),"HIL help enters from work")
	await t.settled()
	var panel = app.help_panel
	var snapshot: Dictionary = Store.snapshot(app.session,app.session.view_state)
	var path: String = app.store.path_for(app.store.key_for_definition(app.session.definition.id))
	var saved: PackedByteArray = t.bytes(path)
	var active: int = app.session.get_instance_id()
	t.check(panel.chapter == 0 and panel.buttons.size() == 4,"HIL fresh visit starts principle with four direct chapters")

	await scroll_to(t,panel.figures[4].get_parent())

	# One detailed configuration, the others only for the actual content/clip
	# boundaries. No routes × chapters × resolutions Cartesian replay.
	# This is a help-layout diagnostic, not a display-preset acceptance test.
	# ANZ's native monitor watchdog otherwise restores its configured preset
	# midway through a directly imposed measurement viewport (notably 1440p).
	var controller: Node = app.display_controller
	var display_processing: bool = controller != null and controller.is_processing()
	var prior_mode: int = t.root.mode
	var prior_borderless: bool = t.root.borderless
	if controller != null: controller.set_process(false)
	if OS.get_name() == "Windows":
		t.root.mode = Window.MODE_WINDOWED
		t.root.borderless = true
	var layouts: int = 0
	for spec: Array in [[1920,1080,1.0],[1280,720,1.25],[2560,1440,1.25]]:
		t.root.size = Vector2i(spec[0],spec[1])
		if OS.get_name() == "Windows": DisplayServer.window_set_size(t.root.size)
		book.set_ui_scale(spec[2])
		await t.frames(5)
		for i: int in range(4):
			panel.choose(0)
			await t.frames(3)
			click(t,panel.buttons[i])
			# Native Labels reshape after drawing, then nested CopyColumns update
			# the article range. Do not send all wheel events into an old range.
			await t.frames(10)
			t.check(panel.chapter == i and panel.buttons[i].selected and app.info.help_scroll.scroll_vertical == 0,"HIL direct chapter starts at top")
			layouts += 1
			var scroll: ScrollContainer = app.info.help_scroll
			t.check(scroll.get_h_scroll_bar().max_value <= scroll.size.x+1,"HIL no horizontal scroll at "+str(spec))
			layout(t,panel.chapters[i],scroll.size.x,app.ui_scale)
			for figure: Control in panel.figures:
				if figure.is_visible_in_tree():
					t.check(figure.size.x <= scroll.size.x and figure.cell_size >= 32,"HIL readable native diagram within paper")
			# Real wheel events must reach the content end and must not zoom or
			# edit the hidden work board. Bound enough for the longest chapter.
			for n: int in range(200):
				var event := InputEventMouseButton.new()
				event.position = scroll.get_global_rect().get_center()
				event.global_position = event.position
				event.button_index = MOUSE_BUTTON_WHEEL_DOWN
				event.pressed = true
				t.root.push_input(event,true)
				event = event.duplicate()
				event.pressed = false
				t.root.push_input(event,true)
				if n % 8 == 7:
					# Native text/range invalidation may arrive with the input batch.
					# Give it real frames before deciding the article has ended.
					await t.frames(2)
					var range_end: float = scroll.get_v_scroll_bar().max_value-scroll.get_v_scroll_bar().page
					var last: Control = panel.chapters[i].get_children()[-1]
					if scroll.scroll_vertical >= maxi(0,int(range_end)) and last.get_global_rect().end.y <= scroll.get_global_rect().end.y+1: break
			await t.frames(4)
			var bar: VScrollBar = scroll.get_v_scroll_bar()
			var reached: bool = scroll.scroll_vertical == maxi(0,int(bar.max_value-bar.page)) and panel.chapters[i].get_global_rect().end.y <= scroll.get_global_rect().end.y+1
			if not reached: print("HIL_SCROLL_RANGE ",spec," chapter=",i," offset=",scroll.scroll_vertical," end=",bar.max_value-bar.page," content=",panel.chapters[i].get_global_rect()," clip=",scroll.get_global_rect())
			t.check(reached,"HIL final chapter content reachable")
			t.check(app.info.right_return.get_global_rect().end.y < scroll.get_global_rect().position.y,"HIL return stays above independent clip")
	t.check(layouts == 12,"HIL complete native chapter layout coverage")
	t.check(panel.figures.all(func(item: Control) -> bool: return not item.is_processing() and not item.is_physics_processing()),"HIL passive diagrams have no processing tick")
	t.root.mode = prior_mode
	t.root.borderless = prior_borderless
	t.root.size = Vector2i(1920,1080)
	if controller != null: controller.set_process(display_processing)
	book.set_ui_scale(1.0)
	panel.choose(1)

	panel.choose(3)
	await scroll_to(t,panel.chapters[3].get_child(3))

	panel.choose(2)
	for figure: Control in panel.figures:
		if figure.identity == "help/clue-open": await scroll_to(t,figure.get_parent())

	var offset: int = app.info.help_scroll.scroll_vertical
	t.check(offset > 0,"HIL help retains a nonzero reading position")
	# Passive content clicks use the same native GUI dispatch as chapter
	# buttons and wheel input, with the real board present behind the page.
	click(t,app.info.help_scroll)
	t.check(Store.snapshot(app.session,app.session.view_state) == snapshot and app.session.get_instance_id() == active and t.bytes(path) == saved,"HIL editorial input preserves session history view and save")
	t.check(book.information_routes.request("settings"),"HIL switches to settings")
	var deadline: int = Time.get_ticks_msec()+8000
	while book.state == book.State.PREPARING and Time.get_ticks_msec() < deadline: await t.process_frame
	while book.state == book.State.OPENING and book.elapsed < 0.25 and Time.get_ticks_msec() < deadline: await t.process_frame
	t.check(book.capture != null and not book.information_routes.textures.is_empty(),"HIL content participates in moving book captures")

	await t.settled()
	t.check(book.information_routes.request("help"),"HIL returns to help in same visit")
	await t.settled()
	t.check(panel.chapter == 2 and app.info.help_scroll.scroll_vertical == offset,"HIL chapter and scroll survive settings pan")
	t.check(book.information_routes.request_return(),"HIL returns to bound puzzle")
	await t.settled()
	t.check(app.work.visible and app.session.get_instance_id() == active and Store.snapshot(app.session,app.session.view_state) == snapshot,"HIL work origin preserves all durable state")
	t.check(book.request_return(),"HIL opens bound catalog")
	await t.settled()
	var context: Dictionary = book.context().duplicate(true)
	t.check(book.information_routes.request("help"),"HIL help enters from catalog")
	await t.settled()
	t.check(panel.chapter == 0 and app.info.help_scroll.scroll_vertical == 0,"HIL new catalog visit resets chapter and scroll")
	t.check(book.information_routes.request_return(),"HIL catalog return accepted")
	await t.settled()
	t.check(book.context() == context and book.capture == null and book.information_routes.textures.is_empty(),"HIL catalog context and capture lifetime preserved")
	# Restore this integration route's prior work origin for its remaining cases.
	t.check(book.request_open(str(app.session.definition.id)),"HIL restores test work origin")
	await t.settled()

static func without_session(t: SceneTree) -> void:
	var app = t.book.app
	click(t,app.help_panel.buttons[2])
	await t.frames(4)
	t.check(app.help_panel.chapter == 2 and app.session == null and app.sessions.is_empty(),"HIL direct operation without any session")
