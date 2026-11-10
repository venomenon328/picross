extends SceneTree
## Temporary HP-I2-T01 observer. Instantiates the unchanged regular product root.
const Book = preload("res://book/main.gd")
const Registry = preload("res://model/content_registry.gd")
const Store = preload("res://model/save_store.gd")
const NativeLoader = preload("res://book/puzzle_background_loader.gd")
const A = "pz-hp-i2-a"
const B = "pz-hp-i2-b"
const NONE = "pz-hp-i2-none"
const LEGACY = "pz-hp-i2-legacy"
var book: Book
var output: String
var label: String
var assertions: Array = []
var observations: Array = []
var captures: Array = []
var freeze: Dictionary = {}
var last_observation: String = ""
var started: int
var frame_gaps: Array = []
var last_frame: int = 0
var transitions: Array = []
var active_transition: Dictionary = {}
var zoom_baseline: Dictionary = {}

class DelayedLoader extends RefCounted:
	var inner: RefCounted = NativeLoader.new()
	var delay_ms: int = 700
	var fail: bool = false
	var due: int = 0
	var owner: Control
	var wait_for_publication: bool = false
	var held_result: bool = false
	func start(path: String) -> String:
		due = Time.get_ticks_msec()+delay_ms
		return inner.start(path)
	func poll() -> Dictionary:
		# Only the adapter's result timing is controlled. The product publishes,
		# animates, settles and handles all input on its ordinary lifecycle.
		if held_result or (wait_for_publication and owner != null and not owner.frozen): return {"status":"pending"}
		if Time.get_ticks_msec() < due: return {"status":"pending"}
		var value: Dictionary = inner.poll()
		if fail and value.get("status") != "pending": return {"status":"error","error":"T01_controlled_decode_failure"}
		return value
	func cancel() -> bool: return inner.cancel()

func _initialize() -> void: call_deferred("run")

func check(ok: bool, name: String, detail: Variant = null) -> void:
	assertions.append({"name":name,"passed":ok,"detail":detail})
	if not ok: print("HP_I2_T01_FAIL ",name," ",detail)

func rect(value: Rect2) -> Array:
	return [value.position.x,value.position.y,value.size.x,value.size.y]

func observe_transition(now: int) -> void:
	var moving: bool = book.state in [Book.State.PREPARING,Book.State.OPENING]
	if moving and not book.motion_kind.is_empty():
		if not active_transition.is_empty() and active_transition.preparation_started_usec != book.preparation_started:
			check(false,"observer missed the end of an earlier transition",active_transition)
			transitions.append(active_transition.duplicate(true))
			active_transition = {}
		if active_transition.is_empty():
			var expected: float = book.information_routes.duration() if book.information_routes.moving() else Book.DURATION if book.motion_kind == "open" else Book.RETURN_DURATION if book.motion_kind == "return" else Book.PAGE_DURATION
			active_transition = {"kind":book.motion_kind,"generation":book.generation,
				"preparation_started_usec":book.preparation_started,"expected_motion_seconds":expected,
				"saw_opening":false,"start_visit":book.app.background_visit,"input_barrier_at_start":book.release_barrier}
	if active_transition.is_empty(): return
	if book.state == Book.State.OPENING:
		active_transition.saw_opening = true
		active_transition["preparation_seconds"] = book.preparation_seconds
		active_transition["opening_started_usec"] = book.wall_started
		active_transition["last_observed_motion_seconds"] = book.elapsed
	if not moving and not active_transition.has("settled_at_usec"):
		active_transition["settled_at_usec"] = now
		active_transition["interrupted"] = book.interrupted
		if active_transition.saw_opening:
			active_transition["motion_seconds"] = book.motion_wall_seconds if book.interrupted.is_empty() else (now-int(active_transition.opening_started_usec))/1000000.0
			active_transition["motion_clock"] = "product elapsed wall time" if book.interrupted.is_empty() else "observer interval until interrupted settlement"
		else:
			active_transition["preparation_seconds"] = (now-int(active_transition.preparation_started_usec))/1000000.0
			active_transition["motion_seconds"] = 0.0
			active_transition["motion_clock"] = "interrupted during preparation; no opening observed"
	if not moving and not book.release_barrier:
		active_transition["barrier_released_at_usec"] = now
		active_transition["post_settlement_input_barrier_seconds"] = (now-int(active_transition.settled_at_usec))/1000000.0
		active_transition["total_observed_seconds"] = (now-int(active_transition.preparation_started_usec))/1000000.0
		active_transition["state_after"] = book.state
		active_transition["process_mode_after"] = book.app.process_mode
		active_transition["last_background_request_usec"] = book.app.puzzle_background.last_load_usec
		if active_transition.saw_opening and str(active_transition.interrupted).is_empty():
			check(float(active_transition.motion_seconds) >= float(active_transition.expected_motion_seconds)-0.001,"natural transition retains its declared duration",active_transition.duplicate(true))
		transitions.append(active_transition.duplicate(true))
		active_transition = {}

