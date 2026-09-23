extends RefCounted
const Player = preload("res://model/player.gd")
const Gesture = preload("res://model/gesture.gd")
var definition: Dictionary
var player: Player
var gesture: Gesture = Gesture.new()
var completed: bool = false

func _init(data: Dictionary) -> void:
	definition = data.duplicate(true)
	player = Player.new(int(data.width), int(data.height))

func is_solution() -> bool:
	for y: int in range(player.height):
		for x: int in range(player.width):
			var actual: int = player.cells[y * player.width + x]
			var expected: int = int(definition.solution[y][x])
			if (expected > 0 and actual != expected) or (expected == 0 and actual > 0):
				return false
	return true

func finish() -> bool:
	var changed: bool = gesture.finish(player)
	if changed:
		completed = is_solution()
	return changed

func undo() -> void:
	gesture.cancel()
	if player.undo():
		completed = is_solution()

func redo() -> void:
	gesture.cancel()
	if player.redo():
		completed = is_solution()

func visible_cells() -> Array[int]:
	var result: Array[int] = player.cells.duplicate()
	for change: Dictionary in gesture.changes():
		result[change.index] = change.after
	return result

func album_title() -> String:
	return str(definition.reveal.name) if completed else "Blatt %s · %d × %d" % [str(definition.id).trim_prefix("F-"), player.width, player.height]

func reveal() -> Dictionary:
	return definition.reveal.duplicate(true) if completed else {}
