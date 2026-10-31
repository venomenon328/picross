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

class Baseline extends Main:
	func create_store() -> SaveStore: return Study.Content.MemoryStore.new()
	func puzzle_definitions() -> Array[Dictionary]:
		var result: Array[Dictionary] = []
		var input: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://study/book/fixtures.json"))
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

func screenshot(name: String) -> Image:
	await frames()
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
		app.palette_row.get_rect(), app.tools_scroll.get_rect(), app.title.get_rect()]

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
		study.app.hide()
		study.hide()
		baseline.show()
		var original_image: Image = await screenshot("baseline-%d" % configuration[0].x)
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
		if reason == "resize": root.size = Vector2i(1920, 1080)
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
		events.append({"kind":"page","direction":study.direction,"seconds":study.elapsed,"first_frame":begin,"last_frame":Engine.get_frames_drawn()})
		await frames(12)
	var begin: int = Engine.get_frames_drawn()
	await prepare_open("T-06")
	while study.state == Study.State.OPENING: await process_frame
	events.append({"kind":"open","direction":1,"seconds":study.elapsed,"first_frame":begin,"last_frame":Engine.get_frames_drawn()})
	await frames(15)
	await screenshot("movie-final")
	var file := FileAccess.open(output.path_join("movie.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"fps":30,"events":events,"final_state":"WORK","final_id":str(study.app.session.definition.id),"failures":failures})+"\n")
	file.close()
	print("BOOK_STUDY_MOVIE_OK total=", study.elapsed, " fixed_fps=30 native_motion_separately_measured=true")
	# Keep the settled scene alive through the engine's final recorded frame.
	quit(0 if failures.is_empty() else 4)

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
	var item = study.app.sessions[0]
	var changes: Array[Dictionary] = []
	for y: int in range(item.player.height):
		for x: int in range(item.player.width):
			var index: int = y*item.player.width+x
			var value: int = int(item.definition.solution[y][x])
			if item.player.cells[index] != value: changes.append({"index":index,"before":item.player.cells[index],"after":value})
	item.player.commit(changes)
	item.completed = item.is_solution()
	var token: int = study.generation
	check(study.request_open("T-01"),"solved selection accepted")
	await frames()
	check(study.state == Study.State.WORK and study.generation == token and study.app.ending.visible and not study.app.reveal_view.active,"solved puzzle opens directly without replay")
	study.app._ask_reset_id("T-01","ending")
	study.app._reset_selected()
	study.app.reset_dialog.hide()
	await frames()
	check(study.generation == token and study.app.work.visible and study.app.session.definition.id == "T-01" and study.app.session.player.cells.count(-1) == 400,"ending reset opens same empty page without book animation")

func interruption_cases() -> void:
	for kind: String in ["page","open"]:
		for phase: String in ["prepare","motion"]:
			for reason: String in ["resize","ui-scale","focus","leave"]:
				study.app.show_album()
				study.app.album.commit_page(0,40)
				await frames(6)
				var source: Dictionary = study.context()
				var cells: Array = fingerprint()
				var writes: int = study.app.store.writes
				check(study.request_page(1) if kind == "page" else study.request_open("T-06"),"matrix request %s/%s/%s" % [kind,phase,reason])
				if phase == "motion":
					while study.state == Study.State.PREPARING: await process_frame
					await frames(2)
				var token: int = study.generation
				study.interrupt(reason)
				await frames(6)
				var expected_work: bool = kind == "open" and reason != "leave"
				check(study.state == (Study.State.WORK if expected_work else Study.State.CATALOG) and study.generation > token,"matrix stable target %s/%s/%s" % [kind,phase,reason])
				if not expected_work:
					check(study.app.album.page_index == (1 if reason != "leave" else source.page),"matrix catalog target %s/%s/%s" % [kind,phase,reason])
					if reason == "leave": check(study.app.album.scroll_vertical == source.scroll and study.app.album.selected_id == source.selection,"retained catalog context %s/%s" % [kind,phase])
				check(fingerprint() == cells and study.app.store.writes == writes,"matrix no history or save %s/%s/%s" % [kind,phase,reason])
				check(study.capture == null and study.catalog_texture == null and study.resource_report().visible_leaves == 0,"matrix releases resources %s/%s/%s" % [kind,phase,reason])
				interruptions.append({"kind":kind,"phase":phase,"reason":reason,"state":study.state})
