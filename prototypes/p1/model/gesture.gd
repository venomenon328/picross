extends RefCounted
const Player = preload("res://model/player.gd")
enum Axis { UNLOCKED, HORIZONTAL, VERTICAL }
var active: bool = false
var start: Vector2i
var endpoint: Vector2i
var axis: Axis = Axis.UNLOCKED
var target: int = Player.UNKNOWN
var source: Array[int] = []
var width: int
var height: int

func begin(player: Player, cell: Vector2i, frozen_target: int) -> bool:
	if active or cell.x < 0 or cell.y < 0 or cell.x >= player.width or cell.y >= player.height:
		return false
	width = player.width
	height = player.height
	source = player.cells.duplicate()
	start = cell
	endpoint = cell
	axis = Axis.UNLOCKED
	target = frozen_target
	active = true
	return true

func move(cell: Vector2i) -> void:
	if not active or cell.x < 0 or cell.y < 0 or cell.x >= width or cell.y >= height:
		return
	var delta: Vector2i = cell - start
	if axis == Axis.UNLOCKED:
		if absi(delta.x) > absi(delta.y):
			axis = Axis.HORIZONTAL
		elif absi(delta.y) > absi(delta.x):
			axis = Axis.VERTICAL
	if axis == Axis.HORIZONTAL:
		endpoint = Vector2i(cell.x, start.y)
	elif axis == Axis.VERTICAL:
		endpoint = Vector2i(start.x, cell.y)

func changes() -> Array:
	var result: Array = []
	if not active:
		return result
	for y: int in range(mini(start.y, endpoint.y), maxi(start.y, endpoint.y) + 1):
		for x: int in range(mini(start.x, endpoint.x), maxi(start.x, endpoint.x) + 1):
			var index: int = y * width + x
			var before: int = source[index]
			if before != target and (target == Player.UNKNOWN or before == Player.UNKNOWN):
				result.append({"index": index, "before": before, "after": target})
	return result

func finish(player: Player) -> bool:
	var pending: Array = changes()
	cancel()
	return player.commit(pending)

func cancel() -> void:
	active = false
	source.clear()
