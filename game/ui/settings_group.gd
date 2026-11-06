extends PanelContainer
## Settings-local frame and attached title tab; HZ contours have stable identities.
const Paper = preload("res://ui/book_style.gd")
var heading: Label
var content: VBoxContainer
var ui_scale: float = 1.0

func configure(app: Control, caption: String, id: String) -> void:
	name = id
	mouse_filter = Control.MOUSE_FILTER_PASS
	content = VBoxContainer.new()
	add_child(content)
	heading = app.label(caption,20)
	heading.add_theme_font_override("font",app.settings_title.get_theme_font("font"))
	heading.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heading.hide()
	add_child(heading)
	set_scale_value(app.ui_scale)

func set_scale_value(value: float) -> void:
	ui_scale = value
	var margin := StyleBoxEmpty.new()
	margin.content_margin_left = 22*value
	margin.content_margin_right = 22*value
	margin.content_margin_top = 58*value
	margin.content_margin_bottom = 22*value
	add_theme_stylebox_override("panel",margin)
	content.add_theme_constant_override("separation",roundi(12*value))
	queue_redraw()

func tab_rect() -> Rect2:
	var width: float = heading.get_theme_font("font").get_string_size(heading.text,HORIZONTAL_ALIGNMENT_LEFT,-1,heading.get_theme_font_size("font_size")).x
	return Rect2(Vector2(18,0)*ui_scale,Vector2(width+36*ui_scale,44*ui_scale))

func _draw() -> void:
	if heading == null: return
	var tab: Rect2 = tab_rect()
	var style = Paper.make("settings/"+str(name),ui_scale,Color.TRANSPARENT)
	style.ink = Color("6d624d")
	var body: Rect2 = Rect2(Vector2(0,18*ui_scale),size-Vector2(0,18*ui_scale))
	var lines: Array = style.contours(body)
	for index: int in range(4):
		if index != 0:
			draw_polyline(lines[index],style.ink,1.5*ui_scale,true)
			continue
		# Break the top edge at the tab, so ink never crosses its caption.
		var part := PackedVector2Array()
		for point: Vector2 in lines[index]:
			if point.x > tab.position.x+5*ui_scale and point.x < tab.end.x-5*ui_scale:
				if part.size() > 1: draw_polyline(part,style.ink,1.5*ui_scale,true)
				part.clear()
			else: part.append(point)
		if part.size() > 1: draw_polyline(part,style.ink,1.5*ui_scale,true)
	draw_style_box(Paper.make("settings-tab/"+str(name),ui_scale,Color.TRANSPARENT),tab)
	var font: Font = heading.get_theme_font("font")
	var fs: int = heading.get_theme_font_size("font_size")
	var baseline: float = tab.position.y+(tab.size.y-font.get_height(fs))/2+font.get_ascent(fs)
	draw_string(font,Vector2(tab.position.x+14*ui_scale,baseline),heading.text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,Color("293e3d"))
