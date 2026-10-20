extends SceneTree
## TEST ONLY: regular scene, real viewport mouse events, isolated saves and frames.
const Main = preload("res://ui/main.gd")
const Session = preload("res://model/session.gd")
const Registry = preload("res://model/content_registry.gd")
const Store = preload("res://model/save_store.gd")
const Card = preload("res://ui/catalog_card.gd")
var app: Main
var surface: SubViewport
var output: String
var mode: String
var checks: int = 0
var failures: Array[String] = []
var captures: Array = []
var timings: Dictionary = {}
var quit_slot_hashes: Dictionary = {}
var kb_measurements: Array = []
var kk_measurements: Array = []
var kk_pointer_measurements: Array = []
var ke_graphics_measurements: Array = []
var at_measurements: Array = []

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
	if control is Card:
		# Both title and footer can be clipped after a preserved scroll offset.
		# The centre may be a recovery action; the visible inset belongs to the card.
		var visible: Rect2 = control.get_global_rect().intersection(app.album.scroll.get_global_rect())
		point = Vector2(visible.position.x+5*app.ui_scale,visible.get_center().y)
	if control.get_window() != root: point += Vector2(control.get_window().position)
	click_at(point)

func choose(id: String) -> void:
	var unchanged: bool = app.album.category_id == id
	var old_page: int = app.album.page_index
	var old_scroll: int = app.album.scroll_vertical
	click(app.album.category_choice)
	# The offscreen SubViewport is not a Window: unlike the real player it
	# gets no focus-out when an embedded popup opens. Deliver that native
	# notification so the opener's left-button capture cannot retain wheels.
	surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
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
	check(not popup.visible, "category popup closes after real item click")
	check(app.album.category_id == id and app.album.page_index == (old_page if unchanged else 0) and app.album.scroll_vertical == (old_scroll if unchanged else 0), "category resets page and scroll only on change")

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
	if name == "all-1280-ui125" or name.begins_with("sorting"): regions["layout"] = region(app.album)
	if not app.choices.is_empty(): regions["card"] = region(app.choices[0].get_parent())
	else: regions["empty"] = region(app.album.empty_message, true)
	if app.album.next_button.get_parent().visible: regions["page"] = region(app.album.page_label, true)
	if mode in ["kb", "kk", "ke"]:
		regions["layout"] = region(app.album if app.album.visible else app.work)
		regions["title"] = region(app.title)
	for card: Button in app.choices:
		for label: Label in [card.caption,card.detail,card.leaf,card.note]:
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
	# Existing KAT/KE scenarios bind their synthetic slots by canonical order.
	# All their added dates are unknown; KU-B's large scenario tests real sorting.
	if not mode in ["large", "adapter", "empty", "invalid"]: app.album.choose_sort("added")
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
	# Offscreen native SubViewport has no container to deliver mouse-enter.
	# This enables the same built-in hover delay/tooltip path as a real window.
	surface.notify_mouse_entered()
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
		await sorting()
	elif mode == "information":
		await information_saves()
	elif mode == "kb":
		await compact_buttons()
	elif mode == "kk":
		await fixed_cards()
		await preload("res://tests/hz_native.gd").run(self)
		await preload("res://tests/hz_b_native.gd").run(self)
	elif mode == "ke":
		await catalog_labels()
		await preload("res://tests/ke_graphics.gd").run(self)
	elif mode == "at":
		await transparent_reveals()
	elif mode == "adapter":
		var id: String = "pz-test-direct-mono"
		check(app.album.items.has(id), "registered KAT1 adapter content appears in All")
		app.album.ensure_control_visible(app.choices[-1])
		await shot("growth-all-long-name")
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
		check(app.session.definition.id == "T-02" and app.session.player.cells[0] == 1, "pointer resumes restored redo history")
	else:
		await regular()
	if mode == "information":
		# The actual Beenden callback must end this process. A blocked quit resumes
		# below and rewrites the report as a failure; no test stub replaces quit().
		for filename: String in save_bytes():
			quit_slot_hashes[filename] = FileAccess.get_sha256(Store.test_root_override.path_join(filename))
		write_report()
		print("KAT2_QUIT_ATTEMPT catalog-origin information")
		click(caption_button(app.settings_panel, "Beenden"))
		await frames()
		check(false, "catalog-origin information permits regular process quit")
	write_report()
	quit(0 if failures.is_empty() else 4)

