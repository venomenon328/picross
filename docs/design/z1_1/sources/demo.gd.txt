extends RefCounted
## Versioned demo gestures, never derived from the hidden solution.
const Definition = preload("res://model/definition.gd")
const Session = preload("res://model/session.gd")
const REVISION: String = "z1-demo-1"

static func stroke(session: Session, start: Vector2i, end: Vector2i, value: int) -> void:
	session.gesture.begin(session.player, start, value)
	session.gesture.move(end)
	session.finish()

static func create(index: int) -> Session:
	var session: Session = Session.new(Definition.load_fixture(["f01", "f02", "f03"][index]))
	# Explicit illustrative user inputs; errors are allowed and never corrected.
	if index == 0:
		stroke(session, Vector2i(3, 8), Vector2i(9, 8), 1)
		stroke(session, Vector2i(4, 9), Vector2i(9, 9), 1)
		stroke(session, Vector2i(2, 7), Vector2i(10, 7), 0)
	elif index == 1:
		stroke(session, Vector2i(1, 1), Vector2i(38, 1), 4)
		stroke(session, Vector2i(0, 0), Vector2i(12, 0), 0)
		for y: int in range(6, 12):
			stroke(session, Vector2i(5, y), Vector2i(10, y), 2)
		for y: int in range(13, 18):
			stroke(session, Vector2i(19, y), Vector2i(22, y), 3)
		stroke(session, Vector2i(4, 12), Vector2i(12, 12), 0)
		stroke(session, Vector2i(14, 20), Vector2i(24, 20), 1)
		stroke(session, Vector2i(14, 21), Vector2i(20, 21), 1)
	else:
		for y: int in range(42, 49):
			stroke(session, Vector2i(40, y), Vector2i(45, y), 1 + y % 4)
		stroke(session, Vector2i(39, 49), Vector2i(53, 49), 0)
		stroke(session, Vector2i(50, 40), Vector2i(50, 47), 3)
	# A real undone action leaves a coherent redo branch in each comparison.
	stroke(session, Vector2i(2, 2), Vector2i(4, 2), 1)
	session.undo()
	if index == 1:
		session.view_state.zoom = 18
	return session
