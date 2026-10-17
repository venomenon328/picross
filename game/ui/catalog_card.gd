extends "res://ui/book_button.gd"
## KK: content never contributes a minimum to the grid cell or its neighbours.
const Miniature = preload("res://ui/miniature.gd")
const Reveal = preload("res://ui/reveal.gd")
const MOTIF_FONT = preload("res://art/drawing/BaksoDaging-Regular.ttf")
const Ink = preload("res://ui/catalog_ink.gd")
const Tip = preload("res://ui/catalog_tip.gd")
const Difficulty = preload("res://model/catalog_difficulty.gd")
signal recovery_activated
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
var label_area: Rect2
var unknown: Ink
var paper: Ink
var mode_icon: Ink
var status_icon: Ink
var dimensions: Label
var difficulty: Tip
var mode_tip: Tip
var recovery_armed: bool = false
var recovery_press_position: Vector2 = Vector2.ZERO
var recovery_press_scroll: int = 0

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
	paper = Ink.new()
	paper.kind = "paper"
	add_child(paper)
	dimensions = label("", 14, false)
	difficulty = Tip.new()
	add_child(difficulty)
	mode_tip = Tip.new()
	add_child(mode_tip)
	mode_icon = Ink.new()
	mode_tip.add_child(mode_icon)
	status_icon = Ink.new()
	add_child(status_icon)
	note = label("", 14, false)
	unknown = Ink.new()
	add_child(unknown)
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
	# The scroll view owns wheel/scrollbar events. Plain left clicks on its
	# noninteractive text are relayed explicitly; repair buttons remain isolated.
	recovery.mouse_filter = Control.MOUSE_FILTER_STOP
	recovery.gui_input.connect(_recovery_input)
	add_child(recovery)
	recovery_content = VBoxContainer.new()
	recovery_content.mouse_filter = Control.MOUSE_FILTER_PASS
	recovery_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	recovery.add_child(recovery_content)
	diagnosis = Label.new()
	diagnosis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	diagnosis.mouse_filter = Control.MOUSE_FILTER_IGNORE
	recovery_content.add_child(diagnosis)

func _recovery_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse: InputEventMouseButton = event
		if mouse.button_index != MOUSE_BUTTON_LEFT:
			# A wheel gesture is not a neutral click, even when reverse scrolling
			# returns to the original offset before the held left button is released.
			recovery_armed = false
			return
		if mouse.pressed:
			recovery_armed = true
			recovery_press_position = mouse.position
			recovery_press_scroll = recovery.scroll_vertical
		else:
			var can_open: bool = recovery_armed and not disabled and recovery.visible and Rect2(Vector2.ZERO,recovery.size).has_point(mouse.position) and recovery_press_position.distance_to(mouse.position) <= 8.0*ui_scale and recovery.scroll_vertical == recovery_press_scroll
			recovery_armed = false
			if can_open: recovery_activated.emit()
	elif event is InputEventMouseMotion and recovery_armed:
		var motion: InputEventMouseMotion = event
		if recovery_press_position.distance_to(motion.position) > 8.0*ui_scale: recovery_armed = false

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
	recovery_armed = false
	diagnosis.text = message
	recovery.visible = not message.is_empty()
	unknown.visible = message.is_empty() and note.text == "Neu" and not disabled
	preview.visible = message.is_empty() and picture.payload.is_empty() and not disabled and not unknown.visible
	picture.visible = message.is_empty() and not picture.payload.is_empty()
	status_icon.kind = note.text
	status_icon.queue_redraw()
	if reset != null:
		reset.visible = reset_allowed
		reset.focus_mode = Control.FOCUS_ALL if reset.visible else Control.FOCUS_NONE
	layout_content()

func set_metadata(width: int, height: int, colored: bool, assessment: Variant) -> void:
	dimensions.text = "%d × %d" % [width, height]
	mode_icon.kind = "color" if colored else "mono"
	mode_tip.tooltip_text = "Farbiges Rätsel" if colored else "Monochromes Rätsel"
	difficulty.text = Difficulty.label(assessment)
	difficulty.tooltip_text = Difficulty.explanation(assessment)

func layout_content() -> void:
	if caption == null: return
	var u: float = ui_scale
	var inset: float = roundf(10*u)
	var gap: float = roundf(8*u)
	var hit: float = roundf(44*u)
	for control: Label in [caption, detail, leaf, note, dimensions]:
		control.add_theme_font_size_override("font_size", roundi(float(control.get_meta("base_font"))*u))
	difficulty.add_theme_font_size_override("font_size",roundi(14*u))
	difficulty.ui_scale = u
	mode_tip.ui_scale = u
	var title_height: float = ceilf(caption.get_theme_font("font").get_height(roundi(20*u))*2)+caption.get_theme_constant("line_spacing")
	var meta_height: float = ceilf(detail.get_theme_font("font").get_height(roundi(14*u))*2)+detail.get_theme_constant("line_spacing")
	var footer_height: float = ceilf(leaf.get_theme_font("font").get_height(roundi(15*u)))
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
	unknown.position = image_area.position
	unknown.size = image_area.size
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
	# Fixed two-column label; widest German metadata fits at 228px/UI125.
	var row_height: float = maxf(roundf(28*u),ceilf(difficulty.get_theme_font("font").get_height(roundi(14*u))))
	label_area = Rect2(Vector2(inset,image_area.end.y+gap),Vector2(width,2*row_height+12*u))
	paper.position = label_area.position
	paper.size = label_area.size
	var left: float = roundf(105*u)
	var origin: Vector2 = label_area.position+Vector2(7,5)*u
	dimensions.position = origin
	dimensions.size = Vector2(left,row_height)
	difficulty.position = origin+Vector2(0,row_height)
	difficulty.size = Vector2(left,row_height)
	mode_tip.position = origin+Vector2(left,0)
	mode_tip.size = Vector2(width-left-14*u,row_height)
	mode_icon.size = mode_tip.size
	status_icon.position = origin+Vector2(left,row_height)
	status_icon.size = Vector2(16*u,row_height)
	note.position = status_icon.position+Vector2(18*u,0)
	note.size = Vector2(width-left-32*u,row_height)
	for control: Label in [dimensions,difficulty,note]: control.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	for drawing: Ink in [paper,mode_icon,status_icon,unknown]:
		drawing.ui_scale = u
		drawing.queue_redraw()
	var bottom: float = label_area.end.y+gap
	var leaf_width: float = ceilf(leaf.get_theme_font("font").get_string_size(leaf.text,HORIZONTAL_ALIGNMENT_LEFT,-1,roundi(15*u)).x)
	leaf.position = Vector2(inset,bottom)
	leaf.size = Vector2(leaf_width,footer_height)
	custom_minimum_size.y = bottom+footer_height+inset
	preview.queue_redraw()
	picture.queue_redraw()
