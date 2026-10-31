extends SceneTree
## Finite B-A native proof. Actual renderer and pointer dispatch, synthetic inputs.
const Study = preload("res://study/book/main.gd")
const Main = preload("res://ui/main.gd")
const Current = preload("res://tests/current_visual_cases.gd")
var study: Study
var checks: int = 0
var failures: Array[String] = []
var output: String
var layouts: Array = []
var handoffs: Array = []
var assertions: Array = []
var catalog_layouts: Array = []
var page_motions: Array = []
var interruptions: Array = []
var ink_margins: Array = []
var returns: Array = []
var tooltip_cases: Array = []

class Baseline extends Main:
	func create_store() -> SaveStore: return Study.Content.MemoryStore.new()
	func puzzle_definitions() -> Array[Dictionary]:
		var result: Array[Dictionary] = []
		var input: Dictionary = Study.Content.Inputs.read()
		Registry.cached = input.registry
		for data: Dictionary in input.definitions: result.append(data)
		return result
	func validate_definition(data: Dictionary) -> String:
		return Definition.validate(data, {data.id: data.reveal.image})

func _initialize() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	assertions.append({"label":label,"passed":ok})
	if not ok:
		failures.append(label)
		print("BOOK_STUDY_FAIL ", label)

func frames(count: int = 3) -> void:
	for i: int in range(count): await process_frame
	await RenderingServer.frame_post_draw

func screenshot(name: String, already_drawn: bool = false) -> Image:
	if not already_drawn: await frames()
	var image: Image = root.get_texture().get_image()
	check(image.save_png(output.path_join(name+".png")) == OK, "native framebuffer " + name)
	return image

func fingerprint() -> Array:
	var result: Array = []
	for s: RefCounted in study.app.sessions:
		result.append([s.player.cells.duplicate(), s.player.history.duplicate(true), s.player.cursor, s.player.undo_used, s.completed])
	return result

func geometry(app: Control) -> Array:
	return [app.board.get_rect(), app.board.view.bounds(), app.board.view.cell_size,
		app.board.fit_ceiling, app.board.type_size, app.board.slot_pitch,
		app.board.reserve_slots, app.board.composition_envelope(), app.mini.get_rect(),
		app.palette_row.get_rect(), app.tools_scroll.get_rect()]