func observe(record_frame: bool = true) -> void:
	var now: int = Time.get_ticks_usec()
	if record_frame:
		if last_frame > 0: frame_gaps.append((now-last_frame)/1000.0)
		last_frame = now
	if book == null or book.app == null: return
	observe_transition(now)
	var bg = book.app.puzzle_background
	var sample: Dictionary = bg.snapshot()
	sample.rect = rect(bg.box)
	sample.merge({"book_state":book.state,"motion":book.motion_kind,"capture":book.capture != null,"source_snapshot":book.catalog_texture != null,
		"input_barrier":book.release_barrier,"held_buttons":book.held_buttons,
		"work":book.app.work.visible,"background_visible":bg.visible,"information":book.app.information.visible})
	var signature: String = JSON.stringify(sample)
	if signature != last_observation:
		last_observation = signature
		observations.append({"at_ms":(now-started)/1000.0,"sample":sample})
	if sample.frozen:
		var token: String = str(sample.binding.token)
		var decision: Array = [sample.state,sample.visible_id,sample.visible_revision,sample.visible_token,sample.request_count]
		if freeze.has(token) and freeze[token] != decision:
			check(false,"frozen visit changed after first publication",{"before":freeze[token],"after":decision})
		else: freeze[token] = decision
	if sample.active_requests > 1 or sample.stale_requests > 1:
		check(false,"request retention exceeds the concrete one-operation bound",sample)

func frames(count: int = 2) -> void:
	for index: int in range(count):
		await process_frame
		observe()

func settle() -> void:
	var deadline: int = Time.get_ticks_msec()+20000
	while (book.state in [Book.State.PREPARING,Book.State.OPENING] or book.release_barrier) and Time.get_ticks_msec() < deadline:
		await frames(1)
	check(book.state not in [Book.State.PREPARING,Book.State.OPENING] and not book.release_barrier,"unaccelerated transition settled",book.state)
	await frames(2)
	check(book.capture == null and book.catalog_texture == null and book.information_routes.textures.is_empty(),"settlement releases all owned transition captures")

func move(point: Vector2) -> void:
	var event := InputEventMouseMotion.new()
	event.position = point
	event.global_position = point
	Input.parse_input_event(event)
	observe(false)
	await frames(1)

func button(point: Vector2, which: MouseButton, down: bool) -> void:
	var event := InputEventMouseButton.new()
	event.position = point
	event.global_position = point
	event.button_index = which
	event.pressed = down
	event.button_mask = (1 << (which-1)) if down and which <= MOUSE_BUTTON_MIDDLE else 0
	Input.parse_input_event(event)
	observe(false)
	await frames(1)

func click(point: Vector2, which: MouseButton = MOUSE_BUTTON_LEFT) -> void:
	await move(point)
	await button(point,which,true)
	await button(point,which,false)

