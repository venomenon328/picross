extends StyleBox
## HZ-B control-only ink. The seed never contains state, list position or time.
const Scribble = preload("res://ui/scribble.gd")
var identity: String = "paper"
var ui_scale: float = 1.0
var paper: Color = Color("fffaf0")
var ink: Color = Color("78674f")
var selected: bool = false
var focus: bool = false

static func make(id: String, scale: float, color: Color = Color("fffaf0")) -> StyleBox:
	var result = load("res://ui/book_style.gd").new()
	result.identity = id
	result.ui_scale = scale
	result.paper = color
	result.set_content_margin_all(0)
	return result

func contours(rect: Rect2, overrun: bool = true) -> Array:
	var u: float = ui_scale
	var large: bool = maxf(rect.size.x,rect.size.y) > 200*u
	var inset: float = (11.0 if large else 7.0) if focus else (7.0 if large else 4.5)
	var box: Rect2 = rect.grow(-inset * u)
	var p: Vector2 = box.position
	var e: Vector2 = box.end
	var corners: Array[Vector2] = [p, Vector2(e.x,p.y), e, Vector2(p.x,e.y)]
	for i: int in range(4):
		corners[i] += Vector2(Scribble.unit(identity,i*2),Scribble.unit(identity,i*2+1))*0.8*u
	var lines: Array = []
	for i: int in range(4):
		var a: Vector2 = corners[i]
		var b: Vector2 = corners[(i+1)%4]
		var tangent: Vector2 = (b-a).normalized()
		var normal: Vector2 = tangent.orthogonal()
		var bend: float = clampf(a.distance_to(b)/65.0,1.7*u,(5.0 if large else 2.0)*u)
		var c: Vector2 = a.lerp(b,0.33) + normal*Scribble.unit(identity,i+12)*bend
		var d: Vector2 = a.lerp(b,0.68) + normal*Scribble.unit(identity,i+18)*bend
		var points := PackedVector2Array()
		for step: int in range(25):
			var t: float = float(step)/24
			points.append(a.bezier_interpolate(c,d,b,t))
		# Small pen overruns, safely inside the four-pixel AA envelope.
		if overrun:
			points[0] -= tangent*0.9*u
			points[24] += tangent*1.1*u
		lines.append(points)
	return lines

func _draw(canvas: RID, rect: Rect2) -> void:
	var lines: Array = contours(rect)
	if paper.a > 0:
		var polygon := PackedVector2Array()
		for line: PackedVector2Array in contours(rect,false):
			polygon.append_array(line.slice(0,24))
		RenderingServer.canvas_item_add_polygon(canvas,polygon,PackedColorArray([paper]))
	var color: Color = Color("376a60") if selected else ink
	for i: int in range(4):
		RenderingServer.canvas_item_add_polyline(canvas,lines[i],PackedColorArray([color]),(1.65 if selected else 1.15)*ui_scale,true)
	# Short, deliberately offset retracing; never a second mechanical rectangle.
	if not focus:
		for i: int in [0,3]:
			var trace := PackedVector2Array()
			for j: int in range(3,10):
				trace.append(lines[i][j] + Vector2(0.65,0.8)*ui_scale)
			RenderingServer.canvas_item_add_polyline(canvas,trace,PackedColorArray([color]),0.65*ui_scale,true)
	if selected:
		var line: PackedVector2Array = lines[2]
		RenderingServer.canvas_item_add_polyline(canvas,PackedVector2Array([line[5]-Vector2(0,3)*ui_scale,line[19]-Vector2(0,3)*ui_scale]),PackedColorArray([color]),1.3*ui_scale,true)

func _test_mask(point: Vector2, rect: Rect2) -> bool:
	return rect.has_point(point)
