extends RefCounted

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
		return _result(0, slots - 1, false, true, slots, 0, position, maximum)
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
