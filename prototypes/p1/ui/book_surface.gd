extends Control
## Only the UI-free material is reflected for the right information page.
const ART = preload("res://art/book/bp2-a-inventarband.png")
const ButtonPaint = preload("res://ui/book_button.gd")
var information: bool = false
var card: Rect2
var miniature: Rect2
var palette: Rect2
var wells: Array[Rect2] = []
var work_visible: bool = false

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func material_rect() -> Rect2:
	# Contain the whole bound master; never stretch/crop away its protected paper.
	var ratio: float = minf(size.x/2560.0,size.y/1440.0)
	var extent: Vector2 = Vector2(2560,1440)*ratio
	return Rect2((size-extent)/2,extent)

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO,size),Color("332719"))
	var rect: Rect2 = material_rect()
	if information:
		draw_set_transform(Vector2(size.x,0),0,Vector2(-1,1))
	draw_texture_rect(ART, rect, false)
	draw_set_transform(Vector2.ZERO)
	if not work_visible:
		return
	for box: Rect2 in wells:
		mount(box,Color("cbb991"))
	mount(palette,Color("f4ead4"))
	mount(card,Color("fffaf0"))
	draw_rect(miniature,Color("fffaf0"))
	for x: float in [card.position.x+3,card.end.x-7]:
		draw_rect(Rect2(x,card.position.y+7,3,13),Color("a68a55"))
	draw_line(Vector2(card.position.x+9,miniature.position.y-5),Vector2(card.end.x-9,miniature.position.y-5),Color("c1b18d"),0.7,true)

func mount(box: Rect2, fill: Color) -> void:
	if not box.has_area():
		return
	draw_colored_polygon(ButtonPaint.points(box,3),Color("a38b65"))
	draw_colored_polygon(ButtonPaint.points(box.grow(-2),2),fill)
	draw_polyline(ButtonPaint.points(box,3),Color("8c7047"),1,true)
