extends Control
## Original KE drawings, authored here for picross; no font or puzzle asset.
const Scribble = preload("res://ui/scribble.gd")
const GRAPHITE = Color("655e51")
var kind: String = "unknown"
var ui_scale: float = 1.0
var pencils: Array[Node2D] = []
var pencil_index: int = 0

class Pencil extends Node2D:
	const SHAPE = [Vector2(-3,-11),Vector2(2.5,-10.5),Vector2(3,8),Vector2(0,14),Vector2(-3.5,8),Vector2(-3,-11)]
	var body: Polygon2D
	func _init() -> void:
		body = Polygon2D.new()
		body.polygon = PackedVector2Array(SHAPE.slice(0,-1))
		body.antialiased = true
		body.show_behind_parent = true
		add_child(body)
		var wood := Polygon2D.new()
		wood.polygon = PackedVector2Array([Vector2(-3,8),Vector2(2.5,8),Vector2(0,14)])
		wood.color = Color("d6bc8d")
		wood.antialiased = true
		wood.show_behind_parent = true
		add_child(wood)
	func _draw() -> void:
		draw_polyline(PackedVector2Array(SHAPE),Color("655e51"),0.9,true)
		draw_line(Vector2(-1,-8),Vector2(-1,7),Color("ead9ae"),0.8,true)
		draw_line(Vector2(0,11),Vector2(0,14),Color("655e51"),1.5,true)

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func pencil(origin: Vector2, angle: float, color: Color, scale_value: float) -> void:
	if pencil_index == pencils.size():
		var created := Pencil.new()
		created.show_behind_parent = true
		add_child(created)
		pencils.append(created)
	var drawing: Pencil = pencils[pencil_index]
	pencil_index += 1
	drawing.position = origin
	drawing.rotation = angle
	drawing.scale = Vector2.ONE*scale_value
	drawing.body.color = color
	drawing.show()

func _draw() -> void:
	pencil_index = 0
	for drawing: Node2D in pencils: drawing.hide()
	var u: float = ui_scale
	var center: Vector2 = size/2
	match kind:
		"paper":
			draw_rect(Rect2(Vector2(1,2)*u,size-Vector2(2,3)*u),Color(0.3,0.24,0.15,0.07))
			draw_rect(Rect2(Vector2.ONE*u,size-Vector2(3,4)*u),Color("f0e6cf"))
			for line: Dictionary in Scribble.outline_strokes(Rect2(Vector2.ONE*u,size-Vector2(3,4)*u),"catalog-label",0.7*u):
				Scribble.paint(self,line,Color("a49478"))
		"mono":
			pencil(center+Vector2(-5,-1)*u,0.45,Color("46504c"),0.85*u)
			draw_polyline(PackedVector2Array([center+Vector2(4,8)*u,center+Vector2(12,7)*u,center+Vector2(5,10)*u,center+Vector2(12,9)*u]),GRAPHITE,1.6*u,true)
		"color":
			pencil(center+Vector2(-7,-2)*u,0.45,Color("ac6250"),0.85*u)
			pencil(center+Vector2(0,-3)*u,0.05,Color("627f91"),0.85*u)
			pencil(center+Vector2(7,-1)*u,-0.4,Color("c2a451"),0.85*u)
		"Neu":
			draw_arc(center,5*u,0.3,TAU-0.15,19,GRAPHITE,1.3*u,true)
		"Begonnen": pencil(center,0.5,Color("9b773b"),0.55*u)
		"Fertig":
			draw_polyline(PackedVector2Array([center+Vector2(-6,0)*u,center+Vector2(-2,5)*u,center+Vector2(1,1)*u,center+Vector2(7,-6)*u]),Color("557250"),2*u,true)
		"Ungültig":
			draw_line(center-Vector2(0,6)*u,center+Vector2(0,2)*u,Color("925348"),2*u,true)
			draw_circle(center+Vector2(0,6)*u,u,Color("925348"))
		"unknown":
			draw_rect(Rect2(Vector2.ZERO,size),Color("faf3e3"))
			# A deliberately asymmetric outlined pencil sketch, 56/112 of image height.
			var scale_value: float = size.y/112.0
			draw_set_transform(center-Vector2(20,28)*scale_value,0,Vector2.ONE*scale_value)
			var outline := PackedVector2Array([Vector2(2,12),Vector2(5,5),Vector2(14,1),Vector2(26,2),Vector2(34,7),Vector2(37,15),Vector2(34,23),Vector2(27,28),Vector2(23,31),Vector2(22,39),Vector2(14,40),Vector2(14,30),Vector2(18,24),Vector2(26,19),Vector2(27,14),Vector2(24,10),Vector2(17,9),Vector2(12,12),Vector2(10,16),Vector2(2,12)])
			draw_colored_polygon(outline,Color("c4bcab"))
			draw_polyline(outline,GRAPHITE,1.2,true)
			for line: PackedVector2Array in [PackedVector2Array([Vector2(7,9),Vector2(12,5)]),PackedVector2Array([Vector2(13,7),Vector2(20,3)]),PackedVector2Array([Vector2(23,7),Vector2(28,4)]),PackedVector2Array([Vector2(30,13),Vector2(34,10)]),PackedVector2Array([Vector2(28,21),Vector2(34,17)]),PackedVector2Array([Vector2(18,29),Vector2(25,25)]),PackedVector2Array([Vector2(16,35),Vector2(21,32)])]:
				draw_polyline(line,Color("8e8574"),0.8,true)
			var dot := PackedVector2Array([Vector2(14,47),Vector2(21,46),Vector2(23,52),Vector2(19,56),Vector2(13,54),Vector2(14,47)])
			draw_colored_polygon(dot,Color("b8af9e"))
			draw_polyline(dot,GRAPHITE,1.2,true)
			draw_line(Vector2(15,52),Vector2(20,49),Color("8e8574"),0.8,true)
			draw_set_transform(Vector2.ZERO)