func write_report() -> void:
	var report: Dictionary = {"format": "picross-kat2-native-v1", "test_only": true, "mode": mode, "checks": checks, "failures": failures, "timings_ms": timings, "captures": captures, "kb_measurements": kb_measurements, "kk_measurements": kk_measurements, "kk_pointer_measurements": kk_pointer_measurements, "quit_slot_hashes": quit_slot_hashes, "display_server": DisplayServer.get_name(), "adapter": RenderingServer.get_video_adapter_name()}
	report["ke_graphics_measurements"] = ke_graphics_measurements
	report["at_measurements"] = at_measurements
	var file: FileAccess = FileAccess.open(output.path_join(mode + ".json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	if failures.is_empty(): print("KAT2_PROBE_OK ", mode, " checks=", checks, " timings_ms=", timings)

func transparent_reveals() -> void:
	check(app.choices[0].picture.artwork == null and app.choices[2].picture.artwork == null, "AT fresh cards do not load new artwork")
	app.select_puzzle(0)
	await frames()
	click_at(app.board.global_position+app.board.view.cell_rect(Vector2i(2,2)).get_center())
	app.show_album()
	await frames()
	check(app.choices[0].picture.artwork == null and app.choices[0].note.text == "Begonnen", "AT begun card shows only own fill")
	var item = app.sessions[2]
	for y: int in range(item.player.height):
		for x: int in range(item.player.width):
			var value: int = item.definition.solution[y][x]
			if value > 0:
				item.gesture.begin(item.player,Vector2i(x,y),value)
				item.finish()
	check(item.completed and app.store.write_slot(item,item.view_state).is_empty(), "AT synthetic completion earned and saved")
	app.show_album()
	var hidden_board: Rect2 = app.board.get_rect()
	var hidden_view: Dictionary = app.board.capture_view()
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
		surface.size=Vector2i(spec[0],spec[1])
		app.set_ui_scale(spec[2])
		await frames()
		check(app.board.get_rect() == hidden_board and app.board.capture_view() == hidden_view,"AT album resize leaves hidden work geometry and saved view unchanged")
		var card = app.choices[2]
		app.album.ensure_control_visible(card)
		await frames()
		var before := await preload("res://tests/at_alpha.gd").sample(self,card.picture,"catalog-%d" % spec[0])
		var motion := InputEventMouseMotion.new()
		motion.position=card.get_global_rect().get_center()
		surface.push_input(motion,true)
		await create_timer(0.6).timeout
		var hover := await preload("res://tests/at_alpha.gd").sample(self,card.picture,"hover-%d" % spec[0])
		check(card.is_hovered(), "AT actual card hover reached")
		check(app.choices[0].picture.artwork == null and app.choices[1].picture.artwork == null,"AT begun/new remain spoiler-free alongside solved image")
		at_measurements.append({"window":spec,"small":before,"hover":hover})
	app.select_puzzle(0)
	await frames()
	check(app.work.visible and app.board.get_rect() != hidden_board and app.board.layout_valid,"AT opening begun work applies current viewport geometry")
	check(app.board.capture_view() == hidden_view,"AT deferred layout preserves desired work state")

func caption_button(parent: Node, caption: String) -> Button:
	for node: Node in parent.find_children("*", "Button", true, false):
		if node.text == caption: return node
	check(false, "UI button exists: " + caption)
	return null

func choose_view(index: int) -> void:
	click(app.view_choice)
	await frames()
	var popup: PopupMenu = app.view_choice.get_popup()
	check(popup.visible, "puzzle view popup opens by pointer")
	# Native popup hit testing, including the actual item_selected signal.
	for y: int in range(4, popup.size.y - 4, 4):
		var point: Vector2 = Vector2(popup.position) + Vector2(60, y)
		var motion: InputEventMouseMotion = InputEventMouseMotion.new()
		motion.position = point
		motion.global_position = point
		motion.relative = Vector2(0, 4)
		motion.velocity = Vector2(0, 240)
		surface.push_input(motion, true)
		if popup.get_focused_item() == index:
			for down: bool in [true, false]:
				var event: InputEventMouseButton = InputEventMouseButton.new()
				event.position = point
				event.global_position = point
				event.button_index = MOUSE_BUTTON_LEFT
				event.pressed = down
				surface.push_input(event, true)
			break
	await frames()
	check(app.board.mode == ("V" if index == 1 else "G") and not popup.visible, "pointer changes puzzle view")

func information_profile(base: String, state: String) -> void:
	if app != null:
		app.free()
		app = null
	Store.test_root_override = base.path_join(state)
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	var valid: PackedByteArray = FileAccess.get_file_as_bytes("res://tests/fixtures/runtime/t01.json")
	for suffix: String in [".json", ".bak"]:
		if state == "recovered_missing" and suffix == ".json": continue
		var file: FileAccess = FileAccess.open(Store.test_root_override.path_join("t01" + suffix), FileAccess.WRITE)
		var damaged: bool = state == "error" or (state == "recovered" and suffix == ".json") or (state == "backup_invalid" and suffix == ".bak")
		file.store_buffer(("{TEST ONLY damaged " + suffix).to_utf8_buffer() if damaged else valid)
		file.close()
	# A separate valid slot makes unintended writes/rotation observable too.
	var foreign: FileAccess = FileAccess.open(Store.test_root_override.path_join("t02.json"), FileAccess.WRITE)
	foreign.store_buffer(FileAccess.get_file_as_bytes("res://tests/fixtures/runtime/t02.json"))
	foreign.close()
	await new_app()

func information_saves() -> void:
	var base: String = Store.test_root_override
	for state: String in ["error", "recovered", "recovered_missing", "backup_invalid"]:
		await information_profile(base, state)
		var expected: String = "recovered" if state == "recovered_missing" else state
		check(app.slot_status[0] == expected, state + ": isolated T01 state loaded")
		var original: Dictionary = save_bytes()
		var history: Array = app.session.player.history.duplicate(true)
		await choose("fahrzeuge-verkehr")
		click(caption_button(app.album, "Einstellungen / Info"))
		await frames()
		check(app.information.visible and app.information_origin == "album", state + ": pointer opens catalog information")
		await choose_view(1)
		check(app.save_timer.is_stopped(), state + ": catalog view change schedules no slot save")
		await create_timer(0.5).timeout
		check(app.slot_errors[0].is_empty() and save_bytes() == original, state + ": no save attempt after debounce")
		click(app.ui_scale_button)
		await frames()
		click(app.clue_reset_button)
		click(app.clue_completion_toggle)
		click(app.animation_toggle)
		click(app.actions["nav-work"])
		await frames()
		check(app.album.visible and app.album.category_id == "fahrzeuge-verkehr", state + ": return preserves catalog selection and reset access")
		check(save_bytes() == original and app.session.player.history == history, state + ": information navigation preserves all slot bytes and history")
		if not app.album.visible: continue # Keep the original failure evidence; next case has its own profile.
		var foreign: Dictionary = save_bytes("t01")
		var dialog: ConfirmationDialog = app.reset_dialog if state == "error" else app.repair_dialog
		var action: Button = app.album.reset_buttons["T-01"] if state == "error" else app.album.repair_buttons["T-01"]
		click(action)
		await frames()
		check(dialog.visible and save_bytes() == original, state + ": repair/reset requires confirmation")
		click(dialog.get_cancel_button())
		await frames()
		check(not dialog.visible and save_bytes() == original, state + ": cancellation preserves damaged bytes")
		if state != "error":
			click(app.choices[0])
			await frames()
			click_at(app.board.global_position + app.board.view.cell_rect(Vector2i(2, 0)).get_center())
			check(not app.slot_errors[0].is_empty() and save_bytes() == original, state + ": real work edit cannot bypass recovery lock")
			click(app.album_button)
			check(app.work.visible, state + ": unsaved recovery edit blocks leaving work")
			click(app.work_repair_button)
		else:
			click(app.album.reset_buttons["T-01"])
		await frames()
		click(dialog.get_ok_button())
		await frames()
		check(app.album.visible and app.slot_status[0] in ["fresh", "loaded"], state + ": explicit confirmation restores navigation")
		check(save_bytes("t01") == foreign, state + ": explicit action preserves foreign slots")
		if state != "error":
			var loaded: Dictionary = app.store.load_slot(app.sessions[0].definition)
			check(loaded.status == "loaded" and int(loaded.data.cells[2]) == 1 and FileAccess.file_exists(app.store.path_for("t01", ".bak")), state + ": confirmation persists actual work and valid backup")
	# Real unsaved work: both immediate cell save and debounced work-origin view.
	await information_profile(base, "dirty")
	click(app.choices[0])
	await frames()
	app.store.fail_step = "after_temp"
	click_at(app.board.global_position + app.board.view.cell_rect(Vector2i(2, 0)).get_center())
	check(app.session.player.cells[2] == 1 and not app.slot_errors[0].is_empty(), "dirty: actual pointer edit remains unsaved on write failure")
	click(app.actions["menu"])
	click(app.album_button)
	app.select_by_id("T-02")
	app.notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
	await frames()
	check(app.work.visible and app.session.definition.id == "T-01" and app.status_label.visible, "dirty: failed flush blocks info, catalog, slot switch and WM close")
	app.store.fail_step = ""
	click(app.actions["menu"])
	await frames()
	check(app.information.visible and app.information_origin == "work", "dirty: successful retry permits work-origin information")
	check(int(app.store.load_slot(app.session.definition).data.cells[2]) == 1, "dirty: retry persists confirmed cell")
	app.store.fail_step = "after_temp"
	await choose_view(1)
	check(not app.save_timer.is_stopped(), "dirty: work-origin view still schedules mandatory save")
	click(app.actions["nav-work"])
	click(caption_button(app.settings_panel, "Beenden"))
	app.notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
	await create_timer(0.5).timeout
	check(app.information.visible and app.status_label.visible and not app.slot_errors[0].is_empty(), "dirty: view failure blocks return, Beenden and WM close")
	app.store.fail_step = ""
	click(app.actions["nav-work"])
	await frames()
	check(app.work.visible and app.slot_errors[0].is_empty(), "dirty: retry clears failure and restores work")
	# A fresh damaged profile tests the real Beenden path at the end of run().
	await information_profile(base, "error-quit")
	for suffix: String in [".json", ".bak"]:
		var file: FileAccess = FileAccess.open(app.store.path_for("t01", suffix), FileAccess.WRITE)
		file.store_string("{TEST ONLY damaged quit")
		file.close()
	await new_app()
	click(caption_button(app.album, "Einstellungen / Info"))
	await frames()
	await choose_view(1)
	await create_timer(0.5).timeout
	check(app.slot_status[0] == "error" and app.slot_errors[0].is_empty(), "quit: damaged slot remains untouched before regular Beenden")

func regular() -> void:
	check(app.album.category_choice.item_count == 21 and app.sessions.size() == 6, "six technical puzzles and all twenty categories")
	check(app.album.visible_ids == ["T-01", "T-02", "T-04", "T-06", "T-08", "T-09"], "fixed technical catalog order")
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
	check(app.album.visible_ids == ["T-09"] and app.choices[0].leaf.text == "Blatt 06", "filtered zero is global five and keeps number")
	click(app.choices[0])
	await frames()
	check(app.session.definition.id == "T-09" and app.work.visible, "pointer opens stable filtered ID")
	var point: Vector2 = app.board.global_position + app.board.view.cell_rect(Vector2i.ZERO).get_center()
	click_at(point)
	click(app.undo_button)
	check(app.session.player.cursor == 0 and app.session.player.history.size() == 1, "real edit and undo retain redo-only state")
	click(app.album_button)
	await frames()
	check(app.album.category_id == "voegel" and app.album.notes[0].text == "Begonnen", "return and redo-only status")
	check(app.choices[0].accessibility_name.contains("Fortsetzen"), "KB redo-only action continues")
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
	var foreign: Dictionary = save_bytes("t09")
	click(app.album.reset_buttons["T-09"])
	await frames()
	check(app.reset_id == "T-09" and app.reset_dialog.visible, "reset confirmation bound to filtered ID")
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.album.notes[0].text == "Neu" and save_bytes("t09") == foreign, "confirmed reset affects only target bytes")
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
	check(app.album.notes[0].text == "Gelöst" and app.album.summary.text == "1 von 1 gelöst" and app.choices[0].caption.text == "TEST ONLY Muster 9", "validated solved card/name/count after restart")
	check(app.album.reveals[0].artwork != null, "earned image loaded only for visible card")
	check(app.choices[0].accessibility_name.contains("Ansehen"), "KB solved action views existing completion")
	await shot("solved")
	app.sessions[5].definition.reveal.name = "TEST ONLY Ein besonders langer verdienter Motivname mit Umlauten und mehreren umbrochenen Zeilen auf derselben kompakten Karte"
	app.show_album()
	await shot("long-earned-name")
	var path: String = app.store.path_for("t09")
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
	var backup: FileAccess = FileAccess.open(app.store.path_for("t09", ".bak"), FileAccess.WRITE)
	backup.store_buffer(bytes)
	backup.close()
	var broken: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	broken.store_string("{bad")
	broken.close()
	await new_app()
	await choose("voegel")
	check(app.choices[0].diagnosis.text.contains("Backup geladen") and app.album.repair_buttons.has("T-09"), "validated backup marked with repair")
	var recovered_card: Card = app.choices[0]
	var recovered_point: Vector2 = recovered_card.diagnosis.get_global_rect().position + Vector2(8, 8)
	check(recovered_card.recovery.get_global_rect().has_point(recovered_point), "KK recovered diagnosis has visible interior pointer target")
	click_at(recovered_point)
	await frames()
	check(app.session.definition.id == "T-09" and app.ending.visible and not app.album.visible, "KK recovered diagnosis pointer opens valid earned card")
	click(app.album_button)
	await frames()
	check(app.album.visible and app.album.category_id == "voegel", "KK recovery card returns to same filter")
	foreign = save_bytes("t09")
	click(app.album.repair_buttons["T-09"])
	await frames()
	click(app.repair_dialog.get_ok_button())
	await frames()
	check(app.store.load_slot(app.sessions[5].definition).status == "loaded", "card repair targets recovered slot")
	check(save_bytes("t09") == foreign, "card repair preserves foreign slot bytes")
	broken = FileAccess.open(app.store.path_for("t09", ".bak"), FileAccess.WRITE)
	broken.store_string("{bad")
	broken.close()
	await new_app()
	await choose("voegel")
	check(app.session.definition.id == "T-01" and app.slot_status[5] == "backup_invalid", "nonactive filtered slot has damaged backup")
	var damaged_backup_card: Card = app.choices[0]
	var damaged_backup_point: Vector2 = damaged_backup_card.diagnosis.get_global_rect().position + Vector2(8, 8)
	check(damaged_backup_card.recovery.get_global_rect().has_point(damaged_backup_point), "KK invalid-backup diagnosis has visible interior pointer target")
	click_at(damaged_backup_point)
	await frames()
	check(app.session.definition.id == "T-09" and app.ending.visible and not app.album.visible, "KK invalid-backup diagnosis pointer opens valid earned card")
	click(app.album_button)
	await frames()
	check(app.album.visible and app.album.category_id == "voegel", "KK invalid-backup card returns to same filter")
	click(app.album.repair_buttons["T-09"])
	await frames()
	click(app.repair_dialog.get_ok_button())
	await frames()
	check(app.store.load_slot(app.sessions[5].definition).status == "loaded" and FileAccess.file_exists(app.store.path_for("t09", ".bak")), "foreign card renewal actually creates a valid backup")
	check(save_bytes("t09") == foreign, "foreign backup renewal leaves active slot bytes unchanged")
	click(app.album.reset_buttons["T-09"])
	await frames()
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.album.notes[0].text == "Neu" and app.album.summary.text == "0 von 1 gelöst", "reset of earned slot clears validated completion count")
	for suffix: String in [".json", ".bak"]:
		broken = FileAccess.open(app.store.path_for("t09", suffix), FileAccess.WRITE)
		broken.store_string("{bad")
		broken.close()
	await new_app()
	await choose("voegel")
	check(app.choices[0].disabled and app.album.notes[0].text == "Ungültig" and app.album.summary.text == "0 von 1 gelöst", "invalid saves are neither new nor solved")
	check(app.choices[0].disabled and app.album.reset_buttons["T-09"].visible and not app.album.reset_buttons["T-09"].disabled, "KB damaged save blocks play but retains reset")
	var corrupted_primary: PackedByteArray = FileAccess.get_file_as_bytes(app.store.path_for("t09"))
	var corrupted_backup: PackedByteArray = FileAccess.get_file_as_bytes(app.store.path_for("t09", ".bak"))
	check(app._flush_current(), "KK unrelated pending state flushed before cross-slot reset comparison")
	var unaffected_slots: Dictionary = save_bytes("t09")
	click(app.album.reset_buttons["T-09"])
	await frames()
	check(app.reset_dialog.visible and app.reset_id == "T-09" and app.album.visible, "KK disabled invalid card exposes reset to real pointer")
	click(app.reset_dialog.get_cancel_button())
	await frames()
	check(FileAccess.get_file_as_bytes(app.store.path_for("t09")) == corrupted_primary and FileAccess.get_file_as_bytes(app.store.path_for("t09", ".bak")) == corrupted_backup, "KK error reset cancellation preserves invalid slot bytes")
	await shot("invalid-save")
	click(app.album.reset_buttons["T-09"])
	await frames()
	check(app.reset_dialog.visible and app.reset_id == "T-09", "KK disabled card reset remains accessible after cancel")
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.album.visible, "KK confirmed invalid reset stays in catalog")
	check(app.slot_status[5] == "fresh", "KK confirmed invalid reset clears only target status")
	check(not app.choices[0].disabled and not app.album.reset_buttons["T-09"].visible, "KK confirmed invalid reset restores fresh clickable card")
	check(save_bytes("t09") == unaffected_slots, "KK confirmed invalid reset keeps every unrelated flushed slot byte")
	# Leave independently validated solved and redo-only slots for another process.
	for suffix: String in [".json", ".bak"]:
		var restored: FileAccess = FileAccess.open(app.store.path_for("t09", suffix), FileAccess.WRITE)
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

