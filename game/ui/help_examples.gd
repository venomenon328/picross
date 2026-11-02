extends RefCounted
## Fixed, passive teaching diagrams. -1 unknown, 0 empty, positive = palette ID.
## These are illustrations, never definitions, sessions or catalog entries.
const MONO = Color("343f42")
const RED = Color("bd604a")
const BLUE = Color("6c9aab")

static func line(cells: Array, clues: Array, colors: Array = [MONO]) -> Dictionary:
	return {"cells":[cells], "rows":[clues], "columns":[], "colors":colors}

static func all() -> Dictionary:
	var hints: Array = [[1],[3],[5],[3],[1]]
	return {
		"e1":line([1,1,1,0,1,1,1],[3,3]),
		"e2-cross":{"cells":[[-1,-1,1,-1,-1],[-1,-1,1,-1,-1],[1,1,1,1,1],[-1,-1,1,-1,-1],[-1,-1,1,-1,-1]],"rows":hints,"columns":hints,"colors":[MONO]},
		"e2-empty":{"cells":[[0,0,1,0,0],[0,-1,1,-1,0],[1,1,1,1,1],[0,-1,1,-1,0],[0,0,1,0,0]],"rows":hints,"columns":hints,"colors":[MONO]},
		"e2-finish":{"cells":[[0,0,1,0,0],[0,1,1,1,0],[1,1,1,1,1],[0,1,1,1,0],[0,0,1,0,0]],"rows":hints,"columns":hints,"colors":[MONO]},
		"e3-first":line([1,1,1,1,1,0,0],[5]),
		"e3-last":line([0,0,1,1,1,1,1],[5]),
		"e3-overlap":line([-1,-1,1,1,1,-1,-1],[5]),
		"e4-same":line([1,1,1,0,1,1],[{"length":3,"color":1},{"length":2,"color":1}],[RED,BLUE]),
		"e4-touch":line([1,1,1,2,2,0],[{"length":3,"color":1},{"length":2,"color":2}],[RED,BLUE]),
		"e4-gap":line([1,1,1,0,2,2],[{"length":3,"color":1},{"length":2,"color":2}],[RED,BLUE]),
		"unknown":line([-1],[]), "filled":line([1],[]), "empty":line([0],[]),
		"clue-open":{"tokens":[3],"states":[0],"colors":[MONO]},
		"clue-filled":{"tokens":[3],"states":[1],"colors":[MONO]},
		"clue-closed":{"tokens":[3],"states":[2],"colors":[MONO]},
	}
