extends Control
## Viewport overlay: no board clipping, input, model writes or saved state.
var board: Control
var cursor: Vector2 = Vector2.ZERO

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	refresh()

func refresh() -> void:
	visible = board != null and board.is_visible_in_tree() and board.session != null and board.gesture_length() >= 2
	queue_redraw()

func placement() -> Dictionary:
	var font: Font = board.clue_font()
	var fs: int = roundi(24 * board.ui_scale)
	var outline: int = maxi(1, roundi(board.ui_scale))
	var caption: String = str(board.gesture_length())
	var ts: TextServer = TextServerManager.get_primary_interface()
	var rid: RID = font.get_rids()[0]
	var ink: Rect2
	var advance: float = 0.0
	for i: int in range(caption.length()):
		var glyph: int = ts.font_get_glyph_index(rid, fs, caption.unicode_at(i), 0)
		var box: Rect2 = Rect2(Vector2(advance, 0) + ts.font_get_glyph_offset(rid, Vector2i(fs, 0), glyph), ts.font_get_glyph_size(rid, Vector2i(fs, 0), glyph))
		ink = box if i == 0 else ink.merge(box)
		advance += font.get_string_size(caption[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	# Native glyph bearings, outline and AA all fit inside this rectangle.
	ink = ink.grow(outline + 1)
	var client: Rect2 = get_viewport_rect().grow(-4 * board.ui_scale)
	var gap: float = 12 * board.ui_scale
	var place: Vector2 = cursor + Vector2(gap, -gap - ink.size.y)
	if place.x + ink.size.x > client.end.x:
		place.x = cursor.x - gap - ink.size.x
	if place.y < client.position.y:
		place.y = cursor.y + gap
	place = place.clamp(client.position, (client.end - ink.size).max(client.position))
	return {"rect": Rect2(place, ink.size), "baseline": place - ink.position,
		"font": font, "font_size": fs, "outline": outline, "caption": caption}

func _draw() -> void:
	if not visible:
		return
	var p: Dictionary = placement()
	draw_string_outline(p.font, p.baseline, p.caption, HORIZONTAL_ALIGNMENT_LEFT, -1, p.font_size, p.outline, Color("fffaf0"))
	draw_string(p.font, p.baseline, p.caption, HORIZONTAL_ALIGNMENT_LEFT, -1, p.font_size, Color("343f42"))
