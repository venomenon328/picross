extends "res://ui/book_button.gd"
## Same native Button input/tooltip/focus family; editorial text and underline.

func underline() -> Dictionary:
	var width: float = UiText.width(get_theme_font("font"),text,get_theme_font_size("font_size"))
	return Scribble.stroke(Vector2(8,size.y/ui_scale-7)*ui_scale,Vector2(8*ui_scale+width,size.y-8*ui_scale),action_id+"/underline",0.9*ui_scale,1.8*ui_scale,8)

func _draw() -> void:
	var font: Font = get_theme_font("font")
	var fs: int = get_theme_font_size("font_size")
	draw_string(font,Vector2(8*ui_scale,UiText.line_baseline(font,fs,size.y)),text,HORIZONTAL_ALIGNMENT_LEFT,-1,fs,INK)
	if selected or is_hovered() or has_focus():
		Scribble.paint(self,underline(),INK if selected else Color(INK,0.4))
