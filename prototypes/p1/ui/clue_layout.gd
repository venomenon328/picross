extends RefCounted

const GRID_END: String = "grid_end"
const OUTER_START: String = "outer_start"
const MIDDLE: String = "middle"

## Places complete clue tokens and overflow markers on a shared sequence of
## fixed slots. Offset 0 keeps the grid-near end; increasing integer offsets
## move towards the outer beginning one stable reading step at a time.
static func select_window(count: int, capacity: int, offset: int) -> Dictionary:
	var slots: int = maxi(capacity, 1)
	var total: int = maxi(count, 0)
	if total == 0:
		return _result(0, 0, false, false, slots, 0, 0, 0)
	if total <= slots:
		return _result(0, total, false, false, slots, slots - total, 0, 0)
	# Supported clue gutters have at least three slots. This defensive fallback
	# still keeps one complete token and a truthful marker in narrower callers.
	if slots < 3:
		var defensive_offset: int = clampi(offset, 0, total - 1)
		var defensive_index: int = total - 1 - defensive_offset
		return _result(defensive_index, defensive_index + 1, defensive_index > 0,
			defensive_index + 1 < total, slots, slots - 1, defensive_offset, total - 1)
	var maximum: int = total - slots + 2
	var position: int = clampi(offset, 0, maximum)
	if position == 0:
		var visible: int = slots - 1
		return _result(total - visible, total, true, false, slots, 1, position, maximum)
	if position == maximum:
		# Leave the outermost slot free so the first token can land on the
		# nearest integer position when a moving prefix marker disappears.
		return _result(0, slots - 2, false, true, slots, 1, position, maximum)
	var end: int = total - position
	var start: int = end - (slots - 2)
	return _result(start, end, true, true, slots, 1, position, maximum)

static func _result(start: int, end: int, prefix_hidden: bool, suffix_hidden: bool,
		capacity: int, token_slot: int, offset: int, maximum: int) -> Dictionary:
	var units: Array[Dictionary] = []
	if prefix_hidden:
		units.append({"kind": "prefix", "slot": 0})
	for index: int in range(start, end):
		units.append({"kind": "token", "index": index, "slot": token_slot + index - start})
	if suffix_hidden:
		units.append({"kind": "suffix", "slot": capacity - 1})
	return {
		"start": start,
		"end": end,
		"prefix_hidden": prefix_hidden,
		"suffix_hidden": suffix_hidden,
		"slot_count": capacity,
		"token_slot": token_slot,
		"offset": offset,
		"max_offset": maximum,
		"units": units,
	}

## Stores reading intent independently from the current number of slots. Edge
## windows keep their edge anchor; a middle window keeps its visible token
## interval so geometry changes can choose the greatest possible overlap.
static func read_position(count: int, capacity: int, offset: int) -> Dictionary:
	var window: Dictionary = select_window(count, capacity, offset)
	if int(window.max_offset) == 0 or int(window.offset) == 0:
		return {"anchor": GRID_END}
	if int(window.offset) == int(window.max_offset):
		return {"anchor": OUTER_START}
	return {"anchor": MIDDLE, "start": int(window.start), "end": int(window.end)}

static func grid_end_position() -> Dictionary:
	return {"anchor": GRID_END}

static func offset_for_read_position(count: int, capacity: int, position: Dictionary) -> int:
	var grid_end: Dictionary = select_window(count, capacity, 0)
	var maximum: int = int(grid_end.max_offset)
	if maximum == 0:
		return 0
	var anchor: String = str(position.get("anchor", GRID_END))
	if anchor == OUTER_START:
		return maximum
	if anchor != MIDDLE:
		return 0
	var target_start: int = clampi(int(position.get("start", 0)), 0, maxi(count, 0))
	var target_end: int = clampi(int(position.get("end", target_start)), target_start, maxi(count, 0))
	var best_offset: int = 1
	var best_overlap: int = -1
	var best_center_distance: int = 1 << 30
	var best_edge_distance: int = 1 << 30
	# Middle offsets exclude both edge anchors. Supported overflowing layouts
	# always have at least one such offset, including the defensive narrow path.
	for candidate: int in range(1, maximum):
		var window: Dictionary = select_window(count, capacity, candidate)
		var overlap: int = maxi(0, mini(target_end, int(window.end)) - maxi(target_start, int(window.start)))
		var center_distance: int = absi(int(window.start) + int(window.end) - target_start - target_end)
		var edge_distance: int = absi(int(window.start) - target_start) + absi(int(window.end) - target_end)
		if overlap > best_overlap or (overlap == best_overlap and center_distance < best_center_distance) or (overlap == best_overlap and center_distance == best_center_distance and edge_distance < best_edge_distance):
			best_offset = candidate
			best_overlap = overlap
			best_center_distance = center_distance
			best_edge_distance = edge_distance
	return best_offset
