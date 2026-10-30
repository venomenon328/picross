extends "res://ui/main.gd"
## Developer-only regular UI, synthetic sessions, no filesystem persistence.
const StudySurface = preload("res://study/book/surface.gd")
signal opening_requested(id: String)
signal catalog_shown
signal exit_requested
signal scale_changing

class MemoryPreference extends "res://model/catalog_preference.gd":
	func load_selection() -> void: pass
	func save_selection() -> bool:
		saved = criterion + "/" + direction
		return true

class MemoryStore extends "res://model/save_store.gd":
	var snapshots: Dictionary = {}
	var writes: int = 0
	func load_slot(data: Dictionary) -> Dictionary:
		return {"status": "fresh"} if not snapshots.has(data.id) else {"status": "loaded", "data": snapshots[data.id]}
	func write_slot(item: Session, view: Dictionary) -> String:
		writes += 1
		snapshots[item.definition.id] = snapshot(item, view)
		return ""
	func key_for_definition(id: String) -> String: return id
	func reset_slot(id: String) -> String:
		snapshots.erase(id)
		return ""

func _ready() -> void:
	# Do not call the product lifecycle: no real saves, preference or web storage.
	var input: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://study/book/fixtures.json"))
	Registry.cached = input.registry
	Registry.load_error = ""
	store = MemoryStore.new()
	for data: Dictionary in input.definitions:
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

func select_puzzle(index: int) -> void:
	if index >= 0 and index < sessions.size(): opening_requested.emit(str(sessions[index].definition.id))

func activate(id: String) -> void:
	super.select_puzzle(int(session_indices[id]))

func set_ui_scale(value: float) -> void:
	scale_changing.emit()
	super.set_ui_scale(value)

func show_album() -> void:
	super.show_album()
	catalog_shown.emit()

func _schedule_view_save() -> void:
	if session != null and board != null and _puzzle_view_active(): session.view_state = board.capture_view()

func _save_current() -> bool:
	if session != null and board != null:
		session.view_state = board.capture_view()
		store.write_slot(session, session.view_state)
	return true

func leave_app() -> void: exit_requested.emit()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and board != null: _cancel_interaction()