func sorting() -> void:
	await choose("")
	var original: Dictionary = save_bytes()
	for spec: Vector3i in [Vector3i(1280,720,125), Vector3i(1920,1080,100), Vector3i(2560,1440,125)]:
		surface.size = Vector2i(spec.x, spec.y)
		app.set_ui_scale(spec.z / 100.0)
		await frames()
		for control: Control in [app.album.category_choice, app.album.sort_choice, app.album.direction_button]:
			check(Rect2(Vector2.ZERO, Vector2(surface.size)).encloses(control.get_global_rect()), "KU-B sort controls fit native viewport")
		check(app.album.category_choice.get_global_rect().end.x <= app.album.sort_choice.get_global_rect().position.x and app.album.sort_choice.get_global_rect().end.x <= app.album.direction_button.get_global_rect().position.x, "KU-B adjacent sort controls do not overlap")
		await sort_pointer(3)
		check(app.album.preference.direction == "desc", "KU-B actual added menu defaults newest")
		var ids: Array[String] = app.album.filtered_ids.duplicate()
		check(ids.size() == 300 and app.album.visible_ids == ids.slice(0,24), "KU-B sorts all 300 before pagination")
		var unknown: bool = false
		for index: int in range(ids.size()):
			var date: Variant = app.album.metadata[ids[index]].get("added_at")
			if date == null: unknown = true
			else: check(not unknown, "KU-B unknown date is always last")
			if index > 0:
				var prior: Variant = app.album.metadata[ids[index-1]].get("added_at")
				if prior == date: check(Registry.ordinal(ids[index-1]) < Registry.ordinal(ids[index]), "KU-B date ties use canonical Blatt order")
				elif prior != null and date != null: check(prior > date, "KU-B newest-first actual key order")
		click(app.album.next_button)
		await frames()
		check(app.album.visible_ids == ids.slice(24,48), "KU-B page two belongs to full sorted result")
		app.album.scroll_vertical = 80
		await frames()
		var position: int = app.album.scroll_vertical
		var id: String = app.album.visible_ids[0]
		app.album.ensure_control_visible(app.choices[0])
		await frames()
		position = app.album.scroll_vertical
		click(app.choices[0])
		await frames()
		check(app.session.definition.id == id, "KU-B sorted card opens its stable ID")
		app.show_album()
		await frames()
		check(app.album.page_index == 1 and app.album.scroll_vertical == position and app.album.selected_id == id and app.album.filtered_ids == ids, "KU-B sorted return retains page scroll selection and order")
		click(app.album.direction_button)
		await frames()
		check(app.album.preference.direction == "asc" and app.album.page_index == 0 and app.album.scroll_vertical == 0, "KU-B pointer direction resets page and scroll")
		await shot("sorting-%d-ui%d" % [spec.x, spec.z])
		await sort_pointer(0)
	check(save_bytes() == original, "KU-B browsing and preference writes never modify slots")
	app.album.choose_sort("category")
	if app.album.preference.direction != "asc": app.album.reverse_sort()

