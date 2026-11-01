extends RefCounted
## Finite N18-N21 proof: ten real pointer routes, cheap state variants, native ink.
var p: SceneTree
var book: Node3D
var app: Control
var rows: Dictionary = {"routes":[],"layouts":[],"interruptions":[],"logic":[],"settings":{}}

func frames(count: int = 1) -> void: await p.frames(count)

func settled() -> void:
	while book.state in [book.State.PREPARING,book.State.OPENING] or book.release_barrier: await p.process_frame
	await frames()

func click(control: Control) -> void:
	p.check(control.is_visible_in_tree() and Rect2(Vector2.ZERO,Vector2(p.root.size)).encloses(control.get_global_rect()),"N05 visible pointer target "+str(control.name))
	var point: Vector2 = control.get_global_rect().get_center()
	p.button(true,point)
	p.button(false,point)

func target_control(destination: String) -> Control:
	if book.state == book.State.INFORMATION:
		if destination in ["catalog","work","ending"]: return app.actions["nav-work"] if app.info.section == "settings" else app.info.right_return
		return app.information.get_node("help-access" if destination == "help" else "settings-access")
	if book.state == book.State.WORK: return app.actions["menu" if destination == "settings" else "help"]
	for child: Node in app.album.find_children("*","Button",true,false):
		if child.text == ("Hilfe" if destination == "help" else "Einstellungen / Info"): return child
	return null

func camera() -> Array:
	return [book.camera.position.x,book.camera.position.y,book.camera.size]

func route(source: String, destination: String) -> void:
	var before: Array = p.fingerprint()
	var before_view: Dictionary = app.board.capture_view().duplicate(true)
	var old_return: Dictionary = book.return_context.duplicate(true)
	var start: Array = camera()
	click(target_control(destination))
	p.check(book.state == book.State.PREPARING,"N05 synchronous bind "+source+"/"+destination)
	var origin: Dictionary = book.information_routes.origin.duplicate(true)
	var expected_origin: String = source if source in ["catalog","work","ending"] else str(origin.kind)
	p.check(origin.kind == expected_origin and origin.id == app.session.definition.id,"N05 immutable origin "+source+"/"+destination)
	var samples: Array = []
	var leaves: int = 0
	var midpoint: bool = false
	while book.state in [book.State.PREPARING,book.State.OPENING]:
		if book.state == book.State.OPENING:
			leaves = maxi(leaves,book.resource_report().visible_leaves)
			samples.append([book.elapsed,camera(),book.leaf_material.get_shader_parameter("turn")])
			if not midpoint and book.motion_kind == "info-pan" and book.elapsed >= 0.30:
				midpoint = true
				await p.screenshot("info-pan-"+destination+"-middle",true)
		await p.process_frame
	await settled()
	var kind: String = "pan" if source in ["settings","help"] and destination in ["settings","help"] else "enter" if destination in ["settings","help"] else "return"
	var destination_ok: bool = app.information.visible and app.info.section == destination if destination in ["settings","help"] else app.album.visible if destination == "catalog" else app.ending.visible if destination == "ending" else app.work.visible
	p.check(destination_ok and p.fingerprint() == before and book.return_context == old_return,"N05 exact target and untouched work "+source+"/"+destination)
	p.check(not app.title.visible if app.information.visible else app.title.visible,"N05 global information title removed "+source+"/"+destination)
	p.check(app.board.capture_view() == before_view,"N05 work tool color zoom and clue reads unchanged "+source+"/"+destination)
	p.check(book.capture == null and book.information_routes.textures.is_empty(),"N05 transient release "+source+"/"+destination)
	rows.routes.append({"source":source,"target":destination,"kind":kind,"direction":book.direction,"seconds":book.elapsed,"wall_seconds":book.motion_wall_seconds,
		"start":start,"end":camera(),"samples":samples,"leaves":leaves,"origin":origin,"id":str(app.session.definition.id),
		"catalog_after":book.context(),"view_before":before_view,"view_after":app.board.capture_view(),"state_unchanged":p.fingerprint() == before,"return_context_unchanged":book.return_context == old_return})

func force_open() -> void:
	if book.state == book.State.INFORMATION:
		book.information_routes.request_return()
		book.interrupt("focus")
		await settled()
	app.show_album()
	await settled()
	book.request_open("T-06")
	book.interrupt("focus")
	await settled()

