extends RefCounted
## Six review-only diagnosis families bound before the E1 layout comparison.
const Definition = preload("res://model/definition.gd")

static func fixture(template: Dictionary, maximum: int, transition: bool = false, transpose: bool = false) -> Dictionary:
	var data: Dictionary = template.duplicate(true)
	data.id = "VS-E18" if transition else "VS-E%d" % (12 + maximum)
	data.width = 50 if transition else maximum * 2 - 1
	data.height = 30 if transition else maximum * 2 - 1
	data.solution = []
	for y: int in range(data.height):
		var row: Array = []
		var count: int = mini(maximum, 5 + y / 10) if transition and maximum < 25 else maximum
		for x: int in range(data.width):
			row.append(1 if x % 2 == 0 and x < count * 2 - 1 and (transition or y % 2 == 0) else 0)
		data.solution.append(row)
	if transpose:
		var matrix: Array = []
		for x: int in range(data.width):
			matrix.append(Definition.column(data.solution, x))
		data.solution = matrix
		var old_width: int = data.width
		data.width = data.height
		data.height = old_width
	data.rows = []
	data.columns = []
	for row: Array in data.solution:
		data.rows.append(Definition.hints(row))
	for x: int in range(data.width):
		data.columns.append(Definition.hints(Definition.column(data.solution, x)))
	return data

static func drag_probe(board: Control, check: Callable) -> Dictionary:
	var report: Dictionary = {"states": 0, "minimum": 999, "minimum_surplus":999, "axes": {}}
	for axis: String in ["row", "column"]:
		var lines: Array = board.session.definition.rows if axis == "row" else board.session.definition.columns
		var minimum: int = 999
		for index: int in range(lines.size()):
			var layout: Dictionary = board.clue_layout(axis, index)
			var count: int = layout.entries.size()
			var offsets: Array[int] = [0, int(layout.max_offset) / 2, int(layout.max_offset)]
			for offset: int in offsets:
				board.set_clue_step(axis, index, offset)
				layout = board.clue_layout(axis, index)
				var pitch: float = layout.slot_extent
				var base: int = int(layout.token_slot) - int(layout.start)
				var shifts: Array[float] = [0.0]
				if count > int(layout.slot_count):
					for distance: float in board.sequence_transitions(layout.entries, int(layout.slot_count), axis, board.clue_font_size()):
						shifts.append(distance + (int(layout.slot_count) - count - base) * pitch)
				board.pan_button = MOUSE_BUTTON_MIDDLE
				board.pan_target = axis
				board.pan_line_index = index
				for shift: float in shifts:
					board.pan_drag_distance = shift
					var units: Array = board.visual_hint_units(axis, index).units
					var tokens: Array = units.filter(func(u: Dictionary) -> bool: return u.kind == "token")
					minimum = mini(minimum, tokens.size())
					report.minimum_surplus = mini(int(report.minimum_surplus),tokens.size()-mini(5,count))
					report.states += 1
					check.call(tokens.size() >= mini(5, count), "%s line %d shift %.3f draws min(5,n) full tokens" % [axis,index,shift])
					for i: int in range(1, tokens.size()):
						check.call(int(tokens[i].index) == int(tokens[i-1].index) + 1 and tokens[i].center > tokens[i-1].center, "drawn tokens consecutive and monotone")
					check.call(board.clue_step(axis, index) == offset, "drag does not snap before release")
					# Verify actual moving ink against the two marker boxes.
					for token: Dictionary in tokens:
						var ink: Vector2 = board.token_ink(str(layout.entries[int(token.index)].text), axis, board.clue_font_size())
						for marker: Dictionary in units:
							if marker.kind == "token": continue
							var bounds: Vector2 = board.token_ink("…", axis, board.clue_font_size())
							check.call(token.center - ink.x >= marker.center + bounds.y or token.center + ink.y <= marker.center - bounds.x, "real marker ink never hides a counted number")
				board.cancel_gesture()
			board.set_clue_step(axis, index, 0)
		report.axes[axis] = minimum
		report.minimum = mini(int(report.minimum), minimum)
	return report