func sort_pointer(index: int) -> void:
	click(app.album.sort_choice)
	surface.notification(Node.NOTIFICATION_WM_WINDOW_FOCUS_OUT)
	await frames()
	var popup: PopupMenu = app.album.sort_choice.get_popup()
	check(popup.visible, "KU-B sort menu opens by mouse")
	var hit: bool = false
	for y: int in range(4, popup.size.y-4, 3):
		var point: Vector2 = Vector2(popup.position) + Vector2(30,y)
		var motion: InputEventMouseMotion = InputEventMouseMotion.new()
		motion.position = point
		motion.global_position = point
		motion.relative = Vector2(0,3)
		motion.velocity = Vector2(0,240)
		surface.push_input(motion, true)
		if popup.get_focused_item() != index: continue
		for down: bool in [true, false]:
			var event: InputEventMouseButton = InputEventMouseButton.new()
			event.position = point
			event.global_position = point
			event.button_index = MOUSE_BUTTON_LEFT
			event.pressed = down
			surface.push_input(event, true)
		hit = true
		break
	await frames()
	check(hit and not popup.visible and app.album.preference.criterion == app.album.Preference.CRITERIA[index], "KU-B criterion selected through actual pointer hit")

func large() -> void:
	# Equal areas recover the canonical ordering needed by the pre-existing
	# page/reset assertions; sorting() separately covers editorial/default order.
	app.album.choose_sort("size")
	check(app.sessions.size() == 300 and app.album.categories.size() == 20, "300 synthetic sessions and twenty categories")
	check(app.album.summary.text == "150 von 300 gelöst" and app.choices.size() == 24, "valid saved completions counted across all pages")
	await shot("first-page")
	var before: Dictionary = save_bytes()
	var released: Array[WeakRef] = []
	for picture: Control in app.album.reveals:
		if picture.artwork != null: released.append(weakref(picture.artwork))
	var started: int = Time.get_ticks_usec()
	click(app.album.next_button)
	await frames()
	timings["page_ms"] = (Time.get_ticks_usec() - started) / 1000.0
	check(app.album.page_index == 1 and app.album.visible_ids[0] == "pz-test-kat2-024", "second page canonical stable ID")
	for reference: WeakRef in released:
		check(reference.get_ref() == null, "old page reveal texture actually released")
	app.album.scroll_vertical = 150
	await frames()
	var position: int = app.album.scroll_vertical
	app.show_information()
	app.return_to_work()
	await frames()
	check(app.album.page_index == 1 and app.album.scroll_vertical == position, "info return preserves page and scroll")
	check(save_bytes() == before, "paging and info do not modify saves")
	await shot("second-page")
	app.album.scroll_vertical = 64
	await frames()
	position = app.album.scroll_vertical
	var id: String = app.album.visible_ids[1]
	click(app.choices[1])
	await frames()
	check(app.session.definition.id == id and app.work.visible, "later page opens correct unsolved slot")
	click_at(app.board.global_position + app.board.view.cell_rect(Vector2i.ZERO).get_center())
	click(app.album_button)
	await frames()
	check(app.album.page_index == 1 and app.album.scroll_vertical == position and app.album.notes[1].text == "Begonnen", "later page resume return preserves scroll")
	var foreign: Dictionary = save_bytes("kat2_025")
	app.album.ensure_control_visible(app.album.reset_buttons[id])
	await frames()
	click(app.album.reset_buttons[id])
	await frames()
	check(app.reset_dialog.visible and app.reset_id == id,"KK later-page reset reached through an unclipped pointer target")
	# Changing the page with an outstanding request cannot retarget the dialog.
	app.album.turn_page(1)
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.sessions[25].player.cells.count(-1) == 400 and save_bytes("kat2_025") == foreign, "later-page reset owns ID and preserves foreign slots")
	started = Time.get_ticks_usec()
	await choose("gebaeude-bauwerke")
	timings["category_ms"] = (Time.get_ticks_usec() - started) / 1000.0
	check(app.album.filtered_ids.size() == 250 and app.choices.size() == 24, "uneven category keeps pagination bound")
	await choose("obst-nuesse")
	check(app.choices.is_empty() and app.album.summary.text == "0 von 0 gelöst", "large catalog includes empty categories")
	app.store.fail_step = "after_temp"
	app.board.eraser = not app.board.eraser
	check(not app._save_current(), "pending failed save prepared for filtered-out active slot")
	app.show_information()
	check(app.album.visible and app.album.feedback.visible, "blocked flush remains visible with active slot outside filter")
	app.store.fail_step = ""
	app.show_information()
	app.return_to_work()
	await frames()
	check(app.album.visible and not app.album.feedback.visible, "catalog error feedback clears after successful retry")
	await choose("")
	for index: int in range(12):
		app.album.turn_page(1)
		check(app.choices.size() <= 24, "every page bounded during repeated navigation")
	await frames()
	check(app.choices.size() == 12 and app.album.next_button.disabled, "last page contains remainder")
	for card: Control in app.choices:
		check(card.size == app.choices[0].size and card.get_parent().size == app.choices[0].get_parent().size,"KK last mixed completion page has identical bounded grid cells")
	await shot("last-page")

func hover(control: Control) -> void:
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = control.get_global_rect().get_center()
	surface.push_input(motion, true)
	await frames()

func button_pixels(control: Control) -> PackedByteArray:
	await frames()
	await RenderingServer.frame_post_draw
	return surface.get_texture().get_image().get_region(Rect2i(control.get_global_rect())).get_data()

func visible_popups() -> int:
	var count: int = 0
	for window: Window in surface.get_embedded_subwindows():
		if window.visible: count += 1
	return count

func card_geometry() -> Array:
	var result: Array = []
	for card: Control in app.choices:
		result.append({"cell":card.get_parent().get_global_rect(),"card":card.get_global_rect(),"title":Rect2(card.caption.position,card.caption.size),"meta":Rect2(card.detail.position,card.detail.size),"image":card.image_area,"leaf":Rect2(card.leaf.position,card.leaf.size),"status":Rect2(card.note.position,card.note.size),"reset":Rect2(card.reset.position,card.reset.size)})
	return result