func run(proof: SceneTree) -> Dictionary:
	p = proof
	book = p.study
	app = book.app
	p.root.size = Vector2i(1920,1080)
	book.set_ui_scale(1.0)
	await force_open()
	var player = app.session.player
	var previous: int = player.cells[0]
	p.check(player.commit([{"index":0,"before":previous,"after":0 if previous != 0 else 1}]) and player.undo() and player.cursor > 0 and player.cursor < player.history.size(),"N05 begun work has undo and redo history")
	app.refresh()
	app.board.active_color = 4
	app.set_tool("erase")
	app.board.zoom(-1,app.board.view.viewport.get_center())
	app.board.set_clue_step("row",0,3)
	app.board.set_clue_step("column",0,2)
	app.session.view_state = app.board.capture_view()
	p.check(not app.actions.has("nav-album") and app.album_button.get_parent() == app.page,"N05 old tab removed including signal and focus")
	p.check(app.album_button.position.x < app.actions.menu.position.x and app.actions.menu.position.x < app.actions.help.position.x,"N05 work navigation order catalog settings help")
	await route("work","settings")
	await route("settings","work")
	await route("work","help")
	await route("help","work")
	app.show_album()
	app.album.choose_sort("size")
	app.album.reverse_sort()
	app.album.commit_page(0,91,173)
	app.album.selected_id = "T-08"
	await settled()
	var writes: int = app.store.writes
	await route("catalog","settings")
	await route("settings","help")
	await route("help","settings")
	await route("settings","catalog")
	await route("catalog","help")
	await route("help","catalog")
	p.check(app.store.writes == writes,"N05 catalog placeholder never creates save obligation")
	var catalog_origin: Dictionary = book.context().duplicate(true)
	for destination: String in ["help","settings","catalog"]:
		click(target_control(destination))
		book.interrupt("focus")
		await settled()
	p.check(book.context() == catalog_origin and app.store.writes == writes,"N05 catalog help settings returns original context without saves")
	for sample: Dictionary in rows.routes:
		if sample.target == "catalog":
			p.check(sample.catalog_after == sample.origin.catalog,"N05 exact unequal catalog offsets and selection "+sample.source)
	await layout_cases()
	await settings_cases()
	await interruption_cases()
	await handoff_cases()
	# Leave the shared verifier in its ordinary stable catalog context.
	app.show_album()
	app.album.choose_category("")
	app.album.choose_sort("category")
	book.set_ui_scale(1.0)
	p.root.size = Vector2i(1920,1080)
	await settled()
	return rows

func layout_cases() -> void:
	for configuration: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1200,1.0]]:
		p.root.size = Vector2i(configuration[0],configuration[1])
		book.set_ui_scale(configuration[2])
		await settled()
		book.information_routes.request("settings")
		book.interrupt("focus")
		await settled()
		for section: String in ["settings","help"]:
			if section != app.info.section:
				book.information_routes.request(section)
				book.interrupt("focus")
				await settled()
			var scroll: ScrollContainer = app.info_scroll if section == "settings" else app.info.help_scroll
			var panel: Control = app.settings_panel if section == "settings" else app.help_panel
			var suffix: String = "%dx%d" % [p.root.size.x,p.root.size.y]
			await p.screenshot("info-"+section+"-"+suffix,true)
			# Actual wheel path to the complete bottom, with a finite event bound.
			for i: int in range(40): p.button(true,scroll.get_global_rect().get_center(),MOUSE_BUTTON_WHEEL_DOWN)
			await frames()
			var bar: VScrollBar = scroll.get_v_scroll_bar()
			p.check(scroll.scroll_vertical == maxi(0,int(bar.max_value-bar.page)),"N05 complete scroll end "+section+"/"+suffix)
			p.check(panel.get_global_rect().end.y <= scroll.get_global_rect().end.y+1,"N05 final content reachable "+section+"/"+suffix)
			var old: Vector2i = app.info.positions()
			p.check(not book.information_routes.request(section) and app.info.positions() == old,"N05 same page no-op "+section+"/"+suffix)
			var hidden: ScrollContainer = app.info.help_scroll if section == "settings" else app.info_scroll
			p.check(not hidden.is_visible_in_tree(),"N05 offscreen controls cannot receive focus "+section+"/"+suffix)
			await p.screenshot("info-"+section+"-bottom-"+suffix,true)
			await ink(section,scroll,suffix)
		var offsets: Vector2i = app.info.positions()
		book.information_routes.request("settings")
		book.interrupt("focus")
		await settled()
		p.check(app.info.positions() == offsets,"N05 both information offsets survive pan %s" % [configuration])
		book.information_routes.request_return()
		book.interrupt("focus")
		await settled()

