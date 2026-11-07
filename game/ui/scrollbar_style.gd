extends StyleBox
## SBR-A: narrow, bounded ink; geometry depends only on identity and size.
## Godot owns range, hit testing, drag, wheel and page steps.
const Scribble = preload("res://ui/scribble.gd")
const TRACK = Color("62615e")
var identity: String = "book-scroll"
var ui_scale: float = 1.0
var horizontal: bool = false
var thumb: bool = false
var state: String = "normal"

static func make(u: float, sideways: bool, handle: bool, appearance: String) -> StyleBox:
	var style = load("res://ui/scrollbar_style.gd").new()
	style.ui_scale = u
	style.horizontal = sideways
	style.thumb = handle
	style.state = appearance
	# Track width 22; thumb minimum length 28. All states share the same
	# native geometry. Along-axis track margins leave two pixels at each end.
	var along: float = (14.0 if handle else 2.0)*u
	style.content_margin_left = along if sideways else 11*u
	style.content_margin_right = style.content_margin_left
	style.content_margin_top = 11*u if sideways else along
	style.content_margin_bottom = style.content_margin_top
	return style

func point(p: Vector2, rect: Rect2) -> Vector2:
	return rect.position + (Vector2(p.y,p.x) if horizontal else p)

func outline(rect: Rect2) -> PackedVector2Array:
	var u: float = ui_scale
	var size: Vector2 = Vector2(rect.size.y,rect.size.x) if horizontal else rect.size
	var result := PackedVector2Array()
	# Extra inset on the handle exposes the track down both sides. Bounded
	# drift on short segments avoids the large Paper style's long-edge bows.
	var inset: float = (3.0 if thumb else 1.8)*u
	var corners: Array[Vector2] = [Vector2(inset,1.8*u),Vector2(size.x-inset,1.8*u),Vector2(size.x-inset,size.y-1.8*u),Vector2(inset,size.y-1.8*u)]
	for side: int in range(4):
		var a: Vector2 = corners[side]
		var b: Vector2 = corners[(side+1)%4]
		var count: int = maxi(2,ceili(a.distance_to(b)/(23*u)))
		for index: int in range(count):
			var p: Vector2 = a.lerp(b,float(index)/count)
			p += (b-a).normalized().orthogonal()*Scribble.unit(identity+str(side),index)*0.4*u
			result.append(point(p,rect))
	result.append(result[0])
	return result

func hatching(rect: Rect2) -> Array[PackedVector2Array]:
	var u: float = ui_scale
	var size: Vector2 = Vector2(rect.size.y,rect.size.x) if horizontal else rect.size
	var lines: Array[PackedVector2Array] = []
	var y: float = 6*u
	var index: int = 0
	while y < size.y-4*u:
		var id: String = identity+"/hatch/"+str(index)
		var a := Vector2((3.3+Scribble.unit(id,0)*0.8)*u,y)
		var b := Vector2(size.x-(3.3+Scribble.unit(id,1)*0.9)*u,maxf(3*u,y-(9.0+Scribble.unit(id,2)*2.0)*u))
		var mid: Vector2 = a.lerp(b,0.48)+Vector2(Scribble.unit(id,3)*0.45,Scribble.unit(id,4)*0.65)*u
		lines.append(PackedVector2Array([point(a,rect),point(mid,rect),point(b,rect)]))
		y += (7.8+Scribble.unit(id,5)*2.4)*u
		index += 1
	return lines

func _draw(canvas: RID, rect: Rect2) -> void:
	if minf(rect.size.x,rect.size.y) < 4*ui_scale: return
	var edge: PackedVector2Array = outline(rect)
	var color: Color = Color("fffdf5") if state == "hover" else Color("e5e1d7") if state == "pressed" else Color("f3f0e7")
	RenderingServer.canvas_item_add_polygon(canvas,edge,PackedColorArray([color if thumb else TRACK]))
	if not thumb:
		for line: PackedVector2Array in hatching(rect):
			RenderingServer.canvas_item_add_polyline(canvas,line,PackedColorArray([Color("363735")]),0.85*ui_scale,true)
	RenderingServer.canvas_item_add_polyline(canvas,edge,PackedColorArray([Color("3c3d3a")]),1.05*ui_scale,true)
	if thumb:
		var size: Vector2 = Vector2(rect.size.y,rect.size.x) if horizontal else rect.size
		# A small graphite grip, doubled while pressed, distinguishes interaction
		# by marks as well as lightness without reshaping the handle.
		for offset: float in ([-2.0,1.5] if state == "pressed" else [0.0]):
			var a: Vector2 = point(Vector2(7*ui_scale,size.y*0.5+offset*ui_scale),rect)
			var b: Vector2 = point(Vector2(size.x-7*ui_scale,size.y*0.5+(offset+0.6)*ui_scale),rect)
			RenderingServer.canvas_item_add_line(canvas,a,b,Color("77756e"),0.9*ui_scale,true)
	elif state == "focus":
		var line := PackedVector2Array([point(Vector2(3*ui_scale,3*ui_scale),rect),point(Vector2(3.5*ui_scale,(rect.size.x if horizontal else rect.size.y)-3*ui_scale),rect)])
		RenderingServer.canvas_item_add_polyline(canvas,line,PackedColorArray([Color("f3f0e7")]),1.1*ui_scale,true)

func _test_mask(p: Vector2, rect: Rect2) -> bool:
	return rect.has_point(p)