func catalog_labels() -> void:
	# Fixed metadata examples, independent of the production inventory.
	var levels: Array = [null,"L1","L2","L3","L4","L5"]
	for index: int in range(app.sessions.size()):
		var value: Variant = null
		if levels[index] != null:
			value = {"method":"picross-difficulty-0.3","level":levels[index],"assessment_type":"instrumented","confidence":"medium","plausible_range":[levels[index],levels[index]],"r4_required":false}
		app.album.metadata[app.sessions[index].definition.id]["difficulty"] = value
		for entry: Dictionary in Registry.cached.entries:
			if entry.id == app.sessions[index].definition.id: entry.difficulty = value
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25],[1920,1080,1.25]]:
		surface.size = Vector2i(spec[0],spec[1])
		app.set_ui_scale(float(spec[2]))
		app.album._render(0)
		await frames()
		var geometry: Array = card_geometry()
		for card: Card in app.choices:
			check(card.unknown.visible and not card.preview.visible and card.picture.artwork == null,"KE new uses common drawing and never loads reveal")
			check(card.image_area.size.y == roundf(112*app.ui_scale),"KE preview retains full image height")
			for label: Label in [card.dimensions,card.difficulty,card.note]:
				var width: float = label.get_theme_font("font").get_string_size(label.text,HORIZONTAL_ALIGNMENT_LEFT,-1,label.get_theme_font_size("font_size")).x
				check(width <= label.size.x,"KE unabridged metadata fits: "+label.text)
			check(card.difficulty.position.x+card.difficulty.size.x+9*app.ui_scale <= card.mode_tip.position.x,"KU-A single-line difficulty and mode never overlap")
			check(card.dimensions.position.y == card.difficulty.position.y and card.mode_tip.position.y == card.dimensions.position.y,"KU-A metadata shares one row")
			check(card.dimensions.position.x+card.dimensions.size.x < card.difficulty_icon.position.x and card.difficulty_icon.position.x+card.difficulty_icon.size.x < card.difficulty.position.x,"KU-A dimension, filled circle and text have distinct gaps")
			check(card.note.position.y == card.leaf.position.y and card.status_icon.kind == card.note.text,"KU-A footer status drawing matches label")
			check(card.note.horizontal_alignment == HORIZONTAL_ALIGNMENT_RIGHT and is_equal_approx(card.note.position.x+card.note.size.x,card.size.x-roundf(10*app.ui_scale)),"KU-A status group ends at the shared right inset")
			check(card.size.x >= card.minimum_card_width(app.ui_scale),"KU-A measured common width is respected")
			var marks := Rect2()
			var first_point: bool = true
			for pencil: Node2D in card.mode_icon.pencils:
				if not pencil.visible: continue
				for vertex: Vector2 in pencil.body.polygon:
					var point: Vector2 = pencil.to_global(vertex)-card.mode_icon.global_position
					if first_point: marks = Rect2(point,Vector2.ZERO); first_point = false
					else: marks = marks.expand(point)
			check(not first_point and marks.get_center().distance_to(card.mode_icon.size/2) < 0.1 and is_equal_approx(maxf(marks.size.x,marks.size.y),30*app.ui_scale),"KU-A actual pencil polygons are centred and enlarged to 30 logical pixels")
			check(card.accessibility_name.contains(card.difficulty.text) and not card.accessibility_name.contains("Motiv"),"KE accessible metadata remains spoiler-free")
			check(card.note.get_theme_font("font").get_string_size("Begonnen",HORIZONTAL_ALIGNMENT_LEFT,-1,card.note.get_theme_font_size("font_size")).x <= card.note.size.x,"KE longest status fits without clipping")
			kk_measurements.append({"ku_surface":spec,"card_width":card.size.x,"minimum_width":card.minimum_card_width(app.ui_scale),"metadata_widths":card.metadata_widths(app.ui_scale),"label":card.difficulty.text,"circle_color":card.difficulty_icon.ink_color.to_html(false),"strip":card.label_area,"footer_y":card.note.position.y})
		check(app.choices[1].difficulty.text == "Sehr leicht" and app.choices[5].difficulty.text == "Sehr schwer","KU-A full scale without numbers survives UI rebuilds")
		await shot("labels-%d-ui%d" % [spec[0],roundi(float(spec[2])*100)])
		var first: Card = app.choices[0]
		var unknown_pixels: PackedByteArray = await button_pixels(first.unknown)
		first.preview.width = app.choices[1].preview.width
		first.preview.height = app.choices[1].preview.height
		first.layout_content()
		check(unknown_pixels == await button_pixels(first.unknown),"KE unknown drawing is invariant under distinct puzzle dimensions")
		# All assessment shapes use the same tooltip-free label, including native
		# Label's fallback for clipped text. These mutations are synthetic only.
		for value: Variant in [null,app.album.metadata["T-09"].difficulty,{"method":"picross-difficulty-0.1","level":"L5","assessment_type":"editorial_estimate","confidence":"low","plausible_range":["L1","L5"],"r4_required":false},{"method":"picross-difficulty-0.2","level":"L5","assessment_type":"instrumented","confidence":"medium","plausible_range":["L5","L5"],"r4_required":true},{"method":"picross-difficulty-0.3","level":"L5","assessment_type":"instrumented","confidence":"medium","plausible_range":["L5","L5"],"r4_required":true}]:
			first.set_metadata(50,50,false,value)
			await frames()
			await RenderingServer.frame_post_draw
			var expected_color: Color = Color("85857f") if value == null else Color({"L1":"52734e","L2":"74713e","L3":"997337","L4":"a36342","L5":"9b514b"}[value.level])
			var center_pixel: Color = surface.get_texture().get_image().get_pixelv(Vector2i(first.difficulty_icon.get_global_rect().get_center()))
			check(center_pixel.is_equal_approx(expected_color),"KU-A filled circle has the prescribed native centre pixel")
			await hover(first.caption)
			for part: Control in [first.difficulty_icon,first.difficulty]:
				await hover(part)
				await create_timer(0.8).timeout
				check(visible_popups() == 0 and first.difficulty.tooltip_text.is_empty() and first.difficulty.get_tooltip().is_empty() and first.tooltip_ref == null,"KU-A actual circle/text hover has no popup, including native fallback")
			if value != null and value.method == "picross-difficulty-0.3" and value.r4_required:
				await shot("no-tooltip-%d-ui%d" % [spec[0],roundi(float(spec[2])*100)])
			app.set_ui_scale(1.0 if app.ui_scale == 1.25 else 1.25)
			await frames()
			app.set_ui_scale(float(spec[2]))
			await frames()
			first = app.choices[0]
		check(card_geometry() == geometry,"KE metadata and UI roundtrip preserve all rectangles")
		await hover(first.mode_tip)
		await create_timer(0.8).timeout
		check(first.mode_tip.tooltip_ref != null and first.mode_tip.tooltip_ref.get_ref() != null,"KE native mode tooltip")
		for part: String in ["dimensions","difficulty_icon","difficulty","mode_tip","paper","leaf","status_icon","note"]:
			click(app.choices[0].get(part))
			await frames()
			check(app.work.visible and app.session.definition.id == "T-01","KE passive label click opens owning card: "+part)
			app.show_album()
			await frames()
	# Cross actual column thresholds, rather than assuming the old 228px grid.
	var previous_columns: int = 0
	var transitions: int = 0
	for width: int in range(1280,1921,16):
		surface.size = Vector2i(width,1080)
		await frames()
		if previous_columns > 0 and app.album.grid.columns != previous_columns: transitions += 1
		previous_columns = app.album.grid.columns
		for card: Card in app.choices:
			check(card.size == app.choices[0].size and card.size.x >= card.minimum_card_width(app.ui_scale),"KU-A column transition preserves shared measured geometry")
	check(transitions > 0,"KU-A resize crosses a new column threshold")
	# Wrong own fill, X-only and redo-only are deliberately distinct from Neu.
	var item: Session = app.sessions[0]
	item.gesture.begin(item.player,Vector2i(0,0),1)
	item.finish()
	app.show_album()
	await frames()
	check(app.choices[0].note.text == "Begonnen" and not app.choices[0].unknown.visible and app.choices[0].preview.cells == item.player.cells and item.player.cells[0] != item.definition.solution[0][0],"KE wrong own fill stays uncorrected and hides question mark")
	var filled: PackedByteArray = await button_pixels(app.choices[0].preview)
	item.player.undo()
	app.show_album()
	await frames()
	var empty: PackedByteArray = await button_pixels(app.choices[0].preview)
	check(empty != filled and app.choices[0].note.text == "Begonnen" and not app.choices[0].unknown.visible,"KE undo leaves empty begun preview, never question mark")
	item.gesture.begin(item.player,Vector2i(0,0),0)
	item.finish()
	app.show_album()
	await frames()
	check(empty == await button_pixels(app.choices[0].preview) and not app.choices[0].unknown.visible,"KE X-only preview is neutral like empty begun preview")
	await shot("x-only")