func ink(section: String, scroll: ScrollContainer, suffix: String) -> void:
	var viewport := SubViewport.new()
	viewport.size = p.root.size
	viewport.disable_3d = true
	viewport.transparent_bg = true
	viewport.gui_disable_input = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	p.root.add_child(viewport)
	app.reparent(viewport,false)
	await frames()
	var image: Image = viewport.get_texture().get_image()
	var hull: Rect2i = image.get_used_rect()
	var paper: Rect2 = book.projected_information(-1 if section == "settings" else 1)
	var safe: Rect2 = paper
	if section == "help": safe.position.x += paper.size.x*0.075
	safe.size.x -= paper.size.x*0.075
	var margin: float = minf(minf(hull.position.x-safe.position.x,safe.end.x-hull.end.x),minf(hull.position.y-safe.position.y,safe.end.y-hull.end.y))
	p.check(hull.has_area() and margin >= 8,"N05 actual information ink margin "+section+"/"+suffix)
	var file: String = "info-"+section+"-ink-"+suffix+".png"
	p.check(image.save_png(p.output.path_join(file)) == OK,"N05 native ink image "+file)
	var clip: Rect2 = scroll.get_global_rect()
	rows.layouts.append({"section":section,"width":p.root.size.x,"height":p.root.size.y,"scale":app.ui_scale,"file":file,
		"hull":[hull.position.x,hull.position.y,hull.size.x,hull.size.y],"margin":margin,"clip":[clip.position.x,clip.position.y,clip.size.x,clip.size.y],
		"scroll":scroll.scroll_vertical,"limit":maxi(0,int(scroll.get_v_scroll_bar().max_value-scroll.get_v_scroll_bar().page))})
	app.reparent(book,false)
	viewport.queue_free()
	await frames()

func settings_cases() -> void:
	p.root.size = Vector2i(1920,1080)
	book.set_ui_scale(1.0)
	await force_open()
	var before: Array = p.fingerprint()
	click(target_control("settings"))
	book.interrupt("focus")
	await settled()
	for expected: float in [1.25,1.0]:
		click(app.ui_scale_button)
		await frames()
		p.check(app.ui_scale == expected,"N05 actual UI toggle %s" % expected)
	# Native popup selection, then ordinary checkbox signals.
	click(app.view_choice)
	await frames()
	var popup: PopupMenu = app.view_choice.get_popup()
	p.check(popup.visible,"N05 native settings popup opens")
	var row_height: float = (popup.size.y-18*app.ui_scale)/2.0
	var point: Vector2 = Vector2(popup.position)+Vector2(popup.size.x/2.0,9*app.ui_scale+row_height*1.5)
	p.button(true,point)
	p.button(false,point)
	await frames()
	click(app.clue_completion_toggle)
	click(app.animation_toggle)
	click(app.clue_reset_button)
	await frames()
	p.check(app.board.row_clue_reads.all(func(r: Dictionary) -> bool: return r == app.board.ClueLayout.grid_end_position()) and app.board.column_clue_reads.all(func(r: Dictionary) -> bool: return r == app.board.ClueLayout.grid_end_position()),"N05 explicit clue reset remains effective")
	rows.settings = {"mode":app.board.mode,"mark":app.board.mark_completed_clues,"animations":app.animation_toggle.button_pressed,"ui":app.ui_scale}
	p.check(rows.settings == {"mode":"V","mark":false,"animations":false,"ui":1.0},"N05 actual controls change settings")
	click(target_control("help"))
	book.interrupt("focus")
	await settled()
	click(target_control("work"))
	book.interrupt("focus")
	await settled()
	p.check(p.fingerprint() == before and app.board.mode == "V" and not app.board.mark_completed_clues and not app.animation_toggle.button_pressed,"N05 explicit settings survive work return")
	# The study's real memory-store failure takes the same mandatory flush path.
	app.store.failure = "synthetic N05 failure"
	app.slot_errors[app.sessions.find(app.session)] = app.store.failure
	var token: int = book.generation
	p.check(not book.information_routes.request("help") and book.state == book.State.WORK and token == book.generation,"N05 failed mandatory flush blocks preparation")
	app.store.failure = ""
	app._save_current()
	app.set_puzzle_view(0)
	app.set_clue_completion(true)
	app.animation_toggle.set_pressed_no_signal(true)
	app.board.set_animations(true)
	# Stable completion reopens directly, without replaying its success sequence.
	var snapshot: Dictionary = app.store.snapshot(app.session,app.board.capture_view())
	var changes: Array[Dictionary] = []
	for y: int in range(app.session.player.height):
		for x: int in range(app.session.player.width):
			var index: int = y*app.session.player.width+x
			var value: int = app.session.definition.solution[y][x]
			if app.session.player.cells[index] != value: changes.append({"index":index,"before":app.session.player.cells[index],"after":value})
	app.session.player.commit(changes)
	app.session.completed = app.session.is_solution()
	app.open_puzzle()
	await frames()
	book.information_routes.request("help")
	p.check(book.information_routes.origin.kind == "ending","N05 stable completion origin")
	book.interrupt("focus")
	await settled()
	book.information_routes.request_return()
	book.interrupt("leave")
	await settled()
	p.check(app.ending.visible and not app.reveal_view.active,"N05 completion return never replays success")
	app.SaveStore.apply(snapshot,app.session)
	app.open_puzzle()

