extends Label
## Passive label: native hover explanation, clicks bubble to the card.
const BookTooltip = preload("res://ui/book_tooltip.gd")
var ui_scale: float = 1.0
var tooltip_ref: WeakRef

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
