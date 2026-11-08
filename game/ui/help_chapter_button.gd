extends "res://ui/book_button.gd"
## Same native Button input/tooltip/focus family; editorial text and underline.

func underline() -> Dictionary:
	var width: float = UiText.width(get_theme_font("font"),text,get_theme_font_size("font_size"))
	return Scribble.stroke(Vector2(8,size.y/ui_scale-7)*ui_scale,Vector2(8*ui_scale+width,size.y-8*ui_scale),action_id+"/underline",0.9*ui_scale,1.8*ui_scale,8)

func _draw() -> void:
	var font: Font = get_theme_font("font")
	var fs: int = get_theme_font_size("font_size")
	draw_string(font,Vector2(8*ui_scale,UiText.line_baseline(font,fs,size.y)),text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,INK)
	if selected or is_hovered():
		Scribble.paint(self,underline(),INK if selected else Color(INK,0.4))
	if has_focus():
		# Two separate pencil ticks, not a box or a second selection underline.
		for x: float in [2*ui_scale,size.x-3*ui_scale]:
			Scribble.paint(self,Scribble.stroke(Vector2(x,12*ui_scale),Vector2(x,size.y-12*ui_scale),action_id+"/focus",0.6*ui_scale,1.2*ui_scale,3),INK)
