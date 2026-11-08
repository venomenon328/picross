extends "res://ui/book_button.gd"
## Same native Button input/tooltip/focus family; editorial text and underline.

func underline() -> Dictionary:
	var width: float = UiText.width(get_theme_font("font"),text,get_theme_font_size("font_size"))
	return Scribble.stroke(Vector2(8,size.y/ui_scale-7)*ui_scale,Vector2(8*ui_scale+width,size.y-8*ui_scale),action_id+"/underline",0.9*ui_scale,1.8*ui_scale,8)

func _draw() -> void:
	var box := Rect2(Vector2.ZERO,size)
	if is_hovered() or is_pressed():
		var style = PaperStyle.make(action_id,ui_scale,Color(0.18,0.24,0.23,0.06))
		style.ink = Color(0.18,0.24,0.23,0.35)
		draw_style_box(style,box.grow(-2*ui_scale))
	var font: Font = get_theme_font("font")
	var fs: int = get_theme_font_size("font_size")
	draw_string(font,Vector2(8*ui_scale,UiText.line_baseline(font,fs,size.y)),text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,INK)
	if selected: Scribble.paint(self,underline(),INK)
	if has_focus():
		var style = PaperStyle.make(action_id,ui_scale,Color.TRANSPARENT)
		style.focus = true
		style.ink = INK
		draw_style_box(style,box)