func key(code: Key) -> void:
	for down: bool in [true,false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = down
		Input.parse_input_event(event)
		observe(false)
		await frames(1)

func open_card(id: String) -> void:
	check(book.state == Book.State.CATALOG,"card opening starts in catalog",id)
	var album = book.app.album
	var index: int = album.visible_ids.find(id)
	check(index >= 0,"requested synthetic card is visible",id)
	if index < 0: return
	var card: Control = album.choices[index]
	var scroll: ScrollContainer = album.right_scroll if album.right_grid.is_ancestor_of(card) else album.scroll
	var visible: Rect2 = card.get_global_rect().intersection(scroll.get_global_rect())
	await click(Vector2(visible.position.x+6*book.app.ui_scale,visible.get_center().y))
	check(book.state in [Book.State.PREPARING,Book.State.OPENING,Book.State.WORK],"real card click enters opening",id)

func open_and_settle(id: String) -> void:
	await open_card(id)
	await settle()
	check(book.state == Book.State.WORK and book.app.session.definition.id == id,"real card click reaches bound puzzle",id)

func catalog() -> void:
	await click(book.app.album_button.get_global_rect().get_center())
	await settle()
	check(book.state == Book.State.CATALOG and book.app.puzzle_background.binding.is_empty(),"real return click leaves background visit")

func geometry() -> Dictionary:
	var app = book.app
	var controls: Dictionary = {}
	for id: String in ["help","menu","nav-information"]:
		controls[id] = rect(app.actions[id].get_global_rect())
	return {"board":rect(app.board.get_global_rect()),"title":rect(app.title.get_global_rect()),
		"coordinate":rect(app.coordinate.get_global_rect()),"tools":rect(app.tools_scroll.get_global_rect()),
		"navigation":controls,"composition":rect(Rect2(app.board.composition_envelope().position+app.board.position,app.board.composition_envelope().size)),
		"cell_size":app.board.view.cell_size,"paper":rect(book.projected_paper(true))}

func capture(name: String, scenario: String) -> void:
	await frames(2)
	await RenderingServer.frame_post_draw
	var image: Image = root.get_texture().get_image()
	check(image != null and not image.is_empty() and image.get_size() == root.size,"native original has exact viewport size",name)
	var path: String = output.path_join(name)
	check(image.save_png(path) == OK,"unmodified native PNG saved",name)
	var bg = book.app.puzzle_background
	var snap: Dictionary = bg.snapshot()
	snap.rect = rect(bg.box)
	captures.append({"file":name,"scenario":scenario,"resolution":[root.size.x,root.size.y],
		"ui_scale":book.app.ui_scale,"background":snap,"geometry":geometry()})

func zoom_in() -> void:
	var board = book.app.board
	var prior: float = board.view.cell_size
	var fixed: Rect2 = book.app.puzzle_background.box
	var token: int = book.app.background_visit
	var count: int = book.app.puzzle_background.request_count
	zoom_baseline = {"id":str(book.app.session.definition.id),"cell":prior,"canvas":fixed,"token":token,"request_count":count,"steps":0}
	for index: int in range(4):
		var before: float = board.view.cell_size
		await click(board.global_position+board.view.viewport.get_center(),MOUSE_BUTTON_WHEEL_UP)
		if board.view.cell_size > before: zoom_baseline.steps += 1
	check(board.view.cell_size > prior,"actual wheel events zoom into work",[prior,board.view.cell_size])
	check(book.app.puzzle_background.box == fixed and book.app.background_visit == token and book.app.puzzle_background.request_count == count,"zoom keeps anchor opacity visit and request count")
	var ink: Rect2 = board.composition_envelope()
	ink.position += board.position
	check(ink.intersects(fixed),"actual work zoom overlaps the background canvas",{"ink":rect(ink),"background":rect(fixed)})

func zoom_out() -> void:
	var board = book.app.board
	var prior: float = board.view.cell_size
	check(not zoom_baseline.is_empty() and zoom_baseline.id == str(book.app.session.definition.id),"inverse wheel probe belongs to the original zoom visit")
	for index: int in range(int(zoom_baseline.get("steps",0))):
		await click(board.global_position+board.view.viewport.get_center(),MOUSE_BUTTON_WHEEL_DOWN)
	check(board.view.cell_size < prior,"actual wheel events zoom back",[prior,board.view.cell_size])
	check(is_equal_approx(board.view.cell_size,float(zoom_baseline.cell)) and book.app.puzzle_background.box == zoom_baseline.canvas and book.app.background_visit == zoom_baseline.token and book.app.puzzle_background.request_count == zoom_baseline.request_count,"inverse wheel events restore original zoom canvas and visit",{"before":zoom_baseline.cell,"after":board.view.cell_size,"accepted_up_steps":zoom_baseline.steps})

func passive_input() -> void:
	var app = book.app
	var background = app.puzzle_background
	check(background.mouse_filter == Control.MOUSE_FILTER_IGNORE and background.focus_mode == Control.FOCUS_NONE,"background owns no mouse or focus route")
	var hit_size: float = 44*app.ui_scale
	for id: String in ["help","menu","nav-information"]:
		check(app.actions[id].size.x >= hit_size and app.actions[id].size.y >= hit_size,"navigation keeps the 44/55px target",id)
	var cells: Array = app.session.player.cells.duplicate()
	var point: Vector2 = app.board.global_position+app.board.view.origin+Vector2(4.5,4.5)*app.board.view.cell_size
	await click(point)
	check(app.session.player.cells != cells,"real pointer paints the ordinary grid through the passive layer")
	await click(app.undo_button.get_global_rect().get_center())
	check(app.session.player.cells == cells,"real undo restores exact cells")
	await key(KEY_TAB)
	var focus: Control = root.gui_get_focus_owner()
	check(focus != null and is_instance_valid(focus) and focus != background and focus.is_visible_in_tree() and focus.focus_mode != Control.FOCUS_NONE,"real Tab reaches a visible functional control and skips the background",str(focus.get_path()) if focus != null else null)

func slot_files(id: String) -> Dictionary:
	var result: Dictionary = {}
	var key_value: String = Registry.key_for_id(id)
	for suffix: String in [".json",".bak"]:
		var path: String = book.app.store.path_for(key_value,suffix)
		result[suffix] = FileAccess.get_file_as_bytes(path) if FileAccess.file_exists(path) else null
	return result

func slot_fingerprints(files: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for suffix: String in files:
		if files[suffix] == null:
			result[suffix] = {"exists":false}
		else:
			var bytes: PackedByteArray = files[suffix]
			var digest := HashingContext.new()
			digest.start(HashingContext.HASH_SHA256)
			digest.update(bytes)
			result[suffix] = {"exists":true,"bytes":bytes.size(),"sha256":digest.finish().hex_encode()}
	return result

func control_visibility_probe() -> void:
	# This is a bounded view-visibility check, explicitly not a completion E2E
	# claim. It exercises the actual work visibility signal with no extra image.
	var app = book.app
	var bg = app.puzzle_background
	var before: Dictionary = bg.snapshot()
	var cells: Array = app.session.player.cells.duplicate()
	var files: Dictionary = slot_files(str(app.session.definition.id))
	check(app.work.visible and bg.visible,"control visibility probe starts on visible work")
	app.work.hide()
	check(not bg.visible and not app.work.visible,"control visibility probe hides background with work, no layout required")
	app.work.show()
	check(bg.visible and bg.snapshot() == before and app.session.player.cells == cells and slot_files(str(app.session.definition.id)) == files,"control visibility probe restores drawing without visit load cell or save changes")

func deep_cases() -> void:
	var app = book.app
	var background = app.puzzle_background
	await zoom_in()
	check(background.state == "visible","A remains visible behind zoomed cells and clues")
	var selected_geometry: Dictionary = geometry()
	await capture("04-2560x1440-ui100-selected-zoom.png","selected A, same visit after real wheel zoom with overlap")
	await passive_input()
	await zoom_out()
	await catalog()
	await open_and_settle(NONE)
	await zoom_in()
	check(background.state == "none" and background.texture == null and app.marginalia.family.is_empty(),"explicit none owns no texture or category fallback")
	check(geometry() == selected_geometry,"selected and none preserve exact functional geometry",{"selected":selected_geometry,"none":geometry()})
	await capture("05-2560x1440-ui100-none-control.png","explicit none at corresponding work zoom, geometry control")
	await catalog()
	await open_and_settle(B)
	check(background.state == "visible" and background.binding.id == B,"second distinct selected image is displayed")
	await catalog()
	await open_and_settle(A)
	check(background.state == "visible" and background.binding.id == A,"A to B to A never keeps the wrong image")
	var old_visit: int = app.background_visit
	await click(app.actions["help"].get_global_rect().get_center())
	await settle()
	check(book.state == Book.State.INFORMATION and background.binding.is_empty() and background.texture == null,"real help click releases work texture after source capture")
	await click(app.info.right_return.get_global_rect().get_center())
	await settle()
	check(book.state == Book.State.WORK and app.background_visit > old_visit,"real information return creates a fresh visit")
	await catalog()
	await open_and_settle(LEGACY)
	check(background.state == "legacy" and background.texture == null,"Legacy retains the category path without a new request")
	await catalog()
	# Controlled async adapter changes timing/failure only. It still loads the
	# real imported resource and cannot alter any book state or held-button mask.
	var delayed := DelayedLoader.new()
	delayed.owner = background
	delayed.delay_ms = 0
	delayed.wait_for_publication = true
	background.backend = delayed
	await open_and_settle(A)
	check(background.state == "omitted" and background.texture == null,"late result stays omitted throughout settled visit",background.diagnostic)
	await frames(3)
	check(background.request.is_empty(),"late native request was drained without a retained texture")
	await catalog()
	delayed.wait_for_publication = false
	delayed.delay_ms = 0
	delayed.fail = true
	await open_and_settle(B)
	check(background.state == "omitted" and background.texture == null and background.diagnostic == "T01_controlled_decode_failure","controlled decode failure remains diagnosed omission",background.diagnostic)
	await catalog()
	delayed.delay_ms = 0
	delayed.fail = false
	delayed.held_result = true
	var rapid_start: int = observations.size()
	await open_card(A)
	var before_escape: int = book.generation
	await key(KEY_ESCAPE)
	await settle()
	check(book.state == Book.State.CATALOG and book.generation > before_escape and background.binding.is_empty(),"real Escape cancels opening and invalidates visit")
	await open_card(B)
	await key(KEY_ESCAPE)
	await settle()
	await open_card(A)
	var publication_deadline: int = Time.get_ticks_msec()+20000
	while not background.frozen and book.state in [Book.State.PREPARING,Book.State.OPENING] and Time.get_ticks_msec() < publication_deadline:
		await frames(1)
	check(background.frozen,"rapid target reaches its ordinary publication before releasing the controlled stale result")
	delayed.held_result = false
	await settle()
	check(book.state == Book.State.WORK and app.session.definition.id == A,"rapid return reaches the real A work page")
	check(background.state == "omitted" and background.texture == null,"rapid A to B to A discards the earlier request")
	var saw_stale_queue: bool = false
	for observation: Dictionary in observations.slice(rapid_start):
		if observation.sample.stale_requests == 1 and observation.sample.queued: saw_stale_queue = true
	check(saw_stale_queue,"rapid A to B to A actually observed one stale request plus latest queued metadata")
	check(background.peak_requests <= 1 and background.request.is_empty(),"bounded stale work drained after rapid return")
	await catalog()
	background.backend = NativeLoader.new()
	await open_and_settle(A)
	check(background.state == "visible","a new visit retries successfully after late failure and abort")
	await catalog()
	# Same ID and path, a fresh technical image revision, unchanged logical
	# definition/save identity. Replace the disposable remapped texture with B's
	# independently imported bytes; no source/production file is modified.
	var logical: Dictionary = app.sessions[int(app.session_indices[A])].definition.duplicate(true)
	var old_entry: Dictionary = Registry.by_id(A)
	var identity: Dictionary = {"id":old_entry.id,"key":old_entry.key,"save_slot":old_entry.save_slot}
	var saves_before: Dictionary = slot_files(A)
	check(saves_before[".json"] != null and saves_before[".bak"] != null,"image-only comparison begins with actual primary and backup files",slot_fingerprints(saves_before))
	var a_import := ConfigFile.new()
	var b_import := ConfigFile.new()
	check(a_import.load("res://art/backgrounds/"+A+".png.import") == OK and b_import.load("res://art/backgrounds/"+B+".png.import") == OK,"both independent imported resources exist")
	var a_path: String = a_import.get_value("remap","path","")
	var b_path: String = b_import.get_value("remap","path","")
	var original: PackedByteArray = FileAccess.get_file_as_bytes(a_path)
	var replacement: PackedByteArray = FileAccess.get_file_as_bytes(b_path)
	var file := FileAccess.open(a_path,FileAccess.WRITE)
	file.store_buffer(replacement)
	file.close()
	for entry: Dictionary in Registry.cached.entries:
		if entry.id == A:
			entry.background.image_revision = int(old_entry.background.image_revision)+1
	await open_and_settle(A)
	var expected: Texture2D = ResourceLoader.load("res://art/backgrounds/"+B+".png","Texture2D",ResourceLoader.CACHE_MODE_IGNORE)
	check(background.state == "visible" and background.binding.image_revision == int(old_entry.background.image_revision)+1 and background.texture.get_image().get_data() == expected.get_image().get_data(),"same-path revision installs the new image, not a cached old one")
	check(app.session.definition == logical,"decorative image switch preserves the complete logical definition")
	control_visibility_probe()
	await catalog()
	var new_entry: Dictionary = Registry.by_id(A)
	var saves_after: Dictionary = slot_files(A)
	check({"id":new_entry.id,"key":new_entry.key,"save_slot":new_entry.save_slot} == identity,"image-only visit preserves ID key and save-slot identity",identity)
	check(saves_after == saves_before,"image-only visit preserves exact primary and backup save bytes",{"before":slot_fingerprints(saves_before),"after":slot_fingerprints(saves_after)})
	file = FileAccess.open(a_path,FileAccess.WRITE)
	file.store_buffer(original)
	file.close()
	check(background.texture == null and background.ready_texture == null and background.request.is_empty() and background.desired.is_empty(),"final leave releases all owned image and request references")

func run() -> void:
	output = OS.get_environment("HP_I2_OUTPUT")
	label = OS.get_environment("HP_I2_CASE")
	if output.is_empty() or label.is_empty(): quit(4); return
	started = Time.get_ticks_usec()
	Store.test_root_override = output.path_join("profiles/"+label+"/saves")
	DirAccess.make_dir_recursive_absolute(Store.test_root_override)
	book = load("res://main.tscn").instantiate()
	root.add_child(book)
	# Root handlers were connected in _ready first. Observing after their signal
	# handlers captures a queued request even when publication follows this frame.
	book.app.opening_requested.connect(func(_id: String) -> void: observe(false))
	book.app.return_requested.connect(func() -> void: observe(false))
	await frames(3)
	check(book.get_script().resource_path == "res://book/main.gd","unchanged regular main.tscn book root")
	var version: Dictionary = Engine.get_version_info()
	check(version.major == 4 and version.minor == 7 and version.patch == 2 and str(version.hash).begins_with("ed1daf0bf"),"bound Godot version",version)
	check(book.app.catalog_error.is_empty() and Registry.cached.format == "picross-runtime-registry-v6","actual v6 integration projection enters real reader",book.app.catalog_error)
	book.set_ui_scale(1.25 if label == "1920" else 1.0)
	await frames(3)
	await open_and_settle(A)
	check(book.app.puzzle_background.state == "visible","native selected image ready before first publication",book.app.puzzle_background.snapshot())
	var names: Dictionary = {"1280":"01-1280x720-ui100-selected-fit.png","1920":"02-1920x1080-ui125-selected-fit.png","2560":"03-2560x1440-ui100-selected-fit.png","3840":"06-3840x2160-ui100-selected-fit.png"}
	await capture(names[label],"selected A fit, natural initial visit")
	if label == "2560": await deep_cases()
	else: await catalog()
	var sorted_gaps: Array = frame_gaps.duplicate()
	sorted_gaps.sort()
	var passed: bool = assertions.all(func(row: Dictionary) -> bool: return row.passed)
	var report: Dictionary = {"format":"hp-i2-t01/v1","case":label,"passed":passed,"assertions":assertions,
		"observations":observations,"captures":captures,"publication_decisions":freeze,"transitions":transitions,"unfinished_transition":active_transition,"engine":Engine.get_version_info(),
		"os":OS.get_name(),"rendering_method":RenderingServer.get_current_rendering_method(),"rendering_driver":RenderingServer.get_current_rendering_driver_name(),
		"elapsed_seconds":(Time.get_ticks_usec()-started)/1000000.0,
		"frame_observation":{"count":frame_gaps.size(),"p50_ms":sorted_gaps[sorted_gaps.size()/2] if not sorted_gaps.is_empty() else null,"max_ms":sorted_gaps[-1] if not sorted_gaps.is_empty() else null,"meaning":"observed whole-frame intervals, not a GPU/FPS guarantee or decoration-only timing"},
		"timing_meaning":"transition preparation/product motion/observed post-settlement input barrier are separate; last_background_request_usec includes polling and controlled adapter delay, not pure decoder CPU time; whole-frame observations include probe readback/PNG work",
		"limits":"Linux native original/engine input; no Windows start or browser interaction; owned references, not allocator/GPU RSS reclamation"}
	var result := FileAccess.open(output.path_join("T01-"+label+".json"),FileAccess.WRITE)
	result.store_string(JSON.stringify(report,"\t")+"\n")
	result.close()
	book.free()
	book = null
	await frames(2)
	print("HP_I2_T01_OK" if passed else "HP_I2_T01_FAILED")
	quit(0 if passed else 1)
