extends SceneTree
## TEST ONLY: regular scene, real viewport mouse events, isolated saves and frames.
const Main = preload("res://ui/main.gd")
const Session = preload("res://model/session.gd")
const Registry = preload("res://model/content_registry.gd")
const Store = preload("res://model/save_store.gd")
var app: Main
var surface: SubViewport
var output: String
var mode: String
var checks: int = 0
var failures: Array[String] = []
var captures: Array = []
var timings: Dictionary = {}

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, description: String) -> void:
	checks += 1
	if not ok:
		failures.append(description)
		print("KAT2_FAIL: ", description)

func frames() -> void:
	await process_frame
	await process_frame
	await process_frame

func click_at(point: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = point
	surface.push_input(motion, true)
	for down: bool in [true, false]:
		var event: InputEventMouseButton = InputEventMouseButton.new()
		event.position = point
		event.button_index = button
		event.pressed = down
		surface.push_input(event, true)

func click(control: Control) -> void:
	var point: Vector2 = control.get_global_rect().get_center()
	if control.get_window() != root: point += Vector2(control.get_window().position)
	click_at(point)

func choose(id: String) -> void:
	click(app.album.category_choice)
	await frames()
	var popup: PopupMenu = app.album.category_choice.get_popup()
	check(popup.visible, "category popup opens by pointer")
	for index: int in range(app.album.category_choice.item_count):
		if app.album.category_choice.get_item_metadata(index) != id: continue
		if index == app.album.category_choice.item_count - 1:
			popup.scroll_to_item(0)
			for step: int in range(app.album.category_choice.item_count):
				click_at(Vector2(popup.position) + Vector2(80, popup.size.y / 2.0), MOUSE_BUTTON_WHEEL_DOWN)
		else:
			popup.scroll_to_item(index)
		await frames()
		var hit: bool = false
		for y: int in range(4, popup.size.y - 4, 4):
			var point: Vector2 = Vector2(popup.position) + Vector2(80, y)
			var motion: InputEventMouseMotion = InputEventMouseMotion.new()
			motion.position = point
			motion.global_position = point
			motion.relative = Vector2(0, 4)
			motion.velocity = Vector2(0, 240)
			surface.push_input(motion, true)
			if popup.get_focused_item() != index: continue
			for down: bool in [true, false]:
				var event: InputEventMouseButton = InputEventMouseButton.new()
				event.position = point
				event.button_index = MOUSE_BUTTON_LEFT
				event.pressed = down
				event.global_position = point
				surface.push_input(event, true)
			hit = true
			break
		check(hit, "category item reached through popup pointer hit testing")
		break
	await frames()
	check(app.album.category_id == id and app.album.page_index == 0 and app.album.scroll_vertical == 0, "category resets page and scroll")

func shot(name: String) -> void:
	await frames()
	await RenderingServer.frame_post_draw
	var image: Image = surface.get_texture().get_image()
	var filename: String = mode + "-" + name + ".png"
	check(image.save_png(output.path_join(filename)) == OK, "native frame saved " + filename)
	var textures: int = 0
	for reveal: Control in app.album.reveals:
		if reveal.artwork != null: textures += 1
	check(app.choices.size() <= 24 and textures <= 24 and app.album.grid.get_child_count() <= 24, "bounded cards and earned textures")
	var regions: Dictionary = {"selector": region(app.album.category_choice), "count": region(app.album.summary, true)}
	if name == "all-1280-ui125": regions["layout"] = region(app.album)
	if not app.choices.is_empty(): regions["card"] = region(app.choices[0].get_parent())
	else: regions["empty"] = region(app.album.empty_message, true)
	if app.album.next_button.get_parent().visible: regions["page"] = region(app.album.page_label, true)
	for card: Button in app.choices:
		for label: Node in card.find_children("*", "Label", true, false):
			check(card.get_global_rect().grow(1).encloses(label.get_global_rect()), "card labels fit without overlap")
	captures.append({"file": filename, "framebuffer": [image.get_width(), image.get_height()], "window_client": [root.size.x, root.size.y], "ui_scale": app.ui_scale, "category": app.album.category_id, "page": app.album.page_index, "scroll": app.album.scroll_vertical, "cards": app.choices.size(), "textures": textures, "summary": app.album.summary.text, "ids": app.album.visible_ids.duplicate(), "regions": regions})

func region(control: Control, trim_label: bool = false) -> Array:
	var rect: Rect2 = control.get_global_rect()
	if trim_label and control is Label:
		rect.size.x = minf(rect.size.x, control.get_theme_font("font").get_multiline_string_size(control.text, HORIZONTAL_ALIGNMENT_LEFT, rect.size.x, control.get_theme_font_size("font_size")).x + 8)
	rect = rect.intersection(Rect2(Vector2.ZERO, Vector2(surface.size)))
	return [floori(rect.position.x), floori(rect.position.y), ceili(rect.end.x), ceili(rect.end.y)]

func save_bytes(excluded: String = "") -> Dictionary:
	var result: Dictionary = {}
	for filename: String in DirAccess.get_files_at(Store.test_root_override):
		if not filename.begins_with(excluded + "."):
			result[filename] = FileAccess.get_file_as_bytes(Store.test_root_override.path_join(filename))
	return result

func new_app() -> void:
	if app != null:
		app.free()
	var started: int = Time.get_ticks_usec()
	app = load("res://main.tscn").instantiate()
	surface.add_child(app)
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await frames()
	timings["startup_ms"] = (Time.get_ticks_usec() - started) / 1000.0
	check(app.album.visible and not app.work.visible and not app.ending.visible, "regular start is catalog")

func run() -> void:
	output = OS.get_environment("KAT2_OUTPUT")
	mode = OS.get_environment("KAT2_MODE")
	Store.test_root_override = OS.get_environment("P1_TEST_SAVE_ROOT")
	if output.is_empty() or Store.test_root_override.is_empty(): quit(4); return
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	surface = SubViewport.new()
	surface.gui_embed_subwindows = true
	surface.size = Vector2i(1920, 1080)
	surface.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(surface)
	await new_app()
	if mode in ["empty", "invalid"]:
		check(app.session == null and app.choices.is_empty(), "no fake session for absent catalog")
		check(app.catalog_error.is_empty() == (mode == "empty"), "valid empty and invalid registry distinguished")
		check(app.album.empty_message.text.contains("noch keine") if mode == "empty" else app.album.empty_message.text.contains("nicht geladen"), "explicit empty/error message")
		await shot("catalog")
		app.show_information()
		app.set_ui_scale(1.25)
		app.set_puzzle_view(1)
		app.return_to_work()
		check(app.album.visible and app.session == null, "empty/error settings and return usable")
		check(save_bytes().is_empty(), "empty/error path writes no saves")
	elif mode == "large":
		await large()
	elif mode == "adapter":
		var id: String = "pz-test-direct-mono"
		check(app.album.items.has(id), "registered KAT1 adapter content appears in All")
		await choose("test-only-kat2-extra")
		check(app.album.visible_ids == [id], "new data category and adapter puzzle appear without UI changes")
		await shot("category-growth")
	elif mode == "restart":
		check(app.album.category_id.is_empty() and app.album.page_index == 0, "real process restart defaults to All page one")
		check(app.album.notes[0].text == "Neu" and app.album.notes[1].text == "Begonnen" and app.album.notes[5].text == "Gelöst", "empty, redo-only and solved saves survive real process restart")
		check(app.sessions[1].player.cursor == 0 and app.sessions[1].player.history.size() == 1, "redo history restored from disk")
		await choose("gebaeude-bauwerke")
		click(app.choices[0])
		await frames()
		click(app.redo_button)
		check(app.session.definition.id == "F-02" and app.session.player.cells[0] == 1, "pointer resumes restored redo history")
	else:
		await regular()
	var report: Dictionary = {"format": "picross-kat2-native-v1", "test_only": true, "mode": mode, "checks": checks, "failures": failures, "timings_ms": timings, "captures": captures, "display_server": DisplayServer.get_name(), "adapter": RenderingServer.get_video_adapter_name()}
	var file: FileAccess = FileAccess.open(output.path_join(mode + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	if failures.is_empty(): print("KAT2_PROBE_OK ", mode, " checks=", checks, " timings_ms=", timings)
	quit(0 if failures.is_empty() else 4)

func regular() -> void:
	check(app.album.category_choice.item_count == 21 and app.sessions.size() == 6, "six regular puzzles and all twenty categories")
	check(app.album.visible_ids == ["F-01", "F-02", "F-04", "F-06", "F-08", "F-09"], "canonical order without retired slots")
	await choose(str(app.album.categories[-1].id))
	await choose("")
	for spec: Array in [[1920,1080,1.0], [1920,1080,1.25], [1280,720,1.25], [2560,1440,1.0]]:
		surface.size = Vector2i(spec[0], spec[1])
		app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		app.set_ui_scale(float(spec[2]))
		await frames()
		check(Rect2(Vector2.ZERO, Vector2(surface.size)).encloses(app.album.get_global_rect()), "catalog fits requested surface")
		check(app.album.scroll.get_global_rect().position.y >= app.album.summary.get_global_rect().end.y, "cards do not overlap category/count")
		await shot("all-%d-ui%d" % [spec[0], spec[2]*100])
		await choose("gemuese-pilze-kraeuter")
		check(app.album.category_choice.text.contains("Gemüse, Pilze & Kräuter (1)"), "long category name and count")
		check(app.album.category_choice.get_theme_font("font").get_string_size(app.album.category_choice.text, HORIZONTAL_ALIGNMENT_LEFT, -1, app.album.category_choice.get_theme_font_size("font_size")).x < app.album.category_choice.size.x - 32, "initial long category fits selector")
		await shot("filtered-%d-ui%d" % [spec[0], spec[2]*100])
		await choose("")
	surface.size = Vector2i(1920,1080)
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	app.set_ui_scale(1.0)
	await choose("obst-nuesse")
	check(app.choices.is_empty() and app.album.empty_message.visible and app.album.all_button.visible, "empty category has direct All action")
	await shot("empty-category")
	click(app.album.all_button)
	await frames()
	check(app.album.category_id.is_empty(), "pointer returns to All")
	# An automatically created empty save is still new.
	app._save_current()
	app.show_album()
	check(app.album.notes[0].text == "Neu", "empty saved slot is new")
	var original: Dictionary = save_bytes()
	await choose("voegel")
	check(save_bytes() == original, "category change writes no save")
	check(app.album.visible_ids == ["F-09"] and app.choices[0].text.begins_with("Blatt 09"), "filtered zero is global five and keeps number")
	click(app.choices[0])
	await frames()
	check(app.session.definition.id == "F-09" and app.work.visible, "pointer opens stable filtered ID")
	var point: Vector2 = app.board.global_position + app.board.view.cell_rect(Vector2i.ZERO).get_center()
	click_at(point)
	click(app.undo_button)
	check(app.session.player.cursor == 0 and app.session.player.history.size() == 1, "real edit and undo retain redo-only state")
	click(app.album_button)
	await frames()
	check(app.album.category_id == "voegel" and app.album.notes[0].text == "Begonnen", "return and redo-only status")
	check(app.album.reveals[0].payload.is_empty() and app.album.reveals[0].artwork == null, "no unearned texture")
	click(app.choices[0])
	await frames()
	click(app.redo_button)
	check(app.session.player.cells[0] == 1, "pointer resumes and redoes same session")
	app.store.fail_step = "after_temp"
	app.board.eraser = true
	click(app.album_button)
	check(app.work.visible and app.status_label.visible, "failed flush blocks catalog return visibly")
	app.store.fail_step = ""
	click(app.album_button)
	await frames()
	check(app.album.visible and app.album.previews[0].cells[0] == 1, "retry returns own uncorrected progress")
	await shot("begun")
	var foreign: Dictionary = save_bytes("f09")
	click(app.album.reset_buttons["F-09"])
	await frames()
	check(app.reset_id == "F-09" and app.reset_dialog.visible, "reset confirmation bound to filtered ID")
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.album.notes[0].text == "Neu" and save_bytes("f09") == foreign, "confirmed reset affects only target bytes")
	# Earned state and corrupted/recovered saves are loaded by fresh scene instances.
	var target: Session = app.sessions[5]
	var changes: Array[Dictionary] = []
	for y: int in range(target.player.height):
		for x: int in range(target.player.width):
			if int(target.definition.solution[y][x]) > 0: changes.append({"index": y*target.player.width+x, "before": -1, "after": int(target.definition.solution[y][x])})
	target.player.commit(changes)
	target.completed = target.is_solution()
	check(app.store.write_slot(target, target.view_state).is_empty(), "valid earned save written")
	await new_app()
	await choose("voegel")
	check(app.album.notes[0].text == "Gelöst" and app.album.summary.text == "1 von 1 gelöst" and app.choices[0].text == "Eule", "validated solved card/name/count after restart")
	check(app.album.reveals[0].artwork != null, "earned image loaded only for visible card")
	await shot("solved")
	var path: String = app.store.path_for("f09")
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
	var backup: FileAccess = FileAccess.open(app.store.path_for("f09", ".bak"), FileAccess.WRITE)
	backup.store_buffer(bytes)
	backup.close()
	var broken: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	broken.store_string("{bad")
	broken.close()
	await new_app()
	await choose("voegel")
	check(app.album.notes[0].text.contains("Backup geladen") and app.album.repair_buttons.has("F-09"), "validated backup marked with repair")
	click(app.album.repair_buttons["F-09"])
	await frames()
	click(app.repair_dialog.get_ok_button())
	await frames()
	check(app.store.load_slot(app.sessions[5].definition).status == "loaded", "card repair targets recovered slot")
	for suffix: String in [".json", ".bak"]:
		broken = FileAccess.open(app.store.path_for("f09", suffix), FileAccess.WRITE)
		broken.store_string("{bad")
		broken.close()
	await new_app()
	await choose("voegel")
	check(app.choices[0].disabled and app.album.notes[0].text.contains("ungültig") and app.album.summary.text == "0 von 1 gelöst", "invalid saves are neither new nor solved")
	await shot("invalid-save")
	# Leave independently validated solved and redo-only slots for another process.
	for suffix: String in [".json", ".bak"]:
		var restored: FileAccess = FileAccess.open(app.store.path_for("f09", suffix), FileAccess.WRITE)
		restored.store_buffer(bytes)
		restored.close()
	await choose("gebaeude-bauwerke")
	click(app.choices[0])
	await frames()
	click_at(app.board.global_position + app.board.view.cell_rect(Vector2i.ZERO).get_center())
	click(app.undo_button)
	click(app.album_button)
	await frames()
	check(app.album.notes[0].text == "Begonnen", "redo-only slot prepared through pointer before process exit")

func large() -> void:
	check(app.sessions.size() == 300 and app.album.categories.size() == 20, "300 synthetic sessions and twenty categories")
	check(app.album.summary.text == "150 von 300 gelöst" and app.choices.size() == 24, "valid saved completions counted across all pages")
	await shot("first-page")
	var before: Dictionary = save_bytes()
	var started: int = Time.get_ticks_usec()
	click(app.album.next_button)
	await frames()
	timings["page_ms"] = (Time.get_ticks_usec() - started) / 1000.0
	check(app.album.page_index == 1 and app.album.visible_ids[0] == "pz-test-kat2-024", "second page canonical stable ID")
	app.album.scroll_vertical = 150
	await frames()
	var position: int = app.album.scroll_vertical
	app.show_information()
	app.return_to_work()
	await frames()
	check(app.album.page_index == 1 and app.album.scroll_vertical == position, "info return preserves page and scroll")
	check(save_bytes() == before, "paging and info do not modify saves")
	await shot("second-page")
	app.album.scroll_vertical = 0
	await frames()
	var id: String = app.album.visible_ids[1]
	click(app.choices[1])
	await frames()
	check(app.session.definition.id == id and app.work.visible, "later page opens correct unsolved slot")
	click_at(app.board.global_position + app.board.view.cell_rect(Vector2i.ZERO).get_center())
	click(app.album_button)
	await frames()
	check(app.album.page_index == 1 and app.album.notes[1].text == "Begonnen", "later page resume return")
	var foreign: Dictionary = save_bytes("kat2_025")
	click(app.album.reset_buttons[id])
	await frames()
	# Changing the page with an outstanding request cannot retarget the dialog.
	app.album.turn_page(1)
	app.reset_dialog.confirmed.emit()
	app.reset_dialog.hide()
	await frames()
	check(app.sessions[25].player.cells.count(-1) == 400 and save_bytes("kat2_025") == foreign, "later-page reset owns ID and preserves foreign slots")
	started = Time.get_ticks_usec()
	await choose("gebaeude-bauwerke")
	timings["category_ms"] = (Time.get_ticks_usec() - started) / 1000.0
	check(app.album.filtered_ids.size() == 250 and app.choices.size() == 24, "uneven category keeps pagination bound")
	await choose("obst-nuesse")
	check(app.choices.is_empty() and app.album.summary.text == "0 von 0 gelöst", "large catalog includes empty categories")
	await choose("")
	for index: int in range(12):
		app.album.turn_page(1)
		check(app.choices.size() <= 24, "every page bounded during repeated navigation")
	await frames()
	check(app.choices.size() == 12 and app.album.next_button.disabled, "last page contains remainder")
	await shot("last-page")