func interruption_cases() -> void:
	for kind: String in ["enter","pan","return"]:
		for phase: String in ["prepare","motion"]:
			await force_open()
			if kind != "enter":
				book.information_routes.request("settings")
				book.interrupt("focus")
				await settled()
			var before: Array = p.fingerprint()
			var origin: Dictionary = book.return_context.duplicate(true)
			if kind == "return": book.information_routes.request_return()
			else: book.information_routes.request("help")
			var token: int = book.generation
			p.check(not book.information_routes.request("settings") and not book.request_return(),"N05 moving commands discarded "+kind+"/"+phase)
			if phase == "motion":
				while book.state == book.State.PREPARING: await p.process_frame
				while book.elapsed < 0.15: await p.process_frame
			p.button(true,Vector2(600,400))
			p.button(true,Vector2(600,400),MOUSE_BUTTON_WHEEL_DOWN)
			var reason: String = "leave" if phase == "prepare" else "resize" if kind == "enter" else "ui-scale" if kind == "pan" else "focus"
			if reason == "leave":
				var event := InputEventKey.new()
				event.keycode = KEY_ESCAPE
				event.pressed = true
				p.root.push_input(event,true)
			elif reason == "resize": p.root.size += Vector2i(8,0)
			elif reason == "ui-scale": book.set_ui_scale(1.25)
			else: book._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
			await frames()
			var held_blocked: bool = book.release_barrier and not app.session.gesture.active
			p.check(held_blocked,"N05 held press remains blocked "+kind+"/"+phase)
			p.button(false,Vector2(600,400))
			await settled()
			var endpoint: String = app.info.section if book.state == book.State.INFORMATION else "work"
			var expected: String = "work" if kind == "return" or (kind == "enter" and reason == "leave") else "settings" if kind == "pan" and reason == "leave" else "help"
			p.check(endpoint == expected and book.generation > token and p.fingerprint() == before and book.return_context == origin,"N05 interruption result "+kind+"/"+phase)
			rows.interruptions.append({"kind":kind,"phase":phase,"reason":reason,"endpoint":endpoint,"held_blocked":held_blocked,"released":not book.release_barrier,"textures":book.information_routes.textures.size()})
			p.root.size = Vector2i(1920,1080)
			book.set_ui_scale(1.0)
			await frames()
	# Exhaust the decision table without rendering 24 redundant transitions.
	for kind: String in ["enter","pan","return"]:
		for phase: String in ["prepare","motion"]:
			for reason: String in ["resize","ui-scale","focus","leave"]:
				var source: String = "work" if kind == "enter" else "settings"
				var target: String = "work" if kind == "return" else "help"
				var endpoint: String = book.information_routes.endpoint(source,target,"info-"+kind,reason != "leave")
				p.check(endpoint == (source if reason == "leave" and kind != "return" else target),"N05 cheap interruption table "+kind+"/"+phase+"/"+reason)
				rows.logic.append({"kind":kind,"phase":phase,"reason":reason,"endpoint":endpoint})

func handoff_cases() -> void:
	await force_open()
	for destination: String in ["settings","help","work","catalog"]:
		if destination == "catalog":
			app.show_album()
			await settled()
			book.information_routes.request("help")
			book.interrupt("focus")
			await settled()
		if destination in ["work","catalog"]: book.information_routes.request_return()
		else: book.information_routes.request(destination)
		while book.state == book.State.PREPARING: await p.process_frame
		book.set_process(false)
		book._pose(1)
		await p.screenshot("info-handoff-texture-"+destination)
		book._settle(true)
		book.set_process(true)
		await p.screenshot("info-handoff-direct-"+destination)
		p.handoffs.append({"configuration":[p.root.size,app.ui_scale],"texture":"info-handoff-texture-"+destination+".png","direct":"info-handoff-direct-"+destination+".png"})
		await settled()
