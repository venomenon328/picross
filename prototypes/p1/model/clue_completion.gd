extends RefCounted
## Exact single-line feasibility. -1 is unknown, 0 is X, positive values are colors.
## A DAG node (i, p) has consumed i clues and cells before p. Edges either
## consume one empty cell or the next block (plus its required same-color gap).
## Forward reachability and backward feasibility identify every possible start.
## O(clues * cells) time/storage; no full placements or puzzle definition.
static func analyze(cells: Array[int], clues: Array) -> Array[bool]:
	var n: int = cells.size()
	var k: int = clues.size()
	var flags: Array[bool] = []
	flags.resize(k)
	flags.fill(false)
	var ends: Array[PackedInt32Array] = []
	for i: int in range(k):
		var length: int = int(clues[i].length)
		var color: int = int(clues[i].color)
		if length <= 0 or color <= 0:
			return flags
		var bad: PackedInt32Array = PackedInt32Array()
		bad.resize(n + 1)
		for p: int in range(n):
			bad[p + 1] = bad[p] + (0 if cells[p] == -1 or cells[p] == color else 1)
		var targets: PackedInt32Array = PackedInt32Array()
		targets.resize(n + 1)
		targets.fill(-1)
		var gap: bool = i + 1 < k and color == int(clues[i + 1].color)
		for p: int in range(n - length + 1):
			var end: int = p + length
			if bad[end] != bad[p]:
				continue
			if gap:
				if end >= n or cells[end] > 0:
					continue
				end += 1
			targets[p] = end
		ends.append(targets)
	var forward: Array[PackedByteArray] = []
	var backward: Array[PackedByteArray] = []
	for i: int in range(k + 1):
		var row: PackedByteArray = PackedByteArray()
		row.resize(n + 1)
		forward.append(row.duplicate())
		backward.append(row.duplicate())
	forward[0][0] = 1
	for i: int in range(k + 1):
		for p: int in range(n + 1):
			if forward[i][p] == 0:
				continue
			if p < n and cells[p] <= 0:
				forward[i][p + 1] = 1
			if i < k and ends[i][p] >= 0:
				forward[i + 1][ends[i][p]] = 1
	if forward[k][n] == 0:
		return flags
	backward[k][n] = 1
	for i: int in range(k, -1, -1):
		for p: int in range(n, -1, -1):
			if p < n and cells[p] <= 0 and backward[i][p + 1] == 1:
				backward[i][p] = 1
			if i < k and ends[i][p] >= 0 and backward[i + 1][ends[i][p]] == 1:
				backward[i][p] = 1
	for i: int in range(k):
		var start: int = -1
		for p: int in range(n + 1):
			if forward[i][p] == 1 and ends[i][p] >= 0 and backward[i + 1][ends[i][p]] == 1:
				if start >= 0:
					start = -1
					break
				start = p
		if start < 0:
			continue
		flags[i] = true
		for p: int in range(start, start + int(clues[i].length)):
			if cells[p] != int(clues[i].color):
				flags[i] = false
				break
	return flags
