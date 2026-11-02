extends SceneTree
## B-B: real product root, isolated synthetic registry and actual filesystem.
const Book = preload("res://book/main.gd")
const Store = preload("res://model/save_store.gd")
const Registry = preload("res://model/content_registry.gd")
var book: Book
var assertions: Array = []
var output: String

func _initialize() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
	assertions.append({"label":label,"passed":ok})
	if not ok: print("BOOK_INTEGRATION_FAIL ",label)

func frames(count: int = 3) -> void:
	for i: int in range(count): await process_frame

func settled() -> void:
	var deadline: int = Time.get_ticks_msec()+8000
	while (book.state in [Book.State.PREPARING,Book.State.OPENING] or book.release_barrier) and Time.get_ticks_msec() < deadline:
		await process_frame
	check(book.state not in [Book.State.PREPARING,Book.State.OPENING] and not book.release_barrier,"bounded motion settled")
	await frames()

func bytes(path: String) -> PackedByteArray:
	return FileAccess.get_file_as_bytes(path) if FileAccess.file_exists(path) else PackedByteArray()

func run() -> void:
	output = OS.get_environment("BOOK_INTEGRATION_OUTPUT")
	if output.is_empty():
		push_error("Isolated output required")
		quit(4)
		return
	Store.test_root_override = output.path_join("saves")
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	var frozen: PackedByteArray = FileAccess.get_file_as_bytes("res://tests/book-save-v1.json")
	var seed: Store = Store.new(Store.test_root_override)
	var frozen_path: String = seed.path_for("t02")
	var seed_file := FileAccess.open(frozen_path,FileAccess.WRITE)
	seed_file.store_buffer(frozen)
	seed_file.close()
	root.size = Vector2i(1920,1080)
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames()
	var app = book.app
	check(book.get_script().resource_path == "res://book/main.gd" and app.store.get_script() == Store,"regular root and real SaveStore")
	check(app.catalog_error.is_empty() and app.sessions.size() > 1 and app.album.visible,"regular registry starts catalog")
	check(app.album.preference.path == "user://p1/catalog-preference.json","unchanged preference identity")
	var first: String = str(app.sessions[0].definition.id)
	var other: String = str(app.sessions[1].definition.id)
	var frozen_data: Dictionary = JSON.parse_string(frozen.get_string_from_utf8())
	# Compare JSON values: parsing produces floats while the player deliberately
	# restores typed integer arrays. No numeric tolerance or omitted fields.
	check(JSON.parse_string(JSON.stringify(Store.snapshot(app.sessions[1],app.sessions[1].view_state))) == frozen_data,"frozen schema1 history redo and view load exactly")
	check(book.request_open(first),"valid opening accepted")
	await settled()
	check(book.state == Book.State.WORK and app.session.definition.id == first and app.work.visible,"opening reaches bound work")
	var save: String = app.store.path_for(app.store.key_for_definition(first))
	check(not FileAccess.file_exists(save),"opening/capture creates no save")
	# The filesystem hook fails after validated temp bytes, before primary commit.
	app.store.fail_step = "after_temp"
	app.session.player.commit([{"index":0,"before":-1,"after":1}])
	check(not app._save_current(),"actual filesystem failure reported")
	var pending: Dictionary = Store.snapshot(app.session,app.session.view_state)
	var serial: int = book.generation
	check(not book.request_return() and book.state == Book.State.WORK and book.generation == serial,"failed flush blocks return before preparation")
	check(not book.information_routes.request("settings") and app.work.visible,"failed flush blocks information before preparation")
	app.leave_app()
	await frames()
	check(app.work.visible and app.save_retry.visible and not app.save_error.is_empty(),"failed quit stays usable with retry")
	check(not FileAccess.file_exists(save) and Store.snapshot(app.session,app.session.view_state) == pending,"failed navigation preserves pending state and primary bytes")
	app.store.fail_step = ""
	app.save_retry.pressed.emit()
	await frames()
	check(app.save_error.is_empty() and FileAccess.file_exists(save),"visible retry commits real slot")
	var committed: PackedByteArray = bytes(save)
	check(book.request_return(),"return after retry accepted")
	await settled()
	check(bytes(save) == committed and book.state == Book.State.CATALOG,"capture and return do not rewrite save")
	check(book.request_open(other),"second valid slot accepted")
	var restored: Dictionary = app.board.capture_view()
	check(restored.tool == "erase" and restored.active_color == 2 and restored.zoom == 18 and restored.row_clue_reads[35].anchor == "outer_start" and restored.column_clue_reads[21].anchor == "outer_start","frozen tool color zoom and clue anchors survive activation")
	var old_generation: int = book.generation
	book.interrupt("leave")
	await frames()
	check(book.state == Book.State.CATALOG and app.session.definition.id == first,"cancelled opening restores source binding")
	book._focus_interrupt(old_generation)
	check(book.generation != old_generation and book.capture == null,"stale callback cannot revive capture")
	check(bytes(frozen_path) == frozen,"passive opening preserves frozen save bytes")
	await settled()
	check(book.request_open(other),"opening before wrong-ID negative control")
	app._bind_session(int(app.session_indices[first]))
	await frames()
	check(book.state == Book.State.CATALOG and app.session.definition.id == first and book.capture == null and not app.presentation_locked,
		"wrong session ID invalidates pending capture")
	await settled()
	var index: int = int(app.session_indices[other])
	app.slot_status[index] = "error"
	check(not book.request_open(other) and app.session.definition.id == first,"invalid save blocks only its slot")
	check(book.request_open(first),"unrelated valid slot still opens")
	await settled()
	check(bytes(save) == committed,"switching leaves unrelated bytes unchanged")
	check(book.information_routes.request("settings"),"work information accepts durable origin")
	await settled()
	app.set_ui_scale(1.25)
	check(book.information_routes.request("help"),"settings to help")
	await settled()
	check(book.information_routes.request_return(),"information returns to bound work")
	await settled()
	check(app.ui_scale == 1.25 and app.session.definition.id == first and bytes(save) == committed,"options survive without transient camera save")
	check(book.request_return(),"final work return")
	await settled()
	book.free()
	await frames()
	# Backup-only compatibility never silently publishes a missing primary.
	Store.test_root_override = output.path_join("recovery")
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	seed = Store.new(Store.test_root_override)
	seed_file = FileAccess.open(seed.path_for("t02",".bak"),FileAccess.WRITE)
	seed_file.store_buffer(frozen)
	seed_file.close()
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames()
	app = book.app
	check(app.slot_status[1] == "recovered" and not FileAccess.file_exists(seed.path_for("t02")),"backup-only load stays write blocked")
	check(book.request_open(other),"backup can be viewed")
	await settled()
	check(not app._save_current(),"backup-only write requires confirmation")
	app.leave_app()
	await frames()
	check(bytes(seed.path_for("t02",".bak")) == frozen and not FileAccess.file_exists(seed.path_for("t02")) and app.work_repair_button.visible,"backup-only quit preserves bytes and exposes recovery")
	app._ask_repair_id(other)
	app.album.selected_id = first
	app.repair_dialog.hide()
	app.repair_dialog.confirmed.emit()
	await frames()
	check(seed.load_slot(app.sessions[1].definition).status == "loaded" and not FileAccess.file_exists(seed.path_for("t01")),"confirmed recovery remains ID bound")
	book.free()
	await frames()
	# Fresh product lifecycle with no session: both valid empty and invalid data.
	var registry: Dictionary = Registry.cached.duplicate(true)
	for invalid: bool in [false,true]:
		Registry.cached = registry.duplicate(true)
		Registry.cached.entries = []
		Registry.load_error = "synthetic invalid registry" if invalid else ""
		book = load("res://main.tscn").instantiate()
		root.add_child(book)
		await frames()
		check(book.app.session == null and book.context().session == "","null session context")
		check(book.app.album.empty_message.text.begins_with("Katalog konnte" if invalid else "Hier gibt"),"empty and invalid catalogs distinct")
		check(book.information_routes.request("settings"),"null session settings reachable")
		await settled()
		check(book.information_routes.request("help"),"null session help reachable")
		await settled()
		check(book.information_routes.request_return(),"null session catalog return")
		await settled()
		check(book.app.album.visible and book.capture == null,"null session returns without retained resources")
		book.free()
		await frames()
	Registry.cached = registry.duplicate(true)
	Registry.cached.entries = []
	Registry.load_error = ""
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	await frames()
	check(book.information_routes.request("settings"),"null session starts final preparation")
	# The product close path must end this real process. If it fails to quit,
	# the watchdog overwrites the report and makes the producer fail closed.
	create_timer(3).timeout.connect(func() -> void:
		check(false,"null session native close did not quit")
		write_result()
		quit(4))
	book._notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
	check(book.capture == null and not book.app.presentation_locked and book.state == Book.State.CATALOG,
		"null session native close invalidates preparation")
	if not write_result(): quit(4)

func write_result() -> bool:
	var passed: bool = assertions.all(func(row: Dictionary) -> bool: return row.passed)
	var file := FileAccess.open(output.path_join("integration.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":passed,"assertions":assertions,"engine":Engine.get_version_info()},"\t")+"\n")
	file.close()
	print("BOOK_INTEGRATION_OK" if passed else "BOOK_INTEGRATION_FAILED")
	return passed
