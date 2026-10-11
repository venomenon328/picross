extends RefCounted
## Confirmed state only. A change stores exact before/after values per cell.
const UNKNOWN: int = -1
const EMPTY: int = 0
var width: int
var height: int
var cells: Array[int] = []
var history: Array[Array] = []
var cursor: int = 0
var undo_used: bool = false

func _init(w: int, h: int) -> void:
	width = w
	height = h
	cells.resize(w * h)
	cells.fill(UNKNOWN)

func commit(changes: Array) -> bool:
	if changes.is_empty():
		return false
	# Check the entire transaction before changing any cell.
	var seen: Dictionary = {}
	for change: Dictionary in changes:
		var index: int = change.index
		if index < 0 or index >= cells.size() or seen.has(index):
			return false
		if cells[index] != change.before or change.before == change.after:
			return false
		seen[index] = true
	history.resize(cursor)
	history.append(changes.duplicate(true))
	cursor += 1
	for change: Dictionary in changes:
		cells[change.index] = change.after
	return true

func undo() -> bool:
	if cursor == 0:
		return false
	cursor -= 1
	for change: Dictionary in history[cursor]:
		cells[change.index] = change.before
	undo_used = true
	return true

func redo() -> bool:
	if cursor == history.size():
		return false
	for change: Dictionary in history[cursor]:
		cells[change.index] = change.after
	cursor += 1
	return true