func fixed_cards() -> void:
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
		surface.size = Vector2i(spec[0],spec[1])
		app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		app.set_ui_scale(float(spec[2]))
		await frames()
		var initial: Array = card_geometry()
		var u: float = app.ui_scale
		for card: Control in app.choices:
			check(card.size == app.choices[0].size and card.get_parent().size == app.choices[0].get_parent().size,"KK shared actual card AND grid cell dimensions")
			check(card.caption.text == "???" and card.text.is_empty(),"KK only neutral question marks; no native hidden caption")
			check(card.caption.get_theme_font("font") == app.WORK_TITLE_FONT and card.caption.get_theme_font_size("font_size") < app.title.get_theme_font_size("font_size"),"KK original smaller Bakso role")
			check(card.caption.max_lines_visible == 2 and card.caption.text_overrun_behavior == TextServer.OVERRUN_TRIM_ELLIPSIS,"KK two-line bounded ellipsis")
			check(not card.reset.visible and card.reset.focus_mode == Control.FOCUS_NONE,"KK new reset invisible and unfocusable")
			check(card.find_children("play-*","Button",true,false).is_empty(),"KK play control, hit and focus station absent")
			check(card.label_area.end.y < card.leaf.position.y and card.note.position.y == card.leaf.position.y and card.leaf.position.x+card.leaf.size.x < card.status_icon.position.x,"KU-A status and stable leaf share footer below metadata")
			check(card.image_area.encloses(Rect2(card.preview.position,card.preview.size)),"KK proportional own preview inside fixed area")
			check(is_equal_approx(card.preview.size.x/card.preview.size.y,float(card.preview.width)/card.preview.height),"KK own preview preserves aspect")
		await shot("new-%d" % spec[0])
		# Actual validated empty save stays new, while the same slot's redo-only
		# history stays begun. The native card controls are rebuilt in each step.
		check(app._save_current(),"KK valid empty save written")
		app.show_album()
		await frames()
		check(card_geometry() == initial and not app.album.reset_buttons["T-01"].visible,"KK empty save never changes geometry or reset visibility")
		click(app.choices[0])
		await frames()
		click_at(app.board.global_position+app.board.view.cell_rect(Vector2i(2,0)).get_center())
		click(app.undo_button)
		click(app.album_button)
		await frames()
		check(card_geometry() == initial and app.choices[0].note.text == "Begonnen" and app.choices[0].reset.visible,"KK pointer edit/undo changes status but no rectangles")
		check(app.album.previews[0].cells == app.sessions[0].player.cells and app.album.reveals[0].payload.is_empty(),"KK uncorrected own state and no early reveal")
		await shot("begun-%d" % spec[0])
		# Finish the fixed synthetic input via the normal Session boundary.
		var item: Session = app.sessions[0]
		for y: int in range(item.player.height):
			for x: int in range(item.player.width):
				if int(item.definition.solution[y][x]) > 0:
					item.gesture.begin(item.player,Vector2i(x,y),int(item.definition.solution[y][x]))
					item.finish()
		check(item.completed and app.store.write_slot(item,item.view_state).is_empty(),"KK synthetic completion validated and saved")
		app.show_album()
		await frames()
		check(card_geometry() == initial and app.choices[0].caption.text == item.definition.reveal.name,"KK completion adds earned title without moving following rows")
		check(app.choices[0].note.text == "Gelöst" and app.choices[0].status_icon.kind == "Gelöst","KU-A validated completion selects the check-mark drawing")
		var check_pixels: PackedByteArray = await button_pixels(app.choices[0].status_icon)
		app.choices[0].status_icon.kind = "test-only-no-symbol"
		app.choices[0].status_icon.queue_redraw()
		check(check_pixels != await button_pixels(app.choices[0].status_icon),"KU-A solved check mark really contributes native pixels")
		app.choices[0].status_icon.kind = "Gelöst"
		app.choices[0].status_icon.queue_redraw()
		await shot("solved-%d" % spec[0])
		for aspect: Vector2i in [Vector2i(320,80),Vector2i(80,320)]:
			var image: Image = Image.create(aspect.x,aspect.y,false,Image.FORMAT_RGBA8)
			image.fill(Color("376a60"))
			app.choices[0].picture.artwork = ImageTexture.create_from_image(image)
			app.choices[0].picture.queue_redraw()
			await frames()
			var fitted: Rect2 = app.choices[0].picture.artwork_rect()
			check(Rect2(Vector2.ZERO,app.choices[0].picture.size).encloses(fitted) and is_equal_approx(fitted.size.x/fitted.size.y,float(aspect.x)/aspect.y),"KK wide/tall earned image fits completely without distortion")
			check(card_geometry() == initial,"KK image aspect never changes grid geometry")
			kk_measurements.append({"surface":spec,"artwork_size":aspect,"fitted":fitted})
		item.definition.reveal.name = "TEST ONLY Ein außerordentlich langer verdienter Motivname mit Umlauten und mehr als zwei möglichen Zeilen ohne Änderung der Kachelgeometrie"
		app.show_album()
		await frames()
		check(card_geometry() == initial and app.choices[0].caption.get_line_count() > 2 and app.choices[0].caption.get_visible_line_count() == 2,"KK long name overflows exactly the reserved two lines")
		check(app.choices[0].accessibility_name.contains(item.definition.reveal.name),"KK full earned name remains accessible")
		var category_name: String = app.album.categories[0].name
		app.album.categories[0].name = "Äußerst lange technische Kategorienbezeichnung ".repeat(3).left(128)
		app.album._render(0)
		await frames()
		check(card_geometry() == initial and app.choices[0].detail.get_visible_line_count() <= 2,"KK legal 128-character category cannot grow metadata or grid")
		app.album.categories[0].name = category_name
		app.album._render(0)
		await frames()
		var card: Control = app.choices[0]
		await hover(card.caption)
		await create_timer(0.8).timeout
		check(card.tooltip_text.is_empty() and card.tooltip_ref == null and card.caption.get_tooltip().is_empty() and card.picture.get_tooltip().is_empty(),"KK actual card hover has no tooltip")
		await hover(card.reset)
		await create_timer(0.8).timeout
		var tip: Control = card.reset.tooltip_ref.get_ref() if card.reset.tooltip_ref != null else null
		check(tip != null and tip.is_visible_in_tree() and card.reset.tooltip_text == "Rätsel zurücksetzen","KK real reset hover retains tooltip")
		await shot("long-name-%d" % spec[0])
		app.set_ui_scale(1.0 if u == 1.25 else 1.25)
		await frames()
		check(tip == null or not is_instance_valid(tip) or not tip.is_visible_in_tree(),"KK UI change dismisses existing reset popup")
		app.set_ui_scale(u)
		await frames()
		check(card_geometry() == initial,"KK UI roundtrip restores exact rectangles")
		await choose("fahrzeuge-verkehr")
		check(app.choices[0].size == initial[0].card.size and app.choices[0].image_area == initial[0].image and Rect2(app.choices[0].note.position,app.choices[0].note.size) == initial[0].status,"KK category removal reserves same metadata/image/footer space")
		var foreign: Dictionary = save_bytes("t01")
		click(app.album.reset_buttons["T-01"])
		await frames()
		check(app.reset_dialog.visible and app.reset_id == "T-01" and app.album.visible,"KK reset pointer never also opens earned card")
		# While modal, change the underlying filter directly: the bound ID must
		# survive; this is a target-stability counterexample, not a pointer claim.
		app.album.choose_category("voegel")
		click(app.reset_dialog.get_ok_button())
		await frames()
		check(app.album.visible and not app.sessions[0].completed and save_bytes("t01") == foreign,"KK confirmed catalog reset remains catalog and owns only captured slot")
		await choose("")
		check(card_geometry() == initial and app.choices[0].caption.text == "???" and not app.choices[0].reset.visible,"KK reset returns exact original geometry with no stale hit")
		await shot("reset-%d" % spec[0])
		kk_measurements.append({"surface":spec,"initial":initial,"after_reset":card_geometry(),"columns":app.album.grid.columns})
	await recovery_pointer_cases()
	# A small resize band crosses real column thresholds, no content-dependent
	# width/height response or horizontal catalogue scroll is allowed.
	for width: int in [1279,1281,1599,1601,1919,1921]:
		surface.size = Vector2i(width,1080)
		app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await frames()
		for card: Control in app.choices: check(card.size == app.choices[0].size,"KK resize has one shared geometry")
		check(app.album.grid.size.x <= app.album.scroll.size.x and app.album.scroll.scroll_horizontal == 0,"KK column boundary has no horizontal scroll")
		kk_measurements.append({"resize_width":width,"columns":app.album.grid.columns,"geometry":card_geometry()})
	await empty_write_error()

func pointer_button(point: Vector2, button: MouseButton, down: bool, mask: int = 0) -> void:
	var event: InputEventMouseButton = InputEventMouseButton.new()
	event.position = point
	event.global_position = point
	event.button_index = button
	event.button_mask = mask
	event.pressed = down
	surface.push_input(event, true)

func pointer_move(from: Vector2, to: Vector2, mask: int = 0) -> void:
	var motion: InputEventMouseMotion = InputEventMouseMotion.new()
	motion.position = to
	motion.global_position = to
	motion.relative = to-from
	motion.button_mask = mask
	surface.push_input(motion, true)

