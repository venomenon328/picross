extends "res://ui/book_button.gd"
## Entire compact panel is the one ID-bound resume target; own fills only.
const Miniature = preload("res://ui/miniature.gd")
var caption: Label
var detail: Label
var preview: Miniature

func _ready() -> void:
	action_id = "catalog-recent"
	tooltip_text = "Zuletzt bearbeitetes Rätsel fortsetzen"
	accessibility_name = tooltip_text
	paper_transparent = true
	super._ready()
	for title: String in ["Zuletzt bearbeitetes Rätsel fortsetzen", ""]:
		var item := Label.new()
		item.text = title
		item.mouse_filter = Control.MOUSE_FILTER_IGNORE
		item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		add_child(item)
		if caption == null: caption = item
		else: detail = item
	preview = Miniature.new()
	preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(preview)
	resized.connect(layout)

func present(item) -> void:
	detail.text = item.neutral_title()
	preview.cells = item.player.cells.duplicate()
	preview.width = item.player.width
	preview.height = item.player.height
	preview.palette = item.definition.palette
	preview.style_identity = str(item.definition.id)+"/recent"
	preview.queue_redraw()
	layout()

func text_heights(width: float) -> Vector2:
	var heights := Vector2.ZERO
	for index: int in range(2):
		var item: Label = caption if index == 0 else detail
		UiText.small_label(item,UiText.small_size(ui_scale),ui_scale)
		var paragraph := TextParagraph.new()
		paragraph.width = maxf(1,width-item.get_theme_stylebox("normal").get_minimum_size().x)
		paragraph.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
		paragraph.add_string(item.text,item.get_theme_font("font"),item.get_theme_font_size("font_size"))
		heights[index] = UiText.label_height(item,UiText.small_size(ui_scale),maxi(1,paragraph.get_line_count()))
	return heights

func fits(width: float, height: float) -> bool:
	# The same shaped font, wrapping and safety margins as the actual labels.
	# Reserve the complete 56*UI miniature, text gap and both inner edges.
	var text_width: float = width-84*ui_scale
	if text_width <= 0 or width < 44*ui_scale or height < 68*ui_scale: return false
	var heights: Vector2 = text_heights(text_width)
	return heights.x+heights.y <= height-12*ui_scale

func layout() -> void:
	if preview == null: return
	var u: float = ui_scale
	var side: float = minf(56*u,size.y-12*u)
	preview.position = Vector2(size.x-side-8*u,6*u)
	preview.size = Vector2.ONE*side
	var width: float = maxf(1,preview.position.x-20*u)
	var heights: Vector2 = text_heights(width)
	for item: Label in [caption,detail]:
		item.position.x = 12*u
		item.size.x = width
	var caption_height: float = heights.x
	var detail_height: float = heights.y
	caption.size.y = caption_height
	detail.size.y = detail_height
	caption.position.y = maxf(0,(size.y-caption_height-detail_height)/2)
	detail.position.y = caption.position.y+caption_height
