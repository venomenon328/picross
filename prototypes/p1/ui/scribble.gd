extends RefCounted
## Pure, identity-bound decoration. No RNG, clock, cell state or animation owner.

static func unit(identity: String, index: int) -> float:
	var value: int = 17
	for code: int in identity.to_utf8_buffer():
		value = (value * 131 + code) % 1000003
	value = (value * 8191 + (index + 1) * 104729) % 1000003
	return float(value % 2001) / 1000.0 - 1.0

static func stroke(start: Vector2, end: Vector2, identity: String, amplitude: float, width: float, count: int) -> Dictionary:
	var points: PackedVector2Array = PackedVector2Array()
	var normal: Vector2 = (end-start).normalized().orthogonal()
	for i: int in range(count+1):
		var delta: float = 0.0 if i == 0 or i == count else amplitude * unit(identity, i)
		points.append(start.lerp(end,float(i)/count) + normal*delta)
	return {"points":points,"width":width}

static func paint(canvas: CanvasItem, line: Dictionary, color: Color) -> void:
	canvas.draw_polyline(line.points,color,line.width,true)

static func outline_strokes(box: Rect2, identity: String, width: float = 1.2) -> Array:
	var corners: Array[Vector2] = [box.position,Vector2(box.end.x,box.position.y),box.end,Vector2(box.position.x,box.end.y),box.position]
	var result: Array = []
	for i: int in range(4):
		result.append(stroke(corners[i],corners[i+1],identity+str(i),0.25,width,maxi(2,ceili(corners[i].distance_to(corners[i+1])/24.0))))
	return result
