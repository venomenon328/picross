extends "res://ui/main.gd"
## Developer-only regular UI, synthetic sessions, no filesystem persistence.
const StudySurface = preload("res://study/book/surface.gd")
const StudyCatalog = preload("res://study/book/catalog.gd")
const Inputs = preload("res://study/book/inputs.gd")
const Information = preload("res://study/book/information.gd")
signal opening_requested(id: String)
signal return_requested
signal catalog_shown
signal exit_requested
signal scale_changing
var resetting_ending: bool = false
var book: Node3D
var info: RefCounted

class MemoryPreference extends "res://model/catalog_preference.gd":
	func load_selection() -> void: pass
	func save_selection() -> bool:
		saved = criterion + "/" + direction
		return true

class MemoryStore extends "res://model/save_store.gd":
	var snapshots: Dictionary = {}
	var writes: int = 0
	var failure: String = ""
	func load_slot(data: Dictionary) -> Dictionary:
		return {"status": "fresh"} if not snapshots.has(data.id) else {"status": "loaded", "data": snapshots[data.id]}
	func write_slot(item: Session, view: Dictionary) -> String:
		writes += 1
		if not failure.is_empty(): return failure
		snapshots[item.definition.id] = snapshot(item, view)
		return ""
	func key_for_definition(id: String) -> String: return id
	func reset_slot(id: String) -> String:
		snapshots.erase(id)
		return ""

func _ready() -> void:
	# Do not call the product lifecycle: no real saves, preference or web storage.
	var input: Dictionary = Inputs.read()
	if not input.error.is_empty():
		push_error(input.error)
		get_tree().quit(4)
		return
	Registry.cached = input.registry
	Registry.load_error = ""
	store = MemoryStore.new()
	# Three shapes, 27 fixed IDs: one full spread and one partial spread.
	for index: int in range(input.registry.entries.size()):
		var data: Dictionary = input.definitions[index].duplicate(true)
		var item := Session.new(data)
		# Fixed own entries, including wrong colors and X. Never copy the solution.
		if not sessions.is_empty():
			item.player.commit([{"index": 3, "before": -1, "after": 1}, {"index": 4, "before": -1, "after": 0}])
		session_indices[data.id] = sessions.size()
		sessions.append(item)
		slot_status.append("fresh")
		slot_errors.append("")
	session = sessions[0]
	var punctuation: FontFile = BODY_FONT.duplicate()
	punctuation.allow_system_fallback = false
	var title_font: FontFile = WORK_TITLE_FONT
	title_font.allow_system_fallback = false
	title_font.fallbacks = [punctuation]
	_build()
	save_timer = Timer.new()
	save_timer.one_shot = true
	save_timer.timeout.connect(_save_current)
	add_child(save_timer)
	resized.connect(_check_minimum)
	_check_minimum()
	board.restore_view(session.view_state)
	show_album()

func _build() -> void:
	# Build off-tree so Catalog._ready() receives the memory preference.
	var parent: Node = get_parent()
	parent.remove_child(self)
	laying_out = true
	super._build()
	laying_out = false
	# Remove the old left tab completely. Reuse the three existing right slots;
	# the middle menu remains the unchanged sidebar axis in the base layout.
	album_button.free()
	actions.erase("nav-album")
	album_button = actions["nav-information"]
	album_button.pressed.disconnect(show_information.bind("settings"))
	album_button.pressed.connect(func() -> void: return_requested.emit())
	album_button.action_id = "nav-work"
	album_button.image = load("res://art/book/nav-work.svg")
	album_button.tooltip_text = "Zurück zum Katalog"
	album_button.accessibility_name = "Zurück zum Katalog"
	for id: String in ["help","menu","nav-information"]: actions[id].reparent(page)
	var old_album: Control = album
	page.remove_child(old_album)
	old_album.free()
	album = StudyCatalog.new()
	page.add_child(album)
	album.opened.connect(select_by_id)
	album.reset_requested.connect(_ask_reset_id)
	album.repair_requested.connect(_ask_repair_id)
	album.information_requested.connect(show_information.bind("settings"))
	album.help_requested.connect(show_information.bind("help"))
	album.quit_requested.connect(leave_app)
	album.preference = MemoryPreference.new()
	# The regular catalog polls the web storage status; the study has no storage.
	album.set_process(false)
	var previous: Control = surface
	remove_child(previous)
	previous.free()
	surface = StudySurface.new()
	surface.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(surface)
	move_child(surface, 0)
	parent.add_child(self)
	for item: Node in find_children("*","Button",true,false):
		if item is BookButton: item.paper_transparent = true
		if item is BookChoice: item.paper_transparent = true

