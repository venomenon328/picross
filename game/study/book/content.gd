extends "res://book/content.gd"
## Developer-only synthetic sessions; never exported in regular players.
const Inputs = preload("res://study/book/inputs.gd")

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

func configure_catalog(catalog: Control) -> void:
	catalog.preference = MemoryPreference.new()
	catalog.set_process(false)

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