func recovery_pointer_cases() -> void:
	var stable: Array = card_geometry()
	var counts: Dictionary = {"open":0,"reset":0,"repair":0,"id":""}
	app.album.opened.connect(func(id: String) -> void: counts.open += 1; counts.id = id)
	app.album.reset_requested.connect(func(id: String) -> void: counts.reset += 1; counts.id = id)
	app.album.repair_requested.connect(func(id: String) -> void: counts.repair += 1; counts.id = id)
	for state: String in ["error","recovered","backup_invalid"]:
		app.slot_status[0] = state
		var display_errors: Array[String] = app.slot_errors.duplicate()
		display_errors[0] = "TEST ONLY ausführliche Dateidiagnose. ".repeat(30)
		# Long text is a presentation fixture, not pending unsaved work.
		app.album.present(app.sessions,app.slot_status,display_errors,"","T-01")
		await frames()
		var card: Card = app.choices[0]
		check(card.recovery.mouse_filter == Control.MOUSE_FILTER_STOP and card.recovery_content.mouse_filter == Control.MOUSE_FILTER_PASS,"KK "+state+": wheel ownership and text click routing stay explicitly separated")
		check(card_geometry() == stable,"KK "+state+": fixed card and grid geometry")
		check(card.reset.visible and card.recovery.visible,"KK "+state+": reset and diagnosis visible")
		check(card.note.text == ("Ungültig" if state == "error" else "Neu"),"KK "+state+": short validated progress")
		check(card.diagnosis.text.contains("TEST ONLY"),"KK "+state+": complete storage diagnosis")
		check(card.diagnosis.get_line_count() > 2,"KK "+state+": long diagnosis wraps")
		var bar: VScrollBar = card.recovery.get_v_scroll_bar()
		var inner_range: float = bar.max_value-bar.page
		check(bar.visible and inner_range > 0,"KK "+state+": real inner scroll range")
		var point: Vector2 = card.recovery.get_global_rect().position + Vector2(10,10)
		var outer_before: int = app.album.scroll_vertical
		var opened_before: int = counts.open
		var repaired_before: int = counts.repair
		# Wheel down AND up: an unmatched down retains Viewport mouse capture,
		# routing the next action to the old content even at correct coordinates.
		click_at(point,MOUSE_BUTTON_WHEEL_DOWN)
		await frames()
		var wheel_after: int = card.recovery.scroll_vertical
		check(wheel_after > 0,"KK "+state+": wheel scrolls inside bounded diagnosis")
		check(app.album.scroll_vertical == outer_before,"KK "+state+": inner wheel keeps outer scroll")
		check(counts.open == opened_before and counts.repair == repaired_before and counts.reset == 0,"KK "+state+": wheel emits no card action")
		# A text drag out and back must not turn into a neutral click.
		pointer_move(point,point)
		pointer_button(point,MOUSE_BUTTON_LEFT,true,MOUSE_BUTTON_MASK_LEFT)
		pointer_move(point,point+Vector2(30,0),MOUSE_BUTTON_MASK_LEFT)
		pointer_move(point+Vector2(30,0),point,MOUSE_BUTTON_MASK_LEFT)
		pointer_button(point,MOUSE_BUTTON_LEFT,false)
		await frames()
		check(counts.open == opened_before,"KK "+state+": returning text drag never opens card")
		# Scroll down and back during a held left click. Equal final offset does
		# not make this a neutral click; the scroll gesture must cancel activation.
		pointer_button(point,MOUSE_BUTTON_LEFT,true,MOUSE_BUTTON_MASK_LEFT)
		for wheel: MouseButton in [MOUSE_BUTTON_WHEEL_DOWN,MOUSE_BUTTON_WHEEL_UP]:
			pointer_button(point,wheel,true,MOUSE_BUTTON_MASK_LEFT)
			pointer_button(point,wheel,false,MOUSE_BUTTON_MASK_LEFT)
			await frames()
		pointer_button(point,MOUSE_BUTTON_LEFT,false)
		await frames()
		check(counts.open == opened_before,"KK "+state+": wheel during held click cancels opening even after reverse scroll")
		# Native scrollbar page-click and thumb drag use their own hit targets.
		card.recovery.scroll_vertical = 0
		await frames()
		var bar_point: Vector2 = bar.get_global_rect().position + Vector2(bar.size.x/2,bar.size.y*0.65)
		click_at(bar_point)
		await frames()
		check(card.recovery.scroll_vertical > 0,"KK "+state+": scrollbar track really scrolls")
		check(counts.open == opened_before and counts.repair == repaired_before,"KK "+state+": scrollbar track never activates card or repair")
		card.recovery.scroll_vertical = 0
		await frames()
		var arrow_height: float = bar.get_theme_icon("decrement").get_height()
		var grabber_height: float = bar.get_theme_stylebox("grabber").get_minimum_size().y
		bar_point = bar.get_global_rect().position + Vector2(bar.size.x/2,arrow_height+grabber_height/2)
		var drag_before: int = card.recovery.scroll_vertical
		pointer_move(point,bar_point)
		pointer_button(bar_point,MOUSE_BUTTON_LEFT,true,MOUSE_BUTTON_MASK_LEFT)
		check(card.recovery.scroll_vertical == drag_before,"KK "+state+": thumb down itself does not page scroll")
		pointer_move(bar_point,bar_point+Vector2(0,bar.size.y*0.45),MOUSE_BUTTON_MASK_LEFT)
		pointer_button(bar_point+Vector2(0,bar.size.y*0.45),MOUSE_BUTTON_LEFT,false)
		await frames()
		check(card.recovery.scroll_vertical > 0,"KK "+state+": scrollbar drag really scrolls")
		check(counts.open == opened_before and counts.repair == repaired_before,"KK "+state+": scrollbar drag never activates card or repair")
		card.recovery.scroll_vertical = 0
		await frames()
		check(card.recovery.scroll_vertical == 0,"KK "+state+": restore capture scroll")
		if state != "error":
			check(app.album.repair_buttons.has("T-01"),"KK "+state+": text recovery action retained")
			card.recovery.ensure_control_visible(card.repair)
			await frames()
			check(card.recovery.get_global_rect().encloses(card.repair.get_global_rect()),"KK "+state+": scrolled repair pointer target fully inside clip")
			click(card.repair)
			await frames()
			check(app.repair_dialog.visible,"KK "+state+": repair pointer opens confirmation")
			check(app.repair_id == "T-01" and counts.id == "T-01" and counts.repair == repaired_before+1,"KK "+state+": repair emits once for stable registry ID")
			check(counts.open == opened_before and app.album.visible,"KK "+state+": repair keeps catalog and never opens card")
			check(not app.work.visible and not app.ending.visible,"KK "+state+": repair opens neither work nor ending")
			var before_cancel: Dictionary = save_bytes()
			if app.repair_dialog.visible:
				click(app.repair_dialog.get_cancel_button())
				await frames()
			check(not app.repair_dialog.visible and save_bytes() == before_cancel,"KK "+state+": repair cancellation preserves bytes")
		await shot(state)
		# Neutral text after inner scrolling opens valid cards once; the invalid
		# card remains blocked. Keep capture state independent from navigation.
		card.recovery.scroll_vertical = 30
		await frames()
		click_at(point)
		await frames()
		check(counts.open == opened_before+(0 if state == "error" else 1),"KK "+state+": neutral diagnosis click respects validity")
		if state != "error":
			check(counts.id == "T-01" and app.work.visible and not app.album.visible,"KK "+state+": neutral click opens bound new slot")
			# Synthetic long diagnostics are display fixtures, not disk corruption.
			# Remove only this fixture state before returning through normal flush.
			app.slot_status[0] = "fresh"
			app.slot_errors[0] = ""
			click(app.album_button)
			await frames()
		check(app.album.visible,"KK "+state+": catalog remains or returns after neutral click")
		kk_pointer_measurements.append({"state":state,"inner_range":inner_range,"wheel_after":wheel_after,"outer_before":outer_before,"counts":counts.duplicate(),"neutral_point":point,"scrollbar_thumb_point":bar_point})
	app.slot_status[0] = "fresh"
	app.slot_errors[0] = ""
	app.show_album()
	await frames()

func empty_write_error() -> void:
	# A separate empty profile exercises the real SaveStore failure path without
	# inheriting pointer capture, synthetic recovery status or history.
	Store.test_root_override = Store.test_root_override.path_join("empty-write-error")
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	await new_app()
	check(app.slot_status[0] == "fresh" and save_bytes().is_empty(),"KK runtime error starts with absent saves")
	app.store.fail_step = "after_temp"
	check(not app._save_current(),"KK empty slot real write fails before primary publication")
	await frames()
	var card: Card = app.choices[0]
	check(card.reset.visible and not card.reset.disabled,"KK empty write failure exposes enabled reset")
	check(card.note.text == "Neu" and app.session.player.history.is_empty() and not app.session.completed,"KK empty write failure never invents progress")
	check(card.recovery.visible and card.diagnosis.text.contains(app.slot_errors[0]) and not app.slot_errors[0].is_empty(),"KK empty write failure has actual storage diagnosis")
	check(app.album.feedback.visible and app.album.feedback.text.contains(app.slot_errors[0]),"KK empty write failure has global feedback")
	check(not FileAccess.file_exists(app.store.path_for("t01")) and FileAccess.file_exists(app.store.path_for("t01",".tmp")),"KK empty failed save has temp only")
	var original: Dictionary = save_bytes()
	var foreign: FileAccess = FileAccess.open(app.store.path_for("t02"),FileAccess.WRITE)
	foreign.store_buffer(FileAccess.get_file_as_bytes("res://tests/fixtures/runtime/t02.json"))
	foreign.close()
	var unaffected: Dictionary = save_bytes("t01")
	click(card.reset)
	await frames()
	check(app.reset_dialog.visible and app.reset_id == "T-01" and app.album.visible,"KK empty write failure reset pointer reaches bound confirmation")
	click(app.reset_dialog.get_cancel_button())
	await frames()
	check(save_bytes("t02") == original and save_bytes("t01") == unaffected,"KK empty write failure reset cancellation preserves all bytes")
	check(app.choices[0].reset.visible,"KK empty failed slot retains reset after cancellation")
	click(app.choices[1])
	await frames()
	check(app.album.visible and app.session.definition.id == "T-01" and not app.slot_errors[0].is_empty(),"KK empty write failure blocks slot switch on failed mandatory flush")
	click(app.choices[0].reset)
	await frames()
	check(app.reset_dialog.visible,"KK empty failed slot reset remains reachable after blocked switch")
	click(app.reset_dialog.get_ok_button())
	await frames()
	check(app.album.visible and app.slot_status[0] == "fresh" and app.slot_errors[0].is_empty(),"KK empty write failure confirmed reset restores fresh catalog state")
	check(save_bytes("t02").is_empty(),"KK empty write failure reset removes target primary backup and temp")
	check(save_bytes("t01") == unaffected,"KK empty write failure reset preserves foreign slot bytes")
	check(not app.choices[0].reset.visible and not app.choices[0].recovery.visible,"KK empty write failure reset clears diagnosis and reset hit")
	app.store.fail_step = ""

