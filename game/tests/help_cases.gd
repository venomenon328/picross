extends RefCounted
## Independent tiny enumeration of the actual displayed data, not text copies.
const Examples = preload("res://ui/help_examples.gd")

static func runs(cells: Array) -> Array:
	var result: Array = []
	var last: int = 0
	for cell: int in cells:
		if cell > 0:
			if cell == last: result[-1].length += 1
			else: result.append({"length":1,"color":cell})
		last = cell
	return result

static func clues(values: Array) -> Array:
	var result: Array = []
	for value: Variant in values: result.append(value if value is Dictionary else {"length":value,"color":1})
	return result

static func candidates(values: Array, hints: Array) -> Array:
	var result: Array = []
	# All tested lines are mono and at most seven cells. Full enumeration is
	# deliberately separate from the runtime H1 and production solvers.
	for bits: int in range(1 << values.size()):
		var line: Array = []
		for i: int in range(values.size()): line.append((bits >> i)&1)
		if runs(line) != clues(hints): continue
		var fits: bool = true
		for i: int in range(values.size()):
			if values[i] >= 0 and values[i] != line[i]: fits = false
		if fits: result.append(line)
	return result

static func forced(values: Array, hints: Array, index: int, value: int) -> bool:
	var possible: Array = candidates(values,hints)
	return not possible.is_empty() and possible.all(func(line: Array) -> bool: return line[index] == value)

static func run(t: Object) -> void:
	var data: Dictionary = Examples.all()
	var e1: Dictionary = data.e1
	t.check(candidates([-1,-1,-1,-1,-1,-1,-1],e1.rows[0]) == e1.cells,"HIL E1 unique seven-cell 3 3")
	var placements: Array = candidates([-1,-1,-1,-1,-1,-1,-1],[5])
	t.check(placements.size() == 3 and data["e3-first"].cells[0] == placements[0] and data["e3-last"].cells[0] == placements[2],"HIL E3 actual extreme placements")
	for i: int in range(7):
		var value: int = data["e3-overlap"].cells[0][i]
		t.check((value == 1) == forced([-1,-1,-1,-1,-1,-1,-1],[5],i,1) and (value == 1 or value == -1),"HIL E3 intersection leaves other cells unknown "+str(i))
	var previous: Array = []
	for y: int in range(5): previous.append([-1,-1,-1,-1,-1])
	for key: String in ["e2-cross","e2-empty","e2-finish"]:
		var example: Dictionary = data[key]
		for y: int in range(5):
			for x: int in range(5):
				var value: int = example.cells[y][x]
				if previous[y][x] >= 0:
					t.check(value == previous[y][x],"HIL E2 preserves prior entries %s/%d/%d" % [key,x,y])
				elif value >= 0:
					var column: Array = []
					for row: Array in previous: column.append(row[x])
					t.check(forced(previous[y],example.rows[y],x,value) or forced(column,example.columns[x],y,value),"HIL E2 next deduction follows prior lines %s/%d/%d" % [key,x,y])
		previous = example.cells.duplicate(true)
	for i: int in range(5):
		var column: Array = []
		for row: Array in previous: column.append(row[i])
		t.check(runs(previous[i]) == clues([1,3,5,3,1].slice(i,i+1)) and runs(column) == runs(previous[i]),"HIL E2 final rows and columns match "+str(i))
	for key: String in ["e4-same","e4-touch","e4-gap"]:
		var example: Dictionary = data[key]
		t.check(example.cells[0].size() == 6 and runs(example.cells[0]) == clues(example.rows[0]),"HIL E4 actual lengths colors and spacing "+key)
	t.check(data["unknown"].cells == [[-1]] and data["filled"].cells == [[1]] and data["empty"].cells == [[0]],"HIL legend actual cell states")
	t.check(data["clue-open"].states == [0] and data["clue-filled"].states == [1] and data["clue-closed"].states == [2],"HIL legend actual clue states")
