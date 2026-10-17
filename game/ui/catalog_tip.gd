extends Label
## Passive label: native hover explanation, clicks bubble to the card.
const BookTooltip = preload("res://ui/book_tooltip.gd")
var ui_scale: float = 1.0
var tooltip_ref: WeakRef
var number_accent: Color = Color("343f42")
var numbered: bool = false

func _draw() -> void:
	if not numbered: return
	# Keep the complete native text for sizing/accessibility; only its digit is
	# coloured. Draw both runs with the same Plex font, baseline and advances.
	var font: Font = get_theme_font("font")
	var pixels: int = get_theme_font_size("font_size")
	var baseline := Vector2(0, (size.y-font.get_height(pixels))/2+font.get_ascent(pixels))
	draw_string(font,baseline,text.left(1),HORIZONTAL_ALIGNMENT_LEFT,-1,pixels,number_accent)
	baseline.x += font.get_string_size(text.left(1),HORIZONTAL_ALIGNMENT_LEFT,-1,pixels).x
	draw_string(font,baseline,text.substr(1),HORIZONTAL_ALIGNMENT_LEFT,-1,pixels,Color("343f42"))

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	add_to_group("book-buttons")
	resized.connect(dismiss_tooltip)
	visibility_changed.connect(dismiss_tooltip)

func _get_tooltip(_at_position: Vector2) -> String:
	return tooltip_text

func _make_custom_tooltip(for_text: String) -> Object:
	var tip: BookTooltip = BookTooltip.new()
	tip.configure(for_text, ui_scale, get_viewport_rect().size.x, get_theme_font("font"))
	tooltip_ref = weakref(tip)
	return tip

func dismiss_tooltip() -> void:
	if tooltip_ref == null: return
	var tip: Control = tooltip_ref.get_ref()
	if tip != null and tip.is_inside_tree() and tip.get_window() != get_window(): tip.get_window().hide()
	tooltip_ref = null