func _layout_book(prepare_board: bool = false) -> void:
	super._layout_book(prepare_board)
	if album == null or surface == null or laying_out: return
	if info == null: return
	var material: Rect2 = surface.material_rect()
	var title_origin: Vector2 = material.position+Vector2(material.size.x*0.12,38*ui_scale)
	for id: String in ["help","menu","nav-information"]:
		actions[id].visible = work.visible or ending.visible
	if work.visible or ending.visible:
		var paper_top: float = book.projected_paper(true).position.y if book != null else 0.0
		title_origin.y = maxf(title_origin.y,paper_top+12*ui_scale)
		title.position = title_origin
		var axis: float = actions["menu"].position.x
		album_button.position.x = axis-58*ui_scale
		actions["help"].position.x = axis+58*ui_scale
		for id: String in ["help","menu","nav-information"]:
			actions[id].position.y = maxf(actions["menu"].position.y,paper_top+8*ui_scale)
	layout_warning.position.x = maxf(layout_warning.position.x, title_origin.x)
	title.visible = not information.visible
	if information.visible: info.layout()
	if album.summary != null: album.summary.visible = album.visible and catalog_error.is_empty()
	if album.visible:
		# Projected paper is already in viewport pixels, including letterboxing.
		# Use that one coordinate system for heading, clip areas and both footers.
		var left_paper: Rect2 = book.projected_paper(false,-1)
		var right_paper: Rect2 = book.projected_paper(false,1)
		var inset: float = 18*ui_scale
		var margin: float = left_paper.position.x+inset
		var edge: float = right_paper.end.x-inset
		var curve: float = left_paper.size.x*0.075
		album.fold_gap = 2*(curve+12*ui_scale)
		var right_heading: float = right_paper.position.x+curve+inset
		var heading_top: float = maxf(left_paper.position.y+12*ui_scale,material.size.y*0.035+12*ui_scale)
		var catalog_top: float = heading_top+53*ui_scale
		var footer_width: float = album.right_pager.get_child(0).get_combined_minimum_size().x+album.next_button.get_combined_minimum_size().x+12*ui_scale
		album.right_pager.vertical = (edge-margin-album.fold_gap)/2 < footer_width
		_place(album, Rect2(Vector2(margin,catalog_top),Vector2(edge-margin,left_paper.end.y-inset-catalog_top)))
		_place(title, Rect2(Vector2(margin,heading_top),Vector2(left_paper.end.x-curve-inset-margin,45*ui_scale)))
		if album.summary != null:
			_place(album.summary,Rect2(Vector2(right_heading,heading_top),Vector2(edge-right_heading,45*ui_scale)))
			album.summary.add_theme_font_size_override("font_size",roundi(18*ui_scale))
		album._layout_cards()

func select_puzzle(index: int) -> void:
	if resetting_ending:
		super.select_puzzle(index)
		return
	if index >= 0 and index < sessions.size(): opening_requested.emit(str(sessions[index].definition.id))

func _reset_selected() -> void:
	resetting_ending = reset_origin == "ending"
	super._reset_selected()
	resetting_ending = false

func activate(id: String) -> void:
	super.select_puzzle(int(session_indices[id]))

func set_ui_scale(value: float) -> void:
	scale_changing.emit()
	super.set_ui_scale(value)
	if info != null: info.layout()

func _build_information() -> void:
	super._build_information()
	info = Information.new(self)

func show_information(section: String = "settings") -> void:
	if book != null: book.information_routes.request(section)

func _information_section(section: String) -> void:
	if info == null: information_section = section
	else: show_information(section)

func return_to_work() -> void:
	if book != null: book.information_routes.request_return()

func show_album() -> void:
	super.show_album()
	catalog_shown.emit()

func _schedule_view_save() -> void:
	if session != null and board != null and _puzzle_view_active(): session.view_state = board.capture_view()

func _save_current() -> bool:
	if session != null and board != null:
		if save_timer != null: save_timer.stop()
		session.view_state = board.capture_view()
		save_error = store.write_slot(session, session.view_state)
		slot_errors[sessions.find(session)] = save_error
		_update_status()
	return save_error.is_empty()

func leave_app() -> void: exit_requested.emit()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and board != null: _cancel_interaction()
