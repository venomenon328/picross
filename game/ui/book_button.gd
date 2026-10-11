extends Button
## BP-3 mounting and icon are separate from the unchanged colour sample.
const INK = Color("293e3d")
const PAPER = Color("fffaf0")
const Scribble = preload("res://ui/scribble.gd")
var action_id: String = ""
var selected: bool = false
var swatch: Color = Color.TRANSPARENT
var image: Texture2D
var ui_scale: float = 1.0

func _ready() -> void:
	focus_mode = Control.FOCUS_NONE
	for state: String in ["normal", "hover", "pressed", "disabled", "focus"]:
		add_theme_stylebox_override(state, StyleBoxEmpty.new())
	mouse_entered.connect(queue_redraw)
	mouse_exited.connect(queue_redraw)
	button_down.connect(queue_redraw)
	button_up.connect(queue_redraw)

static func points(box: Rect2, cut: float) -> PackedVector2Array:
	var p: Vector2 = box.position
	var e: Vector2 = box.end
	return PackedVector2Array([p + Vector2(cut, 0), Vector2(e.x-cut,p.y), Vector2(e.x,p.y+cut), e-Vector2(0,cut), e-Vector2(cut,0), Vector2(p.x+cut,e.y), Vector2(p.x,e.y-cut), p+Vector2(0,cut), p+Vector2(cut,0)])

func swatch_strokes() -> Array:
	return Scribble.outline_strokes(Rect2(Vector2.ZERO,size).grow(-1.0),"swatch/"+action_id,1.2)

func _draw() -> void:
	var u: float = ui_scale
	var box: Rect2 = Rect2(Vector2.ZERO, size)
	var body: Color = Color("f4ead4")
	if disabled:
		body = Color("e9e2d4")
	elif selected:
		body = Color("293f3e")
	elif is_pressed():
		body = Color("c5d6cd")
	elif is_hovered():
		body = Color("e0ece6")
	draw_colored_polygon(points(box.grow(-0.5), 4*u), Color("a68a55"))
	if swatch.a > 0:
		for line: Dictionary in swatch_strokes():
			Scribble.paint(self,line,Color("68583f"))
	else:
		draw_polyline(points(box.grow(-0.5), 4*u), Color("68583f"), 1, true)
	draw_colored_polygon(points(box.grow(-2*u), 3*u), body)
	draw_line(Vector2(6,4)*u,Vector2(size.x-6*u,4*u),Color("fff5d6"),0.7,true)
	draw_line(Vector2(6*u,size.y-3*u),size-Vector2(6,3)*u,Color("74664d"),0.7,true)
	if swatch.a > 0:
		draw_rect(box.grow(-5*u), swatch)
		if selected:
			for corner: PackedVector2Array in [PackedVector2Array([Vector2(2,14)*u,Vector2(2,2)*u,Vector2(14,2)*u]),PackedVector2Array([size-Vector2(14,2)*u,size-Vector2(2,2)*u,size-Vector2(2,14)*u])]:
				draw_polyline(corner, INK, 3*u, true)
				draw_polyline(corner, PAPER, u, true)
	elif image != null:
		var ink: Color = PAPER if selected else (Color("757970") if disabled else INK)
		var offset: Vector2 = (size-Vector2(26,26)*u)/2 + Vector2(0,u if is_pressed() else 0)
		draw_texture_rect(image, Rect2(offset,Vector2(26,26)*u), false, ink)
		if selected:
			draw_line(Vector2(11*u,size.y-6*u),size-Vector2(11,6)*u,PAPER,2*u,true)
	if disabled:
		draw_line(Vector2(6*u,size.y-7*u),Vector2(10*u,size.y-7*u),Color("757970"),1.5*u,true)
	if not text.is_empty():
		var font: Font = get_theme_font("font")
		var fs: int = get_theme_font_size("font_size")
		var width: float = font.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs).x
		draw_string(font,Vector2((size.x-width)/2,(size.y+font.get_ascent(fs)-font.get_descent(fs))/2),text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,get_theme_color("font_color"))
	if has_focus():
		draw_polyline(points(box.grow(-5*u),2*u),INK,1.0,true)
