extends "res://ui/book_surface.gd"
## Keep the regular layout and SL frames; the shared book supplies the 3D paper.
func _draw() -> void:
	if not work_visible: return
	for box: Rect2 in wells:
		draw_texture_rect(frames.tools, box, false, Color(1, 1, 1, work_alpha))
	draw_texture_rect(frames.palette, palette, false, Color(1, 1, 1, work_alpha))
	draw_texture_rect(frames.preview, card, false, Color(1, 1, 1, work_alpha))
