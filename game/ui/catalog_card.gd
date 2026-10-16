extends "res://ui/book_button.gd"
## KK: content never contributes a minimum to the grid cell or its neighbours.
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
const MOTIF_FONT = preload("res://art/drawing/BaksoDaging-Regular.ttf")
class CardLabel extends Label:
	# Label otherwise offers its clipped text as a replacement tooltip.
	func _get_tooltip(_at_position: Vector2) -> String: return ""
var caption: Label
var detail: Label
var leaf: Label
var note: Label
var preview: Miniature
var picture: Reveal
var reset: Button
var diagnosis: Label
var recovery: ScrollContainer
var recovery_content: VBoxContainer
var repair: Button
var image_area: Rect2

func _make_custom_tooltip(_for_text: String) -> Object:
	# BookButton's custom factory also runs for empty native tooltip text.
	# The card has no popup at all; its reset child keeps the shared factory.
	return null

func _ready() -> void:
	super._ready()
	clip_contents = true
	resized.connect(layout_content)

func configure(title: String, meta: String, number: String) -> void:
	# No hidden native Button text: it otherwise contributes its font minimum.
	text = ""
	tooltip_text = ""
	caption = label(title, 20)
	caption.add_theme_font_override("font", MOTIF_FONT)
	caption.max_lines_visible = 2
	# Original Bakso's U+2026 glyph is a letter. An unsupported noncharacter
	# selects Godot's native three-period ellipsis fallback, preserving bytes.
	caption.ellipsis_char = "\uFFFF"
	detail = label(meta, 14)
	detail.max_lines_visible = 2
	leaf = label(number, 15, false)
	note = label("", 15, false)
	note.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	preview = Miniature.new()
	preview.draw_frame = false
	preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(preview)
	picture = Reveal.new()
	picture.paired = false
	picture.fit_available = true
	picture.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(picture)
	# Long filesystem diagnostics remain readable by scrolling within the image
	# area, never by adding a variable strip beneath the grid cell.
	recovery = ScrollContainer.new()
	recovery.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	recovery.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(recovery)
	recovery_content = VBoxContainer.new()
	recovery_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	recovery.add_child(recovery_content)
	diagnosis = Label.new()
	diagnosis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	diagnosis.mouse_filter = Control.MOUSE_FILTER_IGNORE
	recovery_content.add_child(diagnosis)

func label(value: String, font_size: int, wrap: bool = true) -> Label:
	var result: Label = CardLabel.new()
	result.text = value
	result.clip_text = true
	result.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if wrap else TextServer.AUTOWRAP_OFF
	result.mouse_filter = Control.MOUSE_FILTER_IGNORE
	result.set_meta("base_font", font_size)
	add_child(result)
	return result

func set_diagnosis(message: String, reset_allowed: bool) -> void:
	diagnosis.text = message
	recovery.visible = not message.is_empty()
	preview.visible = message.is_empty() and picture.payload.is_empty() and not disabled
	picture.visible = message.is_empty() and not picture.payload.is_empty()
	if reset != null:
		reset.visible = reset_allowed
		reset.focus_mode = Control.FOCUS_ALL if reset.visible else Control.FOCUS_NONE
	layout_content()

func layout_content() -> void:
	if caption == null: return
	var u: float = ui_scale
	var inset: float = roundf(10*u)
	var gap: float = roundf(8*u)
	var hit: float = roundf(44*u)
	for control: Label in [caption, detail, leaf, note]:
		control.add_theme_font_size_override("font_size", roundi(float(control.get_meta("base_font"))*u))
	var title_height: float = ceilf(caption.get_theme_font("font").get_height(roundi(20*u))*2)+caption.get_theme_constant("line_spacing")
	var meta_height: float = ceilf(detail.get_theme_font("font").get_height(roundi(14*u))*2)+detail.get_theme_constant("line_spacing")
	var footer_height: float = ceilf(note.get_theme_font("font").get_height(roundi(15*u)))
	var width: float = size.x - 2*inset
	caption.position = Vector2(inset, inset)
	caption.custom_maximum_size = Vector2(maxf(1, width-hit-gap), title_height)
	caption.size = caption.custom_maximum_size
	if reset != null:
		reset.ui_scale = u
		reset.custom_minimum_size = Vector2.ONE*hit
		reset.size = Vector2.ONE*hit
		reset.position = Vector2(size.x-inset-hit, inset)
	detail.position = Vector2(inset, inset+maxf(title_height,hit)+gap)
	detail.custom_maximum_size = Vector2(width, meta_height)
	detail.size = detail.custom_maximum_size
	image_area = Rect2(Vector2(inset, detail.position.y+meta_height+gap), Vector2(width, roundf(112*u)))
	# The miniature's own regular draw/hit projection stays unchanged. Give it
	# the proportional rectangle, centred in the shared bounded image area.
	var fitted: Vector2 = Vector2(preview.width, preview.height)
	fitted *= minf(image_area.size.x/fitted.x, image_area.size.y/fitted.y)
	preview.position = image_area.position+(image_area.size-fitted)/2
	preview.size = fitted
	picture.position = image_area.position
	picture.size = image_area.size
	recovery.position = image_area.position
	recovery.size = image_area.size
	diagnosis.add_theme_font_size_override("font_size", roundi(14*u))
	diagnosis.custom_maximum_size.x = maxf(1,image_area.size.x-recovery.get_v_scroll_bar().get_combined_minimum_size().x)
	recovery_content.add_theme_constant_override("separation", roundi(6*u))
	if repair != null:
		repair.ui_scale = u
		repair.add_theme_font_size_override("font_size", roundi(14*u))
		repair.custom_minimum_size = Vector2(0, hit)
	var bottom: float = image_area.end.y+gap
	var leaf_width: float = ceilf(leaf.get_theme_font("font").get_string_size(leaf.text,HORIZONTAL_ALIGNMENT_LEFT,-1,roundi(15*u)).x)
	leaf.position = Vector2(inset,bottom)
	leaf.size = Vector2(leaf_width,footer_height)
	note.position = Vector2(inset+leaf_width+gap,bottom)
	note.size = Vector2(maxf(1,width-leaf_width-gap),footer_height)
	custom_minimum_size.y = bottom+footer_height+inset
	preview.queue_redraw()
	picture.queue_redraw()