func compact_buttons() -> void:
	for spec: Array in [[1280,720,1.25],[1920,1080,1.0],[2560,1440,1.25]]:
		surface.size = Vector2i(spec[0],spec[1])
		app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		app.set_ui_scale(float(spec[2]))
		await frames()
		var u: float = app.ui_scale
		check(app.title.get_theme_font("font") == app.WORK_TITLE_FONT, "KB catalog uses original Bakso")
		var title_rid: RID = app.WORK_TITLE_FONT.get_rids()[0]
		for character: String in "Rätselkatalog":
			check(TextServerManager.get_primary_interface().font_has_char(title_rid,character.unicode_at(0)), "KB catalog title glyph bound offline: "+character)
		var widths: Array = []
		var interiors: Array = []
		for index: int in range(app.choices.size()):
			var card: Button = app.choices[index]
			var id: String = app.album.visible_ids[index]
			var reset: Button = app.album.reset_buttons[id]
			widths.append(card.size.x)
			check(card.size.x >= card.minimum_card_width(u) and card.size.x <= card.minimum_card_width(u)+16*u, "KU-A compact card follows measured metadata width")
			check(card.get_global_rect().encloses(reset.get_global_rect()), "KB icons inside card")
			check(reset.size.x >= 44*u and reset.size.y >= 44*u, "KB 44/55 pointer targets")
			check(reset.position == Vector2(card.size.x-roundf(10*u)-44*u,roundf(10*u)), "KK fixed top/right reset anchor")
			check(card.focus_mode == Control.FOCUS_ALL and reset.focus_mode == Control.FOCUS_NONE and not reset.visible, "KB catalog focus preserved")
			var labels: Array[Node] = card.find_children("*","Label",true,false)
			check(not labels[0].text.contains("×") and card.dimensions.text.count("×") == 1 and not card.detail.text.contains("×"), "KB dimensions exactly once")
			check(labels[0].get_global_rect().end.x <= reset.get_global_rect().position.x-7*u, "KB metadata does not enter actions")
			interiors.append({"card":region(card),"meta":region(labels[1]),"reset":region(reset),"preview":region(app.album.previews[index]),"status":region(app.album.notes[index])})
		check(app.album.grid.size.x <= app.album.scroll.size.x and app.album.scroll.scroll_horizontal == 0, "KB no horizontal overflow")
		check(app.album.grid.columns > 4 if spec[0] >= 1920 else app.album.grid.columns >= 2, "KB responsive columns without four-column cap")
		kb_measurements.append({"surface":spec,"columns":app.album.grid.columns,"widths":widths,"interiors":interiors})
		await shot("compact-%d-ui%d" % [spec[0],spec[2]*100])
		await choose("voegel")
		check(app.choices.size() == 1 and app.choices[0].size.x <= app.choices[0].minimum_card_width(u)+16*u, "KU-A single filtered card stays at common compact width")
		await choose("")
	# Return to a normal frame and exercise real down/up actions independently.
	surface.size = Vector2i(1920,1080)
	app.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	app.set_ui_scale(1.0)
	await frames()
	var counts: Dictionary = {"open":0,"reset":0,"repair":0}
	app.album.opened.connect(func(_id: String) -> void: counts.open += 1)
	app.album.reset_requested.connect(func(_id: String) -> void: counts.reset += 1)
	app.album.repair_requested.connect(func(_id: String) -> void: counts.repair += 1)
	check(app.choices[0].accessibility_name.contains("Spielen") and not app.album.reset_buttons["T-01"].visible, "KK fresh card action and hidden reset")
	click(app.choices[0])
	await frames()
	check(counts.open == 1 and counts.reset == 0 and app.work.visible, "KK card opens once through pointer")
	# ZR: a grid-origin up over a tool must not activate that button.
	var start: Vector2 = app.board.global_position+app.board.view.cell_rect(Vector2i(2,0)).get_center()
	var down: InputEventMouseButton = InputEventMouseButton.new()
	down.position = start; down.button_index = MOUSE_BUTTON_LEFT; down.pressed = true
	surface.push_input(down,true)
	var up: InputEventMouseButton = InputEventMouseButton.new()
	up.position = app.undo_button.get_global_rect().get_center(); up.button_index = MOUSE_BUTTON_LEFT
	surface.push_input(up,true)
	await frames()
	check(app.session.player.cursor == 1 and app.session.player.history.size() == 1, "KB ZR release over Undo commits once without undo")
	click(app.album_button)
	await frames()
	check(app.choices[0].accessibility_name.contains("Fortsetzen"), "KK begun action label")
	var original: Dictionary = save_bytes()
	click(app.album.reset_buttons["T-01"])
	await frames()
	check(counts == {"open":1,"reset":1,"repair":0} and app.reset_dialog.visible and app.album.visible and save_bytes() == original, "KK reset emits only reset and writes nothing before confirmation")
	click(app.reset_dialog.get_cancel_button())
	await frames()
	check(save_bytes() == original and app.album.visible, "KK reset cancellation inert")
	click(app.choices[0])
	await frames()
	for id: String in app.TOOL_IDS:
		var tool: Control = app.actions[id]
		check(tool.size == Vector2(44,44), "KB work targets retain exact sidebar geometry")
		if id in ["fill","undo","minus"]: check(tool.position.x == app.actions.fill.position.x, "KB left tool column")
		else: check(tool.position.x > app.actions.fill.position.x, "KB right tool column")
	click(app.undo_button)
	click(app.redo_button)
	click(app.actions.erase)
	check(app.board.eraser, "KB eraser remains usable")
	click(app.actions.fill)
	check(not app.board.eraser, "KB fill remains usable")
	click(app.actions.minus)
	click(app.actions.plus)
	# Actual rendered state differences and stable repeated ink.
	var tool: Button = app.actions.fill
	tool.selected = false
	tool.release_focus()
	await hover(app.actions.menu)
	var normal: PackedByteArray = await button_pixels(tool)
	var repeat: PackedByteArray = await button_pixels(tool)
	check(normal == repeat, "KB contour stable across redraws")
	await hover(tool)
	check(normal != await button_pixels(tool), "KB native hover visible")
	var held: InputEventMouseButton = InputEventMouseButton.new()
	held.position = tool.get_global_rect().get_center(); held.button_index = MOUSE_BUTTON_LEFT; held.pressed = true
	surface.push_input(held,true)
	check(tool.is_pressed() and normal != await button_pixels(tool), "KB native pressed visible")
	held = held.duplicate(); held.pressed = false
	surface.push_input(held,true)
	tool.release_focus()
	tool.selected = false
	await hover(app.actions.menu)
	tool.selected = true
	check(normal != await button_pixels(tool), "KB programmatic selected immediately redraws")
	tool.selected = false
	tool.disabled = true
	check(normal != await button_pixels(tool), "KB programmatic disabled immediately redraws")
	tool.disabled = false
	tool.grab_focus()
	check(normal != await button_pixels(tool), "KB native focus visible")
	await shot("work-focus")
	tool.release_focus()
	# Native tooltip creation, clamping and dismissal across an information switch.
	tool.tooltip_text = "Lange technische Prüfbeschriftung mit Umlauten: Rätsel zurücksetzen, Änderungen bestätigen und zum ursprünglichen Arbeitsstand zurückkehren."
	await hover(tool)
	await create_timer(0.8).timeout
	var tip: Control = tool.tooltip_ref.get_ref() if tool.tooltip_ref != null else null
	check(tip != null and tip.is_visible_in_tree(), "KB tooltip created through real hover")
	if tip != null:
		var popup: Window = tip.get_window()
		check(Rect2(Vector2.ZERO,Vector2(surface.size)).encloses(Rect2(Vector2(popup.position),Vector2(popup.size))), "KB complete tooltip fits client")
		kb_measurements.append({"tooltip_position":popup.position,"tooltip_size":popup.size,"scale":app.ui_scale})
		await shot("tooltip")
	click(app.actions.menu)
	await frames()
	check(app.information.visible and (tip == null or not is_instance_valid(tip) or not tip.is_visible_in_tree()), "KB switch dismisses stale tooltip")
	click(app.actions["nav-work"])
	click(app.album_button)
	await frames()
	check(app.title.get_theme_font("font") == app.WORK_TITLE_FONT, "KB Bakso preserved after Work/Info return")
	for u: float in [1.25,1.0]:
		app.set_ui_scale(u)
		await frames()
		check(app.album.reset_buttons["T-01"].size == Vector2.ONE*44*u, "KB UI roundtrip has no stale button minima")