func button(down: bool, point: Vector2, index: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var event := InputEventMouseButton.new()
	event.position = point
	event.button_index = index
	event.pressed = down
	root.push_input(event, true)

func no_spoiler(image: Image, label: String) -> void:
	var data: PackedByteArray = image.get_data()
	var found: bool = false
	for i: int in range(0, data.size()-4, 64):
		if data[i] > 175 and data[i+1] < 85 and data[i+2] > 150:
			found = true
			break
	check(not found, "no synthetic magenta reveal in " + label)
	check(not "VERBORGENER" in study.app.title.text, "neutral work title " + label)
	check(study.app.reveal_view.artwork == null and not study.app.ending.visible, "no earned ending " + label)

func prepare_open(id: String) -> void:
	study.app.show_album()
	await frames()
	check(study.request_open(id), "ID-bound opening accepted " + id)
	check(not study.request_open("T-01"), "repeated request is discarded")
	while study.state == Study.State.PREPARING: await process_frame
	check(study.state == Study.State.OPENING, "actual texture preparation completes")

func run() -> void:
	output = OS.get_environment("BOOK_STUDY_OUTPUT")
	if output.is_empty(): quit(4); return
	root.gui_embed_subwindows = true
	root.size = Vector2i(1920, 1080)
	study = Study.new()
	root.add_child(study)
	await frames(6)
	if OS.get_cmdline_user_args().has("--movie"):
		await movie()
		return
	check(study.app.sessions.size() == 27, "three synthetic shapes with 27 fixed catalog IDs")
	fixture_cases()
	await control_cases()
	tooltip_cases = await preload("res://study/book/tooltip_cases.gd").new().run(self)
	var before: Array = fingerprint()
	var writes_before: int = study.app.store.writes
	var start: Image = await screenshot("catalog")
	no_spoiler(start, "catalog")
	await catalog_cases()
	# Real pointer activation through the existing catalog card.
	var card: Control = study.app.album.choices[1]
	var point: Vector2 = card.get_global_rect().get_center()
	button(true, point)
	button(false, point)
	await frames(1)
	check(study.selected_id == "T-06", "actual catalog pointer selects correct ID")
	check(not study.request_open("T-08"), "no queued second selection")
	while study.state == Study.State.PREPARING: await process_frame
	var mid_saved: bool = false
	var late_saved: bool = false
	while study.state == Study.State.OPENING:
		if study.elapsed > 1.0 and not mid_saved:
			mid_saved = true
			var turns: Array = study.leaves.map(func(sheet: MeshInstance3D) -> float: return sheet.material_override.get_shader_parameter("turn"))
			check(study.resource_report().visible_leaves == 3 and turns[0] > turns[1] and turns[1] > turns[2],"three independently moving leaves")
			no_spoiler(await screenshot("opening-middle"), "moving front")
			button(true, Vector2(500, 400))
			button(false, Vector2(500, 400))
		if study.elapsed > 1.9 and not late_saved:
			late_saved = true
			no_spoiler(await screenshot("opening-back"), "blank underside")
		await process_frame
	check(study.elapsed == 3.0 and study.motion_wall_seconds >= 2.8, "natural total three-second movement")
	check(fingerprint() == before, "motion and blocked pointer input preserve cells/history/redo")
	check(study.app.store.writes == writes_before, "presentation creates no save action")
	var motion_ms: Array[float] = study.frames_ms.duplicate()
	var motion_wall: float = study.motion_wall_seconds
	# Quiet measurement excludes screenshot readback/PNG work from frame times.
	await prepare_open("T-06")
	while study.state == Study.State.OPENING: await process_frame
	var quiet_ms: Array[float] = study.frames_ms.duplicate()
	var quiet_wall: float = study.motion_wall_seconds
	var baseline := Baseline.new()
	baseline.size = Vector2(root.size)
	root.add_child(baseline)
	baseline.hide()
	baseline.process_mode = Node.PROCESS_MODE_DISABLED
	await frames()
	for index: int in range(3):
		var configuration: Array = Current.CONFIGURATIONS[index]
		root.size = configuration[0]
		study.set_ui_scale(configuration[1])
		baseline.size = Vector2(configuration[0])
		baseline.set_ui_scale(configuration[1])
		var id: String = ["T-01", "T-06", "T-08"][index]
		baseline.select_puzzle(index)
		await prepare_open(id)
		# Controlled final pose checks the SAME actual viewport/material against
		# direct UI, separately from the unaccelerated motion above.
		study.set_process(false)
		study._pose(1)
		var textured: Image = await screenshot("handoff-texture-%d" % configuration[0].x)
		var expected: Array = geometry(baseline)
		check(geometry(study.app) == expected, "unchanged regular fit/font/slot/control geometry " + id)
		study._settle(true)
		study.set_process(true)
		var direct: Image = await screenshot("work-%d" % configuration[0].x)
		no_spoiler(direct, "stable " + id)
		check(geometry(study.app) == expected, "handoff preserves geometry " + id)
		check(study.app.board.layout_valid, "valid fit " + id)
		check(study.app.board.view.cell_size <= 24.0, "small raster preserves zoom wish " + id)
		await measure_ink(true)
		study.app.hide()
		study.hide()
		baseline.show()
		var original_image: Image = await screenshot("baseline-%d" % configuration[0].x)
		for control: Control in study.app.palette_row.get_children():
			var center := Vector2i(control.get_global_rect().get_center())
			check(original_image.get_pixelv(center) == direct.get_pixelv(center),"unchanged original swatch pixel %s/%s" % [id,control.name])
		if configuration[0].x == 1920:
			check(original_image.get_region(Rect2i(1780,0,140,1080)).save_png(output.path_join("material-original-detail.png")) == OK,"original material native detail")
			check(direct.get_region(Rect2i(0,0,140,1080)).save_png(output.path_join("material-study-detail.png")) == OK,"revised material native detail")
		baseline.hide()
		study.show()
		study.app.show()
		layouts.append({"configuration": configuration, "id": id, "geometry": expected})
		var bounds := Rect2i(study.app.board.position+study.app.board.view.bounds().position, study.app.board.view.bounds().size)
		# Preserve original full-resolution pairs for independent pixel inspection.
		handoffs.append({"configuration": configuration, "board_pixels": bounds, "texture": "handoff-texture-%d.png" % configuration[0].x, "direct": "work-%d.png" % configuration[0].x})
		var report: Dictionary = study.resource_report()
		check(report.ui_capture_targets == 0 and report.catalog_rgba_textures == 0, "transient textures released " + id)
	baseline.free()
	await return_cases()
	await interruption_cases()
	# Existing popups and gestures are cancelled before a page can move.
	study.app.show_album()
	await frames()
	study.app.album.sort_choice.show_popup()
	await frames()
	check(study.app.album.sort_choice.get_popup().visible, "actual regular popup opened")
	check(study.request_open("T-06"), "open dismisses popup before capture")
	check(not study.app.album.sort_choice.get_popup().visible, "no global popup bypasses input lock")
	button(true, Vector2(400, 300), MOUSE_BUTTON_WHEEL_UP)
	check(study.release_barrier and study.app.process_mode == Node.PROCESS_MODE_DISABLED, "preparing input remains locked")
	study.interrupt("focus")
	await frames()
	check(not study.release_barrier, "wheel event cannot leave a held-button lock")
	var gesture_cells: Array = fingerprint()
	var start_cell: Vector2 = study.app.board.global_position+study.app.board.view.origin+Vector2(5.5, 5.5)*study.app.board.view.cell_size
	button(true, start_cell)
	check(study.app.session.gesture.active, "actual cell gesture exists before leaving")
	study.app.show_album()
	button(false, start_cell)
	await frames()
	check(not study.app.session.gesture.active and fingerprint() == gesture_cells, "leaving cancels gesture without commit")
	# Interrupted preparation and movement: stale awaits cannot restore old pages.
	for reason: String in ["resize", "ui-scale", "focus", "leave"]:
		study.app.show_album()
		await frames()
		var cells: Array = fingerprint()
		check(study.request_open("T-06"), "interruption starts " + reason)
		var token: int = study.generation
		if reason == "resize": root.size += Vector2i(8,0)
		elif reason == "ui-scale": study.set_ui_scale(1.0)
		elif reason == "focus": study._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
		else:
			study.interrupt("leave")
			study.app.show_album()
		await frames(8)
		check(study.generation > token and study.state == (Study.State.CATALOG if reason == "leave" else Study.State.WORK), "stable interrupted end state " + reason)
		check(study.capture == null and (not study.leaf.visible or study.leaf_material.get_shader_parameter("turn") == 1.0), "no half leaf or stale viewport " + reason)
		check(fingerprint() == cells, "interruption has no cell/history effect " + reason)
		check(not study.release_barrier, "input barrier eventually releases " + reason)
	await prepare_open("T-01")
	button(true, Vector2(400, 300))
	study.interrupt("focus")
	await frames()
	check(study.release_barrier and study.app.process_mode == Node.PROCESS_MODE_DISABLED, "held blocked button cannot become a gesture")
	var cell_point: Vector2 = study.app.board.global_position+study.app.board.view.origin+Vector2(5.5, 5.5)*study.app.board.view.cell_size
	button(false, cell_point)
	await frames()
	check(not study.release_barrier and not study.app.session.gesture.active, "consumed release cannot commit")
	var old_cursor: int = study.app.session.player.cursor
	button(true, cell_point)
	button(false, cell_point)
	await frames()
	check(study.app.session.player.cursor == old_cursor+1, "fresh actual pointer gesture works after interruption")
	await solved_reset_case()
	var report: Dictionary = {"checks": checks, "assertions":assertions, "failures": failures, "layouts": layouts, "handoffs": handoffs,
		"catalog_layouts":catalog_layouts,"page_motions":page_motions,"interruptions":interruptions,
		"ink_margins":ink_margins,"returns":returns,"tooltip_cases":tooltip_cases,
		"resources": study.resource_report(), "motion_frame_ms_with_captures": motion_ms, "motion_wall_seconds_with_captures": motion_wall,
		"motion_frame_ms_quiet": quiet_ms, "motion_wall_seconds_quiet": quiet_wall,
		"engine": Engine.get_version_info(), "display": DisplayServer.get_name(), "adapter": RenderingServer.get_video_adapter_name(),
		"renderer": RenderingServer.get_current_rendering_method(), "logical_window": root.size,
		"screen_size": DisplayServer.screen_get_size(), "screen_scale": DisplayServer.screen_get_scale(), "screen_dpi": DisplayServer.screen_get_dpi()}
	var file := FileAccess.open(output.path_join("native.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t")+"\n")
	file.close()
	study.free()
	print("BOOK_STUDY_OK checks=", checks, " failures=", failures.size())
	quit(0 if failures.is_empty() else 4)

func movie() -> void:
	await frames(12)
	var events: Array = []
	for target: int in [1,0]:
		var begin: int = Engine.get_frames_drawn()
		check(study.request_page(target),"movie page accepted")
		while study.state in [Study.State.PREPARING,Study.State.OPENING]: await process_frame
		events.append(movie_event("page",begin))
		await frames(12)
	var begin: int = Engine.get_frames_drawn()
	await prepare_open("T-06")
	while study.state == Study.State.OPENING: await process_frame
	events.append(movie_event("open",begin))
	await frames(15)
	var point: Vector2 = study.app.board.global_position+study.app.board.view.origin+Vector2(5.5,5.5)*study.app.board.view.cell_size
	button(true,point)
	button(false,point)
	await frames(15)
	var edited_cursor: int = study.app.session.player.cursor
	begin = Engine.get_frames_drawn()
	var tab: Vector2 = study.app.album_button.get_global_rect().get_center()
	button(true,tab)
	button(false,tab)
	while study.state in [Study.State.PREPARING,Study.State.OPENING]: await process_frame
	events.append(movie_event("return",begin))
	await frames(15)
	check(study.state == Study.State.CATALOG and study.app.session.player.cursor == edited_cursor,"movie returns edited content to catalog")
	await screenshot("movie-final")
	var file := FileAccess.open(output.path_join("movie.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"fps":30,"events":events,"final_state":"CATALOG","final_id":str(study.app.session.definition.id),"edited_cursor":edited_cursor,"failures":failures})+"\n")
	file.close()
	print("BOOK_STUDY_MOVIE_OK total=", study.elapsed, " fixed_fps=30 native_motion_separately_measured=true")
	# Keep the settled scene alive through the engine's final recorded frame.
	quit(0 if failures.is_empty() else 4)

func movie_event(kind: String, begin: int) -> Dictionary:
	return {"kind":kind,"direction":study.direction,"seconds":study.elapsed,"first_frame":begin,"last_frame":Engine.get_frames_drawn(),"preparation_seconds":study.preparation_seconds,"capture_motion_wall_seconds":study.motion_wall_seconds,"frame_ms":study.frames_ms.duplicate()}

func catalog_cases() -> void:
	for configuration: Array in Current.CONFIGURATIONS:
		root.size = configuration[0]
		study.set_ui_scale(configuration[1])
		await frames(6)
		var catalog = study.app.album
		var paper_top: float = root.size.y*(1.0-12.4/study.view_rect(false).w)/2.0
		check(study.app.title.position.y >= paper_top and study.app.title.get_rect().end.y <= catalog.position.y,"catalog heading stays inside paper and above controls %d" % configuration[0].x)
		check(catalog.choices.size() == 24 and catalog.grid.get_child_count() == 12 and catalog.right_grid.get_child_count() == 12,"24 active cards distributed over both pages %s" % configuration[0])
		var fold: float = root.size.x/2.0
		var measurements: Array = []
		for i: int in range(catalog.choices.size()):
			var card = catalog.choices[i]
			var rect: Rect2 = card.get_global_rect()
			check(rect.end.x < fold-12 if i < 12 else rect.position.x > fold+12,"card outside gutter %d/%d" % [configuration[0].x,i])
			check(card.size.x >= card.minimum_card_width(catalog.ui_scale) and card.image_area.size.y >= 112*catalog.ui_scale and card.reset.size.x >= 44*catalog.ui_scale,"unreduced card budgets %d/%d" % [configuration[0].x,i])
			check(card.caption.text == "???" and card.picture.payload.is_empty() and card.preview.cells == catalog.items[catalog.visible_ids[i]].player.cells,"neutral card and own cells %d/%d" % [configuration[0].x,i])
			measurements.append({"id":catalog.visible_ids[i],"rect":rect,"image":card.image_area,"font":card.detail.get_theme_font_size("font_size"),"reset":card.reset.size})
		catalog_layouts.append({"configuration":configuration,"cards":measurements,"left_scroll":catalog.scroll.get_global_rect(),"right_scroll":catalog.right_scroll.get_global_rect()})
		no_spoiler(await screenshot("catalog-%d" % configuration[0].x),"spread %d" % configuration[0].x)
		await measure_ink(false)
	root.size = Vector2i(1920,1080)
	study.set_ui_scale(1.0)
	await frames()
	var catalog = study.app.album
	var original: Array = catalog.visible_ids.duplicate()
	for target: int in [1,0]:
		var control: Control = catalog.next_button if target == 1 else catalog.previous_button
		button(true,control.get_global_rect().get_center())
		button(false,control.get_global_rect().get_center())
		check(study.state == Study.State.PREPARING,"pointer starts catalog turn %d" % target)
		check(not study.request_page(target) and not study.request_open("T-06"),"turn discards repeated selection %d" % target)
		catalog.choose_sort("size")
		catalog.choose_category("technical")
		catalog.reverse_sort()
		check(catalog.category_id.is_empty() and catalog.preference.criterion == "category" and catalog.preference.direction == "asc","filter and sort discarded during turn %d" % target)
		while study.state == Study.State.PREPARING: await process_frame
		while study.elapsed < 0.30: await process_frame
		no_spoiler(await screenshot("page-forward" if target == 1 else "page-backward"),"catalog leaf %d" % target)
		while study.state == Study.State.OPENING: await process_frame
		await frames()
		page_motions.append({"target":target,"direction":study.direction,"seconds":study.elapsed,"wall_seconds":study.motion_wall_seconds,"preparation_seconds":study.preparation_seconds})
		check(catalog.page_index == target and study.elapsed == Study.PAGE_DURATION,"short catalog motion settles target %d" % target)
		check(catalog.choices.size() == (3 if target == 1 else 24),"partial last spread %d" % target)
		check(catalog.visible_ids == (catalog.filtered_ids.slice(24) if target == 1 else original),"global ordering precedes pagination %d" % target)
		var token: int = study.generation
		catalog.turn_page(1 if target == 1 else -1)
		check(study.generation == token and study.state == Study.State.CATALOG,"edge action has no animation %d" % target)
	# Pointer routes on both page halves must select their bound ID.
	for i: int in [0,12]:
		var id: String = catalog.visible_ids[i]
		var point: Vector2 = catalog.choices[i].get_global_rect().get_center()
		button(true,point)
		button(false,point)
		check(study.selected_id == id and study.state == Study.State.PREPARING,"correct ID from page half %d" % i)
		study.interrupt("leave")
		await frames(6)
	var token: int = study.generation
	catalog.choose_category("missing-synthetic-category")
	await frames()
	check(catalog.choices.is_empty() and catalog.empty_message.visible and study.generation == token,"empty filter is immediate and reachable")
	var actions: Control = catalog.next_button.get_parent().get_child(0)
	check(actions.is_visible_in_tree() and actions.get_child_count() == 2 and not catalog.next_button.visible,"empty filter retains settings and quit")
	catalog.choose_category("")
	catalog.choose_sort("size")
	await frames()
	check(study.generation == token and catalog.page_index == 0 and catalog.filtered_ids[0] == "T-01","sort is global and immediate")
	catalog.choose_sort("category")
	await frames()

func solved_reset_case() -> void:
	study.app.show_album()
	await frames()
	study.app.album.commit_page(1)
	await frames()
	var item = study.app.sessions[24]
	var id: String = item.definition.id
	var changes: Array[Dictionary] = []
	for y: int in range(item.player.height):
		for x: int in range(item.player.width):
			var index: int = y*item.player.width+x
			var value: int = int(item.definition.solution[y][x])
			if item.player.cells[index] != value: changes.append({"index":index,"before":item.player.cells[index],"after":value})
	item.player.commit(changes)
	item.completed = item.is_solution()
	var token: int = study.generation
	check(study.request_open(id),"solved selection accepted")
	await frames()
	check(study.state == Study.State.WORK and study.generation == token and study.app.ending.visible and not study.app.reveal_view.active,"solved puzzle opens directly without replay")
	check(item.reveal().definition_id == id and item.reveal().image == "res://study/book/art/t34.svg" and study.app.reveal_view.artwork != null,"copied ID on second spread has its earned reveal")
	check(study.request_return(),"stable ending accepts animated return")
	while study.state in [Study.State.PREPARING,Study.State.OPENING]: await process_frame
	await frames()
	check(study.app.album.page_index == 1 and study.app.album.visible_ids[0] == id and study.app.album.reveals[0].payload.image == item.reveal().image,"earned copied reveal returns to second spread")
	var reopened: bool = study.request_open(id)
	if not reopened: print("REOPEN_DIAGNOSTIC state=",study.state," barrier=",study.release_barrier," held=",study.held_buttons," physical=",Input.get_mouse_button_mask()," id=",id)
	check(reopened,"solved copied ID reopens directly")
	await frames()
	token = study.generation
	study.app._ask_reset_id(id,"ending")
	study.app._reset_selected()
	study.app.reset_dialog.hide()
	await frames()
	check(study.generation == token and study.app.work.visible and study.app.session.definition.id == id and study.app.session.player.cells.count(-1) == 400,"ending reset opens same empty page without book animation")

func interruption_cases() -> void:
	for kind: String in ["page","open","return"]:
		for phase: String in ["prepare","motion"]:
			for reason: String in ["resize","ui-scale","focus","leave"]:
				print("BOOK_MATRIX ",kind,"/",phase,"/",reason)
				study.app.show_album()
				study.app.album.commit_page(0,40)
				await frames(6)
				if kind == "return":
					check(study.request_open("T-06"),"matrix return setup")
					study.interrupt("focus")
					await frames(6)
				var source: Dictionary = study.context()
				var cells: Array = fingerprint()
				var writes: int = study.app.store.writes
				check(study.request_page(1) if kind == "page" else study.request_return() if kind == "return" else study.request_open("T-06"),"matrix request %s/%s/%s" % [kind,phase,reason])
				if phase == "motion":
					while study.state == Study.State.PREPARING: await process_frame
					await frames(2)
				var token: int = study.generation
				if reason == "leave":
					var escape := InputEventKey.new()
					escape.keycode = KEY_ESCAPE
					escape.pressed = true
					root.push_input(escape,true)
				else: study.interrupt(reason)
				await frames(6)
				var expected_work: bool = kind == "open" and reason != "leave"
				check(study.state == (Study.State.WORK if expected_work else Study.State.CATALOG) and study.generation > token,"matrix stable target %s/%s/%s" % [kind,phase,reason])
				if not expected_work:
					check(study.app.album.page_index == (1 if reason != "leave" and kind == "page" else source.page),"matrix catalog target %s/%s/%s" % [kind,phase,reason])
					if reason == "leave": check(study.app.album.scroll_vertical == source.scroll and study.app.album.selected_id == source.selection,"retained catalog context %s/%s" % [kind,phase])
				check(fingerprint() == cells and study.app.store.writes == writes,"matrix no history or save %s/%s/%s" % [kind,phase,reason])
				check(study.capture == null and study.catalog_texture == null and study.resource_report().visible_leaves == 0,"matrix releases resources %s/%s/%s" % [kind,phase,reason])
				interruptions.append({"kind":kind,"phase":phase,"reason":reason,"state":study.state})

func fixture_cases() -> void:
	var input: Dictionary = Study.Content.Inputs.read()
	check(input.error.is_empty(),"normal registry and definition validators accept all 27 instances")
	for field: String in ["id","key","save_slot","definition","reveal"]:
		var bad: Dictionary = input.registry.duplicate(true)
		bad.entries[24][field] = bad.entries[0][field]
		check(not Study.Content.Inputs.validate(bad,input.definitions).is_empty(),"duplicate fixture binding rejected "+field)
	for field: String in ["id","definition_id","image"]:
		var bad: Array = input.definitions.duplicate(true)
		if field == "id": bad[24].id = bad[0].id
		else: bad[24].reveal[field] = bad[0].reveal[field]
		check(not Study.Content.Inputs.validate(input.registry,bad).is_empty(),"foreign fixture binding rejected "+field)

func measure_ink(work: bool) -> void:
	# Inspect real transparent-rendered glyph/contour alpha, including antialiasing.
	var viewport := SubViewport.new()
	viewport.size = root.size
	viewport.disable_3d = true
	viewport.transparent_bg = true
	viewport.gui_disable_input = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	study.app.reparent(viewport,false)
	await frames()
	var image: Image = viewport.get_texture().get_image()
	var controls: Array[Control] = [study.app.title]
	if work:
		controls.append(study.app.album_button)
		for id: String in ["help","menu","nav-information"]: controls.append(study.app.actions[id])
	else:
		controls.append(study.app.album.summary)
		for node: Node in study.app.album.find_children("*","Button",true,false):
			if node.is_visible_in_tree() and not study.app.album.scroll.is_ancestor_of(node) and not study.app.album.right_scroll.is_ancestor_of(node): controls.append(node)
	for control: Control in controls:
		var region := Rect2i(control.get_global_rect().grow(3)).intersection(Rect2i(Vector2i.ZERO,root.size))
		var hull := Rect2i()
		var found: bool = false
		for y: int in range(region.position.y,region.end.y):
			for x: int in range(region.position.x,region.end.x):
				if image.get_pixel(x,y).a > 0.01:
					var pixel := Rect2i(x,y,1,1)
					hull = hull.merge(pixel) if found else pixel
					found = true
		var side: int = 1 if work or control.get_global_rect().get_center().x > root.size.x/2.0 else -1
		var paper: Rect2 = study.projected_paper(work,side)
		var curve: float = 0.75*paper.size.x/10.0
		var safe: Rect2 = paper
		if side == 1: safe.position.x += curve
		safe.size.x -= curve
		var margin: float = minf(minf(hull.position.x-safe.position.x,safe.end.x-hull.end.x),minf(hull.position.y-safe.position.y,safe.end.y-hull.end.y))
		if not found or margin < 8: print("INK_DIAGNOSTIC ",control.name," width=",root.size.x," found=",found," margin=",margin," hull=",hull," safe=",safe)
		check(found and margin >= 8.0,"actual glyph and contour margin %s/%d/%s" % ["work" if work else "catalog",root.size.x,control.name])
		ink_margins.append({"view":"work" if work else "catalog","width":root.size.x,"control":str(control.name),"hull":[hull.position.x,hull.position.y,hull.size.x,hull.size.y],"paper":[paper.position.x,paper.position.y,paper.size.x,paper.size.y],"flat_safe":[safe.position.x,safe.position.y,safe.size.x,safe.size.y],"margin":margin})
	study.app.reparent(study,false)
	viewport.queue_free()
	await frames()

func control_cases() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(160,64)
	viewport.disable_3d = true
	viewport.transparent_bg = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var control = Main.BookButton.new()
	control.theme = study.app.theme
	control.text = "Probe"
	control.action_id = "study-state-proof"
	control.paper_transparent = true
	control.position = Vector2(5,5)
	control.size = Vector2(150,54)
	viewport.add_child(control)
	var names: Array[String] = ["normal","hover","pressed","selected","disabled","focus"]
	var strip := Image.create(160*names.size(),64,false,Image.FORMAT_RGBA8)
	var masks: Dictionary = {}
	for index: int in range(names.size()):
		control.disabled = false
		control.selected = false
		control.release_focus()
		var up := InputEventMouseButton.new()
		up.position = Vector2(80,32)
		up.button_index = MOUSE_BUTTON_LEFT
		up.pressed = false
		viewport.push_input(up,true)
		var move := InputEventMouseMotion.new()
		move.position = Vector2(80,32) if names[index] in ["hover","pressed"] else Vector2(159,63)
		viewport.push_input(move,true)
		if names[index] == "pressed":
			var down := InputEventMouseButton.new()
			down.position = Vector2(80,32)
			down.button_index = MOUSE_BUTTON_LEFT
			down.pressed = true
			viewport.push_input(down,true)
		if names[index] == "selected": control.selected = true
		if names[index] == "disabled": control.disabled = true
		if names[index] == "focus": control.grab_focus()
		control.queue_redraw()
		await frames()
		var image: Image = viewport.get_texture().get_image()
		strip.blit_rect(image,Rect2i(Vector2i.ZERO,viewport.size),Vector2i(index*160,0))
		var alpha := PackedByteArray()
		var covered: int = 0
		for y: int in range(14,50):
			for x: int in range(14,146):
				var value: int = roundi(image.get_pixel(x,y).a*255)
				alpha.append(value)
				if value > 20: covered += 1
		var whole_alpha := PackedByteArray()
		var rgba: PackedByteArray = image.get_data()
		for pixel: int in range(3,rgba.size(),4): whole_alpha.append(rgba[pixel])
		masks[names[index]] = whole_alpha
		check(covered < alpha.size()*0.5,"transparent control interior "+names[index])
	check(masks.normal != masks.hover and masks.hover != masks.pressed and masks.normal != masks.selected and masks.normal != masks.disabled and masks.normal != masks.focus,"control states retain non-color ink distinctions")
	check(study.app.album.sort_choice.get_popup().theme.get_stylebox("panel","PopupMenu").paper.a == 1.0,"popup remains opaque in study")
	check(strip.save_png(output.path_join("control-states.png")) == OK,"native control state strip")
	viewport.queue_free()
	await frames()

func return_cases() -> void:
	root.size = Vector2i(1920,1080)
	study.set_ui_scale(1.0)
	study.app.show_album()
	study.app.album.choose_category("technical")
	study.app.album.commit_page(0,0)
	await frames()
	var first_page: Image = await screenshot("paper-page-one")
	study.app.album.commit_page(1,0)
	await frames()
	var context: Dictionary = study.context()
	var initial: Image = await screenshot("paper-page-two")
	check(study.request_open("T-34"),"return setup opens copied ID from second spread")
	study.interrupt("focus")
	await frames()
	# Idle Escape is not a second, global navigation command.
	var escape := InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	root.push_input(escape,true)
	check(study.state == Study.State.WORK and study.app.work.visible,"idle Escape is not catalog navigation")
	var point: Vector2 = study.app.board.global_position+study.app.board.view.origin+Vector2(5.5,5.5)*study.app.board.view.cell_size
	var cursor: int = study.app.session.player.cursor
	button(true,point)
	button(false,point)
	await frames()
	check(study.app.session.player.cursor == cursor+1,"return starts with actual edited content")
	var cells: Array = fingerprint()
	var writes: int = study.app.store.writes
	var source: Image = await screenshot("return-edited-work")
	var tab: Vector2 = study.app.album_button.get_global_rect().get_center()
	button(true,tab)
	button(false,tab)
	check(study.motion_kind == "return" and study.state == Study.State.PREPARING,"explicit catalog tab starts return")
	while study.state == Study.State.PREPARING: await process_frame
	check(study.direction == -1 and not study.request_return() and not study.request_open("T-06") and not study.request_page(0),"return direction and discarded repeated commands")
	var saved: bool = false
	while study.state == Study.State.OPENING:
		if study.elapsed > 0.7 and not saved:
			saved = true
			no_spoiler(await screenshot("return-middle"),"returning edited page")
		await process_frame
	await frames()
	var returned: Image = await screenshot("paper-page-two-return")
	check(study.state == Study.State.CATALOG and study.elapsed == Study.RETURN_DURATION and study.app.album.page_index == context.page and study.app.album.category_id == context.category and study.app.album.preference.criterion == context.criterion and study.app.album.preference.direction == context.direction and study.app.album.scroll_vertical == context.scroll and study.app.album.selected_id == context.selection,"return retains exact catalog context")
	check(fingerprint() == cells and study.app.store.writes == writes,"return does not mutate history or add saves")
	check(study.app.album.previews[0].cells == study.app.session.player.cells,"return catalog shows current edited progress")
	# A quiet paper-only region is invariant even though the card progress changed.
	var paper: Rect2 = study.projected_paper(false,1)
	var patch := Rect2i(Vector2(paper.position.x+paper.size.x*0.15,paper.end.y-7),Vector2(paper.size.x*0.3,3))
	check(first_page.get_region(patch).get_data() != initial.get_region(patch).get_data(),"different logical pages have different organic paper")
	check(initial.get_region(patch).get_data() == returned.get_region(patch).get_data(),"same logical page retains exact paper after return")
	returns.append({"seconds":study.elapsed,"wall_seconds":study.motion_wall_seconds,"preparation_seconds":study.preparation_seconds,"frame_ms":study.frames_ms.duplicate(),"id":"T-34","page":study.app.album.page_index})
	# Exercise the real return gesture cancellation before any flush.
	check(study.request_open("T-34"),"cancel return setup")
	study.interrupt("focus")
	await frames()
	point = study.app.board.global_position+study.app.board.view.origin+Vector2(6.5,6.5)*study.app.board.view.cell_size
	button(true,point)
	check(study.app.session.gesture.active,"return has active gesture to cancel")
	check(study.request_return(),"explicit return cancels active gesture")
	while study.state == Study.State.PREPARING: await process_frame
	study.set_process(false)
	study._pose(1)
	await screenshot("return-handoff-texture")
	study._settle(true)
	study.set_process(true)
	button(false,point)
	await frames()
	await screenshot("return-handoff-direct")
	handoffs.append({"configuration":[root.size,study.app.ui_scale],"texture":"return-handoff-texture.png","direct":"return-handoff-direct.png"})
	check(fingerprint() == cells and not study.app.session.gesture.active,"return cancellation never commits held gesture")
	study.app.album.choose_category("")
	study.app.album.commit_page(0)
	await frames()
