extends RefCounted
const Session = preload("res://model/session.gd")

static func create(data: Dictionary) -> Session:
	var result: Session = Session.new(data)
	var changes: Array = []
	# Deliberately own, possibly wrong marks. Never inspect solution/reveal/proof.
	for y: int in range(result.player.height):
		for x: int in range(result.player.width):
			var value: int = -1
			if y > 3 and (x * 5 + y * 3) % 13 < 8:
				value = 0
			if y > 3 and x % 11 in [3, 4, 5] and y % 9 in [4, 5, 6]:
				value = 1 + (x / 11 + y / 9) % data.palette.size()
			if value >= 0:
				changes.append({"index": y * result.player.width + x, "before": -1, "after": value})
	result.player.commit(changes)
	return result
