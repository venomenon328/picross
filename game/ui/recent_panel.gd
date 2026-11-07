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
	preview.cells = item.visible_cells()
	preview.width = item.player.width
	preview.height = item.player.height
	preview.palette = item.definition.palette
	preview.style_identity = str(item.definition.id)+"/recent"
	preview.queue_redraw()
	layout()

func layout() -> void:
	if preview == null: return
	var u: float = ui_scale
	var side: float = minf(56*u,size.y-12*u)
	preview.position = Vector2(size.x-side-8*u,6*u)
	preview.size = Vector2.ONE*side
	var width: float = maxf(1,preview.position.x-20*u)
	for item: Label in [caption,detail]:
		UiText.small_label(item,UiText.small_size(u),u)
		item.position.x = 12*u
		item.size.x = width
	caption.size.y = 0
	detail.size.y = 0
	var caption_height: float = caption.get_minimum_size().y
	var detail_height: float = detail.get_minimum_size().y
	caption.position.y = maxf(0,(size.y-caption_height-detail_height)/2)
	detail.position.y = caption.position.y+caption_height
