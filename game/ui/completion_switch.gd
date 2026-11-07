extends Button
## One native toggle with a rectangular pencil track and an immediate paper slider.
const Scribble = preload("res://ui/scribble.gd")
const PaperStyle = preload("res://ui/book_style.gd")
const UiText = preload("res://ui/ui_text.gd")
const INK = Color("293e3d")
var ui_scale := 1.0:
	set(value):
		ui_scale = value
		queue_redraw()

func _ready() -> void:
	toggle_mode = true
	accessibility_name = "Abschlussansicht: Bild links, Raster rechts"
	for state: String in ["normal","hover","pressed","hover_pressed","disabled","focus"]:
		add_theme_stylebox_override(state,StyleBoxEmpty.new())
	for event: Signal in [toggled,mouse_entered,mouse_exited,button_down,button_up,focus_entered,focus_exited]:
		event.connect(func(_value: Variant = null) -> void: queue_redraw())

func track_rect() -> Rect2:
	return Rect2(Vector2(64,7)*ui_scale,Vector2(88,30)*ui_scale)

func slider_rect() -> Rect2:
	return Rect2(track_rect().position+Vector2(3+(41 if button_pressed else 0),3)*ui_scale,Vector2(41,24)*ui_scale)

func hatch_strokes() -> Array:
	var box := track_rect().grow(-1.5*ui_scale)
	var result: Array = []
	for offset: int in range(-ceili(box.size.y/ui_scale),ceili(box.size.x/ui_scale),4):
		var start := Vector2(box.position.x+offset*ui_scale,box.end.y)
		var end := start+Vector2(box.size.y,-box.size.y)
		if start.x < box.position.x:
			start += Vector2(box.position.x-start.x,-(box.position.x-start.x))
		if end.x > box.end.x:
			end += Vector2(-(end.x-box.end.x),end.x-box.end.x)
		result.append(Scribble.stroke(start,end,"completion-switch/hatch/"+str(offset),0.3*ui_scale,0.9*ui_scale,3))
	return result

func outline(rect: Rect2, identity: String, paper: Color = Color.TRANSPARENT) -> void:
	var style = PaperStyle.make(identity,ui_scale,paper)
	style.ink = Color("8a887d") if disabled else INK
	draw_style_box(style,rect.grow(4.5*ui_scale))

func _draw() -> void:
	var color := Color("8a887d") if disabled else INK
	# Only pencil lines make the dark rail; it has no solid dark fill.
	for line: Dictionary in hatch_strokes(): Scribble.paint(self,line,Color(color,0.70))
	outline(track_rect(),"completion-switch/track")
	outline(slider_rect(),"completion-switch/slider",Color("fffaf0"))
	if is_hovered() and not disabled:
		var style = PaperStyle.make("completion-switch/slider",ui_scale,Color.TRANSPARENT)
		for line: PackedVector2Array in style.contours(slider_rect().grow(4.5*ui_scale)):
			draw_polyline(line,color,1.7*ui_scale,true)
	var font: Font = UiText.font()
	var fs := UiText.small_size(ui_scale)
	for index: int in range(2):
		var caption: String = "Bild" if index == 0 else "Raster"
		var center := (28.0 if index == 0 else 192.0)*ui_scale
		var bounds := UiText.ink(font,caption,fs)
		draw_string(font,Vector2(roundf(center-bounds.size.x/2-bounds.position.x),UiText.line_baseline(font,fs,size.y)),caption,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,color)
		if button_pressed == (index == 1):
			draw_line(Vector2(center-14*ui_scale,size.y-7*ui_scale),Vector2(center+14*ui_scale,size.y-7*ui_scale),color,ui_scale,true)
	if has_focus():
		var style = PaperStyle.make("completion-switch/focus",ui_scale,Color.TRANSPARENT)
		style.focus = true
		style.ink = color
		draw_style_box(style,Rect2(Vector2.ZERO,size).grow(2*ui_scale))
